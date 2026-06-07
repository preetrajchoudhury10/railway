# GenAI Job Hunter — Scraper Module
# Sources: Reddit, Naukri, Company Career Pages, RSS, Google Jobs

import requests
from bs4 import BeautifulSoup
import json, os, time, hashlib, re
from datetime import datetime, timedelta
from urllib.parse import quote, urljoin
import urllib3
urllib3.disable_warnings()

KEYWORDS = [
    "generative ai","genai","llm","large language model","rag",
    "retrieval augmented","agentic ai","langchain","prompt engineer",
    "foundation model","ai engineer","ai developer","nlp engineer",
    "deep learning","ai fresher","ai intern","hugging face",
    "fine tuning","vector database","ai/ml","chatbot","ai enabler"
]
EXCLUDE = [
    "senior","lead","principal","staff","manager","director",
    "head of","architect","vp","vice president","15+","10+",
    "7+ years","5+ years","experienced","san francisco","remote - us",
    "san jose","new york","seattle","los angeles","united states"
]
INCLUDE_LEVEL = [
    "intern","fresher","entry level","entry-level","new grad","new graduate",
    "junior","associate","apprentice","trainee","0-1","0-2","graduate",
    "early career","early-career","ai engineer","software engineer",
    "machine learning engineer","data engineer","developer",
    "research engineer","research scientist","applied scientist"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
]

def get_headers():
    return {
        "User-Agent": USER_AGENTS[int(time.time()) % len(USER_AGENTS)],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",
        "Connection": "keep-alive",
    }

def jid(co, role):
    return hashlib.md5(f"{co}|{role}".lower().strip().encode()).hexdigest()

def relevant(title, desc="", strict=False):
    text = f"{title} {desc[:500]}".lower()
    for ex in EXCLUDE:
        if ex in text:
            return False
    score = sum(1 for kw in KEYWORDS if kw.lower() in text)
    if strict:
        has_level = any(lvl in text for lvl in INCLUDE_LEVEL)
        return score >= 1 and has_level
    return score >= 1

def fetch(url, parser="html.parser", timeout=20):
    for attempt in range(2):
        try:
            r = requests.get(url, headers=get_headers(), verify=False, timeout=timeout)
            r.raise_for_status()
            return BeautifulSoup(r.text, "html5lib" if parser=="html.parser" else parser)
        except:
            time.sleep(2)
    return None

def fetch_text(url, timeout=15):
    try:
        r = requests.get(url, headers=get_headers(), verify=False, timeout=timeout)
        r.raise_for_status()
        return r.text
    except:
        return None


# =====================
# SOURCE 1: REDDIT
# =====================
def scrape_reddit():
    """Scrape Reddit for job posts mentioning GenAI"""
    jobs = []
    subreddits = ["jobs", "cscareerquestions", "developersIndia", "genai", "machinelearningjobs"]
    for sub in subreddits:
        # Use Reddit's JSON API (no auth required for public subreddits)
        url = f"https://www.reddit.com/r/{sub}/search.json?q=generative+AI+OR+genai+OR+LLM+OR+hiring&restrict_sr=on&sort=new&t=week&limit=25"
        try:
            r = requests.get(url, headers={"User-Agent": "GenAIJobHunter/1.0"}, timeout=15)
            if r.status_code != 200: continue
            data = r.json()
            for post in data.get("data", {}).get("children", []):
                p = post.get("data", {})
                title = p.get("title", "")
                url = p.get("url", "")
                text = p.get("selftext", "") or ""
                permalink = f"https://www.reddit.com{p.get('permalink', '')}"
                if relevant(title, text):
                    # Check if it's a job posting
                    tags = p.get("link_flair_text", "") or ""
                    if any(t in title.lower() or t in tags.lower() for t in ["hiring", "job", "opening", "offer", "position"]):
                        jobs.append({
                            "co": f"Reddit/r/{sub}",
                            "role": title[:100],
                            "url": permalink,
                            "desc": text[:300],
                            "source": "Reddit"
                        })
        except: pass

    return jobs


# =====================
# SOURCE 2: COMPANY CAREER PAGES
# =====================
def scrape_company_careers():
    """Scrape known company career pages for GenAI roles"""
    jobs = []
    companies = [
        {"name": "Google", "url": "https://careers.google.com/jobs/results/?q=generative+AI"},
        {"name": "Microsoft", "url": "https://jobs.careers.microsoft.com/global/en/search?q=generative%20AI&rt=us"},
        {"name": "OpenAI", "url": "https://openai.com/careers/search?q=engineer"},
        {"name": "Anthropic", "url": "https://www.anthropic.com/careers"},
        {"name": "Meta", "url": "https://www.metacareers.com/jobs/?q=generative%20AI"},
        {"name": "Amazon", "url": "https://www.amazon.jobs/en/search?base_query=generative+AI&loc_query=India"},
        {"name": "LinkedIn", "url": "https://www.linkedin.com/jobs/search/?keywords=generative%20AI&location=India"},
        {"name": "NVIDIA", "url": "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/jobs?q=generative+AI"},
    ]
    for co in companies:
        try:
            html = fetch_text(co["url"])
            if not html: continue
            soup = BeautifulSoup(html, "html5lib")
            # Various career page patterns
            for a in soup.select("a[href*='job']") + soup.select("a[href*='career']") + soup.select("a[href*='position']"):
                title = a.text.strip()
                href = a.get("href", "")
                if title and len(title) > 10 and relevant(title, "", strict=True):
                    if not href.startswith("http"):
                        href = urljoin(co["url"], href)
                    jobs.append({
                        "co": co["name"],
                        "role": title[:100],
                        "url": href,
                        "desc": "",
                        "source": "Careers"
                    })
        except: pass
    return jobs


# =====================
# SOURCE 3: NAUKRI.COM
# =====================
def scrape_naukri():
    jobs = []
    queries = ["generative-ai-jobs", "genai-jobs", "llm-engineer-jobs", "ai-engineer-fresher-jobs"]
    for q in queries:
        soup = fetch(f"https://www.naukri.com/{q}-in-india?k={q.replace('-','+')}")
        if not soup: continue
        for card in soup.select("article.jobTuple") or soup.select("div.job-card") or soup.select("div[class*=jobCard]"):
            title_el = card.select_one("a.title") or card.select_one("a[class*=title]")
            comp_el = card.select_one("a.subTitle") or card.select_one("a[class*=comp-name]")
            if title_el:
                title = title_el.text.strip()
                co = comp_el.text.strip() if comp_el else "Naukri"
                link = title_el.get("href", "")
                if link and not link.startswith("http"):
                    link = "https://www.naukri.com" + link
                if relevant(title, ""):
                    jobs.append({"co": co, "role": title[:100], "url": link, "desc": "", "source": "Naukri"})
        time.sleep(2)
    return jobs


# =====================
# SOURCE 4: INDEED RSS
# =====================
def scrape_indeed_rss():
    jobs = []
    queries = ["generative+AI+fresher+India", "genai+engineer+India",
               "LLM+engineer+fresher+India", "AI+fresher+Pune"]
    for q in queries:
        try:
            from xml.etree import ElementTree as ET
            for domain in ["https://in.indeed.com", "https://www.indeed.com"]:
                resp = requests.get(f"{domain}/rss?q={q}", headers=get_headers(), timeout=10, verify=False)
                if resp.status_code != 200: continue
                root = ET.fromstring(resp.content)
                for item in root.findall(".//channel/item") or root.findall(".//item"):
                    t = item.findtext("title", "")
                    d = item.findtext("description", "")
                    link = item.findtext("link", "")
                    co = item.findtext("source", "Indeed")
                    if " - " in t:
                        parts = t.rsplit(" - ", 1)
                        t = parts[0].strip()
                        if co == "Indeed": co = parts[1].strip()
                    if relevant(t, d):
                        jobs.append({"co": co, "role": t[:100], "url": link, "desc": d[:300], "source": "Indeed"})
                if jobs: break
        except:
            pass
    return jobs


# =====================
# SOURCE 5: GOOGLE JOBS / SEARCH
# =====================
def scrape_google_jobs():
    jobs = []
    queries = [
        '"generative AI" fresher India 2026',
        '"genai" engineer fresher India 2026',
        '"LLM engineer" entry level India 2026',
        '"AI engineer" fresher Pune 2026',
        '"agentic AI" fresher India',
    ]
    for q in queries:
        try:
            soup = fetch(f"https://html.duckduckgo.com/html/?q={quote(q)}")
            if not soup: continue
            for a in soup.select("a.result__a") or soup.select("a[class*=result]"):
                href = a.get("href", "")
                title = a.text.strip()
                if relevant(title, "") and href:
                    # Clean DDG redirect
                    if "uddg=" in href:
                        from urllib.parse import parse_qs, urlparse
                        parsed = urlparse(href)
                        qs = parse_qs(parsed.query)
                        if "uddg" in qs:
                            href = qs["uddg"][0]
                    co = "Unknown"
                    for domain in ["linkedin.com","naukri.com","internshala.com","indeed.com"]:
                        if domain in href: co = domain.split(".")[0].title(); break
                    if "job" in title.lower() or "hiring" in title.lower() or "opening" in title.lower():
                        if " - " in title: title = title.rsplit(" - ", 1)[0].strip()
                        jobs.append({"co": co, "role": title[:100], "url": href, "desc": "", "source": "Search"})
        except: pass
    return jobs


# =====================
# SOURCE 6: INDEED HTML SEARCH (falls back if RSS fails)
# =====================
def scrape_indeed_html():
    jobs = []
    queries = ["generative+AI+Entry+Level", "genai+fresher", "AI+Engineer+fresher"]
    for q in queries:
        soup = fetch(f"https://www.indeed.com/jobs?q={q}&l=India")
        if not soup: continue
        for card in soup.select("div.job_seen_beacon") or soup.select("div[class*=job-card]"):
            title_el = card.select_one("h2.jobTitle a") or card.select_one("a[class*=jobTitle]")
            comp_el = card.select_one("span.companyName")
            link_el = card.select_one("a[class*=jcs-JobTitle]")
            if title_el:
                title = title_el.text.strip()
                co = comp_el.text.strip() if comp_el else "Indeed"
                link = ""
                if link_el:
                    link = "https://www.indeed.com" + link_el.get("href", "")
                elif title_el.get("href"):
                    link = "https://www.indeed.com" + title_el.get("href", "")
                if relevant(title, ""):
                    jobs.append({"co": co, "role": title[:100], "url": link, "desc": "", "source": "Indeed"})
        time.sleep(2)
    return jobs


# =====================
# SOURCE 7: INTERNSHALA
# =====================
def scrape_internshala():
    jobs = []
    for path in ["genai-jobs", "artificial-intelligence-jobs", "machine-learning-jobs"]:
        soup = fetch(f"https://internshala.com/{path}/")
        if not soup: continue
        for card in soup.select("div.individual_internship") or soup.select("div.internship_meta"):
            links = card.select("a[href*='/job/']") or card.select("a[href*='/internship/']")
            title_el = links[0] if links else None
            comp_el = card.select_one("a[class*=company]") or card.select_one("p.company-name")
            if title_el:
                title = title_el.text.strip()
                co = comp_el.text.strip() if comp_el else "Internshala"
                link = title_el.get("href", "")
                if link and not link.startswith("http"):
                    link = "https://internshala.com" + link
                if relevant(title, ""):
                    jobs.append({"co": co, "role": title[:100], "url": link, "desc": "", "source": "Internshala"})
        time.sleep(1)
    return jobs


# =====================
# MASTER HUNTER
# =====================
def hunt_all():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting GenAI job hunt...")
    all_jobs = []
    sources = [
        ("Reddit", scrape_reddit),
        ("Company Careers", scrape_company_careers),
        ("Naukri", scrape_naukri),
        ("Indeed RSS", scrape_indeed_rss),
        ("Search", scrape_google_jobs),
        ("Indeed HTML", scrape_indeed_html),
        ("Internshala", scrape_internshala),
    ]
    for name, fn in sources:
        try:
            results = fn()[:25]  # Max 25 per source to prevent flooding
            print(f"  {name}: {len(results)} jobs")
            for j in results:
                j["source"] = name
            all_jobs.extend(results)
        except Exception as e:
            print(f"  {name}: ERROR - {e}")

    # Deduplicate
    seen = set()
    unique = []
    for j in all_jobs:
        j["id"] = jid(j.get("co","?"), j.get("role","?"))
        if j["id"] not in seen:
            seen.add(j["id"])
            j["date"] = datetime.now().isoformat()
            unique.append(j)

    print(f"\n  Total unique: {len(unique)}")
    return unique


if __name__ == "__main__":
    jobs = hunt_all()
    # Print results
    for j in jobs:
        print(f"  [{j['source']:15}] {j['role'][:55]}")
        print(f"  {'':18}{j['co']}")

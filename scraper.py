# GenAI Job Hunter — Parallel Scraper with 200+ Sources
# Each source is a unique website URL. Scraped in parallel with short timeouts.

import requests
from bs4 import BeautifulSoup
import json, os, time, hashlib, re, threading
from datetime import datetime
from urllib.parse import quote, urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
urllib3.disable_warnings()

KEYWORDS = [
    "generative ai","genai","llm","large language model","rag",
    "retrieval augmented","agentic ai","langchain","prompt engineer",
    "foundation model","ai engineer","ai developer","nlp engineer",
    "deep learning","ai fresher","ai intern","hugging face",
    "fine tuning","vector database","ai/ml","chatbot","ai enabler",
    "artificial intelligence","machine learning","neural network",
    "transformer","gpt","bert","t5","diffusion","embedding"
]
EXCLUDE = [
    "senior","lead","principal","staff","manager","director",
    "head of","architect","vp","vice president","15+","10+",
    "7+ years","5+ years","experienced","san francisco",
    "remote - us","united states","austin","chicago","boston"
]
INCLUDE_LEVEL = [
    "intern","fresher","entry level","entry-level","new grad","new graduate",
    "junior","associate","apprentice","trainee","0-1","0-2","graduate",
    "early career","early-career","0-3","fresher"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125.0.0.0",
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

def relevant(title, desc=""):
    text = f"{title} {desc[:500]}".lower()
    for ex in EXCLUDE:
        if ex in text:
            return False
    score = sum(1 for kw in KEYWORDS if kw.lower() in text)
    return score >= 1

def fetch_text_fast(url, timeout=8):
    try:
        r = requests.get(url, headers=get_headers(), verify=False, timeout=timeout)
        r.raise_for_status()
        return r.text
    except:
        return None


# =============================================================
# SOURCE HANDLERS
# =============================================================

def handler_generic_careers(url, name):
    """Scrape any company career page for job links"""
    html = fetch_text_fast(url)
    if not html: return []
    soup = BeautifulSoup(html, "html5lib")
    jobs = []
    seen_titles = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        title = a.get_text().strip()
        if not title or len(title) < 10: continue
        job_indicators = ["job","career","position","opening","role","opportunity","apply","hiring"]
        if not any(x in href.lower() for x in job_indicators):
            if not any(x in title.lower() for x in job_indicators):
                continue
        if any(x in href.lower() for x in ["login","sign","register","#","javascript"]): continue
        t_clean = re.sub(r'\s+', ' ', title).strip()[:100]
        if t_clean in seen_titles: continue
        seen_titles.add(t_clean)
        if relevant(title):
            if not href.startswith("http"):
                href = urljoin(url, href)
            jobs.append({"co": name, "role": t_clean, "url": href, "desc": "", "source": name})
    return jobs[:15]

def handler_linkedin(query, source_name):
    """Scrape LinkedIn job search"""
    url = f"https://www.linkedin.com/jobs/search/?keywords={quote(query)}&location=India&f_E=1%2C2"
    html = fetch_text_fast(url)
    if not html: return []
    soup = BeautifulSoup(html, "html5lib")
    jobs = []
    seen = set()
    for card in soup.select("div[class*=job-card]") or soup.select("li[class*=job]") or soup.select("a[class*=job-card]"):
        title_el = card.select_one("a[class*=title]") or card.select_one("a[class*=jobTitle]") or card.select_one("h3 a")
        comp_el = card.select_one("span[class*=company]") or card.select_one("a[class*=company]")
        if title_el:
            title = title_el.get_text().strip()
            if title in seen: continue
            seen.add(title)
            co = comp_el.get_text().strip() if comp_el else "LinkedIn"
            link = title_el.get("href", "")
            if link and not link.startswith("http"):
                link = "https://www.linkedin.com" + link
            if relevant(title):
                jobs.append({"co": co, "role": title[:100], "url": link, "desc": "", "source": source_name})
    return jobs[:10]

def handler_indeed(query, domain, country, source_name):
    """Scrape Indeed job search"""
    url = f"https://{domain}/jobs?q={quote(query)}&l={country}"
    html = fetch_text_fast(url)
    if not html: return []
    soup = BeautifulSoup(html, "html5lib")
    jobs = []
    seen = set()
    for card in soup.select("div.job_seen_beacon") or soup.select("div[class*=job-card]") or soup.select("li[class*=job]"):
        title_el = card.select_one("h2.jobTitle a") or card.select_one("a[class*=jobTitle]") or card.select_one("a[class*=title]")
        comp_el = card.select_one("span.companyName") or card.select_one("span[class*=company]")
        if title_el:
            title = title_el.get_text().strip()
            if title in seen: continue
            seen.add(title)
            co = comp_el.get_text().strip() if comp_el else "Indeed"
            link = ""
            if title_el.get("href"):
                link = "https://" + domain + title_el.get("href", "")
            if relevant(title):
                jobs.append({"co": co, "role": title[:100], "url": link, "desc": "", "source": source_name})
    return jobs[:10]

def handler_search_engine(query, engine_url, source_name):
    """Scrape search engine results for job listings"""
    url = engine_url.format(q=quote(query))
    html = fetch_text_fast(url)
    if not html: return []
    soup = BeautifulSoup(html, "html5lib")
    jobs = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        title = a.get_text().strip()
        if not title or len(title) < 15: continue
        if "uddg=" in href:
            parsed = urlparse(href)
            qs = parse_qs(parsed.query)
            if "uddg" in qs: href = qs["uddg"][0]
        t_clean = re.sub(r'\s+', ' ', title).strip()[:100]
        if t_clean in seen: continue
        seen.add(t_clean)
        if not any(x in title.lower() for x in ["job","hiring","opening","position","career","vacancy"]):
            continue
        if relevant(title):
            jobs.append({"co": "Unknown", "role": t_clean, "url": href, "desc": "", "source": source_name})
    return jobs[:8]

def handler_reddit(subreddit, source_name):
    """Scrape Reddit for job posts"""
    url = f"https://www.reddit.com/r/{subreddit}/search.json?q=generative+AI+OR+genai+OR+LLM+OR+hiring+OR+job&restrict_sr=on&sort=new&t=week&limit=25"
    try:
        r = requests.get(url, headers={"User-Agent": "GenAIJobHunter/1.0"}, timeout=8)
        if r.status_code != 200: return []
        data = r.json()
        jobs = []
        for post in data.get("data", {}).get("children", []):
            p = post.get("data", {})
            title = p.get("title", "")
            text = p.get("selftext", "") or ""
            permalink = f"https://www.reddit.com{p.get('permalink', '')}"
            if relevant(title, text):
                tags = p.get("link_flair_text", "") or ""
                if any(t in title.lower() or t in tags.lower() for t in ["hiring","job","opening","offer","position"]):
                    jobs.append({"co": f"Reddit/r/{subreddit}", "role": title[:100], "url": permalink, "desc": text[:300], "source": source_name})
        return jobs[:5]
    except:
        return []

def handler_naukri(query, source_name):
    url = f"https://www.naukri.com/{query}-in-india?k={query.replace('-','+')}"
    html = fetch_text_fast(url)
    if not html: return []
    soup = BeautifulSoup(html, "html5lib")
    jobs = []
    seen = set()
    for card in soup.select("article.jobTuple") or soup.select("div.job-card") or soup.select("div[class*=list]") or soup.select("li[class*=job]"):
        title_el = card.select_one("a.title") or card.select_one("a[class*=title]") or card.select_one("a[class*=jobTitle]")
        comp_el = card.select_one("a.subTitle") or card.select_one("a[class*=comp-name]") or card.select_one("span[class*=comp]")
        if title_el:
            title = title_el.get_text().strip()
            if title in seen: continue
            seen.add(title)
            co = comp_el.get_text().strip() if comp_el else "Naukri"
            link = title_el.get("href", "")
            if link and not link.startswith("http"): link = "https://www.naukri.com" + link
            if relevant(title):
                jobs.append({"co": co, "role": title[:100], "url": link, "desc": "", "source": source_name})
    return jobs[:10]

def handler_internshala(path, source_name):
    url = f"https://internshala.com/{path}/"
    html = fetch_text_fast(url)
    if not html: return []
    soup = BeautifulSoup(html, "html5lib")
    jobs = []
    seen = set()
    for card in soup.select("div.individual_internship") or soup.select("div.internship_meta") or soup.select("div[class*=internship]") or soup.select("div[class*=card]"):
        links = card.select("a[href*='/job/']") or card.select("a[href*='/internship/']")
        title_el = links[0] if links else None
        comp_el = card.select_one("a[class*=company]") or card.select_one("p.company-name")
        if title_el:
            title = title_el.get_text().strip()
            if title in seen: continue
            seen.add(title)
            co = comp_el.get_text().strip() if comp_el else "Internshala"
            link = title_el.get("href", "")
            if link and not link.startswith("http"): link = "https://internshala.com" + link
            if relevant(title):
                jobs.append({"co": co, "role": title[:100], "url": link, "desc": "", "source": source_name})
    return jobs[:10]


# =============================================================
# 200+ SOURCES LIST
# Fields: (source_name, handler_function, handler_arg)
# Each source = one unique website/URL being queried
# =============================================================

SOURCES = []

# --- 30 COMPANY CAREER PAGES ---
CAREER_PAGES = [
    ("Google AI", "https://careers.google.com/jobs/results/?q=generative+AI"),
    ("Microsoft AI", "https://jobs.careers.microsoft.com/global/en/search?q=generative%20AI"),
    ("Meta AI", "https://www.metacareers.com/jobs/?q=generative%20AI"),
    ("Amazon AI India", "https://www.amazon.jobs/en/search?base_query=generative+AI&loc_query=India"),
    ("NVIDIA AI", "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/jobs?q=generative+AI"),
    ("Apple AI", "https://jobs.apple.com/en-us/search?search=generative%20AI"),
    ("IBM AI", "https://www.ibm.com/careers/search/?q=generative%20AI"),
    ("Intel AI", "https://jobs.intel.com/search?q=generative+AI"),
    ("Salesforce AI", "https://careers.salesforce.com/en/jobs/?q=generative+AI"),
    ("Adobe AI", "https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/jobs?q=generative+AI"),
    ("Cisco AI", "https://jobs.cisco.com/jobs/search?q=generative+AI"),
    ("Oracle AI", "https://eeho.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/search?keyword=generative+AI"),
    ("Uber AI", "https://www.uber.com/us/en/careers/list/?q=generative+AI"),
    ("Qualcomm AI", "https://qualcomm.wd5.myworkdayjobs.com/en-US/External/jobs?q=generative+AI"),
    ("AMD AI", "https://careers.amd.com/search?q=generative+AI"),
    ("Dell AI", "https://jobs.dell.com/search?q=generative+AI"),
    ("HP AI", "https://jobs.hp.com/search?q=generative+AI"),
    ("Samsung India", "https://www.samsung.com/in/careers/search/?q=ai"),
    ("Siemens India", "https://jobs.siemens.com/search?q=ai+fresher&location=india"),
    ("Bosch India", "https://www.bosch.in/careers/search/?q=ai"),
    ("TCS AI", "https://careers.tcs.com/search?q=ai+fresher"),
    ("Infosys AI", "https://career.infosys.com/joblist?q=ai+fresher"),
    ("Wipro AI", "https://careers.wipro.com/search?q=ai+fresher"),
    ("Accenture AI", "https://www.accenture.com/in-en/careers/jobsearch?q=generative+ai+fresher"),
    ("Cognizant AI", "https://careers.cognizant.com/search?q=generative+AI+fresher"),
    ("Capgemini AI", "https://www.capgemini.com/careers/job-results/?keywords=generative+AI+fresher"),
    ("HCL AI", "https://www.hcltech.com/careers/search?q=AI+fresher"),
    ("TechM AI", "https://careers.techmahindra.com/search?q=AI+fresher"),
    ("Persistent AI", "https://careers.persistent.com/search?q=generative+ai+fresher"),
    ("Flipkart AI", "https://www.flipkartcareers.com/search?q=AI+fresher"),
]
for name, url in CAREER_PAGES:
    SOURCES.append((name, handler_generic_careers, url))

# --- 30 MORE INDIAN COMPANY CAREER PAGES ---
INDIAN_CAREERS = [
    ("Swiggy AI", "https://careers.swiggy.com/search?q=AI+fresher"),
    ("Zomato AI", "https://www.zomato.com/careers?q=AI"),
    ("Paytm AI", "https://paytm.careers/?q=AI"),
    ("Razorpay AI", "https://razorpay.com/careers/?q=AI"),
    ("PhonePe AI", "https://careers.phonepe.com/search?q=AI"),
    ("Groww AI", "https://groww.in/careers?q=AI"),
    ("Zerodha AI", "https://zerodha.com/careers?q=AI"),
    ("Nykaa AI", "https://careers.nykaa.com/search?q=AI"),
    ("Meesho AI", "https://careers.meesho.com/search?q=AI"),
    ("ShareChat AI", "https://careers.sharechat.com/search?q=AI"),
    ("Zoho AI", "https://careers.zoho.com/search?q=ai+fresher"),
    ("Freshworks AI", "https://careers.freshworks.com/search?q=ai+fresher"),
    ("Postman AI", "https://www.postman.com/company/careers/?q=ai"),
    ("BrowserStack AI", "https://www.browserstack.com/careers?q=ai"),
    ("Chargebee AI", "https://www.chargebee.com/careers/?q=ai"),
    ("LTI Mindtree", "https://careers.ltimindtree.com/search?q=ai+fresher"),
    ("Mphasis AI", "https://careers.mphasis.com/search?q=ai"),
    ("Coforge AI", "https://careers.coforge.com/search?q=ai"),
    ("KPIT AI", "https://careers.kpit.com/search?q=ai"),
    ("L&T Tech AI", "https://careers.lnttechservices.com/search?q=ai"),
    ("Tata Elxsi", "https://careers.tataelxsi.com/search?q=ai"),
    ("OpenText AI", "https://careers.opentext.com/search?q=ai"),
    ("SAP Labs India", "https://www.sap.com/careers/search.html?q=ai&location=india"),
    ("VMware AI", "https://careers.vmware.com/search?q=ai"),
    ("Red Hat AI", "https://www.redhat.com/en/jobs/search?q=ai"),
    ("Databricks AI", "https://www.databricks.com/company/careers/search?q=ai"),
    ("Snowflake AI", "https://careers.snowflake.com/search?q=ai"),
    ("ServiceNow AI", "https://careers.servicenow.com/search?q=ai"),
    ("HubSpot AI", "https://www.hubspot.com/careers/search?q=ai"),
    ("Atlassian AI", "https://www.atlassian.com/company/careers/search?q=ai"),
]
for name, url in INDIAN_CAREERS:
    SOURCES.append((name, handler_generic_careers, url))

# --- 40 MORE COMPANY CAREER PAGES ---
MORE_CAREERS = [
    ("Splunk AI", "https://careers.splunk.com/search?q=ai"),
    ("Datadog AI", "https://www.datadoghq.com/careers/search/?q=ai"),
    ("NetApp AI", "https://careers.netapp.com/search?q=ai"),
    ("Nutanix AI", "https://www.nutanix.com/company/careers/search?q=ai"),
    ("Cloudflare AI", "https://www.cloudflare.com/careers/search/?q=ai"),
    ("MongoDB AI", "https://www.mongodb.com/careers/search?q=ai"),
    ("Elastic AI", "https://www.elastic.co/about/careers/search?q=ai"),
    ("Confluent AI", "https://www.confluent.io/careers/search/?q=ai"),
    ("HashiCorp AI", "https://www.hashicorp.com/careers/search?q=ai"),
    ("GitLab AI", "https://about.gitlab.com/jobs/search/?q=ai"),
    ("Goldman Sachs", "https://www.goldmansachs.com/careers/search?q=ai+india"),
    ("JPMC India", "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/search?keyword=ai&location=India"),
    ("Morgan Stanley", "https://www.morganstanley.com/careers/search?q=ai+india"),
    ("Barclays India", "https://barclays.wd3.myworkdayjobs.com/en-US/Barclays_External_Careers/jobs?q=ai&locationCountry=India"),
    ("Deutsche Bank", "https://careers.db.com/search?q=ai+india"),
    ("HSBC India", "https://www.hsbc.com/careers/search?q=ai+india"),
    ("Amex India", "https://www.americanexpress.com/en-us/careers/search/?q=ai+india"),
    ("Mastercard AI", "https://mastercard.wd1.myworkdayjobs.com/en-US/CorporateCareers/jobs?q=ai&locationCountry=India"),
    ("Visa India", "https://visa.wd1.myworkdayjobs.com/en-US/ExternalVisaCareerSite/jobs?q=ai&locationCountry=India"),
    ("PayPal India", "https://paypal.eightfold.ai/careers?query=ai&location=india"),
    ("Stripe India", "https://stripe.com/jobs/search?q=ai&location=india"),
    ("ICICI Bank", "https://www.icicicareers.com/search?q=ai"),
    ("HDFC Bank", "https://careers.hdfcbank.com/search?q=ai"),
    ("Axis Bank", "https://www.axisbank.com/careers/search?q=ai"),
    ("Bajaj Finserv", "https://www.bajajfinserv.in/careers/search?q=ai"),
    ("Reliance Jio", "https://careers.jio.com/search?q=ai"),
    ("Airtel India", "https://www.airtel.in/careers/search?q=ai"),
    ("Adani Group", "https://www.adani.com/careers/search?q=ai"),
    ("Mahindra AI", "https://www.mahindra.com/careers/search?q=ai"),
    ("Maruti Suzuki", "https://www.marutisuzuki.com/careers/search?q=ai"),
    ("Tata Motors", "https://www.tatamotors.com/careers/search?q=ai"),
    ("Honeywell India", "https://careers.honeywell.com/search?q=ai&location=India"),
    ("Schneider India", "https://www.se.com/in/en/about-us/careers/search/?q=ai"),
    ("ABB India", "https://careers.abb/search?q=ai&location=in"),
    ("Philips India", "https://www.careers.philips.com/search?q=ai&location=india"),
    ("GE India", "https://www.ge.com/careers/search?q=ai&location=india"),
    ("GE HealthCare", "https://careers.gehealthcare.com/search?q=ai&location=india"),
    ("3M India", "https://www.3mindia.in/careers/search?q=ai"),
    ("Caterpillar India", "https://www.caterpillar.com/en/careers/search.html?q=ai+india"),
    ("John Deere India", "https://www.deere.com/en/careers/search/?q=ai+india"),
]
for name, url in MORE_CAREERS:
    SOURCES.append((name, handler_generic_careers, url))

# --- 20 JOB BOARDS (multiple queries each) ---
JOBBOARD_NAUKRI = [
    "generative-ai-jobs", "genai-jobs", "llm-engineer-jobs",
    "ai-engineer-fresher-jobs", "machine-learning-engineer-jobs",
    "deep-learning-jobs", "nlp-engineer-jobs", "prompt-engineer-jobs",
    "rag-engineer-jobs", "agentic-ai-jobs", "ai-developer-jobs",
    "artificial-intelligence-jobs", "data-scientist-jobs",
    "chatbot-developer-jobs", "computer-vision-jobs",
    "ai-ml-engineer-jobs", "python-ai-jobs", "langchain-jobs",
    "generative-ai-fresher", "ai-research-jobs",
]
for q in JOBBOARD_NAUKRI:
    SOURCES.append((f"Naukri-{q[:20]}", handler_naukri, q))

INTERNSHALA_PATHS = [
    "genai-jobs", "artificial-intelligence-jobs", "machine-learning-jobs",
    "deep-learning-jobs", "data-science-jobs", "nlp-jobs",
    "python-jobs", "research-jobs", "tech-jobs",
    "software-engineering-jobs", "ai-engineer-jobs",
    "computer-science-jobs", "data-analyst-jobs",
    "ml-engineer-jobs", "llm-jobs",
]
for p in INTERNSHALA_PATHS:
    SOURCES.append((f"Internshala-{p[:20]}", handler_internshala, p))

# --- INDEED (10 country domains × 3 queries = 30 sources) ---
INDEED_DOMAINS = [
    ("in.indeed.com", "India"), ("www.indeed.com", "India"),
    ("uk.indeed.com", "UK"), ("ca.indeed.com", "Canada"),
    ("au.indeed.com", "Australia"), ("de.indeed.com", "Germany"),
    ("fr.indeed.com", "France"), ("sg.indeed.com", "Singapore"),
    ("ae.indeed.com", "UAE"), ("nz.indeed.com", "New Zealand"),
]
INDEED_QUERIES = ["generative+AI+fresher", "genai+engineer", "AI+Engineer+fresher", "LLM+fresher", "machine+learning+fresher"]
for domain, country in INDEED_DOMAINS:
    for q in INDEED_QUERIES[:3]:
        SOURCES.append((f"Indeed-{country[:3]}-{q[:15]}", handler_indeed, (q, domain, country)))

# --- LINKEDIN (15 queries = 15 sources) ---
LINKEDIN_QUERIES = [
    "generative+AI+India", "genai+fresher+India", "LLM+Engineer+India",
    "AI+Engineer+Entry+Level+India", "machine+learning+fresher+India",
    "deep+learning+fresher+India", "NLP+Engineer+India",
    "LangChain+fresher+India", "prompt+engineer+India",
    "agentic+AI+India", "RAG+engineer+India", "AI+intern+India",
    "artificial+intelligence+fresher", "AI+developer+fresher+Pune",
    "data+scientist+entry+level+India",
]
for q in LINKEDIN_QUERIES:
    SOURCES.append((f"LinkedIn-{q[:20]}", handler_linkedin, (q, f"LinkedIn-{q[:15]}")))

# --- DUCKDUCKGO SEARCH (15 queries = 15 sources) ---
DDG_QUERIES = [
    "generative AI fresher India 2026 job",
    "genai engineer entry level India hiring",
    "LLM engineer fresher India job opening",
    "AI engineer fresher Pune job",
    "agentic AI fresher job India 2026",
    "RAG engineer fresher hiring India",
    "LangChain developer fresher job",
    "prompt engineer fresher India",
    "NLP engineer entry level India",
    "generative AI internship India 2026",
    "AI ML fresher job India",
    "deep learning fresher job India",
    "machine learning fresher hiring India",
    "AI developer fresher Bangalore",
    "genai job fresher remote India",
]
DDG_URL = "https://html.duckduckgo.com/html/?q={q}"
for q in DDG_QUERIES:
    SOURCES.append((f"DDG-{q[:20]}", handler_search_engine, (q, DDG_URL, "DDG-Search")))

# --- BING SEARCH (10 queries = 10 sources) ---
BING_QUERIES = [
    "generative AI fresher India job 2026",
    "genai engineer fresher hiring India",
    "LLM engineer entry level job India",
    "AI fresher job Pune 2026",
    "agentic AI job fresher India",
    "LangChain developer fresher India",
    "prompt engineer job fresher India",
    "RAG engineer fresher hiring",
    "AI ML engineer fresher India",
    "generative AI internship 2026 India",
]
BING_URL = "https://www.bing.com/search?q={q}+job+hiring"
for q in BING_QUERIES:
    SOURCES.append((f"Bing-{q[:20]}", handler_search_engine, (q, BING_URL, "Bing-Search")))

# --- YAHOO SEARCH (10 queries = 10 sources) ---
YAHOO_QUERIES = [
    "generative AI fresher India job",
    "genai engineer fresher hiring",
    "LLM entry level job India",
    "AI engineer fresher Pune 2026",
    "agentic AI fresher job",
    "machine learning fresher India",
    "deep learning entry level India",
    "LangChain developer fresher",
    "AI intern India 2026",
    "genai fresher job Bangalore",
]
YAHOO_URL = "https://search.yahoo.com/search?p={q}+job"
for q in YAHOO_QUERIES:
    SOURCES.append((f"Yahoo-{q[:20]}", handler_search_engine, (q, YAHOO_URL, "Yahoo-Search")))

# --- REDDIT (15 subreddits = 15 sources) ---
SUBREDDITS = [
    "jobs", "cscareerquestions", "developersIndia",
    "genai", "machinelearningjobs", "artificial",
    "datascience", "forhire", "Indian_Academia",
    "learnmachinelearning", "PythonJobs", "AIJobs",
    "deeplearning", "Jobopenings", "freshers",
]
for sub in SUBREDDITS:
    SOURCES.append((f"Reddit-{sub}", handler_reddit, sub))

# --- ADDITIONAL JOB BOARD URLS ---
EXTRA_JOB_BOARDS = [
    ("TimesJobs-GenAI", "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&txtKeywords=generative+ai&txtLocation=India"),
    ("TimesJobs-AI", "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&txtKeywords=ai+engineer&txtLocation=India"),
    ("TimesJobs-ML", "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&txtKeywords=machine+learning&txtLocation=India"),
    ("TimesJobs-LLM", "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&txtKeywords=llm+engineer&txtLocation=India"),
    ("Foundit-GenAI", "https://www.foundit.in/search/?q=generative+ai&loc=India"),
    ("Foundit-ML", "https://www.foundit.in/search/?q=machine+learning&loc=India"),
    ("Foundit-AI", "https://www.foundit.in/search/?q=artificial+intelligence&loc=India"),
    ("Shine-GenAI", "https://www.shine.com/job-search/generative-ai-jobs-in-india"),
    ("Shine-AI", "https://www.shine.com/job-search/ai-engineer-jobs-in-india"),
    ("Shine-ML", "https://www.shine.com/job-search/machine-learning-jobs-in-india"),
    ("Freshersworld-AI", "https://www.freshersworld.com/jobs/ai-engineer-jobs-in-india"),
    ("Freshersworld-ML", "https://www.freshersworld.com/jobs/machine-learning-jobs-in-india"),
    ("Monster-GenAI", "https://www.monsterindia.com/search/generative-ai-jobs-in-india"),
    ("Monster-AI", "https://www.monsterindia.com/search/artificial-intelligence-jobs-in-india"),
    ("Hirist-AI", "https://www.hirist.com/search/?q=ai+fresher"),
    ("Hirist-ML", "https://www.hirist.com/search/?q=machine+learning+fresher"),
    ("Upwork-AI", "https://www.upwork.com/search/jobs/?q=generative+AI"),
    ("Freelancer-AI", "https://www.freelancer.com/jobs/artificial-intelligence/"),
    ("Glassdoor-AI", "https://www.glassdoor.co.in/Job/india-generative-ai-jobs-SRCH_IL.0,5_IN115_KO6,20.htm"),
    ("Learn4Good-AI", "https://www.learn4good.com/jobs/india/artificial-intelligence/"),
]
for name, url in EXTRA_JOB_BOARDS:
    SOURCES.append((name, handler_generic_careers, url))


# =============================================================
# PARALLEL HUNTER
# =============================================================

# Shared progress state (thread-safe via dict + threading.Lock)
progress = {"current": "", "done": 0, "total": len(SOURCES), "hits": 0, "errors": 0, "running": False}
progress_lock = threading.Lock()

def hunt_all():
    global progress
    with progress_lock:
        progress["running"] = True
        progress["done"] = 0
        progress["hits"] = 0
        progress["errors"] = 0

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting parallel hunt with {len(SOURCES)} sources...")

    all_jobs = []
    all_jobs_lock = threading.Lock()

    def scrape_one(item):
        name, handler, arg = item
        with progress_lock:
            progress["current"] = name
        try:
            if isinstance(arg, tuple):
                result = handler(*arg)
            else:
                result = handler(arg, name)
            if result:
                with all_jobs_lock:
                    for j in result:
                        j["source"] = name
                        j["date"] = datetime.now().isoformat()
                        j["id"] = jid(j.get("co","?"), j.get("role","?"))
                        all_jobs.append(j)
                with progress_lock:
                    progress["hits"] += 1
            return len(result)
        except Exception as e:
            with progress_lock:
                progress["errors"] += 1
            return 0
        finally:
            with progress_lock:
                progress["done"] += 1

    # Run in parallel with up to 10 workers
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scrape_one, item) for item in SOURCES]
        for future in as_completed(futures):
            pass  # results collected in scrape_one

    # Deduplicate
    seen = set()
    unique = []
    for j in all_jobs:
        if j["id"] not in seen:
            seen.add(j["id"])
            unique.append(j)

    with progress_lock:
        progress["running"] = False
        progress["current"] = ""

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Hunt complete: {len(unique)} unique jobs from {len(all_jobs)} raw, {len(SOURCES)} sources")
    return unique


def get_progress():
    with progress_lock:
        return dict(progress)


if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"  GenAI Job Hunter — {len(SOURCES)} Sources (Parallel)")
    print(f"{'='*60}\n")
    jobs = hunt_all()
    print(f"\n{'='*60}")
    print(f"  Results: {len(jobs)} unique jobs found")
    print(f"{'='*60}\n")
    for j in jobs[:30]:
        print(f"  [{j.get('source','?')[:20]:20}] {j['role'][:55]}")
        print(f"  {'':22}{j.get('co','?')}")
    if len(jobs) > 30:
        print(f"  ... and {len(jobs)-30} more")

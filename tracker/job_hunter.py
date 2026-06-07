"""
GenAI Job Hunter v5 — Multi-strategy job finder 
Strategies: RSS feeds, Google Alerts, direct URL fetch, manual import
"""

import json, os, time, hashlib, subprocess
from datetime import datetime
from plyer import notification
import urllib.request, urllib.error
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE, "job_history.json")
FRESH_FILE = os.path.join(BASE, "fresh_jobs.json")
ALL_FILE = os.path.join(BASE, "all_jobs.json")

KEYWORDS = [
    "generative AI", "genai", "LLM", "large language model",
    "prompt engineer", "RAG", "agentic AI", "LangChain",
    "AI engineer", "AI developer", "NLP", "deep learning",
    "AI fresher", "AI intern", "Hugging Face", "fine tuning",
    "foundation model", "vector database", "AI/ML", "chatbot", "AI enabler"
]
EXCLUDE = [
    "senior", "lead", "principal", "staff", "manager", "director",
    "head of", "architect", "vp ", "vice president", "15+", "10+",
    "7+ years", "5+ years", "experienced"
]

def jid(co, role):
    return hashlib.md5(f"{co}|{role}".lower().strip().encode()).hexdigest()

def relevant(title, desc=""):
    text = f"{title} {desc[:500]}".lower()
    for ex in EXCLUDE:
        if ex in text: return False
    score = sum(1 for kw in KEYWORDS if kw.lower() in text)
    return score >= 1

def http_get(url, timeout=15):
    """Fetch a URL with browser-like headers using urllib"""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except: return None

class JobHunter:
    def __init__(self):
        self.history = self.load_history()
        self.fresh = []
        self.all_jobs = []

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE) as f: return set(json.load(f))
        return set()

    def save_history(self):
        with open(HISTORY_FILE, "w") as f:
            json.dump(list(self.history), f)

    def add_job(self, co, role, url, desc, source):
        j = {"id": jid(co, role), "co": co, "role": role, "url": url, "desc": desc[:300], "from": source, "date": datetime.now().isoformat()}
        self.all_jobs.append(j)
        if j["id"] not in self.history:
            self.fresh.append(j)
            self.history.add(j["id"])

    def parse_rss(self, rss_text, source, co_extract=True):
        """Parse RSS/XML feed for job items"""
        if not rss_text: return
        try:
            root = ET.fromstring(rss_text)
            # Handle RSS 2.0
            for item in root.findall(".//channel/item") or root.findall(".//item"):
                t = item.findtext("title", "")
                d = item.findtext("description", "")
                l = item.findtext("link", "")
                co = item.findtext("source", source) if co_extract else source
                if t:
                    role = t.replace("Job: ", "").replace("job: ", "").strip()
                    if co == source and " - " in role:
                        parts = role.rsplit(" - ", 1)
                        role = parts[0].strip()
                        co = parts[1].strip()
                    if relevant(role, d):
                        self.add_job(co, role, l, d, source)

        except ET.ParseError:
            pass

    # === STRATEGY 1: Indeed RSS ===
    def hunt_indeed(self):
        for q in ["generative+AI+fresher+India", "genai+engineer+India",
                   "LLM+fresher+India", "AI+fresher+Pune", "artificial+intelligence+fresher+India"]:
            for domain in ["https://in.indeed.com", "https://www.indeed.com"]:
                text = http_get(f"{domain}/rss?q={q}")
                if text:
                    self.parse_rss(text, "Indeed")
                    if self.fresh: return

    # === STRATEGY 2: LinkedIn RSS ===
    def hunt_linkedin(self):
        for kw in ["Generative+AI+Fresher+India", "GenAI+Engineer+India",
                    "LLM+Entry+Level+India", "AI+Engineer+Fresher+India"]:
            text = http_get(f"https://www.linkedin.com/jobs/rss?keywords={kw}&location=India")
            if text:
                self.parse_rss(text, "LinkedIn")
                if self.fresh: return

    # === STRATEGY 3: Google Alerts RSS for GenAI jobs ===
    def hunt_google_alerts(self):
        # Google Alerts monitor job search terms
        alerts = [
            ('"generative AI" "fresher" "India"', "generative AI fresher India"),
            ('"genai" engineer "entry level" India', "genai entry level"),
            ('"AI engineer" fresher "Pune"', "AI engineer fresher Pune"),
            ('"LLM" engineer "fresher" India', "LLM fresher India"),
        ]
        for query, label in alerts:
            from urllib.parse import quote
            url = f"https://www.google.com/alerts/feeds/01234567890123456789/{hashlib.md5(query.encode()).hexdigest()}"
            # Google Alerts RSS require a feed ID, so fallback to Google Search RSS
            text = http_get(f"https://www.google.com/search?q={quote(query)}&hl=en&num=15")
            if text:
                # Extract job links and titles from HTML
                import re
                # Look for LinkedIn job posts
                for m in re.finditer(r'<a href="(https?://[^"]*linkedin[^"]*)"[^>]*>(.*?)</a>', text, re.IGNORECASE):
                    url = m.group(1).replace("&amp;", "&") if "&amp;" in m.group(1) else m.group(1)
                    title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
                    if title and relevant(title, ""):
                        self.add_job("LinkedIn", title[:100], url, "", f"GoogleAlert:{label}")
                # Naukri
                for m in re.finditer(r'<a href="(https?://[^"]*naukri[^"]*)"[^>]*>(.*?)</a>', text, re.IGNORECASE):
                    url = m.group(1).replace("&amp;", "&")
                    title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
                    if title and relevant(title, ""):
                        self.add_job("Naukri", title[:100], url, "", f"GoogleAlert:{label}")
                # General job postings
                for m in re.finditer(r'<div[^>]*class="[^"]*(?:v5yQqb|BNeawe)[^"]*"[^>]*>(.*?)</div>', text):
                    content = m.group(1)
                    title_m = re.search(r'(?:^|\.)\s*(Hiring|Job|Opening)[^:]*:?\s*([A-Z][^.]{10,120})', content)
                    if title_m:
                        title = title_m.group(0).strip()[:100]
                        if relevant(title, ""):
                            self.add_job("Jobs", title[:100], "", "", f"GoogleAlert:{label}")

    # === STRATEGY 4: Curl-based scraping of job aggregator pages ===
    def hunt_aggregators(self):
        urls = [
            ("https://www.freshersworld.com/jobs/artificial-intelligence-jobs", "FreshersWorld"),
            ("https://www.freshersworld.com/jobs/machine-learning-jobs", "FreshersWorld"),
        ]
        for url, source in urls:
            try:
                result = subprocess.run(
                    ["curl", "-s", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                     "-L", "--max-time", "15", url],
                    capture_output=True, text=True, timeout=20
                )
                html = result.stdout
                if not html or "captcha" in html.lower() or "security" in html.lower():
                    continue
                import re
                # Extract job card titles
                for m in re.finditer(r'<a[^>]*class="[^"]*(?:job-title|jobTitle|title)[^"]*"[^>]*>([^<]+)</a>', html, re.IGNORECASE):
                    title = m.group(1).strip()
                    if title and relevant(title, ""):
                        self.add_job(source, title[:100], url, "", source)
                for m in re.finditer(r'<h3[^>]*>([^<]+(?:Engineer|AI|ML|GenAI|LLM)[^<]{5,100})</h3>', html, re.IGNORECASE):
                    title = m.group(1).strip()
                    if relevant(title, ""):
                        self.add_job(source, title[:100], url, "", source)
            except: pass

    def hunt_all(self):
        strategies = [
            ("Indeed RSS", self.hunt_indeed),
            ("LinkedIn RSS", self.hunt_linkedin),
            ("Google Alerts", self.hunt_google_alerts),
            ("Job Aggregators", self.hunt_aggregators),
        ]
        total_new = 0
        for name, fn in strategies:
            try:
                fn()
                new = len(self.fresh) - total_new
                total_new = len(self.fresh)
                if new > 0:
                    print(f"  {name}: {new} new jobs")
            except Exception as e:
                print(f"  {name}: Error - {e}")

    def run(self):
        print("=" * 60)
        print("  GenAI JOB HUNTER v5")
        print("  Strategies: Indeed RSS, LinkedIn RSS, Google Alerts, Job Sites")
        print("=" * 60)

        self.hunt_all()

        # Deduplicate fresh
        seen = set()
        deduped = []
        for j in self.fresh:
            if j["id"] not in seen:
                seen.add(j["id"])
                deduped.append(j)
        self.fresh = deduped

        self.save_history()

        # Save files
        with open(FRESH_FILE, "w") as f:
            json.dump(self.fresh, f, indent=2)
        existing = []
        if os.path.exists(ALL_FILE):
            with open(ALL_FILE) as f: existing = json.load(f)
        seen = {j["id"] for j in existing}
        for j in self.all_jobs:
            if j["id"] not in seen:
                existing.append(j); seen.add(j["id"])
        with open(ALL_FILE, "w") as f:
            json.dump(existing, f, indent=2)

        print(f"\n  NEW jobs found: {len(self.fresh)}")
        if self.fresh:
            try:
                notification.notify(title="GenAI Job Hunter",
                    message=f"{len(self.fresh)} new jobs! Check tracker.", timeout=8)
            except: pass
            print(f"\n  {'='*50}")
            print(f"  {'LATEST MATCHES':^50}")
            print(f"  {'='*50}")
            for i, j in enumerate(self.fresh[:20], 1):
                role = j.get("role", "?")
                co = j.get("co", "?")
                src = j.get("from", "?")
                if len(role) > 55: role = role[:52] + "..."
                print(f"  {i:2}. [{src}] {role} @ {co}")
        else:
            print("  No new jobs since last check.\n")
            print("  Note: Many job sites block automated scraping.")
            print("  I will periodically search for new jobs and update your list!")
        print("=" * 60)

if __name__ == "__main__":
    hunter = JobHunter()
    hunter.run()

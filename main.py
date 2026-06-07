import json, os, hashlib, threading, time
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="GenAI Job Finder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = os.path.dirname(os.path.abspath(__file__))
JOBS_FILE = os.path.join(BASE, "jobs.json")
HISTORY_FILE = os.path.join(BASE, "history.json")
APPLIED_FILE = os.path.join(BASE, "applied.json")
SCHEDULE_FILE = os.path.join(BASE, "schedule.json")
TEMPLATE_FILE = os.path.join(BASE, "template.html")

cache = {"jobs": [], "last_updated": None, "running": False}
schedule_info = {"last_auto": None, "enabled": True, "hour": 2}


def load_jobs():
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE) as f:
            return json.load(f)
    return []

def save_jobs(jobs):
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []

def save_history(h):
    with open(HISTORY_FILE, "w") as f:
        json.dump(h, f)

def load_applied():
    if os.path.exists(APPLIED_FILE):
        with open(APPLIED_FILE) as f:
            return set(json.load(f))
    return set()

def save_applied(a):
    with open(APPLIED_FILE, "w") as f:
        json.dump(list(a), f)

def load_schedule():
    global schedule_info
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE) as f:
            s = json.load(f)
            schedule_info["last_auto"] = s.get("last_auto")
            schedule_info["enabled"] = s.get("enabled", True)
            schedule_info["hour"] = s.get("hour", 2)
    return schedule_info

def save_schedule():
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule_info, f)

def classify_role(role):
    r = (role or "").lower()
    if any(x in r for x in ["prompt engineer", "prompt"]):
        return "prompt-eng"
    if any(x in r for x in ["rag", "retrieval"]):
        return "rag"
    if any(x in r for x in ["agentic"]):
        return "agentic-ai"
    if any(x in r for x in ["genai", "generative ai", "generative"]):
        return "genai"
    if any(x in r for x in ["nlp", "natural language"]):
        return "nlp-eng"
    if any(x in r for x in ["machine learning", "ml engineer"]):
        return "ml-eng"
    if any(x in r for x in ["ai engineer", "ai developer", "ai/ml"]):
        return "ai-eng"
    if any(x in r for x in ["deep learning"]):
        return "deep-learning"
    if any(x in r for x in ["llm", "large language"]):
        return "llm"
    return "other"

def time_ago(iso_str):
    if not iso_str: return ""
    try:
        d = datetime.fromisoformat(iso_str)
    except:
        return iso_str[:10] if iso_str else ""
    diff = datetime.now() - d
    if diff.days > 30: return f"{diff.days//30}mo ago"
    if diff.days > 0: return f"{diff.days}d ago"
    if diff.seconds >= 3600: return f"{diff.seconds//3600}h ago"
    if diff.seconds >= 60: return f"{diff.seconds//60}m ago"
    return "just now"

def count_new_24h(jobs):
    cutoff = datetime.now() - timedelta(hours=24)
    return sum(1 for j in jobs if j.get("date") and _parse_iso(j["date"]) > cutoff)

def _parse_iso(s):
    try: return datetime.fromisoformat(s)
    except: return datetime.min


def load_template():
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>Template not found</h1></body></html>"

_TEMPLATE_CACHE = [None]

def generate_html(jobs, last_updated, is_running):
    if _TEMPLATE_CACHE[0] is None:
        _TEMPLATE_CACHE[0] = load_template()
    html = _TEMPLATE_CACHE[0]

    hr = schedule_info.get("hour", 2)
    schedule_str = f"~{hr}:00 AM daily" if schedule_info.get("enabled") else "Off"
    last_str = time_ago(last_updated) if last_updated else "Never"

    html = html.replace("__JOBS_JSON__", json.dumps(jobs))
    html = html.replace("__SOURCES_JSON__", json.dumps(sorted(set(j.get("source", "Unknown") for j in jobs))))
    html = html.replace("__LAST_UPDATED__", last_str)
    html = html.replace("__SCHEDULE_INFO__", schedule_str)
    html = html.replace("__NEW_24H__", str(count_new_24h(jobs)))
    html = html.replace("__GENAI_COUNT__", str(sum(1 for j in jobs if classify_role(j.get("role","")) == "genai")))
    html = html.replace("__COMPANY_COUNT__", str(len(set(j.get("co","") for j in jobs if j.get("co")))))
    return html


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    jobs = cache["jobs"] or load_jobs()
    return generate_html(jobs, cache["last_updated"] or "Never", cache["running"])

@app.get("/api/jobs")
def get_jobs(source: str = None, search: str = None, role: str = None, date_from: str = None, date_to: str = None, sort: str = "newest"):
    jobs = cache["jobs"] or load_jobs()
    if source:
        jobs = [j for j in jobs if j.get("source", "").lower() == source.lower()]
    if search:
        s = search.lower()
        jobs = [j for j in jobs if s in j.get("role","").lower() or s in j.get("co","").lower()]
    if role:
        jobs = [j for j in jobs if classify_role(j.get("role","")) == role.lower()]
    if date_from:
        try:
            df = datetime.fromisoformat(date_from)
            jobs = [j for j in jobs if j.get("date") and datetime.fromisoformat(j["date"]) >= df]
        except: pass
    if date_to:
        try:
            dt = datetime.fromisoformat(date_to)
            jobs = [j for j in jobs if j.get("date") and datetime.fromisoformat(j["date"]) <= dt]
        except: pass
    if sort == "oldest":
        jobs.sort(key=lambda j: j.get("date",""))
    else:
        jobs.sort(key=lambda j: j.get("date",""), reverse=True)
    return {"count": len(jobs), "jobs": jobs, "last_updated": cache["last_updated"]}

@app.get("/api/stats")
def get_stats():
    jobs = cache["jobs"] or load_jobs()
    sources = {}
    for j in jobs:
        s = j.get("source", "Unknown")
        sources[s] = sources.get(s, 0) + 1
    return {
        "total": len(jobs),
        "new_24h": count_new_24h(jobs),
        "genai_roles": sum(1 for j in jobs if classify_role(j.get("role","")) == "genai"),
        "companies": len(set(j.get("co","") for j in jobs if j.get("co"))),
        "sources": sources,
        "last_updated": cache["last_updated"],
        "is_running": cache["running"]
    }

@app.get("/api/progress")
def get_progress():
    from scraper import get_progress as gp
    p = gp()
    p["schedule"] = schedule_info
    return p

@app.post("/api/hunt")
def trigger_hunt():
    thread = threading.Thread(target=run_hunt, daemon=True)
    thread.start()
    return {"status": "started", "message": "Job hunt started in background"}

@app.post("/api/apply/{job_id}")
def mark_applied(job_id: str):
    applied = load_applied()
    applied.add(job_id)
    save_applied(applied)
    return {"status": "ok"}

@app.get("/api/applied")
def get_applied():
    return {"applied": list(load_applied())}

@app.get("/api/sources")
def get_sources():
    jobs = cache["jobs"] or load_jobs()
    return {"sources": sorted(set(j.get("source", "Unknown") for j in jobs))}

@app.get("/api/schedule")
def get_schedule():
    load_schedule()
    return schedule_info

@app.post("/api/schedule/toggle")
def toggle_schedule():
    load_schedule()
    schedule_info["enabled"] = not schedule_info["enabled"]
    save_schedule()
    return schedule_info


def run_hunt():
    if cache["running"]:
        return
    cache["running"] = True
    try:
        from scraper import hunt_all
        fresh = hunt_all(exclude_ids=load_applied())
        history = load_history()
        seen_history = set(history)
        for j in fresh:
            seen_history.add(j["id"])
        save_history(list(seen_history))
        existing = load_jobs()
        seen = {j["id"] for j in existing}
        for j in fresh:
            if j["id"] not in seen:
                existing.append(j)
                seen.add(j["id"])
        save_jobs(existing)
        cache["jobs"] = existing
        cache["last_updated"] = datetime.now().isoformat()
        from scraper import SOURCES
        print(f"Hunt complete: {len(fresh)} unique from {len(SOURCES)} sources, {len(existing)} total")
    except Exception as e:
        print(f"Hunt error: {e}")
        import traceback; traceback.print_exc()
    finally:
        cache["running"] = False


def scheduler_loop():
    """Background thread that auto-triggers hunts at night"""
    while True:
        try:
            load_schedule()
            now = datetime.now()
            if schedule_info.get("enabled"):
                target_hour = schedule_info.get("hour", 2)
                if now.hour == target_hour and 0 <= now.minute < 5:
                    last_auto = schedule_info.get("last_auto")
                    if last_auto:
                        try:
                            last = datetime.fromisoformat(last_auto)
                            if (now - last).total_seconds() < 82800:
                                time.sleep(300)
                                continue
                        except:
                            pass
                    if not cache["running"]:
                        print(f"[{now.strftime('%H:%M:%S')}] Nightly auto-hunt triggered")
                        run_hunt()
                        schedule_info["last_auto"] = datetime.now().isoformat()
                        save_schedule()
                    time.sleep(300)
        except Exception as e:
            print(f"Scheduler error: {e}")
        time.sleep(60)


def seed_default_jobs():
    if load_jobs():
        return
    defaults = [
        {"id": hashlib.md5(b"HARMAN|Associate Engineer (Agentic AI)").hexdigest(), "co": "HARMAN", "role": "Associate Engineer (Agentic AI)", "url": "https://openjobnet.com/harman-associate-engineer-2026-agentic-ai-engineer/", "source": "Seed", "date": datetime.now().isoformat(), "location": "Bangalore", "salary": "Competitive", "desc": "0-1yr. LLMs, RAG, LangChain, Agentic AI."},
        {"id": hashlib.md5(b"Associative|AI Developer (Fresher)").hexdigest(), "co": "Associative", "role": "AI Developer (Fresher)", "url": "https://associative.in/ai-developer-fresher/", "source": "Seed", "date": datetime.now().isoformat(), "location": "Pune", "salary": "₹4-8 LPA", "desc": "Python, LangChain, TensorFlow. Full-time Pune."},
        {"id": hashlib.md5(b"Siemens Energy|AI/Machine Learning Engineer").hexdigest(), "co": "Siemens Energy", "role": "AI/Machine Learning Engineer", "url": "https://freshersrecruitment.co.in/siemens-energy-off-campus-drive-2026/", "source": "Seed", "date": datetime.now().isoformat(), "location": "Gurugram", "salary": "Competitive", "desc": "0-3yr. Python, ML, GenAI, RAG."},
        {"id": hashlib.md5(b"EY|AI Developer (GenAI)").hexdigest(), "co": "EY", "role": "AI Developer (GenAI)", "url": "https://jobcode.in/freshers-ai-developer-2026-ey-hiring-ai-developers-for-freshers/", "source": "Seed", "date": datetime.now().isoformat(), "location": "Trivandrum", "salary": "Competitive", "desc": "0-1yr. GenAI, Python, ML."},
        {"id": hashlib.md5(b"TraceLink|Agentic AI Engineer").hexdigest(), "co": "TraceLink", "role": "Agentic AI Engineer", "url": "https://freshershunt.in/tracelink-freshers-hiring-2026-agentic-ai-engineer/", "source": "Seed", "date": datetime.now().isoformat(), "location": "Pune", "salary": "Competitive", "desc": "0-2yr. GenAI, RAG, multi-agent."},
        {"id": hashlib.md5(b"Cognizant Ace|Full-Stack AI Engineer").hexdigest(), "co": "Cognizant Ace", "role": "Full-Stack AI Engineer", "url": "https://jobcode.in/cognizant-full-stack-ai-engineer-2026-ace-team-hiring-for-freshers-12-18-lpa/", "source": "Seed", "date": datetime.now().isoformat(), "location": "Multiple Cities", "salary": "₹12-18 LPA", "desc": "2026 batch. 12LPA/18LPA. LLMs, RAG."},
        {"id": hashlib.md5(b"NVIDIA|Test & Tools Development Engineer").hexdigest(), "co": "NVIDIA", "role": "Test & Tools Development Engineer", "url": "https://offcampusjobs4u.com/nvidia-off-campus-drive-2026-test-tools-development-engineer-pune/", "source": "Seed", "date": datetime.now().isoformat(), "location": "Pune", "salary": "Competitive", "desc": "2026 batch. Python, LLMs, multi-agent."},
        {"id": hashlib.md5(b"IndiaMART|Associate Engineer (AI/ML)").hexdigest(), "co": "IndiaMART", "role": "Associate Engineer (AI/ML)", "url": "https://freshershunt.in/indiamart-off-campus-drive-2026/", "source": "Seed", "date": datetime.now().isoformat(), "location": "Noida", "salary": "₹6-10 LPA", "desc": "Fresher. Python, LLMs, LangChain."},
        {"id": hashlib.md5(b"Fujitsu|Data & AI Apprentice").hexdigest(), "co": "Fujitsu", "role": "Data & AI Apprentice", "url": "https://freshershunt.in/fujitsu-off-campus-drive-2026-data-ai-apprentice-pune/", "source": "Seed", "date": datetime.now().isoformat(), "location": "Pune", "salary": "Stipend", "desc": "Python, SQL, GenAI."},
        {"id": hashlib.md5(b"Citi|GenAI Developer").hexdigest(), "co": "Citi", "role": "GenAI Developer", "url": "https://www.jobinsider.in/jobs/citi-gen-ai-developer-job-sde-engineer-26/", "source": "Seed", "date": datetime.now().isoformat(), "location": "Chennai/Pune", "salary": "₹15-17 LPA", "desc": "0-2yr. GenAI."},
    ]
    save_jobs(defaults)
    cache["jobs"] = defaults
    cache["last_updated"] = datetime.now().isoformat()
    print(f"Seeded {len(defaults)} default jobs")

# Start scheduler thread
scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
scheduler_thread.start()

seed_default_jobs()
load_schedule()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

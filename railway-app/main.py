"""
GenAI Job Finder — Railway-deployable FastAPI app
Scrapes Reddit, career pages, Naukri, Indeed, and more for GenAI jobs.
"""

import json, os, hashlib, threading, time
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

app = FastAPI(title="GenAI Job Finder")

BASE = os.path.dirname(os.path.abspath(__file__))
JOBS_FILE = os.path.join(BASE, "jobs.json")
HISTORY_FILE = os.path.join(BASE, "history.json")

cache = {"jobs": [], "last_updated": None, "running": False, "html": None}


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
            return set(json.load(f))
    return set()

def save_history(h):
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(h), f)

def generate_html(jobs, last_updated, is_running):
    """Generate the full HTML page"""
    jobs_json = json.dumps(jobs)
    sources = sorted(set(j.get("source", "Unknown") for j in jobs))
    sources_json = json.dumps(sources)
    total = len(jobs)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GenAI Job Finder</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f0f1a; color: #e0e0e0; }}
.header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 24px 40px; border-bottom: 1px solid #2a2a4a; }}
.header h1 {{ color: #fff; font-size: 24px; }}
.header p {{ color: #8888aa; margin-top: 4px; }}
.container {{ max-width: 1300px; margin: 0 auto; padding: 24px; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; margin-bottom: 24px; }}
.stat-card {{ background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 12px; padding: 16px; text-align: center; }}
.stat-card .num {{ font-size: 28px; font-weight: 700; color: #fff; }}
.stat-card .label {{ font-size: 12px; color: #8888aa; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }}
.toolbar {{ display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }}
.btn {{ padding: 8px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s; }}
.btn-primary {{ background: #4361ee; color: white; }}
.btn-primary:hover {{ background: #3a56d4; }}
.btn-success {{ background: #2a9d8f; color: white; }}
.btn-success:hover {{ background: #21867a; }}
.btn-outline {{ background: transparent; border: 1px solid #3a3a5a; color: #aaaacc; }}
.btn-outline:hover {{ background: #1a1a2e; }}
.refresh-btn {{ background: #4361ee; color: white; padding: 8px 16px; }}
.refresh-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}
select, input {{ padding: 8px 12px; border: 1px solid #2a2a4a; border-radius: 8px; font-size: 14px; background: #1a1a2e; color: #e0e0e0; }}
.search-input {{ flex: 1; min-width: 200px; background: #1a1a2e; border: 1px solid #2a2a4a; color: #e0e0e0; padding: 8px 12px; border-radius: 8px; }}
table {{ width: 100%; border-collapse: collapse; background: #1a1a2e; border-radius: 12px; overflow: hidden; border: 1px solid #2a2a4a; }}
th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #2a2a4a; }}
th {{ background: #12122a; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: #8888aa; font-weight: 600; }}
td {{ font-size: 14px; }}
tr:hover {{ background: #1e1e3a; }}
.source-badge {{ padding: 2px 8px; border-radius: 4px; font-size: 11px; background: #2a2a4a; color: #aaaacc; }}
.job-actions {{ display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }}
.empty-state {{ text-align: center; padding: 60px 20px; color: #666688; }}
.loading {{ display: inline-block; width: 16px; height: 16px; border: 2px solid #8888aa; border-top: 2px solid #4361ee; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.last-updated {{ color: #666688; font-size: 12px; }}
@media (max-width: 768px) {{ .container {{ padding: 12px; }} .header {{ padding: 16px; }} td, th {{ padding: 8px; }} }}
</style>
</head>
<body>
<div class="header">
    <h1>GenAI Job Finder</h1>
    <p>Live jobs from Reddit, Naukri, Career Pages, Indeed, and more</p>
</div>
<div class="container">
    <div class="stats" id="stats"></div>
    <div class="toolbar">
        <button class="btn refresh-btn" id="huntBtn" onclick="triggerHunt()">🔄 Refresh Jobs</button>
        <span class="last-updated" id="lastUpdated">Last: {last_updated}</span>
        <select id="sourceFilter" onchange="filterJobs()"><option value="">All Sources</option></select>
        <input class="search-input" id="searchInput" placeholder="Search company or role..." oninput="filterJobs()">
    </div>
    <table>
        <thead><tr>
            <th>Source</th><th>Company</th><th>Role</th><th>Location</th><th>Salary</th><th>Date</th><th>Actions</th>
        </tr></thead>
        <tbody id="jobTable"></tbody>
    </table>
    <div class="empty-state" id="emptyState" style="display:none">
        <p>No jobs found matching your criteria.</p>
    </div>
</div>
<script>
let allJobs = {jobs_json};
let sources = {sources_json};

const sel = document.getElementById("sourceFilter");
sources.forEach(s => {{ sel.innerHTML += `<option value="${{s}}">${{s}}</option>` }});

function render(jobs) {{
    const total = allJobs.length;
    const srcCounts = {{}};
    allJobs.forEach(j => {{ const s = j.source || 'Unknown'; srcCounts[s] = (srcCounts[s]||0)+1 }});
    const genaiCount = allJobs.filter(j => j.role.toLowerCase().includes('genai') || j.role.toLowerCase().includes('generative')).length;
    const redditCount = allJobs.filter(j => j.source === 'Reddit').length;
    document.getElementById("stats").innerHTML = `
        <div class="stat-card"><div class="num">${{total}}</div><div class="label">Total Jobs</div></div>
        <div class="stat-card"><div class="num">${{Object.keys(srcCounts).length}}</div><div class="label">Sources</div></div>
        <div class="stat-card"><div class="num">${{genaiCount}}</div><div class="label">GenAI Roles</div></div>
        <div class="stat-card"><div class="num">${{redditCount}}</div><div class="label">From Reddit</div></div>
    `;
    const tbody = document.getElementById("jobTable");
    const empty = document.getElementById("emptyState");
    if (!jobs || jobs.length === 0) {{ tbody.innerHTML = ""; empty.style.display = "block"; return; }}
    empty.style.display = "none";
    tbody.innerHTML = jobs.map(j => {{
        const src = j.source || '?', co = j.co || '?', role = j.role || '?';
        const loc = j.location || j.desc?.split(',')[0] || '-';
        const sal = j.salary || '-';
        const date = j.date ? j.date.slice(0,10) : '-';
        const url = j.url || '';
        const btn = url ? `<a href="${{esc(url)}}" target="_blank" class="btn btn-success" style="padding:4px 10px;font-size:12px">Apply</a>` : '';
        return `<tr><td><span class="source-badge">${{esc(src)}}</span></td>
            <td><strong>${{esc(co)}}</strong></td><td>${{esc(role)}}</td>
            <td>${{esc(loc)}}</td><td>${{esc(sal)}}</td><td>${{date}}</td>
            <td class="job-actions">${{btn}}</td></tr>`;
    }}).join("");
}}
function esc(s) {{ if (!s) return '-'; const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }}
function filterJobs() {{
    let jobs = [...allJobs];
    const src = document.getElementById("sourceFilter").value;
    const q = document.getElementById("searchInput").value.toLowerCase();
    if (src) jobs = jobs.filter(j => (j.source||'').toLowerCase() === src.toLowerCase());
    if (q) jobs = jobs.filter(j => (j.role+'').toLowerCase().includes(q) || (j.co+'').toLowerCase().includes(q));
    render(jobs);
}}
async function triggerHunt() {{
    const btn = document.getElementById("huntBtn");
    btn.disabled = true; btn.innerHTML = '<span class="loading"></span> Hunting...';
    try {{
        await fetch('/api/hunt', {{method:'POST'}});
        setTimeout(async () => {{
            const r = await fetch('/api/jobs');
            const j = await r.json();
            allJobs = j.jobs;
            document.getElementById("lastUpdated").textContent = 'Last: ' + (j.last_updated || 'Just now');
            filterJobs();
            btn.disabled = false; btn.innerHTML = '🔄 Refresh Jobs';
        }}, 5000);
    }} catch(e) {{ btn.disabled = false; btn.innerHTML = '🔄 Refresh Jobs'; }}
}}
filterJobs();
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    jobs = cache["jobs"] or load_jobs()
    return generate_html(jobs, cache["last_updated"] or "Never", cache["running"])

@app.get("/api/jobs")
def get_jobs(source: str = None, search: str = None):
    jobs = cache["jobs"] or load_jobs()
    if source:
        jobs = [j for j in jobs if j.get("source", "").lower() == source.lower()]
    if search:
        s = search.lower()
        jobs = [j for j in jobs if s in j.get("role","").lower() or s in j.get("co","").lower()]
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
        "sources": sources,
        "last_updated": cache["last_updated"],
        "is_running": cache["running"]
    }

@app.post("/api/hunt")
def trigger_hunt():
    thread = threading.Thread(target=run_hunt, daemon=True)
    thread.start()
    return {"status": "started", "message": "Job hunt started in background"}

@app.get("/api/sources")
def get_sources():
    jobs = cache["jobs"] or load_jobs()
    return {"sources": sorted(set(j.get("source", "Unknown") for j in jobs))}


def run_hunt():
    if cache["running"]:
        return
    cache["running"] = True
    try:
        from scraper import hunt_all
        fresh = hunt_all()
        if not fresh:
            cache["running"] = False
            return
        history = load_history()
        for j in fresh:
            history.add(j["id"])
        save_history(history)
        existing = load_jobs()
        seen = {j["id"] for j in existing}
        for j in fresh:
            if j["id"] not in seen:
                existing.append(j)
                seen.add(j["id"])
        save_jobs(existing)
        cache["jobs"] = existing
        cache["last_updated"] = datetime.now().isoformat()
        print(f"Hunt complete: {len(fresh)} fresh, {len(existing)} total")
    except Exception as e:
        print(f"Hunt error: {e}")
    finally:
        cache["running"] = False


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


seed_default_jobs()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

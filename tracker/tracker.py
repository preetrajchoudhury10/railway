"""
GenAI Job Tracker v2 — Enhanced tracker with notification + auto-import
Reads from all_jobs.json (updated by AI web searches) and shows new matches
"""

import json, os, time, hashlib
from datetime import datetime
from plyer import notification

BASE = os.path.dirname(os.path.abspath(__file__))
ALL_JOBS_FILE = os.path.join(BASE, "all_jobs.json")
NOTIFIED_FILE = os.path.join(BASE, "notified_history.json")
FRESH_FILE = os.path.join(BASE, "fresh_jobs.json")
JOBS_WEB_FILE = os.path.join(BASE, "jobs_web.json")

def bold(t): return f"\033[1m{t}\033[0m"

def load_json(path):
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=2)

def get_stats(jobs):
    total = len(jobs)
    sources = {}
    for j in jobs:
        s = j.get("from", j.get("source", "Unknown"))
        sources[s] = sources.get(s, 0) + 1
    return total, sources

def show_fresh():
    fresh = load_json(FRESH_FILE)
    all_jobs = load_json(ALL_JOBS_FILE)

    print(f"  {bold('All-time jobs:')} {len(all_jobs)}")
    print(f"  {bold('Fresh (unread):')} {len(fresh)}")

    if fresh:
        print(f"\n  {'='*55}")
        print(f"  {'NEW JOB MATCHES':^55}")
        print(f"  {'='*55}")
        for i, j in enumerate(fresh[:25], 1):
            role = j.get("role", "?")
            co = j.get("co", j.get("company", "?"))
            src = j.get("from", j.get("source", "?"))
            if len(role) > 55: role = role[:52] + "..."
            print(f"  {i:2}. [{src}] {role}")
            print(f"      {co}")
        if len(fresh) > 25:
            print(f"  ... +{len(fresh)-25} more")
        print()

    total, sources = get_stats(all_jobs)
    print(f"  {bold('By source:')}")
    for s, c in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"    {s}: {c}")

if __name__ == "__main__":
    print(f"\n  {'='*55}")
    print(f"  GenAI JOB TRACKER — Dashboard")
    print(f"  {'='*55}\n")
    show_fresh()

    # Attempt notification for fresh jobs
    fresh = load_json(FRESH_FILE)
    if fresh:
        try:
            notification.notify(
                title="GenAI Job Tracker",
                message=f"{len(fresh)} new job matches waiting for you!",
                timeout=8
            )
        except: pass

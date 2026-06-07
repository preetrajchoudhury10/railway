import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

STATUSES = ["Saved", "Applied", "Screening", "Interview", "Offer", "Rejected"]

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        role TEXT NOT NULL,
        location TEXT,
        salary TEXT,
        url TEXT,
        status TEXT DEFAULT 'Saved',
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    )""")
    return conn

def add_job():
    conn = get_conn()
    print("=== Add New Application ===")
    company = input("Company: ").strip()
    role = input("Role: ").strip()
    loc = input("Location: ").strip()
    salary = input("Salary (optional): ").strip()
    url = input("URL (optional): ").strip()
    notes = input("Notes (optional): ").strip()
    conn.execute("INSERT INTO jobs (company, role, location, salary, url, notes) VALUES (?,?,?,?,?,?)",
                 (company, role, loc, salary, url, notes))
    conn.commit()
    conn.close()
    print(f"Added: {role} @ {company}")

def list_jobs():
    conn = get_conn()
    filter_status = input("Filter by status? (blank for all): ").strip()
    if filter_status:
        rows = conn.execute("SELECT * FROM jobs WHERE status=? ORDER BY updated_at DESC", (filter_status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM jobs ORDER BY updated_at DESC").fetchall()
    conn.close()
    if not rows:
        print("No applications found.")
        return
    print(f"\n{'ID':<3} {'Company':<20} {'Role':<30} {'Location':<15} {'Status':<12} {'Updated':<10}")
    print("-"*90)
    for r in rows:
        print(f"{r['id']:<3} {r['company']:<20} {r['role']:<30} {r['location']:<15} {r['status']:<12} {r['updated_at'][:10]}")

def update_job():
    conn = get_conn()
    list_jobs()
    jid = input("\nJob ID to update: ").strip()
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone()
    if not row:
        print("Not found.")
        conn.close()
        return
    print(f"Current status: {row['status']}")
    print(f"Statuses: {', '.join(STATUSES)}")
    new_status = input("New status: ").strip()
    if new_status not in STATUSES:
        print("Invalid status.")
        conn.close()
        return
    notes = input(f"Notes (current: {row['notes'] or 'none'}): ").strip()
    conn.execute("UPDATE jobs SET status=?, notes=?, updated_at=datetime('now') WHERE id=?", (new_status, notes, jid))
    conn.commit()
    conn.close()
    print("Updated!")

def delete_job():
    conn = get_conn()
    list_jobs()
    jid = input("\nJob ID to delete: ").strip()
    conn.execute("DELETE FROM jobs WHERE id=?", (jid,))
    conn.commit()
    conn.close()
    print("Deleted!")

def export_json():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM jobs ORDER BY updated_at DESC").fetchall()
    conn.close()
    data = [dict(r) for r in rows]
    path = os.path.join(os.path.dirname(__file__), "jobs_export.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Exported {len(data)} jobs to {path}")

def import_from_web():
    path = os.path.join(os.path.dirname(__file__), "jobs_web.json")
    if not os.path.exists(path):
        print("No jobs_web.json found.")
        return
    with open(path) as f:
        data = json.load(f)
    conn = get_conn()
    count = 0
    for j in data:
        conn.execute("INSERT INTO jobs (company, role, location, salary, url, status, notes) VALUES (?,?,?,?,?,?,?)",
                     (j.get("company",""), j.get("role",""), j.get("location",""), j.get("salary",""), j.get("url",""), j.get("status","Saved"), j.get("notes","")))
        count += 1
    conn.commit()
    conn.close()
    print(f"Imported {count} jobs.")

def main():
    while True:
        print("\n=== Job Tracker CLI ===")
        print("1. Add job")
        print("2. List jobs")
        print("3. Update status")
        print("4. Delete job")
        print("5. Export to JSON")
        print("6. Import from web")
        print("0. Exit")
        choice = input("> ").strip()
        if choice == "1": add_job()
        elif choice == "2": list_jobs()
        elif choice == "3": update_job()
        elif choice == "4": delete_job()
        elif choice == "5": export_json()
        elif choice == "6": import_from_web()
        elif choice == "0":
            print("Good luck with your job search!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

# Deploy GenAI Job Finder to Railway (Free)

## Step 1: Create a GitHub Repository

```bash
cd railway-app
git init
git add .
git commit -m "Initial commit"
# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/genai-job-finder.git
git push -u origin main
```

## Step 2: Deploy on Railway

1. Go to https://railway.app and sign up (GitHub login)
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `genai-job-finder` repo
4. Railway auto-detects the Python app and deploys
5. Wait 2-3 minutes, then click the URL to open

## Step 3: Connect Local Dashboard

1. After deployment, copy your Railway URL (e.g., `https://genai-job-finder.up.railway.app`)
2. Open `dashboard.html`
3. Click **"Sync Railway"** button
4. Paste your Railway URL
5. Jobs get imported automatically

## What the Railway App Does

| Feature | How |
|---------|-----|
| **Auto-scrapes** every time you visit `/api/hunt` | Reddit, Company Careers, Naukri, Indeed, Internshala |
| **Web Dashboard** | Shows all jobs with Apply Now buttons |
| **REST API** | `/api/jobs`, `/api/stats`, `/api/hunt` |
| **Persistent SQLite** | Jobs stored across restarts |

## Making It Auto-Scrape

### Option A: Railway Cron (if available)
Add in railway.json:
```json
"cron": {
    "schedule": "0 */6 * * *",
    "command": "python scraper.py"
}
```

### Option B: GitHub Actions
Create `.github/workflows/scrape.yml`:
```yaml
name: Scrape Jobs
on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:
jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: curl -X POST https://YOUR-APP.railway.app/api/hunt
```

### Option C: Manual
Just click the **"Refresh Jobs"** button on the web UI.

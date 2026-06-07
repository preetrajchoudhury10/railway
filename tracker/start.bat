@echo off
title GenAI Job Finder
cls
echo ===================================================
echo        GENAI JOB FINDER - Your Career Hub
echo ===================================================
echo.
echo  [1] OPEN WEB DASHBOARD (visual tracker + Apply Now)
echo  [2] RUN CLI TRACKER
echo  [3] RUN JOB HUNTER (scan Reddit, Careers, Naukri, etc)
echo  [4] DEPLOY TO RAILWAY (free cloud hosting)
echo  [5] SHOW LATEST JOBS
echo  [6] RESUME TIPS
echo  [7] OPEN TRACKER FOLDER
echo  [0] EXIT
echo.
set /p c="Choose [0-7]: "

if "%c%"=="1" start "" "%~dp0dashboard.html"
if "%c%"=="2" python "%~dp0cli.py"
if "%c%"=="3" (
    cd /d "%~dp0railway-app"
    python scraper.py
    if errorlevel 0 (
        echo.
        echo Scraping complete! Check the results.
        pause
    )
)
if "%c%"=="4" (
    echo.
    echo ===== DEPLOY TO RAILWAY =====
    echo.
    echo 1. Create free account at https://railway.app
    echo 2. Install Railway CLI: npm install -g @railway/cli
    echo 3. Or deploy via GitHub:
    echo    - Push railway-app/ to a GitHub repo
    echo    - Connect repo to Railway
    echo    - Railway auto-detects the Python app
    echo.
    echo Files ready in: %~dp0railway-app\
    echo.
    echo Quick deploy with GitHub:
    echo   cd %~dp0railway-app
    echo   git init ^&^& git add . ^&^& git commit -m "init"
    echo   gh repo create genai-job-finder --public --push
    echo   Then: https://railway.app/new - connect repo
    echo.
    pause
)
if "%c%"=="5" python "%~dp0tracker.py"
if "%c%"=="6" start "" "%~dp0resume_tips.md"
if "%c%"=="7" start "" "%~dp0"
if "%c%"=="0" exit /b

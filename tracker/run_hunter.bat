@echo off
cd /d "%~dp0"
python job_hunter.py
if %errorlevel%==0 (
    echo Job hunt completed at %date% %time%
) else (
    echo Job hunt encountered an error at %date% %time%
)

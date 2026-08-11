@echo off
rem =====================================================================
rem Job Tracker Backend Auto-Launcher
rem Starts Uvicorn FastAPI server minimized on port 5000.
rem =====================================================================

cd /d "%~dp0"

start "Job Tracker Backend" /min py -m uvicorn server.main:app --port 5000

echo Job Tracker server started on http://localhost:5000

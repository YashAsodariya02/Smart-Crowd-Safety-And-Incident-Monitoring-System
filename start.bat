@echo off
title SMART CROWD SAFETY SYSTEM - BACKEND & UI
color 0A

echo ========================================================
echo   SMART CROWD SAFETY & INCIDENT MONITORING SYSTEM
echo   AI Surveillance & Crowd Hazard Perception Platform
echo ========================================================
echo.
echo [1/2] Starting server at http://127.0.0.1:8000 ...
echo [2/2] Opening browser in 3 seconds...
echo.

start "" http://127.0.0.1:8000/

cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000

pause

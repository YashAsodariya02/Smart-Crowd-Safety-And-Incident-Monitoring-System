@echo off
title SMART CROWD SAFETY SYSTEM - DEV MODE
color 0B

echo ========================================================
echo   SMART CROWD SAFETY - DEVELOPMENT MODE (HOT RELOAD)
echo ========================================================
echo.
echo Launching Backend (FastAPI on Port 8000)...
start "CrowdMonitor - Backend" cmd /k "cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo Launching Frontend (Vite on Port 5173)...
start "CrowdMonitor - Frontend" cmd /k "cd frontend && npm run dev"

echo Opening browser at http://127.0.0.1:5173/ ...
timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:5173/

echo.
echo Both services are running in separate terminal windows.
pause

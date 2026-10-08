@echo off
title Starting AI Career Guidance System
echo ============================================================
echo   Starting AI Powered Agentic Career Guidance System
echo ============================================================
echo.

echo [1/3] Starting Backend API (FastAPI on Port 8000)...
start "Career Guidance - Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --reload --port 8000"

echo [2/3] Waiting 3 seconds for Backend to initialize...
timeout /t 3 /nobreak >nul

echo [3/3] Starting Frontend Server (Vite React on Port 5173)...
start "Career Guidance - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

timeout /t 3 /nobreak >nul

echo Opening browser at http://localhost:5173 ...
start http://localhost:5173

echo.
echo ============================================================
echo   Application started!
echo   Frontend : http://localhost:5173
echo   Backend  : http://127.0.0.1:8000
echo   API Docs : http://127.0.0.1:8000/docs
echo ============================================================

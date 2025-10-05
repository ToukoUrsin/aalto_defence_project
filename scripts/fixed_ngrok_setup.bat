@echo off
echo ========================================
echo Military Hierarchy System - Fixed ngrok Setup
echo ========================================
echo.

echo Step 1: Starting Backend API...
start "Backend API" cmd /k "cd /d %~dp0.. && python backend.py"

echo Waiting 10 seconds for backend to start...
timeout /t 10 /nobreak > nul

echo.
echo Step 2: Starting Unified Dashboard...
start "Unified Dashboard" cmd /k "cd /d %~dp0..\mil_dashboard && npm run dev"

echo Waiting 10 seconds for dashboard to start...
timeout /t 10 /nobreak > nul

echo.
echo Step 3: Starting ngrok tunnels with separate URLs...
echo.

echo Starting Backend API tunnel (Port 8000)...
start "ngrok Backend API" cmd /k "cd /d %~dp0..\ngrok && ngrok.exe http 8000"

echo Waiting 5 seconds...
timeout /t 5 /nobreak > nul

echo.
echo Starting Unified Dashboard tunnel (Port 3000)...
start "ngrok Unified Dashboard" cmd /k "cd /d %~dp0..\ngrok && ngrok.exe http 3000"

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo Your Military Hierarchy System is now running!
echo.
echo Check the ngrok windows for your separate public URLs:
echo - Backend API: https://xxxxx.ngrok-free.dev (Port 8000)
echo - Unified Dashboard: https://yyyyy.ngrok-free.dev (Port 3000)
echo.
echo Local URLs:
echo - Backend API: https://military-hierarchy-backend.onrender.com/
echo - Unified Dashboard: http://localhost:3000 (includes Reports)
echo.
echo NOTE: Each service now has its own unique ngrok URL
echo.
echo Press any key to exit...
pause > nul

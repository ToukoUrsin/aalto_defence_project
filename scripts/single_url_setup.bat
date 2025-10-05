@echo off
echo ========================================
echo Military Hierarchy System - Single URL Setup
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
echo Step 3: Starting single ngrok tunnel for Unified Dashboard...
echo.

echo Starting Unified Dashboard tunnel (Port 3000)...
echo This will give you ONE public URL that includes everything!
start "ngrok Unified Dashboard" cmd /k "cd /d %~dp0..\ngrok && ngrok.exe http 3000"

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo Your Military Hierarchy System is now running!
echo.
echo Check the ngrok window for your public URL:
echo - Unified Dashboard: https://xxxxx.ngrok-free.dev (includes everything)
echo.
echo Local URLs:
echo - Backend API: https://military-hierarchy-backend.onrender.com/ (internal only)
echo - Unified Dashboard: http://localhost:3000 (public via ngrok)
echo.
echo NOTE: Only the Unified Dashboard is exposed publicly
echo The Backend API is accessible internally by the dashboard
echo.
echo Press any key to exit...
pause > nul

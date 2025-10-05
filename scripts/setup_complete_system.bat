@echo off
echo ========================================
echo Military Hierarchy System - Complete Setup
echo ========================================
echo.

echo Step 1: Starting Backend API...
cd /d "%~dp0"
start "Backend API" cmd /k "python backend.py"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo Step 2: Starting Main Dashboard...
start "Main Dashboard" cmd /k "cd /d %~dp0\mil_dashboard && npm run dev"

echo Waiting 3 seconds for dashboard to start...
timeout /t 3 /nobreak > nul

echo.
echo Step 3: Starting Reports UI...
start "Reports UI" cmd /k "cd /d %~dp0\ui-for-reports\frontend && npm run dev"

echo Waiting 3 seconds for reports UI to start...
timeout /t 3 /nobreak > nul

echo.
echo Step 4: Testing local services...
echo Testing Backend API...
curl -s https://military-hierarchy-backend.onrender.com// > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API is running
) else (
    echo ❌ Backend API not responding
)

echo Testing Main Dashboard...
curl -s http://localhost:3000/ > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Main Dashboard is running
) else (
    echo ❌ Main Dashboard not responding
)

echo Testing Reports UI...
curl -s http://localhost:3001/ > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Reports UI is running
) else (
    echo ❌ Reports UI not responding
)

echo.
echo Step 5: Starting ngrok tunnels...
echo.

echo Starting Backend API tunnel (port 8000)...
start "ngrok Backend API" cmd /k "ngrok http 8000"

echo.
echo Starting Main Dashboard tunnel (port 3000)...
start "ngrok Main Dashboard" cmd /k "ngrok http 3000"

echo.
echo Starting Reports UI tunnel (port 3001)...
start "ngrok Reports UI" cmd /k "ngrok http 3001"

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo Your Military Hierarchy System is now running!
echo.
echo Local URLs:
echo - Backend API: https://military-hierarchy-backend.onrender.com/
echo - Main Dashboard: http://localhost:3000
echo - Reports UI: http://localhost:3001
echo.
echo Global URLs (check ngrok windows):
echo - Backend API: https://xxxxx.ngrok-free.dev
echo - Main Dashboard: https://yyyyy.ngrok-free.dev
echo - Reports UI: https://zzzzz.ngrok-free.dev
echo.
echo Share the ngrok URLs with anyone, anywhere!
echo.
echo Press any key to exit...
pause > nul

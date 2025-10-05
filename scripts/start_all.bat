@echo off
echo Starting Military Hierarchy System...
echo.

echo Activating virtual environment...
call ..\venv\Scripts\activate

echo.
echo Initializing database...
cd ..
python database_setup.py

echo.
echo Starting backend server in new window...
start "Backend Server" cmd /k "cd /d %~dp0.. && python backend.py"

echo.
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo Testing API endpoints...
cd ..
python tests\test_api.py

echo.
echo Starting frontend dashboard in new window...
start "Frontend Dashboard" cmd /k "cd /d %~dp0..\mil_dashboard && npm run dev"

echo.
echo Starting reports UI in new window...
start "Reports UI" cmd /k "cd /d %~dp0..\ui-for-reports\frontend && npm run dev"

echo.
echo System started successfully!
echo.
echo Backend: https://military-hierarchy-backend.onrender.com/ (or http://10.3.35.27:8000 from other devices)
echo Frontend Dashboard: http://localhost:3000 (or http://10.3.35.27:3000 from other devices)
echo Reports UI: http://localhost:3001 (or http://10.3.35.27:3001 from other devices)
echo.
echo Network Access:
echo - Backend API: http://10.3.35.27:8000
echo - Main Dashboard: http://10.3.35.27:3000
echo - Reports UI: http://10.3.35.27:3001
echo.
echo Press any key to exit...
pause > nul

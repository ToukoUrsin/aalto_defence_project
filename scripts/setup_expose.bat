@echo off
echo Setting up Expose.dev for Military Hierarchy System...
echo.

echo Step 1: Activating Expose token...
expose token c253f28e-fa05-4d37-9121-311f00ceb32d

echo.
echo Step 2: Setting default server to EU-2...
expose default-server eu-2

echo.
echo Step 3: Starting Expose tunnels for all services...
echo.

echo Starting Backend API tunnel (port 8000)...
start "Expose Backend API" cmd /k "expose share https://military-hierarchy-backend.onrender.com/ --subdomain=military-api"

echo.
echo Starting Main Dashboard tunnel (port 3000)...
start "Expose Main Dashboard" cmd /k "expose share http://localhost:3000 --subdomain=military-dashboard"

echo.
echo Starting Reports UI tunnel (port 3001)...
start "Expose Reports UI" cmd /k "expose share http://localhost:3001 --subdomain=military-reports"

echo.
echo ========================================
echo EXPOSE SETUP COMPLETE!
echo ========================================
echo.
echo Your services will be available at:
echo - Backend API: https://military-api.sharedwithexpose.com
echo - Main Dashboard: https://military-dashboard.sharedwithexpose.com  
echo - Reports UI: https://military-reports.sharedwithexpose.com
echo.
echo Share these URLs with anyone, anywhere!
echo.
echo Press any key to exit...
pause > nul

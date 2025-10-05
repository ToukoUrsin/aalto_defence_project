@echo off
echo ========================================
echo Military Backend API - Global Access
echo ========================================
echo.

:: --- Step 1: Start Backend API ---
echo Step 1: Starting Backend API with virtual environment...
start "Backend API" cmd /k "cd /d %~dp0.. && .\venv\Scripts\activate && python backend.py"

echo Waiting 15 seconds for backend to start...
timeout /t 15 /nobreak > nul

:: --- Step 2: Start ngrok tunnel for Backend API ---
echo.
echo Step 2: Starting ngrok tunnel for Backend API...
echo.

:: Kill any previous ngrok instances to avoid ERR_NGROK_334
echo Checking for existing ngrok processes...
taskkill /IM ngrok.exe /F > nul 2>&1

echo Starting Backend API tunnel (Port 8000)...
start "ngrok Backend API" cmd /k "cd /d %~dp0..\ngrok && ngrok.exe http 8000"

echo Waiting 5 seconds for tunnel to establish...
timeout /t 5 /nobreak > nul

:: --- Final Info ---
echo.
echo ========================================
echo BACKEND API EXPOSED GLOBALLY!
echo ========================================
echo.
echo Your Military Backend API is now running and exposed!
echo.
echo Check the ngrok window for your public URL:
echo - Backend API: https://xxxxx.ngrok-free.dev
echo.
echo Local URL:
echo - Backend API: https://military-hierarchy-backend.onrender.com/
echo - API Documentation: https://military-hierarchy-backend.onrender.com//docs
echo.
echo IMPORTANT:
echo - Use the ngrok URL for external POST requests
echo - API supports all military hierarchy operations
echo - Check ngrok window for the actual public URL
echo.
echo Available endpoints:
echo - POST /soldiers - Create new soldier
echo - POST /soldiers/{id}/raw_inputs - Send raw data
echo - POST /soldiers/{id}/reports - Create structured report
echo - PUT /soldiers/{id}/status - Update soldier status
echo - GET /hierarchy - Get military hierarchy
echo - GET /reports - Get all reports
echo.
echo Press any key to exit...
pause > nul

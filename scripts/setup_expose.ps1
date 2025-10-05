# Expose.dev Setup Script for Military Hierarchy System
# This script sets up Expose tunnels for all services

Write-Host "🌐 Setting up Expose.dev for Military Hierarchy System..." -ForegroundColor Green
Write-Host ""

# Step 1: Activate Expose token
Write-Host "Step 1: Activating Expose token..." -ForegroundColor Yellow
& .\expose token c253f28e-fa05-4d37-9121-311f00ceb32d

Write-Host ""
Write-Host "Step 2: Setting default server to EU-2..." -ForegroundColor Yellow
& .\expose default-server eu-2

Write-Host ""
Write-Host "Step 3: Starting Expose tunnels..." -ForegroundColor Yellow
Write-Host ""

# Start Backend API tunnel
Write-Host "🚀 Starting Backend API tunnel (port 8000)..." -ForegroundColor Cyan
Start-Process -FilePath ".\expose" -ArgumentList "share", "https://military-hierarchy-backend.onrender.com/", "--subdomain=military-api" -WindowStyle Normal

Start-Sleep -Seconds 2

# Start Main Dashboard tunnel  
Write-Host "🚀 Starting Main Dashboard tunnel (port 3000)..." -ForegroundColor Cyan
Start-Process -FilePath ".\expose" -ArgumentList "share", "http://localhost:3000", "--subdomain=military-dashboard" -WindowStyle Normal

Start-Sleep -Seconds 2

# Start Reports UI tunnel
Write-Host "🚀 Starting Reports UI tunnel (port 3001)..." -ForegroundColor Cyan
Start-Process -FilePath ".\expose" -ArgumentList "share", "http://localhost:3001", "--subdomain=military-reports" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "🎉 EXPOSE SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your services are now available at:" -ForegroundColor White
Write-Host "• Backend API: https://military-api.sharedwithexpose.com" -ForegroundColor Yellow
Write-Host "• Main Dashboard: https://military-dashboard.sharedwithexpose.com" -ForegroundColor Yellow
Write-Host "• Reports UI: https://military-reports.sharedwithexpose.com" -ForegroundColor Yellow
Write-Host "• API Documentation: https://military-api.sharedwithexpose.com/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌍 Share these URLs with anyone, anywhere!" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

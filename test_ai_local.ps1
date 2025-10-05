# Test AI chat endpoint locally with proper JSON format

$body = @'
{
    "message": "What is the current tactical situation?",
    "context": {
        "node": {
            "name": "1st Infantry Battalion",
            "unit_id": "unit-001"
        },
        "reports": [
            {
                "report_type": "SITREP",
                "timestamp": "2025-10-04T22:47:17",
                "soldier_name": "Cpl. Smith",
                "structured_json": "{\"status\": \"All units operational\", \"location\": \"Grid 123456\", \"engagement_status\": \"No contact\"}"
            }
        ]
    }
}
'@

Write-Host "Testing LOCAL backend..." -ForegroundColor Cyan
Write-Host "URL: https://military-hierarchy-backend.onrender.com//ai/chat" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "https://military-hierarchy-backend.onrender.com//ai/chat" `
        -Method Post `
        -Body $body `
        -ContentType "application/json" `
        -ErrorAction Stop `
        -TimeoutSec 60
    
    Write-Host ""
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 10
    
} catch {
    Write-Host ""
    Write-Host "FAILED!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "Status Code: $statusCode" -ForegroundColor Yellow
        
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host ""
        Write-Host "Response Body:" -ForegroundColor Yellow
        Write-Host $responseBody
    }
}

Write-Host ""
Write-Host "Note: Make sure backend is running locally: python backend/backend.py" -ForegroundColor Gray

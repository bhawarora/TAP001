  # Power Apps Login Launcher Script
# Right-click → Run with PowerShell to execute

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Power Apps Login Automation Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables for this session
$env:POWERAPPS_USER = 'bhawna.arora@protivitiglobal.in'
$env:POWERAPPS_WAIT_SECONDS = '600'

# Navigate to project directory
Push-Location C:\Users\bhawna.arora\PycharmProjects\PythonProject\PythonProject2

Write-Host "Starting script..." -ForegroundColor Green
Write-Host "Chrome will open automatically" -ForegroundColor Yellow
Write-Host ""

# Run the Python script
python code.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Script completed" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Clean up
Pop-Location

# Pause so user can see output
Read-Host "Press Enter to close this window"


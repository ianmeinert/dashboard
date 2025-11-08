# Quick manual reset script for Windows (PowerShell)
# Run this to immediately reset all weekly points

Write-Host "🔄 Resetting weekly points for all family members..." -ForegroundColor Cyan

# Test API connectivity
$apiUrl = $null

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/chores/members" -Method GET -TimeoutSec 5 -ErrorAction Stop
    $apiUrl = "http://localhost:8000"
    Write-Host "📡 Found API at: $apiUrl" -ForegroundColor Green
}
catch {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/chores/members" -Method GET -TimeoutSec 5 -ErrorAction Stop
        $apiUrl = "http://127.0.0.1:8000"
        Write-Host "📡 Found API at: $apiUrl" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Cannot detect running API server" -ForegroundColor Red
        Write-Host "Please check:" -ForegroundColor Yellow
        Write-Host "1. Is your FastAPI server running?"
        Write-Host "2. Is it running on port 8000?"
        Write-Host "3. Try running manually: Invoke-RestMethod -Uri 'http://localhost:8000/api/chores/admin/reset-weekly' -Method POST"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Call the manual reset endpoint
Write-Host "Calling reset endpoint..." -ForegroundColor Yellow

try {
    $resetResponse = Invoke-RestMethod -Uri "$apiUrl/api/chores/admin/reset-weekly" -Method POST -ErrorAction Stop
    
    Write-Host "✅ Weekly reset successful!" -ForegroundColor Green
    Write-Host "Response: $($resetResponse | ConvertTo-Json -Depth 2)" -ForegroundColor White
    Write-Host ""
    Write-Host "🎉 All family members' weekly points have been reset to 0" -ForegroundColor Green
    Write-Host "📅 New weekly period started: $(Get-Date -Format 'yyyy-MM-dd')" -ForegroundColor Green
    
    # Verify by checking member status
    Write-Host ""
    Write-Host "🔍 Verifying reset by checking member status..." -ForegroundColor Cyan
    
    try {
        $members = Invoke-RestMethod -Uri "$apiUrl/api/chores/members" -Method GET -ErrorAction Stop
        Write-Host "Member weekly points after reset:" -ForegroundColor White
        foreach ($member in $members) {
            Write-Host "  $($member.name): $($member.weekly_points)/$($member.weekly_points_cap) weekly points" -ForegroundColor White
        }
    }
    catch {
        Write-Host "⚠️  Could not verify member status, but reset was successful" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Reset failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running manually:" -ForegroundColor Yellow
    Write-Host "Invoke-RestMethod -Uri '$apiUrl/api/chores/admin/reset-weekly' -Method POST"
}

Write-Host ""
Write-Host "Press Enter to continue..." -ForegroundColor Gray
Read-Host
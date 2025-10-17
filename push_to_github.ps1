# PowerShell script to push code to GitHub
# Run this script to push your code to the repository

Write-Host "🚀 Pushing AI-Powered Smart Attendance System to GitHub..." -ForegroundColor Green
Write-Host ""

# Navigate to project directory
Set-Location "d:\Projcet"

# Check git status
Write-Host "📋 Current git status:" -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "🔐 AUTHENTICATION REQUIRED:" -ForegroundColor Red
Write-Host "When prompted for credentials, use:" -ForegroundColor White
Write-Host "  Username: bhanu4554" -ForegroundColor Cyan
Write-Host "  Password: Your GitHub Personal Access Token" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 To create a Personal Access Token:" -ForegroundColor Yellow
Write-Host "  1. Go to: https://github.com/settings/tokens" -ForegroundColor White
Write-Host "  2. Click 'Generate new token (classic)'" -ForegroundColor White
Write-Host "  3. Select scopes: repo, workflow" -ForegroundColor White
Write-Host "  4. Copy the token and use it as password" -ForegroundColor White
Write-Host ""

# Prompt user to continue
$continue = Read-Host "Press Enter to continue with push, or Ctrl+C to cancel"

# Push to GitHub
Write-Host "🚀 Pushing to GitHub repository..." -ForegroundColor Green
git push -u origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SUCCESS! Your code has been pushed to:" -ForegroundColor Green
    Write-Host "   https://github.com/bhanu4554/attendance" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎉 Your AI-Powered Smart Attendance System is now on GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📚 Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Share the repository with your team" -ForegroundColor White
    Write-Host "  2. Set up development environment following QUICK_START.md" -ForegroundColor White
    Write-Host "  3. Install dependencies and test the system" -ForegroundColor White
    Write-Host "  4. Deploy to production using DEPLOYMENT_CHECKLIST.md" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Push failed. Please check your credentials and try again." -ForegroundColor Red
    Write-Host "   Make sure you're using your Personal Access Token as password" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
Read-Host
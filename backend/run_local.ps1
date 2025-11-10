# PowerShell script to run TriModal XAI backend locally

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  🚀 TriModal XAI - Local Server" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if in correct directory
if (-not (Test-Path "app.py")) {
    Write-Host "❌ Error: app.py not found!" -ForegroundColor Red
    Write-Host "   Please run this script from the backend directory`n" -ForegroundColor Yellow
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created!`n" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check if dependencies are installed
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

Write-Host "✅ Dependencies installed!`n" -ForegroundColor Green

# Start the server
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🎉 Starting FastAPI Server..." -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "📖 API Documentation: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "❤️  Health Check:     " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/health" -ForegroundColor Cyan

Write-Host "🏠 Home:              " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/`n" -ForegroundColor Cyan

Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

# Start uvicorn with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

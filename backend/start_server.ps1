#!/usr/bin/env pwsh
# Startup script for TriModal XAI Backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TriModal XAI Backend Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if uv is installed
Write-Host "Checking for uv installation..." -ForegroundColor Yellow
$uvInstalled = Get-Command uv -ErrorAction SilentlyContinue

if (-not $uvInstalled) {
    Write-Host "❌ uv is not installed!" -ForegroundColor Red
    Write-Host "Installing uv..." -ForegroundColor Yellow
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

Write-Host "✅ uv is installed" -ForegroundColor Green

# Check if dependencies are installed
Write-Host ""
Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
uv sync

Write-Host ""
Write-Host "✅ Dependencies ready" -ForegroundColor Green

# Check for required files
Write-Host ""
Write-Host "Checking for required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "best_model.keras",
    "knowledge_db.json",
    "app.py",
    "preprocessing.py",
    "model_utils.py",
    "xai.py",
    "knowledge_utils.py"
)

$allFilesPresent = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file (missing!)" -ForegroundColor Red
        $allFilesPresent = $false
    }
}

if (-not $allFilesPresent) {
    Write-Host ""
    Write-Host "⚠️  Some required files are missing!" -ForegroundColor Yellow
    Write-Host "Please ensure all files are in the backend directory." -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# Start the server
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting FastAPI Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Server will be available at:" -ForegroundColor Green
Write-Host "   http://localhost:8000" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/docs (Swagger UI)" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/redoc (ReDoc)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000

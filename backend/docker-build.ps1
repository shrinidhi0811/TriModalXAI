#!/usr/bin/env pwsh
# Docker Build and Test Script for Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TriModal XAI - Docker Build & Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue

if (-not $dockerInstalled) {
    Write-Host "❌ Docker is not installed!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Docker is installed" -ForegroundColor Green
docker --version

Write-Host ""
Write-Host "Building Docker image..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes on first build..." -ForegroundColor Gray

# Build the image
docker build -t trimodal-xai-backend:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Docker image built successfully!" -ForegroundColor Green

# Check if container is already running
$existingContainer = docker ps -a --filter "name=trimodal-backend" --format "{{.Names}}"

if ($existingContainer) {
    Write-Host ""
    Write-Host "Stopping and removing existing container..." -ForegroundColor Yellow
    docker stop trimodal-backend 2>$null
    docker rm trimodal-backend 2>$null
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Container" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Container will be available at:" -ForegroundColor Green
Write-Host "   http://localhost:8000" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/docs (Swagger UI)" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/health (Health Check)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the container" -ForegroundColor Yellow
Write-Host ""

# Run the container
docker run --name trimodal-backend -p 8000:8000 trimodal-xai-backend:latest

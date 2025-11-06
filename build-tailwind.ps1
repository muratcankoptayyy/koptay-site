# Tailwind CSS Build Script for Tevkil
# This script compiles and optimizes Tailwind CSS

Write-Host "Building Tailwind CSS..." -ForegroundColor Cyan

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js not found! Please install Node.js from: https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Create package.json if it doesn't exist
if (-not (Test-Path "package.json")) {
    Write-Host "Creating package.json..." -ForegroundColor Yellow
    
    $packageJson = @{
        name = "tevkil-platform"
        version = "1.0.0"
        description = "Tevkil - Avukat Bul ve Ilan Paylas Platformu"
        scripts = @{
            "build:css" = "tailwindcss -i ./static/css/tailwind-input.css -o ./static/css/tailwind-output.css --minify"
            "watch:css" = "tailwindcss -i ./static/css/tailwind-input.css -o ./static/css/tailwind-output.css --watch"
        }
        devDependencies = @{
            "tailwindcss" = "^3.4.1"
        }
    } | ConvertTo-Json -Depth 10
    
    $packageJson | Out-File -FilePath "package.json" -Encoding utf8
    Write-Host "package.json created" -ForegroundColor Green
}

# Install npm packages if node_modules doesn't exist
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: npm install failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "npm packages installed" -ForegroundColor Green
}

# Tailwind CSS'i build et
Write-Host "Building Tailwind CSS..." -ForegroundColor Yellow
npm run build:css

if ($LASTEXITCODE -eq 0) {
    $outputSize = (Get-Item "static/css/tailwind-output.css").Length / 1KB
    Write-Host "SUCCESS! Tailwind CSS built successfully! Size: $outputSize KB" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next: Update base.html to use compiled CSS instead of CDN" -ForegroundColor Cyan
    Write-Host "   OLD: <link href='https://cdn.tailwindcss.com' rel='stylesheet'>" -ForegroundColor Red
    Write-Host "   NEW: <link href=`"{{ url_for('static', filename='css/tailwind-output.css') }}`" rel='stylesheet'>" -ForegroundColor Green
    Write-Host ""
    Write-Host "Size reduction: ~300KB -> $outputSize KB" -ForegroundColor Yellow
} else {
    Write-Host "ERROR: Tailwind CSS build failed!" -ForegroundColor Red
    exit 1
}

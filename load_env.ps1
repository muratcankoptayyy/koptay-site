# ================================================================
# LOAD ENVIRONMENT VARIABLES - Quick Fix
# ================================================================

Write-Host "`nLoading environment variables from registry..." -ForegroundColor Cyan

# Reload User Environment Variables
$userPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
$env:PATH = "$userPath;$env:PATH"

$env:JAVA_HOME = [System.Environment]::GetEnvironmentVariable('JAVA_HOME', 'User')
$env:ANDROID_HOME = [System.Environment]::GetEnvironmentVariable('ANDROID_HOME', 'User')

Write-Host "Done! Environment variables loaded.`n" -ForegroundColor Green

# Show what was loaded
Write-Host "JAVA_HOME = $env:JAVA_HOME" -ForegroundColor Yellow
Write-Host "ANDROID_HOME = $env:ANDROID_HOME" -ForegroundColor Yellow
Write-Host "`nNow run: .\verify_setup.ps1`n" -ForegroundColor Cyan

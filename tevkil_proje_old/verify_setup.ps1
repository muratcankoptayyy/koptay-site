# ================================================================
# TEVKIL MOBILE APP - SETUP VERIFICATION SCRIPT
# ================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "     FINAL VERIFICATION - NEW POWERSHELL" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$allOk = $true

# 1. Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "   [OK] Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Node.js not found!" -ForegroundColor Red
    $allOk = $false
}

# 2. npm
Write-Host "`nChecking npm..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version
    Write-Host "   [OK] npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] npm not found!" -ForegroundColor Red
    $allOk = $false
}

# 3. Git
Write-Host "`nChecking Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "   [OK] Git: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Git not found!" -ForegroundColor Red
    $allOk = $false
}

# 4. Java 17
Write-Host "`nChecking Java..." -ForegroundColor Yellow
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    if ($javaVersion -like "*17.0*") {
        Write-Host "   [OK] Java: $javaVersion" -ForegroundColor Green
    } else {
        Write-Host "   [WARNING] Java: $javaVersion (not version 17!)" -ForegroundColor Yellow
        $allOk = $false
    }
} catch {
    Write-Host "   [ERROR] Java not found!" -ForegroundColor Red
    $allOk = $false
}

# 5. JAVA_HOME
Write-Host "`nChecking JAVA_HOME..." -ForegroundColor Yellow
if ($env:JAVA_HOME) {
    Write-Host "   [OK] JAVA_HOME: $env:JAVA_HOME" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] JAVA_HOME not set!" -ForegroundColor Red
    $allOk = $false
}

# 6. ANDROID_HOME
Write-Host "`nChecking ANDROID_HOME..." -ForegroundColor Yellow
if ($env:ANDROID_HOME) {
    Write-Host "   [OK] ANDROID_HOME: $env:ANDROID_HOME" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] ANDROID_HOME not set!" -ForegroundColor Red
    $allOk = $false
}

# 7. adb
Write-Host "`nChecking Android Debug Bridge (adb)..." -ForegroundColor Yellow
try {
    $adbVersion = adb --version 2>&1 | Select-Object -First 1
    Write-Host "   [OK] adb: $adbVersion" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] adb not found (not in PATH)!" -ForegroundColor Red
    $allOk = $false
}

# RESULTS
Write-Host "`n========================================" -ForegroundColor Gray

if ($allOk) {
    Write-Host "`nCONGRATULATIONS! ALL REQUIREMENTS READY!" -ForegroundColor Green
    Write-Host "`nNEXT STEP - CAPACITOR SETUP:" -ForegroundColor Cyan
    Write-Host "   python setup_capacitor.py`n" -ForegroundColor White
} else {
    Write-Host "`nSOME ISSUES FOUND!" -ForegroundColor Yellow
    Write-Host "   Please fix the [ERROR] items above`n" -ForegroundColor Yellow
}

Write-Host "========================================`n" -ForegroundColor Gray

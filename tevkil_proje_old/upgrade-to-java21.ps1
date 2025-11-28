# Java 21 LTS Upgrade Script for Windows
# This script helps download and install Java 21 LTS (Eclipse Temurin)

Write-Host "=== Java 21 LTS Upgrade Script ===" -ForegroundColor Cyan
Write-Host ""

# Check current Java version
Write-Host "Current Java version:" -ForegroundColor Yellow
java -version 2>&1 | Select-Object -First 1
Write-Host ""

# Check if Java 21 is already installed
$java21Paths = @(
    "C:\Program Files\Eclipse Adoptium\jdk-21.0.5.11-hotspot",
    "C:\Program Files\Java\jdk-21",
    "C:\Program Files\Java\jdk-21.0.5",
    "C:\Program Files\Microsoft\jdk-21.0.5.11-hotspot"
)

$java21Found = $false
foreach ($path in $java21Paths) {
    if (Test-Path $path) {
        Write-Host "Java 21 found at: $path" -ForegroundColor Green
        $java21Found = $true
        $java21Path = $path
        break
    }
}

if (-not $java21Found) {
    Write-Host "Java 21 LTS not found on this system" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Java 21 LTS using one of these options:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 1 - Eclipse Temurin (Recommended for free use):" -ForegroundColor Cyan
    Write-Host "  Download from: https://adoptium.net/temurin/releases/?version=21"
    Write-Host "  - Select: Windows x64 MSI installer"
    Write-Host "  - During installation, check 'Set JAVA_HOME' and 'Add to PATH'"
    Write-Host ""
    Write-Host "Option 2 - Microsoft Build of OpenJDK:" -ForegroundColor Cyan
    Write-Host "  Download from: https://learn.microsoft.com/en-us/java/openjdk/download#openjdk-21"
    Write-Host "  - Select: Windows x64 MSI"
    Write-Host ""
    Write-Host "Option 3 - Oracle JDK 21:" -ForegroundColor Cyan
    Write-Host "  Download from: https://www.oracle.com/java/technologies/downloads/#java21"
    Write-Host "  - Select: Windows x64 Installer"
    Write-Host "  - Note: Requires Oracle account for production use"
    Write-Host ""
    
    $response = Read-Host "Would you like to open the download page in your browser? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Start-Process "https://adoptium.net/temurin/releases/?version=21"
    }
    
    Write-Host ""
    Write-Host "After installing Java 21, run this script again to complete the setup." -ForegroundColor Yellow
    exit
}

# Update gradle.properties
Write-Host ""
Write-Host "Updating gradle.properties with Java 21 path..." -ForegroundColor Yellow

$gradlePropsPath = Join-Path $PSScriptRoot "android\gradle.properties"
if (Test-Path $gradlePropsPath) {
    $content = Get-Content $gradlePropsPath -Raw
    
    # Escape backslashes for Java path
    $escapedPath = $java21Path -replace '\\', '\\'
    
    # Update or add the org.gradle.java.home property
    if ($content -match 'org\.gradle\.java\.home=') {
        # Uncomment if commented
        $content = $content -replace '#\s*org\.gradle\.java\.home=.*', "org.gradle.java.home=$escapedPath"
    } else {
        # Add the property
        $content += "`norg.gradle.java.home=$escapedPath`n"
    }
    
    Set-Content $gradlePropsPath -Value $content
    Write-Host "Updated gradle.properties" -ForegroundColor Green
} else {
    Write-Host "gradle.properties not found at: $gradlePropsPath" -ForegroundColor Red
}

# Verify Gradle build
Write-Host ""
Write-Host "Testing Gradle with Java 21..." -ForegroundColor Yellow
Push-Location "android"

try {
    if (Test-Path ".\gradlew.bat") {
        Write-Host "Running: .\gradlew.bat --version" -ForegroundColor Cyan
        & .\gradlew.bat --version
        
        Write-Host ""
        $response = Read-Host "Would you like to run a clean build to verify everything works? (y/n)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Write-Host "Running: .\gradlew.bat clean assembleDebug" -ForegroundColor Cyan
            & .\gradlew.bat clean assembleDebug
        }
    } else {
        Write-Host "gradlew.bat not found" -ForegroundColor Red
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "=== Upgrade Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open Android Studio"
Write-Host "2. Go to: File -> Project Structure -> SDK Location"
Write-Host "3. Set JDK location to: $java21Path"
Write-Host "4. Go to: File -> Settings -> Build Tools -> Gradle"
Write-Host "5. Set Gradle JDK to: '21'"
Write-Host "6. Click: File -> Invalidate Caches / Restart"
Write-Host ""

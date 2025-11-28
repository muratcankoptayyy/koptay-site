# UTAP Mobil Uygulama - Build ve Test Komuları

# Flutter bağımlılıklarını yükle
Write-Host "Flutter paketleri yükleniyor..." -ForegroundColor Cyan
flutter pub get

if ($LASTEXITCODE -ne 0) {
    Write-Host "Hata: Paket yüklemesi başarısız!" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Paketler başarıyla yüklendi!" -ForegroundColor Green

# Kullanılabilir cihazları göster
Write-Host "`n📱 Kullanılabilir cihazlar:" -ForegroundColor Cyan
flutter devices

# Kullanıcıya seçenek sun
Write-Host "`nNe yapmak istersiniz?" -ForegroundColor Yellow
Write-Host "1. Debug modda çalıştır (Emulator)"
Write-Host "2. Release APK oluştur"
Write-Host "3. Debug APK oluştur"
Write-Host "4. Çıkış"

$choice = Read-Host "`nSeçiminiz (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`n🚀 Debug modda başlatılıyor..." -ForegroundColor Cyan
        flutter run
    }
    "2" {
        Write-Host "`n📦 Release APK oluşturuluyor..." -ForegroundColor Cyan
        flutter build apk --release
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Release APK oluşturuldu!" -ForegroundColor Green
            Write-Host "Konum: build\app\outputs\flutter-apk\app-release.apk" -ForegroundColor Yellow
            
            # APK dosyasını göster
            $apkPath = "build\app\outputs\flutter-apk\app-release.apk"
            if (Test-Path $apkPath) {
                $apkSize = (Get-Item $apkPath).Length / 1MB
                Write-Host "Boyut: $([math]::Round($apkSize, 2)) MB" -ForegroundColor Yellow
                
                # Dosyayı Explorer'da göster
                $openExplorer = Read-Host "`nDosyayı Explorer'da açmak ister misiniz? (E/H)"
                if ($openExplorer -eq "E" -or $openExplorer -eq "e") {
                    explorer.exe /select,"$PWD\$apkPath"
                }
            }
        } else {
            Write-Host "`n❌ APK oluşturulamadı!" -ForegroundColor Red
        }
    }
    "3" {
        Write-Host "`n📦 Debug APK oluşturuluyor..." -ForegroundColor Cyan
        flutter build apk --debug
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Debug APK oluşturuldu!" -ForegroundColor Green
            Write-Host "Konum: build\app\outputs\flutter-apk\app-debug.apk" -ForegroundColor Yellow
        }
    }
    "4" {
        Write-Host "`nÇıkılıyor..." -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host "`n❌ Geçersiz seçim!" -ForegroundColor Red
        exit 1
    }
}

# 🔧 Java 17 ve Android Studio Kurulum Talimatları

## ☕ JAVA 17 KURULUMU

### İndirme Tamamlandıktan Sonra:

1. **İndirilen .msi dosyasını çalıştırın**
   - Dosya adı: `OpenJDK17U-jdk_x64_windows_hotspot_17.x.x.msi`
   - Genelde: `C:\Users\KOPTAY\Downloads\` klasöründe

2. **Kurulum Wizard'ı:**
   - **Welcome** → `Next`
   - **Custom Setup** → ÖNEMLİ: `Set JAVA_HOME variable` seçeneğini **WILL BE INSTALLED** olarak değiştirin
   - **Custom Setup** → ÖNEMLİ: `Add to PATH` seçeneğini **WILL BE INSTALLED** olarak değiştirin
   - **Ready to Install** → `Install`
   - **Administrator** izni istesin → `Yes`
   - **Finish** → `Finish`

3. **Doğrulama (Kurulum bittikten sonra):**
   ```powershell
   # YENİ PowerShell penceresi açın (eski kapatıp yeni açın!)
   java -version
   # Çıktı: openjdk version "17.0.x" görmelisiniz
   
   $env:JAVA_HOME
   # Çıktı: C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot\
   ```

---

## 📱 ANDROID STUDIO KURULUMU

### İndirme Tamamlandıktan Sonra:

1. **İndirilen .exe dosyasını çalıştırın**
   - Dosya adı: `android-studio-2024.x.x.xx-windows.exe`
   - Genelde: `C:\Users\KOPTAY\Downloads\` klasöründe

2. **Kurulum Wizard'ı (1. Adım):**
   - **Welcome** → `Next`
   - **Choose Components:**
     - [x] Android Studio
     - [x] Android Virtual Device
     - `Next`
   - **Configuration Settings:**
     - Kurulum yeri: Varsayılan (C:\Program Files\Android\Android Studio)
     - `Next`
   - **Choose Start Menu Folder:** Varsayılan → `Install`
   - **Administrator** izni → `Yes`
   - Kurulum başlayacak (5-10 dakika)
   - **Installation Complete** → `Next`
   - **Completing Setup** → [x] Start Android Studio → `Finish`

3. **İlk Açılış (Setup Wizard - 2. Adım):**

   **a) Import Settings:**
   - "Do not import settings" seçin → `OK`

   **b) Data Sharing:**
   - "Don't send" veya "Send" (tercihiniz) → `Continue`

   **c) Welcome:**
   - `Next`

   **d) Install Type:**
   - **ÖNEMLİ:** `Standard` seçin (Recommended)
   - `Next`

   **e) Select UI Theme:**
   - `Darcula` (koyu) veya `Light` (açık) seçin
   - `Next`

   **f) Verify Settings:**
   ```
   SDK Folder: C:\Users\KOPTAY\AppData\Local\Android\Sdk
   SDK Components:
   - Android SDK Build-Tools
   - Android Emulator
   - Android SDK Platform-Tools
   - Intel x86 Emulator Accelerator (HAXM)
   ```
   - Kontrol edin → `Next`

   **g) License Agreement:**
   - **android-sdk-license** → `Accept`
   - **android-sdk-arm-dbt-license** → `Accept`
   - Diğer tüm lisanslar → `Accept`
   - `Finish`

   **h) Downloading Components:**
   - SDK Platform-Tools, Emulator vb. indirilecek (1-2 GB)
   - İnternet hızınıza göre 10-20 dakika sürebilir
   - ☕ Kahve molası verilebilir
   - **Finish** görünce → `Finish`

4. **SDK Manager Ayarları (3. Adım - Önemli!):**

   Android Studio açıldıktan sonra:

   **a) SDK Manager'ı Açın:**
   - Ana ekranda **More Actions** (3 nokta) → `SDK Manager`
   - VEYA: **File** → **Settings** → **Languages & Frameworks** → **Android SDK**

   **b) SDK Platforms Tab:**
   - Şunları seçin (checkbox):
     - [x] **Android 14.0 ("UpsideDownCake")** - API Level 34
     - [x] **Android 13.0 ("Tiramisu")** - API Level 33
     - [x] **Android 12.0 ("S")** - API Level 31
   - Sağ altta: `Apply` → `OK`
   - Onayda: `OK`
   - İndirme başlayacak (2-3 GB, 10-15 dk)

   **c) SDK Tools Tab:**
   - Sağ altta: [x] `Show Package Details` işaretleyin
   - Şunları kontrol edin (zaten seçili olmalı):
     - [x] Android SDK Build-Tools (en yeni versiyon)
     - [x] Android SDK Command-line Tools (latest)
     - [x] Android Emulator
     - [x] Android SDK Platform-Tools
     - [x] Intel x86 Emulator Accelerator (HAXM)
   - `Apply` → `OK` (eğer değişiklik yaptıysanız)

5. **Environment Variables Ayarlama:**

   **PowerShell'de (Admin olarak):**
   ```powershell
   # ANDROID_HOME ayarla
   [System.Environment]::SetEnvironmentVariable('ANDROID_HOME', 'C:\Users\KOPTAY\AppData\Local\Android\Sdk', 'User')
   
   # PATH'e platform-tools ekle
   $currentPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
   $newPath = "$currentPath;C:\Users\KOPTAY\AppData\Local\Android\Sdk\platform-tools;C:\Users\KOPTAY\AppData\Local\Android\Sdk\tools"
   [System.Environment]::SetEnvironmentVariable('PATH', $newPath, 'User')
   
   Write-Host "✅ Environment variables ayarlandı!" -ForegroundColor Green
   Write-Host "⚠️  PowerShell'i YENİDEN BAŞLATMANIZ gerekiyor!" -ForegroundColor Yellow
   ```

6. **Doğrulama (YENİ PowerShell'de):**
   ```powershell
   # PowerShell'i KAPAT ve YENİ PowerShell aç
   
   $env:ANDROID_HOME
   # Çıktı: C:\Users\KOPTAY\AppData\Local\Android\Sdk
   
   adb --version
   # Çıktı: Android Debug Bridge version 1.x.x
   ```

---

## ✅ TÜM KURULUMLAR TAMAMLANDI MI KONTROL

### Son Kontrol:
```powershell
# YENİ PowerShell penceresi açın

Write-Host "`n🔍 Kurulum Kontrolü:" -ForegroundColor Cyan

# Node.js
node --version
Write-Host "✅ Node.js: $(node --version)" -ForegroundColor Green

# npm
npm --version
Write-Host "✅ npm: $(npm --version)" -ForegroundColor Green

# Git
git --version
Write-Host "✅ Git: $(git --version)" -ForegroundColor Green

# Java
java -version 2>&1 | Select-String "version"
Write-Host "✅ Java: $((java -version 2>&1 | Select-String 'version').ToString())" -ForegroundColor Green

# Android SDK
if ($env:ANDROID_HOME) {
    Write-Host "✅ Android SDK: $env:ANDROID_HOME" -ForegroundColor Green
} else {
    Write-Host "❌ Android SDK: AYARLI DEĞİL!" -ForegroundColor Red
}

# ADB
try {
    $adbVersion = adb --version 2>&1 | Select-String "version"
    Write-Host "✅ ADB: $adbVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ADB: BULUNAMADI!" -ForegroundColor Red
}

Write-Host "`n🎉 Tüm kurulumlar tamamsa CAPACITOR'a geçebiliriz!`n" -ForegroundColor Yellow
```

---

## 🚨 SORUN GİDERME

### Java version görmüyorsanız:
```powershell
# JAVA_HOME'u manuel ayarlayın
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Eclipse Adoptium\jdk-17.0.9-hotspot', 'User')
```

### ANDROID_HOME görmüyorsanız:
```powershell
# Manuel ayarlayın
[System.Environment]::SetEnvironmentVariable('ANDROID_HOME', 'C:\Users\KOPTAY\AppData\Local\Android\Sdk', 'User')
```

### ADB bulunamıyorsa:
```powershell
# PATH'e manuel ekleyin
$currentPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
$newPath = "$currentPath;C:\Users\KOPTAY\AppData\Local\Android\Sdk\platform-tools"
[System.Environment]::SetEnvironmentVariable('PATH', $newPath, 'User')
```

**HER ENVIRONMENT VARIABLE DEĞİŞİKLİĞİNDEN SONRA:**
- PowerShell'i **KAPAT**
- **YENİ** PowerShell aç
- Kontrol et

---

## 📞 SONRAKI ADIM

Tüm kurulumlar bittiğinde ve kontroller ✅ gösterdiğinde:

```powershell
cd C:\Users\KOPTAY\Desktop\tevkil_proje
python setup_capacitor.py
```

**HEYECANLI OLUN! MOBİL APP'İNİZ HAZIR! 🚀**

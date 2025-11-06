# 📦 Tevkil Mobil App - Gerekli Kurulumlar

## ✅ KONTROL LİSTESİ

### Windows için (Android)
- [ ] Node.js 18+ kurulu
- [ ] Git kurulu
- [ ] Android Studio kurulu
- [ ] Java JDK 17+ kurulu
- [ ] Android SDK Tools kurulu
- [ ] Environment Variables ayarlanmış

### Mac için (iOS - Opsiyonel)
- [ ] Xcode 14+ kurulu
- [ ] CocoaPods kurulu
- [ ] Apple Developer hesabı ($99/yıl)

### Her İkisi İçin
- [ ] Google Play Console hesabı ($25 tek seferlik)
- [ ] Apple Developer hesabı ($99/yıl)
- [ ] App icons hazır (1024x1024 PNG)
- [ ] Screenshots hazır

---

## 🔧 ADIM 1: NODE.JS KURULUMU

### Kurulum:
1. https://nodejs.org adresine gidin
2. **LTS (Long Term Support)** versiyonu indirin (v20.x.x)
3. Installer'ı çalıştırın
4. "Add to PATH" seçeneğini işaretleyin

### Doğrulama:
```powershell
node --version  # v20.x.x görünmeli
npm --version   # 10.x.x görünmeli
```

---

## 🔧 ADIM 2: GIT KURULUMU

### Kurulum:
1. https://git-scm.com/download/win
2. Installer'ı çalıştırın
3. Varsayılan ayarlarla devam edin

### Doğrulama:
```powershell
git --version  # git version 2.x.x
```

---

## 🔧 ADIM 3: ANDROID STUDIO KURULUMU

### Kurulum:
1. https://developer.android.com/studio
2. **Download Android Studio** tıklayın
3. Installer'ı çalıştırın (2-3 GB indirme)
4. İlk açılışta:
   - **Standard** installation seçin
   - Android SDK, SDK Platform, Android Virtual Device otomatik yüklenecek

### SDK Kurulumu:
1. Android Studio açın
2. **More Actions** > **SDK Manager**
3. **SDK Platforms** tab'ında:
   - [x] Android 13.0 (Tiramisu) - API Level 33
   - [x] Android 12.0 (S) - API Level 31
   - [x] Android 11.0 (R) - API Level 30
4. **SDK Tools** tab'ında:
   - [x] Android SDK Build-Tools
   - [x] Android SDK Command-line Tools
   - [x] Android Emulator
   - [x] Android SDK Platform-Tools
5. **Apply** > **OK**

### Environment Variables:
```powershell
# PowerShell'de (Admin olarak):
[System.Environment]::SetEnvironmentVariable('ANDROID_HOME', 'C:\Users\KOPTAY\AppData\Local\Android\Sdk', 'User')
[System.Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';C:\Users\KOPTAY\AppData\Local\Android\Sdk\platform-tools', 'User')
[System.Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';C:\Users\KOPTAY\AppData\Local\Android\Sdk\tools', 'User')
```

### Doğrulama:
```powershell
# PowerShell'i yeniden başlat, sonra:
$env:ANDROID_HOME  # C:\Users\KOPTAY\AppData\Local\Android\Sdk
adb --version      # Android Debug Bridge version 1.x.x
```

---

## 🔧 ADIM 4: JAVA JDK KURULUMU

### Kurulum:
1. https://adoptium.net/ (Eclipse Temurin)
2. **JDK 17 LTS** indirin (Windows x64 MSI)
3. Installer'ı çalıştırın
4. "Set JAVA_HOME" seçeneğini işaretleyin

### Doğrulama:
```powershell
java -version  # openjdk version "17.0.x"
```

---

## 🔧 ADIM 5: XCODE KURULUMU (iOS İÇİN - MAC GEREKLİ)

### Mac sahibi değilseniz:
- **Seçenek 1:** Mac sahibi arkadaştan yardım alın (1 gün)
- **Seçenek 2:** Cloud Mac kiralayın (MacStadium, $50/ay)
- **Seçenek 3:** Önce Android'i yayınlayın, iOS'u sonra ekleyin

### Mac'iniz varsa:
1. App Store'dan **Xcode** indirin (14+ GB)
2. Terminal'de:
   ```bash
   xcode-select --install
   sudo gem install cocoapods
   pod --version  # 1.x.x
   ```

---

## 💳 ADIM 6: DEVELOPER HESAPLARI

### Google Play Console (Android):
1. https://play.google.com/console
2. **Create Account** > **Developer**
3. **$25 tek seferlik ödeme** (kredi kartı)
4. Kimlik doğrulama (1-2 gün sürebilir)

### Apple Developer (iOS):
1. https://developer.apple.com
2. **Account** > **Join Apple Developer Program**
3. **$99/yıl ödeme**
4. Kimlik doğrulama (1-2 gün)

---

## 🎨 ADIM 7: APP ASSETS HAZIRLIĞI

### App Icon (Zorunlu):
- **1024x1024 PNG** (şeffaf arka plan YOK)
- Köşeler kare (sistem otomatik yuvarlatır)
- https://www.figma.com veya Canva ile oluşturun

### Splash Screen (Opsiyonel):
- **2732x2732 PNG** (iPad Pro için)
- Merkezde logo (güvenli alan: 1200x1200)

### Screenshots (Store için):
**Android (Play Store):**
- 5.5" Phone: 1080x1920 (en az 2 adet)
- 7" Tablet: 1200x1920 (opsiyonel)

**iOS (App Store):**
- 6.5" iPhone: 1242x2688 (en az 3 adet)
- 12.9" iPad: 2048x2732 (opsiyonel)

**İpucu:** Capacitor ile app'i çalıştırıp screenshot alın

---

## ✅ KURULUM DOĞRULAMA

### Hepsini test edin:
```powershell
# PowerShell'de:
node --version
npm --version
git --version
java -version
$env:ANDROID_HOME
adb --version

# Eğer hepsi çalışıyorsa:
Write-Host "✅ Tüm gereksinimler hazır!" -ForegroundColor Green
```

---

## 🚨 SIK KARŞILAŞILAN SORUNLAR

### "adb: command not found"
```powershell
# PATH'e manuel ekleyin:
[System.Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';C:\Users\KOPTAY\AppData\Local\Android\Sdk\platform-tools', 'User')
# PowerShell'i yeniden başlatın
```

### "JAVA_HOME not set"
```powershell
# Manuel ayarlayın:
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot', 'User')
```

### "Android licenses not accepted"
```powershell
# Terminal'de:
cd $env:ANDROID_HOME\tools\bin
.\sdkmanager --licenses
# Her satırda 'y' basın
```

---

## 📞 SONRAKI ADIM

Tüm kurulumlar tamamlandıktan sonra:
```powershell
cd C:\Users\KOPTAY\Desktop\tevkil_proje
# Capacitor kurulumuna geçeceğiz
```

**Hazır olduğunuzda bana bildirin!** ✅

# Keystore oluşturma için komutlar ve yapılandırma

## 1) KEYSTORE OLUŞTURMA (PowerShell'de çalıştır)

```powershell
# JDK keytool ile release keystore oluştur
keytool -genkeypair `
  -v `
  -keystore $env:USERPROFILE\tevkil-release-key.jks `
  -alias tevkil-key-alias `
  -keyalg RSA `
  -keysize 2048 `
  -validity 10000 `
  -storepass "GÜÇLÜ_ŞİFRE_BURAYA" `
  -keypass "GÜÇLÜ_ŞİFRE_BURAYA" `
  -dname "CN=Koptay, OU=Development, O=Tevkil, L=Istanbul, ST=Istanbul, C=TR"
```

**ÖNEMLİ:** 
- `GÜÇLÜ_ŞİFRE_BURAYA` yerine gerçek şifre yazın (min 6 karakter)
- Şifreyi güvenli yerde saklayın (LastPass, 1Password vb.)
- `tevkil-release-key.jks` dosyasını **yedekleyin** (kaybolursa uygulama güncellenemez!)

---

## 2) GRADLE SIGNING CONFIG (keystore.properties)

Şifreleri kod içinde tutmamak için `keystore.properties` dosyası oluşturun:

**android/keystore.properties** (bu dosyayı .gitignore'a ekleyin!)
```properties
storePassword=GÜÇLÜ_ŞİFRE_BURAYA
keyPassword=GÜÇLÜ_ŞİFRE_BURAYA
keyAlias=tevkil-key-alias
storeFile=C:/Users/KOPTAY/tevkil-release-key.jks
```

---

## 3) GRADLE SIGNING CONFIG (build.gradle)

`android/app/build.gradle` dosyasında `android {}` bloğunun içine ekleyin:

```gradle
android {
    // ... existing config

    // Keystore properties yükle
    def keystorePropertiesFile = rootProject.file("keystore.properties")
    def keystoreProperties = new Properties()
    if (keystorePropertiesFile.exists()) {
        keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
    }

    signingConfigs {
        release {
            if (keystorePropertiesFile.exists()) {
                keyAlias keystoreProperties['keyAlias']
                keyPassword keystoreProperties['keyPassword']
                storeFile file(keystoreProperties['storeFile'])
                storePassword keystoreProperties['storePassword']
            }
        }
    }

    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }

    // ... rest of config
}
```

---

## 4) .GITIGNORE GÜNCELLEMESI

`android/.gitignore` dosyasına ekleyin:
```
keystore.properties
*.jks
*.keystore
```

---

## 5) AAB BUILD KOMUTLARI

### Manuel Build (PowerShell):
```powershell
# 1. Web assets'leri Capacitor'a kopyala
npx cap copy android

# 2. Android projesine git
cd android

# 3. Release AAB oluştur (signed)
.\gradlew bundleRelease

# 4. Çıktı dosyası:
# android/app/build/outputs/bundle/release/app-release.aab
```

### Otomatik Script (opsiyonel):
`build-release.ps1` oluştur:
```powershell
# Tevkil AAB Build Script
Write-Host "📦 Tevkil AAB Build başlatılıyor..." -ForegroundColor Cyan

# Web build (eğer varsa)
# npm run build

# Capacitor sync
Write-Host "🔄 Capacitor sync..." -ForegroundColor Yellow
npx cap copy android
npx cap sync android

# Android build
Write-Host "🏗️ Android AAB build..." -ForegroundColor Yellow
cd android
.\gradlew clean bundleRelease

# Sonuç
$aabPath = "app\build\outputs\bundle\release\app-release.aab"
if (Test-Path $aabPath) {
    Write-Host "✅ AAB başarıyla oluşturuldu!" -ForegroundColor Green
    Write-Host "📍 Konum: android\$aabPath" -ForegroundColor Cyan
    
    # Dosya boyutu
    $size = (Get-Item $aabPath).Length / 1MB
    Write-Host "📦 Boyut: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan
} else {
    Write-Host "❌ AAB oluşturulamadı!" -ForegroundColor Red
}

cd ..
```

Çalıştırma:
```powershell
.\build-release.ps1
```

---

## 6) AAB DOĞRULAMA

```powershell
# AAB içeriğini görüntüle (opsiyonel)
cd android
.\gradlew :app:validateReleaseBundle

# APK'ya dönüştür (lokal test için)
bundletool build-apks --bundle=app\build\outputs\bundle\release\app-release.aab --output=app-release.apks --mode=universal
```

---

## 7) PLAY CONSOLE'A YÜKLEME

1. Play Console → Production → Internal testing (veya Closed testing)
2. "Create new release" tıklayın
3. AAB dosyasını sürükle-bırak
4. Release notes ekleyin:
```
İlk sürüm (v1.0.0)
- Avukat profil sistemi
- İlan oluşturma ve görüntüleme
- Güvenli mesajlaşma
- Harita entegrasyonu
- WhatsApp bildirimleri
- Push notifications
- Koyu/aydınlık tema
```
5. "Save" → "Review release" → "Start rollout to internal testing"

---

## 8) TEST KULLANICILARI EKLEME

1. Play Console → Testing → Internal testing → Testers tab
2. Email listesi oluşturun:
```
test1@example.com
test2@example.com
```
3. "Save changes"
4. "Copy link" → Test kullanıcılarına opt-in linkini gönderin

---

## 9) PRODUCTION YAYINI

Internal test başarılı olursa:
1. Internal testing → "Promote release" → Production
2. Kademeli rollout seçin: %10 → %25 → %50 → %100
3. Her aşamada 2-3 gün bekleyin, crash reports izleyin

---

## ⚠️ ÖNEMLİ HATIRLATMALAR

1. **Keystore yedekleme:** `tevkil-release-key.jks` dosyasını güvenli yerde saklayın (Google Drive, OneDrive, USB)
2. **Şifre yedekleme:** Keystore şifresini şifre yöneticisinde saklayın
3. **Version artırma:** Her yeni yayında `versionCode` ve `versionName` artırın
4. **Test:** AAB'yi internal test'e yüklemeden önce lokal APK ile test edin
5. **.gitignore:** `keystore.properties` ve `*.jks` dosyalarını asla commit etmeyin
6. **Play App Signing:** Play Console'da Play App Signing'i aktifleştirin (Google anahtarınızı yedekler)

---

## 🔗 YARDIMCI BAĞLANTILAR

- Keystore kaybı durumunda: https://support.google.com/googleplay/android-developer/answer/7384423
- Play App Signing: https://support.google.com/googleplay/android-developer/answer/9842756
- AAB formatı: https://developer.android.com/guide/app-bundle

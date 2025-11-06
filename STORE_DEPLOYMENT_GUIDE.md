# 🚀 Tevkil Mobil App - Her İki Store İçin Tam Rehber

## ✅ HAZIRLIK (1-2 SAAT)

### Adım 1: Gereksinimleri Yükleyin

**Sırayla kurun:**
1. Node.js: https://nodejs.org (LTS version)
2. Git: https://git-scm.com/download/win
3. Android Studio: https://developer.android.com/studio
4. Java JDK 17: https://adoptium.net/

**Doğrulama:**
```powershell
node --version  # v20.x.x
npm --version   # 10.x.x
git --version   # 2.x.x
java -version   # 17.x.x
```

Detaylı kurulum: `SETUP_REQUIREMENTS.md` dosyasına bakın

---

## 🤖 ANDROID APP (2-3 SAAT)

### Adım 1: Capacitor Otomatik Kurulum

```powershell
cd C:\Users\KOPTAY\Desktop\tevkil_proje
python setup_capacitor.py
```

**Bu script:**
- ✅ Capacitor paketlerini yükler
- ✅ Android platformu ekler
- ✅ Config dosyalarını oluşturur
- ✅ Projeyi senkronize eder

### Adım 2: Android Studio'da Açın

```powershell
npm run android:build
```

**Veya manuel:**
```powershell
npx cap open android
```

Android Studio açılacak (ilk açılış 5-10 dk sürebilir)

### Adım 3: APK Build

**Android Studio'da:**
1. Üstte **Build** menüsü
2. **Build Bundle(s) / APK(s)**
3. **Build APK(s)**
4. Build tamamlanınca: **locate** tıklayın
5. APK hazır: `android/app/build/outputs/apk/debug/app-debug.apk`

### Adım 4: Test

**Telefonda test:**
1. Telefonu USB ile bağlayın
2. **Developer Options** > **USB Debugging** açın
3. Android Studio'da **Run** (▶️) tıklayın
4. Telefonunuzu seçin
5. App yüklenecek ve açılacak

**Emulator'da test:**
1. Android Studio'da **Device Manager**
2. **Create Device** > **Pixel 5** seçin
3. **Run** (▶️) tıklayın

### Adım 5: Release APK (Store için)

**1. Signing Key Oluştur:**
```powershell
cd android/app
keytool -genkey -v -keystore tevkil-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias tevkil
```

**Şifre girin ve saklayin!**

**2. Gradle Config:**

`android/app/build.gradle` düzenleyin:
```gradle
android {
    ...
    signingConfigs {
        release {
            storeFile file('tevkil-release-key.jks')
            storePassword 'ŞİFRENİZ'
            keyAlias 'tevkil'
            keyPassword 'ŞİFRENİZ'
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

**3. Release Build:**
```powershell
cd android
.\gradlew assembleRelease
```

Release APK: `android/app/build/outputs/apk/release/app-release.apk`

### Adım 6: Play Store'a Yükleme

**1. Play Console'a girin:**
https://play.google.com/console

**2. Create App:**
- App name: Tevkil
- Default language: Turkish
- App type: App
- Free/Paid: Free

**3. Store Listing:**
- **Short description** (80 karakter):
  ```
  Avukatlar arası iş devri ve tevkil platformu. Hızlı, güvenli, kolay.
  ```

- **Full description** (4000 karakter):
  ```
  Tevkil, avukatlar arasında iş devri ve tevkil süreçlerini kolaylaştıran modern bir platformdur.
  
  ÖZELLİKLER:
  • İlan Paylaşımı: İş devri ve tevkil ilanlarınızı hızlıca yayınlayın
  • Anlık Mesajlaşma: Diğer avukatlarla gerçek zamanlı iletişim
  • Harita Görünümü: Size yakın avukatları haritada görün
  • Güvenli Platform: Kimlik doğrulama ve güvenlik önlemleri
  • Değerlendirme Sistemi: Güvenilir avukatları referanslarla bulun
  
  NASIL ÇALIŞIR:
  1. Ücretsiz hesap oluşturun
  2. İlan paylaşın veya ilanları inceleyin
  3. İlgilendiğiniz avukatlarla mesajlaşın
  4. İş devrini güvenle gerçekleştirin
  
  Avukatlar için, avukatlar tarafından geliştirildi.
  ```

- **App icon:** 512x512 PNG yükleyin
- **Feature graphic:** 1024x500 PNG
- **Screenshots:** En az 2 adet (1080x1920)

**4. App Access:**
- Not restricted

**5. Ads:**
- No (reklam yok)

**6. Content Rating:**
- Questionnaire'i doldurun (PEGI 3)

**7. Target Audience:**
- 18+ (professionals)

**8. Privacy Policy:**
- URL: https://tevkil.fly.dev/privacy (oluşturmalısınız)

**9. App Content:**
- Data safety form doldurun

**10. Release:**
- **Production** > **Create Release**
- APK/AAB yükle: `app-release.apk`
- Release notes:
  ```
  İlk sürüm! Avukatlar arası iş devri platformu.
  - İlan paylaşımı ve arama
  - Anlık mesajlaşma
  - Harita görünümü
  - Profil yönetimi
  ```
- **Review and rollout**

**İnceleme süresi:** 1-3 gün

---

## 🍎 iOS APP (1-2 GÜN - MAC GEREKLİ)

### Ön Gereksinim: Mac

**Seçenekler:**
1. **Kendi Mac'iniz** → İdeal
2. **Mac sahibi arkadaş** → 1 gün ödünç alın
3. **Cloud Mac kirala** → MacStadium ($50/ay)
4. **Sonra yap** → Önce Android'i yayınlayın

### Adım 1: Xcode Kurulumu (Mac'te)

```bash
# App Store'dan Xcode indirin (14+ GB)
xcode-select --install
sudo gem install cocoapods
pod --version
```

### Adım 2: iOS Platformu Ekle (Mac'te)

```bash
cd /Users/.../tevkil_proje
npx cap add ios
npx cap sync
```

### Adım 3: Xcode'da Açın

```bash
npx cap open ios
```

### Adım 4: Signing & Capabilities

**Xcode'da:**
1. **Project Navigator** > **App**
2. **Signing & Capabilities** tab
3. **Team:** Apple Developer hesabınızı seçin
4. **Bundle Identifier:** `com.koptay.tevkil`
5. Xcode otomatik provisioning profile oluşturacak

### Adım 5: Test

**Simulator'da:**
1. Üstte **iPhone 14 Pro** seçin
2. **Run** (▶️) tıklayın
3. Simulator açılacak

**Gerçek iPhone'da:**
1. iPhone'u Mac'e bağlayın
2. iPhone'da **Settings > General > Device Management** > Sertifikayı güvenilir yap
3. Xcode'da iPhone'u seçin
4. **Run** (▶️)

### Adım 6: Archive (Store için)

**1. Archive Oluştur:**
1. **Product** > **Archive**
2. Build tamamlanınca **Organizer** açılacak

**2. Distribute:**
1. **Distribute App**
2. **App Store Connect** seçin
3. **Upload** tıklayın
4. Apple'a yüklenecek (5-10 dk)

### Adım 7: App Store Connect

**1. App Store Connect'e girin:**
https://appstoreconnect.apple.com

**2. My Apps > + > New App:**
- Platform: iOS
- Name: Tevkil
- Primary Language: Turkish
- Bundle ID: com.koptay.tevkil
- SKU: tevkil-001

**3. App Information:**
- **Category:** Business / Productivity
- **Privacy Policy URL:** https://tevkil.fly.dev/privacy

**4. Pricing:**
- **Price:** Free

**5. Prepare for Submission:**

**App Store Screenshots:**
- 6.5" iPhone: 1242x2688 (en az 3)
- 5.5" iPhone: 1242x2208 (opsiyonel)
- iPad: 2048x2732 (opsiyonel)

**Promotional Text:**
```
Avukatlar arası iş devri ve tevkil platformu. Hızlı, güvenli, kolay.
```

**Description:**
```
Tevkil, avukatlar arasında iş devri ve tevkil süreçlerini kolaylaştıran modern bir platformdur.

ÖZELLİKLER:
• İlan Paylaşımı: İş devri ve tevkil ilanlarınızı hızlıca yayınlayın
• Anlık Mesajlaşma: Diğer avukatlarla gerçek zamanlı iletişim
• Harita Görünümü: Size yakın avukatları haritada görün
• Güvenli Platform: Kimlik doğrulama ve güvenlik önlemleri
• Değerlendirme Sistemi: Güvenilir avukatları referanslarla bulun

NASIL ÇALIŞIR:
1. Ücretsiz hesap oluşturun
2. İlan paylaşın veya ilanları inceleyin
3. İlgilendiğiniz avukatlarla mesajlaşın
4. İş devrini güvenle gerçekleştirin

Avukatlar için, avukatlar tarafından geliştirildi.
```

**Keywords:**
```
avukat,tevkil,iş devri,hukuk,adliye,lawyer
```

**Support URL:** https://tevkil.fly.dev/support

**6. Build:**
- **Select Build** > Xcode'dan yüklediğiniz build'i seçin

**7. Version Information:**
- **Version:** 1.0
- **Copyright:** 2025 Koptay

**8. App Review Information:**
- **Notes:** İlk sürüm. Test için demo hesap:
  ```
  Email: demo@tevkil.com
  Password: Demo123!
  ```

**9. Submit for Review:**
- **Submit** tıklayın

**İnceleme süresi:** 1-7 gün (Android'den daha katı)

---

## 📱 PUSH NOTIFICATIONS (İKİ PLATFORM İÇİN)

### Firebase Kurulumu

**1. Firebase Console:**
https://console.firebase.google.com

**2. Create Project:**
- Project name: Tevkil
- Google Analytics: Enable

**3. Add Android App:**
- Package name: `com.koptay.tevkil`
- Download `google-services.json`
- Kopyala: `android/app/google-services.json`

**4. Add iOS App:**
- Bundle ID: `com.koptay.tevkil`
- Download `GoogleService-Info.plist`
- Xcode'da projeye ekle (drag & drop)

**5. Cloud Messaging:**
- **Cloud Messaging** > **Web Push certificates** > **Generate key pair**
- VAPID key'i kopyalayın

### Backend Entegrasyonu (app.py)

```python
# app.py'ye ekleyin:

from firebase_admin import credentials, messaging
import firebase_admin

# Firebase başlat
cred = credentials.Certificate('firebase-credentials.json')
firebase_admin.initialize_app(cred)

@app.route('/api/send-notification', methods=['POST'])
@login_required
def send_notification():
    """Push notification gönder"""
    data = request.json
    token = data.get('fcm_token')
    title = data.get('title')
    body = data.get('body')
    
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )
    
    response = messaging.send(message)
    return jsonify({'success': True, 'message_id': response})
```

---

## 🔄 GÜNCELLEME SÜRECİ

### Kod Değişikliği Yaptığınızda:

```powershell
# 1. Backend değişiklikleri deploy et
fly deploy --app tevkil

# 2. Mobil sync
npm run sync

# 3. Android Studio'da build
npm run android:build
# Build > Generate Signed Bundle / APK

# 4. Play Store'a yeni versiyon yükle
# android/app/build.gradle'de versionCode ve versionName arttır
```

---

## 💰 MALİYET ÖZET

| Öğe | Maliyet | Süre |
|-----|---------|------|
| **Google Play Console** | $25 tek seferlik | Ömür boyu |
| **Apple Developer** | $99/yıl | Yıllık |
| **Mac kirala (opsiyonel)** | $0-50 | 1 gün |
| **Firebase (Free Tier)** | $0 | Ömür boyu |
| **TOPLAM (ilk yıl)** | $124-174 | - |
| **TOPLAM (sonraki yıllar)** | $99/yıl | - |

---

## ⏰ ZAMAN ÇİZELGESİ

| Aşama | Süre | Açıklama |
|-------|------|----------|
| **Gereksinim kurulumu** | 1-2 saat | Node, Android Studio, vb. |
| **Capacitor setup** | 30 dk | Otomatik script |
| **Android build** | 1-2 saat | İlk build yavaş |
| **Android test** | 30 dk | Emulator veya telefon |
| **Play Store hazırlık** | 2 saat | Screenshots, açıklama |
| **Play Store onay** | 1-3 gün | Google inceleme |
| **iOS build (Mac)** | 2-3 saat | Xcode + archive |
| **App Store hazırlık** | 2 saat | Metadata |
| **App Store onay** | 1-7 gün | Apple inceleme |
| **TOPLAM** | **7-14 gün** | Store onayları dahil |

---

## ✅ CHECKLIST

### Android:
- [ ] Node.js kurulu
- [ ] Android Studio kurulu
- [ ] `python setup_capacitor.py` çalıştırıldı
- [ ] Android build başarılı
- [ ] APK test edildi
- [ ] Signing key oluşturuldu
- [ ] Release APK build edildi
- [ ] Play Console hesabı açıldı ($25)
- [ ] Screenshots hazırlandı
- [ ] Store listing dolduruldu
- [ ] APK yüklendi
- [ ] İncelemeye gönderildi

### iOS:
- [ ] Mac erişimi var
- [ ] Xcode kurulu
- [ ] Apple Developer hesabı ($99)
- [ ] iOS platformu eklendi
- [ ] Xcode'da build başarılı
- [ ] iPhone'da test edildi
- [ ] Archive oluşturuldu
- [ ] App Store Connect'e yüklendi
- [ ] Screenshots hazırlandı
- [ ] App Store listing dolduruldu
- [ ] İncelemeye gönderildi

---

## 🆘 SORUN GİDERME

### "Gradle build failed"
```powershell
cd android
.\gradlew clean
.\gradlew build
```

### "Android SDK not found"
```powershell
# Environment variable ekle:
$env:ANDROID_HOME = "C:\Users\KOPTAY\AppData\Local\Android\Sdk"
```

### "Capacitor sync failed"
```powershell
# Cache temizle:
rm -r node_modules
npm install
npx cap sync
```

### iOS "Signing failed"
- Xcode > Preferences > Accounts > Apple ID ekle
- Signing & Capabilities > Team seç

---

## 📞 BAŞLAMAK İÇİN

**ŞİMDİ YAPILACAKLAR:**

1. **Gereksinimleri kurun** (1-2 saat):
   ```powershell
   # SETUP_REQUIREMENTS.md'ye bakın
   ```

2. **Capacitor setup** (5 dakika):
   ```powershell
   cd C:\Users\KOPTAY\Desktop\tevkil_proje
   python setup_capacitor.py
   ```

3. **Android Studio'da açın**:
   ```powershell
   npm run android:build
   ```

**HAZIR MISINIZ?** 🚀

Ben her adımda yardımcı olacağım. Başlamak için:
```powershell
python setup_capacitor.py
```

Komutunu çalıştırın!

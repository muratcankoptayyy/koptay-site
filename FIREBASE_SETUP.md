# Firebase Cloud Messaging (FCM) Kurulumu

Bu rehber, Tevkil uygulamasında push notification (anlık bildirimler) çalışması için Firebase Cloud Messaging kurulumunu anlatmaktadır.

## 🔥 Adım 1: Firebase Projesi Oluşturma

1. [Firebase Console](https://console.firebase.google.com) adresine git
2. **"Proje Ekle"** butonuna tıkla
3. Proje adı: `tevkil-platform` (veya istediğin bir isim)
4. Google Analytics'i etkinleştir (opsiyonel)
5. Projeyi oluştur

## 📱 Adım 2: Android Uygulaması Ekleme

1. Firebase Console'da projenize gidin
2. **Android simgesine** tıklayın
3. Uygulama bilgilerini girin:
   - **Android paket adı**: `com.tevkil.app` (capacitor.config.json'dan)
   - **Uygulama takma adı**: Tevkil
   - **SHA-1 sertifikası**: (şimdilik boş bırakabilirsiniz)
4. **"Uygulamayı kaydet"** butonuna tıklayın

## 📥 Adım 3: google-services.json İndirme

1. Firebase Console'dan **`google-services.json`** dosyasını indirin
2. İndirdiğiniz dosyayı şu konuma kopyalayın:
   ```
   android/app/google-services.json
   ```

## 🔑 Adım 4: Service Account Anahtarı Alma (Backend için)

1. Firebase Console → **Proje Ayarları** (⚙️ ikonu)
2. **"Hizmet hesapları"** (Service accounts) sekmesine git
3. **"Yeni özel anahtar oluştur"** butonuna tıkla
4. JSON formatında anahtarı indir
5. Bu JSON dosyasının içeriğini kopyala

## 🔐 Adım 5: Environment Variable Ayarlama

### Lokal Development (.env dosyası)

`.env` dosyanıza şunu ekleyin:

```env
FIREBASE_CREDENTIALS_JSON='{"type":"service_account","project_id":"tevkil-platform","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}'
```

**Not**: Tek satırda, tek tırnaklar içinde olmalı!

### Fly.io Production

```bash
fly secrets set FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'
```

## 📦 Adım 6: Android Build Dependencies

`android/app/build.gradle` dosyasına Firebase dependencies eklendi (zaten mevcut):

```gradle
dependencies {
    implementation 'com.google.firebase:firebase-messaging:23.4.0'
}
```

`android/build.gradle` dosyasına classpath eklendi:

```gradle
buildscript {
    dependencies {
        classpath 'com.google.gms:google-services:4.4.0'
    }
}
```

`android/app/build.gradle` dosyasının en sonuna eklendi:

```gradle
apply plugin: 'com.google.gms.google-services'
```

## 🎨 Adım 7: Notification Icon Oluşturma

Android notification icon'u `android/app/src/main/res/drawable/` klasörüne ekleyin:

- `ic_notification.xml` (vector drawable - beyaz renk, şeffaf arka plan)

## 🧪 Test Etme

### 1. Uygulamayı Çalıştır

```bash
cd android
./gradlew assembleDebug
```

### 2. Backend'i Başlat

```bash
python app.py
```

### 3. Test Notification Gönder

Python console'dan:

```python
from app import send_push_notification

# User ID 1'e test bildirimi gönder
send_push_notification(
    user_id=1,
    title='Test Bildirimi',
    body='Firebase Cloud Messaging çalışıyor! 🎉',
    data={'type': 'test', 'page': '/dashboard'}
)
```

## 🔍 Sorun Giderme

### "No device tokens found"

- Uygulamada login olun
- Push notification izni verildiğinden emin olun
- Device token backend'e kaydedildi mi kontrol edin

### "FIREBASE_CREDENTIALS_JSON not set"

- Environment variable doğru ayarlandı mı kontrol edin
- Tek tırnaklar içinde, tek satırda olmalı
- JSON formatı bozuk mu kontrol edin

### Bildirim Gelmiyor

1. **Firebase Console** → **Cloud Messaging** → **Test notification** ile test edin
2. Uygulama ön planda mı arka planda mı? (Her ikisinde de çalışmalı)
3. Android bildirim izinleri verilmiş mi?
4. `adb logcat | grep FCM` ile logları kontrol edin

## 📚 Faydalı Linkler

- [Firebase Console](https://console.firebase.google.com)
- [FCM Documentation](https://firebase.google.com/docs/cloud-messaging)
- [Capacitor Push Notifications](https://capacitorjs.com/docs/apis/push-notifications)
- [Firebase Admin SDK (Python)](https://firebase.google.com/docs/admin/setup)

## ✅ Kontrol Listesi

- [ ] Firebase projesi oluşturuldu
- [ ] Android uygulaması Firebase'e eklendi
- [ ] `google-services.json` indirildi ve `android/app/` klasörüne kopyalandı
- [ ] Service account JSON anahtarı alındı
- [ ] `FIREBASE_CREDENTIALS_JSON` environment variable ayarlandı
- [ ] Backend'de `firebase-admin` paketi yüklendi (`pip install -r requirements.txt`)
- [ ] Android uygulaması build edildi
- [ ] Test bildirimi başarıyla gönderildi

---

**Not**: Firebase ücretsiz planı (Spark) günde 10,000 bildirim gönderebilir. Daha fazla için Blaze (ödeme) planına geçilmeli.

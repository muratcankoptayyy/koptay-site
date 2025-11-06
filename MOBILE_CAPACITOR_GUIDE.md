# Tevkil Mobil App - Capacitor Kurulum Rehberi

## 🚀 Capacitor ile Native App (iOS + Android)

### Neden Capacitor?
- ✅ PWA kodunuzu olduğu gibi kullanır (0 değişiklik)
- ✅ Flask backend entegrasyonu otomatik
- ✅ SocketIO gerçek zamanlı çalışır
- ✅ Tamamen ücretsiz, open-source
- ✅ Cordova'dan %40 daha hızlı

---

## 📋 Gereksinimler

### Windows için:
- Node.js 16+ (https://nodejs.org)
- Android Studio (https://developer.android.com/studio)
- Git (https://git-scm.com)

### Mac için (iOS için gerekli):
- Xcode 14+
- CocoaPods (`sudo gem install cocoapods`)

---

## 🔧 Adım 1: Capacitor Kurulumu

### 1.1 Proje klasörüne gidin:
```bash
cd C:\Users\KOPTAY\Desktop\tevkil_proje
```

### 1.2 Capacitor yükleyin:
```bash
npm install @capacitor/core @capacitor/cli
npm install @capacitor/android @capacitor/ios
```

### 1.3 Capacitor başlatın:
```bash
npx cap init "Tevkil" "com.koptay.tevkil" --web-dir=static
```

**Açıklama:**
- `Tevkil`: App adı
- `com.koptay.tevkil`: Bundle ID (değiştirin)
- `--web-dir=static`: Flask static klasörü

---

## 🤖 Adım 2: Android App Oluşturma

### 2.1 Android platformu ekleyin:
```bash
npx cap add android
```

### 2.2 Web dosyalarını kopyalayın:
```bash
npx cap copy android
```

### 2.3 Android Studio'da açın:
```bash
npx cap open android
```

### 2.4 Android Studio'da:
1. **Build > Build Bundle(s) / APK(s) > Build APK(s)**
2. APK hazır: `android/app/build/outputs/apk/debug/app-debug.apk`
3. Telefonunuza yükleyin veya Play Store'a gönderin

---

## 🍎 Adım 3: iOS App Oluşturma (Mac Gerekli)

### 3.1 iOS platformu ekleyin:
```bash
npx cap add ios
```

### 3.2 Web dosyalarını kopyalayın:
```bash
npx cap copy ios
```

### 3.3 Xcode'da açın:
```bash
npx cap open ios
```

### 3.4 Xcode'da:
1. **Product > Archive**
2. **Distribute App > App Store Connect**
3. Apple Developer hesabı gerekli ($99/yıl)

---

## 🔄 Adım 4: Backend Entegrasyonu

### 4.1 Flask URL'ini ayarlayın:

**capacitor.config.json** dosyasını düzenleyin:
```json
{
  "appId": "com.koptay.tevkil",
  "appName": "Tevkil",
  "webDir": "static",
  "server": {
    "url": "https://tevkil.fly.dev",
    "cleartext": false,
    "androidScheme": "https"
  },
  "plugins": {
    "PushNotifications": {
      "presentationOptions": ["badge", "sound", "alert"]
    },
    "SplashScreen": {
      "launchShowDuration": 2000,
      "backgroundColor": "#1a56db",
      "showSpinner": false
    }
  }
}
```

### 4.2 CORS ayarları (app.py'de zaten var):
```python
# app.py - satır 52
CORS(app)  # ✅ Mobil app erişimi için
```

---

## 📱 Adım 5: Push Notifications

### 5.1 Plugin yükleyin:
```bash
npm install @capacitor/push-notifications
```

### 5.2 app.py'ye ekleyin:
```python
from flask import request

@app.route('/api/register-device', methods=['POST'])
def register_device():
    """Mobil cihaz FCM token kaydı"""
    data = request.json
    token = data.get('fcm_token')
    user_id = current_user.id if current_user.is_authenticated else None
    
    # Token'ı database'e kaydet
    # TODO: DeviceToken modeli ekle
    
    return jsonify({'success': True})
```

### 5.3 Mobil tarafta (JavaScript):
```javascript
// static/js/mobile-push.js
import { PushNotifications } from '@capacitor/push-notifications';

PushNotifications.requestPermissions().then(result => {
  if (result.receive === 'granted') {
    PushNotifications.register();
  }
});

PushNotifications.addListener('registration', token => {
  // Backend'e gönder
  fetch('/api/register-device', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({fcm_token: token.value})
  });
});
```

---

## 🧪 Adım 6: Test

### Android Test:
1. USB Debug açık telefon bağlayın
2. Android Studio'da **Run** (▶️) tıklayın
3. App telefonda açılır

### iOS Test (Mac):
1. iPhone bağlayın
2. Xcode'da device seçin
3. **Product > Run** (⌘R)

### Local Test:
```bash
# Flask server başlat
python app.py

# Mobil simulator'da test et
npx cap run android  # veya ios
```

---

## 📦 Adım 7: Yayınlama

### Google Play Store:
1. **Play Console** hesabı ($25 tek seferlik)
2. APK/AAB yükle: `android/app/build/outputs/bundle/release/`
3. Metadata (screenshot, açıklama) ekle
4. İnceleme 1-3 gün

### Apple App Store:
1. **Apple Developer** hesabı ($99/yıl)
2. Xcode'dan Archive > Upload
3. App Store Connect'te metadata
4. İnceleme 1-7 gün

---

## 🔥 Bonus: LiveUpdate (Over-The-Air)

Capacitor + Appflow ile app güncelleme **App Store onay beklemeden**:

```bash
npm install @capacitor/live-updates
```

**Nasıl çalışır?**
1. HTML/CSS/JS değişikliği yaptınız
2. `npx cap sync` → backend'e push
3. Kullanıcı app'i açınca otomatik günceller
4. **Native kod değişikliği için App Store gerekli**

---

## 💡 İpuçları

### Hata: "CORS error"
```python
# app.py
CORS(app, resources={
    r"/api/*": {
        "origins": ["capacitor://localhost", "http://localhost", "https://tevkil.fly.dev"]
    }
})
```

### Hata: "Cleartext traffic not allowed"
**android/app/src/main/AndroidManifest.xml**:
```xml
<application
    android:usesCleartextTraffic="true">
```

### iOS Keyboard Sorunları
```json
// capacitor.config.json
{
  "plugins": {
    "Keyboard": {
      "resize": "ionic",
      "style": "dark"
    }
  }
}
```

---

## 📊 Performans Optimizasyonu

### 1. Image Lazy Loading
```html
<!-- templates/ilans.html -->
<img loading="lazy" src="...">
```

### 2. Bundle Size
```bash
# Gereksiz dosyaları exclude et
echo "node_modules/" >> .gitignore
echo "__pycache__/" >> .gitignore
```

### 3. Cache Strategy
Service worker zaten yapıyor (PWA'dan), ek bir şey gerekmez.

---

## 🎯 Özet

| Adım | Süre | Zorluk |
|------|------|--------|
| 1. Kurulum | 15 dk | Kolay |
| 2. Android Build | 30 dk | Orta |
| 3. iOS Build | 1 saat | Zor (Mac gerekli) |
| 4. Backend Entegrasyon | 10 dk | Kolay |
| 5. Push Notifications | 1 saat | Orta |
| 6. Test | 30 dk | Kolay |
| 7. Yayınlama | 2-7 gün | Orta |

**TOPLAM:** Android için 2-3 saat, iOS için +1 gün

---

## 🆘 Sorun mu var?

1. **Capacitor Docs:** https://capacitorjs.com/docs
2. **Ionic Forum:** https://forum.ionicframework.com
3. **Stack Overflow:** `[capacitor]` tag

---

## ✅ Checklist

- [ ] Node.js kurulu
- [ ] Android Studio kurulu (Android için)
- [ ] Xcode kurulu (iOS için, Mac)
- [ ] `npx cap init` başarılı
- [ ] `npx cap add android` başarılı
- [ ] Android Studio'da build başarılı
- [ ] APK oluşturuldu
- [ ] Backend entegrasyonu test edildi
- [ ] Push notifications çalışıyor
- [ ] Play Store'a yüklendi

**Hazırsanız başlayalım! Hangi adımda yardım istersiniz?**

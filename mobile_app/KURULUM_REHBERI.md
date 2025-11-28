# Flutter Mobil Uygulama Kurulum ve Çalıştırma Rehberi

## 📋 Gereksinimler

1. **Flutter SDK** - https://docs.flutter.dev/get-started/install/windows
2. **Android Studio** - https://developer.android.com/studio
3. **Git** - https://git-scm.com/download/win

## 🚀 Adım 1: Flutter Kurulumu

### Flutter SDK İndir ve Kur

```powershell
# 1. Flutter SDK'yı indirin (https://flutter.dev/docs/get-started/install/windows)
# 2. ZIP dosyasını C:\src\ dizinine çıkarın
# 3. PATH'e ekleyin:

# PowerShell Admin olarak:
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "Machine") + ";C:\src\flutter\bin",
    "Machine"
)

# 4. Terminali yeniden başlatın ve kontrol edin:
flutter --version
```

### Flutter Doctor Çalıştır

```powershell
flutter doctor
```

**Çıktı şöyle olmalı:**
```
Doctor summary (to see all details, run flutter doctor -v):
[✓] Flutter (Channel stable, 3.x.x)
[✓] Android toolchain - develop for Android devices
[✓] Chrome - develop for the web
[✓] Android Studio
[✓] VS Code
[✓] Connected device
```

## 🔧 Adım 2: Android Studio Kurulumu

1. **Android Studio İndir ve Kur**
   - https://developer.android.com/studio
   - Varsayılan ayarlarla kurulumu tamamlayın

2. **SDK Kurulumu**
   - Android Studio'yu açın
   - `Tools > SDK Manager`
   - **Android SDK Platform 33** veya üstü yükleyin
   - **Android SDK Build-Tools** yükleyin
   - **Android Emulator** yükleyin

3. **Flutter ve Dart Eklentileri**
   - `File > Settings > Plugins`
   - "Flutter" araştırın ve kurun (Dart otomatik kurulur)

## 📱 Adım 3: Android Emulator Oluşturma

```powershell
# Android Studio'da:
# Tools > Device Manager > Create Device
# Örnek: Pixel 7 - API 33

# Komut satırından da oluşturabilirsiniz:
flutter emulators --create --name pixel_7
```

## 💻 Adım 4: Mobil Uygulamayı Çalıştırma

### Backend API'yi Başlatın

```powershell
cd c:\Users\KOPTAY\Desktop\tevkil_proje

# Sanal ortamı aktifleştirin
.\venv\Scripts\Activate.ps1

# Flask uygulamasını başlatın
python app.py
```

**Backend şu adreste çalışacak:** `http://localhost:5000`

### API Ayarlarını Güncelleyin

`mobile_app\lib\config\api_config.dart` dosyasını düzenleyin:

```dart
static const String baseUrl = 'http://10.0.2.2:5000'; // Emulator için
// static const String baseUrl = 'http://YOUR_LOCAL_IP:5000'; // Fiziksel cihaz için
```

**NOT:** 
- Android Emulator için: `10.0.2.2` = localhost
- Fiziksel Android cihaz için: PC'nizin local IP'sini kullanın (örn: `192.168.1.100`)

### Bağımlılıkları Yükleyin

```powershell
cd mobile_app

# Flutter paketlerini yükle
flutter pub get
```

### Emulator'ü Başlatın

```powershell
# Kullanılabilir emulatorleri listele
flutter emulators

# Emulator başlat
flutter emulators --launch <emulator_id>

# Veya Android Studio'dan başlatın:
# Tools > Device Manager > Play butonu
```

### Uygulamayı Çalıştırın

```powershell
# Debug mode
flutter run

# Veya VS Code'da:
# F5 tuşuna basın
```

## 📦 Adım 5: APK Build (Android Cihaza Yükleme)

### Release APK Oluşturma

```powershell
cd mobile_app

# Release APK build
flutter build apk --release

# APK konumu:
# build\app\outputs\flutter-apk\app-release.apk
```

### APK'yı Cihaza Yükleme

**Yöntem 1: USB Kablo ile**

```powershell
# 1. Android cihazda "Geliştirici Seçenekleri"ni aktifleştirin:
#    Ayarlar > Telefon Hakkında > Yapı Numarası'na 7 kez tıklayın

# 2. USB Hata Ayıklama'yı açın:
#    Ayarlar > Geliştirici Seçenekleri > USB Hata Ayıklama

# 3. USB ile bağlayın ve cihazı kontrol edin:
flutter devices

# 4. APK'yı yükleyin:
flutter install
```

**Yöntem 2: APK Dosyasını Paylaşma**

```powershell
# APK dosyasını telefonunuza atın:
# - USB ile kopyalayın
# - Google Drive/Dropbox ile paylaşın
# - WhatsApp ile gönderin

# Telefonda:
# 1. APK dosyasına tıklayın
# 2. "Bilinmeyen Kaynaklardan Yükleme" izni verin
# 3. Yükle'ye tıklayın
```

## 🔍 Sorun Giderme

### "Unable to connect to backend" Hatası

```powershell
# Backend çalışıyor mu kontrol edin:
curl http://localhost:5000/api/mobile/verify

# Firewall'u kontrol edin - Python'a izin verin
```

### "Gradle build failed" Hatası

```powershell
cd mobile_app\android
.\gradlew clean

cd ..
flutter clean
flutter pub get
```

### Emulator Yavaş

```powershell
# Android Studio'da:
# Tools > Device Manager > Emulator Settings
# - RAM: 4GB
# - Graphics: Hardware
```

### Hot Reload Çalışmıyor

```powershell
# Uygulamayı durdurun ve tekrar çalıştırın:
flutter run
```

## 📱 Fiziksel Cihazda Test

1. **Aynı WiFi Ağına Bağlanın**
   - PC ve telefon aynı ağda olmalı

2. **PC IP Adresinizi Bulun**
   ```powershell
   ipconfig
   # IPv4 Adresi'ni not edin (örn: 192.168.1.100)
   ```

3. **API Config Güncelleyin**
   ```dart
   // lib/config/api_config.dart
   static const String baseUrl = 'http://192.168.1.100:5000';
   ```

4. **Yeniden Build Edin**
   ```powershell
   flutter run
   ```

## ✅ Test Checklist

- [ ] Backend API çalışıyor (`http://localhost:5000`)
- [ ] Flutter doctor başarılı
- [ ] API config doğru (10.0.2.2 veya local IP)
- [ ] Emulator/Cihaz bağlı
- [ ] Bağımlılıklar yüklendi (`flutter pub get`)
- [ ] Uygulama çalıştırıldı (`flutter run`)
- [ ] Login ekranı görünüyor
- [ ] Giriş yapılabiliyor
- [ ] İlanlar listeleniyor

## 📞 Destek

Sorun yaşarsanız:

```powershell
# Flutter detaylı bilgi:
flutter doctor -v

# Uygulamayı verbose mode'da çalıştırın:
flutter run -v

# Logları görüntüleyin:
flutter logs
```

## 🎯 Sonraki Adımlar

✅ Backend API hazır
✅ Mobil uygulama oluşturuldu
✅ Login, Dashboard, Posts, Profile ekranları hazır

**TODO:**
- [ ] Başvuru yönetimi ekranlarını tamamla
- [ ] Mesajlaşma ekranlarını tamamla
- [ ] Bildirim sistemi
- [ ] Profil düzenleme
- [ ] Şifre sıfırlama

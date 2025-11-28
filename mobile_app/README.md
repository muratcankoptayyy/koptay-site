# UTAP - Mobil Uygulama

Flutter ile geliştirilmiş UTAP (Ulusal Tevkil Ağı Projesi) mobil uygulaması.

## 🚀 Başlangıç

### Gereksinimler
- Flutter SDK (3.0+)
- Dart SDK
- Android Studio / Xcode
- Android SDK (API 21+)

### Kurulum

1. **Flutter SDK'yı yükleyin:**
```bash
# Flutter'ı indirin: https://flutter.dev/docs/get-started/install
flutter --version
```

2. **Bağımlılıkları yükleyin:**
```bash
cd mobile_app
flutter pub get
```

3. **Uygulamayı çalıştırın:**
```bash
# Android emulator veya cihaz
flutter run

# Release build (APK)
flutter build apk --release
```

## 📱 Özellikler

- ✅ Kullanıcı Girişi (Email/Şifre)
- ✅ Dashboard (İstatistikler)
- ✅ İlan Listesi (Filtreleme)
- ✅ İlan Detayı
- ✅ İlan Oluşturma
- ✅ Başvuru Yapma
- ✅ Başvuru Yönetimi
- ✅ Mesajlaşma (Real-time)
- ✅ Bildirimler
- ✅ Profil Yönetimi
- ✅ Kalıcı Oturum (API Token)

## 🏗️ Mimari

```
mobile_app/
├── lib/
│   ├── main.dart
│   ├── config/
│   │   └── api_config.dart          # API endpoint ayarları
│   ├── models/
│   │   ├── user.dart                # Kullanıcı modeli
│   │   ├── post.dart                # İlan modeli
│   │   ├── application.dart         # Başvuru modeli
│   │   ├── conversation.dart        # Konuşma modeli
│   │   └── notification.dart        # Bildirim modeli
│   ├── services/
│   │   ├── api_service.dart         # HTTP istekleri
│   │   ├── auth_service.dart        # Kimlik doğrulama
│   │   ├── storage_service.dart     # Local storage
│   │   └── notification_service.dart# Push notification
│   ├── providers/
│   │   ├── auth_provider.dart       # Auth state
│   │   ├── post_provider.dart       # Post state
│   │   └── message_provider.dart    # Message state
│   ├── screens/
│   │   ├── auth/
│   │   │   ├── login_screen.dart
│   │   │   └── register_screen.dart
│   │   ├── home/
│   │   │   └── dashboard_screen.dart
│   │   ├── posts/
│   │   │   ├── posts_list_screen.dart
│   │   │   ├── post_detail_screen.dart
│   │   │   └── create_post_screen.dart
│   │   ├── applications/
│   │   │   └── applications_screen.dart
│   │   ├── messages/
│   │   │   ├── conversations_screen.dart
│   │   │   └── chat_screen.dart
│   │   └── profile/
│   │       └── profile_screen.dart
│   └── widgets/
│       ├── post_card.dart
│       ├── application_card.dart
│       └── message_bubble.dart
├── android/
├── ios/
└── pubspec.yaml
```

## 🔌 API Entegrasyonu

Backend API: `http://YOUR_SERVER_IP:5000`

### Endpoints

**Authentication:**
```
POST /api/mobile/login
POST /api/mobile/logout
POST /api/mobile/verify
```

**Posts:**
```
GET  /api/posts
GET  /api/posts/{id}
POST /api/posts
```

**Applications:**
```
GET  /api/applications/my
POST /api/applications/{post_id}
```

**Messages:**
```
GET  /api/conversations
GET  /api/conversations/{id}/messages
POST /api/conversations/{id}/messages
```

**Profile:**
```
GET  /api/profile
PUT  /api/profile
```

**Notifications:**
```
GET  /api/notifications
POST /api/notifications/{id}/read
```

## 🔧 Yapılandırma

`lib/config/api_config.dart` dosyasını düzenleyin:

```dart
class ApiConfig {
  static const String baseUrl = 'http://YOUR_SERVER_IP:5000';
  static const String apiVersion = '/api';
}
```

## 📦 Bağımlılıklar

```yaml
dependencies:
  flutter:
    sdk: flutter
  provider: ^6.1.1              # State management
  http: ^1.1.0                  # HTTP requests
  shared_preferences: ^2.2.2    # Local storage
  intl: ^0.18.1                 # Date formatting
  flutter_secure_storage: ^9.0.0 # Secure storage (token)
```

## 🎨 Tema

Material Design 3 kullanılır.

Renk Paleti:
- Primary: #2563EB (Blue)
- Secondary: #10B981 (Green)
- Background: #F9FAFB
- Surface: #FFFFFF

## 📱 APK Build

Release APK oluşturmak için:

```bash
flutter build apk --release
```

APK konumu: `build/app/outputs/flutter-apk/app-release.apk`

## 🐛 Hata Ayıklama

```bash
# Logları izle
flutter logs

# Cihazları listele
flutter devices

# Uygulamayı temizle
flutter clean
flutter pub get
```

## 📄 Lisans

MIT License

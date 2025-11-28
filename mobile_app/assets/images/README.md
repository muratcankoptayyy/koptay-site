# Uygulama İkonu ve Açılış Ekranı Görselleri

Bu klasöre aşağıdaki dosyaları eklemeniz gerekmektedir:

1.  **icon.png**: Uygulama ikonu (Önerilen boyut: 1024x1024 px)
2.  **splash.png**: Açılış ekranı logosu (Önerilen boyut: 512x512 px, şeffaf arka plan)

Dosyaları ekledikten sonra terminalde şu komutları çalıştırarak ikonları ve splash screen'i oluşturabilirsiniz:

```powershell
cd mobile_app
flutter pub get
flutter pub run flutter_launcher_icons
flutter pub run flutter_native_splash:create
```

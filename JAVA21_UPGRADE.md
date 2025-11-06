# Java 21 Yükseltme Kılavuzu

## ✅ Yapılan Değişiklikler

### 1. Android Gradle Yapılandırması
- **Dosya**: `android/app/build.gradle`
- **Değişiklik**: Java 17 → Java 21
```gradle
compileOptions {
    sourceCompatibility JavaVersion.VERSION_21
    targetCompatibility JavaVersion.VERSION_21
}
```

### 2. Gradle Properties
- **Dosya**: `android/gradle.properties`
- **Ekleme**: Java home path ayarı (Java 21 kurulduktan sonra)
```properties
# Uncomment after installing Java 21:
# org.gradle.java.home=C:\\Program Files\\Eclipse Adoptium\\jdk-21.0.5.11-hotspot
```

## 📋 Gereksinimler

### Java 21 Kurulumu (JDK 21)

#### Windows için:
1. **Eclipse Temurin (Önerilen)**:
   - İndir: https://adoptium.net/temurin/releases/?version=21
   - MSI installer'ı indirin ve kurun
   - Kurulum sırasında "Set JAVA_HOME" seçeneğini işaretleyin

2. **Oracle JDK 21**:
   - İndir: https://www.oracle.com/java/technologies/downloads/#java21
   - Windows x64 Installer'ı indirin ve kurun

3. **Kurulumu Doğrulama**:
```powershell
java -version
# Çıktı: java version "21.0.x" olmalı
```

### Android Studio Ayarları

1. **File → Project Structure → SDK Location**
2. **JDK location** kısmına Java 21 yolunu girin:
   - Örnek: `C:\Program Files\Java\jdk-21`

3. **File → Settings → Build, Execution, Deployment → Build Tools → Gradle**
4. **Gradle JDK** seçeneğini "21" olarak ayarlayın

## 🚀 Build Komutları

### Gradle ile Build
```powershell
cd android
.\gradlew assembleDebug
```

### Release Build
```powershell
cd android
.\gradlew assembleRelease
```

### Clean Build
```powershell
cd android
.\gradlew clean assembleDebug
```

## 🔍 Sorun Giderme

### Problem: "Unsupported class file major version"
**Çözüm**: Gradle'ın Java 21 kullandığından emin olun:
```powershell
cd android
.\gradlew --version
# "Launcher JVM" kısmı 21.x.x göstermeli
```

### Problem: JAVA_HOME hatası
**Çözüm**: Ortam değişkenlerini ayarlayın:
```powershell
setx JAVA_HOME "C:\Program Files\Java\jdk-21"
```

### Problem: Android Studio Java sürümü uyumsuz
**Çözüm**: 
1. Android Studio'yu kapatın
2. `gradle.properties` dosyasındaki yolu kontrol edin
3. Android Studio'yu yeniden açın ve "File → Invalidate Caches / Restart"

## 📊 Java 21 Özellikleri

### Yeni Özellikler:
- ✅ **Virtual Threads** (Project Loom) - Daha iyi performans
- ✅ **Pattern Matching** - Daha temiz kod
- ✅ **Record Patterns** - Veri yapıları için
- ✅ **Sequenced Collections** - Yeni koleksiyon API'leri
- ✅ **String Templates** (Preview) - String manipülasyonu

### Performans İyileştirmeleri:
- Daha hızlı garbage collection (ZGC, G1GC iyileştirmeleri)
- Daha az memory kullanımı
- Daha iyi startup time

## 📝 Notlar

- Java 21, Eylül 2023'te yayınlanan **Long Term Support (LTS)** versiyonudur
- Sonraki LTS versiyonu Java 25 (2025 Eylül) olacak
- Android Gradle Plugin 8.7.2, Java 21'i tam destekler
- Capacitor uygulamaları için ideal Java versiyonudur

## 🔗 Yararlı Linkler

- [Java 21 Release Notes](https://www.oracle.com/java/technologies/javase/21-relnotes.html)
- [Android Gradle Plugin Compatibility](https://developer.android.com/build/releases/gradle-plugin)
- [Capacitor Android Documentation](https://capacitorjs.com/docs/android)

---

**Son Güncelleme**: 25 Ekim 2025
**Versiyon**: Java 21 (LTS)

# Play Console Kontrol Listesi
# Uygulama yayınlamadan önce tamamlanması gereken adımlar

## ✅ TAMAMLANMASI GEREKENLER

### 1. Store Listing (Mağaza İçeriği)
- [ ] **Uygulama adı:** "Tevkil - Avukat Ağı" (30 char) ✅ PLAY_STORE_LISTING.md'de hazır
- [ ] **Kısa açıklama:** 80 karakter ✅ PLAY_STORE_LISTING.md'de hazır
- [ ] **Tam açıklama:** 4000 karakter ✅ PLAY_STORE_LISTING.md'de hazır
- [ ] **Uygulama kategorisi:** İş (Business)
- [ ] **Telefon ekran görüntüleri:** Minimum 2, maksimum 8
  - Format: PNG veya JPEG
  - Boyut: 16:9 veya 9:16
  - Minimum: 320 px
  - Maksimum: 3840 px
  - **ÖNEMLİ:** Screenshot'lar hazırlanmalı!
- [ ] **Hi-res icon:** 512x512 PNG (alpha yok)
  - **ÖNEMLİ:** İcon hazırlanmalı!
- [ ] **Feature graphic:** 1024x500 JPEG veya PNG
  - **ÖNEMLİ:** Grafik hazırlanmalı!
- [ ] **Promo video:** Opsiyonel (YouTube link)

### 2. İletişim Bilgileri
### Developer Details
- [ ] **Developer name:** UTAP - Ulusal Tevkil Ağı Projesi ✅
- [ ] **E-posta:** destek@utap.com.tr ✅
- [ ] **Website:** https://utap.com.tr ✅
- [ ] **Web sitesi:** https://tevkil.fly.dev ✅
- [ ] **Telefon:** Opsiyonel (eklenebilir)

### 3. Gizlilik Politikası
- [ ] **URL:** https://tevkil.fly.dev/privacy-policy ✅
- [ ] **KVKK uyumlu:** Evet ✅
- [ ] **Erişilebilir:** Evet (web'de mevcut) ✅

### 4. Data Safety Form
- [ ] **Veri toplama beyanı:** ✅ DATA_SAFETY_FORM.md'de hazır
- [ ] **Toplanan veri türleri:** ✅ Detaylı liste mevcut
- [ ] **Veri kullanım amaçları:** ✅ Belirtildi
- [ ] **Veri paylaşımı:** ✅ Üçüncü taraf paylaşımı belirtildi
- [ ] **Güvenlik pratikleri:** ✅ Şifreleme ve kullanıcı hakları belirtildi

### 5. Content Rating (İçerik Derecelendirmesi)
- [ ] **Soru formu:** Doldurulmalı
- [ ] **PEGI:** 3+ (tahmin)
- [ ] **ESRB:** Everyone (tahmin)
- [ ] **Şiddet içeriği:** Hayır
- [ ] **Cinsel içerik:** Hayır
- [ ] **Uyuşturucu/alkol:** Hayır
- [ ] **Küfür:** Hayır

### 6. Fiyatlandırma ve Dağıtım
- [ ] **Uygulama tipi:** Ücretsiz
- [ ] **Uygulama içi satın alma:** Hayır
- [ ] **Reklam içeriyor:** Hayır
- [ ] **Dağıtım ülkeleri:** Türkiye (başlangıç), sonra genişletilebilir
- [ ] **Cihaz kategorileri:** Telefon, Tablet

### 7. App Signing (Uygulama İmzalama)
- [ ] **Upload key oluşturuldu:** ❌ KEYSTORE_SETUP.md'deki komutları çalıştırın
- [ ] **keystore.properties dosyası:** ❌ Oluşturulmalı
- [ ] **Play App Signing aktif:** Play Console'da aktifleştirin (önerilir)

### 8. AAB (Android App Bundle)
- [ ] **versionCode:** 2 ✅
- [ ] **versionName:** 1.0.0 ✅
- [ ] **targetSdkVersion:** 35 ✅
- [ ] **AAB oluşturuldu:** ❌ build-release.ps1 çalıştırın

### 9. Test
- [ ] **Internal testing track:** Oluşturulmalı
- [ ] **Test kullanıcıları:** Minimum 12 kişi (önerilen: 20+)
- [ ] **Test süresi:** Minimum 14 gün (önerilen)
- [ ] **Crash test:** Test kullanıcıları uygulamayı test etmeli

### 10. Yasal Uyumluluk
- [ ] **Kullanım şartları:** https://tevkil.fly.dev/terms-of-service ✅
- [ ] **KVKK uyumlu:** Evet ✅
- [ ] **GDPR (eğer AB'de yayınlanacaksa):** Evet ✅
- [ ] **Avukatlık mevzuatına uygun:** Evet (TBB uyumlu)

---

## 📝 ŞU AN YAPILABİLECEKLER (SIZIN İÇİN)

### ✅ Hemen Yapabilirim:
1. **Keystore oluşturma:** KEYSTORE_SETUP.md'deki komutu çalıştırmamı ister misiniz?
2. **AAB build:** keystore hazırsa build-release.ps1 ile AAB oluşturabilirim
3. **Screenshot template:** Figma/Canva template önerebilirim
4. **Icon & Feature Graphic:** Mevcut logo ile uygun boyutlarda export edebilirim

### ⏳ Manuel Yapmanız Gerekenler:
1. **Screenshot çekme:** Uygulamayı açıp ekran görüntüleri alın
2. **Play Console form doldurma:** DATA_SAFETY_FORM.md'deki bilgileri manuel girin
3. **Content rating soru formu:** Play Console'da doldurulmalı
4. **Test kullanıcıları ekleme:** Email listesi hazırlayın

---

## 🚀 HIZLI BAŞLANGIÇ (ÖNERİLEN SIRALAMA)

1. **Keystore oluştur** (5 dk)
   ```powershell
   # KEYSTORE_SETUP.md'deki komutu çalıştır
   ```

2. **AAB build** (2 dk)
   ```powershell
   .\build-release.ps1
   ```

3. **Screenshot hazırla** (30 dk)
   - Uygulamayı aç
   - Ana sayfa, ilan listesi, profil, chat, harita ekranlarından screenshot al
   - Boyutlandır: 1080x1920 (9:16) veya 1920x1080 (16:9)

4. **Icon & Feature Graphic** (15 dk)
   - 512x512 icon (logo-icon.svg → export PNG)
   - 1024x500 feature graphic (Canva'da tasarla)

5. **Play Console'da uygulama oluştur** (10 dk)
   - Create app
   - Store listing bilgilerini gir (PLAY_STORE_LISTING.md'den kopyala)

6. **Data safety form** (15 dk)
   - DATA_SAFETY_FORM.md'deki bilgileri Play Console'a gir

7. **Content rating** (5 dk)
   - Soru formunu doldur (hepsi "Hayır")

8. **AAB yükle** (5 dk)
   - Internal testing track → Create release → Upload AAB

9. **Test kullanıcıları ekle** (5 dk)
   - Email listesi hazırla ve ekle

10. **Test & Review** (14 gün)
    - Test kullanıcıları uygulamayı test etsin
    - Geri bildirimleri topla
    - Gerekirse düzelt ve yeni AAB yükle

---

## ❓ SORULAR VE CEVAPLAR

**S: AAB ne kadar sürede hazır olur?**  
C: Keystore hazırsa 2-3 dakika.

**S: Screenshot nasıl alınır?**  
C: Android cihazda Power + Volume Down tuşlarına aynı anda basın.

**S: Play Console ücreti ne kadar?**  
C: Tek seferlik $25 (kayıt olurken ödenir).

**S: Internal testing ne kadar sürer?**  
C: Minimum 14 gün önerilir, ama daha kısa sürede production'a alınabilir.

**S: Play App Signing nedir?**  
C: Google'ın sizin keystore'unuzu yedeklemesi ve yönetmesi. Keystore kaybında uygulama güncellenebilir.

---

## 📞 YARDIM

Herhangi bir adımda takılırsanız:
- KEYSTORE_SETUP.md
- PLAY_STORE_LISTING.md
- DATA_SAFETY_FORM.md
- veya bana sorun! 😊

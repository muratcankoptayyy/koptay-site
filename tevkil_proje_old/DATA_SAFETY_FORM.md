# Google Play Data Safety Form - Tevkil Uygulaması

> Play Console → App content → Data safety bölümünde doldurulacak form yanıtları

---

## 1️⃣ VERİ TOPLAMA VE GÜVENLİK

### Uygulamanız kullanıcı verisi topluyor mu?
**EVET** ✅

---

## 2️⃣ TOPLANAN VERİ TÜRLERİ

### 📍 Konum (Location)
**Toplanan:** EVET  
**Veri Türü:**
- ✅ Yaklaşık konum (Approximate location)

**Kullanım Amacı:**
- ✅ App functionality (Uygulama işlevselliği)
- ✅ Analytics (Analitik)

**Toplama Şekli:**
- ✅ Kullanıcı uygulamayı kullanırken
- ❌ Arka planda toplama yok

**Veri İşleme:**
- ✅ Veriler şifrelenerek iletiliyor (in transit)
- ✅ Veriler şifrelenerek saklanıyor (at rest)
- ❌ Kullanıcılar silme talebinde bulunabilir

---

### 👤 Kişisel Bilgiler (Personal info)
**Toplanan:** EVET  
**Veri Türü:**
- ✅ İsim (Name)
- ✅ E-posta adresi (Email address)
- ✅ Telefon numarası (Phone number)
- ✅ Adres (Physical address)
- ❌ Kullanıcı kimlikleri (User IDs) - opsiyonel
- ❌ Fotoğraflar (Photos) - opsiyonel

**Kullanım Amacı:**
- ✅ App functionality (Kimlik doğrulama, profil)
- ✅ Account management (Hesap yönetimi)
- ❌ Advertising or marketing
- ❌ Fraud prevention

**Veri İşleme:**
- ✅ Veriler şifrelenerek iletiliyor
- ✅ Veriler şifrelenerek saklanıyor
- ✅ Kullanıcılar hesap silme talebinde bulunabilir

---

### 📧 Mesajlar (Messages)
**Toplanan:** EVET  
**Veri Türü:**
- ✅ E-postalar (Emails)
- ✅ SMS or MMS
- ✅ Diğer uygulama içi mesajlar (Other in-app messages)

**Kullanım Amacı:**
- ✅ App functionality (Mesajlaşma sistemi)
- ❌ Advertising or marketing

**Veri İşleme:**
- ✅ Veriler şifrelenerek iletiliyor
- ✅ Veriler şifrelenerek saklanıyor
- ✅ Kullanıcılar mesajları silebilir

---

### 🖼️ Fotoğraf ve Videolar (Photos and videos)
**Toplanan:** EVET (opsiyonel - kullanıcı profil fotoğrafı)  
**Veri Türü:**
- ✅ Fotoğraflar (Photos)
- ❌ Videolar (Videos)

**Kullanım Amacı:**
- ✅ App functionality (Profil fotoğrafı)

**Veri İşleme:**
- ✅ Veriler şifrelenerek iletiliyor
- ✅ Veriler şifrelenerek saklanıyor
- ✅ Kullanıcılar silebilir

---

### 📂 Dosyalar ve Belgeler (Files and docs)
**Toplanan:** EVET  
**Veri Türü:**
- ✅ Dosyalar ve belgeler (Files and docs)

**Kullanım Amacı:**
- ✅ App functionality (Belge paylaşımı - ilan, dava dosyaları)

**Veri İşleme:**
- ✅ Veriler şifrelenerek iletiliyor
- ✅ Veriler şifrelenerek saklanıyor
- ✅ Kullanıcılar silebilir

---

### 🎭 Uygulama Aktivitesi (App activity)
**Toplanan:** EVET  
**Veri Türü:**
- ✅ Uygulama etkileşimleri (App interactions)
- ✅ Uygulama içi arama geçmişi (In-app search history)
- ✅ Yüklenen içerik (Installed apps) - YOK
- ❌ Diğer kullanıcı tarafından oluşturulan içerik
- ❌ Diğer işlemler

**Kullanım Amacı:**
- ✅ Analytics (İstatistikler)
- ✅ App functionality

**Veri İşleme:**
- ✅ Veriler şifrelenerek iletiliyor
- ✅ Veriler şifrelenerek saklanıyor
- ❌ Kullanıcılar silme talebinde bulunamaz (analitik veri)

---

### 📱 Cihaz veya Diğer Kimlikler (Device or other IDs)
**Toplanan:** EVET  
**Veri Türü:**
- ✅ Cihaz veya diğer kimlikler (Device or other IDs)

**Kullanım Amacı:**
- ✅ Analytics
- ✅ App functionality (Push notifications)

**Veri İşleme:**
- ✅ Veriler şifrelenerek iletiliyor
- ✅ Veriler şifrelenerek saklanıyor
- ❌ Silme mümkün değil (cihaz ID)

---

## 3️⃣ VERİ PAYLAŞIMI

### Verilerinizi üçüncü taraflarla paylaşıyor musunuz?
**EVET** (sınırlı)

**Paylaşılan taraflar:**
1. **Hosting sağlayıcısı (Fly.io)** - Altyapı
2. **WhatsApp Business API** - Bildirimler (opsiyonel kullanıcı onayı ile)
3. **Google Analytics** (opsiyonel, anonim)

**Paylaşım amacı:**
- ✅ App functionality
- ❌ Advertising or marketing
- ❌ Fraud prevention

**NOT:** Kullanıcıların birbirleriyle paylaşımı (mesajlar, ilanlar) **uygulama içi** olup, üçüncü taraf değildir.

---

## 4️⃣ GÜVENLİK PRATİKLERİ

### Veriler nasıl korunuyor?

#### 🔒 İletim Sırasında Şifreleme (Data encrypted in transit)
- ✅ **EVET** - Tüm veriler HTTPS/TLS 1.3 ile şifrelenir
- ✅ SSL/TLS sertifikası (Let's Encrypt)
- ✅ Tüm API istekleri şifreli kanal üzerinden

#### 💾 Depolama Sırasında Şifreleme (Data encrypted at rest)
- ✅ **EVET** - Fly.io PostgreSQL otomatik disk şifrelemesi (AES-256)
- ✅ Şifreler: Bcrypt hash algoritması (tek yönlü, geri döndürülemez)
- ✅ API Token'lar: UUID v4 güvenli rastgele token
- ✅ 2FA kodları: Tek kullanımlık, hash'lenmiş
- ✅ Hassas veriler uygulama seviyesinde hash'lenir

#### 🗑️ Kullanıcı Hakları
- ✅ Kullanıcılar hesap silme talebinde bulunabilir
- ✅ Kullanıcılar verilerini indirebilir (KVKK hakkı)
- ✅ Mesajları dilediği zaman silebilir
- ✅ Profil verilerini düzenleyebilir/silebilir

### Veri saklama süresi
- **Aktif hesaplar:** Hesap silinene kadar
- **Pasif hesaplar:** 3 yıl sonra otomatik silinir
- **Mesajlar:** Kullanıcılar diledikleri zaman silebilir
- **Log verileri:** 6 ay

---

## 5️⃣ KVKK & GDPR UYUMLULUĞU

### Aydınlatma Metni
✅ Gizlilik politikası mevcut: https://tevkil.fly.dev/privacy-policy

### Kullanıcı Hakları (KVKK md. 11)
- ✅ Kişisel verilerinin işlenip işlenmediğini öğrenme
- ✅ İşlenmişse bilgi talep etme
- ✅ İşlenme amacını öğrenme
- ✅ Yurt içi/yurt dışı aktarımı öğrenme
- ✅ Eksik/yanlış işlenmişse düzeltme
- ✅ Şartları oluştuğunda silme/yok etme
- ✅ Zarara uğramanız halinde tazminat talep etme

### İletişim
**Veri Sorumlusu:** UTAP - Ulusal Tevkil Ağı Projesi  
**E-posta:** destek@utap.com.tr

---

## 6️⃣ ÖZEL DURUMLAR

### Çocuk Gizliliği
❌ Uygulama 18 yaş altına yönelik değildir.  
❌ Bilinçli olarak 18 yaş altından veri toplamıyoruz.

### Hassas Veriler
❌ Sağlık bilgisi toplamıyoruz  
❌ Finansal bilgi toplamıyoruz (ödeme sistemi henüz yok)  
❌ Cinsel yönelim/din/etnik köken gibi hassas veriler toplamıyoruz

---

## ✅ ÖZET CHECKBOX'LAR (Play Console)

Data safety section'daki checkbox'lar için özet:
- ✅ Uygulama kullanıcı verisi topluyor
- ✅ Tüm veriler şifrelenerek iletiliyor
- ✅ Kullanıcılar veri silme talebinde bulunabilir
- ✅ Bu veriler bağımsız bir güvenlik incelemesinden geçti (HAYIR - bu opsiyonel)
- ✅ Veriler üçüncü taraflarla paylaşılıyor (sınırlı - hosting/analytics)
- ✅ Gizlilik politikası mevcut (URL: https://tevkil.fly.dev/privacy-policy)

---

## 📝 NOTLAR

1. **Google Analytics:** Eğer GA kullanıyorsanız bunu Data Safety'de belirtmelisiniz.
2. **WhatsApp:** Push notification için WhatsApp kullanılıyorsa üçüncü taraf olarak belirtilmeli.
3. **Baro Doğrulaması:** Baro sicil numarası hassas veri sayılabilir (mesleki kimlik), "Professional info" olarak eklenebilir.
4. **Play App Signing:** Google Play App Signing kullanırsanız Google'ın APK'yı yeniden imzaladığını not edin.

---

## 🔗 İLGİLİ BAĞLANTILAR

- Privacy Policy: https://tevkil.fly.dev/privacy-policy
- Terms of Service: https://tevkil.fly.dev/terms-of-service
- Cookie Policy: https://tevkil.fly.dev/cookie-policy
- Contact: destek@utap.com.tr

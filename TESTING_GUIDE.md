# 🧪 Test Rehberi

UTAP platformunun test edilmesi için kapsamlı rehber.

## 📋 Test Checklist

### 1. Kimlik Doğrulama (Authentication)

#### Kayıt Ol (Register)
- [ ] `/register` sayfası açılıyor
- [ ] Form alanları görünüyor
- [ ] Zorunlu alan uyarıları çalışıyor
- [ ] Email formatı kontrol ediliyor
- [ ] Şifre eşleşme kontrolü çalışıyor
- [ ] Başarılı kayıt sonrası giriş yapılıyor
- [ ] Aynı email ile tekrar kayıt engelleniyor

**Test Senaryosu:**
```
1. /register sayfasına git
2. Tüm alanları doldur
3. "Kayıt Ol" butonuna tıkla
4. Dashboard'a yönlendirildiğini kontrol et
5. Logout yap
6. Aynı email ile tekrar kayıt olmayı dene
7. Hata mesajı göründüğünü doğrula
```

#### Giriş Yap (Login)
- [ ] `/login` sayfası açılıyor
- [ ] Email ve şifre alanları çalışıyor
- [ ] Yanlış bilgilerle hata mesajı gösteriliyor
- [ ] "Beni Hatırla" özelliği çalışıyor
- [ ] Başarılı giriş sonrası dashboard'a yönlendirme

**Test Senaryosu:**
```
1. /login sayfasına git
2. Kayıtlı kullanıcı bilgileriyle giriş yap
3. Dashboard'a yönlendirildiğini kontrol et
4. Logout yap
5. Yanlış şifre ile giriş dene
6. Hata mesajı göründüğünü doğrula
```

#### Çıkış Yap (Logout)
- [ ] Logout butonu görünüyor
- [ ] Logout sonrası login sayfasına yönlendirme
- [ ] Session temizleniyor
- [ ] Korumalı sayfalara erişim engelleniyor

### 2. Dashboard

#### Genel
- [ ] İstatistikler doğru gösteriliyor
- [ ] Aktif ilan sayısı doğru
- [ ] Başvuru sayısı doğru
- [ ] Mesaj sayısı doğru
- [ ] Rating görünüyor

**Test Senaryosu:**
```
1. Dashboard'a git
2. İlan sayısını kontrol et
3. Yeni ilan oluştur
4. Dashboard'a dön
5. İlan sayısının arttığını doğrula
```

#### Quick Actions
- [ ] "Yeni İlan" butonu çalışıyor
- [ ] "Mesajlar" butonu çalışıyor
- [ ] "Profilim" butonu çalışıyor

### 3. İlan Yönetimi (Posts)

#### İlan Listesi
- [ ] Tüm ilanlar listeleniyor
- [ ] Filtreleme çalışıyor (Tümü/Aktif/Beklemede/Tamamlandı)
- [ ] Arama çalışıyor
- [ ] Kendi ilanları görünüyor
- [ ] Detay butonları çalışıyor

**Test Senaryosu:**
```
1. /posts sayfasına git
2. İlanların görüntülendiğini kontrol et
3. "Aktif" filtresini seç
4. Sadece aktif ilanların göründüğünü doğrula
5. Arama kutusuna bir kelime yaz
6. İlgili ilanların filtrelendiğini kontrol et
```

#### İlan Oluşturma
- [ ] `/posts/create` formu açılıyor
- [ ] Tüm alanlar görünüyor
- [ ] Başlık zorunlu kontrolü
- [ ] Açıklama zorunlu kontrolü
- [ ] İl seçimi çalışıyor
- [ ] İlçe seçimi çalışıyor
- [ ] Dava türü seçimi
- [ ] Fiyat validasyonu
- [ ] Başarılı oluşturma sonrası yönlendirme

**Test Senaryosu:**
```
1. Dashboard'dan "Yeni İlan" butonuna tıkla
2. Formu doldur:
   - Başlık: "Test Tevkil İlanı"
   - Açıklama: "Test için oluşturulmuştur"
   - İl: "İstanbul"
   - İlçe: "Kadıköy"
   - Dava Türü: "Ceza Hukuku"
   - Fiyat: "5000"
3. "İlan Oluştur" butonuna tıkla
4. İlan detay sayfasına yönlendirildiğini kontrol et
5. İlanın listelendiğini doğrula
```

#### İlan Düzenleme
- [ ] Edit butonu çalışıyor
- [ ] Form mevcut verilerle dolu geliyor
- [ ] Güncelleme çalışıyor
- [ ] Başarı mesajı gösteriliyor

**Test Senaryosu:**
```
1. İlan listesinden bir ilan seç
2. "Düzenle" butonuna tıkla
3. Başlığı değiştir
4. "Güncelle" butonuna tıkla
5. Değişikliğin kaydedildiğini kontrol et
```

#### İlan Silme
- [ ] Silme butonu görünüyor
- [ ] Onay modalı açılıyor
- [ ] İlan siliniyor
- [ ] Liste güncelleniyor

### 4. Başvuru Sistemi (Applications)

#### Başvuru Yapma
- [ ] Başvuru formu çalışıyor
- [ ] Teklif fiyatı girilemiyor mu kontrol
- [ ] Mesaj alanı çalışıyor
- [ ] Başarılı başvuru bildirimi

**Test Senaryosu:**
```
1. İlan detayına git
2. "Başvuru Yap" butonuna tıkla
3. Teklif fiyatı: "4500"
4. Mesaj: "İlanınız için başvuru yapmak istiyorum"
5. "Başvur" butonuna tıkla
6. Başarı mesajını kontrol et
```

#### Başvuruları Görüntüleme
- [ ] `/applications` sayfası açılıyor
- [ ] Gelen başvurular listeleniyor
- [ ] Giden başvurular listeleniyor
- [ ] Kabul/Reddet butonları çalışıyor

**Test Senaryosu:**
```
1. /applications sayfasına git
2. "Gelen" sekmesine tıkla
3. Başvuruların listelendiğini kontrol et
4. Bir başvuruyu kabul et
5. Durumun "Kabul Edildi" olduğunu doğrula
```

### 5. Mesajlaşma (Messages)

#### Mesaj Listesi
- [ ] Konuşmalar listeleniyor
- [ ] Okunmamış sayısı görünüyor
- [ ] Son mesaj preview görünüyor
- [ ] Arama çalışıyor

#### Mesaj Gönderme
- [ ] Mesaj kutusu çalışıyor
- [ ] Enter ile gönderim çalışıyor
- [ ] Gönder butonu çalışıyor
- [ ] Mesaj anında görünüyor
- [ ] Karşı tarafta bildirim gidiyor

**Test Senaryosu:**
```
1. /messages sayfasına git
2. Bir konuşma seç
3. Mesaj kutusuna "Test mesajı" yaz
4. "Gönder" butonuna tıkla
5. Mesajın görüntülendiğini kontrol et
6. Okunmamış sayısının güncellendiğini doğrula
```

#### Mesaj Okuma
- [ ] Mesajlar sıralı görünüyor
- [ ] Okunma durumu güncelleniyor
- [ ] Scroll otomatik en alta gidiyor

### 6. Profil (Profile)

#### Profil Görüntüleme
- [ ] `/profile` sayfası açılıyor
- [ ] Kullanıcı bilgileri görünüyor
- [ ] İstatistikler görünüyor
- [ ] Profil fotoğrafı görünüyor

#### Profil Düzenleme
- [ ] Düzenle butonu çalışıyor
- [ ] Form mevcut verilerle dolu
- [ ] Ad Soyad değiştirilebiliyor
- [ ] Telefon değiştirilebiliyor
- [ ] Adres güncellenebiliyor
- [ ] Profil fotoğrafı yüklenebiliyor
- [ ] Başarılı güncelleme mesajı

**Test Senaryosu:**
```
1. /profile sayfasına git
2. "Profili Düzenle" butonuna tıkla
3. Telefon numarasını değiştir
4. "Kaydet" butonuna tıkla
5. Değişikliğin kaydedildiğini kontrol et
```

### 7. Ayarlar (Settings)

#### Genel Ayarlar
- [ ] Email değişikliği çalışıyor
- [ ] Bildirim tercihleri kaydediliyor
- [ ] Dil seçimi çalışıyor (gelecekte)

#### Güvenlik
- [ ] Şifre değiştirme çalışıyor
- [ ] Eski şifre kontrolü yapılıyor
- [ ] Yeni şifre validasyonu çalışıyor

**Test Senaryosu:**
```
1. /settings sayfasına git
2. "Güvenlik" sekmesine tıkla
3. Eski şifre: mevcut şifren
4. Yeni şifre: yeni güçlü şifre
5. Şifre tekrar: aynı şifre
6. "Şifreyi Güncelle" butonuna tıkla
7. Başarı mesajını kontrol et
8. Logout yap
9. Yeni şifre ile giriş yap
```

## 🔍 Browser Testing

### Desktop
- [ ] Chrome (son versiyon)
- [ ] Firefox (son versiyon)
- [ ] Edge (son versiyon)
- [ ] Safari (Mac)

### Mobile
- [ ] Chrome Mobile (Android)
- [ ] Safari Mobile (iOS)
- [ ] Samsung Internet

### Responsive Breakpoints
- [ ] 1920px (Desktop)
- [ ] 1366px (Laptop)
- [ ] 768px (Tablet)
- [ ] 414px (Mobile L)
- [ ] 375px (Mobile M)
- [ ] 320px (Mobile S)

## ⚡ Performance Testing

### Page Load Times
```bash
# Lighthouse audit
lighthouse https://yourdomain.com --view

# Expected Scores:
# Performance: >80
# Accessibility: >90
# Best Practices: >90
# SEO: >80
```

### Database Queries
- [ ] N+1 query problemi yok
- [ ] Index'ler doğru kullanılıyor
- [ ] Sayfa başına <10 query

## 🔐 Security Testing

### Authentication
- [ ] Korumalı sayfalara erişim engelleniyor
- [ ] CSRF token kontrolü çalışıyor
- [ ] Session timeout çalışıyor
- [ ] XSS koruması aktif

### Input Validation
- [ ] SQL injection korumalı
- [ ] XSS saldırılarına karşı korumalı
- [ ] File upload güvenli
- [ ] URL parameter validasyonu

**Test:**
```
# XSS Test
<script>alert('XSS')</script>

# SQL Injection Test
' OR '1'='1
```

## 🐛 Bug Reporting Template

Bir bug bulduğunuzda:

```markdown
**Başlık:** Kısa açıklayıcı başlık

**Açıklama:** Detaylı açıklama

**Adımlar:**
1. Sayfayı aç
2. Butona tıkla
3. Formu doldur

**Beklenen Sonuç:** Ne olması gerekiyordu

**Gerçekleşen Sonuç:** Ne oldu

**Ekran Görüntüsü:** [Varsa ekle]

**Tarayıcı:** Chrome 120.0.0

**OS:** Windows 11

**Önem Derecesi:** Yüksek/Orta/Düşük
```

## ✅ Test Tamamlandı

Tüm testler başarılı ise:
- [ ] Test raporu oluştur
- [ ] Bulunan bugları kaydet
- [ ] Production deployment için onay ver

---

**Test Versiyonu:** 1.0  
**Son Güncelleme:** Kasım 2025

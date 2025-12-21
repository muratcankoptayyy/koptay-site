# Flutter Mobil Uygulama Test Rehberi

## ✅ Pre-Test Checklist

- [ ] Backend API çalışıyor (`python app.py`)
- [ ] Flutter SDK kurulu (`flutter doctor`)
- [ ] Android Emulator veya fiziksel cihaz hazır
- [ ] API config doğru (`lib/config/api_config.dart`)
- [ ] Bağımlılıklar yüklendi (`flutter pub get`)

---

## 🧪 Test Senaryoları

### 1. Giriş (Login) Testi

#### Test 1.1: Başarılı Giriş
1. Uygulamayı başlatın: `flutter run`
2. Login ekranını görün
3. Email: `test@example.com` (veya mevcut kullanıcı)
4. Şifre: `password123` (veya doğru şifre)
5. "Giriş Yap" butonuna tıklayın

**Beklenen:**
- ✅ Loading indicator görünür
- ✅ Dashboard ekranına yönlendirme
- ✅ Hoşgeldin mesajı gösterilir
- ✅ Kullanıcı adı doğru görünür

#### Test 1.2: Hatalı Giriş
1. Email: `wrong@example.com`
2. Şifre: `wrongpassword`
3. "Giriş Yap" tıklayın

**Beklenen:**
- ✅ Hata mesajı (Snackbar) gösterilir
- ✅ Login ekranında kalınır

#### Test 1.3: Validasyon
1. Email boş bırakın → Hata: "E-posta gerekli"
2. Email geçersiz: `notanemail` → Hata: "Geçerli bir e-posta girin"
3. Şifre boş → Hata: "Şifre gerekli"
4. Şifre 5 karakter → Hata: "Şifre en az 6 karakter olmalı"

---

### 2. Dashboard Testi

#### Test 2.1: Dashboard Görünümü
1. Giriş yapın
2. Dashboard ekranını inceleyin

**Beklenen:**
- ✅ Kullanıcı bilgi kartı görünür
- ✅ 4 hızlı eylem kartı var (Yeni İlan, İlan Ara, Başvurularım, Mesajlar)
- ✅ Bottom navigation 5 tab gösterir
- ✅ Bildirim butonu appbar'da

#### Test 2.2: Hızlı Eylemler
1. "Yeni İlan" kartına tıklayın → Create Post ekranı açılır
2. Geri dönün, "İlan Ara" tıklayın → Posts tab'ına geçer
3. "Başvurularım" → Applications tab
4. "Mesajlar" → Conversations tab

---

### 3. İlanlar (Posts) Testi

#### Test 3.1: İlan Listesi
1. Bottom navigation'dan "İlanlar" sekmesine tıklayın
2. İlanları görün

**Beklenen:**
- ✅ En az 1 ilan varsa liste görünür
- ✅ Her ilan kartında: Başlık, açıklama, kategori, yazar, tarih
- ✅ Görüntülenme ve başvuru sayısı gösterilir
- ✅ Scroll yaptıkça yeni ilanlar yüklenir (pagination)

#### Test 3.2: Arama
1. Arama kutusuna "ceza" yazın
2. Enter tuşuna basın

**Beklenen:**
- ✅ Liste yenilenir
- ✅ "ceza" içeren ilanlar gösterilir

#### Test 3.3: Kategori Filtreleme
1. "Ceza" kategorisine tıklayın

**Beklenen:**
- ✅ Sadece Ceza Hukuku ilanları gösterilir
- ✅ Chip seçili görünür (farklı renk)

2. "Tümü" tıklayın → Tüm ilanlar gösterilir

#### Test 3.4: Pull-to-Refresh
1. İlan listesini yukarıdan aşağı çekin

**Beklenen:**
- ✅ Refresh indicator gösterilir
- ✅ Liste yenilenir

---

### 4. İlan Detayı Testi

#### Test 4.1: İlan Görüntüleme
1. Herhangi bir ilana tıklayın
2. Detay ekranını inceleyin

**Beklenen:**
- ✅ Başlık, açıklama, yazar bilgisi
- ✅ Kategori, konum, son başvuru tarihi (varsa)
- ✅ Görüntülenme ve başvuru istatistikleri
- ✅ İlan resimleri (varsa) galeride görüntülenir
- ✅ Başvuru formu (eğer süre dolmamışsa)

#### Test 4.2: Başvuru Yapma
1. İlan detay ekranında aşağı kaydırın
2. "Mesajınız" alanına yazın: "Merhaba, bu işe başvurmak istiyorum"
3. "Başvuru Gönder" tıklayın

**Beklenen:**
- ✅ Success snackbar: "Başvurunuz gönderildi"
- ✅ Ekran kapanır

---

### 5. Yeni İlan Oluşturma Testi

#### Test 5.1: İlan Oluşturma
1. Dashboard → "Yeni İlan" veya Posts → FAB (+) tıklayın
2. Form doldurun:
   - Başlık: "Test İlanı - Ceza Avukatı Aranıyor"
   - Kategori: "Ceza Hukuku"
   - Açıklama: "Bu bir test ilanıdır. En az 50 karakter olmalı, bu yüzden biraz daha uzun yazıyorum..."
   - Konum (opsiyonel): "İstanbul/Kadıköy"
   - Son Başvuru: Gelecek bir tarih seçin
   - Resim Ekle: Galeriden 1-2 resim seçin
3. "İlanı Yayınla" tıklayın

**Beklenen:**
- ✅ Loading gösterilir
- ✅ Success snackbar
- ✅ İlan listesine dönülür
- ✅ Yeni ilan listenin başında görünür (varsa thumbnail ile)

#### Test 5.2: Validasyon
1. Başlık 5 karakter → Hata: "En az 10 karakter"
2. Açıklama 20 karakter → Hata: "En az 50 karakter"
3. Boş form göndermeye çalışın → Hatalar gösterilir

---

### 6. Profil Testi

#### Test 6.1: Profil Görüntüleme
1. Bottom navigation → "Profil"

**Beklenen:**
- ✅ Avatar (varsa resim, yoksa baş harf)
- ✅ Ad soyad
- ✅ Kullanıcı tipi (Avukat/Vekil Arayan)
- ✅ Email, telefon (varsa), adres (varsa)
- ✅ "Profili Düzenle" butonu
- ✅ "Çıkış Yap" butonu

#### Test 6.2: Profil Fotoğrafı Yükleme
1. Profil resmine veya düzenle butonuna tıklayın
2. Galeriden/Kameradan fotoğraf seçin

**Beklenen:**
- ✅ Fotoğraf yüklenir
- ✅ Profil resmi güncellenir

#### Test 6.3: Çıkış Yapma
1. "Çıkış Yap" butonuna tıklayın

**Beklenen:**
- ✅ Login ekranına yönlendirme
- ✅ Token temizlendi
- ✅ Tekrar giriş yapılması gerekir

---

### 7. Başvurular Testi

#### Test 7.1: Başvuru Listesi
1. Bottom navigation → "Başvurular"
2. "Yaptığım Başvurular" ve "Gelen Başvurular" sekmelerini kontrol edin

**Beklenen:**
- ✅ Başvurular listelenir
- ✅ Başvuru yoksa "Empty State" (Boş durum) ekranı görünür
- ✅ Başvuru durumları (Beklemede, Kabul, Red) doğru renklerle görünür

#### Test 7.2: Başvuru Yönetimi (Gelen Başvurular)
1. "Gelen Başvurular" sekmesine geçin (İlan sahibiyseniz)
2. Bekleyen bir başvuruda "Kabul Et" veya "Reddet" butonuna tıklayın

**Beklenen:**
- ✅ Durum güncellenir (Kabul Edildi/Reddedildi)
- ✅ Butonlar kaybolur

---

### 8. Mesajlar Testi

#### Test 8.1: Mesaj Listesi
1. Bottom navigation → "Mesajlar"

**Beklenen:**
- ✅ Konuşma listesi görünür
- ✅ Mesaj yoksa "Empty State" ekranı görünür
- ✅ Okunmamış mesaj sayısı (varsa) görünür

#### Test 8.2: Sohbet Ekranı
1. Bir konuşmaya tıklayın
2. Mesaj yazıp gönderin

**Beklenen:**
- ✅ Mesaj balonu eklenir
- ✅ Karşı tarafın mesajları görünür

---

### 9. Bildirimler Testi

#### Test 9.1: Bildirim Listesi
1. Dashboard → Sağ üstteki zil ikonuna tıklayın

**Beklenen:**
- ✅ Bildirimler listelenir
- ✅ Bildirim yoksa "Empty State" ekranı görünür
- ✅ Okunmamış bildirimler farklı renkte görünür
- ✅ Tıklayınca ilgili ekrana yönlendirir (örn: başvuru detayı)

---

## 🔌 Backend API Testleri

### Manuel API Test (Postman/curl)

#### Test: Login
```bash
curl -X POST http://localhost:5000/api/mobile/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

**Beklenen:**
```json
{
  "token": "abcd1234...",
  "user": {
    "id": 1,
    "email": "test@example.com",
    ...
  }
}
```

#### Test: Posts (Token gerekli)
```bash
curl http://localhost:5000/api/posts \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Beklenen:**
```json
{
  "posts": [...],
  "total": 10
}
```

---

## 🐛 Bilinen Sorunlar ve Çözümler

### Sorun 1: "Connection refused"
**Sebep:** Backend çalışmıyor
**Çözüm:** `python app.py` ile backend'i başlatın

### Sorun 2: "Unable to connect"
**Sebep:** API URL yanlış
**Çözüm:** 
- Emulator için: `10.0.2.2:5000`
- Fiziksel cihaz için: Local IP (örn: `192.168.1.100:5000`)

### Sorun 3: "Token expired" veya 401 Unauthorized
**Sebep:** Token geçersiz
**Çözüm:** Uygulamayı kapat-aç, tekrar login yap

### Sorun 4: Infinite scroll çalışmıyor
**Sebep:** Backend'de yeterli veri yok
**Çözüm:** En az 20+ ilan oluşturun

---

## 📊 Test Raporu Şablonu

### Test Özeti
- **Tarih:** [TARİH]
- **Test Eden:** [İSİM]
- **Cihaz:** [Emulator/Fiziksel - Model]
- **Flutter Version:** `flutter --version`
- **Backend Status:** Çalışıyor / Çalışmıyor

### Test Sonuçları

| Test ID | Test Adı | Sonuç | Not |
|---------|----------|-------|-----|
| 1.1 | Başarılı Giriş | ✅ / ❌ | |
| 1.2 | Hatalı Giriş | ✅ / ❌ | |
| 2.1 | Dashboard Görünümü | ✅ / ❌ | |
| 3.1 | İlan Listesi | ✅ / ❌ | |
| 4.1 | İlan Detayı | ✅ / ❌ | |
| 5.1 | İlan Oluşturma | ✅ / ❌ | |
| 6.1 | Profil Görüntüleme | ✅ / ❌ | |
| 6.2 | Çıkış Yapma | ✅ / ❌ | |

### Bulunan Hatalar
1. [Hata açıklaması]
2. [Hata açıklaması]

### Öneriler
1. [Öneri]
2. [Öneri]

---

## ✅ Production Readiness Checklist

- [ ] Tüm test senaryoları başarılı
- [ ] Emulator'de test edildi
- [ ] Fiziksel cihazda test edildi
- [ ] API error handling doğru
- [ ] Loading states düzgün
- [ ] Validasyonlar çalışıyor
- [ ] Token persistence çalışıyor
- [ ] Logout düzgün temizliyor
- [ ] Pagination çalışıyor
- [ ] Search/Filter çalışıyor
- [ ] Release APK build başarılı
- [ ] APK boyutu kabul edilebilir (<50MB)

---

**Not:** Bu dokümandaki testleri sırayla yapın. Her test başarılı olmalı.

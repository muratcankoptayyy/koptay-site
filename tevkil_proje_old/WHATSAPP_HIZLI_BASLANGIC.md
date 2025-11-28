# 🚀 WhatsApp Entegrasyonu - Hızlı Başlangıç

## 📱 Sistem Özeti

**Ulusal Tevkil Ağı** merkezi WhatsApp bot sistemi kullanır. Yani:
- ✅ **TEK WhatsApp numarası** - Tüm avukatlar için
- ✅ **Kullanıcı telefon numarasından tanıma** - Ayrı hesap gerektirmez
- ✅ **Otomatik bildirimler** - Başvuru geldiğinde WhatsApp'tan bildirim
- ✅ **WhatsApp'tan ilan oluşturma** - #ILAN komutu ile

---

## ⚡ HIZLI KURULUM (3 DAKİKA)

### Yöntem 1: Otomatik Kurulum Script'i

```bash
python setup_whatsapp.py
```

Bu script size adım adım:
1. Meta credentials'ları sorar
2. `.env` dosyasını otomatik oluşturur
3. Webhook bilgilerini gösterir
4. Bağlantı testi yapar

### Yöntem 2: Manuel Kurulum

1. `.env.example` dosyasını kopyalayın:
```bash
copy .env.example .env
```

2. `.env` dosyasını açın ve düzenleyin:
```env
META_PHONE_NUMBER_ID=123456789012345
META_ACCESS_TOKEN=EAAxxxxxxxxxxxx...
META_WEBHOOK_VERIFY_TOKEN=tevkil_webhook_2025
```

---

## 🔑 Credentials Nereden Alınır?

### 1. META_PHONE_NUMBER_ID

```
https://developers.facebook.com/apps/
→ Uygulamanız → WhatsApp → API Setup
→ "Phone number ID" kopyalayın
```

**Örnek:** `123456789012345`

### 2. META_ACCESS_TOKEN

**Geçici Token (24 saat):**
```
WhatsApp Dashboard → API Setup
→ "Temporary access token" kopyalayın
```

**Kalıcı Token (Önerilen):**
```
https://business.facebook.com
→ Business Settings → System Users
→ "Add" → Kullanıcı oluştur
→ "Generate New Token" → App seçin
→ İzinler: whatsapp_business_management, whatsapp_business_messaging
→ Token'ı kopyalayın
```

**Örnek:** `EAABwzLixnjYBO7Yr0BQl...`

### 3. META_WEBHOOK_VERIFY_TOKEN

Bu kendiniz belirlersiniz. Meta Dashboard'da aynı token'ı gireceksiniz.

**Varsayılan:** `tevkil_webhook_2025`

---

## 🌐 Webhook Yapılandırması

### Production (Canlı Sunucu)

```
WhatsApp Dashboard → Configuration → Webhook → Edit

Callback URL: https://utap.com.tr/api/whatsapp/webhook
Verify Token: tevkil_webhook_2025
Webhook Fields: ✅ messages
```

### Local Test (Ngrok ile)

```bash
# Terminal 1: Flask'ı başlat
python app.py

# Terminal 2: Ngrok başlat
ngrok http 5000
```

Ngrok URL'ini alın (örn: `https://abc123.ngrok.io`) ve Meta'ya girin:
```
Callback URL: https://abc123.ngrok.io/api/whatsapp/webhook
Verify Token: tevkil_webhook_2025
```

---

## 🧪 Test Etme

### 1. Web Arayüzünden Test

```
http://127.0.0.1:5000/whatsapp/setup
→ Test bölümü
→ Komut seçin (#YARDIM, #ILAN, vb.)
→ "Test Komutu Gönder" butonuna tıklayın
```

### 2. Gerçek WhatsApp'tan Test

```
1. Profilinizde telefon numaranızı kaydedin
2. Meta'da test numarası olarak ekleyin
3. Meta'nın WhatsApp numarasına mesaj gönderin:

#YARDIM
```

Bot size otomatik cevap verecek!

### 3. Terminal'den Test

```bash
python setup_whatsapp.py test
```

Bu komut credentials'larınızı doğrular ve Meta API bağlantısını test eder.

---

## 📋 Kullanılabilir Komutlar

| Komut | Açıklama | Örnek |
|-------|----------|-------|
| `#ILAN` | Yeni ilan oluştur | Aşağıya bakın |
| `#YARDIM` | Yardım menüsü | `#YARDIM` |
| `#DURUM` | Hesap durumu | `#DURUM` |
| `#ILANLARIM` | Aktif ilanlarım | `#ILANLARIM` |
| `#BASVURULARIM` | Yaptığım başvurular | `#BASVURULARIM` |

### İlan Oluşturma Format:

```
#ILAN
Başlık: Ankara Adliyesi Duruşma Temsili
Kategori: Ceza Hukuku
Şehir: Ankara
Açıklama: 25 Ocak 2025 saat 14:00 duruşma temsili gerekiyor
Fiyat: 3500
Aciliyet: Acil
```

Bot otomatik cevap verir:
```
✅ İLAN OLUŞTURULDU!

📋 İlan No: #123
📌 Başlık: Ankara Adliyesi Duruşma Temsili
🏛 Kategori: Ceza Hukuku
📍 Şehir: Ankara
💰 Ücret: 3500 TL
⚡ Aciliyet: Acil

Başvurular geldiğinde size WhatsApp'tan bildirim göndereceğiz!
```

---

## 🔔 Otomatik Bildirimler

Bot şu durumlarda otomatik bildirim gönderir:

### 1. Yeni Başvuru (İlan Sahibine)
```
🔔 YENİ BAŞVURU!

📋 İlanınız: Ankara Duruşma Temsili
👤 Başvuran: Av. Mehmet Yılmaz
📍 Şehir: İstanbul
💰 Teklif: 3500 TL

💬 Mesaj: Ceza hukuku alanında 10 yıllık tecrübem var...
```

### 2. Başvuru Kabul (Başvuran Avukata)
```
✅ BAŞVURUNUZ KABUL EDİLDİ!

📋 İlan: Ankara Duruşma Temsili
👤 İlan Sahibi: Av. Ayşe Demir
📞 İletişim: 0555 123 4567
💰 Anlaşılan Ücret: 3500 TL
```

### 3. Başvuru Red (Başvuran Avukata)
```
❌ BAŞVURUNUZ REDDEDİLDİ

📋 İlan: Ankara Duruşma Temsili
📍 Şehir: Ankara

Başka ilanlara göz atmaya devam edebilirsiniz.
```

---

## ❗ Sık Karşılaşılan Hatalar

### 1. "Invalid access token"
**Çözüm:** 
- Access token'ın doğru olduğundan emin olun
- Kalıcı token oluşturun (24 saat geçerliliği olanlar çabuk biter)

### 2. "Phone number not found"
**Çözüm:**
- META_PHONE_NUMBER_ID'yi kontrol edin
- WhatsApp Dashboard'dan doğru Phone ID'yi kopyalayın

### 3. "Webhook verification failed"
**Çözüm:**
- META_WEBHOOK_VERIFY_TOKEN doğru mu?
- Meta Dashboard'da aynı token'ı girdiniz mi?

### 4. "User not found" 
**Çözüm:**
- Telefon numaranızı profilde kaydettiğinizden emin olun
- Numara formatı: +905551234567 (ülke kodu ile)

### 5. Mesaj gelmiyor
**Çözüm:**
- Webhook doğru yapılandırılmış mı?
- Ngrok çalışıyor mu? (local test için)
- Flask çalışıyor mu?
- Webhook'a gelen istekleri kontrol edin

---

## 🔒 Güvenlik Notları

⚠️ **ÖNEMLİ:**
- `.env` dosyasını ASLA GitHub'a yüklemeyin!
- `.gitignore` dosyasına `.env` eklendi mi kontrol edin
- Production'da güçlü SECRET_KEY kullanın
- Access Token'ları güvenli saklayın

---

## 📚 Detaylı Dokümantasyon

- **Tam Kurulum Rehberi:** `WHATSAPP_KURULUM.md`
- **Meta Docs:** https://developers.facebook.com/docs/whatsapp
- **API Reference:** https://developers.facebook.com/docs/whatsapp/cloud-api

---

## 🆘 Destek

Sorun mu yaşıyorsunuz?

1. **Dokümantasyonu okuyun:** `WHATSAPP_KURULUM.md`
2. **Test yapın:** `python setup_whatsapp.py test`
3. **Log'ları kontrol edin:** Flask terminal çıktısı
4. **İletişim:** destek@utap.com.tr

---

## ✅ Checklist

Kurulumu tamamladınız mı? Kontrol edin:

- [ ] Meta Developer hesabı oluşturdum
- [ ] WhatsApp Business App oluşturdum
- [ ] Phone Number ID aldım
- [ ] Access Token aldım (kalıcı token)
- [ ] `.env` dosyasını oluşturdum
- [ ] Credentials'ları `.env`'e ekledim
- [ ] Webhook'u yapılandırdım
- [ ] Test numarası ekledim
- [ ] Web arayüzünden test yaptım
- [ ] WhatsApp'tan #YARDIM göndererek test ettim

Hepsi tamamsa: **🎉 Hazırsınız!**

---

**Başarılar! 🚀**

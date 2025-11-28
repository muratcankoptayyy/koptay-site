# 🚀 Meta WhatsApp Cloud API Kurulum Rehberi

## ✅ Entegrasyon Tamamlandı!

Kodlar hazır! Sadece Meta hesabını ayarlaman gerekiyor.

---

## 📋 Adım 1: Meta Business Hesabı Oluştur

1. **Facebook Business Manager'a Git**
   - https://business.facebook.com
   - "Hesap Oluştur" tıkla
   - İş bilgilerini doldur:
     - İş Adı: "Tevkil Ağı" veya şirket adın
     - Adın
     - İş E-mailan

2. **Hesabını Doğrula**
   - E-posta doğrulama linkine tıkla
   - Telefon numaranı doğrula

---

## 📋 Adım 2: WhatsApp Business Platform Setup

### 2.1. WhatsApp Business App Oluştur

1. Meta Business Manager → **Ayarlar** (Settings)
2. Sol menüden **İş Entegrasyonları** (Business Integrations)
3. **WhatsApp** → **Başlat** (Get Started)
4. Veya direkt: https://business.facebook.com/wa/manage/home/

### 2.2. WhatsApp Business Hesabı Oluştur

1. **Create WhatsApp Business Account** tıkla
2. İş bilgilerini doldur:
   - Business Name: "Tevkil Ağı"
   - Category: "Professional Services" veya "Legal"
   - Description: "Avukatlar arası iş devri platformu"

### 2.3. Telefon Numarası Ekle

1. **Add Phone Number** tıkla
2. **Türk numaranı gir** (+90 555 123 4567)
3. **SMS veya Çağrı ile Doğrula**
   - Doğrulama kodu gelecek
   - Kodu gir
4. ✅ Numara onaylandı!

---

## 📋 Adım 3: API Credentials Al

### 3.1. Phone Number ID Al

1. WhatsApp Manager → **API Setup**
2. **Phone Number ID** göreceksin
   - Örnek: `123456789012345`
   - 📋 Kopyala!

### 3.2. Access Token Al

1. Aynı sayfada **Temporary Access Token** göreceksin
2. **Copy** tıkla
   - Bu token 24 saat geçerli (test için yeterli)
3. 📋 Kopyala!

### 3.3. Permanent Token Oluştur (Production İçin)

1. Meta Business Manager → **Sistem Kullanıcıları** (System Users)
2. **Ekle** → "WhatsApp Bot" adıyla sistem kullanıcısı oluştur
3. **Token Oluştur** tıkla
4. İzinler:
   - ✅ whatsapp_business_management
   - ✅ whatsapp_business_messaging
5. Token'ı **GÜVENLİ BİR YERE KAYDET!**
   - Bu token bir daha gösterilmeyecek
   - Kaybedersen yenisini oluşturman gerekir

---

## 📋 Adım 4: .env Dosyasını Güncelle

`.env` dosyasında şunları değiştir:

```env
# Meta WhatsApp Cloud API
META_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxx  # 👈 Buraya token yapıştır
META_PHONE_NUMBER_ID=123456789012345  # 👈 Buraya Phone Number ID yapıştır
META_WEBHOOK_VERIFY_TOKEN=Tevkil2024_Secure_Webhook_9x7mN2p  # 👈 Bu zaten hazır
META_API_VERSION=v21.0  # 👈 Bu da hazır
```

**Örnek:**
```env
META_ACCESS_TOKEN=EAAUtDMHauXgBOxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
META_PHONE_NUMBER_ID=855387697648523
META_WEBHOOK_VERIFY_TOKEN=Tevkil2024_Secure_Webhook_9x7mN2p
META_API_VERSION=v21.0
```

---

## 📋 Adım 5: Webhook Ayarla

### 5.1. Public URL Al (Ngrok ile Test)

**Local test için Ngrok kullan:**

```bash
# Ngrok indir: https://ngrok.com/download
# Çalıştır:
ngrok http 5000

# Çıktı:
# Forwarding: https://abc123.ngrok.io -> http://localhost:5000
```

📋 `https://abc123.ngrok.io` URL'ini kopyala

### 5.2. Meta'da Webhook Ayarla

1. WhatsApp Manager → **Yapılandırma** (Configuration)
2. **Webhook** bölümü
3. **Edit** tıkla
4. **Callback URL**: `https://abc123.ngrok.io/api/whatsapp/webhook`
5. **Verify Token**: `Tevkil2024_Secure_Webhook_9x7mN2p`
6. **Verify and Save** tıkla

✅ Meta webhook'u doğrulayacak!

### 5.3. Webhook Subscription'ları Ayarla

1. **Webhook Fields** kısmında **Subscribe** butonu
2. Şunları seç:
   - ✅ **messages** (Gelen mesajlar)
   - ✅ **message_status** (Mesaj durumu)
3. **Subscribe** tıkla

---

## 📋 Adım 6: Test Et!

### 6.1. İlk Mesajı Gönder

1. **Kendi WhatsApp numarana** test mesajı gönder
2. Meta Console → **API Setup** sayfasında **Send Test Message** var
3. Veya direkt web sitemizden test et:
   - http://localhost:5000/whatsapp-ilan
   - "Bot'u Test Et" bölümü

### 6.2. Test Mesajı

WhatsApp'tan bot numarana gönder:

```
#ILAN
Başlık: Test İlan Oluşturma
Kategori: Ceza Hukuku
Şehir: İstanbul
Açıklama: Bu bir test ilanıdır
Fiyat: 1000
Aciliyet: Normal
```

### 6.3. Sonuç

✅ Bot otomatik yanıt verecek:
```
✅ İlan başarıyla oluşturuldu!

İlan No: #123
Başlık: Test İlan Oluşturma
...
```

✅ İlan web sitesinde görünecek!

---

## 📋 Adım 7: Production'a Geç (Railway Deployment)

### 7.1. Railway Deploy

```bash
# Railway'e push et
git add .
git commit -m "Meta WhatsApp API entegrasyonu"
git push
```

### 7.2. Railway'de Environment Variables

Railway Dashboard → **Variables** → Ekle:

```
META_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxx
META_PHONE_NUMBER_ID=123456789012345
META_WEBHOOK_VERIFY_TOKEN=Tevkil2024_Secure_Webhook_9x7mN2p
META_API_VERSION=v21.0
```

### 7.3. Production Webhook URL

1. Railway URL'ini al: `https://yourapp.up.railway.app`
2. Meta Webhook'u güncelle:
   - Callback URL: `https://yourapp.up.railway.app/api/whatsapp/webhook`
   - Verify Token: `Tevkil2024_Secure_Webhook_9x7mN2p`

---

## 🎉 TAMAMLANDI!

### ✅ Çalışan Özellikler:

1. **WhatsApp'tan İlan Oluşturma**
   - Kullanıcı bot numarasına #ILAN ile mesaj gönderir
   - Bot otomatik ilan oluşturur
   - Onay mesajı gönderir

2. **Başvuru Bildirimleri**
   - Başvuru geldiğinde ilan sahibine WhatsApp bildirimi
   - Başvuran bilgileri, teklif, mesaj

3. **Kabul/Red Bildirimleri**
   - Kabul edildiğinde her iki tarafa bildirim
   - Red edildiğinde başvurana bildirim

4. **Real-time**
   - Tüm bildirimler anlık
   - Webhook ile otomatik

---

## 🔧 Sorun Giderme

### Problem: "Webhook verification failed"

**Çözüm:**
- Verify Token'ın .env'de doğru olduğundan emin ol
- Ngrok URL'inin doğru olduğundan emin ol
- `/api/whatsapp/webhook` endpoint'inin çalıştığını test et

### Problem: "Access token invalid"

**Çözüm:**
- Temporary token 24 saat geçerli, yenisini al
- Veya permanent token oluştur (Adım 3.3)

### Problem: "Phone number not registered"

**Çözüm:**
- Kullanıcının profilde WhatsApp numarasını kaydetmiş olması lazım
- Profile Edit → WhatsApp Numarası ekle

### Problem: "Message not sent"

**Çözüm:**
- .env dosyasındaki credentials'ları kontrol et
- Meta Business Manager'da phone number'ın aktif olduğundan emin ol
- Log'lara bak: `print()` çıktılarını kontrol et

---

## 📞 Destek

Herhangi bir sorun yaşarsan:

1. **Meta Documentation**: https://developers.facebook.com/docs/whatsapp/cloud-api
2. **Ngrok Docs**: https://ngrok.com/docs
3. **Console Log'lar**: Flask debug mode'da hataları gösterir

---

## 💰 Maliyet

- **İlk 1000 konuşma/ay**: **ÜCRETSİZ** 🎉
- Sonrası: ~$0.005/mesaj (≈0.17 TL)
- Business Profile: **ÜCRETSİZ**

**900 TL bütçenle 6+ ay rahat kullanabilirsin!**

---

## 🚀 Sonraki Adımlar

1. Meta hesabını oluştur (15 dk)
2. Credentials'ları .env'e ekle (2 dk)
3. Webhook ayarla (5 dk)
4. Test et! (2 dk)
5. **HAZIR!** 🎉

Başarılar! 🚀

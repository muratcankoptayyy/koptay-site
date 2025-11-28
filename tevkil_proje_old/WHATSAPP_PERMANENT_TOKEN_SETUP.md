# 🔐 WHATSAPP KALICI TOKEN KURULUMU

## 📋 ÖNCEKİ DURUM (Geçici Token - 24-72 saat)
```
❌ Test Mode Token → Her gün yenilenmeli
❌ Developer Console'dan manuel alınıyor
❌ Production için UYGUN DEĞİL!
```

## ✅ YENİ DURUM (Kalıcı System User Token)
```
✅ Permanent Token → ASLA EXPIRE OLMAZ
✅ Otomatik yenileme yok
✅ Production'a hazır
✅ 7/24 çalışır
```

---

## 🎯 ADIM ADIM KURULUM

### ADIM 1: Meta Business Hesabı Doğrula

1. **Meta Business Suite**'e git:
   - https://business.facebook.com/

2. **İşletme Hesabı** seç ya da oluştur:
   - Ulusal Tevkil Ağı

3. **Doğrulama** (Business Verification):
   - Settings → Security Center → Business Verification
   - ⚠️ **ÖNEMLİ**: Tam doğrulama gerekli (ID, vergi belgesi)
   - Süre: 1-3 iş günü

**Neden Gerekli?**
- Kalıcı token için business hesabı doğrulanmalı
- API limitleri artırılır (1000 → Unlimited mesaj/gün)

---

### ADIM 2: System User Oluştur (Kalıcı Token için)

1. **Business Settings** → **Users** → **System Users**
   - https://business.facebook.com/settings/system-users

2. **Add System User** tıkla:
   ```
   Name: Tevkil API Bot
   Role: Admin
   ```

3. **Generate New Token** tıkla:
   - App seç: (WhatsApp Business App'iniz)
   - Permissions seç:
     ✅ whatsapp_business_management
     ✅ whatsapp_business_messaging
     ✅ business_management
   - Token Expiration: **Never (Asla)**

4. **Token'ı KAYDET**:
   ```
   EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   ⚠️ Bu token bir daha gösterilmeyecek! Hemen kaydet!

---

### ADIM 3: WhatsApp Business Account'a Erişim Ver

1. System User sayfasında:
   - **Assets** → **Apps** → **Add Assets**
   - WhatsApp Business App'inizi seç
   - **Full Control** yetkisi ver

2. **WhatsApp Business Account** ekle:
   - Assets → WhatsApp Accounts → Add
   - Hesabınızı seç
   - **Manage WhatsApp Account** yetkisi ver

---

### ADIM 4: Phone Number ID Al

1. **Meta for Developers** → Your Apps:
   - https://developers.facebook.com/apps/

2. WhatsApp App'inizi aç

3. **API Setup** sekmesine git:
   ```
   Phone number ID: 123456789012345
   ```
   Bu numarayı kopyala!

4. **Test numarası** ekle (ilk testler için):
   - Add phone number
   - Kendi numaranı ekle (+905xxxxxxxxx)

---

### ADIM 5: Webhook Kurulumu (Production)

1. **Webhook URL** hazırla:
   ```
   https://tevkil.fly.dev/api/whatsapp/webhook
   ```
   (Fly.io deploy'dan sonra bu URL'i alacağız)

2. **Verify Token** belirle:
   ```
   tevkil_webhook_2025_production
   ```

3. **Meta Dashboard** → **Webhooks**:
   - Callback URL: `https://tevkil.fly.dev/api/whatsapp/webhook`
   - Verify token: `tevkil_webhook_2025_production`
   - Fields: `messages` (subscribe)

4. **Test** tıkla → Başarılı olmalı!

---

### ADIM 6: .env Dosyasını Güncelle

Projende `.env` dosyası oluştur (`.env.example`'dan kopyala):

```bash
# META WHATSAPP BUSINESS API - PRODUCTION
META_PHONE_NUMBER_ID=123456789012345  # ADIM 4'ten aldın
META_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # ADIM 2'den aldın (KALICI!)
META_API_VERSION=v21.0
META_WEBHOOK_VERIFY_TOKEN=tevkil_webhook_2025_production

# Flask
FLASK_SECRET_KEY=super-secret-production-key-change-this
FLASK_ENV=production

# Database (Fly.io'da otomatik olacak)
DATABASE_URL=postgresql://...

# Base URL (Deploy'dan sonra güncellenecek)
BASE_URL=https://tevkil.fly.dev
```

---

### ADIM 7: Webhook Endpoint'i Kontrol Et

Mevcut webhook kodunu kontrol edelim:

```python
# app.py'de webhook endpoint'i var mı?
@app.route('/api/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    # Verification (GET)
    if request.method == 'GET':
        ...
    
    # Mesaj alma (POST)
    if request.method == 'POST':
        ...
```

---

## 🔒 GÜVENLİK KONTROL LİSTESİ

### ✅ Yapılması Gerekenler:

1. **Token Güvenliği**:
   - ✅ `.env` dosyasını `.gitignore`'a ekle
   - ✅ Token'ı ASLA GitHub'a pushlamadın
   - ✅ Production'da environment variable olarak sakla

2. **Webhook Güvenliği**:
   - ✅ Verify token kullan
   - ✅ Signature doğrulaması ekle (opsiyonel ama önerilir)
   - ✅ HTTPS kullan (HTTP kabul edilmez!)

3. **Rate Limiting**:
   - ✅ Meta limitleri: 1000 msg/gün (unverified), Unlimited (verified)
   - ✅ Flask-Limiter ile internal rate limit ekle

---

## 🧪 TEST SENARYOSU

### 1. Token Testi (Terminal):

```bash
# Test 1: Token geçerli mi?
curl -X GET "https://graph.facebook.com/v21.0/me?access_token=YOUR_TOKEN"

# Başarılı cevap:
{
  "id": "123456789012345",
  "name": "Ulusal Tevkil Ağı"
}
```

### 2. Mesaj Gönderme Testi:

```bash
# Test 2: Kendine mesaj gönder
curl -X POST "https://graph.facebook.com/v21.0/PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "905XXXXXXXXX",
    "type": "text",
    "text": {
      "body": "Test mesajı - Kalıcı token çalışıyor! 🎉"
    }
  }'
```

### 3. Webhook Testi (Ngrok ile local):

```bash
# Terminal 1: Ngrok başlat
ngrok http 5000

# Terminal 2: Flask app çalıştır
python app.py

# Meta Dashboard'da webhook URL'i güncelle:
# https://xxxx-xx-xx-xxx-xxx.ngrok.io/api/whatsapp/webhook
```

Kendine WhatsApp'tan mesaj at → Console'da log görmelisin!

---

## 📊 TOKEN KARŞILAŞTIRMASI

| Özellik | Geçici Token (Test) | Kalıcı Token (Production) |
|---------|-------------------|-------------------------|
| **Süre** | 24-72 saat | Asla expire olmaz ✅ |
| **Alınır** | Developer Console | System User |
| **Permissions** | Sınırlı | Full control |
| **Rate Limit** | 1000 msg/gün | Unlimited (verified) |
| **Production** | ❌ Hayır | ✅ Evet |
| **Yenileme** | Her gün manuel | Gerekmiyor! |

---

## 🚨 SORUN GİDERME

### Hata: "Invalid OAuth access token"
**Çözüm:**
- Token'ı doğru kopyaladın mı?
- System User'a WhatsApp erişimi verdin mi?
- Token expire olmamış mı? (Never seçtin mi?)

### Hata: "Webhook verification failed"
**Çözüm:**
- Verify token doğru mu? (Meta Dashboard = .env)
- HTTPS kullanıyor musun? (HTTP kabul edilmez)
- Endpoint `/api/whatsapp/webhook` doğru mu?

### Hata: "Rate limit exceeded"
**Çözüm:**
- Business account verified mı?
- Günde 1000 mesajdan fazla gönderiyorsun
- Business verification sonrasında unlimited olacak

---

## ✅ SONRAKI ADIMLAR

1. **Şimdi yap**:
   - [ ] Meta Business hesabını doğrula (1-3 gün)
   - [ ] System User oluştur
   - [ ] Kalıcı token al
   - [ ] `.env` dosyasını güncelle

2. **Test et**:
   - [ ] Token'ı test et (curl)
   - [ ] Kendine mesaj gönder
   - [ ] Webhook'u test et (ngrok)

3. **Deploy et**:
   - [ ] Fly.io'ya deploy
   - [ ] Production webhook URL güncelle
   - [ ] CANLI TEST! 🚀

---

## 💡 ÖNEMLİ NOTLAR

1. **Token'ı SAKLA**:
   - System User token'ı bir daha gösterilmez!
   - Password manager'da sakla
   - Backup al

2. **Business Verification ÖNEMLİ**:
   - Rate limit kaldırılır (unlimited)
   - Green checkmark alırsın
   - Kullanıcılar daha fazla güvenir

3. **Template Mesajlar**:
   - İlk 24 saat: Template gerekli
   - Sonra: Free-form mesaj gönderebilirsin
   - Template'leri önceden onaylat!

---

## 🎯 HEMEN BAŞLA

### 1. Meta Business Settings'e git:
https://business.facebook.com/settings/system-users

### 2. System User oluştur ve token al

### 3. Token'ı bana ver, `.env`'e ekleyelim! 

**Hazır mısın? System User oluşturmaya başlayalım mı?** 😊

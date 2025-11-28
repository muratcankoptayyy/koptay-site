# 📱 WhatsApp Credentials Nasıl Alınır?

## 🎯 ÖZETİN ÖZETİ (1 DAKİKA)

1. **Meta Developer hesabı aç:** https://developers.facebook.com
2. **Uygulama oluştur:** "Business" tipinde
3. **WhatsApp ekle:** Add Product → WhatsApp
4. **2 değer kopyala:**
   - **Phone Number ID:** `123456789012345`
   - **Access Token:** `EAAxxxxxxxxxx...`
5. **`.env` dosyasına yapıştır**
6. **Bitti!** 🎉

---

## 📸 ADIM ADIM EKRAN GÖRÜNTÜLERİYLE

### 1. Meta Developer Hesabı (2 dakika)

```
🌐 https://developers.facebook.com
   ↓
👤 "Başlat" → Facebook ile giriş
   ↓
✅ Developer hesabı oluştur
```

### 2. Uygulama Oluşturma (1 dakika)

```
🌐 https://developers.facebook.com/apps/
   ↓
➕ "Uygulama Oluştur"
   ↓
🏢 "Business" seç
   ↓
📝 İsim: "Ulusal Tevkil Ağı"
    E-posta: info@utap.com.tr
   ↓
✅ "Uygulama Oluştur"
```

### 3. WhatsApp Ekleme (1 dakika)

```
📱 App Dashboard
   ↓
➕ "Add Product"
   ↓
💬 "WhatsApp" → "Set Up"
   ↓
📋 "Getting Started" sayfası açılır
```

### 4. Credentials Kopyalama (30 saniye)

**Sayfada görecekleriniz:**

```
┌─────────────────────────────────────────────┐
│ Phone number ID                             │
│ 123456789012345                  [KOPYALA]  │ ← BU
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Temporary access token                      │
│ EAABwzLixnjYBO7Yr0BQl...        [KOPYALA]  │ ← BU
└─────────────────────────────────────────────┘
```

### 5. .env Dosyasına Yapıştırma (30 saniye)

Proje klasöründe `.env` dosyası oluşturun:

```env
META_PHONE_NUMBER_ID=123456789012345
META_ACCESS_TOKEN=EAABwzLixnjYBO7Yr0BQl...
META_WEBHOOK_VERIFY_TOKEN=tevkil_webhook_2025
FLASK_SECRET_KEY=dev-secret-key-2025
```

**TAMAM! Kurulum bitti!** ✅

---

## 🚀 HIZLI KURULUM - KOPYALA YAPIŞTIR

### Otomatik Script ile:

```bash
python setup_whatsapp.py
```

Bu script:
- Size adım adım rehberlik eder
- `.env` dosyasını otomatik oluşturur
- Bağlantıyı test eder

### Manuel ile:

**1. `.env` dosyası oluştur:**
```bash
copy .env.example .env
```

**2. Değerleri değiştir:**
```env
# ÖNCESİ (örnek dosyada):
META_PHONE_NUMBER_ID=your_phone_number_id_here
META_ACCESS_TOKEN=your_permanent_access_token_here

# SONRASI (gerçek değerler):
META_PHONE_NUMBER_ID=123456789012345
META_ACCESS_TOKEN=EAABwzLixnjYBO7Yr0BQl...
```

**3. Kaydet ve kapat!**

---

## 🔑 Credentials'ların Konumları

### META_PHONE_NUMBER_ID

**Konum:**
```
WhatsApp Dashboard
→ API Setup
→ "Phone number ID" 
```

**Nasıl görünür:**
```
Phone number ID: 123456789012345 [📋]
```

**Format:** Sadece rakamlar (15 haneli)

---

### META_ACCESS_TOKEN

**2 TÜR VAR:**

#### A) Geçici Token (24 saat) - Test için

**Konum:**
```
WhatsApp Dashboard
→ API Setup
→ "Temporary access token"
```

**Nasıl görünür:**
```
Temporary access token: EAABwzL... [📋]
```

#### B) Kalıcı Token (Sınırsız) - Production için ⭐ ÖNERİLEN

**Konum:**
```
https://business.facebook.com
→ Business Settings (⚙️)
→ Users → System Users
→ Add → İsim: "WhatsApp Bot"
→ Generate New Token
→ App seçin: "Ulusal Tevkil Ağı"
→ İzinler seç:
   ✅ whatsapp_business_management
   ✅ whatsapp_business_messaging
→ Generate Token
```

**Nasıl görünür:**
```
Access Token: EAABwzLixnjYBO7Yr0BQl... [📋]
⚠️ Bu token'ı bir daha göremezsiniz!
```

**Format:** `EAA` ile başlar, çok uzun (200+ karakter)

---

### META_WEBHOOK_VERIFY_TOKEN

**Özel durum:** Bu kendiniz belirlersiniz!

**Önerilen:** `tevkil_webhook_2025`

**Kullanım:**
```
1. .env dosyasına: META_WEBHOOK_VERIFY_TOKEN=tevkil_webhook_2025
2. Meta Dashboard'a: Aynı değeri girin
```

---

## 📋 CHECKLIST - Eksik Bir Şey Var mı?

Kontrol edin:

- [ ] Meta Developer hesabım var
- [ ] WhatsApp Business App oluşturdum
- [ ] Phone Number ID'yi kopyaladım
- [ ] Access Token'ı kopyaladım
- [ ] `.env` dosyası oluşturdum
- [ ] İki değeri `.env`'e yapıştırdım
- [ ] Dosyayı kaydettim

Hepsi ✅ ise: **HAZIR!**

---

## 🧪 TEST ETME

### Yöntem 1: Script ile Test

```bash
python setup_whatsapp.py test
```

**Çıktı:**
```
✅ Phone Number ID: 123456789012345
✅ Access Token: EAABwzLixnjYBO7Yr0...**********************
✅ Webhook Token: tevkil_webhook_2025
📡 Meta API bağlantı testi yapılıyor...
✅ Bağlantı başarılı!
```

### Yöntem 2: Web Arayüzü ile Test

```
1. python app.py
2. http://127.0.0.1:5000/whatsapp/setup
3. Test bölümü → "#YARDIM" → Gönder
```

**Başarılıysa:**
```
✅ İşlem başarılı!
📖 ULUSAL TEVKİL AĞI - YARDIM

🔹 KOMUTLAR:
#ILAN - Yeni ilan oluştur
#YARDIM - Bu yardım menüsü
...
```

---

## ❌ SORUN GİDERME - HIZLI ÇÖZÜMLER

### "Phone number ID not found"
```
❌ Sorun: META_PHONE_NUMBER_ID yanlış
✅ Çözüm: WhatsApp Dashboard → API Setup → Tekrar kopyala
```

### "Invalid access token"
```
❌ Sorun: Token süresi dolmuş veya yanlış
✅ Çözüm: 
   1. Kalıcı token oluştur (yukarıdaki B şıkkı)
   2. Yeni token'ı .env'e yapıştır
```

### ".env dosyası yüklenmiyor"
```
❌ Sorun: Dosya adı yanlış veya konumu hatalı
✅ Çözüm:
   1. Dosya adı tam olarak: .env (nokta ile başlar)
   2. Konum: Proje ana klasörü (app.py ile aynı yerde)
```

### "Webhook verification failed"
```
❌ Sorun: Webhook token uyuşmuyor
✅ Çözüm:
   1. .env'deki: META_WEBHOOK_VERIFY_TOKEN=tevkil_webhook_2025
   2. Meta'daki: Verify Token = tevkil_webhook_2025
   3. İkisi de aynı olmalı!
```

---

## 📞 DESTEK

Hala sorun mu yaşıyorsunuz?

1. **Detaylı rehber okuyun:** `WHATSAPP_KURULUM.md`
2. **Hızlı başlangıç:** `WHATSAPP_HIZLI_BASLANGIC.md`
3. **E-posta:** destek@utap.com.tr

---

## 💡 İPUCU

**İlk kez yapıyorsanız:**
1. Geçici token ile başlayın (hızlı test)
2. Her şey çalışınca kalıcı token oluşturun
3. Production'a geçin

**Tavsiye:** Script kullanın, her şey otomatik olsun!

```bash
python setup_whatsapp.py
```

---

**Başarılar!** 🎉

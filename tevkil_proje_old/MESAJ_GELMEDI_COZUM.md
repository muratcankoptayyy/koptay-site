# 🚨 MESAJ GELMEDİ SORUNU - ÇÖZÜM

## 🎯 Sorun: "Recipient phone number not in allowed list"

Meta WhatsApp API **test modunda** çalışıyor. Test modunda sadece izin verilen numaralara mesaj gönderilebilir.

---

## ✅ ÇÖZÜM: 3 ADIMDA NUMARA EKLE

### Adım 1: Meta Business Manager'a Git

1. https://business.facebook.com/wa/manage/home/
2. WhatsApp Manager'ı aç
3. Sol menüden **"API Setup"** seçeneğine tıkla

### Adım 2: Test Numarası Ekle

1. **"Step 5: Send Messages with the API"** bölümünü bul
2. **"To:"** kısmında **"Manage phone number list"** linkine tıkla
   - VEYA direkt: "Add recipient phone number" butonuna tıkla

3. Açılan pencerede:
   - **Phone Number**: `+905307111864` (senin numaran)
   - **Name**: İsmin (örn: "Ahmet")
   - **Add** butonuna tıkla

4. **Telefona doğrulama kodu gelecek**
   - WhatsApp'tan kod gelir
   - Kodu Meta sayfasına gir
   - **Verify** tıkla

5. ✅ Numaran artık izin listesinde!

### Adım 3: Test Et

```bash
python debug_meta_api.py
```

Numaran: `905307111864` (veya `5307111864`)

---

## 🚀 ALTERNATİF: Meta'nın Test Arayüzünü Kullan

Daha kolay yol:

1. WhatsApp Manager → **API Setup**
2. **Step 5: Send Messages with the API** bölümü
3. **"To:"** dropdown'dan numaranı seç
4. Message alanına bir şey yaz
5. **"Send Message"** tıkla

Bu şekilde direkt Meta'nın arayüzünden test edebilirsin!

---

## 📋 Ekran Görüntüleri Rehberi

### 1. WhatsApp Manager'a Git
```
https://business.facebook.com/wa/manage/phone-numbers/
└─ Soldaki menüden "API Setup" seç
```

### 2. Recipient Phone Number Ekle
```
API Setup Sayfası
└─ Step 5: Send Messages with the API
   └─ To: [Manage phone number list] ← Buraya tıkla
      └─ + Add phone number ← Buraya tıkla
         └─ +905307111864 gir
         └─ Name: Ahmet
         └─ Add & Verify
```

### 3. WhatsApp'tan Kod Al
```
WhatsApp'ına gelecek:
"Your WhatsApp Business verification code is: 123456"

Meta sayfasına kodu gir → Verify tıkla → ✅ Numara eklendi!
```

---

## ⚡ HIZLI TEST (Meta UI'dan)

Numara ekledikten sonra:

1. API Setup sayfası
2. "To:" dropdown → Numaranı seç
3. Message: "Test mesajı"
4. **Send Message** tıkla
5. ✅ WhatsApp'ına mesaj gelecek!

---

## 🎉 Production'a Geçiş (Tüm Numaralara Mesaj Gönder)

Test modundan çıkmak için:

1. Meta Business Manager → WhatsApp → **Settings**
2. **Business Verification** tamamla
3. **WhatsApp Business Account Review** başvur
4. Onay gelince **tüm numaralara** mesaj gönderebilirsin!

Ama şimdilik test modu yeterli! İzin listesine 5-10 numara ekleyebilirsin.

---

## 📞 Önemli Notlar

- ✅ Test modunda **5 numara** ücretsiz eklenebilir
- ✅ Her numara WhatsApp doğrulaması gerektirir
- ✅ Test modunda **1000 mesaj/ay** ücretsiz
- ✅ Production'a geçince **tüm numaralara** gönderebilirsin

---

## 🔧 Sorun Devam Ederse

Numara eklemeye çalış, hata alırsan söyle! Birlikte çözeriz. 😊

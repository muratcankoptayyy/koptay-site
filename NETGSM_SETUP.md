# 📱 Netgsm SMS Entegrasyonu Kurulum Rehberi

## ✅ Kurulum Tamamlandı!

SMS servisi sisteme entegre edildi. Şimdi sadece Netgsm hesabı açıp API bilgilerini girmen gerekiyor.

---

## 🚀 1. Netgsm Hesap Açma

### Adım 1: Kayıt Ol
1. **Web sitesi:** https://www.netgsm.com.tr
2. **"Ücretsiz Dene"** veya **"Kayıt Ol"** butonuna tıkla
3. Firma bilgilerini gir:
   - Firma adı: Tevkil Platform (veya kendi firma adın)
   - Telefon: 0530 711 1864
   - E-posta: aktif bir email adresi
   - Vergi/TC No

### Adım 2: Demo Kredisi Al
- İlk kayıtta **500 TL** demo kredisi veriyorlar
- Test amaçlı kullanabilirsin

### Adım 3: Başlık (Sender ID) Tanımla
- Netgsm panelinde **"Başlık Tanımla"** bölümüne git
- **Başlık:** `TEVKIL` (11 karakter max)
- Onay süreci: 1-2 iş günü
- Onay beklerken **numerik başlık** (telefon numarası) kullanılır

---

## 🔑 2. API Bilgilerini Al

### Netgsm Paneli:
1. Giriş yap: https://www.netgsm.com.tr/giris
2. **"Ayarlar" → "API Bilgileri"** menüsüne git
3. Şu bilgileri kopyala:
   - **Kullanıcı Adı:** (genelde firma telefon numarası)
   - **Şifre:** (API şifresi, normal şifre değil!)

---

## ⚙️ 3. .env Dosyasını Güncelle

`.env` dosyasını aç ve şu satırları doldur:

```env
# Netgsm SMS Configuration
NETGSM_USERNAME=8503XXXXXXX         # Netgsm kullanıcı adın
NETGSM_PASSWORD=your-api-password   # Netgsm API şifren
NETGSM_SENDER=TEVKIL                # Mesaj başlığı (onaylandıysa)
```

**Not:** Başlık onayı gelmeden, `NETGSM_SENDER` yerine telefon numaranı kullanabilirsin.

---

## 🧪 4. Test Et

Test scripti hazır! Şu komutu çalıştır:

```powershell
python sms_service.py
```

**ÖNEMLİ:** Test etmeden önce:
1. `sms_service.py` dosyasını aç
2. En altta `test_phone = "5XXXXXXXXX"` satırını bul
3. Kendi telefon numaranı gir: `test_phone = "5307111864"`
4. Dosyayı kaydet
5. Test komutunu çalıştır

---

## 📊 5. Fiyatlandırma

### Netgsm SMS Ücretleri:
- **Standart SMS:** ~0.03-0.05 TL/SMS
- **Toplu SMS:** Daha ucuz (hacme göre indirim)
- **OTP SMS:** ~0.04-0.06 TL/SMS
- **Demo Kredi:** 500 TL (yaklaşık 10,000-15,000 SMS)

### Paket Önerileri:
- **Başlangıç:** 1,000 SMS - ~40-50 TL
- **Orta:** 5,000 SMS - ~150-200 TL
- **Profesyonel:** 50,000 SMS - ~1,000-1,500 TL

---

## 🎯 6. Sisteme Entegre Edilen Özellikler

### ✅ Hazır SMS Fonksiyonları:

1. **`send_new_post_notification()`** - Yeni ilan bildirimi
2. **`send_application_notification()`** - Başvuru bildirimi
3. **`send_urgent_post_alert()`** - Acil ilan uyarısı (toplu)
4. **`send_low_application_reminder()`** - Az başvuru hatırlatması
5. **`send_otp()`** - 2FA doğrulama kodu
6. **`send_application_accepted()`** - Başvuru kabul
7. **`send_application_rejected()`** - Başvuru red

### Örnek Kullanım (app.py içinde):

```python
from sms_service import NetgsmSMSService

sms = NetgsmSMSService()

# Yeni ilan oluşturulduğunda
sms.send_new_post_notification(
    user_phone="5307111864",
    post_title="İstanbul 3. Aile Mahkemesi",
    city="İstanbul",
    price=3000,
    post_id=123
)

# Başvuru geldiğinde
sms.send_application_notification(
    owner_phone="5307111864",
    applicant_name="Av. Ahmet Yılmaz",
    post_title="İstanbul 3. Aile Mahkemesi",
    post_id=123
)

# 2FA kodu gönder
sms.send_otp("5307111864", "123456")
```

---

## ⚠️ Önemli Notlar

1. **Test Aşamasında:**
   - Demo krediyi kullan
   - Sadece kendi numarana test SMS'leri gönder
   
2. **Production'a Geçerken:**
   - Gerçek kredi yükle
   - Başlık onayını bekle
   - SMS gönderim limitlerini ayarla

3. **Güvenlik:**
   - `.env` dosyasını Git'e **EKLEME** (`.gitignore`'da olmalı)
   - API şifresini kimseyle paylaşma
   
4. **Optimizasyon:**
   - Gereksiz SMS gönderme
   - Kullanıcıya SMS tercihi seçeneği sun
   - Günlük/haftalık özet SMS'leri topla

---

## 🆘 Sorun Giderme

### Hata: "Geçersiz kullanıcı adı/şifre" (Kod: 30)
- API şifresini kontrol et (panel şifren değil!)
- Netgsm panelinde yeni API şifresi oluştur

### Hata: "Mesaj başlığı tanımlı değil" (Kod: 40)
- Başlık onayı bekle
- Geçici olarak telefon numaranı başlık olarak kullan

### Hata: "Kredi yok" (Kod: 50)
- Hesabına kredi yükle
- Demo kredinin bittiğini kontrol et

### SMS Gitmiyor
- Telefon numarası formatını kontrol et (5XXXXXXXXX)
- Netgsm panelinde gönderim loglarını kontrol et
- API limitlerini kontrol et

---

## 📞 Netgsm Destek

- **Telefon:** 0850 222 63 84
- **Email:** destek@netgsm.com.tr
- **Canlı Destek:** https://www.netgsm.com.tr (sağ altta chat ikonu)
- **Dokümantasyon:** https://www.netgsm.com.tr/dokuman

---

## ✨ Sonraki Adımlar

1. ✅ Netgsm hesabı aç
2. ✅ API bilgilerini `.env` dosyasına ekle
3. ✅ `sms_service.py` ile test et
4. ✅ `app.py`'e SMS gönderim kodları ekle
5. ✅ Production'da gerçek kredi yükle

**Hazırsın!** 🚀

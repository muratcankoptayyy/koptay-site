# ============================================
# META WHATSAPP BUSINESS API KURULUM REHBERİ
# ============================================

## ADIM 1: META DEVELOPER HESABI OLUŞTURMA

1. https://developers.facebook.com adresine gidin
2. Sağ üst köşeden "Başlat" (Get Started) butonuna tıklayın
3. Facebook hesabınızla giriş yapın (yoksa oluşturun)
4. Developer hesabı oluşturmak için:
   - İsim
   - E-posta
   - Telefon numarası (doğrulama için)
   
5. Hesap türünü seçin:
   ✅ "Business" seçeneğini işaretleyin

---

## ADIM 2: WHATSAPP BUSINESS APP OLUŞTURMA

1. https://developers.facebook.com/apps/ adresine gidin
2. "Uygulama Oluştur" (Create App) butonuna tıklayın
3. Uygulama türünü seçin:
   ✅ "Business" seçin
   
4. Uygulama bilgilerini girin:
   - App Name: "Ulusal Tevkil Ağı" (veya istediğiniz isim)
   - Contact Email: info@utap.com.tr (sizin e-postanız)
   - Business Account: Yeni oluştur veya var olanı seç
   
5. "Uygulama Oluştur" butonuna tıklayın

---

## ADIM 3: WHATSAPP ÜRÜNÜ EKLEME

1. App Dashboard'da "Add Product" bölümüne gidin
2. "WhatsApp" kartını bulun
3. "Set Up" butonuna tıklayın

4. WhatsApp Business API sayfası açılacak:
   - Sol menüden "Getting Started" seçin
   - Burada 2 önemli bilgi göreceksiniz:
   
   📱 **Phone Number ID**: 
      Örnek: 123456789012345
      (Bu numara Meta'nın size verdiği test numarasıdır)
   
   🔑 **Access Token**: 
      Örnek: EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
      (Bu token mesaj göndermeniz için gereklidir)

---

## ADIM 4: TEST NUMARASI EKLEME

1. WhatsApp Dashboard'da "From" bölümünden test numaranızı seçin
2. "To" bölümüne kendi WhatsApp numaranızı ekleyin:
   - Telefon numaranızı girin (örn: +905551234567)
   - WhatsApp'ınıza onay kodu gelecek
   - Kodu girerek numaranızı doğrulayın
   
3. Maksimum 5 test numarası ekleyebilirsiniz (ücretsiz)

---

## ADIM 5: PERMANENT ACCESS TOKEN ALMA

Temporary token 24 saat geçerlidir. Kalıcı token almak için:

1. Meta Business Suite'e gidin: https://business.facebook.com
2. Sol menüden "Business Settings" seçin
3. "System Users" seçin
4. "Add" butonuna tıklayarak yeni sistem kullanıcısı oluşturun:
   - Name: "WhatsApp Bot"
   - Role: "Admin"
   
5. Oluşturulan kullanıcıya tıklayın
6. "Generate New Token" butonuna tıklayın
7. Uygulamanızı seçin (Ulusal Tevkil Ağı)
8. İzinleri seçin:
   ✅ whatsapp_business_management
   ✅ whatsapp_business_messaging
   
9. "Generate Token" butonuna tıklayın
10. Token'ı kopyalayın ve güvenli bir yere kaydedin!

---

## ADIM 6: WEBHOOK YAPLANDIRMA

1. WhatsApp Dashboard'da sol menüden "Configuration" seçin
2. "Webhook" bölümünde "Edit" butonuna tıklayın
3. Webhook URL'i girin:
   
   🌐 **Production için:**
   https://utap.com.tr/api/whatsapp/webhook
   
   🧪 **Test için (Ngrok kullanarak):**
   https://your-ngrok-url.ngrok.io/api/whatsapp/webhook
   
4. Verify Token girin:
   tevkil_webhook_2025
   
5. "Verify and Save" butonuna tıklayın

6. Webhook alanlarını seçin:
   ✅ messages
   
7. "Subscribe" butonuna tıklayın

---

## ADIM 7: .ENV DOSYASINA CREDENTIALS EKLEME

Proje klasöründe `.env` dosyası oluşturun (varsa açın):

```env
# Flask
FLASK_SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///tevkil.db

# Meta WhatsApp Business API
META_PHONE_NUMBER_ID=123456789012345
META_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
META_API_VERSION=v21.0
META_WEBHOOK_VERIFY_TOKEN=tevkil_webhook_2025
```

**ÖNEMLİ:** 
- META_PHONE_NUMBER_ID: WhatsApp Dashboard'dan aldığınız Phone Number ID
- META_ACCESS_TOKEN: Permanent token (yukarıda oluşturduğunuz)
- META_WEBHOOK_VERIFY_TOKEN: Webhook doğrulama için belirlediğiniz token

---

## ADIM 8: NGROK İLE LOCAL TEST (Opsiyonel)

Local bilgisayarınızda test etmek için Ngrok kullanın:

1. Ngrok indirin: https://ngrok.com/download
2. Ngrok hesabı oluşturun (ücretsiz)
3. Auth token'ı alın: https://dashboard.ngrok.com/get-started/your-authtoken
4. Terminal'de ngrok'u yapılandırın:
   ```
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```
5. Flask'ı başlatın:
   ```
   python app.py
   ```
6. Başka bir terminal'de ngrok başlatın:
   ```
   ngrok http 5000
   ```
7. Ngrok size bir URL verecek (örn: https://abc123.ngrok.io)
8. Bu URL'i Meta Webhook ayarlarına ekleyin:
   https://abc123.ngrok.io/api/whatsapp/webhook

---

## ADIM 9: TESTİ ÇALIŞTIRMA

1. Web sitesine giriş yapın: http://127.0.0.1:5000
2. "WhatsApp Ayarları" menüsüne gidin
3. Test bölümünde şu mesajı gönderin:
   ```
   #YARDIM
   ```
4. "Test Komutu Gönder" butonuna tıklayın
5. Eğer başarılıysa, yardım mesajı gelecek!

Gerçek WhatsApp testi için:
1. Telefon numaranızı profilde kaydedin
2. Meta'nın WhatsApp test numarasına (#ADIM 4'te eklediğiniz) mesaj gönderin:
   ```
   #ILAN
   Başlık: Test İlan
   Kategori: Ceza Hukuku
   Şehir: Ankara
   Açıklama: Test mesajı
   Fiyat: 2500
   Aciliyet: Normal
   ```
3. Bot otomatik cevap verecek!

---

## SORUN GİDERME

### Hata: "Invalid access token"
✅ Çözüm: Access token'ı yeniden oluşturun (Permanent token alın)

### Hata: "Phone number not found"
✅ Çözüm: META_PHONE_NUMBER_ID'yi kontrol edin

### Hata: "Webhook verification failed"
✅ Çözüm: META_WEBHOOK_VERIFY_TOKEN'ın doğru olduğundan emin olun

### Hata: "User not found"
✅ Çözüm: Telefon numaranızı profilde kaydettiğinizden emin olun

### Mesaj gelmiyor
✅ Çözüm: 
  - Webhook'un doğru yapılandırıldığından emin olun
  - Ngrok çalışıyor olmalı (local test için)
  - Flask çalışıyor olmalı

---

## GÜVENLİK ÖNERİLERİ

⚠️ Access Token'ı ASLA GitHub'a yüklemeyin!
⚠️ .env dosyasını .gitignore'a ekleyin
⚠️ Production'da güçlü SECRET_KEY kullanın
⚠️ HTTPS kullanın (production için)

---

## FAYDALÎ LİNKLER

📚 Meta WhatsApp Docs: https://developers.facebook.com/docs/whatsapp
📱 WhatsApp Business API: https://business.whatsapp.com
🔧 Ngrok: https://ngrok.com
💼 Meta Business Suite: https://business.facebook.com

---

Kurulum tamamlandı! 🎉
Sorularınız için: destek@utap.com.tr

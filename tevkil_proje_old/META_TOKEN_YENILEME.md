# ============================================
# META WHATSAPP ACCESS TOKEN YENİLEME REHBERİ
# ============================================

## SORUN:
Access Token süresi dolmuş:
"Session has expired on Tuesday, 21-Oct-25 17:00:00 PDT"

## ÇÖZÜM ADIMLARI:

### 1. Meta Business Manager'a Gidin:
https://business.facebook.com/

### 2. WhatsApp Manager'ı Açın:
- Sol menüden "WhatsApp Accounts" seçin
- Hesabınızı seçin

### 3. Yeni Access Token Alın:

#### Yöntem A: Geçici Token (24 saat)
1. https://developers.facebook.com/apps/ adresine gidin
2. Uygulamanızı seçin
3. Sol menüden "WhatsApp" → "API Setup" seçin
4. "Temporary access token" butonuna tıklayın
5. Yeni token'ı kopyalayın

#### Yöntem B: Kalıcı Token (System User - Önerilen)
1. https://business.facebook.com/settings/system-users/ adresine gidin
2. "Add" butonuna tıklayın veya mevcut System User'ı seçin
3. "Generate New Token" butonuna tıklayın
4. Uygulamanızı seçin
5. Şu permissions'ları seçin:
   - whatsapp_business_management
   - whatsapp_business_messaging
6. "Generate Token" butonuna tıklayın
7. Token'ı kopyalayın (GÜVENLİ BİR YERDE SAKLAYIN!)

### 4. .env Dosyasını Güncelleyin:

Yeni token'ı .env dosyasındaki META_ACCESS_TOKEN değerine yapıştırın:

```
META_ACCESS_TOKEN=YENI_TOKEN_BURAYA
```

### 5. Flask'ı Yeniden Başlatın:

PowerShell'de:
```powershell
Get-Process python | Stop-Process -Force
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\KOPTAY\Desktop\tevkil_proje; python run_flask.py"
```

## ÖNEMLİ NOTLAR:

1. **Geçici Token**: 24 saat geçerli, test için uygundur
2. **System User Token**: Süresiz geçerli, production için önerilir
3. **Token Güvenliği**: Token'ı GitHub'a yüklemeyin, .env dosyasını .gitignore'a ekleyin

## TOKEN KONTROL:

Token'ın çalışıp çalışmadığını test edin:
```powershell
python -c "from whatsapp_meta_api import MetaWhatsAppAPI; api = MetaWhatsAppAPI(); print('Token geçerli!' if api.access_token else 'Token yok!')"
```

## HATA KODLARI:

- 190: Invalid or expired token
- 463: Session expired
- 401: Unauthorized

Tüm bu hatalar token yenilemeyle çözülür.

## DESTEK:

Meta WhatsApp Business API Docs:
https://developers.facebook.com/docs/whatsapp/business-management-api/get-started

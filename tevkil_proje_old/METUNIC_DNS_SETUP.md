# 🌐 Metunic DNS Ayarlama Rehberi - utap.com.tr

## 1️⃣ METUNİC KONTROL PANELİNE GİRİŞ

1. **https://metunic.com.tr** adresine gidin
2. Sağ üstteki **"Giriş Yap"** butonuna tıklayın
3. E-posta ve şifrenizle giriş yapın
4. **"Müşteri Paneli"** açılacak

---

## 2️⃣ ALAN ADI YÖNETİMİNE GİT

1. Sol menüden **"Alan Adlarım"** veya **"Domain Names"** seçeneğine tıklayın
2. `utap.com.tr` alan adınızı bulun
3. Sağ tarafta **"Yönet"** veya **"Manage"** butonuna tıklayın

---

## 3️⃣ DNS YÖNETİMİNİ AÇ

İki yöntem var:

### Yöntem A: DNS Sunucularını Değiştir (DAHA KOLAY)
1. **"Name Server Yönetimi"** veya **"DNS Yönetimi"** sekmesine gidin
2. **"Özel Name Server Kullan"** seçeneğini seçin (eğer varsa)
3. Şu name serverleri ekleyin:
   ```
   ns1.metunic.com.tr
   ns2.metunic.com.tr
   ```
4. Kaydet butonuna basın

### Yöntem B: DNS Kayıtlarını Doğrudan Düzenle (ÖNERİLEN)
1. **"DNS Yönetimi"** veya **"DNS Zone Editor"** sekmesine gidin
2. **"Kayıt Ekle"** veya **"Add Record"** butonuna tıklayın

---

## 4️⃣ DNS KAYITLARINI EKLE

Aşağıdaki **4 kayıt**ı tek tek ekleyin:

### ✅ KAYIT 1: Root Domain A Kaydı
```
Kayıt Tipi: A
Host/Name: @ (veya boş bırakın)
Değer/Value: 66.241.124.228
TTL: 3600
```

### ✅ KAYIT 2: Root Domain AAAA Kaydı
```
Kayıt Tipi: AAAA
Host/Name: @ (veya boş bırakın)
Değer/Value: 2a09:8280:1::a9:1e18:0
TTL: 3600
```

### ✅ KAYIT 3: WWW Subdomain A Kaydı
```
Kayıt Tipi: A
Host/Name: www
Değer/Value: 66.241.124.228
TTL: 3600
```

### ✅ KAYIT 4: WWW Subdomain AAAA Kaydı
```
Kayıt Tipi: AAAA
Host/Name: www
Değer/Value: 2a09:8280:1::a9:1e18:0
TTL: 3600
```

**NOT:** 
- Host/Name kısmında `@` sembolü = root domain (utap.com.tr)
- Bazı panellerde `@` yerine boş bırakmanız gerekebilir
- `www` = www.utap.com.tr subdomain'i

---

## 5️⃣ ESKİ KAYITLARI SİL (ÖNEMLİ!)

Eğer varsayılan olarak gelen kayıtlar varsa:
1. **Eski A kayıtlarını silin** (örn: park sayfası kayıtları)
2. **Eski CNAME kayıtlarını silin**
3. **Sadece yukarıdaki 4 kayıt kalmalı**

MX kayıtlarına (e-posta için) dokunmayın!

---

## 6️⃣ KAYDET VE BEKLE

1. Tüm değişiklikleri **kaydedin**
2. **5-30 dakika** bekleyin (DNS yayılması için)
3. Kahve molası verin ☕

---

## 7️⃣ DOĞRULAMA

### PowerShell'de Kontrol:
```powershell
# Root domain kontrolü
nslookup utap.com.tr

# www kontrolü  
nslookup www.utap.com.tr
```

**Beklenen sonuç:**
```
Server:  UnKnown
Address: 192.168.1.1

Name:    utap.com.tr
Addresses:  2a09:8280:1::a9:1e18:0
          66.241.124.228
```

### Fly.io SSL Durumu:
```powershell
fly certs show utap.com.tr -a tevkil
fly certs show www.utap.com.tr -a tevkil
```

**Başarılı durum:**
```
The certificate for utap.com.tr has been issued.

Hostname                  = utap.com.tr
DNS Provider              = metunic
Certificate Authority     = Let's Encrypt
Issued                    = ecdsa
Added to App              = 1 minute ago
Source                    = fly
Status                    = Ready ✅
```

---

## 8️⃣ WEB SİTESİNİ TEST ET

### Tarayıcıda Açın:
```powershell
start https://utap.com.tr
start https://www.utap.com.tr
```

**Kontrol edin:**
- ✅ Sayfa açılıyor mu?
- ✅ Adres çubuğunda 🔒 kilidi var mı? (SSL aktif)
- ✅ HTTPS ile açılıyor mu?

---

## 📸 METUNİC PANEL EKRAN GÖRÜNTÜLERİ

### DNS Kayıt Listesi Şöyle Görünmeli:

```
┌────────────┬──────────┬─────────────────────────┬──────┐
│ Tip        │ Host     │ Değer                   │ TTL  │
├────────────┼──────────┼─────────────────────────┼──────┤
│ A          │ @        │ 66.241.124.228          │ 3600 │
│ AAAA       │ @        │ 2a09:8280:1::a9:1e18:0  │ 3600 │
│ A          │ www      │ 66.241.124.228          │ 3600 │
│ AAAA       │ www      │ 2a09:8280:1::a9:1e18:0  │ 3600 │
└────────────┴──────────┴─────────────────────────┴──────┘
```

---

## ⏱️ ZAMAN ÇİZELGESİ

| Adım | Süre | Açıklama |
|------|------|----------|
| DNS kayıtlarını ekleme | 5 dk | Metunic panelinde işlem |
| DNS yayılması | 5-30 dk | Otomatik (kahve molası ☕) |
| SSL sertifika oluşumu | 2-10 dk | Fly.io otomatik yapar |
| **TOPLAM** | **~30-45 dk** | İlk erişim |

---

## 🚨 SORUN GİDERME

### "DNS kayıtları yayılmadı" Hatası:

**Neden:** DNS değişikliklerinin internet genelinde yayılması zaman alır.

**Çözüm:**
1. 30 dakika bekleyin
2. Farklı DNS sunucularından kontrol edin:
```powershell
nslookup utap.com.tr 8.8.8.8
nslookup utap.com.tr 1.1.1.1
```

### "SSL sertifikası oluşmadı" Hatası:

**Neden:** DNS kayıtları henüz Fly.io'ya ulaşmadı.

**Çözüm:**
1. DNS yayıldığından emin olun (`nslookup`)
2. Sertifikayı manuel tetikleyin:
```powershell
fly certs check utap.com.tr -a tevkil
```

### "Sayfa park sayfasına gidiyor" Hatası:

**Neden:** Metunic'in varsayılan park sayfası kayıtları hala aktif.

**Çözüm:**
1. Metunic paneline girin
2. **Eski A kayıtlarını silin**
3. Sadece Fly.io IP'lerini bırakın
4. DNS cache'i temizleyin:
```powershell
ipconfig /flushdns
```

---

## ✅ BAŞARI KONTROL LİSTESİ

- [ ] Metunic paneline giriş yaptım
- [ ] DNS Yönetimi sayfasını buldum
- [ ] 4 DNS kaydını ekledim (2 A, 2 AAAA)
- [ ] Eski kayıtları sildim
- [ ] Değişiklikleri kaydettim
- [ ] 30 dakika bekledim
- [ ] `nslookup` ile IP'leri doğruladım
- [ ] `fly certs show` ile SSL durumunu kontrol ettim
- [ ] https://utap.com.tr adresini tarayıcıda açtım
- [ ] 🔒 SSL kilidi göründü
- [ ] Web sitesi çalışıyor! 🎉

---

## 📞 YARDIM

Takıldığınız bir yer olursa:
1. Metunic destek: destek@metunic.com.tr
2. Bana ekran görüntüsü gönderin
3. `nslookup` çıktısını paylaşın

**DNS ayarlarını yaptıktan sonra bana haber verin, birlikte kontrol edelim!** 🚀

---

## 🎯 SONRAKİ ADIMLAR

DNS ayarları tamamlandıktan sonra:
1. ✅ Web sitesi `utap.com.tr` adresinden erişilebilir olacak
2. ✅ Privacy Policy URL'i güncellenebilir (Play Store için)
3. ✅ Google Analytics domain değiştirilebilir
4. ✅ Uygulama ayarlarında domain güncellenebilir

**İyi çalışmalar!** 💪

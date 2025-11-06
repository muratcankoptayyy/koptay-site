# 🌐 utap.com.tr Alan Adı Bağlama Rehberi

## ✅ FLY.IO TARAFINDA TAMAMLANDI

Alan adları Fly.io'ya başarıyla eklendi:
- ✅ `utap.com.tr` 
- ✅ `www.utap.com.tr`

---

## 📋 DNS AYARLARI (ALAN ADI SAĞLAYICINIZDA YAPILACAK)

Alan adı sağlayıcınızın (örn: GoDaddy, Namecheap, Cloudflare, Turkticaret vb.) kontrol paneline girin ve aşağıdaki DNS kayıtlarını ekleyin:

### SEÇENEK 1: A ve AAAA Kayıtları (ÖNERİLEN)

| Tip | Hostname | Değer | TTL |
|-----|----------|-------|-----|
| **A** | `@` (veya boş) | `66.241.124.228` | 3600 |
| **AAAA** | `@` (veya boş) | `2a09:8280:1::a9:1e18:0` | 3600 |
| **A** | `www` | `66.241.124.228` | 3600 |
| **AAAA** | `www` | `2a09:8280:1::a9:1e18:0` | 3600 |

**ÖNEMLİ:** 
- `@` sembolü root domain'i (utap.com.tr) temsil eder
- Bazı sağlayıcılarda `@` yerine boş bırakmanız gerekebilir
- `www` kaydı www.utap.com.tr için

---

### SEÇENEK 2: CNAME Kaydı (Sadece www için)

| Tip | Hostname | Değer | TTL |
|-----|----------|-------|-----|
| **CNAME** | `www` | `pn11px3.tevkil.fly.dev` | 3600 |

**NOT:** Root domain (`@`) için CNAME kullanılamaz, mutlaka A/AAAA kaydı gerekir.

---

## 🔐 SSL SERTİFİKASI (OTOMATİK)

Fly.io, DNS kayıtlarını tespit ettikten sonra **otomatik olarak** Let's Encrypt SSL sertifikası oluşturacak.

**Süreç:**
1. DNS kayıtlarını ekleyin ✅
2. 5-30 dakika bekleyin (DNS yayılması)
3. Fly.io SSL sertifikasını otomatik oluşturur 🔒
4. HTTPS aktif olur ✅

---

## 📍 ALAN ADI SAĞLAYICINA GÖRE AYAR ÖRNEKLERİ

### GoDaddy:
1. GoDaddy hesabınıza giriş yapın
2. **My Products** → **Domains** → **utap.com.tr** → **Manage DNS**
3. **DNS Records** bölümüne gidin
4. **Add** butonuna tıklayın
5. Yukarıdaki A ve AAAA kayıtlarını ekleyin

### Cloudflare:
1. Cloudflare hesabınıza giriş yapın
2. **utap.com.tr** domain'ini seçin
3. **DNS** sekmesine gidin
4. **Add record** ile kayıtları ekleyin
5. **⚠️ ÖNEMLİ:** Cloudflare kullanıyorsanız, "Proxy status" ayarını **DNS only** (gri bulut) yapın!

### Namecheap:
1. Namecheap hesabınıza giriş yapın
2. **Domain List** → **utap.com.tr** → **Manage**
3. **Advanced DNS** sekmesine gidin
4. **Add New Record** ile kayıtları ekleyin

### Natro/Turhost/Turkticaret (Türk Hosting):
1. Kontrol panelinize giriş yapın
2. **Alan Adı Yönetimi** → **DNS Yönetimi**
3. **Yeni Kayıt Ekle** ile A ve AAAA kayıtlarını ekleyin

---

## ✅ DOĞRULAMA ADIMLARI

### 1. DNS Kayıtlarını Kontrol Edin (5-30 dk sonra)

```powershell
# Windows PowerShell (Bilgisayarınızdan çalıştırın)

# Root domain kontrolü
nslookup utap.com.tr

# www kontrolü
nslookup www.utap.com.tr
```

**Beklenen Sonuç:**
```
Name:    utap.com.tr
Address: 66.241.124.228
Address: 2a09:8280:1::a9:1e18:0
```

### 2. SSL Sertifikası Durumunu Kontrol Edin

```powershell
fly certs show utap.com.tr -a tevkil
fly certs show www.utap.com.tr -a tevkil
```

**Başarılı SSL:**
```
Status: Ready
```

### 3. Web Sitesini Test Edin

```powershell
# Tarayıcıda açın:
start https://utap.com.tr
start https://www.utap.com.tr
```

---

## 🔄 WWW YÖNLENDİRMESİ (Opsiyonel)

Eğer `www.utap.com.tr` → `utap.com.tr` yönlendirmesi yapmak isterseniz, uygulama kodunda middleware ekleyebiliriz.

**Flask app.py'ye eklenecek kod:**
```python
@app.before_request
def redirect_www():
    """Redirect www to non-www"""
    if request.host.startswith('www.'):
        url = request.url.replace('www.', '', 1)
        return redirect(url, code=301)
```

---

## 🚨 SORUN GİDERME

### DNS yayılmadı (5-30 dakika beklenmeli):
```powershell
# Farklı DNS sunucularından kontrol
nslookup utap.com.tr 8.8.8.8
nslookup utap.com.tr 1.1.1.1
```

### SSL sertifikası oluşmadı:
```powershell
# Sertifika durumunu kontrol edin
fly certs check utap.com.tr -a tevkil

# Sertifikayı yeniden deneyin
fly certs add utap.com.tr -a tevkil
```

### Cloudflare kullanıyorsanız:
- **Proxy Status:** DNS only (gri bulut) ✅
- **SSL/TLS Mode:** Full (strict) ✅
- **Always Use HTTPS:** Açık ✅

### Eski DNS kayıtları varsa:
1. Alan adı sağlayıcısında **TÜM** eski A/AAAA/CNAME kayıtlarını silin
2. Sadece yukarıdaki kayıtları ekleyin
3. 30 dakika bekleyin

---

## 📊 DURUM TAKİBİ

### Şu an yapılması gerekenler:

- [ ] **Alan adı sağlayıcısına giriş yapın**
- [ ] **DNS kayıtlarını ekleyin** (A ve AAAA)
- [ ] **5-30 dakika bekleyin** (DNS yayılması)
- [ ] **SSL durumunu kontrol edin** (`fly certs show`)
- [ ] **Web sitesini test edin** (https://utap.com.tr)

---

## 🎯 SONUÇ

Alan adı bağlama işlemi **3 adımda** tamamlanır:

1. ✅ **Fly.io'ya ekleme** - TAMAMLANDI (bu adım yapıldı)
2. ⏳ **DNS ayarları** - YAPILACAK (alan adı sağlayıcınızda)
3. ⏳ **SSL oluşumu** - OTOMATİK (DNS yayıldıktan sonra)

**Tahmini Süre:** 5-30 dakika (DNS yayılması için)

---

## 📞 DESTEK

DNS ayarlarında sorun yaşarsanız:
- Alan adı sağlayıcınızın destek ekibiyle iletişime geçin
- Fly.io community forumuna danışın: https://community.fly.io
- Bana sorabilirsiniz! 😊

**İyi şanslar!** 🚀

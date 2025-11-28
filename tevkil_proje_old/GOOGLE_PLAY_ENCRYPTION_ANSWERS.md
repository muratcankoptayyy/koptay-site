# 🔐 Google Play Şifreleme Soruları - HIZLI CEVAP

> Play Console → Data Safety → Security practices bölümü için

---

## ❓ GOOGLE'IN SORUSU

**"Is data encrypted in transit?"**  
(Veriler iletim sırasında şifreleniyor mu?)

### ✅ CEVAP: YES (EVET)

**Açıklama:**
```
All data is encrypted in transit using HTTPS/TLS 1.3.
Our API uses SSL/TLS certificates from Let's Encrypt.
No unencrypted communication occurs between the app and server.
```

**Türkçe:**
```
Tüm veriler HTTPS/TLS 1.3 kullanılarak şifrelenir.
API'miz Let's Encrypt SSL/TLS sertifikası kullanır.
Uygulama ve sunucu arasında şifrelenmemiş iletişim olmaz.
```

---

## ❓ GOOGLE'IN SORUSU

**"Is data encrypted at rest?"**  
(Veriler depolama sırasında şifreleniyor mu?)

### ✅ CEVAP: YES (EVET)

**Açıklama:**
```
Data is encrypted at rest using:
- Fly.io PostgreSQL automatic disk encryption (AES-256)
- Passwords: Bcrypt hashing (one-way, irreversible)
- API tokens: Secure UUID v4 generation
- 2FA codes: Temporary, one-time, hashed storage
```

**Türkçe:**
```
Veriler şu yöntemlerle şifrelenir:
- Fly.io PostgreSQL otomatik disk şifrelemesi (AES-256)
- Şifreler: Bcrypt hash (tek yönlü, geri döndürülemez)
- API token'lar: Güvenli UUID v4 üretimi
- 2FA kodları: Geçici, tek kullanımlık, hash'li saklama
```

---

## 📋 DİĞER GÜVENLİK SORULARI

### ❓ "Can users request data deletion?"
**CEVAP: YES** ✅
- Kullanıcılar hesaplarını silebilir
- Mesajları silebilir
- destek@utap.com.tr'ye başvurarak veri silme talep edebilir

### ❓ "Can users request that data is not shared?"
**CEVAP: NO** ❌
- Uygulama temel işlevselliği için veri paylaşımı gereklidir
- Ancak sadece gerekli minimum veriler paylaşılır (Fly.io hosting, WhatsApp bildirimleri)

### ❓ "Independent security review?"
**CEVAP: NO** ❌
- Henüz bağımsız güvenlik denetimi yapılmadı
- İleride yapılabilir (opsiyonel)

---

## 🔗 TEKNİK DETAYLAR

### Şifreleme Teknolojileri
| Veri Tipi | Şifreleme Yöntemi | Algoritma |
|-----------|-------------------|-----------|
| İletim (Transit) | HTTPS/TLS | TLS 1.3 |
| Veritabanı | Disk şifreleme | AES-256 |
| Şifreler | Hash | Bcrypt |
| Session | Cookie | Secure + HttpOnly |
| API Token | UUID | v4 random |

### Kullanılan Kütüphaneler
```python
werkzeug.security import generate_password_hash, check_password_hash
# Bcrypt-based password hashing

# PostgreSQL connection (Fly.io)
database_url = os.getenv('DATABASE_URL')
# Automatic encryption at rest (AES-256)
```

---

## ⏰ HATIRLATICI: DNS KONTROLÜ

**30 dakika sonra çalıştır:**
```powershell
# DNS propagation kontrolü
nslookup utap.com.tr
nslookup www.utap.com.tr

# SSL sertifika kontrolü
fly certs show utap.com.tr -a tevkil
fly certs show www.utap.com.tr -a tevkil
```

**Başarılı ise görülecek:**
- ✅ IP: 66.241.124.228
- ✅ IPv6: 2a09:8280:1::a9:1e18:0
- ✅ Status: "Ready" (yeşil ✓)

---

## ✅ PLAY CONSOLE'DA İŞARETLENECEKLER

Data Safety → Security Practices bölümünde:

```
☑ Data is encrypted in transit
☑ Data is encrypted at rest  
☑ Users can request data deletion
☐ Users can request data not be shared (hayır)
☐ Independent security review (hayır - opsiyonel)
```

---

## 📞 İLETİŞİM

**Veri güvenliği soruları için:**  
📧 destek@utap.com.tr  
🌐 https://utap.com.tr/privacy-policy

**Son güncelleme:** {{ date.today() }}

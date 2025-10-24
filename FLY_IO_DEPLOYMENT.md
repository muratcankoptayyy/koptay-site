# 🚀 Fly.io Deployment Guide - Ulusal Tevkil Ağı Projesi

## 📋 Ön Hazırlık

### ✅ Tamamlanan Kontroller:
- [x] Flask app hazır (`app.py`)
- [x] Requirements.txt güncellendi
- [x] Procfile yapılandırıldı (Gunicorn + Gevent)
- [x] fly.toml oluşturuldu (Istanbul region)
- [x] Health check endpoint eklendi (`/health`)
- [x] WhatsApp feature flag devre dışı (`WHATSAPP_ENABLED=false`)
- [x] .dockerignore oluşturuldu

---

## 🔧 Adım 1: Fly.io CLI Kurulumu

### Windows (PowerShell):
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

Kurulum sonrası terminal'i yeniden başlat veya:
```powershell
$env:PATH += ";$env:USERPROFILE\.fly\bin"
```

### Kurulumu Doğrula:
```powershell
fly version
```

---

## 🔑 Adım 2: Fly.io Login

```bash
fly auth login
```

**Not:** Browser'da açılacak sayfadan GitHub/Google ile login olabilirsin.

---

## 📦 Adım 3: PostgreSQL Database Oluştur

```bash
# Istanbul region'da PostgreSQL oluştur (FREE tier)
fly postgres create --name tevkil-db --region ist --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1
```

**Database Bilgileri Kaydet:**
- Database name: `tevkil-db`
- Region: `ist` (Istanbul)
- Connection string: `postgresql://user:pass@host:5432/dbname`

**Database'i App'e Bağla:**
```bash
fly postgres attach tevkil-db --app tevkil
```

Bu komut otomatik olarak `DATABASE_URL` environment variable oluşturur.

---

## 🔴 Adım 4: Redis Cache Oluştur (Opsiyonel)

```bash
# Upstash Redis (FREE tier, Fly.io entegrasyonu)
fly redis create --name tevkil-redis --region ist
```

**Redis'i App'e Bağla:**
```bash
fly redis attach tevkil-redis --app tevkil
```

Bu komut otomatik olarak `REDIS_URL` environment variable oluşturur.

**Not:** Redis yoksa app otomatik olarak SimpleCache fallback kullanır.

---

## 🚀 Adım 5: App Deploy

### İlk Deployment:
```bash
# fly.toml dosyasını kullanarak deploy
fly launch --no-deploy

# Environment variables set et
fly secrets set FLASK_SECRET_KEY="$(openssl rand -hex 32)"
fly secrets set FLASK_ENV=production
fly secrets set WHATSAPP_ENABLED=false
fly secrets set GEMINI_API_KEY=AIzaSyCtm1otDTI_91bTFHerLA4MvE1WOrkWSfw
fly secrets set GITHUB_TOKEN=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
fly secrets set META_WEBHOOK_VERIFY_TOKEN=tevkil_webhook_2025

# İlk deployment
fly deploy
```

### App İsmi Değiştir (Opsiyonel):
```bash
fly apps rename tevkil --app <eski-isim>
```

---

## 🗄️ Adım 6: Database Migration

Deploy sonrası database tablolarını oluştur:

```bash
# SSH ile app'e bağlan
fly ssh console --app tevkil

# Python shell aç
python

# Database tablolarını oluştur
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database tables created!")
exit()

# SSH'den çık
exit
```

---

## 🌍 Adım 7: Domain Ayarları

### Fly.io Subdomain (FREE):
```
https://tevkil.fly.dev
```

### Custom Domain (Opsiyonel):
```bash
# Domain ekle
fly certs create tevkil.com.tr --app tevkil

# DNS ayarları
# A record: @ → fly.io IP
# CNAME: www → tevkil.fly.dev
```

---

## ✅ Adım 8: Deployment Doğrulama

### Health Check:
```bash
curl https://tevkil.fly.dev/health
```

**Beklenen Cevap:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-10-24T..."
}
```

### App Logları:
```bash
fly logs --app tevkil
```

### App Durumu:
```bash
fly status --app tevkil
```

### Metrics Dashboard:
```bash
fly dashboard --app tevkil
```

---

## 🔄 Güncelleme (Yeni Kod Deploy)

```bash
# Kodları commit et
git add .
git commit -m "Feature: New feature added"

# Fly.io'ya deploy
fly deploy --app tevkil
```

---

## 📊 Monitoring & Debugging

### Real-time Logs:
```bash
fly logs --app tevkil -f
```

### SSH Console:
```bash
fly ssh console --app tevkil
```

### Database Console:
```bash
fly postgres connect --app tevkil-db
```

### Restart App:
```bash
fly apps restart tevkil
```

---

## 🔐 Production Environment Variables

Şu secrets'ları mutlaka set et:

```bash
# Güvenlik
fly secrets set FLASK_SECRET_KEY="super-secret-random-key-2025"
fly secrets set FLASK_ENV=production

# Database (otomatik oluşur)
# DATABASE_URL=postgresql://...
# REDIS_URL=redis://...

# Feature Flags
fly secrets set WHATSAPP_ENABLED=false

# AI Services
fly secrets set GEMINI_API_KEY=your-gemini-key
fly secrets set GITHUB_TOKEN=your-github-token

# WhatsApp (gelecekte)
fly secrets set META_ACCESS_TOKEN=your-meta-token
fly secrets set META_PHONE_NUMBER_ID=your-phone-id
fly secrets set META_WEBHOOK_VERIFY_TOKEN=tevkil_webhook_2025

# Email (opsiyonel)
fly secrets set SENDGRID_API_KEY=your-sendgrid-key
fly secrets set FROM_EMAIL=noreply@tevkil.app

# SMS (opsiyonel)
fly secrets set NETGSM_USERNAME=your-username
fly secrets set NETGSM_PASSWORD=your-password

# URLs
fly secrets set BASE_URL=https://tevkil.fly.dev
fly secrets set FRONTEND_URL=https://tevkil.fly.dev
```

### Secrets Listele:
```bash
fly secrets list --app tevkil
```

---

## 🎯 Kapasite ve Performans

### FREE Tier Limitleri:
- **RAM:** 512 MB (2 GB'a kadar ücretsiz)
- **CPU:** Shared 1x
- **Concurrent Users:** 200-300
- **Daily Active Users:** 5,000-10,000
- **PostgreSQL:** 1 GB storage
- **Uptime:** %99.9

### Scale Up (Gerekirse):
```bash
# RAM arttır
fly scale memory 1024 --app tevkil

# VM sayısı arttır
fly scale count 2 --app tevkil

# Daha güçlü CPU
fly scale vm shared-cpu-2x --app tevkil
```

---

## 🐛 Troubleshooting

### App çalışmıyor:
```bash
fly logs --app tevkil
fly status --app tevkil
fly doctor
```

### Database bağlantı hatası:
```bash
fly postgres connect --app tevkil-db
\l  # Database listesi
\dt  # Tablo listesi
```

### Restart app:
```bash
fly apps restart tevkil
```

### Rebuild from scratch:
```bash
fly deploy --app tevkil --strategy immediate
```

---

## 💰 Maliyet Tahmini

### FREE Tier (İlk 3 Ay):
- App: **$0** (512 MB RAM, 1 CPU)
- PostgreSQL: **$0** (1 GB storage)
- Redis: **$0** (Upstash FREE tier)
- **TOPLAM: $0/ay** 🎉

### Sonrasında (Scale edilirse):
- App (1 GB RAM): ~$5/ay
- PostgreSQL (3 GB): Ücretsiz devam
- Redis: Ücretsiz devam
- **TOPLAM: $0-5/ay** (200-300 concurrent user için)

---

## 🎉 Deployment Başarılı!

Artık uygulamanız şu adreste canlı:
```
https://tevkil.fly.dev
```

### Sonraki Adımlar:
1. ✅ Test kullanıcısı oluştur
2. ✅ İlan oluştur ve test et
3. ✅ Socket.IO chat test et
4. ✅ Performans metrics izle
5. ⏳ Domain bağla (opsiyonel)
6. ⏳ WhatsApp token al ve aktif et (gelecekte)

---

## 📚 Faydalı Linkler

- **Fly.io Dashboard:** https://fly.io/dashboard
- **Fly.io Docs:** https://fly.io/docs
- **Pricing:** https://fly.io/docs/about/pricing
- **Status Page:** https://status.flyio.net

---

**🚀 Happy Deploying!**

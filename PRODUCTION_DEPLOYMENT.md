# 🚀 Production Deployment Rehberi

UTAP projesini production ortamına deploy etmek için adım adım rehber.

## ⚠️ Deployment Öncesi Kontrol Listesi

### 1. Güvenlik Ayarları

#### SECRET_KEY
```bash
# Güçlü bir SECRET_KEY oluşturun
python -c "import secrets; print(secrets.token_hex(32))"
```

`.env` dosyasını production değerleriyle güncelleyin:
```bash
FLASK_ENV=production
DEV_MODE=False
SECRET_KEY=<yukarıda-oluşturulan-güçlü-anahtar>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

#### Session Cookie Ayarları
`config.py` dosyasında production için:
```python
if os.getenv('FLASK_ENV') == 'production':
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
```

### 2. Veritabanı Hazırlığı

#### SQLite → PostgreSQL Geçişi (Önerilir)
```bash
# PostgreSQL bağımlılığı ekleyin
pip install psycopg2-binary

# .env dosyasında
DATABASE_URL=postgresql://username:password@host:5432/database_name
```

#### Veritabanını Initialize Edin
```bash
python init_production_db.py
```

### 3. Statik Dosyalar
```bash
# Tüm statik dosyaların varlığını kontrol edin
ls -la static/css/
ls -la static/images/
ls -la static/js/
```

### 4. Bağımlılıklar
```bash
# requirements.txt güncel mi?
pip freeze > requirements.txt
```

## 🌐 Deployment Seçenekleri

### Option 1: Render.com (Önerilen)

#### Adımlar:
1. GitHub'a push edin
2. Render.com'a gidin ve "New Web Service" oluşturun
3. Repository'yi bağlayın
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app`

#### Environment Variables:
```
FLASK_ENV=production
SECRET_KEY=<güçlü-anahtar>
DEV_MODE=False
DATABASE_URL=<render-postgresql-url>
```

#### PostgreSQL Ekleme:
- Dashboard → New → PostgreSQL
- External Database URL'i kopyalayın
- Web Service Environment Variables'a ekleyin

### Option 2: PythonAnywhere

#### Adımlar:
1. Dosyaları yükleyin (Git veya manuel)
2. Virtual environment oluşturun:
```bash
mkvirtualenv utap-env --python=python3.10
pip install -r requirements.txt
```

3. WSGI Configuration:
```python
import sys
import os

# Proje yolunu ekle
project_home = '/home/yourusername/tevkil_proje'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-secret-key'
os.environ['DEV_MODE'] = 'False'

from app import app as application
```

4. Static Files Mapping:
```
URL: /static/
Directory: /home/yourusername/tevkil_proje/static/
```

5. Web app'i reload edin

### Option 3: Heroku

#### Gerekli Dosyalar:

**Procfile:**
```
web: gunicorn app:app
```

**runtime.txt:**
```
python-3.10.14
```

#### Deploy:
```bash
heroku login
heroku create utap-app
heroku addons:create heroku-postgresql:hobby-dev

# Environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=<güçlü-anahtar>
heroku config:set DEV_MODE=False

# Deploy
git push heroku main

# Veritabanı initialize
heroku run python init_db.py

# Logları izle
heroku logs --tail
```

### Option 4: DigitalOcean App Platform

#### Adımlar:
1. GitHub'a push edin
2. DigitalOcean → Apps → Create App
3. Repository seçin
4. Build Command: `pip install -r requirements.txt`
5. Run Command: `gunicorn app:app`
6. Environment Variables ekleyin
7. Database oluşturun ve bağlayın

### Option 5: VPS (Ubuntu Server)

#### Nginx + Gunicorn ile:

1. Server kurulumu:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

2. Proje kurulumu:
```bash
cd /var/www
git clone <repo-url> utap
cd utap
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

3. Gunicorn servis oluşturun:
```bash
sudo nano /etc/systemd/system/utap.service
```

```ini
[Unit]
Description=UTAP Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/utap
Environment="PATH=/var/www/utap/venv/bin"
EnvironmentFile=/var/www/utap/.env
ExecStart=/var/www/utap/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

4. Nginx konfigürasyonu:
```bash
sudo nano /etc/nginx/sites-available/utap
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /var/www/utap/static;
    }
}
```

5. Servisleri başlatın:
```bash
sudo systemctl enable utap
sudo systemctl start utap
sudo systemctl enable nginx
sudo systemctl restart nginx
```

6. SSL (Let's Encrypt):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 🔍 Deployment Sonrası Kontroller

### 1. Health Check
```bash
curl https://yourdomain.com/
```

### 2. Database Connection
```bash
# Logs kontrol edin
tail -f /var/log/nginx/error.log
# veya
heroku logs --tail
```

### 3. Statik Dosyalar
```bash
curl https://yourdomain.com/static/css/styles.css
```

### 4. Functionality Test
- ✅ Kayıt ol
- ✅ Giriş yap
- ✅ İlan oluştur
- ✅ Mesaj gönder
- ✅ Profil düzenle

## 🐛 Yaygın Sorunlar

### "Internal Server Error"
- Logları kontrol edin
- SECRET_KEY ayarlı mı?
- Database bağlantısı çalışıyor mu?

### Statik Dosyalar Yüklenmiyor
- Nginx/Apache static mapping kontrol edin
- Dosya izinlerini kontrol edin

### Database Connection Error
- DATABASE_URL doğru mu?
- PostgreSQL servisi çalışıyor mu?
- Firewall kuralları açık mı?

### Session Sorunları
- SESSION_COOKIE_SECURE HTTPS'de True olmalı
- Domain cookie settings kontrol edin

## 📊 Monitoring & Maintenance

### Loglar
```bash
# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Gunicorn
journalctl -u utap -f

# Heroku
heroku logs --tail
```

### Backup
```bash
# PostgreSQL
pg_dump dbname > backup.sql

# SQLite
cp instance/tevkil.db instance/tevkil.db.backup
```

### Updates
```bash
git pull origin main
pip install -r requirements.txt
sudo systemctl restart utap
```

## 🔐 Security Best Practices

1. ✅ HTTPS kullanın (SSL certificate)
2. ✅ Güçlü SECRET_KEY
3. ✅ Environment variables (.env)
4. ✅ Database backup otomasyonu
5. ✅ Regular security updates
6. ✅ Rate limiting (Flask-Limiter)
7. ✅ CORS ayarları
8. ✅ CSP headers

## 📞 Deployment Support

Herhangi bir sorun yaşarsanız:
- **Logs:** İlk önce logları kontrol edin
- **Documentation:** Platform dokümantasyonunu okuyun
- **Community:** Stack Overflow, Reddit
- **Email:** destek@utap.com

---

**Son Güncelleme:** Kasım 2025  
**Platform Versiyonu:** 1.0.0

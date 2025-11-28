# Ulusal Tevkil Ağı Projesi - Deployment Guide

## 🚀 PythonAnywhere'de Deploy Etme Adımları

### 1️⃣ Hesap Oluşturma
1. https://www.pythonanywhere.com adresine gidin
2. "Pricing & signup" → "Create a Beginner account" (Ücretsiz)
3. Kullanıcı adı seçin (örn: koptay, tevkil, vb.)
4. E-posta ve şifre ile kayıt olun

### 2️⃣ Proje Dosyalarını Yükleme
**Seçenek A: GitHub ile (Önerilen)**
1. Projeyi GitHub'a yükleyin
2. PythonAnywhere'de Bash console açın
3. `git clone https://github.com/kullaniciadi/tevkil_proje.git` komutu çalıştırın

**Seçenek B: Manuel Yükleme**
1. PythonAnywhere → Files sekmesi
2. "Upload a file" ile dosyaları tek tek yükleyin
3. Veya ZIP ile yükleyip unzip edin

### 3️⃣ Virtual Environment Kurulumu
Bash console'da:
```bash
cd tevkil_proje
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4️⃣ Web App Ayarları
1. PythonAnywhere → "Web" sekmesi
2. "Add a new web app"
3. "Manual configuration" → Python 3.11 seçin
4. WSGI dosyasını düzenleyin (aşağıdaki kodu kullanın)

### 5️⃣ WSGI Yapılandırması
```python
import sys
import os

# Proje klasörünü ekle
path = '/home/KULLANICIADI/tevkil_proje'
if path not in sys.path:
    sys.path.append(path)

# Virtual environment
virtualenv_path = '/home/KULLANICIADI/tevkil_proje/venv'
activate_this = os.path.join(virtualenv_path, 'bin', 'activate_this.py')
exec(open(activate_this).read(), dict(__file__=activate_this))

# Flask app'i import et
from app import app as application
```

### 6️⃣ Static Files Ayarları
Web → Static files:
- URL: `/static/`
- Directory: `/home/KULLANICIADI/tevkil_proje/static`

### 7️⃣ Database Kurulumu
Bash console:
```bash
cd tevkil_proje
source venv/bin/activate
python
>>> from app import app, db
>>> app.app_context().push()
>>> db.create_all()
>>> exit()
```

### 8️⃣ Reload & Test
1. Web sekmesinde "Reload" butonuna basın
2. Sitenize gidin: `https://KULLANICIADI.pythonanywhere.com`

---

## 🎯 Render.com ile Deploy (Alternatif)

### 1. GitHub Repository Oluştur
Projeyi GitHub'a yükleyin

### 2. Render.com Hesabı
1. https://render.com → Sign Up (GitHub ile)
2. "New +" → "Web Service"
3. GitHub repo'nuzu bağlayın

### 3. Ayarlar
- **Name:** tevkil-agi
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
- **Plan:** Free

### 4. Environment Variables
```
FLASK_ENV=production
SECRET_KEY=RANDOM_STRING_BURAYA
```

---

## 📋 Gerekli Dosyalar

### requirements.txt
```
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-CORS==5.0.0
Werkzeug==3.1.3
requests==2.32.3
gunicorn==23.0.0
```

### Procfile (Render için)
```
web: gunicorn app:app
```

### runtime.txt (Render için)
```
python-3.11.5
```

---

## ⚙️ Önemli Değişiklikler

### app.py Değişiklikleri
Production için:
```python
# Debug mode'u kapat
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### Database Path
PythonAnywhere için:
```python
# app.py içinde
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'tevkil.db')
```

---

## 🔐 Güvenlik Kontrolleri

1. ✅ SECRET_KEY'i değiştirin (environment variable kullanın)
2. ✅ Debug mode'u kapatın
3. ✅ CORS ayarlarını kontrol edin
4. ✅ SQL injection koruması (SQLAlchemy zaten koruyor)
5. ✅ HTTPS kullanın (PythonAnywhere otomatik verir)

---

## 🐛 Yaygın Sorunlar & Çözümleri

### "Import Error: No module named 'app'"
- WSGI dosyasındaki path'leri kontrol edin
- Virtual environment aktif mi?

### "Database is locked"
- SQLite PythonAnywhere'de sınırlı, PostgreSQL'e geçin

### "Static files not loading"
- Static files mapping'i doğru mu?
- `/static/` ile başlıyor mu?

### "500 Internal Server Error"
- Error logs'u kontrol edin (Web → Log files)
- `print()` yerine `app.logger.info()` kullanın

---

## 📞 Yardım Kaynakları

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Render Docs: https://render.com/docs
- Flask Deploy Guide: https://flask.palletsprojects.com/en/3.0.x/deploying/

---

## ✅ Deploy Checklist

- [ ] Hesap oluşturuldu
- [ ] Proje dosyaları yüklendi
- [ ] Virtual environment kuruldu
- [ ] requirements.txt yüklendi
- [ ] WSGI yapılandırıldı
- [ ] Database oluşturuldu
- [ ] Static files ayarlandı
- [ ] Test kullanıcısı eklendi
- [ ] SSL aktif
- [ ] Site çalışıyor! 🎉

---

**Önemli:** Deploy sonrası ilk kullanıcıyı manuel olarak oluşturun:
```python
from app import app, db, User
app.app_context().push()
user = User(email='admin@tevkil.com', full_name='Admin', ...)
user.set_password('güvenli_şifre')
db.session.add(user)
db.session.commit()
```

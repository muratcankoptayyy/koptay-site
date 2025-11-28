# PythonAnywhere Deployment Checklist

## 📋 ADIM ADIM KURULUM

### 1️⃣ Hesap Oluşturma
- [ ] https://www.pythonanywhere.com/registration/register/beginner/ adresine git
- [ ] Username seç (örn: koptay, tevkil, utap2025)
- [ ] Email ve şifre ile kayıt ol
- [ ] Email'i doğrula

### 2️⃣ Dosyaları Yükleme
**Seçenek A: GitHub (Önerilen)**
- [ ] GitHub hesabı oluştur
- [ ] Repository oluştur
- [ ] Projeyi GitHub'a yükle
- [ ] PythonAnywhere'de git clone

**Seçenek B: Manuel Upload**
- [ ] Files sekmesine git
- [ ] Dosyaları tek tek yükle
- [ ] Veya ZIP yükleyip unzip et

### 3️⃣ Virtual Environment
Bash Console'da çalıştır:
```bash
cd tevkil_proje
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
- [ ] Virtual environment oluşturuldu
- [ ] Bağımlılıklar yüklendi

### 4️⃣ Database Kurulumu
```bash
python3.11
>>> from app import app, db, User
>>> app.app_context().push()
>>> db.create_all()
>>> exit()
```
- [ ] Database oluşturuldu

### 5️⃣ Test Kullanıcısı (İsteğe Bağlı)
```python
>>> from app import app, db, User
>>> app.app_context().push()
>>> user = User(email='admin@tevkil.com', full_name='Admin', city='İstanbul', bar_association='İstanbul Barosu', lawyer_type='avukat')
>>> user.set_password('admin123')
>>> db.session.add(user)
>>> db.session.commit()
>>> exit()
```
- [ ] Test kullanıcısı oluşturuldu

### 6️⃣ Web App Ayarları
- [ ] Web sekmesine git
- [ ] "Add a new web app" butonuna tıkla
- [ ] "Next" → "Manual configuration"
- [ ] Python 3.11 seç

### 7️⃣ WSGI Dosyası Düzenleme
WSGI configuration file linkine tıkla ve şunu yaz:

```python
import sys
import os

# Proje yolunu değiştir! KULLANICIADI yerine kendi username'ini yaz
path = '/home/KULLANICIADI/tevkil_proje'
if path not in sys.path:
    sys.path.append(path)

# Virtual environment
import site
site.addsitedir('/home/KULLANICIADI/tevkil_proje/venv/lib/python3.11/site-packages')

# Flask app
from app import app as application
```
- [ ] WSGI dosyası düzenlendi
- [ ] KULLANICIADI değiştirildi

### 8️⃣ Virtualenv Ayarı
- [ ] Web sekmesinde "Virtualenv" bölümüne git
- [ ] Path gir: `/home/KULLANICIADI/tevkil_proje/venv`

### 9️⃣ Static Files
- [ ] Web sekmesinde "Static files" bölümü
- [ ] Yeni mapping ekle:
  - URL: `/static/`
  - Directory: `/home/KULLANICIADI/tevkil_proje/static`

### 🔟 Reload & Test
- [ ] Yeşil "Reload" butonuna bas
- [ ] `https://KULLANICIADI.pythonanywhere.com` adresini aç
- [ ] Site çalışıyor! 🎉

## 🐛 Sorun Yaşarsan

### Error Log Kontrolü
- Web sekmesi → Log files
- error.log dosyasını kontrol et

### Bash Console Test
```bash
cd tevkil_proje
source venv/bin/activate
python3.11 app.py
# Hata varsa göreceksin
```

### Database Sorunu
```bash
cd tevkil_proje
python3.11
>>> from app import app, db
>>> app.app_context().push()
>>> db.create_all()
```

## ✅ Başarı Kriterleri
- [ ] Site açılıyor
- [ ] Login sayfası görünüyor
- [ ] Logo yükleniyor
- [ ] Kayıt olunabiliyor
- [ ] Giriş yapılabiliyor

## 📞 Yardım Lazımsa
- PythonAnywhere Forum: https://www.pythonanywhere.com/forums/
- Help: https://help.pythonanywhere.com/

---

**Notlar:**
- Ücretsiz hesapta günde 1 kere reload yapabilirsin
- Site 3 ay aktif değilse uyku moduna girer
- Console 300 saniye sonra kapanır (normal)

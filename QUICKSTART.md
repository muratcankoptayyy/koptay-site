# ⚡ Hızlı Başlangıç Rehberi

UTAP projesini 5 dakikada çalıştırın!

## 🎯 Ön Gereksinimler

✅ Python 3.8 veya üstü yüklü olmalı  
✅ pip (Python paket yöneticisi)  
✅ Git (opsiyonel)

## 🚀 3 Adımda Kurulum

### 1️⃣ Projeyi İndirin

**Git ile:**
```bash
git clone <repository-url>
cd tevkil_proje
```

**veya ZIP olarak indirin ve klasöre gidin**

### 2️⃣ Bağımlılıkları Yükleyin

```powershell
# Virtual environment oluştur (önerilir)
python -m venv .venv

# Aktifleştir
.venv\Scripts\Activate.ps1

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 3️⃣ Çalıştırın

```powershell
# Veritabanını başlat
python init_db.py

# Uygulamayı çalıştır
python app.py
```

🎉 **Hazır!** Tarayıcınızda `http://localhost:5000` adresini açın.

## 👤 İlk Kullanıcı (Development Mode)

Development modunda (`DEV_MODE=True`) **otomatik olarak** ilk kullanıcıya giriş yapılır:

- ✅ Dashboard'a direkt erişim
- ✅ Kullanıcı kaydı/girişi gerekmez
- ✅ Hızlı test için idealdir

**Kendi kullanıcı oluşturmak için:**
1. Logout yapın (sağ üst köşe)
2. "Kayıt Ol" sayfasına gidin
3. Yeni kullanıcı oluşturun

## 📱 Hızlı Test Senaryosu

### 5 Dakikada Tüm Özellikleri Test Edin

#### 1. Dashboard (Ana Sayfa)
- ✅ İstatistikleri görün
- ✅ Quick action butonlarını deneyin

#### 2. İlan Oluşturun
```
Başlık: Test Tevkil İlanı
İl: İstanbul
İlçe: Kadıköy
Dava Türü: Ceza Hukuku
Açıklama: Test için oluşturulmuştur
Fiyat: 5000
```

#### 3. Profil Düzenleyin
- ✅ Telefon numarası ekleyin
- ✅ Adres bilgilerini güncelleyin
- ✅ Biyografi yazın

#### 4. Mesajlaşmayı Deneyin
- ✅ Yeni konuşma başlatın
- ✅ Mesaj gönderin
- ✅ Mesaj alın

## 🎨 Tasarım Sistemi Hızlı Bakış

### Renk Paleti
- **Turkuaz:** `rgb(38, 90, 93)` - Ana renk
- **Beyaz Katmanlar:** 4 farklı ton
- **Success:** Yeşil `#10b981`
- **Warning:** Turuncu `#f59e0b`
- **Danger:** Kırmızı `#ef4444`

### Logo Kullanımı
```html
<!-- Ana logo (turkuaz arka plan) -->
<img src="/static/images/logo.svg" alt="UTAP">

<!-- Light logo (beyaz arka plan) -->
<img src="/static/images/logo-light.svg" alt="UTAP">

<!-- Icon (64x64) -->
<img src="/static/images/logo-icon.svg" alt="UTAP">
```

## 📁 Önemli Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `app.py` | Ana uygulama |
| `models.py` | Veritabanı modelleri |
| `config.py` | Ayarlar |
| `init_db.py` | Veritabanı başlatıcı |
| `.env.example` | Environment variables şablonu |

## 🔧 Yaygın Sorunlar & Çözümler

### "ModuleNotFoundError"
```bash
# Bağımlılıkları tekrar yükleyin
pip install -r requirements.txt
```

### "Database locked"
```bash
# Veritabanını sıfırlayın
rm instance/tevkil.db
python init_db.py
```

### Port 5000 kullanımda
```python
# app.py dosyasında portu değiştirin
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # 5001 kullan
```

### Virtual Environment Aktifleştirme Hatası
```powershell
# PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Tekrar deneyin
.venv\Scripts\Activate.ps1
```

## 🎓 Öğrenme Yolu

### 1. Temel Özellikler (1. Gün)
- ✅ Kayıt/Giriş sistemi
- ✅ Dashboard kullanımı
- ✅ Profil düzenleme

### 2. İlan Yönetimi (2. Gün)
- ✅ İlan oluşturma
- ✅ İlan düzenleme
- ✅ İlan silme

### 3. Başvuru Sistemi (3. Gün)
- ✅ Başvuru yapma
- ✅ Başvuruları görüntüleme
- ✅ Kabul/Reddetme

### 4. Mesajlaşma (4. Gün)
- ✅ Mesaj gönderme
- ✅ Konuşma yönetimi
- ✅ Bildirimler

## 📊 Development vs Production

### Development Mode (Varsayılan)
```python
DEV_MODE = True
FLASK_ENV = 'development'
DEBUG = True
```
- ✅ Otomatik reload
- ✅ Detaylı hata mesajları
- ✅ Otomatik giriş
- ✅ SQLite veritabanı

### Production Mode
```python
DEV_MODE = False
FLASK_ENV = 'production'
DEBUG = False
```
- ✅ Güvenlik ayarları aktif
- ✅ Performans optimizasyonu
- ✅ PostgreSQL (önerilir)
- ✅ HTTPS zorunlu

## 🌐 Deployment Hızlı Başlangıç

### Render.com (En Kolay)
1. GitHub'a push edin
2. Render.com'da "New Web Service"
3. Repository bağlayın
4. Deploy butonuna tıklayın
5. ✅ Hazır!

### PythonAnywhere
1. Dosyaları yükleyin
2. Virtual environment oluşturun
3. WSGI yapılandırın
4. ✅ Yayında!

Detaylar için: `PRODUCTION_DEPLOYMENT.md`

## 🆘 Yardım Gerekiyor mu?

### Dokümantasyon
- 📖 `README.md` - Genel bilgiler
- 🚀 `PRODUCTION_DEPLOYMENT.md` - Deployment rehberi
- 🧪 `TESTING_GUIDE.md` - Test rehberi
- 🔐 `.env.example` - Environment variables

### Hata Bulduysanız
1. Hatayı terminalde kontrol edin
2. Browser console'u kontrol edin
3. `TESTING_GUIDE.md` dosyasındaki bug template'i kullanın
4. GitHub issue açın

### İletişim
- **Email:** destek@utap.com
- **GitHub Issues:** [Project Issues]

## ✅ Checklist

Kurulum tamamlandı mı?

- [ ] Python 3.8+ yüklü
- [ ] Bağımlılıklar yüklendi
- [ ] Veritabanı başlatıldı
- [ ] Uygulama çalışıyor
- [ ] `http://localhost:5000` açılıyor
- [ ] Dashboard görünüyor
- [ ] İlan oluşturulabiliyor

Hepsi tamamsa 🎉 **Başarılı!**

## 🎯 Sonraki Adımlar

1. **Özellikleri Keşfedin**
   - Tüm sayfaları gezin
   - İlan oluşturun
   - Mesajlaşmayı deneyin

2. **Kodu İnceleyin**
   - `blueprints/` klasörüne bakın
   - `models.py` veritabanı yapısını görün
   - `templates/` HTML şablonları inceleyin

3. **Özelleştirin**
   - Renkleri değiştirin (`static/css/`)
   - Logo'yu değiştirin (`static/images/`)
   - Yeni özellikler ekleyin

4. **Deploy Edin**
   - `PRODUCTION_DEPLOYMENT.md` okuyun
   - Platform seçin (Render/Heroku/PythonAnywhere)
   - Deploy edin!

---

**🚀 İyi Kodlamalar!**

*Bu proje Flask 3.1.0, SQLAlchemy ve Alpine.js ile geliştirilmiştir.*

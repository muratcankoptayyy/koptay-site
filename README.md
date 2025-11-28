# UTAP - Ulusal Tevkil Ağı Projesi

Modern, profesyonel ve kullanıcı dostu avukat tevkil platformu.

## 🎨 Yeni Tasarım Sistemi

### Renk Paleti
- **Primary**: `rgb(69, 124, 125)` → `rgb(84, 140, 141)` (Turkuaz-Yeşil Gradient)
- **Success**: `#10b981`
- **Warning**: `#f59e0b`
- **Danger**: `#ef4444`

### Özellikler
✅ Sol tarafta açılır/kapanır sidebar navigation
✅ Animasyonlu arka plan desenleri (daireler, altıgenler, diagonal çizgiler)
✅ Mobile-first responsive tasarım
✅ Modern component library
✅ Alpine.js ile interaktif UI
✅ Flask template inheritance sistemi

## 📁 Proje Yapısı

```
tevkil_proje/
├── templates/
│   ├── layouts/
│   │   └── base.html          # Ana layout template
│   ├── components/
│   │   ├── navbar.html        # Sidebar navigation
│   │   ├── footer.html        # Footer component
│   │   ├── alert.html         # Flash messages
│   │   └── modal.html         # Modal component
│   ├── pages/
│   │   ├── login.html         # Giriş sayfası
│   │   ├── register.html      # Kayıt sayfası
│   │   └── ...
│   └── demo.html              # Demo landing page
├── static/
│   ├── css/
│   │   └── design-system.css  # Complete design system
│   ├── js/
│   └── img/
├── app.py                     # Flask application
├── .env                       # Environment variables
└── requirements.txt           # Python dependencies
```

## 🚀 Kurulum

### 1. Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Dependencies
```powershell
pip install flask python-dotenv
```

### 3. Environment Variables
`.env` dosyası oluşturun:
```
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///tevkil.db
```

### 4. Çalıştırma
```powershell
python app.py
```

Tarayıcıda açın: http://localhost:5000

## 📦 Component Kullanımı

### Base Layout
```jinja
{% extends 'layouts/base.html' %}

{% block title %}Sayfa Başlığı{% endblock %}

{% block content %}
  <div class="container">
    <!-- İçerik buraya -->
  </div>
{% endblock %}
```

### Flash Messages (Otomatik)
```python
from flask import flash
flash('İşlem başarılı!', 'success')
flash('Uyarı mesajı', 'warning')
flash('Hata oluştu', 'danger')
```

### Modal
```jinja
{% include 'components/modal.html' with 
   modal_id='myModal',
   modal_title='Başlık',
   modal_body='İçerik'
%}
```

## 🎯 CSS Classes

### Buttons
```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-lg">Large Button</button>
```

### Forms
```html
<div class="form-group">
  <label class="form-label">Label</label>
  <input type="text" class="form-input">
  <small class="form-help">Yardım metni</small>
</div>
```

### Cards
```html
<div class="card">
  <h3>Başlık</h3>
  <p>İçerik</p>
</div>
```

### Alerts
```html
<div class="alert alert-success">Başarılı!</div>
<div class="alert alert-warning">Uyarı!</div>
<div class="alert alert-danger">Hata!</div>
```

### Badges
```html
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Aktif</span>
```

## 🔄 Backend Entegrasyonu (Sonraki Adım)

Eski projeden (`tevkil_proje_old/`) getirilecekler:
- ✅ `models.py` - Database modelleri
- ✅ `blueprints/` - Route'lar (auth, main, chat, vb.)
- ✅ `utils/` - Yardımcı fonksiyonlar
- ✅ Business logic

## 📝 Yapılacaklar

- [x] Design system CSS
- [x] Component templates
- [x] Base layout
- [x] Login/Register pages
- [ ] Dashboard page
- [ ] Backend entegrasyonu
- [ ] Database migration
- [ ] Test ve deployment

## 🎨 Design Inspiration

- **Tevkilapp**: Modern Next.js patterns
- **Avutap**: Professional color scheme & components
- **Custom**: Animated background patterns

---

**Geliştirici**: UTAP Team
**Tarih**: Kasım 2025
**Versiyon**: 2.0 (Yeni Tasarım)

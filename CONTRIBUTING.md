# 🤝 Katkıda Bulunma Rehberi

UTAP projesine katkıda bulunmak istediğiniz için teşekkürler! Bu rehber size nasıl katkıda bulunabileceğinizi gösterecek.

## 📋 İçindekiler

- [Davranış Kuralları](#-davranış-kuralları)
- [Nasıl Katkıda Bulunurum?](#-nasıl-katkıda-bulunurum)
- [Development Setup](#️-development-setup)
- [Kod Standartları](#-kod-standartları)
- [Commit Mesajları](#-commit-mesajları)
- [Pull Request Süreci](#-pull-request-süreci)
- [Bug Report](#-bug-report)
- [Feature Request](#-feature-request)

## 🌟 Davranış Kuralları

- ✅ Saygılı ve profesyonel olun
- ✅ Yapıcı geri bildirim verin
- ✅ Farklı görüşlere açık olun
- ✅ Topluluğa yardımcı olun
- ❌ Ayrımcılık yapmayın
- ❌ Kaba davranışlarda bulunmayın

## 🚀 Nasıl Katkıda Bulunurum?

### Kod Katkısı
1. Repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'feat: add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

### Kod Dışı Katkı
- 📝 Dokümantasyon düzeltmeleri
- 🐛 Bug raporları
- 💡 Özellik önerileri
- 🧪 Test senaryoları
- 🌐 Çeviri desteği

## 🛠️ Development Setup

### 1. Fork & Clone
```bash
# Fork edin (GitHub web interface)
# Clone edin
git clone https://github.com/YOUR-USERNAME/tevkil_proje.git
cd tevkil_proje

# Upstream ekleyin
git remote add upstream https://github.com/ORIGINAL-OWNER/tevkil_proje.git
```

### 2. Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows
```

### 3. Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### 4. Database
```bash
python init_db.py
```

### 5. Pre-commit Hooks (Opsiyonel)
```bash
pip install pre-commit
pre-commit install
```

## 📝 Kod Standartları

### Python Code Style

#### PEP 8 Uyumu
```python
# ✅ İyi
def create_tevkil_post(title, description, city):
    """Create a new tevkil post.
    
    Args:
        title: Post title
        description: Post description
        city: City name
    
    Returns:
        TevkilPost instance
    """
    post = TevkilPost(
        title=title,
        description=description,
        city=city
    )
    return post

# ❌ Kötü
def create_post(t,d,c):
    post=TevkilPost(title=t,description=d,city=c)
    return post
```

#### Import Sıralaması
```python
# 1. Standard library
import os
import sys
from datetime import datetime

# 2. Third-party
from flask import Flask, render_template
from sqlalchemy import Column, Integer

# 3. Local
from models import User, TevkilPost
from utils import format_date
```

#### Docstrings
```python
def send_notification(user_id, message, notification_type='info'):
    """Send notification to a user.
    
    Args:
        user_id (int): User ID to send notification
        message (str): Notification message
        notification_type (str): Type of notification (info/success/warning/error)
    
    Returns:
        bool: True if sent successfully, False otherwise
    
    Raises:
        ValueError: If user_id is invalid
    """
    pass
```

### HTML/Jinja2

#### Template Yapısı
```jinja
{# ✅ İyi #}
{% extends 'layouts/base.html' %}

{% block title %}Sayfa Başlığı{% endblock %}

{% block content %}
  <div class="container">
    <h1>{{ title }}</h1>
    
    {% if posts %}
      {% for post in posts %}
        <div class="card">
          <h3>{{ post.title }}</h3>
          <p>{{ post.description }}</p>
        </div>
      {% endfor %}
    {% else %}
      <p>İlan bulunamadı.</p>
    {% endif %}
  </div>
{% endblock %}
```

#### Indentation
- 2 spaces for HTML
- 4 spaces for Python
- Consistent nesting

### CSS

#### Class Naming (BEM)
```css
/* ✅ İyi */
.card { }
.card__title { }
.card__description { }
.card--featured { }

/* ❌ Kötü */
.card-title { }
.cardDescription { }
.Card { }
```

#### Organizasyon
```css
/* 1. Layout */
.container { }
.sidebar { }

/* 2. Components */
.btn { }
.card { }

/* 3. Utilities */
.text-center { }
.mt-4 { }
```

### JavaScript

#### Modern ES6+
```javascript
// ✅ İyi
const fetchPosts = async () => {
  try {
    const response = await fetch('/api/posts');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching posts:', error);
  }
};

// ❌ Kötü
function fetchPosts() {
  fetch('/api/posts').then(function(response) {
    return response.json();
  }).then(function(data) {
    return data;
  });
}
```

## 💬 Commit Mesajları

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: Yeni özellik
- `fix`: Bug düzeltmesi
- `docs`: Dokümantasyon
- `style`: Kod formatı (logic değişikliği yok)
- `refactor`: Kod refactoring
- `test`: Test ekleme/düzeltme
- `chore`: Maintenance tasks

### Örnekler
```bash
# Yeni özellik
git commit -m "feat(messages): add real-time messaging"

# Bug fix
git commit -m "fix(auth): resolve login redirect issue"

# Dokümantasyon
git commit -m "docs(readme): update installation instructions"

# Refactoring
git commit -m "refactor(models): improve query performance"

# Detaylı commit
git commit -m "feat(posts): add post filtering

- Add filter by city
- Add filter by case type
- Add search functionality

Closes #123"
```

## 🔄 Pull Request Süreci

### 1. Branch Oluşturun
```bash
# Feature
git checkout -b feature/add-notification-system

# Bug fix
git checkout -b fix/message-count-error

# Hotfix
git checkout -b hotfix/critical-security-issue
```

### 2. Değişiklik Yapın
```bash
# Kod yazın
# Test edin
# Commit edin

git add .
git commit -m "feat(notifications): add push notification system"
```

### 3. Pull Request Açın

**PR Başlığı:**
```
feat(notifications): Add push notification system
```

**PR Açıklaması Template:**
```markdown
## Açıklama
Push notification sistemi eklendi.

## Değişiklikler
- Firebase Cloud Messaging entegrasyonu
- Notification model ve route'lar
- Frontend bildirim gösterimi
- Test senaryoları

## Test Edildi
- [x] Bildirim gönderimi çalışıyor
- [x] Bildirim alımı çalışıyor
- [x] Okunma durumu güncelleniyor
- [x] UI responsive

## Screenshots
![Notification UI](screenshot.png)

## İlgili Issue
Closes #45
```

### 4. Code Review
- ✅ En az 1 reviewer onayı bekleyin
- ✅ Requested changes'leri düzeltin
- ✅ CI/CD testlerinin geçmesini bekleyin

### 5. Merge
- Maintainer tarafından merge edilir
- Branch otomatik silinir

## 🐛 Bug Report

### Issue Template

```markdown
**Bug Açıklaması**
Dashboard'da mesaj sayısı yanlış görünüyor.

**Adımlar**
1. Login ol
2. Dashboard'a git
3. Mesaj sayısına bak

**Beklenen Davranış**
3 mesaj görünmeli

**Gerçekleşen Davranış**
0 mesaj görünüyor

**Ekran Görüntüsü**
![Screenshot](screenshot.png)

**Ortam**
- OS: Windows 11
- Browser: Chrome 120
- Version: 1.0.0

**Ek Bilgi**
Console'da hata yok
```

## 💡 Feature Request

### Issue Template

```markdown
**Özellik Açıklaması**
Kullanıcıların ilanları favorilere ekleyebilmesini istiyorum.

**Kullanım Senaryosu**
Bir kullanıcı olarak, ilgilendiğim ilanları favorilere eklemek ve daha sonra kolayca erişmek istiyorum.

**Önerilen Çözüm**
- Her ilan kartında "Favorilere Ekle" butonu
- Profilde "Favorilerim" sayfası
- Database'de favorites tablosu

**Alternatifler**
- Bookmark sistemi
- "İlgileniyorum" butonu

**Ek Bilgi**
Benzer platformlarda var (örn: X, Y)
```

## 🧪 Testing

### Test Yazma
```python
# tests/test_auth.py
def test_login_success(client):
    """Test successful login"""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 302  # Redirect
    assert '/dashboard' in response.location

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert b'Hatalı email veya şifre' in response.data
```

### Test Çalıştırma
```bash
# Tüm testler
pytest

# Specific file
pytest tests/test_auth.py

# Coverage
pytest --cov=. --cov-report=html
```

## 📚 Dokümantasyon

### Dosya Başlıkları
```python
"""
blueprints/messages/routes.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Messaging system routes and handlers.

This module handles all message-related operations including
sending messages, viewing conversations, and marking messages as read.
"""
```

### Function Dokümantasyonu
```python
def calculate_rating(user_id):
    """Calculate user rating based on reviews.
    
    Calculates average rating from all reviews received by the user.
    Returns 0.0 if no reviews exist.
    
    Args:
        user_id (int): User ID to calculate rating for
    
    Returns:
        float: Average rating (0.0 - 5.0)
    
    Example:
        >>> calculate_rating(1)
        4.5
    """
    pass
```

## 🎨 Design Guidelines

### UI/UX Principles
- **Consistency:** Tutarlı tasarım dili
- **Simplicity:** Sade ve anlaşılır
- **Accessibility:** Erişilebilirlik standartları
- **Responsive:** Mobile-first yaklaşım

### Color Usage
```css
/* Primary Actions */
.btn-primary { background: rgb(38, 90, 93); }

/* Success States */
.alert-success { background: #10b981; }

/* Warnings */
.alert-warning { background: #f59e0b; }

/* Errors */
.alert-danger { background: #ef4444; }
```

## 🏆 Recognition

Katkıda bulunanlar `CONTRIBUTORS.md` dosyasında listelenecektir:

```markdown
# 🌟 Contributors

## Core Team
- [@username](link) - Role

## Contributors
- [@contributor1](link) - Feature X
- [@contributor2](link) - Bug fix Y
```

## ❓ Sorular

Herhangi bir sorunuz varsa:

- 📧 Email: dev@utap.com
- 💬 GitHub Discussions
- 🐛 GitHub Issues

---

**Teşekkürler! 🎉**

*Happy Coding!*

# 📡 API Dokümantasyonu

UTAP platformunun route'ları ve API endpoint'leri.

## 📋 İçindekiler

- [Authentication](#-authentication)
- [Dashboard](#-dashboard)
- [Posts (İlanlar)](#-posts-ilanlar)
- [Applications (Başvurular)](#-applications-başvurular)
- [Messages (Mesajlar)](#-messages-mesajlar)
- [Profile (Profil)](#-profile-profil)
- [Settings (Ayarlar)](#-settings-ayarlar)
- [Notifications (Bildirimler)](#-notifications-bildirimler)

## 🔑 Authentication

### Register (Kayıt Ol)

**Endpoint:** `POST /register`

**Açıklama:** Yeni kullanıcı kaydı

**Form Data:**
```json
{
  "full_name": "Ahmet Yılmaz",
  "email": "ahmet@example.com",
  "password": "securePassword123",
  "confirm_password": "securePassword123",
  "phone": "05551234567",
  "city": "İstanbul"
}
```

**Response:**
- Success: `302 Redirect` → `/dashboard`
- Error: `200` with error message

**Validation:**
- Email format kontrolü
- Şifre minimum 6 karakter
- Şifre eşleşme kontrolü
- Email uniqueness

---

### Login (Giriş Yap)

**Endpoint:** `POST /login`

**Açıklama:** Kullanıcı girişi

**Form Data:**
```json
{
  "email": "ahmet@example.com",
  "password": "securePassword123",
  "remember": true  // Optional
}
```

**Response:**
- Success: `302 Redirect` → `/dashboard`
- Error: Flash message "Hatalı email veya şifre"

---

### Logout (Çıkış Yap)

**Endpoint:** `GET /logout`

**Açıklama:** Kullanıcı çıkışı

**Response:** `302 Redirect` → `/login`

**Side Effects:**
- Session temizlenir
- Flask-Login logout_user() çağrılır

---

## 🏠 Dashboard

### Dashboard Anasayfa

**Endpoint:** `GET /dashboard`

**Authentication:** Required

**Response Data:**
```python
{
  'active_posts': 5,        # Aktif ilan sayısı
  'applications': 12,       # Toplam başvuru sayısı
  'messages': 3,            # Okunmamış mesaj sayısı
  'rating': 4.5            # Kullanıcı puanı
}
```

**Template:** `pages/dashboard.html`

---

## 📝 Posts (İlanlar)

### İlan Listesi

**Endpoint:** `GET /posts`

**Authentication:** Required

**Query Parameters:**
- `status` (optional): `active`, `pending`, `completed`, `all`
- `search` (optional): Arama terimi

**Response:**
```python
{
  'posts': [
    {
      'id': 1,
      'title': 'Ceza Davası Tevkili',
      'description': '...',
      'city': 'İstanbul',
      'district': 'Kadıköy',
      'case_type': 'Ceza Hukuku',
      'price': 5000,
      'status': 'active',
      'created_at': datetime,
      'user': {
        'id': 1,
        'full_name': 'Ahmet Yılmaz'
      }
    }
  ]
}
```

---

### İlan Detayı

**Endpoint:** `GET /posts/<int:post_id>`

**Authentication:** Required

**Response:**
```python
{
  'post': {
    'id': 1,
    'title': 'Ceza Davası Tevkili',
    'description': 'Detaylı açıklama...',
    'city': 'İstanbul',
    'district': 'Kadıköy',
    'case_type': 'Ceza Hukuku',
    'price': 5000,
    'status': 'active',
    'created_at': datetime,
    'updated_at': datetime,
    'user': {
      'id': 1,
      'full_name': 'Ahmet Yılmaz',
      'email': 'ahmet@example.com',
      'phone': '05551234567',
      'rating': 4.5
    },
    'applications': [
      {
        'id': 1,
        'lawyer': {...},
        'offer_price': 4500,
        'message': '...',
        'status': 'pending'
      }
    ]
  }
}
```

---

### İlan Oluşturma

**Endpoint:** `POST /posts/create`

**Authentication:** Required

**Form Data:**
```json
{
  "title": "Ceza Davası Tevkili",
  "description": "Detaylı açıklama...",
  "city": "İstanbul",
  "district": "Kadıköy",
  "case_type": "Ceza Hukuku",
  "price": 5000
}
```

**Validation:**
- `title`: Required, max 200 chars
- `description`: Required, min 20 chars
- `city`: Required
- `price`: Required, > 0

**Response:**
- Success: `302 Redirect` → `/posts/<post_id>`
- Error: Form validation errors

---

### İlan Düzenleme

**Endpoint:** `POST /posts/<int:post_id>/edit`

**Authentication:** Required (Owner only)

**Form Data:** Same as create

**Response:**
- Success: `302 Redirect` → `/posts/<post_id>`
- Error: Form validation errors or 403 Forbidden

---

### İlan Silme

**Endpoint:** `POST /posts/<int:post_id>/delete`

**Authentication:** Required (Owner only)

**Response:**
- Success: `302 Redirect` → `/posts`
- Error: 403 Forbidden

---

## 📋 Applications (Başvurular)

### Başvuru Yapma

**Endpoint:** `POST /applications/apply/<int:post_id>`

**Authentication:** Required

**Form Data:**
```json
{
  "offer_price": 4500,
  "message": "İlanınız için başvuru yapmak istiyorum..."
}
```

**Validation:**
- Kendi ilanına başvuramaz
- Duplicate başvuru kontrolü
- `offer_price` > 0

**Response:**
- Success: Flash message + `302 Redirect`
- Error: Flash error message

**Side Effects:**
- Notification oluşturulur
- Application record oluşturulur

---

### Başvuru Listesi

**Endpoint:** `GET /applications`

**Authentication:** Required

**Query Parameters:**
- `tab`: `incoming` (gelen) veya `outgoing` (giden)

**Response:**
```python
{
  'incoming_applications': [
    {
      'id': 1,
      'post': {...},
      'lawyer': {...},
      'offer_price': 4500,
      'message': '...',
      'status': 'pending',
      'created_at': datetime
    }
  ],
  'outgoing_applications': [...]
}
```

---

### Başvuru Kabul/Reddetme

**Endpoint:** `POST /applications/<int:application_id>/<action>`

**Actions:** `accept` veya `reject`

**Authentication:** Required (Post owner only)

**Response:**
- Success: Flash message + `302 Redirect`
- Error: 403 Forbidden

**Side Effects:**
- Application status güncellenir
- Notification gönderilir
- Post status "in_progress" olabilir (accept)

---

## 💬 Messages (Mesajlar)

### Konuşma Listesi

**Endpoint:** `GET /messages`

**Authentication:** Required

**Response:**
```python
{
  'conversations': [
    {
      'id': 1,
      'user1': {...},
      'user2': {...},
      'last_message': {
        'message': 'Son mesaj içeriği',
        'created_at': datetime
      },
      'unread_count': 3,
      'other_user': {
        'id': 2,
        'full_name': 'Mehmet Demir',
        'profile_image': '/static/uploads/...'
      }
    }
  ]
}
```

---

### Konuşma Detayı

**Endpoint:** `GET /messages/conversation/<int:conversation_id>`

**Authentication:** Required (Conversation participant only)

**Response:**
```python
{
  'conversation': {
    'id': 1,
    'messages': [
      {
        'id': 1,
        'sender': {...},
        'message': 'Mesaj içeriği',
        'message_type': 'text',
        'is_read': True,
        'created_at': datetime
      }
    ],
    'other_user': {
      'id': 2,
      'full_name': 'Mehmet Demir'
    }
  }
}
```

**Side Effects:**
- Okunmamış mesajlar `is_read=True` yapılır
- Unread counter sıfırlanır

---

### Mesaj Gönderme

**Endpoint:** `POST /messages/send`

**Authentication:** Required

**JSON Body:**
```json
{
  "conversation_id": 1,
  "receiver_id": 2,  // If no conversation exists
  "message": "Merhaba, nasılsınız?"
}
```

**Response:**
```json
{
  "success": true,
  "message_id": 123,
  "conversation_id": 1
}
```

**Side Effects:**
- Conversation oluşturulur (yoksa)
- Message kaydedilir
- Unread counter güncellenir
- Notification gönderilir

---

### Mesaj Okuma

**Endpoint:** `POST /messages/mark_read/<int:conversation_id>`

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "unread_count": 0
}
```

**Side Effects:**
- Conversation'daki tüm mesajlar okundu işaretlenir
- Unread counter sıfırlanır

---

## 👤 Profile (Profil)

### Profil Görüntüleme

**Endpoint:** `GET /profile` veya `GET /profile/<int:user_id>`

**Authentication:** Required

**Response:**
```python
{
  'user': {
    'id': 1,
    'full_name': 'Ahmet Yılmaz',
    'email': 'ahmet@example.com',
    'phone': '05551234567',
    'city': 'İstanbul',
    'bio': 'Avukat bio...',
    'profile_image': '/static/uploads/...',
    'rating': 4.5,
    'created_at': datetime
  },
  'stats': {
    'total_posts': 15,
    'active_posts': 5,
    'completed_posts': 10,
    'total_applications': 25
  }
}
```

---

### Profil Düzenleme

**Endpoint:** `POST /profile/edit`

**Authentication:** Required (Own profile only)

**Form Data:**
```json
{
  "full_name": "Ahmet Yılmaz",
  "phone": "05551234567",
  "city": "İstanbul",
  "bio": "Avukat bio...",
  "profile_image": <file>  // Optional
}
```

**File Upload:**
- Allowed: jpg, jpeg, png, gif
- Max size: 5MB
- Saved to: `static/uploads/profiles/`

**Response:**
- Success: Flash message + `302 Redirect` → `/profile`
- Error: Form validation errors

---

## ⚙️ Settings (Ayarlar)

### Ayarlar Sayfası

**Endpoint:** `GET /settings`

**Authentication:** Required

**Template:** `pages/settings.html`

---

### Genel Ayarlar Güncelleme

**Endpoint:** `POST /settings/general`

**Authentication:** Required

**Form Data:**
```json
{
  "email": "newemail@example.com",
  "notifications_enabled": true,
  "email_notifications": true
}
```

**Response:**
- Success: Flash message
- Error: Validation errors

---

### Şifre Değiştirme

**Endpoint:** `POST /settings/password`

**Authentication:** Required

**Form Data:**
```json
{
  "current_password": "oldPassword123",
  "new_password": "newPassword456",
  "confirm_password": "newPassword456"
}
```

**Validation:**
- Current password doğru olmalı
- New password min 6 chars
- Passwords must match

**Response:**
- Success: Flash message + Logout
- Error: Validation errors

---

### Hesap Silme

**Endpoint:** `POST /settings/delete_account`

**Authentication:** Required

**Confirmation:** Required

**Response:** `302 Redirect` → `/login`

**Side Effects:**
- User account soft delete
- All posts deactivated
- All applications cancelled

---

## 🔔 Notifications (Bildirimler)

### Bildirim Listesi

**Endpoint:** `GET /notifications`

**Authentication:** Required

**Response:**
```python
{
  'notifications': [
    {
      'id': 1,
      'type': 'application',  // application, message, post
      'title': 'Yeni Başvuru',
      'message': 'İlanınıza yeni başvuru yapıldı',
      'is_read': False,
      'created_at': datetime,
      'link': '/applications/1'
    }
  ],
  'unread_count': 5
}
```

---

### Bildirimi Okundu İşaretle

**Endpoint:** `POST /notifications/mark_read/<int:notification_id>`

**Authentication:** Required

**Response:**
```json
{
  "success": true
}
```

---

### Tüm Bildirimleri Okundu İşaretle

**Endpoint:** `POST /notifications/mark_all_read`

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "count": 5
}
```

---

## 🔒 Authorization Rules

### Public Routes
- `GET /` (Index)
- `GET /login`
- `POST /login`
- `GET /register`
- `POST /register`

### Authenticated Routes
- Tüm diğer route'lar `@login_required` decorator ile korunur

### Owner-Only Routes
- `POST /posts/<id>/edit` - Post owner
- `POST /posts/<id>/delete` - Post owner
- `POST /profile/edit` - Own profile
- `POST /applications/<id>/accept` - Post owner
- `POST /applications/<id>/reject` - Post owner

---

## 🚨 Error Responses

### 400 Bad Request
```json
{
  "error": "Validation failed",
  "details": {
    "email": ["Invalid email format"],
    "password": ["Password too short"]
  }
}
```

### 401 Unauthorized
```html
<!-- Redirect to /login -->
```

### 403 Forbidden
```html
<!-- Flash: "Bu işlem için yetkiniz yok" -->
<!-- Redirect to referring page -->
```

### 404 Not Found
```html
<!-- 404.html template -->
```

### 500 Internal Server Error
```html
<!-- 500.html template -->
<!-- Log to server logs -->
```

---

## 📊 Database Models

### User
```python
{
  'id': Integer (PK),
  'email': String (Unique),
  'full_name': String,
  'password_hash': String,
  'phone': String,
  'city': String,
  'bio': Text,
  'profile_image': String,
  'rating': Float,
  'created_at': DateTime
}
```

### TevkilPost
```python
{
  'id': Integer (PK),
  'user_id': Integer (FK),
  'title': String,
  'description': Text,
  'city': String,
  'district': String,
  'case_type': String,
  'price': Float,
  'status': Enum('active', 'pending', 'in_progress', 'completed'),
  'created_at': DateTime,
  'updated_at': DateTime
}
```

### Application
```python
{
  'id': Integer (PK),
  'post_id': Integer (FK),
  'lawyer_id': Integer (FK),
  'offer_price': Float,
  'message': Text,
  'status': Enum('pending', 'accepted', 'rejected'),
  'created_at': DateTime
}
```

### Conversation
```python
{
  'id': Integer (PK),
  'user1_id': Integer (FK),
  'user2_id': Integer (FK),
  'unread_count_user1': Integer,
  'unread_count_user2': Integer,
  'created_at': DateTime
}
```

### Message
```python
{
  'id': Integer (PK),
  'conversation_id': Integer (FK),
  'sender_id': Integer (FK),
  'message': Text,
  'message_type': String,
  'is_read': Boolean,
  'created_at': DateTime
}
```

### Notification
```python
{
  'id': Integer (PK),
  'user_id': Integer (FK),
  'type': String,
  'title': String,
  'message': Text,
  'link': String,
  'is_read': Boolean,
  'created_at': DateTime
}
```

---

## 🧪 Testing Examples

### cURL Examples

```bash
# Login
curl -X POST http://localhost:5000/login \
  -d "email=test@example.com&password=password123"

# Create Post (with session)
curl -X POST http://localhost:5000/posts/create \
  -H "Cookie: session=..." \
  -d "title=Test&description=Test desc&city=Istanbul&price=5000"

# Send Message (JSON)
curl -X POST http://localhost:5000/messages/send \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{"conversation_id":1,"message":"Hello"}'
```

---

**API Version:** 1.0  
**Last Updated:** Kasım 2025

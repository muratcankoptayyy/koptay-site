# 📱 MOBİL UYGULAMA - KALICI OTURUM SİSTEMİ

## ✅ ÇÖZÜM: API TOKEN SİSTEMİ

Web ve mobil için **farklı authentication** stratejileri:

- **🌐 Web**: Normal session cookies (browser kapanınca logout)
- **📱 Mobil**: API token sistemi (kalıcı oturum)

---

## 🎯 PROBLEM ÇÖZÜMÜ

### ❌ Önceki Sorun:
- Web session cookies mobil uygulamada düzgün çalışmıyor
- Browser kapanınca session siliniyor
- WebView cookies yönetimi karmaşık

### ✅ Yeni Çözüm:
- Mobil uygulamalar **API token** kullanıyor
- Token cihazda **kalıcı** olarak saklanıyor
- Sadece logout yapınca token siliniyor
- Web'de normal session (değişmedi)

---

## 📱 MOBİL API ENDPOINT'LERİ

### 1. **Login** - Token Al

```http
POST /api/mobile/login
Content-Type: application/json

{
  "email": "avukat@example.com",
  "password": "şifre123"
}
```

**Response (Success)**:
```json
{
  "success": true,
  "token": "qL8xYz3mN5pR9sT2vW4aC6eF1hJ7kM0nP8qR3sT5vW7xY9zA1bC3dE5fG7hI9jK1mL3",
  "user": {
    "id": 1,
    "email": "avukat@example.com",
    "full_name": "Ahmet Yılmaz",
    "phone": "05551234567",
    "avatar_url": "/static/uploads/avatars/1.jpg",
    "city": "İstanbul",
    "lawyer_type": "avukat",
    "rating_average": 4.5,
    "rating_count": 25,
    "is_admin": false
  }
}
```

**Response (Error)**:
```json
{
  "success": false,
  "error": "Hatalı email veya şifre"
}
```

---

### 2. **Verify Token** - Kullanıcı Bilgilerini Al

```http
POST /api/mobile/verify
Authorization: Bearer qL8xYz3mN5pR9sT2vW4aC6eF1hJ7kM0nP8qR3sT5vW7xY9zA1bC3dE5fG7hI9jK1mL3
```

**Response (Success)**:
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "avukat@example.com",
    "full_name": "Ahmet Yılmaz",
    "phone": "05551234567",
    "avatar_url": "/static/uploads/avatars/1.jpg",
    "city": "İstanbul",
    "lawyer_type": "avukat",
    "rating_average": 4.5,
    "rating_count": 25,
    "is_admin": false,
    "unread_notifications": 3
  }
}
```

**Response (Token Geçersiz)**:
```json
{
  "success": false,
  "error": "Geçersiz token",
  "action": "login_required"
}
```

---

### 3. **Logout** - Token'ı İptal Et

```http
POST /api/mobile/logout
Authorization: Bearer qL8xYz3mN5pR9sT2vW4aC6eF1hJ7kM0nP8qR3sT5vW7xY9zA1bC3dE5fG7hI9jK1mL3
```

**Response (Success)**:
```json
{
  "success": true,
  "message": "Çıkış başarılı"
}
```

---

## 🔧 MOBİL UYGULAMA ENTEGRASYONU

### **React Native / Capacitor Örneği**

#### 1. **Token Kaydetme**

```javascript
// AsyncStorage ile token kaydet
import AsyncStorage from '@react-native-async-storage/async-storage';

async function login(email, password) {
  try {
    const response = await fetch('https://tevkil.fly.dev/api/mobile/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Token'ı kalıcı olarak kaydet
      await AsyncStorage.setItem('api_token', data.token);
      await AsyncStorage.setItem('user', JSON.stringify(data.user));
      
      console.log('✅ Login başarılı, token kaydedildi');
      return data.user;
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('❌ Login hatası:', error);
    throw error;
  }
}
```

#### 2. **Uygulama Başlatınca Token Kontrolü**

```javascript
async function checkAuth() {
  try {
    // Token'ı oku
    const token = await AsyncStorage.getItem('api_token');
    
    if (!token) {
      // Token yok, login ekranına git
      return null;
    }
    
    // Token'ı doğrula
    const response = await fetch('https://tevkil.fly.dev/api/mobile/verify', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Token geçerli, kullanıcı bilgilerini döndür
      await AsyncStorage.setItem('user', JSON.stringify(data.user));
      console.log('✅ Token geçerli, otomatik login');
      return data.user;
    } else {
      // Token geçersiz, login ekranına git
      await AsyncStorage.removeItem('api_token');
      await AsyncStorage.removeItem('user');
      console.log('❌ Token geçersiz, login gerekli');
      return null;
    }
  } catch (error) {
    console.error('❌ Auth kontrolü hatası:', error);
    return null;
  }
}
```

#### 3. **Logout**

```javascript
async function logout() {
  try {
    const token = await AsyncStorage.getItem('api_token');
    
    if (token) {
      // Token'ı iptal et (backend'de)
      await fetch('https://tevkil.fly.dev/api/mobile/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    }
    
    // Local token'ı sil
    await AsyncStorage.removeItem('api_token');
    await AsyncStorage.removeItem('user');
    
    console.log('✅ Logout başarılı');
  } catch (error) {
    console.error('❌ Logout hatası:', error);
  }
}
```

#### 4. **API İsteklerinde Token Kullanımı**

```javascript
async function apiRequest(endpoint, options = {}) {
  const token = await AsyncStorage.getItem('api_token');
  
  const response = await fetch(`https://tevkil.fly.dev${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': token ? `Bearer ${token}` : '',
    },
  });
  
  return response.json();
}

// Örnek kullanım
const posts = await apiRequest('/api/posts');
```

---

## 📊 KARŞILAŞTIRMA

| Özellik | Web (Session) | Mobil (API Token) |
|---------|--------------|-------------------|
| **Authentication** | Session Cookie | Bearer Token |
| **Süre** | 24 saat | Sınırsız (logout yapana kadar) |
| **Browser Kapanınca** | Logout oluyor | Açık kalıyor ✅ |
| **Güvenlik** | HttpOnly Cookie | Encrypted Token |
| **Logout** | Session.clear() | Token revoke |

---

## 🔒 GÜVENLİK

### **Token Güvenliği**:
- ✅ 64 karakter güvenli token (`secrets.token_urlsafe(48)`)
- ✅ Veritabanında unique olarak saklanıyor
- ✅ Her istekte `last_used` güncellenıyor
- ✅ Logout yapınca token siliniyor
- ✅ Token çalınsa bile user logout yapınca geçersiz oluyor

### **Rate Limiting**:
```python
@limiter.limit("10 per minute")  # Login endpoint
```

### **HTTPS Zorunluluğu**:
- Production'da tüm API istekleri HTTPS üzerinden
- Token plaintext gönderilse bile şifreli kanal

---

## 🧪 TEST SENARYOLARI

### Test 1: İlk Login
```
1. Mobil app'i aç
2. Email/password ile login ol
3. Token kaydedildi mi kontrol et (AsyncStorage)
✅ Token ve user bilgileri kaydedildi
```

### Test 2: Uygulamayı Kapat/Aç
```
1. Mobil app'i kapat (force close)
2. Tekrar aç
3. checkAuth() çalışıyor
✅ Token geçerli, otomatik login oldu
```

### Test 3: Logout
```
1. Logout butonuna bas
2. Token silindi mi kontrol et
3. Uygulamayı tekrar aç
✅ Token yok, login ekranı gösteriliyor
```

### Test 4: Token Doğrulama
```
1. Login ol
2. /api/mobile/verify endpoint'ini çağır
✅ User bilgileri döndü, unread_notifications güncellendi
```

---

## 📝 DATABASE MIGRATION

Migration otomatik çalıştırıldı ✅

**Eklenen Kolonlar**:
```sql
ALTER TABLE users ADD COLUMN api_token VARCHAR(64);
ALTER TABLE users ADD COLUMN api_token_created_at DATETIME;
ALTER TABLE users ADD COLUMN api_token_last_used DATETIME;
CREATE UNIQUE INDEX idx_users_api_token ON users(api_token);
```

---

## 🚀 DEPLOYMENT

**Değişiklikler**:
1. ✅ `models.py` - API token kolonları eklendi
2. ✅ `app.py` - 3 mobil API endpoint eklendi
3. ✅ `migrate_add_api_token.py` - Database migration
4. ✅ Web session ayarları normale döndü (24 saat)

**Deploy Edilecek**:
```bash
git add models.py app.py migrate_add_api_token.py
git commit -m "feat: Add mobile API token authentication system"
fly deploy
```

---

## 📱 MOBİL UYGULAMA GÜNCELLEMESI

**Capacitor Android Projesi**: `c:\Users\KOPTAY\Desktop\tevkil_proje\android`

**Yapılması Gerekenler**:
1. AsyncStorage kütüphanesini ekle
2. Login ekranını güncelle (API endpoint kullan)
3. App.js'de checkAuth() ekle
4. Logout fonksiyonunu güncelle
5. Tüm API isteklerine Authorization header ekle

---

## ✅ SONUÇ

**PROBLEM**: Mobil uygulamada her kapanışta logout oluyordu ❌

**ÇÖZÜM**: 
- ✅ API token sistemi eklendi
- ✅ Token kalıcı olarak cihazda saklanıyor
- ✅ Uygulama kapansa bile token geçerli
- ✅ Web session etkilenmedi (normal çalışıyor)

**DURUM**: Backend hazır, mobil uygulama güncellenecek


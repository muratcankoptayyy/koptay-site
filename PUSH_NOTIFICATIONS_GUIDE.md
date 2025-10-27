# Push Notifications (FCM) Implementation Guide

Bu doküman, Tevkil Platform'a Firebase Cloud Messaging (FCM) ile push notification özelliğinin nasıl ekleneceğini açıklar.

## ⚠️ Ön Gereksinimler

1. **Firebase Account:** Google hesabı gerekli
2. **Domain:** Web push için HTTPS domain (localhost'ta test edilebilir)
3. **Browser Support:** Chrome, Firefox, Safari (macOS 11.0+)

---

## 📋 Implementation Steps

### Step 1: Firebase Project Setup

#### 1.1 Firebase Console
1. https://console.firebase.google.com/ adresine git
2. "Add project" tıkla
3. Proje adı: `tevkil-platform`
4. Google Analytics: Enable (optional)
5. Proje oluştur

#### 1.2 Web App Registration
1. Project Overview → Add app → Web (</> icon)
2. App nickname: `Tevkil Web`
3. "Also set up Firebase Hosting": Skip
4. Register app

#### 1.3 Get Configuration
Firebase config'i kopyala (örnek):
```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "tevkil-platform.firebaseapp.com",
  projectId: "tevkil-platform",
  storageBucket: "tevkil-platform.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};
```

#### 1.4 Enable Cloud Messaging
1. Project Settings → Cloud Messaging
2. "Cloud Messaging API (Legacy)" → Enable
3. Server key'i kopyala (örnek: `AAAA...xyz`)
4. Sender ID'yi kopyala

---

### Step 2: Environment Variables

`.env` dosyasına ekle:
```bash
# Firebase Cloud Messaging
FCM_SERVER_KEY=AAAA...xyz
FCM_SENDER_ID=123456789
```

---

### Step 3: Frontend Implementation

#### 3.1 Firebase SDK Installation

`templates/base.html` içine ekle (closing `</body>` öncesi):

```html
<!-- Firebase App (Core) -->
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js"></script>

<!-- Firebase Messaging -->
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging-compat.js"></script>

<script>
  // Firebase configuration
  const firebaseConfig = {
    apiKey: "{{ config['FCM_API_KEY'] }}",
    authDomain: "tevkil-platform.firebaseapp.com",
    projectId: "tevkil-platform",
    storageBucket: "tevkil-platform.appspot.com",
    messagingSenderId: "{{ config['FCM_SENDER_ID'] }}",
    appId: "{{ config['FCM_APP_ID'] }}"
  };

  // Initialize Firebase
  firebase.initializeApp(firebaseConfig);
  
  // Get messaging instance
  const messaging = firebase.messaging();
</script>

<script src="{{ url_for('static', filename='js/push-notifications.js') }}"></script>
```

#### 3.2 Service Worker

`static/firebase-messaging-sw.js` oluştur:

```javascript
// Import Firebase scripts (service worker)
importScripts('https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging-compat.js');

// Initialize Firebase in service worker
firebase.initializeApp({
  apiKey: "AIzaSy...",
  authDomain: "tevkil-platform.firebaseapp.com",
  projectId: "tevkil-platform",
  storageBucket: "tevkil-platform.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
});

// Get messaging instance
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log('Background message received:', payload);
  
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/static/logo-icon.svg',
    badge: '/static/badge-icon.png',
    data: payload.data,
    tag: payload.data?.tag || 'default',
    requireInteraction: false
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  const url = event.notification.data?.url || '/';
  
  event.waitUntil(
    clients.openWindow(url)
  );
});
```

#### 3.3 Push Notification Handler

`static/js/push-notifications.js` oluştur:

```javascript
/**
 * Push Notifications Handler
 * Manages FCM token registration and notification display
 */

class PushNotificationManager {
  constructor() {
    this.messaging = null;
    this.currentToken = null;
    this.isSupported = this.checkSupport();
  }

  checkSupport() {
    return 'Notification' in window && 
           'serviceWorker' in navigator && 
           'PushManager' in window;
  }

  async init() {
    if (!this.isSupported) {
      console.warn('Push notifications not supported');
      return false;
    }

    try {
      // Register service worker
      const registration = await navigator.serviceWorker.register(
        '/static/firebase-messaging-sw.js'
      );
      
      // Wait for service worker to be ready
      await navigator.serviceWorker.ready;
      
      // Initialize messaging
      this.messaging = firebase.messaging();
      
      // Handle foreground messages
      this.messaging.onMessage((payload) => {
        this.handleForegroundMessage(payload);
      });

      return true;
    } catch (error) {
      console.error('Service worker registration failed:', error);
      return false;
    }
  }

  async requestPermission() {
    try {
      const permission = await Notification.requestPermission();
      
      if (permission === 'granted') {
        console.log('Notification permission granted');
        await this.getToken();
        return true;
      } else {
        console.log('Notification permission denied');
        return false;
      }
    } catch (error) {
      console.error('Permission request failed:', error);
      return false;
    }
  }

  async getToken() {
    try {
      const token = await this.messaging.getToken({
        vapidKey: 'YOUR_VAPID_KEY' // Get from Firebase Console
      });
      
      if (token) {
        console.log('FCM Token:', token);
        this.currentToken = token;
        
        // Send token to backend
        await this.sendTokenToServer(token);
        
        return token;
      } else {
        console.log('No token available');
        return null;
      }
    } catch (error) {
      console.error('Token retrieval failed:', error);
      return null;
    }
  }

  async sendTokenToServer(token) {
    try {
      const response = await fetch('/api/push/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('[name=csrf_token]')?.value
        },
        body: JSON.stringify({ token })
      });

      if (response.ok) {
        console.log('Token registered successfully');
      } else {
        console.error('Token registration failed');
      }
    } catch (error) {
      console.error('Failed to send token to server:', error);
    }
  }

  handleForegroundMessage(payload) {
    console.log('Foreground message received:', payload);
    
    // Show toast notification
    if (window.toast) {
      const title = payload.notification.title;
      const body = payload.notification.body;
      
      window.toast.info(`${title}: ${body}`, 10000);
    }

    // Optional: Show browser notification anyway
    if (Notification.permission === 'granted') {
      new Notification(payload.notification.title, {
        body: payload.notification.body,
        icon: '/static/logo-icon.svg',
        data: payload.data
      });
    }
  }

  async deleteToken() {
    try {
      await this.messaging.deleteToken();
      this.currentToken = null;
      console.log('Token deleted');
      
      // Notify server
      await fetch('/api/push/unregister', {
        method: 'POST',
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrf_token]')?.value
        }
      });
      
      return true;
    } catch (error) {
      console.error('Token deletion failed:', error);
      return false;
    }
  }
}

// Initialize on page load
let pushManager;

document.addEventListener('DOMContentLoaded', async () => {
  pushManager = new PushNotificationManager();
  
  const initialized = await pushManager.init();
  
  if (initialized) {
    // Auto-request permission for logged-in users
    if (document.body.dataset.userId) {
      // Check if already granted
      if (Notification.permission === 'default') {
        // Show custom prompt first
        showPushPrompt();
      } else if (Notification.permission === 'granted') {
        // Already granted, get token
        await pushManager.getToken();
      }
    }
  }
});

function showPushPrompt() {
  // Custom UI prompt before browser prompt
  const promptHtml = `
    <div class="fixed bottom-4 right-4 bg-white dark:bg-gray-800 rounded-lg shadow-xl p-4 max-w-sm z-50 border border-gray-200 dark:border-gray-700" id="pushPrompt">
      <div class="flex items-start gap-3">
        <span class="material-symbols-outlined text-blue-600 dark:text-blue-400 text-2xl">notifications_active</span>
        <div class="flex-1">
          <h4 class="font-semibold text-gray-900 dark:text-white mb-1">Bildirimleri Aç</h4>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">Yeni mesajlar ve başvurular için anlık bildirim al</p>
          <div class="flex gap-2">
            <button onclick="acceptPushPrompt()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Bildirimleri Aç
            </button>
            <button onclick="dismissPushPrompt()" class="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white px-4 py-2 text-sm font-medium transition-colors">
              Şimdi Değil
            </button>
          </div>
        </div>
        <button onclick="dismissPushPrompt()" class="text-gray-400 hover:text-gray-600">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
    </div>
  `;
  
  document.body.insertAdjacentHTML('beforeend', promptHtml);
}

async function acceptPushPrompt() {
  dismissPushPrompt();
  await pushManager.requestPermission();
}

function dismissPushPrompt() {
  document.getElementById('pushPrompt')?.remove();
}

// Expose to global scope
window.pushManager = pushManager;
```

---

### Step 4: Backend Implementation

#### 4.1 Database Migration

`add_device_tokens_table.py`:

```python
from models import db
from sqlalchemy import text

def add_device_tokens_table():
    """Create device_tokens table for FCM tokens"""
    
    with db.engine.connect() as conn:
        # Create table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS device_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token TEXT NOT NULL UNIQUE,
                device_type VARCHAR(50) DEFAULT 'web',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        '''))
        
        # Create indexes
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_device_tokens_user ON device_tokens(user_id)'))
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_device_tokens_active ON device_tokens(is_active)'))
        
        conn.commit()
    
    print('✓ device_tokens table created successfully')

if __name__ == '__main__':
    from app import app
    with app.app_context():
        add_device_tokens_table()
```

#### 4.2 Push Service

`push_notification_service.py`:

```python
import os
import requests
from datetime import datetime

class PushNotificationService:
    """Firebase Cloud Messaging service"""
    
    FCM_URL = 'https://fcm.googleapis.com/fcm/send'
    
    @staticmethod
    def send_notification(token, title, body, data=None, click_action=None):
        """
        Send push notification to a device
        
        Args:
            token: FCM device token
            title: Notification title
            body: Notification body
            data: Custom data payload
            click_action: URL to open on click
        """
        headers = {
            'Authorization': f'key={os.getenv("FCM_SERVER_KEY")}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'to': token,
            'notification': {
                'title': title,
                'body': body,
                'icon': '/static/logo-icon.svg',
                'click_action': click_action or '/'
            },
            'data': data or {},
            'priority': 'high'
        }
        
        try:
            response = requests.post(
                PushNotificationService.FCM_URL,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': result.get('success', 0) > 0,
                    'message_id': result.get('results', [{}])[0].get('message_id')
                }
            else:
                print(f'FCM Error: {response.status_code} - {response.text}')
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            print(f'Push notification failed: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def send_to_user(user_id, title, body, data=None, click_action=None):
        """
        Send notification to all devices of a user
        
        Args:
            user_id: User ID
            title: Notification title
            body: Notification body
            data: Custom data
            click_action: URL to open
        """
        from models import db
        from sqlalchemy import text
        
        # Get all active tokens for user
        result = db.session.execute(
            text('SELECT token FROM device_tokens WHERE user_id = :user_id AND is_active = TRUE'),
            {'user_id': user_id}
        )
        
        tokens = [row[0] for row in result]
        
        if not tokens:
            return {'success': False, 'error': 'No active tokens'}
        
        results = []
        for token in tokens:
            result = PushNotificationService.send_notification(
                token, title, body, data, click_action
            )
            results.append(result)
        
        success_count = sum(1 for r in results if r.get('success'))
        
        return {
            'success': success_count > 0,
            'sent': success_count,
            'total': len(tokens)
        }
```

#### 4.3 API Endpoints

`app.py`'ye ekle:

```python
from push_notification_service import PushNotificationService

@app.route('/api/push/register', methods=['POST'])
@login_required
def register_push_token():
    """Register FCM token for push notifications"""
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Token required'}), 400
    
    try:
        # Check if token already exists
        existing = db.session.execute(
            text('SELECT id FROM device_tokens WHERE token = :token'),
            {'token': token}
        ).first()
        
        if existing:
            # Update last_used
            db.session.execute(
                text('UPDATE device_tokens SET last_used = NOW(), is_active = TRUE WHERE token = :token'),
                {'token': token}
            )
        else:
            # Insert new token
            db.session.execute(
                text('''
                    INSERT INTO device_tokens (user_id, token, device_type, created_at, last_used)
                    VALUES (:user_id, :token, 'web', NOW(), NOW())
                '''),
                {'user_id': current_user.id, 'token': token}
            )
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Token registered'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/push/unregister', methods=['POST'])
@login_required
def unregister_push_token():
    """Unregister current user's push tokens"""
    try:
        db.session.execute(
            text('UPDATE device_tokens SET is_active = FALSE WHERE user_id = :user_id'),
            {'user_id': current_user.id}
        )
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Example usage in other endpoints:

# In accept_application route:
@app.route('/application/<int:app_id>/accept', methods=['POST'])
@login_required
def accept_application(app_id):
    # ... existing code ...
    
    # Send push notification
    PushNotificationService.send_to_user(
        user_id=application.applicant_id,
        title='Başvurunuz Kabul Edildi!',
        body=f'{current_user.full_name} başvurunuzu kabul etti.',
        data={'type': 'application_accepted', 'application_id': app_id},
        click_action=f'/applications/{app_id}'
    )
    
    # ... rest of code ...

# In new message handler:
@socketio.on('send_message')
def handle_send_message(data):
    # ... existing code ...
    
    # Send push notification
    PushNotificationService.send_to_user(
        user_id=receiver_id,
        title=f'Yeni Mesaj: {current_user.full_name}',
        body=message_content[:100],
        data={'type': 'new_message', 'conversation_id': conversation_id},
        click_action=f'/messages/{conversation_id}'
    )
    
    # ... rest of code ...
```

---

### Step 5: VAPID Key Setup

1. Firebase Console → Project Settings → Cloud Messaging
2. Web Push certificates → Generate key pair
3. VAPID key'i kopyala
4. `push-notifications.js` içinde `YOUR_VAPID_KEY` yerine yapıştır

---

### Step 6: Settings UI

`templates/settings.html`'e ekle:

```html
<!-- Push Notifications Section -->
<div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Push Bildirimleri</h3>
    
    <div class="space-y-4">
        <div class="flex items-center justify-between">
            <div>
                <p class="font-medium text-gray-900 dark:text-white">Tarayıcı Bildirimleri</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">Yeni mesaj ve başvurular için anlık bildirim al</p>
            </div>
            <button id="togglePushNotifications" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
                Bildirimleri Aç
            </button>
        </div>
        
        <div id="pushStatus" class="text-sm text-gray-600 dark:text-gray-400"></div>
    </div>
</div>

<script>
document.getElementById('togglePushNotifications').addEventListener('click', async () => {
    if (!window.pushManager) {
        alert('Push notifications not supported');
        return;
    }
    
    if (Notification.permission === 'granted') {
        // Disable
        await window.pushManager.deleteToken();
        updatePushButton('disabled');
    } else {
        // Enable
        const granted = await window.pushManager.requestPermission();
        updatePushButton(granted ? 'enabled' : 'denied');
    }
});

function updatePushButton(status) {
    const button = document.getElementById('togglePushNotifications');
    const statusText = document.getElementById('pushStatus');
    
    if (status === 'enabled') {
        button.textContent = 'Bildirimleri Kapat';
        button.classList.replace('bg-blue-600', 'bg-red-600');
        button.classList.replace('hover:bg-blue-700', 'hover:bg-red-700');
        statusText.textContent = '✓ Bildirimler aktif';
        statusText.classList.add('text-green-600');
    } else if (status === 'disabled') {
        button.textContent = 'Bildirimleri Aç';
        button.classList.replace('bg-red-600', 'bg-blue-600');
        button.classList.replace('hover:bg-red-700', 'hover:bg-blue-700');
        statusText.textContent = 'Bildirimler kapalı';
        statusText.classList.remove('text-green-600');
    } else {
        statusText.textContent = '⚠ Bildirim izni reddedildi';
    }
}

// Check initial state
if (Notification.permission === 'granted') {
    updatePushButton('enabled');
}
</script>
```

---

## 🧪 Testing

### Local Testing:

```bash
# 1. Start local server with HTTPS
openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365
python -m http.server 5000 --bind localhost

# 2. Visit https://localhost:5000
# 3. Open browser console
# 4. Check for FCM token
console.log(window.pushManager.currentToken);

# 5. Test notification
await window.pushManager.messaging.getToken();
```

### Send Test Notification:

```bash
curl -X POST https://fcm.googleapis.com/fcm/send \
  -H "Authorization: key=YOUR_SERVER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "DEVICE_TOKEN",
    "notification": {
      "title": "Test Notification",
      "body": "This is a test",
      "icon": "/static/logo-icon.svg"
    }
  }'
```

---

## 📱 Notification Types

### 1. New Application
```python
PushNotificationService.send_to_user(
    user_id=post.lawyer_id,
    title='Yeni Başvuru!',
    body=f'{applicant.full_name} ilanınıza başvurdu',
    data={'type': 'new_application', 'post_id': post.id},
    click_action=f'/posts/{post.id}#applications'
)
```

### 2. Application Accepted
```python
PushNotificationService.send_to_user(
    user_id=application.applicant_id,
    title='Başvurunuz Kabul Edildi!',
    body=f'{post.lawyer.full_name} başvurunuzu kabul etti',
    data={'type': 'application_accepted'},
    click_action='/applications'
)
```

### 3. New Message
```python
PushNotificationService.send_to_user(
    user_id=receiver_id,
    title=f'Yeni Mesaj: {sender.full_name}',
    body=message_content[:100],
    data={'type': 'new_message', 'conversation_id': conv_id},
    click_action=f'/messages/{conv_id}'
)
```

### 4. New Rating
```python
PushNotificationService.send_to_user(
    user_id=rated_user_id,
    title='Yeni Değerlendirme',
    body=f'{reviewer.full_name} sizi değerlendirdi: {rating}/5',
    data={'type': 'new_rating'},
    click_action='/profile#ratings'
)
```

---

## 🔒 Security Considerations

1. **Token Storage:** Tokens veritabanında encrypted
2. **HTTPS Only:** Push notifications require HTTPS
3. **Permission:** Always request user permission
4. **Rate Limiting:** Limit notification frequency
5. **Unsubscribe:** Allow users to disable easily

---

## 📊 Analytics

Track notification metrics:
- Delivery rate
- Click-through rate (CTR)
- Permission grant rate
- Active tokens count

---

## 🚨 Troubleshooting

### Token not generating:
- Check VAPID key
- Verify Firebase config
- Check browser console
- Ensure HTTPS

### Notifications not received:
- Check FCM server key
- Verify token is registered
- Check browser permissions
- Look at service worker logs

### Service worker errors:
- Clear browser cache
- Re-register service worker
- Check firebase-messaging-sw.js path

---

## 📝 Next Steps

1. Run `python add_device_tokens_table.py`
2. Create `push_notification_service.py`
3. Create `static/js/push-notifications.js`
4. Create `static/firebase-messaging-sw.js`
5. Update `app.py` with push endpoints
6. Update `templates/base.html`
7. Update `.env` with FCM keys
8. Test locally
9. Deploy to production

---

**Estimated Time:** 6-8 hours  
**Priority:** Low (optional feature)  
**Dependencies:** Firebase account, HTTPS domain

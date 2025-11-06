// PWA Install Prompt Handler
let deferredPrompt;
let installButton;

// Detect if app is already installed
function isAppInstalled() {
  return window.matchMedia('(display-mode: standalone)').matches || 
         window.navigator.standalone === true;
}

// Show install banner
function showInstallBanner() {
  const banner = document.getElementById('pwa-install-banner');
  // Sadece banner elementi varsa göster (giriş yapmış kullanıcılar için)
  if (banner && !isAppInstalled()) {
    banner.style.display = 'block';
    console.log('[PWA] Install banner shown for authenticated user');
  } else if (!banner) {
    console.log('[PWA] Install banner not available (user not authenticated)');
  }
}

// Hide install banner
function hideInstallBanner() {
  const banner = document.getElementById('pwa-install-banner');
  if (banner) {
    banner.style.display = 'none';
  }
}

// Listen for beforeinstallprompt event
window.addEventListener('beforeinstallprompt', (e) => {
  console.log('[PWA] Install prompt ready');
  e.preventDefault();
  deferredPrompt = e;
  showInstallBanner();
});

// Install button click handler
function installPWA() {
  if (!deferredPrompt) {
    console.log('[PWA] No install prompt available');
    return;
  }

  // Show the install prompt
  deferredPrompt.prompt();

  // Wait for user response
  deferredPrompt.userChoice.then((choiceResult) => {
    if (choiceResult.outcome === 'accepted') {
      console.log('[PWA] User accepted install');
      hideInstallBanner();
    } else {
      console.log('[PWA] User dismissed install');
    }
    deferredPrompt = null;
  });
}

// Listen for app installed
window.addEventListener('appinstalled', (e) => {
  console.log('[PWA] App installed successfully');
  hideInstallBanner();
  
  // Show success message
  if (typeof showNotification === 'function') {
    showNotification('✅ Uygulama ana ekranınıza eklendi!', 'success');
  }
});

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/static/service-worker.js')
      .then((registration) => {
        console.log('[PWA] Service Worker registered:', registration.scope);
        
        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          console.log('[PWA] New Service Worker found');
          
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              console.log('[PWA] New version available! Refresh to update.');
              showUpdateNotification();
            }
          });
        });
      })
      .catch((error) => {
        console.error('[PWA] Service Worker registration failed:', error);
      });

    // Check for updates every hour
    setInterval(() => {
      navigator.serviceWorker.ready.then((registration) => {
        registration.update();
      });
    }, 60 * 60 * 1000);
  });
}

// Show update notification
function showUpdateNotification() {
  const updateBanner = document.createElement('div');
  updateBanner.id = 'pwa-update-banner';
  updateBanner.className = 'fixed top-0 left-0 right-0 bg-blue-500 text-white p-4 z-50 shadow-lg';
  updateBanner.innerHTML = `
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="material-symbols-outlined">update</span>
        <span>Yeni sürüm mevcut! Güncellemek için sayfayı yenileyin.</span>
      </div>
      <button onclick="location.reload()" class="bg-white text-blue-500 px-4 py-2 rounded-lg font-semibold hover:bg-blue-50">
        Yenile
      </button>
    </div>
  `;
  document.body.insertBefore(updateBanner, document.body.firstChild);
}

// Request notification permission
async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    console.log('[PWA] Notifications not supported');
    return false;
  }

  if (Notification.permission === 'granted') {
    console.log('[PWA] Notification permission already granted');
    return true;
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    console.log('[PWA] Notification permission:', permission);
    return permission === 'granted';
  }

  return false;
}

// Show a test notification
function showTestNotification() {
  if (Notification.permission === 'granted' && 'serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then((registration) => {
      registration.showNotification('Tevkil', {
        body: 'Bildirimler aktif! Yeni başvuru ve mesajlardan haberdar olacaksınız.',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-96x96.png',
        vibrate: [200, 100, 200],
        tag: 'test-notification'
      });
    });
  }
}

// Background sync for offline actions
async function registerBackgroundSync(tag) {
  if ('serviceWorker' in navigator && 'sync' in navigator.serviceWorker) {
    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.sync.register(tag);
      console.log('[PWA] Background sync registered:', tag);
    } catch (error) {
      console.error('[PWA] Background sync registration failed:', error);
    }
  }
}

// Check if online/offline
window.addEventListener('online', () => {
  console.log('[PWA] Connection restored');
  const banner = document.getElementById('offline-banner');
  if (banner) banner.remove();
  
  // Trigger background sync
  registerBackgroundSync('sync-applications');
  registerBackgroundSync('sync-messages');
});

window.addEventListener('offline', () => {
  console.log('[PWA] Connection lost');
  showOfflineBanner();
});

function showOfflineBanner() {
  const existingBanner = document.getElementById('offline-banner');
  if (existingBanner) return;

  const banner = document.createElement('div');
  banner.id = 'offline-banner';
  banner.className = 'fixed top-0 left-0 right-0 bg-yellow-500 text-white p-3 z-50 shadow-lg';
  banner.innerHTML = `
    <div class="max-w-7xl mx-auto flex items-center justify-center gap-2">
      <span class="material-symbols-outlined">cloud_off</span>
      <span>İnternet bağlantısı yok. Bazı özellikler çalışmayabilir.</span>
    </div>
  `;
  document.body.insertBefore(banner, document.body.firstChild);
}

// Check connection status on load
if (!navigator.onLine) {
  showOfflineBanner();
}

// Display mode detection
function displayModeChanged() {
  const isStandalone = isAppInstalled();
  console.log('[PWA] Running in standalone mode:', isStandalone);
  
  if (isStandalone) {
    document.body.classList.add('pwa-mode');
  } else {
    document.body.classList.remove('pwa-mode');
  }
}

// Listen for display mode changes
const mediaQuery = window.matchMedia('(display-mode: standalone)');
mediaQuery.addListener(displayModeChanged);
displayModeChanged();

console.log('[PWA] PWA script loaded');

// ============================================
// PUSH NOTIFICATIONS - TEVKIL PLATFORM
// ============================================

import { PushNotifications } from '@capacitor/push-notifications';
import { Capacitor } from '@capacitor/core';

class PushNotificationManager {
    constructor() {
        this.isSupported = Capacitor.isNativePlatform();
        this.token = null;
        this.listeners = [];
    }

    // Initialize push notifications
    async init() {
        if (!this.isSupported) {
            console.log('📱 Push notifications not supported on web platform');
            return false;
        }

        try {
            // Request permission
            let permStatus = await PushNotifications.checkPermissions();

            if (permStatus.receive === 'prompt') {
                permStatus = await PushNotifications.requestPermissions();
            }

            if (permStatus.receive !== 'granted') {
                console.warn('⚠️ Push notification permission denied');
                return false;
            }

            // Register with APNs / FCM
            await PushNotifications.register();

            // Listen for registration
            await PushNotifications.addListener('registration', (token) => {
                console.log('✅ Push registration success:', token.value);
                this.token = token.value;
                this.sendTokenToServer(token.value);
            });

            // Listen for registration errors
            await PushNotifications.addListener('registrationError', (error) => {
                console.error('❌ Push registration error:', error);
            });

            // Listen for push notifications received
            await PushNotifications.addListener('pushNotificationReceived', (notification) => {
                console.log('📬 Push notification received:', notification);
                this.handleNotificationReceived(notification);
            });

            // Listen for notification tapped
            await PushNotifications.addListener('pushNotificationActionPerformed', (notification) => {
                console.log('👆 Push notification tapped:', notification);
                this.handleNotificationTapped(notification);
            });

            console.log('✅ Push notifications initialized');
            return true;

        } catch (error) {
            console.error('❌ Error initializing push notifications:', error);
            return false;
        }
    }

    // Send token to backend
    async sendTokenToServer(token) {
        try {
            const response = await fetch('/api/notifications/register-device', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    token: token,
                    platform: Capacitor.getPlatform()
                })
            });

            if (response.ok) {
                console.log('✅ Device token registered on server');
            } else {
                console.error('❌ Failed to register device token');
            }
        } catch (error) {
            console.error('❌ Error sending token to server:', error);
        }
    }

    // Handle notification received (app in foreground)
    handleNotificationReceived(notification) {
        const { title, body, data } = notification;

        // Show in-app notification
        if (window.MobileHelpers) {
            window.MobileHelpers.showToast(`${title}: ${body}`, 'info', 5000);
        }

        // Trigger custom events
        this.listeners.forEach(listener => {
            if (listener.type === 'received') {
                listener.callback(notification);
            }
        });

        // Update UI (e.g., unread count badge)
        if (data.type === 'message') {
            this.updateMessageBadge();
        } else if (data.type === 'application_status') {
            this.showApplicationUpdate(data);
        }
    }

    // Handle notification tapped (user clicked on notification)
    handleNotificationTapped(notification) {
        const { data } = notification.notification;

        // Navigate based on notification type
        if (data.type === 'message') {
            window.location.href = `/chat/${data.conversation_id}`;
        } else if (data.type === 'application_status') {
            window.location.href = `/posts/${data.post_id}`;
        } else if (data.type === 'new_post') {
            window.location.href = `/posts/${data.post_id}`;
        } else {
            window.location.href = '/dashboard';
        }

        // Trigger custom events
        this.listeners.forEach(listener => {
            if (listener.type === 'tapped') {
                listener.callback(notification);
            }
        });
    }

    // Update message badge
    async updateMessageBadge() {
        try {
            const response = await fetch('/api/chat/unread-count');
            const data = await response.json();
            
            const badge = document.querySelector('.bottom-nav-item .badge');
            if (badge) {
                badge.textContent = data.count > 9 ? '9+' : data.count;
                badge.style.display = data.count > 0 ? 'block' : 'none';
            }
        } catch (error) {
            console.error('❌ Error updating message badge:', error);
        }
    }

    // Show application status update
    showApplicationUpdate(data) {
        const message = data.status === 'accepted' 
            ? `✅ Başvurunuz kabul edildi: ${data.post_title}`
            : `❌ Başvurunuz reddedildi: ${data.post_title}`;

        if (window.MobileHelpers) {
            window.MobileHelpers.showToast(message, data.status === 'accepted' ? 'success' : 'error', 5000);
        }
    }

    // Get CSRF token
    getCSRFToken() {
        const token = document.querySelector('input[name="csrf_token"]');
        return token ? token.value : '';
    }

    // Add custom event listener
    addListener(type, callback) {
        this.listeners.push({ type, callback });
    }

    // Remove all listeners
    async removeAllListeners() {
        if (this.isSupported) {
            await PushNotifications.removeAllListeners();
        }
        this.listeners = [];
    }

    // Get delivered notifications
    async getDeliveredNotifications() {
        if (!this.isSupported) return [];

        try {
            const notificationList = await PushNotifications.getDeliveredNotifications();
            return notificationList.notifications;
        } catch (error) {
            console.error('❌ Error getting delivered notifications:', error);
            return [];
        }
    }

    // Clear all notifications
    async clearAllNotifications() {
        if (!this.isSupported) return;

        try {
            await PushNotifications.removeAllDeliveredNotifications();
            console.log('✅ All notifications cleared');
        } catch (error) {
            console.error('❌ Error clearing notifications:', error);
        }
    }
}

// Initialize and export
const pushManager = new PushNotificationManager();

// Auto-initialize when app loads
document.addEventListener('DOMContentLoaded', async () => {
    const initialized = await pushManager.init();
    if (initialized) {
        console.log('✅ Push notifications ready');
    }
});

// Export for use in other modules
export default pushManager;

// Also attach to window for non-module scripts
window.PushManager = pushManager;

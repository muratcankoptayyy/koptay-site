
class NotificationSystem {
    constructor() {
        // Initialize from storage or null
        this.lastCheck = localStorage.getItem('notification_last_check');
        this.checkInterval = 2000; // 2 seconds
        this.container = null;
        this.shownIds = this.getShownIds();
        this.init();
    }

    getShownIds() {
        try {
            return JSON.parse(localStorage.getItem('notification_shown_ids') || '[]');
        } catch {
            return [];
        }
    }

    saveShownIds() {
        // Keep only last 50 IDs
        if (this.shownIds.length > 50) {
            this.shownIds = this.shownIds.slice(-50);
        }
        localStorage.setItem('notification_shown_ids', JSON.stringify(this.shownIds));
    }

    init() {
        this.createContainer();
        this.startPolling();
        
        // Request notification permission for browser notifications
        if ("Notification" in window) {
            if (Notification.permission !== "granted" && Notification.permission !== "denied") {
                Notification.requestPermission();
            }
        }
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 350px;
            pointer-events: none;
        `;
        document.body.appendChild(this.container);
    }

    startPolling() {
        setInterval(() => this.checkNotifications(), this.checkInterval);
    }

    async checkNotifications() {
        try {
            const response = await fetch(`/notifications/check?last_check=${this.lastCheck || ''}`);
            if (!response.ok) return;

            const data = await response.json();
            
            // Update timestamp
            this.lastCheck = data.timestamp;
            localStorage.setItem('notification_last_check', this.lastCheck);

            // Sync shown IDs from storage (in case other tabs updated it)
            this.shownIds = this.getShownIds();

            // Process notifications
            if (data.notifications && data.notifications.length > 0) {
                data.notifications.forEach(notif => {
                    // Deduplication check
                    if (this.shownIds.includes(notif.id)) return;

                    // Don't show message notifications if we are in that conversation
                    if (notif.type === 'message' && window.location.pathname.includes(notif.url)) {
                        return;
                    }
                    
                    this.showNotification(notif);
                    
                    // Mark as shown
                    this.shownIds.push(notif.id);
                });
                
                this.saveShownIds();
            }
        } catch (error) {
            console.error('Notification check failed:', error);
        }
    }

    showNotification(notif) {
        // Browser Notification
        if ("Notification" in window && Notification.permission === "granted" && document.hidden) {
            new Notification(notif.title, {
                body: notif.message,
                icon: '/static/img/logo.png' // Make sure this exists or use a default
            });
        }

        // In-App Toast
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.style.cssText = `
            background: white;
            border-left: 4px solid var(--primary, #30696c);
            padding: 16px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            align-items: flex-start;
            gap: 12px;
            transform: translateX(120%);
            transition: transform 0.3s ease-out;
            pointer-events: auto;
            cursor: pointer;
            min-width: 300px;
        `;

        // Icon/Avatar
        let iconHtml = '';
        if (notif.avatar) {
            iconHtml = `<img src="${notif.avatar}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">`;
        } else {
            iconHtml = `
                <div style="width: 40px; height: 40px; background: var(--bg-light, #f3f4f6); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--primary, #30696c);">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                    </svg>
                </div>
            `;
        }

        toast.innerHTML = `
            ${iconHtml}
            <div style="flex: 1;">
                <h4 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600; color: #111827;">${notif.title}</h4>
                <p style="margin: 0; font-size: 13px; color: #6b7280; line-height: 1.4;">${notif.message}</p>
            </div>
            <button onclick="event.stopPropagation(); this.parentElement.remove()" style="background: none; border: none; color: #9ca3af; cursor: pointer; padding: 4px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        `;

        // Click handler
        toast.onclick = () => {
            if (notif.url) {
                window.location.href = notif.url;
            }
        };

        this.container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.style.transform = 'translateX(0)';
        });

        // Play sound
        this.playSound();

        // Auto remove (increased to 8 seconds)
        setTimeout(() => {
            toast.style.transform = 'translateX(120%)';
            setTimeout(() => toast.remove(), 300);
        }, 8000);
    }

    playSound() {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            
            const ctx = new AudioContext();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            
            osc.connect(gain);
            gain.connect(ctx.destination);
            
            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, ctx.currentTime); // A5
            osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.1); // Drop to A4
            
            gain.gain.setValueAtTime(0.1, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
            
            osc.start();
            osc.stop(ctx.currentTime + 0.1);
        } catch (e) {
            console.log('Audio play failed:', e);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only init if user is logged in (we can check for a specific element or variable)
    // For now, we'll assume the script is only included where needed or check for a global flag
    if (document.body.dataset.userLoggedIn === 'true') {
        window.notificationSystem = new NotificationSystem();
    }
});

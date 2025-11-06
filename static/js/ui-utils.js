/**
 * UI/UX Utility Functions
 * Loading spinners, toast notifications, animations
 */

// Toast Notification System
class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Container oluştur
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠',
            info: 'ℹ'
        };

        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
            <span class="toast-close" onclick="this.parentElement.remove()">×</span>
        `;

        this.container.appendChild(toast);

        // Auto remove
        setTimeout(() => {
            toast.classList.add('hiding');
            setTimeout(() => toast.remove(), 300);
        }, duration);

        return toast;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Global toast instance
const toast = new ToastManager();

// Loading Spinner
class LoadingManager {
    constructor() {
        this.overlay = null;
        this.spinner = null;
        this.init();
    }

    init() {
        // Overlay oluştur
        if (!document.querySelector('.loading-overlay')) {
            this.overlay = document.createElement('div');
            this.overlay.className = 'loading-overlay';
            document.body.appendChild(this.overlay);
        } else {
            this.overlay = document.querySelector('.loading-overlay');
        }

        // Spinner oluştur
        if (!document.querySelector('.loading-spinner')) {
            this.spinner = document.createElement('div');
            this.spinner.className = 'loading-spinner';
            this.spinner.innerHTML = '<div class="spinner"></div>';
            document.body.appendChild(this.spinner);
        } else {
            this.spinner = document.querySelector('.loading-spinner');
        }
    }

    show() {
        this.overlay.classList.add('active');
        this.spinner.classList.add('active');
    }

    hide() {
        this.overlay.classList.remove('active');
        this.spinner.classList.remove('active');
    }
}

// Global loading instance
const loading = new LoadingManager();

// Form Submit with Loading
function submitFormWithLoading(formElement) {
    formElement.addEventListener('submit', function(e) {
        loading.show();
    });
}

// Auto-submit forms with loading
document.addEventListener('DOMContentLoaded', function() {
    // Add loading to all forms with data-loading attribute
    document.querySelectorAll('form[data-loading]').forEach(form => {
        submitFormWithLoading(form);
    });

    // Page transition animation
    document.body.classList.add('page-transition');

    // Stagger animation for lists
    document.querySelectorAll('[data-stagger]').forEach(container => {
        const items = container.children;
        Array.from(items).forEach((item, index) => {
            item.classList.add('stagger-item');
            item.style.animationDelay = `${index * 0.1}s`;
        });
    });
});

// Smooth Scroll
function smoothScroll(target, duration = 800) {
    const targetElement = document.querySelector(target);
    if (!targetElement) return;

    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;

    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = ease(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }

    function ease(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }

    requestAnimationFrame(animation);
}

// Copy to Clipboard
function copyToClipboard(text, successMessage = 'Kopyalandı!') {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            toast.success(successMessage);
        }).catch(err => {
            toast.error('Kopyalama başarısız!');
        });
    } else {
        // Fallback
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            toast.success(successMessage);
        } catch (err) {
            toast.error('Kopyalama başarısız!');
        }
        document.body.removeChild(textArea);
    }
}

// Debounce Function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle Function
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Lazy Load Images
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading on page load
document.addEventListener('DOMContentLoaded', lazyLoadImages);

// Confirm Dialog
function confirmDialog(message, onConfirm, onCancel) {
    if (confirm(message)) {
        if (onConfirm) onConfirm();
        return true;
    } else {
        if (onCancel) onCancel();
        return false;
    }
}

// Export for global use
window.toast = toast;
window.loading = loading;
window.smoothScroll = smoothScroll;
window.copyToClipboard = copyToClipboard;
window.debounce = debounce;
window.throttle = throttle;
window.confirmDialog = confirmDialog;

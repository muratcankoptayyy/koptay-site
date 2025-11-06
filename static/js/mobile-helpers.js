// ============================================
// MOBİL YARDIMCI FONKSİYONLAR - TEVKIL
// ============================================

(function() {
    'use strict';

    // ============================================
    // MOBILE DETECTION
    // ============================================
    const isMobile = () => {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
            || window.innerWidth <= 768;
    };

    const isIOS = () => {
        return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    };

    const isAndroid = () => {
        return /Android/i.test(navigator.userAgent);
    };

    // ============================================
    // HAMBURGER MENU
    // ============================================
    function initMobileMenu() {
        const menuToggle = document.querySelector('.mobile-menu-toggle');
        const mobileMenu = document.querySelector('.mobile-nav-menu');
        const overlay = document.querySelector('.mobile-nav-overlay');

        if (!menuToggle || !mobileMenu) return;

        // Create overlay if doesn't exist
        if (!overlay) {
            const newOverlay = document.createElement('div');
            newOverlay.className = 'mobile-nav-overlay';
            document.body.appendChild(newOverlay);
        }

        menuToggle.addEventListener('click', () => {
            menuToggle.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            document.querySelector('.mobile-nav-overlay').classList.toggle('active');
            document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
        });

        // Close menu when clicking overlay
        document.querySelector('.mobile-nav-overlay').addEventListener('click', () => {
            menuToggle.classList.remove('active');
            mobileMenu.classList.remove('active');
            document.querySelector('.mobile-nav-overlay').classList.remove('active');
            document.body.style.overflow = '';
        });

        // Close menu when clicking a link
        mobileMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                menuToggle.classList.remove('active');
                mobileMenu.classList.remove('active');
                document.querySelector('.mobile-nav-overlay').classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }

    // ============================================
    // OFFLINE DETECTION
    // ============================================
    function initOfflineDetection() {
        let offlineIndicator = document.querySelector('.offline-indicator');
        
        if (!offlineIndicator) {
            offlineIndicator = document.createElement('div');
            offlineIndicator.className = 'offline-indicator';
            offlineIndicator.innerHTML = '⚠️ İnternet bağlantısı yok';
            document.body.insertBefore(offlineIndicator, document.body.firstChild);
        }

        window.addEventListener('online', () => {
            offlineIndicator.classList.remove('show');
            offlineIndicator.innerHTML = '✅ İnternet bağlantısı geri geldi';
            offlineIndicator.style.background = '#10b981';
            offlineIndicator.style.color = 'white';
            offlineIndicator.classList.add('show');
            setTimeout(() => {
                offlineIndicator.classList.remove('show');
            }, 3000);
        });

        window.addEventListener('offline', () => {
            offlineIndicator.innerHTML = '⚠️ İnternet bağlantısı yok';
            offlineIndicator.style.background = '#fbbf24';
            offlineIndicator.style.color = '#78350f';
            offlineIndicator.classList.add('show');
        });
    }

    // ============================================
    // PULL TO REFRESH
    // ============================================
    function initPullToRefresh() {
        if (!isMobile()) return;

        let startY = 0;
        let pullDistance = 0;
        const threshold = 80;

        const pullContainer = document.querySelector('.pull-to-refresh') || document.body;
        let indicator = document.querySelector('.pull-to-refresh-indicator');

        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'pull-to-refresh-indicator';
            indicator.innerHTML = '<span class="material-symbols-outlined spin">refresh</span>';
            pullContainer.insertBefore(indicator, pullContainer.firstChild);
        }

        pullContainer.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
            }
        });

        pullContainer.addEventListener('touchmove', (e) => {
            if (startY === 0) return;

            pullDistance = e.touches[0].clientY - startY;

            if (pullDistance > 0 && window.scrollY === 0) {
                pullContainer.classList.add('pulling');
                indicator.style.transform = `translateX(-50%) rotate(${pullDistance}deg)`;
            }
        });

        pullContainer.addEventListener('touchend', () => {
            if (pullDistance > threshold) {
                location.reload();
            }

            pullContainer.classList.remove('pulling');
            indicator.style.transform = 'translateX(-50%) rotate(0deg)';
            startY = 0;
            pullDistance = 0;
        });
    }

    // ============================================
    // TOUCH FEEDBACK
    // ============================================
    function initTouchFeedback() {
        if (!isMobile()) return;

        document.addEventListener('touchstart', (e) => {
            const target = e.target.closest('button, a, .clickable');
            if (target) {
                target.style.transform = 'scale(0.98)';
                target.style.opacity = '0.9';
            }
        });

        document.addEventListener('touchend', (e) => {
            const target = e.target.closest('button, a, .clickable');
            if (target) {
                setTimeout(() => {
                    target.style.transform = '';
                    target.style.opacity = '';
                }, 150);
            }
        });
    }

    // ============================================
    // VIEWPORT HEIGHT FIX (iOS)
    // ============================================
    function fixViewportHeight() {
        const setVh = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };

        setVh();
        window.addEventListener('resize', setVh);
        window.addEventListener('orientationchange', setVh);
    }

    // ============================================
    // PREVENT ZOOM ON DOUBLE TAP (iOS)
    // ============================================
    function preventDoubleTapZoom() {
        if (!isIOS()) return;

        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
    }

    // ============================================
    // LAZY LOADING IMAGES
    // ============================================
    function initLazyLoading() {
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

    // ============================================
    // SMOOTH SCROLL
    // ============================================
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#') return;

                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // ============================================
    // FORM VALIDATION FEEDBACK
    // ============================================
    function initFormFeedback() {
        const forms = document.querySelectorAll('form');

        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');

            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    if (this.checkValidity()) {
                        this.classList.remove('invalid');
                        this.classList.add('valid');
                    } else {
                        this.classList.remove('valid');
                        this.classList.add('invalid');
                    }
                });

                input.addEventListener('input', function() {
                    this.classList.remove('invalid', 'valid');
                });
            });
        });
    }

    // ============================================
    // LOADING STATES
    // ============================================
    window.showLoading = function(message = 'Yükleniyor...') {
        let loader = document.querySelector('.loading-overlay');
        
        if (!loader) {
            loader = document.createElement('div');
            loader.className = 'loading-overlay';
            loader.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <p class="loading-message">${message}</p>
                </div>
            `;
            document.body.appendChild(loader);
        }

        loader.querySelector('.loading-message').textContent = message;
        loader.style.display = 'flex';
    };

    window.hideLoading = function() {
        const loader = document.querySelector('.loading-overlay');
        if (loader) {
            loader.style.display = 'none';
        }
    };

    // ============================================
    // TOAST NOTIFICATIONS
    // ============================================
    window.showToast = function(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${getToastIcon(type)}</span>
                <span class="toast-message">${message}</span>
            </div>
        `;

        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 100);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    };

    function getToastIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    // ============================================
    // BACK BUTTON HANDLING
    // ============================================
    function initBackButton() {
        const backButtons = document.querySelectorAll('.back-button, [data-back]');
        
        backButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                if (window.history.length > 1) {
                    window.history.back();
                } else {
                    window.location.href = '/';
                }
            });
        });
    }

    // ============================================
    // RESPONSIVE TABLES
    // ============================================
    function initResponsiveTables() {
        const tables = document.querySelectorAll('table:not(.no-responsive)');

        tables.forEach(table => {
            if (!table.parentElement.classList.contains('responsive-table')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'responsive-table';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }

            // Add data-label attributes for mobile view
            const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
            
            table.querySelectorAll('tbody tr').forEach(row => {
                row.querySelectorAll('td').forEach((cell, index) => {
                    if (headers[index]) {
                        cell.setAttribute('data-label', headers[index]);
                    }
                });
            });
        });
    }

    // ============================================
    // NETWORK SPEED DETECTION
    // ============================================
    function detectNetworkSpeed() {
        if ('connection' in navigator) {
            const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
            
            if (connection) {
                const effectiveType = connection.effectiveType;
                console.log('Network speed:', effectiveType);

                // Adjust image quality based on connection
                if (effectiveType === 'slow-2g' || effectiveType === '2g') {
                    document.body.classList.add('slow-connection');
                    // Load lower quality images
                    document.querySelectorAll('img[data-src-low]').forEach(img => {
                        if (img.dataset.srcLow) {
                            img.dataset.src = img.dataset.srcLow;
                        }
                    });
                }
            }
        }
    }

    // ============================================
    // HAPTIC FEEDBACK (if available)
    // ============================================
    function triggerHaptic(type = 'light') {
        if ('vibrate' in navigator) {
            const patterns = {
                light: 10,
                medium: 20,
                heavy: 30,
                success: [10, 50, 10],
                error: [20, 100, 20, 100, 20]
            };
            navigator.vibrate(patterns[type] || patterns.light);
        }
    }

    window.triggerHaptic = triggerHaptic;

    // ============================================
    // INITIALIZE ALL
    // ============================================
    function init() {
        console.log('🚀 Mobile optimizations loaded');
        console.log('📱 Is Mobile:', isMobile());
        console.log('🍎 Is iOS:', isIOS());
        console.log('🤖 Is Android:', isAndroid());

        initMobileMenu();
        initOfflineDetection();
        initPullToRefresh();
        initTouchFeedback();
        fixViewportHeight();
        preventDoubleTapZoom();
        initLazyLoading();
        initSmoothScroll();
        initFormFeedback();
        initBackButton();
        initResponsiveTables();
        detectNetworkSpeed();

        // Add mobile class to body
        if (isMobile()) {
            document.body.classList.add('is-mobile');
        }
        if (isIOS()) {
            document.body.classList.add('is-ios');
        }
        if (isAndroid()) {
            document.body.classList.add('is-android');
        }
    }

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose utility functions globally
    window.MobileHelpers = {
        isMobile,
        isIOS,
        isAndroid,
        showToast,
        showLoading,
        hideLoading,
        triggerHaptic
    };

})();

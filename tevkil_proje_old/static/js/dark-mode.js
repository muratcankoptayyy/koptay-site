// ============================================
// DARK MODE TOGGLE
// ============================================

(function() {
    'use strict';

    const STORAGE_KEY = 'theme-preference';

    // Get initial theme
    function getTheme() {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            return stored;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    // Set theme
    function setTheme(theme) {
        localStorage.setItem(STORAGE_KEY, theme);
        document.documentElement.classList.remove('light', 'dark');
        document.documentElement.classList.add(theme);
        updateToggleButton(theme);
    }

    // Update toggle button
    function updateToggleButton(theme) {
        const toggleBtn = document.getElementById('theme-toggle');
        if (!toggleBtn) return;

        const icon = toggleBtn.querySelector('.material-symbols-outlined');
        if (icon) {
            icon.textContent = theme === 'dark' ? 'light_mode' : 'dark_mode';
        }
    }

    // Toggle theme
    function toggleTheme() {
        const current = getTheme();
        const next = current === 'dark' ? 'light' : 'dark';
        setTheme(next);

        // Haptic feedback if available
        if (window.triggerHaptic) {
            window.triggerHaptic('light');
        }

        // Show toast
        if (window.MobileHelpers) {
            const message = next === 'dark' ? '🌙 Karanlık mod açıldı' : '☀️ Aydınlık mod açıldı';
            window.MobileHelpers.showToast(message, 'info', 2000);
        }
    }

    // Initialize
    function init() {
        // Apply saved theme immediately
        setTheme(getTheme());

        // Add toggle button event listener
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', toggleTheme);
        }

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem(STORAGE_KEY)) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose toggle function globally
    window.toggleDarkMode = toggleTheme;

})();

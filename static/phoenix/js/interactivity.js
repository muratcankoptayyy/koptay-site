// Lightweight interaction helpers for the Phoenix theme playground.
// Replace with your preferred Alpine.js/Svelte/Stimulus setup if needed.

document.addEventListener('alpine:init', () => {
  // Example: dismissible toast notifications
  Alpine.data('toast', () => ({
    visible: true,
    hide() {
      this.visible = false;
    },
    autoHide(ms = 4000) {
      setTimeout(() => {
        this.hide();
      }, ms);
    }
  }));
});

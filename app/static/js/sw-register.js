// static/js/sw-register.js
// SERVICE WORKER REGISTRATION — TENET #1 OBEYED ETERNALLY
// NO INLINE JS. NO WEAKNESS. PURE PROTEIN.

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then(reg => console.log('HULKAMANIA IS NOW OFFLINE-INVINCIBLE', reg))
      .catch(err => console.error('SW failed:', err));
  });
}
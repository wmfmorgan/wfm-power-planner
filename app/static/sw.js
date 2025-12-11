// static/sw.js — BULLETPROOF, NO MORE REQUEST FAILED
const CACHE_NAME = 'wfm-power-planner-v9';

const STATIC_ASSETS = [
  '/static/css/tailwind.min.css',
  '/static/css/main.css',
  '/static/js/lib/sortable.min.js',
  '/static/js/goals_kanban.js',
  '/static/img/icon-192.png',
  '/static/img/icon-512.png',
  '/offline.html'
  // '/' REMOVED — NO MORE 404 FROM SUBPATH SCOPE
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
      .catch(err => console.error('SW install failed — bad path?', err))
  );
});

// activate + fetch stay the same — they're perfect
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  if (STATIC_ASSETS.includes(url.pathname) || url.pathname.startsWith('/static/')) {
    e.respondWith(
      caches.match(e.request).then(cached => cached || fetch(e.request))
    );
    return;
  }

  if (url.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
          return res;
        })
        .catch(() => caches.match('/offline.html'))
    );
    return;
  }

  e.respondWith(
    fetch(e.request)
      .catch(() => caches.match('/offline.html'))
  );
});
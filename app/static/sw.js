const CACHE_NAME = 'wfm-power-planner-v6';
const STATIC_ASSETS = [
  '/',
  '/static/css/main.css',
  '/static/js/lib/sortable.min.js',
  '/static/js/constants.js',
  '/static/js/goals_kanban.js',
  '/static/img/icon-192.png',
  '/static/img/icon-512.png',
  '/offline.html'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
    ))
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Static assets → cache first
  if (STATIC_ASSETS.some(asset => url.pathname === asset) ||
  url.pathname.startsWith('/static/'))
  {
    e.respondWith(
      caches.match(e.request).then(cached => cached || fetch(e.request))
    );
    return;
  }

  // API calls → network first, fallback to cache, then offline page
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(e.request)
        .then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
          return response;
        })
        .catch(() => caches.match(e.request))()
        .catch(() => caches.match('/offline.html'))
    );
    return;
  }

  // Everything else → network first, fallback to cached or offline
  e.respondWith(
    fetch(e.request)
      .catch(() => caches.match(e.request))
      .catch(() => caches.match('/offline.html'))
  );
});
const CACHE_NAME = 'fancy-store-v1';
const OFFLINE_URL = '/offline/';
const CACHED_ASSETS = [
  '/',
  'https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;900&family=Cairo:wght@400;600;700;900&display=swap',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(CACHED_ASSETS)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  if (e.request.url.includes('/admin/')) return;
  e.respondWith(
    fetch(e.request).then(r => {
      if (r.ok && r.type === 'basic') {
        const clone = r.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
      }
      return r;
    }).catch(() => caches.match(e.request).then(r => r || new Response('Offline', {status: 503})))
  );
});

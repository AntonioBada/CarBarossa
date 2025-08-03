self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open('carbarossa-cache').then(function(cache) {
      return cache.addAll([
        '/',
        '/static/style.css',
        '/static/script.js',
        // aggiungi le pagine che vuoi cache
      ]);
    })
  );
});

self.addEventListener('fetch', function(e) {
  e.respondWith(
    caches.match(e.request).then(function(response) {
      return response || fetch(e.request);
    })
  );
});

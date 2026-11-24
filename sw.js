// Service worker do Clausa: deixa o app abrir mesmo sem internet.
// Páginas: tenta a rede primeiro (sempre a versão mais nova) e cai no cache se estiver offline.
// Nunca guarda chamadas ao Supabase nem a outros sites: só arquivos do próprio Clausa.
const VERSAO = 'clausa-v2';
const BASE = ['./', 'index.html', 'app.html', 'entrar.html', 'privacidade.html', 'termos.html',
  'favicon.png', 'manifest.webmanifest', 'js/clausa-config.js', 'img/icones/icone-192.png', 'img/icones/icone-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSAO).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSAO).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;          // Supabase, fontes, CDN: direto na rede
  e.respondWith(
    fetch(req).then(res => {
      if (res.ok && res.type === 'basic') { const copia = res.clone(); caches.open(VERSAO).then(c => c.put(req, copia)); }
      return res;
    }).catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || caches.match('app.html')))
  );
});

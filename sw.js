// 앱 화면을 휴대폰에 저장해서 인터넷이 없어도 열리게 합니다. (데이터 저장은 Firebase가 따로 처리)
const CACHE = "jaego-v7";
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'firebase-config.js', 'icons/icon-192.png', 'icons/icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Firebase/구글 로그인·데이터 요청은 건드리지 않음
  if (url.hostname.includes('googleapis.com') && !url.hostname.startsWith('fonts')) return;
  if (url.hostname.includes('firebaseapp.com') || url.pathname.startsWith('/__/')) return;
  // 보안 확인(reCAPTCHA)은 항상 새로 받기
  if (url.pathname.includes('/recaptcha') || url.hostname === 'www.google.com') return;
  if (req.mode === 'navigate') { e.respondWith(fetch(req).catch(() => caches.match('index.html'))); return; }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => {
    if (res.ok && (url.origin === location.origin || url.hostname.endsWith('gstatic.com') || url.hostname === 'fonts.googleapis.com')) {
      const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy));
    }
    return res;
  })));
});

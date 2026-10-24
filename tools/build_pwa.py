"""Claude 버전(jaego.html)에서 플레이스토어용 public/index.html 을 만듭니다.
Builds public/index.html (PWA + Firebase) from the shared page source."""
import sys, re, pathlib

SRC = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(__file__).parent / 'public' / 'index.html'
FB = '12.18.0'  # Firebase JS SDK (gstatic CDN)

s = SRC.read_text(encoding='utf8')
style = s[s.index('<style>'):s.index('</style>') + 8]
body = s[s.index('</style>') + 8:s.index('<!--INIT-->')]
body = body[body.index('<div class="wrap">'):]

style = style.replace('</style>', '''.login{position:fixed;inset:0;z-index:40;background:var(--bg);display:flex;align-items:center;justify-content:center;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.login .box{max-width:380px;width:100%;display:flex;flex-direction:column;gap:14px;text-align:center;align-items:center}
.login img{width:96px;height:96px;border-radius:22px}
.login p{color:var(--muted);margin:0}
.gbtn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:12px;padding:13px;font-weight:700}
.who{font-size:12px;color:var(--muted);display:flex;gap:8px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.linkbtn{border:0;background:none;color:var(--accent);font-weight:600;padding:4px 0}
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
</style>''')

body = body.replace("Claude 사용을 허락해야 읽을 수 있어요. 다시 누르면 다시 물어봐요.", "읽기 기능을 쓸 수 없어요. 인터넷 연결을 확인해 주세요.")
body = body.replace("É preciso permitir o Claude para ler. Toque de novo para ver o pedido.", "A leitura não está disponível. Verifique a internet.")
body = body.replace('<!--PWA-USER-->', '<div class="who"><span id="whoName"></span><span><button class="linkbtn" type="button" id="setupBtn"></button> · <button class="linkbtn" type="button" id="logoutBtn"></button></span></div>')

login = '''<div class="login" id="login" hidden><div class="box">
  <img src="icons/icon-192.png" alt="">
  <h1 id="lgTitle"></h1><p id="lgSub"></p>
  <div id="setup" hidden style="display:flex;flex-direction:column;gap:10px;width:100%;text-align:left">
    <label class="field" for="cfgText"><span id="suCfgL"></span><textarea id="cfgText" rows="7" spellcheck="false" autocapitalize="off" style="font-family:ui-monospace,Menlo,monospace;font-size:12px"></textarea></label>
    <label class="field" for="cfgKey"><span id="suKeyL"></span><input id="cfgKey" autocapitalize="off" spellcheck="false"></label>
    <p class="err" id="suErr" hidden></p>
    <button class="btn full" type="button" id="suSave"></button>
    <button class="btn soft full" type="button" id="suLocal"></button>
    <p class="hint" id="suLocalHint"></p>
  </div>
  <button class="gbtn" type="button" id="loginBtn"><svg width="20" height="20" viewBox="0 0 48 48" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/><path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/><path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z"/><path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg><span id="loginTxt"></span></button>
  <p id="lgErr" style="color:var(--retail);font-size:13px" hidden></p>
  <div class="lang" role="group" aria-label="언어 / Idioma"><button type="button" data-lang="ko">한국어</button><button type="button" data-lang="pt">Português</button></div>
</div></div>
'''

module = '''<script src="firebase-config.js"></script>
<script type="module">
import { initializeApp } from "https://www.gstatic.com/firebasejs/__V__/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, signInWithRedirect, getRedirectResult, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/__V__/firebase-auth.js";
import { initializeFirestore, persistentLocalCache, persistentMultipleTabManager, collection, doc, setDoc, updateDoc, deleteDoc, onSnapshot, query, orderBy, limit } from "https://www.gstatic.com/firebasejs/__V__/firebase-firestore.js";
import { getAI, getGenerativeModel, GoogleAIBackend } from "https://www.gstatic.com/firebasejs/__V__/firebase-ai.js";
import { initializeAppCheck, ReCaptchaEnterpriseProvider } from "https://www.gstatic.com/firebasejs/__V__/firebase-app-check.js";

const $ = s => document.querySelector(s);
const LG = {
  ko: { title: '재고 정리판', sub: '구글 계정으로 로그인하면 내 상품 정보가 안전하게 저장돼요.', btn: 'Google로 로그인', out: '로그아웃', err: '로그인하지 못했어요. 다시 눌러주세요.',
    suSub: '처음 한 번만 설정해요. Firebase에서 복사한 설정을 붙여넣으세요.', suCfgL: 'Firebase 설정 (const firebaseConfig = { ... } 전체를 붙여넣기)', suKeyL: '보안 키 (reCAPTCHA 키 ID, 없으면 비워두기)',
    suSave: '저장하고 시작하기', suLocal: 'Firebase 없이 이 휴대폰에서만 써보기', suLocalHint: '설정 없이 바로 써볼 수 있어요. 내용은 이 휴대폰에만 저장되고, 영수증 AI 읽기는 Firebase 설정 후에 쓸 수 있어요.',
    suErr: '설정을 읽지 못했어요. apiKey, projectId, appId가 들어 있는지 확인해 주세요.', setup: '앱 설정', local: '이 휴대폰에만 저장 중' },
  pt: { title: 'Controle de Estoque', sub: 'Entre com sua conta Google para guardar seus produtos com segurança.', btn: 'Entrar com Google', out: 'Sair', err: 'Não foi possível entrar. Tente de novo.',
    suSub: 'Configure só uma vez. Cole a configuração copiada do Firebase.', suCfgL: 'Configuração do Firebase (cole todo o const firebaseConfig = { ... })', suKeyL: 'Chave de segurança (ID da chave reCAPTCHA, opcional)',
    suSave: 'Salvar e começar', suLocal: 'Usar só neste celular, sem Firebase', suLocalHint: 'Dá para testar sem configurar. Os dados ficam só neste celular e a leitura de notas por IA funciona depois de configurar o Firebase.',
    suErr: 'Não consegui ler a configuração. Confira se tem apiKey, projectId e appId.', setup: 'Configurar app', local: 'Salvando só neste celular' }
};
let user = null, localMode = false;
const ls = { get: k => { try { return localStorage.getItem(k) } catch (e) { return null } }, set: (k, v) => { try { localStorage.setItem(k, v) } catch (e) {} }, del: k => { try { localStorage.removeItem(k) } catch (e) {} } };
const lg = () => LG[document.documentElement.lang === 'ko' ? 'ko' : 'pt'];
App.onRender = () => { const L = lg();
  $('#lgTitle').textContent = L.title; $('#lgSub').textContent = L.sub; $('#loginTxt').textContent = L.btn;
  $('#logoutBtn').textContent = L.out; $('#whoName').textContent = user ? (user.email || '') : (localMode ? L.local : '');
  $('#setupBtn').textContent = L.setup; $('#logoutBtn').hidden = !user;
  $('#suCfgL').textContent = L.suCfgL; $('#suKeyL').textContent = L.suKeyL; $('#suSave').textContent = L.suSave; $('#suLocal').textContent = L.suLocal; $('#suLocalHint').textContent = L.suLocalHint;
  if (!$('#setup').hidden) $('#lgSub').textContent = L.suSub; };
App.render();

const valid = c => c && c.apiKey && !String(c.apiKey).startsWith('PASTE') && c.projectId && c.appId;
let cfg = window.FIREBASE_CONFIG || {};
if (!valid(cfg)) { try { cfg = JSON.parse(ls.get('fbcfg') || '{}'); } catch (e) { cfg = {}; } }
const loginBox = $('#login'), err = $('#lgErr');
$('#setupBtn').onclick = () => { ls.del('fbcfg'); ls.del('localMode'); location.reload(); };
function parseCfg(text) {
  const o = {}; const re = /["']?(\w+)["']?\s*:\s*["']([^"']+)["']/g; let m;
  while ((m = re.exec(text))) o[m[1]] = m[2];
  if (o.projectId && !o.authDomain) o.authDomain = o.projectId + '.firebaseapp.com';
  return o;
}
function localDb() {
  let store = {}; try { store = JSON.parse(ls.get('jaego-local') || '{}'); } catch (e) {}
  const subs = new Set(); const save = () => ls.set('jaego-local', JSON.stringify(store));
  const fire = () => subs.forEach(f => f()); let seq = 0;
  const kids = p => Object.keys(store).filter(k => k.startsWith(p + '/') && k.split('/').length === p.split('/').length + 1)
    .map(k => ({ id: k.split('/').pop(), data: () => JSON.parse(JSON.stringify(store[k])) }));
  const q = (p, ord, lim) => ({ onSnapshot(n) { const f = () => { let d = kids(p); if (ord) d.sort((a, b) => String(b.data()[ord]).localeCompare(String(a.data()[ord]))); if (lim) d = d.slice(0, lim); n({ docs: d }); }; subs.add(f); setTimeout(f, 0); return () => subs.delete(f); },
    limit(n) { return q(p, ord, n); } });
  const dref = path => ({ id: path.split('/').pop(),
    async set(d) { store[path] = JSON.parse(JSON.stringify(d)); save(); fire(); },
    async update(d) { if (!store[path]) throw new Error('missing'); Object.assign(store[path], JSON.parse(JSON.stringify(d))); save(); fire(); },
    async delete() { delete store[path]; save(); fire(); },
    onSnapshot(n) { const f = () => n({ exists: !!store[path], data: () => store[path] }); subs.add(f); setTimeout(f, 0); return () => subs.delete(f); } });
  return { collection: p => Object.assign(q(p), { orderBy: f => q(p, f), doc: id => dref(p + '/' + (id || ('l' + Date.now().toString(36) + (seq++)))) }), doc: dref };
}
if (!valid(cfg) && ls.get('localMode') === '1') {
  localMode = true; App.attach(localDb()); App.setState('ok');
} else if (!valid(cfg)) {
  loginBox.hidden = false; $('#loginBtn').hidden = true; $('#setup').hidden = false; App.render();
  $('#suSave').onclick = () => { const o = parseCfg($('#cfgText').value); const k = $('#cfgKey').value.trim(); if (k) o.appCheckSiteKey = k;
    if (!valid(o)) { $('#suErr').textContent = lg().suErr; $('#suErr').hidden = false; return; }
    ls.set('fbcfg', JSON.stringify(o)); ls.del('localMode'); location.reload(); };
  $('#suLocal').onclick = () => { ls.set('localMode', '1'); location.reload(); };
} else {
  const app = initializeApp(cfg);
  const siteKey = cfg.appCheckSiteKey;
  if (siteKey && !String(siteKey).startsWith('PASTE')) {
    try { initializeAppCheck(app, { provider: new ReCaptchaEnterpriseProvider(siteKey), isTokenAutoRefreshEnabled: true }); } catch (e) { console.warn('App Check', e); }
  }
  const fs = initializeFirestore(app, { localCache: persistentLocalCache({ tabManager: persistentMultipleTabManager() }) });
  const auth = getAuth(app);

  // --- storage adapter (same shape the shared page code expects) ---
  const w = p => navigator.onLine ? Promise.race([p, new Promise(r => setTimeout(r, 4000))]) : (p.catch(() => {}), Promise.resolve());
  const docRef = r => ({ id: r.id, set: d => w(setDoc(r, d)), update: d => w(updateDoc(r, d)), delete: () => w(deleteDoc(r)),
    onSnapshot: (n, e) => onSnapshot(r, s => n({ exists: s.exists(), data: () => s.data() }), e) });
  const qRef = q => ({ onSnapshot: (n, e) => onSnapshot(q, s => n({ docs: s.docs.map(d => ({ id: d.id, data: () => d.data() })) }), e) });
  const colRef = c => Object.assign(qRef(c), {
    doc: id => docRef(id ? doc(c, id) : doc(c)),
    orderBy: (f, dir) => Object.assign(qRef(query(c, orderBy(f, dir))), { limit: n => qRef(query(c, orderBy(f, dir), limit(n))) })
  });
  const makeDb = uid => ({ collection: p => colRef(collection(fs, `users/${uid}/${p}`)), doc: p => docRef(doc(fs, `users/${uid}/${p}`)) });

  // --- AI: Gemini through Firebase AI Logic ---
  try {
    const ai = getAI(app, { backend: new GoogleAIBackend() });
    const model = getGenerativeModel(ai, { model: cfg.aiModel || 'gemini-3.5-flash', generationConfig: { responseMimeType: 'application/json', temperature: 0.1 } });
    const b64 = b => new Promise((res, rej) => { const fr = new FileReader(); fr.onload = () => res(String(fr.result).split(',')[1]); fr.onerror = rej; fr.readAsDataURL(b); });
    App.setAi(async (prompt, imgs) => {
      const parts = [{ text: prompt }];
      for (const b of imgs || []) parts.push({ inlineData: { data: await b64(b), mimeType: b.type || 'image/jpeg' } });
      const r = await model.generateContent(parts);
      const txt = r.response.text().trim().replace(/^```(?:json)?\\s*/i, '').replace(/```$/, '');
      return JSON.parse(txt);
    }, { images: { maxCount: 4 } });
  } catch (e) { console.warn('AI', e); }

  // --- sign-in ---
  const provider = new GoogleAuthProvider();
  $('#loginBtn').onclick = async () => { err.hidden = true;
    try { await signInWithPopup(auth, provider); }
    catch (e) {
      if (['auth/popup-blocked', 'auth/operation-not-supported-in-this-environment', 'auth/cancelled-popup-request'].includes(e.code)) {
        try { await signInWithRedirect(auth, provider); } catch (e2) { err.textContent = lg().err; err.hidden = false; }
      } else if (e.code !== 'auth/popup-closed-by-user') { err.textContent = lg().err; err.hidden = false; }
    } };
  getRedirectResult(auth).catch(() => {});
  $('#logoutBtn').onclick = () => signOut(auth);
  onAuthStateChanged(auth, u => {
    user = u;
    if (!u) { App.detach(); loginBox.hidden = false; App.setState('wait'); return; }
    loginBox.hidden = true; App.attach(makeDb(u.uid)); App.setState(navigator.onLine ? 'wait' : 'off');
  });
  addEventListener('offline', () => user && App.setState('off'));
  addEventListener('online', () => user && App.setState('ok'));
}
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
</script>
'''.replace('__V__', FB)

headhtml = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>재고 정리판 · Controle de Estoque</title>
<meta name="description" content="옷 상품 코드·입고·판매·재고·수익 관리 / Controle de código, entrada, vendas, estoque e lucro de roupas">
<meta name="theme-color" content="#33408f">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/icon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Do+Hyeon&family=IBM+Plex+Sans+KR:wght@400;500;600;700&display=swap">
'''
out = headhtml + style + '\n</head>\n<body>\n' + body + login + module + '</body>\n</html>\n'
assert 'claude' not in out.lower(), 'artifact-only code leaked into PWA build'
OUT.write_text(out, encoding='utf8')
print('wrote', OUT, len(out), 'bytes')

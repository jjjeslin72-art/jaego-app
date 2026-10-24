# 재고 정리판 · Controle de Estoque

- `public/` 폴더 전체가 웹에 올릴 앱이에요. (Netlify Drop에 이 폴더를 끌어다 놓기)
- `public/firebase-config.js` 에 Firebase 설정을 붙여넣어야 작동해요.
- `firestore.rules` 내용은 Firebase 콘솔 > Firestore > 규칙(Rules)에 붙여넣으세요.
- 자세한 순서는 함께 드린 안내서를 보세요.

Tecnologia: HTML/JS puro (PWA) + Firebase JS SDK 12.18 (modular, gstatic): Auth (Google), Cloud Firestore (users/{uid}/styles, users/{uid}/moves, users/{uid}/config/rules), AI Logic (Gemini Developer API, leitura de notas por foto/voz/texto) e App Check (reCAPTCHA Enterprise). Voz: Web Speech API do Chrome. Pronto para empacotar no PWABuilder (Android / Google Play, TWA).

- `build_pwa.py`: gera public/index.html a partir do arquivo-fonte compartilhado (versão Claude). Não precisa rodar para publicar.

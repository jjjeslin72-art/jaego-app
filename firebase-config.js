// 재고 정리판 Firebase 설정 (프로젝트: jaego-juya)
// 이 값들은 앱 주소 같은 공개 정보예요. 비밀번호가 아니에요.
window.FIREBASE_CONFIG = {
  apiKey: "AIzaSyDgSQaipLF5papkmoGYX8CJ74KuZJTY_pc",
  authDomain: "jaego-juya.firebaseapp.com",
  projectId: "jaego-juya",
  storageBucket: "jaego-juya.firebasestorage.app",
  messagingSenderId: "610006126204",
  appId: "1:610006126204:web:43c1314729e7ac3a4203f9",

  // 영수증 읽기 보안 키 (reCAPTCHA Enterprise 사이트 키) — 3-2단계에서 넣어요
  appCheckSiteKey: "PASTE_RECAPTCHA_SITE_KEY",

  // 영수증을 읽는 AI 모델
  aiModel: "gemini-3.8-flash",
  // 관리 화면은 이 계정에만 보여요 / owner account (admin screen)
  adminUid: "EAyriVqcohQqHL1aKM2w9H5tDmH3",
  // 유료 문의 왓츠앱 번호(국가번호 포함, 예: 5511999999999)와 가격 안내
  contactWhatsApp: "",
  priceText: "월 R$ 29,90 / R$ 29,90 por mês"
};

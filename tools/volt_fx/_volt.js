// 전격술사 이펙트 공용: 플라즈마 팔레트와 몸 둘레 점 고르기.
// pixelfx(https://github.com/patch-gg/pixelfx, MIT)의 번개 도구(../lightning/_lib.js)를 그대로 씀 — tools/volt_fx_build.mjs가 이 폴더를 pixelfx의 src/fx/volt/로 복사해서 굽는다.
// 크기: 우리 캐릭터 키 약 88px (pixelfx 기본 캐릭터 38px의 2.3배) 기준으로 직접 그림. 1 = 게임 화면 1px, 1칸 = 120px.

/** 샘플 전기 색(하늘색 줄기·흰 심)에 남보라 테두리를 더한 플라즈마 램프 (어두움 → 밝음). */
export const PLASMA_V = ["#120c38", "#2c2390", "#2457c8", "#1fa0e6", "#4fdcf6", "#a4f6ff", "#e0feff", "#ffffff"];
/** 튀는 불티 (머리 → 꼬리). */
export const SPARK_V = ["#ffffff", "#d8fcff", "#7ff3ff", "#1ab8e6"];

/** 몸 둘레 타원 위의 점 (각도 a, 가운데 cx, cy, 반지름 rx, ry). */
export const onBody = (a, cx, cy, rx, ry) => [cx + Math.cos(a) * rx, cy + Math.sin(a) * ry];

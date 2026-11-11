// 검사 이펙트 공용: 달빛 강철 팔레트와 발도 참격 시간표.
// pixelfx(https://github.com/patch-gg/pixelfx, MIT)의 근접 도구(../melee/_lib.js: 초승달 참격 slash·through)를 씀 — tools/swordsman_fx_build.mjs가 이 폴더를 pixelfx의 src/fx/swordsman/로 복사해서 굽는다.
// 좌표: 기준점(0, 0) = 칼자루 (게임에서 검사 몸 앞, 발보다 14px 위), +x = 공격 방향. 1 = 게임 화면 1px. 기본 길이 L = 144 (검사 사거리)
import { clamp, rng } from "../../core/index.js";

/** 달빛 강철 램프 (어두움 → 밝음): 짙은 남색 테두리 → 푸른 강철 → 하늘빛 → 흰 날. 기존 검사 검기 색(#a5f3fc)이 6번째 칸 근처 */
export const MOON = ["#0b1430", "#1a2f6a", "#2458a8", "#3a94d6", "#7fd6f2", "#c6f4ff", "#ffffff"];
/** 튀는 불티 (머리 → 꼬리): 흰 → 하늘 → 푸른 강철 */
export const MOON_SPARK = ["#ffffff", "#c6f4ff", "#7fd6f2", "#3a94d6"];

/** 3단 시간표 (초, 30fps): 준비(칼자루 반짝 1칸) → 베기(2칸) → 맞는 순간 멈춤(2칸) → 회복(흐려짐 6칸) */
export const T = { glint: 0.033, sweep: 0.066, hold: 0.066, trail: 0.2 };
export const HIT = T.glint + T.sweep; // 참격이 끝까지 닿는 순간

/** 칼자루 반짝임 (준비): 작은 네 갈래 빛이 커졌다 줄어듦 */
export function hiltGlint(p, t, C, sparkle) {
  const g = t / (T.glint + 0.05);
  if (g >= 1) return;
  sparkle(p, 2, 0, 1 + 4 * Math.sin(Math.PI * g), C[6], C[4], 0.5);
  p.glow(2, 0, 8, C[4], 0.35 * (1 - g));
}

/** 맞은 자리에서 앞쪽으로 튀는 불티 (계산식이라 칸마다 같은 모양): 끝점 (x, y), 기준 방향 ang, 퍼짐 spread */
export function burst(p, t, t0, x, y, ang, spread, n, seed, S) {
  const u = t - t0;
  if (u < 0) return;
  const R = rng(seed, 11);
  for (let i = 0; i < n; i++) {
    const a = ang + R.range(-spread, spread), sp = R.range(110, 240), life = R.range(0.12, 0.28);
    if (u > life) continue;
    const k = 1 - u / life, d = sp * (u - u * u * 1.4), px = x + Math.cos(a) * d, py = y + Math.sin(a) * d;
    const ci = Math.min(S.length - 1, Math.floor((1 - k) * S.length));
    p.dot(px, py, S[ci], k);
    p.dot(px - Math.cos(a) * 1.5, py - Math.sin(a) * 1.5, S[Math.min(S.length - 1, ci + 1)], k * 0.6);
  }
}

/** 지나간 자리에 남는 점선 (흐려지며 사라짐) */
export function dotted(p, x0, x1, y, c, a, step = 2) {
  if (a <= 0.02) return;
  for (let x = x0; x <= x1; x += step) p.dot(x, y, c, a * (0.4 + 0.6 * clamp((x - x0) / Math.max(1, x1 - x0))));
}

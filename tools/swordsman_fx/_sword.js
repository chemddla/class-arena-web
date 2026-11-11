// 검사 이펙트 공용: 달빛 강철 팔레트와 발도 참격 시간표.
// pixelfx(https://github.com/patch-gg/pixelfx, MIT)의 근접 도구(../melee/_lib.js: 초승달 참격 slash·through)를 씀 — tools/swordsman_fx_build.mjs가 이 폴더를 pixelfx의 src/fx/swordsman/로 복사해서 굽는다.
// 좌표: 기준점(0, 0) = 칼자루 (게임에서 검사 몸 앞, 발보다 14px 위), +x = 공격 방향. 1 = 게임 화면 1px. 기본 길이 L = 144 (검사 사거리)
import { clamp, smooth, ease, rng } from "../../core/index.js";
import { smear, glowAlong, onSwing } from "../melee/_lib.js";

/** 흰 강철 램프 (어두움 → 밝음): 짙은 먹색 테두리 → 은회색 → 푸른 기가 살짝 도는 흰빛 → 흰 날 (2026-11-11 "흰색 계열"로 바꿈) */
export const MOON = ["#1a1f2b", "#3b4354", "#6e7a90", "#aab6c9", "#dde6f2", "#f3f8fd", "#ffffff"];
/** 튀는 불티 (머리 → 꼬리): 흰 → 은백 → 은회 */
export const MOON_SPARK = ["#ffffff", "#f3f8fd", "#dde6f2", "#aab6c9"];

/** 3단 시간표 (초, 40fps = 게임 틱): 준비(칼자루 반짝 1칸) → 베기(3칸, 빠르게 시작해 끝에서 감속) → 맞는 순간 멈춤(2칸) → 회복(부드럽게 흐려짐 9칸) */
export const FPS = 40;
export const T = { glint: 0.025, sweep: 0.075, hold: 0.05, trail: 0.22 };
export const HIT = T.glint + T.sweep; // 참격이 끝까지 닿는 순간
/** 빛의 속도: 빛줄기·초승달이 끝까지 닿는 데 걸리는 시간 (1칸). 꼬리가 흐려지는 시간표는 T 그대로 */
export const FLASH = 0.025;

/**
 * 빛의 속도로 지나간 자리: 1칸 만에 x0 → x1 전체가 흰 실선으로 번쩍 + 둘레 빛 번짐(두 겹) + 앞으로 내달리는 가는 속도선.
 * 처음 1칸은 가장 밝고 그 뒤 부드럽게 (반투명으로) 사라짐
 */
export function lightRush(p, t, t0, x0, x1, y, C, seed, life = 0.22) {
  const u = t - t0;
  if (u < 0 || u > life) return;
  const k = u < FLASH ? 1 : Math.pow(1 - (u - FLASH) / (life - FLASH), 1.6), L = x1 - x0;
  p.glowLine(x0, y, x1, y, 12, C[4], 0.3 * k); // 게임에선 투명 위 반투명 흰빛으로 들어가 회색 바닥에서 옅어지므로 넉넉히
  p.glowLine(x0, y, x1, y, 5, C[5], 0.7 * k);
  const core = u < FLASH * 2 ? 1 : k * 0.8;
  for (let x = x0; x <= x1; x += 1) p.blend(x, y, C[6], core * (0.3 + 0.7 * Math.pow((x - x0) / Math.max(1, L), 0.5)));
  const R = rng(seed, 21);
  for (let i = 0; i < 7; i++) { // 속도선: 실선 위아래로 2~11px 떨어져 앞으로 내달림
    const off = (R.chance(0.5) ? -1 : 1) * R.range(2, 11), len = R.range(16, 46), s0 = x0 + R.range(0, Math.max(1, L - len)), v = R.range(500, 900);
    const a0 = s0 + v * u, a1 = Math.min(x1 + 10, a0 + len), kk = k * R.range(0.35, 0.75);
    for (let x = a0; x <= a1; x += 1) p.blend(x, y + off, C[R.chance(0.5) ? 6 : 5], kk * Math.pow((x - a0) / Math.max(1, a1 - a0), 0.8));
  }
}

/** 맞은 자리 빛 번쩍임: 가로로 긴 빛줄(렌즈 플레어) + 짧은 세로 줄, 1칸 만에 켜지고 부드럽게 꺼짐 */
export function lensFlare(p, t, t0, x, y, C, len = 34, life = 0.18) {
  const u = t - t0;
  if (u < 0 || u > life) return;
  const k = u < FLASH ? 1 : Math.pow(1 - (u - FLASH) / (life - FLASH), 1.4), h = len * (0.6 + 0.4 * k);
  p.glowLine(x - h, y, x + h, y, 4, C[6], 0.9 * k);
  for (let dx = -h; dx <= h; dx += 1) p.blend(x + dx, y, C[6], k * (1 - Math.abs(dx) / h));
  p.glowLine(x, y - h * 0.35, x, y + h * 0.35, 2, C[6], 0.4 * k);
  p.glow(x, y, 12, C[5], 0.75 * k);
}

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

/** 지나간 자리에 남는 머리카락 같은 1px 자국 (앞쪽일수록 진하고, 통째로 부드럽게 흐려짐). 점 무늬(디더) 없이 반투명으로 */
export function dotted(p, x0, x1, y, c, a) {
  if (a <= 0.02) return;
  for (let x = x0; x <= x1; x += 1) p.blend(x, y, c, a * Math.pow(clamp((x - x0) / Math.max(1, x1 - x0)), 0.7));
}

/**
 * 매끄러운 초승달 참격: pixelfx melee/_lib.js의 slash와 같은 모양·시간표지만 꼬리를 점 무늬(디더)로 흐리지 않음.
 * 날은 꽉 찬 픽셀로 양끝까지 뾰족하게, 지나간 자국은 반투명 1px 선으로 부드럽게 사라짐. s = through()로 만든 칼질 + ramp
 */
export function sharpSlash(p, s, t) {
  const u = t - s.t0;
  if (u < 0) return;
  const R = s.ramp, n = R.length, life = s.sweep + s.hold + s.trail, hot = s.hot ?? 0;
  const head = ease.outExpo(clamp(u / s.sweep)), tail = smooth(s.sweep + s.hold, life, u), age = clamp(u / life);
  const U = s.span * head, Tt = s.span * tail, W = s.W * (1 - tail * 0.6);
  if (tail < 1 && U - Tt > 0.01) {
    smear(p, s, Tt, U, W, (uu, r, out) => {
      const v = (uu - Tt) / (U - Tt), w = W * Math.pow(Math.sin(Math.PI * v), 0.9);
      if (w < 0.45) return;
      const q = (s.R - r) / w;
      if (q < 0 || q > 1) return;
      const ci = q < hot * 0.8 && age < 0.45 ? 0 : Math.round(q * (n - 1) * 0.6 + age * 2.2 + (1 - v) * 0.5);
      out.c = R[n - 1 - clamp(ci, 0, n - 3)];
      out.a = 1;
    });
    glowAlong(p, s, s.R - W * 0.4, Tt, U, 3 + W, R[n - 2], (uu) => 0.35 * (1 - age) * ((uu - Tt) / (U - Tt)), 0, 0.3);
    glowAlong(p, s, s.R - W * 0.4, Tt, U, 9 + W, R[n - 3], (uu) => 0.22 * (1 - age) * ((uu - Tt) / (U - Tt)), 0, 0.25); // 바깥 빛 번짐 (빛의 속도 느낌)
  }
  const th = 0.55 * (1 - clamp((u - s.sweep - s.hold) / (s.trail + 0.15)));
  if (tail > 0.02 && th > 0.02) {
    const du = 0.6 / Math.max(4, s.R);
    for (let uu = 0; uu <= Tt; uu += du) {
      const [x, y] = onSwing(s, s.R - 0.5, uu);
      p.blend(x, y, R[n - 3], th * (0.3 + 0.7 * uu / s.span));
    }
  }
}

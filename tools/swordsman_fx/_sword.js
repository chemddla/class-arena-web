// 검사 이펙트 공용: 달빛 강철 팔레트와 발도 참격 시간표.
// pixelfx(https://github.com/patch-gg/pixelfx, MIT)의 근접 도구(../melee/_lib.js: 초승달 참격 slash·through)를 씀 — tools/swordsman_fx_build.mjs가 이 폴더를 pixelfx의 src/fx/swordsman/로 복사해서 굽는다.
// 좌표: 기준점(0, 0) = 칼자루 끝 (게임 화면에서 공격 준비 자세는 발에서 앞 19 · 위 30px, 낮게 앉은 자세는 앞 16 · 위 25px), +x = 목표 쪽.
//   1 = 게임 화면 1px. 기본 길이 L = 126 (사거리 144 - 칼자루까지 약 18): 게임은 칼자루 → 목표 가슴 거리에 맞춰 가로만 늘림
import { clamp, smooth, ease, rng, TAU } from "../../core/index.js";
import { glowAlong, onSwing, plane } from "../melee/_lib.js";

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
 * 빛의 날 한 점: 날 안쪽 깊이 q (0 = 바깥 가장자리 · 1 = 안쪽 가장자리), 가장자리까지 남은 px (edge, 반투명 경계용),
 * 날 밖으로 벗어난 px (out, 후광용)으로 색과 투명도를 정해 반투명으로 칠함. 흰 심 → 은백 → 은회로 식고, 경계는 1px에 걸쳐 부드럽게
 */
export function bladePx(p, x, y, C, q, edge, out, age, k) {
  const n = C.length;
  if (out > 0) { // 후광: 날 밖 6px까지 옅은 흰빛이 지수로 사라짐
    const h = 0.42 * k * (1 - age) * Math.exp(-out / 2.2);
    if (h > 0.01) p.blend(x, y, C[n - 2], h);
    return;
  }
  const cov = clamp(edge + 0.5);
  const c = q < 0.55 - age * 0.4 ? C[n - 1] : q < 0.85 - age * 0.3 ? C[n - 2] : C[n - 3 - (age > 0.6 ? 1 : 0)];
  p.blend(x, y, c, cov * k * (age > 0.55 ? 1 - (age - 0.55) / 0.45 * 0.6 : 1));
}

/**
 * 곧은 빛의 날: (x0, y0) → (x1, y1), 굵기 W (반폭). prof(v) = 길이 방향 굵기 비율 (0..1), 기본은 앞쪽이 굵고 양끝 뾰족.
 * 반투명 경계 + 흰 심 + 후광 (bladePx와 같은 칠). age = 식은 정도, k = 밝기
 */
export function lightBeam(p, x0, y0, x1, y1, W, C, age, k, prof = (v) => Math.pow(Math.sin(Math.PI * Math.pow(v, 0.55)), 1.1)) {
  const dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L, M = W + 7;
  for (let y = Math.floor(Math.min(y0, y1) - M); y <= Math.max(y0, y1) + M; y++)
    for (let x = Math.floor(Math.min(x0, x1) - M); x <= Math.max(x0, x1) + M; x++) {
      const px = x + 0.5 - x0, py = y + 0.5 - y0, along = px * ux + py * uy, v = along / L;
      if (v < 0 || v > 1) continue;
      const d = Math.abs(-px * uy + py * ux), w = W * prof(v);
      if (w < 0.25) continue;
      const edge = w - d;
      if (edge >= -0.5) bladePx(p, x, y, C, d / w, edge, 0, age, k);
      else bladePx(p, x, y, C, 0, 0, -edge, age, k * Math.min(1, prof(v) * 1.5));
    }
}

/**
 * 광격 (빛의 초승달): pixelfx melee/_lib.js의 slash와 같은 모양·시간표로 휘두르되, 날을 반투명 빛으로 칠함.
 * 날 가장자리는 1px에 걸쳐 부드럽게(계단·점 무늬 없이), 가운데는 흰 심, 바깥으로 후광이 번짐. 지나간 자국은 반투명 1px 호로 사라짐.
 * s = through()로 만든 칼질 + ramp
 */
export function sharpSlash(p, s, t) {
  const u = t - s.t0;
  if (u < 0) return;
  const R = s.ramp, n = R.length, life = s.sweep + s.hold + s.trail;
  const head = ease.outExpo(clamp(u / s.sweep)), tail = smooth(s.sweep + s.hold, life, u), age = clamp(u / life);
  const U = s.span * head, Tt = s.span * tail, W = s.W * (1 - tail * 0.55);
  if (tail < 1 && U - Tt > 0.01) {
    const B = s.R + 8;
    for (let y = Math.floor(s.cy - B); y <= s.cy + B; y++)
      for (let x = Math.floor(s.cx - B); x <= s.cx + B; x++) {
        const [r, a] = plane(s, x + 0.5, y + 0.5);
        if (r > s.R + 7 || r < s.R - W - 7) continue;
        let uu = (s.dir * (a - s.a0)) % TAU;
        if (uu < 0) uu += TAU;
        if (uu < Tt || uu > U) continue;
        const v = (uu - Tt) / (U - Tt), w = W * Math.pow(Math.sin(Math.PI * v), 0.85); // 양끝 뾰족
        const inner = s.R - w, edge = Math.min(s.R - r, r - inner); // 가장자리까지 남은 거리 (밖이면 음수)
        if (w < 0.3) continue;
        if (edge >= -0.5) bladePx(p, x, y, R, (s.R - r) / w, edge, 0, age, Math.min(1, v * 6));
        else bladePx(p, x, y, R, 0, 0, -edge, age, Math.min(1, v * 3) * Math.sin(Math.PI * v));
      }
    glowAlong(p, s, s.R - W * 0.4, Tt, U, 9 + W, R[R.length - 3], (uu) => 0.18 * (1 - age) * ((uu - Tt) / (U - Tt)), 0, 0.25); // 넓은 빛 번짐
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

// 기공사 일반 공격 시안 공용: 손에 기 모으기, 맞는 순간 터짐. 시간 값은 시안마다 같게 맞춤
import { P, TAU, WHITE, flare, sparkle, ease } from "../../core/index.js";

export const GOLD = ["#1e1206", "#4a2c08", "#86520c", "#c48412", "#f0b424", "#ffe066", "#fff6c4", "#ffffff"];
export const H = 50, X1 = 170;            // 손 높이(발 위) · 맞는 자리(손에서 앞으로)
export const CHARGE = 0.22, FLY = 0.3, HIT = CHARGE + FLY;
export const base = { size: [236, 112], origin: [26, 100], loop: false, fps: 30, bg: "dark" };

// 기 모으기: 둘레에서 손으로 빨려드는 줄기 (STREAK)
export function gather(ps, R, C, t, dt, rate = 1) {
  if (t >= CHARGE) return;
  const n = rate * dt * 90;
  for (let i = 0; i < n; i++) if (R.chance(Math.min(1, n - i))) {
    const a = R.range(0, TAU), d = R.range(14, 30), sp = d / 0.16;
    ps.spawn(P.STREAK, Math.cos(a) * d, -H + Math.sin(a) * d * 0.8, -Math.cos(a) * sp, -Math.sin(a) * sp * 0.8, 0.16, R.pick([C[5], C[6], WHITE]), 0.9);
  }
}

// 맞는 순간: 빛 + 불꽃 튐 + 별빛 (s로 크기)
export function burst(ps, lights, R, C, x, y, s = 1) {
  lights.add(x, y, 46 * s, C[4], 0.95, 0.5);
  lights.add(x, y, 18 * s, WHITE, 0.9, 0.12);
  for (let i = 0; i < 16 * s; i++) {
    const a = R.range(0, TAU), sp = R.range(110, 230) * s;
    ps.spawn(P.SPARK, x, y, Math.cos(a) * sp, Math.sin(a) * sp - 40, R.range(0.12, 0.3));
  }
  for (let i = 0; i < 12 * s; i++) {
    const a = R.range(0, TAU), d = R.range(3, 16) * s;
    ps.spawn(P.STAR, x + Math.cos(a) * d, y + Math.sin(a) * d * 0.8, 0, -R.range(4, 12), R.range(0.35, 0.8), R.pick([C[6], WHITE, C[5]]), R.range(0.8, 2.2), R.range(0.03, 0.3));
  }
}

// 맞는 순간 그림: 별 모양 빛 + 퍼지는 링
export function hitFlash(p, C, q, x, y, s = 1) {
  if (q < 0 || q >= 0.45) return;
  const e = q / 0.45;
  if (e < 0.5) flare(p, x, y, 22 * s * Math.pow(1 - e * 2, 1.2) + 2, 1 - e * 2, C);
  if (e < 0.12) p.circle(x, y, 6 * s * (1 - e / 0.12) + 1, WHITE);
  p.ring(x, y, 4 + 18 * s * ease.outCubic(e), Math.max(1, 2.5 * (1 - e)), e < 0.3 ? C[6] : C[5], Math.min(1, (1 - e) * 1.5));
  if (e < 0.4) sparkle(p, x, y, 7 * s * (1 - e / 0.4), C[6], C[4], 0.6 * (1 - e / 0.4));
}

// 손 앞의 모이는 구슬 (k 0..1)
export function handOrb(p, C, k, r = 4) {
  const rr = 1 + r * ease.outBack(Math.min(1, k));
  p.circle(0, -H, rr + 1.2, C[4]);
  p.circle(0, -H, rr + 0.2, C[5]);
  p.circle(-0.4, -H - 0.4, rr * 0.5, WHITE);
  p.glow(0, -H, 16, C[4], 0.55 * k);
}

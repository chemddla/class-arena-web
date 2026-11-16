// 기공사 이펙트 공용 2판 (반짝임 없음): 별빛·번쩍·불꽃 가루 대신 일렁이는 반투명 기운, 공기를 미는 압력 고리, 먼지
// 사용자 지시 (2026-11-16): 기공이라 반짝반짝 빛나는 이펙트는 안 어울림
import { P, TAU, ease, clamp, noise2 } from "../../core/index.js";

// 금빛 기운 램프: 흰색 없이 크림색까지만 (가장 밝은 칸도 반짝이지 않게)
export const QI_GOLD = ["#24160a", "#4e3210", "#8a5a16", "#c48a24", "#e8b23e", "#f6d27a", "#fbe8b4"];
export const H = 50, X1 = 170, CHARGE = 0.22, FLY = 0.3, HIT = CHARGE + FLY;
export const base = { size: [236, 112], origin: [26, 100], loop: false, fps: 30, bg: "dark" };

// 기 모으기: 손 둘레의 옅은 기운이 천천히 손으로 말려 듦 (안개 입자)
export function qiGather(ps, R, C, t, dt, rate = 1) {
  if (t >= CHARGE) return;
  const n = rate * dt * 50;
  for (let i = 0; i < n; i++) if (R.chance(Math.min(1, n - i))) {
    const a = R.range(0, TAU), d = R.range(10, 20), sp = d / 0.22;
    ps.spawn(P.VAPOUR, Math.cos(a) * d, -H + Math.sin(a) * d * 0.8, -Math.cos(a) * sp - Math.sin(a) * sp * 0.6, -Math.sin(a) * sp * 0.8 + Math.cos(a) * sp * 0.5, 0.22, R.pick([C[4], C[5]]), R.range(1.5, 2.6));
  }
}

// 일렁이는 기운 덩어리: 가장자리가 잡음으로 흔들리는 반투명 원 여러 겹 + 진한 심 (흰 섬광 없음)
export function qiBall(p, C, x, y, r, t, k = 1) {
  p.glow(x, y, r * 2.4, C[3], 0.18 * k);
  p.shade(x - r * 1.5, y - r * 1.5, x + r * 1.5, y + r * 1.5, (px, py, out) => {
    const dx = px - x, dy = py - y, a = Math.atan2(dy, dx), d = Math.hypot(dx, dy);
    const wob = 1 + 0.16 * noise2(Math.cos(a) * 1.6 + t * 5, Math.sin(a) * 1.6 - t * 4);   // noise2는 -1..1
    const e = d / (r * wob);
    if (e > 1.35) return 0;
    if (e > 1) { out.a = 0.35 * k * (1.35 - e) / 0.35; return C[3]; }   // 바깥 옅은 기운 막
    out.a = k;
    return e > 0.8 ? C[4] : e > 0.45 ? C[5] : C[6];
  });
}

// 압력 고리: 두께가 얇아지며 퍼지는 반투명 고리 (sy로 납작하게)
export function pressureRing(p, C, x, y, e, R0, R1, sy = 1, k = 1) {
  if (e < 0 || e >= 1) return;
  const r = R0 + (R1 - R0) * ease.outCubic(e), w = Math.max(1, 3.2 * (1 - e)), a = (1 - e) * 0.8 * k;
  for (let g = 0; g < TAU; g += 0.6 / Math.max(r, 4)) {
    for (let s = 0; s < w; s += 0.5) p.blend(x + Math.cos(g) * (r - s), y + Math.sin(g) * (r - s) * sy, s < 1 ? C[6] : C[4], a * (s < 1 ? 1 : 0.6));
  }
}

// 맞는 순간: 기운이 사방으로 밀려나는 안개 + 바닥 먼지 (불꽃·별 없음)
export function qiImpact(ps, lights, R, C, x, y, s = 1) {
  lights.add(x, y, 36 * s, C[4], 0.55, 0.35);
  for (let i = 0; i < 18 * s; i++) {
    const a = R.range(0, TAU), sp = R.range(50, 120) * s;
    ps.spawn(P.VAPOUR, x, y, Math.cos(a) * sp, Math.sin(a) * sp * 0.8, R.range(0.3, 0.55), R.pick([C[4], C[5], C[6]]), R.range(2, 3.5) * s);
  }
  for (let i = 0; i < 8 * s; i++) {   // 바닥에 이는 먼지 (맞는 자리 아래)
    const dir = i % 2 ? 1 : -1;
    ps.spawn(P.DUST, x + dir * R.range(0, 6), -1, dir * R.range(30, 70), -R.range(4, 14), R.range(0.35, 0.6), "#a08a6a", R.range(2, 3.5));
  }
}

// 맞는 순간 그림: 압력 고리 두 겹 (세로·가로)
export function qiHitRings(p, C, q, x, y, s = 1) {
  pressureRing(p, C, x, y, q / 0.35, 4 * s, 22 * s, 1, 1);
  pressureRing(p, C, x, y, (q - 0.06) / 0.4, 3 * s, 30 * s, 0.45, 0.8);
  pressureRing(p, C, x, 0, (q - 0.02) / 0.45, 4 * s, 26 * s, 0.18, 0.7);   // 바닥 고리
  void clamp;
}

// 실타래 기구슬(일반 공격 J) 그리기를 기공포 시안들이 같이 쓰도록 묶은 것 (반짝임·먼지·바닥 고리 없음)
import { TAU, clamp, ease } from "../../core/index.js";
import { pressureRing } from "./_qi.js";

export function makeLoops(n) {
  const L = [];
  for (let i = 0; i < n; i++) L.push([(i * 2.39) % Math.PI, (i * 1.37) % TAU, (i % 2 ? 1 : -1) * (3 + (i % 4))]);
  return L;
}

// 기운 실 (grow > 1: 비슷한 크기의 고리로 풀려 커짐 ±6%, 군데군데 끊김 · grow < 1은 쓰지 않음)
export function jThreads(p, C, loops, x, y, r, t, k, sx = 1, sy = 1, grow = 1) {
  const open = grow > 1;
  loops.forEach(([tilt, yaw, sp], i) => {
    const ct = Math.cos(tilt) * 0.999, st = Math.sin(tilt), cy = Math.cos(yaw + t * 1.5), sy2 = Math.sin(yaw + t * 1.5);
    const rr = open ? r * 0.9 * grow * (0.94 + 0.12 * ((i * 0.61) % 1)) : r * (0.5 + 0.45 * ((i * 0.37) % 1));
    const gap = open ? 0.08 + 0.3 * clamp((grow - 1) / 5) : 0;
    for (let a = 0; a < TAU; a += 0.6 / rr) {
      const u = a + t * sp, px = Math.cos(u) * rr, py = Math.sin(u) * rr * ct, pz = Math.sin(u) * rr * st;
      const X = px * cy - pz * sy2, Z = px * sy2 + pz * cy;
      if (Z <= 0 || (gap && ((a * 3.1 + i) % 1) < gap)) continue;
      if (open) { p.blend(x + X * sx, y + py * sy, C[6], k); p.blend(x + X * sx, y + py * sy + 1, C[4], k * 0.6); }
      else if (k >= 0.99) p.px(x + X * sx, y + py * sy, i % 3 ? C[5] : C[6]);
      else p.blend(x + X * sx, y + py * sy, i % 3 ? C[5] : C[6], k);
    }
  });
}

// 구슬 (sx·sy 눌림)
export function jOrb(p, C, loops, x, y, r, t, k = 1, sx = 1, sy = 1) {
  p.glow(x, y, r * 2.4, C[3], 0.16 * k);
  p.disc(x, y, (r + 2.5) * Math.max(sx, sy), C[3], 0.3 * k);
  p.shade(x - r * sx - 1, y - r * sy - 1, x + r * sx + 1, y + r * sy + 1, (px, py, out) => {
    const dx = (px - x) / sx, dy = (py - y) / sy, d = Math.hypot(dx, dy) / r;
    if (d > 1.02) return 0;
    out.a = k;
    const lit = clamp(1 - d * 0.95 - (dx + dy) / r * 0.1);
    return d > 0.9 ? C[4] : lit > 0.7 ? C[4] : lit > 0.35 ? C[3] : C[2];
  });
  jThreads(p, C, loops, x, y, r, t, k, sx, sy, 1);
}

// 사방으로 뻗는 선 (e 0..1)
const BURST = [];
for (let i = 0; i < 16; i++) BURST.push([(i / 16) * TAU + ((i * 0.37) % 1 - 0.5) * 0.25, 1.6 + ((i * 0.53) % 1) * 1.6, 0.7 + ((i * 0.71) % 1) * 0.5]);
export function jLines(p, C, x, y, R, e, HS, n = 16) {
  const k = Math.pow(1 - e, 1.2);
  BURST.slice(0, n).forEach(([a0, len, sp]) => {
    const head = R * (1 + 4.2 * HS * sp * ease.outCubic(e)), tail = Math.max(R * 0.8, head - R * len * HS * (1 - e * 0.5));
    for (let d = tail; d <= head; d += 0.5) {
      const f = (d - tail) / Math.max(1, head - tail), cx = x + Math.cos(a0) * d, cy = y + Math.sin(a0) * d * 0.9;
      p.blend(cx, cy, f > 0.7 ? C[6] : f > 0.3 ? C[5] : C[4], k * (0.35 + 0.65 * f));
    }
  });
}

// 일반 공격과 같은 터짐 (b: 터진 뒤 초, R: 구슬 반지름, HS: 크기)
// 터질 때 구슬의 금빛 바탕도 실과 함께 부풀며 옅어짐 (구슬 몸통과 같은 색 단계: 가장자리 밝고 속은 진함, 진짜 반투명)
export function jBody(p, C, x, y, R, e) {
  if (e < 0 || e >= 1) return;
  const Rs = R * (1 + 2.6 * ease.outCubic(e)), fade = Math.pow(1 - e, 1.1);
  const x0 = Math.floor(x - Rs - 1), x1 = Math.ceil(x + Rs + 1), y0 = Math.floor(y - Rs - 1), y1 = Math.ceil(y + Rs + 1);
  for (let py = y0; py <= y1; py++) for (let px = x0; px <= x1; px++) {
    const dx = px + 0.5 - x, dy = py + 0.5 - y, d = Math.hypot(dx, dy) / Rs;
    if (d > 1) continue;
    const lit = clamp(1 - d * 0.95 - (dx + dy) / Rs * 0.1);
    // 처음엔 구슬 몸통 색 그대로, 부풀기 시작하면 밝은 금빛 단계로 (진한 단계가 반투명으로 남으면 탁한 갈색이 됨)
    const c = e < 0.08 ? (d > 0.88 ? C[5] : lit > 0.7 ? C[4] : lit > 0.35 ? C[3] : C[2]) : (d > 0.88 ? C[5] : C[4]);   // 속은 진한 금빛(채도 높은 단)이라 반투명이어도 노랗게 보임
    const a = fade * (e < 0.08 ? 1 : 0.62 + 0.3 * d * d);   // 노란 바탕이 또렷이 남다가 함께 옅어짐 (너무 옅으면 어두운 바탕에 섞여 회갈색이 됨)
    p.blend(px + 0.5, py + 0.5, c, a);
  }
}

export function jBurst(p, C, loops, x, y, R, t, b, HS) {
  if (b < 0) return;
  jBody(p, C, x, y, R, b / 0.34);
  if (b < 0.42) { const e = b / 0.42; jThreads(p, C, loops, x, y, R, t * 0.4 + 2, Math.pow(1 - e, 1.4), 1, 1, 1 + 4 * HS * ease.outCubic(e)); }
  if (b >= 0.06 && b < 0.46) { const e = (b - 0.06) / 0.4; jThreads(p, C, loops, x, y, R, t * 0.4 + 5.3, Math.pow(1 - e, 1.6) * 0.8, 1, 1, 1 + 4.4 * HS * ease.outCubic(e)); }
  if (b < 0.3) jLines(p, C, x, y, R, b / 0.3, HS);
  const S = R / 8;
  pressureRing(p, C, x, y, b / 0.32, 5 * S, 36 * HS * S, 1, 1);
  pressureRing(p, C, x, y, (b - 0.04) / 0.4, 4 * S, 39 * HS * S, 0.4, 0.75);
  pressureRing(p, C, x, y, (b - 0.09) / 0.38, 4 * S, 37 * HS * S, 0.7, 0.6);
}

// 모으기: 큰 고리로 떠 있던 기운 실이 가운데로 감겨 들어옴 (풀림을 거꾸로, e 0..1)
export function jGatherIn(p, C, loops, x, y, R, t, e) {
  const g = 1 + 2.2 * Math.pow(1 - e, 2);   // 처음 고리 반지름 ≈ 구슬의 2.9배 (캐릭터를 너무 가리지 않게)
  jThreads(p, C, loops, x, y, R, t * 0.6, 0.25 + 0.75 * e, 1, 1, g > 1.02 ? g : 1.02);
}

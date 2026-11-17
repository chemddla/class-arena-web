// 기공사 시크릿 레어 전용 이펙트 공용 (청기 淸氣): 실타래 대신 맑게 응축된 순수한 기
//   맺힘(둘레의 기 알갱이가 휘어 들며 빨려 듦) → 응축(한가운데가 가장 밝고 바깥으로 옅어지는 기 덩어리, 심으로 감겨 드는 나선 기류,
//   테두리 선 없이 위로 타오르는 기운 불꽃) → 풀림(압력 파동 · 떠올라 흩어지는 기 알갱이 · 낮은 기 안개)
// 물처럼 보이는 것은 뺌 (2026-11-17 사용자: "테두리에 선이 흐물거리니까 물방울같아. 기의 느낌을 담아줘")
//   - 딱딱한 테두리 선·윤기(반사)·떨어지는 방울·물결 무늬 없음. 반짝임·별빛도 없음 (2026-11-16 지시 유지)
// 좌표: 발 = (0, 0), 앞 = +x, 위 = -y. 땅 = y 0
import { TAU, clamp, hex } from "../../core/index.js";

// 청기 램프: 깊은 남빛 → 하늘 → 물빛 → 얼음빛 → 흰빛에 가까운 하늘 (흰색은 심 한가운데만)
export const QI_SKY = ["#08202c", "#0e3e56", "#16709a", "#2ca8d8", "#62d4f2", "#a8eefa", "#e4fbff"];
export const MINT = hex("#a4f4da"), CORE = hex("#ffffff");
// 게임 그림 px 손 자리 (qigong_sr1 칸 기준 어림값, 발에서)
export const HAND = { charge: [14, -50], punch: [40, -53], cannon: [40, -48], throw: [38, -50], chest: [6, -56], wave: [36, -48] };

export const lerp = (a, b, u) => a + (b - a) * u;
export const eo = u => 1 - Math.pow(1 - clamp(u), 3), ei = u => Math.pow(clamp(u), 2.2);
export const ss = (a, b, x) => { const u = clamp((x - a) / (b - a)); return u * u * (3 - 2 * u); };
export const outBack = u => { u = clamp(u); const k = 1.7; return 1 + (k + 1) * Math.pow(u - 1, 3) + k * Math.pow(u - 1, 2); };
export const wob = (a, t) => Math.sin(a * 3 + t * 2.1) * .5 + Math.sin(a * 5 - t * 3.3) * .3 + Math.sin(a * 2 - t * 1.3) * .2;

// 기운 불꽃 가장자리: 각도 an(화면 atan2, 위 = -π/2)에서 혀 모양 기운이 얼마나 뻗는지 0..~1.3
//   위에서 잰 각 u로 위상을 잡아 양옆 혀가 위로 타고 오름 · 위쪽일수록 높게 (up)
export function tongue(an, t, seed = 0) {
  const u = Math.abs(((an + Math.PI / 2) % TAU + TAU + Math.PI) % TAU - Math.PI);   // 위 0 .. 아래 π
  const tg = Math.max(0, Math.sin(u * 7 + t * 10 + seed) * 0.6 + Math.sin(u * 12 + t * 15 + 1.3 + seed) * 0.4 + Math.sin(an * 3 - t * 4) * 0.25);
  return { tg, up: 1 - u / Math.PI };
}

// 압력 파동 (sy < 0.6: 땅에 누운 파동, 뒤 반은 옅게): 선이 아니라 번진 기운 띠
//   앞머리 쪽이 가장 짙고 바깥으로는 빠르게, 안쪽으로는 길게 옅어짐 (2026-11-17 사용자: "선의 느낌을 최대한 없애")
export function ring(p, C, x, y, r, sy, a, w = 1.5, sx = 1) {
  if (a <= 0.01 || r < 0.6) return;
  const flat = sy < 0.6, W = Math.max(2.5, w * 2) / Math.sqrt(Math.min(sx, sy)), tail = Math.max(W * 1.5, r * (flat ? 0.45 : 0.3));
  soft(p, x - (r + W) * sx - 1, y - (r + W) * sy - 1, x + (r + W) * sx + 1, y + (r + W) * sy + 1, (px, py, out) => {
    const e = Math.hypot((px - x) / sx, (py - y) / sy) - r;
    let b = e > 0 ? 1 - e / W : 1 + e / tail;
    if (b <= 0) return;
    b = b * b * (3 - 2 * b);
    out.a = a * (flat && py < y ? 0.4 : 1) * 0.5 * b; return b > 0.75 ? C[5] : C[4];
  });
}

// 응축된 기 덩어리: 심이 가장 밝고 바깥으로 옅어짐 · 심으로 감겨 드는 나선 기류 · 테두리 선 없이 위로 타오르는 기운 불꽃
export function orb(p, C, x, y, r, t, k = 1, sx = 1, sy = 1) {
  if (r < 0.6 || k <= 0) return;
  p.glow(x, y, r * 2.6, C[3], 0.26 * k);
  const R = r * 1.65;
  soft(p, x - R * sx - 1, y - R * sy - 1, x + R * sx + 1, y + R * sy + 1, (px, py, out) => {
    const dx = (px - x) / sx, dy = (py - y) / sy, an = Math.atan2(dy, dx), d = Math.hypot(dx, dy) / r;
    const { tg, up } = tongue(an, t), E = 1.06 + tg * 0.28 + up * up * 0.25 * (0.5 + tg);
    if (d > E) return;
    if (d > 1) { const f = (d - 1) / (E - 1); out.a = k * 0.55 * (1 - f) * (1 - f); out.k = 0.1 * k * (1 - f); return f < 0.4 ? C[4] : C[3]; }   // 기운 불꽃
    const core = (r > 12 ? 0.24 : 0.36) * (1 + 0.08 * Math.sin(t * 7));
    if (d < core) { out.a = k; out.k = 0.4 * k * (1 - d / core); return d < core * 0.5 ? CORE : C[6]; }   // 뭉친 심
    // 심으로 감겨 드는 나선 기류: 경계 없는 밝기 너울로만 (선 없음)
    const arm = Math.max(0, Math.sin(an * 3 + Math.log(d + 0.06) * 7 + t * 8)) ** 2 * 0.22;
    const b = 1 - d + arm;                                                               // 안에서 밖으로 옅어짐
    out.a = k * (0.95 - 0.3 * d);
    return b > 0.62 ? C[6] : b > 0.36 ? C[5] : b > 0.14 ? C[4] : C[3];
  });
  const n = Math.min(6, 2 + (r / 6 | 0));                                                // 위로 떠올라 흩어지는 기 알갱이
  for (let i = 0; i < n; i++) {
    const q = (t * 1.3 + i / n) % 1, a0 = -Math.PI / 2 + Math.sin(i * 2.4) * 1.1;
    p.blend(x + Math.cos(a0) * r * (1 + q * 0.5) * sx, y + Math.sin(a0) * r * (1 + q * 0.4) * sy - q * r * 0.5, C[5], 0.75 * k * (1 - q));
  }
}

// 날아가는 기 덩어리 뒤 꼬리: 가운데가 밝고 가장자리는 너울대며 옅어짐 (선 없음)
export function tail(p, C, x, y, r, ang, len, a = 1) {
  if (len < 2) return;
  const ca = Math.cos(ang), sa = Math.sin(ang), L = len + r, ph = (x + y) * 0.45;
  soft(p, Math.min(x, x - ca * L) - r - 2, Math.min(y, y - sa * L) - r - 2, Math.max(x, x - ca * L) + r + 2, Math.max(y, y - sa * L) + r + 2, (px, py, out) => {
    const dx = px - x, dy = py - y, s = -(dx * ca + dy * sa), nn = -dx * sa + dy * ca, n = Math.abs(nn);
    if (s < 0 || s > len) return;
    const f = s / len, w = r * 1.05 * Math.pow(1 - f, 0.7) * (1 + 0.3 * Math.sin(s * 0.8 + ph + Math.sign(nn) * 1.7));
    if (n > w) return;
    const e = n / Math.max(w, 0.5);
    out.a = a * Math.pow(1 - f, 1.2) * (0.85 - 0.6 * e);
    return e < 0.3 && f < 0.4 ? C[6] : e < 0.6 ? C[5] : C[4];
  });
}

// 터지는 기: 선 없이 부드러운 압력 띠가 부풀며 옅어짐
export function shell(p, C, x, y, r, a, sy = 1) {
  if (a <= 0.01 || r < 1) return;
  soft(p, x - r * 1.1 - 1, y - r * 1.1 * sy - 1, x + r * 1.1 + 1, y + r * 1.1 * sy + 1, (px, py, out) => {
    const d = Math.hypot(px - x, (py - y) / sy) / r, b = 1 - Math.abs(d - 0.9) / 0.2;
    if (b <= 0) return;
    out.a = a * 0.6 * b * b; return d > 0.9 ? C[5] : C[4];
  });
}

// 조여 드는 압력 고리
export function squeeze(p, C, x, y, r, t, period, rmax, sy = 1) {
  const u = (t % period) / period;
  ring(p, C, x, y, lerp(rmax, r * 1.15, ss(0, 1, u)), sy, Math.sin(Math.PI * u) * 0.55, 1.6);
}

// ───── 입자: 맺혀 드는 기(bead) · 떠올라 흩어지는 기 알갱이(drop) · 기 안개(mist) · 압력 고리(ring) ─────
export class Drops {
  constructor(R) { this.R = R; this.a = []; this.later = []; }
  add(o) { o.age = 0; this.a.push(o); return o; }
  at(t, fn) { this.later.push({ t, fn }); }
  bead(x, y, tgt, o = {}) { return this.add({ k: 0, x, y, vx: o.vx || 0, vy: o.vy || 0, tgt, pull: o.pull || 900, life: o.life || 1.1, h: [] }); }
  // 기 알갱이: 처음 속도로 튀어 나갔다가 금방 멈추며 위로 떠올라 흩어짐 (중력 없음 · g는 옛 호출 호환용으로 무시)
  drop(x, y, vx, vy, o = {}) { return this.add({ k: 1, x, y, vx, vy, r: o.r || 1, life: (o.life || 1.4) * 0.8, ph: this.R.range(0, TAU) }); }
  mist(x, y, vx, vy, r0, r1, life, a = 0.25) { return this.add({ k: 2, x, y, vx, vy, r0, r1, life, a }); }
  ring(x, y, r0, r1, life, o = {}) { return this.add({ k: 3, x, y, r0, r1, life, sy: o.sy ?? 1, sx: o.sx ?? 1, w: o.w ?? 2, a: o.a ?? 1 }); }
  // 둘레에서 기가 휘어 들며 맺힘 (T: {x, y, r} 모이는 자리)
  gather(T, rate, rmin, rmax, dt, spin = 1, sy = 0.85) {
    const R = this.R;
    for (let n = rate * dt; n > 0; n--) if (R.chance(Math.min(1, n))) {
      const a = R.range(0, TAU), d = R.range(rmin, rmax), tv = d * 2.4 * spin;
      this.bead(T.x + Math.cos(a) * d, T.y + Math.sin(a) * d * sy, T, { vx: -Math.sin(a) * tv, vy: Math.cos(a) * tv * sy, pull: d * 22 });
    }
  }
  // 맞는 자리: 기가 터지며 압력 고리 셋(세로·가로·바닥) · 떠오르는 기 알갱이 · 안개
  splash(x, y, s = 1, o = {}) {
    const R = this.R;
    this.ring(x, y, 2 * s, 20 * s, 0.4, { w: 2.5 * s });
    this.ring(x, y, 2 * s, 30 * s, 0.55, { sy: 0.4, w: 2 * s, a: 0.8 });
    if (o.ground !== false) this.ring(x, -1, 3 * s, 32 * s, 0.6, { sy: 0.25, w: 2, a: 0.7 });
    for (let i = 0; i < 14 * s; i++) {
      const a = (o.dir ?? -Math.PI / 2) + R.range(-0.5, 0.5) * (o.spread ?? 2.6), sp = R.range(60, 180) * Math.sqrt(s);
      this.drop(x, y, Math.cos(a) * sp, Math.sin(a) * sp, { r: R.chance(0.3) ? 2 : 1, life: 1.3 });
    }
    for (let i = 0; i < 5 * s; i++) { const a = R.range(0, TAU); this.mist(x, y, Math.cos(a) * 30 * s, Math.sin(a) * 20 * s - 10, 3 * s, 11 * s, R.range(0.6, 0.9), 0.2); }
    this.add({ k: 4, x, y, r0: (o.r ?? 5), r1: (o.r ?? 5) * 2.6, life: 0.32, sy: 1 });
  }
  update(dt, t) {
    for (const L of this.later) if (t >= L.t) L.fn();
    this.later = this.later.filter(L => t < L.t);
    for (const q of this.a) {
      q.age += dt;
      if (q.k === 0) {
        const T = q.tgt, dx = T.x - q.x, dy = T.y - q.y, d = Math.hypot(dx, dy) || 1;
        q.vx += dx / d * q.pull * dt; q.vy += dy / d * q.pull * dt;
        const dr = Math.pow(0.05, dt); q.vx *= dr; q.vy *= dr;
        q.h.unshift([q.x, q.y]); if (q.h.length > 4) q.h.pop();
        q.x += q.vx * dt; q.y += q.vy * dt;
        if (d < (T.r || 2) * 0.9 + 1.5) q.age = q.life;
      } else if (q.k === 1) {
        const dr = Math.pow(0.04, dt); q.vx *= dr; q.vy = q.vy * dr - 45 * dt;
        q.x += (q.vx + Math.sin(q.age * 9 + q.ph) * 6) * dt; q.y += q.vy * dt;
      } else if (q.k === 2) {
        q.x += q.vx * dt; q.y += q.vy * dt; const dr = Math.pow(0.25, dt); q.vx *= dr; q.vy *= dr;
      }
    }
    this.a = this.a.filter(q => q.age < q.life);
  }
  draw(p, C) {
    for (const q of this.a) {
      const u = q.age / q.life;
      if (q.k === 2) {
        const r = lerp(q.r0, q.r1, eo(u)), a = q.a * (u < 0.2 ? u / 0.2 : 1 - (u - 0.2) / 0.8);
        soft(p, q.x - r, q.y - r, q.x + r, q.y + r, (px, py, out) => { const d = Math.hypot(px - q.x, py - q.y) / r; if (d >= 1) return; out.a = a * (1 - d) * (1 - d) * 1.6; return d < 0.5 ? C[5] : C[4]; });
      } else if (q.k === 0) {
        const a = Math.min(1, q.age * 8);   // 꼬리선 없이 번진 알갱이 하나 (바로 뒤 한 칸만 옅게)
        p.glow(q.x, q.y, 2.5, C[4], 0.25 * a);
        if (q.h[1]) p.blend(q.h[1][0], q.h[1][1], C[4], a * 0.3);
        p.blend(q.x, q.y, C[5], a * 0.9);
      } else if (q.k === 1) {
        const a = (u < 0.5 ? 1 : 1 - (u - 0.5) / 0.5) * (0.75 + 0.25 * Math.sin(q.age * 20 + q.ph));
        if (q.r <= 1) p.blend(q.x, q.y, C[5], a);
        else { p.glow(q.x, q.y, 3, C[4], 0.3 * a); p.blend(q.x, q.y, C[6], a); p.blend(q.x, q.y + 1, C[4], a * 0.6); }
      } else if (q.k === 3) ring(p, C, q.x, q.y, lerp(q.r0, q.r1, eo(u)), q.sy, q.a * (1 - u), q.w * (1 - u * 0.6) + 0.5, q.sx);
      else if (q.k === 4) shell(p, C, q.x, q.y, lerp(q.r0, q.r1, eo(u)), 1 - u, q.sy);
    }
  }
}

// p.shade와 같지만 진짜 반투명으로 섞음 (shade는 alpha < 1을 디더링 점무늬로 찍음 → 부드러운 기운엔 안 맞음)
export function soft(p, x0, y0, x1, y1, fn) {
  const o = { c: 0, a: 1, k: 0 };
  p.each(x0, y0, x1, y1, (lx, ly, sx, sy) => {
    o.c = 0; o.a = 1; o.k = 0;
    const c = fn(lx, ly, o) || o.c;
    if (c) p.blendPx(sx, sy, c, Math.min(1, o.a));
    if (o.k > 0) p.add(sx, sy, c, o.k);
  });
}

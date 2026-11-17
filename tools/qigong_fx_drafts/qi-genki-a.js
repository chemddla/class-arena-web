// 기공옥 시안 (원기옥 느낌: 사방에서 모여드는 기운으로 머리 위에 거대한 구체 → 내리꽂아 거대한 기운 돔) — 별빛·흰 섬광 없음
//   미리보기 시간은 게임(시전 8초)을 줄임: 땅에서 모으기 1초 → 떠오르며 키우기 → 최대 크기 · 던지기 → 떨어짐 0.5초 → 터짐 1.8초
//   크기: 게임 px × 0.8 (캐릭터 키 약 43) · 터지는 반지름만 게임(6칸)보다 작게 (화면에 담으려고)
//   이펙트가 커서 세부 묘사를 살림 (2026-11-17 사용자):
//   구체: 스스로 빛나는 기운 덩어리 (한쪽 그늘 없이 가운데 밝고 둘레 밝음, 바이어 디더) · 속에서 도는 나선 기운 팔 · 잡음 기운 결 · 테두리 빛과 바깥 기운 막 ·
//     둘레에서 피어오르는 기운 불꽃(혀) · 혼천의처럼 도는 굵은 실 고리 셋(뒤쪽 반은 구체 뒤로) · 속 실타래 ·
//     줄기를 타고 들어오는 기운 알갱이, 표면에 닿는 자리마다 작은 물결
//   모으기: 사방에서 휘어 드는 기운 줄기 · 발밑 기운 고리와 땅 빛 · 피어오르는 안개 · 구체로 조여 드는 압력 고리
//   떨어짐: 앞쪽 공기를 미는 활 모양 압력 고리 · 지나온 길을 감는 실 두 가닥 · 겨눈 자리에 조여 드는 고리 셋
//   터짐: 땅에 눌림 → 뜨거운 가운데 빛 · 반구 돔(겉면을 도는 경선·위선 기운 실) · 바닥 물결 두 겹 · 얇은 충격 고리 셋 ·
//     땅을 따라 뻗는 기운 줄 · 실 고리 풀림 · 나선 실이 감은 기운 기둥 · 남은 땅 빛과 천천히 솟는 기운 알갱이
import { Particles, P, Rng, fit, ease, clamp, noise2, TAU } from "../../core/index.js";
import { QI_GOLD, pressureRing } from "./_qi.js";
import { makeLoops, jThreads } from "./_jcore.js";

export const T = { GROUND: 1.0, RISE: 2.4, FULL: 3.4, THROW: 3.75, FALL: 0.5, BOOM: 2.2 };
const LAND = T.THROW + T.FALL, END = LAND + T.BOOM;
const HAND = 40, LIFT = 88, ORB = 74;        // 손바닥 높이 · 떠오르는 높이 · 구체 반지름 (게임 50·110·92 × 0.8)
const TX = 600, BR = 400, SY = 0.5;          // 떨어지는 자리 · 터지는 반지름(미리보기용) · 바닥 납작
export const meta = { size: [1300, 620], origin: [190, 350], loop: false, fps: 30, bg: "dark", name: "기공옥 A 원기옥", desc: "사방에서 모인 기운으로 거대한 구체를 내리꽂음", tags: ["qigong"], duration: END + 0.05, options: { palette: QI_GOLD, seed: 9 } };

// 구체 명암 9단 (그늘 → 빛, 흰색 없이 크림색까지) — 게임 QI_J_SHADE와 같은 값
const SHADE = fit(['#2a1806', '#4e3210', '#7a4e12', '#a66c1c', '#c98d26', '#e2ab3a', '#f2c862', '#f9df98', '#fdf0c8'], 9);   // fit: 색 값을 그리기용 형식으로
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map(v => (v + 0.5) / 16);
const L16 = makeLoops(16), L6 = makeLoops(6), L10 = makeLoops(10);
const RINGS = [[0.35, 0, 1.6], [1.25, 1.1, -1.2], [2.2, 2.3, 0.9]];   // 혼천의 고리 [기울기, 방향, 빠르기]
const sstep = (a, b, x) => { const u = clamp((x - a) / (b - a)); return u * u * (3 - 2 * u); };
const fr01 = (x) => x - Math.floor(x);
export function lift01(t) {
  if (t < T.GROUND) return 0;
  if (t < T.THROW) return sstep(T.GROUND, T.RISE, t);
  return 1 - ease.inQuad(clamp((t - T.THROW) / (T.FALL + 0.3)));
}
const orbR = (t) => ORB * (0.15 + 0.85 * ease.inOutSine(clamp(t / T.FULL)));
const orbY = (t, r) => -(HAND + r * 0.9 + LIFT * lift01(t));

// 기운 줄기: 멀리서 휘어 들어오는 곡선 [시작 각, 거리, 휨, 속도]
const STREAMS = [];
for (let i = 0; i < 22; i++) STREAMS.push([((i * 0.618) % 1) * TAU, 260 + ((i * 0.37) % 1) * 260, (((i * 0.73) % 1) - 0.5) * 1.4, 0.8 + ((i * 0.41) % 1) * 0.6]);
function streamPt(i, tx, ty, reach, u) {
  const [a, dist, bend] = STREAMS[i];
  const sx = tx + Math.cos(a) * dist * reach, sy = Math.min(-4, ty + Math.sin(a) * dist * reach * 0.6);
  const mx = (sx + tx) / 2 - (ty - sy) * bend * 0.5, my = (sy + ty) / 2 + (tx - sx) * bend * 0.5, iu = 1 - u;
  return [iu * iu * sx + 2 * iu * u * mx + u * u * tx, iu * iu * sy + 2 * iu * u * my + u * u * ty];
}

// 혼천의 실 고리 (front: true면 앞쪽 반, false면 뒤쪽 반만)
function orbRings(p, C, x, y, r, t, k, front) {
  RINGS.forEach(([tilt, yaw, sp], i) => {
    const ct = Math.cos(tilt), st = Math.sin(tilt), ya = yaw + t * 0.7 * (i % 2 ? 1 : -1), cy = Math.cos(ya), sy = Math.sin(ya), rr = r * (1.14 + 0.06 * i);
    for (let a = 0; a < TAU; a += 0.6 / rr) {
      const u = a + t * sp, px = Math.cos(u), py = Math.sin(u) * ct, pz = Math.sin(u) * st, X = px * cy - pz * sy, Z = px * sy + pz * cy;
      if ((Z > 0) !== front) continue;
      const gap = fr01(u * 1.3 + i * 0.4) < 0.07;   // 군데군데 아주 짧게 끊겨 실처럼 보임
      if (gap) continue;
      if (front) { p.blend(x + X * rr, y + py * rr + 1, C[3], k * 0.8); p.blend(x + X * rr, y + py * rr, C[6], k); }
      else p.blend(x + X * rr, y + py * rr, C[4], k * 0.3);
    }
  });
}

// 둘레에서 피어오르는 기운 불꽃: 테두리에서 바깥으로 휘며 짧게 솟았다 사라지는 혀 (위쪽으로 조금 더 길게)
function orbWisps(p, C, x, y, r, t, k) {
  for (let i = 0; i < 34; i++) {
    const life = 0.55 + (i % 5) * 0.08, ph = fr01(t / life + i * 0.29), g0 = (i / 34) * TAU + Math.sin(i * 7.1) * 0.2 + t * 0.25;
    const up = 0.6 + 0.4 * Math.max(0, -Math.sin(g0)), len = r * (0.18 + 0.14 * fr01(i * 0.61)) * up * Math.sin(ph * Math.PI), curl = (i % 2 ? 1 : -1) * 0.5;
    for (let s = 0; s < 1; s += 1.2 / Math.max(6, len)) {
      const g = g0 + curl * s * s * 0.25, d = r * (0.97 + (len / r) * s), w = Math.sin(ph * Math.PI) * (1 - s);
      p.blend(x + Math.cos(g) * d, y + Math.sin(g) * d - s * len * 0.3, s < 0.35 ? C[6] : C[5], k * w * 0.85);
    }
  }
}

// 거대한 구체
function genkiOrb(p, C, x, y, r, t, k = 1, sx = 1, sy = 1, extras = true) {
  p.glow(x, y, r * 2.2, C[4], 0.35 * k);
  if (extras) orbRings(p, C, x, y, r * Math.max(sx, sy), t, 0.85 * k, false);
  for (let g = 0; g < TAU; g += 0.5 / r) for (let d = 1; d < 1.3; d += 0.8 / r) p.blend(x + Math.cos(g) * r * d * sx, y + Math.sin(g) * r * d * sy, C[5], 0.5 * k * Math.pow((1.3 - d) / 0.3, 1.6));
  p.shade(x - r * sx - 1, y - r * sy - 1, x + r * sx + 1, y + r * sy + 1, (px, py, out) => {
    const ux = (px - x) / (r * sx), uy = (py - y) / (r * sy), d2 = ux * ux + uy * uy;
    if (d2 > 1) return 0;
    const d = Math.sqrt(d2), nz = Math.sqrt(1 - d2);
    const core = nz * nz;   // 스스로 빛나는 기운 덩어리: 한쪽에서 빛을 받는 그늘 없이 가운데가 가장 밝음 (사용자: 금구슬 같은 명암 빼기)
    const ang = Math.atan2(uy, ux), arms = Math.sin(3 * ang + 7 * d - t * 3.2);       // 속에서 도는 나선 기운 팔 셋
    const sw = t * 1.3 + (1 - d) * 2.4, cs = Math.cos(sw), sn = Math.sin(sw), fx = ux * cs - uy * sn, fy = ux * sn + uy * cs;
    let v = 0.5 + 0.3 * core + 0.12 * arms * (1 - d * 0.5) + 0.14 * noise2(fx * 2.6 + 5, fy * 2.6 - t * 0.6) + 0.08 * noise2(fx * 6 - t, fy * 6 + 3);   // 속에서 기운 결·나선 팔이 밝고 어둡게 흐름
    const edge = d > 0.78 ? Math.pow((d - 0.78) / 0.22, 1.5) : 0;   // 테두리: 둘레 전체가 밝아지는 빛 (빛 받는 쪽 더)
    v += edge * 0.35;   // 둘레 전체가 고르게 밝음
    const idx = Math.floor(v * 8 + BAYER[((Math.floor(py) & 3) << 2) | (Math.floor(px) & 3)] - 0.5);
    out.a = k;
    return SHADE[Math.max(4, Math.min(8, idx))];   // 가장 어두운 칸도 진한 금빛까지만
  });
  jThreads(p, C, L16, x, y, r * 0.86, t * 0.5, 0.45 * k, sx, sy);
  if (extras) { orbWisps(p, C, x, y, r, t, k); orbRings(p, C, x, y, r * Math.max(sx, sy), t, 0.85 * k, true); }
}

// 기운 줄기 + 줄기를 타고 들어오는 알갱이 + 표면에 닿는 자리의 작은 물결
function streams(p, C, tx, ty, r, t, k, reach = 1) {
  STREAMS.forEach(([, , , sp], i) => {
    for (let u = 0; u < 1; u += 0.003) {
      const q = ((u - t * sp * 0.9 + i * 0.13) % 0.25 + 0.25) % 0.25, near = u > 0.92 ? (1 - u) / 0.08 : 1;
      const [x, y] = streamPt(i, tx, ty, reach, u);
      p.blend(x, y, C[4], k * 0.22 * u * near);
      if (q < 0.07) p.blend(x, y, q < 0.025 ? C[6] : C[5], k * (0.3 + 0.7 * u) * near * (1 - q / 0.07 * 0.5));
    }
    for (let m = 0; m < 2; m++) {   // 알갱이 (구체에 가까울수록 빨라짐)
      const u = Math.pow(fr01(t * sp * 0.45 + i * 0.37 + m * 0.5), 1.6);
      if (u > 0.93) continue;
      const [x, y] = streamPt(i, tx, ty, reach, u);
      p.disc(x, y, 1.6 + u * 1.2, C[5], k * 0.9); p.blend(x, y, C[6], k);
      const [bx, by] = streamPt(i, tx, ty, reach, Math.max(0, u - 0.03));
      for (let s = 0; s < 1; s += 0.1) p.blend(x + (bx - x) * s, y + (by - y) * s, C[5], k * 0.6 * (1 - s));
    }
    const hit = fr01(t * sp * 0.45 + i * 0.37);   // 표면에 닿는 순간 작은 물결 (닿은 자리에서 짧게)
    if (hit < 0.12 && r > 10) {
      const [ax, ay] = streamPt(i, tx, ty, reach, 0.97), g = Math.atan2(ay - ty, ax - tx), e = hit / 0.12;
      for (let s = -0.35; s <= 0.35; s += 0.02) p.blend(tx + Math.cos(g + s) * r * (1.02 + 0.12 * e), ty + Math.sin(g + s) * r * (1.02 + 0.12 * e), C[6], k * 0.7 * (1 - e) * (1 - Math.abs(s) / 0.35));
    }
  });
}

// 바닥 납작 고리 (실 고리: 앞 반 밝고 굵게, 뒤 반 옅게)
function flatRing(p, C, cx, cy, r, k, t, sp, gap = 0) {
  for (let a = 0; a < TAU; a += 0.7 / Math.max(r, 6)) {
    const u = a + t * sp;
    if (gap && fr01(u * 2.3) < gap) continue;
    const x = cx + Math.cos(u) * r, y = cy + Math.sin(u) * r * SY;
    if (Math.sin(u) > 0) { p.blend(x, y + 1, C[3], k * 0.7); p.blend(x, y, C[6], k); } else p.blend(x, y, C[4], k * 0.35);
  }
}
// 땅 빛 (납작 원판, 가운데 진하고 가장자리로 옅어짐)
function groundGlow(p, C, cx, r, k) {
  if (k <= 0.01) return;
  for (let py = Math.floor(-r * SY); py <= r * SY; py++) for (let px = Math.floor(cx - r); px <= cx + r; px++) {
    const v = Math.hypot((px + 0.5 - cx) / r, (py + 0.5) / (r * SY));
    if (v < 1) p.blend(px + 0.5, py + 0.5, v < 0.4 ? C[5] : C[4], k * Math.pow(1 - v, 1.5) * 0.6);
  }
}

// 바닥 기운 물결 (앞머리가 짙고 안쪽으로 옅어짐, 몸 뒤쪽 반은 옅게)
function groundWave(p, C, cx, r, w, k, t) {
  if (k <= 0.01 || r < 2) return;
  const ry = r * SY;
  for (let py = Math.floor(-ry * 1.08); py <= ry * 1.08; py++) for (let px = Math.floor(cx - r * 1.08); px <= cx + r * 1.08; px++) {
    const dx = px + 0.5 - cx, dy = py + 0.5, a = Math.atan2(dy / SY, dx);
    const v = Math.hypot(dx, dy / SY) / r / (1 + 0.04 * noise2(Math.cos(a) * 2.4 + t * 3, Math.sin(a) * 2.4));
    if (v > 1.07 || v < 1 - w) continue;
    const band = v <= 1 ? sstep(1 - w, 1, v) : 1 - sstep(1, 1.07, v);
    p.blend(px + 0.5, py + 0.5, band > 0.7 ? C[6] : C[5], band * band * k * (0.5 + 0.5 * sstep(-0.4, 0.4, dy / ry)) * 0.9);
  }
}

// 반구 기운 돔: 그라데이션 테두리 + 아주 옅은 속 + 겉면을 도는 경선·위선 기운 실 (앞쪽만 진하게)
function dome(p, C, cx, R, k, t, hol = 0) {
  if (k <= 0.12 || R < 3) return;
  const RY = R * 0.78;
  for (let py = Math.floor(-RY * 1.15); py <= 2; py++) for (let px = Math.floor(cx - R * 1.15); px <= cx + R * 1.15; px++) {
    const dx = px + 0.5 - cx, dy = py + 0.5, a = Math.atan2(dy / RY, dx / R);
    const v = Math.hypot(dx / R, dy / RY) / (1 + 0.03 * noise2(Math.cos(a) * 3 + t * 2, Math.sin(a) * 3));
    if (v > 1.15) continue;
    const band = sstep(0.55, 0.95, v) * (1 - sstep(0.95, 1.15, v));
    // 속: 구체와 같은 결로 일렁이는 빛나는 기운 (가운데가 가장 밝음). hol: 안쪽부터 비어 가는 반지름 (껍질만 남았다 풀림)
    const n = noise2(dx / R * 3.2 + t * 0.8, dy / RY * 3.2 - t * 1.4), n2 = noise2(dx / R * 7 - t, dy / RY * 7 + 5);
    const fill = v < 1 ? (0.36 + 0.2 * n + 0.1 * n2 + 0.3 * Math.pow(1 - v, 2)) * sstep(hol - 0.15, hol + 0.1, v) : 0;
    const al = Math.max(band * 0.85 * (0.8 + 0.2 * noise2(Math.cos(a) * 4 - t * 2, Math.sin(a) * 4)), fill);
    const base = sstep(0, RY * 0.3, -dy);
    const c = band > 0.75 ? C[6] : band > 0.35 ? C[5] : fill > 0.6 ? C[6] : fill > 0.36 ? C[5] : C[4];   // 옅으면 어두운 바탕에 회색으로 보여서 속은 진하게
    if (al * base > 0.01) p.blend(px + 0.5, py + 0.5, c, Math.min(1, al) * k * base);
  }
  // 경선 8줄 (돔 위를 천천히 돎) · 위선 2줄
  for (let m = 0; m < 8; m++) {
    const lon = (m / 8) * Math.PI + t * 0.6, cl = Math.cos(lon), sl = Math.sin(lon);
    if (sl < 0) continue;   // 앞쪽 반만
    for (let el = 0.08; el < Math.PI / 2; el += 0.8 / R) {
      const ce = Math.cos(el), x = cx + cl * ce * R * 0.98, y = -Math.sin(el) * RY * 0.98 + sl * ce * R * SY * 0.25;
      p.blend(x, y, C[6], k * 0.55 * sstep(0.08, 0.4, el) * (0.4 + 0.6 * sl));
    }
  }
  [0.35, 0.7].forEach((h, i) => {
    const ce = Math.cos(h * Math.PI / 2), yy = -Math.sin(h * Math.PI / 2) * RY * 0.98;
    for (let a = 0; a < Math.PI; a += 0.7 / R) p.blend(cx + Math.cos(a + t * (i ? 0.4 : -0.3)) * ce * R * 0.98, yy + Math.sin(a) * ce * R * SY * 0.25, C[5], k * 0.45);
  });
}

const BURST = [];
for (let i = 0; i < 30; i++) BURST.push([(i / 30) * TAU + ((i * 0.37) % 1 - 0.5) * 0.2, 0.2 + ((i * 0.53) % 1) * 0.2, 0.75 + ((i * 0.71) % 1) * 0.3]);

// 기운 파편 [방향, 빠르기, 위로 솟는 힘, 크기]
const SHARDS = [];
for (let i = 0; i < 18; i++) SHARDS.push([(i / 18) * TAU + (fr01(i * 0.37) - 0.5) * 0.3, 220 + fr01(i * 0.53) * 260, 160 + fr01(i * 0.71) * 220, 2.5 + fr01(i * 0.29) * 2.5]);
const GRAV = 620, SHARD_T0 = 0.08;
// 파편 자리 (tau: 날아간 시간) → [x, 땅 y, 땅 위 높이]
function shardAt([a, sp, up], tau) { return [TX + Math.cos(a) * sp * tau, Math.sin(a) * sp * tau * SY, Math.max(0, up * tau - GRAV * tau * tau / 2 + 30)]; }
const shardLand = ([, , up]) => (up + Math.sqrt(up * up + 2 * GRAV * 30)) / GRAV;

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed);
  const ps = new Particles({ rng: R, ground: () => 0, haze: C[4] });
  let t = 0, boomed = false;
  return {
    update(dt) {
      t += dt;
      if (t < T.THROW && R.chance(0.6)) {   // 땅에서 피어오르는 기운 안개 (몸 쪽으로 쏠림)
        const x = R.range(-400, 400), d = Math.sign(-x) || 1;
        ps.spawn(P.VAPOUR, x, -2, d * R.range(10, 40), -R.range(40, 90), R.range(1.0, 1.6), R.pick([C[4], C[5]]), R.range(2, 3.2));
      }
      if (!boomed && t >= LAND) {
        boomed = true;
        for (let i = 0; i < 80; i++) {   // 위로 솟는 기운 + 사방으로 밀려나는 안개
          const up = i < 30, a = R.range(0, TAU), sp = R.range(150, 420);
          if (up) ps.spawn(P.VAPOUR, TX + R.range(-40, 40), R.range(-30, 0), R.range(-30, 30), -R.range(200, 420), R.range(0.6, 1.0), R.pick([C[4], C[5], C[6]]), R.range(3, 5));
          else ps.spawn(P.VAPOUR, TX + Math.cos(a) * 30, Math.sin(a) * 15, Math.cos(a) * sp, Math.sin(a) * sp * SY - 20, R.range(0.5, 0.9), R.pick([C[4], C[5]]), R.range(3, 5));
        }
      }
      const bb = t - LAND;
      if (boomed && bb < 0.8) {   // 퍼지는 물결 앞머리에서 기운 장막이 솟음
        const rr = BR * (0.05 + 0.95 * ease.outQuart(clamp(bb / 1.0)));
        for (let i = 0; i < 6; i++) { const a = R.range(0, TAU); ps.spawn(P.VAPOUR, TX + Math.cos(a) * rr, Math.sin(a) * rr * SY, Math.cos(a) * 40, -R.range(50, 120), R.range(0.35, 0.6), R.pick([C[4], C[5], C[6]]), R.range(2.2, 3.6)); }
      }
      if (boomed && t < END - 0.3 && R.chance(0.8)) {   // 남은 땅에서 천천히 솟는 기운 알갱이
        const a = R.range(0, TAU), d = Math.sqrt(R.range(0, 1)) * BR * 0.8;
        ps.spawn(P.VAPOUR, TX + Math.cos(a) * d, Math.sin(a) * d * SY, 0, -R.range(25, 60), R.range(0.6, 1.0), R.pick([C[5], C[6]]), R.range(1.2, 2));
      }
      ps.update(dt);
    },
    draw(p) {
      // ----- 모으기 -----
      if (t < T.THROW) {
        const r = orbR(t), y = orbY(t, r), k = clamp(t / 0.4), lf = LIFT * lift01(t);
        // 발밑: 땅 빛과 도는 실 고리 둘 (떠오르면 넓어지고 옅어짐)
        groundGlow(p, C, 0, 60 + lf * 0.5, 0.5 * k * (1 - 0.4 * lift01(t)));
        flatRing(p, C, 0, -2, 46 + lf * 0.4, 0.7 * k, t, 1.2, 0.08);
        flatRing(p, C, 0, -2, 64 + lf * 0.6, 0.45 * k, t + 2, -0.8, 0.2);
        ps.draw(p);
        streams(p, C, 0, y, r, t, 0.85 * k * (t > T.FULL ? 1 - clamp((t - T.FULL) / 0.35) * 0.7 : 1), 1 + 0.4 * clamp((t - T.GROUND) / 2));
        if (t > 0.5) { const per = 0.75, q = (t % per) / per; pressureRing(p, C, 0, y, 1 - q, r * 1.05, r * 1.9, 1, 0.45); }
        // 몸에서 구체로 이어진 기운 줄기 (두 손 → 구체 아랫면)
        for (let s = 0; s < 1; s += 0.02) { const yy = -HAND - lf + (y + r * 0.9 + HAND + lf) * s; p.blend(Math.sin(s * 9 + t * 6) * 2, yy, C[5], 0.5 * k); }
        genkiOrb(p, C, 0, y, r, t, k, 1, 1, r > 18);
        return;
      }
      ps.draw(p);
      // ----- 떨어짐 -----
      const r = ORB, f = t - T.THROW;
      if (f < T.FALL) {
        const e = ease.inQuad(clamp(f / T.FALL)), y0 = orbY(T.THROW, r), y1 = -r * 0.7, x = TX * e, y = y0 + (y1 - y0) * e;
        const ang = Math.atan2(y1 - y0, TX);
        // 겨눈 자리: 땅 그림자 + 조여 드는 고리 셋
        for (let g = 0; g < TAU; g += 0.01) for (let d = 0.2; d <= 1; d += 0.1) p.blend(TX + Math.cos(g) * r * 1.2 * d * (0.4 + 0.6 * e), Math.sin(g) * r * 1.2 * d * SY * (0.4 + 0.6 * e), C[1], 0.05 * e);
        for (let j = 0; j < 3; j++) flatRing(p, C, TX, 0, r * (1.6 + j * 0.7) * (1 - 0.55 * fr01(f * 2.2 + j / 3)), 0.6 * (0.3 + 0.7 * e), t, j % 2 ? 1 : -1, 0.15);
        // 지나온 길의 기운 꼬리 + 감아 도는 실 두 가닥
        for (let j = 1; j <= 16; j++) { const e2 = ease.inQuad(clamp((f - j * 0.012) / T.FALL)); p.disc(TX * e2, y0 + (y1 - y0) * e2, r * (0.95 - j * 0.05), C[4], 0.05); }
        for (let i = 0; i < 2; i++) for (let s = 0; s < 1; s += 0.004) {
          const e2 = ease.inQuad(clamp((f - s * 0.2) / T.FALL)), px = TX * e2, py = y0 + (y1 - y0) * e2, ph = s * 26 - t * 12 + i * Math.PI, w = r * 0.85 * (1 - s * 0.6);
          if (Math.cos(ph) > 0) p.blend(px - Math.sin(ang) * Math.sin(ph) * w, py + Math.cos(ang) * Math.sin(ph) * w, C[6], 0.8 * (1 - s));
        }
        genkiOrb(p, C, x, y, r, t);
        // 앞쪽 공기를 미는 활 모양 압력 고리
        for (let j = 0; j < 2; j++) {
          const q = fr01(f * 4 + j * 0.5), rr = r * (1.08 + 0.35 * q);
          for (let s = -1.1; s <= 1.1; s += 0.01) p.blend(x + Math.cos(ang + s) * rr, y + Math.sin(ang + s) * rr, C[6], 0.6 * (1 - q) * (1 - Math.abs(s) / 1.1));
        }
        return;
      }
      // ----- 터짐 -----
      //   0~0.12 땅에 눌림 + 고리가 한 점으로 조여 듦(숨 고르기) → 빛나는 기운 돔이 부풀고(속은 일렁이는 기운) · 바닥 물결 · 충격 고리 ·
      //   기운 파편이 사방으로 포물선을 그리며 날아가 떨어진 자리마다 작은 고리 · 기둥과 위로 오르는 고리 → 돔이 안쪽부터 비어 껍질만 남았다
      //   실 고리로 풀림 · 땅에 기운 문양(겹고리·살)이 남았다 사라짐 · 천천히 솟는 알갱이
      const b = t - LAND;
      groundGlow(p, C, TX, BR * 0.85 * (0.2 + 0.8 * ease.outCubic(clamp(b / 0.5))), 0.8 * Math.pow(1 - clamp((b - 0.3) / 1.8), 1.4));   // 남는 땅 빛
      // 땅 기운 문양: 물결이 지나간 자리에 겹고리 넷과 살 열여섯이 새겨졌다가 천천히 사라짐
      const sealK = clamp((b - 0.3) / 0.3) * Math.pow(1 - clamp((b - 1.1) / 1.0), 1.3);
      if (sealK > 0.01) {
        [0.28, 0.47, 0.66, 0.86].forEach((q, i) => flatRing(p, C, TX, 0, BR * q, sealK * (0.75 - i * 0.1), t * 0.3, i % 2 ? 0.25 : -0.25, 0.1 + 0.04 * i));
        for (let m = 0; m < 16; m++) { const a = (m / 16) * TAU + t * 0.05, ca = Math.cos(a), sa = Math.sin(a) * SY; for (let d = BR * 0.3; d < BR * 0.84; d += 1) p.blend(TX + ca * d, sa * d, C[5], sealK * 0.35 * (sa < 0 ? 0.5 : 1) * (m % 2 ? 0.6 : 1)); }
      }
      if (b < 0.1) { const e = b / 0.1; genkiOrb(p, C, TX, -r * 0.7 * (1 - 0.5 * e), r * (1 - 0.3 * e), t, 1 - e, 1 + 0.5 * e, 1 - 0.45 * e, false); }
      for (let j = 0; j < 2; j++) { const q = clamp((b - j * 0.03) / 0.1); if (q < 1) flatRing(p, C, TX, 0, r * (2.4 - 1.9 * ease.inQuad(q)), 0.8 * q, t, 0); }   // 조여 드는 고리 (터지기 직전)
      // 뜨거운 가운데 빛
      if (b < 0.6) { const e = b / 0.6, rr = 40 + 130 * ease.outCubic(e); for (let py = Math.floor(-rr * 0.6); py <= rr * 0.25; py++) for (let px = Math.floor(TX - rr); px <= TX + rr; px++) { const v = Math.hypot((px - TX) / rr, (py + rr * 0.1) / (rr * 0.45)); if (v < 1) p.blend(px, py, v < 0.35 ? C[6] : C[5], (1 - e) * Math.pow(1 - v, 1.3) * 0.85); } }
      const e = clamp(b / 1.0), k = Math.pow(1 - e, 1.1);
      const DR = BR * 0.62 * (0.1 + 0.9 * ease.outQuart(clamp((b - 0.06) / 0.55)));
      if (b > 0.06) dome(p, C, TX, DR, Math.pow(1 - clamp((b - 0.55) / 0.9), 1.4), t, sstep(0.45, 1.25, b) * 1.05);
      if (b > 0.9 && b < 1.7) { const q = (b - 0.9) / 0.8; jThreads(p, C, L10, TX, -DR * 0.35, DR * 0.55, t * 0.3, Math.pow(1 - q, 1.4) * 0.8, 1, 0.75, 1 + 1.3 * ease.outCubic(q)); }   // 돔 껍질이 실 고리로 풀림
      groundWave(p, C, TX, BR * (0.05 + 0.95 * ease.outQuart(e)), 0.3, k, t);
      const e2 = clamp((b - 0.1) / 1.0);
      if (e2 > 0) groundWave(p, C, TX, BR * (0.05 + 0.75 * ease.outQuart(e2)), 0.22, 0.5 * Math.pow(1 - e2, 1.3), t + 3);
      for (let j = 0; j < 3; j++) { const q = clamp((b - 0.08 - j * 0.07) / 0.5); if (q > 0 && q < 1) flatRing(p, C, TX, 0, BR * 1.05 * ease.outCubic(q), 0.7 * (1 - q), t, 0); }   // 얇은 충격 고리 셋
      if (e < 0.6) {   // 땅을 따라 뻗는 기운 줄
        const kk = Math.pow(1 - e / 0.6, 1.2), rr = BR * (0.05 + 0.95 * ease.outQuart(e));
        BURST.forEach(([a0, len, sp]) => {
          const head = rr * Math.min(1, sp), tail = Math.max(20, head - BR * len), ca = Math.cos(a0), sa = Math.sin(a0) * SY;
          for (let d = tail; d <= head; d += 0.7) { const f2 = (d - tail) / Math.max(1, head - tail); p.blend(TX + ca * d, sa * d, f2 > 0.75 ? C[6] : f2 > 0.35 ? C[5] : C[4], kk * (sa < 0 ? 0.5 : 1) * (0.25 + 0.75 * f2)); }
        });
      }
      if (b < 0.6) jThreads(p, C, L6, TX, -50, 30, t * 0.4 + 2, Math.pow(1 - b / 0.6, 1.4) * 0.8, 1, 0.8, 1 + 5 * ease.outCubic(b / 0.6));
      pressureRing(p, C, TX, -60, (b - 0.1) / 0.5, 20, BR * 0.5, 1, 0.5);
      // 기운 파편: 포물선으로 날아가며 꼬리, 떨어진 자리에 작은 고리와 빛
      SHARDS.forEach((sh) => {
        const tau = b - SHARD_T0, land = shardLand(sh); if (tau <= 0) return;
        if (tau < land) {
          for (let j = 6; j >= 0; j--) { const [x, gy, h] = shardAt(sh, Math.max(0, tau - j * 0.02)); p.disc(x, gy - h, sh[3] * (1 - j * 0.12), j ? C[4] : C[5], j ? 0.35 * (1 - j / 7) : 1); }
          const [x, gy, h] = shardAt(sh, tau); p.disc(x, gy - h, sh[3] * 0.5, C[6], 1);
        } else {
          const q = (tau - land) / 0.4; if (q >= 1) return;
          const [x, gy] = shardAt(sh, land);
          for (let a = 0; a < TAU; a += 0.08) p.blend(x + Math.cos(a) * (4 + 16 * ease.outCubic(q)), gy + Math.sin(a) * (4 + 16 * ease.outCubic(q)) * SY, C[6], 0.8 * (1 - q));
          p.disc(x, gy, 5 * (1 - q), C[5], 0.6 * (1 - q));
        }
      });
      // 위로 솟는 기운 기둥 + 감아 오르는 나선 실 + 위로 오르며 작아지는 고리
      if (b < 0.9) {
        const kk = Math.pow(1 - b / 0.9, 1.2), top = 320 * ease.outCubic(clamp(b / 0.22)), W = 34;
        for (let h = 0; h < top; h++) { const fade = 1 - h / top; for (let dx = -W; dx <= W; dx++) { const q = Math.abs(dx) / (W * (1 - 0.35 * h / top)); if (q < 1) p.blend(TX + dx, -h, q < 0.3 ? C[6] : q < 0.6 ? C[5] : C[4], Math.min(1, kk * fade * Math.pow(1 - q, 1.1) * 1.1)); } }
        for (let i = 0; i < 2; i++) for (let h = 0; h < top; h += 0.8) {
          const ph = h * 0.07 - t * 14 + i * Math.PI, w = 20 * (1 - h / top * 0.6);
          if (Math.cos(ph) > 0) p.blend(TX + Math.sin(ph) * w, -h, C[6], 0.85 * kk * (1 - h / top));
          else p.blend(TX + Math.sin(ph) * w, -h, C[4], 0.3 * kk * (1 - h / top));
        }
        for (let j = 0; j < 4; j++) { const q = fr01(b * 1.6 + j / 4), h = top * q; flatRing(p, C, TX, -h, 44 * (1 - 0.6 * q), kk * (1 - q) * 0.8, t, j % 2 ? 2 : -2, 0); }
      }
    },
  };
}

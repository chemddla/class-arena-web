// 극참 시전 (히든): 3초 동안 내공을 끌어올림 — 무협 느낌. 시전 막대 진행에 맞춰 게임이 프레임을 고름 (처음 → 끝).
//   · 발밑에서 바닥이 갈라지며 금이 사방으로 뻗어 나감 (금 안쪽에 옅은 빛)
//   · 몸에서 기파가 퍼져 나가며 흙먼지 고리가 바깥으로 밀려남 (0.7초 → 0.35초마다, 갈수록 크게)
//   · 돌 조각들이 바닥에서 떠올라 몸 둘레에서 떨며 떠 있음
//   · 몸에서 흰빛 기운이 불꽃처럼 위로 일렁이며 타오름 + 위로 치솟는 바람 줄기
//   · 칼자루에 빛이 맺혀 이따금 가로로 반짝 · 1.6초부터 하늘빛 잔전기가 몸 둘레에서 튐
//   · 2.85 칼자루에서 가로로 날카로운 섬광(칼날이 번뜩이듯) + 큰 기파, 떠 있던 돌이 튕겨 나감 → 곧바로 극참 난사
// 좌표: 기준점(0, 0) = 발, 칼자루 = (16, -25), +x = 검사가 보는 쪽, 1 = 게임 화면 1px. 왼쪽을 보면 게임이 좌우로 뒤집어 그림
import { fit, clamp, smooth, rng, TAU } from "../../core/index.js";
import { MOON, MOON_SPARK, burst } from "./_sword.js";

export const meta = {
  name: "Geukcham charge",
  desc: "Wuxia-style power-up over three seconds: the ground cracks outward from the feet, qi pulses push rings of dust away, pebbles lift off and hover trembling round the body, a white qi aura flares upward like flame with rising wind streaks, light gathers and glints on the hilt, pale crackles start to jump; at the end a sharp horizontal blade-gleam flashes from the hilt with a big qi wave and the pebbles are flung away.",
  tags: ["sword", "charge", "aura", "wuxia", "hidden", "one-shot"],
  size: [240, 200],
  origin: [120, 150],
  duration: 3.0,
  loop: false,
  fps: 20,
  bg: "dark",
  options: {
    palette: MOON, sparks: MOON_SPARK, bolt: ["#ffffff", "#e0f2fe", "#a5d8ff", "#74b9f5"],
    dust: ["#6e675b", "#9a9282", "#c7bfad", "#e6dfd0"], rock: ["#2b2824", "#4a453d", "#6f685c", "#958d7e"], seed: 7,
  },
};

// 시전 자세(9·10번) 몸 윤곽 (칼집 뺌): 왼쪽(등) 허리 → 머리 위 → 오른쪽(얼굴·가슴) 허리. 기운 불꽃 밑동이 여기 붙음
const BODY = [[-7, -18], [-6, -26], [-5, -33], [-3, -40], [-1, -47], [1, -53], [4, -58], [8, -59], [12, -56], [17, -52], [21, -47], [22, -41], [17, -36], [15, -30], [15, -24], [16, -18]];
function onBody(v) { // v 0..1 → 윤곽 위의 점 + 바깥쪽 방향 x
  const f = v * (BODY.length - 1), i = Math.min(BODY.length - 2, Math.floor(f)), w = f - i, [ax, ay] = BODY[i], [bx, by] = BODY[i + 1];
  const tx = bx - ax, ty = by - ay, l = Math.hypot(tx, ty) || 1;
  return [ax + tx * w, ay + ty * w, ty / l]; // 시계 방향으로 도는 윤곽의 바깥 법선 x = ty/l
}
const HX = 16, HY = -25, GY = 0.3, BURST = 2.85; // GY = 바닥 원근 (세로 납작)

const f20 = (t) => Math.floor(t * 20);
function bolt(p, x0, y0, x1, y1, seed, B, a) {
  const R = rng(seed, 5);
  let pts = [[x0, y0], [x1, y1]];
  for (let lv = 0, amp = Math.hypot(x1 - x0, y1 - y0) * 0.3; lv < 3; lv++, amp *= 0.5) {
    const nx = [];
    for (let i = 0; i < pts.length - 1; i++) {
      const [ax, ay] = pts[i], [bx, by] = pts[i + 1], l = Math.hypot(bx - ax, by - ay) || 1, o = R.range(-amp, amp);
      nx.push(pts[i], [(ax + bx) / 2 - ((by - ay) / l) * o, (ay + by) / 2 + ((bx - ax) / l) * o]);
    }
    nx.push(pts[pts.length - 1]);
    pts = nx;
  }
  for (let i = 0; i < pts.length - 1; i++) {
    const [ax, ay] = pts[i], [bx, by] = pts[i + 1], n = Math.max(1, Math.ceil(Math.hypot(bx - ax, by - ay) * 1.5));
    for (let j = 0; j <= n; j++) p.blend(ax + ((bx - ax) * j) / n, ay + ((by - ay) * j) / n, B[i < 2 ? 0 : 1], a);
  }
  p.glowLine(x0, y0, x1, y1, 4, B[2], 0.2 * a);
}

export function draw(p, t, o) { paint(p, t, o, false); }

// back = true: 몸 뒤에 그리는 기운 불꽃만 (게임은 이 시트를 유닛보다 먼저 그림) · false: 나머지 전부 (유닛 위에 덮음)
export function paint(p, t, o, back) {
  const C = fit(o.palette, 7), S = fit(o.sparks, 4), Bc = fit(o.bolt, 4), D = fit(o.dust, 4), K = fit(o.rock, 4);
  const ramp = smooth(0, 2.7, t), u = t - BURST;

  if (!back) {
  // 1) 바닥 금: 발밑에서 7갈래로 꺾이며 뻗음 (중간에 잔가지). 갈수록 길어지고 터질 때 끝까지 뻗음
  const Rc = rng(o.seed, 1);
  for (let i = 0; i < 7; i++) {
    const a0 = (i / 7) * TAU + Rc.range(-0.3, 0.3), Lmax = Rc.range(34, 60);
    const grow = smooth(0.15 + i * 0.05, 2.2, t) * 0.75 + (u > 0 ? 0.25 * clamp(u / 0.05) : 0);
    const n = Math.floor(Lmax * grow), Rw = rng(o.seed, 20 + i);
    for (let s = 0, x = 0, y = 0, a = a0; s < n; s++) {
      if (s % 6 === 0) a = a0 + Rw.range(-0.5, 0.5);
      x += Math.cos(a); y += Math.sin(a) * GY;
      const k = 1 - s / Lmax;
      p.blend(x, y, K[0], 0.85 * k);
      if (s > 6) p.blend(x, y + 1, C[5], 0.35 * k * ramp);
      if (k > 0.5) p.blend(x, y - 1, K[1], 0.5 * k);
      if (s > 8 && s % 3 === 0) p.glow(x, y, 2.5, Bc[2], 0.25 * k * ramp); // 금 안쪽에서 새는 빛
      if (s === 18 && Rw.chance(0.7)) for (let b = 1, bx = x, by = y, ba = a + Rw.range(-1, 1); b < 10; b++) { bx += Math.cos(ba); by += Math.sin(ba) * GY; p.blend(bx, by, K[0], 0.6 * (1 - b / 10)); }
    }
  }

  // 2) 기파 + 흙먼지 고리: 몸에서 바깥으로 밀려 나감 (주기 0.7초 → 0.35초)
  const waves = [];
  for (let tw = 0.25; tw < Math.min(t, BURST); tw += 0.7 - 0.35 * smooth(0, 2.6, tw)) waves.push(tw);
  if (u >= 0) waves.push(BURST);
  for (const t0 of waves) {
    const last = t0 === BURST, big = last ? 1.6 : 0.7 + 0.5 * smooth(0, 2.6, t0), v = (t - t0) / (last ? 0.45 : 0.6);
    if (v < 0 || v > 1) continue;
    const r = 18 + 62 * big * Math.pow(v, 0.55), k = Math.pow(1 - v, 1.3);
    const Rd = rng(o.seed * 7 + Math.round(t0 * 100), 2);
    for (let i = 0; i < 26; i++) { // 흙먼지 뭉치: 들쭉날쭉한 거리·크기로 피어오르며 밀려남, 뒤쪽은 옅게
      const q = (i / 26) * TAU + Rd.range(-0.12, 0.12), rr = r * Rd.range(0.75, 1.1), sz = Rd.range(2, 4.5) * (0.5 + 0.8 * v) * Math.min(1, big);
      const x = Math.cos(q) * rr, y = Math.sin(q) * rr * GY - Rd.range(1, 10) * v, a = 0.4 * k * (Math.sin(q) < 0 ? 0.55 : 1) * Rd.range(0.6, 1);
      p.disc(x, y, sz, D[2], a * 0.7);
      p.disc(x, y, sz * 0.55, D[3], a * 0.5);
    }
  }

  // 3) 떠오르는 돌 조각: 바닥에서 떠올라 떨며 떠 있다가, 터지면 바깥으로 튕겨 나감
  const Rr = rng(o.seed, 3);
  for (let i = 0; i < 18; i++) {
    const q = Rr.range(0, TAU), d = Rr.range(16, 46), x0 = Math.cos(q) * d, y0 = Math.sin(q) * d * GY, on = 0.3 + i * 0.12;
    const hmax = Rr.range(10, 34), sz = Rr.range(1.4, 3), ph = Rr.range(0, TAU);
    if (t < on) continue;
    const lift = smooth(on, on + 0.6, t) * hmax * (0.6 + 0.4 * ramp);
    let x = x0 + Math.sin(t * 9 + ph) * 0.7, y = y0 - lift + Math.sin(t * 6 + ph) * 1.2;
    if (u > 0) { const fly = u * 220; x += Math.cos(q) * fly; y += Math.sin(q) * fly * GY - u * 60 + u * u * 400; }
    const k = u > 0 ? 1 - clamp(u / 0.15) : 1;
    if (k <= 0) continue;
    const rot = ph + t * (u > 0 ? 14 : 1.5), nv = 4 + (i % 2), pts = []; // 모난 돌: 4~5각, 천천히 구름
    for (let j = 0; j < nv; j++) { const a = rot + (j / nv) * TAU, rr = sz * (0.75 + 0.5 * ((i * 7 + j * 3) % 5) / 4); pts.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr]); }
    p.poly(pts, K[1], k);
    const top = pts.reduce((m, q) => (q[1] < m[1] ? q : m));
    p.blend(top[0], top[1] + 0.5, K[3], k); p.blend((top[0] + x) / 2, (top[1] + y) / 2, K[2], k); // 윗면 밝게
    if (u <= 0) p.blend(x0, y0 + 1, K[0], 0.3 * (1 - lift / 40)); // 바닥 그림자
  }

  }

  // 4) 기운: 몸에서 흰빛이 불꽃처럼 위로 일렁이며 타오름 + 위로 치솟는 바람 줄기
  const auraK = smooth(0.2, 1.0, t) * (u > 0 ? 1 - clamp(u / 0.12) : 1);
  if (back && auraK > 0) {
    p.glow(5, -32, 20 + 18 * ramp, Bc[3], (0.15 + 0.3 * ramp) * auraK);
    for (let i = 0; i < 22; i++) { // 기운 불꽃 혀: 몸 실루엣 가장자리(옆·머리 위)에서 바깥·위로 뻗어 일렁이며 가늘어짐. 몸 가운데는 비워 둠
      const Rf = rng(o.seed, 40 + i), [ex, ey, nx] = onBody(clamp(i / 21 + Rf.range(-0.02, 0.02)));
      if (Rf.range(0, 1) > 0.4 + 0.6 * ramp) continue;
      const bx = ex - nx * 2.5, by = ey + 2, sp = Rf.range(6, 10), ph = Rf.range(0, TAU); // 윤곽 안쪽(몸 뒤)에서 피어올라 실루엣 너머로 솟음
      const top = Math.abs(nx) < 0.5; // 머리 위 불꽃은 더 길게
      const L = (11 + 22 * ramp) * (0.55 + 0.45 * Math.sin(t * sp + ph) ** 2) * (top ? 1.4 : 1), k = auraK * Rf.range(0.55, 0.9);
      const dx = nx * 0.6, n = Math.ceil(L); // 옆 불꽃은 바깥으로 휘어 실루엣 밖으로 나옴
      for (let j = n; j >= 0; j--) { // 끝부터 그려 밑동의 흰 심이 위에 오게
        const v = j / n, x = bx + dx * L * v + Math.sin(v * 5 - t * sp + ph) * 1.6 * v, y = by - L * v, w = 2.2 * (1 - v) + 0.4;
        p.disc(x, y, w, Bc[2], 0.22 * k * (1 - v));
        if (w > 1.2) p.disc(x, y, w * 0.5, C[6], 0.5 * k * (1 - v));
        else p.blend(x, y, C[5], 0.7 * k * (1 - v));
      }
      p.glowLine(bx, by, bx + dx * L, by - L, 4, Bc[2], 0.22 * k);
    }
    const Rs = rng(o.seed, 9);
    for (let i = 0; i < 12; i++) { // 머리 위로 날리는 기운 불티
      const per = Rs.range(0.5, 0.9), v = (t / per + Rs.range(0, 1)) % 1, x = Rs.range(-14, 18) + Math.sin(t * 4 + i) * 2 * v, y = -48 - 30 * v * (0.5 + ramp);
      if (Rs.range(0, 1) > ramp) continue;
      p.dot(x, y, C[6], auraK * (1 - v));
      p.glow(x, y, 2, Bc[2], 0.2 * auraK * (1 - v));
    }
  }

  if (back) return;

  // 5) 칼자루에 맺히는 빛 · 이따금 가로로 반짝 · 잔전기
  const hk = u > 0 ? 0 : smooth(0.4, 2.6, t);
  if (hk > 0) {
    p.glow(HX, HY, 5 + 5 * hk, Bc[2], 0.5 * hk);
    p.dot(HX, HY, C[6], hk);
    const g = (t * (1 + 2 * ramp)) % 1;
    if (g < 0.25) { const k = Math.sin((Math.PI * g) / 0.25) * hk, L = 6 + 10 * hk; for (let dx = -L; dx <= L; dx++) p.blend(HX + dx, HY, C[6], k * (1 - Math.abs(dx) / L)); }
  }
  // 전기 기운: 0.8초부터 점점 많이. 바뀌는 주기 0.1초 (번개처럼 매번 다른 모양)
  if (t > 0.8 && u < 0) {
    const ek = smooth(0.8, 2.6, t), fb = Math.floor(t * 10);
    const nb = Math.floor(1 + 5 * ek); // ① 몸 둘레에서 바깥으로 튀는 잔전기
    for (let i = 0; i < nb; i++) {
      const Rb = rng(o.seed * 31 + fb, i), q = Rb.range(0, TAU), r0 = Rb.range(8, 14), r1 = r0 + Rb.range(10, 18 + 14 * ek);
      bolt(p, 5 + Math.cos(q) * r0, -32 + Math.sin(q) * r0 * 1.2, 5 + Math.cos(q) * r1, -32 + Math.sin(q) * r1, o.seed + fb * 7 + i, Bc, 0.8);
    }
    const na = Math.floor(1 + 3 * ek); // ② 몸 윤곽을 따라 두 점 사이를 건너뛰는 호
    for (let i = 0; i < na; i++) {
      const Rb = rng(o.seed * 37 + fb, i), v0 = Rb.range(0, 1), v1 = clamp(v0 + Rb.range(-0.3, 0.3)), [x0, y0, n0] = onBody(v0), [x1, y1, n1] = onBody(v1);
      bolt(p, x0 + n0 * 2, y0, x1 + n1 * 2, y1, o.seed + fb * 11 + i, Bc, 0.9);
    }
    const ng = Math.floor(2 * ek); // ③ 바닥 금으로 내리꽂히는 전기
    for (let i = 0; i < ng; i++) {
      const Rb = rng(o.seed * 41 + fb, i), q = Rb.range(0, TAU), d = Rb.range(14, 34), gx = Math.cos(q) * d, gy = Math.sin(q) * d * GY;
      bolt(p, 5 + Rb.range(-8, 8), -14, gx, gy, o.seed + fb * 13 + i, Bc, 0.85);
      p.glow(gx, gy, 4, Bc[2], 0.4);
    }
    if (ek > 0.3) { // ④ 칼자루에 감기는 작은 전기
      const Rb = rng(o.seed * 43 + Math.floor(t * 20), 0), q = Rb.range(0, TAU);
      bolt(p, HX + Math.cos(q) * 3, HY + Math.sin(q) * 3, HX + Math.cos(q + 2) * 9, HY + Math.sin(q + 2) * 7, o.seed + f20(t), Bc, ek);
    }
  }

  // 6) 터짐: 칼자루에서 가로로 날카로운 섬광 (앞쪽이 길게, 칼날이 번뜩이듯) + 짧은 세로 빛살 + 불티
  if (u >= 0) {
    const k = Math.pow(1 - clamp(u / 0.15), 0.9);
    p.glow(HX, HY, 30, Bc[3], 0.6 * k);
    p.glow(HX, HY, 10, C[6], k);
    const Lf = 110 * (0.5 + 0.5 * k), Lb = 40 * (0.5 + 0.5 * k);
    p.glowLine(HX - Lb, HY, HX + Lf, HY, 4, Bc[1], 0.8 * k);
    for (let dx = -Lb; dx <= Lf; dx++) p.blend(HX + dx, HY, C[6], k * (1 - (dx < 0 ? -dx / Lb : dx / Lf)));
    for (let dy = -14; dy <= 14; dy++) p.blend(HX, HY + dy, C[6], 0.7 * k * (1 - Math.abs(dy) / 14));
    for (let i = 0; i < 8; i++) burst(p, t, BURST + i * 0.004, HX, HY, (i / 8) * TAU, 0.4, 4, o.seed + 60 + i, S);
    if (u < 0.1) for (let i = 0; i < 7; i++) { // 터질 때 사방으로 뻗는 큰 번개
      const q = (i / 7) * TAU + 0.3, L = 34 + (i % 3) * 10;
      bolt(p, HX, HY, HX + Math.cos(q) * L, HY + Math.sin(q) * L * 0.8, o.seed + 90 + i + f20(t) * 9, Bc, k);
    }
  }
}

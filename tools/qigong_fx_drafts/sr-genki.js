// 기공사 SR 기공옥 · 청천옥 (히든, 2판 2026-11-17 사용자: "선의 느낌이 너무 많아. 크니까 선 없이 자연스럽게 디테일을 세부적으로")
//   고리·꼬리선·물결선을 전부 빼고 덩어리(부피)와 번짐으로만 그림. 큰 이펙트라 잡음(fbm)으로 결을 줌
//   모으기: 발밑 기운이 숨 쉬듯 번지고 기운 자락이 피어오름 → 떠올라 머리 위 기 덩어리를 키움
//           (사방·땅에서 부드러운 기운 자락이 휘어 들며 빨려 듦 · 덩어리 속은 소용돌이치는 기의 결, 바깥은 위로 타오르는 기운 · 둘레 기운이 숨 쉬듯 조여 듦)
//   던지기: 기운 자락을 흘리며 내리꽂힘 · 떨어질 자리 땅이 먼저 밝아짐
//   터짐: 빛 기둥이 솟고 · 소용돌이 결이 있는 반구 기운이 부풀었다 속부터 비며 가라앉음 · 땅을 덮으며 퍼지는 빛(앞머리는 잡음으로 흐트러짐)
//         · 땅을 굴러 퍼지는 기운 안개 · 떠올라 흩어지는 기 알갱이 · 남은 기가 천천히 피어오름
import { Rng, fit, noise2, TAU } from "../../core/index.js";
import { QI_SKY, soft, CORE, MINT, Drops, eo, ei, ss, lerp } from "./_sr.js";

const GROUND = 1.0, RISE = 1.6, THROW = 3.8, HIT = 4.4, RMAX = 36, XT = 240;
export const DUMMIES = [XT - 120, XT - 60, XT + 70, XT + 130];
export const meta = { size: [660, 360], origin: [150, 336], loop: false, fps: 30, bg: "dark", name: "기공사 SR 청천옥", desc: "머리 위 거대한 기 덩어리를 내리꽂음", tags: ["qigong"], duration: 7.4, options: { palette: QI_SKY, seed: 7 } };
export const TIMES = { GROUND, RISE, THROW, HIT };

const fbm = (x, y) => noise2(x, y) * 0.55 + noise2(x * 2.1 + 5.2, y * 2.1 - 1.7) * 0.3 + noise2(x * 4.3 - 3.1, y * 4.3 + 8.4) * 0.15;   // -1..1
const level = (C, b) => b > 0.86 ? CORE : b > 0.66 ? C[6] : b > 0.46 ? C[5] : b > 0.26 ? C[4] : b > 0.1 ? C[3] : C[2];
// 반투명일 때는 짙은 하늘빛만 (옅은 흰빛을 반투명으로 얹으면 어두운 배경에서 회색으로 탁해짐), 흰빛은 진할 때만
const tint = (C, b, a) => a < 0.45 ? (b > 0.6 ? C[4] : C[3]) : a < 0.7 ? (b > 0.75 ? C[5] : b > 0.4 ? C[4] : C[3]) : level(C, b);

// 기 덩어리: 소용돌이치는 결(fbm을 나선으로 비틀어 돌림) · 심이 가장 밝음 · 바깥은 위로 타오르는 기운으로 녹아듦 (선 없음)
function mass(p, C, x, y, r, t, k = 1, sx = 1, sy = 1, breathe = 0) {
  if (r < 1) return;
  p.glow(x, y, r * 3.2, C[3], 0.3 * k);
  p.glow(x, y, r * 1.4, C[5], 0.18 * k);
  const R = r * 1.9;
  soft(p, x - R * sx, y - R * 1.15 * sy, x + R * sx, y + R * 0.8 * sy, (px, py, out) => {
    const dx = (px - x) / sx / r, dy = (py - y) / sy / r, d = Math.hypot(dx, dy), an = Math.atan2(dy, dx);
    const sw = an - t * 1.4 - (1 - Math.min(d, 1)) * 2.6;                           // 안쪽일수록 많이 비틀림 → 심으로 감겨 드는 소용돌이
    const turb = fbm(Math.cos(sw) * d * 2.4 + t * 0.25, Math.sin(sw) * d * 2.4 - t * 0.2);
    const up = Math.max(0, -dy / Math.max(d, 0.01));
    const rise = noise2(dx * 1.1, dy * 1.1 + t * 1.3) * 0.5 + 0.5;                 // 위로 흘러가는 굵은 결 (한 겹, 느리게)
    const edgeN = noise2(Math.cos(an) * 1.2 + t * 0.45, Math.sin(an) * 1.2 - t * 0.35) * 0.5 + 0.5;
    const E = (1.12 + 0.14 * edgeN + up * up * 0.42 * rise) * (1 + breathe);
    if (d > E) return;
    const fall = (1 - ss(0.74, E, d)) ** 1.25;                                        // 몸통에서 바깥까지 한 곡선으로 녹아 나감
    // 두 갈래 나선 팔(은하처럼 심으로 감겨 듦)과 그 사이 짙은 결
    const s = an * 2 - Math.log(d + 0.05) * 3.4 + t * 2.4 + turb * 0.6;
    const arm = Math.max(0, Math.cos(s)) ** 3, lane = Math.max(0, -Math.cos(s)) ** 4;
    // 심에서 은은하게 뻗는 빛살 (천천히 돎)
    const ray = Math.max(0, Math.cos(an * 7 - t * 0.7 + turb * 0.8)) ** 8 * Math.max(0, 1 - d * 1.4) * 0.45;
    // 속을 맴도는 밝은 기 매듭 넷
    let knot = 0;
    for (let i = 0; i < 4; i++) {
      const ka = t * (1.3 + i * 0.35) * (i % 2 ? -1 : 1) + i * 1.57, kr = 0.5 + 0.18 * Math.sin(t * 0.9 + i * 2);
      knot += Math.exp(-((dx - Math.cos(ka) * kr) ** 2 + (dy - Math.sin(ka) * kr) ** 2) / 0.012);
    }
    const rg = Math.min(1, d * 2.5);
    const b = Math.pow(Math.max(0, 1 - d), 1.4) * 0.8 + turb * 0.22 * rg + arm * 0.34 * rg - lane * 0.26 * rg + ray + knot * 0.45 + 0.12;
    out.a = k * (0.97 - 0.2 * Math.min(d, 1)) * fall;
    out.k = k * 0.22 * fall * (0.4 + 0.6 * rise) * ss(0.6, 1, d);                     // 가장자리는 빛으로 은은하게
    if (d < 0.18) out.k = 0.45 * k * (1 - d / 0.18);
    if (knot > 0.5) out.k = 0.25 * k * Math.min(1, knot);
    if (arm > 0.7 && d > 0.45 && d < 0.85 && b < 0.7) return MINT;                    // 바깥 팔 끝은 박하빛
    return d > 0.74 ? tint(C, b + 0.15, out.a) : level(C, b);
  });
}

// 바닥 빛: 납작한 타원 안을 채운 번짐 (앞머리 front 근처가 가장 밝고 안쪽으로 길게 옅어짐, 가장자리는 잡음으로 흐트러짐)
function groundLight(p, C, x, rx, k, t, front = 0.6, sy = 0.24, rays = 0) {
  if (rx < 2 || k <= 0.01) return;
  const ry = Math.min(rx * sy, 46);   // 넓게 퍼져도 땅에 붙어 납작하게 (높이 솟으면 화면 전체에 막이 낌)
  soft(p, x - rx * 1.15, -ry * 1.15, x + rx * 1.15, ry * 1.15, (px, py, out) => {
    const dx = (px - x) / rx, dy = py / ry, d = Math.hypot(dx, dy), an = Math.atan2(dy, dx);
    const edge = 1 + 0.12 * fbm(Math.cos(an) * 2 + t * 0.6, Math.sin(an) * 2 - t * 0.4);
    const e = d / edge; if (e > 1) return;
    const band = e > front ? 1 - ((e - front) / (1 - front)) ** 2 : 0.35 + 0.65 * (e / front) ** 2;
    const ray = rays ? (1 - rays) + rays * Math.max(0, Math.cos(an * 13 + fbm(Math.cos(an) * 3, Math.sin(an) * 3) * 2.5)) ** 2 * (0.4 + e) : 1;   // 땅 위로 뻗는 빛 갈래
    const v = k * band * ray * (py < 0 ? 0.55 : 1) * (0.75 + 0.25 * fbm(px * 0.04 + t, py * 0.12));
    out.a = v * 0.3 * (1 - ss(0.5, 1, e)); out.k = v * 0.55; return band > 0.8 ? C[5] : C[4];   // 흰빛을 반투명으로 칠하면 회색으로 탁해져서 빛을 더함
  });
}

// 기운 기둥: 아래가 굵고 위로 가늘어지며 옅어짐 · 가장자리는 잡음으로 일렁임 · 속을 두 가닥 나선 결이 감아 오름 · 위로 솟는 결
function pillar(p, C, x, w, H, k, t) {
  if (H < 2 || k <= 0.01) return;
  p.glowLine(x, 0, x, -H * 0.8, w * 2.4, C[3], 0.25 * k);
  soft(p, x - w * 1.8, -H, x + w * 1.8, 0, (px, py, out) => {
    const h = -py / H, wl = w * (1 - 0.55 * h) * (1 + 0.28 * fbm(py * 0.045 - t * 4, x * 0.1));
    const sx = (px - x) / wl, a = Math.abs(sx);
    if (a > 1) return;
    let hel = 0;
    for (let j = 0; j < 2; j++) { const ph = py * 0.09 + t * 15 + j * Math.PI; hel += Math.exp(-(((sx - Math.sin(ph) * 0.6) / 0.22) ** 2)) * (0.35 + 0.65 * (0.5 + 0.5 * Math.cos(ph))); }
    const rise = Math.max(0, noise2(sx * 2.5 + x, py * 0.05 + t * 7)) ** 2;
    const fade = (1 - h) ** 1.3, b = ((1 - a * a) * 0.8 + hel * 0.3 + rise * 0.3) * fade + 0.1;
    out.a = k * (1 - a * a) * fade * 0.85; out.k = k * 0.25 * (1 - a) * fade;
    return a < 0.15 && h < 0.6 && out.a > 0.6 ? CORE : tint(C, b, out.a);
  });
}

// 먼저 내달리는 압력 반구: 옅게 채운 기운 (앞머리 쪽이 짙고 안쪽으로 길게 옅어짐), 가장자리는 굵은 잡음으로 일렁임
function shock(p, C, x, R, k, t) {
  if (R < 2 || k <= 0.01) return;
  const ry = R * 0.62;
  soft(p, x - R * 1.1, -ry * 1.1, x + R * 1.1, 0, (px, py, out) => {
    const dx = (px - x) / R, dy = py / ry, d = Math.hypot(dx, dy), an = Math.atan2(dy, dx);
    const e = d / (1 + 0.06 * noise2(Math.cos(an) * 2 + t, Math.sin(an) * 2)); if (e > 1) return;
    const band = e > 0.82 ? 1 - ((e - 0.82) / 0.18) ** 2 : 0.15 + 0.85 * (e / 0.82) ** 3;
    const v = k * band; out.a = v * 0.22; out.k = v * 0.35; return C[4];
  });
}

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed), D = new Drops(R);
  const O = { x: 2, y: -120, r: 3 }, W = [];   // W: 기운 자락 (부드러운 덩어리, 속도 방향으로 길쭉)
  let t = 0, boom = false, fx = 0, fy = 0;
  const F = [], GY = [];   // F: 튀었다 녹는 작은 기 덩어리 조각 · 떠오르는 남은 기 구슬, GY: 둘레에서 솟는 기운 분출
  const wisp = (x, y, vx, vy, o2 = {}) => W.push({ x, y, vx, vy, s: o2.s || R.range(5, 9), life: o2.life || 1.4, age: 0, pull: o2.pull ?? 1, a: o2.a ?? 0.22 });
  return {
    update(dt) {
      t += dt;
      if (t < THROW) {
        O.r = 3 + (RMAX - 3) * Math.pow(t / THROW, 0.8);
        O.y = -(t < GROUND ? 112 : lerp(112, 126, ss(GROUND, RISE, t))) - O.r;
        for (let n = (14 + 30 * t / THROW) * dt; n > 0; n--) if (R.chance(Math.min(1, n))) {   // 사방·땅에서 휘어 드는 기운 자락
          const fromGround = R.chance(0.45), a = R.range(0, TAU), d = R.range(150, 230);
          const x = fromGround ? O.x + R.range(-220, 220) : O.x + Math.cos(a) * d, y = fromGround ? -R.range(0, 6) : O.y + Math.sin(a) * d * 0.7;
          const tx = O.x - x, ty = O.y - y, tl = Math.hypot(tx, ty) || 1, sw = R.chance(0.5) ? 1 : -1;
          wisp(x, y, (tx / tl) * 40 - (ty / tl) * 70 * sw, (ty / tl) * 40 + (tx / tl) * 70 * sw + (fromGround ? -60 : 0), { pull: 1 });
        }
        for (let n = (60 * t / THROW + 20) * dt; n > 0; n--) if (R.chance(Math.min(1, n))) {   // 고운 기 알갱이도 같이 빨려 듦
          const a = R.range(0, TAU), d = R.range(60, 200);
          D.bead(O.x + Math.cos(a) * d, O.y + Math.sin(a) * d * 0.8, O, { vx: -Math.sin(a) * d * 1.2, vy: Math.cos(a) * d, pull: d * 6, life: 1.6 });
        }
        if (R.chance(0.5)) wisp(R.range(-40, 40), -2, R.range(-10, 10), R.range(-50, -25), { pull: 0, s: R.range(3, 5), life: 1.2, a: 0.2 });   // 발밑에서 피어오르는 기운
      } else if (t < HIT) {
        const e = ei((t - THROW) / (HIT - THROW));
        fx = lerp(O.x, XT, e); fy = lerp(O.y, -O.r * 0.55, e);
        for (let i = 0; i < 1; i++) { const a = R.range(0, TAU); wisp(fx + Math.cos(a) * O.r * 0.8, fy + Math.sin(a) * O.r * 0.8, R.range(-40, 40) - (XT - O.x) * 0.3, R.range(-60, 0), { pull: 0, s: R.range(5, 9), life: 0.6, a: 0.22 }); }
      } else if (!boom) {
        boom = true;
        for (let i = 0; i < 160; i++) {   // 떠올라 흩어지는 기 알갱이
          const a = -Math.PI * R.range(0.05, 0.95), sp = R.range(140, 520);
          D.drop(XT + Math.cos(a) * 20, -8, Math.cos(a) * sp * 1.3, Math.sin(a) * sp * 0.8, { r: R.chance(0.3) ? 2 : 1, life: R.range(1.4, 2.2) });
        }
        for (let i = 0; i < 56; i++) { const s = R.chance(0.5) ? 1 : -1; wisp(XT + R.range(-30, 30), -R.range(2, 20), s * R.range(180, 460), -R.range(0, 30), { pull: 0, s: R.range(12, 22), life: R.range(1.2, 2.0), a: 0.2 }); }   // 땅을 굴러 퍼지는 기운 안개
        for (let i = 0; i < 14; i++) {   // 사방으로 높이 튀었다 녹는 기 덩어리
          const a = -Math.PI * (0.1 + 0.8 * (i + R.range(0.1, 0.9)) / 14), sp = R.range(220, 360);
          F.push({ x: XT, y: -18, vx: Math.cos(a) * sp * 1.3, vy: Math.sin(a) * sp, g: 240, r: R.range(5, 9), age: 0, life: R.range(0.9, 1.3), ph: R.range(0, 9) });
        }
        for (let i = 0; i < 12; i++) {   // 둘레에서 시차를 두고 바깥으로 번져 가며 솟는 기운 분출
          const s = i % 2 ? 1 : -1, dd = 45 + (i >> 1) * 40 + R.range(-10, 10), x = XT + s * dd;
          GY.push({ x, t0: HIT + 0.06 + dd / 700, H: R.range(90, 170) * (1 - dd / 340), w: R.range(7, 12) * (1 - dd / 500) });
        }
        for (let i = 0; i < 16; i++) D.at(HIT + 0.8 + i * 0.08, () => F.push({ x: XT + R.range(-170, 170), y: -R.range(4, 30), vx: R.range(-6, 6), vy: R.range(-40, -20), g: 0, r: R.range(2, 3.4), age: 0, life: R.range(1.2, 1.8), ph: R.range(0, 9) }));   // 남아 떠오르는 기 구슬
        for (let i = 0; i < 60; i++) D.at(HIT + 0.7 + i * 0.03, () => wisp(XT + R.range(-200, 200), -2, R.range(-8, 8), R.range(-45, -20), { pull: 0, s: R.range(3, 6), life: 1.3, a: 0.18 }));   // 남은 기가 피어오름
      }
      for (const w of W) {
        w.age += dt;
        if (w.pull) {
          const dx = O.x - w.x, dy = O.y - w.y, d = Math.hypot(dx, dy) || 1, f = 260 * w.pull;
          w.vx += dx / d * f * dt; w.vy += dy / d * f * dt;
          const dr = Math.pow(0.35, dt); w.vx *= dr; w.vy *= dr;
          if (d < O.r * 0.8 || t >= THROW) w.age = w.life;
        } else { const dr = Math.pow(0.3, dt); w.vx *= dr; w.vy = w.vy * dr - 10 * dt; }
        w.x += w.vx * dt; w.y += w.vy * dt;
      }
      for (let i = W.length - 1; i >= 0; i--) if (W[i].age >= W[i].life) W.splice(i, 1);
      for (const f of F) {
        f.age += dt; f.vy += f.g * dt;
        const dr = Math.pow(f.g ? 0.5 : 0.8, dt); f.vx *= dr; if (!f.g) f.vy *= dr;
        f.x += f.vx * dt; f.y = Math.min(-f.r * 0.6, f.y + f.vy * dt);
        if (f.g && R.chance(0.5)) D.drop(f.x, f.y, f.vx * 0.2, -20, { life: 0.6 });   // 녹으며 알갱이를 흘림
      }
      for (let i = F.length - 1; i >= 0; i--) if (F[i].age >= F[i].life) F.splice(i, 1);
      D.update(dt, t);
    },
    draw(p) {
      if (t < THROW) {   // 발밑 기운: 숨 쉬듯 번짐 (고리 없음)
        groundLight(p, C, 0, (24 + 56 * ss(0, THROW, t)) * (1 + 0.06 * Math.sin(t * 5)), 0.45, t, 0.15);
        if (t > 0.3) p.glow(O.x, O.y, 220, C[3], 0.12 * ss(0.3, THROW, t));
      }
      if (t >= THROW - 0.4 && t < HIT) {   // 떨어질 자리 땅이 먼저 밝아짐
        const u = ss(THROW - 0.4, HIT, t);
        groundLight(p, C, XT, 20 + 50 * u, 0.4 * u, t, 0.1);
      }
      if (t >= HIT && t < HIT + 2.2) {   // 터짐: 땅을 덮으며 퍼지는 빛
        const u = (t - HIT) / 2.2;
        groundLight(p, C, XT, 40 + 330 * eo(u * 1.3), 0.85 * (1 - ss(0.35, 1, u)), t, 0.72, 0.55);
        const u2 = (t - HIT - 0.5) / 1.2;   // 뒤따르는 둘째 진동
        if (u2 > 0 && u2 < 1) groundLight(p, C, XT, 30 + 200 * eo(u2), 0.5 * (1 - u2), t + 3, 0.8, 0.24, 0.4);
        const u0 = (t - HIT) / 0.55;        // 먼저 내달리는 압력 반구 (옅게 채운 기운, 앞머리 쪽이 짙음)
        if (u0 < 1) shock(p, C, XT, 30 + 330 * eo(u0), 1 - ss(0.3, 1, u0), t);
      }
      for (const g of GY) {   // 둘레 기운 분출
        const u = (t - g.t0) / 0.6; if (u < 0 || u >= 1) continue;
        pillar(p, C, g.x, g.w * (1 - 0.4 * u), g.H * eo(u * 1.8), 1 - ss(0.4, 1, u), t + g.x);
      }
      for (const w of W) {   // 기운 자락: 속도 방향으로 길쭉한 부드러운 덩어리
        const u = w.age / w.life, a = w.a * Math.sin(Math.PI * Math.min(1, u * 1.15)), sp = Math.hypot(w.vx, w.vy) || 1;
        const ux = w.vx / sp, uy = w.vy / sp, L = w.s * (1 + Math.min(0.8, sp / 160)), S = w.s * (1 - 0.3 * u);
        soft(p, w.x - L, w.y - L, w.x + L, w.y + L, (px, py, out) => {
          const dx = px - w.x, dy = py - w.y, along = (dx * ux + dy * uy) / L, side = (-dx * uy + dy * ux) / S, q = along * along + side * side;
          if (q >= 1) return; const v = a * (1 - q) ** 2.2; out.a = v * 0.45; out.k = v * 0.7; return C[4];
        });
      }
      if (t < THROW) mass(p, C, O.x, O.y, O.r, t, 1, 1, 1, 0.06 * Math.sin(t * (4 + 6 * t / THROW)));   // 둘레 기운이 점점 빠르게 숨 쉼
      else if (t < HIT) {
        const u = (t - THROW) / (HIT - THROW);
        mass(p, C, fx, fy, O.r, t, 1, 1 - 0.08 * u, 1 + 0.12 * u, 0.15 * u);
      } else if (t < HIT + 1.8) {
        const u = (t - HIT) / 1.8;
        // 터지는 순간 온 화면을 덮는 빛
        if (u < 0.12) { const f = 1 - u / 0.12; p.glow(XT, -40, 460, C[4], 0.55 * f); p.glow(XT, -20, 120, C[6], 0.7 * f); }
        // 빛 기둥: 솟구쳐 오르며 속을 나선 결이 감아 돎, 위로 옅어짐 · 꼭대기에서 기운 구름이 넓게 퍼짐
        const pk = 1 - ss(0.05, 0.55, u);
        if (pk > 0) pillar(p, C, XT, 40 * (1 - 0.4 * u), 340 * eo(u * 5), pk, t);
        const cu = (u - 0.04) / 0.6;
        if (cu > 0 && cu < 1) { const ck = ss(0, 0.15, cu) * (1 - ss(0.4, 1, cu)), top = -340 * eo(u * 5); p.glow(XT, top + 30, 60 + 90 * eo(cu), C[4], 0.35 * ck); p.glow(XT, top + 40, 24, C[6], 0.4 * ck); }   // 기둥 꼭대기에서 번지는 빛
        // 땅에 닿는 순간 눌려 납작해지는 덩어리
        if (u < 0.1) { const q = u / 0.1; mass(p, C, XT, -O.r * 0.5 * (1 - q), O.r * (1 + 0.5 * q), t, 1 - q, 1 + 0.7 * q, 1 - 0.6 * q, 0.2); }
        // 반구 기운: 소용돌이 결 · 부풀었다 속부터 비며 가라앉음
        const rx = 240 * eo(u * 1.8), ry = 160 * eo(u * 2.1) * (1 - ss(0.45, 1, u)), a = 1 - ss(0.6, 1, u), hollow = ss(0.2, 0.75, u);
        if (ry > 1 && a > 0) {
          p.glow(XT, -ry * 0.4, rx, C[3], 0.25 * a);
          soft(p, XT - rx * 1.2, -ry * 1.45, XT + rx * 1.2, 0, (px, py, out) => {
            const dx = (px - XT) / rx, dy = py / ry, d = Math.hypot(dx, dy);
            const turb = fbm(dx * 3 + t * 0.4, dy * 3 + t * 1.4);                     // 위로 소용돌이쳐 오르는 결
            const an = Math.atan2(dy, dx), up = Math.max(0, -dy / Math.max(d, 0.01));
            const E = 1.08 + 0.1 * (noise2(Math.cos(an) * 1.5 + t * 0.5, Math.sin(an) * 1.5) * 0.5 + 0.5) + up * up * 0.18 * (noise2(dx * 1.4, dy * 1.4 + t * 1.5) * 0.5 + 0.5);
            if (d > E) return;
            const fall = (1 - ss(0.78, E, d)) ** 1.25;
            const base = 0.35 * (1 + dy);                                              // 땅에 가까울수록 밝음
            const col = Math.max(0, noise2(dx * 7 + 3, dy * 1.4 + t * 2.6)) ** 2 * 0.5;      // 돔 속에서 솟아오르는 기둥 결
            const swirl = Math.max(0, Math.cos(an * 3 - Math.log(d + 0.05) * 2.5 + t * 3)) ** 3 * 0.3 * Math.max(0, 1 - d);   // 바닥 가운데 감기는 소용돌이
            const lane = Math.max(0, noise2(dx * 4 - 5, dy * 4 + t * 1.2)) ** 3 * 0.35;     // 짙은 결 (명암 대비)
            const b = (1 - Math.min(d, 1) * 0.6) * (1 - hollow * Math.max(0, 1 - d) ** 1.2) + turb * 0.22 + base + col + swirl - lane;
            const v = a * (1 - hollow * Math.max(0, 1 - d) ** 1.5) * Math.min(1.2, Math.max(0.25, b)) * fall;
            out.a = v * 0.35; out.k = v * 0.4; return tint(C, b, out.a);
          });
        }
      }
      F.forEach(f => { const u = f.age / f.life; mass(p, C, f.x, f.y, f.r * (1 - 0.5 * u), t + f.ph, (1 - u) ** 1.3 * Math.min(1, f.age * 10), 1, 1, 0.1); });   // 조각·남은 구슬
      D.draw(p, C);
    },
  };
}

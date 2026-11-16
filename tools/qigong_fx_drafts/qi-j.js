// 시안 J 실타래 기구슬 (반짝임 없음): 진한 기운 구슬 속에 기운 실이 엉켜 돌고, 둘레는 일렁이는 기운 막. 뒤로 연기 같은 기운 꼬리.
// 맞는 순간: 박힘(구슬이 납작하게 눌림) → 응축(잠깐 오그라듦) → 터짐(빛나는 기운 껍질이 부풀고 기운 혀가 사방으로 뻗음).
//   먼지·안개 입자·별빛·번쩍·불꽃 가루·선 고리·바닥 이펙트 없음 (사용자: 먼지 폭발이 아니라 기가 사방으로 터지는 느낌)
import { Particles, Lights, P, Rng, fit, TAU, clamp, ease, noise2 } from "../../core/index.js";
import { QI_GOLD, H, X1, CHARGE, FLY, HIT, base, qiGather } from "./_qi.js";

export const meta = { ...base, size: [320, 124], origin: [26, 112], name: "기공사 J 실타래 기구슬", desc: "기운 실이 엉켜 도는 구슬, 맞으면 실이 풀리며 터짐 (반짝임 없음)", tags: ["qigong"], duration: HIT + 1.4, options: { palette: QI_GOLD, seed: 4, radius: 8, burst: 'wave' } };

const LOOPS = [];
for (let i = 0; i < 10; i++) LOOPS.push([(i * 2.39) % Math.PI, (i * 1.37) % TAU, (i % 2 ? 1 : -1) * (3 + (i % 4))]);
const SQUASH = 0.045, IMPLODE = 0.085;   // 맞은 뒤: 박힘 끝 · 응축 끝(= 터지는 순간)

// 기가 사방으로 퍼지며 터지는 모습 두 가지 (불꽃·먼지·선 고리·바닥 이펙트 없음, 진짜 반투명으로 칠함)
//   wave   기파: 두툼하고 부드러운 빛의 기운 물결 세 겹이 차례로 사방으로 퍼짐 (안쪽은 옅은 기운으로 차 있다가 빠짐)
//   sphere 구체 팽창: 구슬이 큰 빛 구체로 부풀며 퍼짐. 가장자리가 밝고 속은 옅으며, 속의 기운 실도 같이 커지다 흩어짐
const wob = (a, t, k = 1) => 1 + 0.1 * k * noise2(Math.cos(a) * 2.2 + t * 6, Math.sin(a) * 2.2 - t * 5);

function centerFlash(p, C, x, y, e, R0) {
  if (e >= 0.16) return;
  const k = 1 - e / 0.16;
  p.disc(x, y, R0 * (1 + e * 5), C[5], 0.8 * k);
  p.disc(x, y, R0 * (0.5 + e * 2.5), C[6], 0.75 * k);
}

function waveBurst(p, C, x, y, e, t, R0) {
  centerFlash(p, C, x, y, e, R0);
  const RM = R0 * 4.6;
  const x0 = Math.floor(x - RM - 2), x1 = Math.ceil(x + RM + 2), y0 = Math.floor(y - RM - 2), y1 = Math.ceil(y + RM + 2);
  const W = [[0, 0.9], [0.14, 0.6], [0.28, 0.38]].map(([d, s]) => {   // [늦게 출발, 세기]
    const ew = (e - d) / 0.55;
    return ew <= 0 || ew >= 1 ? null : { r: R0 * (0.8 + 3.8 * ease.outCubic(ew)), th: R0 * (1.1 * (1 - ew) + 0.4), k: s * Math.pow(1 - ew, 1.6), fill: d === 0 ? 0.22 * Math.pow(1 - ew, 3) : 0 };
  }).filter(Boolean);
  if (!W.length) return;
  for (let py = y0; py <= y1; py++) for (let px = x0; px <= x1; px++) {
    const dx = px + 0.5 - x, dy = py + 0.5 - y, a = Math.atan2(dy, dx), d = Math.hypot(dx, dy) / wob(a, t);
    let best = 0, fill = 0;
    for (const w of W) {
      const dd = Math.abs(d - w.r) / w.th;
      if (dd < 1) best = Math.max(best, (1 - dd * dd) * w.k);
      if (d < w.r) fill = Math.max(fill, w.fill);
    }
    if (best > 0.02) p.blend(px + 0.5, py + 0.5, best > 0.6 ? C[6] : best > 0.3 ? C[5] : C[4], Math.min(1, best * 1.1));
    else if (fill > 0.02) p.blend(px + 0.5, py + 0.5, C[5], fill);
  }
}

function sphereBurst(p, C, x, y, e, t, R0) {
  centerFlash(p, C, x, y, e, R0);
  const Rs = R0 * (1 + 3.2 * ease.outCubic(e)), fade = Math.pow(1 - e, 1.3);
  const x0 = Math.floor(x - Rs * 1.15), x1 = Math.ceil(x + Rs * 1.15), y0 = Math.floor(y - Rs * 1.15), y1 = Math.ceil(y + Rs * 1.15);
  for (let py = y0; py <= y1; py++) for (let px = x0; px <= x1; px++) {
    const dx = px + 0.5 - x, dy = py + 0.5 - y, a = Math.atan2(dy, dx), v = Math.hypot(dx, dy) / (Rs * wob(a, t, 1.4));
    if (v > 1) continue;
    const al = (0.18 + 0.75 * v * v * v) * fade;          // 가장자리가 밝은 빛 구체
    p.blend(px + 0.5, py + 0.5, v > 0.85 ? C[6] : v > 0.6 ? C[5] : C[4], al);
  }
  threads(p, C, x, y, Rs * 0.9, t, fade * 0.9, 1, 1, 1.0001);   // 속의 기운 실도 함께 커짐
}

// 구슬 (sx·sy: 가로·세로 눌림)
function orb(p, C, x, y, r, t, k = 1, sx = 1, sy = 1) {
  p.glow(x, y, r * 2.4, C[3], 0.16 * k);
  p.disc(x, y, (r + 2.5) * Math.max(sx, sy), C[3], 0.3 * k);   // 기운 막
  p.shade(x - r * sx - 1, y - r * sy - 1, x + r * sx + 1, y + r * sy + 1, (px, py, out) => {
    const dx = (px - x) / sx, dy = (py - y) / sy, d = Math.hypot(dx, dy) / r;
    if (d > 1.02) return 0;
    out.a = k;
    const lit = clamp(1 - d * 0.95 - (dx + dy) / r * 0.1);
    return d > 0.9 ? C[4] : lit > 0.7 ? C[4] : lit > 0.35 ? C[3] : C[2];
  });
  threads(p, C, x, y, r, t, k, sx, sy, 1);
}

// 기운 실: 기울어진 원 궤도 (grow로 풀려 커짐, 커질수록 옅어지고 끊김)
function threads(p, C, x, y, r, t, k, sx, sy, grow) {
  LOOPS.forEach(([tilt, yaw, sp], i) => {
    if (grow > 1 && i % 2) return;   // 풀릴 때는 다섯 가닥만: 굵직한 고리로 읽히게
    const ct = Math.cos(tilt) * 0.999, st = Math.sin(tilt), cy = Math.cos(yaw + t * 1.5), sy2 = Math.sin(yaw + t * 1.5);
    const rr = r * (0.5 + 0.45 * ((i * 0.37) % 1)) * (grow > 1 ? grow * (0.8 + 0.4 * ((i * 0.61) % 1)) : 1);
    const gap = grow > 1 ? 0.08 + 0.3 * clamp((grow - 1) / 5) : 0;   // 풀릴수록 실이 군데군데 끊김 (가루처럼 보이지 않게 조금만)
    for (let a = 0; a < TAU; a += 0.6 / rr) {
      const u = a + t * sp, px = Math.cos(u) * rr, py = Math.sin(u) * rr * ct, pz = Math.sin(u) * rr * st;
      const X = px * cy - pz * sy2, Z = px * sy2 + pz * cy;
      if (Z <= 0 || (gap && ((a * 3.1 + i) % 1) < gap)) continue;
      if (grow > 1) { p.blend(x + X * sx, y + py * sy, C[6], k); p.blend(x + X * sx, y + py * sy + 1, C[4], k * 0.6); }
      else p.px(x + X * sx, y + py * sy, i % 3 ? C[5] : C[6]);
    }
  });
}

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed), RAD = o.radius;
  const ps = new Particles({ rng: R, ground: () => 0, haze: C[4] }), lights = new Lights();
  let t = 0, boom = false;
  const BX = X1 - 3;   // 박히는 자리 (상대 몸 앞)
  return {
    update(dt) {
      t += dt;
      qiGather(ps, R, C, t, dt);
      if (t >= CHARGE && t < HIT) {
        const x = X1 * (t - CHARGE) / FLY;
        for (let i = 0; i < 2; i++) ps.spawn(P.VAPOUR, x - RAD, -H + R.range(-RAD * 0.6, RAD * 0.6), R.range(-60, -25), R.range(-8, 8), R.range(0.2, 0.35), R.pick([C[4], C[5]]), R.range(2.2, 3.4));
      }
      if (!boom && t >= HIT + IMPLODE) {
        boom = true;
        const y = -H;
      }
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      const q = t - HIT, y = -H;
      ps.draw(p);
      if (t < CHARGE) orb(p, C, 0, y, 2 + (RAD - 2) * 0.7 * (t / CHARGE), t, Math.min(1, t / CHARGE * 1.5));
      else if (q < 0) orb(p, C, X1 * (t - CHARGE) / FLY, y, RAD, t);
      else if (q < SQUASH) {   // 박힘: 앞으로 납작하게 눌림 + 맞닿은 면에 짧은 압력선
        const e = q / SQUASH;
        orb(p, C, BX - 2 * e, y, RAD, t, 1, 1 - 0.35 * e, 1 + 0.3 * e);
        for (let s = -RAD * 1.4; s <= RAD * 1.4; s += 0.5) p.blend(BX + RAD * 0.7, y + s, C[6], 0.7 * (1 - Math.abs(s) / (RAD * 1.4)));
      } else if (q < IMPLODE) {   // 응축: 잠깐 오그라듦 (진해짐)
        const e = (q - SQUASH) / (IMPLODE - SQUASH);
        orb(p, C, BX - 2, y, RAD * (1 - 0.45 * ease.inQuad(e)), t, 1, 0.65 + 0.35 * e, 1.3 - 0.3 * e);
      }
      const b = q - IMPLODE;
      if (b >= 0 && b < 0.42) (o.burst === 'sphere' ? sphereBurst : waveBurst)(p, C, BX, y, b / 0.42, t, RAD);   // 기가 사방으로 퍼지며 터짐
      lights.draw(p);
    },
  };
}

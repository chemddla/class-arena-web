// 시안 J 실타래 기구슬 (반짝임 없음): 진한 기운 구슬 속에 기운 실이 엉켜 돌고, 둘레는 일렁이는 기운 막. 뒤로 연기 같은 기운 꼬리.
// 맞는 순간: 박힘(구슬이 납작하게 눌림) → 응축(잠깐 오그라듦) → 터짐(기운 덩이가 부풀며 껍질이 밀려나 흩어지고, 안개가 사방으로,
//   진한 기운이 상대 뒤로 뚫고 나감) → 여운(남은 기운이 아지랑이처럼 피어오름). 별빛·번쩍·불꽃 가루·선 고리·바닥 이펙트 없음
import { Particles, Lights, P, Rng, fit, TAU, clamp, ease, noise2 } from "../../core/index.js";
import { QI_GOLD, H, X1, CHARGE, FLY, HIT, base, qiGather } from "./_qi.js";

export const meta = { ...base, size: [320, 124], origin: [26, 112], name: "기공사 J 실타래 기구슬", desc: "기운 실이 엉켜 도는 구슬, 맞으면 실이 풀리며 터짐 (반짝임 없음)", tags: ["qigong"], duration: HIT + 1.4, options: { palette: QI_GOLD, seed: 4, radius: 8 } };

const LOOPS = [];
for (let i = 0; i < 10; i++) LOOPS.push([(i * 2.39) % Math.PI, (i * 1.37) % TAU, (i % 2 ? 1 : -1) * (3 + (i % 4))]);
const SQUASH = 0.045, IMPLODE = 0.085;   // 맞은 뒤: 박힘 끝 · 응축 끝(= 터지는 순간)

// 기공이 터지는 모습: 가장자리가 일렁이는 기운 덩이가 확 부풀고, 가운데부터 비어 가며 두꺼운 기운 껍질이 바깥으로 밀려나 흩어짐
//   선 고리·바닥 이펙트 없음 (2026-11-16 사용자: 피사체 밑 이펙트 제거, 4개의 선 대신 기공이 터지는 모습으로)
function blast(p, C, x, y, e, t, R0) {
  const Rb = R0 * (0.7 + 3.0 * ease.outCubic(e)), hole = 0.9 * Math.pow(clamp((e - 0.12) / 0.88), 0.7), fade = Math.pow(1 - e, 1.7);
  p.glow(x, y, Rb * 1.6, C[4], 0.35 * fade);
  // 바둑판 점 찍기 대신 칸마다 진짜 반투명(blend)으로 칠함: 껍질 안쪽은 진하고 바깥 가장자리는 옅음
  const x0 = Math.floor(x - Rb * 1.3), x1 = Math.ceil(x + Rb * 1.3), y0 = Math.floor(y - Rb * 1.3), y1 = Math.ceil(y + Rb * 1.3);
  for (let py = y0; py <= y1; py++) for (let px = x0; px <= x1; px++) {
    const dx = px + 0.5 - x, dy = py + 0.5 - y, a = Math.atan2(dy, dx), d = Math.hypot(dx, dy);
    const wob = 1 + 0.2 * noise2(Math.cos(a) * 2 + t * 6, Math.sin(a) * 2 - t * 5) + 0.08 * noise2(Math.cos(a) * 6 - t * 9, Math.sin(a) * 6);
    const u = d / (Rb * wob);
    if (u > 1) continue;
    const holeW = hole * (1 + 0.15 * noise2(Math.cos(a) * 3 + t * 4, Math.sin(a) * 3));
    if (u < holeW) continue;
    const v = holeW < 1 ? (u - holeW) / (1 - holeW) : 1;   // 껍질 안쪽 0 → 바깥 1
    const c = e < 0.15 && u < 0.45 ? C[6] : v > 0.8 ? C[4] : v > 0.35 ? C[5] : C[6];
    const al = fade * (v > 0.8 ? 0.55 : 0.92) * (holeW > 0 && v < 0.12 ? 0.6 : 1);   // 안쪽 가장자리도 살짝 옅게
    p.blend(px + 0.5, py + 0.5, c, al);
  }
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
        lights.add(BX, y, 44, C[4], 0.6, 0.4);
        // 터지며 사방으로 부풀어 나가는 기운 안개 (구름처럼 퍼짐)
        for (let i = 0; i < 26; i++) {
          const g = (i / 26) * TAU + R.range(-0.12, 0.12), sp = R.range(140, 280);
          ps.spawn(P.VAPOUR, BX + Math.cos(g) * 4, y + Math.sin(g) * 4, Math.cos(g) * sp, Math.sin(g) * sp * 0.8, R.range(0.35, 0.6), R.pick([C[4], C[5], C[6]]), R.range(3, 5));
        }
        // 상대 뒤쪽으로 뚫고 나가는 진한 기운 (원뿔)
        for (let i = 0; i < 12; i++) {
          const g = R.range(-0.5, 0.5), sp = R.range(260, 460);
          ps.spawn(P.DUST, BX, y + R.range(-3, 3), Math.cos(g) * sp, Math.sin(g) * sp * 0.7, R.range(0.35, 0.55), R.pick([C[4], C[5], C[6]]), R.range(3, 5));
        }
        // 여운: 남은 기운이 천천히 피어오름
        for (let i = 0; i < 8; i++) ps.spawn(P.VAPOUR, BX + R.range(-10, 14), y + R.range(-8, 8), R.range(-6, 10), -R.range(10, 22), R.range(0.6, 0.9), R.pick([C[4], C[5]]), R.range(2, 3), R.range(0.12, 0.4));
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
      if (b >= 0 && b < 0.42) blast(p, C, BX, y, b / 0.42, t, RAD);   // 기운 덩이가 부풀며 터짐 (선 고리 없음)
      lights.draw(p);
    },
  };
}

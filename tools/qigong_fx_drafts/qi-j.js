// 시안 J 실타래 기구슬 (반짝임 뺀 판): 진한 기운 구슬 속에 기운 실이 엉켜 돌고, 둘레는 일렁이는 기운 막.
// 빛줄기·흰 심·별빛 없이, 뒤로 연기 같은 기운 꼬리. 맞으면 압력 고리와 안개
import { Particles, Lights, P, Rng, fit, TAU, clamp } from "../../core/index.js";
import { QI_GOLD, H, X1, CHARGE, FLY, HIT, base, qiGather, qiImpact, qiHitRings } from "./_qi.js";

export const meta = { ...base, name: "기공사 J 실타래 기구슬", desc: "기운 실이 엉켜 도는 구슬 (반짝임 없음)", tags: ["qigong"], duration: HIT + 0.8, options: { palette: QI_GOLD, seed: 4, radius: 8 } };

const LOOPS = [];
for (let i = 0; i < 10; i++) LOOPS.push([(i * 2.39) % Math.PI, (i * 1.37) % TAU, (i % 2 ? 1 : -1) * (3 + (i % 4))]);

function orb(p, C, x, y, r, t, k = 1) {
  p.glow(x, y, r * 2.4, C[3], 0.16 * k);
  p.disc(x, y, r + 2.5, C[3], 0.3 * k);   // 기운 막
  p.shade(x - r - 1, y - r - 1, x + r + 1, y + r + 1, (px, py, out) => {
    const dx = px - x, dy = py - y, d = Math.hypot(dx, dy) / r;
    if (d > 1.02) return 0;
    out.a = k;
    const lit = clamp(1 - d * 0.95 - (dx + dy) / r * 0.1);
    return d > 0.9 ? C[4] : lit > 0.7 ? C[4] : lit > 0.35 ? C[3] : C[2];
  });
  LOOPS.forEach(([tilt, yaw, sp], i) => {
    const ct = Math.cos(tilt) * 0.999, st = Math.sin(tilt), cy = Math.cos(yaw + t * 1.5), sy = Math.sin(yaw + t * 1.5), rr = r * (0.5 + 0.45 * ((i * 0.37) % 1));
    for (let a = 0; a < TAU; a += 0.6 / rr) {
      const u = a + t * sp, px = Math.cos(u) * rr, py = Math.sin(u) * rr * ct, pz = Math.sin(u) * rr * st;
      const X = px * cy - pz * sy, Z = px * sy + pz * cy;
      if (Z > 0) p.px(x + X, y + py, i % 3 ? C[5] : C[6]);
    }
  });
}

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed), RAD = o.radius;
  const ps = new Particles({ rng: R, ground: () => 0, haze: C[4] }), lights = new Lights();
  let t = 0, hit = false;
  return {
    update(dt) {
      t += dt;
      qiGather(ps, R, C, t, dt);
      if (t >= CHARGE && t < HIT) {
        const x = X1 * (t - CHARGE) / FLY;
        for (let i = 0; i < 2; i++) ps.spawn(P.VAPOUR, x - RAD, -H + R.range(-RAD * 0.6, RAD * 0.6), R.range(-60, -25), R.range(-8, 8), R.range(0.2, 0.35), R.pick([C[4], C[5]]), R.range(2.2, 3.4));
      }
      if (!hit && t >= HIT) { hit = true; qiImpact(ps, lights, R, C, X1, -H, 1.1); }
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      ps.draw(p);
      if (t < CHARGE) orb(p, C, 0, -H, 2 + (RAD - 2) * 0.7 * (t / CHARGE), t, Math.min(1, t / CHARGE * 1.5));
      else if (t < HIT) orb(p, C, X1 * (t - CHARGE) / FLY, -H, RAD, t);
      qiHitRings(p, C, t - HIT, X1, -H, 1.1);
      lights.draw(p);
    },
  };
}

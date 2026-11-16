// 시안 E 태극 기구슬: 밝은 반과 진한 반이 S자로 나뉜 구슬이 돌며 날아가고, 맞으면 꽃잎 여덟 장으로 펼쳐짐
import { Particles, Lights, P, Rng, fit, TAU, WHITE, ease } from "../../core/index.js";
import { GOLD, H, X1, CHARGE, FLY, HIT, base, gather, burst, handOrb } from "./_lib.js";

export const meta = { ...base, name: "기공사 E 태극 기구슬", desc: "반반 도는 구슬, 꽃잎 터짐", tags: ["qigong"], duration: HIT + 0.8, options: { palette: GOLD, seed: 2 } };

export function create(o) {
  const C = fit(o.palette, 8), R = new Rng(o.seed);
  const ps = new Particles({ rng: R, ground: () => 0, sparks: [WHITE, C[6], C[5], C[4]] }), lights = new Lights();
  let t = 0, hit = false;
  return {
    update(dt) {
      t += dt;
      gather(ps, R, C, t, dt);
      if (t >= CHARGE && t < HIT && R.chance(0.6)) {
        const x = X1 * (t - CHARGE) / FLY;
        ps.spawn(P.STAR, x - 4, -H + R.range(-4, 4), R.range(-40, -10), R.range(-10, 10), R.range(0.2, 0.4), R.pick([C[6], WHITE]), R.range(0.6, 1.4));
      }
      if (!hit && t >= HIT) { hit = true; burst(ps, lights, R, C, X1, -H, 0.7); }
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      ps.draw(p);
      if (t < CHARGE) handOrb(p, C, t / CHARGE, 3.5);
      else if (t < HIT) {
        const x = X1 * (t - CHARGE) / FLY, y = -H, r = 5.5, rot = t * 22;
        p.shade(x - r - 1, y - r - 1, x + r + 1, y + r + 1, (px, py) => {
          const dx = px - x, dy = py - y, d = Math.hypot(dx, dy);
          if (d > r + 0.5) return 0;
          if (d > r - 0.6) return C[3];
          const a = Math.atan2(dy, dx) - rot, sx = Math.cos(a) * d, sy = Math.sin(a) * d;
          let light = sy < 0;
          if (Math.hypot(sx - r / 2, sy) < r / 2) light = true;
          if (Math.hypot(sx + r / 2, sy) < r / 2) light = false;
          return light ? (d < 2 ? WHITE : C[6]) : C[4];
        });
        p.glow(x, y, 18, C[4], 0.6); p.glow(x, y, 6, C[6], 0.45);
      }
      const q = t - HIT;
      if (q >= 0 && q < 0.5) {   // 꽃잎 여덟 장
        const e = q / 0.5, L = 6 + 16 * ease.outCubic(e), a0 = e * 0.6;
        if (e < 0.1) p.circle(X1, -H, 6 * (1 - e / 0.1) + 1, WHITE);
        for (let i = 0; i < 8; i++) {
          const a = a0 + (i * TAU) / 8, ca = Math.cos(a), sa = Math.sin(a);
          for (let u = 0; u <= 1; u += 0.04) {
            const w = Math.sin(u * Math.PI) * 3 * (1 - e * 0.5), cx = X1 + ca * L * u, cy = -H + sa * L * u * 0.85;
            p.dot(cx - sa * w, cy + ca * w, e < 0.3 ? WHITE : C[6], 1 - e);
            p.dot(cx + sa * w, cy - ca * w, C[5], 1 - e);
          }
        }
        p.glow(X1, -H, 24, C[4], 0.6 * (1 - e));
      }
      lights.draw(p);
    },
  };
}

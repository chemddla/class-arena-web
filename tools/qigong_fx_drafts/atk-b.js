// 시안 B 장풍: 반달 파동이 넓어지며 밀려가고, 지나간 자리에 옅은 기운 안개. 맞으면 세로로 긴 충격 링
import { Particles, Lights, P, Rng, fit, WHITE, ease } from "../../core/index.js";
import { GOLD, H, X1, CHARGE, FLY, HIT, base, gather, burst, hitFlash, handOrb } from "./_lib.js";

export const meta = { ...base, name: "기공사 B 장풍", desc: "넓어지는 반달 파동", tags: ["qigong"], duration: HIT + 0.75, options: { palette: GOLD, seed: 5 } };

export function create(o) {
  const C = fit(o.palette, 8), R = new Rng(o.seed);
  const ps = new Particles({ rng: R, ground: () => 0, sparks: [WHITE, C[6], C[5], C[4]] }), lights = new Lights();
  let t = 0, hit = false;
  const at = (u) => [X1 * ease.outQuad(u), 6 + 10 * u];
  return {
    update(dt) {
      t += dt;
      gather(ps, R, C, t, dt);
      if (t >= CHARGE && t < HIT) {
        const [x, h] = at((t - CHARGE) / FLY);
        if (R.chance(0.7)) ps.spawn(P.VAPOUR, x - 4, -H + R.range(-h, h), R.range(-30, -10), R.range(-8, 8), R.range(0.25, 0.45), C[4], R.range(1.2, 2));
        if (R.chance(0.5)) ps.spawn(P.MOTE, x, -H + R.range(-h, h), R.range(-120, -60), 0, R.range(0.12, 0.25), R.pick([C[5], C[6]]), 0.8);
      }
      if (!hit && t >= HIT) { hit = true; burst(ps, lights, R, C, X1, -H, 0.9); }
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      ps.draw(p);
      if (t < CHARGE) handOrb(p, C, t / CHARGE, 3);
      else if (t < HIT) {
        const u = (t - CHARGE) / FLY, [x, h] = at(u);
        for (let k = 0; k < 3; k++) {   // 반달 세 겹 (앞이 가장 밝음)
          const xx = x - k * 5, hh = h - k * 2, c = [WHITE, C[6], C[4]][k], th = [2, 1.5, 1][k];
          for (let s = -hh; s <= hh; s += 0.5) {
            const bend = (1 - (s / hh) ** 2) * (5 + 4 * u);
            for (let w = 0; w < th; w += 0.5) p.dot(xx + bend - w, -H + s, c, 1 - k * 0.25);
          }
        }
        p.glow(x + 4, -H, 18 + 8 * u, C[4], 0.6);
      }
      const q = t - HIT;
      if (q >= 0 && q < 0.35) {   // 세로로 긴 충격 링
        const e = q / 0.35, rx = 3 + 6 * e, ry = 8 + 18 * ease.outCubic(e);
        for (let a = 0; a < Math.PI * 2; a += 0.05) p.dot(X1 + Math.cos(a) * rx, -H + Math.sin(a) * ry, e < 0.3 ? WHITE : C[5], 1 - e);
      }
      hitFlash(p, C, t - HIT, X1, -H, 0.8);
      lights.draw(p);
    },
  };
}

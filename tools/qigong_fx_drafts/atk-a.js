// 시안 A 금빛 기탄: 흰 심의 금빛 구슬이 곧게 날아가며 빛 가루 꼬리를 남기고, 맞으면 별빛으로 터짐
import { Particles, Lights, P, Rng, fit, WHITE } from "../../core/index.js";
import { GOLD, H, X1, CHARGE, FLY, HIT, base, gather, burst, hitFlash, handOrb } from "./_lib.js";

export const meta = { ...base, name: "기공사 A 금빛 기탄", desc: "곧게 나는 금빛 구슬", tags: ["qigong"], duration: HIT + 0.7, options: { palette: GOLD, seed: 3 } };

export function create(o) {
  const C = fit(o.palette, 8), R = new Rng(o.seed);
  const ps = new Particles({ rng: R, ground: () => 0, sparks: [WHITE, C[6], C[5], C[4]] }), lights = new Lights();
  let t = 0, hit = false;
  return {
    update(dt) {
      t += dt;
      gather(ps, R, C, t, dt);
      if (t >= CHARGE && t < HIT) {
        const x = X1 * (t - CHARGE) / FLY;
        if (R.chance(0.9)) ps.spawn(P.MOTE, x - 3, -H + R.range(-2, 2), R.range(-90, -40), R.range(-25, 25), R.range(0.15, 0.3), R.pick([C[4], C[5], C[6]]), 0.8);
      }
      if (!hit && t >= HIT) { hit = true; burst(ps, lights, R, C, X1, -H); }
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      ps.draw(p);
      if (t < CHARGE) handOrb(p, C, t / CHARGE);
      else if (t < HIT) {
        const x = X1 * (t - CHARGE) / FLY, y = -H;
        for (let i = 1; i <= 14; i++) p.dot(x - i, y, i < 4 ? C[6] : i < 9 ? C[5] : C[4], 1 - i / 15);
        p.circle(x, y, 5.4, C[3]); p.circle(x, y, 4.4, C[5]); p.circle(x + 0.6, y - 0.8, 2.2, WHITE);
        p.glow(x, y, 20, C[4], 0.7); p.glow(x, y, 7, C[6], 0.5);
      }
      hitFlash(p, C, t - HIT, X1, -H);
      lights.draw(p);
    },
  };
}

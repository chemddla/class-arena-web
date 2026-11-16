// 시안 C 나선 기류: 구슬 뒤로 금빛·흰빛 두 줄기가 꼬이며 따라가고, 맞으면 소용돌이처럼 감기며 터짐
import { Particles, Lights, P, Rng, fit, TAU, WHITE } from "../../core/index.js";
import { GOLD, H, X1, CHARGE, FLY, HIT, base, gather, burst, hitFlash, handOrb } from "./_lib.js";

export const meta = { ...base, name: "기공사 C 나선 기류", desc: "두 줄기가 꼬이는 구슬", tags: ["qigong"], duration: HIT + 0.75, options: { palette: GOLD, seed: 8 } };

export function create(o) {
  const C = fit(o.palette, 8), R = new Rng(o.seed);
  const ps = new Particles({ rng: R, ground: () => 0, sparks: [WHITE, C[6], C[5], C[4]] }), lights = new Lights();
  let t = 0, hit = false;
  return {
    update(dt) {
      t += dt;
      gather(ps, R, C, t, dt);
      if (!hit && t >= HIT) {
        hit = true; burst(ps, lights, R, C, X1, -H, 0.8);
        for (let i = 0; i < 22; i++) {   // 소용돌이 가루: 바깥으로 돌며 퍼짐
          const a = (i / 22) * TAU, sp = R.range(70, 120);
          ps.spawn(P.MOTE, X1 + Math.cos(a) * 4, -H + Math.sin(a) * 4, (-Math.sin(a) + Math.cos(a) * 0.5) * sp, (Math.cos(a) + Math.sin(a) * 0.5) * sp * 0.8, R.range(0.25, 0.4), i % 2 ? C[5] : WHITE, 0.9);
        }
      }
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      ps.draw(p);
      if (t < CHARGE) handOrb(p, C, t / CHARGE, 3);
      else if (t < HIT) {
        const x = X1 * (t - CHARGE) / FLY, y = -H;
        for (let d = 0; d < 34; d += 0.5) {
          const xx = x - d, ph = xx * 0.22 - t * 18, amp = 4.5 * Math.min(1, d / 6) * (1 - d / 40), k = 1 - d / 34;
          const front = Math.cos(ph) > 0;
          p.dot(xx, y + Math.sin(ph) * amp, front ? WHITE : C[4], k);
          p.dot(xx, y - Math.sin(ph) * amp, front ? C[3] : C[6], k);
        }
        p.circle(x, y, 4.4, C[3]); p.circle(x, y, 3.4, C[5]); p.circle(x + 0.5, y - 0.6, 1.6, WHITE);
        p.glow(x, y, 18, C[4], 0.65); p.glow(x, y, 6, C[6], 0.5);
      }
      hitFlash(p, C, t - HIT, X1, -H, 0.9);
      lights.draw(p);
    },
  };
}

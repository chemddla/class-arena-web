// 시안 I 기류 띠: 손에서 일렁이는 기운 띠가 뱀처럼 굽이치며 뻗어 나가 상대를 치고, 띠는 안개로 풀려 흩어짐
import { Particles, Lights, P, Rng, fit, ease, clamp } from "../../core/index.js";
import { QI_GOLD, H, X1, CHARGE, FLY, HIT, base, qiGather, qiImpact, qiHitRings } from "./_qi.js";

export const meta = { ...base, name: "기공사 I 기류 띠", desc: "굽이치는 기운 띠가 뻗어 침", tags: ["qigong"], duration: HIT + 0.85, options: { palette: QI_GOLD, seed: 9 } };

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed);
  const ps = new Particles({ rng: R, ground: () => 0, haze: C[4] }), lights = new Lights();
  let t = 0, hit = false, freed = false;
  const y = (x, tt) => -H + Math.sin(x * 0.075 - tt * 14) * 5 * Math.sin(Math.PI * clamp(x / X1));
  return {
    update(dt) {
      t += dt;
      qiGather(ps, R, C, t, dt);
      if (!hit && t >= HIT) { hit = true; qiImpact(ps, lights, R, C, X1, -H, 0.9); }
      if (!freed && t >= HIT + 0.12) {   // 띠가 안개로 풀림
        freed = true;
        for (let x = 4; x < X1; x += 6) ps.spawn(P.VAPOUR, x, y(x, t), R.range(-10, 10), R.range(-14, -2), R.range(0.3, 0.55), R.pick([C[4], C[5]]), R.range(2, 3.2));
      }
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      ps.draw(p);
      const head = t < CHARGE ? 0 : X1 * ease.outQuad(clamp((t - CHARGE) / FLY));
      const fade = t < HIT + 0.12 ? 1 : 0;
      if (t >= CHARGE && fade) {
        for (let x = 0; x <= head; x += 0.5) {   // 띠: 머리 쪽이 굵고 진함, 꼬리는 옅음
          const u = head ? x / head : 0, w = 1 + 3.2 * u, yy = y(x, t);
          for (let s = -w; s <= w; s += 0.5) {
            const edge = Math.abs(s) > w - 1;
            p.blend(x, yy + s, edge ? C[4] : u > 0.85 ? C[6] : C[5], (0.25 + 0.65 * u) * (edge ? 0.7 : 1));
          }
        }
        p.glow(head, y(head, t), 12, C[4], 0.3);
      }
      if (t < CHARGE) p.disc(0, -H, 2 + 3 * (t / CHARGE), C[5], 0.7);
      qiHitRings(p, C, t - HIT, X1, -H, 0.9);
      lights.draw(p);
    },
  };
}

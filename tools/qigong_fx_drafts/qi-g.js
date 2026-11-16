// 시안 G 기운 덩어리: 가장자리가 일렁이는 금빛 기운 덩어리가 날아가며 뒤로 연기 같은 기운 꼬리를 흘리고, 맞으면 압력 고리와 안개로 퍼짐
import { Particles, Lights, P, Rng, fit } from "../../core/index.js";
import { QI_GOLD, H, X1, CHARGE, FLY, HIT, base, qiGather, qiBall, qiImpact, qiHitRings } from "./_qi.js";

export const meta = { ...base, name: "기공사 G 기운 덩어리", desc: "일렁이는 기운 덩어리가 연기 꼬리를 남기며 날아감", tags: ["qigong"], duration: HIT + 0.8, options: { palette: QI_GOLD, seed: 3 } };

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed);
  const ps = new Particles({ rng: R, ground: () => 0, haze: C[4] }), lights = new Lights();
  let t = 0, hit = false;
  return {
    update(dt) {
      t += dt;
      qiGather(ps, R, C, t, dt);
      if (t >= CHARGE && t < HIT) {
        const x = X1 * (t - CHARGE) / FLY;
        for (let i = 0; i < 2; i++) ps.spawn(P.VAPOUR, x - 5, -H + R.range(-3, 3), R.range(-70, -30), R.range(-10, 10), R.range(0.2, 0.35), R.pick([C[5], C[5], C[6]]), R.range(2.2, 3.4));
      }
      if (!hit && t >= HIT) { hit = true; qiImpact(ps, lights, R, C, X1, -H); }
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      ps.draw(p);
      if (t < CHARGE) qiBall(p, C, 0, -H, 1.5 + 5 * (t / CHARGE), t, Math.min(1, t / CHARGE * 1.5));
      else if (t < HIT) qiBall(p, C, X1 * (t - CHARGE) / FLY, -H, 8.5, t);
      qiHitRings(p, C, t - HIT, X1, -H);
      lights.draw(p);
    },
  };
}

// 시안 H 기압 장풍: 구슬 없이 손바닥 앞 공기가 눌려 반달 압력 파동 세 겹으로 밀려가고, 둘레로 바람 줄이 스침. 맞으면 상대 뒤로 기운이 뚫고 나감
import { Particles, Lights, P, Rng, fit, ease } from "../../core/index.js";
import { QI_GOLD, H, X1, CHARGE, FLY, HIT, base, qiGather, qiImpact, qiHitRings } from "./_qi.js";

export const meta = { ...base, name: "기공사 H 기압 장풍", desc: "눌린 공기 파동이 밀려가는 장풍", tags: ["qigong"], duration: HIT + 0.8, options: { palette: QI_GOLD, seed: 5 } };

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed);
  const ps = new Particles({ rng: R, ground: () => 0, haze: C[4] }), lights = new Lights();
  let t = 0, hit = false;
  const at = (u) => [X1 * ease.outQuad(u), 10 + 12 * u];
  return {
    update(dt) {
      t += dt;
      qiGather(ps, R, C, t, dt, 0.7);
      if (t >= CHARGE && t < HIT) {
        const [x, h] = at((t - CHARGE) / FLY);
        ps.spawn(P.VAPOUR, x - 6, -H + R.range(-h, h), R.range(-40, -15), R.range(-6, 6), R.range(0.25, 0.4), R.pick([C[4], C[5]]), R.range(2, 3.4));
      }
      if (!hit && t >= HIT) {
        hit = true; qiImpact(ps, lights, R, C, X1, -H, 0.8);
        for (let i = 0; i < 10; i++) ps.spawn(P.VAPOUR, X1 + 6, -H + R.range(-10, 10), R.range(90, 160), R.range(-12, 12), R.range(0.25, 0.45), R.pick([C[4], C[5]]), R.range(2, 3.2));   // 뒤로 뚫고 나감
      }
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      ps.draw(p);
      if (t >= CHARGE && t < HIT) {
        const u = (t - CHARGE) / FLY, [x, h] = at(u);
        for (let k = 0; k < 3; k++) {   // 반달 압력 파동 (반투명, 앞이 진함)
          const xx = x - k * 7, hh = h - k * 2.5, a = [0.85, 0.55, 0.3][k];
          for (let s = -hh; s <= hh; s += 0.5) {
            const bend = (1 - (s / hh) ** 2) * (5 + 4 * u), edge = Math.abs(s) > hh - 2;
            p.blend(xx + bend + 1, -H + s, C[5], a * 0.8);
            p.blend(xx + bend, -H + s, edge ? C[4] : C[6], a);
            p.blend(xx + bend - 1, -H + s, C[5], a * 0.8);
            p.blend(xx + bend - 2, -H + s, C[4], a * 0.55);
            p.blend(xx + bend - 3, -H + s, C[3], a * 0.3);
          }
        }
        for (let i = 0; i < 5; i++) {   // 바람 줄: 파동 뒤로 길게 스치는 가는 선
          const yy = -H + (i - 2) * (h * 0.5), L = 14 + ((i * 7) % 10);
          p.line(x - 8 - L, yy, x - 8, yy, C[5], (u => 0.15 + 0.35 * u)(1 - Math.abs(i - 2) / 3));
        }
      }
      qiHitRings(p, C, t - HIT, X1, -H, 0.9);
      lights.draw(p);
    },
  };
}

// 기공사 SR 기공탄 · 청기 다섯 알: 손 둘레 부채꼴 자리에 다섯 알이 하나씩 맺힘 → 차례로 휘어 날아가 적을 나눠 쫓음
//   (방울 꼬리 · 뒤로 떨어지는 잔 방울) → 맞을 때마다 작은 막이 터지며 압력 고리 고리
import { Rng, fit } from "../../core/index.js";
import { QI_SKY, HAND, Drops, orb, tail, outBack } from "./_sr.js";

const CAST = 0.3, FLY = 0.42;
export const TARGETS = [[175, -42], [245, -40], [315, -42]];
export const meta = { size: [400, 150], origin: [40, 132], loop: false, fps: 30, bg: "dark", name: "기공사 SR 청기 다섯 알", desc: "휘어 날아가는 작은 기 구슬 다섯", tags: ["qigong"], duration: 1.9, options: { palette: QI_SKY, seed: 7 } };
export const TIMES = { CAST };

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed), D = new Drops(R);
  const [hx, hy] = [HAND.throw[0] + 4, HAND.throw[1]];
  const B = [-1.1, -0.55, 0, 0.55, 1.1].map((a, i) => ({ a, T: { x: hx + Math.cos(a) * 15 - 6, y: hy + Math.sin(a) * 15, r: 0 }, tg: TARGETS[[0, 1, 2, 1, 0][i]], t0: CAST + i * 0.07, i }));
  let t = 0;
  return {
    update(dt) {
      t += dt;
      for (const b of B) {
        if (t < b.t0) { b.T.r = 3.2 * outBack((t - b.i * 0.035) / 0.2); if (t > b.i * 0.035) D.gather(b.T, 22, 7, 15, dt); continue; }
        const u = (t - b.t0) / FLY;
        if (u < 1) {
          const p0 = b.T, cx = p0.x + 70, cy = p0.y + Math.sin(b.a) * 80, [tx, ty] = b.tg, q = 1 - u;
          const x = q * q * p0.x + 2 * q * u * cx + u * u * tx, y = q * q * p0.y + 2 * q * u * cy + u * u * ty;
          b.ang = Math.atan2(y - (b.y ?? y), x - (b.x ?? x) || 1); b.x = x; b.y = y;
          if (R.chance(0.4)) D.drop(x, y, -Math.cos(b.ang) * 40, -Math.sin(b.ang) * 40, { g: 150, life: 0.45 });
        } else if (!b.hit) { b.hit = true; D.splash(b.tg[0], b.tg[1], 0.55, { r: 3 }); }
      }
      D.update(dt, t);
    },
    draw(p) {
      for (const b of B) {
        if (t < b.t0) orb(p, C, b.T.x, b.T.y, b.T.r, t + b.a);
        else if (!b.hit && b.x != null) { tail(p, C, b.x, b.y, 3.2, b.ang, 16); orb(p, C, b.x, b.y, 3.2, t + b.a, 1, 1.1, 0.92); }
      }
      D.draw(p, C);
    },
  };
}

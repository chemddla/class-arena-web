// 기공사 SR 일반 공격 · 청기탄: 손끝에 기 알갱이이 맺혀 단단한 이슬 구슬로 응축 → 기운 꼬리를 끌며 날아감(뒤로 잔 방울·세로 압력 고리)
//   → 맞으면 구슬 막이 톡 터지며 압력 고리 고리 셋과 기 알갱이이 흩날림
import { Rng, fit } from "../../core/index.js";
import { QI_SKY, HAND, Drops, orb, tail, outBack, lerp } from "./_sr.js";

const CHARGE = 0.22, FLY = 0.3, HIT = CHARGE + FLY, X1 = HAND.punch[0] + 170;
export const meta = { size: [280, 130], origin: [30, 112], loop: false, fps: 30, bg: "dark", name: "기공사 SR 청기탄", desc: "맑게 응축된 기 구슬 일반 공격", tags: ["qigong"], duration: 1.4, options: { palette: QI_SKY, seed: 7 } };
export const TIMES = { CHARGE, FLY, HIT, X1 };

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed), D = new Drops(R);
  const T = { x: HAND.charge[0] + 6, y: HAND.charge[1] + 2, r: 1 }, [ax, ay] = HAND.punch;
  let t = 0, wake = 0, hit = false, bx = ax, by = ay;
  return {
    update(dt) {
      t += dt;
      if (t < CHARGE) { T.r = 4.5 * outBack(t / CHARGE); D.gather(T, 80, 10, 24, dt); }
      if (t >= CHARGE && t < HIT) {
        const u = (t - CHARGE) / FLY; bx = lerp(ax, X1, Math.pow(u, 0.9)); by = ay - Math.sin(u * Math.PI) * 3;
        if ((wake -= dt) <= 0) { wake = 0.045; D.ring(bx - 4, by, 3, 9, 0.3, { sx: 0.45, w: 1.2, a: 0.6 }); }
        if (R.chance(0.6)) D.drop(bx - 4, by + R.range(-2.5, 2.5), R.range(-80, -40), R.range(-10, 10), { g: 120, life: 0.5 });
      }
      if (t >= HIT && !hit) { hit = true; D.splash(X1, ay, 1, { r: 5 }); }
      D.update(dt, t);
    },
    draw(p) {
      if (t < CHARGE) orb(p, C, T.x, T.y, T.r, t);
      else if (t < HIT) { tail(p, C, bx, by, 4.5, 0, 22); orb(p, C, bx, by, 4.5, t, 1, 1.15, 0.9); }
      D.draw(p, C);
    },
  };
}

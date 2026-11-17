// 기공사 SR 기공후 · 청기 파동: 0.4초 동안 가슴에 기 알갱이이 휘몰려 들고 발밑 기 안개가 빨려 듦
//   → 가슴 구슬이 터지며 막이 부풀고, 땅을 따라 그라데이션 압력 고리 세 겹이 퍼짐 · 압력 고리 앞머리를 따라 기 알갱이 왕관이 튀고 안개가 밀려 남
import { Rng, fit, TAU } from "../../core/index.js";
import { QI_SKY, HAND, Drops, orb, ring, squeeze, eo } from "./_sr.js";

const CAST = 0.4, RX = 150;
export const meta = { size: [440, 170], origin: [220, 150], loop: false, fps: 30, bg: "dark", name: "기공사 SR 청기 파동", desc: "땅을 따라 퍼지는 맑은 기 압력 고리", tags: ["qigong"], duration: CAST + 1.3, options: { palette: QI_SKY, seed: 7 } };
export const TIMES = { CAST, RX };

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed), D = new Drops(R);
  const [cx, cy] = HAND.chest, T = { x: cx, y: cy, r: 3 };
  let t = 0, boom = false;
  return {
    update(dt) {
      t += dt;
      if (t < CAST) {
        D.gather(T, 130, 25, 62, dt, 1.4);
        if (R.chance(0.7)) { const a = R.range(0, TAU), d = R.range(70, 120); D.mist(Math.cos(a) * d, -3 + Math.sin(a) * d * 0.3, -Math.cos(a) * d * 2.6, -Math.sin(a) * d * 0.8, 6, 3, 0.4, 0.16); }
      }
      if (t >= CAST && !boom) {
        boom = true;
        D.add({ k: 4, x: cx, y: cy, r0: 6, r1: 34, life: 0.4, sy: 1 });
        for (let i = 0; i < 44; i++) {
          const a = R.range(0, TAU), sp = R.range(120, 230);
          D.drop(Math.cos(a) * 12, -2 + Math.sin(a) * 4, Math.cos(a) * sp, R.range(-180, -70), { r: R.chance(0.3) ? 2 : 1, g: 380, life: 1.2 });
        }
        for (let i = 0; i < 18; i++) { const a = i / 18 * TAU; D.mist(Math.cos(a) * 10, -6, Math.cos(a) * 180, Math.sin(a) * 30, 5, 14, 0.7, 0.18); }
        for (let i = 0; i < 10; i++) D.mist(R.range(-13, 13), R.range(-60, -30), R.range(-15, 15), R.range(-80, -40), 4, 10, 0.7, 0.15);
      }
      D.update(dt, t);
    },
    draw(p) {
      [CAST, CAST + 0.1, CAST + 0.22].forEach((t0, i) => {   // 앞머리 밝고 뒤로 옅어지는 그라데이션 압력 고리
        const u = (t - t0) / 0.75; if (u < 0 || u >= 1) return;
        const r = (RX - i * 18) * eo(u), k = (1 - u) * (1 - i * 0.2);
        for (let s = 0; s < 8; s++) ring(p, C, 0, -2, r * (1 - s * 0.035), 0.3, k * (s ? 0.28 * (1 - s / 8) : 1), s ? 2 : 1.5);
      });
      if (t < CAST) { orb(p, C, T.x, T.y, 1 + 5 * eo(t / CAST), t); squeeze(p, C, T.x, T.y, 5, t, 0.14, 30); }
      D.draw(p, C);
    },
  };
}

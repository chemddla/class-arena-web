// 기공사 SR 기공포 · 청기구: 0.6초 동안 사방의 기 알갱이이 휘어 들며 손 앞 구슬이 크게 맑아지고 압력 고리가 조여 듦
//   → 꿰뚫고 날아가며 뒤로 뒤로 밀리는 압력 고리·바닥 압력 고리·잔 방울, 꿰뚫린 적마다 작은 기 터짐 → 끝에서 크게 터짐
import { Rng, fit } from "../../core/index.js";
import { QI_SKY, HAND, Drops, orb, tail, shell, squeeze, eo, ss, lerp } from "./_sr.js";

const CAST = 0.6, FLY = 1.3, END = CAST + FLY, RB = 13;
const [AX, AY] = [HAND.cannon[0] + 12, HAND.cannon[1]], X1 = 380;
export const PIERCE = [AX + 110, AX + 200];
export const meta = { size: [480, 150], origin: [40, 132], loop: false, fps: 30, bg: "dark", name: "기공사 SR 청기구", desc: "꿰뚫는 맑은 기 구슬", tags: ["qigong"], duration: END + 0.9, options: { palette: QI_SKY, seed: 7 } };
export const TIMES = { CAST, END, X1 };

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed), D = new Drops(R);
  const T = { x: AX, y: AY, r: 1 }, done = [false, false];
  let t = 0, wake = 0, gw = 0, boom = false, bx = AX;
  return {
    update(dt) {
      t += dt;
      if (t < CAST) { T.r = 1 + (RB - 1) * eo(t / CAST); D.gather(T, 150, 26, 60, dt, 1.1); }
      if (t >= CAST && t < END) {
        const u = (t - CAST) / FLY; bx = lerp(AX, X1, u * u * 0.25 + u * 0.75);
        if ((wake -= dt) <= 0) { wake = 0.09; D.ring(bx - RB * 0.6, AY, RB * 0.95, RB * 1.7, 0.4, { sx: 0.32, w: 1.4, a: 0.38 }); }
        if ((gw -= dt) <= 0) { gw = 0.07; D.ring(bx, -1, RB * 0.4, RB * 1.8, 0.5, { sy: 0.25, w: 1.4, a: 0.5 }); }
        for (let i = 0; i < 2; i++) { const a = Math.PI + R.range(-1, 1); D.drop(bx + Math.cos(a) * RB, AY + Math.sin(a) * RB, R.range(-140, -60), Math.sin(a) * 40, { g: 140, life: 0.6, r: R.chance(0.2) ? 2 : 1 }); }
        if (R.chance(0.3)) D.mist(bx - RB, AY, -30, 0, 4, 12, 0.5, 0.14);
        PIERCE.forEach((x, i) => { if (!done[i] && bx >= x) { done[i] = true; D.splash(x, AY, 0.7, { dir: 0, spread: 2.2, r: RB * 0.6 }); } });
      }
      if (t >= END && !boom) {
        boom = true; D.splash(X1, AY, 2, { r: RB });
        for (let i = 0; i < 3; i++) D.at(END + i * 0.09, () => D.ring(X1, -1, 6, 70 + i * 16, 0.7, { sy: 0.25, w: 2.4, a: 0.7 }));
      }
      D.update(dt, t);
    },
    draw(p) {
      if (t < CAST) { orb(p, C, T.x, T.y, T.r, t); squeeze(p, C, T.x, T.y, T.r, t, 0.2, 44); }
      else if (t < END) {
        tail(p, C, bx, AY, RB, 0, 46 * ss(CAST, CAST + 0.08, t) + 8);
        const pre = t < CAST + 0.06; orb(p, C, bx, AY, RB, t, 1, pre ? 0.85 : 1.08, pre ? 1.12 : 0.94);
      } else { const u = (t - END) / 0.45; if (u < 1) shell(p, C, X1, AY, lerp(RB, 48, eo(u)), 1 - u); }
      D.draw(p, C);
    },
  };
}

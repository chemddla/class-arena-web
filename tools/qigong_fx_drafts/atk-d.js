// 시안 D 삼연 기탄: 손끝에서 작은 기탄 세 발이 빠르게 이어 나가 차례로 톡톡 터짐 (가볍고 빠른 손맛)
import { Particles, Lights, P, Rng, fit, WHITE } from "../../core/index.js";
import { GOLD, H, X1, CHARGE, FLY, HIT, base, gather, burst, hitFlash, handOrb } from "./_lib.js";

const GAP = 0.07, SHOTS = [[0, 0], [GAP, -5], [GAP * 2, 4]];   // [늦게 나가는 시간, 높이 차이]
const T = FLY * 0.8;
export const meta = { ...base, name: "기공사 D 삼연 기탄", desc: "작은 기탄 세 발", tags: ["qigong"], duration: HIT + GAP * 2 + 0.6, options: { palette: GOLD, seed: 11 } };

export function create(o) {
  const C = fit(o.palette, 8), R = new Rng(o.seed);
  const ps = new Particles({ rng: R, ground: () => 0, sparks: [WHITE, C[6], C[5], C[4]] }), lights = new Lights();
  let t = 0; const hit = [false, false, false];
  return {
    update(dt) {
      t += dt;
      gather(ps, R, C, t, dt, 0.7);
      SHOTS.forEach(([dl, dy], i) => {
        const s = t - CHARGE - dl;
        if (s >= 0 && s < T && R.chance(0.5)) ps.spawn(P.MOTE, X1 * s / T, -H + dy, -80, R.range(-15, 15), 0.15, C[5], 0.6);
        if (!hit[i] && s >= T) { hit[i] = true; burst(ps, lights, R, C, X1, -H + dy, 0.45); }
      });
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      ps.draw(p);
      if (t < CHARGE) handOrb(p, C, t / CHARGE, 2.5);
      SHOTS.forEach(([dl, dy]) => {
        const s = t - CHARGE - dl, y = -H + dy;
        if (s >= 0 && s < T) {
          const x = X1 * s / T;
          for (let i = 1; i <= 8; i++) p.dot(x - i, y, i < 3 ? C[6] : C[4], 1 - i / 9);
          p.circle(x, y, 2.6, C[4]); p.circle(x, y, 1.6, C[6]); p.px(x, y, WHITE);
          p.glow(x, y, 10, C[4], 0.55);
        }
        if (s >= 0 && s < 0.04) p.glow(0, -H, 8, C[5], 0.6);   // 손끝 번쩍
        hitFlash(p, C, s - T, X1, y, 0.5);
      });
      lights.draw(p);
    },
  };
}

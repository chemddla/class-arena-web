// 강화 발동 (한 번): 축전 5에서 강화 스킬이 나가는 순간 시전자 둘레에서 터지는 금빛. 기준점 = 발. 스킬 이펙트와 함께 틀어 "더 센 한 방"을 알림.
// 0~0.06초 금빛 줄무늬가 몸으로 빨려 듦 → 흰 섬광 + 몸 둘레 사방으로 짧은 금빛 가지 8줄 → 위로 솟는 금빛 불티 기둥 · 머리 위 왕관처럼 튀는 잔전류 → 0.7초
import { Particles, Lights, P, Rng, fit, flare, clamp, rng, TAU, WHITE } from "../../core/index.js";
import { zigzag, stroke, crackle } from "../lightning/_lib.js";
import { GOLD_V, GOLD_SPARK_V } from "./_volt.js";

const BANG = 0.06, CY = -46, BK = [1, 0.75, 0.9, 0.5, 0.3];
export const meta = {
  name: "Volt empower",
  desc: "An empowered cast: gold streaks rush into the caster, a white flash, short gold forks burst all round, a column of gold sparks lifts, a crown of arcs crackles over the head.",
  tags: ["lightning", "electric", "plasma", "buff", "empower", "one-shot"],
  size: [200, 220],
  origin: [100, 180],
  duration: 0.7,
  loop: false,
  fps: 20,
  bg: "dark",
  options: { palette: GOLD_V, sparks: GOLD_SPARK_V, seed: 41 },
};

export function create(o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), R = new Rng(o.seed), floor = () => 0;
  const ps = new Particles({ rng: R, ground: floor, sparks: o.sparks }), lights = new Lights();
  let t = 0, banged = false;
  return {
    update(dt) {
      t += dt;
      if (t < BANG && R.chance(200 * dt)) {
        const a = R.range(0, TAU), d = R.range(40, 60), T = 0.06;
        ps.spawn(P.STREAK, Math.cos(a) * d, CY + Math.sin(a) * d, -Math.cos(a) * d / T, -Math.sin(a) * d / T, T, R.chance(0.5) ? C[6] : C[5]);
      }
      if (t >= BANG && !banged) {
        banged = true;
        lights.add(0, CY, 90, C[4], 0.7, 0.35);
        lights.add(0, CY, 26, WHITE, 0.7, 0.08);
        for (let i = 0; i < 34; i++) {
          const x = R.range(-22, 22), sp = R.range(120, 260);
          ps.spawn(P.SPARK, x, -R.range(0, 70), R.range(-30, 30), -sp, R.range(0.3, 0.6), S[R.int(0, 2)]);
        }
      }
      ps.update(dt);
      lights.update(dt);
    },
    draw(p) {
      const a = t - BANG, f = Math.floor(t * 20 + 1e-4);
      if (a >= 0 && a < 0.2) {
        const q = a / 0.2;
        flare(p, 0, CY, 60 * Math.pow(1 - q, 1.3), 1 - q, C);
        if (q < 0.4) p.circle(0, CY, 10 * (1 - q * 2) + 2, WHITE);
      }
      const ba = Math.floor(Math.max(0, a) * 20 + 1e-4);
      if (a >= 0 && ba < BK.length) {
        const r = rng(o.seed, 3, ba >> 1);
        for (let i = 0; i < 8; i++) {
          const g = (i / 8) * TAU + r.range(-0.25, 0.25), l = r.range(34, 52);
          stroke(p, zigzag(r, Math.cos(g) * 10, CY + Math.sin(g) * 14, Math.cos(g) * l, CY + Math.sin(g) * l * 1.1, 0.3, 0.4), BK[ba], C, 0.8, { hero: ba === 0, light: 0.5 });
        }
      }
      // 머리 위 왕관 잔전류
      if (a > 0.05 && a < 0.55) {
        const r = rng(o.seed, 5, f), k = 1 - (a - 0.05) / 0.5;
        for (let i = 0; i < 3; i++) {
          const x0 = (i - 1) * 12 + r.range(-3, 3), y0 = -92;
          crackle(p, zigzag(r, x0, y0, x0 + r.range(-5, 5), y0 - r.range(10, 20) * k - 4, 0.45, 0.4), 0.5 + 0.5 * k, C, 0.45);
        }
      }
      ps.draw(p);
      lights.draw(p);
    },
  };
}

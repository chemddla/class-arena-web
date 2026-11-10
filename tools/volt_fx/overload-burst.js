// 오버로드 발동 (한 번): 시전 0.5초 동안 전류가 땅에서 몸으로 빨려 들고(웅크린 자세) → 일어서는 순간 흰 섬광과 함께
// 하늘로 굵은 벼락 기둥이 솟고, 짧은 가지가 사방으로 터지고, 불티가 분수처럼 튀고, 발밑에 플라즈마 물결이 한 번 퍼짐 (원 테두리 대신 바닥을 기는 전류).
// 기준점 = 발. t = 0 ~ 0.5 모으기, 0.5 터짐, 1.4초 끝
import { Particles, Lights, P, Rng, fit, flare, clamp, rng, TAU, WHITE } from "../../core/index.js";
import { zigzag, stroke, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";

export const meta = {
  name: "Volt overload burst",
  desc: "Overload kicking in: current is drawn up out of the floor into a crouched body, then a white flash, a thick bolt column shoots skyward, short forks burst all round, a fountain of sparks, arcs race out along the floor.",
  tags: ["lightning", "electric", "plasma", "buff", "transform", "one-shot"],
  size: [260, 260],
  origin: [130, 210],
  duration: 1.4,
  loop: false,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, seed: 22 },
};

const BANG = 0.5, CY = -44, BK = [1, 0.8, 1, 0.6, 0.85, 0.4, 0.2];

export function create(o) {
  const C = fit(o.palette, 8), R = new Rng(o.seed), floor = () => 0;
  const ps = new Particles({ rng: R, ground: floor, sparks: o.sparks }), lights = new Lights();
  let t = 0, banged = false;
  return {
    update(dt) {
      t += dt;
      // 모으기: 바닥에서 몸으로 빨려 드는 줄무늬
      if (t < BANG && R.chance(70 * dt)) {
        const a = R.range(0, TAU), d = R.range(40, 80), T = R.range(0.12, 0.2), sx = Math.cos(a) * d, sy = Math.sin(a) * d * 0.3;
        ps.spawn(P.STREAK, sx, sy, (-sx / T) * 0.9, ((CY * 0.6 - sy) / T) * 0.9, T, R.chance(0.5) ? C[6] : C[5]);
      }
      if (t >= BANG && !banged) {
        banged = true;
        lights.add(0, CY - 30, 150, C[4], 0.75, 0.45);
        lights.add(0, CY, 34, WHITE, 0.8, 0.08);
        for (let i = 0; i < 60; i++) {
          const a = -Math.PI / 2 + R.range(-1.3, 1.3), sp = R.range(150, 420);
          ps.spawn(P.SPARK, R.range(-6, 6), CY, Math.cos(a) * sp, Math.sin(a) * sp, R.range(0.3, 0.7));
        }
      }
      ps.update(dt);
      lights.update(dt);
    },
    draw(p) {
      const f = Math.floor(t * 20 + 1e-4), a = t - BANG;
      // 모으는 동안: 몸이 점점 밝아지고, 땅에서 발로 전류
      if (t < BANG) {
        const q = t / BANG, r = rng(o.seed, 2, f);
        p.glow(0, CY, 30 + 30 * q, C[4], 0.2 + 0.35 * q);
        for (let i = 0; i < 1 + Math.floor(q * 3); i++) {
          const x = r.range(-60, 60) * (1 - q * 0.5);
          crackle(p, zigzag(r, x, r.range(-6, 6), r.range(-8, 8), CY * r.range(0.2, 0.7), 0.35, 0.4), 0.4 + 0.5 * q, C, 0.4);
        }
      }
      // 섬광
      if (a >= 0 && a < 0.25) {
        const q = a / 0.25;
        flare(p, 0, CY, 70 * Math.pow(1 - q, 1.3), 1 - q, C);
        if (q < 0.4) p.circle(0, CY, 14 * (1 - q * 2) + 3, WHITE);
      }
      // 하늘로 솟는 벼락 기둥 (프레임마다 다시 그음)
      const ba = Math.floor(a * 20 + 1e-4);
      if (a >= 0 && ba < BK.length) {
        const r = rng(o.seed, 3, ba >> 1);
        stroke(p, zigzag(r, 0, 0, r.range(-6, 6), -205, 0.12, 0.6), BK[ba], C, 1.6, { hero: ba === 0, light: 0.6 });
        // 사방 짧은 가지
        for (let i = 0; i < 6; i++) {
          const g = (i / 6) * TAU + r.range(-0.3, 0.3), l = r.range(28, 50);
          stroke(p, zigzag(r, 0, CY, Math.cos(g) * l, CY + Math.sin(g) * l, 0.3, 0.5), BK[ba] * 0.8, C, 0.9);
        }
      }
      // 바닥을 기는 전류: 발에서 양옆으로 퍼짐
      if (a > 0 && a < 0.6) {
        const q = a / 0.6, r = rng(o.seed, 5, f), reach = 20 + 100 * Math.sqrt(q);
        for (const s of [-1, 1]) {
          crackle(p, zigzag(r, s * reach * 0.4, r.range(-2, 2), s * reach, r.range(-4, 4), 0.35, 0.5), 1 - q * 0.7, C, 0.4);
          p.glow(s * reach, -2, 20, C[4], 0.4 * (1 - q));
        }
      }
      ps.draw(p);
      lights.draw(p);
    },
  };
}

// 썬더볼트 (한 번, 대상마다): 하늘에서 내리꽂는 굵은 플라즈마 낙뢰. 기준점 = 대상 발.
// 마법사 썬더볼트·체인 라이트닝(둘 다 적과 적을 가로로 잇는 줄)과 다르게 "위에서 아래로 떨어지는 기둥"으로 구별:
//   0~0.12초 대상 머리 위 높은 곳에 전기 매듭이 모이고 대상 발밑에 가는 전류가 기며 겨냥 → 0.12초 굵은 낙뢰가 내리꽂힘 (흰 첫 프레임, 2프레임마다 다시 그음)
//   → 발밑에 플라즈마가 고였다가 납작하게 퍼지며 식고, 불티 분수, 대상 몸을 감싸는 전류, 기둥 잔광이 위로 걷힘. 0.9초
// 게임: 대상마다 0.1초 간격으로 차례로 틀면 "낙뢰가 3번 연달아 떨어지는" 모습 (체인처럼 줄로 잇지 않음)
// echo: 1 = 강화판 — 0.4초에 같은 자리로 두 번째 낙뢰(조금 가늘게)가 한 번 더 떨어짐 (설계서: 줄기가 되돌아오며 한 번 더 80%)
import { Particles, Lights, P, Rng, fit, flare, clamp, rng, TAU, WHITE } from "../../core/index.js";
import { zigzag, stroke, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";

const TOP = -300, CY = -44;
export const meta = {
  name: "Volt thunderbolt",
  desc: "A heavy plasma bolt dropped from the sky onto a target: a knot gathers high above, then the column slams down, plasma pools and spreads at the feet, sparks fountain, the column's afterglow lifts.",
  tags: ["lightning", "electric", "plasma", "strike", "one-shot"],
  size: [220, 360],
  origin: [110, 330],
  duration: 0.9,
  loop: false,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, echo: 0, width: 1, seed: 17 },
};

const BK = [1, 0.8, 1, 0.65, 0.85, 0.45, 0.25];

export function create(o) {
  const C = fit(o.palette, 8), R = new Rng(o.seed), floor = () => 0, W = o.width;
  const ps = new Particles({ rng: R, ground: floor, sparks: o.sparks }), lights = new Lights();
  const strikes = [{ t0: 0.12, s: 1.9 * W, k: 1 }];
  if (o.echo) strikes.push({ t0: 0.42, s: 1.4 * W, k: 0.85 });
  const hit = strikes.map(() => false);
  let t = 0;
  return {
    update(dt) {
      t += dt;
      for (const [i, s] of strikes.entries())
        if (!hit[i] && t >= s.t0) {
          hit[i] = true;
          lights.add(0, -30, 110, C[4], 0.75 * s.k, 0.35);
          lights.add(0, -4, 30, WHITE, 0.8 * s.k, 0.08);
          for (let j = 0; j < 40 * s.k; j++) {
            const a = -Math.PI / 2 + R.range(-1.35, 1.35), sp = R.range(110, 330);
            ps.spawn(P.SPARK, R.range(-4, 4), -2, Math.cos(a) * sp, Math.sin(a) * sp, R.range(0.25, 0.6));
          }
        }
      ps.update(dt);
      lights.update(dt);
    },
    draw(p) {
      const f = Math.floor(t * 20 + 1e-4);
      // 겨냥: 위에 모이는 매듭과 발밑 전류
      if (t < 0.14) {
        const q = t / 0.12, r = rng(o.seed, 2, f);
        p.glow(0, TOP + 20, 20 + 14 * q, C[4], 0.45 * q + 0.1);
        for (let i = 0; i < 3; i++) {
          const a = r.range(0, TAU), l = r.range(6, 16);
          crackle(p, zigzag(r, 0, TOP + 20, Math.cos(a) * l, TOP + 20 + Math.sin(a) * l, 0.5, 0.4), 0.5 + 0.5 * q, C, 0.4);
        }
        p.circle(0, TOP + 20, 2 + 3 * q, C[6]);
        crackle(p, zigzag(r, -14, 0, 14, r.range(-2, 2), 0.3, 0.3), 0.4 * q + 0.1, C, 0.3);
      }
      for (const [i, s] of strikes.entries()) {
        const a = t - s.t0;
        if (a < 0) continue;
        const ba = Math.floor(a * 20 + 1e-4);
        // 낙뢰 기둥
        if (ba < BK.length) {
          const r = rng(o.seed, 3, i, ba >> 1);
          stroke(p, zigzag(r, r.range(-6, 6), TOP, 0, -2, 0.1, 0.55), BK[ba] * s.k, C, s.s * (ba === 0 ? 1.2 : 1), { hero: ba === 0, light: 0.65, core: ba < 2 ? 1.2 * W : undefined });
          if (ba === 0) flare(p, 0, -6, 60 * s.k, 1, C);
        }
        // 발밑 플라즈마 웅덩이: 고였다가 납작하게 퍼지며 식음 (겹 타원, 테두리 줄 없이 안쪽이 밝음)
        const q = clamp(a / 0.55);
        if (q < 1) {
          // 체크무늬(반투명 점무늬) 없이 단계 색으로: 퍼지면서 안쪽 밝은 층부터 사라짐
          const rx = (16 + 34 * Math.sqrt(q)) * W, k = 1 - q;
          if (k > 0.25) p.ellipse(0, 0, rx, rx * 0.26, k > 0.6 ? C[3] : C[2]);
          if (k > 0.4) p.ellipse(0, 0, rx * 0.66, rx * 0.17, k > 0.7 ? C[5] : C[4]);
          if (k > 0.6) p.ellipse(0, 0, rx * 0.32, rx * 0.09, WHITE);
          p.glow(0, -2, rx * 1.2, C[4], 0.4 * k);
          // 바닥을 기어 퍼지는 전류
          const r = rng(o.seed, 5, i, f);
          for (let j = 0; j < 2; j++) {
            const sgn = j ? 1 : -1, x1 = sgn * rx * r.range(0.8, 1.15);
            crackle(p, zigzag(r, sgn * rx * 0.3, r.range(-2, 2), x1, r.range(-5, 5), 0.35, 0.5), 0.9 * k + 0.1, C, 0.4);
          }
        }
        // 대상 몸을 감싸는 전류
        if (a > 0.05 && a < 0.4) {
          const r = rng(o.seed, 7, i, f), k = 1 - a / 0.4;
          for (let j = 0; j < 2; j++) {
            const y0 = r.range(-80, -10), x0 = r.sign() * r.range(10, 20);
            crackle(p, zigzag(r, x0, y0, -x0 + r.range(-4, 4), y0 + r.range(-18, 18), 0.4, 0.3), 0.5 + 0.5 * k, C, 0.35);
          }
        }
        // 기둥 잔광: 가는 빛기둥이 위로 걷힘
        if (a > 0.2 && a < 0.6) {
          const u = (a - 0.2) / 0.4, y1 = -2 - (1 - u) * 0 - u * 280;
          p.line(0, TOP * (1 - u * 0.2), 0, y1, C[4], 0.6 * (1 - u));
          p.glowLine(0, TOP, 0, y1, 6, C[4], 0.25 * (1 - u));
        }
      }
      ps.draw(p);
      lights.draw(p);
    },
  };
}

// 무참 마지막 일격: 목표 위로 큰 빛의 초승달 둘이 한 칸 차이로 엇갈려 X로 가르고 (섬단과 같은 날), 가운데 큰 섬광 · 둘레로 불티가 터지고 X가 벌어지며 식음
// 좌표: 기준점(0, 0) = 목표 가슴, +x = 검사가 베는 쪽
import { fit, clamp, smooth, rng } from "../../core/index.js";
import { MOON, MOON_SPARK, FLASH, burst, lensFlare, lightCrescent } from "./_sword.js";

export const meta = {
  name: "Mucham final",
  desc: "Two large light crescents cross over the target one frame apart into an X, a big flare and a ring of sparks burst, the X opens out, thins and cools.",
  tags: ["melee", "slash", "sword", "x", "finisher", "one-shot"],
  size: [220, 220],
  origin: [110, 110],
  duration: 0.58,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, W: 10, Rc: 150, span: 0.75, tilt: 0.75, seed: 8 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), S = fit(o.sparks, 4);
  const rv0 = clamp(t / FLASH), rv1 = clamp((t - FLASH) / FLASH), b = clamp((t - 0.08) / 0.46), sc = 1 + 0.3 * Math.pow(b, 0.6), life = smooth(0, 1, b);
  lightCrescent(p, C, 0, 0, o.tilt, o.Rc, o.span, o.W, rv0, sc, life, 1);
  lightCrescent(p, C, 0, 0, -o.tilt, o.Rc, o.span, o.W, rv1, sc, life, 1);
  lensFlare(p, t, FLASH * 2, 0, 0, C, 56, 0.22);
  if (t > FLASH * 2 && t < FLASH * 2 + 0.14) p.glow(0, 0, 34, C[5], 0.55 * (1 - (t - FLASH * 2) / 0.14));
  const R = rng(o.seed, 3);
  for (let i = 0; i < 8; i++) burst(p, t, FLASH * 2 + i * 0.006, 0, 0, (i / 8) * 6.28 + R.range(-0.3, 0.3), 0.35, 3, o.seed + i, S);
}

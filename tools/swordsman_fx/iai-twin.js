// 검사 기본 공격 참격 D: 나란한 사선 두 줄 — 칼바람 뒤 끝자락을 같은 기울기의 초승달 두 개가 1칸 차이로 연달아 가름 (뒷줄이 조금 더 멀리)
import { fit, clamp, sparkle } from "../../core/index.js";
import { slashEnd } from "../melee/_lib.js";
import { MOON, MOON_SPARK, T, hiltGlint, burst, sharpSlash, lensFlare } from "./_sword.js";
import { wind, cutAt, CUT_X } from "./iai-diag.js";

export const meta = {
  name: "Iai twin",
  desc: "A wind line, then two parallel tilted crescents cut the target one frame apart, the second a little further out.",
  tags: ["melee", "slash", "sword", "iai", "double", "one-shot"],
  size: [200, 96],
  origin: [14, 48],
  duration: 0.45,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, len: 144, tilt: 1.15, R: 50, W: 3.5, off: 10, seed: 9 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), L = o.len, t0 = T.glint + 0.02;
  hiltGlint(p, t, C, sparkle);
  wind(p, t, L, C, o.seed);
  const cuts = [[L * CUT_X - o.off, t0], [L * CUT_X + o.off, t0 + 0.025]].map(([x, s0]) => ({ ...cutAt(x, o.tilt, 1, o.R, s0, o.W, 1.15), ramp: C }));
  cuts.forEach((s, i) => {
    sharpSlash(p, s, t);
    const e = slashEnd(s), g = t - (s.t0 + s.sweep);
    if (g > -0.02 && g < 0.13) sparkle(p, e.x, e.y, 5 * Math.sin(Math.PI * clamp((g + 0.02) / 0.15)), C[6], C[4], 0.55);
    lensFlare(p, t, s.t0 + s.sweep * 0.6, s.cx + Math.cos(s.a0 + s.dir * s.span * 0.55) * s.R, s.cy + Math.sin(s.a0 + s.dir * s.span * 0.55) * s.R, C, 24, 0.14);
    burst(p, t, s.t0 + s.sweep, e.x, e.y, Math.atan2(e.dy, e.dx), 0.55, 5, o.seed + i, fit(o.sparks, 4));
  });
}

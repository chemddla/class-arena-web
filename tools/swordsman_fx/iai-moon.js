// 검사 기본 공격 참격 E: 반월 — 빛의 속도로 칼바람이 지나간 뒤, 목표를 거의 세로로 덮는 커다란 빛의 반달이 한 번에 가름
import { fit, clamp, sparkle } from "../../core/index.js";
import { slashEnd } from "../melee/_lib.js";
import { MOON, MOON_SPARK, T, hiltGlint, burst, sharpSlash, lensFlare } from "./_sword.js";
import { wind, cutAt, CUT_X, CUT_Y } from "./iai-diag.js";

export const meta = {
  name: "Iai half moon",
  desc: "A light-speed wind line, then a large half-moon of light sweeps almost vertically over the target, flares and cools.",
  tags: ["melee", "slash", "sword", "iai", "crescent", "one-shot"],
  size: [210, 144],
  origin: [14, 72],
  duration: 0.45,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, len: 126, tilt: 1.45, R: 64, W: 6, seed: 13 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), L = o.len;
  hiltGlint(p, t, C, sparkle);
  wind(p, t, L, C, o.seed);
  const s = { ...cutAt(L * CUT_X - 6, o.tilt, 1, o.R, T.glint + 0.02, o.W, 1.5), ramp: C };
  sharpSlash(p, s, t);
  lensFlare(p, t, s.t0 + s.sweep * 0.6, L * CUT_X, CUT_Y, C, 30);
  const e = slashEnd(s), g = t - (s.t0 + s.sweep);
  if (g > -0.02 && g < 0.15) sparkle(p, e.x, e.y, 6 * Math.sin(Math.PI * clamp((g + 0.02) / 0.17)), C[6], C[4], 0.6);
  burst(p, t, s.t0 + s.sweep, e.x, e.y, Math.atan2(e.dy, e.dx), 0.6, 6, o.seed, fit(o.sparks, 4));
}

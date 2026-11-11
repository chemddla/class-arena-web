// 검사 기본 공격 참격 B: 사선 한 줄 — 칼자루에서 끝까지 옅은 칼바람이 먼저 지나고, 끝자락(목표 몸)을 비스듬한 초승달이 가름
// 위아래 뒤집기는 게임이 무작위로 (내려 베기 / 올려 베기)
import { fit, clamp, sparkle } from "../../core/index.js";
import { through, slashEnd } from "../melee/_lib.js";
import { MOON, MOON_SPARK, T, FLASH, hiltGlint, burst, sharpSlash, lightRush, lensFlare } from "./_sword.js";

export const meta = {
  name: "Iai diagonal",
  desc: "A faint wind line runs out to the end of the reach, then a tilted crescent cuts across the target there, flashes white and cools.",
  tags: ["melee", "slash", "sword", "iai", "diagonal", "one-shot"],
  size: [200, 96],
  origin: [14, 48],
  duration: 0.42,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, len: 144, tilt: 1.05, R: 54, W: 4.5, seed: 5 },
};

/** 칼바람: 빛의 속도로 칼자루에서 끝자락까지 번쩍 지나간 자리 (빛 번짐 + 속도선) */
export function wind(p, t, L, C, seed = 1) {
  lightRush(p, t, T.glint, 6, L * 0.9, 0, C, seed, 0.2);
}

/** 끝자락 x에서 기울기 th로 지나가는 초승달 (R = 반지름, W = 굵기). 칼자루보다 CUT_Y 위 = 목표 가슴 높이 */
export const CUT_Y = -10, CUT_X = 0.97;
export const cutAt = (x, th, dir, R, t0, W = 7, span = 1.15) =>
  through(x, CUT_Y, th, dir, R, span, 0.55, { W, t0, sweep: FLASH * 1.4, hold: T.hold, trail: T.trail, lens: true, hot: 0.45 }); // 얇은 초승달 (양끝 뾰족), 맞는 순간까지 흰 날

export function draw(p, t, o) {
  const C = fit(o.palette, 7), L = o.len;
  hiltGlint(p, t, C, sparkle);
  wind(p, t, L, C, o.seed);
  const s = { ...cutAt(L * CUT_X, o.tilt, 1, o.R, T.glint + 0.02, o.W, 1.25), ramp: C };
  sharpSlash(p, s, t);
  const e = slashEnd(s), g = t - (s.t0 + s.sweep);
  lensFlare(p, t, s.t0 + s.sweep * 0.6, L * CUT_X, CUT_Y, C, 30); // 초승달이 목표 가슴을 지나는 순간
  if (g > -0.02 && g < 0.15) sparkle(p, e.x, e.y, 6 * Math.sin(Math.PI * clamp((g + 0.02) / 0.17)), C[6], C[4], 0.6);
  burst(p, t, s.t0 + s.sweep, e.x, e.y, Math.atan2(e.dy, e.dx), 0.6, 7, o.seed, fit(o.sparks, 4));
}

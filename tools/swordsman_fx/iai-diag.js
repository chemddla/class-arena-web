// 검사 기본 공격 참격 B: 사선 한 줄 — 칼자루에서 끝까지 옅은 칼바람이 먼저 지나고, 끝자락(목표 몸)을 비스듬한 초승달이 가름
// 위아래 뒤집기는 게임이 무작위로 (내려 베기 / 올려 베기)
import { fit, clamp, sparkle } from "../../core/index.js";
import { through, slash, slashEnd } from "../melee/_lib.js";
import { MOON, MOON_SPARK, T, hiltGlint, burst } from "./_sword.js";

export const meta = {
  name: "Iai diagonal",
  desc: "A faint wind line runs out to the end of the reach, then a tilted crescent cuts across the target there, flashes white and cools.",
  tags: ["melee", "slash", "sword", "iai", "diagonal", "one-shot"],
  size: [200, 96],
  origin: [14, 48],
  duration: 0.42,
  loop: false,
  fps: 30,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, len: 144, tilt: 1.05, R: 48, W: 9, seed: 5 },
};

/** 칼바람: 1칸 만에 끝자락까지 그어지고 바로 흐려지는 1px 줄 */
export function wind(p, t, L, C) {
  const u = t - T.glint;
  if (u < 0 || u > 0.16) return;
  const head = L * 0.92 * clamp(u / 0.033), a = 0.6 * (1 - u / 0.16);
  for (let x = 6; x <= head; x += 1) p.dot(x, 0, x > head - 10 ? C[6] : C[4], a * (x % 3 === 0 ? 0.5 : 1));
}

/** 끝자락 x에서 기울기 th로 지나가는 초승달 (R = 반지름, W = 굵기). 칼자루보다 CUT_Y 위 = 목표 가슴 높이 */
export const CUT_Y = -10, CUT_X = 0.97;
export const cutAt = (x, th, dir, R, t0, W = 7, span = 1.15) =>
  through(x, CUT_Y, th, dir, R, span, 0.55, { W, t0, sweep: T.sweep * 0.8, hold: T.hold, trail: T.trail, lens: true });

export function draw(p, t, o) {
  const C = fit(o.palette, 7), L = o.len;
  hiltGlint(p, t, C, sparkle);
  wind(p, t, L, C);
  const s = { ...cutAt(L * CUT_X, o.tilt, 1, o.R, T.glint + 0.02, o.W, 1.3), ramp: C };
  slash(p, s, t);
  const e = slashEnd(s), g = t - (s.t0 + s.sweep);
  if (g > -0.02 && g < 0.15) sparkle(p, e.x, e.y, 7 * Math.sin(Math.PI * clamp((g + 0.02) / 0.17)), C[6], C[4], 0.6);
  burst(p, t, s.t0 + s.sweep, e.x, e.y, Math.atan2(e.dy, e.dx), 0.6, 7, o.seed, fit(o.sparks, 4));
}

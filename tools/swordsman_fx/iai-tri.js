// 검사 기본 공격 참격 F: 삼연 — 칼바람 뒤 목표 가슴에서 내려 베기 → 올려 베기 → 가로 베기가 1~2칸 간격으로 겹쳐 별 모양을 그리고, 마지막에 번쩍
import { fit, clamp, sparkle } from "../../core/index.js";
import { slashEnd } from "../melee/_lib.js";
import { MOON, MOON_SPARK, T, hiltGlint, burst, sharpSlash, lensFlare } from "./_sword.js";
import { wind, cutAt, CUT_X, CUT_Y } from "./iai-diag.js";

export const meta = {
  name: "Iai triple",
  desc: "A wind line, then a down cut, an up cut and a level cut cross over the target a frame or two apart, drawing a star that flares at the end.",
  tags: ["melee", "slash", "sword", "iai", "combo", "one-shot"],
  size: [200, 112],
  origin: [14, 56],
  duration: 0.5,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, len: 126, R: 44, W: 3.5, gap: 0.035, seed: 15 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), L = o.len, X = L * CUT_X, t0 = T.glint + 0.02;
  hiltGlint(p, t, C, sparkle);
  wind(p, t, L, C, o.seed);
  const cuts = [[1.1, 1], [-1.0, -1], [0.12, 1]].map(([th, dir], i) => ({ ...cutAt(X, th, dir, o.R, t0 + o.gap * i, o.W, 1.2), ramp: C }));
  cuts.forEach((s, i) => {
    sharpSlash(p, s, t);
    const e = slashEnd(s);
    burst(p, t, s.t0 + s.sweep, e.x, e.y, Math.atan2(e.dy, e.dx), 0.5, 3, o.seed + i, fit(o.sparks, 4));
  });
  const last = cuts[2], close = last.t0 + last.sweep, g = t - close;
  lensFlare(p, t, close, X, CUT_Y, C, 38, 0.2);
  if (g > -0.02 && g < 0.18) sparkle(p, X, CUT_Y, 9 * Math.sin(Math.PI * clamp((g + 0.02) / 0.2)), C[6], C[5], 0.7);
}

// 검사 기본 공격 참격 C: X자 — 칼바람 뒤 끝자락에서 내려 베기, 2칸 뒤 올려 베기가 겹치며 X가 닫히는 순간 가운데가 번쩍
import { fit, clamp, sparkle } from "../../core/index.js";
import { slash, slashEnd } from "../melee/_lib.js";
import { MOON, MOON_SPARK, T, hiltGlint, burst } from "./_sword.js";
import { wind, cutAt, CUT_X, CUT_Y } from "./iai-diag.js";

export const meta = {
  name: "Iai cross",
  desc: "A wind line, then a down cut and an up cut close an X over the target; the crossing flashes and throws sparks.",
  tags: ["melee", "slash", "sword", "iai", "cross", "one-shot"],
  size: [200, 96],
  origin: [14, 48],
  duration: 0.48,
  loop: false,
  fps: 30,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, len: 144, tilt: 0.95, R: 46, W: 8, gap: 0.066, seed: 7 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), L = o.len, X = L * CUT_X, t0 = T.glint + 0.02;
  hiltGlint(p, t, C, sparkle);
  wind(p, t, L, C);
  const a = { ...cutAt(X, o.tilt, 1, o.R, t0, o.W, 1.3), ramp: C }, b = { ...cutAt(X, -o.tilt, -1, o.R, t0 + o.gap, o.W, 1.3), ramp: C };
  slash(p, a, t);
  slash(p, b, t);
  const close = b.t0 + b.sweep, g = t - close;
  if (g > -0.02 && g < 0.2) {
    const k = Math.sin(Math.PI * clamp((g + 0.02) / 0.22));
    sparkle(p, X, CUT_Y, 11 * k, C[6], C[4], 0.7);
    p.glow(X, CUT_Y, 16, C[5], 0.5 * k);
  }
  burst(p, t, close, X, CUT_Y, 0, 1.4, 10, o.seed, fit(o.sparks, 4));
  const e = slashEnd(a);
  burst(p, t, a.t0 + a.sweep, e.x, e.y, Math.atan2(e.dy, e.dx), 0.5, 4, o.seed + 1, fit(o.sparks, 4));
}

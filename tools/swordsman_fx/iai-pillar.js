// 검사 기본 공격 참격 H: 광주 — 칼바람이 목표에 닿는 순간, 목표를 세로로 가르는 빛의 기둥이 가운데에서 위아래로 1칸 만에 열리고 가로 빛줄과 함께 사라짐
import { fit, clamp, smooth, ease, sparkle } from "../../core/index.js";
import { MOON, MOON_SPARK, T, FLASH, hiltGlint, burst, lensFlare, lightBeam } from "./_sword.js";
import { wind, CUT_X, CUT_Y } from "./iai-diag.js";

export const meta = {
  name: "Iai pillar",
  desc: "As the wind line reaches the target, a vertical pillar of light splits it, opening up and down from the middle in one frame, then fades with a level flare.",
  tags: ["melee", "slash", "sword", "iai", "vertical", "one-shot"],
  size: [200, 112],
  origin: [14, 56],
  duration: 0.42,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, len: 126, h: 38, w: 2.6, seed: 19 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), L = o.len, X = L * CUT_X, Y = CUT_Y;
  hiltGlint(p, t, C, sparkle);
  wind(p, t, L, C, o.seed);
  const t0 = T.glint + FLASH, u = t - t0;
  if (u >= 0) {
    const life = T.hold + T.trail + 0.04, open = ease.outExpo(clamp(u / FLASH)), shut = smooth(T.hold, life, u), age = clamp(u / life);
    const h = o.h * open, cut = h * shut; // 가운데부터 닫힘
    if (h - cut > 1) {
      lightBeam(p, X, Y - h, X, Y - cut, o.w * (1 - shut * 0.5), C, age, 1, (v) => Math.pow(Math.sin(Math.PI * Math.pow(v, 0.7)), 0.9));
      lightBeam(p, X, Y + h, X, Y + cut, o.w * (1 - shut * 0.5), C, age, 1, (v) => Math.pow(Math.sin(Math.PI * Math.pow(v, 0.7)), 0.9));
    }
  }
  lensFlare(p, t, t0, X, Y, C, 36, 0.22);
  const g = t - t0;
  if (g > -0.02 && g < 0.16) sparkle(p, X, Y, 9 * Math.sin(Math.PI * clamp((g + 0.02) / 0.18)), C[6], C[5], 0.7);
  burst(p, t, t0, X, Y, -Math.PI / 2, 2.6, 8, o.seed, fit(o.sparks, 4));
}

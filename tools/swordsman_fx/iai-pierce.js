// 검사 기본 공격 참격 G: 관통 — 칼자루에서 뻗은 빛의 창이 1칸 만에 목표를 꿰뚫고 30% 더 나아감. 꿰뚫은 자리에 빛 고리가 퍼짐
import { fit, clamp, smooth, ease, sparkle } from "../../core/index.js";
import { MOON, MOON_SPARK, T, FLASH, hiltGlint, burst, lightRush, lensFlare, lightBeam } from "./_sword.js";

export const meta = {
  name: "Iai pierce",
  desc: "A spear of light shoots from the hilt through the target and 30% beyond in one frame; a ring of light spreads where it passes through.",
  tags: ["melee", "thrust", "sword", "iai", "pierce", "one-shot"],
  size: [220, 64],
  origin: [14, 32],
  duration: 0.42,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, len: 126, over: 0.3, w: 3, seed: 17 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), L = o.len, F = L * (1 + o.over);
  hiltGlint(p, t, C, sparkle);
  const u = t - T.glint;
  if (u < 0) return;
  const end = T.sweep + T.hold + T.trail;
  const head = F * ease.outExpo(clamp(u / FLASH)), tl = smooth(T.sweep + T.hold, end, u), tail = head * tl * 0.98, age = clamp(u / end);
  if (head - tail > 1) lightBeam(p, tail, 0, head, 0, o.w * (1 - tl * 0.5), C, age, 1, (v) => Math.pow(Math.sin(Math.PI * Math.pow(v, 0.35)), 0.9)); // 창끝이 길고 뾰족
  lightRush(p, t, T.glint, 4, F, 0, C, o.seed, 0.24);
  // 꿰뚫은 자리: 세로로 납작한 빛 고리가 퍼지며 사라짐
  const g = u - FLASH;
  if (g >= 0 && g < 0.22) {
    const q = g / 0.22, r = 4 + 18 * ease.outQuad(q), k = 0.85 * (1 - q);
    for (let a = 0; a < Math.PI * 2; a += 0.6 / r) {
      const x = L + Math.cos(a) * r * 0.45, y = Math.sin(a) * r;
      p.blend(x, y, C[6], k);
      p.blend(x + (Math.cos(a) > 0 ? 1 : -1), y, C[5], k * 0.4);
    }
  }
  lensFlare(p, t, T.glint + FLASH, L, 0, C, 26, 0.16);
  burst(p, t, T.glint + FLASH, F, 0, 0, 0.5, 6, o.seed, fit(o.sparks, 4));
}

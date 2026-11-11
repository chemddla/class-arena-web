// 검사 기본 공격 참격 A: 일직선 — 칼자루에서 공격 범위 끝까지 바늘처럼 가는 빛줄기가 2칸 만에 뻗음
// 준비(칼자루 반짝) → 베기(앞으로 쭉, 앞쪽이 가장 굵고 끝은 뾰족) → 멈춤(흰 날 2칸 + 끝에서 불티) → 회복(뒤에서부터 가늘어지며 식고 점선만 남음)
import { fit, clamp, smooth, ease, sparkle } from "../../core/index.js";
import { MOON, MOON_SPARK, T, FLASH, hiltGlint, burst, dotted, lightRush, lensFlare, lightBeam } from "./_sword.js";

export const meta = {
  name: "Iai line",
  desc: "Sheathed-blade slash: a needle of light flashes from the hilt to the end of the reach in one frame with bloom and speed lines, holds white, then thins from the back and cools into a dotted trace.",
  tags: ["melee", "slash", "sword", "iai", "line", "one-shot"],
  size: [184, 48],
  origin: [14, 24],
  duration: 0.38,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, len: 126, w: 2.2, seed: 3 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), n = C.length, L = o.len;
  hiltGlint(p, t, C, sparkle);
  const u = t - T.glint;
  if (u < 0) return;
  const end = T.sweep + T.hold + T.trail;
  const head = L * ease.outExpo(clamp(u / FLASH)), tl = smooth(T.sweep + T.hold, end, u), tail = head * tl * 0.98, age = clamp(u / end);
  if (head - tail > 1) {
    lightBeam(p, tail, 0, head, 0, o.w * (1 - tl * 0.55), C, age, 1); // 반투명 경계 + 흰 심 + 후광, 앞쪽이 굵고 양끝 뾰족
    p.glowLine(tail, 0, head, 0, 4, C[5], 0.22 * (1 - age));
  }
  lightRush(p, t, T.glint, 4, L, 0, C, o.seed);
  lensFlare(p, t, T.glint + FLASH, L, 0, C);
  // 멈춤: 끝에서 반짝 + 앞으로 튀는 불티
  const g = u - T.sweep;
  if (g > -0.02 && g < 0.14) sparkle(p, L, 0, 6 * Math.sin(Math.PI * clamp((g + 0.02) / 0.18)), C[6], C[4], 0.6);
  burst(p, t, T.glint + FLASH, L, 0, 0, 0.75, 8, o.seed, fit(o.sparks, 4));
  // 지나간 자리 점선
  dotted(p, 4, tail, 0, C[4], 0.45 * (1 - smooth(T.sweep + T.hold + 0.05, end + 0.06, u)) * (tl > 0.02 ? 1 : 0));
}

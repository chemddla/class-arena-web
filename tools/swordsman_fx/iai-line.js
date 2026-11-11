// 검사 기본 공격 참격 A: 일직선 — 칼자루에서 공격 범위 끝까지 바늘처럼 가는 빛줄기가 2칸 만에 뻗음
// 준비(칼자루 반짝) → 베기(앞으로 쭉, 앞쪽이 가장 굵고 끝은 뾰족) → 멈춤(흰 날 2칸 + 끝에서 불티) → 회복(뒤에서부터 가늘어지며 식고 점선만 남음)
import { fit, clamp, smooth, ease, sparkle } from "../../core/index.js";
import { MOON, MOON_SPARK, T, HIT, hiltGlint, burst, dotted } from "./_sword.js";

export const meta = {
  name: "Iai line",
  desc: "Sheathed-blade slash: a needle of moonlight shoots from the hilt to the end of the reach in two frames, holds white, then thins from the back and cools into a dotted trace.",
  tags: ["melee", "slash", "sword", "iai", "line", "one-shot"],
  size: [184, 48],
  origin: [14, 24],
  duration: 0.38,
  loop: false,
  fps: 30,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, len: 144, w: 2.6, seed: 3 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), n = C.length, L = o.len;
  hiltGlint(p, t, C, sparkle);
  const u = t - T.glint;
  if (u < 0) return;
  const end = T.sweep + T.hold + T.trail;
  const head = L * ease.outExpo(clamp(u / T.sweep)), tl = smooth(T.sweep + T.hold, end, u), tail = head * tl * 0.98, age = clamp(u / end);
  const hot = u < T.sweep + T.hold; // 맞는 순간까지는 흰 날
  if (head - tail > 1) {
    const W = o.w * (1 - tl * 0.6);
    p.shade(tail - 1, -W - 2, head + 1, W + 2, (x, y, out) => {
      const v = (x - tail) / (head - tail);
      if (v < 0 || v > 1) return;
      const w = W * Math.pow(Math.sin(Math.PI * Math.pow(v, 0.55)), 0.8) + 0.35; // 앞쪽이 굵고 끝은 뾰족
      const q = Math.abs(y) / w;
      if (q > 1) return;
      const ci = hot && q < 0.5 ? 0 : Math.round(q * (n - 1) * 0.7 + age * 2.6 + (1 - v) * 0.8);
      out.c = C[n - 1 - clamp(ci, 0, n - 2)];
      out.a = Math.min(1, v / 0.15) * (q > 0.75 ? 0.7 : 1);
    });
    p.glowLine(tail, 0, head, 0, 6, C[4], 0.28 * (1 - age));
  }
  // 멈춤: 끝에서 반짝 + 앞으로 튀는 불티
  const g = u - T.sweep;
  if (g > -0.02 && g < 0.16) sparkle(p, L, 0, 7 * Math.sin(Math.PI * clamp((g + 0.02) / 0.18)), C[6], C[4], 0.6);
  burst(p, t, HIT, L, 0, 0, 0.75, 8, o.seed, fit(o.sparks, 4));
  // 지나간 자리 점선
  dotted(p, 4, tail, 0, C[3], 0.6 * (1 - smooth(T.sweep + T.hold + 0.05, end + 0.06, u)) * (tl > 0.02 ? 1 : 0));
}

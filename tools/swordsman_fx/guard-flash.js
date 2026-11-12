// 방어 성공 섬광 (패링 · 투사체 튕겨냄 · 심검): 칼과 부딪친 자리에서 1칸 만에 번쩍 — 흰 심 + 네 갈래 빛살(가로가 가장 김) + 짧은 대각 빛살,
// 퍼지는 가는 충격 고리, 사방으로 튀는 불티, 막아 낸 쪽으로 휘는 작은 빛의 초승달. 0.35초에 식음
// 좌표: 기준점(0, 0) = 부딪친 자리, +x = 막은 공격이 날아온 쪽
import { fit, clamp, rng, TAU } from "../../core/index.js";
import { MOON, MOON_SPARK, burst, lightCrescent } from "./_sword.js";

export const meta = {
  name: "Guard flash",
  desc: "A block lands: in one frame a white core flares with a four-point star (longest across) and short diagonal rays, a thin shock ring spreads, sparks spray all round and a small crescent of light bends toward the blocked attack, then it all cools in a third of a second.",
  tags: ["sword", "parry", "block", "flash", "one-shot"],
  size: [120, 100],
  origin: [60, 50],
  duration: 0.35,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, glow: ["#ffffff", "#e0f2fe", "#a5d8ff", "#74b9f5"], seed: 5 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), S = fit(o.sparks, 4), G = fit(o.glow, 4);
  const k = t < 0.025 ? 1 : Math.pow(1 - clamp((t - 0.025) / 0.3), 1.5); // 첫 칸 가장 밝고 부드럽게 식음
  if (k <= 0) return;
  p.glow(0, 0, 30, G[3], 0.55 * k);
  p.glow(0, 0, 14, G[2], 0.8 * k);
  p.glow(0, 0, 6, C[6], k);
  const ray = (dx, dy, len, a) => { // 빛살: 가운데서 끝으로 가늘고 옅어짐
    const n = Math.ceil(len);
    for (let i = 0; i <= n; i++) p.blend(dx * i, dy * i, C[6], a * (1 - i / n));
    p.glowLine(0, 0, dx * len, dy * len, 2, G[1], 0.35 * a);
  };
  const L = 34 * (0.55 + 0.45 * k);
  ray(1, 0, L, k); ray(-1, 0, L, k);
  ray(0, 1, L * 0.6, k); ray(0, -1, L * 0.6, k);
  const d = Math.SQRT1_2;
  for (const [sx, sy] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) ray(sx * d, sy * d, L * 0.3, 0.8 * k);
  const r = 6 + 34 * Math.pow(clamp(t / 0.2), 0.6), rk = 1 - clamp(t / 0.2); // 충격 고리
  if (rk > 0) for (let i = 0, n = Math.ceil(TAU * r); i < n; i++) { const q = (i / n) * TAU; p.blend(Math.cos(q) * r, Math.sin(q) * r * 0.8, C[5], 0.7 * rk); }
  lightCrescent(p, C, 8, 0, 0, 16, 1.7, 3, clamp(t / 0.05), 1, clamp(t / 0.3), 0.9); // 막아 낸 쪽으로 휜 빛
  for (let i = 0; i < 8; i++) burst(p, t, i * 0.003, 0, 0, (i / 8) * TAU + 0.3, 0.35, 3, o.seed + i, S);
}

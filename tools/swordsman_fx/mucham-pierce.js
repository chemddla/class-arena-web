// 무참 찌르기: 칼끝이 목표 가슴을 꿰뚫는 빛의 창 — 뒤에서 앞으로 1칸 만에 빛의 날이 뻗고 (일섬 갈라짐과 같은 칠), 뚫고 나간 끝에서 고리처럼 퍼지는 섬광 + 앞쪽 불티
// 좌표: 기준점(0, 0) = 목표 가슴, +x = 찌르는 쪽
import { fit, clamp } from "../../core/index.js";
import { MOON, MOON_SPARK, FLASH, burst, lensFlare, lightRush } from "./_sword.js";
import { blade } from "./issen.js";

export const meta = {
  name: "Mucham pierce",
  desc: "A spear of light thrusts through the target's chest in one frame, flares where it exits and throws sparks forward, then thins and cools.",
  tags: ["melee", "thrust", "sword", "pierce", "one-shot"],
  size: [190, 70],
  origin: [90, 35],
  duration: 0.45,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, W: 4.5, seed: 6 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), S = fit(o.sparks, 4);
  lightRush(p, t, 0, -80, 40, 0, C, o.seed, 0.14); // 찌르기 직전 칼바람
  blade(p, C, 150, o.W, clamp(t / FLASH), clamp((t - 0.05) / 0.38), -70); // 잔상: 0.38초에 걸쳐 옅어짐
  lensFlare(p, t, FLASH, 0, 0, C, 24, 0.14);
  lensFlare(p, t, FLASH, 72, 0, C, 16, 0.12);
  const u = t - FLASH;
  if (u > 0 && u < 0.16) { // 뚫고 나간 끝: 세로로 납작한 빛 고리가 퍼짐
    const k = 1 - u / 0.16, r = 4 + 70 * u;
    for (let a = 0; a < 6.28; a += 0.06) p.blend(78 + Math.cos(a) * r * 0.35, Math.sin(a) * r, C[5], 0.6 * k * (0.6 + 0.4 * Math.cos(a)));
  }
  burst(p, t, FLASH, 74, 0, 0, 0.5, 7, o.seed, S);
}

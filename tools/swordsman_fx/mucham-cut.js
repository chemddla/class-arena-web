// 무참 베기: 목표 가슴 위를 빛의 초승달 하나가 1칸 만에 가르고 (발도·섬단과 같은 빛의 날: 흰 광선 테두리 · 뒤로 옅어지는 면 · 뾰족한 양끝),
// 가운데 섬광 + 불티 → 잔상으로 오래 남아 가늘어지며 식음. 게임이 자세마다 각도를 돌려 내려 베기·올려 베기·가로 베기로 씀
// 좌표: 기준점(0, 0) = 목표 가슴, 초승달은 기준점을 지나 +x 쪽으로 볼록 (= 칼이 지나가는 쪽)
import { fit, clamp, sparkle } from "../../core/index.js";
import { MOON, MOON_SPARK, FLASH, burst, lensFlare, lightCrescent } from "./_sword.js";

export const meta = {
  name: "Mucham cut",
  desc: "A light crescent cuts across the target's chest in one frame, flares with sparks, thins and cools.",
  tags: ["melee", "slash", "sword", "crescent", "one-shot"],
  size: [150, 150],
  origin: [75, 75],
  duration: 0.5,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, W: 7, Rc: 70, span: 1.45, seed: 2 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), S = fit(o.sparks, 4);
  const rv = clamp(t / FLASH), life = clamp((t - 0.05) / 0.42); // 잔상: 0.4초에 걸쳐 가늘어지며 옅어짐 (다음 타가 0.2초 뒤라 두세 겹이 겹쳐 보임)
  lightCrescent(p, C, 0, 0, 0, o.Rc, o.span, o.W, rv, 1, life, 1, 2, 4);
  lensFlare(p, t, FLASH * 0.6, 0, 0, C, 26, 0.14);
  const g = t - FLASH;
  if (g > 0 && g < 0.12) sparkle(p, 2, 0, 1 + 5 * Math.sin(Math.PI * g / 0.12), C[6], C[4], 0.6);
  burst(p, t, FLASH, 2, 0, 0, 0.9, 6, o.seed, fit(o.sparks, 4));
}

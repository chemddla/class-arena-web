// 패링 자세: 칼을 세워 받는 순간 몸 앞에 세로 빛의 초승달이 1칸 만에 그어지고(위 → 아래), 칼날 쪽에 작은 반짝임, 0.3초에 식음
// 좌표: 기준점(0, 0) = 발, +x = 검사가 보는 쪽
import { fit, clamp, sparkle } from "../../core/index.js";
import { MOON, lightCrescent } from "./_sword.js";

export const meta = {
  name: "Guard ready",
  desc: "Parry stance: a tall crescent of light is drawn top to bottom in front of the body in one frame, a small glint flicks on the blade, and it cools in 0.3 s.",
  tags: ["sword", "parry", "guard", "one-shot"],
  size: [90, 90],
  origin: [30, 74],
  duration: 0.3,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, glow: ["#ffffff", "#e0f2fe", "#a5d8ff", "#74b9f5"] },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), G = fit(o.glow, 4);
  const rv = clamp(t / 0.04), life = clamp((t - 0.03) / 0.27);
  lightCrescent(p, C, 16, -30, 0, 34, 1.5, 4, rv, 1, life, 1);
  p.glow(16, -30, 18, G[3], 0.3 * (1 - life));
  const g = clamp(t / 0.12);
  if (g < 1) sparkle(p, 10, -46, 1 + 5 * Math.sin(Math.PI * g), C[6], G[2], 0.8);
}

// 축전 5 (반복, 몸): 다음 스킬이 강화로 나간다는 표시. 기준점 = 발. 오버로드 오라보다 가볍게:
// 금빛 알갱이 3개가 몸 둘레 타원을 돌며 꼬리를 끌고, 가끔 몸 가장자리에서 짧은 금빛 잔전류가 튐 (설계서 2절 "축전 5가 되면 몸 둘레에 잔전류")
import { fit, rng, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { GOLD_V, GOLD_SPARK_V, onBody } from "./_volt.js";

export const meta = {
  name: "Volt charged",
  desc: "Fully charged: three gold motes orbit the body trailing light, now and then a short gold arc snaps off its edge.",
  tags: ["lightning", "electric", "buff", "charge", "loop"],
  size: [112, 120],
  origin: [56, 108],
  duration: 1.2,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: GOLD_V, sparks: GOLD_SPARK_V, h: 88, w: 30, seed: 43 },
};

const FPS = 20, N = 24, SNAP = [3, 4, 15];

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, ph = f / N;
  const cy = -o.h * 0.5, rx = o.w, ry = o.h * 0.18;
  p.glow(0, cy, o.h * 0.45, C[4], 0.12);
  // 도는 알갱이 3개 (뒤쪽 반은 어둡게)
  for (let i = 0; i < 3; i++) {
    const a0 = ph * TAU + (i / 3) * TAU, h = cy - 14 + i * 14;
    for (let j = 5; j >= 0; j--) {
      const a = a0 - j * 0.12, [x, y] = onBody(a, 0, h, rx, ry), back = Math.sin(a) < 0;
      const c = j === 0 ? (back ? C[5] : WHITE) : j < 3 ? (back ? C[3] : C[5]) : back ? C[2] : C[4];
      p.px(x, y, c);
      if (j === 0) p.glow(x, y, back ? 4 : 6, C[5], back ? 0.25 : 0.5);
    }
  }
  if (SNAP.includes(f)) {
    const R = rng(o.seed, 1, f), a = R.range(0, TAU), [x0, y0] = onBody(a, 0, cy, rx * 0.8, o.h * 0.42), l = R.range(10, 18);
    crackle(p, zigzag(R, x0, y0, x0 + Math.cos(a) * l, y0 + Math.sin(a) * l, 0.45, 0.4), 0.8, C, 0.45);
  }
}

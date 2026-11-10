// 오버로드 지속 (반복, 몸에 두름): 10초 동안 몸 둘레를 플라즈마가 감쌈. 기준점 = 발.
// 감전(shock)보다 굵고 많음: 몸 둘레를 크게 도는 휜 전류 3~4줄이 매 프레임 새로 튀고, 머리 위로 정전기 가지가 솟고,
// 정전기 알갱이가 계속 위로 떠오르고, 발밑에는 작은 플라즈마 웅덩이가 깜박임. 몸 뒤 빛이 박동처럼 밝아졌다 어두워짐
import { fit, rng, cycle, TAU, WHITE } from "../../core/index.js";
import { zigzag, bowed, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V, onBody } from "./_volt.js";

export const meta = {
  name: "Volt overload aura",
  desc: "An overloaded body wrapped in plasma: wide bowed arcs orbit it, static forks rise off the head, motes stream upward, a flickering pool of current at the feet, a pulsing glow behind.",
  tags: ["lightning", "electric", "plasma", "aura", "buff", "loop"],
  size: [136, 140],
  origin: [68, 124],
  duration: 1,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, h: 88, w: 28, seed: 21 },
};

const FPS = 20, N = 20;

export function drawBack(p, t, o) {
  const C = fit(o.palette, 8), f = Math.floor(t * FPS + 1e-6) % N, beat = 0.7 + 0.3 * Math.max(0, Math.sin((f / N) * TAU * 2));
  p.glow(0, -o.h * 0.5, o.h * 0.75, C[3], 0.3 * beat);
  // 발밑 빛 (납작하게 세 점)
  for (const x of [-o.w * 0.7, 0, o.w * 0.7]) p.glow(x, -1, 12, C[4], 0.3 * beat);
}

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, R = rng(o.seed, 1, f);
  const cy = -o.h * 0.5, rx = o.w, ry = o.h * 0.52;
  // 몸 둘레를 크게 도는 휜 전류
  const n = 3 + R.int(0, 1);
  for (let i = 0; i < n; i++) {
    const a0 = R.range(0, TAU), a1 = a0 + R.range(0.9, 1.8) * R.sign();
    const [x0, y0] = onBody(a0, 0, cy, rx * R.range(0.85, 1.15), ry * R.range(0.8, 1.05)), [x1, y1] = onBody(a1, 0, cy, rx * R.range(0.85, 1.15), ry * R.range(0.8, 1.05));
    crackle(p, bowed(R, x0, y0, x1, y1, R.range(6, 12) * R.sign(), 0.25, 0.45), R.range(0.55, 1), C, 0.45);
  }
  // 머리 위 정전기 가지
  if (R.next() < 0.75) {
    const x0 = R.range(-10, 10), y0 = -o.h + R.range(0, 8);
    crackle(p, zigzag(R, x0, y0, x0 + R.range(-12, 12), y0 - R.range(10, 20), 0.45, 0.6), R.range(0.5, 0.85), C, 0.4);
  }
  // 발밑에서 땅으로
  if (R.next() < 0.6) {
    const x = R.range(-o.w, o.w);
    crackle(p, zigzag(R, x * 0.5, -R.range(8, 16), x, 0, 0.4, 0.4), 0.55, C, 0.35);
  }
  // 떠오르는 정전기 알갱이
  cycle(t, 1, 16, o.seed + 5, (g) => g.range(0.45, 0.8), (age, L, r) => {
    const a = r.range(0, TAU), [sx, sy] = onBody(a, 0, cy, rx * 1.05, ry), q = age / L;
    const x = sx + Math.sin(age * 12 + r.range(0, 6)) * 1.5, y = sy - age * r.range(30, 55);
    p.px(x, y, q < 0.3 ? WHITE : q < 0.6 ? S[1] : S[2]);
    if (q < 0.4) p.px(x, y + 1, S[2]);
    p.glow(x, y, 3, S[2], 0.4 * (1 - q));
  });
}

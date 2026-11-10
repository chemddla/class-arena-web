// 전자포 끝 (반복): 포가 끝나는 자리 (8칸 끝 또는 맵 끝). 기준점 = 포 끝 (포는 왼쪽에서 들어옴). 게임은 몸통을 포 끝까지 그린 뒤 이 그림을 위에 덮음.
// - 몸통 가닥이 끝에서 한 점으로 모였다가(왼쪽 24px) 앞으로 부채처럼 터져 흩어짐
// - 끝에 흰 심 + 큰 빛 → 이음매를 빛이 덮음, 매 프레임 크기가 떨림
// - 앞으로 퍼지는 세로 고리 (충격파가 끝에서 터져 나감)
// - 앞으로 갈라지는 전류 부채, 앞으로 흩어지는 불티
import { fit, rng, cycle, fly, clamp, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";

export const meta = {
  name: "Volt rail tip",
  desc: "The far end of a plasma railgun beam: its strands pinch to a point, a white flare bursts, a shock ring blows forward, arcs fan out, sparks scatter ahead.",
  tags: ["lightning", "electric", "plasma", "beam", "impact", "loop"],
  size: [176, 176],
  origin: [64, 88],
  duration: 0.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, thick: 1, seed: 14 },
};

const FPS = 20, N = 12;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, ph = f / N, R = rng(o.seed, 1, f), k = o.thick;
  const A = 11 * k, jit = R.range(0.85, 1.2);
  p.glow(0, 0, 28 * k * jit, C[4], 0.5);   // 캔버스 안에 들어오게
  p.glow(0, 0, 14 * k, C[6], 0.6);
  // 앞으로 터져 나가는 고리: 끝에서 생겨 커지며 앞으로
  for (let j = 0; j < 2; j++) {
    const u = (ph * 2 + j * 0.5) % 1, cx = 4 + 40 * u, ry = A * (1.4 + 2 * u), rx = (3 + 5 * u) * k;
    for (let a = 0, da = 0.6 / Math.max(ry, rx); a < TAU; a += da) {
      if (u > 0.6 && ((a * 9) | 0) % 2) continue;
      const x = cx + Math.cos(a) * rx, y = Math.sin(a) * ry, fr = Math.cos(a) > 0;
      p.px(x, y, fr ? (u < 0.35 ? WHITE : u < 0.7 ? C[5] : C[3]) : C[2]);
    }
  }
  // 모였다가 앞으로 흩어지는 가닥
  for (const [i, sp] of [0, TAU / 3, (2 * TAU) / 3].entries()) {
    for (let x = -24; x <= 0; x += 0.5) {
      const g = TAU * ((2 * x) / 120 - 2 * ph) + sp, pinch = clamp(-x / 24), y = A * pinch * Math.sin(g), z = Math.cos(g);
      p.px(x, y, z > 0.3 ? WHITE : z > -0.3 ? C[5] : C[3]);
    }
    const a = (i - 1) * 0.55 + R.range(-0.2, 0.2), l = R.range(26, 46) * (0.7 + 0.3 * k);
    crackle(p, zigzag(R, 2, 0, Math.cos(a) * l, Math.sin(a) * l, 0.3, 0.6), R.range(0.6, 1), C, 0.45);
  }
  // 흰 심 + 십자 섬광
  p.ellipse(0, 0, 4.5 * k * jit, 5.5 * k * jit, C[6]);
  p.ellipse(0, 0, 2.5 * k * jit, 3 * k * jit, WHITE);
  p.line(-8 * k, 0, 26 * k * jit, 0, WHITE);
  p.line(0, -18 * k * jit, 0, 18 * k * jit, C[6]);
  cycle(t, 0.6, 14, o.seed + 3, (g) => g.range(0.2, 0.4), (age, L, r) => {
    const a = r.range(-1.1, 1.1), sp = r.range(110, 220), q = 1 - age / L;
    const [x, y] = fly(4, r.range(-A, A) * 0.4, Math.cos(a) * sp, Math.sin(a) * sp, age, 150, 3);
    p.line(x, y, x - Math.cos(a) * 3, y - Math.sin(a) * 3, q > 0.5 ? S[1] : S[3]);
    p.px(x, y, q > 0.5 ? WHITE : S[2]);
    p.glow(x, y, 3, S[2], 0.4 * q);
  });
}

// 전자포 끝 (반복): 포가 끝나는 자리. 기준점 = 포 끝 (포는 왼쪽에서 들어옴). 게임은 몸통을 포 끝까지 그린 뒤 이 그림을 위에 덮음.
// - 몸통과 같은 색·결 무늬의 포가 끝에서 둥글게 닫힘 (흰 테두리 띠가 머리를 감싸며 돎)
// - 끝에 세로·가로 빛살 (흰 동그라미 섬광은 없음), 매 프레임 길이가 떨림
// - 앞으로 갈라지는 굵은 번개 3줄
import { fit, rng, clamp, TAU, WHITE } from "../../core/index.js";
import { zigzag, stroke } from "../lightning/_lib.js";
import { PLASMA_V } from "./_volt.js";
import { edge, beamColor } from "./_wave.js";

export const meta = {
  name: "Volt rail tip",
  desc: "The end of a heavy energy cannon: the beam closes in a rounded head ringed by its white rim, cross rays, heavy forks thrown forward.",
  tags: ["lightning", "electric", "plasma", "beam", "impact", "loop"],
  size: [240, 480],
  origin: [80, 240],
  duration: 0.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, thick: 1, seed: 14 },
};

const FPS = 20, N = 12, TAIL = 24;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), f = Math.floor(t * FPS + 1e-6) % N, ph = f / N, R = rng(o.seed, 1, f), k = o.thick, r0 = edge(0, ph, k);
  const cap = r0 * 0.75, jit = R.range(0.9, 1.15);
  p.glow(cap * 0.5, 0, r0 * 2, C[4], 0.55);
  // 둥글게 닫히는 머리: x ≥ 0에서 반지름이 타원으로 줄어듦, 결 무늬는 몸통과 같은 식 (x를 토막 좌표로)
  p.shade(-TAIL, -r0 * 1.2, cap + 2, r0 * 1.2, (x, y, out) => {
    const s = x <= 0 ? 1 : Math.sqrt(Math.max(0, 1 - (x / cap) ** 2));
    if (s <= 0) return;
    const c = beamColor(((x % 120) + 120) % 120, y, edge(Math.max(0, x), ph, k) * s, ph, C, WHITE);
    if (c) out.c = c;
  });
  // 빛살 (흰 동그라미 섬광은 뺌 · 사용자 요청 2026-11-10)
  const fx = cap * 0.35, b = r0 * 0.55 * jit;
  p.glow(fx, 0, b * 1.4, C[5], 0.35);
  p.line(fx - r0, 0, fx + r0 * 1.8 * jit, 0, WHITE);
  for (let y = -r0 * 1.9 * jit; y <= r0 * 1.9 * jit; y++) p.px(fx, y, Math.abs(y) < r0 ? WHITE : C[5]);
  // 앞으로 갈라지는 굵은 번개
  const R2 = rng(o.seed, 4, f >> 1);
  for (let i = 0; i < 3; i++) {
    const a = (i - 1) * 0.5 + R2.range(-0.2, 0.2), l = R2.range(50, 90) * k, x0 = fx + Math.cos(a) * b, y0 = Math.sin(a) * b;
    stroke(p, zigzag(R2, x0, y0, x0 + Math.cos(a) * l, y0 + Math.sin(a) * l, 0.3, 0.6), f % 2 ? 0.7 : 1, C, 0.7 * k, { light: 0.5 });
  }
}

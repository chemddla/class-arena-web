// 전자포 총구 (반복): 내민 손바닥 앞. 기준점 = 손바닥 (포는 여기서 오른쪽으로 나감, 몸통 토막은 x = 0부터 이어 그림).
// - 손바닥에서 포가 나팔처럼 벌어지며 시작 (첫 28px: 반두께 0.45 → 1, 몸통과 같은 색·결 무늬)
// - 세로 빛기둥: 손바닥 앞을 위아래로 가르는 흰 빛줄 (반두께의 2~2.4배), 매 프레임 길이가 떨림
// - 손바닥의 흰 섬광 덩어리 + 가로 빛살, 뒤로 튀는 반동 전류
import { fit, rng, clamp, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";
import { edge, beamColor } from "./_wave.js";

export const meta = {
  name: "Volt rail muzzle",
  desc: "The muzzle of a heavy energy cannon: the beam flares open from the palm, a tall vertical pillar of light cuts through it, a white burst at the hand, recoil arcs.",
  tags: ["lightning", "electric", "plasma", "beam", "muzzle", "loop"],
  size: [200, 480],
  origin: [72, 240],
  duration: 0.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, thick: 1, seed: 13 },
};

const FPS = 20, N = 12, OPEN = 28;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), f = Math.floor(t * FPS + 1e-6) % N, ph = f / N, R = rng(o.seed, 1, f), k = o.thick, r0 = edge(0, ph, k);
  p.glow(6, 0, r0 * 1.8, C[4], 0.55);
  // 나팔처럼 벌어지는 포의 시작
  p.shade(-2, -r0 * 1.2, OPEN, r0 * 1.2, (x, y, out) => {
    const u = clamp(x / OPEN), r = edge(Math.max(0, x), ph, k) * (0.45 + 0.55 * Math.sqrt(u));
    const c = beamColor(Math.max(0, x), y, r, ph, C, WHITE);
    if (c) out.c = c;
  });
  // 세로 빛기둥
  const ph2 = r0 * (2 + 0.4 * R.next()), px = 4;
  p.glowLine(px, -ph2, px, ph2, 8 * k, C[5], 0.45);
  for (let y = -ph2; y <= ph2; y++) {
    const u = Math.abs(y) / ph2;
    p.px(px, y, u < 0.5 ? WHITE : u < 0.8 ? C[6] : C[4]);
    const w = Math.round((1 - u) * 2 * k);   // 가운데가 굵고 끝으로 가늘게
    for (let d = 1; d <= w; d++) (p.px(px - d, y, d < w ? WHITE : C[6]), p.px(px + d, y, d < w ? WHITE : C[6]));
  }
  // 손바닥 섬광
  const b = r0 * (0.5 + 0.08 * R.next());
  p.ellipse(px + b * 0.35, 0, b * 0.5, b, C[6]);   // 손바닥 앞쪽으로 (뒤로 넓으면 얼굴을 덮음)
  p.ellipse(px + b * 0.35, 0, b * 0.32, b * 0.7, WHITE);
  p.line(px - r0 * 0.8, 0, px + r0 * 1.6, 0, WHITE);
  for (let i = 0; i < 3; i++) {
    const a = Math.PI + R.range(-1.1, 1.1), l = R.range(16, 30) * k;
    crackle(p, zigzag(R, px, R.range(-b, b), px + Math.cos(a) * l, Math.sin(a) * l * 1.4, 0.4, 0.4), R.range(0.55, 0.9), C, 0.4);
  }
}

// 전자포 몸통 (반복, 가로로 이어 붙임): 굵은 플라즈마 포의 120px 한 토막. 기준점 = 왼쪽 끝 세로 가운데.
// 게임은 이 토막을 포 길이만큼 가로로 이어 그림 (왼쪽·오른쪽 끝이 이음매 없이 맞음: 모든 무늬가 120px 주기)
// - 흰 심 → 하늘 몸 → 파랑 → 남보라 테두리 (단계가 딱 끊기는 도트 램프), 두께가 물결처럼 숨 쉼
// - 심 안에 밝은 덩어리가 오른쪽으로 흘러감 (0.6초에 한 토막 = 이음매 없는 반복)
// - 포 표면을 휘감는 짧은 전류와 위아래로 튀는 가지
// thick: 1 = 폭 1칸 (일반), 2 = 폭 2칸 (강화)
import { fit, clamp, rng, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V } from "./_volt.js";

const W = 120;
export const meta = {
  name: "Volt rail body",
  desc: "One seamless 120 px segment of a heavy plasma beam: white core, cyan body, violet fringe, breathing thickness, hot clumps streaming along the core, arcs wrapping its skin.",
  tags: ["lightning", "electric", "plasma", "beam", "tile", "loop"],
  size: [W, 128],
  origin: [0, 64],
  duration: 0.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, thick: 1, seed: 12 },
};

const FPS = 20, N = 12;
const per = (x, n, ph) => Math.sin(TAU * (n * x / W - ph));

export function draw(p, t, o) {
  const C = fit(o.palette, 8), f = Math.floor(t * FPS + 1e-6) % N, ph = f / N, R = rng(o.seed, 1, f), k = o.thick;
  const H = 13 * k;   // 몸 반두께
  const y0 = (x) => 1.5 * k * per(x, 1, ph) + 0.8 * k * per(x, 3, -ph * 2);
  const h = (x) => H * (1 + 0.14 * per(x, 2, ph * 2) + 0.08 * per(x, 5, -ph * 3));
  // 테두리 바깥 옅은 빛
  p.glowLine(-20, 0, W + 20, 0, H * 2.4, C[3], 0.28);
  p.shade(0, -H * 2.2, W, H * 2.2, (x, y, out) => {
    const d = Math.abs(y - y0(x)) / h(x);
    // 심 안의 흐르는 덩어리 (오른쪽으로 흐름: ph만큼 한 토막 이동)
    const clump = 0.5 + 0.5 * per(x, 4, ph * 4);
    if (d < 0.06 + 0.2 * clump * clump) return (out.c = WHITE);
    if (d < 0.36) return (out.c = C[6]);
    if (d < 0.6) return (out.c = C[5]);
    if (d < 0.8) return (out.c = C[4]);
    if (d < 0.95) return (out.c = C[3]);
    if (d < 1.18) { out.c = C[2]; out.a = 0.9; return; }
    if (d < 1.4) { out.c = C[1]; out.a = 0.55; return; }
  });
  p.glowLine(-10, 0, W + 10, 0, H * 0.6, C[5], 0.16);
  // 표면을 휘감는 전류: 토막 밖으로 넘친 부분은 반대쪽에 다시 그려 이음매를 맞춤
  const n = 2 + R.int(0, 1);
  for (let i = 0; i < n; i++) {
    const x0 = R.range(0, W), l = R.range(26, 48), s = R.sign(), ya = s * H * R.range(0.7, 1.2), yb = s * H * R.range(0.6, 1.4);
    const b = zigzag(R, x0, ya, x0 + l, yb, 0.35, 0.5), kk = R.range(0.5, 0.9);
    crackle(p, b, kk, C, 0.35);
    if (x0 + l > W) crackle(p, { paths: b.paths.map((q) => ({ w: q.w, pts: q.pts.map(([x, y]) => [x - W, y]) })) }, kk, C, 0.35);
  }
  // 위아래로 튀는 가지 1개
  if (R.next() < 0.7) {
    const x0 = R.range(8, W - 8), s = R.sign(), l = R.range(10, 18) * k;
    crackle(p, zigzag(R, x0, s * H * 0.9, x0 + R.range(-8, 8), s * (H + l), 0.4, 0.4), 0.7, C, 0.35);
  }
}

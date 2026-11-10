// 전자포 몸통 (반복, 가로로 이어 붙임): 에너지파. 120px 한 토막, 기준점 = 왼쪽 끝 세로 가운데. 무늬가 모두 120px·0.6초 주기라 이음매 없이 이어짐.
// - 넓은 흰 심 → 연하늘 → 하늘 → 파랑 테두리 (두께의 절반이 흰 심: 눈부신 에너지 덩어리)
// - 가장자리가 물결처럼 출렁이며 앞(오른쪽)으로 밀려 나감 (_wave.js edge)
// - 바깥: 반투명 기운이 감싸고, 테두리에서 에너지 혀가 뒤(왼쪽)로 흩날림 (포가 앞으로 밀고 나가는 속도감)
// - 안쪽: 흰·연하늘 흐름줄이 빠르게 앞으로 지나감
// - 가끔 표면에서 짧은 전류가 튐 (전격술사 정체성)
// thick: 1 = 폭 1칸 (일반), 2 = 폭 2칸 (강화)
import { fit, rng, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V } from "./_volt.js";
import { W, edge, band } from "./_wave.js";

export const meta = {
  name: "Volt rail body",
  desc: "One seamless 120 px segment of an energy wave beam: a wide white core, rippling edges pushed forward, a translucent aura shedding tongues backward, flow streaks racing inside.",
  tags: ["lightning", "electric", "plasma", "beam", "tile", "loop"],
  size: [W, 176],
  origin: [0, 88],
  duration: 0.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, thick: 1, seed: 12 },
};

const FPS = 20, N = 12;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), f = Math.floor(t * FPS + 1e-6) % N, ph = f / N, R = rng(o.seed, 1, f), k = o.thick;
  p.glowLine(-30, 0, W + 30, 0, 34 * k, C[3], 0.25);
  p.glowLine(-30, 0, W + 30, 0, 18 * k, C[5], 0.35);
  // 바깥 기운: 반지름의 1~1.45배, 진짜 반투명 (점무늬 없이)
  for (let x = 0; x < W; x++) {
    const r = edge(x, ph, k);
    for (let y = -Math.ceil(r * 1.45); y <= Math.ceil(r * 1.45); y++) {
      const d = Math.abs(y) / r;
      if (d >= 1 && d < 1.45) p.blend(x, y, d < 1.2 ? C[4] : C[3], 0.42 * (1.45 - d) / 0.45);
    }
  }
  // 에너지 혀: 테두리에서 바깥·뒤로 흩날리는 굵은 불꽃 (위아래 각 3개, 앞으로 흐름). 뿌리는 굵고 밝게, 끝은 가늘게 (어두운 꼬리 없음)
  for (let j = 0; j < 6; j++) {
    const r0 = rng(o.seed, 7, j), s = j % 2 ? 1 : -1, len = r0.range(16, 28) * k, rise = r0.range(5, 9) * k;
    const x0 = (((r0.range(0, W) + ph * W) % W) + W) % W;
    for (const ox of [x0, x0 + W])
      for (let i = 0; i <= len; i++) {
        const u = i / len, x = ox - i, re = edge(((x % W) + W) % W, ph, k);
        const y = s * (re * 0.92 + rise * Math.sin(u * Math.PI * 0.6) + Math.sin(u * 5 + j + ph * TAU) * 1.2), w = Math.round((1 - u) * 2 * k);
        for (let d = 0; d <= w; d++) p.px(x, y + s * d * -1, u < 0.35 ? C[6] : C[5]);
      }
  }
  // 몸: 띠 칠하기
  p.shade(0, -60 * k, W, 60 * k, (x, y, out) => {
    const c = band(Math.abs(y) / edge(x, ph, k), C, WHITE);
    if (c) out.c = c;
  });
  // 흐름줄: 흰 심 가장자리·하늘 띠 안을 빠르게 앞으로 (0.6초에 240px)
  for (let j = 0; j < 7; j++) {
    const r0 = rng(o.seed, 5, j), v = r0.sign() * r0.range(0.5, 0.82), len = r0.range(12, 26);
    const x0 = (((r0.range(0, W) + ph * 2 * W) % W) + W) % W;
    for (const ox of [x0, x0 - W])
      for (let i = 0; i < len; i++) {
        const x = ox + i, y = v * edge(((x % W) + W) % W, ph, k);
        p.px(x, y, Math.abs(v) < 0.62 ? C[5] : WHITE);
      }
  }
  // 가끔 튀는 전류 (넘친 부분은 반대쪽에)
  if (R.next() < 0.6) {
    const x0 = R.range(0, W), s = R.sign(), l = R.range(14, 26), r = edge(x0, ph, k);
    const b = zigzag(R, x0, s * r, x0 + l * R.range(0.3, 0.8), s * (r * 1.5 + R.range(4, 10)), 0.4, 0.5), kk = R.range(0.5, 0.85);
    crackle(p, b, kk, C, 0.35);
    if (x0 + l > W - 4) crackle(p, { paths: b.paths.map((q) => ({ w: q.w, pts: q.pts.map(([x, y]) => [x - W, y]) })) }, kk, C, 0.35);
  }
}

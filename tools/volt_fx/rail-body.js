// 전자포 몸통 (반복, 가로로 이어 붙임): 120px 한 토막. 기준점 = 왼쪽 끝 세로 가운데. 무늬가 모두 120px·0.6초 주기라 이음매 없이 이어짐.
// 굵은 색 띠 관 대신 "빛으로 된 포":
// - 심: 3px 흰 줄 + 양옆 연하늘, 둘레를 반투명 플라즈마 몸이 감싸며 숨 쉼
// - 가닥: 심을 꼬며 흐르는 플라즈마 가닥 3줄 (위상이 다른 사인, 앞을 지날 땐 밝고 뒤로 갈 땐 어두움 → 꼬임이 입체로 보임), 오른쪽으로 흘러감
// - 충격 고리: 세로로 납작한 고리가 60px 간격으로 포를 따라 빠르게 날아감 (레일건 느낌), 앞 반은 밝게·뒤 반은 어둡게
// - 빛: 테두리 단계 칠 대신 넓고 옅은 빛 + 심을 따라 뜨거운 빛
// - 가끔 표면에서 튀는 짧은 전류
// thick: 1 = 폭 1칸 (일반), 2 = 폭 2칸 (강화)
import { fit, rng, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V } from "./_volt.js";

const W = 120;
export const meta = {
  name: "Volt rail body",
  desc: "One seamless 120 px segment of a plasma railgun beam: a thin white core, three plasma strands braiding round it, flat shock rings racing along, a translucent plasma sheath, a soft wide glow.",
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
  const A = 11 * k;   // 가닥이 심에서 벌어지는 폭
  // 빛: 넓고 옅게 → 가운데 뜨겁게
  p.glowLine(-30, 0, W + 30, 0, 30 * k, C[2], 0.22);
  p.glowLine(-30, 0, W + 30, 0, 16 * k, C[4], 0.3);
  p.glowLine(-30, 0, W + 30, 0, 6 * k, C[6], 0.45);
  // 가닥 3줄: y = A·sin(2π(2x/W − 2ph) + 위상), 깊이 = cos(같은 각) → 앞(>0)은 밝게
  const strands = [0, TAU / 3, (2 * TAU) / 3];
  const back = [], front = [];
  for (const [i, sp] of strands.entries())
    for (let x = 0; x < W; x += 0.5) {
      const g = TAU * ((2 * x) / W - 2 * ph) + sp, y = A * Math.sin(g) * (0.85 + 0.15 * Math.sin(TAU * (x / W) + i)), z = Math.cos(g);
      (z > 0 ? front : back).push([x, y, z]);
    }
  for (const [x, y, z] of back) p.px(x, y, z > -0.5 ? C[3] : C[2]);
  // 플라즈마 몸: 심 둘레를 반투명 하늘색이 감쌈 (점무늬 없이 진짜 반투명), 두께가 120px 주기로 살짝 숨 쉼
  for (let x = 0; x < W; x++) {
    const sh = (4 + 1.2 * Math.sin(TAU * (3 * x / W - 3 * ph))) * k;
    for (let d = -Math.ceil(sh); d <= Math.ceil(sh); d++) {
      const u = Math.abs(d) / sh;
      if (u <= 1) p.blend(x, d, u < 0.6 ? C[5] : C[4], 0.55 - 0.3 * u);
    }
  }
  // 심: 흰 줄 (일반 3px, 강화 5px) + 양옆 1px 연하늘
  const w = k > 1 ? 2 : 1;
  for (let x = 0; x < W; x++) for (let d = -w - 1; d <= w + 1; d++) p.px(x, d, Math.abs(d) <= w ? WHITE : C[6]);
  for (const [x, y, z] of front) {   // 앞 가닥: 2px (밝은 줄 + 바깥쪽 한 줄)
    p.px(x, y, z > 0.6 ? WHITE : C[5]);
    p.px(x, y + Math.sign(y || 1), z > 0.6 ? C[5] : C[4]);
  }
  // 충격 고리: 60px 간격, 0.6초에 120px 이동 (이음매 없음), 토막 밖으로 넘친 것은 반대쪽에
  for (let j = 0; j < 2; j++) {
    const cx = (((j * 60 + ph * 120) % W) + W) % W, ry = A * 1.9, rx = 3 * k;
    for (const ox of [cx, cx - W, cx + W]) {
      if (ox < -rx - 2 || ox > W + rx + 2) continue;
      for (let a = 0, da = 0.6 / Math.max(ry, rx); a < TAU; a += da) {
        const x = ox + Math.cos(a) * rx, y = Math.sin(a) * ry, fr = Math.cos(a) > 0;
        p.px(x, y, fr ? (Math.abs(Math.sin(a)) > 0.8 ? C[6] : C[5]) : C[2]);
      }
    }
  }
  // 표면에서 튀는 짧은 전류 (이음매: 넘친 부분은 반대쪽에)
  if (R.next() < 0.75) {
    const x0 = R.range(0, W), s = R.sign(), l = R.range(14, 28);
    const b = zigzag(R, x0, s * A * 0.8, x0 + l * R.range(0.4, 1), s * (A * 1.3 + R.range(4, 12) * k), 0.4, 0.5), kk = R.range(0.5, 0.85);
    crackle(p, b, kk, C, 0.35);
    if (x0 + l > W - 4) crackle(p, { paths: b.paths.map((q) => ({ w: q.w, pts: q.pts.map(([x, y]) => [x - W, y]) })) }, kk, C, 0.35);
  }
}

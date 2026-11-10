// 전자포 몸통 (반복, 가로로 이어 붙임): 120px 한 토막, 기준점 = 왼쪽 끝 세로 가운데. 무늬가 모두 120px·0.6초 주기라 이음매 없이 이어짐.
// 사용자 레퍼런스 느낌 (_wave.js 맨 위):
// - 판정 폭에 꽉 차는 굵은 포 (일반 반두께 40, 강화 80)
// - 위아래 테두리가 가장 밝은 흰빛 띠, 속은 짙은 남색 바탕 위로 가로 결 무늬(밝은 대시)가 줄마다 다른 속도로 빠르게 흐름
// - 포를 가로지르는 가늘고 긴 빛줄 (위아래·속)
// - 고리 번개는 따로 (rail-arc): 토막마다 같으면 울타리처럼 반복돼 보여서, 게임이 자리·시작 프레임을 흩뜨려 덧그림
// - 넓은 빛
// thick: 1 = 폭 1칸 (일반), 2 = 폭 2칸 (강화)
import { fit, WHITE } from "../../core/index.js";
import { PLASMA_V } from "./_volt.js";
import { W, edge, beamColor, flareLines } from "./_wave.js";

export const meta = {
  name: "Volt rail body",
  desc: "One seamless 120 px segment of a heavy energy cannon: blazing white rims, a dark core streaked with fast horizontal light, long flare lines across it.",
  tags: ["lightning", "electric", "plasma", "beam", "tile", "loop"],
  size: [W, 480],
  origin: [0, 240],
  duration: 0.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, thick: 1, seed: 12 },
};

const FPS = 20, N = 12;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), f = Math.floor(t * FPS + 1e-6) % N, ph = f / N, k = o.thick, r0 = edge(0, ph, k);
  p.glowLine(-40, 0, W + 40, 0, r0 * 1.7, C[3], 0.3);
  p.glowLine(-40, 0, W + 40, 0, r0 * 1.15, C[5], 0.25);
  // 몸
  p.shade(0, -r0 * 1.2, W, r0 * 1.2, (x, y, out) => {
    const c = beamColor(x, y, edge(x, ph, k), ph, C, WHITE);
    if (c) out.c = c;
  });
  // 테두리 바깥 반투명 기운 (점무늬 없이)
  for (let x = 0; x < W; x++) {
    const r = edge(x, ph, k);
    for (let d = 1.1; d < 1.3; d += 1 / r) for (const s of [-1, 1]) p.blend(x, s * r * d, C[4], 0.5 * (1.3 - d) / 0.2);
  }
  flareLines(p, 0, W, r0, f, o.seed, C, WHITE);
}

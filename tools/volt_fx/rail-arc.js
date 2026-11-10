// 전자포 고리 번개 (반복, 몸통 위에 덧그림): 포 위 테두리에서 크게 솟았다가 다시 포로 내려오는 굵은 번개 + 아래로 처지는 작은 고리.
// 기준점 = 포 가운데 줄 위의 고리 시작점 (왼쪽 발). 0.6초 반복, 2프레임마다 새 모양, 늘 보임.
// 게임: 포를 따라 150~200px마다 하나씩, 자리마다 시작 프레임을 다르게 (예: i × 5) 틀어서 반복이 안 보이게.
// thick: 1 = 일반 (반두께 40), 2 = 강화
import { fit, rng, WHITE } from "../../core/index.js";
import { bowed, stroke, crackle, zigzag } from "../lightning/_lib.js";
import { PLASMA_V } from "./_volt.js";
import { halfH } from "./_wave.js";

export const meta = {
  name: "Volt rail arc",
  desc: "Lightning loops off a heavy energy cannon: a big bolt arching up off the top rim and back down, a smaller one sagging below, re-struck and flickering.",
  tags: ["lightning", "electric", "plasma", "beam", "loop"],
  size: [240, 480],
  origin: [40, 240],
  duration: 0.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, thick: 1, seed: 15 },
};

const FPS = 20, N = 12, OFF = [];   // 꺼지는 프레임 없음 (사용자 요청 2026-11-10: 깜빡이지 않고 계속 보이게)

export function draw(p, t, o) {
  const C = fit(o.palette, 8), f = Math.floor(t * FPS + 1e-6) % N, k = o.thick, r = halfH(k);
  if (OFF.includes(f)) return;
  const R = rng(o.seed, 3, f >> 1), hot = f % 2 === 0;
  // 위로 크게 솟는 고리
  const L = R.range(70, 120) * k, h = R.range(1.1, 1.7) * r;
  const up = bowed(R, 0, -r * 0.92, L, -r * 0.92, -h, 0.16, 0.4);
  stroke(p, up, hot ? 1 : 0.75, C, 1.1 * k, { light: 0.55, hero: hot && f % 4 === 0 });
  // 아래로 처지는 작은 고리 (조금 뒤에서)
  const x0 = R.range(10, 50) * k, L2 = R.range(40, 70) * k;
  stroke(p, bowed(R, x0, r * 0.92, x0 + L2, r * 0.92, R.range(0.6, 1) * r, 0.18, 0.3), hot ? 0.85 : 0.6, C, 0.8 * k, { light: 0.45 });
  // 고리 발이 포에 닿는 자리: 작은 불꽃
  for (const [x, y] of [[0, -r * 0.92], [L, -r * 0.92]]) {
    p.glow(x, y, 10 * k, C[6], 0.5);
    crackle(p, zigzag(R, x, y, x + R.range(-8, 8), y + R.range(-8, 2), 0.5, 0.3), 0.7, C, 0.4);
    p.px(x, y, WHITE);
  }
}

// 전자포 공용 (2026-11-10 사용자 레퍼런스 "이 느낌"에서 가져온 표현, 그림은 새로 그림):
//   판정 폭에 꽉 차는 굵은 포 · 위아래 테두리가 가장 밝은 흰빛 · 속은 짙은 색 위로 가로 결 무늬가 빠르게 흐름 ·
//   포를 가로지르는 가늘고 긴 빛줄 · 포 위아래로 크게 솟았다 내려오는 고리 번개 · 총구의 세로 빛기둥
// 몸통·총구·끝이 같은 두께·색·결 무늬를 쓰게 해서 이음매가 맞음
import { TAU, rng, rand } from "../../core/index.js";

export const W = 120;   // 몸통 토막 길이 (이 주기로 모든 무늬가 반복)
/** 포 반두께: thick 1 = 폭 1칸(120px)의 몸 부분, 2 = 강화 폭 2칸 */
export const halfH = (k) => 40 * k;
/** 가장자리 반지름: 아주 살짝 출렁임 (앞으로 밀려 나감). 크게 흔들면 끝·총구 이음매가 어긋남 */
export function edge(x, ph, k) {
  return halfH(k) * (1 + 0.035 * Math.sin(TAU * ((2 * x) / W - 2 * ph)) + 0.02 * Math.sin(TAU * ((5 * x) / W - 5 * ph) + 1.3));
}

/**
 * 포 한 점의 색. x = 토막 좌표(결 무늬 주기 W), y = 세로, r = 그 자리 반지름, ph = 반복 위상.
 * 테두리 띠(d 0.8~1)가 가장 밝은 흰빛, 속(d < 0.78)은 짙은 바탕 위 가로 결: 2px 줄마다 속도·길이가 다른 밝은 대시가 앞으로 흐름
 * (줄마다 0.6초에 120px의 정수배 이동 → 이음매 없음). 가운데로 갈수록 대시가 밝고 촘촘함. 0 = 바깥
 */
export function beamColor(x, y, r, ph, C, WHITE) {
  const d = Math.abs(y) / r;
  if (d >= 1.1) return 0;
  if (d >= 1) return C[4];
  if (d >= 0.93) return C[6];
  if (d >= 0.8) return WHITE;
  if (d >= 0.76) return C[6];
  // 속: 결 무늬
  const row = Math.floor(y / 3), sp = 1 + Math.floor(rand(row, 3) * 3), n = 1 + Math.floor(rand(row, 5) * 2);   // 3px 줄마다 속도(1~3토막/반복)·긴 대시 수(1~2)
  const u = ((((x - ph * W * sp) / W) * n + rand(row, 7)) % 1 + 1) % 1, duty = 0.3 + 0.4 * (1 - d) * (0.4 + 0.6 * rand(row, 9));
  if (u < duty) return d < 0.3 ? WHITE : d < 0.55 ? C[6] : C[5];
  if (u < duty + 0.08) return C[4];
  return d < 0.4 ? C[3] : d < 0.65 ? C[2] : C[1];
}

/** 포를 가로지르는 긴 빛줄 (프레임마다 높이가 조금 흔들림, 같은 프레임이면 모든 토막에서 같은 높이 → 이어짐) */
export function flareLines(p, x0, x1, r, f, seed, C, WHITE) {
  const R = rng(seed, 21, f >> 1);
  const ys = [-r * R.range(1.15, 1.35), r * R.range(1.15, 1.4), -r * R.range(0.35, 0.55), r * R.range(1.55, 1.8)];
  for (const [i, y] of ys.entries())
    for (let x = x0; x < x1; x++) p.blend(x, y, i === 2 ? WHITE : i % 2 ? C[5] : C[6], i === 2 ? 0.35 : 0.6);
}

export { rng };

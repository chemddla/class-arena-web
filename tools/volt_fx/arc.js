// 전격 줄기 (반복): 기본 공격 채널 줄기 · 체인 라이트닝 줄. 2026-11-11 사용자 선택 "A. 활 줄기" (preview/volt-beam-samples)
// 기준점 = 줄기 시작(손 · 앞 적), 끝 = (len, 0). 게임이 줄 방향으로 돌리고 가로만 실제 길이에 맞게 늘림 (굵기는 그대로)
// 흔들림이 작은 활 모양 번개를 2프레임마다 다시 긋되 휨이 사인으로 부드럽게 오가고, 직전 모양이 옅게 남음. 0.8초 반복
// 옵션: len = 구운 길이, s = 굵기 (기본 공격 0.85, 체인 1.53 = 1.8배)
import { fit, rng, TAU } from "../../core/index.js";
import { bowed, stroke } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";

export const meta = {
  name: "Volt arc",
  desc: "A channelled electric arc: a smooth bowed bolt re-struck every other frame, its bend swinging softly, with a faint afterimage of the last shape.",
  tags: ["lightning", "electric", "plasma", "beam", "chain", "loop"],
  size: [680, 260],
  origin: [20, 150],
  duration: 0.8,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, len: 240, s: 0.85, seed: 4 },
};

const FPS = 20, N = 16;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), f = Math.floor(t * FPS + 1e-6) % N, L = o.len, s = o.s;
  const bend = (g) => -L * (0.07 + 0.05 * Math.sin(TAU * (g / N)));
  const shape = (g) => bowed(rng(o.seed, 3, 0, g >> 1), 0, 0, L, 0, bend(g), 0.11, 0.18);
  const prev = shape((f + N - 2) % N);
  stroke(p, { paths: [prev.paths[0]] }, 0.35, C, s * 0.82, { light: 0.15, a: 0.55 });
  stroke(p, shape(f), f % 4 === 0 ? 1 : 0.8, C, s, { light: 0.55, hero: f % 8 === 0 });
}

// 피격 매듭 (반복): 기본 공격 줄기·체인 라이트닝 줄이 적에 닿는 끝. 기준점 = 닿는 점.
// 닿는 점이 과부하된 매듭처럼 작은 지그재그가 엉겨 끓고, 불티가 튀어 떨어지고, 빛이 깜박임. 줄기가 이어지는 동안 계속 돌림
import { fit, rng, cycle, fly, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";

export const meta = {
  name: "Volt hit knot",
  desc: "Where a channelled arc meets its target: a boiling knot of tiny zigzags, a white flicker, sparks spitting off and falling.",
  tags: ["lightning", "electric", "plasma", "hit", "loop"],
  size: [80, 80],
  origin: [40, 40],
  duration: 0.8,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, seed: 8 },
};

const FPS = 20, N = 16;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, R = rng(o.seed, 1, f);
  const hot = f % 4 === 0, k = hot ? 1 : R.range(0.55, 0.85);
  p.glow(0, 0, hot ? 26 : 18, C[4], 0.35 * k);
  // 엉긴 지그재그 4~6줄 (짧음)
  const n = 4 + R.int(0, 2);
  for (let i = 0; i < n; i++) {
    const a = R.range(0, TAU), l = R.range(4, hot ? 15 : 11);
    crackle(p, zigzag(R, R.range(-2, 2), R.range(-2, 2), Math.cos(a) * l, Math.sin(a) * l, 0.55, 0.3), k * R.range(0.5, 1), C, 0.35);
  }
  p.circle(0, 0, hot ? 3 : 2, C[6]);
  p.px(0, 0, WHITE);
  if (hot) for (const [dx, dy] of [[-3, 0], [3, 0], [0, -3], [0, 3]]) p.px(dx, dy, C[6]);
  cycle(t, 0.8, 12, o.seed + 3, (g) => g.range(0.2, 0.4), (age, L, r) => {
    const a = r.range(-TAU * 0.45, -TAU * 0.05), sp = r.range(60, 140), q = 1 - age / L;
    const [x, y] = fly(0, 0, Math.cos(a) * sp * (r.next() < 0.5 ? -1 : 1), Math.sin(a) * sp, age, 320, 1.5);
    p.line(x, y, x, y + 1, q > 0.5 ? S[1] : S[3]);
    p.px(x, y, q > 0.5 ? WHITE : S[2]);
    p.glow(x, y, 3, S[2], 0.35 * q);
  });
}

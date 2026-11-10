// 감전 (반복, 상태): 감전된 몸 위로 전류가 기어다님. 기준점 = 발. 몸 둘레 타원 위 두 점을 잇는 휜 전류가 매 프레임 새로 튀고,
// 1.2초에 두 번 "찌릿" — 전류가 몰리고 불티가 튐. 발밑으로 땅에 흘러드는 짧은 전류.
// 몸에 빛 웅덩이를 크게 두지 않음 (적 몸 그림을 덮지 않게)
import { fit, rng, fly, TAU, WHITE } from "../../core/index.js";
import { zigzag, bowed, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V, onBody } from "./_volt.js";

export const meta = {
  name: "Volt shock",
  desc: "Shocked status on a body: bowed arcs crawl over it, re-struck every frame, twice a loop a jolt bunches them up and spits sparks, current bleeds into the floor at the feet.",
  tags: ["lightning", "electric", "status", "shock", "loop"],
  size: [104, 116],
  origin: [52, 106],
  duration: 1.2,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, h: 84, w: 22, seed: 4 },
};

const FPS = 20, N = 24, JOLTS = [2, 14];

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, R = rng(o.seed, 1, f);
  const cy = -o.h * 0.52, rx = o.w, ry = o.h * 0.46;
  const j = JOLTS.map((j0) => f - j0).find((d) => d >= 0 && d < 3);
  const jolt = j !== undefined, jk = jolt ? [1, 0.75, 0.45][j] : 0;
  // 몸을 기어가는 전류: 평소 1~2줄, 찌릿할 때 4줄
  const n = jolt ? 4 : 1 + (R.next() < 0.5 ? 1 : 0);
  for (let i = 0; i < n; i++) {
    const a0 = R.range(0, TAU), span = R.range(0.6, 1.5) * R.sign(), a1 = a0 + span;
    const [x0, y0] = onBody(a0, 0, cy, rx * R.range(0.5, 1.05), ry * R.range(0.6, 1)), [x1, y1] = onBody(a1, 0, cy, rx * R.range(0.5, 1.05), ry * R.range(0.6, 1));
    const bow = R.range(4, 9) * (R.next() < 0.5 ? -1 : 1);
    crackle(p, bowed(R, x0, y0, x1, y1, bow, 0.3, 0.35), jolt ? 0.6 + 0.4 * jk : R.range(0.28, 0.42), C, jolt ? 0.5 : 0.25);   // 평소엔 가는 줄 (흰 심 없이)
  }
  // 몸에서 바깥으로 튀는 짧은 가지 (찌릿할 때)
  if (jolt)
    for (let i = 0; i < 3; i++) {
      const a = R.range(0, TAU), [x0, y0] = onBody(a, 0, cy, rx, ry), l = R.range(8, 16) * jk;
      crackle(p, zigzag(R, x0, y0, x0 + Math.cos(a) * l, y0 + Math.sin(a) * l, 0.4, 0.3), 0.5 + 0.4 * jk, C, 0.4);
    }
  // 발밑: 땅으로 흘러드는 짧은 전류
  if (R.next() < 0.55) {
    const x = R.range(-10, 10);
    crackle(p, zigzag(R, x, -R.range(6, 14), x + R.range(-8, 8), 0, 0.4, 0.4), 0.45, C, 0.3);
    p.glow(x, -1, 8, C[4], 0.3);
  }
  if (jolt) p.glow(0, cy, o.h * 0.5, C[4], 0.22 * jk);
  // 찌릿할 때 튀는 불티: 찌릿한 순간에 한꺼번에 튀어 떨어짐
  for (const [ji, j0] of JOLTS.entries()) {
    const age0 = (((t - j0 / FPS) % meta.duration) + meta.duration) % meta.duration;
    for (let i = 0; i < 9; i++) {
      const r = rng(o.seed + 9, ji, i), a = r.range(0, TAU), [sx, sy] = onBody(a, 0, cy, rx, ry), sp = r.range(50, 110), L = r.range(0.25, 0.45), age = age0 - r.range(0, 0.05);
      if (age < 0 || age > L) continue;
      const k = 1 - age / L, [x, y] = fly(sx, sy, Math.cos(a) * sp, Math.sin(a) * sp - 30, age, 260, 2);
      if (y > 0) continue;
      p.line(x, y, x - Math.cos(a) * 2, y - Math.sin(a) * 2, k > 0.5 ? S[1] : S[3]);
      p.px(x, y, k > 0.5 ? WHITE : S[2]);
      p.glow(x, y, 3, S[2], 0.4 * k);
    }
  }
}

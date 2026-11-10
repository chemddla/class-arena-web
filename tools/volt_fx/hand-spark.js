// 손끝 스파크 (반복): 손 위 전기 불꽃·두 손 사이 구체에 덧씌워 살아 있게 함. 대기 · 기본 공격 손 · 썬더볼트/체인 구체 · 일렉트릭 필드 손
// 가운데에서 짧은 전류가 매 프레임 새로 튀고, 작은 불티가 흩어지고, 심이 숨 쉬듯 밝아졌다 어두워짐
import { fit, clamp, rng, cycle, fly, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";

export const meta = {
  name: "Volt hand spark",
  desc: "Plasma crackling round a hand: short arcs re-struck every frame, a breathing white core, flecks spat outward.",
  tags: ["lightning", "electric", "plasma", "hand", "loop"],
  size: [72, 72],
  origin: [36, 36],
  duration: 1,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, r: 4, reach: 20, seed: 3 },
};

const FPS = 20, N = 20;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, R = rng(o.seed, 1, f);
  const breath = 0.75 + 0.25 * Math.sin((f / N) * TAU * 2) + R.range(-0.08, 0.08);
  p.glow(0, 0, o.reach + 12, C[3], 0.28 * breath);
  p.glow(0, 0, o.r + 4, C[6], 0.55 * breath);
  // 짧은 전류 2~3줄: 심 둘레에서 바깥으로
  const n = 2 + (R.next() < 0.45 ? 1 : 0);
  for (let i = 0; i < n; i++) {
    const a = R.range(0, TAU), l = o.reach * R.range(0.55, 1);
    const x0 = Math.cos(a) * o.r * 0.6, y0 = Math.sin(a) * o.r * 0.6;
    crackle(p, zigzag(R, x0, y0, Math.cos(a) * l, Math.sin(a) * l, 0.42, 0.5), i ? R.range(0.3, 0.6) : R.range(0.55, 0.85), C, 0.45);
  }
  // 심: 흰 점과 하늘색 테
  const cr = o.r * (0.45 + 0.2 * breath);
  p.circle(0, 0, cr + 1, C[4]);
  p.circle(0, 0, cr, C[6]);
  p.px(0, 0, WHITE);
  // 흩어지는 불티
  cycle(t, 1, 10, o.seed + 7, (g) => g.range(0.25, 0.5), (age, L, r) => {
    const a = r.range(0, TAU), sp = r.range(30, 70), k = 1 - age / L;
    const [x, y] = fly(Math.cos(a) * o.r, Math.sin(a) * o.r, Math.cos(a) * sp, Math.sin(a) * sp, age, 40, 3);
    p.px(x, y, k > 0.6 ? S[0] : k > 0.3 ? S[2] : S[3]);
    p.glow(x, y, 3, S[2], 0.4 * k);
  });
}

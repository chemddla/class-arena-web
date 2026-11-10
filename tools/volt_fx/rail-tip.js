// 전자포 끝 (반복): 포가 끝나는 자리 (8칸 끝 또는 맵 끝). 기준점 = 포 끝 (포는 왼쪽에서 들어옴).
// 끝이 둥글게 닫히며 부풀고, 앞으로 갈라지는 전류 부채가 매 프레임 새로 튀고, 불티가 앞으로 흩어짐
import { fit, rng, cycle, fly, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";

export const meta = {
  name: "Volt rail tip",
  desc: "The far end of a plasma beam: a swelling rounded head, a fan of forking arcs splitting forward, sparks scattering ahead.",
  tags: ["lightning", "electric", "plasma", "beam", "impact", "loop"],
  size: [112, 128],
  origin: [32, 64],
  duration: 0.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, thick: 1, seed: 14 },
};

const FPS = 20, N = 12;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, R = rng(o.seed, 1, f), k = o.thick;
  const H = 13 * k, sw = 1 + 0.12 * Math.sin((f / N) * TAU * 2) + R.range(-0.05, 0.05);
  p.glow(4, 0, H * 3, C[4], 0.4);
  // 둥근 머리: 몸통과 같은 단계 (몸통 토막이 x < 0에서 끝나므로 반원만)
  const rings = [[1.4, C[1]], [1.18, C[2]], [1, C[3]], [0.88, C[4]], [0.72, C[5]], [0.5, C[6]], [0.3, WHITE]];
  for (const [rr, c] of rings) p.shade(0, -H * 2, H * 2, H * 2, (x, y, out) => (Math.hypot(x / (H * sw * 0.9), y / (H * sw)) < rr ? (out.c = c) : undefined));
  // 앞으로 갈라지는 전류 부채
  for (let i = 0; i < 4; i++) {
    const a = R.range(-0.9, 0.9), l = R.range(22, 44) * (0.7 + 0.3 * k);
    crackle(p, zigzag(R, H * 0.6, R.range(-H, H) * 0.5, Math.cos(a) * l + H * 0.6, Math.sin(a) * l, 0.4, 0.6), R.range(0.5, 1), C, 0.45);
  }
  cycle(t, 0.6, 12, o.seed + 3, (g) => g.range(0.2, 0.4), (age, L, r) => {
    const a = r.range(-1, 1), sp = r.range(100, 200), q = 1 - age / L;
    const [x, y] = fly(H * 0.8, r.range(-H, H) * 0.5, Math.cos(a) * sp, Math.sin(a) * sp, age, 150, 3);
    p.line(x, y, x - Math.cos(a) * 3, y - Math.sin(a) * 3, q > 0.5 ? S[1] : S[3]);
    p.px(x, y, q > 0.5 ? WHITE : S[2]);
    p.glow(x, y, 3, S[2], 0.4 * q);
  });
}

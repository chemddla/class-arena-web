// 전자포 끝 (반복): 포가 끝나는 자리 (8칸 끝 또는 맵 끝). 기준점 = 포 끝 (포는 왼쪽에서 들어옴).
// 이음매 없이 닫히게: 몸통(rail-body)과 같은 색 띠로 왼쪽 TAIL px 꼬리를 그려 몸통 끝을 덮음.
//   - 꼬리 왼쪽 끝은 줄마다 들쭉날쭉 (BLEND px 안에서 프레임마다 바뀜) → 몸통 무늬와 전기가 번지듯 섞여 세로 이음선이 안 생김
//   - 끝(x ≥ 0)은 모든 띠가 탄두처럼 둥글게 모이며 닫힘 (흰 심이 가장 끝까지 감)
// 끝에서 앞으로 갈라지는 전류 부채가 매 프레임 새로 튀고, 끝이 부풀었다 줄었다 하고, 불티가 앞으로 흩어짐
// 게임: 몸통 토막을 포 길이까지 그린 뒤, 포 끝 자리에 이 그림을 위에 덮음
import { fit, rng, rand, cycle, fly, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";

const TAIL = 48, BLEND = 18;
export const meta = {
  name: "Volt rail tip",
  desc: "The far end of a plasma beam: a tail matching the beam bands frays in over it, then every band closes in a rounded nose, arcs fan forward, sparks scatter.",
  tags: ["lightning", "electric", "plasma", "beam", "impact", "loop"],
  size: [160, 128],
  origin: [TAIL + 8, 64],
  duration: 0.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, thick: 1, seed: 14 },
};

const FPS = 20, N = 12;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, R = rng(o.seed, 1, f), k = o.thick;
  const H = 13 * k, sw = 1 + 0.1 * Math.sin((f / N) * TAU * 2) + R.range(-0.04, 0.04);
  const nose = H * 1.1 * sw;   // 끝이 닫히는 길이
  p.glow(nose * 0.5, 0, H * 2.6, C[4], 0.38);
  // 띠 판정: 몸통과 같은 문턱 (흰 심 → 남보라 테두리)
  const band = (d) => (d < 0.26 ? WHITE : d < 0.36 ? C[6] : d < 0.6 ? C[5] : d < 0.8 ? C[4] : d < 0.95 ? C[3] : d < 1.18 ? C[2] : d < 1.4 ? C[1] : 0);
  p.shade(-TAIL, -H * 2, nose * 1.45, H * 2, (x, y, out) => {
    // 끝으로 갈수록 두께가 둥글게 줄어듦 (x ≥ 0), 바깥 테두리 띠일수록 먼저 닫힘
    const s = x <= 0 ? 1 : Math.sqrt(Math.max(0, 1 - (x / nose) ** 2));
    const d = Math.abs(y) / (H * Math.max(s, 0.001));
    // 끝 너머 테두리: 둥근 머리 둘레를 남보라가 감쌈
    const dr = Math.hypot(Math.max(0, x) / (nose * 1.4), y / (H * 1.4));
    let c = s > 0 ? band(d) : 0;
    if (!c && x > 0 && dr < 1) c = dr < 0.86 ? C[2] : C[1];
    if (!c) return;
    if (x < -TAIL + BLEND) {   // 꼬리 왼쪽: 줄마다 다른 자리에서 시작 (2줄씩 묶어 거친 톱니)
      const yy = Math.floor(y / 2), edge = -TAIL + BLEND * (0.5 * rand(yy, f, 77) + 0.5 * rand(yy + 1, f, 78));
      if (x < edge) return;
    }
    out.c = c;
    out.a = d > 1.18 && x <= 0 ? 0.55 : 1;
  });
  // 부푼 머리의 흰 빛
  p.ellipse(nose * 0.25, 0, nose * 0.45 + 1, H * 0.3 * sw + 1, WHITE);
  p.glow(nose * 0.4, 0, H, C[6], 0.35);
  // 앞으로 갈라지는 전류 부채 (머리 끝에서)
  for (let i = 0; i < 4; i++) {
    const a = R.range(-0.9, 0.9), l = R.range(22, 44) * (0.7 + 0.3 * k), x0 = nose * 0.8, y0 = R.range(-H, H) * 0.35;
    crackle(p, zigzag(R, x0, y0, x0 + Math.cos(a) * l, y0 + Math.sin(a) * l, 0.4, 0.6), R.range(0.5, 1), C, 0.45);
  }
  cycle(t, 0.6, 12, o.seed + 3, (g) => g.range(0.2, 0.4), (age, L, r) => {
    const a = r.range(-1, 1), sp = r.range(100, 200), q = 1 - age / L;
    const [x, y] = fly(nose * 0.9, r.range(-H, H) * 0.4, Math.cos(a) * sp, Math.sin(a) * sp, age, 150, 3);
    p.line(x, y, x - Math.cos(a) * 3, y - Math.sin(a) * 3, q > 0.5 ? S[1] : S[3]);
    p.px(x, y, q > 0.5 ? WHITE : S[2]);
    p.glow(x, y, 3, S[2], 0.4 * q);
  });
}

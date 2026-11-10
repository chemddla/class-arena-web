// 전자포 끝 (반복): 에너지파의 머리. 기준점 = 포 끝 (포는 왼쪽에서 들어옴). 게임은 몸통을 포 끝까지 그린 뒤 이 그림을 위에 덮음.
// - 포보다 큰 둥근 머리(반지름 = 포 반두께 × 1.6, 앞으로 살짝 늘어남)가 끓듯 출렁이며 몸통 끝을 덮음 → 이음매 없음
// - 머리 위아래에서 굵은 에너지 혀가 뒤로 길게 흩날림 (밀고 나가는 압력)
// - 머리 앞에 압력 초승달 (얇은 밝은 호), 앞으로 갈라지는 전류, 앞으로 흩어지는 불티
import { fit, rng, cycle, fly, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";
import { halfH, orb } from "./_wave.js";

export const meta = {
  name: "Volt rail tip",
  desc: "The head of an energy wave: a boiling round head wider than the beam, thick tongues streaming back off it, a pressure crescent ahead, arcs and sparks thrown forward.",
  tags: ["lightning", "electric", "plasma", "beam", "impact", "loop"],
  size: [176, 176],
  origin: [64, 88],
  duration: 0.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, thick: 1, seed: 14 },
};

const FPS = 20, N = 12;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, ph = f / N, R = rng(o.seed, 1, f), k = o.thick;
  const H = halfH(k), rs = H * (1.6 + 0.08 * Math.sin(ph * TAU * 2)), cx = H * 0.5;
  p.glow(cx, 0, rs * 2.2, C[4], 0.5);
  // 뒤로 흩날리는 굵은 혀 (위아래 각 2개, 2프레임마다 모양이 바뀜)
  for (let j = 0; j < 4; j++) {
    const s = j % 2 ? 1 : -1, r0 = rng(o.seed, 9, j, f >> 1), len = r0.range(18, 34) * k, a0 = s * (Math.PI / 2 + r0.range(0, 0.6));   // 머리 위·아래 뒤쪽
    const sx = cx + Math.cos(a0) * rs * 0.95, sy = Math.sin(a0) * rs * 0.95;
    for (let i = 0; i <= len; i++) {
      const u = i / len, x = sx - i, y = sy + s * (u * 6 * k + Math.sin(u * 4 + j + ph * TAU) * 2), w = Math.round((1 - u) * 2.5 * k);
      for (let d = -w; d <= w; d++) p.px(x, y + d, u < 0.25 ? C[6] : u < 0.55 ? C[5] : C[4]);
    }
  }
  orb(p, cx, 0, rs, ph, C, WHITE, 1.12);
  // 압력 초승달
  const fr = rs * 1.12 + 4 + 2 * Math.sin(ph * TAU * 2);
  for (let a = -1.0; a <= 1.0; a += 0.02) p.px(cx + Math.cos(a) * fr, Math.sin(a) * rs * 1.15, Math.abs(a) < 0.5 ? C[6] : C[4]);
  for (let i = 0; i < 3; i++) {
    const a = R.range(-0.8, 0.8), l = R.range(20, 36) * (0.7 + 0.3 * k), x0 = cx + Math.cos(a) * rs, y0 = Math.sin(a) * rs;
    crackle(p, zigzag(R, x0, y0, x0 + Math.cos(a) * l, y0 + Math.sin(a) * l, 0.4, 0.6), R.range(0.6, 1), C, 0.45);
  }
  cycle(t, 0.6, 14, o.seed + 3, (g) => g.range(0.2, 0.4), (age, L, r) => {
    const a = r.range(-1.2, 1.2), sp = r.range(110, 220), q = 1 - age / L;
    const [x, y] = fly(cx + Math.cos(a) * rs, Math.sin(a) * rs, Math.cos(a) * sp, Math.sin(a) * sp, age, 150, 3);
    p.line(x, y, x - Math.cos(a) * 3, y - Math.sin(a) * 3, q > 0.5 ? S[1] : S[3]);
    p.px(x, y, q > 0.5 ? WHITE : S[2]);
    p.glow(x, y, 3, S[2], 0.4 * q);
  });
}

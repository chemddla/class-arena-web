// 전자포 총구 (반복): 내민 손바닥 앞. 기준점 = 손바닥 (포는 여기서 오른쪽으로 나감, 몸통 토막은 x = 0부터 이어 그림).
// 손바닥 앞 흰 원판이 떨리며 숨 쉬고, 뒤·위아래로 반동 전류가 튀고, 불티가 손 둘레에서 옆으로 뿜어짐
import { fit, rng, cycle, fly, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";

export const meta = {
  name: "Volt rail muzzle",
  desc: "The muzzle of a plasma beam at an open palm: a trembling white disc, recoil arcs kicking back and out, sparks venting sideways.",
  tags: ["lightning", "electric", "plasma", "beam", "muzzle", "loop"],
  size: [112, 128],
  origin: [56, 64],
  duration: 0.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, thick: 1, seed: 13 },
};

const FPS = 20, N = 12;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, R = rng(o.seed, 1, f), k = o.thick;
  const H = 13 * k, pulse = 0.85 + 0.15 * Math.sin((f / N) * TAU * 3) + R.range(-0.06, 0.06);
  p.glow(4, 0, H * 3.2, C[4], 0.45 * pulse);
  // 원판: 포보다 조금 높고, 가로로 납작
  p.ellipse(2, 0, H * 0.55 * pulse + 2, H * 1.35 * pulse, C[4]);
  p.ellipse(3, 0, H * 0.4 * pulse + 1, H * 1.1 * pulse, C[6]);
  p.ellipse(4, 0, H * 0.25 * pulse + 1, H * 0.75 * pulse, WHITE);
  // 반동 전류: 뒤쪽 위아래로
  for (let i = 0; i < 3; i++) {
    const a = Math.PI + R.range(-1.3, 1.3), l = R.range(14, 26) * (0.7 + 0.3 * k);
    crackle(p, zigzag(R, 0, R.range(-H, H) * 0.6, Math.cos(a) * l, Math.sin(a) * l, 0.4, 0.4), R.range(0.5, 0.9), C, 0.4);
  }
  // 옆으로 뿜는 불티
  cycle(t, 0.6, 12, o.seed + 3, (g) => g.range(0.18, 0.35), (age, L, r) => {
    const s = r.sign(), a = s * r.range(0.6, 1.4) - 0.2 * s, sp = r.range(90, 180), q = 1 - age / L;
    const [x, y] = fly(2, s * H * 0.8, Math.cos(a) * sp * 0.6, Math.sin(a) * sp, age, 0, 4);
    p.line(x, y, x - Math.cos(a) * 3, y - Math.sin(a) * 3, q > 0.5 ? S[1] : S[3]);
    p.px(x, y, q > 0.5 ? WHITE : S[2]);
    p.glow(x, y, 3, S[2], 0.4 * q);
  });
}

// 전자포 총구 (반복): 내민 손바닥 앞. 기준점 = 손바닥 (포는 여기서 오른쪽으로 나감, 몸통 토막은 x = 0부터 이어 그림).
// - 손바닥 앞 흰 심 + 십자 섬광 (가로로 긴 빛살이 포 방향으로), 매 프레임 살짝 떨림
// - 세로 고리 2개가 손바닥에서 생겨 포 방향으로 밀려 나가며 커지다 사라짐 (몸통의 충격 고리와 이어짐)
// - 가닥이 손바닥 한 점에서 시작해 벌어지며 몸통 가닥과 만남 (첫 24px)
// - 손 뒤·위아래로 반동 전류, 옆으로 뿜는 불티
import { fit, rng, cycle, fly, clamp, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";

export const meta = {
  name: "Volt rail muzzle",
  desc: "The muzzle of a plasma railgun at an open palm: a white core with a cross flare, rings born at the palm and pushed out along the beam, strands opening from one point, recoil arcs, sparks venting.",
  tags: ["lightning", "electric", "plasma", "beam", "muzzle", "loop"],
  size: [176, 176],
  origin: [72, 88],
  duration: 0.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, thick: 1, seed: 13 },
};

const FPS = 20, N = 12;

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, ph = f / N, R = rng(o.seed, 1, f), k = o.thick;
  const A = 11 * k, jit = R.range(0.85, 1.15);
  p.glow(4, 0, 26 * k, C[4], 0.5);   // 캔버스 안에 들어오게 (밖으로 잘리면 네모 경계가 보임)
  p.glow(2, 0, 12 * k, C[6], 0.6);
  // 밀려 나가는 고리: 손바닥(x=2)에서 생겨 x=40까지, 0.3초마다 하나
  for (let j = 0; j < 2; j++) {
    const u = (ph * 2 + j * 0.5) % 1, cx = 2 + 38 * u, ry = A * (0.8 + 1.4 * u), rx = (2 + 2 * u) * k;
    for (let a = 0, da = 0.6 / Math.max(ry, rx); a < TAU; a += da) {
      const x = cx + Math.cos(a) * rx, y = Math.sin(a) * ry, fr = Math.cos(a) > 0;
      if (u > 0.75 && ((a * 10) | 0) % 2) continue;   // 사라질 때 끊어지며
      p.px(x, y, fr ? (u < 0.4 ? WHITE : C[5]) : C[2]);
    }
  }
  // 손바닥 한 점에서 벌어지는 가닥 (몸통 가닥과 같은 식: x=0 이후 24px 동안 폭이 0 → A)
  for (const sp of [0, TAU / 3, (2 * TAU) / 3])
    for (let x = 0; x < 24; x += 0.5) {
      const g = TAU * ((2 * x) / 120 - 2 * ph) + sp, open = clamp(x / 24), y = A * open * Math.sin(g), z = Math.cos(g);
      p.px(x, y, z > 0.3 ? WHITE : z > -0.3 ? C[5] : C[3]);
    }
  // 흰 심 + 십자 섬광 (가로 빛살이 길게)
  p.ellipse(2, 0, 3.5 * k * jit, 5 * k * jit, C[6]);
  p.ellipse(3, 0, 2 * k * jit, 3 * k * jit, WHITE);
  p.line(-10 * k * jit, 0, 30 * k * jit, 0, WHITE);
  p.line(-6 * k, -1, 18 * k * jit, -1, C[6]);
  p.line(-6 * k, 1, 18 * k * jit, 1, C[6]);
  p.line(3, -16 * k * jit, 3, 16 * k * jit, C[6]);
  p.px(3, -17 * k * jit, C[4]);
  p.px(3, 17 * k * jit, C[4]);
  // 반동 전류
  for (let i = 0; i < 2; i++) {
    const a = Math.PI + R.range(-1.2, 1.2), l = R.range(12, 22) * (0.7 + 0.3 * k);
    crackle(p, zigzag(R, 0, R.range(-A, A) * 0.5, Math.cos(a) * l, Math.sin(a) * l, 0.4, 0.4), R.range(0.5, 0.85), C, 0.4);
  }
  cycle(t, 0.6, 12, o.seed + 3, (g) => g.range(0.18, 0.35), (age, L, r) => {
    const s = r.sign(), a = s * r.range(0.5, 1.3), sp = r.range(90, 180), q = 1 - age / L;
    const [x, y] = fly(4, s * A * 0.6, Math.cos(a) * sp * 0.7, Math.sin(a) * sp, age, 0, 4);
    p.line(x, y, x - Math.cos(a) * 3, y - Math.sin(a) * 3, q > 0.5 ? S[1] : S[3]);
    p.px(x, y, q > 0.5 ? WHITE : S[2]);
    p.glow(x, y, 3, S[2], 0.4 * q);
  });
}

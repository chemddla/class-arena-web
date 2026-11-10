// 전자포 총구 (반복): 내민 손바닥 앞의 에너지 구체. 기준점 = 손바닥 (포는 여기서 오른쪽으로 나감, 몸통 토막은 x = 0부터 이어 그림).
// - 포보다 조금 큰 구체(반지름 = 포 반두께 × 1.3, 가운데는 손바닥 앞)가 끓듯 출렁이며 몸통 시작을 덮음, 박동처럼 살짝 커졌다 작아짐
// - 구체 둘레로 짧은 빛살이 사방으로 튀고, 손 뒤로 반동 전류, 위아래로 뿜는 불티
import { fit, rng, cycle, fly, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";
import { halfH, orb } from "./_wave.js";

export const meta = {
  name: "Volt rail muzzle",
  desc: "The muzzle of an energy wave at an open palm: a boiling energy sphere a little wider than the beam, pulsing, short rays flicking off it, recoil arcs, sparks venting.",
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
  const H = halfH(k), rs = H * (1.3 + 0.07 * Math.sin(ph * TAU * 2)), cx = rs * 0.55;   // 구체를 손바닥 앞으로 (뒤로 넘치면 얼굴을 덮음)
  p.glow(cx, 0, rs * 2.2, C[4], 0.5);
  // 짧은 빛살 (구체 뒤)
  for (let i = 0; i < 6; i++) {
    const a = R.range(0, TAU), l = rs * R.range(1.3, 1.8);
    p.line(cx + Math.cos(a) * rs * 0.9, Math.sin(a) * rs * 0.9, cx + Math.cos(a) * l, Math.sin(a) * l, R.next() < 0.5 ? C[6] : C[5]);
  }
  orb(p, cx, 0, rs, ph, C, WHITE);
  for (let i = 0; i < 2; i++) {
    const a = Math.PI + R.range(-1.1, 1.1), l = R.range(14, 24) * (0.7 + 0.3 * k);
    crackle(p, zigzag(R, cx + Math.cos(a) * rs, Math.sin(a) * rs, cx + Math.cos(a) * (rs + l * 0.6), Math.sin(a) * (rs + l), 0.4, 0.4), R.range(0.5, 0.85), C, 0.4);
  }
  cycle(t, 0.6, 12, o.seed + 3, (g) => g.range(0.18, 0.35), (age, L, r) => {
    const s = r.sign(), a = s * r.range(0.6, 1.4), sp = r.range(90, 180), q = 1 - age / L;
    const [x, y] = fly(cx, s * rs * 0.8, Math.cos(a) * sp * 0.5, Math.sin(a) * sp, age, 0, 4);
    p.line(x, y, x - Math.cos(a) * 3, y - Math.sin(a) * 3, q > 0.5 ? S[1] : S[3]);
    p.px(x, y, q > 0.5 ? WHITE : S[2]);
    p.glow(x, y, 3, S[2], 0.4 * q);
  });
}

// 과부하 (반복, 상태): 오버로드가 끝난 뒤 10초간 스킬 사용 불가. 기준점 = 발.
// 머리·어깨에서 회색 연기가 피어오르고, 가끔 힘없는 전류가 툭 튀었다 꺼짐 (밝은 흰 심 없이 어두운 파랑)
import { fit, rng, cycle, hex } from "../../core/index.js";
import { zigzag, crackle, puff } from "../lightning/_lib.js";
import { PLASMA_V } from "./_volt.js";

export const meta = {
  name: "Volt burnout",
  desc: "Burnt out after an overload: grey smoke curling up off the head and shoulders, now and then a weak dim arc sputters and dies.",
  tags: ["lightning", "electric", "smoke", "status", "debuff", "loop"],
  size: [96, 140],
  origin: [48, 128],
  duration: 2,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, h: 88, seed: 31 },
};

const FPS = 20, N = 40, SMOKE = hex("#6c7088"), SPUTTER = [7, 8, 26];

export function draw(p, t, o) {
  const C = fit(o.palette, 8), f = Math.floor(t * FPS + 1e-6) % N;
  cycle(t, 2, 9, o.seed + 2, (g) => g.range(1.1, 1.7), (age, L, r) => {
    const x0 = r.range(-16, 16), y0 = -o.h * r.range(0.72, 0.98), u = age / L;
    const x = x0 + Math.sin(age * 2.2 + r.range(0, 6)) * 4 + age * r.range(-4, 4), y = y0 - age * r.range(16, 26);
    puff(p, x, y, r.range(3.5, 5.5), u, SMOKE);
  });
  // 힘없는 전류: 정해진 프레임에만 (이음매 없음)
  if (SPUTTER.includes(f)) {
    const R = rng(o.seed, 1, f), x0 = R.range(-14, 14), y0 = -o.h * R.range(0.4, 0.85);
    // 어두운 색만: crackle에 어두운 쪽 램프를 넘김 (흰 심 대신 하늘색)
    const dim = [C[0], C[1], C[1], C[2], C[3], C[3], C[4], C[4]];
    crackle(p, zigzag(R, x0, y0, x0 + R.range(-12, 12), y0 + R.range(-10, 10), 0.45, 0.3), 0.35, dim, 0.2);
  }
}

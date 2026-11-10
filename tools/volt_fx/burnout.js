// 과부하 (반복, 상태): 오버로드가 끝난 뒤 10초간 스킬 사용 불가. 기준점 = 발. (2026-11-10: 회색 연기 → 붉은 전기 점멸, 머리 위 아이콘 대신 이 그림으로 보임)
// 과전류로 타 버린 몸: 붉은 전기가 몸을 따라 툭툭 터졌다 꺼지기를 불규칙하게 반복
//   - 켜짐(점멸 패턴 ON): 몸 가장자리를 붉은 휜 전류 2~3줄이 감싸고, 몸 전체가 붉게 빛나며, 가끔 바깥으로 짧은 가지가 튐
//   - 꺼짐: 아주 약한 붉은 잔불만 (어두운 불씨 몇 점)
//   - 가끔 붉은 불티가 떨어지고, 머리 위로 짙은 연기 한 줄기 (타 버린 느낌)
import { fit, rng, cycle, fly, hex, TAU, WHITE } from "../../core/index.js";
import { zigzag, bowed, crackle, puff } from "../lightning/_lib.js";
import { onBody } from "./_volt.js";

/** 과부하 붉은 전기 램프 (어두움 → 밝음) */
export const RED_V = ["#2a0606", "#5c0c0c", "#9c1414", "#d42020", "#ff4a3a", "#ff9a8a", "#ffe0d8", "#ffffff"];
const RED_SPARK = ["#ffffff", "#ffd0c0", "#ff6a4a", "#b81818"];

export const meta = {
  name: "Volt burnout",
  desc: "Burnt out after an overload: red current sputters over the body in irregular bursts, the body flares red then goes dark, red sparks drop, a thin smoke curls up.",
  tags: ["lightning", "electric", "status", "debuff", "loop"],
  size: [120, 150],
  origin: [60, 132],
  duration: 1.6,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: RED_V, sparks: RED_SPARK, h: 88, w: 24, seed: 31 },
};

const FPS = 20, N = 32;
// 점멸 패턴 (1 = 켜짐, 2 = 세게): 불규칙하게 툭툭
const BLINK = [2, 1, 0, 0, 1, 0, 2, 2, 1, 0, 0, 0, 1, 1, 0, 2, 1, 0, 0, 1, 0, 0, 2, 1, 1, 0, 0, 0, 1, 0, 2, 0];
const SMOKE = hex("#3a3036");

export function drawBack(p, t, o) {
  const C = fit(o.palette, 8), f = Math.floor(t * FPS + 1e-6) % N, b = BLINK[f];
  if (b) p.glow(0, -o.h * 0.5, o.h * (b > 1 ? 0.6 : 0.45), C[3], b > 1 ? 0.4 : 0.22);
}

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, R = rng(o.seed, 1, f), b = BLINK[f];
  const cy = -o.h * 0.5, rx = o.w, ry = o.h * 0.5;
  // 머리 위 연기 한 줄기
  cycle(t, 1.6, 4, o.seed + 2, (g) => g.range(1, 1.5), (age, L, r) => {
    const u = age / L, x = r.range(-8, 8) + Math.sin(age * 2 + r.range(0, 6)) * 3, y = -o.h * 0.92 - age * r.range(18, 26);
    puff(p, x, y, r.range(3, 4.5), u, SMOKE);
  });
  if (b) {
    // 몸 가장자리를 감싸는 붉은 전류
    const n = b > 1 ? 3 : 2;
    for (let i = 0; i < n; i++) {
      const a0 = R.range(0, TAU), a1 = a0 + R.range(0.8, 1.6) * R.sign();
      const [x0, y0] = onBody(a0, 0, cy, rx * R.range(0.8, 1.1), ry * R.range(0.8, 1)), [x1, y1] = onBody(a1, 0, cy, rx * R.range(0.8, 1.1), ry * R.range(0.8, 1));
      crackle(p, bowed(R, x0, y0, x1, y1, R.range(3, 8) * R.sign(), 0.35, 0.45), b > 1 ? R.range(0.75, 1) : R.range(0.45, 0.7), C, 0.5);
    }
    // 세게 켜질 때 바깥으로 튀는 짧은 가지
    if (b > 1)
      for (let i = 0; i < 3; i++) {
        const a = R.range(0, TAU), [x0, y0] = onBody(a, 0, cy, rx, ry * 0.9), l = R.range(8, 16);
        crackle(p, zigzag(R, x0, y0, x0 + Math.cos(a) * l, y0 + Math.sin(a) * l, 0.5, 0.4), 0.85, C, 0.5);
      }
  } else {
    // 꺼짐: 몸에 남은 어두운 불씨 몇 점
    for (let i = 0; i < 3; i++) {
      const [x, y] = onBody(R.range(0, TAU), 0, cy, rx * R.range(0.3, 0.9), ry * R.range(0.3, 0.9));
      p.px(x, y, C[3]);
      p.glow(x, y, 3, C[3], 0.3);
    }
  }
  // 떨어지는 붉은 불티
  cycle(t, 1.6, 8, o.seed + 9, (g) => g.range(0.3, 0.5), (age, L, r) => {
    const a = r.range(0, TAU), [sx, sy] = onBody(a, 0, cy, rx, ry * 0.8), q = 1 - age / L;
    const [x, y] = fly(sx, sy, Math.cos(a) * r.range(20, 60), -r.range(20, 60), age, 300, 1);
    if (y > 0) return;
    p.px(x, y, q > 0.5 ? S[1] : S[2]);
    p.glow(x, y, 2.5, S[2], 0.35 * q);
  });
}

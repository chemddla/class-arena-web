// 축전 5 (반복, 몸): 다음 스킬이 강화로 나간다는 표시 — 몸에 금빛 전기가 "꽉 차서 넘치는" 느낌. 기준점 = 발.
// - 몸 뒤 금빛 빛이 심장 박동처럼 두 번 뛰고 쉼 (1.2초)
// - 몸 둘레를 감싸는 금빛 전류 2~3줄이 매 프레임 새로 튐 (휜 줄, 몸 가장자리를 따라감)
// - 머리·어깨에서 정전기 가시가 위로 곤두섬 (머리카락이 서듯), 박동 때 더 길게
// - 발밑에서 바닥으로 금빛 잔전류가 흘러나가고, 금빛 알갱이가 빠르게 솟아오름
// - 박동 순간: 몸 가장자리에서 바깥으로 짧은 가지 4줄이 터짐
// 오버로드(하늘색 큰 오라)와 구별되게 금빛·몸에 붙은 크기
import { fit, rng, cycle, TAU, WHITE } from "../../core/index.js";
import { zigzag, bowed, crackle } from "../lightning/_lib.js";
import { GOLD_V, GOLD_SPARK_V, onBody } from "./_volt.js";

export const meta = {
  name: "Volt charged",
  desc: "Brimming with charge: a gold glow beats behind the body, gold arcs hug its edge, static spikes bristle off the head and shoulders, current bleeds into the floor, sparks lift.",
  tags: ["lightning", "electric", "buff", "charge", "loop"],
  size: [124, 140],
  origin: [62, 124],
  duration: 1.2,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: GOLD_V, sparks: GOLD_SPARK_V, h: 88, w: 24, seed: 43 },
};

const FPS = 20, N = 24, BEATS = [0, 5];

export function drawBack(p, t, o) {
  const C = fit(o.palette, 8), f = Math.floor(t * FPS + 1e-6) % N;
  const b = BEATS.map((b0) => f - b0).find((d) => d >= 0 && d < 3), k = b === undefined ? 0.35 : [1, 0.7, 0.5][b];
  p.glow(0, -o.h * 0.5, o.h * 0.62, C[4], 0.32 * k);
  p.glow(0, -o.h * 0.5, o.h * 0.3, C[5], 0.2 * k);
}

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, R = rng(o.seed, 1, f);
  const cy = -o.h * 0.5, rx = o.w, ry = o.h * 0.5;
  const b = BEATS.map((b0) => f - b0).find((d) => d >= 0 && d < 3), beat = b !== undefined, bk = beat ? [1, 0.75, 0.5][b] : 0;
  // 몸 가장자리를 감싸는 전류
  const n = beat ? 3 : 2;
  for (let i = 0; i < n; i++) {
    const a0 = R.range(0, TAU), a1 = a0 + R.range(0.7, 1.4) * R.sign();
    const [x0, y0] = onBody(a0, 0, cy, rx * R.range(0.95, 1.15), ry * R.range(0.85, 1)), [x1, y1] = onBody(a1, 0, cy, rx * R.range(0.95, 1.15), ry * R.range(0.85, 1));
    crackle(p, bowed(R, x0, y0, x1, y1, R.range(3, 7) * R.sign(), 0.3, 0.4), beat ? 0.7 + 0.3 * bk : R.range(0.4, 0.7), C, 0.45);
  }
  // 정전기 가시: 머리 위·양 어깨에서 위로
  const spikes = [[R.range(-14, 0), -o.h + R.range(0, 6)], [R.range(2, 14), -o.h + R.range(2, 10)], [-rx * 0.9, -o.h * 0.68], [rx * 0.9, -o.h * 0.68]];   // 머리 위 두 가시는 자리를 흩뜨림 (대칭이면 귀처럼 보임)
  for (const [sx, sy] of spikes) {
    if (!beat && R.next() < 0.45) continue;
    const l = R.range(6, 12) + 10 * bk, a = -Math.PI / 2 + Math.sign(sx) * R.range(0.1, 0.6);
    crackle(p, zigzag(R, sx, sy, sx + Math.cos(a) * l, sy + Math.sin(a) * l, 0.5, 0.5), 0.5 + 0.5 * bk, C, 0.4);
  }
  // 박동 순간 바깥으로 터지는 가지
  if (beat)
    for (let i = 0; i < 4; i++) {
      const a = R.range(0, TAU), [x0, y0] = onBody(a, 0, cy, rx, ry * 0.9), l = R.range(10, 18) * bk;
      crackle(p, zigzag(R, x0, y0, x0 + Math.cos(a) * l, y0 + Math.sin(a) * l, 0.45, 0.4), 0.6 + 0.4 * bk, C, 0.45);
    }
  // 발밑 잔전류
  if (R.next() < 0.7) {
    const s = R.sign(), x0 = s * R.range(2, 10);
    crackle(p, zigzag(R, x0, -R.range(2, 8), x0 + s * R.range(14, 26), R.range(-2, 2), 0.4, 0.4), 0.5, C, 0.35);
    p.glow(x0, -1, 12, C[4], 0.3);
  }
  // 솟아오르는 금빛 알갱이 (빠르게, 짧게)
  cycle(t, 1.2, 14, o.seed + 5, (g) => g.range(0.3, 0.55), (age, L, r) => {
    const a = r.range(0, TAU), [sx, sy] = onBody(a, 0, cy, rx * 1.05, ry * 0.95), q = age / L;
    const x = sx + Math.sin(age * 14 + r.range(0, 6)) * 1.2, y = sy - age * r.range(50, 90);
    p.line(x, y, x, y + 2, q < 0.5 ? S[1] : S[3]);
    p.px(x, y, q < 0.4 ? WHITE : S[2]);
    p.glow(x, y, 3, S[2], 0.45 * (1 - q));
  });
}

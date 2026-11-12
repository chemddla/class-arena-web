// 심검 시작: 눈을 감고 정신을 모음 — 발밑에서 고요한 물결 고리 세 겹이 차례로 퍼지고, 몸을 따라 가는 빛줄 하나가 위로 스치며,
// 빛 알갱이 몇 개가 천천히 떠오름. 0.8초
// 좌표: 기준점(0, 0) = 발, 1 = 게임 화면 1px. 좌우 대칭
import { fit, clamp, rng } from "../../core/index.js";
import { MOON } from "./_sword.js";

export const meta = {
  name: "Mind start",
  desc: "Mindblade begins: three calm ripple rings spread one after another from the feet, a thin line of light sweeps up the body and a few motes drift slowly upward.",
  tags: ["sword", "focus", "aura", "one-shot"],
  size: [130, 100],
  origin: [65, 80],
  duration: 0.8,
  loop: false,
  fps: 20,
  bg: "dark",
  options: { palette: MOON, glow: ["#ffffff", "#e0f2fe", "#a5d8ff", "#74b9f5"], seed: 4 },
};

export function draw(p, t, o) {
  const C = fit(o.palette, 7), G = fit(o.glow, 4);
  for (let i = 0; i < 3; i++) { // 물결 고리
    const u = clamp((t - i * 0.14) / 0.55);
    if (u <= 0 || u >= 1) continue;
    const r = 8 + 48 * Math.pow(u, 0.7), a = Math.pow(1 - u, 1.2) * 0.9;
    for (let j = 0, n = Math.ceil(r * 7); j < n; j++) {
      const q = (j / n) * Math.PI * 2;
      p.blend(Math.cos(q) * r, Math.sin(q) * r * 0.28, G[Math.sin(q) < 0 ? 2 : 1], a * (Math.sin(q) < 0 ? 0.55 : 1));
    }
  }
  const s = clamp(t / 0.25), sk = 1 - clamp((t - 0.25) / 0.3); // 몸을 스치는 빛줄
  if (sk > 0) { const y = -4 - 56 * s; p.glowLine(0, -2, 0, y, 3, G[2], 0.3 * sk); for (let yy = -2; yy >= y; yy--) p.blend(0, yy, C[6], sk * 0.8 * (1 - (yy - y) / -(y + 2))); }
  p.glow(0, -26, 22, G[3], 0.25 * Math.sin(Math.PI * clamp(t / 0.8)));
  const R = rng(o.seed, 1);
  for (let i = 0; i < 7; i++) { // 떠오르는 알갱이
    const x = R.range(-26, 26), t0 = R.range(0, 0.3), u = clamp((t - t0) / 0.5);
    if (u <= 0 || u >= 1) continue;
    p.dot(x, -4 - 40 * u, C[6], Math.sin(Math.PI * u));
    p.glow(x, -4 - 40 * u, 3, G[2], 0.3 * Math.sin(Math.PI * u));
  }
}

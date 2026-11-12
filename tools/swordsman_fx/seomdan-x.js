// 섬단: X자 검기 — 발도 섬륜과 같은 빛의 날(흰 광선 테두리 · 뒤로 옅어지는 반투명 면 · 후광 · 뾰족한 양끝)로 된 초승달 둘이 엇갈려 X를 이루고 앞으로 날아감.
// 시트는 제자리(기준점 = X 가운데)에서 굽고, 게임이 칼자루 앞 → 4칸 끝까지 옮기며 그림 (+x = 날아가는 쪽). 뒤로 잔상 한 겹과 속도선이 흘러 나는 느낌을 냄
//   0.00~0.05 X가 그어짐 (첫 날 1칸, 둘째 날 한 칸 늦게) · 0.05~0.30 날아감 (게임이 옮김) · 0.30~ 끝에서 터지며 벌어지고 식음
import { fit, clamp, smooth, rng } from "../../core/index.js";
import { MOON, MOON_SPARK, FLASH, burst, lensFlare } from "./_sword.js";

export const meta = {
  name: "Seomdan X",
  desc: "Two light crescents with beam rims and translucent faces cut across each other into an X, fly forward trailing afterimages and speed lines, then burst open at the end, flare and cool.",
  tags: ["melee", "slash", "sword", "projectile", "x", "one-shot"],
  size: [330, 170],
  origin: [230, 85],
  duration: 0.52,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, W: 9, Rc: 230, span: 0.68, tilt: 0.72, seed: 4 },
};

export const FORM = 0.05, END = 0.3; // 그어짐 끝 · 날아감 끝 (게임이 이 사이에 X를 옮김)
const RIM = 2, GRAD = 4.5;

/**
 * 빛의 초승달 하나: X 가운데 (ox, oy)를 지나며 앞(+x)으로 볼록, rot만큼 기울임. 반지름 Rc, 펼친 각 span.
 * rv = 그어진 정도 (0..1, 위 끝부터), sc = 크기 배율, life = 식은 정도 (0..1), k = 밝기
 */
function crescent(p, C, ox, oy, rot, Rc, span, W, rv, sc, life, k) {
  if (rv <= 0 || k <= 0.01 || life >= 1) return;
  const R = Rc * sc, cr = Math.cos(rot), sr = Math.sin(rot), B = R * span * 0.5 + W * GRAD + 14;
  for (let y = Math.floor(oy - B); y <= oy + B; y++)
    for (let x = Math.floor(ox - B); x <= ox + B; x++) {
      const dx = x + 0.5 - ox, dy = y + 0.5 - oy, lx = dx * cr + dy * sr + R, ly = -dx * sr + dy * cr; // 원 중심 기준 (원 중심 = X 가운데 뒤 R)
      const r = Math.hypot(lx, ly), a = Math.atan2(ly, lx), v = (a + span / 2) / span;
      if (v < 0 || v > 1 || v > rv) continue;
      const head = clamp((rv - v) / 0.12) ** 0.8; // 그어지는 머리도 뾰족
      const w = W * sc * Math.pow(Math.sin(Math.PI * v), 1.3) * head * Math.pow(1 - life, 0.7);
      if (w < 0.3) continue;
      const d = R - r;
      const cov = clamp(d + 0.5);
      if (cov < 1) { // 바깥: 광선 후광 (가장자리 1px에서도 빈틈 없게 날과 나눠 칠함)
        const out = Math.max(0, -d), b = k * clamp(w / 6) * (1 - life) * (1 - cov);
        if (out < 14) p.blend(x, y, C[5], b * (0.8 * Math.exp(-out / 2.2) + 0.3 * Math.exp(-out / 7)));
        if (cov <= 0) continue;
      }
      const x1 = d / (w * GRAD);
      if (x1 >= 1) continue;
      p.blend(x, y, C[4], cov * 0.75 * k * Math.pow(1 - life, 1.2) * Math.pow(1 - x1, 1.6)); // 뒤로 옅어지는 면
      const e = d / (w * RIM);
      if (e < 1) p.blend(x, y, C[6], cov * k * (1 - life * 0.6) * Math.pow(1 - e, 1.1)); // 흰 날
      const cw = Math.max(1, w * 0.18), cd = Math.abs(d - Math.max(1.2, w * 0.3)) / cw;
      if (cd < 1) p.blend(x, y, C[6], k * (1 - life * 0.8) * (1 - cd * cd)); // 광선 심
    }
}

/** X 한 벌: 두 날을 rv0, rv1만큼 그어서 */
function cross(p, C, o, x, rv0, rv1, sc, life, k) {
  crescent(p, C, x, 0, o.tilt, o.Rc, o.span, o.W, rv0, sc, life, k);
  crescent(p, C, x, 0, -o.tilt, o.Rc, o.span, o.W, rv1, sc, life, k);
}

export function draw(p, t, o) {
  const C = fit(o.palette, 7), S = fit(o.sparks, 4);
  const rv0 = clamp(t / FLASH), rv1 = clamp((t - FLASH) / FLASH); // 첫 날 1칸, 둘째 날 1칸
  const burstT = clamp((t - END) / 0.2), sc = 1 + 0.35 * Math.pow(burstT, 0.6), life = smooth(0, 1, burstT);
  const fly = t > FORM && t < END + 0.04, pulse = 0.88 + 0.12 * Math.sin(t * 90); // 밝기는 1을 넘지 않게 (넘으면 색이 깨짐)
  // 속도선: 날개 사이 높이에서 뒤로 흘러가는 가는 빛줄 (X는 제자리, 게임이 앞으로 옮기므로 줄이 뒤로 흐르면 나는 것처럼 보임)
  if (fly) {
    const R = rng(o.seed, 7), kk = clamp((t - FORM) / 0.03) * (1 - clamp((t - END) / 0.04));
    for (let i = 0; i < 16; i++) {
      const y = R.range(-52, 52), len = R.range(30, 90), ph = R.range(0, 1), sp = R.range(500, 800);
      const x0 = -18 - ((ph * 200 + sp * t) % 200), a = kk * R.range(0.3, 0.7) * (1 - Math.abs(y) / 70);
      for (let x = x0 - len; x <= x0; x++) p.blend(x, y, C[x > x0 - 6 ? 6 : 5], a * Math.pow((x - x0 + len) / len, 1.4));
    }
    // 잔상: 뒤로 한 겹, 옅게
    for (const [dx, a] of [[-30, 0.2]]) cross(p, C, o, dx, 1, 1, 1, 0.35, a * kk);
  }
  cross(p, C, o, 0, rv0, rv1, sc, life, t < END ? pulse : 1);
  // 가운데 교차점: 그어지는 순간과 터지는 순간 섬광
  lensFlare(p, t, FLASH * 1.5, 4, 0, C, 26, 0.12);
  lensFlare(p, t, END, 6, 0, C, 44, 0.2);
  if (t > END - 0.01 && t < END + 0.12) p.glow(6, 0, 30, C[5], 0.5 * (1 - (t - END) / 0.12));
  const R2 = rng(o.seed, 13);
  for (let i = 0; i < 4; i++) burst(p, t, END + i * 0.01, 10 + R2.range(-8, 8), R2.range(-40, 40), R2.range(-0.5, 0.5), 0.7, 4, o.seed + i, S);
}

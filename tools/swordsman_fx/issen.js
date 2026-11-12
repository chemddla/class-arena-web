// 일섬: 벽력일섬처럼 번개 같은 돌진 — 검사가 빛줄기가 되어 길을 내달리고(머리 섬광 · 속도선 · 머리 둘레로 잔전기),
// 길에는 머리카락 같은 빛 자국만 남아 잔전기가 몇 번 튀다가, 잠시 뒤 길 전체가 한 번에 갈라짐 (발도·섬단과 같은 빛의 날: 흰 심 · 반투명 면 · 양끝 뾰족)
// 갈라질 때 작은 번개 가지가 길에서 튀어 나가고 식음. 전격은 옅은 하늘빛으로 조금만.
// 좌표: 기준점(0, 0) = 출발점 가슴 높이, +x = 돌진 방향. 구운 길이 L = 480 (4칸): 게임은 실제 거리에 맞춰 가로만 늘림
//   0.00~0.20 돌진 (게임 SWORD_ISSEN_TICKS 8틱) · 0.20~0.45 고요 (SWORD_ISSEN_DELAY 10틱) · 0.45 길이 갈라짐
import { fit, clamp, smooth, rng } from "../../core/index.js";
import { MOON, MOON_SPARK, FLASH, lensFlare, burst } from "./_sword.js";

export const meta = {
  name: "Issen",
  desc: "A thunder-flash dash: the swordsman becomes a streak of light racing down the path with a flaring head, speed lines and small crackles; a hairline trail lingers with stray sparks, then the whole path splits at once into a light blade with small lightning branches, and cools.",
  tags: ["melee", "slash", "sword", "dash", "lightning", "one-shot"],
  size: [540, 120],
  origin: [30, 60],
  duration: 0.72,
  loop: false,
  fps: 40,
  bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, bolt: ["#ffffff", "#e0f2fe", "#a5d8ff", "#74b9f5"], len: 480, W: 7, seed: 9 },
};

export const DASH = 0.2, CUT = 0.45;
const GRAD = 5, LIFE = 0.26;

/** 작은 번개: (x0, y0) → (x1, y1)을 꺾인 1px 선으로 (중점 흔들기 3번), 둘레 옅은 빛. 같은 seed면 같은 모양 */
function bolt(p, x0, y0, x1, y1, seed, B, a) {
  if (a <= 0.02) return;
  const R = rng(seed, 5);
  let pts = [[x0, y0], [x1, y1]];
  for (let lv = 0, amp = Math.hypot(x1 - x0, y1 - y0) * 0.28; lv < 3; lv++, amp *= 0.5) {
    const nx = [];
    for (let i = 0; i < pts.length - 1; i++) {
      const [ax, ay] = pts[i], [bx, by] = pts[i + 1], l = Math.hypot(bx - ax, by - ay) || 1, o = R.range(-amp, amp);
      nx.push(pts[i], [(ax + bx) / 2 - ((by - ay) / l) * o, (ay + by) / 2 + ((bx - ax) / l) * o]);
    }
    nx.push(pts[pts.length - 1]);
    pts = nx;
  }
  for (let i = 0; i < pts.length - 1; i++) {
    const [ax, ay] = pts[i], [bx, by] = pts[i + 1], n = Math.max(1, Math.ceil(Math.hypot(bx - ax, by - ay) * 1.5));
    for (let j = 0; j <= n; j++) {
      const x = ax + ((bx - ax) * j) / n, y = ay + ((by - ay) * j) / n, f = 1 - (i + j / n) / pts.length; // 뿌리 쪽이 진함
      p.blend(x, y, B[i < 2 ? 0 : 1], a * (0.5 + 0.5 * f));
    }
  }
  p.glowLine(x0, y0, x1, y1, 4, B[2], 0.18 * a);
}

/** 길 위의 빛의 날: 가운데 흰 심이 위아래로 옅어지는 면으로 이어짐 (발도·섬단과 같은 칠). rv = 그어진 정도, life = 식은 정도 */
function blade(p, C, L, W, rv, life) {
  if (rv <= 0 || life >= 1) return;
  const B = Math.ceil(W * GRAD) + 2;
  for (let x = -4; x <= L * rv + 4; x++) {
    const v = clamp(x / L), w = W * Math.pow(Math.sin(Math.PI * v), 0.7) * clamp((L * rv - x) / 30) ** 0.8 * Math.pow(1 - life, 0.7);
    if (w < 0.3) continue;
    for (let y = -B; y <= B; y++) {
      const d = Math.abs(y + 0.5) / 1, x1 = d / (w * GRAD);
      if (x1 >= 1) continue;
      p.blend(x, y, C[4], 0.7 * Math.pow(1 - life, 1.2) * Math.pow(1 - x1, 1.8)); // 위아래로 옅어지는 면
      const e = d / w;
      if (e < 1) p.blend(x, y, C[6], (1 - life * 0.6) * Math.pow(1 - e, 1.2)); // 흰 심
    }
  }
}

export function draw(p, t, o) {
  const C = fit(o.palette, 7), S = fit(o.sparks, 4), Bc = fit(o.bolt, 4), L = o.len;
  // 1) 돌진: 머리가 0 → L, 뒤로 빛줄기 (머리 쪽이 가장 밝음) + 속도선 + 머리 둘레 잔전기
  const hx = L * clamp(t / DASH), dk = 1 - smooth(DASH, DASH + 0.1, t);
  if (t > 0 && dk > 0) {
    p.glowLine(0, 0, hx, 0, 10, C[4], 0.22 * dk);
    p.glowLine(Math.max(0, hx - 160), 0, hx, 0, 4, C[5], 0.55 * dk);
    for (let x = 0; x <= hx; x++) p.blend(x, 0, C[6], dk * (0.25 + 0.75 * Math.pow(x / Math.max(1, hx), 2)));
    const R = rng(o.seed, 3);
    for (let i = 0; i < 12; i++) { // 속도선: 길 위아래 2~12px에서 머리를 따라 달림
      const off = (R.chance(0.5) ? -1 : 1) * R.range(2, 12), len = R.range(30, 90), lag = R.range(0, 120), a = R.range(0.3, 0.7) * dk;
      const x1 = hx - lag, x0 = Math.max(0, x1 - len);
      for (let x = x0; x <= x1; x++) p.blend(x, off, C[x > x1 - 5 ? 6 : 5], a * Math.pow((x - x0) / Math.max(1, x1 - x0), 1.3));
    }
    if (t < DASH + FLASH) { // 머리: 빛 덩이 + 짧은 가로 섬광 + 잔전기 2~3가닥 (칸마다 모양이 바뀜)
      p.glow(hx, 0, 22, C[5], 0.55);
      p.glowLine(hx - 22, 0, hx + 10, 0, 3, C[6], 0.8);
      const f = Math.floor(t * 40);
      for (let i = 0; i < 3; i++) {
        const Rb = rng(o.seed * 31 + f, i), a = Rb.range(-2.6, 2.6), l = Rb.range(10, 22);
        bolt(p, hx - Rb.range(0, 14), 0, hx - 8 + Math.cos(a) * l, Math.sin(a) * l * 0.8, o.seed + f * 7 + i, Bc, 0.8);
      }
    }
  }
  // 2) 고요: 머리카락 같은 자국 + 이따금 길 위에서 튀는 잔전기
  const trail = clamp((t - DASH) / 0.04) * (1 - smooth(CUT - 0.02, CUT + 0.02, t));
  if (trail > 0) {
    for (let x = 0; x <= L; x++) p.blend(x, 0, C[5], 0.5 * trail * (0.4 + 0.6 * x / L));
    const f = Math.floor(t * 40);
    if (f % 2 === 0) {
      const Rb = rng(o.seed * 17 + f, 1), x = Rb.range(30, L - 30), a = Rb.chance(0.5) ? -1 : 1;
      bolt(p, x, 0, x + Rb.range(-14, 14), a * Rb.range(8, 16), o.seed + f, Bc, 0.7 * trail);
    }
  }
  // 3) 갈라짐: 길 전체를 1칸 만에 빛의 날이 가름 → 잠깐 머문 뒤 가늘어지며 식음 + 번개 가지 + 섬광 + 불티
  const u = t - CUT;
  if (u >= 0) {
    const rv = clamp(u / FLASH), life = clamp((u - 0.05) / LIFE);
    blade(p, C, L, o.W, rv, life);
    lensFlare(p, t, CUT + FLASH * 0.5, L * 0.5, 0, C, 60, 0.2);
    lensFlare(p, t, CUT + FLASH, L * 0.85, 0, C, 30, 0.16);
    const Rb = rng(o.seed, 41), bk = 1 - clamp((u - 0.02) / 0.14);
    for (let i = 0; i < 7; i++) { // 번개 가지: 길에서 비스듬히 튀어 나가 2~5칸 동안 깜빡이며 사라짐
      const x = Rb.range(20, L - 20), sgn = Rb.chance(0.5) ? -1 : 1, l = Rb.range(18, 38), a = sgn * Rb.range(0.5, 1.2), t1 = Rb.range(0, 0.04);
      const flick = Math.floor((u - t1) * 40) % 2 === 0 ? 1 : 0.55;
      if (u >= t1) bolt(p, x, 0, x + Math.cos(a) * l * (Rb.chance(0.5) ? 1 : -1), Math.sin(a) * l, o.seed + i * 13, Bc, bk * flick);
    }
    const R2 = rng(o.seed, 51);
    for (let i = 0; i < 5; i++) burst(p, t, CUT + FLASH + i * 0.008, R2.range(30, L - 30), 0, R2.chance(0.5) ? -Math.PI / 2 : Math.PI / 2, 1.1, 3, o.seed + i, S);
  }
}

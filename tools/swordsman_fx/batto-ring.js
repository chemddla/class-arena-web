// 발도: 섬륜 — 칼자루가 반짝한 뒤, 3시 방향에서 시계 방향으로 3칸(0.075초) 만에 둘레 3칸을 한 바퀴 베어 냄.
// 기본 공격 참격처럼 빛의 날(흰 심 · 반투명 경계 · 후광), 머리는 바늘처럼 뾰족하고 지나간 자리는 가늘어지며 식음.
// 고리가 닫히면 시작점(3시)에서 뾰족한 머리와 꼬리가 맞물리며 섬광 + 불티, 그 뒤 1px 자국만 남고 사라짐
import { fit, clamp, smooth, sparkle, rng, TAU } from "../../core/index.js";
import { plane, onSwing } from "../melee/_lib.js";
import { MOON, MOON_SPARK, FLASH, bladePx, burst, lensFlare } from "./_sword.js";
import { SIZE, ORIGIN, CY, R0, ring, ringTrace } from "./_batto.js";

export const meta = {
  name: "Batto ring",
  desc: "Hilt glint, then from three o'clock a needle of light cuts one clockwise circle round the swordsman at three cells in two frames; the pointed head meets its tail with a flare and sparks, thins, cools and leaves a hairline trace.",
  tags: ["melee", "slash", "sword", "batto", "aoe", "one-shot"],
  size: SIZE, origin: ORIGIN, duration: 0.48, loop: false, fps: 40, bg: "dark",
  options: { palette: MOON, sparks: MOON_SPARK, W: 24, seed: 3 },
};

const T0 = 0.025, SWEEP = FLASH * 3, LIFE = 0.36; // 한 바퀴 3칸 (첫 칸 2/3 → 둘째 칸 거의 다 → 셋째 칸 닫힘) · 지나간 자리는 0.36초에 걸쳐 가늘어지며 사라짐
const head = (u) => (u >= SWEEP ? TAU : TAU * (1 - Math.pow(2, -4 * u / SWEEP)) / (1 - Math.pow(2, -4))); // 끝에서 감속, 정확히 SWEEP에 닫힘
const passedAt = (uu) => SWEEP * -Math.log2(1 - (uu / TAU) * (1 - Math.pow(2, -4))) / 4; // 머리가 uu를 지난 시각
const RIM = 2; // 흰 날(테두리) 두께 = 날 굵기의 2배
const GRAD = 6; // 안쪽 그라데이션 길이 = 날 굵기의 6배
const backK = (a) => 1 - 0.45 * clamp(-Math.sin(a) * 2.5); // 뒤쪽 반은 부드럽게 흐리게 (끊김 없이)

/** 3시 방향(a0 = 0)에서 시계 방향(dir = +1, 화면 y가 아래라 각이 늘면 시계 방향)으로 도는 빛의 날 */
function ringCut(p, s, t, W, C) {
  const u = t - s.t0;
  if (u < 0 || u > SWEEP + LIFE) return;
  const U = head(u), bx = s.R + 32, by = s.R * s.sy + 32;
  for (let y = Math.floor(s.cy - by); y <= s.cy + by; y++)
    for (let x = Math.floor(s.cx - bx); x <= s.cx + bx; x++) {
      const [r, a] = plane(s, x + 0.5, y + 0.5);
      if (r > s.R + 30 / s.sy || r < s.R - (W * GRAD * 1.25) / s.sy - 20) continue;
      let uu = a % TAU;
      if (uu < 0) uu += TAU;
      if (uu > U) continue;
      const ageP = u - passedAt(uu), life = clamp(ageP / LIFE);
      if (life >= 1) continue;
      // 굵기: 머리 끝·시작점 꼬리 모두 바늘처럼 뾰족 (1.3rad에 걸쳐 오목하게 커짐, 닫히면 3시에서 두 끝이 맞물림) · 지난 뒤 가늘어짐
      const lag = U - uu, tip = Math.pow(clamp(lag / 1.3), 1.25) * Math.pow(clamp(uu / 1.3), 1.25);
      const w = W * tip * (0.5 + 0.5 * Math.exp(-lag / 2.5)) * (1 + 0.25 * Math.sin(a)) * Math.pow(1 - life, 0.8); // 머리 뒤가 가장 두껍고 꼬리로 갈수록 가늘어지는 초승달, 앞쪽(가까운 쪽)은 조금 더 두껍게
      if (w < 0.3) continue;
      const sc = Math.hypot(Math.cos(a), Math.sin(a) * s.sy), d = (s.R - r) * sc; // 화면 px로 잰 깊이
      const k = backK(a) * (1 - smooth(0.55, 1, life));
      const cov = clamp(d + 0.5);
      if (cov < 1) { // 바깥: 테두리 빛 번짐 (가까이 진한 후광 + 멀리 넓은 은은한 빛, 뾰족한 끝은 작게) · 가장자리 1px에서도 빈틈 없게 날과 나눠 칠함
        const out = Math.max(0, -d), b = k * Math.pow(1 - life, 1.3) * clamp(w / 10) * (1 - cov);
        p.blend(x, y, C[5], b * (0.8 * Math.exp(-out / 2.5) + 0.3 * Math.exp(-out / 9)));
        if (cov <= 0) continue;
      }
      // 안쪽: 바깥 가장자리(흰 날)에서 원 중심 쪽으로 끊김 없이 옅어지는 참격 면. 두 겹을 겹쳐 부드럽게:
      //   흰 날 = 굵기 w × RIM에 걸쳐 흰빛이 1.1제곱으로 사라짐 · 빛 면 = w × GRAD에 걸쳐 은백빛이 1.6제곱으로 사라짐
      const x1 = d / (w * GRAD);
      if (x1 >= 1) continue;
      const fade = Math.pow(1 - life, 1.2) * (1 - smooth(0.3, 0.6, (s.R - r) / s.R));
      p.blend(x, y, C[4], cov * 0.75 * k * fade * Math.pow(1 - x1, 1.6));
      const e = d / (w * RIM);
      if (e < 1) p.blend(x, y, C[6], cov * k * (1 - life * 0.6) * Math.pow(1 - e, 1.1));
      // 광선 심: 테두리 안쪽에 흰 심 한 줄 (빛줄기처럼 가운데가 가장 뜨겁고 양옆으로 번짐)
      const cw = Math.max(1.2, w * 0.18), cd = Math.abs(d - Math.max(1.5, w * 0.3)) / cw;
      if (cd < 1) p.blend(x, y, C[6], k * (1 - life * 0.8) * (1 - cd * cd));
    }
}

export function draw(p, t, o) {
  const C = fit(o.palette, 7), S = fit(o.sparks, 4), A = ring({ a0: 0, dir: 1, t0: T0 }), u = t - T0;
  if (t < T0 + 0.03) sparkle(p, 16, CY, 1 + 6 * Math.sin(Math.PI * t / (T0 + 0.03)), C[6], C[4], 0.6); // 칼자루 반짝
  ringCut(p, A, t, o.W, C);
  // 빛줄기 머리: 날 끝을 따라 달리는 밝은 빛
  if (u >= 0 && u < SWEEP + FLASH) {
    const [x, y] = onSwing(A, A.R - 8, Math.min(TAU, head(u)));
    p.glow(x, y, 40, C[5], 0.6);
  }
  // 광선 줄기: 고리 바깥·안쪽 2~12px에서 날을 따라 시계 방향으로 내달리는 가늘고 긴 빛줄 (기본 공격 빛의 속도선과 같은 결)
  const Rn = rng(o.seed, 21);
  for (let i = 0; i < 30; i++) {
    const off = (Rn.chance(0.6) ? 1 : -1) * Rn.range(2, 12) / A.sy, a0 = Rn.range(0, TAU), len = Rn.range(0.3, 0.8), sp = Rn.range(5, 9), t1 = passedAt(a0 % TAU) + Rn.range(0, 0.02);
    const g = u - t1, kk = 0.85 * (1 - clamp(g / 0.2)) * Rn.range(0.5, 1);
    if (g < 0 || kk <= 0) continue;
    const s0 = a0 + sp * g * 0.25;
    for (let v = 0; v <= len; v += 0.8 / A.R) {
      const [x, y] = onSwing(A, A.R - 3 + off, s0 + v);
      p.blend(x, y, C[v / len > 0.7 ? 6 : 5], kk * Math.pow(v / len, 0.8) * backK(s0 + v));
    }
  }
  // 닫히는 순간: 3시 시작점에서 섬광 + 접선 방향(아래)으로 불티 · 고리 전체에 옅은 빛 번짐
  const [ex, ey] = onSwing(A, A.R - 2, 0), close = T0 + SWEEP;
  lensFlare(p, t, close - FLASH * 0.5, ex, ey, C, 48, 0.2);
  burst(p, t, close, ex, ey, Math.PI / 2, 0.7, 9, o.seed, S);
  const gk = 0.16 * (1 - clamp((t - close) / 0.15)) * clamp((u) / SWEEP);
  if (gk > 0.01) for (let uu = 0; uu < head(u); uu += 6 / A.R) { const [x, y] = onSwing(A, A.R - 3, uu); p.glow(x, y, 14, C[4], gk * 0.35 * backK(uu)); }
  lensFlare(p, t, close, 16, CY, C, 22, 0.14); // 칼자루 쪽 작은 섬광 (휘두른 손)
  ringTrace(p, A, C[4], 0.35 * clamp((t - close - 0.08) / 0.05) * (1 - clamp((t - close - 0.13) / 0.25)));
}

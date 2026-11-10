// 방전 (한 번): 몸에서 사방으로 터지는 전류. 기준점 = 발. 원 테두리 없음 (설계서 8-5) — 범위는 벼락이 꽂히는 자리로 보임.
// 0~0.1초 불티가 가슴으로 빨려 듦 → 0.1초 흰 섬광(가슴) → 굵은 벼락 12줄이 바닥 타원 위 자리로 꽂히고(번쩍 2~3번 다시 그음) 공중으로도 몇 줄
// → 꽂힌 자리에서 불티 분수·바닥을 기는 잔전류 → 몸 둘레 잔전류가 사그라짐. 1.1초
// 크기 옵션 R = 반지름 (게임 px). 기본 3칸 = 360, 강화 4칸 = 480 (따로 구움)
import { Particles, Lights, P, Rng, fit, flare, clamp, ease, rng, TAU, WHITE, mix, hex } from "../../core/index.js";
import { zigzag, stroke, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";

const R0 = 360, RMAX = 480, SQ = 0.62, CY = -48;   // SQ = 게임 바닥 원의 세로 비율 (판정 원과 맞춤). 캔버스는 강화 4칸(480)까지 담게 (묶을 때 빈 곳은 잘림)
export const meta = {
  name: "Volt discharge",
  desc: "Plasma bursting out of a body: sparks rush in, a white flash at the chest, a dozen heavy forked bolts stab the floor all round and tear into the air, sparks fountain where they land, arcs crawl along the floor, the charge bleeds away.",
  tags: ["lightning", "electric", "plasma", "nova", "aoe", "one-shot"],
  size: [RMAX * 2 + 40, Math.round(RMAX * SQ + 230)],
  origin: [RMAX + 20, 200],
  duration: 1.1,
  loop: false,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, R: R0, seed: 6 },
};

const BANG = 0.1, BK = [1, 0.75, 0.95, 0.55, 0.8, 0.35, 0.2];
const ASH = hex("#4a5470");

export function create(o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), R = new Rng(o.seed), RR = o.R, floor = () => 0;
  const ps = new Particles({ rng: R, ground: floor, sparks: o.sparks }), lights = new Lights();
  // 바닥 벼락 12줄: 각도를 고르게 나누고 흔듦, 거리는 반지름의 0.55~1
  const bolts = [];
  for (let i = 0; i < 12; i++) {
    const a = ((i + R.range(-0.3, 0.3)) / 12) * TAU, d = RR * R.range(0.55, 1);
    bolts.push({ ground: true, x1: Math.cos(a) * d, y1: Math.sin(a) * d * SQ, t0: BANG + R.range(0, 0.07), s: R.range(1.2, 1.6) });
  }
  // 공중 벼락 5줄: 위로 찢어짐
  for (let i = 0; i < 5; i++) {
    const a = -Math.PI / 2 + ((i - 2) / 2) * R.range(0.8, 1.1), l = R.range(70, 120);
    bolts.push({ ground: false, x1: Math.cos(a) * l * 1.6, y1: CY + Math.sin(a) * l, t0: BANG + R.range(0, 0.05), s: R.range(0.9, 1.2) });
  }
  const landed = bolts.map(() => false);
  let t = 0, banged = false;
  return {
    update(dt) {
      t += dt;
      if (t < BANG && R.chance(120 * dt)) {
        const a = R.range(0, TAU), d = R.range(28, 50), T = R.range(0.07, 0.1), v = (d * 3) / (Math.exp(3 * T) - 1);
        ps.spawn(P.STREAK, Math.cos(a) * d, CY + Math.sin(a) * d * 0.8, -Math.cos(a) * v, -Math.sin(a) * v * 0.8, T, R.chance(0.5) ? C[6] : C[5]);
      }
      if (t >= BANG && !banged) {
        banged = true;
        lights.add(0, CY, 180, C[4], 0.7, 0.4);
        lights.add(0, CY, 40, WHITE, 0.7, 0.08);
        for (let i = 0; i < 70; i++) {
          const a = R.range(0, TAU), sp = R.range(220, 520);
          ps.spawn(P.SPARK, Math.cos(a) * 8, CY + Math.sin(a) * 8, Math.cos(a) * sp, Math.sin(a) * sp * 0.7 - 60, R.range(0.25, 0.6));
        }
      }
      for (const [i, b] of bolts.entries())
        if (b.ground && !landed[i] && t >= b.t0) {
          landed[i] = true;
          lights.add(b.x1, b.y1 - 4, 70, C[4], 0.65, 0.3);
          for (let j = 0; j < 14; j++) {
            const a = -Math.PI / 2 + R.range(-1.1, 1.1), sp = R.range(90, 260);
            ps.spawn(P.SPARK, b.x1, b.y1 - 1, Math.cos(a) * sp, Math.sin(a) * sp, R.range(0.25, 0.55));
          }
          for (let j = 0; j < 2; j++) ps.spawn(P.SMOKE, b.x1 + R.range(-4, 4), b.y1 - 2, R.range(-15, 15), -R.range(10, 25), R.range(0.5, 0.8), mix(ASH, C[3], 0.35), R.range(4, 7), 0);
        }
      ps.update(dt);
      lights.update(dt);
    },
    draw(p) {
      const f = Math.floor(t * 20 + 1e-4), a = t - BANG;
      // 꽂힌 자리의 바닥 빛과 그을음 대신 플라즈마 웅덩이 (흰 점 → 하늘색 → 사라짐)
      for (const b of bolts)
        if (b.ground && t >= b.t0) {
          const k = clamp(1 - (t - b.t0) / 0.7);
          if (k <= 0) continue;
          p.ellipse(b.x1, b.y1, 9 * k + 2, (9 * k + 2) * 0.4, k > 0.6 ? C[6] : k > 0.3 ? C[4] : C[2], Math.min(1, k * 1.6));
          p.glow(b.x1, b.y1 - 2, 26, C[5], 0.5 * k);
        }
      // 섬광: 가슴에서 흰 원 + 빛줄기
      if (a >= 0 && a < 0.25) {
        const q = a / 0.25;
        flare(p, 0, CY, 90 * Math.pow(1 - q, 1.3), 1 - q, C);
        if (q < 0.4) p.circle(0, CY, 18 * (1 - q * 2) + 3, WHITE);
        p.glow(0, CY, 90, C[5], 0.4 * (1 - q));
      }
      // 벼락: 꽂히고 번쩍이며 2프레임마다 다시 그음
      for (const [i, b] of bolts.entries()) {
        const ba = Math.floor((t - b.t0) * 20 + 1e-4);
        if (t < b.t0 || ba >= BK.length) continue;
        const r = rng(o.seed, 3, i, ba >> 1);
        stroke(p, zigzag(r, 0, CY, b.x1, b.y1, 0.2, b.ground ? 0.55 : 0.8), BK[ba], C, b.s * (ba === 0 ? 1.15 : 1), { hero: ba === 0, light: 0.6 });
        if (b.ground && ba < 3) {
          p.circle(b.x1, b.y1 - 1, 4 * BK[ba] + 1, C[6]);
          p.px(b.x1, b.y1 - 1, WHITE);
        }
      }
      // 바닥을 기는 잔전류: 꽂힌 자리에서 옆으로
      if (a > 0.15 && a < 0.75) {
        const r = rng(o.seed, 9, f), k = 1 - (a - 0.15) / 0.6;
        for (let j = 0; j < 4; j++) {
          const b = bolts[r.int(0, 11)], d = r.range(14, 34) * r.sign();
          crackle(p, zigzag(r, b.x1, b.y1, b.x1 + d, b.y1 + r.range(-5, 5), 0.35, 0.4), 0.5 + 0.4 * k, C, 0.4);
        }
      }
      // 몸 둘레 잔전류
      if (a > 0.2 && a < 0.9) {
        const r = rng(o.seed, 11, f), k = 1 - (a - 0.2) / 0.7;
        for (let j = 0; j < 2; j++) {
          const x0 = r.range(-20, 20), y0 = r.range(-80, -10), g = r.range(0, TAU), l = r.range(10, 20);
          crackle(p, zigzag(r, x0, y0, x0 + Math.cos(g) * l, y0 + Math.sin(g) * l, 0.4, 0.3), 0.8 * k + 0.1, C, 0.35);
        }
      }
      ps.draw(p);
      lights.draw(p);
    },
  };
}

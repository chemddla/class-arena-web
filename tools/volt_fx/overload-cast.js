// 오버로드 시전 (한 번, 히든 스킬): 시전 0.5초 동안 하늘에서 낙뢰가 몰아치며 몸에 축전 → 발동 순간 거대한 금빛 낙뢰 기둥. 기준점 = 발. 1.5초
//   0.00~0.50 하늘색 낙뢰 4번이 점점 굵게·빠르게 캐릭터에게 꽂힘 (0, 0.15, 0.28, 0.40초) — 꽂힐 때마다 몸이 하얗게 빛나고 바닥에 전류가 튐
//             몸 둘레로 사방에서 빛줄기가 빨려 들고(축전), 머리 위 하늘에 전기 매듭이 커짐
//   0.50      발동: 하얀 섬광(넓은 빛) → 굵기 2.6배 금빛 낙뢰 기둥이 여러 번 다시 그어지며 꽂힘, 주변 공중으로 금빛 가지 8줄
//             바닥: 금빛 균열 전류가 좌우 멀리 달려 나감 + 바닥 빛 / 불티 분수가 크게 솟음
//   0.50~1.50 기둥 잔광이 위로 걷히고, 금빛 불티가 비처럼 내리고, 몸 둘레 잔전류가 사그라짐
// 하늘색(PLASMA_V)으로 모으고 금빛(GOLD_V)으로 터짐 — 오버로드 동안 모든 스킬이 강화(금빛)인 것과 이어짐
import { Particles, Lights, P, Rng, fit, flare, clamp, rng, mix, TAU, WHITE } from "../../core/index.js";
import { zigzag, stroke, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V, GOLD_V, GOLD_SPARK_V } from "./_volt.js";

const TOP = -440, CY = -46, BANG = 0.5;
export const meta = {
  name: "Volt overload cast",
  desc: "Overload cast: cyan bolts hammer the caster from the sky, then a colossal gold pillar slams down, gold cracks race across the floor, sparks rain.",
  tags: ["lightning", "electric", "plasma", "hidden", "ultimate", "one-shot"],
  size: [520, 560],
  origin: [260, 500],
  duration: 1.5,
  loop: false,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, gold: GOLD_V, goldSparks: GOLD_SPARK_V, seed: 51 },
};

const STRIKES = [[0.0, 1.0], [0.15, 1.25], [0.28, 1.5], [0.4, 1.8]];   // [시각, 굵기]
const BK = [1, 0.75, 1, 0.6, 0.85, 0.45];
const PK = [1, 1, 0.85, 1, 0.75, 0.9, 0.6, 0.7, 0.45, 0.3];   // 금빛 기둥: 더 오래 여러 번 다시 그음

// 바닥 빛 웅덩이 (그라데이션): 가운데 흰빛 → 밝은 색 → 짙은 색으로 부드럽게 번지고, 가장자리로 갈수록 진짜 반투명으로 사라짐 (점무늬·단색 띠 없음)
//   cols = [가운데, 중간, 바깥] 색, k = 세기 0~1
function pool(p, rx, ry, cols, k) {
  if (k <= 0.01 || rx < 1) return;
  for (let y = Math.floor(-ry); y <= Math.ceil(ry); y++)
    for (let x = Math.floor(-rx); x <= Math.ceil(rx); x++) {
      const d = Math.hypot((x + 0.5) / rx, (y + 0.5) / ry);
      if (d >= 1) continue;
      const c = d < 0.35 ? mix(cols[0], cols[1], d / 0.35) : mix(cols[1], cols[2], (d - 0.35) / 0.65);
      p.blend(x, y, c, k * Math.min(0.95, 1.5 * Math.pow(1 - d, 0.8)));   // 가운데는 거의 불투명, 가장자리로 부드럽게 0
    }
  p.glow(0, -2, rx * 0.9, cols[1], 0.5 * k);
  p.glow(0, -1, rx * 0.35, cols[0], 0.5 * k);
}

export function create(o) {
  const C = fit(o.palette, 8), G = fit(o.gold, 8), R = new Rng(o.seed), floor = () => 0;
  const ps = new Particles({ rng: R, ground: floor, sparks: o.sparks }), gp = new Particles({ rng: R, ground: floor, sparks: o.goldSparks }), lights = new Lights();
  const hit = STRIKES.map(() => false);
  let t = 0, banged = false;
  return {
    update(dt) {
      t += dt;
      // 축전: 사방에서 몸으로 빨려 드는 빛줄기 (점점 많이)
      if (t < BANG && R.chance((60 + 200 * t) * dt)) {
        const a = R.range(0, TAU), d = R.range(50, 110), T = R.range(0.1, 0.16);
        ps.spawn(P.STREAK, Math.cos(a) * d, CY + Math.sin(a) * d * 0.8, (-Math.cos(a) * d) / T, (-Math.sin(a) * d * 0.8) / T, T, R.chance(0.5) ? C[6] : C[5]);
      }
      for (const [i, [t0, w]] of STRIKES.entries())
        if (!hit[i] && t >= t0) {
          hit[i] = true;
          lights.add(0, -30, 90 * w, C[4], 0.55, 0.22);
          for (let j = 0; j < 14 * w; j++) {
            const a = -Math.PI / 2 + R.range(-1.3, 1.3), sp = R.range(80, 220) * w;
            ps.spawn(P.SPARK, R.range(-4, 4), -2, Math.cos(a) * sp, Math.sin(a) * sp, R.range(0.2, 0.45));
          }
        }
      if (t >= BANG && !banged) {
        banged = true;
        lights.add(0, -60, 260, G[4], 0.85, 0.6);
        lights.add(0, CY, 60, WHITE, 0.9, 0.12);
        for (let j = 0; j < 90; j++) {
          const a = -Math.PI / 2 + R.range(-1.45, 1.45), sp = R.range(180, 520);
          gp.spawn(P.SPARK, R.range(-8, 8), -4, Math.cos(a) * sp, Math.sin(a) * sp, R.range(0.35, 0.9));
        }
      }
      // 발동 뒤: 금빛 불티 비
      if (t > BANG + 0.1 && t < 1.25 && R.chance(70 * dt)) gp.spawn(P.SPARK, R.range(-200, 200), TOP * R.range(0.35, 0.7), R.range(-20, 20), R.range(60, 160), R.range(0.5, 0.9));
      ps.update(dt);
      gp.update(dt);
      lights.update(dt);
    },
    draw(p) {
      const f = Math.floor(t * 20 + 1e-4);
      // 하늘 매듭: 머리 위 높은 곳에서 커짐
      if (t < BANG + 0.05) {
        const q = clamp(t / BANG), r = rng(o.seed, 2, f);
        p.glow(0, TOP + 30, 30 + 40 * q, C[4], 0.3 + 0.4 * q);
        for (let i = 0; i < 2 + Math.floor(q * 4); i++) {
          const a = r.range(0, TAU), l = r.range(14, 30) + 30 * q;
          crackle(p, zigzag(r, 0, TOP + 30, Math.cos(a) * l * 1.6, TOP + 30 + Math.sin(a) * l * 0.6, 0.5, 0.5), 0.6 + 0.4 * q, C, 0.45);
        }
        p.circle(0, TOP + 30, 3 + 6 * q, C[6]);
        // 몸이 점점 밝아짐 + 몸 둘레 전류
        p.glow(0, CY, 30 + 40 * q, C[4], 0.25 + 0.35 * q);
        for (let i = 0; i < 1 + Math.floor(q * 3); i++) {
          const a0 = r.range(0, TAU), a1 = a0 + r.range(0.8, 1.6);
          crackle(p, zigzag(r, Math.cos(a0) * 24, CY + Math.sin(a0) * 46, Math.cos(a1) * 24, CY + Math.sin(a1) * 46, 0.4, 0.4), 0.5 + 0.5 * q, C, 0.4);
        }
      }
      // 하늘색 낙뢰 4번
      for (const [i, [t0, w]] of STRIKES.entries()) {
        const ba = Math.floor((t - t0) * 20 + 1e-4);
        if (t < t0 || ba >= BK.length) continue;
        const r = rng(o.seed, 3, i, ba >> 1);
        stroke(p, zigzag(r, r.range(-30, 30), TOP, 0, -6, 0.12, 0.6), BK[ba], C, w * (ba === 0 ? 1.2 : 1), { hero: ba === 0, light: 0.6 });
        if (ba < 2) {
          pool(p, 26 * w, 7 * w, [WHITE, C[5], C[3]], ba === 0 ? 1 : 0.7);
          crackle(p, zigzag(r, -6, 0, -r.range(30, 60) * w, r.range(-4, 4), 0.35, 0.5), 0.9, C, 0.4);
          crackle(p, zigzag(r, 6, 0, r.range(30, 60) * w, r.range(-4, 4), 0.35, 0.5), 0.9, C, 0.4);
        }
      }
      // 발동: 섬광 + 금빛 기둥 + 공중 가지 + 바닥 균열
      const a = t - BANG;
      if (a >= 0 && a < 0.3) {
        const q = a / 0.3;
        flare(p, 0, CY, 200 * Math.pow(1 - q, 1.2), 1 - q, G);
        if (q < 0.3) p.circle(0, CY, 40 * (1 - q * 3) + 4, WHITE);
        p.glow(0, -120, 200, G[5], 0.45 * (1 - q));
      }
      const pa = Math.floor(a * 20 + 1e-4);
      if (a >= 0 && pa < PK.length) {
        const r = rng(o.seed, 5, pa >> 1);
        stroke(p, zigzag(r, r.range(-10, 10), TOP - 20, 0, -4, 0.08, 0.45), PK[pa], G, 2.6 * (pa === 0 ? 1.15 : 1), { hero: pa < 2, light: 0.75, core: pa < 4 ? 2.4 : undefined });
        stroke(p, zigzag(r, r.range(-60, -30), TOP, r.range(-14, -6), -4, 0.14, 0.4), PK[pa] * 0.7, G, 1.1, { light: 0.4 });
        stroke(p, zigzag(r, r.range(30, 60), TOP, r.range(6, 14), -4, 0.14, 0.4), PK[pa] * 0.7, G, 1.1, { light: 0.4 });
        if (pa < 6)
          for (let i = 0; i < 8; i++) {
            const g = (i / 8) * TAU + r.range(-0.2, 0.2), l = r.range(50, 90);
            stroke(p, zigzag(r, Math.cos(g) * 16, CY + Math.sin(g) * 30, Math.cos(g) * l * 1.3, CY + Math.sin(g) * l, 0.3, 0.5), PK[pa] * 0.85, G, 0.9);
          }
      }
      if (a > 0 && a < 0.8) {
        const q = a / 0.8, r = rng(o.seed, 7, f), reach = 30 + 220 * Math.sqrt(q), k = 1 - q;
        // 바닥 빛 웅덩이: 그라데이션으로 퍼지며 흐려짐 (가운데 흰빛 → 금빛 → 주황, 가장자리는 투명하게)
        pool(p, reach * 0.62, reach * 0.15, [k > 0.5 ? WHITE : G[6], G[5], G[2]], Math.min(1, k * 1.3));
        for (const s of [-1, 1])
          for (let j = 0; j < 2; j++) {
            const y0 = r.range(-6, 6);
            crackle(p, zigzag(r, s * reach * 0.3, y0, s * reach, y0 + r.range(-14, 14), 0.3, 0.6), 0.6 + 0.4 * k, G, 0.45);
            p.glow(s * reach, -2, 26, G[4], 0.45 * k);
          }
      }
      // 기둥 잔광이 위로 걷힘
      if (a > 0.45 && a < 1) {
        const u = (a - 0.45) / 0.55;
        p.glowLine(0, TOP, 0, -4 - u * 420, 14, G[4], 0.35 * (1 - u));
      }
      // 발동 뒤 몸 둘레 금빛 잔전류
      if (a > 0.2 && a < 0.95) {
        const r = rng(o.seed, 9, f), k = 1 - (a - 0.2) / 0.75;
        for (let i = 0; i < 2; i++) {
          const x0 = r.range(-22, 22), y0 = r.range(-86, -10), g = r.range(0, TAU), l = r.range(12, 24);
          crackle(p, zigzag(r, x0, y0, x0 + Math.cos(g) * l, y0 + Math.sin(g) * l, 0.4, 0.4), 0.6 * k + 0.3, G, 0.4);
        }
      }
      ps.draw(p);
      gp.draw(p);
      lights.draw(p);
    },
  };
}

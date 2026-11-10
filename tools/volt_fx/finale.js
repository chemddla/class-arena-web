// 시크릿 레어 히든 피날레 (한 번): 오버로드가 끝날 때 — 사방에 퍼진 전기를 모아 공중으로 도약해 터뜨림. 기준점 = 발 (땅). 백열 은빛(GOLD_V) + 흰빛. 2초
//   게임 시간과 맞춤 (index.html VOLT_FIN_*): 0~1.2초 모음(웅크림) · 1.2~1.8초 도약(공중으로 JUMP px) · 1.8초 터짐(최고점) · 1.8~2.8초 방출 자세로 공중에 떠 있음 · 2.8~3.7초 체공 자세로 천천히 내려옴 (2026-11-10) (2026-11-10: 모음·도약 시간과 높이를 늘림)
//   0.00~0.60 모음: 바닥 사방 멀리서 전류가 땅을 기어 발밑으로 몰려 듦(점점 많이·밝게), 빛 알갱이가 빨려 듦, 몸이 점점 하얗게 달아오름, 발밑 빛 웅덩이가 커짐
//   0.60~0.90 도약: 땅에서 몸까지 흰 빛기둥이 따라 올라감, 발밑에서 위로 튀는 전류, 몸 둘레 고리 빛
//   0.90      터짐 (최고점 = 몸 가운데): 하얀 섬광 원이 확 커졌다 사라짐, 사방 긴 빛살(플레어), 굵은 번개 14줄이 최고점에서 바닥 타원 위 사방으로 내리꽂힘(여러 번 다시 그음),
//             공중으로도 가지 6줄, 큰 불티 폭발, 바닥 꽂힌 자리마다 빛 웅덩이·불티
//   0.90~2.00 잔광: 최고점의 플라즈마 구체가 줄어들며 사라짐, 불티 비, 바닥을 기는 잔전류, 빛이 걷힘
// 10칸(1200px) 끝까지의 번개는 게임 코드가 그림 (적마다 굵은 줄기 · 바닥 먼 자리) — 이 그림은 캐릭터 둘레 약 3칸
import { Particles, Lights, P, Rng, fit, flare, clamp, rng, mix, ease, TAU, WHITE } from "../../core/index.js";
import { zigzag, stroke, crackle } from "../lightning/_lib.js";
import { GOLD_V, GOLD_SPARK_V, PLASMA_V } from "./_volt.js";

const GATHER = 1.2, BANG = 1.8, JUMP = 130, HOVER = BANG + 1, FALL = HOVER + 0.9, CY = -46, SQ = 0.62, RG = 300;
export const meta = {
  name: "Volt finale",
  desc: "Secret Rare finale: current crawls in from all over the floor, the caster leaps and bursts like a white sun, heavy bolts slam the ground all round, sparks rain.",
  tags: ["lightning", "electric", "plasma", "hidden", "ultimate", "one-shot"],
  size: [780, 720],
  origin: [390, 520],
  duration: 4.2,
  loop: false,
  fps: 20,
  bg: "dark",
  options: { palette: GOLD_V, sparks: GOLD_SPARK_V, cool: PLASMA_V, seed: 61 },
};

// 바닥 빛 웅덩이 (그라데이션, 진짜 반투명)
function pool(p, cx, cy, rx, ry, cols, k) {
  if (k <= 0.01 || rx < 1) return;
  for (let y = Math.floor(-ry); y <= Math.ceil(ry); y++)
    for (let x = Math.floor(-rx); x <= Math.ceil(rx); x++) {
      const d = Math.hypot((x + 0.5) / rx, (y + 0.5) / ry);
      if (d >= 1) continue;
      const c = d < 0.35 ? mix(cols[0], cols[1], d / 0.35) : mix(cols[1], cols[2], (d - 0.35) / 0.65);
      p.blend(cx + x, cy + y, c, k * Math.min(0.95, 1.5 * Math.pow(1 - d, 0.8)));
    }
  p.glow(cx, cy - 2, rx * 0.9, cols[1], 0.4 * k);
}
// 몸이 떠 있는 높이 (게임 jumpY와 같은 곡선)
function lift(t) {
  if (t < GATHER) return 0;
  if (t < BANG) return JUMP * Math.sin(((t - GATHER) / (BANG - GATHER)) * Math.PI / 2);
  if (t < HOVER) return JUMP * (1 + 0.04 * Math.sin((t - BANG) * 7));   // 체공: 터뜨린 뒤 1초 동안 떠서 살짝 오르내림
  if (t < FALL) return JUMP * (1 + Math.cos(((t - HOVER) / (FALL - HOVER)) * Math.PI)) / 2;   // 체공 자세로 0.9초에 걸쳐 천천히 내려옴 (게임 voltFinLift와 같음)
  return 0;
}

const BK = [1, 1, 0.8, 1, 0.65, 0.85, 0.5, 0.65, 0.35, 0.2];

export function create(o) {
  const C0 = fit(o.palette, 8), K = fit(o.cool, 8), R = new Rng(o.seed), floor = () => 0;
  // 번개·섬광 램프: 바깥은 짙은 푸른 플라즈마(대비), 안은 백열 은빛·흰 심 — 은빛만 쓰면 터질 때 하얗게 뭉개짐
  const C = [K[0], K[1], K[2], K[3], C0[4], C0[5], C0[6], WHITE];
  const ps = new Particles({ rng: R, ground: floor, sparks: o.sparks }), lights = new Lights();
  // 바닥 꽂히는 번개 14줄: 각도 고르게, 거리 0.45~1 × RG
  const bolts = Array.from({ length: 14 }, (_, i) => {
    const a = ((i + R.range(-0.3, 0.3)) / 14) * TAU, d = RG * R.range(0.45, 1);
    return { x1: Math.cos(a) * d, y1: Math.sin(a) * d * SQ, t0: BANG + R.range(0, 0.08), s: R.range(0.95, 1.35) };
  });
  const sky = Array.from({ length: 6 }, (_, i) => { const a = -Math.PI / 2 + ((i - 2.5) / 2.5) * 1.1; return { a, l: R.range(140, 220) }; });
  const landed = bolts.map(() => false);
  let t = 0, banged = false;
  return {
    update(dt) {
      t += dt;
      const apex = CY - lift(t);
      // 모음: 빛 알갱이가 사방에서 몸으로
      if (t < BANG && R.chance((80 + 260 * clamp(t / GATHER)) * dt)) {
        const a = R.range(0, TAU), d = R.range(90, 220), T = R.range(0.12, 0.2);
        const sx = Math.cos(a) * d, sy = apex + Math.sin(a) * d * 0.7;
        ps.spawn(P.STREAK, sx, sy, -Math.cos(a) * d / T, -Math.sin(a) * d * 0.7 / T, T, R.chance(0.5) ? C[6] : C[5]);
      }
      if (t >= BANG && !banged) {
        banged = true;
        lights.add(0, apex, 360, C[3], 0.75, 0.6);
        lights.add(0, apex, 90, WHITE, 1, 0.15);
        for (let i = 0; i < 160; i++) {
          const a = R.range(0, TAU), sp = R.range(200, 620);
          ps.spawn(P.SPARK, Math.cos(a) * 10, apex + Math.sin(a) * 10, Math.cos(a) * sp, Math.sin(a) * sp * 0.75 - 80, R.range(0.35, 1));
        }
      }
      for (const [i, b] of bolts.entries())
        if (!landed[i] && t >= b.t0) {
          landed[i] = true;
          lights.add(b.x1, b.y1 - 6, 90, C[4], 0.7, 0.3);
          for (let j = 0; j < 12; j++) {
            const a = -Math.PI / 2 + R.range(-1.2, 1.2), sp = R.range(90, 260);
            ps.spawn(P.SPARK, b.x1, b.y1 - 1, Math.cos(a) * sp, Math.sin(a) * sp, R.range(0.25, 0.6));
          }
        }
      if (t > BANG + 0.15 && t < FALL && R.chance(70 * dt)) ps.spawn(P.SPARK, R.range(-320, 320), -R.range(200, 380), R.range(-20, 20), R.range(60, 170), R.range(0.5, 1));
      ps.update(dt);
      lights.update(dt);
    },
    draw(p) {
      const f = Math.floor(t * 20 + 1e-4), h = lift(t), apex = CY - h, q = clamp(t / GATHER);
      // ---- 모음 ----
      if (t < BANG) {
        const r = rng(o.seed, 2, f), k = t < GATHER ? q : 1;
        pool(p, 0, 0, 40 + 50 * k, (40 + 50 * k) * 0.25, [WHITE, C[5], C[2]], 0.5 + 0.5 * k);
        // 땅을 기어 들어오는 전류: 멀리서 발밑까지 (가까울수록 밝음)
        const n = 3 + Math.floor(k * 6);
        for (let i = 0; i < n; i++) {
          const a = r.range(0, TAU), d0 = r.range(160, RG + 40), d1 = d0 * r.range(0.25, 0.6) * (1 - 0.6 * k);
          crackle(p, zigzag(r, Math.cos(a) * d0, Math.sin(a) * d0 * SQ, Math.cos(a) * d1, Math.sin(a) * d1 * SQ, 0.35, 0.5), 0.45 + 0.5 * k, C, 0.45);
        }
        // 몸이 달아오름 + 몸 둘레 전류
        p.glow(0, apex, 30 + 50 * k, C[5], 0.3 + 0.4 * k);
        for (let i = 0; i < 1 + Math.floor(k * 3); i++) {
          const a0 = r.range(0, TAU), a1 = a0 + r.range(0.8, 1.6);
          crackle(p, zigzag(r, Math.cos(a0) * 26, apex + Math.sin(a0) * 40, Math.cos(a1) * 26, apex + Math.sin(a1) * 40, 0.4, 0.4), 0.55 + 0.45 * k, C, 0.45);
        }
      }
      // ---- 도약: 땅에서 몸까지 흰 빛기둥, 몸 둘레 고리 빛 ----
      if (t >= GATHER && t < BANG + 0.1) {
        const u = clamp((t - GATHER) / (BANG - GATHER)), r = rng(o.seed, 4, f);
        p.glowLine(0, 0, 0, apex + 20, 16, C[5], 0.55);
        for (let y = apex + 30; y <= 0; y++) { p.px(0, y, WHITE); p.px(-1, y, C[6]); p.px(1, y, C[6]); }
        pool(p, 0, 0, 70, 18, [WHITE, C[5], C[2]], 1 - u * 0.5);
        for (let i = 0; i < 3; i++) {
          const x0 = r.range(-30, 30);
          crackle(p, zigzag(r, x0, -r.range(0, 6), x0 * 0.3, apex + r.range(20, 50), 0.35, 0.4), 0.8, C, 0.45);
        }
        for (let a = 0; a < TAU; a += 0.03) {
          const x = Math.cos(a) * (30 + 40 * u), y = apex + 30 + Math.sin(a) * (8 + 10 * u);
          if (Math.sin(a) > 0 || ((a * 20) | 0) % 2) p.px(x, y, Math.sin(a) > 0 ? C[6] : C[4]);
        }
      }
      // ---- 터짐 ----
      const a = t - BANG;
      if (a >= 0 && a < 0.4) {
        const q2 = a / 0.4;
        flare(p, 0, apex, 300 * Math.pow(1 - q2, 1.2), 1 - q2, C);
        if (q2 < 0.45) { p.circle(0, apex, 70 * ease.outCubic(q2 / 0.45) * (1 - q2) + 10, C[6]); p.circle(0, apex, 50 * ease.outCubic(q2 / 0.45) * (1 - q2) + 6, WHITE); }
        p.glow(0, apex, 260, C[3], 0.45 * (1 - q2));
        // 가로·세로 긴 빛살
        const L = 340 * (1 - q2);
        p.line(-L, apex, L, apex, WHITE);
        p.line(0, apex - L * 0.7, 0, apex + L * 0.7, C[6]);
      }
      for (const [i, b] of bolts.entries()) {
        const ba = Math.floor((t - b.t0) * 20 + 1e-4);
        if (t < b.t0 || ba >= BK.length) continue;
        const r = rng(o.seed, 5, i, ba >> 1);
        stroke(p, zigzag(r, 0, apex, b.x1, b.y1, 0.18, 0.55), BK[ba], C, b.s * (ba < 2 ? 1.15 : 1), { hero: ba === 0 && i % 3 === 0, light: 0.4 });
        pool(p, b.x1, b.y1, 30 * (1 - ba / BK.length) + 8, (30 * (1 - ba / BK.length) + 8) * 0.3, [WHITE, C[5], C[3]], 1 - ba / BK.length);
      }
      const sa = Math.floor(a * 20 + 1e-4);
      if (a >= 0 && sa < 7) {
        const r = rng(o.seed, 6, sa >> 1);
        for (const s of sky) stroke(p, zigzag(r, 0, apex, Math.cos(s.a) * s.l * 1.3, apex + Math.sin(s.a) * s.l, 0.25, 0.6), BK[sa] * 0.85, C, 0.85, { light: 0.35 });
      }
      // 잔광: 최고점의 플라즈마 구체가 줄어들며 사라짐
      if (a > 0.1 && t < FALL - 0.05) {
        // 체공 동안 몸에 남은 전기 구체: 터진 뒤 0.3초 동안 줄어들고, 떠 있는 동안 작게 지지직, 내려오며 사라짐
        const k = a < 0.4 ? 1 - (a - 0.1) / 0.3 * 0.6 : t < HOVER ? 0.4 + 0.08 * Math.sin(t * 30) : 0.4 * (1 - (t - HOVER) / 0.25), rr = 34 * k + 4, r = rng(o.seed, 8, f);
        p.glow(0, apex, rr * 3, C[5], 0.5 * k);
        p.circle(0, apex, rr, C[4]);
        p.circle(0, apex, rr * 0.75, C[6]);
        p.circle(0, apex, rr * 0.45, WHITE);
        for (let i = 0; i < 3; i++) {
          const g = r.range(0, TAU), l = rr + r.range(10, 30);
          crackle(p, zigzag(r, Math.cos(g) * rr, apex + Math.sin(g) * rr, Math.cos(g) * l, apex + Math.sin(g) * l, 0.4, 0.4), 0.5 + 0.5 * k, C, 0.45);
        }
      }
      // 바닥을 기는 잔전류
      if (a > 0.2 && a < 1) {
        const r = rng(o.seed, 9, f), k = 1 - (a - 0.2) / 0.8;
        for (let j = 0; j < 4; j++) {
          const b = bolts[r.int(0, bolts.length - 1)], d = r.range(20, 50) * r.sign();
          crackle(p, zigzag(r, b.x1, b.y1, b.x1 + d, b.y1 + r.range(-8, 8), 0.35, 0.4), 0.5 + 0.4 * k, C, 0.4);
        }
      }
      ps.draw(p);
      lights.draw(p);
    },
  };
}

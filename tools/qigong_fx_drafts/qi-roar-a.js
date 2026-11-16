// 기공후 시안 (기공막·실타래 기구슬 바탕) — 반짝임·별빛·불꽃 가루 없음
//   모으기 0.4초(게임 시전 hu1): 둘레의 기운 실이 가슴으로 감겨 들고, 발밑 기운이 몸 쪽으로 빨려 듦
//   터뜨리기(hu2, 두 팔 펴기): 가슴 구슬이 터지며 몸 둘레로 기운이 한꺼번에 밀려 나감 (게임: 바닥 납작 타원 0.55, 반지름 2칸)
//   style: 'a' 기압 물결 (그라데이션 기운 막이 물결로 퍼지고 땅을 따라 밀리는 기운 줄)
//          'b' 고리 폭풍 (기공막 B처럼 굵은 실 고리 셋이 높이를 달리해 휘몰아치며 퍼짐)
//          'c' 기운 숨결 (선 없이 안개 같은 기운이 한 번에 부풀어 밀려 나감)
import { Particles, P, Rng, fit, ease, clamp, noise2, TAU } from "../../core/index.js";
import { QI_GOLD, pressureRing } from "./_qi.js";
import { makeLoops, jOrb, jThreads, jGatherIn, jBody } from "./_jcore.js";

const CAST = 0.4, WAVE = 0.55, END = CAST + 0.95;
const CY = -50, GY = -6;          // 가슴 높이 · 물결 중심(발 조금 위)
const RX = 300, SY = 0.55;        // 게임 범위(2칸)를 미리보기 캐릭터 키 비율로 조금 줄임, 납작한 정도는 게임 그대로
export const meta = { size: [700, 380], origin: [350, 190], loop: false, fps: 30, bg: "dark", name: "기공후 A 기압 물결", desc: "몸 둘레로 기운 물결이 밀려 나감", tags: ["qigong"], duration: END + 0.05, options: { palette: QI_GOLD, seed: 5, style: "a" } };
export const TIMES = { CAST, WAVE, END };

const L10 = makeLoops(10), L12 = makeLoops(12);
const sstep = (a, b, x) => { const u = clamp((x - a) / (b - a)); return u * u * (3 - 2 * u); };

// 그라데이션 기운 물결: 앞머리가 가장 짙고 뒤로 길게 옅어지는 띠 (딱딱한 1칸 선 없음). r: 앞머리 반지름, w: 띠 너비(비율)
function wave(p, C, r, w, k, t, wob = 0.05) {
  if (k <= 0.01 || r < 2) return;
  const ry = r * SY, pad = 1.08;
  for (let py = Math.floor(GY - ry * pad); py <= GY + ry * pad; py++) for (let px = Math.floor(-r * pad); px <= r * pad; px++) {
    const dx = px + 0.5, dy = py + 0.5 - GY, a = Math.atan2(dy / SY, dx);
    const v = Math.hypot(dx, dy / SY) / r / (1 + wob * noise2(Math.cos(a) * 2.4 + t * 3, Math.sin(a) * 2.4 - t * 2.5));
    if (v > 1.07 || v < 1 - w) continue;
    const band = v <= 1 ? sstep(1 - w, 1, v) : 1 - sstep(1, 1.07, v);
    const breathe = 0.75 + 0.25 * noise2(Math.cos(a) * 3.5 - t * 2, Math.sin(a) * 3.5 + t * 1.5);
    const back = 0.5 + 0.5 * sstep(-0.4, 0.4, dy / ry);   // 몸 뒤쪽(위) 반은 옅게 → 땅에 누운 물결로 보임
    p.blend(px + 0.5, py + 0.5, band > 0.7 ? C[6] : C[5], band * band * breathe * k * back * 0.9);
  }
}

// 땅을 따라 밀려 나가는 기운 줄 (머리 밝고 꼬리 옅게)
const STREAKS = [];
for (let i = 0; i < 22; i++) STREAKS.push([(i / 22) * TAU + ((i * 0.37) % 1 - 0.5) * 0.22, 0.18 + ((i * 0.53) % 1) * 0.16, 0.8 + ((i * 0.71) % 1) * 0.3]);
function streaks(p, C, r, k) {
  STREAKS.forEach(([a0, len, sp]) => {
    const head = r * Math.min(1, sp), tail = Math.max(14, head - RX * len);
    const ca = Math.cos(a0), sa = Math.sin(a0) * SY, back = sa < 0 ? 0.5 : 1;
    for (let d = tail; d <= head; d += 0.6) {
      const f = (d - tail) / Math.max(1, head - tail);
      p.blend(ca * d, GY + sa * d, f > 0.75 ? C[6] : f > 0.35 ? C[5] : C[4], k * back * (0.25 + 0.75 * f));
    }
  });
}

// 굵은 실 고리 (기공막 B와 같은 그림): 납작한 타원 고리, 앞 반은 밝고 굵게, 뒤 반은 옅게, 군데군데 끊김
function threadRing(p, C, y, r, k, t, sp, gap) {
  const ry = r * SY;
  for (let a = 0; a < TAU; a += 0.7 / Math.max(r, 6)) {
    const u = a + t * sp, w = 1 + 0.05 * Math.sin(u * 3 + t * 6);
    if (gap && ((u * 2.3) % 1 + 1) % 1 < gap) continue;
    const x = Math.cos(u) * r * w, yy = y + Math.sin(u) * ry * w;
    if (Math.sin(u) > 0) { p.blend(x, yy, C[6], k); p.blend(x, yy + 1, C[5], k * 0.8); }
    else p.blend(x, yy, C[4], k * 0.35);
  }
}

export function create(o) {
  const C = fit(o.palette, 7), st = o.style || "a", R = new Rng(o.seed);
  const ps = new Particles({ rng: R, ground: () => 0, haze: C[4] });
  let t = 0, boom = false;
  return {
    update(dt) {
      t += dt;
      // 모으기: 발밑 둘레의 기운 안개가 몸 쪽으로 빨려 듦
      if (t < CAST - 0.06) for (let i = 0; i < 3; i++) {
        const a = R.range(0, TAU), d = R.range(60, 110), sp = d / 0.32;
        ps.spawn(P.VAPOUR, Math.cos(a) * d, GY + Math.sin(a) * d * SY, -Math.cos(a) * sp, -Math.sin(a) * sp * SY - 30, 0.3, R.pick([C[3], C[4], C[5]]), R.range(1.6, 2.8));
      }
      if (!boom && t >= CAST) {
        boom = true;
        // 위로 솟는 기운 (지금 게임의 솟는 줄기를 안개로)
        for (let i = 0; i < 16; i++) ps.spawn(P.VAPOUR, R.range(-18, 18), R.range(-60, -10), R.range(-25, 25), R.range(-110, -50), R.range(0.35, 0.6), R.pick([C[4], C[5]]), R.range(2, 3.4));
        if (st === "c") for (let i = 0; i < 45; i++) {   // 숨결: 사방으로 밀려 나가는 안개
          const a = R.range(0, TAU), sp = R.range(0.6, 1) * RX / 0.5;
          ps.spawn(P.VAPOUR, Math.cos(a) * 12, GY + Math.sin(a) * 12 * SY, Math.cos(a) * sp, Math.sin(a) * sp * SY, R.range(0.42, 0.62), R.pick([C[4], C[5], C[5], C[6]]), R.range(2.2, 3.6));
        }
      }
      ps.update(dt);
    },
    draw(p) {
      const b = t - CAST;
      // 모으기: 큰 고리로 떠 있던 실이 가슴으로 감겨 들며 구슬이 차오름
      if (b < 0) {
        const e = clamp(t / CAST);
        jGatherIn(p, C, L12, 0, CY, 9, t, ease.inOutSine(e));
        jOrb(p, C, L10, 0, CY, 1.5 + 6.5 * ease.outBack(e), t, clamp(e * 2));
      }
      // 발밑 고리가 조여 듦 (모으기 끝 무렵)
      if (b < 0 && t > CAST * 0.4) { const e = (t - CAST * 0.4) / (CAST * 0.6); wave(p, C, 70 * (1 - 0.75 * ease.inQuad(e)), 0.35, 0.35 * e, t); }
      ps.draw(p);
      if (b < 0) return;
      const e = clamp(b / WAVE), r = RX * (0.06 + 0.94 * ease.outQuart(e)), k = Math.pow(1 - e, 1.15);
      // 가슴 구슬이 터지며 부풀었다 사라짐
      jBody(p, C, 0, CY, 8, b / 0.28);
      if (b < 0.3) { const f = b / 0.3; jThreads(p, C, L10, 0, CY, 8, t * 0.4 + 2, Math.pow(1 - f, 1.4), 1, 1, 1 + 5 * ease.outCubic(f)); }
      pressureRing(p, C, 0, CY, b / 0.3, 8, 48, 1, 0.6);   // 몸 높이에서 한 번 세로로 밀어 냄
      if (st === "a") {
        wave(p, C, r, 0.3, k, t);
        wave(p, C, RX * (0.04 + 0.7 * ease.outQuart(clamp((b - 0.08) / WAVE))), 0.25, 0.45 * Math.pow(1 - clamp((b - 0.08) / WAVE), 1.3), t + 3);
        if (e < 0.7) streaks(p, C, r * 1.02, Math.pow(1 - e / 0.7, 1.2));
        // 끊김 없는 실 고리 둘이 물결 앞머리를 따라 퍼짐 (사용자: A 고리는 이어지게)
        threadRing(p, C, GY, r * 0.97, k * 0.8, t, 1.4, 0);
        threadRing(p, C, GY - 2, r * 0.86, k * 0.45, t + 1.7, -1.1, 0);
      }
      if (st === "b") {
        wave(p, C, r, 0.3, k * 0.55, t);   // 옅은 바탕 물결
        // 고리 셋: 높이를 달리해 조금씩 늦게, 서로 반대로 돌며 퍼짐
        [[GY, 0, 1.6, 1], [CY * 0.45, 0.05, -2.1, 0.86], [CY * 0.95, 0.1, 1.3, 0.7]].forEach(([y, d, sp, sc]) => {
          const f = clamp((b - d) / WAVE); if (f <= 0 || f >= 1) return;
          const rr = RX * sc * (0.05 + 0.95 * ease.outQuart(f)), kk = Math.pow(1 - f, 1.1);
          threadRing(p, C, y, rr, kk, t, sp, 0.1 + 0.3 * f);
          threadRing(p, C, y + 2, rr * 0.93, kk * 0.5, t + 1.7, -sp * 0.8, 0.25 + 0.3 * f);   // 뒤따르는 가는 실
        });
        if (e < 0.6) streaks(p, C, r, 0.6 * Math.pow(1 - e / 0.6, 1.3));
      }
      if (st === "c") {
        // 선 없이 부드러운 기운 덩이: 안쪽까지 채운 넓은 그라데이션
        wave(p, C, r, 0.95, k * 0.75, t, 0.09);
      }
    },
  };
}

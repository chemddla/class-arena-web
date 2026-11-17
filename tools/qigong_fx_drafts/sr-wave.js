// 기공사 SR 기공파 · 청기파 (2판, 2026-11-17 사용자: "테두리 부분까지 파동이 겹쳐서 멋이 안 나")
//   모으기: 두 손 사이로 기 알갱이가 소용돌이쳐 들며 구슬이 커지고, 둘레 기운이 점점 조여 들며 짙어짐 (고리 없음)
//   쏘기: 층이 나뉜 기 포 — 하얀 심(맥박은 심 안에서만 부풀며 앞으로 밀려감) · 몸통은 심에서 바깥으로 매끈하게 옅어지고
//         그 안을 길쭉한 기류 덩어리가 앞으로 내달림 · 가장자리는 잔잔한 기운 번짐뿐 (테두리 선·파동·불꽃 혀 없음)
//         · 가장자리에서 기 알갱이가 뒤로 흩어져 떠오름 · 머리는 둥글게 부푼 빛 · 바닥에 비친 기운
//   SR 둘째 자세(쏘는 시간 절반): 손 앞에서 기운이 한 번 크게 부풀며 포가 굵어짐 → 손 쪽부터 가늘어지며 끝
import { Rng, fit, clamp, noise2 } from "../../core/index.js";
import { QI_SKY, soft, CORE, MINT, HAND, Drops, orb, eo, ei, ss, lerp, outBack } from "./_sr.js";

const CHARGE = 1.2, SR2 = 2.5, FADE = 3.9, END = 4.2;
const [X0, CY] = [HAND.wave[0] + 2, HAND.wave[1]], XMAX = 454;
export const HITS = [210, 310, 410];
export const meta = { size: [500, 150], origin: [40, 132], loop: false, fps: 30, bg: "dark", name: "기공사 SR 청기파", desc: "심에서 바깥으로 번지는 맑은 기 포", tags: ["qigong"], duration: END + 0.5, options: { palette: QI_SKY, seed: 7 } };
export const TIMES = { CHARGE, SR2, FADE, END };

function beam(p, C, xs, x1, cy, hw, t, swell) {
  if (x1 - xs < 1 || hw < 0.5) return;
  p.glowLine(xs, cy, x1, cy, hw * 3, C[3], 0.3);
  p.glowLine(xs, cy, x1, cy, hw * 1.2, C[5], 0.18);
  p.glow(x1, cy, hw * 3.2, C[4], 0.35);   // 머리 빛
  soft(p, xs, cy - hw * 1.3, x1 + hw * 1.3, cy + hw * 1.3, (px, py, out) => {
    const cap = clamp((x1 + hw * 0.4 - px) / (hw * 1.6)), prof = Math.sqrt(1 - (1 - cap) ** 2);   // 둥근 머리
    const neck = 0.8 + 0.2 * ss(0, hw * 3, px - X0);
    const h = hw * prof * neck * (1 + 0.06 * noise2(px * 0.03 - t * 2.5, 0.5));               // 잔잔하게 숨 쉬는 굵기
    if (h < 0.3) return;
    const vn = (py - cy) / h, av = Math.abs(vn);
    if (av > 1) return;
    // 맥박: 심 안에서만 부풀며 앞으로 밀려감 · 심 굵기도 잘게 떨림
    const pp = ((px - X0 - t * 300) % 52 + 52) % 52, pulse = Math.exp(-(((pp - 10) / 9) ** 2));
    const coreW = (0.18 + 0.1 * pulse + 0.06 * swell) * (1 + 0.35 * noise2(px * 0.09 - t * 22, 7.3));
    // 감아 도는 기운 두 가닥: 포를 나선으로 감음 (앞으로 돈 쪽은 밝고 뒤로 돈 쪽은 옅게 → 입체감, 선 아닌 번진 띠)
    let helix = 0;
    for (let j = 0; j < 2; j++) {
      const ph = (px - X0) * 0.075 - t * 16 + j * Math.PI, yo = Math.sin(ph) * 0.62, depth = 0.35 + 0.65 * (0.5 + 0.5 * Math.cos(ph));
      helix += Math.exp(-(((vn - yo) / 0.2) ** 2)) * depth;
    }
    // 기류 두 겹: 빠르고 잘게 내달리는 결 + 느리고 크게 굽이치는 소용돌이 (밝은 곳·짙은 곳이 함께 있어 단조롭지 않게)
    const fast = Math.max(0, noise2((px - t * 640) * 0.045, vn * 3.2 + 11)) ** 2;
    const slow = noise2((px - t * 170) * 0.014, vn * 1.3 + t * 0.6);
    const b = Math.pow(1 - av, 1.6) * 0.75 + helix * 0.32 + fast * 0.35 + slow * 0.18 * (1 - av);
    out.a = Math.pow(1 - av, 0.45) * 0.97;                                                   // 바깥으로 갈수록 투명 (선 없음)
    if (av < coreW) { out.k = 0.25 + 0.2 * pulse; return av < coreW * 0.55 ? CORE : C[6]; }   // 하얀 심
    if (helix > 0.75 && av > 0.3) { out.k = 0.08; return b > 0.75 ? C[6] : MINT; }          // 가닥이 가장 앞에 올 때는 박하빛
    return b > 0.74 ? C[6] : b > 0.5 ? C[5] : b > 0.27 ? C[4] : b > 0.1 ? C[3] : C[2];
  });
  for (let k = 0; k < 14; k++) {   // 포 속을 내달리는 기 알갱이 (빠르기·높이 제각각, 뒤로 번짐)
    const sp = 380 + (k * 97) % 300, px = X0 + ((t * sp + k * 61) % 560); if (px < xs + 4 || px > x1 - 2) continue;
    const yy = cy + Math.sin(k * 2.7 + t * 3) * hw * 0.55;
    p.blend(px, yy, C[6], 0.85); p.blend(px - 1, yy, C[5], 0.5); p.blend(px - 2, yy, C[4], 0.25);
  }
  if (xs <= X0 + 1) orb(p, C, X0, cy, hw * 1.3 * (1 + 0.25 * swell), t);
}

// 둘레 기운이 조여 들며 짙어짐 (고리 대신 채운 번짐: 바깥 반지름이 줄어듦)
function gatherHaze(p, C, x, y, R, k) {
  soft(p, x - R, y - R, x + R, y + R, (px, py, out) => {
    const d = Math.hypot(px - x, py - y) / R; if (d >= 1) return;
    out.a = k * 0.28 * Math.pow(1 - d, 1.6); return d < 0.4 ? C[5] : C[4];
  });
}

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed), D = new Drops(R);
  const T = { x: HAND.wave[0] - 8, y: CY + 6, r: 1 };   // 모으기는 두 손 사이 (기공파 모으기 칸)
  let t = 0, tick = 0, sr2 = false, xs = X0, x1 = X0, hw = 0, swell = 0;
  const puff = (x, y, n, sp, life, a) => { for (let i = 0; i < n; i++) { const an = R.range(0, Math.PI * 2); D.mist(x, y, Math.cos(an) * sp, Math.sin(an) * sp * 0.7 - 10, 3, R.range(8, 14), life, a); } };
  return {
    update(dt) {
      t += dt;
      if (t < CHARGE) { T.r = 1 + 8 * eo(t / CHARGE); D.gather(T, 170, 30, 75, dt, 1.3); }
      if (t >= CHARGE && t < END) {
        const f = clamp((t - FADE) / (END - FADE));
        x1 = X0 + (XMAX - X0) * Math.pow(clamp((t - CHARGE) / 0.22), 0.7);
        xs = lerp(X0, x1, ei(f));
        swell = t >= SR2 ? Math.exp(-(t - SR2) * 5) : 0;
        hw = (10 + (t >= SR2 ? 5 * outBack((t - SR2) / 0.25) : 0)) * (1 - f * 0.7);
        if (t >= SR2 && !sr2) { sr2 = true; puff(X0, CY, 12, 70, 0.6, 0.22); }
        if ((tick -= dt) <= 0 && f < 0.5) {   // 맞는 자리: 고리 없이 기운이 번지고 알갱이가 흩어져 떠오름
          tick = 0.25;
          for (const x of HITS) if (x1 > x) {
            puff(x, CY, 3, 40, 0.45, 0.16);
            for (let i = 0; i < 6; i++) D.drop(x + R.range(-3, 3), CY + R.range(-1, 1) * hw, R.range(-30, 60), R.range(-80, 40), { life: 0.9, r: R.chance(0.25) ? 2 : 1 });
          }
        }
        if (f < 1) for (let i = 0; i < 2; i++) if (R.chance(0.7)) {   // 가장자리에서 뒤로 흩어져 떠오르는 기 알갱이
          const x = lerp(xs, x1, R.next()), s = R.chance(0.5) ? -1 : 1;
          D.drop(x, CY + s * hw * R.range(0.6, 0.95), R.range(-70, -20), s * R.range(10, 40), { life: 0.6 });
        }
        if (R.chance(0.25) && f < 0.8) D.mist(lerp(xs, x1, R.next()), CY + R.range(-1, 1) * hw, -20, -8, 4, 10, 0.6, 0.1);
      }
      D.update(dt, t);
    },
    draw(p) {
      if (t < CHARGE) {
        const e = t / CHARGE, j = t > CHARGE - 0.2 ? R.range(-0.7, 0.7) : 0;
        gatherHaze(p, C, T.x, T.y, lerp(52, 16, ss(0, 1, e)), ss(0, 0.3, e));
        orb(p, C, T.x + j, T.y, T.r, t);
      } else if (t < END) {
        soft(p, xs, -5, x1 + 6, 4, (px, py, out) => { out.a = 0.22 * (1 - Math.abs(py + 1) / 5) * (0.7 + 0.3 * noise2(px * 0.05 - t * 4, 1)); return C[4]; });   // 바닥에 비친 기운
        beam(p, C, xs, x1, CY, hw, t, swell);
      }
      D.draw(p, C);
    },
  };
}

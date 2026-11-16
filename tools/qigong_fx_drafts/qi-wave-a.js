// 기공파 시안 (에네르기파 같은 굵은 기 포 + 전격술사 전자포의 결 무늬·테두리 + 기공사 실타래 구슬·실 고리) — 별빛·흰 섬광 없음
//   모으기 1.5초(게임 시전, pa1 자세: 두 손을 뒤 허리로 당김): 큰 고리로 떠 있던 기운 실이 두 손 사이로 감겨 들어 구슬이 커지고,
//     압력 고리가 구슬 쪽으로 조여 듦(점점 빨라짐), 둘레 기운 안개가 빨려 듦. 끝 무렵 구슬이 떨림
//   쏘기(pa2 자세: 두 손을 앞으로): 손 앞 큰 실타래 구슬에서 둥근 머리가 앞으로 내달리고 뒤로 굵은 포가 이어짐
//     포: 가장자리 크림빛 테두리 · 속은 가로 결 무늬가 앞으로 흐름 · 기운 실 두 가닥이 포를 감아 돌며 나아감 · 실 고리가 포를 따라 흘러감
//   끝: 포가 손 쪽부터 가늘어지며 사라지고 구슬은 실로 풀림
//   style: 'a' 금빛 기포 (속이 가장 밝은 에네르기파) · 'b' 결 기포 (전자포처럼 속은 짙고 테두리가 밝음, 결 무늬가 또렷)
import { Particles, P, Rng, fit, ease, clamp, noise2, TAU } from "../../core/index.js";
import { QI_GOLD, pressureRing } from "./_qi.js";
import { makeLoops, jOrb, jThreads, jGatherIn, jBody } from "./_jcore.js";

const CAST = 1.5, FIRE = 1.9, FADE = 0.35, END = CAST + FIRE + FADE;
const CX = -16, CY = -40;          // 모으기 구슬 (뒤 허리, 두 손 사이)
const HX = 60, HY = -48;           // 손 앞 구슬 가운데 (구슬 왼쪽 끝이 두 손에 닿게)
const LEN = 620, HW = 40;          // 미리보기 포 길이(게임은 8칸이라 화면 밖까지) · 반두께
const RUSH = 0.16;                 // 머리가 끝까지 내달리는 시간
export const meta = { size: [760, 300], origin: [90, 230], loop: false, fps: 30, bg: "dark", name: "기공파 A 금빛 기포", desc: "에네르기파처럼 굵은 금빛 기 포", tags: ["qigong"], duration: END + 0.05, options: { palette: QI_GOLD, seed: 7, style: "a" } };
export const TIMES = { CAST, FIRE, FADE, END };

const L16 = makeLoops(16), L10 = makeLoops(10);
const hash = (a, b) => { let h = (a * 374761393 + b * 668265263) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967295; };

// 포 반지름: 손에서 넓어지고(구슬 크기 → HW), 머리 쪽은 둥글게
function radius(x, head, t, thin) {
  if (x > head) return 0;
  const grow = clamp(x / 60), w = 1;   // 테두리 출렁임 없음 (사용자: 물결치는 움직임 제거)
  const tip = head - x < HW ? Math.sqrt(1 - ((HW - (head - x)) / HW) ** 2) : 1;   // 둥근 머리
  // 손 앞 구슬(반지름 HW·1.15)에서 시작해 부드럽게 좁아져 포 굵기로 (잘록한 목 없이 이어짐)
  return HW * (1 + 0.15 * Math.exp(-((x / 42) ** 2))) * w * tip * thin;
}

// 포 한 점의 색 (d = |y|/r): 'a' 속이 가장 밝음 · 'b' 속은 짙고 테두리가 밝음. 결 무늬는 3px 줄마다 속도가 다른 대시
function beamColor(x, y, d, t, C, st) {
  const row = Math.floor(y / 3), sp = 260 + hash(row, 3) * 380, n = 1 + Math.floor(hash(row, 5) * 2);
  const u = ((((x - t * sp) / 120) * n + hash(row, 7)) % 1 + 1) % 1, dash = u < 0.25 + 0.4 * (1 - d) * (0.4 + 0.6 * hash(row, 9));
  if (d >= 0.93) return C[4];
  if (d >= 0.8) return C[6];        // 테두리
  if (d >= 0.76) return C[5];
  if (st === "a") return d < 0.22 ? C[6] : dash ? (d < 0.5 ? C[6] : d < 0.68 ? C[5] : C[4]) : d < 0.45 ? C[5] : d < 0.66 ? C[4] : C[3];
  return dash ? (d < 0.35 ? C[6] : C[5]) : d < 0.4 ? C[3] : d < 0.65 ? C[2] : C[1];
}

export function create(o) {
  const C = fit(o.palette, 7), st = o.style || "a", R = new Rng(o.seed);
  const ps = new Particles({ rng: R, ground: () => 0, haze: C[4] });
  let t = 0;
  return {
    update(dt) {
      t += dt;
      if (t < CAST - 0.1) {   // 둘레 기운 안개가 구슬로 빨려 듦 (끝으로 갈수록 많이·빨리)
        const n = dt * (30 + 70 * t / CAST);
        for (let i = 0; i < n; i++) if (R.chance(Math.min(1, n - i))) {
          const a = R.range(0, TAU), d = R.range(40, 80), life = R.range(0.3, 0.45), sp = d / life;
          ps.spawn(P.VAPOUR, CX + Math.cos(a) * d, CY + Math.sin(a) * d * 0.8, -Math.cos(a) * sp, -Math.sin(a) * sp * 0.8, life, R.pick([C[4], C[5]]), R.range(1.6, 2.8));
        }
      }
      const f = t - CAST;
      if (f >= 0 && f < FIRE) for (let i = 0; i < 3; i++) {   // 포 둘레로 밀려 나는 기운 안개
        const x = R.range(HX + 20, HX + Math.min(LEN, LEN * f / RUSH)), s = R.chance(0.5) ? 1 : -1;
        ps.spawn(P.VAPOUR, x, HY + s * HW * R.range(0.9, 1.1), R.range(60, 160), s * R.range(15, 40), R.range(0.25, 0.4), R.pick([C[4], C[5]]), R.range(1.8, 3));
      }
      ps.update(dt);
    },
    draw(p) {
      const f = t - CAST;
      // ----- 모으기 -----
      if (f < 0) {
        const e = clamp(t / CAST), ee = ease.inOutSine(e), shake = e > 0.8 ? (Math.sin(t * 90) * 0.8) : 0;
        jGatherIn(p, C, L16, CX + shake, CY, 12, t, ee);
        jOrb(p, C, L16, CX + shake, CY, 2 + 11 * ease.outCubic(e), t, clamp(e * 3));
        // 조여 드는 압력 고리 (거꾸로 도는 시간, 점점 잦아짐)
        const per = 0.42 - 0.24 * e, q = (t % per) / per;
        pressureRing(p, C, CX, CY, 1 - q, 14, 50, 0.85, 0.5 * clamp(e * 2));
        ps.draw(p);
        return;
      }
      ps.draw(p);
      const fe = clamp((f - FIRE) / FADE), head = HX + Math.min(LEN, LEN * ease.outQuad(clamp(f / RUSH)));
      // 끝: 손 쪽부터 가늘어짐 (꼬리 x가 앞으로 밀려 나감)
      const tail = HX + LEN * ease.inQuad(fe) * 0.8, thin = 1 - ease.inQuad(fe);
      // ----- 손 앞 큰 구슬 -----
      const orbK = 1 - ease.inQuad(fe), pulse = 1 + 0.03 * Math.sin(t * 30);
      if (fe < 1) {
        // 포와 같은 색 띠로 칠한 구슬 (가운데 밝고 테두리 크림빛) → 포가 구슬에서 그대로 흘러나오는 것처럼 보임
        const RO = HW * 1.15 * pulse * (0.4 + 0.6 * ease.outBack(clamp(f / 0.12))) * thin;
        p.glow(HX, HY, RO * 1.9, C[4], 0.3 * orbK);
        p.shade(HX - RO - 1, HY - RO - 1, HX + RO + 1, HY + RO + 1, (px, py, out) => {
          const d = Math.hypot(px - HX, py - HY) / RO;
          return d >= 1 ? 0 : beamColor(px, py - HY, d, t, C, st);
        });
        for (let g = 0; g < TAU; g += 0.6 / RO) for (let d = 1; d < 1.3; d += 1 / RO) p.blend(HX + Math.cos(g) * RO * d, HY + Math.sin(g) * RO * d, C[4], 0.5 * (1.3 - d) / 0.3);
        jThreads(p, C, L16, HX, HY, RO * 0.75, t, 0.7 * orbK);   // 구슬 속에서 엉켜 도는 실
      }
      // ----- 포 몸통 -----
      if (fe < 1) {
        p.glowLine(Math.max(HX + HW, tail), HY, head, HY, HW * 1.9 * thin, C[3], 0.28 * (1 - fe));
        p.shade(HX, HY - HW * 1.35, head + 1, HY + HW * 1.35, (px, py, out) => {
          if (px < tail) return 0;
          const r = radius(px - HX, head - HX, t, thin), dy = py - HY;
          if (r <= 0) return 0;
          const d = Math.abs(dy) / r;
          if (d >= 1) return 0;
          return beamColor(px, dy, d, t, C, st);   // 반투명으로 칠하면 바둑판 무늬가 생겨서 몸통은 꽉 칠하고, 끝은 가늘어지기로만 사라짐
        });
        for (let x = Math.max(HX, Math.ceil(tail)); x < head; x++) {   // 테두리 밖 반투명 기운 (blend라 무늬 없음)
          const r = radius(x - HX, head - HX, t, thin);
          for (let d = 1; d < 1.3 && r > 0; d += 1 / r) for (const sg of [-1, 1]) p.blend(x, HY + sg * r * d, C[4], 0.5 * (1.3 - d) / 0.3);
        }
        // 기운 실 두 가닥이 포를 감아 돌며 나아감 (앞쪽 반만 진하게, 아래 그늘 줄로 포 위에서도 보이게)
        for (let i = 0; i < 2; i++) for (let x = Math.max(HX + 6, tail); x < head - 4; x += 0.6) {
          const r = radius(x - HX, head - HX, t, thin), ph = (x - HX) * TAU / 95 - t * 14 + i * Math.PI, z = Math.cos(ph), y = HY + Math.sin(ph) * r * 0.92;
          if (z > 0) { p.blend(x, y + 1, C[2], 0.75 * (1 - fe)); p.blend(x, y, C[3], 0.9 * (1 - fe)); p.blend(x, y - 1, C[6], 0.8 * (1 - fe)); }
          else p.blend(x, y, C[3], 0.3 * (1 - fe));
        }
        // 포를 따라 흘러가는 실 고리 (0.18초마다 손에서 나와 앞으로)
        for (let j = 0; j < 12; j++) {
          const age = ((f / 0.18) % 1 + j) * 0.18, x = HX + 20 + age * 520;
          if (age > f || x > head - 10 || x < tail) continue;
          const r = radius(x - HX, head - HX, t, thin) * 1.12, a = Math.max(0, 1 - age / 1.3) * 0.75 * (1 - fe);
          for (let g = 0; g < TAU; g += 0.04) {
            const front = Math.cos(g) > 0;
            p.blend(x + Math.cos(g) * 5, HY + Math.sin(g) * r, front ? C[6] : C[4], a * (front ? 1 : 0.35));
          }
        }
        // 포를 가로지르는 가늘고 긴 기운 줄 (전자포 빛줄을 옅게, 깜박이며 높이가 흔들림)
        const fr = Math.floor(t * 15);
        [[-1.35, C[5]], [1.45, C[5]], [-1.7, C[4]]].forEach(([k, c], i) => {
          const y = HY + HW * thin * k * (1 + 0.1 * (hash(fr, i) - 0.5));
          for (let x = Math.max(HX + 30, tail); x < head - HW; x++) p.blend(x, y, c, 0.32 * (1 - fe) * (0.6 + 0.4 * hash(fr, i + 9)));
        });
        // 둥근 머리: 실타래가 엉켜 도는 밝은 머리
        if (head < HX + LEN - 1 || f < FIRE) jThreads(p, C, L10, head - HW * 0.55, HY, HW * 0.55 * thin, t, 0.85 * (1 - fe));
      }
      // 쏘는 순간 구슬에서 압력 고리 두 겹
      pressureRing(p, C, HX, HY, f / 0.35, HW * 0.5, HW * 1.5, 1, 0.9);
      pressureRing(p, C, HX + 10, HY, (f - 0.06) / 0.4, HW * 0.4, HW * 1.7, 1.25, 0.6);
      // 끝: 구슬이 실로 풀림
      if (fe > 0) { jBody(p, C, HX, HY, HW * 0.3, fe); jThreads(p, C, L10, HX, HY, HW * 0.3, t * 0.4, (1 - fe) * 0.9, 1, 1, 1 + 4 * ease.outCubic(fe)); }
    },
  };
}

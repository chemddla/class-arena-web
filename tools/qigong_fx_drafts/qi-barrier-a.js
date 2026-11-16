// 기공막 시안 (일반 공격 실타래 기구슬 바탕) — 반짝임·먼지·바닥 고리 없음
//   모으기 0.4초(게임 시전 시간): 가슴 앞에 작은 실타래 구슬이 차오름
//   펼치기 0.25초: 구슬이 몸을 감싸는 세로로 긴 타원 막으로 부풀어 오름 (게임: 가로 반지름 0.42칸, 세로 1.18배, 몸통 가운데)
//   유지: 막이 은은하게 돎. 날아온 투사체가 막에 닿으면 닿은 자리가 출렁이며 밝아지고 작은 압력 고리, 투사체는 금빛으로 물들어 되돌아감
//   끝: 막이 실 고리로 풀리며 옅어짐
//   style: 'a' 실타래 막 (막 표면을 기운 실 열여섯 가닥이 감싸 돎) · 'b' 고리 막 (굵은 실 고리 세 개만 혼천의처럼 돎) · 'c' 일렁 막 (가장자리가 기운처럼 일렁이고 실이 표면을 따라 흐름)
import { Rng, fit, ease, clamp, noise2, TAU } from "../../core/index.js";
import { QI_GOLD, pressureRing } from "./_qi.js";
import { makeLoops, jOrb, jThreads, jLines } from "./_jcore.js";

const CAST = 0.4, OPEN = 0.25, END = 2.7, FADE = 0.45;
const CY = -51, RX = 80, RY = 94;                  // 게임 크기(반지름 50·59, 몸통 가운데 발 위 32)를 미리보기 캐릭터 키 86 비율로
const SHOT_T0 = 1.15, SHOT_V = 330, SHOT_Y = -60;  // 오른쪽에서 날아오는 적 투사체
const HIT_X = RX * Math.sqrt(1 - ((SHOT_Y - CY) / RY) ** 2), SHOT_X0 = 260, HIT_T = SHOT_T0 + (SHOT_X0 - HIT_X) / SHOT_V;
export const meta = { size: [440, 300], origin: [150, 250], loop: false, fps: 30, bg: "dark", name: "기공막 A 실타래 막", desc: "몸을 감싸는 실타래 막, 투사체 튕겨내기", tags: ["qigong"], duration: END + FADE + 0.05, options: { palette: QI_GOLD, seed: 3, style: "a" } };
export const TIMES = { CAST, OPEN, END, FADE, HIT_T };

const L16 = makeLoops(16), L3 = [[0.15, 0, 2.2], [1.15, 1.2, -1.7], [2.05, 2.4, 1.4]];

// 막 안쪽 바탕: 아주 옅은 금빛, 가장자리로 갈수록 진해지는 띠 (진짜 반투명)
const sstep = (a, b, x) => { const u = clamp((x - a) / (b - a)); return u * u * (3 - 2 * u); };
function shell(p, C, sc, k, t, wobK, hit, soft) {
  const rx = RX * sc, ry = RY * sc, pad = soft ? 0.16 : 0.03;
  for (let py = Math.floor(CY - ry * (1 + pad) - 2); py <= CY + ry * (1 + pad) + 2; py++) for (let px = Math.floor(-rx * (1 + pad) - 2); px <= rx * (1 + pad) + 2; px++) {
    const dx = px + 0.5, dy = py + 0.5 - CY, a = Math.atan2(dy / ry, dx / rx);
    let w = 1 + wobK * noise2(Math.cos(a) * 2.2 + t * 2.5, Math.sin(a) * 2.2 - t * 2);
    // 투사체가 닿은 자리: 안으로 눌렸다가 출렁임
    if (hit) { const da = Math.atan2(Math.sin(a - hit.a), Math.cos(a - hit.a)); w -= hit.dent * Math.exp(-(da * da) / 0.08) * Math.cos(hit.ph); }
    const v = Math.hypot(dx / rx, dy / ry) / w;
    let al, c;
    if (soft) {
      // 그라데이션 기운 막 (사용자: 테두리가 코드 선 같음 → 자연스러운 기의 막): 안쪽(0.5)에서 서서히 진해져 0.93에서 가장 짙고,
      //   바깥으로 1.14까지 부드럽게 번져 사라짐. 둘레를 따라 짙고 옅음이 천천히 일렁임 (딱딱한 1칸 선 없음)
      if (v > 1.14 || (v < 0.5 && !(hit && hit.glow > 0))) continue;
      const band = sstep(0.5, 0.93, v) * (1 - sstep(0.93, 1.14, v));
      const breathe = 0.78 + 0.22 * noise2(Math.cos(a) * 3 + t * 1.6, Math.sin(a) * 3 - t * 1.2);
      al = band * breathe * 0.82;
      c = band > 0.8 ? C[6] : band > 0.45 ? C[5] : C[4];
    } else {
      if (v > 1) continue;
      if (v < 0.62 && !(hit && hit.glow > 0)) continue;   // 안쪽은 비워 둠 (금빛을 캐릭터 위에 덮으면 칙칙해짐)
      al = v > 0.9 ? 0.75 : v > 0.78 ? 0.3 : 0.14 * (v - 0.62) / 0.16;
      c = v > 0.9 ? C[5] : C[4];
    }
    // 닿은 자리 빛 (그라데이션 막에서는 부드럽게 번짐)
    if (hit && hit.glow > 0) { const da = Math.atan2(Math.sin(a - hit.a), Math.cos(a - hit.a)); const g = hit.glow * Math.exp(-(da * da) / 0.12) * (soft ? sstep(0.45, 0.92, v) * (1 - sstep(0.95, 1.14, v)) : clamp((v - 0.55) / 0.45)); al = Math.min(1, al + g * 0.7); if (g > 0.4) c = C[6]; }
    p.blend(px + 0.5, py + 0.5, c, al * k);
  }
}

// 막 표면을 감싸 도는 기운 실 (타원에 맞춰 늘림)
function surfThreads(p, C, loops, sc, k, t, thick) {
  loops.forEach(([tilt, yaw, sp], i) => {
    const ct = Math.cos(tilt), st = Math.sin(tilt), ya = yaw + t * 0.6 * (i % 2 ? 1 : -1), cy = Math.cos(ya), sy = Math.sin(ya);
    for (let a = 0; a < TAU; a += 0.012) {
      const u = a + t * sp * 0.25, px = Math.cos(u), py = Math.sin(u) * ct, pz = Math.sin(u) * st;
      const X = px * cy - pz * sy, Z = px * sy + pz * cy;
      const x = X * RX * sc * 0.97, y = CY + py * RY * sc * 0.97;
      if (Z > 0) { p.blend(x, y, C[6], k); if (thick) p.blend(x, y + 1, C[5], k * 0.8); }
      else p.blend(x, y, C[4], k * 0.28);   // 뒤쪽 반은 막 너머로 옅게
    }
  });
}

export function create(o) {
  const C = fit(o.palette, 7), st = o.style || "a";
  let t = 0;
  return {
    update(dt) { t += dt; },
    draw(p) {
      // 모으기: 가슴 앞 작은 구슬
      if (t < CAST + 0.05) { const e = clamp(t / CAST); jOrb(p, C, makeLoops(10), 10, CY + 2, 1.5 + 6 * ease.outBack(e), t, clamp(e * 2)); }
      if (t < CAST) return;
      // 크기·투명도: 펼치기(구슬이 부풀어 막이 됨) → 유지 → 끝(실 고리로 풀리며 옅어짐)
      const op = clamp((t - CAST) / OPEN), fe = clamp((t - END) / FADE);
      const sc = (0.12 + 0.88 * ease.outBack(op)) * (1 + 0.12 * ease.outCubic(fe)), k = (0.4 + 0.6 * op) * (1 - fe);
      let hit = null;
      const hb = t - HIT_T;
      if (hb >= 0 && hb < 0.6) hit = { a: Math.atan2((SHOT_Y - CY) / RY, HIT_X / RX), dent: 0.07 * Math.exp(-hb * 6), ph: hb * 26, glow: Math.max(0, 1 - hb / 0.35) };
      shell(p, C, sc, k, t, st === "c" ? 0.06 : 0.025, hit, st !== "c");   // A·B는 그라데이션 기운 막 테두리
      if (st === "a") surfThreads(p, C, L16, sc, k * 0.6, t, false);   // 실은 조금 옅게 (막의 그라데이션이 주인공)
      if (st === "b") surfThreads(p, C, L3, sc, k, t, true);
      if (st === "c") {   // 표면을 따라 흐르는 짧은 실 줄기 (가장자리 둘레를 돎)
        for (let i = 0; i < 14; i++) {
          const a0 = (i / 14) * TAU + t * (0.9 + (i % 3) * 0.25) * (i % 2 ? 1 : -1), len = 0.5 + (i % 4) * 0.12, rr = 0.82 + 0.13 * ((i * 0.37) % 1);
          for (let a = a0; a < a0 + len; a += 0.01) { const f = (a - a0) / len; p.blend(Math.cos(a) * RX * sc * rr, CY + Math.sin(a) * RY * sc * rr, f > 0.7 ? C[6] : C[5], k * (0.2 + 0.8 * f)); }
        }
      }
      // 펼치는 순간 막 테두리가 한 번 밀려 나감
      if (op < 1 || t - CAST < OPEN + 0.3) pressureRing(p, C, 0, CY, (t - CAST) / (OPEN + 0.3), RX * 0.3, RX * 1.1, RY / RX, 0.6 * (1 - fe));
      // 끝: 실 고리로 풀리며 퍼짐
      if (fe > 0) jThreads(p, C, makeLoops(10), 0, CY, RX * 0.55, t, (1 - fe) * 0.9, 1, RY / RX, 1 + 1.4 * ease.outCubic(fe));
      // 적 투사체: 오른쪽에서 날아와 막에 닿으면 금빛으로 물들어 되돌아감
      const s0 = t - SHOT_T0;
      if (s0 >= 0) {
        const back = t >= HIT_T, x = back ? HIT_X + (t - HIT_T) * SHOT_V * 1.15 : SHOT_X0 - s0 * SHOT_V;
        if (x < 300) {
          const col = back ? C[5] : 0x8a7fa6, rim = back ? C[6] : 0xd6d0ea;
          p.circle(x, SHOT_Y, 3.6, col); p.circle(x - (back ? -1 : 1), SHOT_Y - 1, 1.6, rim);
          for (let d = 1; d < 12; d++) p.blend(x + (back ? -d : d), SHOT_Y, back ? C[5] : 0x8a7fa6, 0.5 * (1 - d / 12));
        }
      }
      if (hb >= 0 && hb < 0.4) { pressureRing(p, C, HIT_X, SHOT_Y, hb / 0.3, 3, 16, 1, 0.9); if (hb < 0.18) jLines(p, C, HIT_X, SHOT_Y, 4, hb / 0.18, 0.5, 8); }
    },
  };
}

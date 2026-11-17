// 기공사 SR 기공막 · 청기막: 가슴으로 기가 모여 → 기의 막이 부풀며 출렁이다 자리 잡음
//   (선 없이 안에서 밖으로 짙어지는 기운 띠 · 띠를 타고 위로 흐르는 기류 · 바깥으로 타오르는 기운 불꽃 · 떠오르는 기 알갱이 · 바닥 압력 고리)
//   → 날아온 화살이 막에 닿으면 그 자리가 움푹 패며 압력 고리가 일고 그대로 되튕김 → 끝나면 막이 기 알갱이로 흩어짐
import { Rng, fit, TAU, hex } from "../../core/index.js";
import { QI_SKY, soft, tongue, HAND, Drops, orb, outBack } from "./_sr.js";

const CAST = 0.4, POP = 3.0, ARROW = 1.4, RX = 46, RY = 56, BY = -50;
export const meta = { size: [260, 170], origin: [130, 152], loop: false, fps: 30, bg: "dark", name: "기공사 SR 청기막", desc: "위로 타오르는 맑은 기의 막", tags: ["qigong"], duration: POP + 1.0, options: { palette: QI_SKY, seed: 7 } };
export const TIMES = { CAST, POP };
const SHAFT = hex("#c9c2b4"), HEAD = hex("#e4ddcf"), FLETCH = hex("#9b5b45");

// 기의 막 (dent: 맞은 자리 움푹, dang: 그 방향): 선 없이 안에서 밖으로 짙어지는 기운 띠 · 띠를 타고 위로 흐르는 기류 ·
//   바깥으로 혀처럼 타오르는 기운 불꽃(위쪽일수록 높게) · 속에서 떠오르는 기 알갱이
function bubble(p, C, x, y, rx, ry, t, a, dent, dang) {
  if (rx < 2) return;
  p.glow(x, y, rx * 1.4, C[3], 0.14 * a);
  soft(p, x - rx * 1.3, y - ry * 1.4, x + rx * 1.3, y + ry * 1.2, (px, py, out) => {
    const dx = (px - x) / rx, dy = (py - y) / ry, an = Math.atan2(dy, dx), da = Math.atan2(Math.sin(an - dang), Math.cos(an - dang));
    const d = Math.hypot(dx, dy) / (1 - dent * Math.exp(-((da / 0.32) ** 2)));
    const { tg, up } = tongue(an, t * 0.8), E = 1.03 + tg * 0.1 + up * up * 0.16 * (0.4 + tg);
    if (d > E) return;
    if (d > 1) { const f = (d - 1) / (E - 1); out.a = a * 0.5 * (1 - f) * (1 - f); return f < 0.4 ? C[4] : C[3]; }   // 기운 불꽃
    if (d > 0.84) {
      const e = (d - 0.84) / 0.16, u = Math.abs(((an + Math.PI / 2) % TAU + TAU + Math.PI) % TAU - Math.PI);
      const flow = Math.max(0, Math.sin(u * 9 + t * 7)) ** 3 * 0.35 * e;               // 띠를 타고 위로 흐르는 기류: 밝기 너울로만
      out.a = a * (0.12 + 0.55 * e * e + flow); return e + flow > 0.85 ? C[6] : e > 0.5 ? C[5] : C[4];
    }
    out.a = a * 0.07; return C[3];
  });
  for (let i = 0; i < 9; i++) {   // 떠오르는 기 알갱이
    const span = ry * 1.8, q = (t * 22 + i * span / 9) % span;
    p.blend(x + Math.sin(i * 2.7 + t * 1.3) * rx * 0.6, y + ry * 0.85 - q, C[5], 0.6 * a * Math.sin(Math.PI * q / span));
  }
}

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed), D = new Drops(R);
  const [cx, cy] = HAND.chest, T = { x: cx, y: cy - 2, r: 3 };
  let t = 0, fl = 0, popped = false, arrow = null, dent = null;
  return {
    update(dt) {
      t += dt;
      if (t < CAST) D.gather(T, 110, 22, 50, dt, 1.2);
      if (t >= CAST && t < POP && (fl -= dt) <= 0) { fl = 0.55; D.ring(0, -1, 30, 62, 1, { sy: 0.22, w: 1.5, a: 0.4 }); }
      if (t >= ARROW && !arrow) arrow = { x: 130, y: -62, vx: -320 };
      if (arrow) {
        arrow.x += arrow.vx * dt;
        if (arrow.vx < 0 && arrow.x <= RX + 2) {
          arrow.vx = 300; dent = { t0: t, ang: Math.atan2((arrow.y - BY) / RY, 1) };
          D.ring(arrow.x, arrow.y, 1, 12, 0.45, { sx: 0.35, w: 1.5 }); D.ring(arrow.x, arrow.y, 2, 20, 0.55, { sx: 0.25, w: 1, a: 0.6 });
          for (let i = 0; i < 7; i++) D.drop(arrow.x, arrow.y, R.range(40, 120), R.range(-100, -40), { life: 0.8 });
        }
      }
      if (t >= POP && !popped) {
        popped = true;
        for (let i = 0; i < 46; i++) {
          const a = i / 46 * TAU, x = Math.cos(a) * RX, y = BY + Math.sin(a) * RY;
          D.drop(x, y, Math.cos(a) * R.range(30, 70), Math.sin(a) * 30 - 30, { r: R.chance(0.25) ? 2 : 1, life: 1.1 });
          if (i % 4 === 0) D.mist(x, y, Math.cos(a) * 20, Math.sin(a) * 20, 3, 10, 0.7, 0.16);
        }
        D.add({ k: 4, x: 0, y: BY, r0: RX, r1: RX * 1.3, life: 0.3, sy: RY / RX });
      }
      D.update(dt, t);
    },
    draw(p) {
      if (t < CAST) orb(p, C, T.x, T.y, 1 + 4 * (t / CAST), t);
      if (t >= CAST && t < POP) {
        const e = t - CAST, k = outBack(e / 0.32), jig = Math.sin(e * 26) * Math.exp(-e * 4.5) * 0.09;
        let dd = 0;
        if (dent) { const d = t - dent.t0; dd = 0.14 * Math.exp(-d * 6) * Math.cos(d * 22); }
        bubble(p, C, 0, BY, RX * k * (1 + jig), RY * k * (1 - jig), t, Math.min(1, e * 5), dd, dent ? dent.ang : 0);
      }
      if (arrow && arrow.x < 140) {
        const s = Math.sign(arrow.vx);
        p.line(arrow.x, arrow.y, arrow.x - s * 16, arrow.y, SHAFT, 1);
        p.tri(arrow.x + s * 3, arrow.y, arrow.x, arrow.y - 2, arrow.x, arrow.y + 2, HEAD, 1);
        p.rect(arrow.x - s * 16 - (s > 0 ? 0 : 2), arrow.y - 2, 3, 4, FLETCH, 1);
      }
      D.draw(p, C);
    },
  };
}

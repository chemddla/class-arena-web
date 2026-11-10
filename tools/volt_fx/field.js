// 일렉트릭 필드 (반복, 바닥 장판): 바닥에 깔린 전류 그물. 기준점 = 장판 가운데 (바닥). 원 테두리 없음 — 그물 무늬의 끝으로 범위가 보임.
// - 그물: 흔들린 육각 격자 점을 이웃끼리 지그재그 줄로 이음 (바닥 원근: 세로 RY/R). 바깥으로 갈수록 줄이 옅어지지만 끝까지 보임
// - 맥박: 가운데에서 바깥으로 0.75초마다 밝은 물결이 그물을 타고 퍼짐 (1.5초에 두 번, 이음매 없음)
// - 매 프레임 그물 몇 줄이 새로 번쩍 (다시 그은 굵은 전류), 매듭점에서 짧은 전류가 위로 튀고, 작은 빛 알갱이가 떠오름
// 크기 옵션 R = 반지름 (게임 px, 1칸 = 120). 기본 3칸 = 360. 강화 4칸은 같은 시트를 4/3배로 그리거나 R: 480으로 따로 구움
import { fit, clamp, rng, Rng, cycle, TAU, WHITE } from "../../core/index.js";
import { zigzag, crackle } from "../lightning/_lib.js";
import { PLASMA_V, SPARK_V } from "./_volt.js";

const R0 = 360, SQ = 0.3;
export const meta = {
  name: "Volt field",
  desc: "An electric net on the floor: a jittered lattice of jagged current, pulses rolling out from the middle, strands flaring, short arcs jumping up off the knots, motes drifting up. No rim: the net's edge marks the area.",
  tags: ["lightning", "electric", "plasma", "zone", "ground", "loop"],
  size: [R0 * 2 + 24, Math.round(R0 * SQ * 2 + 70)],
  origin: [R0 + 12, Math.round(R0 * SQ + 52)],
  duration: 1.5,
  loop: true,
  fps: 20,
  bg: "dark",
  options: { palette: PLASMA_V, sparks: SPARK_V, R: R0, gap: 74, seed: 11 },
};

const FPS = 20, N = 30, PULSE = 0.75;
const cache = new Map();
// 그물 모양: 한 번만 만듦 (같은 R·gap·seed면 매 프레임 같은 그물)
function net(Rr, gap, seed) {
  const key = `${Rr}|${gap}|${seed}`;
  if (cache.has(key)) return cache.get(key);
  const G = new Rng(seed * 31 + 7), nodes = [], edges = [];
  const rowH = gap * 0.866;
  for (let r = -Math.ceil(Rr / rowH); r <= Math.ceil(Rr / rowH); r++)
    for (let c = -Math.ceil(Rr / gap) - 1; c <= Math.ceil(Rr / gap) + 1; c++) {
      const u = c * gap + (r & 1 ? gap / 2 : 0) + G.range(-gap * 0.22, gap * 0.22), v = r * rowH + G.range(-gap * 0.22, gap * 0.22);
      const d = Math.hypot(u, v) / Rr;
      if (d < 0.97) nodes.push({ u, v, d });
    }
  for (let i = 0; i < nodes.length; i++)
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j], l = Math.hypot(a.u - b.u, a.v - b.v);
      if (l < gap * 1.3 && G.next() < 0.78) {
        const pts = zigzag(G, a.u, a.v * SQ, b.u, b.v * SQ, 0.16, 0).paths[0].pts;
        edges.push({ pts, d: (a.d + b.d) / 2, mx: (a.u + b.u) / 2, my: ((a.v + b.v) / 2) * SQ, a, b });
      }
    }
  const out = { nodes, edges };
  cache.set(key, out);
  return out;
}

export function draw(p, t, o) {
  const C = fit(o.palette, 8), S = fit(o.sparks, 4), f = Math.floor(t * FPS + 1e-6) % N, R = rng(o.seed, 1, f);
  const { nodes, edges } = net(o.R, o.gap, o.seed);
  // 바닥 빛: 넓고 옅게
  for (let i = 0; i < 5; i++) p.glow(((i - 2) / 2) * o.R * 0.55, 0, o.R * 0.5, C[3], 0.07);
  // 맥박 물결: 0.75초마다 하나 (반복 1.5초에 두 번)
  const waves = [(t / PULSE) % 1];
  for (const e of edges) {
    const fade = clamp(1.15 - e.d * 0.75);
    let w = 0;
    for (const ph of waves) w = Math.max(w, 1 - Math.abs(e.d - ph * 1.05) / 0.09);
    if (w > 0) {
      // 물결이 지나가는 줄: 밝은 몸 + 흰 심
      for (let i = 0; i < e.pts.length - 1; i++) {
        const [ax, ay] = e.pts[i], [bx, by] = e.pts[i + 1];
        if (w > 0.4) p.line(ax, ay + 1, bx, by + 1, C[3]);   // 아래쪽 한 줄 더: 물결이 굵고 무겁게
        p.line(ax, ay, bx, by, w > 0.55 ? WHITE : C[5]);
      }
      p.glow(e.mx, e.my, 22, C[4], 0.45 * w * fade);
    } else for (let i = 0; i < e.pts.length - 1; i++) p.line(e.pts[i][0], e.pts[i][1], e.pts[i + 1][0], e.pts[i + 1][1], e.d > 0.75 ? C[1] : C[2], 0.35 + 0.35 * fade);   // 평소 그물은 옅은 남색 (유닛을 가리지 않게)
  }
  // 매듭점: 작은 밝은 점
  for (const n of nodes) {
    const y = n.v * SQ;
    p.px(n.u, y, n.d < 0.85 ? C[4] : C[3]);
    if (((n.u * 7 + n.v * 13 + f * 5) | 0) % 9 === 0) p.glow(n.u, y, 6, C[5], 0.35);
  }
  // 번쩍이는 줄: 매 프레임 4~6줄을 굵은 전류로 다시 그음
  const m = 4 + R.int(0, 2);
  for (let i = 0; i < m; i++) {
    const e = edges[R.int(0, edges.length - 1)];
    crackle(p, zigzag(R, e.a.u, e.a.v * SQ, e.b.u, e.b.v * SQ, 0.28, 0.4), R.range(0.6, 1), C, 0.45);
  }
  // 매듭점에서 위로 튀는 짧은 전류 2~3개
  const k = 2 + R.int(0, 1);
  for (let i = 0; i < k; i++) {
    const n = nodes[R.int(0, nodes.length - 1)], x = n.u, y = n.v * SQ, h = R.range(10, 22);
    crackle(p, zigzag(R, x, y, x + R.range(-6, 6), y - h, 0.45, 0.4), R.range(0.5, 0.9), C, 0.4);
    p.glow(x, y, 10, C[5], 0.4);
  }
  // 떠오르는 빛 알갱이
  cycle(t, 1.5, 46, o.seed + 5, (g) => g.range(0.6, 1.1), (age, L, r) => {
    const a = r.range(0, TAU), d = Math.sqrt(r.next()) * 0.92 * o.R, x = Math.cos(a) * d, y0 = Math.sin(a) * d * SQ;
    const q = age / L, y = y0 - age * r.range(22, 40), x2 = x + Math.sin(age * 9 + r.range(0, 6)) * 1.5;
    const c = q < 0.3 ? WHITE : q < 0.65 ? S[1] : S[2];
    p.px(x2, y, c);
    p.glow(x2, y, 3, S[2], 0.35 * (1 - q));
  });
}

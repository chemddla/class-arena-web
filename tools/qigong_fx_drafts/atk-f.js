// 시안 F 실타래 기구슬 (사용자 참고 그림 느낌): 속이 꽉 찬 빛 구슬 안에 가는 빛 실이 촘촘히 엉켜 돌고,
// 가운데는 하얗게 타며 테두리는 또렷한 밝은 선. 바깥으로 짧은 빛줄기가 방사형으로 뻗어 돌고, 맞으면 실이 풀리듯 사방으로 튀며 터짐
import { Particles, Lights, P, Rng, fit, TAU, WHITE, ease, clamp } from "../../core/index.js";
import { GOLD, H, X1, CHARGE, FLY, HIT, base, gather, burst, hitFlash } from "./_lib.js";

export const meta = { ...base, name: "기공사 F 실타래 기구슬", desc: "빛 실이 엉켜 도는 꽉 찬 구슬", tags: ["qigong"], duration: HIT + 0.8, options: { palette: GOLD, seed: 4, radius: 10 } };

// 실 한 가닥 = 기울어진 원 궤도 [기울기, 방향, 도는 빠르기]
const LOOPS = [];
for (let i = 0; i < 12; i++) LOOPS.push([(i * 2.39) % Math.PI, (i * 1.37) % TAU, (i % 2 ? 1 : -1) * (4 + (i % 5))]);

function orb(p, C, x, y, r, t, k = 1) {
  p.glow(x, y, r * 3, C[4], 0.16 * k);   // 빛은 옅게: 시트로 구우면 빛이 색에 더해져 실 무늬를 덮음
  // 바탕: 가장자리 진한 호박색 → 가운데로 갈수록 밝게 (왼쪽 위가 조금 밝음). 실이 보이게 바탕은 밝은 단계를 안 씀
  p.shade(x - r - 1, y - r - 1, x + r + 1, y + r + 1, (px, py, out) => {
    const dx = px - x, dy = py - y, d = Math.hypot(dx, dy) / r;
    if (d > 1.02) return 0;
    out.a = k;
    if (d > 0.9) return C[5];                           // 또렷한 테두리
    const lit = clamp(1 - d * 0.95 - (dx + dy) / r * 0.1);
    return lit > 0.75 ? C[5] : lit > 0.45 ? C[4] : lit > 0.2 ? C[3] : C[2];
  });
  // 실: 앞쪽 반은 흰빛·밝은 금빛 선, 뒤쪽 반은 바탕보다 한 단 밝은 금빛
  LOOPS.forEach(([tilt, yaw, sp], i) => {
    const ct = Math.cos(tilt) * 0.999, st = Math.sin(tilt), cy = Math.cos(yaw + t * 1.7), sy = Math.sin(yaw + t * 1.7), rr = r * (0.55 + 0.4 * ((i * 0.37) % 1));
    for (let a = 0; a < TAU; a += 0.6 / rr) {
      const u = a + t * sp, px = Math.cos(u) * rr, py = Math.sin(u) * rr * ct, pz = Math.sin(u) * rr * st;
      const X = px * cy - pz * sy, Z = px * sy + pz * cy;
      if (Z > 0) p.px(x + X, y + py, i % 3 ? C[6] : WHITE);
      else p.dot(x + X, y + py, C[4], 0.8 * k);
    }
  });
  p.glow(x - r * 0.1, y - r * 0.1, r * 0.6, C[6], 0.3 * k);
  p.circle(x - r * 0.1, y - r * 0.1, r * 0.22, WHITE);
  // 바깥 빛줄기: 짧은 선이 방사형으로 뻗었다 사라지며 천천히 돎
  for (let i = 0; i < 14; i++) {
    const a = (i / 14) * TAU + t * 2.2, ph = (t * 3 + i * 0.37) % 1, r0 = r * (1.15 + ph * 0.7), L = r * (0.35 + 0.25 * ((i * 0.53) % 1));
    p.line(x + Math.cos(a) * r0, y + Math.sin(a) * r0, x + Math.cos(a) * (r0 + L), y + Math.sin(a) * (r0 + L), i % 2 ? C[5] : C[6], (1 - ph) * 0.8 * k);
  }
}

export function create(o) {
  const C = fit(o.palette, 8), R = new Rng(o.seed), RAD = o.radius;
  const ps = new Particles({ rng: R, ground: () => 0, sparks: [WHITE, C[6], C[5], C[4]] }), lights = new Lights();
  let t = 0, hit = false;
  const fx = (u) => X1 * (0.4 * ease.inQuad(u) + 0.6 * u);
  return {
    update(dt) {
      t += dt;
      gather(ps, R, C, t, dt);
      if (t >= CHARGE && t < HIT && R.chance(0.8)) {
        const x = fx((t - CHARGE) / FLY);
        ps.spawn(P.MOTE, x - RAD, -H + R.range(-RAD * 0.7, RAD * 0.7), R.range(-90, -40), R.range(-20, 20), R.range(0.15, 0.3), R.pick([C[5], C[6]]), 0.8);
      }
      if (!hit && t >= HIT) {
        hit = true; burst(ps, lights, R, C, X1, -H, 1.1);
        for (let i = 0; i < 30; i++) {   // 풀려 나가는 실 조각
          const a = R.range(0, TAU), sp = R.range(80, 180);
          ps.spawn(P.MOTE, X1 + Math.cos(a) * RAD * 0.6, -H + Math.sin(a) * RAD * 0.6, Math.cos(a) * sp, Math.sin(a) * sp * 0.85, R.range(0.2, 0.42), R.pick([C[6], WHITE, C[5]]), 1.1);
        }
      }
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      ps.draw(p);
      if (t < CHARGE) { const k = t / CHARGE; orb(p, C, 0, -H, 2 + (RAD - 2) * 0.6 * ease.outBack(k), t, Math.min(1, k * 1.5)); }
      else if (t < HIT) orb(p, C, fx((t - CHARGE) / FLY), -H, RAD, t);
      const q = t - HIT;
      if (q >= 0 && q < 0.12) orb(p, C, X1, -H, RAD * (1 + q * 4), t, 1 - q / 0.12);   // 맞는 순간 부풀며 꺼짐
      hitFlash(p, C, q, X1, -H, 1.2);
      lights.draw(p);
    },
  };
}

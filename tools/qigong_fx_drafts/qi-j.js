// 시안 J 실타래 기구슬 (반짝임 없음): 진한 기운 구슬 속에 기운 실이 엉켜 돌고, 둘레는 일렁이는 기운 막. 뒤로 연기 같은 기운 꼬리.
// 맞는 순간 (2026-11-16 개선): 박힘(구슬이 납작하게 눌림) → 응축(잠깐 오그라듦) → 터짐(실이 큰 고리로 풀려 퍼지고, 두꺼운 압력 고리,
//   기운이 상대 뒤로 뚫고 나감, 바닥 먼지·자갈) → 여운(남은 기운이 아지랑이처럼 피어오름). 별빛·번쩍·불꽃 가루 없음
import { Particles, Lights, P, Rng, fit, TAU, clamp, ease } from "../../core/index.js";
import { QI_GOLD, H, X1, CHARGE, FLY, HIT, base, qiGather, pressureRing } from "./_qi.js";

export const meta = { ...base, size: [320, 112], name: "기공사 J 실타래 기구슬", desc: "기운 실이 엉켜 도는 구슬, 맞으면 실이 풀리며 터짐 (반짝임 없음)", tags: ["qigong"], duration: HIT + 1.4, options: { palette: QI_GOLD, seed: 4, radius: 8 } };

const LOOPS = [];
for (let i = 0; i < 10; i++) LOOPS.push([(i * 2.39) % Math.PI, (i * 1.37) % TAU, (i % 2 ? 1 : -1) * (3 + (i % 4))]);
const SQUASH = 0.045, IMPLODE = 0.085;   // 맞은 뒤: 박힘 끝 · 응축 끝(= 터지는 순간)

// 구슬 (sx·sy: 가로·세로 눌림)
function orb(p, C, x, y, r, t, k = 1, sx = 1, sy = 1) {
  p.glow(x, y, r * 2.4, C[3], 0.16 * k);
  p.disc(x, y, (r + 2.5) * Math.max(sx, sy), C[3], 0.3 * k);   // 기운 막
  p.shade(x - r * sx - 1, y - r * sy - 1, x + r * sx + 1, y + r * sy + 1, (px, py, out) => {
    const dx = (px - x) / sx, dy = (py - y) / sy, d = Math.hypot(dx, dy) / r;
    if (d > 1.02) return 0;
    out.a = k;
    const lit = clamp(1 - d * 0.95 - (dx + dy) / r * 0.1);
    return d > 0.9 ? C[4] : lit > 0.7 ? C[4] : lit > 0.35 ? C[3] : C[2];
  });
  threads(p, C, x, y, r, t, k, sx, sy, 1);
}

// 기운 실: 기울어진 원 궤도 (grow로 풀려 커짐, 커질수록 옅어지고 끊김)
function threads(p, C, x, y, r, t, k, sx, sy, grow) {
  LOOPS.forEach(([tilt, yaw, sp], i) => {
    if (grow > 1 && i % 2) return;   // 풀릴 때는 다섯 가닥만: 굵직한 고리로 읽히게
    const ct = Math.cos(tilt) * 0.999, st = Math.sin(tilt), cy = Math.cos(yaw + t * 1.5), sy2 = Math.sin(yaw + t * 1.5);
    const rr = r * (0.5 + 0.45 * ((i * 0.37) % 1)) * (grow > 1 ? grow * (0.8 + 0.4 * ((i * 0.61) % 1)) : 1);
    const gap = grow > 1 ? 0.08 + 0.3 * clamp((grow - 1) / 5) : 0;   // 풀릴수록 실이 군데군데 끊김 (가루처럼 보이지 않게 조금만)
    for (let a = 0; a < TAU; a += 0.6 / rr) {
      const u = a + t * sp, px = Math.cos(u) * rr, py = Math.sin(u) * rr * ct, pz = Math.sin(u) * rr * st;
      const X = px * cy - pz * sy2, Z = px * sy2 + pz * cy;
      if (Z <= 0 || (gap && ((a * 3.1 + i) % 1) < gap)) continue;
      if (grow > 1) { p.blend(x + X * sx, y + py * sy, C[6], k); p.blend(x + X * sx, y + py * sy + 1, C[4], k * 0.6); }
      else p.px(x + X * sx, y + py * sy, i % 3 ? C[5] : C[6]);
    }
  });
}

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed), RAD = o.radius;
  const ps = new Particles({ rng: R, ground: () => 0, haze: C[4] }), lights = new Lights();
  let t = 0, boom = false;
  const BX = X1 - 3;   // 박히는 자리 (상대 몸 앞)
  return {
    update(dt) {
      t += dt;
      qiGather(ps, R, C, t, dt);
      if (t >= CHARGE && t < HIT) {
        const x = X1 * (t - CHARGE) / FLY;
        for (let i = 0; i < 2; i++) ps.spawn(P.VAPOUR, x - RAD, -H + R.range(-RAD * 0.6, RAD * 0.6), R.range(-60, -25), R.range(-8, 8), R.range(0.2, 0.35), R.pick([C[4], C[5]]), R.range(2.2, 3.4));
      }
      if (!boom && t >= HIT + IMPLODE) {
        boom = true;
        const y = -H;
        lights.add(BX, y, 44, C[4], 0.6, 0.4);
        // 기운 분출: 대부분 상대 뒤쪽(+x)으로 원뿔처럼, 일부는 옆·앞으로
        for (let i = 0; i < 26; i++) {
          const back = i < 18, a = back ? R.range(-0.7, 0.7) : R.range(0, TAU), sp = back ? R.range(260, 460) : R.range(40, 90);   // 입자에 끌림(drag)이 강해서 뒤로는 빠르게 쏴야 상대 몸 뒤까지 나감
          ps.spawn(back ? P.DUST : P.VAPOUR, BX, y + R.range(-3, 3), Math.cos(a) * sp, Math.sin(a) * sp * 0.7, R.range(0.35, 0.6), R.pick([C[4], C[5], C[6]]), back ? R.range(3, 5) : R.range(2, 3));   // 뒤로 뚫는 기운은 진한 덩이(DUST)
        }
        // 바닥: 먼지 띠와 튀는 자갈 (상대 발밑)
        for (let i = 0; i < 12; i++) {
          const dir = i % 2 ? 1 : -1;
          ps.spawn(P.DUST, BX + 6 + dir * R.range(0, 8), -1, dir * R.range(30, 90), -R.range(4, 16), R.range(0.4, 0.7), "#a08a6a", R.range(2.2, 4));
        }
        for (let i = 0; i < 7; i++) ps.spawn(P.GRIT, BX + 6 + R.range(-6, 6), -1, R.range(-50, 80), -R.range(80, 150), R.range(0.5, 0.75), R.pick(["#6e5a44", "#8a7458"]), 1);
        // 여운: 남은 기운이 천천히 피어오름
        for (let i = 0; i < 8; i++) ps.spawn(P.VAPOUR, BX + R.range(-10, 14), y + R.range(-8, 8), R.range(-6, 10), -R.range(10, 22), R.range(0.6, 0.9), R.pick([C[4], C[5]]), R.range(2, 3), R.range(0.12, 0.4));
      }
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      const q = t - HIT, y = -H;
      ps.draw(p);
      if (t < CHARGE) orb(p, C, 0, y, 2 + (RAD - 2) * 0.7 * (t / CHARGE), t, Math.min(1, t / CHARGE * 1.5));
      else if (q < 0) orb(p, C, X1 * (t - CHARGE) / FLY, y, RAD, t);
      else if (q < SQUASH) {   // 박힘: 앞으로 납작하게 눌림 + 맞닿은 면에 짧은 압력선
        const e = q / SQUASH;
        orb(p, C, BX - 2 * e, y, RAD, t, 1, 1 - 0.35 * e, 1 + 0.3 * e);
        for (let s = -RAD * 1.4; s <= RAD * 1.4; s += 0.5) p.blend(BX + RAD * 0.7, y + s, C[6], 0.7 * (1 - Math.abs(s) / (RAD * 1.4)));
      } else if (q < IMPLODE) {   // 응축: 잠깐 오그라듦 (진해짐)
        const e = (q - SQUASH) / (IMPLODE - SQUASH);
        orb(p, C, BX - 2, y, RAD * (1 - 0.45 * ease.inQuad(e)), t, 1, 0.65 + 0.35 * e, 1.3 - 0.3 * e);
      }
      const b = q - IMPLODE;
      if (b >= 0) {
        // 실이 큰 고리로 풀리며 퍼짐
        if (b < 0.42) { const e = b / 0.42; threads(p, C, BX, y, RAD, t * 0.4 + 2, Math.pow(1 - e, 1.4), 1, 1, 1 + 5 * ease.outCubic(e)); }
        // 두꺼운 압력 고리 (세로로 선 것, 비스듬히 누운 것, 바닥)
        pressureRing(p, C, BX, y, b / 0.32, 5, 26, 1, 1);
        pressureRing(p, C, BX, y, (b - 0.04) / 0.4, 4, 36, 0.4, 0.75);
        pressureRing(p, C, BX + 6, 0, (b - 0.02) / 0.5, 5, 30, 0.18, 0.7);
        // 터지는 순간 가운데 기운 덩이가 확 부풀었다 사라짐 (흰빛 없이 크림색까지만)
        if (b < 0.1) { const e = b / 0.1; p.disc(BX, y, RAD * (0.6 + 1.6 * e), C[5], 0.85 * (1 - e)); p.disc(BX, y, RAD * (0.3 + 0.8 * e), C[6], 0.7 * (1 - e)); }
      }
      lights.draw(p);
    },
  };
}

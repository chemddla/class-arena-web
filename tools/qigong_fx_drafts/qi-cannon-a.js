// 기공포 시안 (일반 공격 실타래 기구슬 바탕) — 반짝임·먼지·바닥 고리 없음
//   모으기 0.6초: 큰 고리로 떠 있던 기운 실 열여섯 가닥이 가슴 앞으로 감겨 들어와 큰 구슬이 됨 (일반 공격 터짐을 거꾸로)
//   발사: 큰 실타래 구슬이 곧게 날아가며 적을 꿰뚫음 — 지나가는 적마다 작은 압력 고리·짧은 선 (멈추지 않음)
//   끝: 사거리 끝에서 일반 공격보다 크게 터짐
//   style: 'a' 큰 구슬 + 기운 꼬리 · 'b' 구슬 뒤로 기운 실 두 가닥이 나선으로 꼬이며 따라감 · 'c' 지나간 자리에 세로 압력 고리가 줄지어 남음
import { Particles, Lights, P, Rng, fit, ease, clamp } from "../../core/index.js";
import { QI_GOLD, H, base, pressureRing } from "./_qi.js";
import { makeLoops, jOrb, jThreads, jLines, jBurst, jGatherIn } from "./_jcore.js";

export const CHARGE = 0.6, FLY = 0.55, END = 270, TARGETS = [110, 200], RC = 15;
const HIT = CHARGE + FLY;
export const meta = { ...base, size: [420, 150], origin: [40, 130], name: "기공포 A 큰 실타래 포", desc: "꿰뚫는 큰 실타래 구슬 (기운 꼬리)", tags: ["qigong"], duration: HIT + 0.75, options: { palette: QI_GOLD, seed: 7, style: "a" } };

const LOOPS = makeLoops(16);
const xAt = (t) => END * clamp((t - CHARGE) / FLY);   // 곧게 일정한 빠르기 (꿰뚫으며 감속 없음)
export const passTime = (tx) => CHARGE + (tx / END) * FLY;

export function create(o) {
  const C = fit(o.palette, 7), R = new Rng(o.seed), st = o.style || "a";
  const ps = new Particles({ rng: R, ground: () => 0, haze: C[4] }), lights = new Lights();
  let t = 0;
  const wake = [];   // style c: 남겨 둔 압력 고리 [x, 남긴 시각]
  let nextWake = 24;
  return {
    update(dt) {
      t += dt;
      if (t >= CHARGE && t < HIT) {
        const x = xAt(t);
        if (st !== "b") for (let i = 0; i < 2; i++) ps.spawn(P.VAPOUR, x - RC, -H + R.range(-RC * 0.6, RC * 0.6), R.range(-70, -30), R.range(-10, 10), R.range(0.25, 0.4), R.pick([C[4], C[5]]), R.range(3, 5));
        if (st === "c" && x >= nextWake) { wake.push([x - RC * 0.4, t]); nextWake += 30; }
      }
      ps.update(dt); lights.update(dt);
    },
    draw(p) {
      ps.draw(p);
      const y = -H;
      // 모으기: 실이 감겨 들어오고, 끝 무렵 구슬이 차오름
      if (t < CHARGE) {
        const e = t / CHARGE;
        jGatherIn(p, C, LOOPS, 0, y, RC, t, ease.inOutSine(e));
        if (e > 0.55) jOrb(p, C, LOOPS, 0, y, RC * ease.outBack((e - 0.55) / 0.45), t, clamp((e - 0.55) / 0.3));
      }
      // style c: 지나간 자리의 세로 압력 고리
      wake.forEach(([wx, wt]) => pressureRing(p, C, wx, y, (t - wt) / 0.45, RC * 0.9, RC * 1.6, 1, 0.55));
      // 날아가는 구슬
      if (t >= CHARGE && t < HIT) {
        const x = xAt(t);
        if (st === "b") {   // 뒤로 나선으로 꼬이며 따라가는 기운 실 두 가닥
          for (let d = RC * 0.6; d < RC * 4.5; d += 0.5) {
            const f = d / (RC * 4.5), ph = (x - d) * 0.16 - t * 20, amp = RC * 0.75 * (1 - f * 0.5), k = 1 - f;
            const front = Math.cos(ph) > 0;
            p.blend(x - d, y + Math.sin(ph) * amp, front ? C[6] : C[4], k);
            p.blend(x - d, y - Math.sin(ph) * amp, front ? C[4] : C[6], k);
          }
        }
        jOrb(p, C, LOOPS, x, y, RC, t);
      }
      // 꿰뚫음: 지나가는 적마다 작은 압력 고리와 짧은 선 (구슬은 멈추지 않음)
      TARGETS.forEach((tx) => {
        const b = t - passTime(tx);
        if (b < 0 || b > 0.4) return;
        pressureRing(p, C, tx, y, b / 0.3, RC * 0.8, RC * 2.1, 1, 0.9);
        if (b < 0.2) jLines(p, C, tx, y, RC * 0.7, b / 0.2, 0.45, 10);
      });
      // 끝: 크게 터짐
      jBurst(p, C, LOOPS, END, y, RC, t, t - HIT, 1.0);
      lights.draw(p);
    },
  };
}

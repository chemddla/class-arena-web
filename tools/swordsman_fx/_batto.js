// 발도 공용: 검사 둘레 3칸(반지름 360px)을 허리 높이의 수평 고리로 벰. 비스듬히 내려다본 원 = 납작한 타원 (게임 바닥 원과 같은 0.45)
// 좌표: 기준점(0, 0) = 검사 몸 가운데 (unit.x, unit.y), 고리 중심은 칼자루 높이 CY. 1 = 게임 화면 1px
import { TAU } from "../../core/index.js";
import { swing, onSwing } from "../melee/_lib.js";

export const R0 = 360, SY = 0.45, CY = -16;
export const SIZE = [2 * R0 + 40, Math.ceil(2 * R0 * SY) + 90], ORIGIN = [R0 + 20, Math.ceil(R0 * SY) + 56];

/** 고리 하나: swing + { span, W, t0, sweep, hold, trail, ramp }. far half (뒤쪽)는 흐리게 */
export const ring = (o) => ({ ...swing({ cx: 0, cy: CY, R: R0, sy: SY, a0: 0.35, dir: -1 }), span: TAU, ...o });

/** 지나간 자리에 남는 1px 고리 자국 (뒤쪽은 흐리게) */
export function ringTrace(p, s, c, a, back = 0.5) {
  if (a <= 0.02) return;
  const du = 0.6 / s.R;
  for (let uu = 0; uu <= s.span; uu += du) {
    const [x, y] = onSwing(s, s.R - 0.5, uu), g = s.a0 + s.dir * uu;
    p.blend(x, y, c, a * (Math.sin(g) < 0 ? back : 1));
  }
}

/** 고리 위 각 u의 화면 점 */
export const ringAt = (s, uu, r = s.R) => onSwing(s, r, uu);

// 에너지파 전자포 공용: 몸통·총구·끝이 같은 두께·색 단계·출렁임을 쓰게 함 (이음매가 맞도록)
import { TAU } from "../../core/index.js";

export const W = 120;   // 몸통 토막 길이 (이 주기로 모든 무늬가 반복)
/** 포 반두께 (thick 1 = 일반 폭 1칸, 2 = 강화 폭 2칸) */
export const halfH = (k) => 15 * k;
/** x(토막 좌표)·ph(0~1 반복 위상)에서 가장자리 반지름: 출렁임이 앞으로 밀려 나감 */
export function edge(x, ph, k) {
  return halfH(k) * (1 + 0.09 * Math.sin(TAU * ((2 * x) / W - 2 * ph)) + 0.05 * Math.sin(TAU * ((5 * x) / W - 5 * ph) + 1.3) + 0.03 * Math.sin(TAU * ((9 * x) / W + 3 * ph)));
}
/** d = |y| / 반지름 → 색 (흰 심이 넓고, 테두리로 갈수록 짙어짐). 0 = 바깥 */
export const band = (d, C, WHITE) => (d < 0.48 ? WHITE : d < 0.64 ? C[6] : d < 0.78 ? C[5] : d < 0.9 ? C[4] : d < 1 ? C[3] : 0);

/**
 * 에너지 구체: 가운데 (cx, cy), 반지름 rs, 가장자리가 끓듯 출렁임 (ph로 반복). 몸통과 같은 색 단계 + 바깥 반투명 기운.
 * stretch: 가로로 늘림 (앞으로 밀고 나가는 머리는 >1)
 */
export function orb(p, cx, cy, rs, ph, C, WHITE, stretch = 1) {
  const rr = (a) => rs * (1 + 0.035 * Math.sin(7 * a + ph * TAU * 2) + 0.03 * Math.sin(11 * a - ph * TAU * 3) + 0.02 * Math.sin(17 * a + ph * TAU * 4));   // 잔잔하게 끓음 (크게 흔들면 별 모양이 됨)
  const ext = Math.ceil(rs * 1.6 * stretch);
  for (let y = Math.floor(cy - rs * 1.6); y <= cy + rs * 1.6; y++)
    for (let x = Math.floor(cx - ext); x <= cx + ext; x++) {
      const dx = (x + 0.5 - cx) / stretch, dy = y + 0.5 - cy, a = Math.atan2(dy, dx), d = Math.hypot(dx, dy) / rr(a);
      if (d >= 1 && d < 1.45) p.blend(x, y, d < 1.2 ? C[4] : C[3], (0.45 * (1.45 - d)) / 0.45);
    }
  p.shade(cx - ext, cy - rs * 1.2, cx + ext, cy + rs * 1.2, (x, y, out) => {
    const dx = (x - cx) / stretch, dy = y - cy, a = Math.atan2(dy, dx), d = Math.hypot(dx, dy) / rr(a);
    const c = band(d, C, WHITE);
    if (c) out.c = c;
  });
  p.px(cx - rs * 0.35 * stretch, cy - rs * 0.4, WHITE);   // 위왼쪽 반짝임 (입체감)
}

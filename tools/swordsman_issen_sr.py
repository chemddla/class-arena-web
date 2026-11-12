# 시크릿 레어 검사 일섬 시트 (assets/sprites/fx/sword/issen-sr.webp): issen.webp에서 전격(잔전기·번개 가지)만 뺀 것 (2026-11-12 사용자: 참격은 그대로, 가미된 전격만 빼고 깃털 잔상)
#   빛줄기·빛의 날은 길(가로줄) 위아래로 대칭이고 (tools/swordsman_fx/issen.js blade: d = |y + 0.5|), 번개·잔전기는 매번 다른 꺾인 모양이라 대칭이 아님
#   → 칸마다 위아래를 뒤집은 그림과 비교해 더 옅은 쪽만 남김 (대칭인 빛은 그대로, 한쪽에만 있는 번개는 사라짐)
#   기준선: 칸 높이 68, 기준점 y 34 (생성기 y = -1, 0 이 33, 34번째 줄) → r 줄의 짝은 67 - r 줄
#   돌진 뒤 속도선은 가로로 길게 이어진 줄이라 되살림 (RUN)
#   사용: python tools/swordsman_issen_sr.py
import numpy as np
from PIL import Image

SRC, OUT = 'assets/sprites/fx/sword/issen.webp', 'assets/sprites/fx/sword/issen-sr.webp'
CW, CH = 511, 68
RUN = 14   # 이만큼 가로로 이어지면 속도선 (번개 가지는 꺾여서 짧음)

a = np.array(Image.open(SRC).convert('RGBA'))
out = a.copy()
for y0 in range(0, a.shape[0], CH):
    for x0 in range(0, a.shape[1] - CW + 1, CW):
        c = a[y0:y0 + CH, x0:x0 + CW]
        m = c[::-1]   # 67 - r 줄
        keep = c[..., 3] <= m[..., 3]
        o = np.where(keep[..., None], c, m)
        # 속도선(돌진 뒤 가로로 긴 빛줄)은 대칭이 아니어도 전격이 아니므로 되살림: 지워진 점 가운데 가로로 RUN칸 넘게 이어진 줄만
        gone = (c[..., 3].astype(int) - o[..., 3]) > 8
        for r in range(CH):
            x = 0
            while x < CW:
                if not gone[r, x]: x += 1; continue
                e = x
                while e < CW and gone[r, e]: e += 1
                if e - x >= RUN: o[r, x:e] = c[r, x:e]
                x = e
        out[y0:y0 + CH, x0:x0 + CW] = o
assert (out[..., 3] <= a[..., 3]).all()   # 빛을 더하지는 않음 (빼기만)
Image.fromarray(out, 'RGBA').save(OUT, 'WEBP', lossless=True)
print(OUT, out.shape)

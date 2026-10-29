# 빙결술사 시트(frost_0~5.webp) 손질: 동결 시전 칸(22·23)의 잘린 지팡이 수정을 좌우대칭으로 완성하고,
# 프리즈 칸(20·21) 맨 위에 남은 가는 흰 줄을 지움. 사용: python tools/frost_sprite_fix.py (여러 번 돌려도 같은 결과가 되도록 먼저 잘린 열을 확인)
import numpy as np
from PIL import Image

CELL_W = 151
# 칸 번호: (잘린 마지막 열, 접어 붙일 폭, 대상 줄 범위)
STAFF = {22: (128, 10, (30, 70)), 23: (137, 9, (30, 70))}
STRAY = {20: range(0, 4), 21: range(0, 6)}

for v in range(6):
    path = f'assets/sprites/merc/frost_{v}.webp'
    im = Image.open(path).convert('RGBA')
    a = np.array(im)
    for f, rows in STRAY.items():
        for r in rows:
            a[r, f * CELL_W:(f + 1) * CELL_W, 3] = 0
    for f, (c, n, (r0, r1)) in STAFF.items():
        x0 = f * CELL_W
        # 이미 고친 시트면 건너뜀 (끝 열 오른쪽에 그림이 있으면)
        if a[r0:r1, x0 + c + 1:x0 + c + 3, 3].max() > 20:
            continue
        for j in range(n):
            a[r0:r1, x0 + c + 1 + j] = a[r0:r1, x0 + c - j]
    Image.fromarray(a).save(path, lossless=True, quality=100)
    print(path)

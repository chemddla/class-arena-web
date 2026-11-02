# 용병 시트 가장자리에 남은 배경 테두리(검은 외곽선 바깥의 흰 점선·반투명 밝은 띠) 지우기.
# 투명 칸에 닿아 있고 바로 안쪽에 어두운 외곽선이 있는 밝은 가장자리 픽셀만 벗겨냄 → 외곽선 안쪽 그림은 그대로.
# 사용: python tools/sprite_halo_clean.py [시트 이름 ...]  (기본: 빙결술사 0~5, 성녀·궁수 1~5)
# 여러 번 돌려도 외곽선에서 멈추므로 결과가 거의 같음
import sys
import numpy as np
from PIL import Image

DEFAULT = [f'frost_{v}' for v in range(6)] + [f'healer_{v}' for v in range(1, 6)] + [f'archer_{v}' for v in range(1, 6)]
PASSES = 2


def lum(rgb):
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


def shifts(arr, fill):
    # 8방향 이웃 (가장자리 밖은 fill)
    h, w = arr.shape[:2]
    p = np.pad(arr, ((1, 1), (1, 1)) + ((0, 0),) * (arr.ndim - 2), constant_values=fill)
    return [p[1 + dy:1 + dy + h, 1 + dx:1 + dx + w] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]


def clean(a):
    a = a.copy()
    removed = 0
    for _ in range(PASSES):
        al = a[..., 3].astype(int)
        L = lum(a[..., :3].astype(float))
        n_al = shifts(al, 0)
        touches_bg = np.zeros(al.shape, bool)
        for i, s in enumerate(n_al):
            if i in (1, 3, 4, 6):  # 상하좌우
                touches_bg |= s == 0
        # 안쪽 이웃 중 가장 어두운 불투명 픽셀(=외곽선)
        darkest = np.full(al.shape, 999.0)
        for sa, sl in zip(n_al, shifts(L, 999.0)):
            darkest = np.minimum(darkest, np.where(sa > 200, sl, 999.0))
        soft = (al > 0) & (al < 200) & (L > 70)
        bright = (al >= 200) & (L > 85)
        kill = (al > 0) & touches_bg & (soft | bright) & (darkest < L - 50) & (darkest < 80)
        # 아무것과도 안 붙은 흐린 점
        lone = (al > 0) & (al < 120) & (np.sum([s > 0 for s in n_al], axis=0) <= 1)
        kill |= lone
        if not kill.any():
            break
        removed += int(kill.sum())
        a[kill] = 0
    return a, removed


# 색 변형 외형은 원본 외형과 투명 영역이 같음 → 테두리와 그림 색이 비슷한 흰·회색 외형도 원본에서 찾은 자리로 지움
MASK_FROM = {f'frost_{v}': 'frost_0' for v in range(1, 6)}

for name in sys.argv[1:] or DEFAULT:
    path = f'assets/sprites/merc/{name}.webp'
    a = np.array(Image.open(path).convert('RGBA'))
    if name in MASK_FROM:
        # 원본 외형은 목록 앞에서 이미 정리됨 → 디스크의 정리된 그림을 그대로 기준으로 씀
        src = np.array(Image.open(f'assets/sprites/merc/{MASK_FROM[name]}.webp').convert('RGBA'))
        kill = (src[..., 3] == 0) & (a[..., 3] > 0)
        out, n = a.copy(), int(kill.sum())
        out[kill] = 0
    else:
        out, n = clean(a)
    Image.fromarray(out).save(path, lossless=True, quality=100)
    print(path, n)

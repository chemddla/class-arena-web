# 공용 불 폭발(spell_hit_fx.webp의 fire_hit 3칸: 마법사·화염술사 파이어볼 폭발)의 흰 배경 찌꺼기 정리 — 시트를 그 자리에서 고침
# 사용: python tools/spell_hit_fire_clean.py   (여러 번 돌려도 결과가 거의 같음)
# - 투명 배경과 맞닿은 연한 점(흰색·연회색·크림 테두리)을 바깥부터 PEEL겹, 아주 흰 점(흰 배경이 남은 덩어리)은 WHITE_PEEL겹 벗김
# - 연한 점만으로 된 작은 조각(떠 있는 흰 점)은 통째로 지움
# - 가운데 크림색 불꽃 심은 둘레가 주황·빨강이라 투명 배경과 닿지 않아 남음
# - 원본(손실 webp)을 다시 무손실로 저장하면 파일이 두 배가 되므로 손실 압축(QUALITY)으로 저장하되, fire_hit 밖은 원본 칸 그대로
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SHEET = 'assets/sprites/fx/spell_hit_fx.webp'
REGION = (0, 0, 677, 276)   # fire_hit 칸들 (x0, y0, x1, y1)
PEEL = 2
WHITE_PEEL = 8
QUALITY = 92


def pale(c):     # 흰색·연회색·크림 (불꽃 노랑 255,230,120 같은 진한 색은 빠짐)
    return (c.min(axis=2) > 150) & (c.max(axis=2) - c.min(axis=2) < 110)


def white(c):    # 흰 배경이 그대로 남은 점
    return (c.min(axis=2) > 215) & (c.max(axis=2) - c.min(axis=2) < 45)


def main():
    im = np.array(Image.open(SHEET).convert('RGBA')).astype(np.int32)
    x0, y0, x1, y1 = REGION
    reg = im[y0:y1, x0:x1]
    c, a = reg[..., :3], reg[..., 3]
    p = pale(c)
    before = int((a > 0).sum())
    for k in range(max(PEEL, WHITE_PEEL)):
        clear = a == 0
        rim = (a > 0) & ndi.binary_dilation(clear, structure=np.ones((3, 3)))
        a[rim & (p if k < PEEL else white(c))] = 0
    op = a > 0
    lab, n = ndi.label(op, structure=np.ones((3, 3)))
    if n:
        sz = ndi.sum(op, lab, range(1, n + 1))
        pale_n = ndi.sum(op & p, lab, range(1, n + 1))
        drop = 1 + np.where((pale_n >= sz * 0.6) & (sz < 60))[0]
        a[np.isin(lab, drop)] = 0
    reg[..., 3] = a
    im[y0:y1, x0:x1] = reg
    Image.fromarray(im.clip(0, 255).astype(np.uint8), 'RGBA').save(SHEET, 'WEBP', quality=QUALITY, method=6)
    print(f'지운 점 {before - int((a > 0).sum())}개')


if __name__ == '__main__':
    main()

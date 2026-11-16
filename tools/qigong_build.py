# 기공사 외형 시트: 격투가 외형 0(brawler_0.webp)의 도복·띠·머리 색을 바꾸고, 기운 칸(31)의 노랑·파랑 불꽃을 청록 기운으로 칠함
# 사용: python tools/qigong_build.py   → assets/sprites/merc/qigong_0.webp (칸 구성·크기는 brawler_0과 같음)
#   임시 그림: 비취 도복·금빛 띠·검은 머리. 사용자가 기공사 샘플을 주면 그 그림으로 바꿈
import sys, os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb
from brawler_variants_build import masks, paint, dark_rim, _hex

SRC = 'assets/sprites/merc/brawler_0.webp'
CELL_W = 119
AURA_CELL = 31  # 격투가 멸식 시전 칸 (발밑에서 솟는 기운 불꽃)
LOOKS = [
    (0, '비취 도복·금빛 띠', ('#2f9e8a', '#d9a441', '#2a2020')),
]
# 청록 기운 램프 (pixelfx 계열: 그림자 → 본색 → 거의 흰색)
QI = ['#0b4f4a', '#14857a', '#2dd4bf', '#99f6e4', '#f0fffb']


def recolor_aura(out, src):
    """기운 칸의 진한 노랑·파랑 불꽃만 청록 램프로 (명도 순서 유지). 도복·살은 진한 색이 아니라 그대로"""
    x0, x1 = AURA_CELL * CELL_W, (AURA_CELL + 1) * CELL_W
    a = src[:, x0:x1]
    hsv = rgb2hsv(a[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    al = a[..., 3] > 0
    flame = al & (s >= 0.45) & (v >= 0.45) & (((h >= 38) & (h <= 75)) | ((h >= 185) & (h <= 255)))
    ramp = np.array([_hex(c) for c in QI])
    idx = np.clip(np.round(v * 4.4 - 0.6 + (h < 80) * 0.6), 0, 4).astype(int)  # 노란 불꽃은 한 단 밝게
    seg = out[:, x0:x1]
    seg[flame, :3] = (ramp[idx][flame] * 255 + .5).astype(np.uint8)
    out[:, x0:x1] = seg
    return out


def main():
    im = np.array(Image.open(SRC).convert('RGBA'))
    skin, hair, hair_edge, trim = masks(im)
    hair_all = hair | hair_edge
    for num, label, (dobok, belt, hair_c) in LOOKS:
        out = paint(im, skin, hair_all, trim, dobok, belt, hair_c)
        out = dark_rim(out, im)
        out = recolor_aura(out, im)
        Image.fromarray(out, 'RGBA').save(f'assets/sprites/merc/qigong_{num}.webp', 'WEBP', lossless=True)
        print(f'qigong_{num}.webp  {label}')


if __name__ == '__main__':
    main()

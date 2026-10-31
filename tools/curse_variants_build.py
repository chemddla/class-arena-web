# 주술사 외형 0(curse_0.webp)에서 색 변형 시트 만들기 (칸 구성·크기 모두 같음)
# 사용: python tools/curse_variants_build.py   → assets/sprites/merc/curse_1~N.webp
# 규칙: 보라·검붉은 계열(망토·바지·깃털·시트에 그려진 이펙트)만 바꿈.
#   피부·소 해골 가면·뼈 지팡이·녹색 털은 그대로
import sys, os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb

SRC = 'assets/sprites/merc/curse_0.webp'
CELL_W = 144
# (번호, 이름, 바꿀 색상(도, None = 그대로), 채도 배율, 명도 배율)
VARIANTS = [
    (1, '진홍', 355, 1.1, 1.0),
    (2, '칠흑', None, 0.3, 0.55),
    (3, '심야 남보라', 258, 0.8, 0.55),
    (4, '묵청', 215, 0.5, 0.5),
    (5, '뼈빛 회갈', 30, 0.25, 1.05),
]


def cloth_mask(f):
    # 보라~자홍(250도 이상) + 어두운 검붉은색. 피부(주황 계열·밝음)와 가면(채도 낮음)은 빠짐
    a = f[..., 3] > 0
    hsv = rgb2hsv(f[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    return a & (s > 0.12) & ((h >= 250) | ((h < 12) & (v < 0.6)))


def recolor(f, hue, sat, val):
    m = cloth_mask(f)
    hsv = rgb2hsv(f[..., :3] / 255.)
    if hue is not None: hsv[..., 0] = np.where(m, hue / 360., hsv[..., 0])
    hsv[..., 1] = np.where(m, np.clip(hsv[..., 1] * sat, 0, 1), hsv[..., 1])
    hsv[..., 2] = np.where(m, np.clip(hsv[..., 2] * val, 0, 1), hsv[..., 2])
    out = f.copy()
    out[m, :3] = (hsv2rgb(hsv)[m] * 255 + .5).clip(0, 255).astype(np.uint8)
    return out


def main():
    im = np.array(Image.open(SRC).convert('RGBA'))
    n = im.shape[1] // CELL_W
    for num, label, hue, sat, val in VARIANTS:
        sheet = np.hstack([recolor(im[:, i * CELL_W:(i + 1) * CELL_W], hue, sat, val) for i in range(n)])
        Image.fromarray(sheet, 'RGBA').save(f'assets/sprites/merc/curse_{num}.webp', 'WEBP', lossless=True)
        print(f'curse_{num}.webp  {label}')


if __name__ == '__main__':
    main()

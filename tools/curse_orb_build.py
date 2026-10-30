# 주술사 기본 공격 불꽃 샘플(초록 배경, 위 = 해골 불꽃 · 아래 = 둥근 보라 불꽃) → assets/sprites/fx/curse_orb.webp
# 사용: python tools/curse_orb_build.py [샘플 png]  (기본 assets/sprites/fx/samples/curse_orb_src.png)
# 아래 불꽃만 씀. 둥근 쪽이 앞(오른쪽)을 향하게 왼쪽으로 90도 돌려서, 꼬리 불길이 뒤로 끌리며 날아감
# 프레임 [x, y, w, h, 기준점x, 기준점y] (기준점 = 둥근 머리 가운데)
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = 'assets/sprites/fx/curse_orb.webp'
KEY = np.array([31.0, 238.0, 8.0])
BOX = (44, 42, 98, 120)  # 아래 불꽃 + 위로 튄 불티 (x0, y0, x1, y1)
HEAD = (70, 103)         # 샘플 좌표의 둥근 머리 가운데


def main(path):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    bright = (g > 150) & (g - np.maximum(r, b) > 50)
    d = np.sqrt(((im - KEY) ** 2).sum(axis=2))
    a = np.where(bright, np.clip((d - 45) / 150, 0, 1), 1.0)
    # 위 해골 불꽃과 이어진 덩어리는 빼고, 상자 안의 덩어리만
    lab, n = ndi.label(a > 0.35)
    x0, y0, x1, y1 = BOX
    keep = np.zeros_like(a, bool)
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if xs.min() >= x0 and xs.max() < x1 and ys.min() >= y0 and ys.max() < y1: keep |= ndi.binary_dilation(lab == i, iterations=1)
    a = np.where(keep, a, 0)
    al = np.maximum(a, 1e-3)[..., None]
    rgb = np.where(a[..., None] < 1, KEY + (im - KEY) / al, im).clip(0, 255)
    rgb[..., 1] = np.minimum(rgb[..., 1], np.maximum(rgb[..., 0], rgb[..., 2]))  # 불꽃엔 초록이 없으니 테두리에 번진 초록 기운은 모두 지움
    rgba = np.dstack([rgb, a * 255]).astype(np.uint8)[y0:y1, x0:x1]
    # 왼쪽으로 90도: 아래(둥근 머리) → 오른쪽
    rot = np.rot90(rgba, 1)
    ys, xs = np.where(rot[..., 3] > 0)
    rot = rot[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # 반시계 90도: 샘플 (x, y) → 돌린 그림 (y, W - 1 - x)
    hx, hy = HEAD[0] - x0, HEAD[1] - y0
    W = rgba.shape[1]
    ax, ay = hy - xs.min(), (W - 1 - hx) - ys.min()
    Image.fromarray(rot, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'flame: [[0,0,{rot.shape[1]},{rot.shape[0]},{ax},{ay}]]')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/fx/samples/curse_orb_src.png')

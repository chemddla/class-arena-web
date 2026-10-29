# 눈꽃 낱개 그림 모음(흰 배경 도트 시트 한 장) → assets/sprites/fx/snowflakes.webp 한 줄 (큰 것부터)
# 사용: python tools/snowflake_build.py <png>   · 흰 배경을 지우고 떨어진 조각마다 한 칸으로 떼어 냄
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = 'assets/sprites/fx/snowflakes.webp'


def main(path):
    rgb = np.array(Image.open(path).convert('RGB')).astype(float)
    a = ((255 - rgb.min(axis=2)) / 45).clip(0, 1)
    a = np.where(a < 0.06, 0, a)
    col = np.where(a[..., None] > 0, (rgb - 255 * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0).clip(0, 255)
    lab, n = ndi.label(ndi.binary_dilation(a > 0.3, iterations=1))
    cells = []
    for i, sl in enumerate(ndi.find_objects(lab)):
        m = (lab[sl] == i + 1)
        aa, cc = a[sl] * m, col[sl]
        if (aa > 0.5).sum() < 14: continue  # 점처럼 작은 얼룩은 뺌
        ys, xs = np.where(aa > 0)
        aa, cc = aa[ys.min():ys.max() + 1, xs.min():xs.max() + 1], cc[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        cells.append(np.dstack([cc, aa * 255]).clip(0, 255).astype(np.uint8))
    cells.sort(key=lambda c: -(c.shape[0] * c.shape[1]))
    H = max(c.shape[0] for c in cells); W = sum(c.shape[1] + 2 for c in cells)
    sheet = np.zeros((H, W, 4), np.uint8); x, table = 0, []
    for c in cells:
        sheet[:c.shape[0], x:x + c.shape[1]] = c
        table.append(f"[{x},0,{c.shape[1]},{c.shape[0]}]")
        x += c.shape[1] + 2
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f"[{', '.join(table)}]")


if __name__ == '__main__':
    main(sys.argv[1])

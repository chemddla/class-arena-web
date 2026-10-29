# 빙결술사 이펙트 샘플(흰 배경 도트 시트) → assets/sprites/fx/frost_fx.webp 한 장 (가로로 이어 붙임, 0.5배)
# 사용: python tools/frost_fx_build.py <샘플 폴더>  (3.webp = 스킬 이펙트, 4.webp = 소환진, 5.webp = 충격파, 8.webp = 눈보라)
# 흰 배경은 지우고, 밝은 얼음빛은 흰색과 섞인 만큼 투명하게 되살림 (게임에서 'lighter'로 겹쳐 그려도 번지지 않음)
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = 'assets/sprites/fx/frost_fx.webp'
SC = 0.5
# 이름, 시트, x0, y0, x1, y1, 기준점 (c = 가운데, b = 아래 가운데)
PIECES = [
    ('bubble0', 3, 311, 118, 452, 237, 'c'), ('bubble1', 3, 467, 118, 632, 237, 'c'),
    ('spike0', 3, 149, 262, 298, 353, 'b'), ('spike1', 3, 352, 262, 558, 362, 'b'),
    ('spike2', 3, 595, 238, 776, 362, 'b'), ('spike3', 3, 831, 238, 1004, 353, 'b'),
    ('ring', 3, 191, 374, 256, 442, 'c'), ('cube0', 3, 374, 362, 535, 464, 'c'), ('cube1', 3, 628, 362, 748, 460, 'c'),
    ('trail0', 3, 352, 484, 543, 572, 'c'), ('trail1', 3, 588, 475, 788, 572, 'c'),
    ('circle0', 4, 152, 17, 300, 118, 'c'), ('circle1', 4, 325, 24, 484, 124, 'c'), ('circle2', 4, 505, 1, 658, 121, 'c'),
    ('glaze0', 5, 156, 376, 309, 452, 'c'), ('glaze1', 5, 352, 355, 569, 461, 'c'), ('glaze2', 5, 588, 355, 795, 461, 'c'),
    ('snow0', 8, 155, 365, 435, 572, 'c'), ('snow1', 8, 442, 365, 728, 572, 'c'), ('snow2', 8, 734, 365, 1019, 572, 'c'),
]


def unblend(rgb):
    # 흰 배경 위에 섞인 색 → (색, 불투명도). 가장 진한 채널이 얼마나 흰색에서 떨어졌는지로 불투명도를 정함
    a = ((255 - rgb.min(axis=2)) / 140).clip(0, 1)
    a = np.where(a < 0.06, 0, a)
    out = np.where(a[..., None] > 0, (rgb - 255 * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0)
    return out.clip(0, 255), a


def main(folder):
    sheets, cells = {}, []
    for name, sh, x0, y0, x1, y1, anc in PIECES:
        if sh not in sheets: sheets[sh] = np.array(Image.open(f'{folder}/{sh}.webp').convert('RGB')).astype(float)
        rgb, a = unblend(sheets[sh][y0:y1, x0:x1])
        if name.startswith('snow'):  # 판이 네모로 잘려 있어서 가장자리를 부드럽게 지움
            h, w = a.shape
            ry = np.minimum(np.arange(h), np.arange(h)[::-1])[:, None] / 24
            rx = np.minimum(np.arange(w), np.arange(w)[::-1])[None, :] / 24
            a *= np.minimum(1, np.minimum(ry, rx))
        im = Image.fromarray(np.dstack([rgb * a[..., None], a * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
        im = im.resize((max(1, round((x1 - x0) * SC)), max(1, round((y1 - y0) * SC))), Image.LANCZOS)
        p = np.array(im).astype(float)
        p[..., :3] = np.where(p[..., 3:] > 0, p[..., :3] * 255 / np.maximum(p[..., 3:], 1), 0)
        cells.append((name, p.clip(0, 255).astype(np.uint8), anc))
    H = max(c[1].shape[0] for c in cells)
    W = sum(c[1].shape[1] + 2 for c in cells)
    sheet = np.zeros((H, W, 4), np.uint8)
    x, table = 0, []
    for name, p, anc in cells:
        h, w = p.shape[:2]
        sheet[:h, x:x + w] = p
        table.append(f"{name}: [{x},0,{w},{h},{w // 2},{h // 2 if anc == 'c' else h - 1}]")
        x += w + 2
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(', '.join(table))


if __name__ == '__main__':
    main(sys.argv[1])

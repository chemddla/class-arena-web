# 빙결술사 이펙트 그림(흰 배경 도트 그림) → 한 줄 시트 (원래 크기, 빈 가장자리는 잘라 냄)
# 사용: python tools/dfreeze_fx_build.py <그림 6장 png를 순서대로>   → assets/sprites/fx/dfreeze_fx.webp (동결 스킬)
#       python tools/dfreeze_fx_build.py blizzard <그림 3장 png: 눈바람·눈꽃·시전 끝 충격>     → assets/sprites/fx/blizzard_cast_fx.webp
#  1 시전 소용돌이+물방울 · 2 시전 바닥 얼음 가시 고리 · 3 발동 때 터지는 얼음 큐브 · 4 빙결 큐브 · 5 금 간 큐브 · 6 부서진 조각
import sys, numpy as np
from PIL import Image

OUT = 'assets/sprites/fx/dfreeze_fx.webp'
NAMES = ['swirl', 'ring', 'burst', 'cube', 'crack', 'shard']


def unblend(rgb):
    a = ((255 - rgb.min(axis=2)) / 140).clip(0, 1)
    a = np.where(a < 0.06, 0, a)
    out = np.where(a[..., None] > 0, (rgb - 255 * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0)
    return out.clip(0, 255), a


def main(paths):
    global OUT, NAMES
    if paths[0] == 'blizzard':
        OUT, NAMES, paths = 'assets/sprites/fx/blizzard_cast_fx.webp', ['wind', 'flake', 'burst'], paths[1:]
    cells = []
    for p in paths:
        c, a = unblend(np.array(Image.open(p).convert('RGB')).astype(float))
        ys, xs = np.where(a > 0)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        cells.append(np.dstack([c[y0:y1, x0:x1] * a[y0:y1, x0:x1, None], a[y0:y1, x0:x1] * 255]).clip(0, 255).astype(np.uint8))
    H = max(c.shape[0] for c in cells)
    W = sum(c.shape[1] + 2 for c in cells)
    sheet = np.zeros((H, W, 4), np.uint8)
    x, table = 0, []
    for name, p in zip(NAMES, cells):
        h, w = p.shape[:2]
        q = p.astype(float)
        q[..., :3] = np.where(q[..., 3:] > 0, q[..., :3] * 255 / np.maximum(q[..., 3:], 1), 0)
        sheet[:h, x:x + w] = q.clip(0, 255).astype(np.uint8)
        table.append(f"{name}: [{x},0,{w},{h}]")
        x += w + 2
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(', '.join(table))


if __name__ == '__main__':
    main(sys.argv[1:])

# 주술사 [저주의 늪] 장판 샘플(초록 배경, 한 줄 5칸) → assets/sprites/fx/curse_swamp_fx.webp
# 사용: python tools/curse_swamp_fx_build.py [샘플 png]  (기본 assets/sprites/fx/samples/curse_swamp_fx_src.png)
# 칸: 0 검은 기운이 퍼짐 · 1 가시 솟은 늪 · 2 가시·거품 늪 · 3·4 해골이 떠오르는 늪
# 마지막 칸 늪 안의 ✦ 워터마크는 주변 늪 색으로 메움
# 프레임 [x, y, w, h, 기준점x, 기준점y] (기준점 = 늪 타원 가운데: 바닥에서 POOL_HALF만큼 위)
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = 'assets/sprites/fx/curse_swamp_fx.webp'
COLS = [(8, 201), (218, 406), (417, 613), (624, 818), (828, 1020)]
POOL_HALF = 38
MARK = (968, 990, 80, 102)  # ✦ (x0, x1, y0, y1)


def main(path):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    bright = (g > 150) & (g - np.maximum(r, b) > 50)
    key = np.median(im[bright], axis=0)
    d = np.sqrt(((im - key) ** 2).sum(axis=2))
    a = np.where(bright, np.clip((d - 45) / 150, 0, 1), 1.0)
    al = np.maximum(a, 1e-3)[..., None]
    rgb = np.where(a[..., None] < 1, key + (im - key) / al, im).clip(0, 255)
    rgb[..., 1] = np.minimum(rgb[..., 1], np.maximum(rgb[..., 0], rgb[..., 2]))  # 보라·검정뿐이라 초록 번짐은 모두 지움
    x0, x1, y0, y1 = MARK
    ring = np.zeros(a.shape, bool); ring[y0 - 3:y1 + 3, x0 - 3:x1 + 3] = True; ring[y0:y1, x0:x1] = False
    rgb[y0:y1, x0:x1] = np.median(rgb[ring], axis=0); a[y0:y1, x0:x1] = 1
    tiles = []
    for c0, c1 in COLS:
        ca = a[:, c0:c1].copy()
        m = ca > 0.05
        lab, n = ndi.label(m)
        areas = ndi.sum(m, lab, range(1, n + 1))
        ca = np.where(np.isin(lab, 1 + np.where(areas >= 8)[0]), ca, 0)  # 압축 티끌
        ys, xs = np.where(ca > 0.05)
        t = np.dstack([rgb[:, c0:c1], ca * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8)
        tiles.append((t, t.shape[1] / 2, t.shape[0] - 1 - POOL_HALF))
    W = sum(t.shape[1] + 2 for t, _, _ in tiles); H = max(t.shape[0] for t, _, _ in tiles)
    atlas = np.zeros((H, W, 4), np.uint8); x = 0; frames = []
    for t, ax, ay in tiles:
        atlas[:t.shape[0], x:x + t.shape[1]] = t
        frames.append(f'[{x},0,{t.shape[1]},{t.shape[0]},{round(ax)},{round(ay)}]')
        x += t.shape[1] + 2
    Image.fromarray(atlas, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('[' + ', '.join(frames) + ']')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/fx/samples/curse_swamp_fx_src.png')

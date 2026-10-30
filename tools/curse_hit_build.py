# 주술사 피격 이펙트 샘플(초록 배경) 2장 → assets/sprites/fx/curse_hit_fx.webp (가로로 이어 붙인 아틀라스)
# 사용: python tools/curse_hit_build.py [샘플 폴더]  (기본 assets/sprites/fx/samples)
#   orb = curse_orb_hit_src.png  기본 공격 불꽃이 맞았을 때 보라 폭발
#   hex = curse_hex_hit_src.png  저주 해골이 맞았을 때 해골 폭발. 오른쪽 테두리에 잘린 줄기들은 지움
# 프레임 [x, y, w, h, 기준점x, 기준점y] (기준점 = 폭발 가운데)
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = 'assets/sprites/fx/curse_hit_fx.webp'
# (이름, 파일, 잘라낼 곳 (가운데x, 가운데y, 가로 반지름, y0, y1) — y0~y1 줄에서 타원 바깥 오른쪽을 지움, 폭발 가운데)
SRC = [
    ('orb', 'curse_orb_hit_src.png', None, None),
    ('hex', 'curse_hex_hit_src.png', (66, 82, 52, 58, 143), (70, 78)),  # 위쪽 붉은 가시는 남기고 잘린 줄기 높이만, 구름 가장자리는 둥글게
]


def cut(path, xcut, center):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    bright = (g > 150) & (g - np.maximum(r, b) > 50)
    key = np.median(im[bright], axis=0)
    d = np.sqrt(((im - key) ** 2).sum(axis=2))
    a = np.where(bright, np.clip((d - 45) / 150, 0, 1), 1.0)
    if xcut is not None:
        cx, cy, rx, y0, y1 = xcut
        yy, xx = np.mgrid[:a.shape[0], :a.shape[1]]
        out = (yy >= y0) & (yy < y1) & (xx > cx) & (((xx - cx) / rx) ** 2 + ((yy - cy) / 72) ** 2 > 1)
        a[out] = 0
        # 새로 잘린 가장자리에 원래 그림처럼 어두운 테두리 1px
        edge = (a > 0.5) & ndi.binary_dilation(out, iterations=1)
        im[edge] = [34, 16, 40]; a[edge] = 1
    m = a > 0.05
    lab, n = ndi.label(m)
    areas = ndi.sum(m, lab, range(1, n + 1))
    a = np.where(np.isin(lab, 1 + np.where(areas >= 8)[0]), a, 0)  # 압축 티끌
    al = np.maximum(a, 1e-3)[..., None]
    rgb = np.where(a[..., None] < 1, key + (im - key) / al, im).clip(0, 255)
    rgb[..., 1] = np.minimum(rgb[..., 1], np.maximum(rgb[..., 0], rgb[..., 2]))  # 보라·검정뿐이라 테두리 초록 번짐은 모두 지움
    ys, xs = np.where(a > 0.05)
    rgba = np.dstack([rgb, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8)
    cx, cy = center if center else ((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2)
    return rgba, round(cx - xs.min()), round(cy - ys.min())


def main(folder):
    tiles = [(nm,) + cut(f'{folder}/{fn}', xc, c) for nm, fn, xc, c in SRC]
    W = sum(t.shape[1] + 2 for _, t, _, _ in tiles); H = max(t.shape[0] for _, t, _, _ in tiles)
    atlas = np.zeros((H, W, 4), np.uint8); x = 0; frames = []
    for nm, t, ax, ay in tiles:
        atlas[:t.shape[0], x:x + t.shape[1]] = t
        frames.append(f'{nm}: [{x},0,{t.shape[1]},{t.shape[0]},{ax},{ay}]')
        x += t.shape[1] + 2
    Image.fromarray(atlas, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('{ ' + ', '.join(frames) + ' }')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/fx/samples')

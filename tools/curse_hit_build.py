# 주술사 피격 이펙트 샘플(초록 배경) 2장 → assets/sprites/fx/curse_hit_fx.webp (가로로 이어 붙인 아틀라스)
# 사용: python tools/curse_hit_build.py [샘플 폴더]  (기본 assets/sprites/fx/samples)
#   orb = curse_orb_hit_src.png  기본 공격 불꽃이 맞았을 때 보라 폭발
#   hex = curse_hex_hit_src.webp 저주 해골이 맞았을 때 해골 폭발 (오른쪽 아래 ✦ 워터마크 지움)
#   sip = curse_sip_hit_src.png  흡혼에 맞은 적 발밑에서 솟는 보라 불길 (기준점 = 바닥 가운데)
# 프레임 [x, y, w, h, 기준점x, 기준점y] (기준점 = 폭발 가운데, sip만 바닥 가운데)
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = 'assets/sprites/fx/curse_hit_fx.webp'
SCALE = {'hex': 0.155}  # 큰 샘플은 다른 그림과 비슷한 크기(약 140px)로 줄임
# (이름, 파일, 지울 곳 (x0, y0) — x0부터 오른쪽 끝, y0부터 아래 끝까지, 폭발 가운데)
SRC = [
    ('orb', 'curse_orb_hit_src.png', None, None),
    ('hex', 'curse_hex_hit_src.webp', (860, 860), (520, 540)),  # ✦ 워터마크. 1024px 샘플이라 아래 SCALE로 줄임
    ('sip', 'curse_sip_hit_src.png', None, 'bottom'),
]


def cut(path, xcut, center):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    bright = (g > 150) & (g - np.maximum(r, b) > 50)
    key = np.median(im[bright], axis=0)
    d = np.sqrt(((im - key) ** 2).sum(axis=2))
    a = np.where(bright, np.clip((d - 45) / 150, 0, 1), 1.0)
    if xcut is not None: a[xcut[1]:, xcut[0]:] = 0
    m = a > 0.05
    lab, n = ndi.label(m)
    areas = ndi.sum(m, lab, range(1, n + 1))
    a = np.where(np.isin(lab, 1 + np.where(areas >= 8)[0]), a, 0)  # 압축 티끌
    al = np.maximum(a, 1e-3)[..., None]
    rgb = np.where(a[..., None] < 1, key + (im - key) / al, im).clip(0, 255)
    rgb[..., 1] = np.minimum(rgb[..., 1], np.maximum(rgb[..., 0], rgb[..., 2]))  # 보라·검정뿐이라 테두리 초록 번짐은 모두 지움
    ys, xs = np.where(a > 0.05)
    rgba = np.dstack([rgb, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8)
    if center == 'bottom': cx, cy = (xs.min() + xs.max()) / 2, ys.max()
    else: cx, cy = center if center else ((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2)
    return rgba, round(cx - xs.min()), round(cy - ys.min())


def main(folder):
    tiles = []
    for nm, fn, xc, c in SRC:
        t, ax, ay = cut(f'{folder}/{fn}', xc, c)
        if nm in SCALE:
            sc = SCALE[nm]
            pm = t.astype(float); pm[..., :3] *= pm[..., 3:] / 255
            sm = np.array(Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((round(t.shape[1] * sc), round(t.shape[0] * sc)), Image.BOX)).astype(float)
            sm[..., :3] = np.where(sm[..., 3:] > 0, sm[..., :3] * 255 / np.maximum(sm[..., 3:], 1), 0)
            t, ax, ay = sm.clip(0, 255).astype(np.uint8), round(ax * sc), round(ay * sc)
        tiles.append((nm, t, ax, ay))
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

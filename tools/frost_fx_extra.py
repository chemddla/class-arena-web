# 프리즈용 추가 얼음 그림을 frost_fx.webp 끝에 이어 붙임 (이미 붙어 있으면 건너뜀)
# 사용: python tools/frost_fx_extra.py <스케이팅 파편·줄기 그림 3장 png> <비스듬한 가시 3장 png>
#  - 두 그림 모두 흰 배경 도트 시트(2배 크기). 흰 배경을 지우고 0.5배로 줄여 칸마다 떼어 냄
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = 'assets/sprites/fx/frost_fx.webp'
SC = 0.5


def unblend(rgb):
    a = ((255 - rgb.min(axis=2)) / 140).clip(0, 1)
    a = np.where(a < 0.06, 0, a)
    out = np.where(a[..., None] > 0, (rgb - 255 * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0)
    return out.clip(0, 255), a


def split(path, n):
    rgb = np.array(Image.open(path).convert('RGB')).astype(float)
    c, a = unblend(rgb)
    cols = ndi.binary_dilation((a > 0).any(axis=0), iterations=7)
    lab, k = ndi.label(cols)
    assert k == n, (path, k)
    out = []
    for i in range(1, k + 1):
        xs = np.where(lab.max(axis=0) == i)[0] if False else np.where(lab == i)[0]
        x0, x1 = xs.min(), xs.max() + 1
        sub = a[:, x0:x1]
        ys = np.where((sub > 0).any(axis=1))[0]
        y0, y1 = ys.min(), ys.max() + 1
        px = np.dstack([c[y0:y1, x0:x1] * a[y0:y1, x0:x1, None], a[y0:y1, x0:x1] * 255]).clip(0, 255).astype(np.uint8)
        im = Image.fromarray(px, 'RGBA').resize((max(1, round((x1 - x0) * SC)), max(1, round((y1 - y0) * SC))), Image.LANCZOS)
        p = np.array(im).astype(float)
        p[..., :3] = np.where(p[..., 3:] > 0, p[..., :3] * 255 / np.maximum(p[..., 3:], 1), 0)
        out.append(p.clip(0, 255).astype(np.uint8))
    return out


def main(skate_png, spike_png):
    base = Image.open(OUT).convert('RGBA')
    cells = [('shard', c, 'c') for c in split(skate_png, 3)[:1]]
    cells += [(f'streak{i}', c, 'l') for i, c in enumerate(split(skate_png, 3)[1:])]
    cells += [(f'dspike{i}', c, 'b') for i, c in enumerate(split(spike_png, 3))]
    H = max(base.height, max(c[1].shape[0] for c in cells))
    W = base.width + sum(c[1].shape[1] + 2 for c in cells) + 2
    sheet = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sheet.paste(base, (0, 0))
    x, table = base.width + 2, []
    for name, p, anc in cells:
        h, w = p.shape[:2]
        sheet.paste(Image.fromarray(p, 'RGBA'), (x, 0))
        ay = {'c': h // 2, 'l': h // 2, 'b': h - 1}[anc]
        ax = {'c': w // 2, 'l': 0, 'b': w // 2}[anc]
        table.append(f"{name}: [{x},0,{w},{h},{ax},{ay}]")
        x += w + 2
    sheet.save(OUT, 'WEBP', lossless=True)
    print(', '.join(table))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

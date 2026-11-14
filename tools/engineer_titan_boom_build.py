# 최종병기 자폭 이펙트 '핵폭발' (2026-11-14 사용자 선택: 후보 2) → assets/sprites/fx/engineer_titan_nuke.webp
# 사용: python tools/engineer_titan_boom_build.py
# 샘플 = pixelfx explosions/nuke 렌더 시트 (assets/sprites/fx/samples/engineer_titan_nuke_src.png + .json, --sheet --bg none --no-actor)
#   - 원래 9초짜리라 0~94칸을 2칸씩 건너 48칸(30fps, 1.6초)으로 빠르게
#   - 박격포 폭발과 같은 정리: 연기는 번져 하나로, 큰 불꽃 덩어리는 불빛으로 메워 하나의 불덩이로,
#     26칸(0.87초) 뒤부터 14칸 동안 불꽃이 사그라들어 버섯구름 연기만 남음 · 마지막 10칸은 흐려짐
#   - 칸이 커서 8칸씩 여러 줄로 놓음 (가로 한 줄이면 그림 폭 한도를 넘음)
#   - 기준점 = 폭발 바닥 가운데 (원본 200, 284)
import json
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

SRC = 'assets/sprites/fx/samples/engineer_titan_nuke_src'
OUT = 'assets/sprites/fx/engineer_titan_nuke.webp'
N, STEP, COLS, OX, OY = 48, 2, 8, 200, 284


def blur(a, mask, rad, boost):
    sm = np.zeros_like(a); sm[mask] = a[mask]; pm = sm.copy(); pm[..., :3] *= pm[..., 3:] / 255
    b = np.array(Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').filter(ImageFilter.GaussianBlur(rad))).astype(float)
    b[..., :3] = np.where(b[..., 3:] > 0, b[..., :3] * 255 / np.maximum(b[..., 3:], 1), 0); b[..., 3] = np.minimum(255, b[..., 3] * boost)
    return b


def merge(f, k):
    fade = max(0.0, min(1.0, 1 - (k - 26) / 14))
    a = np.array(f).astype(float); c = a[..., :3]; al = a[..., 3] > 0; sat = c.max(axis=2) - c.min(axis=2)
    smoke = al & (sat < 40) & (c.max(axis=2) < 225)
    fire = al & (sat >= 40) & (c[..., 0] > 120) & (c[..., 0] >= c[..., 2])
    lab, n = ndi.label(fire, structure=np.ones((3, 3)))
    if n:
        sz = ndi.sum(fire, lab, range(1, n + 1)); fire &= np.isin(lab, 1 + np.where(sz >= 12)[0])
    out = Image.fromarray(blur(a, smoke, 3, 1.25).clip(0, 255).astype(np.uint8), 'RGBA')
    if fire.any() and fade > 0:
        fb = blur(a, fire, 4, 3.5); fb[..., 3] = np.where(fb[..., 3] > 60, np.minimum(255, fb[..., 3] * 1.2), 0) * fade
        out.alpha_composite(Image.fromarray(fb.clip(0, 255).astype(np.uint8), 'RGBA'))
    rest = a.copy(); rest[smoke] = 0
    ember = al & (sat >= 40) & (c[..., 0] > 90) & (c[..., 0] >= c[..., 2]) & ~((c[..., 0] > 200) & (c[..., 1] > 150))
    rest[ember, 3] *= fade
    out.alpha_composite(Image.fromarray(rest.clip(0, 255).astype(np.uint8), 'RGBA'))
    if k >= N - 10:
        o = np.array(out).astype(float); o[..., 3] *= (N - k) / 10; out = Image.fromarray(o.clip(0, 255).astype(np.uint8), 'RGBA')
    return out


def main():
    im = Image.open(SRC + '.png').convert('RGBA')
    js = json.load(open(SRC + '.json', encoding='utf-8'))
    frs = []
    for k in range(N):
        f = js['frames'][k * STEP]['frame']
        frs.append(merge(im.crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h'])), k))
    box = None
    for f in frs:
        b = f.getbbox()
        if b: box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    rows = (N + COLS - 1) // COLS
    sheet = Image.new('RGBA', (w * COLS, h * rows), (0, 0, 0, 0))
    for i, f in enumerate(frs):
        sheet.alpha_composite(f.crop(box), ((i % COLS) * w, (i // COLS) * h))
    sheet.save(OUT, 'WEBP', quality=90, method=6)   # 무손실이면 2.4MB → 손실 90으로 약 1MB (부드러운 폭발 그림이라 차이 거의 없음)
    print(json.dumps({'w': w, 'h': h, 'n': N, 'cols': COLS, 'ox': OX - x0, 'oy': OY - y0}), sheet.size)


if __name__ == '__main__':
    main()

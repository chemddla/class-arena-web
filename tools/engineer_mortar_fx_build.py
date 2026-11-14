# 박격포탑 폭발 이펙트 (2026-11-14 사용자 선택: 후보 2 '불꽃 꼬리 + 수류탄 폭발') → assets/sprites/fx/engineer_mortar_blast.webp
# 사용: python tools/engineer_mortar_fx_build.py
# 샘플 = pixelfx explosions/grenade 렌더 시트 (assets/sprites/fx/samples/engineer_mortar_blast_src.png + .json, --sheet --bg none --no-actor)
#   - 수류탄이 굴러오는 앞부분은 버리고 터지는 칸(49)부터 40칸(30fps, 1.33초)만. 터지는 자리 = (200, 170) (효과 기준점 160이 아님)
#   - 연기(색 없는 회색)는 번지게 해 둥근 덩어리를 하나의 연기로, 큰 불꽃 덩어리는 사이를 불빛으로 메워 하나의 불덩이로
#   - 0.4초(12칸) 뒤부터 0.33초 동안 불꽃이 사그라들어 연기로 넘어감 (식은 붉은 공이 따로 떠다니지 않게), 밝은 노랑 불티는 남김
#   - 폭발 왼쪽 바닥의 붉은 줄(수류탄 심지가 타며 굴러온 자국)은 지움
#   - 마지막 10칸은 흐려짐
# 날아가는 포탄의 불꽃 꼬리는 게임이 포물선을 따라 도트로 그림 (index.html drawEngineerEffect eng_shell)
import json
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

SRC = 'assets/sprites/fx/samples/engineer_mortar_blast_src'
OUT = 'assets/sprites/fx/engineer_mortar_blast.webp'
START, N, CX, CY = 49, 40, 200, 170
FUSE = (0, 168, 163, 999)   # 지울 심지 자국 상자 (x0, x1, y0, y1): 폭발 왼쪽 바닥


def blur_layer(a, mask, rad, boost):
    sm = np.zeros_like(a); sm[mask] = a[mask]
    pm = sm.copy(); pm[..., :3] *= pm[..., 3:] / 255
    b = np.array(Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').filter(ImageFilter.GaussianBlur(rad))).astype(float)
    b[..., :3] = np.where(b[..., 3:] > 0, b[..., :3] * 255 / np.maximum(b[..., 3:], 1), 0)
    b[..., 3] = np.minimum(255, b[..., 3] * boost)
    return b


def merge(f, k):
    a = np.array(f).astype(float)
    c = a[..., :3]; al = a[..., 3] > 0
    sat = c.max(axis=2) - c.min(axis=2)
    x0, x1, y0, y1 = FUSE
    hot = al & (sat >= 40) & (c[..., 0] > 90) & (c[..., 0] >= c[..., 2])
    zone = np.zeros(al.shape, bool); zone[y0:y1, x0:x1] = True
    a[hot & zone] = 0; al = a[..., 3] > 0                         # 심지 자국
    smoke = al & (sat < 40) & (c.max(axis=2) < 225)
    fire = al & (sat >= 40) & (c[..., 0] > 120) & (c[..., 0] >= c[..., 2])
    lab, n = ndi.label(fire, structure=np.ones((3, 3)))
    if n:
        sizes = ndi.sum(fire, lab, range(1, n + 1))
        fire &= np.isin(lab, 1 + np.where(sizes >= 12)[0])
    out = Image.fromarray(blur_layer(a, smoke, 3, 1.25).clip(0, 255).astype(np.uint8), 'RGBA')
    fade = max(0.0, min(1.0, 1 - (k - 12) / 10))
    if fire.any() and fade > 0:
        fb = blur_layer(a, fire, 4, 3.5)
        fb[..., 3] = np.where(fb[..., 3] > 60, np.minimum(255, fb[..., 3] * 1.2), 0) * fade
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
        f = js['frames'][START + k]['frame']
        frs.append(merge(im.crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h'])), k))
    # 모든 칸을 덮는 상자로 자름
    box = None
    for f in frs:
        b = f.getbbox()
        if b: box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sheet = Image.new('RGBA', (w * N, h), (0, 0, 0, 0))
    for i, f in enumerate(frs):
        sheet.alpha_composite(f.crop(box), (i * w, 0))
    sheet.save(OUT, 'WEBP', lossless=True)
    a0 = np.array(frs[3])[..., 3] > 40; ys, xs = np.where(a0)
    print(json.dumps({'w': w, 'h': h, 'n': N, 'ox': CX - x0, 'oy': CY - y0, 'r0': round((xs.max() - xs.min()) / 2)}))


if __name__ == '__main__':
    main()

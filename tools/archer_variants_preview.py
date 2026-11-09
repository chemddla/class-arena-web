# 궁수 새 기본 외형(archer_0, 2026-11-09 금발 궁수) 외형 1~5 후보 미리보기 — 피부는 그대로, 나머지 채도·명도만 바꿈 (화염술사 외형 1~5와 같은 방식)
# 사용: python tools/archer_variants_preview.py masks <경로>    → 피부로 잡힌 곳 (빨강) 확인
#       python tools/archer_variants_preview.py preview <경로>  → 후보마다 대기 칸 크게 + 여러 칸 줄
# 색상(hue)은 그대로라 금발·초록 망토·갈색 가죽의 조합은 같고, 바랜/어두운/무채 같은 느낌만 달라짐.
# 눈 흰자·눈동자 하이라이트는 피부와 함께 그대로 둠
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

sys.path.insert(0, 'tools')
from frost_variants_build import rgb2hsv, hsv2rgb

SRC = 'assets/sprites/merc/archer_0.webp'
CW, N = 214, 14
SHOW = [0, 1, 5, 13, 10, 11, 7, 9]   # 줄에 보일 칸: 대기·걷기·공격·쏜 뒤·화살비·회피·피격·쓰러짐
# (이름, 채도 배율, 명도 배율)
VARIANTS = [
    ('원본', 1.0, 1.0),
    ('A 바랜 들판', 0.55, 1.08),
    ('B 어스름', 0.5, 0.72),
    ('C 짙은 숲', 0.9, 0.6),
    ('D 그림자', 0.3, 0.42),
    ('E 무채 은회', 0.08, 1.0),
    ('F 선명', 1.35, 1.04),
    ('G 파스텔', 0.4, 1.2),
    ('H 먹빛', 0.05, 0.55),
]


def skin_mask(im):
    hsv = rgb2hsv(im[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    al = im[..., 3] > 200
    # 핵심 살색: 밝고 연한 살구색 (금발은 색조 40° 이상·채도가 높아서 빠짐)
    core = al & (h >= 8) & (h <= 34) & (s >= 0.1) & (s <= 0.42) & (v > 0.78)
    lab, n = ndimage.label(core)
    sizes = ndimage.sum(core, lab, range(1, n + 1))
    keep = np.isin(lab, np.where(sizes >= 3)[0] + 1)
    # 머리띠의 밝은 줄(살색과 비슷한 가로 2px 이하 띠)은 피부가 아님
    for k, sl in enumerate(ndimage.find_objects(lab)):
        if sl and sl[0].stop - sl[0].start <= 2 and sl[1].stop - sl[1].start >= 4: keep[lab == k + 1] = False
    # 살 그림자·하이라이트는 핵심 살색에 이어진 것만
    broad = al & (((h <= 36) | (h >= 345)) & (s <= 0.5) & (v > 0.6) | (v > 0.96) & (s < 0.12))
    grown = ndimage.binary_propagation(keep, mask=broad | keep)
    # 눈: 얼굴 상자 안 작은 구멍(흰자·초록 눈동자 빛점)은 그대로
    holes = ndimage.binary_fill_holes(grown) & ~grown
    hl, hn = ndimage.label(holes)
    hs = ndimage.sum(holes, hl, range(1, hn + 1))
    eyes = np.isin(hl, np.where(hs <= 6)[0] + 1) & (v > 0.85) & (s < 0.2)
    return grown | eyes | eye_whites(im, grown, h, s, v)


def eye_whites(im, skin, h, s, v):
    # 흰자: 칸마다 얼굴(가장 큰 살색 덩어리) 상자 안에서 초록 눈동자 둘레 2px의 밝은 무채색 → 어느 후보든 그대로 흰색
    al = im[..., 3] > 200
    out = np.zeros_like(skin)
    for i in range(im.shape[1] // CW):
        sl = (slice(None), slice(i * CW, (i + 1) * CW))
        lab, n = ndimage.label(skin[sl])
        if not n: continue
        big = np.argmax(ndimage.sum(skin[sl], lab, range(1, n + 1))) + 1
        ys, xs = np.where(lab == big)
        box = np.zeros(skin[sl].shape, bool)
        box[max(0, ys.min() - 2):ys.max() + 1, max(0, xs.min() - 3):xs.max() + 4] = True
        iris = box & al[sl] & (h[sl] >= 75) & (h[sl] <= 170) & (s[sl] > 0.2)
        out[sl] = box & ndimage.binary_dilation(iris, iterations=2) & al[sl] & (s[sl] < 0.22) & (v[sl] > 0.6)
    return out


def tone(im, skin, sat, val):
    hsv = rgb2hsv(im[..., :3] / 255.)
    m = (im[..., 3] > 0) & ~skin
    s0, v0 = hsv[..., 1].copy(), hsv[..., 2].copy()
    hsv[..., 1] = np.where(m, np.clip(s0 * sat, 0, 1), s0)
    # 어둡게 할 때 금발·밝은 하이라이트는 조금 덜 어둡게 (노랑이 어두워지면 탁한 올리브가 됨)
    glow = np.clip((v0 - 0.75) / 0.2, 0, 1) * np.clip((s0 - 0.3) / 0.3, 0, 1)
    k = val + (1 - val) * glow * 0.5 if val < 1 else np.full_like(v0, val)
    hsv[..., 2] = np.where(m, np.clip(v0 * k, 0, 1), v0)
    out = im.copy()
    out[m, :3] = (hsv2rgb(hsv)[m] * 255 + .5).clip(0, 255).astype(np.uint8)
    return out


def font(sz):
    for f in ('C:/Windows/Fonts/malgun.ttf', 'C:/Windows/Fonts/gulim.ttc'):
        try: return ImageFont.truetype(f, sz)
        except OSError: pass
    return ImageFont.load_default()


def on_bg(rgba, bg=(74, 96, 74)):
    b = Image.new('RGBA', (rgba.shape[1], rgba.shape[0]), bg + (255,))
    b.alpha_composite(Image.fromarray(rgba, 'RGBA'))
    return b


def masks(path):
    im = np.array(Image.open(SRC).convert('RGBA'))
    sk = skin_mask(im)
    vis = im.copy(); vis[sk] = [255, 0, 0, 255]
    cells = [on_bg(np.hstack([im[:, i * CW:(i + 1) * CW], vis[:, i * CW:(i + 1) * CW]])) for i in SHOW]
    out = Image.new('RGB', (cells[0].width * 2, cells[0].height * ((len(cells) + 1) // 2)))
    for i, c in enumerate(cells): out.paste(c, ((i % 2) * c.width, (i // 2) * c.height))
    out.resize((out.width * 2, out.height * 2), Image.NEAREST).save(path)


def crop_cell(arr, i, pad=8):
    c = arr[:, i * CW:(i + 1) * CW]
    xs = np.where(c[..., 3].any(axis=0))[0]
    return c[:, max(0, xs.min() - pad):xs.max() + pad + 1]


def preview(path):
    im = np.array(Image.open(SRC).convert('RGBA'))
    sk = skin_mask(im)
    H = im.shape[0]; big = 3
    rows = []
    for name, sat, val in VARIANTS:
        rc = tone(im, sk, sat, val)
        idle = on_bg(crop_cell(rc, 0)).resize((crop_cell(rc, 0).shape[1] * big, H * big), Image.NEAREST)
        strip = [on_bg(crop_cell(rc, i)) for i in SHOW[1:]]
        sw = sum(s.width for s in strip) + 6 * len(strip)
        row = Image.new('RGB', (idle.width + 20 + sw * 2, H * big + 34), (36, 40, 48))
        d = ImageDraw.Draw(row)
        d.text((10, 4), f'{name}  (채도 ×{sat}, 명도 ×{val})', fill=(240, 240, 240), font=font(20))
        row.paste(idle, (10, 32))
        x = idle.width + 24
        for s_ in strip:
            row.paste(s_.resize((s_.width * 2, H * 2), Image.NEAREST), (x, 32 + (H * big - H * 2)))
            x += s_.width * 2 + 6
        rows.append(row)
    W = max(r.width for r in rows)
    out = Image.new('RGB', (W, sum(r.height for r in rows)), (36, 40, 48))
    y = 0
    for r in rows: out.paste(r, (0, y)); y += r.height
    out.save(path)
    print(path, out.size)


if __name__ == '__main__':
    mode, p = sys.argv[1], sys.argv[2]
    {'masks': masks, 'preview': preview}[mode](p)

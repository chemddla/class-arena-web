# 마법사 새 기본 외형(mage_0, 11칸) 색 조합 후보 미리보기 — 외형 1~5 샘플 제작 참고용 (게임 시트를 만드는 도구 아님)
# 사용: python tools/mage0_palette_preview.py masks <경로>    → 칸마다 부위 나눈 결과 (색 표시)
#       python tools/mage0_palette_preview.py preview <경로>  → 후보마다 대기 칸 크게 + 11칸 줄
# 부위는 칸마다 색으로 나눔 (윤곽·피부·입·볼은 그대로):
#   로브 = 파랑(모자·로브) · 장식 = 보라(모자 띠·망토 안감·치마, 눈동자 포함) · 머리 = 밝은 무채색(은발)
#   금장식 = 노랑 · 가죽 = 갈색(지팡이·허리띠·부츠) · 수정 = 하늘색(수정·스킬 소용돌이)
# 색 바꾸기: 부위마다 (색조, 채도 배율, 명도 배율, 무채색에 더할 채도). 색조는 부위 가운데 색조로 옮기고 원래 색조 차이는 반만 남김
#   → 명암 계단(그늘·빛)은 그대로라 도트 느낌 유지
import sys, colorsys
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont

SRC = 'assets/sprites/merc/mage_0.webp'
CW, N = 172, 11
NAMES = ['대기', '걷기A', '대기', '걷기B', '공격1', '공격2', '스킬1', '스킬2', '피격', '쓰러짐1', '쓰러짐2']
PART_COLORS = {'robe': (40, 90, 255), 'trim': (190, 60, 255), 'hair': (230, 230, 230), 'gold': (255, 210, 0),
               'leather': (140, 80, 30), 'crystal': (0, 255, 255), 'eyew': (255, 0, 0)}

# (이름, {부위: (색조°, 채도 배율, 명도 배율, 더할 채도)}) — 없는 부위는 그대로
VARIANTS = [
    ('원본 (은발·파랑)', {}),
    ('칠흑 (검은 로브·진홍 장식·붉은 수정)', {'robe': (245, 0.22, 0.62, 0), 'trim': (352, 1.0, 1.05, 0), 'crystal': (352, 1.0, 1.0, 0)}),
    ('진홍 (붉은 로브·검은 장식·금발)', {'robe': (356, 0.95, 0.95, 0), 'trim': (300, 0.25, 0.55, 0), 'hair': (44, 1, 1.0, 0.38), 'crystal': (38, 1.1, 1.05, 0)}),
    ('에메랄드 (초록 로브·청록 장식)', {'robe': (150, 0.85, 0.88, 0), 'trim': (182, 0.9, 1.0, 0), 'crystal': (125, 1.0, 1.0, 0), 'hair': (160, 1, 1.0, 0.1)}),
    ('새벽 (연하늘 로브·분홍 장식·분홍 머리)', {'robe': (205, 0.45, 1.18, 0), 'trim': (330, 0.75, 1.15, 0), 'hair': (335, 1, 1.0, 0.22), 'crystal': (325, 0.9, 1.05, 0)}),
    ('순백 (흰 로브·금빛 장식·금발)', {'robe': (220, 0.1, 1.38, 0), 'trim': (44, 0.95, 1.2, 0), 'hair': (46, 1, 1.02, 0.3), 'crystal': (48, 1.0, 1.08, 0)}),
    ('심해 (짙은 남색·하늘 장식)', {'robe': (232, 1.05, 0.62, 0), 'trim': (192, 0.95, 1.12, 0), 'hair': (205, 1, 0.98, 0.12)}),
]


def load():
    im = np.array(Image.open(SRC).convert('RGBA')).astype(float)
    return im


def hsv_arrays(im):
    rgb = im[..., :3] / 255
    flat = rgb.reshape(-1, 3)
    hsv = np.array([colorsys.rgb_to_hsv(*p) for p in flat]).reshape(rgb.shape)
    return hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]


def parts_of(im, h, s, v, cw=CW):
    a = im[..., 3] > 30
    outline = v < 0.17
    col = a & ~outline & (s >= 0.22)
    skin = a & (h >= 5) & (h < 40) & (s < 0.45) & (v > 0.72)
    P = {
        'robe': col & (h >= 205) & (h < 262),
        'trim': col & (h >= 262) & (h < 305),
        'gold': col & (h >= 38) & (h < 65) & (v > 0.5) & ~skin,
        'leather': col & ((h < 38) | (h >= 345)) & ~skin & (v > 0.2),
        'crystal': col & (h >= 170) & (h < 205),
        'hair': (im[..., 3] > 200) & ~outline & (s < 0.22) & (v > 0.35),   # 반투명 테두리(밝은 무채색)는 빼서 윤곽이 물들지 않게
    }
    P['leather'] &= ~(col & (h >= 300) & (v < 0.35))   # 입·볼(어두운 분홍)은 그대로
    # 얼굴: 칸마다 살색 덩어리의 구멍(눈·입)까지 채운 것. 얼굴 안은 눈동자(보라)만 장식색으로 칠하고 흰자·속눈썹은 그대로
    face = np.zeros_like(a)
    eyew = np.zeros_like(a)   # 흰자: 얼굴 상자 안 눈동자(보라) 둘레 3px의 밝은 무채색 — 머리카락과 붙어 있어 머리로 잡히던 것
    for i in range(im.shape[1] // cw):
        sl = (slice(None), slice(i * cw, (i + 1) * cw))
        lab, n = ndi.label(ndi.binary_closing(skin[sl], iterations=2))
        if n:
            big = np.argmax(ndi.sum(skin[sl], lab, range(1, n + 1))) + 1
            fc = ndi.binary_fill_holes(lab == big)
            face[sl] = fc
            ys, xs = np.where(fc)
            box = np.zeros_like(fc); box[ys.min():ys.max() + 1, max(0, xs.min() - 3):xs.max() + 4] = True
            iris = box & col[sl] & (h[sl] >= 240) & (h[sl] < 305)
            eyew[sl] = box & ndi.binary_dilation(iris, iterations=3) & a[sl] & ~outline[sl] & (s[sl] < 0.3) & (v[sl] > 0.7) & ~skin[sl]
    for k in P: P[k] &= ~(face | eyew)
    P['eyew'] = eyew
    # 수정의 짙은 파랑 그늘·흰 빛점은 로브·머리 색 범위에 들어 얼룩이 됨 → 하늘색 수정 둘레 2px 안의 로브·머리 픽셀은 수정으로
    near = ndi.binary_dilation(P['crystal'], iterations=2)
    for k in ('robe', 'hair'):
        moved = P[k] & near
        P[k] &= ~moved; P['crystal'] |= moved
    P['trim'] |= face & col & (h >= 240) & (h < 305)   # 눈동자
    return P


def recolor(im, h, s, v, P, spec):
    out = im.copy()
    ew = P['eyew']
    out[..., :3][ew] = (v[ew] * 255)[:, None]   # 흰자는 어느 후보든 무채색 흰색 (밝기만 남김)
    for k, m in P.items():
        if k not in spec or not m.any(): continue
        th, ks, kv, add = spec[k]
        hm = np.median(h[m])
        dh = ((h[m] - hm + 180) % 360) - 180
        dh = np.where(s[m] < 0.15, 0, np.clip(dh * 0.5, -12, 12))   # 거의 무채색 픽셀은 색조가 들쭉날쭉해서 차이를 버림 (안 그러면 초록·빨강 얼룩)
        nh = ((th + dh) % 360) / 360
        ns = np.clip(s[m] * ks + add, 0, 1)
        nv = np.clip(v[m] * kv, 0, 1)
        rgb = np.array([colorsys.hsv_to_rgb(a_, b_, c_) for a_, b_, c_ in zip(nh, ns, nv)]) * 255
        out[..., :3][m] = rgb
    return out


def font(sz):
    for f in ('C:/Windows/Fonts/malgun.ttf', 'C:/Windows/Fonts/gulim.ttc'):
        try: return ImageFont.truetype(f, sz)
        except OSError: pass
    return ImageFont.load_default()


def on_bg(rgba, bg=(74, 96, 74)):
    b = Image.new('RGBA', (rgba.shape[1], rgba.shape[0]), bg + (255,))
    b.alpha_composite(Image.fromarray(rgba.clip(0, 255).astype(np.uint8), 'RGBA'))
    return b


def masks(path):
    im = load(); h, s, v = hsv_arrays(im); P = parts_of(im, h, s, v)
    vis = np.zeros_like(im); vis[..., 3] = (im[..., 3] > 30) * 255; vis[..., :3] = 60
    for k, m in P.items(): vis[..., :3][m] = PART_COLORS[k]
    sc = 3
    top = on_bg(im).resize((im.shape[1] * sc // 2, im.shape[0] * sc // 2), Image.NEAREST)
    bot = on_bg(vis, (20, 20, 20)).resize(top.size, Image.NEAREST)
    out = Image.new('RGB', (top.width, top.height * 2)); out.paste(top, (0, 0)); out.paste(bot, (0, top.height))
    out.save(path)


def preview(path):
    im = load(); h, s, v = hsv_arrays(im); P = parts_of(im, h, s, v)
    big, small = 3, 1
    fh = im.shape[0]
    rowh = fh * big + 26
    W = CW * big + CW * N * small // 1 + 40
    sheet = Image.new('RGB', (max(W, 900), rowh * len(VARIANTS) + 10), (36, 40, 48))
    d = ImageDraw.Draw(sheet); f = font(18)
    for r, (name, spec) in enumerate(VARIANTS):
        rc = recolor(im, h, s, v, P, spec)
        y = 10 + r * rowh
        d.text((12, y), f'{r}. {name}', fill=(240, 240, 240), font=f)
        idle = on_bg(rc[:, :CW]).resize((CW * big, fh * big), Image.NEAREST)
        sheet.paste(idle, (10, y + 24))
        strip = on_bg(rc).resize((im.shape[1] * small, fh * small), Image.NEAREST)
        # 11칸 줄은 두 줄로 접어서 (대기 확대 옆)
        half = (N + 1) // 2 * CW * small
        sheet.paste(strip.crop((0, 0, half, fh)), (CW * big + 24, y + 24))
        sheet.paste(strip.crop((half, 0, strip.width, fh)), (CW * big + 24, y + 24 + fh + 8))
    sheet.save(path)


if __name__ == '__main__':
    mode, path = sys.argv[1], sys.argv[2]
    {'masks': masks, 'preview': preview}[mode](path)

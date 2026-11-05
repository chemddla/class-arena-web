# 소환사 추가 외형 1~5 색조합 후보 미리보기 (대기 칸에 부위별 색을 입힌 리컬러 — 샘플 제작 참고용, 게임 시트를 만드는 도구 아님)
# 사용: python tools/summoner_palette_preview.py docs/summoner-skin-palette.png      (색표: docs/summoner-skin-palette.md)
#       python tools/summoner_palette_preview.py <경로> masks                        → 부위 나누기 확인 그림
# 색 입히기는 픽셀아트 저장소 기법을 따름 (pixel-art-studio scripts/pixelstudio.py ramp · pxl shades):
#   - 부위마다 목표 색 하나로 '색조가 도는 명암 계단'을 만듦: 그림자는 파랑(240°) 쪽, 밝은 곳은 노랑(60°) 쪽으로 최대 HUE_SHIFT°,
#     채도는 중간 밝기에서 가장 높고 밝은 쪽에서 45%까지 빠짐. 계단 가운데 = 목표 색
#   - 원래 픽셀의 밝기가 그 부위 안에서 어디쯤인지(아래 5% ~ 위 95%)를 계단 위 자리로 옮김 → 명암 모양은 그대로, 색만 바뀜
#   - 피부·검은 윤곽·흰자·책 장식 금박은 그대로. 같은 재질은 한 계단(로브·두건, 치마·소매 안감)
# 부위 (대기 칸 기준, 113×106): 머리(화관 위쪽·왼쪽 긴 머리·얼굴 오른쪽 옆머리) · 로브(나머지 초록) · 치마(올리브·갈색 안감)
#   · 금장식(치마 앞 금색 테) · 꽃(화관 장미) · 책 표지 · 눈동자
import sys, colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC = 'assets/sprites/merc/summoner_0.webp'
W, H = 113, 106
HUE_SHIFT = 16.0
SCALE = 4

VARIANTS = [
    (1, '서리꽃 소환사', dict(hair='#d6dfeb', vine='#5f8fa8', robe='#3c6aa4', skirt='#8e9bb0', trim='#d4dce8', flower='#6fbdf0', book='#2b3a68', eyes='#3f9fe0')),
    (2, '노을 불꽃',     dict(hair='#e2643c', vine='#6b5a2a', robe='#962a2c', skirt='#bf9038', trim='#f0c252', flower='#f6c43a', book='#4a2024', eyes='#e09a2a')),
    (3, '달밤 정령술사', dict(hair='#55449a', vine='#3d5a6a', robe='#28325e', skirt='#6c6690', trim='#c6cbe2', flower='#ecedf6', book='#26232f', eyes='#a48cea')),
    (4, '벚꽃 정원',     dict(hair='#f0a4c0', vine='#4f7a3a', robe='#c9b394', skirt='#d48aa8', trim='#e2b862', flower='#d23f7c', book='#e2d8c6', eyes='#d0508a')),
    (5, '가을 숲',       dict(hair='#c0803e', vine='#5a6a2a', robe='#7e3b24', skirt='#c4b088', trim='#b48242', flower='#eab232', book='#2a5c3c', eyes='#4a9a5a')),
]
PARTS = ('hair', 'vine', 'robe', 'skirt', 'trim', 'flower', 'book', 'eyes')


def hexrgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def toward(h, target, amt):
    d = (target - h + 540) % 360 - 180
    return (h + max(-amt, min(amt, d))) % 360


def ramp_color(base, t, dark=0.45, light=0.62):
    """pixelstudio.ramp를 이어지는 값 t(0 어두움 ~ 1 밝음)로: 가운데(0.5) = base"""
    h, s, v = colorsys.rgb_to_hsv(*hexrgb(base)); hd = h * 360
    v_dark = max(0.06, v * (1 - dark)); v_light = min(1.0, v + (1 - v) * light)
    if t < 0.5:
        u = (0.5 - t) * 2
        vv = v + (v_dark - v) * u; hh = toward(hd, 240, u * HUE_SHIFT); ss = min(1.0, s * (1 + 0.25 * u))
    else:
        u = (t - 0.5) * 2
        vv = v + (v_light - v) * u; hh = toward(hd, 60, u * HUE_SHIFT); ss = s * (1 - 0.45 * u)
    return colorsys.hsv_to_rgb(hh / 360, max(0, ss), max(0, min(1, vv)))


def masks(im):
    a = im[..., 3] > 0   # 가장자리 반투명 픽셀까지 (빼면 머리 끝에 원래 회녹색이 남음)
    hsv = np.array([colorsys.rgb_to_hsv(*(p / 255)) for p in im[..., :3].reshape(-1, 3)]).reshape(H, W, 3)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    yy, xx = np.mgrid[0:H, 0:W]
    outline = v < 0.14
    skin = a & (h >= 5) & (h < 40) & (s <= 0.45) & (v > 0.6)
    green = a & (h >= 85) & (h < 195) & (s > 0.08) & ~outline   # 채도 낮은 회녹색(머리 끝·로브 그늘)·청록빛 그늘(185~195)까지
    green |= a & (h >= 70) & (h < 85) & (s > 0.08) & (yy < 40) & ~outline   # 화관 둘레 누런 초록 (치마 올리브와 겹치는 색이라 머리 높이에서만)
    eyebox = (xx >= 57) & (xx <= 74) & (yy >= 38) & (yy <= 48)   # 눈 왼쪽 앞머리(x 54~56)는 머리
    eyes = green & eyebox & (s > 0.12)   # 홍채 아래쪽 흐린 초록까지
    hair = green & ~eyebox & ((yy < 52) | ((xx < 45) & (yy < 80)) | ((xx >= 75) & (xx < 84) & (yy < 62)))
    robe = green & ~hair & ~eyebox
    vine = hair & (yy >= 21) & (yy <= 36) & (xx >= 36) & (xx <= 84) & (v < 0.34) & (h >= 95)   # 화관 덩굴 (머리 위를 가로지르는 짙은 초록 띠)
    hair &= ~vine
    reddish = a & ((h >= 330) | (h < 12)) & (s > 0.35) & ~outline
    bookbox = (xx >= 73) & (yy >= 46) & (yy < 78)
    book = a & ~outline & bookbox & ~skin & (((h < 40) | (h >= 330)) & (s > 0.2))
    bookgold = book & (h >= 28) & (v > 0.5)            # 책 표지 금박 무늬는 그대로
    book &= ~bookgold & (v < 0.5)   # 표지만 (밝은 종이 가장자리는 그대로)
    flower = reddish & (yy < 36)
    warm = a & ~outline & ~skin & ~book & ~bookgold & ~flower & (h >= 12) & (h < 85) & (s > 0.2)
    trim = warm & (s > 0.45) & (v > 0.5)
    skirt = warm & ~trim
    parts = dict(hair=hair, vine=vine, robe=robe, skirt=skirt, trim=trim, flower=flower, book=book, eyes=eyes)
    # 윤곽선 (selout): 검은 윤곽 픽셀은 가장 가까운 부위(2칸 안)의 것으로. 피부·흰자에 붙은 윤곽은 그대로
    from scipy import ndimage as ndi
    line = a & outline
    keys = list(parts)
    dist = np.full((H, W), 99.0); owner = np.full((H, W), -1)
    for i, k in enumerate(keys):
        d = ndi.distance_transform_edt(~parts[k])
        better = d < dist; dist[better] = d[better]; owner[better] = i
    dskin = ndi.distance_transform_edt(~skin)
    lines = {k: line & (owner == i) & (dist <= 2.5) & (dist < dskin) for i, k in enumerate(keys)}
    return parts, v, lines


def recolor(im, parts, val, colors, lines=None):
    out = im.copy()
    for k, m in parts.items():
        c = colors.get(k)
        if c is None or not m.any(): continue
        lo, hi = np.percentile(val[m], 5), np.percentile(val[m], 95)
        t = (val[m] - lo) / max(1e-3, hi - lo)
        cols = np.array([ramp_color(c, x) for x in np.clip(t, 0, 1)])
        # 계단 아래 5%보다 어두운 픽셀(머리카락 결·접힌 선)은 계단 맨 아래 색에서 원래 어두운 만큼 더 어둡게 → 밝은 머리도 결이 뭉개지지 않음
        under = t < 0
        if under.any():
            k_ = np.clip(val[m][under] / max(1e-3, lo), 0.35, 1.0)
            cols[under] = cols[under] * k_[:, None]
        out[m, :3] = cols * 255
        if lines is not None and lines[k].any():
            # 윤곽 픽셀: 그 부위 맨 아래 색의 색조·채도에 원래 어두움 그대로 (pxl selout · pixel-art-studio 'selout' 윤곽)
            hh, ss, vv = colorsys.rgb_to_hsv(*ramp_color(c, 0))
            lv = val[lines[k]]
            nv = np.clip(np.maximum(lv, 0.05) * 1.1, 0.04, vv * 0.45)
            out[lines[k], :3] = np.array([colorsys.hsv_to_rgb(hh, min(1, ss * 0.9 + 0.1), x) for x in nv]) * 255
    return out


def font(sz):
    for f in ('C:/Windows/Fonts/malgunbd.ttf', 'C:/Windows/Fonts/malgun.ttf'):
        try: return ImageFont.truetype(f, sz)
        except Exception: pass
    return ImageFont.load_default()


def main(path, mode=None):
    im = np.array(Image.open(SRC).convert('RGBA'))[:, :W].astype(float)
    parts, val, lines = masks(im)
    if mode == 'masks':
        col = im.copy(); col[..., :3] = col[..., :3] * 0.3 + 255 * 0.7
        for k, c in zip(PARTS, [(230, 40, 40), (120, 255, 120), (30, 150, 50), (240, 190, 0), (255, 120, 0), (230, 0, 230), (40, 60, 230), (0, 200, 220)]):
            col[parts[k], :3] = c
        Image.fromarray(col.astype(np.uint8), 'RGBA').resize((W * 6, H * 6), Image.NEAREST).save(path); return
    cols = [('외형 0 · 지금', im, None)] + [(f'외형 {n} · {name}', recolor(im, parts, val, c, lines), c) for n, name, c in VARIANTS]
    cw, top, sw = W * SCALE, 34, 22
    sheet = Image.new('RGBA', (cw * len(cols), top + H * SCALE + 10 + sw * 2 + 40), (232, 234, 240, 255))
    d = ImageDraw.Draw(sheet); f = font(17); fs = font(11)
    for i, (title, arr, c) in enumerate(cols):
        x0 = i * cw
        if i % 2: d.rectangle([x0, 0, x0 + cw - 1, sheet.size[1]], fill=(222, 225, 233, 255))
        tw = d.textlength(title, font=f); d.text((x0 + (cw - tw) / 2, 8), title, font=f, fill=(30, 34, 48, 255))
        spr = Image.fromarray(arr.astype(np.uint8), 'RGBA').resize((cw, H * SCALE), Image.NEAREST)
        sheet.alpha_composite(spr, (x0, top))
        if c:   # 부위별 계단 (어두움 → 밝음 5단)
            y = top + H * SCALE + 10
            for j, k in enumerate(PARTS):
                cx = x0 + 8 + (j % 4) * (cw - 16) // 4; cy = y + (j // 4) * (sw + 4)
                for st in range(5):
                    r, g, b = ramp_color(c[k], st / 4)
                    d.rectangle([cx + st * 11, cy, cx + st * 11 + 10, cy + 10], fill=(round(r * 255), round(g * 255), round(b * 255), 255))
                d.text((cx, cy + 11), {'hair': '머리', 'vine': '덩굴', 'robe': '로브', 'skirt': '치마', 'trim': '금장식', 'flower': '꽃', 'book': '책', 'eyes': '눈'}[k], font=fs, fill=(60, 64, 80, 255))
    sheet.save(path)
    print('saved', path)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)

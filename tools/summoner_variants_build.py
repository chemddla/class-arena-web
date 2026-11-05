# 소환사 외형 0(summoner_0.webp, 12칸)에서 색 조합 변형 시트 만들기 — 외형 1~5 (칸 구성·크기·기준점 모두 같음)
# 사용: python tools/summoner_variants_build.py                 → assets/sprites/merc/summoner_1~5.webp
#       python tools/summoner_variants_build.py preview <경로>   → 외형 0~5 × 12칸 비교 그림 (칸 아래에 대기 칸을 같이 둔 확대 그림은 'detail <경로> <칸>')
#       python tools/summoner_variants_build.py masks <경로>     → 부위 나누기 확인 그림 (12칸)
# 색·이름은 tools/summoner_palette_preview.py VARIANTS, 색 입히는 법(색조가 도는 명암 계단 · selout 윤곽 · 옷은 고르게 펴서 5단)도 거기 것을 씀.
#   대기 칸 샘플(docs/summoner-skin-palette.png)에서 지적받아 고친 점을 모든 칸에 똑같이 적용:
#   - 얼굴(칸마다 가장 큰 살색 덩어리의 볼록 껍질)은 눈동자 말고 칠하지 않음. 얼굴 안 초록빛 선은 흰자 = 무채색 · 눈 모서리 = 눈동자 그늘 · 머리 경계 = 머리 윤곽 · 속눈썹 = 거의 검은 갈색
#   - 머리와 로브는 둘 다 초록이라 색과 이어짐으로 나눔: 머리 = 정수리(얼굴 위쪽) 초록에서 이어진 밝은 초록(색조 142° 아래, 또는 160° 아래면서 밝음).
#     로브 위로 늘어진 머리 갈래도 이어져 있어 머리, 로브 밝은 주름처럼 따로 떨어진 조각은 로브 → 로브에 머리색 얼룩이 생기지 않음
#   - 화관 덩굴 = 정수리 둘레 짙은 초록 · 장미 = 머리 가까이 빨강 · 책 = 가장 큰 갈색 덩어리(표지만, 금박·종이는 그대로)
#   - 치마·금장식 = 몸통의 올리브·금색 (얼굴·책·화관 근처 빼고). 어느 부위에도 안 든 옷 픽셀(푸른빛 회색 그늘·회색 점)은 둘레에 많은 옷 부위로
#   - 소환 발동 칸의 연둣빛 마법진(밝은 초록·반투명)은 효과라 그대로
import os, sys, colorsys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import ConvexHull

sys.path.insert(0, os.path.dirname(__file__))
import summoner_palette_preview as PP

SRC = 'assets/sprites/merc/summoner_0.webp'
CW, CH, N = 113, 106, 12
NAMES = ['대기', '걷기1', '걷기2', '걷기3', '걷기4', '피격', '쓰러짐1', '쓰러짐2', '쓰러짐3', '공격', '시전', '발동']
K8 = np.ones((3, 3), int)
LYING = {6, 7, 8}
BOOKLESS = {10}       # 시전 칸: 책이 빛나는 종이뿐이라 갈색 표지가 없음 (그늘이 표지로 잡혀 얼룩이 됐음)     # 뒤로 젖히거나 엎드린 칸: 정수리 위치·화관 띠를 얼굴 위쪽으로 잡을 수 없음


def hsv_of(rgb):
    f = rgb.reshape(-1, 3) / 255.0
    out = np.array([colorsys.rgb_to_hsv(*p) for p in f]).reshape(rgb.shape)
    return out[..., 0] * 360, out[..., 1], out[..., 2]


def hull_mask(m, shape):
    ys, xs = np.where(m)
    if len(xs) < 5: return m.copy()
    try: hull = ConvexHull(np.c_[xs, ys].astype(float))
    except Exception: return m.copy()
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    out = np.ones(shape, bool)
    for a_, b_, c_ in hull.equations:
        out &= a_ * xx + b_ * yy + c_ <= 0.5
    return out


def frame_masks(im, f):
    """칸 하나(CH×CW RGBA float)의 부위 마스크·윤곽 마스크"""
    H, W = im.shape[:2]
    a = im[..., 3] > 0
    h, s, v = hsv_of(im[..., :3])
    yy, xx = np.mgrid[0:H, 0:W]
    # 윤곽 = 아주 어두운 픽셀. 단 채도 있는 짙은 초록(망토 깊은 그늘, 밝기 0.07~0.14)은 윤곽이 아니라 옷·머리 (걷기·공격 칸 망토가 원래 초록으로 남던 것)
    darkgreen = a & (h >= 85) & (h < 195) & (s > 0.25) & (v >= 0.07) & (v < 0.14)
    outline = (v < 0.14) & ~darkgreen
    upright = f not in LYING
    skin = a & (h >= 5) & (h < 30) & (s <= 0.5) & (v > 0.6)
    lab, n = ndi.label(skin)
    big = lab == (np.argmax(ndi.sum(skin, lab, range(1, n + 1))) + 1) if n else skin
    face = ndi.binary_dilation(hull_mask(big, (H, W)), iterations=1)
    fy, fx = np.where(big)
    ftop, fbot = fy.min(), fy.max(); fh = max(1, fbot - ftop)
    fcx = fx.mean()
    # 앞머리가 덮는 이마는 얼굴 보호에서 뺌 (얼굴 위 25%)
    guard = face & (yy >= ftop + 0.25 * fh)
    glow = a & (h >= 70) & (h < 170) & ((v > 0.68) | (im[..., 3] < 230)) & (s > 0.15) & (xx >= CW // 2)   # 소환 빛 (밝은 연두·반투명)
    green = a & (h >= 85) & (h < 195) & (s > 0.08) & ~outline & ~glow
    band = (yy >= ftop + 0.30 * fh) & (yy <= ftop + 0.72 * fh)
    eyes = green & ndi.binary_erosion(face, iterations=1) & band & (s > 0.12) & upright
    # 장미: 빨강 덩어리 중 평균 색조가 분홍빛 빨강(345~355°, 0° 기준 -5° 아래)이고 채도 0.5 넘는 것 (덩어리째).
    #   손·목의 붉은 그늘(색조 0~11°, 채도 0.5 아래)은 로브에 닿아 있어도 장미가 아님
    reddish = a & ((h >= 330) | (h < 12)) & (s > 0.35) & ~outline & ~face
    lab, n = ndi.label(reddish, structure=K8)
    flower = np.zeros((H, W), bool)
    hs = np.where(h > 180, h - 360, h)
    for i in range(1, n + 1):
        m = lab == i
        my = np.where(m)[0].mean()
        # 15픽셀 넘고, 서 있는 칸은 얼굴 위쪽 40% 안 (공격 칸 목 아래 옷깃 붉은 그늘이 장미 → 둘레 두건이 덩굴 색이 되던 것)
        if hs[m].mean() < -5 and s[m].mean() > 0.5 and m.sum() >= 15 and (not upright or my < ftop + 0.4 * fh):
            flower |= m
    near_flower = ndi.distance_transform_edt(~flower) <= 6 if flower.any() else np.zeros((H, W), bool)
    green |= a & (h >= 70) & (h < 85) & (s > 0.08) & (((yy < ftop + 0.3 * fh) & upright) | near_flower) & ~outline & ~glow
    # 머리: 정수리(장미 둘레 6칸 · 서 있는 칸은 얼굴 위쪽도) 초록이 씨앗, 밝은 초록으로 이어진 것까지 (누운 칸도 장미 자리로 머리를 찾음)
    seed = green & ~eyes & ~guard & (near_flower | ((yy < ftop + 0.2 * fh) & upright))
    hairish = green & ~eyes & ~guard & ((h < 142) | ((h < 160) & (v >= 0.32)))
    lab, n = ndi.label(seed | hairish, structure=K8)
    keep = np.unique(lab[seed]); keep = keep[keep > 0]
    hair = (seed | hairish) & np.isin(lab, keep)
    # 어두운 한 줄 띠로 끊긴 머리 갈래(쓰러짐 1칸 왼쪽으로 늘어진 머리): 머리에서 3칸 안에 있는 머리색 덩어리(12픽셀 넘고 평균 밝기 0.22 넘음)는 이어 붙임 (두 번)
    for _ in range(2):
        rest = hairish & ~hair
        lab2, n2 = ndi.label(rest, structure=K8)
        near = ndi.binary_dilation(hair, iterations=3)
        for i in np.unique(lab2[near & rest]):
            if i == 0: continue
            m = lab2 == i
            if m.sum() >= 12 and v[m].mean() > 0.22:   # 공격 칸 왼쪽으로 날리는 어두운 머리도
                hair |= m
    robe = green & ~hair & ~eyes & ~guard
    # 머리·로브 경계 잡티 고르기: 둘레 8칸 중 6칸 넘게 다른 쪽이면 그쪽으로 (두 번)
    for _ in range(2):
        nh = ndi.convolve(hair.astype(int), K8, mode='constant') - hair
        nr = ndi.convolve(robe.astype(int), K8, mode='constant') - robe
        to_r = hair & (nr >= 6) & (nh <= 1); to_h = robe & (nh >= 6) & (nr <= 1)
        hair = (hair & ~to_r) | to_h; robe = (robe & ~to_h) | to_r
    # 화관 덩굴: 장미 둘레 5칸 + (서 있는 칸) 정수리 둘레 띠의 짙은 초록. 누운 칸은 장미 둘레만 (띠로 잡으면 머리 대부분이 덩굴이 됨)
    crownband = (yy >= ftop - 14) & (yy <= ftop + 0.15 * fh) & upright
    near5 = ndi.distance_transform_edt(~flower) <= 5 if flower.any() else np.zeros((H, W), bool)
    vine = hair & (crownband | near5) & (v < 0.34) & (h >= 95)
    hair &= ~vine
    # 책: 가장 큰 갈색 덩어리 (표지). 종이·금박은 그 안이라도 그대로
    brown = a & ~outline & ~face & ~skin & ((h < 36) | (h >= 330)) & (s > 0.2) & (v < 0.5) & ~flower
    lab, n = ndi.label(brown, structure=K8)
    book = np.zeros_like(brown)
    if n and f not in BOOKLESS:
        sz = ndi.sum(brown, lab, range(1, n + 1)); i = int(np.argmax(sz))
        if sz[i] >= 40: book = lab == i + 1
    bookarea = ndi.binary_fill_holes(ndi.binary_dilation(book, iterations=2)) if book.any() else book
    bookgold = bookarea & ~book & a & (h >= 25) & (h < 60) & (v > 0.45)
    # 표지 무늬(룬): 표지 안의 밝은 갈색·금색 (색조 18~40°, 채도 0.28 넘고 밝기 0.38 넘음). 원래 갈색으로 두면 초록·남색 표지 위에서 살구색 얼룩 → 외형 금장식 색으로
    rune = bookarea & ~book & a & ~outline & (h >= 18) & (h < 40) & (s >= 0.28) & (v >= 0.38)
    # 치마·금장식: 몸통 올리브·금색 (얼굴·책·화관 근처 빼고)
    head_zone = ndi.distance_transform_edt(~(vine | flower)) <= 3
    pages = a & (h >= 20) & (h < 60) & (v > 0.6) & (s < 0.4)   # 빛나는 책 종이 (시전 칸)·책 종이 가장자리 — 그대로
    if f in BOOKLESS:   # 시전 칸 펼친 책 (오른손 위, x 70~ · y 72 위): 빛나는 밝은 종이는 그대로, 흐린 갈색 표지·그늘은 책 표지 색으로
        bookzone = a & (xx >= 70) & (yy <= 72) & (h >= 10) & (h < 60) & ~skin & ~outline
        cover = bookzone & ~((v > 0.6) & (s < 0.4))
        bookarea = bookarea | bookzone
        pages |= bookzone & ~cover
    warm = a & ~outline & ~skin & ~face & ~bookarea & ~flower & ~head_zone & ~glow & ~pages & (h >= 12) & (h < 85) & (s > 0.2) & ~hair & ~robe & ~vine
    trim = warm & (s > 0.45) & (v > 0.5)
    skirt = warm & ~trim
    castbook = cover if f in BOOKLESS else np.zeros((H, W), bool)   # 시전 칸 빛나는 표지: 책 색, 밝기 범위는 이 칸 것으로 (시트 범위면 계단 맨 밝은 끝에만 놓여 거의 원본처럼 보임)
    parts = dict(hair=hair, vine=vine, robe=robe, skirt=skirt, trim=trim, flower=flower, book=book, eyes=eyes, rune=rune, castbook=castbook)
    # 빈 옷 픽셀 → 둘레에 많은 옷 부위로
    assigned = np.zeros((H, W), bool)
    for m in parts.values(): assigned |= m
    cool = (h >= 185) & (h < 270) & (s > 0.08)
    grayish = (s < 0.1) & (v > 0.3)
    loose = a & ~assigned & ~outline & ~face & ~bookarea & ~glow & (cool | grayish)
    for _ in range(2):
        votes = [ndi.convolve(parts[k].astype(int), K8, mode='constant') for k in ('robe', 'skirt', 'trim')]
        best = np.argmax(votes, axis=0); has = np.max(votes, axis=0) > 0
        for i, k in enumerate(('robe', 'skirt', 'trim')):
            parts[k] |= loose & has & (best == i)
        loose &= ~has
    # 윤곽 (selout)
    line = a & outline
    keys = list(parts)
    dist = np.full((H, W), 99.0); owner = np.full((H, W), -1)
    for i, k in enumerate(keys):
        if not parts[k].any(): continue
        d = ndi.distance_transform_edt(~parts[k])
        better = d < dist; dist[better] = d[better]; owner[better] = i
    dskin = ndi.distance_transform_edt(~skin) if skin.any() else np.full((H, W), 99.0)
    lines = {k: line & (owner == i) & (dist <= 2.5) & (dist < dskin) & (~guard if k != 'eyes' else True) for i, k in enumerate(keys)}
    # 선 모양 어두운 픽셀(밝기 0.22 아래, 투명한 곳과 맞닿았거나 둘레보다 0.15 넘게 어두움) = 실루엣·머리와 로브 경계·옷 주름 선 → 그 부위 윤곽(selout)
    #   짙은 초록을 옷·머리로 넣으면서 이 선들이 밝은 크림 로브·연분홍 머리에서 밝게 칠해져 윤곽이 끊기고 머리와 로브가 한 덩어리로 보이던 것
    near_tr = ndi.binary_dilation(im[..., 3] < 40, structure=K8)
    vmax = ndi.maximum_filter(np.where(a, v, 0.0), size=3)
    edge_dark = (v < 0.22) & ~guard & (near_tr | (vmax - v >= 0.15))
    for k in ('hair', 'vine', 'robe', 'skirt'):
        lines[k] |= parts[k] & edge_dark
    greenish = a & (h >= 70) & (h < 200) & (s > 0.05) & ~glow
    face_px = guard & ~eyes & ~lines['eyes'] & ~skin & (greenish | outline)
    near_eye = ndi.distance_transform_edt(~eyes) <= 2.5 if eyes.any() else np.zeros((H, W), bool)
    near_hair = ndi.distance_transform_edt(~hair) <= 1.5 if hair.any() else np.zeros((H, W), bool)
    lines['white'] = face_px & (v > 0.5)
    lines['eyeshade'] = face_px & ~lines['white'] & near_eye & (v > 0.14)
    lines['hairedge'] = face_px & ~lines['white'] & ~lines['eyeshade'] & near_hair
    lines['face'] = face_px & ~lines['white'] & ~lines['eyeshade'] & ~lines['hairedge']
    return parts, lines, v


def load():
    sheet = np.array(Image.open(SRC).convert('RGBA')).astype(float)
    frames = [sheet[:, i * CW:(i + 1) * CW] for i in range(N)]
    info = [frame_masks(fr, i) for i, fr in enumerate(frames)]
    # 부위별 밝기 범위는 시트 전체로 (칸끼리 같은 색이 같은 계단에 오게)
    rng = {}
    for k in [k for k in info[0][0] if k != 'castbook']:   # castbook은 칸 안 범위 (recolor가 percentile로)
        vals = np.concatenate([inf[2][inf[0][k]] for inf in info if inf[0][k].any()]) if any(inf[0][k].any() for inf in info) else np.array([0.3])
        rng[k] = (np.percentile(vals, 5), np.percentile(vals, 95))
    return sheet, frames, info, rng


def recolor_frame(fr, parts, lines, val, colors, rng):
    colors = dict(colors, rune=colors['trim'], castbook=colors['book'])   # 책 무늬는 외형 금장식 색, 시전 칸 표지는 책 색
    return PP.recolor(fr, parts, val, colors, lines, rng)


def build_all():
    sheet, frames, info, rng = load()
    outs = {}
    for n_, name, c in PP.VARIANTS:
        out = np.concatenate([recolor_frame(frames[i], *info[i], c, rng) for i in range(N)], axis=1)
        outs[n_] = out
    return sheet, outs, info


def save():
    sheet, outs, _ = build_all()
    for n_, out in outs.items():
        p = f'assets/sprites/merc/summoner_{n_}.webp'
        Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA').save(p, 'WEBP', lossless=True)
        print('saved', p)


def on_bg(arr, bg=(200, 205, 215, 255)):
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
    b = Image.new('RGBA', im.size, bg); b.alpha_composite(im); return b


def preview(path, scale=2):
    sheet, outs, _ = build_all()
    rows = [sheet] + [outs[n_] for n_, _, _ in PP.VARIANTS]
    W = sheet.shape[1] * scale; Hh = CH * scale
    img = Image.new('RGBA', (W + 120, Hh * len(rows) + 24), (232, 234, 240, 255))
    d = ImageDraw.Draw(img); f = PP.font(13)
    for i, nm in enumerate(NAMES):
        d.text((120 + i * CW * scale + 4, 4), f'{i} {nm}', font=f, fill=(40, 44, 60, 255))
    labels = ['외형 0'] + [f'{n_} {nm}' for n_, nm, _ in PP.VARIANTS]
    for r, arr in enumerate(rows):
        img.alpha_composite(on_bg(arr).resize((W, Hh), Image.NEAREST), (120, 24 + r * Hh))
        d.text((6, 24 + r * Hh + Hh // 2 - 8), labels[r], font=f, fill=(30, 34, 48, 255))
    img.save(path); print('saved', path)


def detail(path, fi, scale=5):
    """칸 fi를 외형 0~5로, 위에는 그 칸 · 아래에는 대기 칸(0) — 원본·대기와 견주어 보는 확대 그림"""
    sheet, outs, _ = build_all()
    rows = [sheet] + [outs[n_] for n_, _, _ in PP.VARIANTS]
    cw = CW * scale
    img = Image.new('RGBA', (cw * 6, CH * scale * 2 + 8), (255, 255, 255, 255))
    for c, arr in enumerate(rows):
        for r, k in enumerate((fi, 0)):
            img.alpha_composite(on_bg(arr[:, k * CW:(k + 1) * CW]).resize((cw, CH * scale), Image.NEAREST), (c * cw, r * (CH * scale + 8)))
    img.save(path); print('saved', path)


def masks_img(path, scale=3):
    sheet, frames, info, _ = load()
    cols = dict(hair=(230, 40, 40), vine=(120, 255, 120), robe=(30, 150, 50), skirt=(240, 190, 0), trim=(255, 120, 0),
                flower=(230, 0, 230), book=(40, 60, 230), eyes=(0, 200, 220), rune=(255, 255, 0))
    out = []
    for i in range(N):
        fr = frames[i].copy(); fr[..., :3] = fr[..., :3] * 0.3 + 255 * 0.7
        parts, lines, _ = info[i]
        for k, c in cols.items(): fr[parts[k], :3] = c
        for k in ('white', 'eyeshade', 'hairedge', 'face'): fr[lines[k], :3] = (120, 60, 20)
        out.append(fr)
    Image.fromarray(np.concatenate(out, axis=1).astype(np.uint8), 'RGBA').resize((CW * N * scale, CH * scale), Image.NEAREST).save(path)
    print('saved', path)


if __name__ == '__main__':
    import warnings; warnings.filterwarnings('ignore')
    if len(sys.argv) > 1 and sys.argv[1] == 'preview': preview(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == 'detail': detail(sys.argv[2], int(sys.argv[3]))
    elif len(sys.argv) > 1 and sys.argv[1] == 'masks': masks_img(sys.argv[2])
    else: save()

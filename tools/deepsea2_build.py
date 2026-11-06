# 심해족 나머지 샘플 (인어 주술사·사제·창기병·작살 저격수·빙결 인어·세이렌, 먹물 암살·저주 문어, 집게 방패기사, 크라켄 보스)
# → 몸 시트 + 투사체 아틀라스. 첫 4종은 tools/deepsea_build.py
# 사용: python tools/deepsea2_build.py            (모두 만들기)
#       python tools/deepsea2_build.py debug <폴더> [이름...]   (칸 미리보기만)
# 샘플: assets/sprites/monster/samples/<이름>_src.webp
# 배경이 샘플마다 다름 (단색, 체크무늬·격자 칸, 산호·해초가 그려진 바닷속 장면): 칸 테두리에서 어둡고 채도 낮은 색을 모아 배경 색 묶음으로 쓰고,
# 그 색들로 테두리에서 이어진 곳을 지움. 장식 조각은 몸에서 떨어진 조각 거르기·지울 네모로 뺌
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.cluster.vq import kmeans2

sys.path.insert(0, 'tools')
from deepsea_build import unwatermark, WM_FIT, paste, poly_mask  # noqa: E402

S = 'assets/sprites/monster/samples/'


def load(name):
    return np.asarray(Image.open(S + name + '_src.webp').convert('RGB')).astype(float).copy()


def luma(c):
    return c[..., 0] * 0.3 + c[..., 1] * 0.59 + c[..., 2] * 0.11


def palette(c):
    """칸 테두리(3px)의 어둡고 채도 낮은 색들 → 배경 색 묶음 (k-평균 8개)"""
    ring = np.concatenate([c[:3].reshape(-1, 3), c[-3:].reshape(-1, 3), c[:, :3].reshape(-1, 3), c[:, -3:].reshape(-1, 3)])
    sat = ring.max(1) - ring.min(1)
    ring = ring[(sat < 45) & (luma(ring) < 110)]
    np.random.seed(1)
    cent, _ = kmeans2(ring, min(8, len(ring)), minit='++', seed=1)
    return cent


def cut2(im, box, o, wm=None):
    """box 칸을 잘라 배경을 지운 RGBA (칸 좌표). o = 칸 설정"""
    x0, x1, y0, y1 = box
    c = im[y0:y1, x0:x1].copy()
    h, w, _ = c.shape
    pal = palette(c)
    ringpx = np.concatenate([c[:3].reshape(-1, 3), c[:, :3].reshape(-1, 3)])
    fill = pal[np.argmin([np.sqrt(((ringpx - p) ** 2).sum(1)).mean() for p in pal])]   # 테두리에 가장 흔한 배경색
    # 라벨 글자: 네모 안의 밝고 채도 낮은 픽셀(+둘레 1px) → 배경색
    for lx0, lx1, ly0, ly1 in o.get('lab', []):
        sub = (slice(max(0, ly0 - y0), max(0, ly1 - y0)), slice(max(0, lx0 - x0), max(0, lx1 - x0)))
        s = c[sub]
        txt = (luma(s) > o.get('lab_l', 120)) & ((s.max(2) - s.min(2)) < 60)
        txt = ndi.binary_dilation(txt, iterations=2) & ((s.max(2) - s.min(2)) < 70)
        s[txt] = fill
    for ex0, ex1, ey0, ey1 in o.get('erase_r', []):   # 배경색으로 칠할 네모 (글자 줄 등, 샘플 좌표)
        c[max(0, ey0 - y0):max(0, ey1 - y0), max(0, ex0 - x0):max(0, ex1 - x0)] = fill
    for poly in o.get('erase', []):          # 배경색으로 칠할 다각형 (샘플 좌표)
        m = poly_mask(h, w, [(x - x0, y - y0) for x, y in poly])
        c[m] = fill
    d = np.min(np.stack([np.sqrt(((c - p) ** 2).sum(2)) for p in pal]), 0)
    tol = o.get('tol', 14)
    near = d < tol
    if o.get('glow'):   # 배경 위에 번진 옅은 빛(배경보다 조금 밝은 색)도 배경으로
        near |= (d < o["glow"]) & (luma(c) > luma(fill) + 2) & (luma(c) < o.get("glow_l", 255))
    if o.get('warm_glow'):   # 금빛 구슬 둘레에 번진 누런 빛
        L = luma(c)
        near |= (c[..., 0] > c[..., 2] + 3) & (L > 26) & (L < o['warm_glow']) & ((c.max(2) - c.min(2)) < 60)
    if o.get('dark_bg'):   # 장면 배경: 아주 어두운 채도 낮은 곳(바닥 그림자 포함)도 배경 후보
        near |= (luma(c) < o['dark_bg']) & ((c.max(2) - c.min(2)) < 30)
    lab, n = ndi.label(near)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgm = np.isin(lab, list(edge))
    lab2, n2 = ndi.label((d < 7) & ~bgm)
    if n2:
        areas = ndi.sum(np.ones_like(d), lab2, range(1, n2 + 1))
        bgm |= np.isin(lab2, 1 + np.where(areas >= o.get('pocket', 30))[0])
    a = (~bgm).astype(float)
    ring = (~bgm) & ndi.binary_dilation(bgm)
    a[ring] = np.clip((d[ring] - 6) / 28, 0.25, 1)
    for dx0, dx1, dy0, dy1 in o.get('drop', []):
        a[max(0, dy0 - y0):max(0, dy1 - y0), max(0, dx0 - x0):max(0, dx1 - x0)] = 0
    for poly in o.get('drop_poly', []):
        a[poly_mask(h, w, [(x - x0, y - y0) for x, y in poly])] = 0
    for (rx0, rx1, ry0, ry1), kind in o.get('color_drop', []):   # 네모 안에서 특정 색(불꽃·폭발 등)만 지움
        sub = (slice(max(0, ry0 - y0), max(0, ry1 - y0)), slice(max(0, rx0 - x0), max(0, rx1 - x0)))
        s = c[sub]; R, G, B = s[..., 0], s[..., 1], s[..., 2]
        if kind == 'fire':      # 주황·노랑·빨강 불꽃 + 파란 불꽃 (얼음보다 진하고 R이 낮음)
            m = ((R > 150) & (B < 140) & (R > G - 10) & (R - B > 70)) | ((B > 140) & (R < 140) & (B - R > 70) & (G < B))
        elif kind == 'orange':  # 주황 불꽃만 (얼음은 안 건드림)
            m = (R > 95) & (R - B > 45) & (R > G + 15)
        elif kind == 'decor':   # 배경에 그려진 보라·자주 산호 장식 (분홍 지팡이는 B < G라서 안 걸림)
            m = (R > G + 15) & (B > G) & (luma(s) < 100)
        elif kind == 'burst':   # 노랑·빨강 폭발
            m = (R > 150) & (B < 120) & (R - B > 90)
        m = ndi.binary_dilation(m, iterations=1) & ~(((s.max(2) - s.min(2)) < 25) & (luma(s) > 120))
        a[sub][m] = 0
    if wm:
        bx, by, br = wm
        yy, xx = np.mgrid[0:h, 0:w]
        q = (np.abs(xx + x0 - bx) ** 0.8 + np.abs(yy + y0 - by) ** 0.8) / br ** 0.8
        zone = (q > 0.8) & (q < 1.3)
        opened = ndi.binary_opening(a > 0.3, structure=np.ones((3, 3)))
        a[zone & ~opened] = 0
    if o.get('open'):   # 지운 뒤 남은 가는 실선 떼기
        opened = ndi.binary_opening(a > 0.3, structure=np.ones((3, 3)), iterations=o['open'])
        a[(a > 0) & ~ndi.binary_dilation(opened, iterations=1)] = 0
    m = a > 0.3
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    if n:
        areas = ndi.sum(m, lab, range(1, n + 1))
        keep = np.r_[False, areas >= o.get('min', 40)]
        if 'core' in o:   # 몸 가까이(무게중심이 core 네모 안)인 조각만 + 가장 큰 조각
            cx0, cx1, cy0, cy1 = o['core']
            com = ndi.center_of_mass(m, lab, range(1, n + 1))
            for i, (cy, cx) in enumerate(com):
                if not (cx0 <= cx + x0 <= cx1 and cy0 <= cy + y0 <= cy1): keep[i + 1] = False
            keep[1 + int(np.argmax(areas))] = True
        a = np.where(keep[lab], a, 0)
    core = a >= 1
    if core.any():
        _, (iy, ix) = ndi.distance_transform_edt(~core, return_indices=True)
        e = (a > 0) & ~core
        c[e] = c[iy, ix][e] * 0.6 + c[e] * 0.4
    return np.dstack([c, a * 255])


def trim(rgba, ox, oy):
    ys, xs = np.where(rgba[..., 3] > 0)
    return rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1], ox + xs.min(), oy + ys.min()


# ── 샘플별 설정 ──
# cells: 칸 이름 → 설정 { box: (x0, x1, y0, y1), cx: 몸 가운데 x (없으면 불투명 무게중심), lab/drop/... (cut2 참고) }
# order: 시트 칸 순서 (이름 끝 '~' = 좌우반전 칸)
SAMPLES = {}


def cells_of(name):
    cfg = SAMPLES[name]
    im = load(name)
    if 'wm' in cfg:
        bg = np.median(np.concatenate([im[:4].reshape(-1, 3), im[:, :4].reshape(-1, 3)]), 0)
        unwatermark(im, bg, *cfg['wm'])
    wm = WM_FIT.get(id(im))
    out = {}
    for k, o in cfg['cells'].items():
        r = cut2(im, o['box'], {**cfg.get('common', {}), **o}, wm)
        out[k] = trim(r, o['box'][0], o['box'][2])
    if 'fix' in cfg: cfg['fix'](out, im)
    return out, im


def frames_of(name):
    cfg = SAMPLES[name]
    cells, im = cells_of(name)
    frames = []
    for k in cfg['order']:
        flip = k.endswith('~'); k0 = k.rstrip('~')
        r, ox, oy = cells[k0]
        o = cfg['cells'][k0]
        cx = o.get('cx')
        if cx is None:
            wsum = r[..., 3].sum(0)
            cx = ox + (wsum * np.arange(r.shape[1])).sum() / wsum.sum()
        ys = np.where((r[..., 3] > 128).any(1))[0]
        ay = ys.max() + 1 + o.get('dy', 0)
        ax = cx - ox
        if flip: r = r[:, ::-1].copy(); ax = r.shape[1] - ax
        frames.append((r, ax, ay))
    return frames, cells, im


def build(name, show=None):
    cfg = SAMPLES[name]
    frames, cells, im = frames_of(name)
    if 'also' in cfg: frames += frames_of(cfg['also'])[0]   # 다른 샘플 칸을 뒤에 이어 붙임 (크라켄 스킬)
    k = cfg.get('scale', 1)
    if k != 1:
        fr = []
        for r, ax, ay in frames:
            img = Image.fromarray(np.clip(r, 0, 255).astype(np.uint8), 'RGBA')
            img = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
            fr.append((np.asarray(img).astype(float), ax * k, ay * k))
        frames = fr
    L = max(ax for _, ax, _ in frames); R = max(r.shape[1] - ax for r, ax, _ in frames)
    U = max(ay for _, _, ay in frames); D = max(r.shape[0] - ay for r, _, ay in frames)
    cw, ch = int(np.ceil(L + R)) + 2, int(np.ceil(U + D)) + 2
    axp, ayp = int(round(L)) + 1, int(round(U)) + 1
    sheet = Image.new('RGBA', (cw * len(frames), ch))
    for i, (r, ax, ay) in enumerate(frames):
        sheet.alpha_composite(Image.fromarray(np.clip(r, 0, 255).astype(np.uint8), 'RGBA'), (i * cw + int(round(axp - ax)), int(round(ayp - ay))))
    out = f'{show}/{name}.png' if show else f"assets/sprites/monster/{cfg.get('out', name)}.webp"
    sheet.save(out, **({} if show else {'format': 'WEBP', 'quality': 90, 'alpha_quality': 100, 'method': 6}))
    print(f'{out}: cellW {cw}, cellH {ch}, anchor ({axp}, {ayp}), count {len(frames)}, idleH {frames[0][2]:.0f}')
    return sheet, cw, ch, axp, ayp


def preview(name, show):
    """시트를 초록 바탕에 놓고, 아래에 칸을 겹친 그림 (기준점 확인)"""
    sheet, cw, ch, ax, ay = build(name, show)
    n = sheet.width // cw
    out = Image.new('RGBA', (sheet.width, ch * 2 + 4), (90, 140, 90, 255))
    out.alpha_composite(sheet, (0, 0))
    for i in range(n):
        f = sheet.crop((i * cw, 0, (i + 1) * cw, ch))
        out.alpha_composite(Image.blend(Image.new('RGBA', f.size), f, 0.45), ((i % 3) * cw, ch + 4))
    d = ImageDraw.Draw(out)
    for i in range(n): d.line([(i * cw, 0), (i * cw, ch)], fill=(255, 255, 255))
    for j in range(3): d.line([(j * cw + ax, ch + 4), (j * cw + ax, 2 * ch + 4)], fill=(255, 0, 0))
    d.line([(0, ch + 4 + ay), (3 * cw, ch + 4 + ay)], fill=(255, 0, 0))
    out.save(f'{show}/pv_{name}.png')


B = lambda x0, x1, y0, y1, **k: {'box': (x0, x1, y0, y1), **k}
STD = ['idle', 'walk_a', 'walk_b', 'atk_a', 'atk_b', 'hurt', 'death_a', 'death_b']

# 인어 작살 저격수 (작살총·안대): 회색 단색 배경, 라벨은 왼쪽에 따로
SAMPLES['merfolk_sniper'] = {
    'cells': {
        'idle': B(225, 440, 10, 200), 'walk_a': B(225, 445, 205, 400), 'walk_b': B(460, 760, 205, 400),
        'atk_a': B(215, 445, 405, 600), 'atk_b': B(480, 765, 405, 600), 'hurt': B(215, 430, 605, 800),
        'death_a': B(215, 435, 810, 1004), 'death_b': B(440, 765, 860, 1010),
    },
    'order': STD,
}
# 먹물 암살 문어 (복면·단검 두 자루)
SAMPLES['octopus_rogue'] = {
    'wm': (662, 921, 20.5),
    'common': {'pocket': 10 ** 9},   # 몸 무늬가 배경색과 가까워 '갇힌 배경' 찾기는 끔
    'cells': {
        'idle': B(20, 240, 110, 320), 'walk_a': B(285, 475, 110, 320), 'walk_b': B(530, 745, 110, 320),
        'atk_a': B(15, 245, 420, 640), 'atk_b': B(255, 525, 420, 640), 'hurt': B(525, 750, 415, 640, min=20),
        'death_a': B(90, 330, 730, 955), 'death_b': B(400, 710, 795, 955),
    },
    'order': STD,
}
# 세이렌 가수 (분홍 머리·하프·마이크): 작은 그림. 공격 칸 앞 음파는 투사체 siren_wave로 따로
SAMPLES['merfolk_bard'] = {
    'cells': {
        'idle': B(270, 400, 38, 195), 'walk_a': B(130, 300, 252, 388), 'walk_b': B(385, 570, 252, 388),
        'atk_a': B(75, 345, 425, 598, erase_r=[(270, 420, 415, 449)], drop=[(278, 345, 460, 560)], min=15),
        'atk_b': B(395, 660, 425, 598, erase_r=[(395, 420, 415, 449)], drop=[(590, 660, 460, 560)], min=15),
        'hurt': B(280, 410, 652, 802, erase_r=[(280, 400, 645, 658)]),
        'death_a': B(120, 262, 815, 995), 'death_b': B(365, 640, 870, 995),
    },
    'order': STD,
}
# 인어 창기병 (투구·소라 뿔창·해마): 라벨이 칸 위에 붙어 있음
SAMPLES['merfolk_lancer'] = {
    'wm': (595, 912, 20),
    'cells': {
        'idle': B(30, 215, 35, 252), 'walk_a': B(255, 450, 35, 255), 'walk_b': B(480, 655, 35, 252),
        'walk_c': B(35, 245, 285, 505, lab=[(120, 255, 280, 296)]),
        'atk_a': B(405, 640, 285, 505, lab=[(460, 640, 280, 296)]),
        'atk_b': B(35, 330, 528, 762, lab=[(90, 275, 528, 556)]),
        'hurt': B(395, 620, 518, 758, lab=[(460, 550, 518, 552)]),
        'death_a': B(35, 330, 790, 1018, lab=[(100, 250, 790, 803)]), 'death_b': B(365, 672, 840, 1020),
    },
    'order': ['idle', 'walk_a', 'walk_b', 'walk_c', 'atk_a', 'atk_b', 'hurt', 'death_a', 'death_b'],
}
# 인어 사제 (초록 망토·산호 지팡이·금빛 구슬): 걷기 두 칸이 겹쳐 그려져 있어 몸 가까운 조각만 남김.
# 공격 칸 앞 금빛 빛줄기는 투사체 healer_light로, 피격 칸 뒤 큰 폭발 그림은 지움
SAMPLES['merfolk_healer'] = {
    'wm': (722, 915, 20.5),
    'cells': {
        'idle': B(15, 285, 20, 292, warm_glow=105, glow=32), 'walk_a': B(285, 582, 25, 292, core=(290, 560, 0, 1024)), 'walk_b': B(550, 822, 25, 295, core=(575, 822, 0, 1024), drop=[(550, 600, 25, 295)]),
        'atk_a': B(0, 282, 375, 652, core=(0, 262, 0, 1024), warm_glow=125, glow=40, drop=[(240, 282, 590, 652)]), 'atk_b': B(222, 560, 375, 652, core=(240, 560, 0, 1024), drop=[(452, 560, 440, 560)]),
        'hurt': B(555, 822, 375, 652, color_drop=[((555, 665, 420, 652), 'burst'), ((700, 822, 478, 652), 'burst')], open=1),
        'death_a': B(120, 388, 710, 962), 'death_b': B(390, 792, 745, 962),
    },
    'order': STD,
}
# 집게 방패기사 (철 투구·갑옷·가시 조개 방패): 칸 이름·줄 제목 글자가 그림 바로 위아래에 붙어 있음
SAMPLES['crab_knight'] = {
    'cells': {
        'idle': B(300, 485, 25, 212, erase_r=[(325, 440, 192, 215)]),
        'walk_a': B(150, 335, 200, 410, erase_r=[(150, 350, 200, 227), (150, 305, 380, 410)]),
        'walk_b': B(470, 645, 222, 410, erase_r=[(480, 625, 384, 410)]),
        'atk_a': B(120, 320, 405, 616, erase_r=[(120, 400, 405, 436), (125, 318, 590, 616)]),
        'atk_b': B(465, 700, 428, 616, erase_r=[(490, 640, 590, 616)]),
        'hurt': B(285, 490, 612, 802, erase_r=[(285, 321, 612, 648), (325, 475, 778, 805)]),
        'death_a': B(115, 345, 812, 1012, erase_r=[(115, 405, 812, 834), (145, 305, 990, 1015)], lab=[(255, 310, 832, 842)]),
        'death_b': B(410, 715, 856, 1012, erase_r=[(490, 645, 990, 1012)]),
    },
    'order': STD,
}
# 심해 빙결 인어 (얼음 왕관·얼음 삼지창): 칸 테두리선 있음. 공격 칸 앞 얼음 창 다발은 투사체 frost_lance로.
# 피격 칸 옆의 주황·파랑 불꽃은 빙결 인어와 안 맞는 잘못 그려진 것이라 지움
SAMPLES['merfolk_frost'] = {
    'cells': {
        'idle': B(40, 300, 40, 248), 'walk_a': B(370, 680, 40, 248), 'walk_b': B(740, 1012, 40, 248),
        'atk_a': B(40, 300, 292, 502, lab=[(170, 330, 262, 296)], min=12, glow=120, glow_l=95),
        'atk_b': B(525, 1012, 292, 502, lab=[(690, 845, 262, 296)], drop=[(796, 1012, 300, 480)], glow=120, glow_l=95),
        'hurt': B(40, 320, 548, 762, lab=[(120, 210, 518, 552)], color_drop=[((212, 300, 640, 718), 'fire'), ((185, 250, 580, 700), 'orange')],
                  drop_poly=[[(238, 588), (305, 588), (305, 718), (204, 718), (214, 650), (231, 615)]], open=1, min=150),
        'death_a': B(370, 680, 548, 762, lab=[(445, 575, 518, 552)]), 'death_b': B(720, 1020, 560, 762),
    },
    'order': STD,
}
# 저주 먹물 문어 (해골 투구·뼈 지팡이·보라 기운): 칸마다 체크무늬 바탕과 테두리. 공격 칸 앞 보라 탄은 투사체 curse_ink로
SAMPLES['octopus_curse'] = {
    'wm': (943, 600, 20),
    'common': {'tol': 16, 'pocket': 10 ** 9},
    'cells': {
        'idle': B(12, 248, 62, 330), 'walk_a': B(262, 505, 62, 330), 'walk_b': B(520, 762, 62, 330), 'atk_a': B(778, 1016, 62, 330),
        'atk_b': B(10, 312, 405, 672, core=(10, 246, 400, 660), drop=[(196, 312, 495, 556)]),
        'hurt': B(266, 505, 405, 672, core=(266, 505, 400, 660), drop=[(262, 312, 495, 556)]),
        'death_a': B(520, 762, 405, 672, core=(520, 762, 400, 660)), 'death_b': B(778, 1016, 405, 672, core=(778, 1016, 400, 660)),
    },
    'order': STD,
}
# 인어 주술사 (해초 머리·산호 지팡이): 산호·해초가 그려진 바닷속 장면 배경과 바닥 그림자. 쓰러짐은 한 칸뿐이라 피격 → 쓰러짐으로 씀.
# 공격 칸 앞 물살은 투사체 mage_tide로
SAMPLES['merfolk_mage'] = {
    'wm': (765, 912, 20.5),
    'common': {'dark_bg': 30, 'tol': 16},
    'cells': {
        'idle': B(40, 242, 25, 290), 'walk_a': B(250, 448, 25, 285), 'walk_b': B(450, 642, 25, 285),
        'walk_c': B(640, 852, 25, 285, color_drop=[((815, 852, 150, 285), 'decor')], core=(640, 812, 0, 300)),
        'atk_a': B(95, 330, 350, 628), 'atk_b': B(390, 830, 370, 628, drop=[(655, 830, 430, 545)]),
        'hurt': B(425, 612, 680, 948), 'death': B(640, 852, 720, 955, core=(660, 845, 700, 960), color_drop=[((640, 852, 720, 955), 'decor')]),
    },
    'order': ['idle', 'walk_a', 'walk_b', 'walk_c', 'atk_a', 'atk_b', 'hurt', 'hurt', 'death'],
}
# 크라켄 (심해족 보스, 탑 81~90층): 격자 바탕 위 칸 패널. 동작 샘플 + 스킬 샘플 (회전공격·지진·강타·포이즌 붐·사자후 한 칸씩)
SAMPLES['kraken_tower'] = {
    'common': {'tol': 15, 'pocket': 10 ** 9},
    'cells': {
        'idle': B(15, 262, 82, 302), 'walk_a': B(278, 522, 82, 302), 'walk_b': B(538, 800, 82, 302),
        'atk_a': B(78, 348, 340, 562), 'atk_b': B(425, 772, 340, 562), 'hurt': B(65, 348, 590, 802),
        'death_a': B(445, 748, 598, 802), 'death_b': B(436, 752, 855, 992),
    },
    'order': STD,
    'also': 'kraken_tower_skill',
}
SAMPLES['kraken_tower_skill'] = {
    'skip': True,   # kraken_tower 시트 뒤에 붙음
    'wm': (912, 690, 20.5),
    'common': {'tol': 15, 'pocket': 10 ** 9},
    'cells': {
        'spin': B(18, 338, 92, 368), 'quake': B(340, 706, 88, 388), 'smash': B(704, 1008, 92, 382),
        'poison': B(52, 488, 438, 722), 'roar': B(572, 964, 438, 718),
    },
    'order': ['spin', 'quake', 'smash', 'poison', 'roar', 'spin~'],
}

# 투사체 (공격 칸에서 떼어 냄). 이름 → (샘플, 네모, 추가 설정). 기준점 = 앞(오른쪽) 끝 가운데
FX = {
    'light': ('merfolk_healer', (446, 562, 450, 552), {'warm_glow': 125, 'glow': 40}),            # 인어 사제 금빛 빛줄기
    'tide':  ('merfolk_mage', (652, 830, 425, 548), {}),               # 인어 주술사 물살
    'lance': ('merfolk_frost', (797, 1000, 318, 472), {'min': 6, 'glow': 120, 'glow_l': 95}),     # 심해 빙결 인어 얼음 창 다발
    'ink':   ('octopus_curse', (214, 314, 492, 558), {}),             # 저주 먹물 문어 보라 탄
    'wave':  ('merfolk_bard', (278, 346, 455, 565), {'min': 6}),       # 세이렌 음파
}
OUT_FX = 'assets/sprites/fx/deepsea2_fx.webp'


def build_fx(show=None):
    pieces = []
    ims = {}
    for k, (name, box, extra) in FX.items():
        if name not in ims:
            im = load(name)
            if 'wm' in SAMPLES[name]:
                bg = np.median(np.concatenate([im[:4].reshape(-1, 3), im[:, :4].reshape(-1, 3)]), 0)
                unwatermark(im, bg, *SAMPLES[name]['wm'])
            ims[name] = im
        o = {**SAMPLES[name].get('common', {}), **extra}
        o.pop('core', None)
        r, _, _ = trim(cut2(ims[name], box, o), 0, 0)
        pieces.append((k, r))
    W = sum(p.shape[1] + 2 for _, p in pieces); H = max(p.shape[0] for _, p in pieces)
    sheet = Image.new('RGBA', (W, H)); x = 0; anims = {}
    for k, p in pieces:
        sheet.alpha_composite(Image.fromarray(np.clip(p, 0, 255).astype(np.uint8), 'RGBA'), (x, 0))
        h, w = p.shape[:2]
        ys = np.where(p[:, -max(4, w // 8):, 3].max(1) > 100)[0]
        anims[k] = [x, 0, w, h, w - 1, round(float(ys.mean()), 1)]
        x += w + 2
    out = f'{show}/deepsea2_fx.png' if show else OUT_FX
    sheet.save(out, **({} if show else {'format': 'WEBP', 'quality': 92, 'alpha_quality': 100, 'method': 6}))
    print(out, anims)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        if sys.argv[3:] == ['fx']: build_fx(sys.argv[2])
        else:
            for n in (sys.argv[3:] or [k for k in SAMPLES if not SAMPLES[k].get('skip')]): preview(n, sys.argv[2])
    else:
        for n in SAMPLES:
            if not SAMPLES[n].get('skip'): build(n)
        build_fx()

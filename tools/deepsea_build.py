# 심해족 일반 몬스터 샘플(남색 배경 · 라벨 · ✦ 워터마크) → 몸 시트 + 투사체 아틀라스
# 사용: python tools/deepsea_build.py   (debug 인자를 주면 칸 미리보기만 scratch에 저장)
# 샘플: assets/sprites/monster/samples/{crab_warrior,merfolk_archer,octopus_archer,octopus_mage}_src.webp
# 결과: assets/sprites/monster/{crab_warrior,merfolk_archer,octopus_archer,octopus_mage}.webp, assets/sprites/fx/deepsea_fx.webp
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

S = 'assets/sprites/monster/samples/'


def load(name):
    return np.asarray(Image.open(S + name + '_src.webp').convert('RGB')).astype(float)


def wm_cover(cx, cy, r, x0, y0, w, h, ss=4):
    """✦ 모양 |dx|^0.8+|dy|^0.8 <= r^0.8 이 픽셀을 덮는 비율 (4×4 부분 표본)"""
    o = (np.arange(ss) + 0.5) / ss - 0.5
    yy, xx = np.mgrid[0:h, 0:w]
    cov = np.zeros((h, w))
    for dy in o:
        for dx in o:
            cov += (np.abs(xx + x0 + dx - cx) ** 0.8 + np.abs(yy + y0 + dy - cy) ** 0.8) <= r ** 0.8
    return cov / ss / ss


def unwatermark(im, bg, cx, cy, r, k=0.31):
    """✦ 워터마크 = 흰색 k 겹침. 가운데·크기·세기를 배경 픽셀에 맞춰 조금씩 찾아 맞춘 뒤,
    덮인 비율만큼 겹침을 되돌림 (테두리 반쯤 덮인 픽셀도 그 비율로)"""
    R = int(r * 1.6) + 3
    x0, y0 = int(cx) - R, int(cy) - R
    win = im[y0:y0 + 2 * R, x0:x0 + 2 * R]
    h, w, _ = win.shape
    sat = win.max(2) - win.min(2)
    use = (sat < 16) & (win.mean(2) < 125) & (win.mean(2) > 18)   # 배경 또는 배경 위 워터마크

    def fix(c, kk):
        kc = (kk * c)[..., None]
        return (win - kc * 255) / (1 - kc)

    def err(px, py, rr, kk):
        f = fix(wm_cover(px, py, rr, x0, y0, w, h), kk)
        return np.minimum(np.sqrt(((f - bg) ** 2).sum(2)), 30)[use].sum()

    best = (err(cx, cy, r, k), cx, cy, r, k)
    for step in (1.0, 0.5, 0.25):
        improved = True
        while improved:
            improved = False
            _, bx, by, br, bk = best
            for nx, ny, nr, nk in [(bx + step, by, br, bk), (bx - step, by, br, bk), (bx, by + step, br, bk), (bx, by - step, br, bk),
                                   (bx, by, br + step / 2, bk), (bx, by, br - step / 2, bk), (bx, by, br, bk + 0.01 * step), (bx, by, br, bk - 0.01 * step)]:
                e = err(nx, ny, nr, nk)
                if e < best[0] - 1e-6: best = (e, nx, ny, nr, nk); improved = True
    _, bx, by, br, bk = best
    print("wm", round(bx,2), round(by,2), round(br,2), round(bk,3), file=sys.stderr)
    win[:] = np.clip(fix(wm_cover(bx, by, br, x0, y0, w, h), bk), 0, 255)
    # 테두리에 남은 가는 회색·검은 실선 (배경 근처 색, 채도 낮음) → 배경
    yy, xx = np.mgrid[0:h, 0:w]
    q = (np.abs(xx + x0 - bx) ** 0.8 + np.abs(yy + y0 - by) ** 0.8) / br ** 0.8
    sat = win.max(2) - win.min(2)
    d = np.sqrt(((win - bg) ** 2).sum(2))
    win[(q > 0.9) & (q < 1.15) & (sat < 22) & (d < 50)] = bg
    WM_FIT[id(im)] = (bx, by, br)
    return im


WM_FIT = {}


def cut(im, bg, box, drop=(), keep_min=40, bgtol=16, wm=None):
    """box = (x0, x1, y0, y1) 칸을 잘라 배경을 지운 RGBA. 테두리에서 배경색(거리 < bgtol)으로 이어진 곳 + 갇힌 순수 배경 덩어리 = 배경.
    drop = 지울 네모(샘플 좌표), keep_min = 남길 조각 최소 넓이"""
    x0, x1, y0, y1 = box
    c = im[y0:y1, x0:x1]
    d = np.sqrt(((c - bg) ** 2).sum(2))
    near = d < bgtol
    lab, n = ndi.label(near)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgm = np.isin(lab, list(edge))
    lab2, n2 = ndi.label((d < 6) & ~bgm)
    if n2:
        areas = ndi.sum(np.ones_like(d), lab2, range(1, n2 + 1))
        bgm |= np.isin(lab2, 1 + np.where(areas >= 30)[0])
    a = (~bgm).astype(float)
    # 배경에 닿은 가장자리만 부드럽게
    ring = (~bgm) & ndi.binary_dilation(bgm)
    a[ring] = np.clip((d[ring] - 8) / 30, 0.25, 1)
    for dx0, dx1, dy0, dy1 in drop:
        a[max(0, dy0 - y0):max(0, dy1 - y0), max(0, dx0 - x0):max(0, dx1 - x0)] = 0
    if wm:   # 워터마크 테두리 자리에 붙어 남은 가는 실선은 열림 연산으로 떼어 냄
        bx, by, br = wm
        h, w = a.shape
        yy, xx = np.mgrid[0:h, 0:w]
        q = (np.abs(xx + x0 - bx) ** 0.8 + np.abs(yy + y0 - by) ** 0.8) / br ** 0.8
        zone = (q > 0.8) & (q < 1.3)
        opened = ndi.binary_opening(a > 0.3, structure=np.ones((3, 3)))
        a[zone & ~opened] = 0
    m = a > 0.3
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    if n:
        areas = ndi.sum(m, lab, range(1, n + 1))
        keep = np.r_[False, areas >= keep_min]
        a = np.where(keep[lab], a, 0)
    # 가장자리 색은 안쪽 색으로 (남색 테두리 번짐 줄이기)
    core = a >= 1
    if core.any():
        _, (iy, ix) = ndi.distance_transform_edt(~core, return_indices=True)
        edge_px = (a > 0) & ~core
        c = c.copy()
        c[edge_px] = c[iy, ix][edge_px] * 0.6 + c[edge_px] * 0.4
    return np.dstack([c, a * 255])


def trim(rgba, ox, oy):
    ys, xs = np.where(rgba[..., 3] > 0)
    return rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1], ox + xs.min(), oy + ys.min()


def paste(dst, src, x, y, mask=None):
    """dst 위에 src(RGBA)를 (x, y)에 알파 합성. mask = src 크기의 bool (붙일 부분)"""
    s = src.copy()
    if mask is not None: s[..., 3] *= mask
    h, w = s.shape[:2]
    D = dst[y:y + h, x:x + w]
    sa, da = s[..., 3:] / 255, D[..., 3:] / 255
    oa = sa + da * (1 - sa)
    rgb = np.where(oa > 0, (s[..., :3] * sa + D[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6), 0)
    D[..., :3], D[..., 3:] = rgb, oa * 255


def poly_mask(h, w, pts):
    from PIL import ImageDraw
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
    return np.asarray(m) > 127


# 칸: 이름 → (x0, x1, y0, y1)   (샘플 좌표, 라벨 줄은 빼고)
SAMPLES = {
    'crab_warrior': {
        'wm': (662.5, 921, 20.6),
        'cells': {
            'idle': (0, 262, 0, 280), 'walk_a': (262, 515, 0, 280), 'walk_b': (515, 765, 0, 280),
            'atk_a': (0, 270, 335, 628), 'atk_b': (270, 525, 335, 628), 'hurt': (525, 765, 335, 628),
            'death_a': (0, 360, 690, 968), 'death_b': (360, 765, 690, 968),
        },
    },
    'merfolk_archer': {
        'wm': (662.5, 921, 20.6),
        'cells': {
            'idle': (0, 259, 0, 287), 'walk_a': (259, 522, 0, 287), 'walk_b': (522, 765, 0, 287),
            'atk_a': (0, 258, 335, 642), 'atk_b': (258, 542, 335, 642), 'hurt': (542, 765, 335, 642),
            'death_a': (0, 357, 735, 972), 'death_b': (357, 765, 735, 972),
        },
    },
    'octopus_archer': {
        'wm': (922, 663, 20.6),
        'cells': {
            'idle': (0, 345, 0, 233), 'walk_a': (345, 700, 0, 233), 'walk_b': (700, 1024, 0, 233),
            'atk_a': (0, 345, 268, 496), 'atk_b': (345, 700, 268, 496), 'hurt': (700, 1024, 268, 496),
            'death_a': (0, 420, 528, 726), 'death_b': (420, 1024, 528, 726),
        },
        'drop': {'atk_b': [(632, 700, 268, 496)]},     # 소라 앞 물방울은 투사체로 따로
    },
    'octopus_mage': {
        'wm': (662.5, 921, 20.6),
        'cells': {
            'idle': (0, 265, 0, 275), 'walk_a': (265, 515, 0, 275), 'walk_b': (515, 765, 0, 275),
            'atk_a': (0, 280, 330, 620), 'atk_b': (280, 765, 330, 620), 'hurt': (0, 247, 690, 962),
            'death_a': (247, 485, 690, 962), 'death_b': (485, 765, 690, 962),
        },
        'min': {'idle': 700},                          # 대기 칸 둘레에 흩어진 먹물 방울은 지움
        'drop': {'atk_b': [(570, 765, 330, 620)]},     # 던져서 날아가는 폭탄·궤적 선은 투사체로 따로
    },
}


def cells_of(name):
    cfg = SAMPLES[name]
    im = load(name)
    bg = np.median(np.concatenate([im[:4].reshape(-1, 3), im[-4:].reshape(-1, 3), im[:, :4].reshape(-1, 3)]), 0)
    if 'wm' in cfg: im = unwatermark(im, bg, *cfg['wm'])
    out = {}
    for k, box in cfg['cells'].items():
        rgba = cut(im, bg, box, cfg.get('drop', {}).get(k, ()), keep_min=cfg.get('min', {}).get(k, 40), wm=WM_FIT.get(id(im)))
        out[k] = trim(rgba, box[0], box[2])
    if name in FIXES: FIXES[name](out, im, bg)
    return out, im, bg


def place(cell, layer, lx, ly):
    """cell = (rgba, ox, oy) 위에 layer(RGBA, 왼쪽 위 = 샘플 좌표 (lx, ly))를 덮어 그림. 칸이 모자라면 넓힘"""
    r, ox, oy = cell
    x0, y0 = min(ox, lx), min(oy, ly)
    x1, y1 = max(ox + r.shape[1], lx + layer.shape[1]), max(oy + r.shape[0], ly + layer.shape[0])
    big = np.zeros((y1 - y0, x1 - x0, 4))
    big[oy - y0:oy - y0 + r.shape[0], ox - x0:ox - x0 + r.shape[1]] = r
    paste(big, layer, lx - x0, ly - y0)
    return big, x0, y0


def spear_layer(im, bg):
    """인어 작살수 대기 칸의 작살 (쥔 오른손 포함). 왼손·몸에 가린 자루는 자루 색으로 이어 그림.
    돌려주는 값: (RGBA, 왼쪽 위 x, y, 손 가운데 x, y)  (샘플 좌표)"""
    from PIL import ImageDraw
    x0, x1, y0, y1 = 55, 262, 92, 215
    r = cut(im, bg, (x0, x1, y0, y1))
    h, w = r.shape[:2]
    sh = lambda pts: [(x - x0, y - y0) for x, y in pts]
    R, G, B = r[..., 0], r[..., 1], r[..., 2]
    teal = (G > R + 25) & (B > R + 15)
    parts = poly_mask(h, w, sh([(64, 186), (106, 176), (110, 192), (82, 210), (62, 202)]))           # 꼬리 깃
    parts |= poly_mask(h, w, sh([(121, 164), (166, 138), (182, 128), (186, 160), (171, 157), (126, 182)]))  # 자루·뼈 갈고리
    parts |= poly_mask(h, w, sh([(197, 121), (258, 96), (258, 114), (238, 130), (204, 143)]))        # 촉
    hand = poly_mask(h, w, sh([(178, 127), (203, 121), (210, 148), (196, 166), (178, 161)]))         # 쥔 오른손
    m = (parts & ~teal) | hand
    lay = r.copy(); lay[..., 3] *= m
    # 몸·왼손에 가린 자루 (꼬리 깃 ~ 자루 보이는 곳)
    shaft = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(shaft)
    a, b = (98 - x0, 184 - y0), (128 - x0, 170 - y0)
    d.line([a, b], fill=(28, 24, 26, 255), width=7)
    d.line([a, b], fill=(112, 82, 62, 255), width=3)
    sh_a = np.asarray(shaft).astype(float)
    base = np.zeros_like(lay); paste(base, sh_a, 0, 0); paste(base, lay, 0, 0)
    return base, x0, y0, 192, 143


def fix_merfolk(out, im, bg):
    # 걷기 B·피격 칸은 작살이 빠져 있어서 대기 칸 작살을 오른손 자리에 쥐여 줌 (손 그림째 덮음)
    lay, lx, ly, hx, hy = spear_layer(im, bg)
    for k, (fx, fy) in (('walk_b', (716, 173)), ('hurt', (727, 524))):
        out[k] = place(out[k], lay, lx + fx - hx, ly + fy - hy)


FIXES = {'merfolk_archer': fix_merfolk}


def debug():
    P = sys.argv[2]
    for name in SAMPLES:
        cells, _, _ = cells_of(name)
        W = sum(c[0].shape[1] + 10 for c in cells.values()); H = max(c[0].shape[0] for c in cells.values())
        sheet = Image.new('RGBA', (W, H), (90, 140, 90, 255))
        x = 0
        for k, (r, ox, oy) in cells.items():
            sheet.alpha_composite(Image.fromarray(r.astype(np.uint8), 'RGBA'), (x, 0)); x += r.shape[1] + 10
            print(name, k, r.shape[1], r.shape[0], ox, oy)
        sheet.save(f'{P}/dbg_{name}.png')


# 칸 순서 (모두 오른쪽을 봄): 대기, 걷기 A·B, 공격 준비, 공격, 피격, 쓰러짐 2장 (+ 집게 전사는 공격 좌우반전 = 회전베기용)
ORDER = ['idle', 'walk_a', 'walk_b', 'atk_a', 'atk_b', 'hurt', 'death_a', 'death_b']
# 칸마다 몸 가운데 x (샘플 좌표). 샘플이 3칸 격자로 그려져 있어 격자 가운데를 쓰고, 안 맞는 칸은 따로 맞춤
GRID = {
    'crab_warrior':   {'idle': 131, 'walk_a': 388, 'walk_b': 640, 'atk_a': 136, 'atk_b': 390, 'hurt': 640, 'death_a': None, 'death_b': None},
    'merfolk_archer': {'idle': 127, 'walk_a': 383, 'walk_b': 637, 'atk_a': 127, 'atk_b': 383, 'hurt': 637, 'death_a': None, 'death_b': None},
    'octopus_archer': {'idle': 170, 'walk_a': 512, 'walk_b': 853, 'atk_a': 170, 'atk_b': 512, 'hurt': 853, 'death_a': None, 'death_b': None},
    'octopus_mage':   {'idle': 117, 'walk_a': 383, 'walk_b': 637, 'atk_a': 140, 'atk_b': 395, 'hurt': 127, 'death_a': 383, 'death_b': None},
}


def build(name, show=None):
    cells, im, bg = cells_of(name)
    order = list(ORDER)
    frames = []
    for k in order:
        r, ox, oy = cells[k]
        cx = GRID[name][k]
        if cx is None:
            cols = np.where(r[..., 3].sum(0) > 0)[0]
            w = r[..., 3].sum(0)
            cx = ox + (w * np.arange(r.shape[1])).sum() / w.sum()
        ys = np.where((r[..., 3] > 128).any(1))[0]
        frames.append((r, cx - ox, ys.max() + 1))
    if name == 'crab_warrior':   # 회전베기용 공격 좌우반전
        r, ax, ay = frames[4]
        frames.append((r[:, ::-1].copy(), r.shape[1] - ax, ay)); order.append('atk_b_flip')
    L = max(ax for _, ax, _ in frames); R = max(r.shape[1] - ax for r, ax, _ in frames)
    U = max(ay for _, _, ay in frames); D = max(r.shape[0] - ay for r, _, ay in frames)
    cw, ch = int(np.ceil(L + R)) + 2, int(np.ceil(U + D)) + 2
    axp, ayp = int(round(L)) + 1, int(round(U)) + 1
    sheet = Image.new('RGBA', (cw * len(frames), ch))
    for i, (r, ax, ay) in enumerate(frames):
        sheet.alpha_composite(Image.fromarray(np.clip(r, 0, 255).astype(np.uint8), 'RGBA'), (i * cw + int(round(axp - ax)), int(round(ayp - ay))))
    idle_h = frames[0][2]
    out = f'assets/sprites/monster/{name}.webp'
    if show: out = f'{show}/{name}.png'
    # 원본 샘플이 이미 손실 압축이라 몸 시트는 손실 압축(품질 90, 투명도는 무손실)으로 용량을 1/3로
    sheet.save(out, **({} if show else {'format': 'WEBP', 'quality': 90, 'alpha_quality': 100, 'method': 6}))
    print(f'{out}: cellW {cw}, cellH {ch}, anchor ({axp}, {ayp}), count {len(frames)}, 대기 키 {idle_h}')
    return sheet, cw, ch, axp, ayp


def spear_proj(im, bg):
    """작살 투사체: 대기 칸 작살에서 손을 빼고 자루를 끝까지 이어 그린 뒤 수평으로 눕힘 (촉이 오른쪽)"""
    from PIL import ImageDraw
    x0, x1, y0, y1 = 55, 262, 92, 215
    r = cut(im, bg, (x0, x1, y0, y1))
    h, w = r.shape[:2]
    sh = lambda pts: [(x - x0, y - y0) for x, y in pts]
    R, G, B = r[..., 0], r[..., 1], r[..., 2]
    teal = (G > R + 25) & (B > R + 15)
    parts = poly_mask(h, w, sh([(64, 186), (106, 176), (110, 192), (82, 210), (62, 202)]))
    parts |= poly_mask(h, w, sh([(121, 164), (166, 138), (182, 128), (186, 160), (171, 157), (126, 182)]))
    parts |= poly_mask(h, w, sh([(197, 121), (258, 96), (258, 114), (238, 130), (204, 143)]))
    lay = r.copy(); lay[..., 3] *= parts & ~teal
    shaft = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(shaft)
    a, b = (98 - x0, 184 - y0), (206 - x0, 133 - y0)
    d.line([a, b], fill=(28, 24, 26, 255), width=7)
    d.line([a, b], fill=(112, 82, 62, 255), width=3)
    base = np.zeros_like(lay); paste(base, np.asarray(shaft).astype(float), 0, 0); paste(base, lay, 0, 0)
    ang = np.degrees(np.arctan2(197 - 103, 254 - 68))
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), 'RGBA').rotate(-ang, Image.BICUBIC, expand=True)
    return np.asarray(img).astype(float)


def build_fx(show=None):
    """투사체 아틀라스 deepsea_fx: harpoon(인어 작살수 작살, 기준점 = 촉 끝), squirt(먹물 저격 문어 물방울, 기준점 = 앞 끝),
    bomb(먹물폭탄 문어 폭탄, 기준점 = 폭탄 가운데)"""
    mf = load('merfolk_archer'); bgm = np.median(mf[:4].reshape(-1, 3), 0)
    harpoon, _, _ = trim(spear_proj(mf, bgm), 0, 0)
    oa = load('octopus_archer'); bga = np.median(oa[:4].reshape(-1, 3), 0)
    squirt, _, _ = trim(cut(oa, bga, (630, 700, 340, 410), keep_min=8), 0, 0)
    om = load('octopus_mage'); bgo = np.median(om[:4].reshape(-1, 3), 0)
    bomb, bx, by = trim(cut(om, bgo, (660, 740, 345, 450)), 660, 345)
    pieces = [('harpoon', harpoon), ('squirt', squirt), ('bomb', bomb)]
    W = sum(p.shape[1] + 2 for _, p in pieces); H = max(p.shape[0] for _, p in pieces)
    sheet = Image.new('RGBA', (W, H)); x = 0; anims = {}
    for k, p in pieces:
        sheet.alpha_composite(Image.fromarray(np.clip(p, 0, 255).astype(np.uint8), 'RGBA'), (x, 0))
        h, w = p.shape[:2]
        if k == 'bomb':
            # 폭탄 몸통(검은 공) 가운데: 어두운 픽셀 무게중심
            dark = (p[..., :3].max(2) < 90) & (p[..., 3] > 200)
            yy, xx = np.where(dark)
            ax, ay = round(xx.mean(), 1), round(yy.mean(), 1)
        else:
            ys = np.where(p[:, -3:, 3].max(1) > 100)[0]
            ax, ay = w - 1, round(ys.mean(), 1)
        anims[k] = [x, 0, w, h, ax, ay]
        x += w + 2
    out = f'{show}/deepsea_fx.png' if show else 'assets/sprites/fx/deepsea_fx.webp'
    sheet.save(out, **({} if show else {'format': 'WEBP', 'lossless': True, 'quality': 100, 'method': 6}))
    print(out, anims)


def onion(show):
    """칸을 겹쳐 그려 기준점이 맞는지 보기"""
    for name in SAMPLES:
        sheet, cw, ch, ax, ay = build(name, show)
        n = sheet.width // cw
        bgim = Image.new('RGBA', (cw * 3, ch), (90, 140, 90, 255))
        for i in range(n):
            f = sheet.crop((i * cw, 0, (i + 1) * cw, ch))
            if i < 3: bgim.alpha_composite(Image.blend(Image.new('RGBA', f.size), f, 0.5), (0, 0))
            elif i < 6: bgim.alpha_composite(Image.blend(Image.new('RGBA', f.size), f, 0.5), (cw, 0))
            else: bgim.alpha_composite(Image.blend(Image.new('RGBA', f.size), f, 0.5), (cw * 2, 0))
        from PIL import ImageDraw
        d = ImageDraw.Draw(bgim)
        for j in range(3): d.line([(j * cw + ax, 0), (j * cw + ax, ch)], fill=(255, 0, 0)); d.line([(j * cw, ay), ((j + 1) * cw, ay)], fill=(255, 0, 0))
        bgim.save(f'{show}/onion_{name}.png')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'debug': debug()
    elif len(sys.argv) > 1 and sys.argv[1] == 'onion': onion(sys.argv[2]); build_fx(sys.argv[2])
    else:
        for name in SAMPLES: build(name)
        build_fx()

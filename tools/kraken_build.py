# 심해의 폭군 크라켄 샘플(흰 배경 도트) → 몸 시트 assets/sprites/monster/kraken.webp + 이펙트 assets/sprites/fx/kraken_fx.webp
# 사용: python tools/kraken_build.py
# 샘플: assets/sprites/monster/samples/kraken_*_src.* (몸), assets/sprites/fx/samples/kraken_ink_bomb_fx_src.png · kraken_tsunami_fx_src.png (이펙트)
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

S = 'assets/sprites/monster/samples/'
F = 'assets/sprites/fx/samples/'

# 이름: (파일, x0, x1, y0, y1, 옵션)
# 옵션: flip = 좌우 뒤집기(걷기 샘플은 왼쪽을 봄), lab = 이 y(샘플 좌표)보다 위에만 있는 떨어진 조각은 라벨 글자로 보고 지움,
#       wm = ✦ 워터마크 네모 (회색 픽셀: 몸에 갇힌 건 둘레 몸 색으로 메우고 나머지는 지움),
#       drop = 지울 네모 [(x0, x1, y0, y1)] (샘플 좌표), min = 남길 조각의 최소 넓이(px, 기본 6)
CELLS = {
    'idle_big': (S + 'kraken_idle_src.webp', 90, 924, 0, 572, {}),
    'walk_a':   (S + 'kraken_walk_src.webp', 0, 512, 40, 470, {'flip': True}),
    'walk_b':   (S + 'kraken_walk_src.webp', 512, 1024, 40, 470, {'flip': True}),
    'idle':     (S + 'kraken_walk2_src.png', 0, 244, 0, 120, {}),
    'walk_c':   (S + 'kraken_walk2_src.png', 244, 504, 0, 120, {}),
    'atk_a':    (S + 'kraken_attack_src.png', 0, 362, 30, 189, {}),
    'atk_b':    (S + 'kraken_attack_src.png', 362, 652, 30, 189, {}),
    'hurt':     (S + 'kraken_hurt_src.png', 0, 251, 24, 192, {}),
    'death_a':  (S + 'kraken_death_src.png', 0, 232, 30, 146, {}),
    'death_b':  (S + 'kraken_death_src.png', 232, 480, 30, 146, {}),
    'vortex_a': (S + 'kraken_skill1_src.webp', 0, 236, 64, 292, {}),
    'vortex_b': (S + 'kraken_skill1_src.webp', 236, 512, 64, 292, {}),
    'sweep_a':  (S + 'kraken_skill1_src.webp', 512, 764, 64, 292, {}),
    'sweep_b':  (S + 'kraken_skill1_src.webp', 764, 1024, 64, 292, {}),
    'twist_a':  (S + 'kraken_skill1_src.webp', 0, 270, 343, 572, {}),
    'twist_b':  (S + 'kraken_skill1_src.webp', 270, 512, 343, 572, {}),
    'crush_a':  (S + 'kraken_skill1_src.webp', 512, 767, 343, 572, {}),
    'crush_b':  (S + 'kraken_skill1_src.webp', 767, 1024, 343, 572, {'wm': (912, 956, 460, 504)}),
    'wrap_a':   (S + 'kraken_skill2_src.png', 0, 178, 0, 173, {'lab': 46}),
    'wrap_b':   (S + 'kraken_skill2_src.png', 178, 364, 0, 173, {'lab': 46}),
    'wrap_c':   (S + 'kraken_skill2_src.png', 364, 681, 0, 173, {'lab': 46}),
    'ink_a':    (S + 'kraken_skill3_src.png', 0, 183, 0, 179, {'lab': 42}),
    'ink_b':    (S + 'kraken_skill3_src.png', 183, 366, 0, 179, {'lab': 42}),
    'ink_c':    (S + 'kraken_skill3_src.png', 366, 556, 0, 179, {'lab': 42}),
    'roar_a':   (S + 'kraken_skill4_src.png', 0, 186, 0, 169, {'lab': 38}),
    'roar_b':   (S + 'kraken_skill4_src.png', 186, 358, 0, 169, {'lab': 38}),
    'tidal':    (S + 'kraken_skill4_src.png', 358, 681, 0, 169, {'lab': 38}),
}
FX_CELLS = {
    'inkfx_0': (F + 'kraken_ink_bomb_fx_src.png', 0, 160, 38, 200, {'min': 2}),
    'inkfx_1': (F + 'kraken_ink_bomb_fx_src.png', 160, 330, 38, 200, {'min': 2}),
    'inkfx_2': (F + 'kraken_ink_bomb_fx_src.png', 330, 510, 38, 200, {'min': 2}),
    'inkfx_3': (F + 'kraken_ink_bomb_fx_src.png', 510, 682, 38, 200, {'min': 2}),
    'wave_0':  (F + 'kraken_tsunami_fx_src.png', 0, 187, 38, 192, {'min': 2}),
    'wave_1':  (F + 'kraken_tsunami_fx_src.png', 187, 363, 38, 192, {'min': 2}),
    'wave_2':  (F + 'kraken_tsunami_fx_src.png', 363, 538, 38, 192, {'min': 2}),
    'wave_3':  (F + 'kraken_tsunami_fx_src.png', 538, 716, 38, 192, {'min': 2}),
}
# 물 이펙트 샘플 2장 (한 줄에 4칸씩, 줄 위에 한글 라벨): (파일, 줄 y0, y1, 칸 경계 x)
WATER_ROWS = {
    'splash':  (F + 'kraken_water_fx1_src.webp', 36, 180, [40, 250, 520, 780, 1024]),   # 물보라 사방 튀기: 작게 튐 · 크게 튐 · 높이 흩어짐 · 사라짐
    'sweep':   (F + 'kraken_water_fx1_src.webp', 232, 360, [0, 258, 512, 768, 1024]),   # 지면 물 휩쓸기: 밀려옴 · 크게 말림 · 쓸고 지나감 · 잔물결
    'spiral':  (F + 'kraken_water_fx1_src.webp', 412, 565, [0, 255, 510, 770, 1024]),   # 소용돌이 (위에서 본 그림): 촘촘함 · 크게 돎 · 풀림 · 물방울만
    'geyser':  (F + 'kraken_water_fx1_src.webp', 602, 765, [0, 250, 510, 770, 1024]),   # 솟는 물기둥: 솟음 · 퍼짐 · 가장 큼 · 무너짐
    'burst':   (F + 'kraken_water_fx2_src.png', 20, 100, [0, 165, 350, 530, 705]),      # 물 폭발: 섬광 · 터짐 · 갈라짐 · 흩어짐
    'twister': (F + 'kraken_water_fx2_src.png', 218, 298, [0, 175, 355, 530, 705]),     # 물 회오리: 바닥 고리 · 감아 오름 · 가장 큼 · 무너짐
}
for key, (path, y0, y1, xs) in WATER_ROWS.items():
    for i in range(4):
        FX_CELLS[f'{key}_{i}'] = (path, xs[i], xs[i + 1], y0, y1, {'min': 2})

_SRC = {}


def load(path):
    """흰 배경을 지운 (rgb, a). 테두리에서 이어진 흰색 + 안쪽에 갇힌 순백 덩어리 = 배경.
    물보라 거품은 살짝 청록빛(R이 8쯤 낮음)이라 순백 기준에 안 걸려 남음. 가장자리는 가까운 안쪽 색과 흰색 사이에서 불투명도를 되살림"""
    if path in _SRC: return _SRC[path]
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    mn, mx = im.min(2), im.max(2)
    whiteish = (mn >= 236) & (mx - mn <= 9)
    lab, n = ndi.label(whiteish)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    pure = (mn >= 245) & (mx - mn <= 5)
    lab2, n2 = ndi.label(pure & ~bg)
    if n2:
        areas = ndi.sum(np.ones_like(mn), lab2, range(1, n2 + 1))
        bg |= np.isin(lab2, 1 + np.where(areas >= 12)[0])
    fg = ~bg
    core = ndi.binary_erosion(fg, iterations=2)
    if not core.any(): core = fg
    _, (iy, ix) = ndi.distance_transform_edt(~core, return_indices=True)
    t = im[iy, ix]
    a_edge = np.clip(((255 - im) / np.maximum(255 - t, 1)).max(2), 0, 1)
    band = fg & ~core
    a = np.where(core, 1.0, np.where(band, a_edge, 0.0))
    rgb = np.where(band[..., None], t, im)
    _SRC[path] = (rgb, a)
    return _SRC[path]


def cut(spec):
    """한 칸 잘라 (rgba 배열, 정보). 압축 티끌·라벨 글자는 지우고 물방울 같은 조각은 남김"""
    path, x0, x1, y0, y1, opt = spec
    rgb, a = load(path)
    rgb, a = rgb[y0:y1, x0:x1].copy(), a[y0:y1, x0:x1].copy()
    if 'wm' in opt:
        wx0, wx1, wy0, wy1 = opt['wm']
        bx = (slice(wy0 - y0, wy1 - y0), slice(wx0 - x0, wx1 - x0))
        c = rgb[bx]
        gray = (c.max(2) - c.min(2) < 30) & (c.mean(2) > 95) & (a[bx] > 0)
        solid = (a[bx] > 0.5) & ~gray
        inside = ndi.binary_fill_holes(ndi.binary_closing(solid, iterations=3)) & gray
        _, (iy, ix) = ndi.distance_transform_edt(~solid, return_indices=True)
        c[inside] = c[iy, ix][inside]
        a[bx][gray & ~inside] = 0
        a[bx][inside] = 1
    for dx0, dx1, dy0, dy1 in opt.get('drop', []):
        a[max(0, dy0 - y0):max(0, dy1 - y0), max(0, dx0 - x0):max(0, dx1 - x0)] = 0
    m = a > 0.3
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    areas = ndi.sum(m, lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    for i in range(1, n + 1):
        if areas[i - 1] < opt.get('min', 6): continue
        if 'lab' in opt:
            ys = np.where(lab == i)[0]
            if ys.max() + y0 < opt['lab']: continue
        keep[i] = True
    a = np.where(keep[lab], a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([rgb, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    if opt.get('flip'): rgba = rgba[:, ::-1]
    return rgba, {'x0': x0 + xs.min(), 'y0': y0 + ys.min()}


# 샘플마다 그린 크기가 달라서 머리 길이(정수리~눈)가 HEAD px이 되게 배율을 따로 씀 (샘플 머리 길이: 걷기 105, 대기 161, 걷기 추가·쓰러짐 44,
# 공격 50, 피격 46, 스킬 4종 58, 휘감기·먹물 48. 포효 샘플은 머리를 젖혀서 못 재고 휘감기와 같은 크기로 그려진 것을 눈으로 맞춤)
HEAD = 70
HEAD_LEN = {'kraken_walk_src': 105, 'kraken_idle_src': 161, 'kraken_walk2_src': 40, 'kraken_death_src': 40, 'kraken_attack_src': 50,
            'kraken_hurt_src': 46, 'kraken_skill1_src': 58, 'kraken_skill2_src': 48, 'kraken_skill3_src': 48, 'kraken_skill4_src': 42}
# 칸 순서 (모두 오른쪽을 봄). twist_b_f = 물 회오리 칸 좌우반전 (번갈아 그려 회오리가 도는 것처럼)
ORDER = ['idle_big', 'walk_a', 'idle', 'walk_b', 'walk_c', 'atk_a', 'atk_b', 'hurt', 'death_a', 'death_b',
         'vortex_a', 'vortex_b', 'sweep_a', 'sweep_b', 'twist_a', 'twist_b', 'twist_b_f', 'crush_a', 'crush_b',
         'wrap_a', 'wrap_b', 'wrap_c', 'ink_a', 'ink_b', 'ink_c', 'roar_a', 'roar_b']
OUT_BODY = 'assets/sprites/monster/kraken.webp'


def scaled(name):
    """배율을 맞춘 RGBA 이미지와 기준점 (x = 눈, 쓰러짐은 몸 가운데 / y = 촉수 끝이 닿는 바닥)"""
    spec = CELLS[name.removesuffix('_f')]
    rgba, _ = cut(spec)
    if name.endswith('_f'): rgba = rgba[:, ::-1]
    k = HEAD / next(v for key, v in HEAD_LEN.items() if key in spec[0])
    im = Image.fromarray(rgba.astype(np.uint8), 'RGBA')
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    r = np.array(im).astype(float)
    R, G, B, A = r[..., 0], r[..., 1], r[..., 2], r[..., 3]
    dark = ((R + G + B) / 3 < 110) & (A > 200) & ~((B > R + 40) & (B > 90))
    rows = np.where(dark.sum(1) >= 3)[0]
    ay = rows.max() + 1
    eye = (R > 140) & (R > G + 70) & (R > B + 60) & (A > 200)
    lab, n = ndi.label(ndi.binary_dilation(eye, iterations=2))
    if n and not name.startswith('death'):
        i = 1 + np.argmax(ndi.sum(eye, lab, range(1, n + 1)))
        ax = ndi.center_of_mass(eye, lab, i)[1]
    else:
        cols = np.where((A > 128).any(0))[0]
        ax = (cols.min() + cols.max()) / 2
    return im, ax, ay


def build_body():
    cells = {n: scaled(n) for n in ORDER}
    # 뒤집은 회오리 칸은 원래 칸과 같은 자리에 오게 (회오리 가운데 = 원래 칸 눈 자리를 뒤집은 곳)
    im0, ax0, ay0 = cells['twist_b']
    cells['twist_b_f'] = (cells['twist_b_f'][0], im0.width - ax0, ay0)
    L = max(ax for _, ax, _ in cells.values()); Rr = max(im.width - ax for im, ax, _ in cells.values())
    U = max(ay for _, _, ay in cells.values()); D = max(im.height - ay for im, _, ay in cells.values())
    cw, ch = int(np.ceil(L + Rr)) + 2, int(np.ceil(U + D)) + 2
    ax, ay = round(L) + 1, round(U) + 1
    sheet = Image.new('RGBA', (cw * len(ORDER), ch))
    for i, n in enumerate(ORDER):
        im, x, y = cells[n]
        sheet.alpha_composite(im, (i * cw + round(ax - x), round(ay - y)))
    sheet.save(OUT_BODY, 'WEBP', lossless=True, quality=100, method=6)
    idle_h = cells['idle_big'][2]
    print(f'{OUT_BODY}: cellW {cw}, cellH {ch}, anchor ({ax}, {ay}), count {len(ORDER)}, 대기 키 {idle_h:.0f}')
    return cw, ch, ax, ay


# 이펙트 아틀라스: 키 → 칸 이름들
OUT_FX = 'assets/sprites/fx/kraken_fx.webp'
FX_ANIMS = {
    'ink':  ['inkfx_0', 'inkfx_1', 'inkfx_2', 'inkfx_3'],   # 먹물탄 · 터지기 시작 · 사방으로 튐 · 떨어지며 사라짐
    'wave': ['wave_0', 'wave_1', 'wave_2', 'wave_3'],       # 파도 솟음 · 양쪽으로 갈라짐 · 크게 덮침 · 잔물결·거품
    **{k: [f'{k}_{i}' for i in range(4)] for k in WATER_ROWS},
}
FX_CENTER = ('ink', 'spiral')  # 가운데가 기준점인 그림 (나머지는 바닥 가운데)


def build_fx():
    frames, x = {}, 0
    for key, names in FX_ANIMS.items():
        for n in names:
            if n not in frames:
                rgba, _ = cut(FX_CELLS[n])
                frames[n] = (Image.fromarray(rgba.astype(np.uint8), 'RGBA'), x)
                x += rgba.shape[1] + 2
    H = max(im.height for im, _ in frames.values())
    sheet = Image.new('RGBA', (x, H))
    for im, fx in frames.values(): sheet.alpha_composite(im, (fx, 0))
    sheet.save(OUT_FX, 'WEBP', lossless=True, quality=100, method=6)
    out = {}
    for key, names in FX_ANIMS.items():
        rows = []
        for n in names:
            im, fx = frames[n]
            ay = im.height / 2 if key in FX_CENTER else im.height
            rows.append([fx, 0, im.width, im.height, round(im.width / 2, 1), round(ay, 1)])
        out[key] = rows
    print(OUT_FX, sheet.size)
    for k, v in out.items(): print(f'        {k}: {v},'.replace(' ', '').replace(':', ': ', 1).replace('],[', '],['))


if __name__ == '__main__':
    build_body()
    build_fx()

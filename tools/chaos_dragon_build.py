# 엘리트 종말의 마룡 카오스드래곤 샘플(흰 배경 도트, 검은 비늘·우주 날개·가슴 보라 구슬) → assets/sprites/monster/chaos_dragon.webp + 이펙트 assets/sprites/fx/chaos_dragon_fx.webp
# 사용: python tools/chaos_dragon_build.py
# 샘플: assets/sprites/monster/samples/chaos_dragon_<n>_src.webp (샘플에 적힌 설명은 무시하고 모션마다 어울리는 칸을 골라 씀)
#   2 = 대기 · 걷기 3 · 일반공격 2 · 피격 · 쓰러짐 2       3 = 브레스 2 · 낙뢰 2 · 머리 위 마법진 (+ 운석들)
#   4 = 대지 진동 2 · 용의 분노 2 · 종말의 굉음 2            7 = 기 모으기 · 입에 기운 · 포효 폭발
#   5 = 브레스 큰 불길 (이펙트)   6 = 포효 원뿔 3단계 (이펙트)   8 = 이펙트 모음 (낙뢰·운석·포효 고리·분노·대지 진동·굉음)
# 모든 샘플이 같은 배율이라 크기는 그대로. 배경 지우기는 kraken_build.py의 load·cut, 옆 조각 가르기(cx)는 lich_elite_build.py의 cut
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from kraken_build import load
from lich_elite_build import cut
from ifrit_elite_build import resized

P = 'assets/sprites/monster/samples/chaos_dragon_%d_src.webp'
S2, S3, S4, S5, S6, S7, S8 = (P % i for i in (2, 3, 4, 5, 6, 7, 8))

# 이름: (파일, x0, x1, y0, y1, 옵션) — cx = 무게중심 x가 이 범위인 조각만 (붙은 이펙트·옆 그림 떼기), wm = ✦ 워터마크 네모
# 일반공격 2의 보라 할퀴기 궤적, 브레스의 광선, 낙뢰의 번개, 굉음의 고리는 잘라 냄 (이펙트가 따로 그려짐)
CELLS = {
    'idle':    (S2, 18, 318, 24, 228, {'flip': True, 'k': 0.88}),   # 샘플 대기만 왼쪽을 봐서 뒤집음
    'walk_a':  (S2, 343, 542, 26, 205, {}),
    'walk_b':  (S2, 543, 738, 26, 205, {}),
    'walk_c':  (S2, 752, 962, 26, 205, {}),
    'atk_a':   (S2, 343, 625, 216, 392, {}),
    'atk_b':   (S2, 652, 882, 216, 392, {'drop': [(864, 882, 322, 356)]}),
    'hurt':    (S2, 4, 285, 328, 562, {'k': 0.9}),
    'death_a': (S2, 428, 692, 404, 562, {}),
    'death_b': (S2, 698, 1014, 424, 562, {}),
    # 종말의 브레스: 고개 젖혀 숨 들이쉬기 · 입을 벌려 내뿜기 (광선은 잘라 냄)
    'br_a':    (S7, 543, 755, 26, 205, {'cx': (560, 760)}),
    'br_b':    (S3, 548, 728, 26, 205, {}),
    # 혼돈의 낙뢰: 몸에 보라 전기 두르기 · 발톱 뻗어 내리꽂기 (번개는 잘라 냄)
    'tb_a':    (S3, 343, 648, 214, 392, {}),
    'tb_b':    (S3, 652, 866, 214, 392, {'cx': (0, 862)}),
    # 운석 낙하 / 마룡의 포효 앞자세: 기 모으기
    'charge':  (S7, 18, 272, 30, 250, {}),
    # 운석 낙하: 머리 위 어둠의 마법진
    'rain':    (S3, 4, 330, 288, 562, {'k': 0.9}),
    # 마룡의 포효: 입에 붉은 기운 · 포효 폭발 (입 앞 음파 고리째)
    'ro_b':    (S7, 752, 985, 26, 205, {}),
    'ro_c':    (S7, 343, 658, 214, 392, {}),
    # 대지 진동: 몸 일으키기 · 땅을 내리찍어 바위가 튐
    'eq_a':    (S4, 543, 738, 26, 205, {}),
    'eq_b':    (S4, 752, 1004, 26, 205, {}),
    # 용의 분노: 붉은 번개 두름 · 붉은 화염 오라
    'rg_a':    (S4, 343, 625, 214, 392, {}),
    'rg_b':    (S4, 632, 1012, 214, 392, {}),
    # 종말의 굉음: 입에 검은 구체 · 차원 고리 발사 (고리는 잘라 냄)
    'ds_a':    (S4, 428, 692, 404, 562, {'cx': (0, 676)}),
    'ds_b':    (S4, 668, 887, 404, 562, {}),
}
def clean_watermark(path, x0, x1, y0, y1):
    """✦ 워터마크 (어두운 회색, 채도 거의 없음): 몸에 둘러싸인 곳은 둘레 몸 색으로 메우고 나머지는 지움 (load 캐시를 고침)"""
    rgb, a = load(path)
    c, al = rgb[y0:y1, x0:x1], a[y0:y1, x0:x1]
    sat, mean = c.max(2) - c.min(2), c.mean(2)
    gray = (sat < 34) & (mean > 80) & (al > 0)
    solid = (al > 0.5) & ~gray
    inside = ndi.binary_fill_holes(ndi.binary_closing(solid, iterations=4)) & gray
    _, (iy, ix) = ndi.distance_transform_edt(~solid, return_indices=True)
    c[inside] = c[iy, ix][inside]
    al[gray & ~inside] = 0
    al[inside] = 1


clean_watermark(S2, 900, 962, 452, 514)   # 쓰러짐 2 머리 옆


def drop_white(rgba, lo=222, sat=16):
    """배경 지우기에서 남은 흰 틈 (날개 밑·고리 사이의 덜 하얀 배경 조각): 거의 흰 덩어리 중 4px 이상이거나 투명한 곳에 닿은 것을 지움.
    날개 속 별빛 점(1~3px, 몸에 둘러싸임)은 남김"""
    c, A = rgba[..., :3], rgba[..., 3]
    wh = (c.min(2) >= lo) & (c.max(2) - c.min(2) <= sat) & (A > 0)
    lab, n = ndi.label(wh, structure=np.ones((3, 3)))
    if not n: return rgba
    clear = ndi.binary_dilation(A < 128, iterations=1)
    areas = ndi.sum(wh, lab, range(1, n + 1))
    touch = ndi.maximum(clear, lab, range(1, n + 1))
    kill = np.zeros(n + 1, bool)
    kill[1:] = (areas >= 4) | (touch > 0)
    rgba = rgba.copy()
    rgba[..., 3][kill[lab]] = 0
    # 지운 자리 둘레의 밝은 테두리도 반투명하게
    edge = ndi.binary_dilation(kill[lab], iterations=1) & ~kill[lab] & (c.min(2) >= 200)
    rgba[..., 3][edge] *= 0.4
    return rgba

ORDER = ['idle', 'walk_a', 'walk_b', 'walk_c', 'atk_a', 'atk_b', 'hurt', 'death_a', 'death_b',
         'br_a', 'br_b', 'tb_a', 'tb_b', 'charge', 'rain', 'ro_b', 'ro_c', 'eq_a', 'eq_b', 'rg_a', 'rg_b', 'ds_a', 'ds_b']
OUT = 'assets/sprites/monster/chaos_dragon.webp'


def placed(name):
    im, ax, ay = placed0(name)
    k = CELLS[name][5].get('k', 1)
    if k == 1: return im, ax, ay
    return Image.fromarray(resized(np.array(im).astype(float), k).astype(np.uint8), 'RGBA'), ax * k, ay * k


def placed0(name):
    """RGBA 이미지와 기준점 (x = 가슴 보라 구슬, 없으면 몸통 가운데 · 쓰러짐은 몸 가운데 / y = 발이 닿는 바닥)"""
    path, x0, x1, y0, y1, opt = CELLS[name]
    # min = 칸 구분 점선·라벨 글자 부스러기 지우기
    rgba, info = cut((path, x0, x1, y0, y1, {'min': 60, **opt}))
    # 몸: 찢어진 날개 끝에 낀 연보라빛 흰 배경 조각까지 (용 몸 색은 훨씬 어두움)
    rgba = drop_white(rgba, lo=150, sat=26)
    A = rgba[..., 3]
    c = rgba[..., :3]
    dark = (A > 200) & (c.mean(2) < 110)
    rows = np.where(dark.sum(1) >= 3)[0]
    ay = rows.max() + 1
    if name.startswith('death'):
        cols = np.where((A > 128).any(0))[0]
        return Image.fromarray(rgba.astype(np.uint8), 'RGBA'), (cols.min() + cols.max()) / 2, ay
    h = A.shape[0]
    # 가슴 구슬: 밝은 자홍 (몸 아래쪽 75%에서 가장 큰 덩어리)
    orb = (A > 200) & (c[..., 0] > 200) & (c[..., 2] > 200) & (c[..., 1] < 170)
    orb[:int(h * 0.25)] = False
    lab, n = ndi.label(ndi.binary_dilation(orb, iterations=2))
    # 칸 오른쪽 끝에 닿은 덩어리 = 잘라 낸 브레스 광선의 입가 (구슬 아님)
    for i, sl in enumerate(ndi.find_objects(lab)):
        if sl[1].stop >= A.shape[1] - 2: orb[lab == i + 1] = False
    lab, n = ndi.label(ndi.binary_dilation(orb, iterations=2))
    if n:
        i = 1 + int(np.argmax(ndi.sum(orb, lab, range(1, n + 1))))
        if ndi.sum(orb, lab, i) >= 6:
            ax = ndi.center_of_mass(orb, lab, i)[1]
            return Image.fromarray(rgba.astype(np.uint8), 'RGBA'), ax, ay
    band = dark[int(h * 0.4):int(h * 0.75)]
    ax = float(np.median(np.where(band)[1]))
    print('  구슬 못 찾음:', name)
    return Image.fromarray(rgba.astype(np.uint8), 'RGBA'), ax, ay


def build():
    cells = {n: placed(n) for n in ORDER}
    L = max(ax for _, ax, _ in cells.values()); R = max(im.width - ax for im, ax, _ in cells.values())
    U = max(ay for _, _, ay in cells.values()); D = max(im.height - ay for im, _, ay in cells.values())
    cw, ch = int(np.ceil(L + R)) + 2, int(np.ceil(U + D)) + 2
    ax, ay = round(L) + 1, round(U) + 1
    sheet = Image.new('RGBA', (cw * len(ORDER), ch))
    for i, n in enumerate(ORDER):
        im, x, y = cells[n]
        sheet.alpha_composite(im, (i * cw + round(ax - x), round(ay - y)))
    sheet.save(OUT, 'WEBP', lossless=True, quality=100, method=6)
    print(f'{OUT}: cellW {cw}, cellH {ch}, anchor ({ax}, {ay}), count {len(ORDER)}, 대기 키 {cells["idle"][2]:.0f}, 걷기 키 {cells["walk_a"][2]:.0f}')
    for n in ('idle', 'br_b'):
        im, x, y = cells[n]
        print(f'  {n}: 왼쪽 {x:.0f} 오른쪽 {im.width - x:.0f} 위 {y:.0f}')


# 이펙트. 기준점: 투사체 = 앞 끝, 바닥 그림 = 바닥 가운데, 고리·구체 = 가운데, 원뿔 = 왼쪽 뾰족한 끝(입)
FX_CELLS = {
    'breath':   (S5, 8, 352, 34, 195, {'min': 2}),                      # 종말의 브레스 큰 불길 (머리가 오른쪽)
    'beam':     (S8, 70, 325, 48, 95, {'min': 2}),                      # 일반 공격 보라 숨결 (머리가 오른쪽)
    'bolt':     (S8, 360, 455, 48, 235, {'min': 2, 'white': True}),                    # 낙뢰 기둥 (바닥에 튀는 불꽃째)
    'spark':    (S8, 588, 670, 120, 235, {'min': 2, 'white': True}),                   # 낙뢰가 꽂힌 자리 섬광
    'meteor_0': (S8, 692, 795, 38, 135, {'min': 2, 'big': True}),       # 운석 (꼬리가 왼쪽 위)
    'meteor_1': (S8, 692, 795, 145, 240, {'min': 2, 'big': True, 'flip': True}),  # 큰 운석 (샘플은 꼬리가 오른쪽 위라 뒤집음)
    'impact_0': (S8, 798, 902, 145, 240, {'min': 2, 'white': True}),                   # 운석 충돌 폭발
    'impact_1': (S8, 902, 1006, 145, 240, {'min': 2, 'white': True}),
    'impact_2': (S8, 125, 232, 285, 392, {'min': 2, 'white': True}),
    'sphere':   (S8, 355, 455, 288, 392, {'min': 2}),                   # 포효: 검붉은 기운 구체
    'rings':    (S8, 455, 565, 288, 395, {'min': 2}),                   # 포효: 비스듬한 충격파 고리
    'ripple':   (S8, 455, 565, 470, 560, {'min': 2}),                   # 포효: 바닥 물결 고리 (위에서 본)
    'crack':    (S8, 350, 455, 395, 462, {'min': 2}),                   # 포효: 땅 갈라짐
    'cone_0':   (S6, 150, 268, 140, 290, {'min': 2, 'cx': (170, 300)}), # 포효 원뿔 1~3 (오른쪽으로 퍼짐)
    'cone_1':   (S6, 395, 645, 96, 350, {'min': 2, 'cx': (405, 700)}),
    'cone_2':   (S6, 655, 1016, 58, 550, {'min': 2}),
    'tornado':  (S8, 692, 795, 290, 395, {'min': 2}),                   # 용의 분노: 붉은 회오리
    'spiky':    (S8, 795, 900, 285, 395, {'min': 2}),                   # 용의 분노: 검은 가시 폭발
    'qcrack':   (S8, 350, 455, 395, 462, {'min': 2}),                   # 대지 진동: 땅 갈라짐
    'spike':    (S5, 372, 648, 220, 368, {'min': 2}),                   # 대지 진동: 보라 가시 분출 + 튀는 바위 (샘플 5)
    'flame':    (S8, 122, 228, 448, 562, {'min': 2}),                   # 대지 진동: 보라 불꽃 분출
    'erupt':    (S8, 228, 335, 458, 562, {'min': 2}),                   # 대지 진동: 불꽃 + 바닥 물결
    'hole':     (S8, 690, 798, 450, 560, {'min': 2}),                   # 종말의 굉음: 검은 구멍
    'star':     (S8, 798, 900, 445, 565, {'min': 2}),                   # 종말의 굉음: 어둠의 별 폭발
    'vortex':   (S8, 900, 1010, 450, 562, {'min': 2}),                  # 종말의 굉음: 소용돌이
}
FX_ANIMS = {
    'breath': ['breath'], 'beam': ['beam'], 'bolt': ['bolt'], 'spark': ['spark'],
    'meteor': ['meteor_0', 'meteor_1'], 'impact': ['impact_0', 'impact_1', 'impact_2'],
    'roar': ['sphere', 'rings', 'ripple', 'crack'], 'cone': ['cone_0', 'cone_1', 'cone_2'],
    'rage': ['tornado', 'spiky'], 'quake': ['qcrack', 'spike', 'erupt'], 'disso': ['hole', 'star', 'vortex'],
}
OUT_FX = 'assets/sprites/fx/chaos_dragon_fx.webp'
BOTTOM = {'bolt', 'spark', 'impact_0', 'impact_1', 'impact_2', 'crack', 'qcrack', 'spike', 'tornado', 'flame', 'erupt'}


def fx_cut(spec):
    rgba = fx_cut0(spec)
    return rgba if spec[5].get('white') else drop_white(rgba)


def fx_cut0(spec):
    if not spec[5].get('big'): return cut(spec)[0]
    _, a = load(spec[0])
    p, x0, x1, y0, y1, _ = spec
    m = a[y0:y1, x0:x1] > 0.05
    lab, cnt = ndi.label(m, structure=np.ones((3, 3)))
    big = 1 + int(np.argmax(ndi.sum(m, lab, range(1, cnt + 1))))
    saved = a[y0:y1, x0:x1].copy()
    a[y0:y1, x0:x1][(lab != big) & m] = 0
    try: return cut(spec)[0]
    finally: a[y0:y1, x0:x1] = saved


def build_fx():
    frames, x = {}, 0
    for names in FX_ANIMS.values():
        for n in names:
            rgba = fx_cut(FX_CELLS[n])
            frames[n] = (Image.fromarray(rgba.astype(np.uint8), 'RGBA'), x)
            x += rgba.shape[1] + 2
    H = max(im.height for im, _ in frames.values())
    sheet = Image.new('RGBA', (x, H))
    for im, fx in frames.values(): sheet.alpha_composite(im, (fx, 0))
    sheet.save(OUT_FX, 'WEBP', lossless=True, quality=100, method=6)
    print(OUT_FX, sheet.size)
    for key, names in FX_ANIMS.items():
        rows = []
        for n in names:
            im, fx = frames[n]
            ax, ay = im.width / 2, im.height / 2
            if key in ('breath', 'beam'): ax = im.width - 4
            elif key == 'meteor': ax, ay = im.width * 0.75, im.height * 0.78
            elif key == 'cone':
                # 뾰족한 끝 = 가장 왼쪽 불투명 열의 가운데
                A = np.array(im)[..., 3] > 100
                ax = 0; ay = float(np.median(np.where(A[:, :max(4, im.width // 12)].any(1))[0]))
            elif n in BOTTOM: ay = im.height
            rows.append([fx, 0, im.width, im.height, round(ax, 1), round(float(ay), 1)])
        print(f'        {key}: {rows},'.replace(' ', '').replace(':', ': ', 1))


if __name__ == '__main__':
    build()
    build_fx()

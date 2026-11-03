# 엘리트 망자의 군주 리치 샘플(흰 배경 도트, 로브·해골 지팡이) → assets/sprites/monster/lich_elite.webp + 이펙트 assets/sprites/fx/lich_fx.webp
# 사용: python tools/lich_elite_build.py
# 샘플: assets/sprites/monster/samples/lich_robe_src.webp (4×2: 대기, 걷기 1·2, 일반공격 1 / 일반공격 2, 피격, 쓰러짐 1·2)
#       assets/sprites/monster/samples/lich_robe_skill_src.webp (3×3: 영혼 서리·역병 폭탄·죽음의 저주 × 모으기·기운 두름·방출)
#       assets/sprites/monster/samples/lich_robe_skill2_src.webp (망령 이동 4칸 · 불사의 의식 4칸 · 망자의 늪 3칸)
# 이펙트: assets/sprites/fx/samples/lich_skill_fx_src.webp (영혼 서리 4 · 역병 폭탄 4 · 죽음의 저주 4)
#         assets/sprites/fx/samples/lich_skill_fx2_src.webp (망령 이동 4 · 불사의 의식 4 · 망자의 늪 4)
#   죽음의 저주 이펙트 가운데 두 칸은 리치 몸이 같이 그려져 있어서 안 씀
# 배경 지우기는 kraken_build.py의 load·cut을 그대로 씀. 샘플끼리 배율이 같아서 크기는 그대로
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from kraken_build import cut as kcut, load

S = 'assets/sprites/monster/samples/lich_robe_src.webp'
K = 'assets/sprites/monster/samples/lich_robe_skill_src.webp'
K2 = 'assets/sprites/monster/samples/lich_robe_skill2_src.webp'
F1 = 'assets/sprites/fx/samples/lich_skill_fx_src.webp'
F2 = 'assets/sprites/fx/samples/lich_skill_fx2_src.webp'


def cut(spec):
    """kraken_build.cut + cx = 무게중심(샘플 x)이 이 범위 안인 조각만 남김 (옆 칸 그림이 겹쳐 들어오는 칸)"""
    path, x0, x1, y0, y1, opt = spec
    if 'cx' not in opt: return kcut(spec)
    _, a = load(path)
    m = a[y0:y1, x0:x1] > 0.05
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    cxs = ndi.center_of_mass(m, lab, range(1, n + 1))
    lo, hi = opt['cx']
    hide = np.isin(lab, [i + 1 for i, (_, cx) in enumerate(cxs) if not lo <= cx + x0 < hi])
    keep = a[y0:y1, x0:x1].copy()
    a[y0:y1, x0:x1][hide] = 0
    try: return kcut(spec)
    finally: a[y0:y1, x0:x1] = keep


# 이름: (파일, x0, x1, y0, y1, 옵션) — lab = 이 y보다 위에만 있는 조각은 라벨 글자로 보고 지움
# 일반공격 2의 푸른 불덩이(x 237~292)는 칸 밖으로 잘라 냄 (투사체는 따로 날아감)
# body = 기준점(몸통 가운데)을 잴 샘플 x 범위 (방출 칸은 오른쪽 이펙트에 안 끌려가게), ice = 얼음·눈이 흰빛이라 흰 틈 지우기를 순백에만
# 스킬 방출 칸의 얼음 가시·역병 구름·해골 망령은 칸 안에 그대로 둠 (지팡이 끝과 겹쳐 있어서)
CELLS = {
    'idle':    (S, 0, 262, 40, 290, {}),
    'walk_a':  (S, 262, 510, 40, 290, {}),
    'walk_b':  (S, 510, 766, 40, 290, {}),
    'atk_a':   (S, 766, 1024, 40, 290, {}),
    'atk_b':   (S, 0, 236, 296, 572, {'lab': 349}),
    'hurt':    (S, 294, 510, 296, 572, {'lab': 349}),
    'death_a': (S, 510, 762, 296, 572, {'lab': 349}),
    'death_b': (S, 762, 1024, 296, 572, {'lab': 349}),
    'frost_a':  (K, 0, 270, 37, 258, {'lab': 70}),
    'frost_b':  (K, 270, 520, 37, 258, {'lab': 70, 'ice': True}),
    'frost_c':  (K, 520, 1024, 37, 258, {'lab': 70, 'ice': True, 'body': (556, 720)}),
    'plague_a': (K, 0, 280, 262, 505, {'lab': 320}),
    'plague_b': (K, 280, 520, 262, 505, {'lab': 320}),
    'plague_c': (K, 520, 1024, 262, 505, {'lab': 320, 'body': (544, 720)}),
    'curse_a':  (K, 0, 268, 514, 765, {'lab': 574}),
    'curse_b':  (K, 268, 520, 514, 765, {'lab': 574}),
    'curse_c':  (K, 520, 1024, 514, 765, {'lab': 574, 'body': (536, 720)}),
    # 망령 이동: 그대로 · 망령화(반투명 푸른 몸) · 잔상 남기며 이동 · 보랏빛 꼬리 끌며 재출현 (뒤 두 칸은 그림이 겹쳐서 cx로 나눔)
    'tp_a':  (K2, 0, 262, 40, 252, {'lab': 66}),
    'tp_b':  (K2, 262, 520, 40, 252, {'lab': 66, 'ice': True}),
    'tp_c':  (K2, 520, 1024, 40, 252, {'lab': 66, 'ice': True, 'cx': (0, 735), 'body': (620, 770)}),
    'tp_d':  (K2, 520, 1024, 40, 252, {'lab': 66, 'cx': (735, 1024), 'body': (820, 1000)}),
    # 불사의 의식: 주문 외우기 · 금빛 마법진 · 푸른 불꽃 든 손 · 불길에 휩싸임
    'rit_a': (K2, 0, 268, 262, 502, {'lab': 314}),
    'rit_b': (K2, 268, 520, 262, 502, {'lab': 314}),
    'rit_c': (K2, 520, 766, 262, 502, {'lab': 314}),
    'rit_d': (K2, 766, 1024, 262, 502, {'lab': 314}),
    # 망자의 늪: 의식 집중 · 발밑에 늪 · 지팡이로 늪을 펼쳐 손·망령 소환
    'sw_a':  (K2, 0, 262, 505, 765, {'lab': 566}),
    'sw_b':  (K2, 262, 520, 505, 765, {'lab': 566}),
    'sw_c':  (K2, 520, 1024, 505, 765, {'lab': 566, 'body': (540, 720)}),
}
ORDER = ['idle', 'walk_a', 'walk_b', 'atk_a', 'atk_b', 'hurt', 'death_a', 'death_b',
         'frost_a', 'frost_b', 'frost_c', 'plague_a', 'plague_b', 'plague_c', 'curse_a', 'curse_b', 'curse_c',
         'tp_a', 'tp_b', 'tp_c', 'tp_d', 'rit_a', 'rit_b', 'rit_c', 'rit_d', 'sw_a', 'sw_b', 'sw_c']
OUT = 'assets/sprites/monster/lich_elite.webp'


def placed(name):
    """RGBA 이미지와 기준점 (x = 몸통 가운데, 쓰러짐은 몸 가운데 / y = 발이 닿는 바닥)"""
    spec = CELLS[name]
    opt = spec[5]
    rgba, info = cut(spec)
    # 로브 자락 사이에 갇힌 흰 배경 틈 (load는 넓이 12px 이상 순백만 지워서 남음). 푸른 불꽃·눈빛은 B가 R보다 커서 안 걸림
    c = rgba[..., :3]
    if opt.get('ice'): gap = (c.min(2) >= 248) & (c.max(2) - c.min(2) <= 4)
    else: gap = (c.min(2) >= 185) & (c[..., 2] - c[..., 0] < 18)
    rgba[..., 3][gap] = 0
    A = rgba[..., 3]
    rows = np.where((A > 128).sum(1) >= 3)[0]
    ay = rows.max() + 1
    if name.startswith('death'):
        cols = np.where((A > 128).any(0))[0]
        ax = (cols.min() + cols.max()) / 2
    else:
        # 지팡이·뻗은 팔에 끌려가지 않게 로브 몸통 높이(위에서 35~70%)의 불투명 칸 가운데값
        h = A.shape[0]
        band = A[int(h * 0.35):int(h * 0.7)] > 128
        if 'body' in opt:
            bx0, bx1 = opt['body']
            band[:, :max(0, bx0 - info['x0'])] = False
            band[:, bx1 - info['x0']:] = False
        xs = np.where(band)[1]
        ax = float(np.median(xs))
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
    print(f'{OUT}: cellW {cw}, cellH {ch}, anchor ({ax}, {ay}), count {len(ORDER)}, 대기 키 {cells["idle"][2]}')


# fade = 이웃 칸과 붙어 있어 곧게 자른 쪽(L·R) 가장자리를 20px에 걸쳐 투명하게
# 이펙트 아틀라스: 키 → 칸. 기준점 = frost는 바닥 가운데, rit·swamp는 바닥 타원 가운데, 나머지는 그림 가운데
FX_CELLS = {
    'frost_0':  (F1, 0, 280, 71, 258, {'min': 2}),                   # 한기 집결 (회오리)
    'frost_1':  (F1, 280, 510, 71, 258, {'min': 2}),                 # 얼음 솟구침
    'frost_2':  (F1, 510, 765, 71, 258, {'min': 2}),                 # 빙결 확산 + 영혼
    'frost_3':  (F1, 765, 1024, 71, 258, {'min': 2}),                # 부서짐·잔상
    'plague_0': (F1, 0, 290, 296, 505, {'min': 2, 'lab': 320}),      # 독기 구체 (머리가 오른쪽)
    'plague_1': (F1, 290, 510, 296, 505, {'min': 2, 'lab': 320}),    # 폭발 시작
    'plague_2': (F1, 510, 768, 296, 505, {'min': 2, 'lab': 320}),    # 뼈 섞인 독구름
    'plague_3': (F1, 768, 1024, 296, 505, {'min': 2, 'lab': 320}),   # 흩어지며 소멸
    'hex_0':    (F1, 0, 270, 540, 765, {'min': 2, 'lab': 572}),      # 망령 소용돌이
    'hex_1':    (F1, 740, 1024, 540, 765, {'min': 2, 'lab': 572, 'cx': (780, 1024)}),  # 날아가는 해골 원혼 (머리가 오른쪽)
    'tpfx_0':   (F2, 0, 250, 63, 240, {'min': 2}),                   # 망령 기류
    'tpfx_1':   (F2, 250, 545, 63, 240, {'min': 2}),                 # 고속 이동 궤적 (머리가 오른쪽)
    'tpfx_2':   (F2, 545, 770, 63, 240, {'min': 2}),                 # 잔상 폭발
    'tpfx_3':   (F2, 770, 1024, 63, 240, {'min': 2}),                # 소멸
    'rit_0':    (F2, 0, 268, 286, 500, {'min': 2, 'lab': 318}),      # 마법진
    'rit_1':    (F2, 268, 520, 286, 500, {'min': 2, 'lab': 318}),    # 혼령의 불꽃
    'rit_2':    (F2, 520, 770, 286, 500, {'min': 2, 'lab': 318}),    # 해골 혼령이 솟음
    'rit_3':    (F2, 770, 1024, 286, 500, {'min': 2, 'lab': 318}),   # 잔상·안개
    'sw_0':     (F2, 0, 268, 540, 765, {'min': 2, 'lab': 570}),      # 늪 퍼짐
    'sw_1':     (F2, 268, 530, 540, 765, {'min': 2, 'lab': 570}),    # 손이 솟는 늪
    'sw_2':     (F2, 530, 775, 540, 765, {'min': 2, 'lab': 570, 'fade': 'R'}),   # 망령·뼈가 솟는 늪
    'sw_3':     (F2, 775, 1024, 540, 765, {'min': 2, 'lab': 570, 'fade': 'L'}),  # 잔류 안개
}
FX_ANIMS = {
    'frost': ['frost_0', 'frost_1', 'frost_2', 'frost_3'],
    'plague': ['plague_0', 'plague_1', 'plague_2', 'plague_3'],
    'hex': ['hex_0', 'hex_1'],
    'tp': ['tpfx_0', 'tpfx_1', 'tpfx_2', 'tpfx_3'],
    'rit': ['rit_0', 'rit_1', 'rit_2', 'rit_3'],
    'swamp': ['sw_0', 'sw_1', 'sw_2', 'sw_3'],
}
OUT_FX = 'assets/sprites/fx/lich_fx.webp'


def build_fx():
    frames, x = {}, 0
    for names in FX_ANIMS.values():
        for n in names:
            rgba, _ = cut(FX_CELLS[n])
            side = FX_CELLS[n][5].get('fade')
            if side:
                ramp = np.clip(np.arange(rgba.shape[1]) / 20, 0, 1)
                rgba[..., 3] *= ramp if side == 'L' else ramp[::-1]
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
            ay = im.height / 2
            if key == 'frost': ay = im.height
            elif key in ('rit', 'swamp'):
                # 바닥 타원: 맨 아래에서 위로 70px 안에서 가장 넓은 줄 = 타원 가운데
                w = (np.array(im)[..., 3] > 100).sum(1)
                lo = max(0, im.height - 70)
                ay = lo + int(np.argmax(w[lo:]))
            rows.append([fx, 0, im.width, im.height, round(im.width / 2, 1), round(float(ay), 1)])
        print(f'        {key}: {rows},'.replace(' ', '').replace(':', ': ', 1))


if __name__ == '__main__':
    build()
    build_fx()

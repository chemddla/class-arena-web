# 엘리트 겁화의 이프리트 샘플(흰 배경 도트, 불꽃 뿔·용암 갑옷·맨손) → assets/sprites/monster/ifrit_elite.webp + 이펙트 assets/sprites/fx/ifrit_fx.webp
# 사용: python tools/ifrit_elite_build.py
# 샘플: assets/sprites/monster/samples/ifrit_elite_src.webp (대기 · 걷기 1·2 / 일반공격 1·2 · 피격 / 쓰러짐 1·2. 대기 아래 다리만 있는 조각은 안 씀)
#       assets/sprites/monster/samples/ifrit_elite_skill_src.webp (겁화구 2칸 + 날아가는 겁화구 · 화염 폭발 3칸 · 불비 3칸)
#       assets/sprites/monster/samples/ifrit_elite_skill2_src.webp (용암 분출 2칸 · 불꽃 순간이동 2칸 · 불꽃 분노 2칸)
# 이펙트: assets/sprites/fx/samples/ifrit_skill_fx_src.webp (용암 분출 4 · 불꽃 순간이동 4 · 불꽃 분노 4)
#         assets/sprites/fx/samples/ifrit_fireball_boom_src.png (겁화구 폭발) · ifrit_meteor_rain_src.png (떨어지는 운석들 · 지면 타격)
# 배경 지우기는 kraken_build.py의 load·cut, 옆 칸 조각 가르기는 lich_elite_build.py의 cut(cx)을 그대로 씀.
# 샘플마다 그린 크기가 달라서 칸마다 배율 k를 씀 (기본 = 걷기 칸 크기. 대기·스킬 샘플 1은 크게, 스킬 샘플 2는 작게 그려짐)
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from kraken_build import load
from lich_elite_build import cut

S = 'assets/sprites/monster/samples/ifrit_elite_src.webp'
K = 'assets/sprites/monster/samples/ifrit_elite_skill_src.webp'
K2 = 'assets/sprites/monster/samples/ifrit_elite_skill2_src.webp'
F = 'assets/sprites/fx/samples/ifrit_skill_fx_src.webp'
FB = 'assets/sprites/fx/samples/ifrit_fireball_boom_src.png'  # 화염구 터지는 이펙트 3단계 (불꽃 폭발)
FR = 'assets/sprites/fx/samples/ifrit_meteor_rain_src.png'   # 불비 내리는 이펙트 1단계 (강우 징조) · 2단계 (지면 타격)

# 이름: (파일, x0, x1, y0, y1, 옵션) — lab = 이 y보다 위에만 있는 조각은 라벨 글자로 보고 지움, k = 배율,
# body = 기준점(몸통 가운데)을 잴 샘플 x 범위, main = 가장 큰 조각과 바닥(아래 25px)에 닿은 조각만 남김 (불비 칸의 날아오는 운석 지우기)
# 일반공격 2·겁화구 2의 불덩이는 칸 밖으로 잘라 냄 (투사체는 따로 날아감)
KS1, KS2, KS3 = 0.8, 0.84, 1.2
CELLS = {
    'idle':    (S, 25, 270, 30, 262, {'k': 0.8}),
    'walk_a':  (S, 320, 490, 30, 205, {'lab': 30}),
    'walk_b':  (S, 520, 700, 30, 205, {'lab': 30}),
    'atk_a':   (S, 285, 495, 228, 408, {'lab': 232}),
    'atk_b':   (S, 500, 698, 228, 408, {'lab': 232}),
    'hurt':    (S, 790, 1000, 228, 408, {'lab': 232}),
    'death_a': (S, 295, 500, 438, 572, {'lab': 440}),
    'death_b': (S, 515, 750, 438, 572, {'lab': 440}),
    # 겁화구: 등 뒤로 불덩이 모으기 · 손 뻗어 발사
    'fb_a':    (K, 60, 340, 44, 262, {'lab': 48, 'k': KS2}),
    'fb_b':    (K, 360, 642, 44, 262, {'lab': 48, 'k': KS2}),
    # 화염 폭발: 기 모으기 · 불길 두름 · 불꽃 돔 폭발
    'bu_a':    (K, 40, 292, 300, 510, {'lab': 304, 'k': KS2}),
    'bu_b':    (K, 292, 580, 300, 512, {'lab': 304, 'k': KS2}),
    'bu_c':    (K, 585, 1000, 272, 514, {'k': KS2, 'body': (690, 900)}),
    # 불비: 두 손 치켜든 의식 · 내려다봄 · 운석이 쏟아짐 (운석은 지우고 장판에서 따로 떨어뜨림)
    'ra_a':    (K, 40, 292, 512, 765, {'lab': 556, 'k': KS2}),
    'ra_b':    (K, 296, 520, 528, 765, {'lab': 557, 'k': KS2}),
    'ra_c':    (K, 600, 880, 520, 765, {'k': KS2, 'main': True}),
    # 용암 분출: 웅크려 기 모으기(연기) · 용암 위로 솟음
    'la_a':    (K2, 210, 500, 42, 192, {'lab': 44, 'k': KS3, 'body': (330, 470)}),
    'la_b':    (K2, 565, 860, 42, 192, {'lab': 44, 'k': KS3}),
    # 불꽃 순간이동: 불길에 휘감겨 사라짐 · 불기둥 속에서 나타남
    'tp_a':    (K2, 210, 410, 232, 390, {'lab': 233, 'k': KS3}),
    'tp_b':    (K2, 565, 860, 232, 390, {'lab': 233, 'k': KS3}),
    # 불꽃 분노: 포효 · 양옆으로 불길이 휘몰아침
    'rg_a':    (K2, 190, 405, 383, 572, {'k': KS3}),
    'rg_b':    (K2, 565, 880, 390, 572, {'lab': 392, 'k': KS3}),
}
ORDER = ['idle', 'walk_a', 'walk_b', 'atk_a', 'atk_b', 'hurt', 'death_a', 'death_b',
         'fb_a', 'fb_b', 'bu_a', 'bu_b', 'bu_c', 'ra_a', 'ra_b', 'ra_c', 'la_a', 'la_b', 'tp_a', 'tp_b', 'rg_a', 'rg_b']
OUT = 'assets/sprites/monster/ifrit_elite.webp'


def keep_main(spec):
    """가장 큰 조각 + 칸 바닥에 닿은 조각만 남긴 사본 spec (나머지 조각은 load 캐시의 알파를 잠깐 0으로)"""
    path, x0, x1, y0, y1, opt = spec
    _, a = load(path)
    m = a[y0:y1, x0:x1] > 0.05
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    areas = ndi.sum(m, lab, range(1, n + 1))
    big = 1 + int(np.argmax(areas))
    objs = ndi.find_objects(lab)
    keep = [big] + [i + 1 for i, s in enumerate(objs) if s[0].stop >= (y1 - y0) - 25]
    return ~np.isin(lab, keep) & m


def resized(rgba, k):
    if abs(k - 1) < 1e-3: return rgba
    # 알파를 곱한 채로 줄여야 가장자리에 흰 테가 안 생김
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:4] / 255
    h, w = rgba.shape[:2]
    out = np.stack([np.array(Image.fromarray(pm[..., c].astype(np.float32), 'F').resize((round(w * k), round(h * k)), Image.LANCZOS)) for c in range(4)], -1)
    out = np.clip(out, 0, 255)
    a = out[..., 3:4]
    out[..., :3] = np.where(a > 0, out[..., :3] * 255 / np.maximum(a, 1e-3), 0)
    return np.clip(out, 0, 255)


def placed(name):
    """배율 맞춘 RGBA 이미지와 기준점 (x = 몸통 가운데, 쓰러짐은 몸 가운데 / y = 발이 닿는 바닥)"""
    spec = CELLS[name]
    opt = spec[5]
    path, x0, x1, y0, y1, _ = spec
    if opt.get('main'):
        _, a = load(path)
        hide = keep_main(spec)
        saved = a[y0:y1, x0:x1].copy()
        a[y0:y1, x0:x1][hide] = 0
        try: rgba, info = cut(spec)
        finally: a[y0:y1, x0:x1] = saved
    else:
        rgba, info = cut(spec)
    A = rgba[..., 3]
    # 기준점은 원래 크기에서 재고 배율만큼 옮김
    rows = np.where((A > 128).sum(1) >= 3)[0]
    ay = rows.max() + 1
    if name.startswith('death'):
        cols = np.where((A > 128).any(0))[0]
        ax = (cols.min() + cols.max()) / 2
    else:
        # 불길·뻗은 팔에 끌려가지 않게 몸통 높이(위에서 35~70%)의 진한 칸(용암 갑옷·몸) 가운데값
        h = A.shape[0]
        c = rgba[..., :3]
        dark = (A > 200) & (c.mean(2) < 120)
        band = dark[int(h * 0.35):int(h * 0.7)].copy()
        if 'body' in opt:
            bx0, bx1 = opt['body']
            band[:, :max(0, bx0 - info['x0'])] = False
            band[:, bx1 - info['x0']:] = False
        xs = np.where(band)[1]
        ax = float(np.median(xs))
    k = opt.get('k', 1.0)
    rgba = resized(rgba, k)
    return Image.fromarray(rgba.astype(np.uint8), 'RGBA'), ax * k, ay * k


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


# 이펙트 아틀라스. lava = 용암 분출(열기 상승·용암 폭발·사방 비산·냉각 잔상), tp = 불꽃 순간이동(불꽃 고리·화염 소용돌이·대폭발·연기 잔상),
# rage = 불꽃 분노(불꽃 충전·충격파 고리·전방위 대방출·잔불 고리), orb = 일반공격 불덩이, ball = 겁화구 (투사체는 머리가 오른쪽),
# boom = 겁화구 폭발, meteor = 불비 운석 큰 것·작은 것 (꼬리가 왼쪽 위), hit = 운석 지면 타격. big = 칸 안에서 가장 큰 조각 하나만
FX_CELLS = {
    'lava_0': (F, 0, 260, 60, 250, {'min': 2, 'lab': 60}),
    'lava_1': (F, 260, 510, 60, 250, {'min': 2, 'lab': 60}),
    'lava_2': (F, 510, 780, 60, 250, {'min': 2, 'lab': 60}),
    'lava_3': (F, 780, 1024, 60, 250, {'min': 2, 'lab': 60}),
    'tp_0':   (F, 0, 260, 314, 505, {'min': 2, 'lab': 314}),
    'tp_1':   (F, 260, 510, 314, 505, {'min': 2, 'lab': 314}),
    'tp_2':   (F, 510, 780, 314, 505, {'min': 2, 'lab': 314}),
    'tp_3':   (F, 780, 1024, 314, 505, {'min': 2, 'lab': 314}),
    'rage_0': (F, 0, 260, 566, 765, {'min': 2, 'lab': 566}),
    'rage_1': (F, 260, 510, 566, 765, {'min': 2, 'lab': 566}),
    'rage_2': (F, 510, 780, 562, 765, {'min': 2, 'lab': 562}),
    'rage_3': (F, 780, 1024, 566, 765, {'min': 2, 'lab': 566}),
    'orb':    (S, 698, 775, 236, 352, {'min': 2}),
    'ball':   (K, 650, 960, 46, 205, {'min': 2}),
    'boom':     (FB, 0, 180, 40, 174, {'min': 2, 'lab': 40}),
    'meteor_0': (FR, 0, 150, 40, 170, {'min': 2, 'big': True}),
    'meteor_1': (FR, 60, 126, 40, 116, {'min': 2, 'big': True}),
    'hit':      (FR, 155, 333, 40, 170, {'min': 2, 'lab': 44}),
}
FX_ANIMS = {
    'lava': ['lava_0', 'lava_1', 'lava_2', 'lava_3'],
    'tp': ['tp_0', 'tp_1', 'tp_2', 'tp_3'],
    'rage': ['rage_0', 'rage_1', 'rage_2', 'rage_3'],
    'orb': ['orb'], 'ball': ['ball'], 'boom': ['boom'], 'meteor': ['meteor_0', 'meteor_1'], 'hit': ['hit'],
}
OUT_FX = 'assets/sprites/fx/ifrit_fx.webp'


def build_fx():
    frames, x = {}, 0
    for names in FX_ANIMS.values():
        for n in names:
            spec = FX_CELLS[n]
            if spec[5].get('big'):
                _, a = load(spec[0])
                p, x0, x1, y0, y1, _ = spec
                m = a[y0:y1, x0:x1] > 0.05
                lab, cnt = ndi.label(m, structure=np.ones((3, 3)))
                big = 1 + int(np.argmax(ndi.sum(m, lab, range(1, cnt + 1))))
                saved = a[y0:y1, x0:x1].copy()
                a[y0:y1, x0:x1][(lab != big) & m] = 0
                try: rgba, _ = cut(spec)
                finally: a[y0:y1, x0:x1] = saved
            else:
                rgba, _ = cut(spec)
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
            A = np.array(im)[..., 3] > 100
            ax, ay = im.width / 2, im.height / 2
            if key in ('lava', 'rage') or n in ('tp_0', 'tp_1'):
                ay = im.height  # 바닥에서 솟는 그림 = 바닥 가운데
                if n in ('tp_0', 'rage_1', 'rage_3'):
                    # 바닥 고리: 맨 아래에서 위로 50px 안에서 가장 넓은 줄 = 고리 가운데
                    w = A.sum(1); lo = max(0, im.height - 50)
                    ay = lo + int(np.argmax(w[lo:]))
            elif key in ('orb', 'ball'):
                ax, ay = im.width - 4, im.height / 2  # 앞 끝
            elif key == 'meteor':
                ax, ay = im.width * 0.78, im.height * 0.8  # 돌덩이 (오른쪽 아래)
            elif key == 'hit':
                ay = im.height  # 바닥 가운데
            rows.append([fx, 0, im.width, im.height, round(ax, 1), round(float(ay), 1)])
        print(f'        {key}: {rows},'.replace(' ', '').replace(':', ': ', 1))


if __name__ == '__main__':
    build()
    build_fx()

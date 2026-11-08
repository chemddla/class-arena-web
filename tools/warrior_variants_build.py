# 전사 기본 외형(대검 기사, warrior_0.webp)에서 갑옷·망토·머리 색만 바꾼 외형 시트 (칸 구성·크기 모두 같음)
# 사용: python tools/warrior_variants_build.py preview  → _preview_warrior_variants.png (색 조합 미리보기만)
#       python tools/warrior_variants_build.py masks    → _preview_warrior_masks.png (부위 판정 확인용)
#       python tools/warrior_variants_build.py          → assets/sprites/merc/warrior_1~5.webp + assets/sprites/fx/warrior_excalibur_cast_1~5.webp
#         (엑스칼리버 시전 그림도 기본 외형 4칸(warrior_excalibur_cast.webp, 칸 200)을 같은 색으로 칠함 — 예전 2칸 외형별 그림을 대체)
# 고정: 피부(얼굴·손)·눈·입, 금장식(칼자루·테두리), 가죽(장갑·벨트·부츠), 검날, 이펙트(바람 고리·궤적·먼지)
# 바꿈: 머리카락 · 갑옷 쇠 · 갑옷 안 파란 천 · 망토·목도리 (원래 명암을 새 색의 그늘~밝은 면으로 옮겨 칠함)
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb

SRC = 'assets/sprites/merc/warrior_0.webp'
EXCAL_SRC = 'assets/sprites/fx/warrior_excalibur_cast.webp'
EXCAL_CELL = 149   # warrior_excalibur0_build.py가 출력하는 cellW
FX_MASK = 'assets/sprites/fx/samples/warrior_0_fxmask.png'   # warrior_build.py가 남긴 이펙트 자리 (흰·검정 비교 칸의 바람 고리·바람 줄·흙먼지)
CELL = 171   # 시트 칸 폭 (warrior_build.py가 출력하는 cellW)
NAMES = 'idle walk1 walk2 atk1 atk2 hurt down1 down2 whirl1 whirl2 whirl3 roar1 roar2 dash1 dash2 dash3'.split()

# (번호, 이름, 머리, 갑옷 쇠, 천, 망토) — 색 하나 = 그 색의 그늘~밝은 면으로 칠함, None = 원래 색
VARIANTS = [
    (1, '금발 · 은빛 갑옷 · 남색 천 · 파랑 망토',      '#e8c25a', '#c9d3e0', '#23366e', '#2f5fc4'),
    (2, '적발 · 검은 쇠 · 검정 천 · 진홍 망토',        '#b8402a', '#5a5660', '#2a2630', '#a3182c'),
    (3, '흑발 · 자줏빛 쇠 · 금빛 천 · 보라 망토',      '#2c2633', '#8a7ea8', '#c99a2e', '#6a2fa0'),
    (4, '녹발 · 청동 갑옷 · 고동 천 · 초록 망토',      '#3f8f4a', '#b08a5a', '#6a4426', '#2f7a3a'),
    (5, '은발 · 흑철 갑옷 · 진홍 천 · 검정 망토',      '#d8dce6', '#3c4048', '#9a1c2c', '#26232b'),
]


def hsv_of(im):
    hsv = rgb2hsv(im[..., :3] / 255.)
    return hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2], hsv


def comps(m, min_sz=1, conn=8):
    lab, n = ndi.label(m, np.ones((3, 3), int) if conn == 8 else None)
    sz = ndi.sum(m, lab, range(1, n + 1)) if n else np.array([])
    return lab, n, sz


def masks(cell, fxk=None):
    """한 칸의 부위 판정: dict(skin, hair, red, cloth, steel, sword, gold)
    색 기준 (warrior_0 측정): 머리 색상 7~16·채도 0.4~0.65·밝기 0.15~0.62 / 피부 색상 13~28·채도 0.12~0.5·밝기 0.6 이상
    망토·목도리 색상 345~6·채도 0.6 이상 / 천 색상 200~240·채도 0.38 이상 / 쇠 채도 0.36 미만"""
    h, s, v, _ = hsv_of(cell)
    a = cell[..., 3]
    solid = a > 200
    skin = solid & (h >= 13) & (h <= 28) & (s >= 0.12) & (s <= 0.5) & (v >= 0.6)
    brown = solid & (h >= 6) & (h <= 17) & (s >= 0.38) & (s <= 0.7) & (v >= 0.13) & (v < 0.64)
    # 머리카락 = 가장 큰 갈색 덩어리와 그만한 덩어리들 (장갑·벨트·부츠 가죽은 작은 덩어리라 빠짐)
    lab, n, sz = comps(brown)
    hair = np.isin(lab, np.where(sz >= max(30, sz.max() * 0.35))[0] + 1) if n else brown
    # 눈동자·눈썹·감은 눈 선: 머리 덩어리 밖의 작은 어두운 갈색 조각 중 둘레 40% 이상이 살 → 그대로 (머리색으로 칠하지 않음)
    warm_dark = solid & ((h <= 22) | (h >= 345)) & (s >= 0.25) & (v < 0.55) & ~hair
    lab, n, sz = comps(warm_dark)
    eyes = np.zeros_like(hair)
    # 얼굴 안 이목구비: 살을 닫아 메운 얼굴 덩어리 안, 이마(위 30%)보다 아래의 살 아닌 칸 → 눈·눈썹·입 (그대로)
    face = ndi.binary_fill_holes(ndi.binary_closing(skin, iterations=2))
    fl, fn, fsz = comps(face)
    for i in range(fn):
        if fsz[i] < 40: continue
        f = fl == i + 1
        ys = np.where(f.any(axis=1))[0]
        below = np.zeros_like(f); below[int(ys.min() + 0.3 * (ys.max() - ys.min())):] = True
        eyes |= f & ~skin & below & solid
    for i in range(n):
        if sz[i] > 30: continue
        c = lab == i + 1
        ring = ndi.binary_dilation(c, iterations=2) & ~c
        if (ring & skin).sum() >= 0.4 * ring.sum(): eyes |= c
    # 머리 테두리·머리끝의 진한 갈색 (밝기·채도가 갈색 범위 밖이라 빠지던 점): 머리 둘레 2칸 안의 따뜻한 어두운 칸
    #   (망토 진홍은 채도 0.75 넘어서 안 섞임)
    hair |= ndi.binary_dilation(hair, iterations=2) & solid & ((h <= 20) | (h >= 345)) & (s >= 0.3) & (s <= 0.75) & (v < 0.45) & ~skin & ~eyes
    # 앞머리 끝에 붙은 감은 눈·찡그린 눈 선: 머리 안의 어두운 칸(밝기 0.34 미만) 중 둘레 5×5의 절반 가까이(12칸 이상)가 살 → 눈
    sk5 = ndi.convolve(skin.astype(int), np.ones((5, 5), int), mode='constant')
    lines = hair & (v < 0.34) & (sk5 >= 12)
    eyes |= lines; hair &= ~lines
    hair &= ~eyes
    red = solid & ((h >= 325) | (h <= 6)) & (s >= 0.5) & (v > 0.12) & ~hair & ~eyes   # 망토 가장 어두운 그늘은 보랏빛(색상 338~339)이라 325부터
    # 벌린 입 (포효): 둘레가 살로 둘러싸인 작은 붉은 조각 → 고정
    lab, n, sz = comps(red)
    near_skin = ndi.binary_dilation(skin, iterations=3)
    mouth = []
    for i in range(n):
        if sz[i] > 80: continue
        c = lab == i + 1
        ring = ndi.binary_dilation(c, iterations=2) & ~c
        if (ring & skin).sum() >= 0.3 * ring.sum(): mouth.append(i + 1)
    red &= ~np.isin(lab, mouth)
    cloth = solid & (h >= 200) & (h <= 240) & (s > 0.38) & (v > 0.2)
    gold = solid & (h > 30) & (h < 60) & (s > 0.35)
    dust = (h >= 18) & (h <= 70) & (s > 0.12)   # 흙먼지·가죽 (따뜻한 무채색 갈색) → 고정
    known_fx = fxk > 0 if fxk is not None else np.zeros_like(solid)
    pale_any = solid & (s < 0.4) & (v >= 0.32) & ~skin & ~hair & ~red & ~cloth & ~gold & ~dust & ~known_fx
    # 검날·이펙트(바람 고리·궤적·바람 줄) = 크게 이어진 밝은 덩어리 → 고정. 갑옷 광택은 작은 조각
    bright = pale_any & (v >= 0.7)
    # 외곽선(검은 선) 바로 옆 칸을 떼고 덩어리를 나눔: 바람 줄·고리처럼 외곽선 없는 이펙트가 갑옷(외곽선 있음)에 맞붙어도 따로 갈림
    outline = solid & (v < 0.22)
    lab, n, sz = comps(bright & ~ndi.binary_dilation(outline))
    blade = np.zeros_like(bright); fx = np.zeros_like(bright)
    # 길쭉한 덩어리 = 검날 (35칸 이상) · 아주 큰 덩어리 = 바람 고리·궤적 (300칸 이상). 뭉툭한 건 어깨·가슴·다리 갑옷의 큰 광택 → 갑옷으로
    for i in range(n):
        if sz[i] < 35: continue
        c_ = lab == i + 1
        ys, xs = np.where(c_)
        ev = np.sort(np.linalg.eigvalsh(np.cov(np.vstack([xs, ys]))))
        if ev[0] <= 0 or ev[1] / ev[0] >= 6: blade |= c_
        elif sz[i] >= 300: fx |= c_
    # 검날 그늘 쪽 절반(밝기 0.4~0.7)과 가운데 어두운 능선(0.2~0.32)도 날로: 날에서 이어진 쇠색을 검은 외곽선(0.2 미만)까지,
    #   날 둘레 10칸 안에서만 (넓은 대검 날 폭만큼, 갑옷으로 번지지 않게). 베기 궤적(크기로 잡은 이펙트)에 붙은 날도 같이
    #   (흰·검정 비교 칸의 이펙트는 자리 표로 미리 빠져 있어서 다리·부츠와 맞붙어 번질 일이 없음)
    blade_ok = solid & (s < 0.4) & (v >= 0.2) & ~skin & ~hair & ~red & ~cloth & ~gold & ~dust & ~known_fx
    seed = blade | fx
    sword = ndi.binary_propagation(seed, mask=blade_ok & ndi.binary_dilation(seed, iterations=10)) & pale_any
    steel = pale_any & ~sword
    # 눈 흰자: 얼굴(살) 안의 작은 밝은 조각 → 고정
    lab, n, sz = comps(steel)
    eye = [i + 1 for i in range(n) if sz[i] <= 10 and (near_skin & (lab == i + 1)).all()]
    steel &= ~np.isin(lab, eye)
    # 얼굴 안 회색 칸(눈 둘레·흰자 가장자리): 둘레 7×7에 쇠보다 살이 많으면 갑옷이 아님 → 고정 (갑옷 색이 눈가에 점으로 찍히던 곳)
    k7 = np.ones((7, 7), int)
    for _ in range(2):
        steel &= ~(ndi.convolve(skin.astype(int), k7, mode='constant') > ndi.convolve(steel.astype(int), k7, mode='constant'))
    steel &= ~(ndi.binary_dilation(eyes, iterations=2) & ndi.binary_dilation(skin, iterations=2))   # 눈가 반짝임·땀방울
    # 머리끝이 이마로 내려온 곳의 중간 갈색 (머리와 살 사이 색): 머리 둘레 3칸 안의 따뜻한 칸을 '머리다움'만큼 섞어 칠함
    #   머리다움 = 채도 높고(0.3→0.45) 어두울수록(밝기 0.72→0.6) 1. 이마 피부 그늘(밝기 0.72 이상)은 0이라 그대로
    fr = solid & ~hair & ~eyes & ((h <= 22) | (h >= 350)) & ndi.binary_dilation(hair, iterations=3) & (s >= 0.3) & (v < 0.72)
    fringe = np.where(fr, np.clip((s - 0.3) / 0.15, 0, 1) * np.clip((0.72 - v) / 0.12, 0, 1), 0)
    parts = dict(skin=skin, hair=hair, red=red, cloth=cloth, steel=steel, sword=sword, gold=gold, fringe=fringe)
    for k_ in ('hair', 'red', 'cloth', 'steel'): parts[k_] = parts[k_] & ~known_fx
    parts['fringe'] = np.where(known_fx, 0, fringe)
    parts['sword'] = sword | (known_fx & solid)
    return parts


def _hex(c):
    return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)]) / 255.


def paint(hsv, hsv0, m, color, lo, hi, gloss=0.45, floor=None, gamma=1.0):
    """m 영역을 color로: 원래 밝기 lo~hi를 그 색의 그늘(floor, 기본 42%)~밝은 면(112%)으로. 가장 밝은 칸은 색을 조금 빼 광택
    머리는 floor를 낮게: 금발·은발로 칠해도 머리 그늘·눈썹·감은 눈 선이 어둡게 남음"""
    th, ts, tv = rgb2hsv(_hex(color)[None, None])[0, 0]
    t = np.clip((hsv0[..., 2] - lo) / (hi - lo), 0, 1) ** gamma
    if floor is None:
        floor = 0.42 + 0.35 * np.clip((tv - 0.75) / 0.2, 0, 1) * np.clip(1 - ts / 0.25, 0, 1)
    vv = np.clip(tv * (floor + (1.12 - floor) * t), 0, 1)
    ss = ts * (1 - gloss * np.clip((t - 0.8) / 0.2, 0, 1))
    hsv[..., 0] = np.where(m, th, hsv[..., 0])
    hsv[..., 1] = np.where(m, ss, hsv[..., 1])
    hsv[..., 2] = np.where(m, vv, hsv[..., 2])


def recolor(im, hair_c, steel_c, cloth_c, cape_c, cw=CELL, steel_cells=None, fxmask=None):
    # steel_cells: 갑옷 쇠를 칠할 칸 (None = 모두). 엑스칼리버 빛 칸은 얼굴까지 하얗게 날아가 쇠로 잡히므로 빼고 칠함
    out = im.copy()
    for k in range(im.shape[1] // cw):
        cell = im[:, k * cw:(k + 1) * cw]
        m = masks(cell, None if fxmask is None else fxmask[:, k * cw:(k + 1) * cw])
        _, _, _, hsv0 = hsv_of(cell)
        hsv = hsv0.copy()
        ch = np.zeros(cell.shape[:2], bool)
        fr = m['fringe'] > 0
        for mk, col, lo, hi in (('hair', hair_c, 0.12, 0.72), ('steel', steel_c, 0.32, 1.0),
                                ('cloth', cloth_c, 0.2, 0.85), ('red', cape_c, 0.18, 0.85)):
            if mk == 'steel' and steel_cells is not None and k not in steel_cells: continue
            if col:
                region = m[mk] | fr if mk == 'hair' else m[mk]
                paint(hsv, hsv0, region, col, lo, hi, gloss=0.6 if mk == 'steel' else 0.45,
                      floor=0.16 if mk == 'hair' else None, gamma=0.6 if mk == 'hair' else 1.0)   # 머리: 외곽선만 어둡게, 중간 톤은 밝게
                ch |= m[mk]
        rgb = (hsv2rgb(hsv) * 255 + .5).clip(0, 255).astype(np.uint8)
        o = out[:, k * cw:(k + 1) * cw]
        o[ch, :3] = rgb[ch]
        if hair_c:   # 머리끝 중간 갈색: 머리다움만큼 새 머리색과 섞음
            w = m['fringe'][..., None]
            o[fr, :3] = (o[fr, :3] * (1 - w[fr]) + rgb[fr] * w[fr] + .5).astype(np.uint8)
    return out


def show_masks(im, fxm=None):
    cols = {'skin': (255, 200, 150), 'hair': (255, 0, 200), 'red': (255, 40, 40), 'cloth': (40, 90, 255),
            'steel': (60, 230, 120), 'sword': (255, 255, 0), 'gold': (255, 140, 0)}
    out = np.zeros_like(im); out[..., 3] = 255; out[..., :3] = 30
    for k in range(im.shape[1] // CELL):
        cell = im[:, k * CELL:(k + 1) * CELL]
        m = masks(cell, fxm[:, k * CELL:(k + 1) * CELL] if fxm is not None else None)
        o = out[:, k * CELL:(k + 1) * CELL]
        o[cell[..., 3] > 0, :3] = 90
        for name, c in cols.items():
            o[m[name], :3] = c
    return out


def grid(im, cells, bg, scale=2, per_row=8):
    rows = (len(cells) + per_row - 1) // per_row
    H = im.shape[0]
    g = Image.new('RGBA', (CELL * per_row, H * rows), bg)
    for j, i in enumerate(cells):
        c = Image.fromarray(im[:, i * CELL:(i + 1) * CELL].astype(np.uint8), 'RGBA')
        g.alpha_composite(c, ((j % per_row) * CELL, (j // per_row) * H))
    return g.resize((g.width * scale, g.height * scale), Image.NEAREST)


def main():
    im = np.array(Image.open(SRC).convert('RGBA'))
    fxm = np.array(Image.open(FX_MASK).convert('L')) if os.path.exists(FX_MASK) else None
    mode = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if mode == 'masks':
        grid(show_masks(im, fxm), range(16), (30, 30, 30, 255)).save('_preview_warrior_masks.png')
        return
    if mode == 'preview':
        cells = [0, 4, 12, 9, 14]   # 대기 · 베기 · 포효 · 회전 뒷모습 · 돌진
        rows = [('0 기본', im)] + [(f'{n} {name}', recolor(im, *cols, fxmask=fxm)) for n, name, *cols in VARIANTS]
        H = im.shape[0] * 2
        sheet = Image.new('RGBA', (CELL * len(cells) * 2, H * len(rows)), (0, 0, 0, 0))
        for r, (_, sh) in enumerate(rows):
            bg = (70, 72, 66, 255) if r % 2 == 0 else (86, 88, 80, 255)
            sheet.alpha_composite(grid(sh, cells, bg, per_row=len(cells)), (0, r * H))
        sheet.save('_preview_warrior_variants.png')
        for name, _ in rows: print(name)
        return
    ex = np.array(Image.open(EXCAL_SRC).convert('RGBA'))
    for n, name, *cols in VARIANTS:
        Image.fromarray(recolor(im, *cols, fxmask=fxm), 'RGBA').save(f'assets/sprites/merc/warrior_{n}.webp', 'WEBP', lossless=True)
        Image.fromarray(recolor(ex, *cols, cw=EXCAL_CELL, steel_cells={0}), 'RGBA').save(f'assets/sprites/fx/warrior_excalibur_cast_{n}.webp', 'WEBP', lossless=True)
        print(f'warrior_{n}.webp · warrior_excalibur_cast_{n}.webp  {name}')


if __name__ == '__main__':
    main()

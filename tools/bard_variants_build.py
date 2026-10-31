# 음유시인 외형 0(bard_0.webp)에서 색 조합 변형 시트 만들기 (칸 구성·크기 모두 같음)
# 사용: python tools/bard_variants_build.py   → assets/sprites/merc/bard_1~N.webp
# 규칙: 한 색으로 통일하지 않고 부위마다 다른 색을 넣음 — 베레모 · 조끼 · 바지 · 머리카락
#   피부·셔츠·가죽(가방·장갑·부츠)·류트·시트에 그려진 이펙트는 그대로
#   부위별로 원래 명암(밝기·채도의 비율)을 살린 채 색상만 옮기고, 가운데 밝기·채도를 목표값에 맞춤
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb

SRC = 'assets/sprites/merc/bard_0.webp'
CELL_W = 143
# 베레모가 날아가 머리와 떨어진 쓰러짐 칸: 머리카락 덩어리를 찾을 점 (칸 안 x, y)
HAIR_SEEDS = {8: [(71, 43)], 9: [(38, 64)]}
# 부위별 (색상 도, 채도, 밝기) — 각 부위 가운데 값이 이 값이 되도록 맞춤. None = 그대로
# (번호, 이름, 베레모, 조끼, 바지, 머리카락)
VARIANTS = [
    (1, '남색·진홍', (222, 0.60, 0.40), (354, 0.68, 0.48), (35, 0.18, 0.62), (40, 0.48, 0.80)),
    (2, '장미·하늘', (335, 0.50, 0.62), (204, 0.52, 0.60), (210, 0.10, 0.82), (6, 0.66, 0.62)),
    (3, '하늘·레몬', (200, 0.45, 0.66), (52, 0.60, 0.76), (210, 0.08, 0.84), None),
    (4, '진홍·검정', (355, 0.70, 0.50), (0, 0.0, 0.22), (220, 0.06, 0.48), (225, 0.20, 0.22)),
]


def hsv_of(f):
    hsv = rgb2hsv(f[..., :3] / 255.)
    return hsv, hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]


def part_masks(f, idx):
    a = f[..., 3] > 0
    hsv, h, s, v = hsv_of(f)
    # 옷 초록: 어둡고 채도 중간 (빛의 돔·바람·번개 초록은 밝거나 채도가 높아서 빠짐)
    green = a & (h >= 95) & (h <= 168) & (s > 0.2) & (s < 0.72) & (v > 0.12) & (v < 0.56)
    lab, k = ndi.label(green, np.ones((3, 3)))
    sizes = ndi.sum(green, lab, range(1, k + 1)) if k else []
    beret = lab == (int(np.argmax(sizes)) + 1) if k else np.zeros_like(green)
    # 조끼: 반투명 빛(수호의 선율 돔)이 덮인 칸에서는 빛에 물든 둘레가 같은 초록이라, 불투명하고 반투명 픽셀에 닿지 않은 곳만
    semi = (f[..., 3] > 0) & (f[..., 3] < 255)
    solid = (f[..., 3] == 255) & ~ndi.binary_dilation(semi)
    vest = green & ~beret & solid
    pants = a & (h >= 195) & (h <= 250) & (s > 0.15) & (s < 0.6) & (v > 0.15) & (v < 0.62)
    # 바지 안쪽에 채도가 낮거나 아주 어두운 남색 점이 섞여 있어 밝은 바지로 바꾸면 얼룩처럼 남음 → 바지 덩어리 안의 구멍도 바지로
    #   (검은 외곽선은 그대로: 바지 덩어리를 닫아서 생긴 안쪽만, 차가운 색이거나 무채색인 곳만)
    cool = (h >= 180) & (h <= 260) | (s < 0.15)
    pants |= a & ndi.binary_closing(pants, np.ones((3, 3)), iterations=2) & cool & (v > 0.08) & (v < 0.62)
    # 머리카락: 베레모에 닿은 갈색 덩어리 (검은 외곽선에서 끊겨 가방·류트와 나뉨), 베레모 바로 아래 범위만
    #   피부(연하고 밝음)는 빠지고, 불꽃은 채도가 높아서 빠짐
    skin = (s < 0.36) & (v > 0.7)
    warm = a & ((h <= 32) | (h >= 340)) & (s > 0.25) & (s < 0.8) & (v > 0.24) & (v < 0.75) & ~skin
    ys, xs = np.nonzero(beret)
    if len(ys):
        box = np.zeros_like(warm)
        box[max(0, ys.min()):ys.max() + 30, max(0, xs.min() - 8):xs.max() + 3] = True  # 오른쪽(얼굴 쪽)은 좁게: 치켜든 류트 머리가 베레모에 닿음
        warm_in = warm & box
    else:
        warm_in = warm
    lab2, _ = ndi.label(warm_in, np.ones((3, 3)))
    ids = set(np.unique(lab2[ndi.binary_dilation(beret, iterations=2) & warm_in]))
    hair = np.isin(lab2, [i for i in ids if i > 0])
    if idx in HAIR_SEEDS:
        loose = a & ((h <= 32) | (h >= 340)) & (s > 0.25) & (s < 0.9) & (v > 0.24) & (v < 0.75) & ~skin  # 이 칸 머리는 채도가 더 높음
        lab3, _ = ndi.label(loose, np.ones((3, 3)))
        hair = np.isin(lab3, [lab3[y, x] for x, y in HAIR_SEEDS[idx] if lab3[y, x] > 0])
    # 덩어리는 넉넉하게 잡아 이어 붙이고, 실제로 칠하는 건 머리카락 색만: 피부 그늘(채도 낮음)·눈동자·볼(붉은 쪽 색상)은 빠짐
    hair_col = a & (h >= 5) & (h <= 30) & (s >= 0.45) & (s < 0.8) & (v >= 0.2) & (v < 0.78)  # 채도·밝기가 높은 불꽃은 빠짐
    if len(ys) and idx not in HAIR_SEEDS:
        hair_col[:(ys.min() + ys.max()) // 2] = False  # 베레모 위쪽 절반 높이보다 위는 머리가 아님 (치켜든 류트 머리)
    #   피부에 둘러싸인 곳(입·볼 그늘)도 빠짐
    face = (h <= 40) & (s < 0.5) & (v > 0.7)
    hair_col &= ~(ndi.binary_fill_holes(face) & ~face)
    hair &= hair_col
    # 어깨까지 내려온 뒷머리: 찾은 머리에 머리카락 색으로 이어진 곳을 조금 더 넓은 범위(아래·뒤쪽)까지
    #   (쓰러짐 칸은 찾은 머리 둘레만) · 1px 외곽선 너머 가닥까지 잇기 위해 2px 넓혀서 닿은 덩어리
    ext = np.zeros_like(warm)
    if len(ys) and idx not in HAIR_SEEDS:
        ext[max(0, ys.min()):ys.max() + 40, max(0, xs.min() - 14):xs.max() + 3] = True
    elif hair.any():
        hy, hx = np.nonzero(hair)
        ext[max(0, hy.min() - 4):hy.max() + 5, max(0, hx.min() - 4):hx.max() + 5] = True
    lab4, _ = ndi.label(hair_col & ext, np.ones((3, 3)))
    hair |= np.isin(lab4, [i for i in np.unique(lab4[ndi.binary_dilation(hair, iterations=2)]) if i > 0])
    return {'beret': beret, 'vest': vest, 'pants': pants, 'hair': hair & ~beret, 'solid': solid}


def base_medians(im):
    # 대기 자세에서 부위별 가운데 채도·밝기 (모든 칸에 같은 배율을 써야 칸마다 색이 흔들리지 않음)
    f = im[:, :CELL_W]
    m = part_masks(f, 0)
    _, _, s, v = hsv_of(f)
    return {k: (np.median(s[mk]), np.median(v[mk])) for k, mk in m.items() if k != 'solid'}


def recolor(f, idx, spec, med):
    masks = part_masks(f, idx)
    hsv, h, s, v = hsv_of(f)
    out = f.copy()
    # 초록 기가 도는 검은 외곽선: 베레모·조끼 바로 둘레만 그 부위 색상으로 (어두운 정도는 그대로)
    dark_green = (f[..., 3] > 0) & (h >= 85) & (h <= 170) & (s > 0.15) & (v <= 0.2)
    for key, target in zip(('beret', 'vest', 'pants', 'hair'), spec):
        m = masks[key]
        if target is None or not m.any(): continue
        th, ts, tv = target
        if key in ('beret', 'vest'):
            # 조끼 둘레는 빛에 물든 픽셀을 피함 (베레모는 돔 안에서도 둘레가 외곽선뿐이라 불투명이면 바꿈)
            rim = dark_green & ndi.binary_dilation(m, iterations=2) & ~m & (masks['solid'] if key == 'vest' else f[..., 3] == 255)
            if rim.any():
                rgb = hsv2rgb(np.stack([np.full(rim.sum(), th / 360.), hsv[..., 1][rim], hsv[..., 2][rim]], -1)[None])[0]
                out[rim, :3] = (rgb * 255 + .5).clip(0, 255).astype(np.uint8)
        ms, mv = med[key]
        nh = np.full(m.sum(), th / 360.)
        ns = np.clip(hsv[..., 1][m] * ts / ms, 0, 1)
        nv = np.clip(hsv[..., 2][m] * tv / mv, 0, 1)
        rgb = hsv2rgb(np.stack([nh, ns, nv], -1)[None])[0]
        out[m, :3] = (rgb * 255 + .5).clip(0, 255).astype(np.uint8)
    return out


def main():
    im = np.array(Image.open(SRC).convert('RGBA'))
    n = im.shape[1] // CELL_W
    med = base_medians(im)
    for num, label, *spec in VARIANTS:
        sheet = np.hstack([recolor(im[:, i * CELL_W:(i + 1) * CELL_W], i, spec, med) for i in range(n)])
        Image.fromarray(sheet, 'RGBA').save(f'assets/sprites/merc/bard_{num}.webp', 'WEBP', lossless=True)
        print(f'bard_{num}.webp  {label}')


if __name__ == '__main__':
    main()

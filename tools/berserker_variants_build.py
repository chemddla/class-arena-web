# 광전사 외형 0(berserker_0*.webp)에서 색 조합 변형 시트 만들기 (칸 구성·크기 모두 같음)
# 사용: python tools/berserker_variants_build.py           → assets/sprites/merc/berserker_<번호>[_rage|_undying|_rage_undying].webp
#       python tools/berserker_variants_build.py preview <저장 경로>   → 후보 미리보기 한 장
#   berserker_build.py로 0번 시트를 다시 만들면 이것도 다시 돌림
# 규칙: 피부는 그대로. 부위마다 다른 색 — 머리털 · 털가죽(망토·어깨 가죽·장화·도끼 자루) · 문신(얼굴·팔 파란 물감) · 허리천
#   해골·이빨·도끼 날·검은 윤곽·이펙트(불길·X자·흙먼지)는 그대로
#   부위별로 원래 명암(밝기·채도의 비율)을 살린 채 색상만 옮기고, 가운데 밝기·채도를 목표값에 맞춤 (음유시인 변형과 같은 방법)
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb

SRC = 'assets/sprites/merc/berserker_0.webp'
COUNT = 22
HAIR_BAND = 0.31  # 머리털 꼭대기~발 중 위쪽 이만큼이 머리털 (0.35면 어깨 털가죽 끝이 머리색으로 물들었음)
SKIN_MAX_HUE = 23  # 살 덩어리 평균 색상이 이 도보다 노란 쪽이면 털가죽 조각
OUTLINE_V = 0.12  # 이보다 어두운 픽셀 = 검은 윤곽 (색을 바꾸지 않음). 0.2로 두면 망토의 어두운 털까지 윤곽으로 남아 얼룩졌음
# (번호, 이름, 머리털, 털가죽, 문신, 허리천) — (색상 도, 채도, 밝기). None = 그대로
VARIANTS = [
    (1, '설원 늑대', (35, 0.06, 0.86), (215, 0.07, 0.66), None, None),
    (2, '핏빛 전사', (0, 0.25, 0.16), (355, 0.55, 0.36), None, (0, 0.10, 0.80)),
    (3, '사막 약탈자', (30, 0.35, 0.76), (35, 0.42, 0.62), None, (25, 0.30, 0.70)),
    (4, '붉은 머리 바이킹', (16, 0.78, 0.52), (28, 0.22, 0.34), None, None),
    (5, '흑요석', (222, 0.18, 0.15), (220, 0.12, 0.27), None, (215, 0.06, 0.74)),
]


def part_masks(f):
    a = f[..., 3] > 200
    hsv = rgb2hsv(f[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    # 피부: 밝은 살색 + 그 둘레에 이어진 어두운 살색 그늘(채도 중간·밝기 0.4 넘음)까지
    skin = a & (R > 120) & (R > G + 20) & (G > B) & (R - B < 130)
    # 얼굴 옆 어깨 털가죽의 밝은 황갈색 조각은 살색과 비슷해서 살로 잡혀 원래 색으로 남았음 → 덩어리 평균이 노란 쪽(색상 23도 넘음)이면 털
    #   (살은 붉은 쪽 6~19도, 털 조각은 28~33도. 크기로 가르면 도끼 쥔 손(11~23px)까지 털이 됐음)
    lab, n = ndi.label(skin)
    if n:
        mh = ndi.mean(h, lab, range(1, n + 1))
        skin = np.isin(lab, 1 + np.where(mh <= SKIN_MAX_HUE)[0])
    skin_tone = a & (h >= 0) & (h <= 32) & (s > 0.2) & (s < 0.6) & (v > 0.4)
    for _ in range(3): skin |= skin_tone & ndi.binary_dilation(skin)
    # 그늘진 살 (다리·팔 안쪽): 붉은 기가 도는 어두운 살색(색상 18도 아래)도 살에 이어져 있으면 살 (털은 21~30도로 노란 쪽)
    shade = a & ((h <= 18) | (h >= 345)) & (s > 0.15) & (s < 0.62) & (v > 0.28)
    for _ in range(4): skin |= shade & ndi.binary_dilation(skin)  # 붉은 기 도는 어두운 털까지 번지지 않게 덜 어두운 그늘만, 4겹까지
    # 문신: 채도 높은 파랑만 (X자 이펙트·흰 빛의 옅은 파란 기운은 빠짐)
    paint = a & (h >= 170) & (h <= 235) & (s > 0.35) & (v > 0.22) & (v < 0.95)
    # 갈색: 어두운 털·머리털·가죽 (해골·이빨의 연한 그늘은 밝아서 빠짐)
    brown = a & ((h <= 45) | (h >= 345)) & (s > 0.16) & (v > 0.08) & (v < 0.55) & ~skin
    dark_brown = brown & (v <= OUTLINE_V)  # 갈색 기운이 있는 아주 어두운 픽셀 (뒷머리 그늘·망토 깊은 곳·윤곽)
    # 검은 윤곽(아주 어두운 픽셀)은 밝기를 옮기지 않음 — 밝은 색으로 바꾸면 윤곽이 사라져 그림이 깨져 보였음
    brown &= v > OUTLINE_V
    # 털 사이에 끼어 채도가 낮은 털·그늘 픽셀도 털로 (빠지면 밝은 색으로 바꿨을 때 갈색 얼룩으로 남았음)
    #   털 덩어리를 닫아서 생긴 안쪽 중 윤곽·피부·문신이 아니고 너무 밝지 않은 곳 (해골·도끼 날 하이라이트는 밝아서 빠짐)
    inner = ndi.binary_closing(brown, np.ones((3, 3)), iterations=2) & a & ~skin & ~paint & (v > OUTLINE_V) & (v < 0.6) & (s < 0.45)
    brown |= inner
    ys = np.where(a.any(axis=1))[0]
    top, bot = (ys.min(), ys.max()) if len(ys) else (0, 1)
    # 머리털 범위: 몸의 위쪽 35% — 위쪽 끝은 그림 맨 위가 아니라 가장 위의 큰 갈색 덩어리(머리털) 꼭대기
    #   (X자·치켜든 도끼가 그림을 위로 늘린 칸에서 범위가 위로 밀려 머리털 아래쪽이 털가죽 색으로 바뀌었음)
    lab, n = ndi.label(brown)
    htop = top
    if n:
        sizes = ndi.sum(brown, lab, range(1, n + 1))
        big = [i + 1 for i in range(n) if sizes[i] >= 40]
        if big: htop = min(np.where((lab == i).any(axis=1))[0].min() for i in big)
    band = np.zeros(a.shape, bool); band[:htop + int((bot - htop) * HAIR_BAND)] = True
    hair = brown & band
    fur = brown & ~band
    # 아주 어두운 갈색: 머리털·털가죽 쪽에 붙은 것만 (얼굴·몸 윤곽은 빼고). 밝은 색으로 바꿀 때 밝기는 그대로 두고 색만 입힘
    #   (안 바꾸면 하얀·모래색 머리에서 뒷머리 그늘이 갈색으로 남았음)
    near_h, near_f = ndi.binary_dilation(hair, iterations=2), ndi.binary_dilation(fur, iterations=2)
    hair_dark = dark_brown & near_h & ~ndi.binary_dilation(skin, iterations=1)
    fur_dark = dark_brown & near_f & ~hair_dark & ~ndi.binary_dilation(skin, iterations=1)
    # 허리천: 몸 아래쪽 절반의 크림색 큰 덩어리 (해골·이빨·X자는 작거나 위쪽이라 빠짐)
    cream = a & (s < 0.25) & (v > 0.66) & (h >= 20) & (h <= 60) & ~band
    lab, n = ndi.label(cream)
    cloth = np.zeros_like(cream)
    if n:
        sizes = ndi.sum(cream, lab, range(1, n + 1))
        low = np.zeros(a.shape, bool); low[top + int((bot - top) * 0.5):] = True
        for i in np.argsort(-sizes)[:2]:
            if sizes[i] >= 12 and (lab == i + 1)[low].any(): cloth |= lab == i + 1
    return {'hair': hair, 'fur': fur, 'paint': paint, 'cloth': cloth, 'hair_dark': hair_dark, 'fur_dark': fur_dark}


def recolor(f, mask, target):
    if target is None or not mask.any(): return
    th, ts, tv = target
    hsv = rgb2hsv(f[..., :3] / 255.)
    s, v = hsv[..., 1], hsv[..., 2]
    ms, mv = np.median(s[mask]), np.median(v[mask])
    out = hsv.copy()
    out[..., 0] = np.where(mask, th / 360., hsv[..., 0])
    out[..., 1] = np.where(mask, np.clip(s * (ts / max(ms, 1e-3)), 0, 1), s)
    # 밝기: 원래 밝기 비율대로 옮겨 털 결 사이 어두운 선이 밝은 색에서도 어둡게 남게 하고 (더하기로 옮기면 선이 같이 밝아져 결이 사라졌음),
    #   0.8 넘는 쪽만 부드럽게 눌러 하얗게 날아가지 않게 함
    x = v * (tv / max(mv, 1e-3))
    x = np.where(x > 0.8, 0.8 + (x - 0.8) * 0.35, x)
    out[..., 2] = np.where(mask, np.clip(x, 0, 0.97), v)
    if tv > 0.5:
        # 밝은 색으로 바꿀 때 윤곽 다듬기 — 원본에서 윤곽이어야 하는 곳을 찾아 원본 밝기 그대로 둠 (색만 새 색):
        #   주변(5×5)보다 확실히 어두운 픽셀 = 털 결·옷·얼굴 둘레의 선, 그림 바깥(투명)과 닿은 가장자리
        #   (비율로 밝히면 이 선들이 같이 밝아져 옷·얼굴 둘레 테두리가 끊겨 보였음)
        a = f[..., 3] > 0
        local = ndi.uniform_filter(np.where(a, v, 0), 5) / np.maximum(ndi.uniform_filter(a.astype(float), 5), 1e-3)
        line = mask & ((v < local - 0.08) | ndi.binary_dilation(~a)) & (v < 0.42)
        out[..., 2] = np.where(line, np.clip(v * 1.15, 0, 0.42), out[..., 2])
        out[..., 1] = np.where(line, np.clip(np.maximum(s, 0.2) * 0.8, 0, 0.5), out[..., 1])
    rgb = hsv2rgb(out) * 255
    f[..., :3] = np.where(mask[..., None], rgb, f[..., :3])


def face_mask(cell):
    # 얼굴 (원본 그대로 둘 곳): 눈에 닿은 살 덩어리 + 그 안의 구멍(눈·눈썹·문신·입) + 둘레 1px 윤곽
    #   눈은 광폭 시트를 만들 때와 같은 find_eyes로 찾음 (칸마다 머리 높이·각도가 달라도 얼굴만 잡힘)
    from berserker_build import find_eyes
    f = cell.astype(float)
    a = f[..., 3] > 0
    ys, xs = np.where(a)
    if not len(ys): return np.zeros(a.shape, bool)
    y0, x0 = ys.min(), xs.min()
    try:
        e = find_eyes(f[y0:ys.max() + 1, x0:xs.max() + 1])
    except Exception:
        e = None
    face = np.zeros(a.shape, bool)
    if not e or not e[0].any(): return face
    eyes = np.zeros(a.shape, bool); eyes[y0:y0 + e[0].shape[0], x0:x0 + e[0].shape[1]] = e[0]
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    skin = a & (R > 120) & (R > G + 20) & (G > B) & (R - B < 130)
    lab, n = ndi.label(skin)
    near = ndi.binary_dilation(eyes, iterations=3)
    ids = np.unique(lab[near & skin])
    face = np.isin(lab, ids[ids > 0]) | eyes
    face = ndi.binary_fill_holes(ndi.binary_closing(face, iterations=2))
    return ndi.binary_dilation(face) & a


def bone_mask(cell):
    # 해골·뼈 (원본 그대로 둘 곳): 연한 크림색 덩어리 + 그 안의 그늘·눈구멍 + 둘레 1px (그늘이 털로 잡혀 해골이 털 색으로 물들었음)
    #   허리천은 아래쪽 절반의 큰 덩어리라 따로 칠하고, 해골은 위쪽 절반에서만 찾음
    f = cell.astype(float)
    a = f[..., 3] > 0
    hsv = rgb2hsv(f[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    bone = a & (v > 0.68) & (s < 0.3) & (h >= 20) & (h <= 60)
    ys = np.where(a.any(axis=1))[0]
    if not len(ys): return np.zeros(a.shape, bool)
    bone[ys.min() + int((ys.max() - ys.min()) * 0.6):] = False
    lab, n = ndi.label(bone)
    if not n: return bone
    sz = ndi.sum(bone, lab, range(1, n + 1))
    bone = np.isin(lab, 1 + np.where(sz >= 12)[0])
    return ndi.binary_dilation(ndi.binary_fill_holes(ndi.binary_closing(bone, iterations=2))) & a


FIRE_FRAMES = (9, 10, 20, 21)  # 광폭화·불사의 분노 시전 칸: 불길(채도 높은 빨강·자홍)은 털로 보지 않음


def cell_masks(cell, idx=None):
    # 부위 나누기는 평소 시트 칸에서 함 (광폭·불사 시트는 같은 자리에 같은 그림이라 이 마스크를 그대로 씀)
    f = cell.astype(float)
    m = part_masks(f)
    keep = face_mask(cell) | bone_mask(cell)
    if idx in FIRE_FRAMES:
        hsv = rgb2hsv(f[..., :3] / 255.)
        keep |= ndi.binary_dilation(hsv[..., 1] > 0.62)
    for k in m: m[k] = m[k] & ~keep
    return m


def variant_cell(cell, var, masks=None):
    f = cell.astype(float).copy()
    m = masks if masks is not None else cell_masks(cell)  # 얼굴은 원본 그대로 (칸마다 얼굴 일부가 머리털·털 색으로 바뀌었음)
    _, _, hair, fur, paint, cloth = var
    for k, t in (('hair', hair), ('fur', fur), ('paint', paint), ('cloth', cloth)):
        recolor(f, m[k], t)
    # 밝은 머리털·털가죽: 아주 어두운 갈색 그늘은 밝기는 두고 새 색상으로만 물들임 (갈색으로 남지 않게)
    for k, t in (('hair_dark', hair), ('fur_dark', fur)):
        if t is None or t[2] <= 0.5 or not m[k].any(): continue
        hsv = rgb2hsv(f[..., :3] / 255.)
        hsv[..., 0] = np.where(m[k], t[0] / 360., hsv[..., 0])
        hsv[..., 1] = np.where(m[k], np.minimum(hsv[..., 1], max(t[1], 0.12)), hsv[..., 1])
        f[..., :3] = np.where(m[k][..., None], hsv2rgb(hsv) * 255, f[..., :3])
    return f.clip(0, 255).astype(np.uint8)


def preview(out_path):
    sheet = np.array(Image.open(SRC).convert('RGBA'))
    cw = sheet.shape[1] // COUNT
    frames = [0, 1, 5, 8, 11, 19]
    rows = [[sheet[:, i * cw:(i + 1) * cw] for i in frames]]
    for var in VARIANTS:
        rows.append([variant_cell(sheet[:, i * cw:(i + 1) * cw], var) for i in frames])
    H = sheet.shape[0]
    crop = (30, 70, cw - 15, H)  # 몸 근처만
    w, hh = crop[2] - crop[0], crop[3] - crop[1]
    canvas = Image.new('RGBA', (w * len(frames), hh * len(rows)), (40, 140, 60, 255))
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            canvas.alpha_composite(Image.fromarray(cell, 'RGBA').crop(crop), (c * w, r * hh))
    canvas = canvas.crop((0, 0, canvas.size[0], canvas.size[1]))
    canvas.resize((canvas.size[0] * 2, canvas.size[1] * 2), Image.NEAREST).save(out_path)


SHEETS = ('', '_rage', '_undying', '_rage_undying')


def build():
    base = np.array(Image.open(SRC).convert('RGBA'))
    cw = base.shape[1] // COUNT
    masks = [cell_masks(base[:, i * cw:(i + 1) * cw], i) for i in range(COUNT)]
    for suffix in SHEETS:
        src = np.array(Image.open(f'assets/sprites/merc/berserker_0{suffix}.webp').convert('RGBA'))
        for var in VARIANTS:
            out = src.copy()
            for i in range(COUNT):
                out[:, i * cw:(i + 1) * cw] = variant_cell(src[:, i * cw:(i + 1) * cw], var, masks[i])
            Image.fromarray(out, 'RGBA').save(f'assets/sprites/merc/berserker_{var[0]}{suffix}.webp', 'WEBP', lossless=True)
        print('built', suffix or 'normal')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        build()
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':
        preview(sys.argv[2])

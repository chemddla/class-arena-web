# 성기사 시크릿 레어 1 (금발 천사 날개·금빛 갑옷·십자 방패·전쟁 망치) 샘플 → assets/sprites/merc/paladin_sr1.webp
# 사용: python tools/paladin_sr1_build.py
# 샘플 (흰 배경, assets/sprites/fx/samples/):
#   paladin_sr1_sheet_src.png (862×513): "1. 대기" 1칸 · "2. 걷기" 4칸 · "3. 일반공격" 4칸 (준비 → 치켜듦 → 내리치기 + 은빛 궤적 → 마무리) · "4. 피격" 1칸
#     (맨 아래에 다음 줄 머리가 조금 잘려 들어와 있음 → 버림, 왼쪽 줄 제목 글씨도 버림. 공격 1칸과 피격 칸은 붙어 있어 391행에서 나눔)
#   paladin_sr1_down_a_src.png (170×122): 쓰러짐 1 (무릎 꿇고 이를 악묾)
#   paladin_sr1_down_b_src.png (261×113): 쓰러짐 2 (뒤로 누움, 망치는 떨어져 바닥에 — 망치 조각도 남김)
#   paladin_sr1_consec_src.png (1024×1024, 원본 webp를 png로): 축성 (서서 눈 감고 두 손 모아 기도, 망치는 세워 기댐). 크게 그려 와서
#     머리 꼭대기~발 키(약 750px)를 대기와 같게 → 대기 배율 × 123/750
#   paladin_sr1_charge_src.png (1024×1024, 원본 webp를 png로): 성스러운 돌격 (방패를 앞세워 날개 펴고 돌진, 바람 줄·금빛 불꽃·흙먼지).
#     얼굴·머리 폭을 축성 칸에 맞춰 축성 배율 × 1.1. 다리를 앞뒤로 벌려서 기준점은 두 발 가운데(샘플 x 390)로 직접
# 칸 순서: 0 대기 · 1~4 걷기 · 5~8 기본 공격 · 9 피격 · 10~11 쓰러짐 · 12 축성 · 13 성스러운 돌격
# 크기: 대기의 머리 꼭대기~발 키를 TARGET_H(성기사 0번과 같은 110)로. 같은 장(sheet)의 다른 칸도 같은 배율,
#   쓰러짐 두 장은 따로 그려 와서 얼굴·방패 폭으로 맞춘 배율(DOWN_K)
# 흰 배경 지우기는 paladin_build.py와 같음: 가장자리에서 이어진 흰 픽셀만 배경, 배경과 섞인 2px 테두리는 흰색을 빼서 투명도·색을 되살림
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/paladin_sr1_'
OUT = 'assets/sprites/merc/paladin_sr1.webp'
TARGET_H = 110
DOWN_K = 1.0   # 쓰러짐 샘플 배율 (시트 기준) — 얼굴·방패 폭이 시트 칸과 같아서 그대로
# 연한 은빛 공격 궤적: 흰 배경과 거의 같은 색이라 배경으로 지워짐 → 이 상자(시트 좌표) 안은 흰색에서 떨어진 만큼 반투명으로 살림
FOOTX = {'charge': 390}
GAP = {'charge': [(150, 680, 360, 930)]}   # 갇힌 흰 배경을 지울 상자 (샘플 x0, y0, x1, y1): 망치 자루·다리·흙먼지 사이   # 발 가운데를 샘플 x로 직접
SOFT = {'sheet': [(597, 258, 652, 370)]}

# (칸 이름, 샘플, 상자 (x0, y0, x1, y1), 배율 보정)
FRAMES = [
    ('idle', 'sheet', (112, 0, 290, 129), 1),
    ('walk0', 'sheet', (118, 129, 292, 258), 1), ('walk1', 'sheet', (295, 122, 470, 255), 1),
    ('walk2', 'sheet', (470, 122, 645, 255), 1), ('walk3', 'sheet', (645, 122, 830, 255), 1),
    ('atk0', 'sheet', (118, 258, 298, 391), 1), ('atk1', 'sheet', (295, 255, 470, 405), 1),
    ('atk2', 'sheet', (470, 258, 655, 405), 1), ('atk3', 'sheet', (655, 258, 840, 405), 1),
    ('hurt', 'sheet', (118, 391, 300, 513), 1),
    ('down0', 'down_a', None, 'down'), ('down1', 'down_b', None, 'down'),
    ('consec', 'consec', None, 123 / 750),
    ('charge', 'charge', None, 123 / 750 * 1.1),
]


def load(name, box):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    if box:
        x0, y0, x1, y1 = box; im = im[y0:y1, x0:x1]
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), constant_values=255)   # 상자 가장자리에 걸친 칸도 배경이 가장자리와 이어지게
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    if name in GAP:
        gbox = np.zeros_like(bg)
        for x0, y0, x1, y1 in GAP[name]: gbox[y0 + 2:y1 + 2, x0 + 2:x1 + 2] = True
        ids = np.arange(1, n + 1)
        bg |= np.isin(lab, ids[(ndi.sum(white & gbox, lab, ids) >= 30) & (ndi.mean(im.min(axis=2), lab, ids) > 238)]) & gbox
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)
    ox, oy = (box[0], box[1]) if box else (0, 0)
    for x0, y0, x1, y1 in SOFT.get(name, ()):
        sx0, sy0, sx1, sy1 = x0 - ox + 2, y0 - oy + 2, x1 - ox + 2, y1 - oy + 2   # +2 = 위에서 덧댄 여백
        if sx1 <= 2 or sy1 <= 2 or sx0 >= im.shape[1] - 2 or sy0 >= im.shape[0] - 2: continue
        sl = (slice(max(sy0, 0), sy1), slice(max(sx0, 0), sx1))
        soft = np.clip((250 - im[sl].min(axis=2)) / 90, 0, 1) ** 0.8
        soft = np.where(soft < 0.08, 0, soft)
        a[sl] = np.maximum(a[sl], soft)
        rim[sl] |= (soft > 0) & (soft < 1)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    # 큰 덩어리(몸)와 그 근처 조각(공격 궤적·떨어진 망치)만 남김 — 상자에 걸린 이웃 칸·글씨는 상자 가장자리에 닿은 작은 조각이라 지움
    m = a > 0.3
    lab, n = ndi.label(ndi.binary_dilation(m))
    sz = ndi.sum(m, lab, range(1, n + 1))
    big = int(np.argmax(sz)) + 1
    keep = [big]
    by, bx = ndi.find_objects(lab)[big - 1]
    for i, s in enumerate(ndi.find_objects(lab)):
        if i + 1 == big or sz[i] < 40: continue
        sy, sx = s
        touches = sy.start <= 2 or sx.start <= 2 or sy.stop >= lab.shape[0] - 2 or sx.stop >= lab.shape[1] - 2
        if not touches and sy.start < by.stop and sy.stop > by.start: keep.append(i + 1)   # 몸과 높이가 겹치는 조각만
    a = np.where(np.isin(lab, keep), a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    body = np.isin(lab, [big])[ys.min():ys.max() + 1, xs.min():xs.max() + 1] & (rgba[..., 3] > 0)
    foot = np.where(body[int(body.shape[0] * 0.92):].any(axis=0))[0].mean()   # 발 가운데 (몸 아래 8%)
    if name in FOOTX: foot = FOOTX[name] + 2 - xs.min()   # +2 = 덧댄 여백
    return rgba, foot


def main():
    idle, _ = load('sheet', FRAMES[0][2])
    k0 = TARGET_H / idle.shape[0]   # 대기는 머리 꼭대기가 가장 높음 (날개 끝은 머리보다 낮음)
    pieces = []
    for name, src, box, k in FRAMES:
        rgba, foot = load(src, box)
        sc = k0 * (DOWN_K if k == 'down' else k)
        if name == 'down1': foot = rgba.shape[1] * 0.45   # 누운 칸은 몸 가운데쯤을 기준점으로
        p = shrink(rgba, sc)
        pieces.append((name, p, foot * sc))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{sc:.3f} → {p.shape[1]}x{p.shape[0]}')
    L = max(int(np.ceil(c)) for _, _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 4
    H = max(p.shape[0] for _, p, _ in pieces) + 5
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = H - 2 - p.shape[0]
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'paladin_sr1 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)}')


if __name__ == '__main__':
    main()

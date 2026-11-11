# 검사 전용 샘플(검은 머리 묶음·회색 머리띠·남색 도복·검은 하카마, 흰 배경) → 캐릭터 시트 assets/sprites/merc/swordsman_0.webp
# 사용: python tools/swordsman_build.py   (샘플은 assets/sprites/fx/samples/swordsman_*_src.png, 동작 샘플이 오는 대로 FRAMES에 늘림)
# 칸 순서: 0 대기 (오른손을 칼자루에 얹고 왼손으로 칼집을 잡은 발도 자세)
# 크기 통일: 대기 자세 몸 키(머리털 끝~발, 샘플 px)를 TARGET_H로 줄임. 다른 동작은 대기와 같은 배율('idle')로 줄여 얼굴 크기를 맞춤
# 샘플 정리:
#   - 대기 샘플(768×1024)은 도트 그림을 흐리게 키운 것, 테두리 없음
#   - 피부가 첫 샘플보다 어두워서 살색만 밝힘 (SKIN)
#   - 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움 (짚신·옷깃의 밝은 회색은 검은 외곽선 안쪽이라 남음)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/swordsman_'
OUT = 'assets/sprites/merc/swordsman_0.webp'
TARGET_H = 86   # 대기 자세 머리 묶음 끝~발 → 게임 칸 키 (격투가와 같은 키, 연결할 때 standH·topH로 맞춤)

CARD = {}   # (x0, x1, y0, y1): 샘플 테두리 잘라 냄
WHITE_MIN = {}
CUT = {}   # 지울 상자 (x0, x1, y0, y1)
SKIN = {'idle'}   # 피부를 첫 샘플(밝은 살색)만큼 밝힘: 받은 대기 샘플은 피부가 어두운 갈색


def lighten_skin(rgba):   # 살색 픽셀만 밝기에 따라 더함. 기준 두 색: 그림자 (140,86,70)→(176,121,103) · 바탕 (213,133,94)→(243,184,150)
    rgb = rgba[..., :3].astype(float)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    warm = (r - b > 35) & (r > g) & (g > b)
    t = np.clip((r - 140) / 73, 0, 1.2)[..., None]
    add = np.array([36, 35, 33]) + t * (np.array([30, 51, 56]) - np.array([36, 35, 33]))
    w = (np.clip((r - 90) / 40, 0, 1) * warm)[..., None]   # 외곽선 가까운 어두운 갈색은 덜 바꿈
    rgba = rgba.copy()
    rgba[..., :3] = np.clip(rgb + add * w, 0, 255)
    return rgba


def load(name, pick=0):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    if name in CARD:
        x0, x1, y0, y1 = CARD[name]; im = im[y0:y1, x0:x1]
    wm = WHITE_MIN.get(name, 222)
    white = (im.min(axis=2) > wm) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    for x0, x1, y0, y1 in CUT.get(name, ()): bg[y0:y1, x0:x1] = True
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)   # 흐린 외곽: 흰 배경과 섞인 만큼 반투명
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
    sz = ndi.sum(m, lab, range(1, n + 1))
    if pick == 'big':
        a = np.where(lab == 1 + int(np.argmax(sz)), a, 0)
    else:
        bigs = [i + 1 for i in range(n) if sz[i] >= sz.max() * 0.3]
        bigs.sort(key=lambda i: np.where(lab == i)[1].mean())
        a = np.where(lab == bigs[pick], a, 0)
    a = np.where(a < 0.12, 0, a)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 127
    body = np.where(k.any(axis=1))[0]
    foot = np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()
    return rgba, foot, body.max() - body.min() + 1


# (샘플 이름, 칸 이름, 배율: 'H' = 몸 키를 TARGET_H로 · 칸 이름 = 그 칸 배율 그대로, 샘플 안 몇 번째 그림(왼쪽부터))
FRAMES = [
    ('idle', 'idle', 'H', 0),
]
FOOTX = {}   # 칸 이름 → 발 가운데 (자른 그림 기준 px)


def main():
    pieces, scale = [], {}
    for src, name, k, pick in FRAMES:
        rgba, foot, bh = load(src, pick)
        if src in SKIN: rgba = lighten_skin(rgba)
        if name in FOOTX: foot = FOOTX[name]
        sc = scale[k] if k != 'H' else TARGET_H / bh
        scale[name] = sc
        p = shrink(rgba, sc)
        pieces.append((name, p, foot * sc))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} 키 {bh} ×{sc:.3f} → {p.shape[1]}x{p.shape[0]}  발 {foot:.0f}')
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
    print(f'swordsman_0 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)}')


if __name__ == '__main__':
    main()

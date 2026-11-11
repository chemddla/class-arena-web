# 검사 전용 샘플(검은 머리 묶음·회색 머리띠·남색 도복·검은 하카마, 흰 배경) → 캐릭터 시트 assets/sprites/merc/swordsman_0.webp
# 사용: python tools/swordsman_build.py   (샘플은 assets/sprites/fx/samples/swordsman_*_src.png, 동작 샘플이 오는 대로 FRAMES에 늘림)
# 칸 순서: 0 대기 (오른손을 칼자루에 얹고 왼손으로 칼집을 잡은 발도 자세, 맨발에 조리) · 1 피격 (몸을 젖히며 소리침) · 2 쓰러짐 1 (앞으로 숙이며 무너짐) · 3 쓰러짐 2 (뒤로 누워 기절, 머리가 뒤쪽·칼은 허리에서 위로 솟음)
#   · 4 일반공격 1 (낮게 앉아 칼자루를 쥐고 뽑기 직전)
# 크기 통일: 대기 자세 몸 키(머리털 끝~발, 샘플 px)를 TARGET_H로 줄임. 다른 동작은 대기와 같은 배율('idle')로 줄여 얼굴 크기를 맞춤
# 샘플 정리:
#   - 대기 샘플(768×1024)은 도트 그림을 흐리게 키운 것, 테두리 없음
#   - 피격·쓰러짐 샘플(766×250)은 세 칸을 한 장에 그린 것 + 위 잘린 글자 줄·칸 이름('[피격]' 등). 왼쪽부터 0·1번째 덩어리로 고름 (2번째 = 예전 쓰러짐 2, 지금은 안 씀)
#   - 쓰러짐 2 샘플(346×158)은 흰 배경 한 장, 머리카락이 왼쪽 끝에 닿음. 누운 그림이라 몸 길이로 크기를 맞춤 (FIT_W)
#     '[쓰러짐 1]' 글자는 쓰러짐 1 머리 묶음과 붙어 있어 상자로 지움 (CUT). 해상도가 대기 샘플과 달라 키를 따로 맞춤 (FIT_H)
#   - 일반공격 샘플(209×271)은 오른쪽 끝에 옆 칸 조각 점 → 가장 큰 덩어리만
#   - 회색 별 모양 워터마크가 몸에 겹친 샘플은 그 자리를 머리카락 색으로 덮음 (SCRUB, 지금은 해당 샘플 없음)
#   - 피격·쓰러짐·일반공격 1은 같은 그림의 어두운 배경 판(swordsman_dark_src)과 겹쳐 비교해 테두리 투명도를 다시 구함 (DARK, dark_matte)
#   - 피부가 어두운 샘플은 살색만 밝힘 (SKIN)
#   - 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움 (짚신·옷깃의 밝은 회색은 검은 외곽선 안쪽이라 남음)
import os, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/swordsman_'
OUT = 'assets/sprites/merc/swordsman_0.webp'
TARGET_H = 86   # 대기 자세 머리 묶음 끝~발 → 게임 칸 키 (격투가와 같은 키, 연결할 때 standH·topH로 맞춤)

CARD = {}   # (x0, x1, y0, y1): 샘플 테두리 잘라 냄
WHITE_MIN = {'hurtdown': 200}   # 피격·쓰러짐 샘플은 흐린 밝은 테두리가 넓어 더 어두운 흰색까지 배경으로 봄
CUT = {'hurtdown': [(0, 766, 0, 8), (284, 384, 12, 45), (384, 390, 12, 36)]}   # 지울 상자 (x0, x1, y0, y1): 위 잘린 글자 줄 · '[쓰러짐 1' · ']' (머리 묶음에 붙은 세로줄)
FIT_H = {'HURT': 78, 'ATK': 84}   # 샘플마다 해상도가 달라 몸 키를 직접 정해 머리 크기를 대기와 맞춤: 피격(뒤로 젖힘) · 일반공격(낮게 앉음). 쓰러짐 1은 피격과 같은 배율
FIT_W = {'DOWN2': 108}   # 누운 그림은 머리~발 가로 길이로 맞춤
DARK_SRC = f'{D}dark_src.png'   # 같은 동작을 어두운 배경(25,25,25)에 그린 샘플: 피격 · 쓰러짐 1 · 쓰러짐 2 · 일반공격 1 (왼쪽부터, 발밑 그림자·오른쪽 아래 반짝이 표시 있음)
DARK = {('hurtdown', 0): 0, ('hurtdown', 1): 1, ('atk0', 'big'): 3}   # (샘플, 고른 덩어리) → 어두운 샘플 몇 번째 그림
DARK_BG = 25.0
SCRUB = {}   # 샘플 이름 → 지울 워터마크 다각형 꼭짓점 (샘플 px): 몸에 겹친 회색 네 갈래 별 → 안의 회색만 머리카락 남색으로 칠함 (원래 밝기 차이는 조금 남김)
# 예전 쓰러짐 2(hurtdown 2번째 그림)는 [(671, 144), (686, 158), (704, 164), (698, 176), (686, 178), (677, 192), (667, 176), (662, 168), (667, 157)]
SCRUB_HAIR = np.array([23, 25, 36])   # 둘레 머리카락 색
SKIN = set()   # 피부가 어두운 샘플만 넣어 첫 샘플(밝은 살색)만큼 밝힘. 지금 대기 샘플은 처음부터 밝아서 비워 둠


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


_dark = {}


def dark_figures():   # 어두운 샘플을 읽고 그림 4개의 상자(x0, x1, y0, y1)를 왼쪽부터
    if not _dark:
        im = np.array(Image.open(DARK_SRC).convert('RGB')).astype(float)
        fg = np.abs(im - DARK_BG).max(axis=2) > 18
        lab, n = ndi.label(ndi.binary_dilation(fg, iterations=2))
        sz = ndi.sum(fg, lab, range(1, n + 1))
        idx = np.argsort(sz)[::-1][:4] + 1
        boxes = []
        for i in idx:
            ys, xs = np.where(lab == i); boxes.append((xs.min(), xs.max(), ys.min(), ys.max()))
        _dark['im'], _dark['boxes'] = im, sorted(boxes)
    return _dark['im'], _dark['boxes']


def dark_matte(raw, a, im, idx):
    """흰 배경·어두운 배경 두 장을 겹쳐 투명도를 다시 구함 (두 배경 비교).
    흰 배경 그림만으로는 외곽선 바깥의 흐린 회백색 테두리가 몸인지 배경인지 모름 → 어두운 그림에 맞춰 놓고
    두 장의 차이(흰 배경일수록 밝아지는 만큼)로 투명도 = 1 - (흰 - 어두운) / (255 - 25).
    두 그림은 따로 만든 것이라 크기·위치가 조금 달라 ECC(아핀)로 맞추고, 피부 톤 등 안쪽 색도 조금 달라서
    몸 안쪽(흰 그림 덩어리를 2px 깎은 곳)은 그대로 불투명, 색은 흰 배경 그림 것을 씀. 발밑 그림자는 배경보다 어두워 투명이 됨"""
    D_im, boxes = dark_figures()
    m = a > 0.5
    ys, xs = np.where(a > 0)
    P = 10
    y0, y1 = max(0, ys.min() - P), min(raw.shape[0], ys.max() + P + 1)
    x0, x1 = max(0, xs.min() - P), min(raw.shape[1], xs.max() + P + 1)
    W = raw[y0:y1, x0:x1]
    mw = m[y0:y1, x0:x1]
    fill = ndi.binary_fill_holes(ndi.binary_dilation(mw, iterations=1))
    tmpl = np.where(fill[..., None], W, DARK_BG).mean(axis=2).astype(np.float32) / 255
    wy, wx = np.where(mw)
    dx0, dx1, dy0, _ = boxes[idx]
    sc = (dx1 - dx0 + 1) / (wx.max() - wx.min() + 1)   # 흰 그림 1px → 어두운 그림 sc px (가로 폭으로 처음 값, 그림자는 아래에만 있어 위·왼쪽을 맞춤)
    A = np.array([[sc, 0, dx0 - wx.min() * sc], [0, sc, dy0 - wy.min() * sc]], np.float32)
    img = D_im.mean(axis=2).astype(np.float32) / 255
    _, A = cv2.findTransformECC(tmpl, img, A, cv2.MOTION_AFFINE,
                                (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6), None, 5)
    Dw = cv2.warpAffine(D_im.astype(np.float32), A, (W.shape[1], W.shape[0]),
                        flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderValue=(DARK_BG,) * 3).astype(float)
    a2 = np.clip(1 - (W - Dw).mean(axis=2) / (255 - DARK_BG), 0, 1)
    a2 = np.where(ndi.binary_erosion(mw, iterations=2), 1.0, a2)          # 몸 안쪽은 불투명
    a2 = np.where(ndi.binary_dilation(a[y0:y1, x0:x1] > 0, iterations=3), a2, 0.0)   # 고른 덩어리 근처만 (글자·옆 그림 제외)
    a2 = np.where(a2 > 0.85, 1.0, np.where(a2 < 0.15, 0.0, a2))
    al = np.maximum(a2, 1e-3)[..., None]
    col = np.where((a2 < 1)[..., None], (W - 255 * (1 - al)) / al, W).clip(0, 255)   # 반투명 테두리: 흰 배경과 섞인 만큼 빼서 원래 색
    a_new = np.zeros_like(a); a_new[y0:y1, x0:x1] = a2
    im = im.copy(); im[y0:y1, x0:x1] = col
    return a_new, im


def scrub(im, poly):
    pm = Image.new('L', (im.shape[1], im.shape[0]), 0); ImageDraw.Draw(pm).polygon(poly, fill=1)
    pm = np.array(pm) > 0
    sat, v = im.max(axis=2) - im.min(axis=2), im.mean(axis=2)
    g = pm & (sat < 30) & (v > 55) & (v < 200)
    g = ndi.binary_dilation(g) & pm & (v < 200)   # 별 가장자리의 흐린 회색까지, 흰 배경은 건드리지 않음
    t = np.clip((v - 55) / 120, 0, 1)[..., None]
    im = im.copy(); im[g] = (SCRUB_HAIR * (0.85 + 0.6 * t))[g]
    return im


def load(name, pick=0):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    if name in SCRUB: im = scrub(im, SCRUB[name])
    if name in CARD:
        x0, x1, y0, y1 = CARD[name]; im = im[y0:y1, x0:x1]
    raw = im.copy()
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
    if (name, pick) in DARK: a, im = dark_matte(raw, a, im, DARK[(name, pick)])
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
    ('hurtdown', 'hurt', 'HURT', 0),
    ('hurtdown', 'down1', 'hurt', 1),
    ('down2', 'down2', 'DOWN2', 'big'),
    ('atk0', 'atk0', 'ATK', 'big'),
]
FOOTX = {}   # 칸 이름 → 발 가운데 (자른 그림 기준 px)


def main():
    pieces, scale = [], {}
    for src, name, k, pick in FRAMES:
        rgba, foot, bh = load(src, pick)
        if src in SKIN: rgba = lighten_skin(rgba)
        if name in FOOTX: foot = FOOTX[name]
        sc = TARGET_H / bh if k == 'H' else FIT_H[k] / bh if k in FIT_H else FIT_W[k] / rgba.shape[1] if k in FIT_W else scale[k]
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

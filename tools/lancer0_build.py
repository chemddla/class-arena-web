# 창병 기본 외형(lancer_0) 교체: 검은 판금 갑옷·투구(십자 무늬)·갈색 눈·장창 샘플 → assets/sprites/merc/lancer_0.webp
#   + 히든 스킬 [무쌍난무] 자세 그림 assets/sprites/fx/lancer_musou_cast.webp (기본 외형용 10칸)
# 사용: python tools/lancer0_build.py
# 샘플 (흰 배경, 왼쪽 한글 라벨은 몸 덩어리만 남겨서 지움): assets/sprites/merc/samples/lancer_edit_*
#   1 대기 · 2 걷기 4 · 3 휘두르기 3 (아래로 겨눔 · 휘두르며 초승달 · 앞으로 찌름) · 4 일반공격 2 (당김 · 찌르기 바람) + 피격 + 쓰러짐 2
#   5 스킬 6 (윗줄: 겨눔 · 찌르기+초승달 · 찌르기+바람 / 아랫줄: 회전 고리 · 창을 머리 위로 돌림 · 돌진)
#   6 스킬 6 (윗줄: 아래로 겨눔 · 올려 베기 초승달 · 낮게 휘두르기 / 아랫줄: 창을 어깨 뒤로 당김 · 던진 뒤 빈손 · 양쪽 초승달 회전)
# 칸 순서는 예전 lancer_0(26칸)과 같게 → index.html의 anims·skillAnims·castFrames 그대로
#   0·1 대기 · 2~5 걷기 · 6~8 휘두르기 · 9~11 찌르기 · 12~14 피어싱 · 15·16 투창 · 17~19 회전·난무 · 20~22 창돌격 · 23 피격 · 24·25 쓰러짐
# 크기: 샘플 장마다 그린 크기가 달라서, 대기 칸 머리(투구+얼굴)를 각 장에서 찾아 그 비율로 맞춤 (head_scale)
#   대기 몸 키(투구 꼭대기~발, 창 빼고)를 IDLE_H로
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/merc/samples/lancer_edit_'
SRC = {1: '1_idle_src.png', 2: '2_walk_src.webp', 3: '3_sweep_src.png', 4: '4_thrust_hurt_fall_src.png',
       5: '5_skill_a_src.webp', 6: '6_skill_b_src.png'}
OUT = 'assets/sprites/merc/lancer_0.webp'
MUSOU_OUT = 'assets/sprites/fx/lancer_musou_cast.webp'
IDLE_H = 96
IDLE_BODY = 165          # 대기 샘플의 몸 키 (투구 꼭대기 y 42 ~ 발 y 207)
IDLE_HEAD = (182, 40, 252, 112)   # 대기 샘플 머리 (투구+얼굴)
# 장마다 머리 크기를 잴 곧게 선 칸 (샘플 상자)
HEAD_REF = {1: (150, 0, 316, 214), 2: (30, 160, 275, 625), 3: (15, 8, 237, 174), 4: (195, 0, 395, 175),
            5: (727, 39, 1018, 265), 6: (401, 241, 586, 431)}
B = {  # (샘플 장, 상자, 이펙트 포함 여부: True면 큰 덩어리를 모두 남김)
    'idle': (1, (150, 0, 316, 214), False),
    'walk0': (2, (30, 160, 275, 625), False), 'walk1': (2, (278, 160, 522, 625), False),
    'walk2': (2, (525, 160, 760, 625), False), 'walk3': (2, (762, 160, 1012, 625), False),
    'swReady': (6, (43, 27, 300, 216), False), 'swUp': (6, (407, 0, 680, 218), True), 'swLow': (6, (689, 30, 1022, 218), True),
    'thReady': (4, (195, 0, 395, 178), False), 'thStab': (4, (395, 0, 645, 178), True), 'thEnd': (3, (467, 8, 688, 174), True),
    'pcReady': (5, (49, 30, 323, 268), False), 'pcCres': (5, (339, 31, 689, 268), True), 'pcWind': (5, (727, 39, 1022, 268), True),
    'jvBack': (6, (11, 235, 273, 434), False), 'jvThrow': (6, (401, 241, 586, 434), False),
    'spinRing': (5, (0, 298, 341, 568), True), 'spinUp': (5, (341, 298, 680, 568), True), 'spinCres': (6, (689, 218, 1022, 434), True),
    'chReady': (3, (15, 8, 237, 174), False), 'chDash': (5, (681, 340, 1024, 568), True),
    'hurt': (4, (195, 180, 392, 348), False), 'down0': (4, (170, 358, 368, 524), False), 'down1': (4, (368, 398, 692, 527), False),
    'swing': (3, (239, 8, 458, 174), True),
}
SHEET = ['idle', 'idle', 'walk0', 'walk1', 'walk2', 'walk3', 'swReady', 'swUp', 'swLow', 'thReady', 'thStab', 'thEnd',
         'pcReady', 'pcCres', 'pcWind', 'jvBack', 'jvThrow', 'spinRing', 'spinUp', 'spinCres', 'chReady', 'chDash', 'chDash',
         'hurt', 'down0', 'down1']
# 무쌍난무 자세 (예전 cast와 같은 뜻의 10칸): 0 서 있음 · 1 창 치켜듦(올려 베기) · 2 회전 고리 · 3 찌르기+바람 · 4 휘두르기
#   · 5 다중 찌르기(초승달) · 6 창 당김 · 7·8 돌진 · 9 양쪽 초승달 회전
MUSOU = ['swReady', 'swUp', 'spinRing', 'pcWind', 'swing', 'pcCres', 'jvBack', 'chDash', 'chDash', 'spinCres']


def rgb_of(n):
    return np.array(Image.open(D + SRC[n]).convert('RGB')).astype(np.float32)


def head_scale(n):
    # n번 장의 머리가 대기 샘플 머리의 몇 배인지 (기울기 ±15°, 배율 0.5~3.2)
    import cv2
    S1 = rgb_of(1); x0, y0, x1, y1 = IDLE_HEAD; T0 = S1[y0:y1, x0:x1]
    x0, y0, x1, y1 = HEAD_REF[n]; im = rgb_of(n)[y0:y1, x0:x1]
    best = (-1, 1)
    for ang in (-12, -6, 0, 6, 12):
        M = cv2.getRotationMatrix2D((T0.shape[1] / 2, T0.shape[0] / 2), ang, 1)
        R = cv2.warpAffine(T0, M, (T0.shape[1], T0.shape[0]), borderValue=(255, 255, 255))[4:-4, 4:-4]
        for sc in np.arange(0.5, 3.2, 0.01):
            t = cv2.resize(R, (round(R.shape[1] * sc), round(R.shape[0] * sc)), interpolation=cv2.INTER_CUBIC)
            if t.shape[0] > im.shape[0] or t.shape[1] > im.shape[1]: continue
            v = cv2.minMaxLoc(cv2.matchTemplate(im, t, cv2.TM_CCOEFF_NORMED))[1]
            if v > best[0]: best = (v, sc)
    return best[1], best[0]


def load(n, box, fx):
    im = rgb_of(n).astype(float)
    x0, y0, x1, y1 = box; im = im[y0:y1, x0:x1]
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), constant_values=255)
    white = (im.min(axis=2) > 222) & (im.max(axis=2) - im.min(axis=2) < 18)
    lab, k = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    ids = np.arange(1, k + 1)   # 갇힌 흰 배경 (창대·팔 사이): 아주 하얗고 30px 이상
    pure = (ndi.sum(white, lab, ids) >= 30) & (ndi.mean(im.min(axis=2), lab, ids) > 247)
    bg |= np.isin(lab, ids[pure])
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    m = a > 0.3
    lab, k = ndi.label(ndi.binary_dilation(m, iterations=3))
    sz = ndi.sum(m, lab, range(1, k + 1))
    keep = np.isin(lab, 1 + np.where(sz >= 250)[0]) if fx else lab == int(np.argmax(sz)) + 1
    if fx:   # 이펙트 칸도 몸 덩어리에서 먼 글씨·이웃 칸 조각은 지움: 몸 덩어리 + 몸에서 가로 세로 70% 안
        body = lab == int(np.argmax(sz)) + 1
        keep &= ~((lab > 0) & ~body & np.isin(lab, 1 + np.where(sz < 900)[0]))
    a = np.where(keep, a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # 발: 갑옷(어둡고 무채색) 픽셀의 맨 아래 줄들 → 창끝·이펙트는 빼고 잼
    c = rgba[..., :3]
    armor = (rgba[..., 3] > 200) & (c.max(-1) < 95) & (c.max(-1) - c.min(-1) < 30)
    armor = ndi.binary_opening(armor, iterations=1)
    ay, ax = np.where(armor)
    fy = ay.max(); band = ay >= fy - max(3, int((fy - ay.min()) * 0.07))
    return rgba, ax[band].mean(), fy + 1


def pack(pieces, out, label):
    # pieces: (이름, rgba, 발x, 발y) — 발 기준점에 맞춰 같은 크기 칸에 늘어놓음
    L = max(int(np.ceil(fx)) for _, _, fx, _ in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - fx)) for _, p, fx, _ in pieces) + 3
    U = max(int(np.ceil(fy)) for _, _, _, fy in pieces) + 2
    Bt = max(int(np.ceil(p.shape[0] - fy)) for _, p, _, fy in pieces) + 2
    cw, ch = L + R, U + Bt
    sheet = np.zeros((ch, cw * len(pieces), 4), np.uint8)
    for i, (name, p, fx, fy) in enumerate(pieces):
        x = i * cw + L - int(round(fx)); y = U - int(round(fy))
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(out, 'WEBP', lossless=True)
    print(f'{label} cellW={cw} cellH={ch} anchorX={L} anchorY={U} count={len(pieces)}')
    return cw, ch, L, U


def soften_edge(p):
    # 줄인 뒤 투명한 칸에 닿은 흰 배경 찌꺼기 (아주 밝은 무채색) 한 겹만 지움 — 창끝 은색·바람 이펙트의 옅은 하늘색은 남김
    a = p[..., 3] > 0
    edge = a & ndi.binary_dilation(~a)
    c = p[..., :3].astype(int)
    p[edge & (c.min(-1) > 225) & (c.max(-1) - c.min(-1) < 14)] = 0
    return p


def main():
    hs = {}
    for n in SRC:
        hs[n], v = head_scale(n)
        print(f'장 {n}: 머리 = 대기의 {hs[n] / hs[1]:.3f}배 (일치 {v:.2f})')
    k1 = IDLE_H / IDLE_BODY
    built = {}
    for name, (n, box, fx) in B.items():
        rgba, fxx, fyy = load(n, box, fx)
        kk = k1 * hs[1] / hs[n]
        if name == 'down1': fxx = rgba.shape[1] * 0.42   # 누운 칸: 몸 가운데쯤
        p = soften_edge(shrink(rgba, kk))
        built[name] = (name, p, fxx * kk, fyy * kk)
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{kk:.3f} → {p.shape[1]}x{p.shape[0]}, 발 ({fxx * kk:.1f}, {fyy * kk:.1f})')
    pack([built[n] for n in SHEET], OUT, 'lancer_0')
    pack([built[n] for n in MUSOU], MUSOU_OUT, 'lancer_musou_cast')


if __name__ == '__main__':
    main()

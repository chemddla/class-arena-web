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
from lancer_fx_grey import grey

D = 'assets/sprites/merc/samples/lancer_edit_'
SRC = {1: '1_idle_src.png', 2: '2_walk_src.webp', 3: '3_sweep_src.png', 4: '4_thrust_hurt_fall_src.png',
       5: '5_skill_a_src.webp', 6: '6_skill_b_src.png', 7: '7_musou_src.webp', 8: '8_charge_swing_white_src.webp'}
# 8 = 2026-11-10 새 샘플 4자세 (흰 배경 + 같은 그림의 회색 배경 PAIR): 왼쪽 위 창돌격 겨눔 · 오른쪽 위 창돌격 돌진(뒤 속도선)
#   · 왼쪽 아래 휘두르기 베기(몸 뒤 속도선은 지움, STRIP_LINES) · 오른쪽 아래 낮게 휩쓸기(고리 이펙트) → 무쌍난무 10번 자세
#   배경이 다른 두 장을 비교해서(matte) 배경을 걷어냄: 이펙트의 반투명·흰 부분이 그대로 살아서 구멍·흰 찌꺼기가 생기지 않음
PAIR = {8: '8_charge_swing_grey_src.webp'}
# 스킬 샘플 5·6의 검은 배경 짝 (같은 그림을 검은 배경으로, 2026-11-10 사용자 제공) → black_pair
BLACK = {5: '5_skill_a_black_src.webp', 6: '6_skill_b_black_src.webp'}
# 장마다 배율 보정
#   8: 머리 맞추기가 약하게 맞은 장(일치 0.66) — 다른 칸과 얼굴 넓이(살색 픽셀 수 ≈ 130)가 같아지게
#   2·3·5 (2026-11-10 사용자: "대기 모션 기준으로 크기·비율 통일"): 머리 크기는 장마다 같게 맞아도 몸이 길게 그려진 장이라
#     곧게 선 자세의 키(투구 꼭대기~발)가 대기(98px)보다 컸음 → 걷기 102.5 · 찌르기 뻗음(3번 장) 102 · 피어싱 겨눔 104를 98로
SCALE_FIX = {8: 0.9, 2: 0.956, 3: 0.961, 5: 0.942}
# 7 = 무쌍난무 자세 6칸 (회색 배경 198, 윗줄: 겨눔 · 창을 치켜들며 큰 초승달 · 회전 고리 / 아랫줄: 잔상 남기며 다중 찌르기(금빛 불꽃) · 휘두르기 초승달 · 사선 찌르기)
#   오른쪽 아래 ✦ 워터마크는 ERASE 상자를 배경색으로 칠해 지움
OUT = 'assets/sprites/merc/lancer_0.webp'
MUSOU_OUT = 'assets/sprites/fx/lancer_musou_cast.webp'
IDLE_H = 96
IDLE_BODY = 165          # 대기 샘플의 몸 키 (투구 꼭대기 y 42 ~ 발 y 207)
IDLE_HEAD = (182, 40, 252, 112)   # 대기 샘플 머리 (투구+얼굴)
# 장마다 머리 크기를 잴 곧게 선 칸 (샘플 상자)
HEAD_REF = {1: (150, 0, 316, 214), 2: (30, 160, 275, 625), 3: (15, 8, 237, 174), 4: (195, 0, 395, 175),
            5: (727, 39, 1018, 265), 6: (401, 241, 586, 431), 7: (95, 100, 265, 240),
            8: (60, 80, 440, 305)}
ERASE = {7: [(920, 458, 952, 494)]}
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
    'mu0': (7, (95, 100, 265, 240), True), 'mu1': (7, (430, 25, 640, 240), True), 'mu2': (7, (745, 85, 985, 240), True),
    'mu3': (7, (10, 385, 355, 532), True), 'mu4': (7, (435, 385, 640, 540), True), 'mu5': (7, (755, 375, 968, 540), True),
    'chReady8': (8, (60, 80, 440, 305), False), 'chDash8': (8, (620, 75, 1010, 300), True),
    'swing8': (8, (50, 470, 410, 740), True), 'sweep8': (8, (515, 520, 1000, 735), True),
}
# 몸 뒤 속도선 지우기 (사용자 요청: 휘두르기 베기는 피사체 뒤 움직임 이펙트 없이): 샘플 x가 이보다 왼쪽인 가로로 긴 가는 줄기 + 따로 지울 상자
STRIP_LINES = {'swing8': (260, [(150, 525, 178, 545)])}
FOOT_X = {'mu3': 112}   # 잔상이 겹친 칸: 앞 사람(왼쪽) 발 가운데 (샘플 x)
# 2026-11-10: 7 휘두르기 = mu4 (무쌍난무 휘두르기 자세, 사용자: 기본 공격 휘두르기는 이 자세 하나만 · 6·8칸은 안 씀), 20 창돌격 겨눔 = chReady8, 21·22 창돌격 돌진 = chDash8 (새 샘플 8번 장)
SHEET = ['idle', 'idle', 'walk0', 'walk1', 'walk2', 'walk3', 'swReady', 'mu4', 'swLow', 'thReady', 'thStab', 'thEnd',
         'pcReady', 'pcCres', 'pcWind', 'jvBack', 'jvThrow', 'spinRing', 'spinUp', 'spinCres', 'chReady8', 'chDash8', 'chDash8',
         'hurt', 'down0', 'down1']
# 무쌍난무 자세 (예전 cast와 같은 뜻의 10칸): 0 서 있음 · 1 창 치켜듦(올려 베기) · 2 회전 고리 · 3 찌르기+바람 · 4 휘두르기
#   · 5 다중 찌르기(초승달) · 6 창 당김 · 7·8 돌진 · 9 양쪽 초승달 회전
#   · 10 낮게 휩쓸기(고리 이펙트, 2026-11-10 추가)
#   0~5는 무쌍난무 전용 샘플(7번 장), 6~10은 스킬 샘플을 같이 씀 (7·8 돌진·10 휩쓸기는 새 샘플 8번 장)
MUSOU = ['mu0', 'mu1', 'mu2', 'mu3', 'mu4', 'mu5', 'jvBack', 'chDash8', 'chDash8', 'spinCres', 'sweep8']


def rgb_of(n):
    im = np.array(Image.open(D + SRC[n]).convert('RGB')).astype(np.float32)
    bgc = np.median(np.concatenate([im[0], im[-1], im[:, 0], im[:, -1]]), axis=0)
    for x0, y0, x1, y1 in ERASE.get(n, []): im[y0:y1, x0:x1] = bgc
    return im


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


# 이펙트 줄기 사이 틈을 어디까지 안쪽으로 볼지 (닫기 횟수 ≈ 틈 폭의 절반 px, 샘플 기준). 초승달은 바깥 선과 안쪽 줄기 사이가 넓고,
#   회전 고리는 고리끼리 사이가 배경이라 좁게
GAP_ITERS = {'swUp': 10, 'pcCres': 10, 'spinRing': 3, 'spinUp': 3, 'spinCres': 3}


_GREY_BG = {}


def matte(n, box, name):
    # 흰 배경(W=255)과 회색 배경(G) 두 장: W - C_g = (1 - a)(255 - G) → a, 색 = (C_g - (1 - a)G) / a
    w = rgb_of(n).astype(float)
    g = np.array(Image.open(D + PAIR[n]).convert('RGB')).astype(float)
    if n not in _GREY_BG:   # 회색 배경 밝기: 흰 장에서 순수 배경인 자리의 회색 장 값을 둘레로 번지게
        bgm = w.min(-1) > 250
        _, (iy, ix) = ndi.distance_transform_edt(~bgm, return_indices=True)
        _GREY_BG[n] = ndi.uniform_filter(g.mean(-1)[iy, ix], 15)
    x0, y0, x1, y1 = box
    w, g, G = w[y0:y1, x0:x1], g[y0:y1, x0:x1], _GREY_BG[n][y0:y1, x0:x1]
    a = np.clip(1 - (w - g).mean(-1) / np.maximum(255 - G, 1), 0, 1)
    a[a < 0.06] = 0
    im = np.clip((g - (1 - a)[..., None] * G[..., None]) / np.maximum(a, 1e-3)[..., None], 0, 255)
    if name in STRIP_LINES:
        xmax, boxes = STRIP_LINES[name]
        xs = np.arange(im.shape[1])[None, :] + x0
        ys = np.arange(im.shape[0])[:, None] + y0
        thick = ndi.binary_opening(a > 0.78, structure=np.ones((7, 1)))      # 몸·창: 세로로 7px 넘게 두꺼운 곳 (속도선은 4~5px)
        thick = ndi.binary_opening(thick, structure=np.ones((1, 3)))
        brown = im[..., 0] - im[..., 2] > 8                                   # 창대
        cand = (a > 0) & ~ndi.binary_dilation(thick) & ~brown & (xs < xmax) & (im.mean(-1) < 150)   # 밝은 초승달은 남김
        lab, _ = ndi.label(cand)
        kill = np.zeros_like(cand)
        for i, sl in enumerate(ndi.find_objects(lab), 1):
            h, wd = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if wd >= 3 and wd >= h * 1.2: kill |= lab == i                    # 가로로 긴 조각만
        for bx0, by0, bx1, by1 in boxes:
            kill |= cand & (xs >= bx0) & (xs < bx1) & (ys >= by0) & (ys < by1)
        a = np.where(kill | ((a <= 0.16) & (xs < xmax)), 0, a)
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), mode='edge')
    a = np.pad(a, 2)
    return im, a


def load(n, box, fx, name=''):
    if n in PAIR:
        im, a = matte(n, box, name)
        x0 = box[0]
        return finish(im, a, fx, x0, paired=True)
    im = rgb_of(n).astype(float)
    full = im
    x0, y0, x1, y1 = box; im = im[y0:y1, x0:x1]
    bgc = np.median(np.concatenate([full[0], full[-1], full[:, 0], full[:, -1]]), axis=0)
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), mode='constant')
    im[:2] = im[-2:] = im[:, :2] = im[:, -2:] = bgc
    if bgc.mean() > 240:   # 흰 배경
        white = (im.min(axis=2) > 222) & (im.max(axis=2) - im.min(axis=2) < 18)
        trapped = lambda lab, ids: ndi.mean(im.min(axis=2), lab, ids) > 247
        rim_a = lambda: np.clip((255 - im.min(axis=2)) / 200, 0, 1)
    else:                  # 회색 배경 (7번 장): 배경색과의 차이로 — 흰 초승달은 더 밝고, 윤곽은 더 어두움
        dist = np.abs(im - bgc).max(axis=2)
        white = dist <= 9
        trapped = lambda lab, ids: ndi.mean(dist, lab, ids) < 4
        rim_a = lambda: np.clip(dist / 60, 0, 1)
    lab, k = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    ids = np.arange(1, k + 1)   # 갇힌 배경 (창대·팔 사이): 배경과 거의 같고 30px 이상
    pure = (ndi.sum(white, lab, ids) >= 30) & trapped(lab, ids)
    bg |= np.isin(lab, ids[pure])
    if fx and bgc.mean() > 240:
        # 이펙트(초승달·바람·회전 고리) 속의 흰 부분은 배경이 아님 (2026-11-09 사용자 지적: 7·8·13·14·19칸 이펙트 가운데가 비어 있었음)
        #   이펙트 픽셀 = 청록·하늘빛이 도는 밝은 픽셀과 밝은 회색 줄기. 이것을 닫고(틈 메움) 속을 채운 범위 안의 흰 배경은 불투명 흰색으로 되살림
        c = im.astype(int)
        eff = ~bg & (np.maximum(c[..., 1], c[..., 2]) - c[..., 0] > 6) & (c.max(-1) > 110)
        dark = ~bg & (c.max(-1) < 95)   # 갑옷·창대·윤곽
        eff |= ~bg & (c.min(-1) > 95) & (c.max(-1) - c.min(-1) < 30) & ~ndi.binary_dilation(dark, iterations=3)   # 회색 바람 줄기 (갑옷 하이라이트·창날은 빼려고 어두운 곳 3px 안은 제외)
        eff = ndi.binary_opening(eff, iterations=1) | (eff & ndi.binary_dilation(eff, iterations=1).astype(bool))
        lab_e, ne = ndi.label(ndi.binary_dilation(eff, iterations=2))
        big = np.isin(lab_e, 1 + np.where(ndi.sum(eff, lab_e, range(1, ne + 1)) >= 40)[0])
        # 테두리 안쪽만 (2026-11-09 사용자: "회색 안쪽만 채우고 테두리 밖의 흰색은 배경"): 흰 덩어리 중 둘레가 거의 다 이펙트 줄기인 것만 채움
        #   (1px 틈은 메워서 봄). 몸·창에 닿거나 바깥 배경과 이어진 흰색은 배경으로 남김
        wall = ndi.binary_closing(big, iterations=1, border_value=0) | big
        cand = white & ~wall
        lab_h, nh = ndi.label(cand)
        border_ids = set(np.unique(np.concatenate([lab_h[0], lab_h[-1], lab_h[:, 0], lab_h[:, -1]])))
        fill = np.zeros_like(cand)
        for i, sl in enumerate(ndi.find_objects(lab_h), 1):
            if i in border_ids: continue
            y0, y1, x0, x1 = max(0, sl[0].start - 1), sl[0].stop + 1, max(0, sl[1].start - 1), sl[1].stop + 1
            h = lab_h[y0:y1, x0:x1] == i
            ring = ndi.binary_dilation(h) & ~h
            if wall[y0:y1, x0:x1][ring].mean() >= 0.92: fill[y0:y1, x0:x1] |= h
        # 끝이 열린 초승달·바람 줄기: 줄기 사이 좁은 틈(GAP_ITERS)도 안쪽으로 봄. 몸(어두운 곳) 4px 안은 빼서 몸과 줄기 사이 배경은 남김
        between = ndi.binary_closing(big, iterations=GAP_ITERS.get(name, 3), border_value=0) & ~ndi.binary_dilation(dark, iterations=4)
        bg &= ~((fill | wall | between) & white)
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, rim_a(), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - bgc * (1 - al)) / al, im).clip(0, 255)
    if n in BLACK: im, a = black_pair(n, box, im, a)
    return finish(im, a, fx, box[0])


def black_pair(n, box, im, a):
    # 검은 배경 짝 (2026-11-10): 흰 장에서 흰색(배경과 구별 안 되는) 자리만 검은 장으로 다시 판단
    #   흰 장 W=255 · 검은 장 K → a = K/255 (흰 바탕이면 1 - (W - K)/255), 색 = K / a
    #   → 이펙트 속 흰 부분은 불투명하게 살아나고(구멍 메움), 줄기 사이 흰 배경은 투명(흰 찌꺼기 지움)
    #   몸·창(흰색이 아닌 곳)은 흰 장 결과 그대로 — 6번 검은 장은 몸 색이 조금 어둡게 다시 그려져서 몸에는 안 씀
    #   6번 장은 자세마다 1~4px 어긋나 있어서 조각마다 몸(어두운 곳)이 가장 잘 겹치는 이동을 찾아 맞춤
    w = rgb_of(n)
    k = np.array(Image.open(D + BLACK[n]).convert('RGB')).astype(float)
    x0, y0, x1, y1 = box
    W = w[y0:y1, x0:x1]
    dark = W.max(-1) < 100
    best = (1e9, 0, 0)
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            ys, xs = slice(max(0, y0 + dy), y1 + dy), slice(max(0, x0 + dx), x1 + dx)
            K = k[ys, xs]
            if K.shape != W.shape: continue
            e = np.abs(K - W).mean(-1)[dark].mean()
            if e < best[0]: best = (e, dx, dy)
    _, dx, dy = best
    K = np.pad(k[y0 + dy:y1 + dy, x0 + dx:x1 + dx], ((2, 2), (2, 2), (0, 0)))
    Wp = np.pad(W, ((2, 2), (2, 2), (0, 0)), constant_values=255)
    white = (Wp.min(-1) > 215) & (Wp.max(-1) - Wp.min(-1) < 20)
    ap = np.clip(1 - (Wp - K).mean(-1) / 255, 0, 1)
    ap[ap < 0.08] = 0
    col = np.clip(K / np.maximum(ap, 1e-3)[..., None], 0, 255)
    a = np.where(white, ap, a)
    im = np.where(white[..., None], col, im)
    print(f'  검은 짝 {n}번 장 {box}: 이동 ({dx}, {dy}) 몸 차이 {best[0]:.1f}')
    return im, a


def finish(im, a, fx, x0, paired=False):
    # paired: 두 장 비교 샘플 — 상자 안에 다른 칸 조각·글씨가 없어서 30px 넘는 조각(돌진 뒤 속도선)은 모두 남김
    m = a > 0.3
    lab, k = ndi.label(ndi.binary_dilation(m, iterations=3))
    sz = ndi.sum(m, lab, range(1, k + 1))
    keep = np.isin(lab, 1 + np.where(sz >= (30 if paired else 250))[0]) if fx else lab == int(np.argmax(sz)) + 1
    if fx:   # 이펙트 칸도 몸 덩어리에서 먼 글씨·이웃 칸 조각은 지움: 몸 덩어리 + 몸에서 가로 세로 70% 안
        body = lab == int(np.argmax(sz)) + 1
        if not paired: keep &= ~((lab > 0) & ~body & np.isin(lab, 1 + np.where(sz < 900)[0]))
    a = np.where(keep, a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    ox = x0 + xs.min() - 2   # 자른 그림 왼쪽 끝의 샘플 x
    # 발: 갑옷(어둡고 무채색) 픽셀의 맨 아래 줄들 → 창끝·이펙트는 빼고 잼
    c = rgba[..., :3]
    armor = (rgba[..., 3] > 200) & (c.max(-1) < 95) & (c.max(-1) - c.min(-1) < 30)
    armor = ndi.binary_opening(armor, iterations=1)
    ay, ax = np.where(armor)
    fy = ay.max(); band = ay >= fy - max(3, int((fy - ay.min()) * 0.07))
    return rgba, ax[band].mean(), fy + 1, ox


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
        rgba, fxx, fyy, ox = load(n, box, fx, name)
        if name in FOOT_X: fxx = FOOT_X[name] - ox
        kk = k1 * hs[1] / hs[n] * SCALE_FIX.get(n, 1)
        if name == 'down1': fxx = rgba.shape[1] * 0.42   # 누운 칸: 몸 가운데쯤
        p = grey(soften_edge(shrink(rgba, kk)))   # 청록 이펙트(초승달·바람·회전 고리)는 회색으로 (tools/lancer_fx_grey.py)
        built[name] = (name, p, fxx * kk, fyy * kk)
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{kk:.3f} → {p.shape[1]}x{p.shape[0]}, 발 ({fxx * kk:.1f}, {fyy * kk:.1f})')
    _, _, L0, U0 = pack([built[n] for n in SHEET], OUT, 'lancer_0')
    _, _, Lm, Um = pack([built[n] for n in MUSOU], MUSOU_OUT, 'lancer_musou_cast')
    from lancer0_fx_holes import main as fill_holes
    fill_holes(anchors={'lancer_0': (L0, U0), 'musou': (Lm, Um)})   # 사용자가 표시한 자리: 이펙트 속 빈 곳은 채우고 흰 배경 찌꺼기는 지움 (tools/lancer0_fx_marks.json, 2026-11-10)


if __name__ == '__main__':
    main()

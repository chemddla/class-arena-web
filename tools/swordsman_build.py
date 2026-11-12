# 검사 전용 샘플(검은 머리 묶음·회색 머리띠·남색 도복·검은 하카마, 흰 배경) → 캐릭터 시트 assets/sprites/merc/swordsman_0.webp
# 사용: python tools/swordsman_build.py   (샘플은 assets/sprites/fx/samples/swordsman_*_src.png, 동작 샘플이 오는 대로 FRAMES에 늘림)
# 칸 순서: 0 대기 (오른손을 칼자루에 얹고 왼손으로 칼집을 잡은 발도 자세, 맨발에 조리) · 1 피격 (몸을 젖히며 소리침) · 2 쓰러짐 1 (앞으로 숙이며 무너짐) · 3 쓰러짐 2 (뒤로 누워 기절, 머리가 뒤쪽·칼은 허리에서 위로 솟음)
#   · 4 일반공격 1 (낮게 앉아 칼자루를 쥐고 뽑기 직전) · 5 발도 (칼을 뒤로 뽑아 든 채 낮게 벌려 선 자세)
#   · 6~8 걷기 1~3 (칼자루를 쥔 채 걸음: 받은 순서대로 walk_a 왼쪽·오른쪽, walk_b). 1·2는 비슷한 자세, 3은 뒷발을 차올린 자세라
#     재생은 1 → 3 → 2 → 3 반복 (WALK_ANIM, 게임 anims.walk에 그대로 씀)
#   · 9 스킬 시전 1 (다리를 넓게 벌리고 낮게 앉아 칼자루를 쥔 자세) · 10 시전 2 (몸 둘레 노란 불꽃) · 11 시전 3 (칼자루 앞 노란 섬광)
#   · 12 심검 (칼을 머리 위로 비스듬히 들어 막는 자세. 칼자루 아래 하늘색 잔상은 지움)
#   · 13~19 무참 1~7 (칼을 뽑아 든 베기 자세 일곱, FRAMES 주석 참고) · 20~22 일섬 1~3
# 크기 통일: 대기 자세 몸 키(머리털 끝~발, 샘플 px)를 TARGET_H로 줄임. 다른 동작은 대기와 같은 배율('idle')로 줄여 얼굴 크기를 맞춤
# 샘플 정리:
#   - 대기 샘플(768×1024)은 도트 그림을 흐리게 키운 것, 테두리 없음
#   - 피격·쓰러짐 샘플(766×250)은 세 칸을 한 장에 그린 것 + 위 잘린 글자 줄·칸 이름('[피격]' 등). 왼쪽부터 0·1번째 덩어리로 고름 (2번째 = 예전 쓰러짐 2, 지금은 안 씀)
#   - 발도 샘플(1024×498)은 흰 배경 + 같은 그림의 검은 배경 판(draw_dark). 칼날은 옅은 하늘색이라 두 배경 비교로 땀
#   - 걷기 샘플: walk_a(508×453)는 두 칸 + 왼쪽 끝 옆 칸 칼집 조각, walk_b(294×447)는 한 칸 + 양 옆 칸 조각 → 큰 덩어리만 (화면 캡처라 흰 배경 한 장씩)
#   - 머리띠 끈 사이로 비친 흰 배경은 가장자리와 안 이어져 남으므로 한 점씩 짚어 지움 (HOLES)
#   - 줄인 뒤 가장자리에 남은 밝은 회색·흰 점 한두 개는 지움 (drop_light_edge, 칼날 칸(무참·일섬)은 외톨이 점만, 불꽃·잔상 칸은 빼고)
#   - 스킬 시전 샘플(197×259)은 흰 배경 한 장 + 오른쪽 끝 옆 칸 조각 → 큰 덩어리만
#   - 시전 2·3 샘플(207×229·205×218)은 투명 배경 체크무늬(흰 242·회색 191, 약 17px 칸)가 그대로 찍힘 → 가장자리와 이어진 무채색 밝은 픽셀을 배경으로 (CHECKER)
#     몸과 떨어진 노란 불꽃도 남김 ('all'). 발 옆 회색 흙먼지는 체크무늬 회색과 구별이 안 돼 함께 빠짐
#   - 심검 샘플(208×286)은 흰 배경 한 장 + 위 잘린 칸 이름 글자·양 옆 칸 조각 → 큰 덩어리만. 칼자루 아래 옅은 하늘색 잔상은 TRAIL_OFF로 지움
#   - 쓰러짐 2 샘플(346×158)은 흰 배경 한 장, 머리카락이 왼쪽 끝에 닿음. 누운 그림이라 몸 길이로 크기를 맞춤 (FIT_W)
#     '[쓰러짐 1]' 글자는 쓰러짐 1 머리 묶음과 붙어 있어 상자로 지움 (CUT). 해상도가 대기 샘플과 달라 키를 따로 맞춤 (FIT_H)
#   - 일반공격 샘플(209×271)은 오른쪽 끝에 옆 칸 조각 점 → 가장 큰 덩어리만
#   - 어두운 배경 판이 없는 쓰러짐 2·걷기는 테두리 색을 안쪽 색으로 바꿔 회백색 테두리를 없앰 (DEFRINGE)
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
CUT = {'hurtdown': [(0, 766, 0, 8), (284, 384, 12, 45), (384, 390, 12, 36)], 'mucham4': [(168, 334, 213, 236), (150, 168, 226, 236)]}   # 지울 상자 (x0, x1, y0, y1): 위 잘린 글자 줄 · '[쓰러짐 1' · ']' (머리 묶음에 붙은 세로줄) · 무참 4 앞발에 붙은 옆 칸 조각
FIT_H = {'HURT': 78, 'ATK': 84, 'DRAW': 84, 'WALK': 86, 'CAST': 84, 'CAST2': 84, 'MIND': 86}   # 샘플마다 해상도가 달라 몸 키를 직접 정해 머리 크기를 대기와 맞춤: 피격(뒤로 젖힘) · 일반공격(낮게 앉음). 쓰러짐 1은 피격과 같은 배율
FIT_W = {'DOWN2': 108}   # 누운 그림은 머리~발 가로 길이로 맞춤
# 같은 동작을 어두운 배경에 그린 샘플 (배경색은 테두리 중앙값으로 잼):
#   swordsman_dark_src = 피격 · 쓰러짐 1 · 예전 쓰러짐 2 · 일반공격 1 (왼쪽부터, 배경 (25,25,25), 발밑 그림자·오른쪽 아래 반짝이 표시 있음)
#   swordsman_draw_dark_src = 발도 (배경 거의 검정, 오른쪽 아래 반짝이 표시)
DARK = {('hurtdown', 0): ('dark', 0), ('hurtdown', 1): ('dark', 1), ('atk0', 'big'): ('dark', 3),
        ('draw', 'big'): ('draw_dark', 0)}   # (샘플, 고른 덩어리) → (어두운 샘플, 왼쪽부터 몇 번째 그림)
SCRUB = {}   # 샘플 이름 → 지울 워터마크 다각형 꼭짓점 (샘플 px): 몸에 겹친 회색 네 갈래 별 → 안의 회색만 머리카락 남색으로 칠함 (원래 밝기 차이는 조금 남김)
# 예전 쓰러짐 2(hurtdown 2번째 그림)는 [(671, 144), (686, 158), (704, 164), (698, 176), (686, 178), (677, 192), (667, 176), (662, 168), (667, 157)]
SCRUB_HAIR = np.array([23, 25, 36])   # 둘레 머리카락 색
CHECKER = {'cast2', 'cast3'}   # 투명 배경을 체크무늬로 그린 채 캡처한 샘플
GREY_EDGE = CHECKER | {'mind'}   # 테두리 정리 때 회색 섞인 테두리까지 버리고, 색 있는 효과(불꽃·칼 잔상)는 색을 지킴
HOLES = {'idle': [(276, 269)], 'walk_a': [(72, 125), (298, 125)], 'walk_b': [(91, 108)], 'cast': [(117, 80), (105, 68)], 'cast2': [(97, 73), (107, 83)], 'cast3': [(105, 70)], 'mind': [(83, 86)],
         # 무참·일섬 (2026-11-12): 머리카락·머리띠 끈 사이, 얼굴과 머리 사이로 비친 흰 배경 (눈 흰자는 그대로)
         'mucham1': [(76, 71)], 'mucham2': [(185, 94), (204, 99)], 'mucham4': [(147, 86)],
         'issen1': [(190, 54), (176, 47), (171, 56)], 'issen2': [(83, 42), (80, 49), (76, 39), (98, 39)], 'issen3': [(93, 38)]}
# 몸에 둘러싸여 가장자리와 안 이어진 흰 틈 (샘플 px 한 점): 모두 머리띠 끈·머리카락 가닥 사이로 비친 배경. 눈 흰자는 넣지 않음
DEFRINGE = {'down2', 'walk_a', 'walk_b', 'cast'}   # 어두운 배경 판이 없는 샘플: 외곽 2px의 색을 바로 안쪽 불투명 색으로 바꾸고 거의 흰 픽셀은 투명하게 → 어두운 바탕에서 보이던 회백색 테두리 제거
SKIN = set()   # 피부가 어두운 샘플만 넣어 첫 샘플(밝은 살색)만큼 밝힘. 지금 대기 샘플은 처음부터 밝아서 비워 둠


def face_size(rgba):   # 얼굴 크기 (샘플 px): 몸 위쪽 45% 안의 가장 큰 살색 덩어리의 가로·세로 중 큰 값 (팔이나 고개 돌림으로 한쪽이 가려져도 맞게)
    c = rgba.astype(float); r, g, b, a = c[..., 0], c[..., 1], c[..., 2], c[..., 3]
    mx, mn = c[..., :3].max(axis=2), c[..., :3].min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1)
    skin = (a > 200) & (r >= g) & (g >= b - 5) & (sat > 0.15) & (sat < 0.6) & (mx > 150) & (r - b > 30)
    ys = np.where((a > 127).any(axis=1))[0]
    lab, n = ndi.label(skin)
    best = (0, 0)
    for j in range(1, n + 1):
        yy, xx = np.where(lab == j)
        if len(yy) >= 20 and yy.mean() <= ys.min() + 0.45 * (ys.max() - ys.min() + 1) and len(yy) > best[0]:
            best = (len(yy), max(yy.max() - yy.min(), xx.max() - xx.min()) + 1)
    return best[1]


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


def dark_figures(src):   # 어두운 샘플을 읽고 배경색, 그림 상자(x0, x1, y0, y1)를 왼쪽부터 (가장 큰 그림의 30% 이상만: 반짝이 표시 등은 빠짐)
    if src not in _dark:
        im = np.array(Image.open(f'{D}{src}_src.png').convert('RGB')).astype(float)
        bg = float(np.median(np.concatenate([im[0], im[-1], im[:, 0], im[:, -1]])))
        fg = np.abs(im - bg).max(axis=2) > 18
        lab, n = ndi.label(ndi.binary_dilation(fg, iterations=2))
        sz = ndi.sum(fg, lab, range(1, n + 1))
        boxes = []
        for i in range(n):
            if sz[i] < sz.max() * 0.3: continue
            ys, xs = np.where(lab == i + 1); boxes.append((xs.min(), xs.max(), ys.min(), ys.max()))
        _dark[src] = im, sorted(boxes), bg
    return _dark[src]


def dark_matte(raw, a, im, dark):
    """흰 배경·어두운 배경 두 장을 겹쳐 투명도를 다시 구함 (두 배경 비교).
    흰 배경 그림만으로는 외곽선 바깥의 흐린 회백색 테두리가 몸인지 배경인지 모름 → 어두운 그림에 맞춰 놓고
    두 장의 차이(흰 배경일수록 밝아지는 만큼)로 투명도 = 1 - (흰 - 어두운) / (255 - 어두운 배경).
    두 그림은 따로 만든 것이라 크기·위치가 조금 달라 ECC(아핀)로 맞추고, 피부 톤 등 안쪽 색도 조금 달라서
    몸 안쪽(흰 그림 덩어리를 2px 깎은 곳)은 그대로 불투명, 색은 흰 배경 그림 것을 씀. 발밑 그림자는 배경보다 어두워 투명이 됨"""
    D_im, boxes, BG = dark_figures(dark[0])
    m = a > 0.5
    ys, xs = np.where(a > 0)
    P = 10
    y0, y1 = max(0, ys.min() - P), min(raw.shape[0], ys.max() + P + 1)
    x0, x1 = max(0, xs.min() - P), min(raw.shape[1], xs.max() + P + 1)
    W = raw[y0:y1, x0:x1]
    mw = m[y0:y1, x0:x1]
    fill = ndi.binary_fill_holes(ndi.binary_dilation(mw, iterations=1))
    tmpl = np.where(fill[..., None], W, BG).mean(axis=2).astype(np.float32) / 255
    wy, wx = np.where(mw)
    dx0, dx1, dy0, _ = boxes[dark[1]]
    sc = (dx1 - dx0 + 1) / (wx.max() - wx.min() + 1)   # 흰 그림 1px → 어두운 그림 sc px (가로 폭으로 처음 값, 그림자는 아래에만 있어 위·왼쪽을 맞춤)
    A = np.array([[sc, 0, dx0 - wx.min() * sc], [0, sc, dy0 - wy.min() * sc]], np.float32)
    img = D_im.mean(axis=2).astype(np.float32) / 255
    _, A = cv2.findTransformECC(tmpl, img, A, cv2.MOTION_AFFINE,
                                (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6), None, 5)
    Dw = cv2.warpAffine(D_im.astype(np.float32), A, (W.shape[1], W.shape[0]),
                        flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderValue=(BG,) * 3).astype(float)
    a2 = np.clip(1 - (W - Dw).mean(axis=2) / (255 - BG), 0, 1)
    core = ndi.binary_erosion(mw, iterations=2) & ~ndi.binary_dilation(W.min(axis=2) > 200, iterations=1)
    a2 = np.where(core, 1.0, a2)   # 몸 안쪽은 불투명. 단 몸에 둘러싸인 흰 틈(손가락과 칼집 사이, 머리카락 사이)은 어두운 그림과 비교해 배경이면 투명
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


def defringe(raw, a, im, checker=False):
    clear = a < 0.12
    edge = ~clear & ndi.binary_dilation(clear, iterations=2)
    inner = (a > 0.99) & ~edge
    _, (iy, ix) = ndi.distance_transform_edt(~inner, return_indices=True)
    sat = raw.max(axis=2) - raw.min(axis=2)
    fix = edge & (sat < 40) if checker else edge   # 체크무늬 칸은 노란 불꽃(채도 높음)을 몸 색으로 덮지 않음
    im = im.copy(); im[fix] = im[iy, ix][fix]   # 테두리 색 = 가장 가까운 안쪽 색 (대개 검은 외곽선)
    a = np.where(edge & (raw.min(axis=2) > 200), 0.0, a)   # 흰 배경과 거의 같은 테두리 픽셀은 버림
    if checker: a = np.where(edge & (sat < 20) & (raw.mean(axis=2) > 140), 0.0, a)   # 회색 칸과 섞인 테두리도 버림
    return a, im


TRAIL_OFF = {'mind': ((165, 205, 50, 135),)}   # 심검: 칼자루 아래 옅은 하늘색 잔상은 지움 (2026-11-11 사용자 요청)
SHINY = {'draw', 'mind', 'cast2', 'cast3', 'mucham1', 'mucham2', 'mucham3', 'mucham4', 'mucham5', 'mucham6', 'mucham7', 'issen1', 'issen2', 'issen3'}   # 칼날·잔상·불꽃처럼 밝은 무채색이 몸 가장자리에 있는 칸 (drop_light_edge 안 함, 무참·일섬만 3px 이하 외톨이 밝은 점을 지움)


def drop_light_edge(p, shiny=False):   # 줄인 그림에서 투명 칸에 닿은 밝은 회색·흰 픽셀(흰 배경 찌꺼기 한두 점)을 지움
    a = p[..., 3] > 0
    rgb = p[..., :3].astype(int)
    edge = a & ndi.binary_dilation(~a)
    light = (rgb.max(axis=2) - rgb.min(axis=2) < 25) & (rgb.mean(axis=2) > 150)
    if shiny:   # 칼날 칸: 칼날처럼 밝은 픽셀이 길게 이어진 곳은 두고, 몸 가장자리의 외톨이 밝은 점(덩어리 3px 이하)만
        lab, n = ndi.label(light & a, structure=np.ones((3, 3)))
        light = light & np.isin(lab, [i + 1 for i, c in enumerate(ndi.sum(np.ones_like(lab), lab, range(1, n + 1))) if c <= 3])
    p = p.copy(); p[edge & light, 3] = 0
    return p


def erase_trail(im, box):   # 상자 안의 옅은 하늘색 잔상 덩어리(외곽선 없음)를 흰 배경으로 칠함 → 배경과 함께 빠짐
    x0, x1, y0, y1 = box
    pale = (im[..., 2] - im[..., 0] > 12) & (im.mean(axis=2) > 140)
    lab, n = ndi.label(pale)
    ids = np.unique(lab[y0:y1, x0:x1]); ids = ids[ids > 0]
    m = ndi.binary_dilation(np.isin(lab, ids)) & (im.mean(axis=2) > 120)   # 잔상 둘레의 흐린 테두리까지 (어두운 칼자루는 그대로)
    im = im.copy(); im[m] = 255
    return im


def load(name, pick=0):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    if name in SCRUB: im = scrub(im, SCRUB[name])
    if name in TRAIL_OFF: im = erase_trail(im, *TRAIL_OFF[name])
    if name in CARD:
        x0, x1, y0, y1 = CARD[name]; im = im[y0:y1, x0:x1]
    raw = im.copy()
    wm = WHITE_MIN.get(name, 222)
    white = (im.min(axis=2) > wm) & (im.max(axis=2) - im.min(axis=2) < 20)
    if name in CHECKER:   # 흰·회색(191) 체크무늬: 가장자리와 이어진 무채색 밝은 픽셀(회색 칸·흰 칸·칸 경계의 흐린 회색)이 배경
        white = (im.max(axis=2) - im.min(axis=2) < 16) & (im.mean(axis=2) >= 165)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    for x0, x1, y0, y1 in CUT.get(name, ()): bg[y0:y1, x0:x1] = True
    for hx, hy in HOLES.get(name, ()):   # 몸에 둘러싸인 흰 틈: 그 점과 이어진 흰 픽셀을 배경으로
        bg |= lab == lab[hy, hx] if white[hy, hx] else False
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    if name in CHECKER: rim[:] = False   # 배경이 회색이라 흰 배경 기준 반투명 계산은 안 맞음 → 테두리는 defringe가 정리
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)   # 흐린 외곽: 흰 배경과 섞인 만큼 반투명
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
    sz = ndi.sum(m, lab, range(1, n + 1))
    if pick == 'big':
        a = np.where(lab == 1 + int(np.argmax(sz)), a, 0)
    elif pick == 'all':   # 몸 + 따로 떨어진 불꽃 조각까지 (아주 작은 점은 버림)
        a = np.where(np.isin(lab, [i + 1 for i in range(n) if sz[i] >= 5]), a, 0)
    else:
        bigs = [i + 1 for i in range(n) if sz[i] >= sz.max() * 0.3]
        bigs.sort(key=lambda i: np.where(lab == i)[1].mean())
        a = np.where(lab == bigs[pick], a, 0)
    if (name, pick) in DARK: a, im = dark_matte(raw, a, im, DARK[(name, pick)])
    if name in DEFRINGE or name in GREY_EDGE: a, im = defringe(raw, a, im, name in GREY_EDGE)
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
    ('draw', 'draw', 'DRAW', 'big'),
    ('walk_a', 'walk1', 'WALK', 0),
    ('walk_a', 'walk2', 'WALK', 1),
    ('walk_b', 'walk3', 'WALK', 'big'),
    ('cast', 'cast', 'CAST', 'big'),
    ('cast2', 'cast2', 'CAST2', 'all'),
    ('cast3', 'cast3', 'CAST2', 'all'),
    ('mind', 'mind', 'MIND', 'big'),
    # 13~19 무참 1~7 (칼을 뽑아 든 베기 자세들, 2026-11-12): 같은 해상도로 그린 샘플이라 시전 1과 같은 배율. 옆 칸 조각·발밑 검은 조각은 'big'으로 빠짐
    ('mucham1', 'mucham1', 'FACE', 'big'),   # 낮게 웅크려 칼끝을 아래로 비스듬히 (베고 난 자세)
    ('mucham2', 'mucham2', 'FACE', 'big'),   # 칼을 뒤로 높이 치켜든 자세 (내려 베기 직전)
    ('mucham3', 'mucham3', 'FACE', 'big'),   # 낮게 벌려 서서 칼을 뒤로 뻗음
    ('mucham4', 'mucham4', 'FACE', 'big'),   # 앞으로 칼을 곧게 내지른 찌르기
    ('mucham5', 'mucham5', 'FACE', 'big'),   # 무릎을 꿇듯 낮게 앉아 칼을 앞 아래로 (베어 지나간 뒤)
    ('mucham6', 'mucham6', 'FACE', 'big'),   # 아주 낮게 웅크려 칼을 뒤로 (돌진 직전)
    ('mucham7', 'mucham7', 'FACE', 'big'),   # 크게 내디뎌 칼을 앞으로 곧게 뻗음 (마지막 일격)
    # 20~22 일섬 1~3 (2026-11-12): 무참 샘플보다 작게 그린 샘플 → 비슷한 자세(무참 3·4)와 몸 키를 비교해 시전 1 배율 × 1.135
    ('issen1', 'issen1', 'FACE', 'big'),   # 낮게 벌려 서서 칼을 뒤로 뻗음
    ('issen2', 'issen2', 'FACE', 'big'),   # 앞으로 칼을 곧게 내지름
    ('issen3', 'issen3', 'FACE', 'big'),   # 몸을 숙여 칼끝을 아래로 (베고 지나간 뒤)
]
WALK_ANIM = [6, 8, 7, 8]   # 걷기 재생 칸 순서: 걷기 1 → 3 → 2 → 3 (되풀이하면 1 3 2 3 1 3 2 …)
FOOTX = {}   # 칸 이름 → 발 가운데 (자른 그림 기준 px)


def main():
    pieces, scale = [], {}
    for src, name, k, pick in FRAMES:
        rgba, foot, bh = load(src, pick)
        if src in SKIN: rgba = lighten_skin(rgba)
        if name in FOOTX: foot = FOOTX[name]
        if k == 'FACE': sc = face_ref / face_size(rgba)   # 얼굴 크기를 대기와 같게 (샘플마다 해상도가 조금씩 달라 몸 키·폭으로는 머리 크기가 들쭉날쭉)
        else: sc = scale[k[0]] * k[1] if isinstance(k, tuple) else TARGET_H / bh if k == 'H' else FIT_H[k] / bh if k in FIT_H else FIT_W[k] / rgba.shape[1] if k in FIT_W else scale[k]
        scale[name] = sc
        if name == 'idle': face_ref = face_size(rgba) * sc
        p = shrink(rgba, sc)
        if src not in SHINY or src.startswith(('mucham', 'issen')): p = drop_light_edge(p, src in SHINY)   # 불꽃·잔상 칸(시전 2·3, 발도, 심검)은 그대로
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

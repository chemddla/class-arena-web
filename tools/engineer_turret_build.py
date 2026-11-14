# 기계공 포탑·드론 그림 → 동작 칸 띠 (가로로 칸을 이어 붙임)
# 사용: python tools/engineer_turret_build.py   (결과 칸 크기·기준점·총구 자리를 출력 → index.html ENG_TURRET_SHEET에 옮겨 적음)
#
# 샘플 (assets/sprites/fx/samples/)
#   engineer_turret_motion_src.png : 포탑 발사 동작표 (줄마다 기관포탑·박격포탑·레이저탑, 칸 5개, 아래 칸 이름 글자)
#       칸 경계는 칸 이름 글자 가운데(88·236·384·532·682)의 가운데 → COLS. 줄 제목 글자('1. 기관포 탑' 등)는 상자로 지움
#   engineer_laser_start_src.png      : 레이저탑 발사 시작 (크게)
#   engineer_laser_sustain_cool_src.png : 레이저탑 지속 발사(왼쪽) + 냉각(오른쪽) (크게)
#       → 레이저 빔은 어느 각도로든 쏘므로 그림에서 지우고(렌즈 둘레 빛만 남김) 게임이 각도에 맞춰 그림
#       → 동작표의 레이저 3~5칸은 빔이 옆 칸까지 넘어가 있어 큰 그림을 씀
#   engineer_drone_{idle,fire,dive}_src.png : 드론 평소·사격·자폭 돌진 (드론은 왼쪽을 봄)
#
# 칸 순서
#   기관포탑 0 준비 · 1 회전 시동 · 2 사격 · 3 지속 사격 · 4 반동·복귀(연기)
#   박격포탑 0 준비 · 1 장전·압축 · 2 발사(불꽃) · 3 강한 반동(연기) · 4 재장전·복귀
#   레이저탑 0 준비 · 1 충전 · 2 발사 시작 · 3 지속 발사 · 4 냉각·잔상 (2~4는 대기 칸 몸 + 큰 샘플에서 딴 효과: LASER_FX)
#   드론     0 평소 · 1 사격 · 2 자폭 돌진
#
# 크기: 0번 칸(효과 없는 몸)의 키를 BODY_H(px)로 줄이고, 같은 샘플에서 나온 칸은 같은 배율.
#   다른 샘플(큰 레이저·드론 사격/자폭)은 몸 기준 폭(BASE: 포탑은 받침 폭, 드론은 앞 철판 폭)이 0번 칸과 같아지도록 줄임
# 기준점: 포탑은 받침 바닥 가운데, 드론은 몸(가장 큰 덩어리)의 가운데
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
from engineer_build import defringe   # 테두리 흰 찌꺼기 정리 (포탑 외곽선은 짙은 갈색이라 outline=110, 흰 연기를 살리려고 외곽선 근처의 밝은 테두리만: near, 3배 그림이라 깎는 횟수·거리도 RES배)

S = 'assets/sprites/fx/samples/engineer_'
OUT = 'assets/sprites/fx/engineer_turret_{}.webp'
COLS = [0, 162, 310, 458, 606, 765]
ROW = {'gatling': (92, 290), 'mortar': (372, 645), 'laser': (790, 985)}
TITLE = {'gatling': (0, 200, 92, 128), 'mortar': (0, 200, 372, 418)}   # 줄 제목 글자 (x0, x1, y0, y1)
BODY_H = {'gatling': 46, 'mortar': 50, 'laser': 54, 'drone': 34}   # 게임에서 보이는 몸 키 (px)
RES = 3   # 그림은 RES배 크게 만들고 게임이 1/RES로 줄여 그림 → 화면을 확대해도 선명 (출력: cw·ch는 그림 px, ax·ay·muzzle은 게임 px)
# 칸: (샘플, 자를 상자 x0,x1,y0,y1, 지울 상자들)
MARGIN = 70   # 동작표 칸은 양옆으로 넓게 잘라 낸 뒤, 덩어리 가운데가 이 칸 경계 안에 있는 것만 남김 (불꽃·연기가 경계를 넘어가도 잘리지 않게)
BALL = (505, 552, 360, 412)   # 박격포 발사 칸 위로 날아가는 포탄 (옆 칸 자리에 있어 지움, 포탄은 게임이 따로 그림)


GAT_COLS = [0, 165, 305, 460, 607, 765]
GAT_EXT = 25   # 기관포 칸 오른쪽으로 더 잘라 넘어간 자기 총구 끝·불꽃을 살림 (더 자른 곳에선 이 칸 몸과 불꽃 색만 남김)   # 기관포 줄: 칸 경계 = 탄약통 왼쪽 끝 (불꽃이 옆 칸 탄약통과 붙어 있어 덩어리로 못 가름, 옆으로 넓게 자르지 않음)


def sheet(kind, i):
    y0, y1 = ROW[kind]
    if kind == 'gatling':
        return ('turret_motion', (GAT_COLS[i], min(765, GAT_COLS[i + 1] + GAT_EXT), y0, y1), [TITLE[kind]], 'gat')
    er = ([TITLE[kind]] if kind in TITLE else []) + ([BALL] if kind == 'mortar' else [])
    return ('turret_motion', (max(0, COLS[i] - MARGIN), min(765, COLS[i + 1] + MARGIN), y0, y1), er, (COLS[i], COLS[i + 1]))
FRAMES = {
    'gatling': [sheet('gatling', i) for i in range(5)],
    'mortar': [sheet('mortar', i) for i in range(5)],
    'laser': [sheet('laser', 0), sheet('laser', 1),
              ('laser_start', (0, 1024, 0, 930), [(780, 1024, 0, 1024)], None),
              ('laser_sustain_cool', (0, 640, 0, 515), [(415, 640, 0, 572)], None),
              ('laser_sustain_cool', (640, 1024, 0, 515), [(985, 1024, 470, 572)], None)],
    'drone': [('drone_idle', (0, 358, 0, 357), [], None), ('drone_fire', (0, 563, 0, 470), [], None), ('drone_dive', (0, 349, 0, 433), [], None)],
}
SAME_SCALE = {'drone'}   # 샘플 세 장의 해상도가 같음 (앞 철판 폭 80·79px) → 한 배율
DRONE_ANCHOR = {'drone_idle': (97, 173), 'drone_fire': (267, 193), 'drone_dive': (136, 251)}   # 앞 철판 가운데 (샘플 px) = 기준점
MUZZLE0 = {'gatling': (0.5, 0.28), 'mortar': (0.3, 0.12), 'laser': (0.37, 0.27), 'drone': (-0.42, 0.88)}   # 0번 칸 몸 상자 기준 (가운데에서 폭의 몇 배, 위에서 키의 몇 배) · 기관포 0.28 = 쏘는 칸 총열 가운데 (2026-11-14, 0.36은 3.6px 낮았음)


def load(name):
    return np.array(Image.open(S + name + '_src.png').convert('RGBA')).astype(float)


def cut(rgba, box, erase, own=None):
    x0, x1, y0, y1 = box
    im = rgba.copy()
    for ex0, ex1, ey0, ey1 in erase:
        im[ey0:ey1, ex0:ex1, :3] = 255
    im = im[y0:y1, x0:x1]
    fire = ext = None
    if own == 'gat':
        R, G, B = im[..., 0], im[..., 1], im[..., 2]
        fire = (R > 190) & (B < 150) & (R - B > 70)   # 총구 불꽃 (주황·노랑·빨강)
        ext = np.zeros(fire.shape, bool); ext[:, -GAT_EXT:] = True if x1 < 765 else False   # 옆 칸으로 더 잘라 낸 곳
        lft = np.zeros(fire.shape, bool); lft[:, :40] = True   # 칸 왼쪽 40px의 불꽃 색 = 앞 칸 불꽃 끝
        im[..., :3] = np.where((lft & fire)[..., None], 255, im[..., :3])
    rgb = im[..., :3]
    white = (rgb.min(axis=2) > 232) & (rgb.max(axis=2) - rgb.min(axis=2) < 18)
    lab, nw = ndi.label(white)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    sizes = ndi.sum(white, lab, range(1, nw + 1))
    bg |= np.isin(lab, 1 + np.where(sizes >= 40)[0])   # 사슬 고리·전선 사이에 갇힌 흰 배경 (큰 것)
    # 작게 갇힌 흰·연회색 배경 (사슬과 몸 사이 틈 등, 흐린 샘플이라 176~255 연회색이 섞임): 6px 이상이고 둘레의 절반 넘게가 검은 외곽선이면 배경
    #   (반짝임은 6px 미만, 불꽃 속 흰 심·연기는 둘레가 밝아서 남음)
    dark = rgb.max(axis=2) < 110
    pale = (rgb.min(axis=2) > 165) & (rgb.max(axis=2) - rgb.min(axis=2) < 25) & ~np.isin(lab, list(edge))
    plab, pn = ndi.label(pale)
    psz = ndi.sum(pale, plab, range(1, pn + 1))
    for i in np.where((psz >= 6) & (psz < 400))[0]:
        m = plab == i + 1
        ys, xs = np.where(m)
        sl = (slice(max(0, ys.min() - 1), ys.max() + 2), slice(max(0, xs.min() - 1), xs.max() + 2))
        ring = ndi.binary_dilation(m[sl]) & ~m[sl]
        if ring.any() and dark[sl][ring].mean() >= 0.5:
            bg |= m
    bg = ndi.binary_dilation(bg, iterations=2) & (rgb.min(axis=2) > 150)
    a = np.where(bg, 0, 255)
    body, n = ndi.label(a > 0, structure=np.ones((3, 3)))
    sizes = ndi.sum(a > 0, body, range(1, n + 1))
    ok = sizes >= 12   # 탄피·불티·연기도 남김 (12px 미만 티끌만 지움)
    if own == 'gat':   # 자른 상자 왼쪽 끝에 닿은 조각 = 앞 칸 불꽃·탄피 → 지움 (몸 = 가장 큰 덩어리는 남김)
        ok &= np.array([not (body[:, :22] == i).any() for i in range(1, n + 1)])   # 왼쪽 22px 안에 걸친 조각
        bi = int(np.argmax(sizes)); ok[bi] = True
        # 옆 칸으로 더 잘라 낸 곳: 이 칸 몸(총구 끝)과 불꽃만 남기고 다음 칸 탄약통·사슬은 지움
        a = np.where(ext & ~(body == bi + 1) & ~firemask(im[..., :3]), 0, a)   # (밝은 불꽃만: 붉은 손잡이는 지움)
    elif own:
        cx = ndi.center_of_mass(a > 0, body, range(1, n + 1))
        ok &= np.array([own[0] <= c[1] + x0 < own[1] for c in cx])
    big = 1 + int(np.argmax(np.where(ok, sizes, 0)))
    a = np.where(np.isin(body, 1 + np.where(ok)[0]), a, 0)
    im[..., 3] = a
    fill_specks(im)
    return im, body == big   # 그림, 몸(가장 큰 덩어리)


def fill_specks(im, maxpx=12):
    """몸 안에 박힌 작은 순백 점(흐린 샘플이 남긴 구멍·잡티)을 둘레 색(중간값)으로 메움.
    둘레에 불꽃·청록 같은 진한 색이 있으면(불꽃 속 흰 심·렌즈 반짝임) 그대로 둠."""
    rgb, a = im[..., :3], im[..., 3] > 0
    pw = a & (rgb.min(axis=2) > 225) & (rgb.max(axis=2) - rgb.min(axis=2) < 20)
    colored = (rgb.max(axis=2) - rgb.min(axis=2)) > 70
    lab, n = ndi.label(pw)
    for sl, i in zip(ndi.find_objects(lab), range(1, n + 1)):
        ys, xs = sl
        sl2 = (slice(max(0, ys.start - 2), ys.stop + 2), slice(max(0, xs.start - 2), xs.stop + 2))
        m = lab[sl2] == i
        if m.sum() > maxpx:
            continue
        ring = ndi.binary_dilation(m, iterations=2) & ~m & a[sl2]
        if not ring.any() or colored[sl2][ring].any():
            continue
        sub = im[sl2]
        sub[m, :3] = np.median(sub[..., :3][ring], axis=0)


def firemask(c):
    R, G, B = c[..., 0].astype(int), c[..., 1].astype(int), c[..., 2].astype(int)
    return (R > 200) & (R + G > 320) & (B < 150) & (G <= R)   # 밝은 주황·노랑 불빛 (구릿빛 몸 (170,100,60)은 안 걸림)


def defire(s, passes=9):
    """불꽃 둘레 테두리의 흰 배경 찌꺼기: 투명한 곳과 맞닿고 불꽃 색 옆에 붙은 밝은 무채색 픽셀을 passes번 깎음"""
    out = s.copy()
    cross = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    for _ in range(passes):
        a = out[..., 3] > 0
        edge = a & ndi.binary_dilation(~a, structure=cross)
        c = out[..., :3].astype(int)
        pale = (c.min(axis=2) > 190) & (c.max(axis=2) - c.min(axis=2) < 45)
        junk = edge & pale & ndi.binary_dilation(a & firemask(c), iterations=2)
        if not junk.any():
            break
        out[junk] = 0
    return out


def drop_back_fire(s, ax):
    """기관포: 몸 가운데(기준점 x)보다 왼쪽에 있는 불꽃 색 덩어리 = 앞 칸 총구 불꽃이 잘려 들어온 것 → 지움 (이 칸 불꽃은 늘 총구 = 오른쪽)"""
    out = s.copy()
    a = out[..., 3] > 0
    c = out[..., :3].astype(int)
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    f = a & (firemask(c) | ((R > 170) & (R - B > 80) & (G < R - 30)))   # 빨간 불꽃 줄기까지
    lab, n = ndi.label(f, structure=np.ones((3, 3)))
    if not n:
        return out
    sizes = ndi.sum(f, lab, range(1, n + 1))
    cx = ndi.center_of_mass(f, lab, range(1, n + 1))
    for i, (cy, x) in enumerate(cx):
        if x < ax - 10 and sizes[i] < 600:   # 작은 덩어리만 (구릿빛 몸이 같이 걸려도 크기로 걸러짐)
            out[lab == i + 1] = 0
    # 몸 왼쪽의 작은 조각(불티 끝 점 등)은 색과 상관없이 지움 (탄피는 오른쪽 아래로 튐)
    a = out[..., 3] > 0
    lab, n = ndi.label(a, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndi.sum(a, lab, range(1, n + 1))
        cx = ndi.center_of_mass(a, lab, range(1, n + 1))
        for i, (cy, x) in enumerate(cx):
            if x < ax - 10 and sizes[i] < 60:
                out[lab == i + 1] = 0
    return out


ALIGN = {'gatling', 'mortar', 'laser'}   # 동작표 칸을 대기 칸 몸통에 맞춰 옮김 (register)
GAT_TIP = 40   # 기관포 총구 끝 = 기준점에서 오른쪽으로 (게임 px)


def clip_front(s, ax):
    """기관포: 총구 끝보다 오른쪽엔 불꽃(밝은 주황·노랑·빨강 + 그 안 흰 심)만 남김 (다음 칸 손잡이가 불꽃에 붙어 들어옴),
    몸 오른쪽(기준점 +30px 넘어)에서 떨어진 불꽃 아닌 조각(다음 칸 사슬 끝)도 지움"""
    out = s.copy()
    c = out[..., :3].astype(int)
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    flame = firemask(c) | ((R > 180) & (R - B > 100) & (G < R - 40))
    flame |= ndi.binary_dilation(flame, iterations=3) & (c.min(axis=2) > 190)
    tip = int(round(ax + GAT_TIP * RES))
    cut_m = np.zeros(flame.shape, bool); cut_m[:, tip:] = True
    out[cut_m & ~flame] = 0
    a = out[..., 3] > 0
    lab, n = ndi.label(a, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndi.sum(a, lab, range(1, n + 1))
        big = 1 + int(np.argmax(sizes))
        for sl, i in zip(ndi.find_objects(lab), range(1, n + 1)):
            if i == big or sl[1].start <= ax + 30 * RES:
                continue
            m = lab == i
            if not flame[m].mean() > 0.5:
                out[m] = 0
    return out


def body_mask(s):
    """위치 맞춤용 몸통: 불꽃·연기(밝은 무채색)·불티를 뺀 불투명 픽셀"""
    c = s[..., :3].astype(int)
    a = s[..., 3] > 0
    pale = (c.min(axis=2) > 150) & (c.max(axis=2) - c.min(axis=2) < 40)
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    hot = firemask(c) | ((R > 170) & (R - B > 80) & (G < R - 30))
    return a & ~pale & ~hot


def register(m0, ax0, ay0, m, ax, ay, rng=15):
    """대기 칸 몸통(m0, 기준점 ax0·ay0)과 가장 많이 겹치도록 이 칸(m, 기준점 ax·ay)을 옮길 (dx, dy) — 그림 px"""
    H = int(max(ay0, ay) + max(m0.shape[0] - ay0, m.shape[0] - ay)) + 4 * rng + 4
    W = int(max(ax0, ax) + max(m0.shape[1] - ax0, m.shape[1] - ax)) + 4 * rng + 4
    def put(mm, x, y):
        cv = np.zeros((H, W), bool); cv[y:y + mm.shape[0], x:x + mm.shape[1]] = mm; return cv
    cx, cy = 2 * rng + int(round(max(ax0, ax))), 2 * rng + int(round(max(ay0, ay)))   # 같은 기준점 자리
    base = put(m0, cx - int(round(ax0)), cy - int(round(ay0)))
    best, bd = -1, (0, 0)
    for dy in range(-rng, rng + 1):
        for dx in range(-rng, rng + 1):
            mv = put(m, cx - int(round(ax)) + dx, cy - int(round(ay)) + dy)
            sc = (base & mv).sum() / max(1, (base | mv).sum())
            if sc > best:
                best, bd = sc, (dx, dy)
    return bd, best


def despeck(s, minpx=60, sat=50):
    """줄인 뒤 몸에서 떨어진 작은 무채색 티끌(흰·회색 점) 지움. 불티·탄피처럼 색이 있는 조각은 남김."""
    a = s[..., 3] > 0
    lab, n = ndi.label(a, structure=np.ones((3, 3)))
    if n < 2:
        return s
    sizes = ndi.sum(a, lab, range(1, n + 1))
    c = s[..., :3].astype(int)
    sat_px = c.max(axis=2) - c.min(axis=2)
    msat = ndi.mean(sat_px, lab, range(1, n + 1))
    drop = (sizes < minpx) & (msat < sat)
    out = s.copy()
    out[np.isin(lab, 1 + np.where(drop)[0])] = 0
    return out


def teal_center(im, a=None, cyan=False):
    """렌즈 가운데 (가장 큰 청록 덩어리). cyan=True면 발사 고리(밝은 청록)"""
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    al = im[..., 3] > 0 if a is None else a
    m = ((G > 140) & (B > 140) & (R < 170) & (G - R > 40)) if cyan else ((G > 120) & (B > 110) & (G - R > 50))
    m &= al
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1))
    cy, cx = ndi.center_of_mass(m, lab, 1 + int(np.argmax(sizes)))
    return cx, cy


# 레이저탑 2~4칸: 큰 샘플은 몸 모양·비율이 대기 칸과 달라 몸은 대기 칸을 그대로 쓰고 효과만 따서 렌즈 자리에 얹음
#   2 발사 시작 = 대기 몸 + 청록 고리·전기 / 3 지속 발사 = 달아오른(주황) 대기 몸 + 청록 고리 + 불티 / 4 냉각 = 대기 몸 + 연기
LASER_FX = {2: 'ring', 3: 'hot', 4: 'smoke'}


def laser_overlay(im, body, mode):
    R, G, B = [im[..., i] for i in range(3)]
    al = im[..., 3] > 0
    cyan = al & (G > 140) & (B > 140) & (R < 170) & (G - R > 40)
    core = al & (im[..., :3].min(axis=2) > 225) & ndi.binary_dilation(cyan, iterations=3)   # 고리 안 흰 빛
    if mode == 'smoke':
        pale = al & ~body & (im[..., :3].min(axis=2) > 140) & (im[..., :3].max(axis=2) - im[..., :3].min(axis=2) < 35)
        m = pale
    else:
        m = cyan | core
        if mode == 'hot':
            m |= al & ~body & (R > 190) & (B < 150) & (R - B > 70)   # 몸에서 튄 불티
    ov = im.copy()
    ov[..., 3] = np.where(m, 255, 0)
    return ov


def heat(s):   # 지속 발사: 구릿빛 몸을 주황으로 달굼
    out = s.astype(float).copy()
    R, G, B = out[..., 0], out[..., 1], out[..., 2]
    warm = (out[..., 3] > 0) & (R > G + 8) & (R > B + 15)
    out[..., 0] = np.where(warm, np.minimum(255, R * 1.2 + 35), R)
    out[..., 1] = np.where(warm, G * 0.8, G)
    out[..., 2] = np.where(warm, B * 0.6, B)
    return out.clip(0, 255).astype(np.uint8)


def bbox(m):
    ys, xs = np.where(m)
    return xs.min(), xs.max() + 1, ys.min(), ys.max() + 1


def base_w(kind, body):   # 크기 맞출 기준 폭
    x0, x1, y0, y1 = bbox(body)
    if kind == 'drone':
        return x1 - x0
    rows = body[y1 - max(3, (y1 - y0) // 12): y1]   # 받침 아래쪽 줄들
    xs = np.where(rows.any(axis=0))[0]
    return xs.max() - xs.min() + 1


def anchor(kind, body):
    x0, x1, y0, y1 = bbox(body)
    if kind == 'drone':
        return (x0 + x1) / 2, (y0 + y1) / 2
    rows = body[y1 - max(3, (y1 - y0) // 12): y1]
    xs = np.where(rows.any(axis=0))[0]
    return (xs.min() + xs.max() + 1) / 2, y1


def main():
    srcs = {}
    info = {}
    for kind, frames in FRAMES.items():
        cuts = []
        for src, box, er, own in frames:
            if src not in srcs:
                srcs[src] = load(src)
            cuts.append((src,) + cut(srcs[src], box, er, own) + (box,))
        s0, im0, b0, box0 = cuts[0]
        anc = lambda src, body, box: ((DRONE_ANCHOR[src][0] - box[0], DRONE_ANCHOR[src][1] - box[2]) if src in DRONE_ANCHOR else anchor(kind, body))
        bx0, bx1, by0, by1 = bbox(b0)
        sc0 = BODY_H[kind] * RES / (by1 - by0)
        bw0 = base_w(kind, b0) * sc0
        placed = []
        for src, im, body, box in cuts:
            sc = sc0 if (src == s0 or kind in SAME_SCALE) else bw0 / base_w(kind, body)
            ax, ay = anc(src, body, box)
            s = defire(defringe(shrink(im, sc), passes=4 * RES, light=200, outline=110, near=4 * RES), passes=3 * RES)
            if kind == 'gatling':
                s = drop_back_fire(s, ax * sc)
                s = clip_front(s, ax * sc)
            s = despeck(s)
            placed.append((s, ax * sc, ay * sc))
        if kind in ALIGN:   # 동작표에서 딴 칸을 대기 칸 몸통 위치에 맞춤 (기준점을 옮김)
            s0_, ax0_, ay0_ = placed[0]
            m0 = body_mask(s0_)
            for i in range(1, len(placed)):
                if cuts[i][0] != 'turret_motion':
                    continue
                s_, ax_, ay_ = placed[i]
                (dx, dy), sc_ = register(m0, ax0_, ay0_, body_mask(s_), ax_, ay_)
                placed[i] = (s_, ax_ - dx, ay_ - dy)
                print(kind, i, '옮김', dx, dy, '겹침', round(float(sc_), 3))
        if kind == 'laser':
            s_idle, ax0, ay0 = placed[0]
            lx0, ly0 = teal_center(im0)
            lx0, ly0 = lx0 * sc0, ly0 * sc0   # 대기 칸 렌즈 (줄인 그림 좌표)
            for i, mode in LASER_FX.items():
                src, im, body, box = cuts[i]
                sc = bw0 / base_w(kind, body)
                lx, ly = teal_center(im, cyan=(mode != 'smoke'))
                ov = shrink(laser_overlay(im, body, mode), sc)
                dx, dy = int(round(lx0 - lx * sc)), int(round(ly0 - ly * sc))
                base = heat(s_idle) if mode == 'hot' else s_idle
                px, py = max(0, -dx), max(0, -dy)   # 효과가 대기 그림 밖으로 나가면 바탕을 넓힘
                W = max(px + base.shape[1], px + dx + ov.shape[1]); H = max(py + base.shape[0], py + dy + ov.shape[0])
                cv = np.zeros((H, W, 4), np.uint8)
                cv[py:py + base.shape[0], px:px + base.shape[1]] = base
                reg = cv[py + dy:py + dy + ov.shape[0], px + dx:px + dx + ov.shape[1]]
                cv[py + dy:py + dy + ov.shape[0], px + dx:px + dx + ov.shape[1]] = np.where(ov[..., 3:] > 0, ov, reg)
                placed[i] = (cv, ax0 + px, ay0 + py)
        L = max(ax for s, ax, ay in placed); R = max(s.shape[1] - ax for s, ax, ay in placed)
        T = max(ay for s, ax, ay in placed); B = max(s.shape[0] - ay for s, ax, ay in placed)
        cw, ch, AX, AY = int(np.ceil(L + R)) + 2, int(np.ceil(T + B)) + 2, int(np.ceil(L)) + 1, int(np.ceil(T)) + 1
        strip = np.zeros((ch, cw * len(placed), 4), np.uint8)
        for i, (s, ax, ay) in enumerate(placed):
            x = i * cw + AX - int(round(ax)); y = AY - int(round(ay))
            h, w = s.shape[:2]
            region = strip[y:y + h, x:x + w]
            strip[y:y + h, x:x + w] = np.where(s[..., 3:] > 0, s, region)
        Image.fromarray(strip, 'RGBA').save(OUT.format(kind), 'WEBP', lossless=True)
        # 0번 칸 몸 상자 (기준점 기준 좌표)
        a0 = anc(s0, b0, box0)
        bl, bt = (bx0 - a0[0]) * sc0, (by0 - a0[1]) * sc0
        bwid, bhei = (bx1 - bx0) * sc0, (by1 - by0) * sc0
        mx, my = MUZZLE0[kind]
        muzzle = [round((bl + bwid / 2 + bwid * mx) / RES, 1), round((bt + bhei * my) / RES, 1)]
        info[kind] = {'cw': cw, 'ch': ch, 'res': RES, 'ax': round(AX / RES, 2), 'ay': round(AY / RES, 2), 'n': len(placed), 'h': BODY_H[kind], 'muzzle': muzzle}
    print(json.dumps(info))


if __name__ == '__main__':
    main()

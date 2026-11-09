# 성녀 기본 외형(healer_0) 교체: 은발·흰 베일·흰 금빛 수도복·금빛 십자 지팡이 샘플 → assets/sprites/merc/healer_0.webp
# 사용: python tools/healer0_build.py
# 샘플 (assets/sprites/merc/samples/healer_edit_*):
#   흰 배경: 1_idle_src.webp (681×1024, 대기 1칸, 아주 크게 그려짐) · 2_walk_src.png (537×187, 걷기 3칸) · 3_attack_heal_src.png (181×180, 일반공격 = 치유 1칸, 반짝이 포함)
#           4_hurt_src.png (168×159, 피격 1칸) · 5_fall_src.png (514×159, 쓰러짐 2칸: 무릎 꿇음 → 엎드림, 지팡이는 따로 떨어져 있음)
#           6_skill_cast_src.png (스킬 시전 2칸 + 잘린 칸 — 8번 검은 배경 장에 다섯 칸이 다 있어서 안 씀)
#           7_hidden_skill_src.webp (783×749, 히든 스킬 [기적] 다섯 단계, 칸 아래 글씨)
#   검은 배경: 8_skill_hidden_black_src.webp (681×1024): 윗줄 스킬 시전 5칸 (준비 · 시작 · 시전 · 발동 · 마무리) / 아랫줄 히든 스킬 5단계 (7번과 같은 그림, 약 0.87배)
# 칸 순서 (healer_0): 0 대기 · 1~3 걷기 · 4 일반공격 (치유) · 5 피격 · 6~7 쓰러짐 · 8~12 스킬 (준비 · 시작 · 시전 · 발동 · 마무리)
# 히든 스킬 [기적] 시전 그림 → assets/sprites/fx/healer_miracle_cast.webp (HEALER_MIRACLE_FX, 5칸: 집중 · 상승 · 시전 · 연출 · 마무리)
# 배경 지우기
#   흰 배경 장: 가장자리에 이어진 흰색만 배경 (흰 수도복 속 새하얀 곳을 지우지 않게 갇힌 흰 배경은 GAP 상자로만)
#   검은 배경 스킬 칸: 몸 = 금빛이 아닌 덩어리를 채운 것 (+ 그 둘레 4px 안의 금빛 장식) → 불투명, 나머지(반짝이·발밑 금빛 고리)는 밝기를 알파로
#   히든 스킬: 흰 배경 장(7)과 검은 배경 장(8)을 맞대어 두 장이 맞는 곳에서 알파를 정확히 구함 (tools/archer0_build.py의 폭풍 시전과 같은 방식)
# 크기: 칸마다 얼굴(가장 큰 살색 덩어리) 크기를 대기 칸에 맞춤. 같은 장의 칸은 같은 배율 (쓰러짐은 피격 장, 히든 스킬은 검은 배경 스킬 줄과 같은 배율)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
from mage0_build import defringe
from archer0_build import shrink_soft

D = 'assets/sprites/merc/samples/healer_edit_'
OUT = 'assets/sprites/merc/healer_0.webp'
CAST_OUT = 'assets/sprites/fx/healer_miracle_cast.webp'
TRAP_DARK = 0.35   # 갇힌 흰 덩어리 둘레 중 검은 윤곽 비율이 이보다 크면 배경
IDLE_H = 100   # 대기 칸 키 (베일 꼭대기~발)
BLACK = '8_skill_hidden_black_src.webp'
WHITE7 = '7_hidden_skill_src.webp'

# (칸 이름, 샘플, 상자, 덩어리 고르기: 'one' 몸만 · 'all' 큰 덩어리 모두 · 'spark' 몸 + 둘레 반짝이, 배율 기준 장)
FRAMES = [
    ('idle', '1_idle_src.webp', None, 'one', 'idle'),
    ('walk0', '2_walk_src.png', (0, 0, 165, 187), 'one', 'walk'),
    ('walk1', '2_walk_src.png', (180, 0, 360, 187), 'one', 'walk'),
    ('walk2', '2_walk_src.png', (370, 0, 537, 187), 'one', 'walk'),
    ('atk', '3_attack_heal_src.png', None, 'spark', 'atk'),
    ('hurt', '4_hurt_src.png', None, 'one', 'hurt'),
    ('down0', '5_fall_src.png', (0, 0, 214, 159), 'one', 'hurt'),
    ('down1', '5_fall_src.png', (214, 0, 514, 159), 'all', 'hurt'),
]
# 9번 검은 배경 장 기본 칸: (칸 이름, 상자, 덩어리 고르기) — 이동 1칸째는 대기와 같아 빼고, 공격은 반짝이 칸(2칸째), 쓰러짐은 지팡이 떨군 두 칸
BASE_BLACK = '9_base_black_src.webp'
BASE = [('idle', (36, 36, 190, 206), 'one'),
        ('walk0', (226, 232, 376, 408), 'one'),
        ('walk1', (413, 232, 563, 408), 'one'),
        ('walk2', (597, 232, 748, 408), 'one'),
        ('atk', (215, 443, 402, 624), 'spark'),
        ('hurt', (42, 652, 211, 820), 'one'),
        ('down0', (205, 846, 423, 1008), 'all'),
        ('down1', (418, 900, 712, 1018), 'all')]
GROUP_H = {'walk': 99, 'hurt': 87, 'down': 84}   # 이동(첫 칸)·피격·쓰러짐(첫 칸) 키
BASE_MARK = (642, 901, 683, 942)   # ✦ 표식 (지움)
SKILL_ROW = (62, 262)   # 검은 배경 장 윗줄 (y)
OUTLINE = np.array([43.0, 41.0, 39.0])   # 대기 칸 바깥 윤곽선 평균 색
SKILL_NAMES = ['ready', 'start', 'cast', 'fire', 'end']
# 히든 스킬: (칸 이름, 흰 배경 상자, 검은 배경 상자) — 연출 칸 발밑의 회색 그림자 타원은 상자 밖으로 뺌
HIDDEN = [('focus', (20, 95, 240, 299), (14, 455, 210, 636)),
          ('rise', (255, 15, 458, 294), (220, 385, 405, 630)),
          ('chant', (462, 0, 716, 290), (405, 366, 630, 624)),
          ('show', (40, 355, 512, 661), (32, 688, 446, 955)),
          ('end', (560, 485, 742, 692), (492, 800, 650, 982))]


HIDDEN_LIFT = {}
# 발 자리 (검은 배경 장 좌표): 금빛 단·날개에 몸이 조각나 자동으로 못 잡는 칸만. 신발 바닥 가운데
#   연출은 떠 있는 자세 → 샘플의 그림자 타원(y 965)을 땅으로 (신발은 그보다 약 20px 위)
HIDDEN_FOOT = {'rise': (307, 618), 'chant': (520, 613), 'show': (240, 965)}


def rgb(src):
    return np.array(Image.open(D + src).convert('RGB')).astype(float)


def black_sil(box):
    # 9번 검은 배경 장 한 칸의 실루엣 (배경은 새까맘 0, 몸 안의 새까만 틈은 배경)
    B = rgb(BASE_BLACK)
    x0, y0, x1, y1 = BASE_MARK; B[y0:y1, x0:x1] = 0
    x0, y0, x1, y1 = box
    v = B[y0:y1, x0:x1].max(axis=2)
    fg = v > 14
    lab, n = ndi.label(ndi.binary_dilation(fg, iterations=2))
    sz = ndi.sum(fg, lab, range(1, n + 1))
    fg &= np.isin(lab, 1 + np.where(sz >= 3)[0])
    ys, xs = np.where(fg)
    return fg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def guide_bg(im, bg, box):
    # 흰 배경 장의 불투명 덩어리와 검은 배경 장 실루엣을 배율·위치를 바꿔 가며 맞대고, 실루엣 밖의 흰빛을 배경으로 돌려줌
    G = black_sil(box)
    fgw = ~bg
    lab, n = ndi.label(fgw)
    sz = ndi.sum(fgw, lab, range(1, n + 1))
    fgw &= np.isin(lab, 1 + np.where(sz >= 30)[0])
    ys, xs = np.where(fgw)
    oy, ox = ys.min(), xs.min()
    Wc = fgw[oy:ys.max() + 1, ox:xs.max() + 1]
    s0 = Wc.shape[0] / G.shape[0]   # 흰 장 / 검은 장
    small = lambda m, s: np.array(Image.fromarray(m.astype(np.uint8) * 255).resize((max(1, round(m.shape[1] / s)), max(1, round(m.shape[0] / s))), Image.BILINEAR)) > 127
    P = 8
    Gp = np.pad(G, P)
    best = None
    for s in s0 * np.arange(0.95, 1.051, 0.01):
        w = small(Wc, s)
        if w.shape[0] > Gp.shape[0] or w.shape[1] > Gp.shape[1]: continue
        for dy in range(0, Gp.shape[0] - w.shape[0] + 1):
            for dx in range(0, Gp.shape[1] - w.shape[1] + 1):
                g = Gp[dy:dy + w.shape[0], dx:dx + w.shape[1]]
                iou = (g & w).sum() / max(1, (g | w).sum())
                if best is None or iou > best[0]: best = (iou, s, dy, dx, w.shape)
    iou, s, dy, dx, (h, w) = best
    print(f'  실루엣 맞춤 IoU {iou:.3f} ×{s:.3f}')
    g = Gp[dy:dy + h, dx:dx + w]
    gw = np.array(Image.fromarray(g.astype(np.uint8) * 255).resize((Wc.shape[1], Wc.shape[0]), Image.BILINEAR)) > 127
    full = np.zeros_like(bg); full[oy:oy + Wc.shape[0], ox:ox + Wc.shape[1]] = gw
    full = ndi.binary_dilation(full, iterations=max(1, round(s * 1.0)))   # 검은 장 1px 만큼 여유
    # 픽셀 단위로 깎으면 맞춤이 어긋난 곳(베일 가장자리)이 뜯김 → 흰빛 덩어리 단위로, 대부분(65%↑)이 실루엣 밖인 덩어리만 배경
    whiteish = (im.min(axis=2) > 200) & (im.max(axis=2) - im.min(axis=2) < 28) & ~bg
    lab, n = ndi.label(whiteish)
    if n == 0: return np.zeros_like(bg)
    tot = ndi.sum(whiteish, lab, range(1, n + 1))
    out = ndi.sum(whiteish & ~full, lab, range(1, n + 1))
    return np.isin(lab, 1 + np.where(out / np.maximum(tot, 1) > 0.65)[0])


def load_white(src, box, pick, guide=None):
    im = rgb(src)
    if box:
        x0, y0, x1, y1 = box; im = im[y0:y1, x0:x1]
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), constant_values=255)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    # 갇힌 흰 배경 (지팡이·머리카락·팔 사이): 새하얗고, 둘레가 대부분 검은 윤곽인 덩어리
    #   (수도복 속 새하얀 곳은 둘레가 연회색 음영·금빛 장식이라 남음)
    dark = im.max(axis=2) < 90
    for i, sl in enumerate(ndi.find_objects(lab)):
        if sl is None or (i + 1) in edge: continue
        m = lab[sl] == i + 1
        if m.sum() < 12 or im[sl][m].min(axis=1).mean() < 244: continue
        ring = ndi.binary_dilation(np.pad(m, 3), iterations=3) & ~np.pad(m, 3)
        d = np.pad(dark[sl], 3)
        # 둘레 3px 안에 검은 윤곽이 얼마나 있는지 (덩어리 바깥 상자가 잘리지 않게 넓혀서 봄)
        y0, x0 = max(0, sl[0].start - 3), max(0, sl[1].start - 3)
        big = dark[y0:sl[0].stop + 3, x0:sl[1].stop + 3]
        mm = np.zeros_like(big); mm[sl[0].start - y0:sl[0].stop - y0, sl[1].start - x0:sl[1].stop - x0] = m
        rg = ndi.binary_dilation(mm, iterations=3) & ~mm
        if big[rg].mean() > TRAP_DARK: bg |= (lab == i + 1)
    if guide:   # 9번 검은 배경 장의 같은 칸 실루엣 밖에 있는 흰빛 = 배경 (갇힌 흰 배경·흰 테두리)
        bg |= guide_bg(im, bg, guide)
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    m = a > 0.3
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=3))
    sz = ndi.sum(m, lab, range(1, n + 1))
    big = int(np.argmax(sz)) + 1
    if pick == 'one':
        keep = lab == big
    elif pick == 'all':
        keep = np.isin(lab, 1 + np.where(sz >= 200)[0])
    else:   # 몸 + 몸 둘레 40px 안의 반짝이
        near = ndi.binary_dilation(lab == big, iterations=40)
        keep = np.isin(lab, np.unique(lab[near & (lab > 0)]))
    a = np.where(keep, a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    body = (rgba[..., 3] > 128) if pick != 'spark' else ((rgba[..., 3] > 128) & (lab == big)[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    return rgba, body


def face_size(rgba):
    # 얼굴 = 가장 큰 살색 덩어리 (가로·세로)
    c = rgba[..., :3] / 255; a = rgba[..., 3] > 200
    mx, mn = c.max(-1), c.min(-1); s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    skin = a & (mx > 0.75) & (s > 0.1) & (s < 0.45) & (r >= g) & (g >= b) & (r - b > 0.1) & (r - g < 0.2)
    lab, n = ndi.label(ndi.binary_closing(skin, iterations=2))
    big = int(np.argmax(ndi.sum(skin, lab, range(1, n + 1)))) + 1
    ys, xs = np.where(lab == big)
    return xs.max() - xs.min() + 1, ys.max() - ys.min() + 1


def foot_x(body):
    ys, xs = np.where(body)
    y1 = ys.max(); return xs[ys >= y1 - max(3, int((y1 - ys.min()) * 0.06))].mean(), y1


def gold(im):
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    return (r - b > 55) & (r >= g - 10)


def load_black(box, pick):
    # 9번 검은 배경 장 한 칸 → (rgba, 몸). 배경은 새까맘(0) → 몸 = 밝은 덩어리를 채운 것, 그 안의 새까만 틈(지팡이와 머리 사이)은 배경
    B = rgb(BASE_BLACK)
    x0, y0, x1, y1 = BASE_MARK; B[y0:y1, x0:x1] = 0
    x0, y0, x1, y1 = box
    B = np.pad(B[y0:y1, x0:x1], ((4, 4), (4, 4), (0, 0)))
    v = B.max(axis=2)
    fg = v > 22
    lab, n = ndi.label(ndi.binary_dilation(fg, iterations=2))
    sz = ndi.sum(fg, lab, range(1, n + 1))
    big = int(np.argmax(sz)) + 1
    if pick == 'one': keep = lab == big
    elif pick == 'all': keep = np.isin(lab, 1 + np.where(sz >= 150)[0])
    else: keep = np.isin(lab, np.unique(lab[ndi.binary_dilation(lab == big, iterations=40) & (lab > 0)]))
    core = fg & np.isin(lab, 1 + np.where(sz >= 150)[0]) & keep
    body = ndi.binary_fill_holes(ndi.binary_closing(core, iterations=1))
    hole = body & (v <= 22)
    hl, hn = ndi.label(hole)
    body &= ~np.isin(hl, 1 + np.where(ndi.sum(hole, hl, range(1, hn + 1)) >= 4)[0])
    # 몸 바깥 가장자리: 검은 배경과 섞인 반투명 → 밝기로 알파 (윤곽선 밝기 ≈ 60 을 불투명으로)
    edge = keep & ~body & ndi.binary_dilation(body, iterations=2)
    spark = keep & ~body & ~edge & fg
    a = np.where(body, 1.0, 0.0)
    a = np.where(edge, np.clip((v - 6) / 54, 0, 1), a)
    a = np.where(spark, np.clip(v / 200, 0, 1), a)
    a = np.where(a < 0.08, 0, a)
    col = np.where(body[..., None], B, B / np.maximum(a, 1e-3)[..., None]).clip(0, 255)
    ys, xs = np.where(a > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    bd = body[y0:y1, x0:x1]
    if pick == 'spark':   # 발 자리용 몸은 가장 큰 덩어리만
        bl, _ = ndi.label(bd); bd = bl == int(np.argmax(np.bincount(bl.ravel())[1:])) + 1
    return np.dstack([col, a * 255])[y0:y1, x0:x1], bd


def load_black_row():
    # 검은 배경 스킬 줄 → 5칸 (rgba, 몸, 발 x, 발 y)
    B = np.pad(rgb(BLACK)[SKILL_ROW[0]:SKILL_ROW[1]], ((6, 6), (6, 6), (0, 0)))
    fg = B.max(axis=2) > 24
    lab, n = ndi.label(fg, structure=np.ones((3, 3)))
    sz = ndi.sum(fg, lab, range(1, n + 1))
    core = fg & ~gold(B)
    clab, cn = ndi.label(core, structure=np.ones((3, 3)))
    csz = ndi.sum(core, clab, range(1, cn + 1))
    bodies = sorted([i + 1 for i in np.argsort(csz)[-5:]], key=lambda i: np.where(clab == i)[1].mean())
    dists = np.stack([ndi.distance_transform_edt(clab != i) for i in bodies])
    owner = np.argmin(dists, axis=0)
    out = []
    for fi, bi in enumerate(bodies):
        mine = np.zeros_like(fg)
        for ci in range(1, n + 1):
            m = lab == ci
            if sz[ci - 1] < 2: continue
            if np.bincount(owner[m], minlength=5).argmax() == fi: mine |= m
        filled = ndi.binary_fill_holes(ndi.binary_closing(clab == bi, iterations=2))
        body = ndi.binary_fill_holes(filled | (mine & ndi.binary_dilation(filled, iterations=4)))
        # 채운 곳 중 새까만 덩어리 (지팡이와 몸 사이 배경)는 다시 빼냄
        #   진짜 배경은 거의 0 → 덩어리 평균이 아주 어두운 것만 (눈·눈썹처럼 어두운 남색은 남김)
        v = B.max(axis=2)
        hole = body & (v <= 24)
        hl, hn = ndi.label(hole)
        idx = np.arange(1, hn + 1)
        hsz, hmean = ndi.sum(hole, hl, idx), ndi.mean(v, hl, idx)
        body &= ~np.isin(hl, idx[(hsz >= 6) & (hmean < 6)])
        # 바깥 테두리: 대기 칸처럼 어두운 윤곽선 한 겹 (검은 배경에 묻힌 윤곽선 픽셀을 지우지 않고 윤곽선 색으로 다짐)
        rim = body & ndi.binary_dilation(~body) & (v < 110)
        B = np.where((rim & (v < OUTLINE.max()))[..., None], OUTLINE, B)
        a = np.where(body, 1.0, np.where(mine & ~ndi.binary_dilation(body, iterations=2) | (mine & (v > 150)), v / 255, 0))
        # 지팡이 끝 금빛 십자처럼 진한 금빛은 대기 칸처럼 불투명 (흐린 빛무리는 밝기 알파 그대로)
        solid_gold = mine & ~body & gold(B) & (v > 120)
        a = np.where(solid_gold, np.maximum(a, np.clip((v - 60) / 90, 0, 1)), a)
        a = np.where(a < 0.08, 0, a)
        col = np.where(body[..., None], B, B / np.maximum(a, 1e-3)[..., None]).clip(0, 255)
        ys, xs = np.where(a > 0)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.dstack([col, a * 255])[y0:y1, x0:x1]; bd = body[y0:y1, x0:x1]
        fx, fy = foot_x(bd)
        out.append((SKILL_NAMES[fi], rgba, bd, fx, fy))
    return out


def opaque_body(im):
    dark = im.mean(axis=2) < 105
    body = ndi.binary_fill_holes(ndi.binary_closing(dark, iterations=2)) & ~((im.min(axis=2) > 228) & ~dark)
    lab, n = ndi.label(body)
    return np.isin(lab, 1 + np.where(ndi.sum(body, lab, range(1, n + 1)) >= 40)[0])


def load_pair(wbox, bbox, foot=None):
    # 흰 배경 장(7)과 검은 배경 장(8)을 맞대어 알파·색을 구함 (archer0_build.load_pair와 같음). 결과는 검은 배경 장 좌표
    import cv2
    W = rgb(WHITE7).astype(np.float32); x0, y0, x1, y1 = wbox; W = W[y0:y1, x0:x1]
    B = rgb(BLACK).astype(np.float32); x0, y0, x1, y1 = bbox; B = np.pad(B[y0:y1, x0:x1], ((8, 8), (8, 8), (0, 0)))
    body = opaque_body(W)
    best = None
    for s in np.arange(0.8, 0.95, 0.004):
        size = (round(W.shape[1] * s), round(W.shape[0] * s))
        if size[0] > B.shape[1] or size[1] > B.shape[0]: continue
        t = cv2.resize(W, size, interpolation=cv2.INTER_AREA)
        m = cv2.resize(body.astype(np.float32), size, interpolation=cv2.INTER_AREA)
        m = cv2.erode((m > 0.99).astype(np.uint8), np.ones((3, 3))).astype(np.float32)
        r = cv2.matchTemplate(B, t, cv2.TM_SQDIFF, mask=np.dstack([m] * 3))
        v, _, loc, _ = cv2.minMaxLoc(r); v /= max(m.sum(), 1)
        if best is None or v < best[0]: best = (v, s, loc, t)
    _, s, (ox, oy), t = best
    Wb = np.full_like(B, 255)
    h = min(t.shape[0], B.shape[0] - oy); w = min(t.shape[1], B.shape[1] - ox)
    Wb[oy:oy + h, ox:ox + w] = t[:h, :w]
    diff = Wb - B
    est = 1 - diff.mean(axis=2) / 255
    agree = (diff.std(axis=2) < 22) & (diff.min(axis=2) > -24)
    glow = B.max(axis=2) / 255
    a = np.where(agree, np.clip(est, 0, 1), glow)
    a = np.where(a < 0.06, 0, a)
    solid = ndi.binary_fill_holes(ndi.binary_opening(a > 0.93, iterations=1))
    lab, n = ndi.label(solid)
    sz = ndi.sum(solid, lab, range(1, n + 1))
    # 발 위치용 몸: 금빛(마법진·날개)을 뺀 불투명 덩어리 중 가장 큰 것
    nb = solid & ~(gold(B) & (B.max(axis=2) > 150))   # 갈색 신발은 몸 (밝은 금빛만 뺌)
    lab, n = ndi.label(nb)
    nsz = ndi.sum(nb, lab, range(1, n + 1))
    body = lab == int(np.argmax(nsz)) + 1
    # 신발은 금빛 단에 막혀 따로 떨어진 덩어리 → 몸 바로 아래(가로 가운데 쪽)의 15px 넘는 덩어리를 몸에 붙임
    ys, xs = np.where(body); cx, hw = xs.mean(), (xs.max() - xs.min()) * 0.3
    for i, sl in enumerate(ndi.find_objects(lab)):
        if nsz[i] < 6: continue
        if abs((sl[1].start + sl[1].stop) / 2 - cx) < hw and sl[0].start <= ys.max() + 16:
            body |= lab == i + 1
    a = np.where(solid, 1.0, a)
    col = (B / np.maximum(a, 1e-3)[..., None]).clip(0, 255)
    ys, xs = np.where(a > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([col, a * 255])[y0:y1, x0:x1]; solid = solid[y0:y1, x0:x1]; body = body[y0:y1, x0:x1]
    fx, fy = foot_x(body)
    if foot:   # 손으로 정한 발 자리 (검은 배경 장 좌표)
        fx, fy = foot[0] - bbox[0] + 8 - x0, foot[1] - bbox[1] + 8 - y0
    print(f'  위치 맞춤 ×{s:.3f} ({ox}, {oy}), 두 장이 맞는 곳 {agree[a > 0].mean():.0%}')
    return rgba, solid, fx, fy


# 발동 칸 이펙트 색 바꾸기: (칸 이름, 빛 색, 빛무리 색). 이펙트 크기 FX_SCALE 배 (이펙트 무게중심 기준으로 퍼지며 커짐)
FX_VARIANTS = [('fx_heal', (74, 222, 128), (34, 197, 94)),       # 다수회복 초록
               ('fx_shield', (96, 165, 250), (37, 99, 235)),     # 보호막 푸른색
               ('fx_bless', (250, 204, 21), (234, 179, 8)),      # 축복 노란색
               ('fx_purify', (248, 250, 255), (148, 170, 210))]  # 정화 흰색 (흰 수도복·밝은 바닥에서도 보이게 빛무리는 옅은 청회색)
FX_SCALE = 1.6


def fx_variant(rgba, body, fx, fy, tint, halo):
    # 몸(지팡이 포함)에 닿지 않는 덩어리 = 이펙트. 이펙트만 떼어 키우고 색을 바꿔 몸 위에 다시 올림
    a = rgba[..., 3] > 0
    eff = a & ~body
    lab, n = ndi.label(eff, structure=np.ones((3, 3)))
    near = ndi.binary_dilation(body, iterations=2)
    keep = [i for i in range(1, n + 1) if not (near & (lab == i)).any()]
    em = np.isin(lab, keep)
    base = rgba.copy(); base[em] = 0
    E = rgba.copy(); E[~em] = 0
    ys, xs = np.where(em)
    w8 = E[ys, xs, 3]
    cy, cx = (ys * w8).sum() / w8.sum(), (xs * w8).sum() / w8.sum()
    # 색: 밝기를 살려 빛 색으로, 가장 밝은 속은 흰빛
    L = E[..., :3].max(axis=2) / 255
    t = np.array(tint, float)
    col = t * (0.55 + 0.45 * L)[..., None]
    wmix = (np.clip((L - 0.75) / 0.25, 0, 1) * 0.7)[..., None]
    E[..., :3] = col * (1 - wmix) + 255 * wmix
    # 키우기 (premultiplied)
    h, w = E.shape[:2]
    S = FX_SCALE
    big = (round(w * S), round(h * S))
    pm = E.copy(); pm[..., :3] *= pm[..., 3:] / 255
    pm = np.array(Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize(big, Image.LANCZOS)).astype(float)
    al = pm[..., 3:]
    pm[..., :3] = np.where(al > 0, pm[..., :3] * 255 / np.maximum(al, 1), 0)
    # 빛무리: 이펙트 알파를 번지게 해서 옅게 깔기
    glow = ndi.gaussian_filter(pm[..., 3], 4) * 0.55
    # 새 캔버스: 원래 칸 + 커진 이펙트가 다 들어가게
    ox, oy = cx * S - cx, cy * S - cy   # 커진 이펙트를 무게중심이 같은 자리에 오게 옮기는 양
    x0 = int(np.floor(min(0, -ox))); y0 = int(np.floor(min(0, -oy)))
    x1 = int(np.ceil(max(w, big[0] - ox))); y1 = int(np.ceil(max(h, big[1] - oy)))
    W, Hh = x1 - x0, y1 - y0
    out = np.zeros((Hh, W, 4)); bd = np.zeros((Hh, W), bool)
    out[-y0:-y0 + h, -x0:-x0 + w] = base; bd[-y0:-y0 + h, -x0:-x0 + w] = body
    ex, ey = int(round(-ox - x0)), int(round(-oy - y0))
    def over(dst, src_rgb, src_a):
        sa = src_a[..., None] / 255; da = dst[..., 3:] / 255
        oa = sa + da * (1 - sa)
        dst[..., :3] = np.where(oa > 0, (src_rgb * sa + dst[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6), 0)
        dst[..., 3:] = oa * 255
    reg = out[ey:ey + big[1], ex:ex + big[0]]
    over(reg, np.broadcast_to(np.array(halo, float), reg.shape[:2] + (3,)), np.clip(glow, 0, 255) * ~bd[ey:ey + big[1], ex:ex + big[0]])
    over(reg, pm[..., :3], pm[..., 3])
    out[..., 3] = np.where(out[..., 3] < 10, 0, out[..., 3])
    ys, xs = np.where(out[..., 3] > 0)
    yy0, yy1, xx0, xx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return out[yy0:yy1, xx0:xx1], bd[yy0:yy1, xx0:xx1], fx - x0 - xx0, fy - y0 - yy0


def add_outline(p, body):
    # 검은 배경 장 칸을 대기 칸처럼: 몸(불투명) 바로 바깥 1px에 대기 칸 윤곽선 색, 몸 둘레 반투명 테두리는 지움
    #   (반짝이·마법진 고리처럼 몸에서 떨어진 빛은 그대로)
    h, w = p.shape[:2]
    bm = np.array(Image.fromarray((body * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)) > 128
    q = np.pad(p, ((1, 1), (1, 1), (0, 0))).astype(float); bm = np.pad(bm, 1)
    op = bm & (q[..., 3] > 60)
    op = ndi.binary_fill_holes(op) & (q[..., 3] > 0) | op
    q[..., 3] = np.where(op, 255, q[..., 3])
    ring = ndi.binary_dilation(op) & ~op
    fringe = ndi.binary_dilation(op, iterations=2) & ~op & ~ring & (q[..., 3] < 160)
    q[..., :3] = np.where(ring[..., None], OUTLINE, q[..., :3])
    q[..., 3] = np.where(ring, 255, np.where(fringe, 0, q[..., 3]))
    return q.clip(0, 255).astype(np.uint8)


def pack(pieces, out, label):
    # pieces: (이름, rgba, 발 x, 발 y). 발 자리를 칸마다 같은 기준점에
    L = max(int(np.ceil(fx)) for _, _, fx, _ in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - fx)) for _, p, fx, _ in pieces) + 3
    U = max(int(np.ceil(fy)) for _, _, _, fy in pieces) + 3
    Bm = max(int(np.ceil(p.shape[0] - fy)) for _, p, _, fy in pieces) + 2
    cw, ch = L + R, U + Bm
    sheet = np.zeros((ch, cw * len(pieces), 4), np.uint8)
    for i, (name, p, fx, fy) in enumerate(pieces):
        x = i * cw + L - int(round(fx)); y = U - int(round(fy))
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = np.maximum(sheet[y:y + p.shape[0], x:x + p.shape[1]], p)
    Image.fromarray(sheet, 'RGBA').save(out, 'WEBP', lossless=True)
    print(f'{label} cellW={cw} cellH={ch} anchorX={L} anchorY={U} count={len(pieces)}')
    return cw, ch, L, U


def main():
    guides = {name: box for name, box, _ in BASE}
    loaded = [(f, *load_white(src, box, pick, guides[f[0]])) for f in FRAMES for (_, src, box, pick, _) in [f]]
    idle = loaded[0][1]
    ki = IDLE_H / idle.shape[0]
    fw0, fh0 = face_size(idle)
    print(f'대기: 샘플 키 {idle.shape[0]}, 얼굴 {fw0}x{fh0}')
    groups = {}
    for (name, src, box, pick, grp), rgba, body in loaded:
        if grp in groups: continue
        fw, fh = face_size(rgba)
        groups[grp] = ki * (fw0 / fw + fh0 / fh) / 2
        if grp == 'hurt': groups[grp] = (groups[grp] * groups['walk']) ** 0.5   # 피격 장은 표정 때문에 얼굴이 커 보임 → 걷기 배율과 반반
        print(f'  배율 {grp}: 얼굴 {fw}x{fh} → ×{groups[grp]:.3f}')
    pieces = []
    for (name, src, box, pick, grp), rgba, body in loaded:
        k = groups[grp]
        fx, fy = foot_x(body)
        if name == 'down1': fx = rgba.shape[1] * 0.42
        if name == 'down0': fx = rgba.shape[1] * 0.45
        p = defringe(shrink(rgba, k))
        pieces.append((name, p, fx * k, p.shape[0] - (rgba.shape[0] - 1 - fy) * k - 1))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{k:.3f} → {p.shape[1]}x{p.shape[0]}')
    # 스킬 줄 (검은 배경): 준비 칸 얼굴로 배율
    row = load_black_row()
    # 검은 배경에서는 머리카락·손이 살색과 섞여 얼굴을 못 잡음 → 준비 칸(똑바로 선 자세) 키를 걷기 칸 키에 맞춤
    #   바깥에 윤곽선 1px을 두르므로 몸은 2px 작게 줄임 (윤곽선까지 걷기 키와 같게)
    kb = (GROUP_H['walk'] - 2) / row[0][1].shape[0]
    print(f'  배율 검은 배경: 준비 칸 키 {row[0][1].shape[0]} → ×{kb:.3f}')
    for name, rgba, bd, fx, fy in row:
        p = add_outline(shrink_soft(rgba, bd, kb), bd)
        pieces.append((name, p, fx * kb + 1, fy * kb + 2))   # 발 = 윤곽선 아래끝
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{kb:.3f} → {p.shape[1]}x{p.shape[0]}')
    # 13~16: 발동 칸(11)의 빛 십자·반짝이를 스킬마다 다른 색으로 키운 칸 (다수회복 · 보호막 · 축복 · 정화)
    fire = [r for r in row if r[0] == 'fire'][0]
    for name, tint, halo in FX_VARIANTS:
        rgba, bd, fx, fy = fx_variant(fire[1], fire[2], fire[3], fire[4], tint, halo)
        p = add_outline(shrink_soft(rgba, bd, kb), bd)
        pieces.append((name, p, fx * kb + 1, fy * kb + 2))
        print(f'{name}: {rgba.shape[1]}x{rgba.shape[0]} → {p.shape[1]}x{p.shape[0]}')
    cell = pack(pieces, OUT, 'healer_0')
    try:
        import cv2   # noqa: F401 — 히든 스킬 맞대기용. 없으면 히든 스킬 그림은 그대로 둠
    except ImportError:
        print('cv2 없음 → healer_miracle_cast 는 다시 안 만듦'); return cell
    hp = []
    for name, wbox, bbox in HIDDEN:
        rgba, solid, fx, fy = load_pair(wbox, bbox, HIDDEN_FOOT.get(name))
        p = shrink_soft(rgba, solid, kb)
        hp.append((name, p, fx * kb, fy * kb + HIDDEN_LIFT.get(name, 0)))
        print(f'{name}: 검은 배경 {rgba.shape[1]}x{rgba.shape[0]} ×{kb:.3f} → {p.shape[1]}x{p.shape[0]}')
    pack(hp, CAST_OUT, 'healer_miracle_cast')
    return cell


if __name__ == '__main__':
    main()

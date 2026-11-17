# 기공사 시크릿 레어 1 (2026-11-17 사용자 샘플: 검은 긴 머리·하늘빛 한복 도포·흰 띠 리본) → assets/sprites/merc/qigong_sr1.webp
# 사용: python tools/qigong_sr1_build.py   (샘플 assets/sprites/merc/samples/qigong_sr1_src*.png, 흰 배경)
#   src = 대기 · src2 = 걷기 4칸 한 장 (위에 '걷기 n' 글씨) · src3 = 일반공격 기 모으기 · src4 = 일반공격 내지르기 (왼쪽 위 글씨)
#   · src5 = 피격 1 + 쓰러짐 2 한 장 (위에 글씨). 누운 칸은 0번처럼 머리가 오른쪽이라 그대로
#   · src6·7 = 기공포 모으기·쏘기 · src8·9 = 기공탄 준비·던지기 · src13·14 = 기공막·기공후 모으기·펼치기
#   · src10·11 = 기공파 모으기·쏘기 · src12 = 기공파 둘째 자세 (SR 전용, 칸 22)
#   · src15~19 = 기공옥: 땅에서 모으기(18) · 두 팔을 들어 떠오름(23, SR 전용) · 최대 크기(19) · 내리꽂으며 던지기(20) · 착지(21)
# 칸 구성은 qigong_0과 같은 22칸 + 22 기공파 둘째 자세 + 23 기공옥 떠오르기
# 맞추기 (대기 칸 기준, 2026-11-17 사용자 요청: 크기·비율·색감·밝기를 대기에 맞추고 흰 배경 깔끔하게):
#   - 흰 배경: brawler_sr1_build.cut (가장자리 흰색 + 리본 고리 안에 갇힌 흰 구멍 + 테두리 회색 찌꺼기) → 가장 큰 덩어리만 (글씨도 빠짐)
#   - 크기: 대기 머리(머리카락·얼굴)를 본으로 배율·기울기를 바꿔 겹쳐 보고(정규화 상호상관) 같은 크기로 (얼굴 살색 넓이는 손·목이 붙어 틀어짐)
#   - 비율: 서 있는 칸(UPRIGHT)은 턱 아래 몸 길이를 머리 대비 대기와 같은 비율로 늘이거나 줄임 (무릎 굽힌 걷기는 조금 짧게)
#   - 색: 얼굴 살색 평균 → 칸 전체 채널별 배율 (밝기·따뜻함), 하늘빛 옷 → 채도·밝기를 대기 옷 평균에 맞춤 (외곽선 검정·머리카락은 그대로)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from brawler_sr1_build import cut, shrink

D = 'assets/sprites/merc/samples/qigong_sr1_'
OUT = 'assets/sprites/merc/qigong_sr1.webp'
COUNT, IDLE_H = 24, 92        # 대기 칸 머리 꼭대기~발 (게임 칸 px)
LIFT = {19: 8}                # 바닥에서 띄울 높이 (게임 px): 기공옥 최대 크기 자세는 0번처럼 공중에 뜬 그림
# (칸 번호, 샘플, 자를 상자 또는 None) — 한 장에 여러 칸인 샘플만 상자 (글씨는 cut이 가장 큰 덩어리만 남겨 빠짐)
FRAMES = [
    (0, 'src.png', None),
    (1, 'src2.png', (40, 0, 200, 205)), (2, 'src2.png', (205, 0, 395, 205)), (3, 'src2.png', (400, 0, 590, 205)), (4, 'src2.png', (595, 0, 765, 205)),
    (5, 'src3.png', None), (6, 'src4.png', None),
    (7, 'src5.png', (35, 32, 215, 217)), (8, 'src5.png', (285, 32, 510, 217)), (9, 'src5.png', (515, 32, 763, 217)),
    (10, 'src6.png', None), (11, 'src7.png', None), (12, 'src8.png', None), (13, 'src9.png', None),
    (14, 'src13.png', None), (15, 'src14.png', None), (16, 'src10.png', None), (17, 'src11.png', None), (22, 'src12.png', None),
    (18, 'src15.png', None), (23, 'src16.png', None), (19, 'src17.png', None), (20, 'src18.png', None), (21, 'src19.png', None),
]
UPRIGHT = {1: 0.95, 2: 0.95, 3: 0.95, 4: 0.95, 18: 1.0, 23: 1.0, 19: 1.0}   # 몸 길이를 맞출 서 있는 칸 → 대기 대비 목표
SAME = {9: 8}                 # 얼굴이 가려 못 재는 칸 → 같은 장 다른 칸의 배율·색을 씀
# 머리 본 맞추기가 빗나가는 칸 (얼굴을 옆·위로 돌려 일치도 0.75 아래, 가장 작은 배율로 쏠림) → 배율을 직접 적음:
#   걷기 4칸은 한 장이라 같은 배율 (본 맞추기 0.80~0.85의 가운데). 걷기 머리 = 대기 × 1/0.82 (본 맞추기, 일치도 0.81~0.87) 에, 나란히 놓고 맞춘 걷기 대비 머리 크기 (내지르기·쏘기 1.12배 · 떠오르기 1.12배
#   · 최대 크기 1.8배 · 던지기 1.6배)를 곱한 값
K_MANUAL = {1: 0.81, 2: 0.81, 3: 0.81, 4: 0.81, 6: 0.73, 11: 0.73, 12: 0.73, 13: 0.73, 22: 0.73, 23: 0.73, 19: 0.46, 20: 0.51}


def load(name, box):
    im = np.array(Image.open(D + name).convert('RGB'))
    if box: im = im[box[1]:box[3], box[0]:box[2]]
    im = np.pad(im, ((3, 3), (3, 3), (0, 0)), constant_values=255)
    return cut(im)


def skin_mask(a):   # 이 그림의 밝은 살색 (약 248,224,215): 흰 옷은 푸른 기라 b > r로 빠짐
    c = a[..., :3].astype(int); r, g, b = c[..., 0], c[..., 1], c[..., 2]
    return (a[..., 3] > 0) & (r > 215) & (r - g > 10) & (r - g < 50) & (g - b > 2) & (g - b < 30) & (b > 160)


def face(a):   # 그림 위쪽 55% 안의 가장 큰 살색 덩어리 = 얼굴 → (넓이, 평균색, 턱 y)
    m = skin_mask(a); m[int(a.shape[0] * .55):] = False
    lab, n = ndi.label(ndi.binary_closing(m, iterations=2) & m)
    if n == 0: return None
    sz = ndi.sum(m, lab, range(1, n + 1))
    f = lab == 1 + int(np.argmax(sz))
    return f.sum(), a[..., :3][f].astype(float).mean(axis=0), int(np.where(f)[0].max())


def flat(a):   # 투명 배경을 흰색으로 (본 맞추기용)
    return (a[..., :3] * (a[..., 3:] / 255) + 255 * (1 - a[..., 3:] / 255)).astype(np.float32)


def head_scale(a, T):   # 대기 머리 본(T)과 가장 닮은 곳의 크기 비율 → (배율, 일치도). 고개를 기울인 칸이 있어 ±35° 기울여 봄, 좌우 뒤집은 본도
    import cv2
    im = flat(a); best = (-1, 1)
    for T, ang in [(T0, g) for T0 in (T, T[:, ::-1].copy()) for g in range(-35, 36, 5)]:   # 몸을 반대로 돌린 칸이 있어 좌우 뒤집은 본도
        M = cv2.getRotationMatrix2D((T.shape[1] / 2, T.shape[0] / 2), ang, 1)
        R = cv2.warpAffine(T, M, (T.shape[1], T.shape[0]), borderValue=(255, 255, 255))[5:-5, 5:-5]
        for sc in np.arange(0.6, 2.4, 0.01):
            t = cv2.resize(R, (round(R.shape[1] * sc), round(R.shape[0] * sc)), interpolation=cv2.INTER_AREA)
            if t.shape[0] > im.shape[0] or t.shape[1] > im.shape[1]: continue
            v = cv2.minMaxLoc(cv2.matchTemplate(im, t, cv2.TM_CCOEFF_NORMED))[1]
            if v > best[0]: best = (v, sc)
    return best[1], best[0]


def cloth_mask(a):   # 하늘빛 옷: 푸른 색조, 어느 정도 채도
    c = a[..., :3].astype(float); mx, mn = c.max(-1), c.min(-1)
    return (a[..., 3] > 0) & (c[..., 2] >= mx - 1) & (mx - mn > 40) & (mx > 120)


def cloth_sv(a):
    c = a[..., :3].astype(float)[cloth_mask(a)]; mx, mn = c.max(-1), c.min(-1)
    return ((mx - mn) / mx).mean(), mx.mean()


def recolor(a, gain, s_k=1.0, v_k=1.0):   # 칸 전체 채널 배율 → 옷 픽셀만 채도 s_k배·밝기 v_k배 (가장 밝은 채널 기준)
    a = a.astype(float).copy()
    cm = cloth_mask(a)
    c = (a[..., :3] * gain).clip(0, 255)
    mx = c.max(-1, keepdims=True)
    new = ((mx - (mx - c) * s_k) * v_k).clip(0, 255)
    a[..., :3] = np.where(cm[..., None], new, c)
    return a


def stretch_body(fig, chin, factor):   # 턱 아래 몸만 위아래로 늘이거나 줄임 (머리 크기는 그대로)
    top, bot = fig[:chin + 1], fig[chin + 1:]
    h = max(1, round(bot.shape[0] * factor))
    bot = np.array(Image.fromarray(bot.astype(np.uint8), 'RGBA').resize((bot.shape[1], h), Image.NEAREST))
    return np.concatenate([top.astype(np.uint8), bot], axis=0)


idle = load('src.png', None)
fa0, fc0, chin0 = face(idle)
y0 = int(np.nonzero(idle[..., 3].max(1))[0][0])
hy, hx = np.nonzero((idle[..., 3] > 0) & (idle[..., :3].max(-1) < 70) & (np.arange(idle.shape[0])[:, None] < y0 + 50))
xc = int(np.median(hx))
T = flat(idle)[y0 + 6:y0 + 52, xc - 20:xc + 22].copy()   # 대기 머리 (머리카락·얼굴, 머리 위 묶음 아래부터)
self_sc = head_scale(idle, T)[0]
s0, v0 = cloth_sv(idle)
sc0 = IDLE_H / idle.shape[0]
body0 = (idle.shape[0] - 1 - chin0) / np.sqrt(fa0)   # 머리 크기 대비 몸 길이
done, cells = {}, {}
for idx, name, box in FRAMES:
    fig = load(name, box)
    f = face(fig)
    hv = 0
    if idx in SAME: k, gain = done[SAME[idx]]
    else:
        if idx in K_MANUAL: k = K_MANUAL[idx]
        else:
            hs, hv = head_scale(fig, T)
            k = self_sc / hs
        gain = np.clip(fc0 / f[1], 0.85, 1.2)
    done[idx] = (k, gain)
    if idx in UPRIGHT:
        body = (fig.shape[0] - 1 - f[2]) / np.sqrt(f[0])
        fig = stretch_body(fig, f[2], body0 * UPRIGHT[idx] / body)
    fig = recolor(fig, gain)
    s, v = cloth_sv(fig)
    fig = recolor(fig, np.ones(3), np.clip(s0 / s, 0.7, 1.6), np.clip(v0 / v, 0.85, 1.15))
    im = shrink(fig.clip(0, 255).astype(np.uint8), sc0 * k)
    al = im[..., 3]
    rows = np.nonzero(al.max(1))[0]
    feet = np.nonzero(al[rows[-1] - 5:rows[-1] + 1].max(0))[0]   # 맨 아래 6줄 = 발
    cells[idx] = (Image.fromarray(im, 'RGBA'), (feet[0] + feet[-1]) // 2, rows[-1] + LIFT.get(idx, 0))
    print(f'cell {idx}: k {k:.2f} match {hv:.2f} face {np.round(f[0] if f else 0)} gain {np.round(gain, 2)} cloth s {s:.2f}->{s0:.2f} v {v:.0f}->{v0:.0f} size {im.shape[1]}x{im.shape[0]}')

L = max(ax for im, ax, by in cells.values()) + 2
R = max(im.width - ax for im, ax, by in cells.values()) + 2
U = max(by for im, ax, by in cells.values()) + 2
CW, CH = L + R, U + 2
sheet = Image.new('RGBA', (CW * COUNT, CH))
for i in range(COUNT):
    im, ax, by = cells.get(i, cells[0])
    sheet.paste(im, (i * CW + L - ax, U - by), im)
sheet.save(OUT, lossless=True)
# 구체가 나가는 손끝 = 내지르기 칸(6)에서 가장 앞(오른쪽) 불투명 픽셀
im6, ax6, by6 = cells[6]
al6 = np.asarray(im6)[..., 3]
hx = np.nonzero(al6.max(0))[0][-1]; hy = int(np.nonzero(al6[:, hx])[0].mean())
print(f'cellW {CW} cellH {CH} anchorX {L} anchorY {U} hand: front {hx - ax6} up {by6 - hy}')

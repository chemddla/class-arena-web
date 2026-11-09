# 성녀 시크릿 레어 1 교체 (2026-11-09): 분홍 단발 천사 (후광·분홍빛 날개·연두 금빛 로브·날개 달린 하프 지팡이)
#   → assets/sprites/merc/healer_sr1.webp
# 사용: python tools/healer_sr1_build.py
# 샘플 (assets/sprites/merc/samples/healer_sr1_edit_*): 같은 그림을 흰 배경(1)·검은 배경(2)으로 받은 한 장 (1024×979, 동작 이름 글씨 포함)
#   대기 1 · 이동(비행) 4 · 일반공격(치유) 2 (지팡이 끝에 초록 빛 → 초록 거품을 앞으로 뿜음) · 피격 1 · 쓰러짐 2 (주저앉음 → 누움, 하프가 떨어짐)
#   3·4 (1024×765, 흰·검은 배경 한 쌍): 윗줄 기도 후 축복 4 (손 모아 기도 → 빛이 모임 → 눈 뜨고 초록 고리 → 금빛 십자·초록 날개 축복)
#         아랫줄 히든 스킬 [기적] 4 (초록 회오리·깃털 → 금빛 마법진 → 은하 날개·유성·빛기둥 → 초록 반짝이 마무리). 검은 장 오른쪽 아래 별 표시는 지움
# 칸 순서 (healer_sr1): 0 대기 · 1~4 비행 · 5~6 일반공격 (치유) · 7 피격 · 8~9 쓰러짐 · 10~13 스킬 (기도 · 빛 모음 · 초록 고리 · 축복)
#   · 14~19 = 기도(10)·초록 고리(12)의 초록 빛만 스킬 색으로 바꾼 것: 14~15 보호막 (푸른) · 16~17 축복 (노란) · 18~19 정화 (흰)
#     (2026-11-09 사용자 요청: 다수 회복 = 초록 그대로 10→12, 부활 = 빛 모음·축복 11→13, 나머지는 기도·고리를 스킬 색으로)
# 히든 스킬 [기적] 시전 그림 → assets/sprites/fx/healer_miracle_cast_sr1.webp (HEALER_MIRACLE_FX.sr, 4칸: 회오리 · 마법진 · 은하 날개 · 마무리)
# 배경 지우기: 두 장은 같은 자리에 있지만 다시 그려져 윤곽이 조금씩 다름
#   흰 장이 하얗고 검은 장이 까만 곳 = 배경 · 두 장의 차이(흰 - 검은)로 알파를 구함 (치유 빛·거품의 반투명)
#   거의 불투명(0.85 넘음)한 덩어리는 작은 틈(다시 그린 윤곽 차이)을 메워 완전히 불투명 → 색은 흰 장, 반투명 곳의 색은 검은 장 / 알파
# 크기: 같은 장의 동작은 같은 크기로 그려져 있어 장마다 한 배율. 스킬 장 윗줄은 몸 키가 대기보다 4% 커서 ×0.96,
#   아랫줄(기적)은 마무리 칸 몸 키가 대기보다 작아 ×1.08. 기적 칸은 이펙트가 발밑까지 덮어 발을 못 찾음 → 얼굴 가운데에서 대기 칸과 같은 거리 아래가 발
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from archer0_build import shrink_soft

D = 'assets/sprites/merc/samples/healer_sr1_edit_'
OUT = 'assets/sprites/merc/healer_sr1.webp'
K = 0.6   # 샘플 → 시트 배율 (대기 머리끝~발 약 100px, healer_0과 같은 키)
# (칸 이름, 상자 x0 y0 x1 y1 — 글씨는 상자 밖, 기준점 x 비율 (None = 발 가운데))
FRAMES = [
    ('idle', (52, 34, 282, 238), None),
    ('fly0', (58, 266, 292, 468), None),
    ('fly1', (303, 266, 524, 468), None),
    ('fly2', (540, 266, 762, 468), None),
    ('fly3', (772, 266, 994, 468), None),
    ('atk0', (36, 498, 298, 714), None),
    ('atk1', (298, 498, 712, 714), None),
    ('hurt', (44, 744, 234, 952), None),
    ('down0', (328, 748, 534, 955), 0.55),
    ('down1', (584, 824, 842, 968), 0.42),
]
SKILL = [   # 스킬 장 윗줄 (×0.96)
    ('pray', (28, 70, 248, 278), None),
    ('gather', (276, 70, 498, 280), None),
    ('ring', (520, 70, 754, 282), None),
    ('bless', (764, 12, 1004, 300), None),
]
K_SKILL = 0.96
MIRACLE = [   # 스킬 장 아랫줄 (×1.08)
    ('whirl', (12, 392, 252, 708)),
    ('circle', (243, 412, 482, 722)),
    ('galaxy', (481, 370, 780, 700)),
    ('end', (778, 398, 1010, 702)),
]
K_MIRACLE = 1.08
MIRACLE_FACE = {'circle': (145, 98)}   # 금빛 마법진이 살색처럼 잡혀 얼굴을 못 찾는 칸: 자른 그림 좌표의 얼굴 가운데
CAST_OUT = 'assets/sprites/fx/healer_miracle_cast_sr1.webp'
STAR = (880, 620, 955, 700)   # 검은 장의 별 표시 (흰 장에는 없음)


def rgb(src):
    return np.array(Image.open(D + src).convert('RGB')).astype(float)


def matte(W, B):
    d = W - B
    a = np.clip(1 - d.mean(axis=2) / 255, 0, 1)
    bg = (W.min(axis=2) > 236) & (B.max(axis=2) < 26)
    # 동작 이름 글씨: 흰 장에선 검고 검은 장에선 하얀 곳 (그림에는 없음) + 둘레 2px
    bg |= ndi.binary_dilation((W.max(axis=2) < 110) & (B.min(axis=2) > 140), iterations=2)
    a[bg] = 0
    # 하프 줄 사이처럼 좁은 틈: 틈 메우기(closing)가 흰 장 색으로 칠해 버리지 않게
    #   배경 같은 곳 (흰 장에선 밝고 검은 장에선 어두움, 압축 번짐 포함)은 투명, 반 넘게 비치는 곳(뒤에 치유 빛)은 메우지 않음
    bgish = (W.min(axis=2) > 200) & (B.max(axis=2) < 70)
    a[bgish & (a < 0.35)] = 0
    solid = ndi.binary_closing(a > 0.85, iterations=2) & ~bg & ~bgish & (a >= 0.5)
    solid = ndi.binary_opening(solid, iterations=1)
    # 작은 반투명 티끌(거품 가운데처럼 진한 점)만 불투명이 되지 않게: 30px 넘는 덩어리만 몸
    lab, n = ndi.label(solid)
    sz = ndi.sum(solid, lab, range(1, n + 1))
    solid = np.isin(lab, 1 + np.where(sz >= 30)[0])
    a = np.where(solid, 1.0, a)
    a = np.where(a < 0.05, 0, a)
    col = np.where(solid[..., None], W, (B / np.maximum(a, 1e-3)[..., None])).clip(0, 255)
    return np.dstack([col, a * 255]), solid


def foot_x(body):
    ys, xs = np.where(body)
    y1 = ys.max(); return xs[ys >= y1 - max(3, int((y1 - ys.min()) * 0.06))].mean(), y1


def face_c(rgba, body):
    # 얼굴 가운데: 몸 덩어리 안의 살색 (밝은 살구색) 가운데
    c = rgba[..., :3]
    sk = body & (c[..., 0] > 235) & (c[..., 1] > 195) & (c[..., 2] > 170) & (c[..., 0] - c[..., 2] > 15) & (c[..., 0] - c[..., 2] < 60)
    lab, n = ndi.label(ndi.binary_closing(sk, iterations=2))
    big = lab == int(np.argmax(ndi.sum(sk, lab, range(1, n + 1)))) + 1
    ys, xs = np.where(big); return xs.mean(), ys.mean()


def cut(W, B, box, near_px=60):
    x0, y0, x1, y1 = box
    rgba, solid = matte(W[y0:y1, x0:x1], B[y0:y1, x0:x1])
    # 몸에서 떨어진 것: 큰 덩어리(몸)와 그 둘레 near_px 안의 빛·거품만
    m = rgba[..., 3] > 0
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
    big = int(np.argmax(ndi.sum(solid, lab, range(1, n + 1)))) + 1
    near = ndi.binary_dilation(lab == big, iterations=near_px)
    keep = np.isin(lab, np.unique(lab[near & (lab > 0)]))
    rgba[..., 3] = np.where(keep, rgba[..., 3], 0)
    sl, sn = ndi.label(solid & (lab == big))
    solid = sl == int(np.argmax(ndi.sum(solid, sl, range(1, sn + 1)))) + 1 if sn else solid
    ys, xs = np.where(rgba[..., 3] > 0)
    sy0, sy1, sx0, sx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return rgba[sy0:sy1, sx0:sx1], solid[sy0:sy1, sx0:sx1]


# 초록 빛 다시 칠하기: (색상 °, 채도 배율, 밝기 더함). 흰 계열은 채도를 거의 없애고 밝힘
RECOLOR = [('shield', (205, 1.0, 0.0)), ('bless', (46, 1.0, 0.04)), ('purify', (0, 0.1, 0.12))]


# 초록 고리 칸(12)의 고리 앞쪽 줄 (로브 위를 가로지르는 밝은 연두 줄): 로브와 색이 같아 색으로는 못 가름 → 자리로 정함
#   기준점(발) 기준 x -45~+42, 가운데 y = -27 - 4·(1 - ((x + 5) / 45)²) 의 위아래 2.5px 안에서 밝은(0.9 넘음) 연두만
RING_FRONT = (-45, 42, -27, 4, 2.5)


def recolor(p, target, anchor=None):
    # 초록 빛 = 초록 색상(58~170°, 연두 포함·금빛 제외) 중 반투명하거나, 머리 아래(위 35% 밑)에서 채도가 진한 곳 (연한 민트 로브·머리 깃털 장식은 그대로)
    #   + anchor가 있으면 고리 앞쪽 줄 (RING_FRONT)
    hue, sm, vadd = target
    rgb = p[..., :3].astype(float) / 255; a = p[..., 3]
    mx, mn = rgb.max(-1), rgb.min(-1); c = mx - mn
    s = np.where(mx > 0, c / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.where(c == 0, 0, np.where(mx == r, ((g - b) / np.maximum(c, 1e-6)) % 6, np.where(mx == g, (b - r) / np.maximum(c, 1e-6) + 2, (r - g) / np.maximum(c, 1e-6) + 4))) * 60
    ys, _ = np.where(a > 0); top = ys.min() + (ys.max() - ys.min()) * 0.35
    yy = np.arange(p.shape[0])[:, None] + np.zeros(p.shape[:2]); xx = np.arange(p.shape[1])[None, :] + np.zeros(p.shape[:2])
    green = (h > 58) & (h < 170) & (s > 0.18) & (a > 0)
    m = green & ((a < 250) | ((s > 0.42) & (mx > 0.45) & (yy > top)))
    m = ndi.binary_opening(m, iterations=1) | (m & (a < 250))
    if anchor:
        x0, x1, cy, bow, half = RING_FRONT
        rx, ry = xx - anchor[0], yy - anchor[1]
        mid = cy - bow * (1 - ((rx + 5) / 45) ** 2)
        m |= (rx >= x0) & (rx <= x1) & (np.abs(ry - mid) <= half) & (h > 50) & (h < 140) & (mx > 0.9) & (s > 0.1) & (a > 0)
    # 색상: 초록(120°) 둘레 퍼짐을 1/4로 줄여 목표 색 둘레에 (노랑이 주황·빨강으로 번지지 않게). 흰 계열은 색상 그대로 채도만 뺌
    nh = np.where(m, (hue + (h - 120) * 0.25) % 360 if hue else h, h) / 60
    ns = np.where(m, np.clip(s * sm * (1.15 if hue else 1), 0, 1), s)
    nv = np.where(m, np.clip(np.where(a < 250, np.maximum(mx, 0.8), mx) + vadd, 0, 1), mx)   # 어두운 반투명 빛은 밝혀서 빛나 보이게
    i_ = np.floor(nh).astype(int) % 6; f = nh - np.floor(nh)
    pp, qq, tt = nv * (1 - ns), nv * (1 - ns * f), nv * (1 - ns * (1 - f))
    res = np.zeros_like(rgb)
    for k, (x, y, z) in enumerate([(nv, tt, pp), (qq, nv, pp), (pp, nv, tt), (pp, qq, nv), (tt, pp, nv), (nv, pp, qq)]):
        w = i_ == k
        res[..., 0][w], res[..., 1][w], res[..., 2][w] = x[w], y[w], z[w]
    q = p.copy()
    q[..., :3] = np.where(m[..., None], (res * 255).round(), p[..., :3]).clip(0, 255).astype(np.uint8)
    return q


def pack(pieces, out, label):
    L = max(int(np.ceil(fx)) for _, _, fx, _ in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - fx)) for _, p, fx, _ in pieces) + 3
    U = max(int(np.ceil(fy)) for _, _, _, fy in pieces) + 3
    Bm = max(int(np.ceil(p.shape[0] - fy)) for _, p, _, fy in pieces) + 2
    cw, ch = L + R, U + Bm
    sheet = np.zeros((ch, cw * len(pieces), 4), np.uint8)
    for i, (name, p, fx, fy) in enumerate(pieces):
        x = i * cw + L - int(round(fx)); y = U - int(round(fy))
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(out, 'WEBP', lossless=True)
    print(f'{label} cellW={cw} cellH={ch} anchorX={L} anchorY={U} count={len(pieces)}')


def main():
    W, B = rgb('1_white_src.webp'), rgb('2_black_src.webp')
    W2, B2 = rgb('3_skill_white_src.webp'), rgb('4_skill_black_src.webp')
    x0, y0, x1, y1 = STAR
    star = W2[y0:y1, x0:x1].min(axis=2) > 225
    B2[y0:y1, x0:x1][star] = 0
    pieces = []
    idle_face = None
    for (W_, B_, frames, k) in ((W, B, FRAMES, K), (W2, B2, SKILL, K * K_SKILL)):
        for name, box, fr in frames:
            rgba, solid = cut(W_, B_, box)
            fx, fy = foot_x(solid)
            if fr is not None: fx = rgba.shape[1] * fr
            if name == 'idle':
                fcx, fcy = face_c(rgba, solid); idle_face = (fx - fcx, fy - fcy)
            p = shrink_soft(rgba, solid, k)   # 두 장으로 알파를 구해 흰 테두리 찌꺼기가 없음 — defringe는 가는 흰 후광을 지워서 안 씀
            pieces.append((name, p, fx * k, fy * k))
            print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} → {p.shape[1]}x{p.shape[0]}, 발 ({fx * k:.0f}, {fy * k:.0f})')
    base = {n: (p, fx, fy) for n, p, fx, fy in pieces}
    for skill, target in RECOLOR:
        for src in ('pray', 'ring'):
            p, fx, fy = base[src]
            pieces.append((f'{src}_{skill}', recolor(p, target, (fx, fy) if src == 'ring' else None), fx, fy))
    pack(pieces, OUT, 'healer_sr1')
    km = K * K_MIRACLE
    mp = []
    for name, box in MIRACLE:
        rgba, solid = cut(W2, B2, box, near_px=400)
        fcx, fcy = MIRACLE_FACE.get(name) or face_c(rgba, solid)
        fx, fy = fcx + idle_face[0] / K_MIRACLE, fcy + idle_face[1] / K_MIRACLE
        p = shrink_soft(rgba, solid, km)
        mp.append((name, p, fx * km, fy * km))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} → {p.shape[1]}x{p.shape[0]}, 발 ({fx * km:.0f}, {fy * km:.0f})')
    pack(mp, CAST_OUT, 'healer_miracle_cast_sr1')


if __name__ == '__main__':
    main()

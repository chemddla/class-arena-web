# 음유시인 시크릿 레어(금발 하프 연주자: 파란 로브·금빛 하프) 샘플 → 캐릭터 시트 assets/sprites/merc/bard_sr1.webp
# 사용: python tools/bard_sr1_build.py   (샘플은 assets/sprites/fx/samples/bard_sr1_src*.webp)
#   src5 = 스킬 3×3 판 (10~18), src6 = 판 (19~21 · 공격 판(안 씀) · 22~25), 어두운 회색 판 위에 그림 (판 위 칸 번호 글씨는 판 밖이라 안 잘림)
#   src1 = 2×2 네 칸 (왼쪽 위 = 대기, 네 칸 모두 = 걷기), src2 = 기본 공격, src3 = 피격, src4 = 쓰러짐 3칸 (흰 배경, 작은 그림)
# 샘플마다 그린 크기가 달라서 서 있는 칸의 머리~발 키를 대기에 맞춤 (공격 샘플 배율을 피격·쓰러짐에도 씀)
# 칸 순서·동작 구성은 bard_0과 같음 (0 대기 · 1~4 걷기 · 5 공격 · 6 피격 · 7~9 쓰러짐 · 10~25 스킬)
#   아직 샘플이 없는 동작 칸은 대기 자세로 채움 (샘플이 오면 FRAMES에 넣으면 그 칸만 바뀜)
# 샘플 정리:
#   - 배경은 아주 연한 회청색 한 가지 → 칸 가장자리에서 배경색과 비슷한 곳을 채워 나가 지움 (검은 외곽선이 있어서 하프 줄·흰 치마는 안 샘)
#   - 외곽선과 배경이 섞인 연한 회색 테두리는 줄일 때 반투명이 되고, 도트 느낌이 나게 투명도를 딱딱하게 만듦
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

D = 'assets/sprites/fx/samples/bard_sr1_'
OUT = 'assets/sprites/merc/bard_sr1.webp'
TARGET_H = 84   # 대기 자세 머리 꼭대기~발 (게임 칸 px), bard_0 대기(베레모~발)와 같은 키
COUNT = 26      # bard_0 칸 수

# (칸 번호, 샘플, x0, x1, y0, y1) — 배율은 샘플마다 SCALE_FROM 칸의 키로 정함
FRAMES = [
    (0, 'src1.webp', 31, 405, 25, 516),
    (1, 'src1.webp', 31, 405, 25, 516), (2, 'src1.webp', 419, 808, 25, 516),
    (3, 'src1.webp', 31, 405, 532, 1010), (4, 'src1.webp', 419, 808, 532, 1010),
    (5, 'src2.png', 0, 162, 0, 207),
    (6, 'src3.png', 0, 186, 0, 197),
    (7, 'src4.png', 0, 290, 0, 183), (8, 'src4.png', 290, 625, 0, 183), (9, 'src4.png', 625, 996, 0, 183),
]
SCALE_FROM = {'src1.webp': 0, 'src2.png': 5, 'src3.png': 5, 'src4.png': 5}
DOWN = (7, 8, 9)  # 쓰러짐: 떨어진 하프 조각도 남기고, 기준점은 몸 전체 가운데
HOLE_MIN = {'src1.webp': 200, 'src2.png': 40, 'src3.png': 40, 'src4.png': 40}  # 하프 안 흰 배경으로 볼 최소 넓이 (샘플 px, 게임 칸에서 약 7px²)
SMALL = (5, 6, 7, 8, 9)  # src2~4에서 온 칸
SRC = {}
RAW = {}  # 비교용: 배경을 빼지 않은 원본 조각 (python tools/bard_sr1_build.py raw → preview/bard_sr1_raw.png)
# 스킬 판: (칸 번호, 샘플, x0, x1, y0, y1) 판 안쪽. src6 가운데 줄 '#5 = 공격 칸'은 반영하지 말라고 해서 뺌
_C5 = [(6, 339), (346, 679), (686, 1020)]
_C6 = [(7, 254), (261, 508), (516, 763), (770, 1017)]
PANELS = [(10 + 3 * r + c, 'src5.webp', *_C5[c], *rw) for r, rw in enumerate([(31, 249), (287, 507), (545, 764)]) for c in range(3)]
PANELS += [(19 + c, 'src6.webp', *_C6[c], 32, 258) for c in range(3)] + [(22 + c, 'src6.webp', *_C6[c], 549, 759) for c in range(4)]
# 기준 판(이펙트가 거의 없는 판)에서 발 위치·배율(머리~발 키)을 재고, 다른 판은 머리 그림을 찾아 그만큼 옮김 (cut_panels)
PANEL_REF = {10: range(10, 19), 25: range(19, 26)}  # 샘플(src5 · src6)마다 기준 판
WATERMARK = {25: (120, 175, 90, 140)}  # 판 안 좌표 x0, x1, y0, y1: 회색 ✦ 워터마크 (채도 낮은 밝은 회색만 지움, 소매·하프는 남음)


def key_panel(f):
    # 어두운 회색 판 배경 빼기: 판 가장자리에서 판 색과 비슷한 곳을 채워 나가 지우고, 안에 갇힌 판 색 덩어리(하프 줄 사이·팔 사이)도 지움
    # 판보다 밝고 판 색과 가까운 픽셀 = 반투명 빛(불꽃·청록 빛·바람 끝) → 판 색을 빼서 투명도·색을 되살림. 판보다 어두운 픽셀(검은 외곽선)은 불투명
    i, name, x0, x1, y0, y1 = f
    im = np.array(Image.open(D + name).convert('RGB')).astype(float)[y0 + 3:y1 - 3, x0 + 3:x1 - 3]
    ring = np.concatenate([im[:3].reshape(-1, 3), im[-3:].reshape(-1, 3), im[:, :3].reshape(-1, 3), im[:, -3:].reshape(-1, 3)])
    K = np.median(ring, axis=0)
    d = np.abs(im - K).max(axis=2)
    lum = im.mean(axis=2) - K.mean()
    sat = im.max(axis=2) - im.min(axis=2)
    near = d < 12
    lab, n = ndi.label(near)
    areas = ndi.sum(near, lab, range(1, n + 1))
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    out = np.isin(lab, edge[edge > 0]) | np.isin(lab, 1 + np.where(areas >= 6)[0])
    # 하프 안 흰 배경 (밝은 판 샘플에도 남아 있으면)
    white = ~out & (im.min(axis=2) > 215) & (sat < 25)
    lab, n = ndi.label(white)
    out |= np.isin(lab, 1 + np.where(ndi.sum(white, lab, range(1, n + 1)) >= 40)[0])
    if i in WATERMARK:
        wx0, wx1, wy0, wy1 = WATERMARK[i]
        box = np.zeros_like(out); box[wy0:wy1, wx0:wx1] = True
        out |= box & (sat < 22) & (im.mean(axis=2) > 70)
    a = np.where(out, 0.0, np.where((lum > 0) & (d < 50), np.clip((d - 10) / 40, 0, 1), 1.0))
    al = np.maximum(a, 0.05)[..., None]
    rgb = np.where(((a > 0) & (a < 1))[..., None], K + (im - K) / al, im).clip(0, 255)
    m = a > 0
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    areas = ndi.sum(m, lab, range(1, n + 1))
    a = np.where(np.isin(lab, 1 + np.where(areas >= 8)[0]), a, 0)  # 음표·반짝이는 남기고 압축 티끌만 지움
    big = lab == np.argmax(areas) + 1
    return rgb, a, big


def head_match(T, rgb, ex, ey, r=40):
    # 기준 판 머리 그림(T)을 이 판의 기대 자리(ex, ey) 둘레 r px 안에서 찾아 가장 닮은 왼쪽 위 자리
    g = rgb.mean(axis=2)
    t = T - T.mean()
    best = (-9, ex, ey)
    for y in range(max(0, ey - r), min(g.shape[0] - T.shape[0], ey + r) + 1):
        for x in range(max(0, ex - r), min(g.shape[1] - T.shape[1], ex + r) + 1):
            w = g[y:y + T.shape[0], x:x + T.shape[1]]
            w = w - w.mean()
            v = (w * t).sum() / (np.sqrt((w * w).sum() * (t * t).sum()) + 1e-6)
            if v > best[0]: best = (v, x, y)
    return best


def cut_panels():
    # 판마다 캐릭터 자리가 조금씩 달라서, 기준 판의 머리(머리카락 꼭대기~이마 보석 아래) 그림을 각 판에서 찾아 그만큼 발 위치를 옮김
    # (이마 보석만 보면 청록 바람·빛에 헷갈림)
    data = {f[0]: (f, *key_panel(f)) for f in PANELS}
    out = {}
    for ref, rng in PANEL_REF.items():
        _, rgb, a, big = data[ref]
        ys, xs = np.where(big)
        foot = ys.max()
        fx = np.where(big[foot - (foot - ys.min()) // 7:foot + 1].any(axis=0))[0].mean()
        sc = TARGET_H / (foot - ys.min() + 1)
        hy0 = ys.min(); hh = int((foot - hy0) * 0.3)
        hx = np.where(big[hy0:hy0 + hh].any(axis=0))[0]
        hx0, hx1 = hx.min(), hx.max() + 1
        T = rgb[hy0:hy0 + hh, hx0:hx1].mean(axis=2)
        for i in rng:
            if i not in data: continue
            _, rgb, a, _ = data[i]
            v, mx, my = head_match(T, rgb, hx0, hy0)
            cx, cy = fx + mx - hx0, foot + my - hy0
            if i != ref: print(f'panel {i}: head shift ({mx - hx0}, {my - hy0}) match {v:.2f}')
            ys, xs = np.where(a > 0)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            out[i] = (np.dstack([rgb, a * 255])[y0:y1, x0:x1], (cx - x0) * sc, (y1 - 1 - cy) * sc, sc)
            f = data[i][0]
            raw = np.array(Image.open(D + f[1]).convert('RGB')).astype(float)[f[4] + 3:f[5] - 3, f[2] + 3:f[3] - 3]
            RAW[i] = np.dstack([raw, np.full(raw.shape[:2], 255.0)])[y0:y1, x0:x1]
        print('panel scale', ref, round(sc, 3))
    return out


def key_bg(name):
    if name not in SRC:
        rgb = np.array(Image.open(D + name).convert('RGB')).astype(float)
        bg = np.median(rgb[:4].reshape(-1, 3), axis=0)
        near = np.abs(rgb - bg).max(axis=2) < 26
        lab, _ = ndi.label(near)
        edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
        out = np.isin(lab, edge[edge > 0])
        # 외곽선 바깥에 번진 연한 회색 테두리(배경과 섞인 픽셀)를 바깥부터 벗겨 냄. 금발·크림색 치마는 채도가 있어서 남음
        sat = rgb.max(axis=2) - rgb.min(axis=2)
        halo = (np.abs(rgb - bg).max(axis=2) < 110) & (sat < 30)
        for _ in range(8):
            rim = ~out & halo & ndi.binary_dilation(out)
            if not rim.any(): break
            out |= rim
        # 하프 줄 사이로 보이는 흰 배경: 안에 갇힌 흰 덩어리 중 큰 것만 지우고 (눈 반짝임·옷 무늬 같은 작은 흰 점은 남김)
        # 흰 칸과 회색 줄이 섞인 연회색 가장자리도 2px까지 벗겨 냄. 회색 줄은 남김
        white = ~out & (rgb.min(axis=2) > 215) & (sat < 25)
        lab, n = ndi.label(white)
        areas = ndi.sum(white, lab, range(1, n + 1))
        hole = np.isin(lab, 1 + np.where(areas >= HOLE_MIN[name])[0])
        for _ in range(2):
            hole |= ~out & ndi.binary_dilation(hole) & (rgb.min(axis=2) > 190) & (sat < 25)
        out |= hole
        a = np.where(out, 0.0, 1.0)
        SRC[name] = (rgb, a)
    return SRC[name]


def cut(f):
    i, name, x0, x1, y0, y1 = f
    rgb, a = key_bg(name)
    rgb, a = rgb[y0:y1, x0:x1], a[y0:y1, x0:x1]
    m = a > 0.5
    lab, n = ndi.label(m)
    areas = ndi.sum(m, lab, range(1, n + 1))
    big = np.argmax(areas) + 1
    keep = m & (lab == big)
    if i in DOWN:
        keep = m & np.isin(lab, 1 + np.where(areas >= areas[big - 1] * 0.04)[0])
    ys, xs = np.where(keep)
    rgba = np.dstack([rgb, keep * 255.0])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    RAW[i] = np.dstack([rgb, np.full(a.shape, 255.0)])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 0
    cx = np.where((k if i in DOWN else k[int(k.shape[0] * 0.85):]).any(axis=0))[0].mean()  # 발(아래 15%) 가운데
    return rgba, cx


def shrink(rgba, sc, hard=True):
    h, w = rgba.shape[:2]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    sm = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * sc)), max(1, round(h * sc))), Image.LANCZOS)
    a = np.array(sm).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    if hard: a[..., 3:] = np.where(al > 90, 255, np.where(al > 40, al * 2, 0))
    else: a[..., 3:] = np.where(al > 200, 255, np.where(al < 12, 0, al))  # 반투명 빛은 살리고 거의 불투명한 곳만 딱딱하게
    return a.clip(0, 255).astype(np.uint8)


TILTED = (7, 8, 9)  # 쓰러지며 하프가 기울어진 칸: 줄 방향을 넓게 찾음
HARP_CELLS = range(0, 19)  # 하프 안이 흰 칸 (19~25는 원본부터 어두운 판 위에 줄이 그려져 있음)


def fix_harp(c, r, i):
    # 하프 점검 (c = 칸, r = 같은 자리·배율의 원본 조각): 원본 하프 안쪽 흰 부분은 배경이라 투명하게 하고,
    # 그 자리를 지나던 하프 줄은 원본 줄 방향·자리 그대로 다시 그음
    #   1) 흰 부분: 원본에서 금빛 테에 둘러싸인 흰 덩어리 (칸 가장자리와 이어진 흰 배경·눈 반짝임·크림색 치마는 빠짐)
    #   2) 줄 단서: 흰 부분 안에서 원본이 흰색보다 어두운 픽셀(희미한 줄) + 흰 부분 바로 아래·옆 2px 안에 보이는 밝은 회청색 줄
    #   3) 줄 방향: 세로에서 -60°~60°를 돌려 보며 단서가 가장 몇 줄로 모이는 각도, 줄 자리: 그 각도로 쟀을 때 단서가 몰린 자리
    #      (단서가 2px보다 띄엄띄엄하면 사이를 같은 간격으로 채움 — 원본 하프 줄은 고르게 늘어서 있음)
    if i not in HARP_CELLS: return
    px = r[..., :3].astype(int)
    L = px.mean(axis=2); sat = px.max(axis=2) - px.min(axis=2)
    R_, G_, B_ = px[..., 0], px[..., 1], px[..., 2]
    gold = (R_ > 130) & (R_ - B_ > 80) & (G_ > 80) & (B_ < 120)
    white = (L > 200) & (sat < (110 if i == 12 else 40))  # 불꽃 칸은 흰 배경이 분홍빛으로 물듦
    lab, n = ndi.label(white | (r[..., 3] == 0))
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))  # 칸 밖 투명한 곳과 이어진 흰 배경
    W = np.zeros_like(white)
    for k in range(1, n + 1):
        if k in border: continue
        reg = (lab == k) & white
        if reg.sum() < 15: continue  # 치마·소매의 작은 흰 무늬는 빠짐
        ring = ndi.binary_dilation(reg, iterations=4) & ~reg
        if gold[ring].mean() < 0.05: continue
        W |= reg
    if not W.any(): return
    W = ndi.binary_dilation(W) & (L > 175) & (sat < (110 if i == 12 else 45)) | W  # 흰 부분 가장자리 번진 픽셀까지
    o = c[..., :3].astype(int)
    oL = o.mean(axis=2); osat = o.max(axis=2) - o.min(axis=2)
    near = ndi.binary_dilation(W, iterations=2) & ~W
    shown = near & (c[..., 3] > 0) & (oL > 120) & (osat < 70) & (o[..., 2] >= o[..., 0] - 10) & ~gold  # 흰 부분 밖에 보이는 줄
    wl = np.median(L[W])
    faint = W & (L < wl - 12)  # 흰 부분 안 희미한 줄
    ev = shown | faint
    ys, xs = np.where(ev)
    c[W, 3] = 0
    if len(xs) < 3:
        print(f'harp cell {i}: white cleared, no string hint'); return
    best = None
    span = 60 if i in TILTED else 20  # 서 있는 자세 하프 줄은 거의 세로
    for deg in range(-span, span + 1, 3):
        t = np.radians(deg)
        u = np.round(xs * np.cos(t) + ys * np.sin(t)).astype(int)
        cnt = np.bincount(u - u.min())
        score = (cnt ** 2).sum() / len(u)
        if best is None or score > best[0]: best = (score, deg)
    t = np.radians(best[1])
    u = np.round(xs * np.cos(t) + ys * np.sin(t)).astype(int)
    cnt = np.bincount(u - u.min()).astype(float)
    # 단서가 몰린 자리(이웃보다 많은 곳)를 줄로, 줄 사이는 2px 이상 띄움
    pos = []
    for k in np.argsort(-cnt):
        if cnt[k] == 0: break
        if all(abs(k - q) >= 2 for q in pos): pos.append(k)
    pos = sorted(int(k + u.min()) for k in pos)
    # 띄엄띄엄한 줄 사이를 고르게 채움 (간격 2px)
    filled = set()
    for a, b in zip(pos, pos[1:] + [pos[-1]]):
        filled.add(a)
        if 3 < b - a <= 8: filled.update(range(a + 2, b - 1, 2))
    wy, wx = np.where(W)
    wu = np.round(wx * np.cos(t) + wy * np.sin(t)).astype(int)
    on = np.isin(wu, sorted(filled))
    # 줄 색 = 흰 부분 밖에 보이는 줄 색. 새하얗거나 회색이면 원본 줄처럼 연회청색, 불꽃에 물든 칸은 그 빛깔 그대로 밝기만 낮춤
    col = np.median(o[shown], axis=0) if shown.sum() >= 3 else np.array([255.0, 255, 255])
    col = np.array([200.0, 210, 226]) if col.max() - col.min() < 25 else col * min(1, 200 / col.mean())
    c[wy[on], wx[on], :3] = col
    c[wy[on], wx[on], 3] = 255
    print(f'harp cell {i}: white {int(W.sum())}px, strings at {best[1]}deg, {len(filled)} line(s)')


def main():
    cuts = {f[0]: cut(f) for f in FRAMES}
    src = {f[0]: f[1] for f in FRAMES}
    sc = {nm: TARGET_H / cuts[i][0].shape[0] for nm, i in SCALE_FROM.items()}
    print('scales', {k: round(v, 3) for k, v in sc.items()})
    pieces = {i: (shrink(r, sc[src[i]]), c * sc[src[i]], 0) for i, (r, c) in cuts.items()}
    for i, (r, c, below, s) in cut_panels().items():
        pieces[i] = (shrink(r, s, hard=False), c, int(round(below)))
    for i in range(COUNT):
        pieces.setdefault(i, pieces[0])
    L = max(int(np.ceil(c)) for _, c, _ in pieces.values()) + 2
    R = max(int(np.ceil(p.shape[1] - c)) for p, c, _ in pieces.values()) + 2
    B = max(d for _, _, d in pieces.values())
    H = max(p.shape[0] - d for p, _, d in pieces.values()) + B + 3
    cellW = L + R
    sheet = np.zeros((H, cellW * COUNT, 4), np.uint8)
    for i in range(COUNT):
        p, c, d = pieces[i]
        x = i * cellW + L - int(round(c))
        y = H - 2 - B - p.shape[0] + d   # 발 = 기준점 (칸 아래에서 B + 2px 위)
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    # 작은 흰 배경 샘플(공격·피격·쓰러짐)은 외곽선이 배경과 번져서 줄이면 바깥에 연회색 점이 남음 → 바깥과 맞닿은 연회색 테두리를 2겹까지 지움
    # (하프 안 구멍은 바깥과 이어지지 않아서 회색 줄은 남음)
    for i in SMALL:
        c = sheet[:, i * cellW:(i + 1) * cellW]
        for _ in range(2):
            op = c[..., 3] > 0
            lab, _ = ndi.label(~op)
            outside = np.isin(lab, np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
            px = c[..., :3].astype(int)
            light = (px.mean(axis=2) > 170) & (px.max(axis=2) - px.min(axis=2) < 45)
            c[op & light & ndi.binary_dilation(outside), 3] = 0
    raw = np.zeros_like(sheet)  # 원본을 같은 배율·자리에 놓은 시트 (하프 점검용)
    for i in range(COUNT):
        p, c, d = pieces[i]
        r = shrink(RAW[i if i in RAW else 0], p.shape[1] / RAW[i if i in RAW else 0].shape[1], hard=False)[:p.shape[0], :p.shape[1]]
        x = i * cellW + L - int(round(c)); y = H - 2 - B - p.shape[0] + d
        raw[y:y + r.shape[0], x:x + r.shape[1]] = r
    for i in range(COUNT):
        fix_harp(sheet[:, i * cellW:(i + 1) * cellW], raw[:, i * cellW:(i + 1) * cellW], i)
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    if 'raw' in sys.argv:
        Image.fromarray(raw, 'RGBA').save('preview/bard_sr1_raw.png')
    idle = pieces[0][0]
    hx = np.where(idle[:int(idle.shape[0] * 0.5), :, 3].any(axis=0))[0]
    print(f'char cellW={cellW} cellH={H} anchorX={L} anchorY={H - 2 - B} count={COUNT} topH={idle.shape[0]} portraitCX={L - int(round(pieces[0][1])) + int(hx.mean())}')


if __name__ == '__main__':
    main()

# 검사 참격 시트 끝 다듬기 (2026-11-12 사용자: 무참·일반공격 참격 끝이 뭉툭함 → 더 날카롭게)
#   원본 시트는 pixelfx로 구운 것(tools/swordsman_fx/*.js)인데 초승달 끝이 둥글고, 무참 베기·X는 칸 끝에서 잘려 끝이 평평함
#   → 칸마다 빛의 뼈대(가운데 선)를 찾아, 뼈대 끝에서 T px 안쪽부터 굵기를 0까지 줄임 (끝을 바늘처럼). 빛을 더하지는 않고 깎기만
#   뼈대: 불투명도 > MASK_A 인 곳을 Zhang-Suen 세선화 → 짧은 가지(SPUR px 미만) 정리. 별·불티처럼 뼈대에서 먼 점은 건드리지 않음
#   원본은 git에 있으니 다시 구우면(tools/swordsman_fx_pack.py) 이 스크립트를 한 번 더 돌릴 것
#   사용: python tools/sword_fx_taper.py [이름...]   (안 주면 NAMES 전부)
import json, sys
from collections import deque
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

D = 'assets/sprites/fx/sword/'
NAMES = ['iai-cross', 'iai-diag', 'iai-line', 'iai-moon', 'iai-pierce', 'iai-pillar', 'iai-tri', 'iai-twin', 'mucham-cut', 'mucham-pierce', 'mucham-final']
MASK_A, T, SPUR, GLOW, TIP_FILL = 110, 26, 6, 2.5, 0.6
HALO = 1.7   # 옅은 빛 줄이는 정도 (불투명도 거듭제곱)   # 뼈대를 찾을 불투명도(밝은 날만) · 끝을 깎는 길이 · 정리할 짧은 가지 길이 · 둘레 빛 = 날 반폭의 몇 배 · 끝 둘레가 이만큼 넘게 빛이면 묻힌 끝
N8 = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]


def thin(m):  # Zhang-Suen 세선화
    m = np.pad(m.astype(np.uint8), 1)
    while True:
        changed = False
        for step in (0, 1):
            P = [np.roll(np.roll(m, -dy, 0), -dx, 1) for dy, dx in [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]]  # P2..P9
            B = sum(P)
            A = sum(((P[i] == 0) & (P[(i + 1) % 8] == 1)).astype(int) for i in range(8))
            c1 = (P[0] * P[2] * P[4] == 0) if step == 0 else (P[0] * P[2] * P[6] == 0)
            c2 = (P[2] * P[4] * P[6] == 0) if step == 0 else (P[0] * P[4] * P[6] == 0)
            rm = (m == 1) & (B >= 2) & (B <= 6) & (A == 1) & c1 & c2
            if rm.any(): m[rm] = 0; changed = True
        if not changed: return m[1:-1, 1:-1].astype(bool)


def neighbors(sk, y, x):
    H, W = sk.shape
    return [(y + dy, x + dx) for dy, dx in N8 if 0 <= y + dy < H and 0 <= x + dx < W and sk[y + dy, x + dx]]


def prune(sk):  # SPUR px보다 짧은 가지와 외딴 점 지움 (긴 가지는 그대로)
    sk = sk.copy()
    for _ in range(3):
        ends = [(y, x) for y, x in zip(*np.where(sk)) if len(neighbors(sk, y, x)) <= 1]
        for e in ends:
            path, cur, prev = [e], e, None
            while len(path) <= SPUR:
                nb = [n for n in neighbors(sk, *cur) if n != prev and n not in path]
                if len(nb) != 1 or len(neighbors(sk, *nb[0])) > 2: break   # 갈림길에 닿음
                prev, cur = cur, nb[0]; path.append(cur)
            nb_end = [n for n in neighbors(sk, *cur) if n not in path]
            if len(path) <= SPUR and len(nb_end) >= 1 and len(neighbors(sk, *nb_end[0])) > 2:   # 갈림길로 이어진 짧은 가지
                for p in path: sk[p] = False
            elif len(path) <= 2 and not nb_end: # 외딴 점
                for p in path: sk[p] = False
    return sk


def taper(rgba):
    a = rgba[..., 3].astype(float)
    amax = a.max()
    if amax < 1: return rgba
    m = a > MASK_A * amax / 255   # 흐려지는 칸도 같은 비율로 (안 그러면 날이 토막나 끝이 여러 개)
    if m.sum() < 20: return rgba
    sk = prune(thin(m))
    if not sk.any(): return rgba
    dt = ndi.distance_transform_edt(m)   # 밝은 날의 반폭
    lit = a > 30 * amax / 255
    H, W = a.shape
    def tip(y, x):   # 정말 바깥으로 뻗은 끝인지: 끝 둘레 원 안이 빛으로 거의 차 있으면 (다른 빛 속에 묻힌 끝 = 속도선이 X·초승달에 닿는 곳) 깎지 않음
        r = int(dt[y, x] * GLOW + 4)
        ys, xs = np.ogrid[-r:r + 1, -r:r + 1]; disk = ys * ys + xs * xs <= r * r
        sub = np.zeros_like(disk)
        y0, y1, x0, x1 = max(0, y - r), min(H, y + r + 1), max(0, x - r), min(W, x + r + 1)
        sub[y0 - (y - r):y1 - (y - r), x0 - (x - r):x1 - (x - r)] = lit[y0:y1, x0:x1]   # 칸 밖은 빈 곳
        return (sub & disk).sum() / disk.sum() < TIP_FILL
    ends = [(y, x) for y, x in zip(*np.where(sk)) if len(neighbors(sk, y, x)) <= 1 and tip(y, x)]
    geo = np.full(sk.shape, np.inf); q = deque()   # 뼈대 끝에서 뼈대를 따라 잰 거리
    for e in ends: geo[e] = 0; q.append(e)
    while q:
        y, x = q.popleft()
        for n in neighbors(sk, y, x):
            if geo[n] > geo[y, x] + 1: geo[n] = geo[y, x] + 1; q.append(n)
    perp, (iy, ix) = ndi.distance_transform_edt(~sk, return_indices=True)
    g = geo[iy, ix]; w = dt[iy, ix] * GLOW + 4   # 가장 가까운 뼈대 점의 끝까지 거리 · 둘레 빛까지 친 반폭
    own = (perp <= w) & np.isfinite(g)   # 이 뼈대의 몸통과 둘레 빛 (별·불티처럼 먼 점은 제외)
    allow = w * np.clip(g / T, 0, 1) ** 0.9   # 끝으로 갈수록 허용 반폭이 0으로
    k = np.where(own, np.clip(1 - (perp - allow) / 2, 0, 1), 1)
    k = ndi.gaussian_filter(ndi.minimum_filter(k, 3), 0.8)   # 어두운 테두리도 같이 깎이게 넓히고 부드럽게 (계단 없게)
    out = rgba.copy()
    a2 = amax * (a / amax) ** HALO   # 옅은 둘레 빛을 줄여 흰 날이 또렷하게 (그 칸에서 가장 진한 날은 그대로)
    out[..., 3] = np.round(a2 * np.minimum(1, k)).astype(np.uint8)
    return out


def main(names):
    meta = json.load(open(D + 'sword_fx.json', encoding='utf-8'))
    for n in names:
        w, h, cols, nf = meta[n][:4]
        im = np.array(Image.open(D + n + '.webp').convert('RGBA'))
        for f in range(nf):
            y0, x0 = (f // cols) * h, (f % cols) * w
            im[y0:y0 + h, x0:x0 + w] = taper(im[y0:y0 + h, x0:x0 + w])
        Image.fromarray(im, 'RGBA').save(D + n + '.webp', 'WEBP', lossless=True)
        print(n, nf, 'frames')


if __name__ == '__main__':
    main(sys.argv[1:] or NAMES)

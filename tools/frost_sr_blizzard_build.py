# 시크릿 레어 빙결술사(얼음 여왕) 블리자드 전용 소용돌이 그림 4장 → fx/frost_sr_blizzard.webp (가로 한 줄)
# 사용: python tools/frost_sr_blizzard_build.py
#  - 원본: fx/samples/frost_sr1_blizzard_1~4_src.webp (검은 배경 1024×572)
#    1번은 2×2 칸 모음이라 4번 칸(꽉 찬 소용돌이)만 2배로 키워 씀, 2~4번은 팔 두 개가 뻗은 소용돌이 그대로
#  - 소용돌이 중심을 그림 가운데에 두고, 원본 밖으로 잘린 부분·✦ 워터마크·칸 번호를 채움
#    core: 같은 그림을 중심 둘레로 돌린 복사본(180°·90°·45°…)으로 · arms: 180° 복사본 → 그래도 빈 곳은 core 소용돌이를 깔아 채움
#  - 바깥 둘레는 서서히 투명하게 → 게임에서 돌려도 잘린 테두리가 보이지 않음
# 칸 순서: arms0 · arms1 · arms2 (2·3·4번) · core (1번의 4번 칸)
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

SRC = 'assets/sprites/fx/samples/frost_sr1_blizzard_{}_src.webp'
OUT = 'assets/sprites/fx/frost_sr_blizzard.webp'
BG = np.array([18.0, 26.0, 27.0])
CELL = 720           # 칸 하나 (정사각형)
SRC_R = 560          # 원본 기준 반지름: 칸 하나가 원본에서 이만큼 반지름을 덮음
FEATHER = 56         # 원본 가장자리·가린 곳에서 복사본으로 넘어가는 폭 (원본 px)
ROTS = [0, np.pi, np.pi / 2, -np.pi / 2, np.pi / 4, -3 * np.pi / 4, -np.pi / 4, 3 * np.pi / 4]
ARM_ROTS = [0, np.pi]


def unblend(rgb):
    d = (rgb - BG).max(axis=2)
    a = (d / 90).clip(0, 1)
    a = np.where(a < 0.06, 0, a)
    c = np.where(a[..., None] > 0, BG + (rgb - BG) / np.maximum(a[..., None], 1e-3), 0).clip(0, 255)
    return c, a


def load(i):
    rgb = np.asarray(Image.open(SRC.format(i)).convert('RGB')).astype(float)
    if i == 1:  # 2×2 칸 중 오른쪽 아래 칸, 칸 경계·번호를 피해 안쪽만 2배로
        rgb = rgb[286 + 3:572, 512 + 3:1024]
        rgb = np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize((rgb.shape[1] * 2, rgb.shape[0] * 2), Image.BICUBIC)).astype(float)
    return rgb


# 소용돌이 중심 · 가릴 곳(원 [x, y, r]) — 원본(1번은 2배로 키운 칸) 좌표
SETUP = {
    2: {'c': (502, 280), 'mask': [(934.4, 483.4, 26)]},
    3: {'c': (505, 268), 'mask': [(934.4, 483.4, 26)]},
    4: {'c': (505, 268), 'mask': [(934.4, 483.4, 26)]},
    1: {'c': ((764 - 515) * 2, (423 - 289) * 2), 'mask': [((934.4 - 515) * 2, (483.4 - 289) * 2, 46), (0, 0, 60)]},
}


def weight_map(h, w, masks):
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    edge = np.minimum.reduce([xx, yy, w - 1 - xx, h - 1 - yy])
    wt = (edge / FEATHER).clip(0, 1)
    for mx, my, mr in masks:
        dist = np.hypot(xx - mx, yy - my) - mr
        wt = np.minimum(wt, (dist / FEATHER).clip(0, 1))
    return wt


def build(i, under=None):
    rgb = load(i)
    col, a = unblend(rgb)
    h, w = a.shape
    s = SETUP[i]
    cx, cy = s['c']
    wt = weight_map(h, w, s['mask'])
    pre = np.dstack([col * a[..., None], a])  # 곱한 색 + 불투명도
    k = SRC_R / (CELL / 2)
    yy, xx = np.mgrid[0:CELL, 0:CELL].astype(float)
    dx, dy = (xx - CELL / 2 + 0.5) * k, (yy - CELL / 2 + 0.5) * k
    acc = np.zeros((CELL, CELL, 4))
    accw = np.zeros((CELL, CELL))
    for r in (ARM_ROTS if under is not None else ROTS):
        sx = cx + dx * np.cos(r) - dy * np.sin(r)
        sy = cy + dx * np.sin(r) + dy * np.cos(r)
        wv = map_coordinates(wt, [sy, sx], order=1, cval=0)
        take = (1 - accw) * wv
        for ch in range(4):
            acc[..., ch] += take * map_coordinates(pre[..., ch], [sy, sx], order=1, cval=0)
        accw += take
    if under is not None:
        # core 소용돌이를 밑에 깔아 겹침: 원본이 있는 곳은 옅게, 빈 곳은 진하게 (경계에 줄이 생기지 않게)
        uw = 0.4 + 0.6 * (1 - accw)
        acc = acc + (1 - acc[..., 3:4]) * under * uw[..., None]
        accw = np.ones_like(accw)
    acc /= np.maximum(accw, 1e-6)[..., None]
    if under is None and i == 1:
        build.core = acc.copy()
    rr = np.hypot(dx, dy) / SRC_R
    fade = ((1 - rr) / 0.2).clip(0, 1)  # 바깥 20%에서 서서히 투명
    fade = fade * fade * (3 - 2 * fade)
    alpha = acc[..., 3] * fade
    color = acc[..., :3] / np.maximum(acc[..., 3:4], 1e-3)
    return np.dstack([color, alpha * 255]).clip(0, 255).astype(np.uint8)


def main():
    core = build(1)
    cells = [build(i, build.core) for i in (2, 3, 4)] + [core]
    Image.fromarray(np.hstack(cells), 'RGBA').save(OUT, 'WEBP', quality=80, method=6)
    print(OUT, len(cells), 'cells of', CELL)


if __name__ == '__main__':
    main()

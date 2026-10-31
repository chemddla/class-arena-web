# 주술사 시크릿 레어(역병 의사) 히든 스킬 [파멸의 의식] 샘플 → 시전 시트 assets/sprites/fx/curse_sr1_ruin_cast.webp
#   + 발동 직후 폭발 자세 통째 그림 assets/sprites/fx/curse_sr1_ruin_boom.webp
# 사용: python tools/curse_sr1_ruin_build.py   (샘플 assets/sprites/fx/samples/curse_sr1_ruin_src.png · curse_sr1_ruin_boom_src.webp)
# 시전 시트 칸은 curse_ruin_cast와 같음: 0·1 붉은 불꽃 두르기 · 2 마법진 위에서 지팡이 치켜들기(검은 기둥) · 3 폭발 · 4 연기 속 마무리
#   (모두 발 = 기준점, 오른쪽을 봄)
# 샘플 정리:
#   - 칸 사이 가는 세로 구분선이 들어가지 않게 마법진·마무리 칸을 좁게 자름
#   - 한 줄 샘플은 연두 배경. 검은 기둥·연기는 반투명이라 배경색을 빼서 반투명 그대로 복원 (curse_ruin_build.py와 같은 방식)
#   - 한 줄 샘플의 마법진 칸(시전 끝)은 따로 받은 샘플(curse_sr1_ruin_circle_src.webp)로 바꿈
#   - 한 줄 샘플의 폭발 칸은 따로 받은 폭발 샘플(어두운 초록 배경)로 바꿈. 3칸에도 같은 그림을 줄여 넣음 (폭발 그림을 못 불러왔을 때만 씀)
#   - 왼쪽 아래 두 칸(평소 자세)은 일반 시트와 겹쳐서 안 씀. 사신 칸은 게임에서 안 써서 자르지 않음
#   - 칸마다 캐릭터 크기가 달라서 후드 꼭대기~옷자락 끝 키를 curse_sr1 시트(86px)에 맞춤.
#     불꽃 두르기 두 칸은 몸이 통통하게 그려져 같은 키면 커 보여서 키를 84로 잡아 조금 작게
#   - 폭발 샘플 오른쪽 아래 ✦ 워터마크 지움
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from curse_ruin_build import crop, shrink

SRC = 'assets/sprites/fx/samples/curse_sr1_ruin_src.png'
BOOM_SRC = 'assets/sprites/fx/samples/curse_sr1_ruin_boom_src.webp'
CIRCLE_SRC = 'assets/sprites/fx/samples/curse_sr1_ruin_circle_src.webp'
OUT_CAST = 'assets/sprites/fx/curse_sr1_ruin_cast.webp'
OUT_BOOM = 'assets/sprites/fx/curse_sr1_ruin_boom.webp'
STAND_H = 86   # curse_sr1 시트 대기 자세 후드 꼭대기~옷자락 끝
# (이름, x0, x1, y0, y1, 후드 꼭대기~옷자락 키, 발 x, 발 y, 잘린 테두리 흐리기 [위, 왼, 오른])
# 폭발 샘플: 후드 꼭대기~옷자락 끝 키, 두 발 가운데 x, 발바닥 y (주변이 온통 검은 폭발이라 눈으로 잼)
BOOM_FIT = (360, 495, 637)
CAST = [
    ('aura0',   0,  95,   0, 104, 84,  45,  99, (0, 0, 0)),
    ('aura1',  95, 195,   0, 104, 84, 140,  99, (0, 0, 0)),
    ('circle', 60, 965,   0, 560, 210, 517, 488, (30, 0, 0)),  # 따로 받은 시전 끝 샘플 (나무 가지 위 붉은 해골). 위가 잘려 있어 흐리게
    ('boom',   None, None, None, None, None, None, None, None),
    ('finish', 864, 1024, 0, 200, 86, 927, 198, (0, 0, 0)),
]


def load_light(path, strip=True):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    key = np.median(np.concatenate([im[:3].reshape(-1, 3), im[-3:].reshape(-1, 3)]), axis=0)
    gex = im[..., 1] - np.maximum(im[..., 0], im[..., 2])
    kg = key[1] - max(key[0], key[2])
    a = np.clip(1 - (gex - 6) / (kg - 6), 0, 1)
    al = np.maximum(a, 1e-3)[..., None]
    rgb = ((im - (1 - a[..., None]) * key) / al).clip(0, 255)
    rgb[..., 1] = np.minimum(rgb[..., 1], np.maximum(rgb[..., 0], rgb[..., 2]) + 6)  # 초록 번짐 (그림엔 초록이 거의 없음)
    a[a < 0.06] = 0
    # 그림 테두리의 밝은 번짐: 반쯤 투명한 가장자리는 어두운 외곽선 색으로 (curse_ruin_build.py와 같음)
    edge = (a < 0.6) & ndi.binary_dilation(a == 0, iterations=1)
    rgb[edge] *= 0.3
    if strip: a[104:200, 0:200] = 0  # 왼쪽 아래 평소 자세 두 칸
    return rgb, a


def load_boom(path):
    # 어두운 초록 배경: 모서리 색을 배경으로 보고, 초록 기운이 도는 픽셀만 배경과 섞인 반투명 (해골·연기·파편은 그대로)
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    key = np.median(np.concatenate([im[:20, :20].reshape(-1, 3), im[:20, -20:].reshape(-1, 3), im[-20:, :20].reshape(-1, 3)]), axis=0)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    d = np.sqrt(((im - key) ** 2).sum(axis=2))
    greenish = g > np.maximum(r, b) + 10
    a = np.where(greenish, np.clip((d - 18) / 70, 0, 1), 1.0)
    wm = im[630:690, 890:950]
    a[630:690, 890:950] = np.where(wm[..., 0] < wm[..., 1] + 40, 0, a[630:690, 890:950])  # ✦ 워터마크 (붉은 마법진만 남김)
    m = a > 0.05
    lab, n = ndi.label(m)
    areas = ndi.sum(m, lab, range(1, n + 1))
    a = np.where(np.isin(lab, 1 + np.where(areas >= 12)[0]), a, 0)
    al = np.maximum(a, 1e-3)[..., None]
    rgb = np.where(a[..., None] < 1, key + (im - key) / al, im).clip(0, 255)
    rgb[..., 1] = np.minimum(rgb[..., 1], np.maximum(rgb[..., 0], rgb[..., 2]) + 6)
    return rgb, a


def main():
    rgb, a = load_light(SRC)
    crgb, ca = load_light(CIRCLE_SRC, strip=False)
    ca[455:510, 910:965] = 0  # ✦ 워터마크
    brgb, ba = load_boom(BOOM_SRC)
    bh, bfx, bfy = BOOM_FIT
    pieces = []
    for name, x0, x1, y0, y1, ch, fx, fy, fade in CAST:
        if name == 'boom':
            sc = STAND_H / bh
            pieces.append((name, shrink(np.dstack([brgb, ba * 255]), sc), bfx * sc, bfy * sc))
            continue
        sc = STAND_H / ch
        src = (crgb, ca) if name == 'circle' else (rgb, a)
        p = shrink(crop(*src, x0, x1, y0, y1, fade), sc)
        pieces.append((name, p, (fx - x0) * sc, (fy - y0) * sc))
    L = int(np.ceil(max(ax for _, _, ax, _ in pieces))) + 1
    R = int(np.ceil(max(p.shape[1] - ax for _, p, ax, _ in pieces))) + 1
    U = int(np.ceil(max(ay for _, _, _, ay in pieces))) + 1
    D = int(np.ceil(max(p.shape[0] - ay for _, p, _, ay in pieces))) + 1
    cellW, cellH = L + R, U + D
    sheet = np.zeros((cellH, cellW * len(pieces), 4), np.uint8)
    for i, (name, p, ax, ay) in enumerate(pieces):
        x, y = i * cellW + L - int(round(ax)), U - int(round(ay))
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT_CAST, 'WEBP', lossless=True)
    print(f'cast cellW={cellW} cellH={cellH} anchorX={L} anchorY={U} count={len(pieces)}')
    # 폭발 통째 그림: 테두리 투명 부분만 잘라냄. boomK = 크기 1일 때 그림 1px의 월드 크기 (캐릭터 키가 curse_sr1과 같게)
    ys, xs = np.where(ba > 0.05)
    t = np.dstack([brgb, ba * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8)
    Image.fromarray(t, 'RGBA').save(OUT_BOOM, 'WEBP', lossless=True)
    print(f'boom: [{t.shape[1]}, {t.shape[0]}, {bfx - xs.min()}, {bfy - ys.min()}]  boomK={STAND_H * 54 / (81 * bh):.3f}')  # 54 = SPRITE_DRAW_H, 81 = curse_sr1 standH


if __name__ == '__main__':
    main()

# 주술사 히든 스킬 [파멸의 의식] 샘플(초록 배경 1024×201 한 줄) → 시전 시트 assets/sprites/fx/curse_ruin_cast.webp + 사신 이펙트 assets/sprites/fx/curse_ruin_fx.webp
# 사용: python tools/curse_ruin_build.py [샘플 png]  (기본 assets/sprites/fx/samples/curse_ruin_src.png)
# 시전 시트 칸: 0·1 붉은 불꽃 두르기 · 2 마법진 위에서 지팡이 치켜들기(검은 기둥) · 3 폭발 · 4 연기 속 마무리 (모두 발 = 기준점, 오른쪽을 봄)
# 샘플 오류 정리:
#   - 검은 기둥·연기·사신 뒤 어둠이 반투명이라 초록과 섞임 → 배경색을 빼서 반투명 그대로 복원
#   - 칸마다 캐릭터 크기가 다름 (작은 칸 뿔~발 약 78px, 마법진 칸 약 98px) → 칸별 배율로 같은 키(STAND_H)에 맞춤
#   - 기둥·사신 칸은 그림 위·옆 테두리에서 잘려 있음 → 테두리 쪽으로 갈수록 흐려지게
#   - 왼쪽 아래 두 칸(평소 자세)은 일반 시트와 겹쳐서 안 씀, 마무리 칸의 ✦ 워터마크 지움
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT_CAST = 'assets/sprites/fx/curse_ruin_cast.webp'
OUT_FX = 'assets/sprites/fx/curse_ruin_fx.webp'
KEY = np.array([25.0, 208.0, 14.0])
STAND_H = 89   # 일반 시트(curse_0) 대기 자세 키와 같게
# (이름, x0, x1, y0, y1, 캐릭터 뿔~발 높이, 발 x, 발 y, 잘린 테두리 흐리기 [위, 왼, 오른])
CAST = [
    ('aura0',   4,  92,   0, 104, 78,  45,  96, (0, 0, 0)),
    ('aura1',  95, 192,   0, 104, 78, 138,  96, (0, 0, 0)),
    ('circle', 205, 398,  0, 201, 98, 290, 160, (40, 0, 0)),
    ('boom',  398, 634,   0, 201, 78, 480, 157, (0, 0, 0)),
    ('finish', 878, 1010, 0, 201, 80, 920, 195, (0, 0, 0)),
]
REAPER = ('reaper', 634, 878, 0, 201, (40, 24, 24))  # 사신 + 붉은 번개 소용돌이 (적 머리 위에 그림). 기준점 = 바닥 소용돌이 가운데
REAPER_SCALE = 0.62


def load(path):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    gex = g - np.maximum(r, b)
    a = np.clip(1 - (gex - 6) / (KEY[1] - KEY[0] - 6), 0, 1)  # 초록 기운만큼 투명 (어두운 연기도 반투명으로)
    al = np.maximum(a, 1e-3)[..., None]
    rgb = ((im - (1 - a[..., None]) * KEY) / al).clip(0, 255)
    a[a < 0.06] = 0
    # 그림 테두리의 밝은 번짐(확대·압축 때 생긴 흰 테두리): 반쯤 투명한 가장자리는 어두운 외곽선 색으로
    edge = (a < 0.6) & ndi.binary_dilation(a == 0, iterations=1)
    rgb[edge] *= 0.3
    a[100:201, 0:200] = 0          # 왼쪽 아래 평소 자세 두 칸
    a[130:165, 965:1010] = np.where(a[130:165, 965:1010] < 0.9, 0, a[130:165, 965:1010])  # ✦ 워터마크(밝은 반투명)
    return rgb, a


def crop(rgb, a, x0, x1, y0, y1, fade, solid=False):
    c, al = rgb[y0:y1, x0:x1], a[y0:y1, x0:x1].copy()
    if solid:  # 사신 뒤 반투명 어둠 사각형은 지우고 붉은 번개 빛만 반투명으로 남김
        c = c.copy()
        red = c[..., 0] > c[..., 1] + 60
        glow = (al < 0.92) & ~red & ndi.binary_dilation(red & (al > 0.9), iterations=4)
        c[glow] = [190, 24, 40]  # 번개 둘레 빛: 초록과 섞여 누렇게 남은 색을 붉게
        al[glow] *= 0.7
        al[(al < 0.92) & ~red & ~glow] = 0
        olive = (c[..., 1] > c[..., 0] - 15) & (c[..., 1] > c[..., 2] + 12) & (al > 0)
        c[olive] = np.array([170.0, 22, 38]) * (c[olive].max(axis=1, keepdims=True) / 200).clip(0.3, 1)
    h, w = al.shape
    t, l, r = fade
    if t: al *= np.clip(np.arange(h) / t, 0, 1)[:, None]
    if l: al *= np.clip(np.arange(w) / l, 0, 1)[None, :]
    if r: al *= np.clip((w - 1 - np.arange(w)) / r, 0, 1)[None, :]
    m = al > 0.05
    lab, n = ndi.label(m)
    areas = ndi.sum(m, lab, range(1, n + 1))
    for i in range(1, n + 1):
        if areas[i - 1] < 6: al[lab == i] = 0
    return np.dstack([c, al * 255])


def shrink(rgba, sc):
    h, w = rgba.shape[:2]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    sm = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * sc)), max(1, round(h * sc))), Image.LANCZOS)
    a = np.array(sm).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    return a.clip(0, 255).astype(np.uint8)


def main(path):
    rgb, a = load(path)
    pieces = []
    for name, x0, x1, y0, y1, ch, fx, fy, fade in CAST:
        sc = STAND_H / ch
        p = shrink(crop(rgb, a, x0, x1, y0, y1, fade), sc)
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
    print(f'cast cellW={cellW} cellH={cellH} anchorX={L} anchorY={U} standH={STAND_H} count={len(pieces)}')
    name, x0, x1, y0, y1, fade = REAPER
    p = shrink(crop(rgb, a, x0, x1, y0, y1, fade, solid=True), REAPER_SCALE)
    Image.fromarray(p, 'RGBA').save(OUT_FX, 'WEBP', lossless=True)
    print(f'reaper w={p.shape[1]} h={p.shape[0]} anchor=({round((760 - x0) * REAPER_SCALE)},{round((188 - y0) * REAPER_SCALE)})')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/fx/samples/curse_ruin_src.png')

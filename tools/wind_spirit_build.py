# 정령사 바람 정령 샘플(흰 배경) → 몬스터 시트 assets/sprites/monster/wind_spirit.webp
# 사용: python tools/wind_spirit_build.py   (샘플은 assets/sprites/fx/samples/wind_spirit_*_src.png)
# 정리 방식은 tools/fire_spirit_build.py와 같음 (SPIRITS에 원소를 더하면 다른 정령도 이 파일로 만들 수 있음)
#
# 🌪️ 바람 (꼬마 회오리): 0 대기 · 1~2 걷기 · 3 기본 공격 (바람 칼날) · 4 피격 · 5 쓰러짐 (흐려지며 풀림) · 6 바람 조각으로 흩어짐 · 7 회피 (반투명)
#   - 대기·피격·회피 샘플 왼쪽 위 모서리의 글자 조각 → 지움
#   - 회피 칸은 몸 전체 불투명도를 0.55로 (바람처럼 흐려지며 비켜남)
# 쓰러짐·폭발 칸(게임의 pop)은 정령이 사라질 때 spirit_pop 이펙트로 그림 (죽은 정령은 유닛으로 그리지 않음)
# 크기: 한 원소의 샘플들은 같은 크기로 그려져 있어서 원소마다 같은 배율 하나
# 샘플 정리:
#   - 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움 (눈의 흰 하이라이트는 남김)
#   - 몸과 떨어진 불씨·물방울도 칸 안에 있으면 그대로 둠
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

# 원소 → (배율, [(샘플, 칸 이름, 샘플 안 x 범위, 지울 상자들 [(x0, x1, y0, y1)], 투명도)])
SPIRITS = {
    'wind': (0.7, [
        ('idle', 'idle', (0, 134), [(0, 15, 0, 13)], 1),
        ('walk', 'walk0', (0, 170), [], 1), ('walk', 'walk1', (170, 335), [], 1),
        ('atk', 'atk', (0, 214), [], 1),
        ('hurt', 'hurt', (0, 151), [(0, 10, 0, 16)], 1),
        ('down', 'down0', (0, 165), [], 1), ('down', 'down1', (165, 333), [], 1),
        ('evade', 'evade', (0, 132), [(0, 16, 0, 22)], 0.55),
    ]),
}


def load(elem, name, xr, cuts, glow=False, allwhite=False):
    # xr = (x0, x1) 또는 (x0, x1, y0, y1): 샘플 안 그 칸 범위 (y를 주면 칸 위에 적힌 글자 줄을 빼고 자를 수 있음)
    im = np.array(Image.open(f'assets/sprites/fx/samples/{elem}_spirit_{name}_src.png').convert('RGB')).astype(float)
    im = im[xr[2]:xr[3], xr[0]:xr[1]] if len(xr) == 4 else im[:, xr[0]:xr[1]]
    white = (im.min(axis=2) > 222) & (im.max(axis=2) - im.min(axis=2) < 22)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    if allwhite: bg = bg | white   # 속이 빈 거품처럼 가장자리와 이어지지 않은 흰 속도 지움 (눈 하이라이트가 없는 칸만)
    for x0, x1, y0, y1 in cuts: bg[y0:y1, x0 - xr[0] if x0 >= xr[0] else 0:max(0, x1 - xr[0])] = True
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)
    if glow:   # 흰 배경 위 옅은 빛(후광): 배경에서 이어진 밝은 픽셀은 흰색과 떨어진 만큼만 불투명 (진한 몸·하트는 그대로)
        cand = ~bg & (im.min(axis=2) > 150)
        lab2, _ = ndi.label(cand | bg)
        g = cand & np.isin(lab2, np.unique(lab2[bg]))
        a = np.where(g, np.clip((255 - im.min(axis=2)) / 170, 0, 1) * 0.8, a)
        rim = rim | g
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    # 아주 작은 얼룩(흐린 배경 점)은 버림
    m = a > 0.3
    lab, n = ndi.label(m)
    sz = ndi.sum(m, lab, range(1, n + 1))
    keep = np.isin(lab, [i + 1 for i in range(n) if sz[i] >= 6])
    a = np.where(keep, a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 128
    h = k.shape[0]
    band = k[int(h * 0.45):int(h * 0.85)]
    cx = np.where(band)[1].mean()   # 몸통 가운데 (꼬리·불씨는 빼고 몸 높이 띠만)
    return rgba, cx


def build(elem):
    scale, frames = SPIRITS[elem]
    pieces = []
    for src, name, xr, cuts, alpha, *opt in frames:
        rgba, cx = load(elem, src, xr, cuts, glow='glow' in opt, allwhite='allwhite' in opt)
        p = shrink(rgba, scale)
        if alpha < 1: p[..., 3] = (p[..., 3] * alpha).round().astype(np.uint8)
        pieces.append((name, p, cx * scale))
        print(f'{name}: {rgba.shape[1]}x{rgba.shape[0]} -> {p.shape[1]}x{p.shape[0]}  cx {cx:.0f}')
    L = max(int(np.ceil(c)) for _, _, c in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 3
    H = max(p.shape[0] for _, p, _ in pieces) + 4
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = H - 2 - p.shape[0]
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(f'assets/sprites/monster/{elem}_spirit.webp', 'WEBP', lossless=True)
    print(f'{elem}_spirit cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)} idleH={pieces[0][1].shape[0]}')


if __name__ == '__main__':
    for e in (sys.argv[1:] or list(SPIRITS)):
        build(e)

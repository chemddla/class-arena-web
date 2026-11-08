# 전사 시크릿 레어 1 [엑스칼리버] 시전 그림 → assets/sprites/fx/warrior_excalibur_cast_sr1.webp (4칸, 기본 외형과 같은 순서)
# 사용: python tools/warrior_excal_sr1_build.py
# 샘플 (assets/sprites/fx/samples/): warrior_excal_sr1_white_src.png (1024×268) · warrior_excal_sr1_black_src.png (1024×254, 참고용)
#   두 장이 따로 그려져 미세하게 달라서(칸마다 배율·위치 어긋남, 맞춰도 색 차이 큼) 기본 외형처럼 두 배경 비교는 못 씀 → 흰 샘플만 씀
# 칸: 0 낮게 웅크려 기를 모음 (붉은 불꽃) · 1 일어서며 불꽃·금빛 번개가 감쌈 · 2 뛰어올라 검을 치켜듦 · 3 내려베기 (금빛 빛기둥·돌조각)
# 배경 제거: 가장자리에서 이어진 흰 곳 = 배경. 나머지는 밝기로 불투명도 (진한 곳 = 불투명, 연한 빛 번짐 = 반투명, 색은 흰 바탕을 뺀 값)
#   색 테두리 안에 갇힌 흰 곳: 검정 샘플의 같은 자리(칸마다 맞춘 배율·위치 BLACK_FIT)가 밝으면 빛의 심 → 거의 불투명한 흰빛,
#   어두우면 불꽃 사이로 보이는 배경 → 지움
# 크기: 시트(warrior_sr1)와 같은 배율 0.5 (대기 샘플과 얼굴 크기가 같음)
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

D = 'assets/sprites/fx/samples/warrior_excal_sr1_'
OUT = 'assets/sprites/fx/warrior_excalibur_cast_sr1.webp'
SC = 0.5
T = 110        # 이 값만큼 흰색에서 멀어지면 불투명
TEXT = [(0, 330, 0, 90), (0, 14, 0, 268)]   # 지울 상자 (x0, x1, y0, y1): 글자 · 왼쪽 테두리 줄
GROUND = None  # 서 있는 칸(1) 발끝 줄 — 자동
# 흰 샘플 x 범위 → 검정 샘플 좌표 = s·(x, y) + (ox, oy)  (몸 색 차이가 가장 작은 값으로 찾음)
BLACK_FIT = [((0, 250), 0.968, 4.0, -2.5), ((250, 480), 0.968, 5.0, -2.5), ((480, 705), 0.972, 3.0, -3.0), ((705, 1024), 0.992, 5.0, -6.0)]


def soft_shrink(rgba, sc):
    h, w = rgba.shape[:2]
    pm = rgba.astype(float); pm[..., :3] *= pm[..., 3:] / 255
    a = np.array(Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * sc)), max(1, round(h * sc))), Image.LANCZOS)).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    a[..., 3:] = np.where(al > 215, 255, np.where(al < 14, 0, al))
    return a.clip(0, 255).astype(np.uint8)


def main():
    W = np.array(Image.open(f'{D}white_src.png').convert('RGB')).astype(float)
    for x0, x1, y0, y1 in TEXT: W[y0:y1, x0:x1] = 255
    mn = W.min(axis=2)
    white = (mn > 238) & (W.max(axis=2) - mn < 14)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    a = np.clip((255 - mn) / T, 0, 1)
    B = np.array(Image.open(f'{D}black_src.png').convert('RGB')).astype(float).mean(axis=2)
    hl, hn = ndi.label(white & ~bg)
    core = np.zeros(hn + 1, bool)
    for j, sl in enumerate(ndi.find_objects(hl), 1):
        ys, xs = np.where(hl[sl] == j); ys = ys + sl[0].start; xs = xs + sl[1].start
        cx = xs.mean()
        _, sc, ox, oy = next(f for f in BLACK_FIT if f[0][0] <= cx < f[0][1])
        bx = np.clip((sc * xs + ox).round().astype(int), 0, B.shape[1] - 1)
        by = np.clip((sc * ys + oy).round().astype(int), 0, B.shape[0] - 1)
        core[j] = B[by, bx].mean() > 110
    enclosed = white & ~bg
    bg = bg | (enclosed & ~core[hl])
    white = white & ~bg
    a = np.where(white, 0.9, a)          # 빛의 심
    a = np.where(bg, 0, a)
    al = np.maximum(a, 1e-3)[..., None]
    col = np.clip((W - 255 * (1 - al)) / al, 0, 255)
    col = np.where((white & ~bg)[..., None], W, col)
    a = np.where(a < 0.06, 0, a)
    rgba = np.dstack([col, a * 255])

    # 칸 나누기: 큰 덩어리 넷 (불투명한 몸), 나머지 조각은 가장 가까운 덩어리 칸으로
    solid = a > 0.95
    lab, n = ndi.label(solid, structure=np.ones((3, 3)))
    sz = ndi.sum(solid, lab, range(1, n + 1))
    objs = ndi.find_objects(lab)
    big = sorted(np.argsort(-sz)[:4] + 1, key=lambda j: objs[j - 1][1].start)
    dist = [ndi.distance_transform_edt(lab != j) for j in big]
    owner = np.argmin(np.stack(dist), axis=0)
    near = np.min(np.stack(dist), axis=0) < 40

    ground = GROUND
    if ground is None:
        ys = np.where((owner == 1) & solid & (lab == big[1]))[0]
        ground = ys.max()
    print('바닥 줄', ground)
    cells = []
    for i in range(4):
        keep = (owner == i) & near & (a > 0)
        xs = np.where(keep.any(axis=0))[0]
        x0, x1 = xs.min(), xs.max() + 1
        c = rgba[:, x0:x1].copy()
        c[..., 3] = np.where(keep[:, x0:x1], c[..., 3], 0)
        k = (lab == big[i])[:, x0:x1]
        if i == 2:   # 공중 칸: 몸 덩어리 가운데
            foot = np.where(k)[1].mean()
        else:
            foot = np.where(k[ground - 10:ground + 1].any(axis=0))[0].mean()
        cells.append((c, foot))
        print(f'칸 {i}: x {x0}~{x1}  발 x {foot + x0:.0f}')
    pieces = []
    for c, foot in cells:
        ys, xs = np.where(c[..., 3] > 0)
        y0, x0 = ys.min(), xs.min()
        p = soft_shrink(c[y0:ys.max() + 1, x0:xs.max() + 1], SC)
        pieces.append((p, (foot - x0) * SC, (ground - y0) * SC))
    L = max(int(np.ceil(fx)) for _, fx, _ in pieces) + 2
    R = max(int(np.ceil(p.shape[1] - fx)) for p, fx, _ in pieces) + 2
    U = max(int(np.ceil(fy)) for _, _, fy in pieces) + 2
    Dn = max(int(np.ceil(p.shape[0] - fy)) for p, _, fy in pieces) + 2
    cw, ch = L + R, U + Dn
    sheet = np.zeros((ch, cw * len(pieces), 4), np.uint8)
    for i, (p, fx, fy) in enumerate(pieces):
        x, y = i * cw + L - int(round(fx)), U - int(round(fy))
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'warrior_excalibur_cast_sr1 cellW={cw} cellH={ch} anchorX={L} anchorY={U} count={len(pieces)}')


if __name__ == '__main__':
    main()

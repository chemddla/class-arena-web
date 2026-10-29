# 블리자드 시전 눈꽃 3장(흰 배경 도트 그림 한 줄)을 blizzard_cast_fx.webp 끝에 이어 붙임
# 사용: python tools/blizzard_snow_build.py <3장 png>   (왼쪽부터 빛나는 눈꽃 · 광륜 터짐 · 주변 눈꽃이 흩어진 눈꽃)
#  - 가운데 그림(광륜)은 위아래가 잘려 있어서, 가운데 눈꽃을 뺀 바깥 빛줄기·고리를 90도 돌린 복사본으로 잘린 쪽을 채움
#  - 작은 눈꽃 조각(mini)은 세 번째 그림의 왼쪽 위 작은 눈꽃을 떼어 냄 (모여드는 눈꽃용)
import sys, numpy as np
from PIL import Image

OUT = 'assets/sprites/fx/blizzard_cast_fx.webp'


def unblend(rgb):
    a = ((255 - rgb.min(axis=2)) / 140).clip(0, 1)
    a = np.where(a < 0.05, 0, a)
    out = np.where(a[..., None] > 0, (rgb - 255 * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0).clip(0, 255)
    # 옅은(흰색에 가까운) 빛 번짐은 색 계산이 불안정해서 어둡게 나오므로, 불투명도가 낮을수록 밝은 하늘색 쪽으로 보정
    w = np.clip(a / 0.55, 0, 1)[..., None]
    return out * w + np.array([150.0, 225.0, 255.0]) * (1 - w), a


def trim(c, a):
    ys, xs = np.where(a > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return c[y0:y1, x0:x1], a[y0:y1, x0:x1]


def to_px(c, a):  # 색·불투명도 → RGBA (색은 불투명도로 나눈 상태 그대로)
    return np.dstack([c, a * 255]).clip(0, 255).astype(np.uint8)


def main(path, cuts=(165, 330)):
    rgb = np.array(Image.open(path).convert('RGB')).astype(float)
    c, a = unblend(rgb)
    H, W = a.shape
    edges = [0, *cuts, W]
    parts = [(c[:, edges[i]:edges[i + 1]], a[:, edges[i]:edges[i + 1]]) for i in range(3)]
    A, B, C = [trim(*p) for p in parts]
    # 가운데 그림 복구: 위아래로 P칸 늘리고, 90도 돌린 복사본(바깥만)으로 빈 곳을 채움. 잘린 가장자리는 부드럽게 이어 붙임
    bc, ba = B
    h, w = ba.shape
    P = 22
    size = max(w, h + 2 * P)
    cc = np.zeros((size, size, 3)); aa = np.zeros((size, size))
    oy, ox = (size - h) // 2, (size - w) // 2
    cc[oy:oy + h, ox:ox + w] = bc; aa[oy:oy + h, ox:ox + w] = ba
    ctr_y, ctr_x = oy + h / 2, ox + w / 2
    rc = np.rot90(cc, 1, axes=(0, 1)); ra = np.rot90(aa, 1, axes=(0, 1))   # 정사각형이라 가운데가 그대로
    # 돌린 복사본은 가운데 눈꽃(반지름 52 안)을 빼고, 위아래 잘린 쪽으로 갈수록 진하게
    yy, xx = np.mgrid[0:size, 0:size]
    cy = cx = (size - 1) / 2
    dist = np.hypot(yy - cy, xx - cx)
    cut_dist = np.abs(yy - cy) - (h / 2 - 10)              # 잘린 선 10칸 안쪽부터 서서히
    ramp = np.clip(cut_dist / 12, 0, 1) * np.clip((dist - 50) / 8, 0, 1)
    ra = ra * ramp
    # 원본은 잘린 선 가까이에서 서서히 옅어짐
    edge = np.clip((h / 2 - np.abs(yy - cy)) / 10, 0, 1)
    edge = np.where(np.abs(yy - cy) <= h / 2, edge, 0)
    fa = aa * edge
    # 합성: 돌린 복사본 위에 원본 (알파 합성, 색은 알파 가중)
    out_a = fa + ra * (1 - fa)
    out_c = np.where(out_a[..., None] > 0, (cc * fa[..., None] + rc * (ra * (1 - fa))[..., None]) / np.maximum(out_a[..., None], 1e-3), 0)
    B2 = trim(out_c, out_a)
    # 작은 눈꽃: 세 번째 그림 왼쪽 위 (그림 안 좌표로 찾아 자름)
    cc3, ca3 = parts[2]
    sub = ca3[:45, :45]
    ys, xs = np.where(sub > 0.15)
    mx0, my0 = xs.min(), ys.min()
    mini = (cc3[my0:my0 + 16, mx0:mx0 + 16], ca3[my0:my0 + 16, mx0:mx0 + 16])
    cells = [('snowA', A), ('snowB', B2), ('snowC', C), ('mini', trim(*mini))]
    base = Image.open(OUT).convert('RGBA')
    Hh = max(base.height, max(p[1].shape[0] for _, p in cells))
    Ww = base.width + sum(p[1].shape[1] + 2 for _, p in cells) + 2
    sheet = Image.new('RGBA', (Ww, Hh), (0, 0, 0, 0))
    sheet.paste(base, (0, 0))
    x, table = base.width + 2, []
    for name, (pc, pa) in cells:
        px = to_px(np.where(pa[..., None] > 0, pc, 0), pa)
        sheet.paste(Image.fromarray(px, 'RGBA'), (x, 0))
        table.append(f"{name}: [{x},0,{px.shape[1]},{px.shape[0]}]")
        x += px.shape[1] + 2
    sheet.save(OUT, 'WEBP', lossless=True)
    print(', '.join(table), base.width)


if __name__ == '__main__':
    main(sys.argv[1])

# 주술사 시크릿 레어(역병 의사) 히든 [파멸의 의식] 적 표식·폭발 샘플(회색·남색 배경) → assets/sprites/fx/curse_sr1_ruin_mark_fx.webp
# 사용: python tools/curse_sr1_ruin_mark_build.py   (샘플 assets/sprites/fx/samples/curse_sr1_ruin_*_src.*)
#   mark0 = curse_sr1_ruin_mark0_src.png   걸린 적 머리 위 보라 불꽃 해골 (의식 처음)
#   mark1 = curse_sr1_ruin_mark1_src.webp  붉은 불꽃 해골 (터질 때가 가까워질수록 mark0에서 이 그림으로 바뀜)
#   bolt  = curse_sr1_ruin_bolt_src.png    터질 때 붉은 번개 소용돌이 속 사신 (기준점 = 바닥 소용돌이 가운데)
# 두 해골은 겹쳐서 서서히 바꾸므로, 두 눈 사이 거리·가운데가 같아지게 배율·기준점을 맞춤 (기준점 = mark0 그림 가운데)
# 샘플 정리:
#   - 배경이 단색(mark1은 위아래로 어두워지는 그러데이션)이라 테두리에서 배경색과 비슷한 곳을 채워 나가 지움
#   - mark1 오른쪽 아래 ✦ 워터마크 지움
#   - bolt는 소용돌이 고리 안쪽에 갇힌 배경이 많아서 배경색과 비슷한 곳을 모두 지움. 왼쪽 끝 세로 테두리 선·작은 얼룩도 지움
# 프레임 [x, y, w, h, 기준점x, 기준점y]
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

D = 'assets/sprites/fx/samples/curse_sr1_ruin_'
OUT = 'assets/sprites/fx/curse_sr1_ruin_mark_fx.webp'
MARK_SCALE = 0.36                          # mark0 샘플 → 저장 크기 (게임에서는 폭 기준으로 다시 줄여 그림)
EYES = {'mark0': ((147, 251), (222, 251)), 'mark1': ((384, 659), (581, 659))}  # 샘플의 두 눈 가운데
BOLT_SCALE = 0.8
BOLT_FOOT = (148, 252)                     # 사신 샘플의 바닥 소용돌이 가운데


def key(path, tol, erase=(), enclosed=False):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    h, w = im.shape[:2]
    # 줄마다 왼쪽·오른쪽 끝 색을 배경으로 보고 가로로 이어 그러데이션 배경을 만듦
    left, right = np.median(im[:, :12], axis=1), np.median(im[:, -12:], axis=1)
    t = np.linspace(0, 1, w)[None, :, None]
    bg = left[:, None] * (1 - t) + right[:, None] * t
    near = np.abs(im - bg).max(-1) < tol
    lab, _ = ndi.label(near)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    a = (~np.isin(lab, border[border > 0])).astype(float)
    if enclosed: a[near] = 0  # 고리·번개에 둘러싸여 테두리와 이어지지 않은 안쪽 배경도 지움
    for x0, y0, x1, y1 in erase: a[y0:y1, x0:x1] = 0
    # 배경과 섞인 가장자리 1px은 지움, 작은 압축 티끌도 지움
    a[ndi.binary_dilation(a == 0, iterations=1) & (np.abs(im - bg).max(-1) < tol * 2)] = 0
    m = a > 0
    lab, n = ndi.label(m)
    areas = ndi.sum(m, lab, range(1, n + 1))
    a = np.where(np.isin(lab, 1 + np.where(areas >= 8)[0]), a, 0)
    return np.dstack([im, a * 255])


def shrink(rgba, sc):
    h, w = rgba.shape[:2]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    sm = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * sc)), max(1, round(h * sc))), Image.LANCZOS)
    a = np.array(sm).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    a[..., 3:] = np.where(al > 110, 255, np.where(al > 40, al * 1.6, 0))  # 도트 느낌: 가장자리를 딱딱하게
    return a.clip(0, 255).astype(np.uint8)


def trim(p):
    ys, xs = np.where(p[..., 3] > 0)
    return p[ys.min():ys.max() + 1, xs.min():xs.max() + 1], xs.min(), ys.min()


def main():
    eye = lambda k: (np.mean([e[0] for e in EYES[k]]), EYES[k][0][1], EYES[k][1][0] - EYES[k][0][0])
    e0x, e0y, d0 = eye('mark0')
    e1x, e1y, d1 = eye('mark1')
    s0, s1 = MARK_SCALE, MARK_SCALE * d0 / d1
    m0, x0, y0 = trim(shrink(key(D + 'mark0_src.png', 16), s0))
    m1, x1, y1 = trim(shrink(key(D + 'mark1_src.webp', 16, [(860, 870, 930, 940)]), s1))
    a0 = (m0.shape[1] / 2, m0.shape[0] / 2)                          # mark0 기준점 = 그림 가운데
    off = (a0[0] - (e0x * s0 - x0), a0[1] - (e0y * s0 - y0))         # 두 눈 가운데에서 기준점까지
    a1 = (e1x * s1 - x1 + off[0], e1y * s1 - y1 + off[1])
    b, bx, by = trim(shrink(key(D + 'bolt_src.png', 14, [(0, 0, 8, 292), (0, 200, 30, 240)], enclosed=True), BOLT_SCALE))
    tiles = [('mark0', m0, a0), ('mark1', m1, a1), ('bolt', b, (BOLT_FOOT[0] * BOLT_SCALE - bx, BOLT_FOOT[1] * BOLT_SCALE - by))]
    W = sum(t.shape[1] + 2 for _, t, _ in tiles); H = max(t.shape[0] for _, t, _ in tiles)
    atlas = np.zeros((H, W, 4), np.uint8); x = 0; frames = []
    for nm, t, (ax, ay) in tiles:
        atlas[:t.shape[0], x:x + t.shape[1]] = t
        frames.append(f'{nm}: [[{x},0,{t.shape[1]},{t.shape[0]},{round(ax)},{round(ay)}]]')
        x += t.shape[1] + 2
    Image.fromarray(atlas, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('{ ' + ', '.join(frames) + ' }')


if __name__ == '__main__':
    main()

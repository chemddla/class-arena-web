# 소환사 불 정령 샘플(작은 불꽃 아이, 흰 배경) → 몬스터 시트 assets/sprites/monster/fire_spirit.webp
# 사용: python tools/fire_spirit_build.py   (샘플은 assets/sprites/fx/samples/fire_spirit_*_src.png)
# 칸 순서: 0 대기 · 1~3 걷기 · 4 기본 공격 (불꽃 주먹) · 5 피격 · 6 쓰러짐 (눈 질끈) · 7 불길에 휩싸임 · 8~9 폭발 (불기둥 → 흩어지는 불꽃·연기)
#   - 6~9는 정령이 사라질 때(쓰러짐·돌려보냄·해방) 그 자리에서 이펙트로 차례로 그림 (죽은 정령은 유닛으로 그리지 않음)
# 크기: 샘플들이 같은 크기로 그려져 있어서 모두 같은 배율 SCALE (대기 샘플 키 192 → 약 115)
# 샘플 정리:
#   - 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움 (눈의 흰 하이라이트는 남김)
#   - 머리 위에 떠 있는 불씨는 몸과 떨어진 덩어리라도 칸 안에 있으면 그대로 둠
#   - 공격 샘플 왼쪽 끝 6줄은 옆 칸 그림 조각 → 지움
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/fire_spirit_'
OUT = 'assets/sprites/monster/fire_spirit.webp'
SCALE = 0.6

# (샘플, 칸 이름, 샘플 안 x 범위)
FRAMES = [
    ('idle', 'idle', (0, 159)),
    ('walk', 'walk0', (0, 160)), ('walk', 'walk1', (160, 330)), ('walk', 'walk2', (330, 500)),
    ('atk', 'atk', (6, 202)),
    ('hurt', 'hurt', (0, 173)),
    ('down', 'down0', (0, 200)), ('down', 'down1', (200, 455)),
    ('boom1', 'boom1', (0, 236)), ('boom2', 'boom2', (0, 204)),
]


def load(name, xr):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)[:, xr[0]:xr[1]]
    white = (im.min(axis=2) > 222) & (im.max(axis=2) - im.min(axis=2) < 22)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)
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


def main():
    pieces = []
    for src, name, xr in FRAMES:
        rgba, cx = load(src, xr)
        p = shrink(rgba, SCALE)
        pieces.append((name, p, cx * SCALE))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} → {p.shape[1]}x{p.shape[0]}  가운데 {cx:.0f}')
    L = max(int(np.ceil(c)) for _, _, c in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 3
    H = max(p.shape[0] for _, p, _ in pieces) + 4
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = H - 2 - p.shape[0]
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'fire_spirit cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)} idleH={pieces[0][1].shape[0]}')


if __name__ == '__main__':
    main()

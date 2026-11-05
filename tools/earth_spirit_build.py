# 소환사 대지 정령 샘플(새싹 달린 작은 바위 아이, 흰 배경) → 몬스터 시트 assets/sprites/monster/earth_spirit.webp
# 사용: python tools/earth_spirit_build.py   (샘플은 assets/sprites/fx/samples/earth_spirit_*_src.png)
# 칸 순서: 0 대기 · 1~3 걷기 · 4 기본 공격 (바위 주먹) · 5 피격 (튕겨 나감)
#          6~8 무너짐 (눈 감고 버팀 → 무너져 내림 → 흙더미) · 9 도발 시전 (움찔 모으기) · 10 도발 발동 (외치기)
#   - 6~8은 정령이 사라질 때(쓰러짐·돌려보냄·해방) 그 자리에서 이펙트로 차례로 그림 (죽은 정령은 유닛으로 그리지 않음)
#   - 9~10은 나올 때 주변 적을 도발하는 순간에 재생
# 크기: 샘플들이 같은 크기로 그려져 있어서 모두 같은 배율 SCALE
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
from fire_spirit_build import load as _load
import fire_spirit_build

fire_spirit_build.D = 'assets/sprites/fx/samples/earth_spirit_'
OUT = 'assets/sprites/monster/earth_spirit.webp'
SCALE = 0.62

# (샘플, 칸 이름, 샘플 안 x 범위, y 범위)
FRAMES = [
    ('idle', 'idle', (0, 132), None),
    ('walk', 'walk0', (0, 165), None), ('walk', 'walk1', (165, 345), None), ('walk', 'walk2', (345, 511), None),
    ('atk', 'atk', (0, 168), None),
    ('down', 'hurt', (0, 547), (0, 175)),
    ('down', 'down0', (0, 180), (175, 347)), ('down', 'down1', (180, 354), (175, 347)), ('down', 'down2', (354, 547), (175, 347)),
    ('taunt1', 'taunt1', (0, 159), None), ('taunt2', 'taunt2', (0, 171), None),
]


def load(name, xr, yr):
    if yr is None:
        return _load(name, xr)
    # 세로로 나뉜 샘플(피격 위 · 무너짐 아래)은 잘라 둔 임시 파일로
    im = Image.open(f'{fire_spirit_build.D}{name}_src.png').convert('RGB').crop((0, yr[0], 10 ** 5, yr[1]))
    tmp = f'{fire_spirit_build.D}_tmp_src.png'
    im.save(tmp)
    try:
        return _load('_tmp', xr)
    finally:
        os.remove(tmp)


def clean(rgba):
    # 덩굴 고리 안에 갇힌 흰 배경(가장자리와 이어지지 않음)도 지움. 눈 하이라이트처럼 작은 흰 점은 남김
    im = rgba[..., :3]
    white = (rgba[..., 3] > 0) & (im.min(axis=2) > 185) & (im.max(axis=2) - im.min(axis=2) < 28)
    lab, n = ndi.label(white)
    sz = ndi.sum(white, lab, range(1, n + 1))
    big = np.isin(lab, [i + 1 for i in range(n) if sz[i] >= 14])
    big = ndi.binary_dilation(big, iterations=1) & (im.min(axis=2) > 160)
    rgba = rgba.copy()
    rgba[big, 3] = 0
    # 가운데: 진한 갈색 몸통(초록 잎·연한 흔들림 선·느낌표 빼고)의 가장 큰 덩어리
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    body = (rgba[..., 3] > 128) & (im.max(axis=2) < 150) & ~(g > r + 8)
    lab, n = ndi.label(body)
    if n:
        sz = ndi.sum(body, lab, range(1, n + 1))
        body = lab == (int(np.argmax(sz)) + 1)
    return rgba, np.where(body)[1].mean()


def main():
    pieces = []
    for src, name, xr, yr in FRAMES:
        rgba, _ = load(src, xr, yr)
        rgba, cx = clean(rgba)
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
    print(f'earth_spirit cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)} idleH={pieces[0][1].shape[0]}')


if __name__ == '__main__':
    main()

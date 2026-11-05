# 정령사 히든 정령왕 샘플(불꽃 머리 흑기사, 흰 배경) → 몬스터 시트 assets/sprites/monster/spirit_king.webp
#                                                    + 강림 이펙트 assets/sprites/fx/spirit_king_burst.webp
# 사용: python tools/spirit_king_build.py   (샘플은 assets/sprites/fx/samples/spirit_king_*_src.png · burst_src.webp)
# 칸 순서: 0 대기 · 1~3 걷기 · 4 공격 1 (검 치켜들기) · 5 공격 2 (불꽃 베기) · 6 강림 (검을 땅에 꽂음)
#          7 피격 · 8~9 쓰러짐 (원소로 갈라짐 → 흩어지는 원소 조각, spirit_pop 이펙트가 그림)
# 강림 이펙트: 다섯 원소가 땅에서 터져 오르는 그림 한 장 (기준점 = 바닥 가운데)
# 샘플 정리: 흰 배경은 가장자리와 이어진 것만 지움. 쓰러짐 샘플 아래 가로줄은 잘라 냄.
#   칸 가운데 = 진한 갑옷 덩어리의 가운데 (검·불꽃·방패가 옆으로 뻗어도 몸이 기준점에 오게)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
import fire_spirit_build as fsb

fsb.D = 'assets/sprites/fx/samples/spirit_king_'
OUT = 'assets/sprites/monster/spirit_king.webp'
OUT_FX = 'assets/sprites/fx/spirit_king_burst.webp'
SCALE = 0.85
BURST_W = 360

# (샘플, 칸 이름, (x0, x1), (y0, y1) 또는 None)
FRAMES = [
    ('idle', 'idle', (5, 135), None),
    ('walk', 'walk0', (0, 132), None), ('walk', 'walk1', (132, 262), None), ('walk', 'walk2', (262, 407), None),
    ('atk1', 'atk1', (0, 205), None), ('atk2', 'atk2', (0, 201), None),
    ('descend', 'descend', (0, 228), None),
    ('hurt', 'hurt', (0, 151), None),
    ('down', 'down0', (0, 205), (0, 150)), ('down', 'down1', (205, 424), (0, 150)),
]


def load(name, xr, yr):
    if yr is None:
        rgba, cx = fsb.load(name, xr)
    else:
        im = Image.open(f'{fsb.D}{name}_src.png').convert('RGB').crop((0, yr[0], 10 ** 5, yr[1]))
        tmp = f'{fsb.D}_tmp_src.png'
        im.save(tmp)
        try:
            rgba, cx = fsb.load('_tmp', xr)
        finally:
            os.remove(tmp)
    # 진한 갑옷 덩어리 가운데 (없으면 원래 값: 쓰러짐 2는 조각만 남음)
    im = rgba[..., :3]
    body = (rgba[..., 3] > 128) & (im.max(axis=2) < 95)
    lab, n = ndi.label(body)
    if n:
        sz = ndi.sum(body, lab, range(1, n + 1))
        if sz.max() > 300:
            cx = np.where(lab == int(np.argmax(sz)) + 1)[1].mean()
    return rgba, cx


def main():
    pieces = []
    for src, name, xr, yr in FRAMES:
        rgba, cx = load(src, xr, yr)
        p = shrink(rgba, SCALE)
        pieces.append((name, p, cx * SCALE))
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
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'spirit_king cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)} idleH={pieces[0][1].shape[0]}')

    # 강림 이펙트: 원본(1024 폭)을 흰 배경 지우고 BURST_W 폭으로
    src = Image.open(f'{fsb.D}burst_src.webp').convert('RGB')
    tmp = f'{fsb.D}_tmp_src.png'
    src.save(tmp)
    try:
        b, _ = fsb.load('_tmp', (0, src.size[0]))
    finally:
        os.remove(tmp)
    bp = shrink(b, BURST_W / b.shape[1])
    Image.fromarray(bp, 'RGBA').save(OUT_FX, 'WEBP', quality=90)
    print(f'burst {bp.shape[1]}x{bp.shape[0]}')


if __name__ == '__main__':
    main()

# 정령사 번개 정령 샘플(삐죽한 번개 아이, 흰 배경) → 몬스터 시트 assets/sprites/monster/storm_spirit.webp
#                                                  + 기본 공격 번개 구슬 assets/sprites/fx/storm_spirit_fx.webp
# 사용: python tools/storm_spirit_build.py   (샘플은 assets/sprites/fx/samples/storm_spirit_*_src.png)
# 칸 순서: 0 대기 · 1~2 이동 · 3 기본 공격 (손 내밀기, 구슬은 투사체로 따로) · 4~6 연쇄 번개 (모으기 → 뿜기 → 굵은 번개)
#          7 피격 · 8~9 쓰러짐 (놀람 → 흩어지는 스파크)
#   - 8~9는 정령이 사라질 때(쓰러짐·돌려보냄·해방) 그 자리에서 spirit_pop 이펙트로 그림
# 샘플 정리: 아래쪽 한글 라벨 줄은 잘라 냄. 공격 샘플 오른쪽 구슬은 몸에서 떼어 투사체 그림으로
# 크기: 샘플들이 같은 크기로 그려져 있어서 모두 같은 배율 SCALE
import os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
import fire_spirit_build as fsb

fsb.D = 'assets/sprites/fx/samples/storm_spirit_'
OUT = 'assets/sprites/monster/storm_spirit.webp'
OUT_FX = 'assets/sprites/fx/storm_spirit_fx.webp'
SCALE = 0.9
BODY_W = 103   # 대기 칸 몸 폭 (샘플 px): 번개를 뿜는 칸은 왼쪽 끝 + 반폭을 가운데로

# (샘플, 칸 이름, (x0, x1), (y0, y1) 또는 None, 가운데를 몸 왼쪽 끝 기준으로 잡을지)
FRAMES = [
    ('idle', 'idle', (0, 120), (0, 130), False),
    ('walk1', 'walk1', (0, 129), None, False), ('walk2', 'walk2', (0, 136), None, False),
    ('atk', 'atk', (0, 98), None, False),
    ('chain', 'chain0', (0, 182), (0, 138), True), ('chain', 'chain1', (182, 358), (0, 138), True), ('chain', 'chain2', (358, 541), (0, 138), True),
    ('hurt', 'hurt', (0, 148), (0, 133), False),
    ('down', 'down0', (0, 150), (0, 136), False), ('down', 'down1', (150, 293), (0, 136), False),
]


def load(name, xr, yr):
    if yr is None:
        return fsb.load(name, xr)
    im = Image.open(f'{fsb.D}{name}_src.png').convert('RGB').crop((0, yr[0], 10 ** 5, yr[1]))
    tmp = f'{fsb.D}_tmp_src.png'
    im.save(tmp)
    try:
        return fsb.load('_tmp', xr)
    finally:
        os.remove(tmp)


def main():
    pieces = []
    for src, name, xr, yr, left in FRAMES:
        rgba, cx = load(src, xr, yr)
        if left:
            cx = BODY_W / 2
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
    print(f'storm_spirit cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)} idleH={pieces[0][1].shape[0]}')

    # 번개 구슬 (기준점 = 앞 끝 = 오른쪽 끝, 세로 가운데)
    orb, _ = fsb.load('atk', (98, 146))
    o = shrink(orb, SCALE)
    Image.fromarray(o, 'RGBA').save(OUT_FX, 'WEBP', lossless=True)
    print(f'orb: [[0,0,{o.shape[1]},{o.shape[0]},{o.shape[1] - 1},{o.shape[0] / 2}]]')


if __name__ == '__main__':
    main()

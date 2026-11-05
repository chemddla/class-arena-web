# 소환사 시크릿 레어 1 (은발·보라 눈·흰 금빛 로브·보라 망토·청록 마법서) 샘플 → assets/sprites/merc/summoner_sr1.webp
# 사용: python tools/summoner_sr1_build.py
# 샘플 (흰 배경, assets/sprites/fx/samples/summoner_sr1_<이름>_src.png) — 모두 같은 해상도로 그려 와서 배율 하나로 줄임
#   idle (152×172): 위에 "1. 대기" 글씨·회색 둥근 카드 테두리 → 글씨 상자는 지움
#   walk1~3, atk, cast, release, hurt, down1, down2: 시트에서 잘라 와서 가장자리에 옆 칸 그림·글씨 조각이 걸쳐 있음
#     → 가장자리에 닿은 작은 덩어리는 버림 (가장 큰 덩어리 = 몸은 남김). 시전·발동 칸의 반짝이(가장자리에 안 닿음)는 남김
#   down2 (누운 모습)는 down1(뒤로 넘어짐, 머리가 왼쪽)과 머리 방향이 반대라 좌우로 뒤집음
# 칸 순서 = 소환사 0번과 같음: 0 대기 · 1~4 걷기 · 5 피격 · 6~8 쓰러짐 · 9 기본 공격 · 10 소환 시전 · 11 소환 발동
#   걷기 샘플은 3장이라 4칸 = 걷기1 · 걷기2 · 걷기3 · 걷기2. 쓰러짐 샘플은 2장이라 3칸 = 피격 · 쓰러짐1 · 쓰러짐2
# 은발이 흰 배경과 비슷한 색이라, 배경은 가장자리에서 이어진 흰 픽셀만 지움 (머리카락은 검은 윤곽 안이라 남음)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/summoner_sr1_'
OUT = 'assets/sprites/merc/summoner_sr1.webp'
TARGET_H = 88   # 대기 자세 머리 꼭대기~발 → 소환사 0번과 같은 키
CUT = {'idle': [(0, 0, 90, 30)]}   # 지울 상자 (x0, y0, x1, y1): 대기 샘플 "1. 대기" 글씨
FLIP = {'down2'}
FOOTX = {}   # 칸 이름 → 발(기준점) 가운데 (샘플 px). 없으면 아래 8% 줄의 가운데

# (칸 이름, 샘플)
FRAMES = [('idle', 'idle'), ('walk0', 'walk1'), ('walk1', 'walk2'), ('walk2', 'walk3'), ('walk3', 'walk2'),
          ('hurt', 'hurt'), ('down0', 'hurt'), ('down1', 'down1'), ('down2', 'down2'),
          ('atk', 'atk'), ('cast', 'cast'), ('release', 'release')]


def load(name):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    if name in FLIP: im = im[:, ::-1]
    for x0, y0, x1, y1 in CUT.get(name, ()): im[y0:y1, x0:x1] = 255
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), constant_values=255)
    white = (im.min(axis=2) > 222) & (im.max(axis=2) - im.min(axis=2) < 16)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    m = a > 0.3
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    sz = ndi.sum(m, lab, range(1, n + 1))
    body = 1 + int(np.argmax(sz))
    H, W = m.shape
    keep = np.zeros(n + 1, bool); keep[body] = True
    for i in range(1, n + 1):
        if i == body or sz[i - 1] < 4: continue
        ys, xs = np.where(lab == i)
        touches = ys.min() <= 3 or xs.min() <= 3 or ys.max() >= H - 4 or xs.max() >= W - 4
        keep[i] = not touches   # 가장자리에 걸친 옆 칸 조각·글씨는 버리고, 떨어진 반짝이·책은 남김
    a = np.where(keep[lab], a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 0
    bm = (lab == body)[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    rows = np.where(bm.any(axis=1))[0]
    foot = np.where(bm[int(bm.shape[0] * 0.92):].any(axis=0))[0].mean()
    return rgba, foot, rows.max() - rows.min() + 1


def main():
    cache = {}
    for _, src in FRAMES:
        if src not in cache: cache[src] = load(src)
    for s, (r, f, h) in cache.items(): print(f'{s}: {r.shape[1]}x{r.shape[0]} 몸 키 {h}')
    sc = TARGET_H / cache['idle'][2]
    pieces = []
    for name, src in FRAMES:
        rgba, foot, _ = cache[src]
        foot = FOOTX.get(name, foot)
        p = shrink(rgba, sc)
        pieces.append((name, p, foot * sc))
    L = max(int(np.ceil(c)) for _, _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 4
    H = max(p.shape[0] for _, p, _ in pieces) + 5
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = H - 2 - p.shape[0]
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'배율 {sc:.3f}  summoner_sr1 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)}')


if __name__ == '__main__':
    main()

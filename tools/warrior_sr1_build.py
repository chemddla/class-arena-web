# 전사 시크릿 레어 1 (금발·금빛 판금·붉은 목도리와 망토·금빛 대검) 샘플 → assets/sprites/merc/warrior_sr1.webp
# 사용: python tools/warrior_sr1_build.py
# 샘플 (흰 배경, assets/sprites/fx/samples/warrior_sr1_<이름>_src.png, 2026-11-08)
#   idle: 대기 1장 · walk: 걷기 3장 가로 · atk: 칼 치켜듦 + 베기 (옅은 금빛 궤적) · down: 무릎 꿇음 + 엎드림 (칼은 떨어져 있음) · hurt: 피격
#   걷기 샘플만 작게 그려져 있어서(얼굴 넓이로 재면 0.755배) 걷기는 배율을 따로 씀. 나머지는 대기와 같은 배율
# 칸 = 0 대기 · 1~3 걷기 · 4 공격 치켜듦 · 5 공격 베기 · 6 피격 · 7~8 쓰러짐 (무릎 → 엎드림)
#   · 9~10 사자후 (숨을 들이쉼 → 주먹을 쥐고 포효) · 11~12 돌진 (칼을 낮게 겨누고 출발 → 칼을 앞세워 달림, 바람 줄)
#   skill: 2×2 시트 (윗줄 사자후 2장, 아랫줄 돌진 2장). 0.625배로 작게 그려져 있음 (얼굴 넓이)
#   사자후 포효 칸 오른쪽의 크림색 음파는 지움 — 게임이 사자후 고리 이펙트를 따로 그림
#   · 13~15 회전베기 (옆 → 뒷모습 → 앞으로 베기). whirl: 3장 가로, 0.65배로 작게 그려져 있음
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/warrior_sr1_'
OUT = 'assets/sprites/merc/warrior_sr1.webp'
TARGET_H = 81          # 대기 자세 머리털 끝~발 (전사 0번과 같은 키)
IDLE_H = 189 - 27      # 대기 샘플의 머리털 끝(27)~발(189)
SRC_SCALE = {'walk': 1 / 0.755, 'skill': 1 / 0.625, 'whirl': 1 / 0.65}  # 작게 그려진 샘플 (대기 대비 얼굴 넓이)
WAVE_X = 346   # skill 샘플 포효 칸: 이 x부터 밝은 크림·금빛(음파)을 지움

# (칸 이름, 샘플, 자를 범위 (x0, x1[, y0, y1]), 발 가운데 x (샘플 좌표, None = 아래 8% 줄의 가운데))
FRAMES = [
    ('idle',  'idle', (0, 208),   125),
    ('walk0', 'walk', (0, 180),   None),
    ('walk1', 'walk', (180, 354), None),
    ('walk2', 'walk', (354, 519), None),
    ('raise', 'atk',  (0, 250),   140),
    ('swing', 'atk',  (250, 591), 405),
    ('hurt',  'hurt', (0, 214),   145),
    ('kneel', 'down', (0, 290),   150),
    ('lie',   'down', (290, 771), 460),
    ('inhale', 'skill', (40, 200, 0, 119),    110),
    ('roar',   'skill', (220, 505, 0, 119),   318),
    ('cstart', 'skill', (0, 200, 119, 229),   118),
    ('crun',   'skill', (240, 505, 119, 229), 330),
    ('whirl0', 'whirl', (0, 220),   None),
    ('whirl1', 'whirl', (220, 460), None),
    ('whirl2', 'whirl', (460, 718), None),
]


def load(src, xr):
    full = np.array(Image.open(f'{D}{src}_src.png').convert('RGB')).astype(float)
    x0, x1, y0, y1 = (*xr, 0, full.shape[0])[:4]
    full = full[y0:y1].copy()
    if src == 'skill' and y0 == 0:   # 포효 음파 지우기 (주먹은 갈색·검정이라 남음)
        w = full[:, WAVE_X:]
        pale = (w[..., 0] > 185) & (w[..., 1] > 130)
        w[pale] = 255
    im = np.pad(full[:, x0:x1], ((2, 2), (2, 2), (0, 0)), constant_values=255)
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
        touches = xs.min() <= 3 or xs.max() >= W - 4 or ys.min() <= 3 or ys.max() >= H - 4
        keep[i] = not touches   # 옆 그림 조각은 버리고, 떨어진 칼·베기 궤적은 남김
    a = np.where(keep[lab], a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bm = (lab == body)[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    foot = np.where(bm[int(bm.shape[0] * 0.92):].any(axis=0))[0].mean()
    return rgba, foot, x0 + xs.min() - 2


def main():
    sc = TARGET_H / IDLE_H
    pieces = []
    for name, src, xr, fx in FRAMES:
        rgba, foot, ox = load(src, xr)
        if fx is not None: foot = fx - ox
        s = sc * SRC_SCALE.get(src, 1)
        p = shrink(rgba, s)
        pieces.append((name, p, foot * s))
        print(f'{name}: {rgba.shape[1]}x{rgba.shape[0]} → {p.shape[1]}x{p.shape[0]}  발 {foot * s:.1f}')
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
    print(f'배율 {sc:.3f}  warrior_sr1 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)}')


if __name__ == '__main__':
    main()

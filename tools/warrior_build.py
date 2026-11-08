# 전사 기본 외형(warrior_0) 새 샘플 → 캐릭터 시트 assets/sprites/merc/warrior_0.webp
# 갈색 머리·은빛 판금 갑옷·붉은 목도리와 망토·어깨에 멘 대검 (흰 배경 샘플 4장, 2026-11-08)
# 사용: python tools/warrior_build.py
# 샘플 (assets/sprites/fx/samples/):
#   warrior_idle_src.png       대기 1장 (왼쪽 위 '대기 (Idle)' 글자)
#   warrior_walk_src.png       걷기 2장
#   warrior_attack_src.png     일반 공격 2장 (치켜듦 → 베기, 베기 칸의 푸른 궤적은 칼에 붙어 있어 남김, 왼쪽 글자)
#   warrior_hurt_down_src.png  위: 피격 1장 · 아래: 쓰러짐 2장 (넘어짐 → 누움), 왼쪽 글자·세로줄
#   warrior_whirl_src.png      회전베기 3장 (옆 → 뒷모습 → 앞으로 베기, 몸을 감는 푸른 바람 고리)
# 칸 순서: 0 대기 · 1~2 걷기 · 3 공격 치켜듦 · 4 공격 베기 · 5 피격 · 6~7 쓰러짐 · 8~10 회전베기
# 샘플 정리:
#   - 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움 (흰 하이라이트는 검은 외곽선 안쪽이라 남음)
#   - 글자·피격 '!' 표시 = 작은 덩어리라 BOX 안에서 큰 덩어리만 남기면 빠짐
#   - 발밑 회색 그림자는 지움 (게임이 따로 그림): 그림 맨 아래 줄 색에서 시작해 비슷한 무채색 회색으로 이어진 곳만
#   - 누운 쓰러짐(2)은 머리가 오른쪽이라 좌우를 뒤집어 넘어짐(1)처럼 뒤로 넘어간 방향을 맞춤
# 크기: 대기 자세 머리털 끝~발을 TARGET_H로. 샘플 4장은 같은 배율이라 다른 칸도 대기 배율 그대로 (머리털 폭으로 확인만 함)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/warrior_'
OUT = 'assets/sprites/merc/warrior_0.webp'
TARGET_H = 81

# (칸 이름, 샘플, 상자 x0 x1 y0 y1)
FRAMES = [
    ('idle',   'idle',      (0, 192, 0, 195)),
    ('walk1',  'walk',      (0, 167, 0, 171)),
    ('walk2',  'walk',      (167, 334, 0, 171)),
    ('atk1',   'attack',    (100, 380, 0, 178)),
    ('atk2',   'attack',    (390, 638, 0, 178)),
    ('hurt',   'hurt_down', (80, 300, 0, 168)),
    ('down1',  'hurt_down', (140, 380, 168, 337)),
    ('down2',  'hurt_down', (380, 667, 168, 337)),
    ('whirl1', 'whirl',     (0, 155, 0, 183)),
    ('whirl2', 'whirl',     (155, 340, 0, 183)),
    ('whirl3', 'whirl',     (340, 514, 0, 183)),
]
FLIP = {'down2'}


def hair_mask(rgba):
    r, g, b, a = [rgba[..., i].astype(float) for i in range(4)]
    return (a > 200) & (r > g) & (g > b) & (r - b > 30) & (r < 210) & (r > 60)


def load(src, box, flip):
    im = np.array(Image.open(f'{D}{src}_src.png').convert('RGB')).astype(float)
    x0, x1, y0, y1 = box
    im = im[y0:y1, x0:x1]
    if flip: im = im[:, ::-1]
    white = (im.min(axis=2) > 222) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    # 다리 사이·팔과 몸 사이에 갇힌 흰 배경: 가장자리와 안 이어져도 배경색(약 250)에 가깝고 40px 이상이면 배경
    #   (갑옷·칼날 하이라이트는 평균 230~243, 베기 궤적 안쪽은 245라 남음)
    for i in range(1, n + 1):
        if i in edge: continue
        m = lab == i
        if m.sum() >= 40 and im[m].mean() >= 247.5: bg |= m
    # 큰 덩어리만 (글자·'!' 표시 빼기)
    fg = ~bg
    lab, n = ndi.label(ndi.binary_dilation(fg, iterations=2))
    sz = ndi.sum(fg, lab, range(1, n + 1))
    keep = [i + 1 for i in range(n) if sz[i] >= sz.max() * 0.25]
    bg = bg | ~np.isin(lab, keep)
    # 발밑 그림자: 무채색 중간 회색, 맨 아래 줄에서 이어진 것
    grey = ~bg & (((im.max(axis=2) - im.min(axis=2) < 22) & (im.mean(axis=2) > 95) & (im.mean(axis=2) < 225)) | ((im.max(axis=2) - im.min(axis=2) < 10) & (im.mean(axis=2) > 60)))   # 그림자 윗선은 더 어두운 회색(약 70)
    ys = np.where((~bg).any(axis=1))[0]
    low = np.zeros_like(grey); low[int(ys.max() - (ys.max() - ys.min()) * 0.22):] = True
    glab, _ = ndi.label(grey & low)
    band = glab[ys.max() - 2:ys.max() + 1]   # 맨 아래 3줄에 닿는 회색 = 그림자
    seeds = np.unique(band[band > 0])
    shadow = np.isin(glab, seeds)
    # 그림자 둘레 흐린 테두리도 같이
    shadow = shadow | (ndi.binary_dilation(shadow, iterations=2) & low & (im.max(axis=2) - im.min(axis=2) < 30) & (im.mean(axis=2) > 80))
    bg = bg | shadow
    # 발 사이에 남은 그림자 윗가장자리 띠: 바로 아래가 배경인 회색(외곽선보다 밝은 무채색)을 아래에서 위로 몇 줄 걷어 냄
    #   (부츠는 검은 외곽선이 아래를 막고 있어 안 걷힘)
    hang = low & (im.max(axis=2) - im.min(axis=2) < 40) & (im.mean(axis=2) > 100)
    for _ in range(6):
        below = np.zeros_like(bg); below[:-1] = bg[1:]
        bg = bg | (hang & below & ~bg)
    lab, n = ndi.label(~bg)
    sz = ndi.sum(~bg, lab, range(1, n + 1))
    bg = bg | ~np.isin(lab, [i + 1 for i in range(n) if sz[i] >= sz.max() * 0.05])
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    a = np.where(a < 0.12, 0, a)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 127
    rows = np.where(k.any(axis=1))[0]
    foot = np.where(k[int(rows.max() - (rows.max() - rows.min()) * 0.08):].any(axis=0))[0].mean()
    hm = hair_mask(rgba)
    hy, hx = np.where(hm)
    top = hy.min()
    return rgba, foot, rows.max() - top + 1, hx.max() - hx.min() + 1, hx.mean()


def main():
    pieces = []
    sc = None
    for name, src, box in FRAMES:
        rgba, foot, bh, hw, hcx = load(src, box, name in FLIP)
        if sc is None: sc = TARGET_H / bh
        p = shrink(rgba, sc)
        pieces.append((name, p, foot * sc))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} 키 {bh} 머리털 폭 {hw} ×{sc:.3f} → {p.shape[1]}x{p.shape[0]}  발 {foot:.0f}')
    L = max(int(np.ceil(c)) for _, _, c in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 3
    H = max(p.shape[0] for _, p, _ in pieces) + 3
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = H - 2 - p.shape[0]
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('cells:', ' '.join(f'{i}={n}' for i, (n, _, _) in enumerate(FRAMES)))
    print(f'warrior_0 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)}')


if __name__ == '__main__':
    main()

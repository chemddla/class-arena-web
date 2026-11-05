# 정령사 전용 샘플(초록 긴 머리·장미 화관·초록 로브·갈색 마법서, 흰 배경) → 캐릭터 시트 assets/sprites/merc/summoner_0.webp
# 사용: python tools/summoner_build.py   (샘플은 assets/sprites/fx/samples/summoner_*_src.png, 동작 샘플이 오는 대로 FRAMES에 늘림)
# 칸 순서: 0 대기 · 1~4 걷기 · 5 피격 · 6~8 쓰러짐 (책을 놓치며 뒤로 젖힘 → 무릎 꿇고 앞으로 고꾸라짐 → 엎드려 쓰러짐)
#   · 9 기본 공격 (주먹 쥔 손을 앞으로 뻗음) · 10 소환 시전 (시전 막대 동안 책을 펼쳐 빛 가루) · 11 소환 발동 (책 위 연둣빛 마법진)
#   - 공격·시전·발동 샘플(184×202, 171×190, 187×192)은 시트에서 잘라 온 것이라 양옆에 옆 칸 그림 조각이 걸쳐 있음 → 가장 큰 덩어리만 ('big')
#   - 발동 칸의 연둣빛 마법진은 흰 배경 위에 옅게 그려져 있어 GLOW 상자 안에서 흰색과 떨어진 만큼만 불투명하게 (반투명 빛으로 남김)
# 크기 통일: 대기·걷기는 몸 키(머리 꼭대기~발, 샘플 px)를 TARGET_H로 줄임. 피격·쓰러짐은 걷기와 같은 크기로 그려져 있어서(얼굴 폭 같음) 걷기 첫 칸 배율 그대로
#   (쓰러짐 첫 칸은 책을 머리 위로 놓쳐서 키로 재면 작아짐)
#   - 피격 샘플(137×160)은 오른쪽 9줄이 검은 테두리 → 잘라 냄. 뒤로 날리는 머리카락은 샘플 왼쪽 끝에서 잘려 있음
# 샘플 정리:
#   - 대기 샘플(1024×960)은 도트 그림을 10배쯤 흐리게 키운 것 + 위 10줄 회색 그림자 띠 · 오른쪽 끝 1줄 회색 → 잘라 냄 (CARD)
#   - 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움 (책 종이·눈의 흰 하이라이트는 남김)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/summoner_'
OUT = 'assets/sprites/merc/summoner_0.webp'
TARGET_H = 88   # 대기 자세 머리(화관) 꼭대기~발 → 게임 칸 키 (마법사 topH 92와 비슷하게)

# (샘플 이름, 칸 이름, 배율: ('h', 몸 키) = 그 키를 TARGET_H로 · 칸 이름 = 그 칸 배율 그대로, 샘플 안 몇 번째 그림(왼쪽부터))
FRAMES = None   # main에서 키를 재서 채움
CARD = {'idle': (0, 1022, 12), 'hurt': (0, 128, 0), 'walk': (0, 501, 0)}   # (x0, x1, 위에서 버릴 줄 수): 대기 = 회색 그림자 띠, 피격 = 오른쪽 9줄 · 걷기 = 오른쪽 3줄 검은 테두리
WHITE_MIN = {'idle': 228}
CUT = {'release': [(0, 19, 40, 135)], 'atk': [(176, 184, 55, 130)]}   # 지울 상자 (x0, x1, y0, y1): 몸에 붙은 옆 칸 조각 (발동 = 왼쪽 책, 공격 = 오른쪽 머리카락)
GLOW = {'release': [(95, 187, 0, 120)]}   # 연둣빛 마법진이 있는 상자 (x0, x1, y0, y1)     # 흐리게 키운 샘플은 배경이 덜 하얌


def load(name, pick=0):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    if name in CARD:
        x0, x1, top = CARD[name]; im = im[top:, x0:x1]
    wm = WHITE_MIN.get(name, 214)
    white = (im.min(axis=2) > wm) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    for x0, x1, y0, y1 in CUT.get(name, ()): bg[y0:y1, x0:x1] = True
    rim = ~bg & ndi.binary_dilation(bg, iterations=2 if name != 'idle' else 6)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)
    if name in GLOW:   # 흰 배경 위 연둣빛 마법진: 배경에서 이어진 밝은 초록 픽셀은 흰색과 떨어진 만큼만 불투명 (피부·책 종이는 붉은 기가 더 세서 빠짐)
        box = np.zeros_like(bg)
        for x0, x1, y0, y1 in GLOW[name]: box[y0:y1, x0:x1] = True
        r, g, b = im[..., 0], im[..., 1], im[..., 2]
        cand = box & ~bg & (im.min(axis=2) > 120) & (g >= r - 4) & (g >= b - 8)
        lab2, _ = ndi.label(cand | bg)
        glow = cand & np.isin(lab2, np.unique(lab2[bg]))
        ga = np.clip((255 - im.min(axis=2)) / 150, 0, 1)
        a = np.where(glow, ga, a)
        rim = rim | glow
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
    sz = ndi.sum(m, lab, range(1, n + 1))
    if pick == 'big':   # 샘플 가장자리에 옆 칸 그림 조각이 걸쳐 있음 → 가장 큰 덩어리만
        a = np.where(lab == 1 + int(np.argmax(sz)), a, 0)
    else:
        bigs = [i + 1 for i in range(n) if sz[i] >= sz.max() * 0.3]
        bigs.sort(key=lambda i: np.where(lab == i)[1].mean())
        a = np.where(lab == bigs[pick], a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 0
    body = np.where((rgba[..., 3] >= 254).any(axis=1))[0]   # 몸 키: 마법진(반투명) 빼고 불투명 픽셀만
    foot = np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()
    return rgba, foot, body.max() - body.min() + 1


FRAMES = [
    ('idle', 'idle', 'H', 0),
    ('walk', 'walk0', 'H', 0), ('walk', 'walk1', 'H', 1), ('walk', 'walk2', 'H', 2), ('walk', 'walk3', 'H', 3),
    ('hurt', 'hurt', 'walk0', 0),
    ('down', 'down0', 'walk0', 0), ('down', 'down1', 'down0', 1), ('down', 'down2', 'down0', 2),
    ('atk', 'atk', 'H', 'big'), ('cast', 'cast', 'H', 'big'), ('release', 'release', 'H', 'big'),
]
FOOTX = {}   # 칸 이름 → 발 가운데 (자른 그림 기준 px)


def main():
    pieces, scale = [], {}
    for src, name, k, pick in FRAMES:
        rgba, foot, bh = load(src, pick)
        if name in FOOTX: foot = FOOTX[name]
        sc = scale[k] if k != 'H' else TARGET_H / bh
        scale[name] = sc
        p = shrink(rgba, sc)
        pieces.append((name, p, foot * sc))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{sc:.3f} → {p.shape[1]}x{p.shape[0]}  발 {foot:.0f}')
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
    print(f'summoner_0 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)}')


if __name__ == '__main__':
    main()

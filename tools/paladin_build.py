# 성기사(성전사) 전용 샘플(은발 땋은 머리·파란 십자 방패·전쟁 망치, 흰 배경 한 장씩) → 캐릭터 시트 assets/sprites/merc/paladin_0.webp
# 사용: python tools/paladin_build.py   (샘플은 assets/sprites/fx/samples/paladin_*_src.png, 동작 샘플이 오는 대로 FRAMES에 늘림)
# 칸 순서 (동작 샘플이 오는 대로 늘림): 0 대기 · 1~4 걷기 · 5 피격 · 6~8 쓰러짐 (서서 뒤로 젖힘 → 무릎 꿇음 → 엎어짐)
# 크기 통일: 대기 샘플의 머리 꼭대기~발 키(IDLE_SRC_H)를 TARGET_H로 줄이는 배율이 기준. 다른 동작은 같은 배율(k=1)로 줄이고,
#   샘플마다 캐릭터를 다르게 그려 왔으면 그 칸의 몸 키(머리 꼭대기~발, 샘플 px)를 ('h', 키)로 적어 대기와 같은 키가 되게 맞춤
# 샘플 정리:
#   - 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움 (갑옷·방패 십자의 흰 하이라이트는 남김), 배경과 섞인 2px 테두리는 흰색을 빼서 투명도·본래 색을 되살림
#   - 대기 샘플(168×195)은 카드 화면을 잘라 온 것이라 오른쪽 4px·아래 1px 회색 테두리와 왼쪽 위 "#2" 번호 글씨가 박혀 있음 → 지움 (CARD, LABEL)
#   - 발은 잘리지 않았음 (부츠 바닥 윤곽선 뒤 1px 연한 띠까지 있음)
#   - 걷기 샘플(753×240, "2. 걷기" 제목 글씨)은 캐릭터가 대기보다 9% 크게 그려짐(키 177px, 머리 폭 77 vs 대기 69) → 몸 키로 대기와 같게
#   - 피격·쓰러짐 샘플(931×178, 제목 글씨 2개)은 얼굴은 대기와 같은데 방패가 15% 작게 그려짐 → 중간값 1.08배로 키움. 무릎 꿇음·엎어짐 칸은 키로 못 재서 첫 칸 배율 그대로
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/paladin_'
OUT = 'assets/sprites/merc/paladin_0.webp'
TARGET_H = 110   # 대기 자세 머리 꼭대기~발 → 게임 칸 키. 게임에선 standH 90(기사와 같음)으로 1.22배 크게 그려 머리·얼굴이 다른 직업만큼 보이게 함
                 #   (샘플은 다른 직업보다 머리가 작은 6등신쯤: 키 165px에 머리 폭 69px. 전사는 키 82에 머리 폭 59)
IDLE_SRC_H = 163 # 대기 샘플 머리 꼭대기~발 키 (샘플 px)

# (샘플 이름, 칸 이름, 배율: 1 = 대기와 같은 배율 · ('h', 몸 키) = 그 키를 TARGET_H로 · 칸 이름 = 그 칸 배율 그대로, 샘플 안 몇 번째 그림(왼쪽부터) 또는 (x0, x1))
FRAMES = [
    ('idle', 'idle', 1, 0),
    ('walk', 'walk0', ('h', 177), 0), ('walk', 'walk1', ('h', 177), 1), ('walk', 'walk2', ('h', 177), 2), ('walk', 'walk3', ('h', 177), 3),
    ('hurt_down', 'hurt', 1.08, 0),
    ('hurt_down', 'down0', 1.08, 1), ('hurt_down', 'down1', 'down0', 2), ('hurt_down', 'down2', 'down0', 3),
]
CARD = {'idle': (163, 194)}   # 카드 테두리를 빼고 쓸 (너비, 높이)
LABEL = {'idle': [(0, 45, 0, 16)]}   # 지울 상자 (x0, x1, y0, y1): 번호 글씨
LIFT = {}   # 땅에서 띄워 그릴 높이 (칸 px)
SRC = {}


def load(name, pick=0):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    if name in CARD:
        w, h = CARD[name]; im = im[:h, :w]
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    for x0, x1, y0, y1 in LABEL.get(name, ()): bg[y0:y1, x0:x1] = True
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    # 큰 덩어리(몸)만 (글씨·티끌은 지움). 한 장에 여러 칸이면 왼쪽부터 pick번째
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m))
    sz = ndi.sum(m, lab, range(1, n + 1))
    if isinstance(pick, tuple):
        cx = ndi.center_of_mass(m, lab, range(1, n + 1))
        keep = [i + 1 for i in range(n) if sz[i] >= 20 and pick[0] <= cx[i][1] < pick[1]]
        a = np.where(np.isin(lab, keep), a, 0)
    else:
        bigs = [i + 1 for i in range(n) if sz[i] >= sz.max() * 0.3]
        bigs.sort(key=lambda i: np.where(lab == i)[1].mean())
        a = np.where(lab == bigs[pick], a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 0
    foot = np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()   # 발 가운데 (아래 8%의 불투명 픽셀 가운데)
    return rgba, foot


def main():
    pieces, scale = [], {}
    for src, name, k, pick in FRAMES:
        rgba, foot = load(src, pick)
        sc = scale[k] if isinstance(k, str) else (TARGET_H / k[1] if isinstance(k, tuple) else TARGET_H / IDLE_SRC_H * k)
        scale[name] = sc
        p = shrink(rgba, sc)
        pieces.append((name, p, foot * sc))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{sc:.3f} → {p.shape[1]}x{p.shape[0]}')
    L = max(int(np.ceil(c)) for _, _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 4
    H = max(p.shape[0] + LIFT.get(n, 0) for n, p, _ in pieces) + 5
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = H - 2 - p.shape[0] - LIFT.get(name, 0)
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'paladin_0 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)}')


if __name__ == '__main__':
    main()

# 격투가 전용 샘플(갈색 머리·흰 도복·검은 띠, 흰 배경) → 캐릭터 시트 assets/sprites/merc/brawler_0.webp
# 사용: python tools/brawler_build.py   (샘플은 assets/sprites/fx/samples/brawler_*_src.png, 동작 샘플이 오는 대로 FRAMES에 늘림)
# 칸 순서: 0 대기 (주먹을 쥐고 선 자세) · 1~4 걷기 (받은 샘플을 WALK_ORDER 순서로 다시 놓음) · 5 피격 (몸을 젖히며 얼굴을 찡그림)
#   · 6~7 쓰러짐 (뒤로 넘어감 → 누워 기절) · 8~23 연격 샘플 0~15 (받은 순서 그대로, 재생 순서는 COMBO_SEQ)
#   · 24 슈퍼아머 (이를 악물고 버티는 자세) · 25 결투 (상대를 향해 기합을 지르는 자세)
#   - 슈퍼아머·결투 샘플은 발 아래 번호 글자('04'·'07') → 몸과 떨어져 있어 가장 큰 덩어리만 남기면 빠짐
#   - 연격 샘플: 0·1은 격자선+바닥 줄, 3·5·8은 왼쪽 끝에 옆 칸 조각 → 격자 자동 제거 + 가장 큰 덩어리만. 3의 발차기 궤적(흰 호)은 다리에 붙어 있어 남김
# 크기 통일: 대기 자세 몸 키(머리털 끝~발, 샘플 px)를 TARGET_H로 줄임. 다른 동작은 대기와 같은 배율('idle')로 줄여 얼굴 크기를 맞춤
# 샘플 정리:
#   - 대기 샘플(158×179)은 도트 그림을 흐리게 키운 것 + 아래 2줄(175~176)·오른쪽 1줄(157) 회색 테두리 → 잘라 냄 (CARD)
#   - 걷기 4번째 샘플(110×147)은 연회색 격자선(가로 36~37·99~100줄, 세로 20~21·89~90칸) + 아래 143줄부터 검은 바닥 줄
#     → 격자선 위의 무채색 회색 픽셀만 흰색으로 칠하고(GRID) 바닥 줄은 잘라 냄
#   - 쓰러짐 샘플(674×156)은 두 칸('쓰러짐 1/2' 글자 포함)을 한 장에 그린 것 + 연회색 격자선 + 가운데 세로 구분선(336~337) + 아래 바닥 줄
#     → 구분선 양쪽으로 나눠 자르고(SRC) 격자선은 자동으로 찾아 지움(GRID_AUTO), 글자는 가장 큰 덩어리(캐릭터)만 남겨 버림
#     쓰러짐 2는 머리가 오른쪽(쓰러짐 1과 반대로 넘어간 모습)이라 좌우를 뒤집어 뒤로 넘어간 방향을 맞춤 (FLIP)
#   - 피격 샘플(151×227)의 머리 옆 주황 타격 불꽃은 몸과 떨어져 있어 가장 큰 덩어리만 남기면 빠짐 (타격 이펙트는 게임에서 따로 그림)
#   - 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움 (흰 도복은 검은 외곽선 안쪽이라 남음)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/brawler_'
OUT = 'assets/sprites/merc/brawler_0.webp'
TARGET_H = 86   # 대기 자세 머리털 끝~발 → 게임 칸 키. 게임에선 standH 78, topH 86으로 그림 (몸이 길고 머리가 작아 86으로 두면 얼굴이 소환사·광전사보다 작아 보임)

CARD = {'idle': (0, 157, 0, 175), 'walk3': (0, 110, 0, 143)}   # (x0, x1, y0, y1): 샘플 테두리 회색 줄 잘라 냄
WHITE_MIN = {}
CUT = {}   # 지울 상자 (x0, x1, y0, y1)
GRID = {'walk3': ([36, 37, 99, 100], [20, 21, 89, 90])}   # (가로줄 y, 세로줄 x): 샘플에 남은 격자선
SRC = {'down1': ('down', (0, 335, 0, 150)), 'down2': ('down', (339, 674, 0, 150))}   # 칸 이름 → (샘플, 자를 상자): 한 장에 여러 칸
GRID_AUTO = {'down1', 'down2'} | {f'combo{i:02d}' for i in range(16)}   # 격자선 줄을 자동으로 찾음 (무채색 회색이 줄의 25% 이상)
FLIP = {'down2'}


def hair_width(rgba):   # 갈색 머리털 덩어리의 가로 폭 (몸이 누워도 머리 크기는 그대로라 배율 기준으로 씀)
    r, g, b, a = [rgba[..., i] for i in range(4)]
    hair = (a > 200) & (r > g) & (g > b) & (r - b > 25) & (r < 200) & (r > 45)
    lab, n = ndi.label(ndi.binary_closing(hair, iterations=2))
    big = 1 + int(np.argmax(ndi.sum(hair, lab, range(1, n + 1))))
    xs = np.where((lab == big).any(axis=0))[0]
    return xs.max() - xs.min() + 1


def load(name, pick=0):
    src, box = SRC.get(name, (name, None))
    im = np.array(Image.open(f'{D}{src}_src.png').convert('RGB')).astype(float)
    if box:
        x0, x1, y0, y1 = box; im = im[y0:y1, x0:x1]
    if name in GRID_AUTO:   # 줄 전체에 걸친 무채색 회색 = 격자선 → 그 줄(±1)의 무채색 회색만 흰색으로
        grey = (im.min(axis=2) > 150) & (im.max(axis=2) - im.min(axis=2) < 8)
        line = np.zeros(im.shape[:2], bool)
        for y in np.where(grey.sum(axis=1) > im.shape[1] * 0.25)[0]: line[max(0, y - 1):y + 2] = True
        for x in np.where(grey.sum(axis=0) > im.shape[0] * 0.25)[0]: line[:, max(0, x - 1):x + 2] = True
        im[line & grey] = 255
        dark = (im.min(axis=2) < 140).sum(axis=1) > im.shape[1] * 0.6   # 아래 바닥 줄 (줄 대부분이 어두움) → 그 위까지만
        bot = [y for y in range(im.shape[0] - 1, int(im.shape[0] * 0.8), -1) if dark[y]]
        if bot: im = im[:min(bot) - 1]
    if name in FLIP: im = im[:, ::-1]
    if name in GRID:   # 격자선: 선 위(±1줄)의 무채색 연회색만 흰색으로 (도복 그림자는 푸른 기가 있어 남음)
        line = np.zeros(im.shape[:2], bool)
        ys, xs = GRID[name]
        for y in ys: line[max(0, y - 1):y + 2] = True
        for x in xs: line[:, max(0, x - 1):x + 2] = True
        grey = (im.min(axis=2) > 195) & (im.max(axis=2) - im.min(axis=2) < 8)
        im[line & grey] = 255
    if name in CARD:
        x0, x1, y0, y1 = CARD[name]; im = im[y0:y1, x0:x1]
    wm = WHITE_MIN.get(name, 222)
    white = (im.min(axis=2) > wm) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    for x0, x1, y0, y1 in CUT.get(name, ()): bg[y0:y1, x0:x1] = True
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)   # 흐린 외곽: 흰 배경과 섞인 만큼 반투명
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
    sz = ndi.sum(m, lab, range(1, n + 1))
    if pick == 'big':
        a = np.where(lab == 1 + int(np.argmax(sz)), a, 0)
    else:
        bigs = [i + 1 for i in range(n) if sz[i] >= sz.max() * 0.3]
        bigs.sort(key=lambda i: np.where(lab == i)[1].mean())
        a = np.where(lab == bigs[pick], a, 0)
    a = np.where(a < 0.12, 0, a)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 127
    body = np.where(k.any(axis=1))[0]
    foot = np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()
    rows = [np.where(k[y])[0] for y in range(int(k.shape[0] * 0.08), int(k.shape[0] * 0.28))]   # 머리 줄 (어깨·팔 위)
    rows = [r for r in rows if len(r)]
    head_w = max(r.max() - r.min() + 1 for r in rows)
    head_cx = float(np.mean([(r.max() + r.min()) / 2 for r in rows]))
    return rgba, foot, body.max() - body.min() + 1, head_w, head_cx, hair_width(rgba)


WALK_ORDER = [0, 2, 3, 1]   # 걷기 칸 1~4에 넣을 샘플 번호 (받은 순서 기준): 뒷발 들고 지나감 → 앞발 내뻗음(발끝 듦) → 두 발 디딤(보폭 최대, 몸이 가장 낮음) → 뒷발 뒤꿈치 듦 → 다시 처음
# (샘플 이름, 칸 이름, 배율: 'H' = 몸 키를 TARGET_H로 · 'W' = 머리 폭을 대기 칸 머리 폭과 같게 · 칸 이름 = 그 칸 배율 그대로, 샘플 안 몇 번째 그림(왼쪽부터))
# 'HAIR' = 갈색 머리털 폭을 대기 칸과 같게 (피격·쓰러짐처럼 머리가 기울거나 누운 칸)
# 걷기는 보폭에 따라 키가 달라서 머리 폭으로 맞추고, 발 기준점도 머리 가운데로 잡아 걸을 때 몸이 좌우로 흔들리지 않게 함 (HEAD_ANCHOR)
FRAMES = [
    ('idle', 'idle', 'H', 0),
] + [(f'walk{i}', f'walk{j}', 'W', 0) for j, i in enumerate(WALK_ORDER)] + [
    ('hurt', 'hurt', 'HAIR', 'big'),
    ('down1', 'down1', 'HAIR', 'big'), ('down2', 'down2', 'down1', 'big'),
] + [(f'combo{i:02d}', f'combo{i:02d}', 'HEAD', 'big') for i in range(16)] + [
    ('armor', 'armor', 'W', 'big'), ('duel', 'duel', 'W', 'big'),
]
# 연격 샘플 머리 폭 (샘플 px). 'HEAD' = 이 폭을 대기 칸 머리 폭(샘플 67px × 대기 배율)과 같게
#   머리 실루엣 가로 폭으로 잼. 주먹·다리가 머리에 붙은 칸(0·1·10·11·13·14)은 실루엣이 이어져 크게 나와서 머리털 폭 × 1.19 (정면 칸들의 머리 폭 ÷ 머리털 폭)
#   뒷모습 칸(6·7·8·12)은 머리털이 머리 전체라 머리털 폭으로는 작게 나와 실루엣 폭을 씀
# 연격 재생 순서 (샘플 번호, 같은 칸을 다시 써도 됨) → 시트 칸 번호는 8 + 샘플 번호. 게임 anims.combo에 넣을 목록은 main이 출력
#   가드 → 잽 → 정권 지르기 → 무릎 당겨 → 중단 돌려차기 → 돌려차기 → 상단 돌려차기 → 무릎 회수
#   → 등 돌림 → 뒤돌며 발 듦 → 무릎 당김(뒷모습) → 뒤후려차기 → 옆차기 → 무릎 당겨 → 내려찍기 들어올림 → 내려찍기(궤적) → 가드
COMBO_SEQ = [15, 0, 2, 13, 1, 14, 10, 4, 12, 6, 8, 7, 9, 13, 11, 3, 5]
HEAD_PX = {'combo00': 62, 'combo01': 62, 'combo02': 88, 'combo03': 67, 'combo04': 66, 'combo05': 66, 'combo06': 58, 'combo07': 60,
           'combo08': 62, 'combo09': 60, 'combo10': 61, 'combo11': 56, 'combo12': 54, 'combo13': 56, 'combo14': 60, 'combo15': 57}
HEAD_ANCHOR = {f'walk{j}' for j in range(4)}
FOOTX = {}   # 칸 이름 → 발 가운데 (자른 그림 기준 px)


def main():
    pieces, scale = [], {}
    ref = {}   # 대기 칸: 게임 px 머리 폭 · 머리 가운데에서 발까지 거리
    for src, name, k, pick in FRAMES:
        rgba, foot, bh, hw, hcx, hair = load(src, pick)
        if name in FOOTX: foot = FOOTX[name]
        sc = TARGET_H / bh if k == 'H' else ref['hw'] / hw if k == 'W' else ref['hair'] / hair if k == 'HAIR' else ref['hw'] / HEAD_PX[name] if k == 'HEAD' else scale[k]
        if name == 'idle': ref = {'hw': hw * sc, 'dx': (hcx - foot) * sc, 'hair': hair * sc}
        if name in HEAD_ANCHOR: foot = hcx - ref['dx'] / sc
        scale[name] = sc
        p = shrink(rgba, sc)
        pieces.append((name, p, foot * sc))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} 키 {bh} ×{sc:.3f} → {p.shape[1]}x{p.shape[0]}  발 {foot:.0f}')
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
    print('combo anim:', [8 + i for i in COMBO_SEQ])
    print(f'brawler_0 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)}')


if __name__ == '__main__':
    main()

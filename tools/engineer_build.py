# 기계공 전용 샘플(갈색 머리·고글·갈색 배낭·국방색 멜빵바지, 흰 배경) → 캐릭터 시트 assets/sprites/merc/engineer_0.webp
# 사용: python tools/engineer_build.py   (샘플은 assets/sprites/fx/samples/engineer_*_src.png, 동작 샘플이 오는 대로 FRAMES에 늘림)
# 칸 순서: 0 대기 · 1~4 걷기 (받은 순서 그대로) · 5~6 리벳총 기본 공격 (5 겨눔 → 6 쏨) · 7~8 수리 (쪼그려 앉아 렌치질, 두 칸 번갈아)
#   수리 샘플은 한 장에 두 칸 → 가운데 빈 세로줄(141)에서 나눠 engineer_repair1/2_src.png로 저장함
# 칸 크기·기준점은 격투가 시트와 같음 (cellW 119 · cellH 106 · anchorX 63 · anchorY 104)
# 크기 통일: 대기 자세 몸 키(머리털 끝~발, 샘플 px)를 TARGET_H로 줄임. 다른 동작 샘플은 해상도가 달라서
#   묶음마다 몸 키 평균이 TARGET_H × GROUP_H 가 되도록 한 배율로 줄임 (칸끼리 키가 튀지 않게)
#   (고글 폭으로 맞추면 옆으로 돈 걷기 자세는 렌즈가 좁아 보여 몸이 작아짐 → 키로 맞춤)
# 가로 위치: 대기는 몸 가운데를 기준점에, 걷기는 고글 가운데를 같은 자리에 둬서 걷는 동안 머리가 좌우로 흔들리지 않게 함
# 샘플 정리: 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움 (흰 셔츠는 검은 외곽선 안쪽이라 남음), 가장 큰 덩어리만 남김
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/engineer_'
OUT = 'assets/sprites/merc/engineer_0.webp'
FRAMES = ['idle', 'walk1', 'walk2', 'walk3', 'walk4', 'attack1', 'attack2', 'repair1', 'repair2']
GROUP = {'walk1': 'walk', 'walk2': 'walk', 'walk3': 'walk', 'walk4': 'walk', 'attack1': 'attack1', 'attack2': 'attack2', 'repair1': 'repair', 'repair2': 'repair'}   # 같은 배율을 쓰는 묶음
GOGGLE_REF = {'attack1', 'attack2', 'repair'}   # 몸 키 대신 고글 폭을 걷기와 같게 맞추는 묶음 (총을 겨누거나 쪼그려 앉아 키로는 못 맞춤, 걷기처럼 옆으로 돈 자세라 고글 폭으로 맞춰도 됨)
GROUP_H = {'walk': 0.97}   # 묶음 몸 키 / 대기 몸 키 (걸을 때는 다리를 벌려 조금 낮아짐)
HEAD_X = {'walk': 66, 'attack1': 50, 'attack2': 50, 'repair': 60}   # 묶음의 고글 가운데 x (칸 안, 기준점 63보다 조금 앞: 앞을 보고 걸어 머리가 앞으로)
CELL_W, CELL_H, ANCHOR_X, ANCHOR_Y = 119, 106, 63, 104
TARGET_H = 98   # 샘플이 가늘고 머리가 작아 86이면 얼굴이 격투가보다 훨씬 작아 보여 키움 (칸 높이 106 안)


def load(name):
    im = np.array(Image.open(D + name + '_src.png').convert('RGBA')).astype(float)
    rgb = im[..., :3]
    white = (rgb.min(axis=2) > 232) & (rgb.max(axis=2) - rgb.min(axis=2) < 18)
    lab, _ = ndi.label(white)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    bg = ndi.binary_dilation(bg, iterations=3) & (rgb.min(axis=2) > 150)   # 샘플이 흐리게 키운 그림이라 외곽선 밖 밝은 번짐 3px까지 배경으로
    im[..., 3] = np.where(bg, 0, 255)
    body, n = ndi.label(im[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndi.sum(im[..., 3] > 0, body, range(1, n + 1))
        im[..., 3] = np.where(body == 1 + int(np.argmax(sizes)), im[..., 3], 0)
    ys, xs = np.where(im[..., 3] > 0)
    return im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def goggle_w(rgba):   # 고글 렌즈(청록) 가로 폭
    r, g, b, a = [rgba[..., i].astype(float) for i in range(4)]
    m = (a > 0) & (g > 110) & (b > 100) & (g - r > 40)
    xs = np.where(m.any(axis=0))[0]
    return xs.max() - xs.min() + 1


def goggle_cx(rgba):   # 고글 렌즈(청록) 가로 가운데
    r, g, b, a = [rgba[..., i].astype(float) for i in range(4)]
    m = (a > 0) & (g > 110) & (b > 100) & (g - r > 40)
    xs = np.where(m.any(axis=0))[0]
    return (xs.max() + xs.min()) / 2


def main():
    srcs = {f: load(f) for f in FRAMES}
    sc0 = TARGET_H / srcs['idle'].shape[0]
    scs = {'idle': sc0}
    for grp in set(GROUP.values()):
        names = [f for f in FRAMES if GROUP.get(f) == grp]
        if grp not in GOGGLE_REF:
            scs[grp] = TARGET_H * GROUP_H[grp] / np.mean([srcs[f].shape[0] for f in names])
    gw_walk = np.mean([goggle_w(srcs[f]) * scs['walk'] for f in FRAMES if GROUP.get(f) == 'walk'])
    for grp in GOGGLE_REF:
        names = [f for f in FRAMES if GROUP.get(f) == grp]
        scs[grp] = gw_walk / np.mean([goggle_w(srcs[f]) for f in names])
    sheet = np.zeros((CELL_H, CELL_W * len(FRAMES), 4), np.uint8)
    for i, f in enumerate(FRAMES):
        sc = scs[GROUP.get(f, 'idle')]
        s = shrink(srcs[f], sc)
        h, w = s.shape[:2]
        grp = GROUP.get(f)
        x0 = i * CELL_W + (round(HEAD_X[grp] - goggle_cx(s)) if grp in HEAD_X else ANCHOR_X - w // 2)
        x0 = min(max(x0, i * CELL_W), (i + 1) * CELL_W - w)
        y0 = ANCHOR_Y - h
        sheet[y0:y0 + h, x0:x0 + w] = s
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('저장', OUT, sheet.shape, {k: round(v, 3) for k, v in scs.items()})


if __name__ == '__main__':
    main()

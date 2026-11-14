# 기계공 전용 샘플(갈색 머리·고글·갈색 배낭·국방색 멜빵바지, 흰 배경) → 캐릭터 시트 assets/sprites/merc/engineer_0.webp
# 사용: python tools/engineer_build.py   (샘플은 assets/sprites/fx/samples/engineer_*_src.png, 동작 샘플이 오는 대로 FRAMES에 늘림)
# 칸 순서: 0 대기 (지금은 대기 샘플 한 장뿐이라 시트도 한 칸)
# 칸 크기·기준점은 격투가 시트와 같음 (cellW 119 · cellH 106 · anchorX 63 · anchorY 104)
# 크기 통일: 대기 자세 몸 키(머리털 끝~발, 샘플 px)를 TARGET_H로 줄임. 다른 동작도 대기와 같은 배율로 줄여 얼굴 크기를 맞춤
# 샘플 정리: 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움 (흰 셔츠는 검은 외곽선 안쪽이라 남음), 가장 큰 덩어리만 남김
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/engineer_'
OUT = 'assets/sprites/merc/engineer_0.webp'
FRAMES = ['idle']
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


def main():
    srcs = {f: load(f) for f in FRAMES}
    sc = TARGET_H / srcs['idle'].shape[0]
    sheet = np.zeros((CELL_H, CELL_W * len(FRAMES), 4), np.uint8)
    for i, f in enumerate(FRAMES):
        s = shrink(srcs[f], sc)
        h, w = s.shape[:2]
        x0 = i * CELL_W + ANCHOR_X - w // 2
        y0 = ANCHOR_Y - h
        sheet[y0:y0 + h, x0:x0 + w] = s
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('저장', OUT, sheet.shape, '배율', round(sc, 3))


if __name__ == '__main__':
    main()

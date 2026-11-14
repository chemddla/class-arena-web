# 기계공 포탑 샘플 한 장(세로로 기관포탑·박격포탑·레이저탑 + 아래 번호 글자, 흰 배경) → 포탑 그림 세 장
# 사용: python tools/engineer_turret_build.py
# 샘플 assets/sprites/fx/samples/engineer_turrets_src.png 의 그림 줄(ROWS, y0~y1)마다 흰 배경을 지우고 가장 큰 덩어리만 남김
# 내보내기: assets/sprites/fx/engineer_turret_{gatling,mortar,laser}.webp (모두 오른쪽을 봄, 게임이 겨눈 쪽으로 좌우를 뒤집어 그림)
#   그림 키는 TURRET_H(px), 기준점 = 받침 바닥 가운데 (그림 아래 가운데)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

SRC = 'assets/sprites/fx/samples/engineer_turrets_src.png'
ROWS = {'gatling': (35, 308), 'mortar': (345, 642), 'laser': (685, 987)}   # 그림 줄 (글자 줄은 뺌)
OUT = 'assets/sprites/fx/engineer_turret_{}.webp'
TURRET_H = {'gatling': 50, 'mortar': 54, 'laser': 58}   # 게임 칸에서 그림 키 (기계공 몸 키 98보다 작게)


def cut(rgba):
    rgb = rgba[..., :3]
    white = (rgb.min(axis=2) > 232) & (rgb.max(axis=2) - rgb.min(axis=2) < 18)
    lab, _ = ndi.label(white)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    sizes = ndi.sum(white, lab, range(1, lab.max() + 1))
    bg |= np.isin(lab, 1 + np.where(sizes >= 40)[0])   # 사슬 고리·전선 사이에 갇힌 흰 배경도 지움 (40px 넘는 흰 덩어리, 렌즈 반짝임은 작아서 남음)
    bg = ndi.binary_dilation(bg, iterations=2) & (rgb.min(axis=2) > 150)
    a = np.where(bg, 0, 255)
    body, n = ndi.label(a > 0, structure=np.ones((3, 3)))
    sizes = ndi.sum(a > 0, body, range(1, n + 1))
    keep = 1 + np.where(sizes >= sizes.max() * 0.02)[0]   # 큰 덩어리들 (기관포탑 사슬·탄약통처럼 떨어진 부품도 남김)
    a = np.where(np.isin(body, keep), a, 0)
    out = rgba.copy(); out[..., 3] = a
    ys, xs = np.where(a > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def main():
    im = np.array(Image.open(SRC).convert('RGBA')).astype(float)
    for k, (y0, y1) in ROWS.items():
        c = cut(im[y0:y1])
        s = shrink(c, TURRET_H[k] / c.shape[0])
        Image.fromarray(s, 'RGBA').save(OUT.format(k), 'WEBP', lossless=True)
        print(k, s.shape[1], 'x', s.shape[0])


if __name__ == '__main__':
    main()

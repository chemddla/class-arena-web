# 성녀 새 기본 외형(healer_0, 2026-11-09 은발 성녀) 외형 1~5 후보 미리보기 — 피부는 그대로, 나머지 채도·명도만 바꿈 (궁수 외형 1~5와 같은 방식)
# 사용: python tools/healer_variants_preview.py masks <경로>    → 피부로 잡힌 곳 (빨강) 확인
#       python tools/healer_variants_preview.py preview <경로>  → 후보마다 대기 칸 크게 + 여러 칸 줄
# 색상(hue)은 그대로. 흰 수도복·은발은 채도가 거의 없어서 명도로, 금빛 장식·푸른 눈은 채도로 느낌이 달라짐
# 13~16 (스킬별 색 이펙트 칸)은 미리보기에 안 넣음
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, 'tools')
import archer_variants_preview as A
from frost_variants_build import rgb2hsv

SRC = 'assets/sprites/merc/healer_0.webp'
CW = 170
SHOW = [0, 1, 4, 5, 7, 8, 11]   # 대기·걷기·공격·피격·쓰러짐·스킬 준비·발동
VARIANTS = [
    ('원본', 1.0, 1.0),
    ('A 상아', 0.45, 1.04),
    ('B 황혼', 0.6, 0.72),
    ('C 짙은 금', 1.4, 0.82),
    ('D 은회', 0.06, 0.9),
    ('E 잿빛', 0.3, 0.58),
    ('F 선명', 1.5, 1.0),
    ('G 그림자', 0.35, 0.42),
    ('H 먹빛', 0.05, 0.5),
]


def skin_mask(im):
    # 살색: 밝은 살구색 덩어리 + 이어진 살 그림자. 은발·흰 수도복(무채색)은 넣지 않음
    hsv = rgb2hsv(im[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    al = im[..., 3] > 200
    core = al & (h >= 8) & (h <= 34) & (s >= 0.12) & (s <= 0.45) & (v > 0.78)
    lab, n = ndimage.label(core)
    sizes = ndimage.sum(core, lab, range(1, n + 1))
    keep = np.isin(lab, np.where(sizes >= 3)[0] + 1)
    broad = al & ((h <= 36) | (h >= 345)) & (s >= 0.12) & (s <= 0.55) & (v > 0.55)
    # 수도복 단의 따뜻한 음영까지 번지지 않게 핵심 살색에서 4px 안만
    grown = ndimage.binary_propagation(keep, mask=(broad & ndimage.binary_dilation(keep, iterations=4)) | keep)
    # 눈: 얼굴 안의 작은 구멍 (흰자·눈동자 빛점·푸른 눈동자)
    holes = ndimage.binary_fill_holes(grown) & ~grown
    hl, hn = ndimage.label(holes)
    hs = ndimage.sum(holes, hl, range(1, hn + 1))
    eyes = np.isin(hl, np.where(hs <= 10)[0] + 1) & (((v > 0.85) & (s < 0.2)) | ((h >= 190) & (h <= 250)))
    return grown | eyes


A.skin_mask = skin_mask


def main(mode, path):
    A.SRC, A.CW, A.SHOW, A.VARIANTS = SRC, CW, SHOW, VARIANTS
    (A.masks if mode == 'masks' else A.preview)(path)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

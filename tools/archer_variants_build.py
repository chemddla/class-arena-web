# 궁수 외형 1~5 (2026-11-09 금발 궁수 기본 외형 archer_0의 색 변형) 만들기 — 칸 구성·크기·색상(hue)은 기본 외형과 같고 채도·명도만 바꿈
# 사용: python tools/archer_variants_build.py   (tools/archer0_build.py로 기본 외형을 다시 만들었으면 그다음에)
#   assets/sprites/merc/archer_0.webp           → archer_1~5.webp (14칸)
#   assets/sprites/fx/archer_storm_cast_0.webp  → archer_storm_cast_1~5.webp (히든 스킬 [폭풍] 시전 3칸)
# 규칙: 피부·눈 흰자는 그대로 (tools/archer_variants_preview.py의 skin_mask). 시전 그림의 반투명 바람·빛과 밝은 연두 바람줄기는
#   그대로 둬서 기본 외형용 연두 바람 고리·돌풍 화살(archer_storm_wind_0·storm_arrow_0)을 모든 외형이 같이 씀
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(__file__))
import archer_variants_preview as P
from frost_variants_build import rgb2hsv

# (번호, 이름, 채도 배율, 명도 배율) — 2026-11-09 후보 8개 중 사용자가 고른 다섯 (docs/archer-variant-allframes.png)
VARIANTS = [
    (1, '파스텔', 0.4, 1.2),
    (2, '짙은 숲', 0.9, 0.6),
    (3, '어스름', 0.5, 0.72),
    (4, '무채 은회', 0.08, 1.0),
    (5, '그림자', 0.3, 0.42),
]
BODY = 'assets/sprites/merc/archer_%s.webp'
CAST = 'assets/sprites/fx/archer_storm_cast_%s.webp'
CAST_CW = 159


def save(arr, path):
    Image.fromarray(arr, 'RGBA').save(path, 'WEBP', lossless=True, method=6)


def cast_keep(im):
    # 시전 그림에서 안 바꿀 곳: 몸 바깥(바람·빛·금빛 줄기) + 밝은 연두·청록 바람줄기(망토 초록보다 훨씬 밝음)
    #   몸 = 칸마다 (불투명도 150 이상 & 바람색 아님)의 가장 큰 덩어리 (흰·검은 배경 비교로 지운 그림이라 머리카락은 불투명도 200~250)
    hsv = rgb2hsv(im[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    wind = (h >= 70) & (h <= 170) & (s > 0.15) & (v > 0.78)
    solid = (im[..., 3] >= 150) & ~wind
    body = np.zeros_like(solid)
    for i in range(im.shape[1] // CAST_CW):
        sl = (slice(None), slice(i * CAST_CW, (i + 1) * CAST_CW))
        lab, n = ndimage.label(solid[sl])
        if not n: continue
        big = np.argmax(ndimage.sum(solid[sl], lab, range(1, n + 1))) + 1
        b = ndimage.binary_fill_holes(lab == big)
        body[sl] = ndimage.binary_dilation(b, iterations=1) & (im[sl][..., 3] > 0)
    return ~body | wind


def main():
    body = np.array(Image.open(BODY % 0).convert('RGBA'))
    P.CW = 214
    bskin = P.skin_mask(body)
    cast = np.array(Image.open(CAST % 0).convert('RGBA'))
    P.CW = CAST_CW
    cskin = P.skin_mask(cast) | cast_keep(cast)
    for n, name, sat, val in VARIANTS:
        save(P.tone(body, bskin, sat, val), BODY % n)
        save(P.tone(cast, cskin, sat, val), CAST % n)
        print(f'외형 {n} {name}: 채도 ×{sat} 명도 ×{val}')


if __name__ == '__main__':
    main()

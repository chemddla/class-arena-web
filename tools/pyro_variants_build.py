# 화염술사 외형 0(pyro_0.webp)에서 채도·명암만 바꾼 외형 시트 만들기 (칸 구성·크기·색상(hue) 모두 같음)
# 사용: python tools/pyro_variants_build.py   → assets/sprites/merc/pyro_1~5.webp
# 규칙: 피부(얼굴·귀·목·어깨·손)는 그대로, 나머지(머리·로브·바지·부츠·시트에 그려진 불꽃)만 채도·명도 배율 적용
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb

SRC = 'assets/sprites/merc/pyro_0.webp'
# (번호, 이름, 채도 배율, 명도 배율)
VARIANTS = [
    (1, '바랜 노을', 0.55, 1.08),
    (2, '잿불', 0.45, 0.7),
    (3, '숯불', 0.85, 0.5),
    (4, '흑염', 0.3, 0.38),
    (5, '무채 은회', 0.08, 1.0),
]


def skin_mask(im):
    hsv = rgb2hsv(im[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    al = im[..., 3] > 0
    warm = (h <= 22) | (h >= 352)
    # 핵심 살색: 얼굴·손·귀·어깨·가슴. 귀·어깨처럼 머리카락·옷선에 갈려 떨어진 작은 조각도 2픽셀부터 잡음
    core = al & warm & ((s >= 0.24) | ((s >= 0.2) & ((h <= 14) | (h >= 352)))) & (s <= 0.55) & (v > 0.7)
    lab, n = ndimage.label(core)
    sizes = ndimage.sum(core, lab, range(1, n + 1))
    keep = np.isin(lab, np.where(sizes >= 2)[0] + 1)
    # 살 그림자·밝은 하이라이트는 핵심 살색에 이어진 것만 넓혀 포함
    # 불빛에 비친 주황 살색(h 22~34)·살 그림자·흰 하이라이트는 핵심 살색에 이어진 것만 포함.
    # 바지(베이지: 채도 0.14~0.23, 명도 0.93 이하)는 이 조건에서 빠져 번지지 않음
    broad = al & ((h <= 34) | (h >= 350)) & (s <= 0.6) & (v > 0.4) & (
        (s >= 0.24) | ((s >= 0.2) & ((h <= 14) | (h >= 350))) | (v >= 0.97))
    grown = ndimage.binary_propagation(keep, mask=broad | keep)
    # 살 안쪽 1~4픽셀 구멍(점 하이라이트)은 메움
    holes = ndimage.binary_fill_holes(grown) & ~grown
    hl, hn = ndimage.label(holes)
    hs = ndimage.sum(holes, hl, range(1, hn + 1))
    grown |= np.isin(hl, np.where(hs <= 4)[0] + 1) & (s <= 0.6)
    # 살 위에 그려진 붉은 앞머리 가닥·눈동자(진한 빨강)는 피부가 아니므로 같이 바뀌게 뺌
    grown &= ~((s > 0.45) & ((h >= 345) | (h <= 8)))
    return grown



def tone(im, skin, sat, val):
    hsv = rgb2hsv(im[..., :3] / 255.)
    m = (im[..., 3] > 0) & ~skin
    hsv[..., 1] = np.where(m, np.clip(hsv[..., 1] * sat, 0, 1), hsv[..., 1])
    # 어둡게 할 때 밝은 불꽃(밝고 진한 주황·노랑)은 덜 어둡게: 노랑이 어두워지면 탁한 올리브가 되는 것 방지
    v0, s0 = hsv[..., 2], rgb2hsv(im[..., :3] / 255.)[..., 1]
    glow = np.clip((v0 - 0.7) / 0.25, 0, 1) * np.clip((s0 - 0.35) / 0.3, 0, 1)
    k = val + (1 - val) * glow * 0.8 if val < 1 else np.full_like(v0, val)
    hsv[..., 2] = np.where(m, np.clip(v0 * k, 0, 1), v0)
    out = im.copy()
    out[m, :3] = (hsv2rgb(hsv)[m] * 255 + .5).clip(0, 255).astype(np.uint8)
    return out


def main():
    im = np.array(Image.open(SRC).convert('RGBA'))
    skin = skin_mask(im)
    for num, label, sat, val in VARIANTS:
        Image.fromarray(tone(im, skin, sat, val), 'RGBA').save(f'assets/sprites/merc/pyro_{num}.webp', 'WEBP', lossless=True)
        print(f'pyro_{num}.webp  {label}')


if __name__ == '__main__':
    main()

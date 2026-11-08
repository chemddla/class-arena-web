# 백호(격투가 SR 1) 전용 타격 이펙트: 흰 소용돌이 고리 + 사방으로 튀는 불티 (검은 배경 샘플)
#   → assets/sprites/fx/brawler_sr1_hit.webp (밝기 = 불투명도, 색은 흰색 그대로) · 게임에서 그림 가운데 = 맞은 자리
# 사용: python tools/brawler_sr1_hit_build.py
import numpy as np
from PIL import Image

SRC = 'assets/sprites/fx/samples/brawler_sr1_hit_src.png'
OUT = 'assets/sprites/fx/brawler_sr1_hit.webp'
BG, FULL = 18, 235


def main():
    im = np.array(Image.open(SRC).convert('RGB')).astype(float)
    lum = im.max(axis=2)
    a = np.clip((lum - BG) / (FULL - BG), 0, 1)
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    a *= np.clip(np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]) / 12, 0, 1)   # 가장자리 잘린 티 없게
    rgb = np.clip(im / np.maximum(a[..., None], 1e-3), 0, 255)   # 검은 배경과 섞였던 만큼 밝기를 되돌림 (흰색)
    rgb = np.where(a[..., None] > 0.02, rgb, 255)
    # 고리 가운데(어두운 구멍)를 그림 가운데로: 밝은 픽셀의 무게중심 기준 정사각형
    cy, cx = (np.array(np.where(a > 0.5)).mean(axis=1)).round().astype(int)
    r = int(min(cx, w - cx, cy, h - cy))
    out = np.dstack([rgb, a * 255])[cy - r:cy + r, cx - r:cx + r].astype(np.uint8)
    Image.fromarray(out, 'RGBA').save(OUT, 'WEBP', quality=92)
    print(OUT, out.shape[:2], 'center', cx, cy)


if __name__ == '__main__':
    main()

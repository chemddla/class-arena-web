# 무녀 외형 0 (임시 그림, 2026-11-17): 기공사 외형 0 시트에서 금빛 도포 천만 붉은 무복 색으로 바꿈 → assets/sprites/merc/shaman_0.webp
# 사용: python tools/shaman_build.py · 사용자가 샘플을 주면 그 그림으로 교체
# 칸 구성·기준점은 qigong_0과 같음 (22칸)
import numpy as np
from PIL import Image
import colorsys

SRC = 'assets/sprites/merc/qigong_0.webp'
OUT = 'assets/sprites/merc/shaman_0.webp'

def main():
    a = np.array(Image.open(SRC).convert('RGBA')).astype(np.float32) / 255
    rgb = a[..., :3]
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    # 색상(도) 계산
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    # 금빛 천: 색상 34~62도 · 채도 0.28 이상 (피부는 20~32도라 그대로)
    m = (h >= 34) & (h <= 62) & (sat >= 0.28) & (a[..., 3] > 0.05)
    out = a.copy()
    ys, xs = np.where(m)
    for y, x in zip(ys, xs):
        hh, ll, ss = colorsys.rgb_to_hls(*rgb[y, x])
        # 붉은 무복: 색상 354도, 밝기는 조금 낮춰 짙게, 채도는 올림
        nr, ng, nb = colorsys.hls_to_rgb(354 / 360, ll * 0.82, min(1, ss * 1.15 + 0.1))
        out[y, x, :3] = (nr, ng, nb)
    Image.fromarray((out * 255).round().astype(np.uint8), 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('saved', OUT, int(m.sum()), 'px')

if __name__ == '__main__':
    main()

# 창병 외형 1~5 = 기본 외형(lancer_0) 그림의 색만 바꾼 것 (2026-11-10 사용자가 색감 샘플에서 고름)
#   갑옷·투구·창(무채색)의 밝기를 색 띠로 바꿈: 어두운 곳 → 바탕색(검은 쇠) → 밝은 테두리·무늬는 빛 색. 이펙트의 중간 밝기도 같은 빛 색으로 물듦
#   피부·눈 흰자는 그대로 (샘플 확인: exports/job-samples/lancer_0_colors3.png)
#   1 흑철·홍광 · 2 흑철·청광 · 3 흑요석·금테 · 4 흑철·은테 · 5 흑철·녹광
#   몸 시트 assets/sprites/merc/lancer_N.webp + 무쌍난무 자세 assets/sprites/fx/lancer_musou_N.webp (칸 구성은 기본 외형과 같음)
# 사용: python tools/lancer_recolor.py   (기본 외형을 다시 만들면 이것도 다시 돌릴 것)
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

PALETTES = {
    1: ((12, 6, 6), (42, 32, 34), (255, 90, 80)),      # 흑철 · 홍광
    2: ((6, 9, 14), (30, 36, 46), (90, 210, 245)),     # 흑철 · 청광
    3: ((10, 10, 14), (40, 38, 46), (220, 180, 80)),   # 흑요석 · 금테
    4: ((8, 9, 12), (36, 38, 44), (215, 225, 238)),    # 흑철 · 은테
    5: ((6, 12, 8), (30, 40, 34), (110, 245, 140)),    # 흑철 · 녹광
}


def recolor(c, pal):
    rgb = c[..., :3]; a = c[..., 3]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    skin = ndi.binary_closing((a > 0) & (r > 140) & (r - b > 35) & (g > 80) & (r - g > 12), iterations=1)
    lum = rgb.mean(-1)
    eyewhite = ndi.binary_dilation(skin, iterations=3) & (mn > 170) & (mx - mn < 40)
    grey = (a > 0) & (mx - mn < 34) & ~skin & ~eyewhite & (lum < 200)   # 밝은 이펙트 속·흰자·피부·갈색은 그대로
    t = np.clip(lum / 150, 0, 1)[..., None]
    p = np.array(pal, float)
    col = np.where(t < 0.5, p[0] + (p[1] - p[0]) * (t / 0.5), p[1] + (p[2] - p[1]) * ((t - 0.5) / 0.5))
    out = c.copy()
    out[..., :3] = np.where(grey[..., None], col, rgb)
    return out


def main():
    body = np.array(Image.open('assets/sprites/merc/lancer_0.webp').convert('RGBA')).astype(float)
    musou = np.array(Image.open('assets/sprites/fx/lancer_musou_cast.webp').convert('RGBA')).astype(float)
    for v, pal in PALETTES.items():
        for src, out in ((body, f'assets/sprites/merc/lancer_{v}.webp'), (musou, f'assets/sprites/fx/lancer_musou_{v}.webp')):
            Image.fromarray(recolor(src, pal).clip(0, 255).astype(np.uint8), 'RGBA').save(out, 'WEBP', lossless=True)
            print(out)


if __name__ == '__main__':
    main()

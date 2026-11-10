# 전격술사 기본 외형(검은 후드 로브·금빛 테두리) 전용 이펙트 색: 시크릿 레어(예전 기본) 이펙트 시트를 색만 바꿔 <이름>.b.webp로 저장
# 사용: python tools/volt_fx_base_recolor.py   (원본 assets/sprites/fx/volt/<이름>.webp → assets/sprites/fx/volt/<이름>.b.webp)
# 사용자 요청 (2026-11-10): 강화 전 = 푸른색 → 노란색 계열 · 강화 = 검정과 노란색을 조화롭게 섞음
#   픽셀마다 색으로 나눔: 푸른 픽셀(파랑 > 빨강) → 노란 램프 YEL · 금빛 픽셀(빨강 > 파랑) → 검정·노랑 램프 BLK
#   원래 램프(PLASMA_V = index.html PFX_RAMPS.volt, GOLD_V = volt_gold)의 몇 번째 단계 밝기인지 찾아 새 램프의 같은 단계로 옮김 (pixelfx 램프 치환)
#   흰 심·회색 픽셀은 그대로. 과부하(burnout, 붉은 연기)는 바꿀 것이 없어서 그대로 복사
#   새 램프는 index.html PFX_RAMPS.volt_b · volt_gold_b와 같음 (코드로 그리는 줄기·터짐도 같은 색)
import glob, os
import numpy as np
from PIL import Image

D = 'assets/sprites/fx/volt/'
hexrgb = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)
PLASMA = [hexrgb(h) for h in ['#2c2390', '#2457c8', '#1fa0e6', '#a4f6ff', '#ffffff']]
GOLD = [hexrgb(h) for h in ['#6a2c08', '#b8600c', '#f0a01a', '#fff080', '#ffffff']]
YEL = [hexrgb(h) for h in ['#5a3200', '#b06a00', '#f0b400', '#ffe76a', '#ffffff']]
BLK = [hexrgb(h) for h in ['#0c0a07', '#2e2716', '#d9a000', '#ffdc3a', '#fff8c8']]
HALO_A, HALO_BOOST = 200, 1.35
HALO_DARK = hexrgb('#120f09')
lum = lambda c: c[..., 0] * 0.299 + c[..., 1] * 0.587 + c[..., 2] * 0.114


def remap(c, src, dst):
    # c (N,3) → 원래 램프 밝기 사이 어디인지(조각 선형) → 새 램프의 같은 자리 색
    ls = np.array([lum(x) for x in src])
    L = lum(c)
    out = np.empty_like(c)
    idx = np.clip(np.searchsorted(ls, L) - 1, 0, len(ls) - 2)
    t = np.clip((L - ls[idx]) / np.maximum(ls[idx + 1] - ls[idx], 1), 0, 1)[:, None]
    lo = np.array(dst)[idx]; hi = np.array(dst)[idx + 1]
    below = L < ls[0]
    out[:] = lo + (hi - lo) * t
    out[below] = np.array(dst[0]) * (L[below] / max(ls[0], 1))[:, None]   # 가장 어두운 단계보다 어두우면 그만큼 더 어둡게
    return out


def main():
    for f in sorted(glob.glob(D + '*.webp')):
        if f.endswith('.b.webp'): continue
        name = os.path.basename(f)[:-5]
        im = Image.open(f).convert('RGBA')
        a = np.array(im).astype(float)
        c = a[..., :3]
        vis = a[..., 3] > 0
        blue = vis & (c[..., 2] > c[..., 0] + 20)
        gold = vis & (c[..., 0] > c[..., 2] + 20) & (c[..., 1] > c[..., 2])   # 붉은 과부하 연기(초록 낮음)는 빠짐
        if name != 'burnout':
            c[blue] = remap(c[blue], PLASMA, YEL)
            c[gold] = remap(c[gold], GOLD, BLK)
            # 강화: 번개 둘레 반투명 빛 번짐(알파 < HALO_A)은 검은 기운으로 → 노란 번개를 검은 기운이 감쌈 (로브의 검정 바탕·금빛 테두리처럼)
            #   번짐이 옅을수록 더 검게 (가장 옅은 곳 = 검정, HALO_A에 가까울수록 짙은 금빛 쪽으로)
            halo = gold & (a[..., 3] < HALO_A)
            k = (a[..., 3][halo] / HALO_A)[:, None] ** 2
            c[halo] = HALO_DARK * (1 - k) + c[halo] * k * 0.55
            a[..., 3][halo] = np.minimum(255, a[..., 3][halo] * HALO_BOOST)   # 검은 번짐은 밝은 번짐보다 덜 보여서 조금 짙게
        a[..., :3] = c
        Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA').save(D + name + '.b.webp', 'WEBP', lossless=True)
        print(f'{name}: 푸른 {blue.sum()} → 노랑 · 금빛 {gold.sum()} → 검정·노랑')


if __name__ == '__main__':
    main()

# 스케이트 얼음길 그림(바둑판 무늬가 구워진 이미지)에서 바닥 배경과, 빙판 아래에 붙은 얼음 덩어리·흙을 지워 빙판만 남김
# 사용: python tools/skate_ice_build.py <입력 이미지> [출력 webp = assets/sprites/fx/skate_ice.webp]
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

# 빙판 앞면 가장자리(고드름 띠가 시작하는 선)의 (x, y) 지점들. 사이는 직선으로 이음
EDGE = [(0, 279), (250, 280), (300, 286), (390, 294), (520, 294), (640, 293), (710, 288), (800, 284), (900, 281), (1023, 279)]


def main(src, out='assets/sprites/fx/skate_ice.webp'):
    a = np.array(Image.open(src).convert('RGB')).astype(int)
    H, W, _ = a.shape
    lum, sat = a.mean(2), a.max(2) - a.min(2)
    bg = (sat <= 6) & (lum < 130)                       # 구워진 회색 바둑판
    xs = np.arange(W)
    edge = np.interp(xs, [p[0] * (W - 1) / 1023 for p in EDGE], [p[1] for p in EDGE]) + 2
    bg |= np.arange(H)[:, None] > edge[None, :]         # 앞면 가장자리 아래(얼음 덩어리·흙)
    bg |= ndi.binary_dilation(bg, iterations=2) & (sat < 25) & (lum < 150)  # 가장자리에 남은 회색 테두리
    lab, n = ndi.label(~bg)                             # 빙판 하나만 남기고 떨어진 조각 제거
    if n > 1:
        sizes = ndi.sum(~bg, lab, range(1, n + 1))
        bg = lab != (1 + int(np.argmax(sizes)))
    # 잘린 아랫부분은 열마다 맨 아래 줄에서 위로 FADE칸에 걸쳐 서서히 투명하게 (자연스럽게 번지도록)
    FADE = 16
    alpha = np.where(bg, 0.0, 255.0)
    for x in range(W):
        rows = np.where(~bg[:, x])[0]
        if len(rows):
            bottom = rows.max()
            r = np.arange(H)
            alpha[:, x] *= np.clip((bottom - r + 1) / FADE, 0, 1) ** 1.3
    rgba = np.dstack([a.clip(0, 255), alpha]).astype(np.uint8)
    ys, xs2 = np.where(alpha > 0)
    img = Image.fromarray(rgba, 'RGBA').crop((xs2.min(), ys.min(), xs2.max() + 1, ys.max() + 1))
    img.save(out, 'WEBP', lossless=True)
    print(out, img.size)


if __name__ == '__main__':
    main(*sys.argv[1:])

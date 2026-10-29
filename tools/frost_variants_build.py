# 빙결술사 외형 0(frost_0.webp)에서 색 변형 시트 5장 만들기 (칸 구성·크기 모두 같음)
# 사용: python tools/frost_variants_build.py   → assets/sprites/merc/frost_1~5.webp
# 규칙: 피부(얼굴·손)는 그대로 두고 나머지 채도를 낮춤. 검정·흰색 섞음은 채도 5%에서 시작.
#   눈 흰자는 검정을 섞어도 밝게 남기고, 흰색을 섞을 땐 검은 외곽선을 보존
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SRC = 'assets/sprites/merc/frost_0.webp'
CELL_W = 151
# (번호, 이름, 남길 채도, 섞을 색(None / 0 검정 / 255 흰색), 섞는 비율)
VARIANTS = [
    (1, '채도 35%',      0.35, None, 0),
    (2, '채도 15%',      0.15, None, 0),
    (3, '채도 5% + 검정', 0.05, 0,    0.35),
    (4, '채도 5% + 흰색', 0.05, 255,  0.35),
    (5, '채도 60%',      0.60, None, 0),
]


def rgb2hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    dd = np.where(d == 0, 1, d)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) / 6
    h = np.where(d == 0, 0, h)
    s = np.where(mx == 0, 0, d / np.where(mx == 0, 1, mx))
    return np.stack([h, s, mx], -1)


def hsv2rgb(hsv):
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = np.floor(h * 6).astype(int) % 6
    f = h * 6 - np.floor(h * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    return np.stack([np.choose(i, [v, q, p, p, t, v]), np.choose(i, [t, v, v, q, p, p]), np.choose(i, [p, p, t, v, v, q])], -1)


def skin_mask(f):
    # 따뜻한 색 + 어느 정도 채도 + 밝음 = 얼굴·손 (흰 털·회색 머리·어두운 갈색 지팡이는 제외)
    a = f[..., 3] > 0
    hsv = rgb2hsv(f[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    return a & ((h <= 50) | (h >= 320)) & (s > 0.09) & (s < 0.8) & (v > 0.55)


def eye_white(f):
    # 눈 흰자: 얼굴 안에서 파란 눈동자 바로 옆의 밝은 무채색
    a = f[..., 3] > 0
    sk = skin_mask(f)
    hsv = rgb2hsv(f[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    face = ndi.binary_dilation(sk, iterations=3)
    iris = a & face & (h >= 170) & (h <= 240) & (s > 0.3)
    return a & ndi.binary_dilation(iris, iterations=3) & face & (v > 0.75) & (s < 0.25) & ~sk


def recolor(f, keep, target, amt):
    a = f[..., 3] > 0
    move = a & ~skin_mask(f)
    hsv = rgb2hsv(f[..., :3] / 255.)
    hsv[..., 1] *= keep
    rgb = (hsv2rgb(hsv) * 255 + .5).clip(0, 255)
    if target is not None:
        w = np.full(rgb.shape[:2], amt)
        if target == 255: w = w * np.clip((rgb.mean(-1) / 255. - 0.10) / 0.25, 0, 1)   # 검은 외곽선은 그대로
        else: w = np.where(eye_white(f), 0, w)                                          # 눈 흰자는 그대로
        rgb = rgb * (1 - w[..., None]) + target * w[..., None]
    out = f.copy()
    out[move, :3] = (rgb[move] + .5).clip(0, 255).astype(np.uint8)
    return out


def main():
    im = np.array(Image.open(SRC).convert('RGBA'))
    n = im.shape[1] // CELL_W
    for num, label, keep, target, amt in VARIANTS:
        sheet = np.hstack([recolor(im[:, i * CELL_W:(i + 1) * CELL_W], keep, target, amt) for i in range(n)])
        Image.fromarray(sheet, 'RGBA').save(f'assets/sprites/merc/frost_{num}.webp', 'WEBP', lossless=True)
        print(f'frost_{num}.webp  {label}  {sheet.shape[1]}x{sheet.shape[0]}')


if __name__ == '__main__':
    main()

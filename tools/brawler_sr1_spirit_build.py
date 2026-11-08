# 백호(격투가 SR 1) 멸식 - 격 마지막 일격 준비 이펙트: 푸른 빛으로 이루어진 백호 얼굴 (어두운 배경 샘플)
#   → assets/sprites/fx/brawler_sr1_spirit.webp (빛 이펙트라 밝기 = 불투명도로 배경을 투명하게, 게임에서 'lighter'로 덧그림)
# 사용: python tools/brawler_sr1_spirit_build.py
#   - 배경 남색(밝기 ~25)은 투명, 밝을수록 불투명 (BG ~ FULL 사이를 부드럽게)
#   - 오른쪽 아래 별 모양 표시(880~945, 755~820)와 아래 가운데 두 점(525~600, 835~890)은 지움
import numpy as np
from PIL import Image

SRC = 'assets/sprites/fx/samples/brawler_sr1_spirit_src.webp'
OUT = 'assets/sprites/fx/brawler_sr1_spirit.webp'
BG, FULL = 34, 170
ERASE = [(880, 945, 755, 820), (525, 600, 835, 890)]   # (x0, x1, y0, y1)
OUT_W = 320


def main():
    im = np.array(Image.open(SRC).convert('RGB')).astype(float)
    lum = im.max(axis=2)
    a = np.clip((lum - BG) / (FULL - BG), 0, 1) ** 1.2
    for x0, x1, y0, y1 in ERASE: a[y0:y1, x0:x1] = 0
    h, w = a.shape   # 가장자리는 서서히 사라지게 (잘린 티 안 나게)
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]) / 60
    a *= np.clip(edge, 0, 1)
    rgb = np.clip(im * 1.15, 0, 255)
    ys, xs = np.where(a > 0.02)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    out = np.dstack([rgb, a * 255])[y0:y1, x0:x1].astype(np.uint8)
    img = Image.fromarray(out, 'RGBA')
    img = img.resize((OUT_W, round(img.height * OUT_W / img.width)), Image.LANCZOS)
    img.save(OUT, 'WEBP', quality=92)
    print(OUT, img.size)


if __name__ == '__main__':
    main()

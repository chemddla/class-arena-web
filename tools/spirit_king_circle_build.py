# 정령왕 소환진: 성기사 축성 마법진(paladin_consec_cast, 흰 별빛 원)을 다섯 원소 색으로 → assets/sprites/fx/spirit_king_circle.webp
# 사용: python tools/spirit_king_circle_build.py
# 색: 둘레를 따라 불 → 번개 → 바람 → 물 → 대지 → (다시 불), 이웃한 색끼리 부드럽게 섞임
# 칸 FRAMES장: 칸마다 색을 1/FRAMES 바퀴씩 돌려 둠 → 게임에서 차례로 그리면 색이 둘레를 따라 흐름 (타원이라 그림을 돌리지 않고 색만 돌림)
# 원래 그림이 흰색·옅은 금색 위주라, 밝기는 남기고 색만 입힘 (아주 밝고 색이 없는 별빛 가운데만 흰색으로 남김)
# 원소 정령 소환진 assets/sprites/fx/spirit_circle.webp: 같은 원을 원소 색 하나로 (칸 순서 = 불·물·대지·바람·번개, SPIRIT_CIRCLE_ELEMS)
# 크기를 SCALE배로 키워 둠 (게임에서 4칸 폭으로 크게 그릴 때 덜 흐릿하게, 도트 느낌 유지)
import numpy as np
from PIL import Image

SRC = 'assets/sprites/fx/paladin_consec_cast.webp'
OUT = 'assets/sprites/fx/spirit_king_circle.webp'
OUT_ELEM = 'assets/sprites/fx/spirit_circle.webp'
ELEM_COLORS = [(255, 100, 20), (30, 140, 255), (190, 120, 40), (40, 230, 190), (255, 215, 0)]  # 불·물·대지·바람·번개 (게임의 SPIRIT_CIRCLE_ELEMS 순서)
FRAMES = 8
SCALE = 2
EL = np.array([(255, 100, 20), (255, 215, 0), (40, 230, 190), (30, 140, 255), (190, 120, 40)], float)  # 불·번개·바람·물·대지


def ring_color(t):
    x = (t % 1) * len(EL)
    i = np.floor(x).astype(int) % len(EL)
    f = (x - np.floor(x))[..., None]
    f = f * f * (3 - 2 * f)
    return EL[i] * (1 - f) + EL[(i + 1) % len(EL)] * f


def frame(b, rot, solid=None):
    h, w = b.shape[:2]
    lum = b[..., :3].max(axis=2) / 255
    sat = b[..., :3].max(axis=2) - b[..., :3].min(axis=2)
    white = np.clip((lum - 0.9) / 0.1, 0, 1) * np.clip(1 - sat / 40, 0, 1)
    yy, xx = np.mgrid[0:h, 0:w]
    cy = h * 0.62   # 원 가운데 (위쪽은 떠 있는 별빛)
    t = np.arctan2((yy - cy) / (h * 0.38), (xx - w / 2) / (w / 2)) / (2 * np.pi) + rot
    col = ring_color(t) if solid is None else np.broadcast_to(np.array(solid, float), t.shape + (3,))
    k = np.clip(lum * 1.25, 0, 1)[..., None]
    rgb = col * k * (1 - white[..., None]) + 255 * white[..., None]
    return np.dstack([np.clip(rgb, 0, 255), b[..., 3]]).astype(np.uint8)


def main():
    im = Image.open(SRC).convert('RGBA')
    im = im.resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)
    b = np.array(im).astype(float)
    h, w = b.shape[:2]
    sheet = np.zeros((h, w * FRAMES, 4), np.uint8)
    for i in range(FRAMES):
        sheet[:, i * w:(i + 1) * w] = frame(b, i / FRAMES)
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'spirit_king_circle cellW={w} cellH={h} frames={FRAMES}')
    sheet = np.zeros((h, w * len(ELEM_COLORS), 4), np.uint8)
    for i, c in enumerate(ELEM_COLORS):
        sheet[:, i * w:(i + 1) * w] = frame(b, 0, c)
    Image.fromarray(sheet, 'RGBA').save(OUT_ELEM, 'WEBP', lossless=True)
    print(f'spirit_circle cellW={w} cellH={h} frames={len(ELEM_COLORS)}')


if __name__ == '__main__':
    main()

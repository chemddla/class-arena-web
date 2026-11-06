# 화염술사 히든 메테오 그림 (흰 배경 일러스트 2장 1024×886) → assets/sprites/fx/pyro_meteor_fx.webp
# 사용: python tools/pyro_meteor_build.py   (샘플 assets/sprites/fx/samples/pyro_meteor_fall_src.webp · pyro_meteor_impact_src.webp)
# 칸: fall = 연기 꼬리를 끌며 오른쪽 아래로 떨어지는 운석 · impact = 땅에 박혀 구덩이·돌 파편이 튐
#   두 칸 모두 기준점 = 운석 바위 가운데 (어두운 바위 픽셀의 무게중심) → 떨어지던 바위가 그 자리에 그대로 박힘
#   떨어지는 방향(꼬리 → 바위)은 약 44° — 게임은 그림을 돌리지 않고 이 방향으로 떨어뜨림 (PYRO_METEOR_DIR)
# 흰 배경: 가장자리에서 이어진 흰 픽셀 + 갇힌 흰 덩어리(돌 파편 사이) 중 큰 것 → 배경, 가장자리·흰 번짐·불길 바깥 살구빛 테두리는 흰색을 빼고 반투명으로 (연기 끝이 부드럽게)
# 그림체가 도트가 아니라 일러스트라 매끄럽게 줄이고(LANCZOS) 손실 압축 webp로 저장 (용량)
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SRC = {'fall': 'assets/sprites/fx/samples/pyro_meteor_fall_src.webp', 'impact': 'assets/sprites/fx/samples/pyro_meteor_impact_src.webp'}
OUT = 'assets/sprites/fx/pyro_meteor_fx.webp'
K = 0.5


def cut(path):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    white = (im.min(axis=2) > 236) & (im.max(axis=2) - im.min(axis=2) < 18)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    sz = ndi.sum(white, lab, range(1, n + 1))
    bg = np.isin(lab, edge[edge > 0]) | np.isin(lab, 1 + np.where(sz >= 60)[0])
    rim = ~bg & ndi.binary_dilation(bg, iterations=3)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)
    # 연기·불길 바깥의 흰 번짐(채도 낮고 밝은 픽셀)도 흰색을 빼고 반투명으로 → 어두운 땅 위에서 하얀 테두리가 뜨지 않게
    haze = ~bg & (im.min(axis=2) > 150) & (im.max(axis=2) - im.min(axis=2) < 28)
    a = np.where(haze, np.minimum(a, np.clip((255 - im.min(axis=2)) / 150, 0, 1)), a)
    rim = rim | haze
    # 불길 바깥 살구빛 테두리(흰 배경 위에 그린 바깥 빛 번짐): 배경에서 12px 안쪽의 밝은 픽셀은 흰색을 빼고 반투명 불꽃색으로
    near = ndi.binary_dilation(bg, iterations=12) & ~bg
    glow = near & (im.min(axis=2) > 140)
    a = np.where(glow, np.minimum(a, np.clip((255 - im.min(axis=2)) / 105, 0, 1)), a)
    rim = rim | glow
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    rock = (im.max(axis=2) < 80) & (a > 0.9)
    ys, xs = np.where(rock)
    sel = (xs > im.shape[1] * 0.4) & (ys > im.shape[0] * 0.4)
    cx, cy = xs[sel].mean(), ys[sel].mean()
    ys, xs = np.where(a > 0.02)
    x0, y0 = xs.min(), ys.min()
    rgba = np.dstack([im, a * 255])[y0:ys.max() + 1, x0:xs.max() + 1].astype(np.uint8)
    img = Image.fromarray(rgba, 'RGBA')
    img = img.resize((round(img.width * K), round(img.height * K)), Image.LANCZOS)
    return img, (cx - x0) * K, (cy - y0) * K


def main():
    parts = [(k, *cut(p)) for k, p in SRC.items()]
    W = sum(p[1].width for p in parts) + 2 * len(parts)
    H = max(p[1].height for p in parts)
    atlas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    x, out = 0, []
    for k, img, ax, ay in parts:
        atlas.paste(img, (x, 0))
        out.append(f'{k}: [[{x},0,{img.width},{img.height},{ax:.1f},{ay:.1f}]]')
        x += img.width + 2
    atlas.save(OUT, 'WEBP', quality=88, method=6)
    print('PYRO_METEOR_FX anims: { ' + ', '.join(out) + ' }')


if __name__ == '__main__':
    main()

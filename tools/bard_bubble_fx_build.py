# 음유시인 기본 공격 물방울 구슬 · 맞았을 때 터지는 빛 샘플(어두운 회색 배경) → 이펙트 아틀라스 assets/sprites/fx/bard_bubble_fx.webp
# 사용: python tools/bard_bubble_fx_build.py   (샘플 assets/sprites/fx/samples/bard_bubble_src.png · bard_bubble_hit_src.png)
#   bubble = 날아가는 하늘색 물방울 (둥글어서 방향 상관없음) · burst = 맞은 자리에서 터지는 하늘빛 별빛
# 샘플 정리: 배경색(가장자리 중앙값)과 얼마나 다른지로 투명도를 정하고 배경색을 빼서 색을 되살림
#   물방울은 테두리까지 단단한 구슬이라 투명도를 빨리 채우고(SOLID), 터지는 빛은 빛살 끝이 옅게 남게 천천히 채움
# 프레임 [x, y, w, h, 기준점x, 기준점y]: 기준점 = 그림 가운데(물방울 가운데 · 폭발 가운데)
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

S = 'assets/sprites/fx/samples/'
OUT = 'assets/sprites/fx/bard_bubble_fx.webp'
PARTS = [('bubble', 'bard_bubble_src.png', 60), ('burst', 'bard_bubble_hit_src.png', 140)]  # (이름, 파일, 불투명해지는 배경색과의 차이)


def main():
    pieces, frames = [], []
    for nm, fn, solid in PARTS:
        im = np.array(Image.open(S + fn).convert('RGB')).astype(float)[2:-2, 2:-2]
        ring = np.concatenate([im[:3].reshape(-1, 3), im[-3:].reshape(-1, 3), im[:, :3].reshape(-1, 3), im[:, -3:].reshape(-1, 3)])
        K = np.median(ring, axis=0)
        d = np.abs(im - K).max(axis=2)
        a = np.clip((d - 10) / solid, 0, 1)
        rgb = np.where(a[..., None] > 0, K + (im - K) / np.maximum(a, 0.05)[..., None], 0).clip(0, 255)
        m = a > 0.04
        lab, n = ndi.label(m, structure=np.ones((3, 3)))
        areas = ndi.sum(m, lab, range(1, n + 1))
        a = np.where(np.isin(lab, 1 + np.where(areas >= 3)[0]), a, 0)
        ys, xs = np.where(a > 0.04)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        if nm == 'bubble':  # 가운데 = 가장 큰 덩어리(물방울)의 가운데
            big = lab == np.argmax(areas) + 1
            by, bx = np.where(big)
            cx, cy = (bx.min() + bx.max()) / 2, (by.min() + by.max()) / 2
        else:  # 터지는 빛 = 밝은 중심의 가운데
            core = a > 0.9
            cy, cx = ndi.center_of_mass(core)
        pieces.append((nm, np.dstack([rgb, a * 255])[y0:y1, x0:x1].astype(np.uint8), round(cx - x0), round(cy - y0)))
    W = sum(p.shape[1] + 2 for _, p, _, _ in pieces); H = max(p.shape[0] for _, p, _, _ in pieces)
    atlas = np.zeros((H, W, 4), np.uint8); x = 0
    for nm, p, ax, ay in pieces:
        atlas[:p.shape[0], x:x + p.shape[1]] = p
        frames.append(f'{nm}: [[{x},0,{p.shape[1]},{p.shape[0]},{ax},{ay}]]')
        x += p.shape[1] + 2
    Image.fromarray(atlas, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('anims: { ' + ', '.join(frames) + ' }')


if __name__ == '__main__':
    main()

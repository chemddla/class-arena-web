# 음유시인 시크릿 레어 전용 히든 [앙코르] 이펙트 샘플 3장(어두운 회색 배경) → 이펙트 아틀라스 assets/sprites/fx/bard_sr1_encore_fx.webp
# 사용: python tools/bard_sr1_encore_fx_build.py   (샘플 assets/sprites/fx/samples/bard_sr1_encore_cast_src.png · _burst_src.png · _ally_src.png)
#   cast  = 금빛 빛기둥·물방울 + 바닥 고리 (시전하는 동안 시전자 발밑에 크게)
#   burst = 금빛·보랏빛 소용돌이 + 겹친 금빛 고리 (발동할 때 시전자 발밑에 크게)
#   ally  = 오선·음표가 소용돌이치는 푸른 구체 + 아래 금빛 마법진 (발동할 때 효과를 받은 아군 발밑, 기본 외형의 아군 마법진 대신)
# 샘플 정리:
#   - 빛나는 그림이라 배경색(가장자리 중앙값)과 얼마나 다른지로 투명도를 정하고, 배경색을 빼서 빛 색을 되살림
#   - burst 위쪽 제목 글씨("#25 발동 …")와 오른쪽 아래 ✦ 워터마크 지움
# 프레임 [x, y, w, h, 기준점x, 기준점y]: 기준점 = 바닥 고리 가운데 → 유닛 발밑에 맞춤
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

S = 'assets/sprites/fx/samples/bard_sr1_encore_'
OUT = 'assets/sprites/fx/bard_sr1_encore_fx.webp'
# (이름, 파일, 지울 상자들 (x0, y0, x1, y1), 바닥 고리를 찾을 아래쪽 비율)
PARTS = [('cast', 'cast_src.png', [], 0.72), ('burst', 'burst_src.png', [(0, 0, 1024, 62), (895, 445, 970, 515)], 0.68),
         ('ally', 'ally_src.png', [], 0.66)]


def key(im):
    ring = np.concatenate([im[:4].reshape(-1, 3), im[-4:].reshape(-1, 3), im[:, :4].reshape(-1, 3), im[:, -4:].reshape(-1, 3)])
    K = np.median(ring, axis=0)
    d = np.clip(im - K, 0, None).max(axis=2)
    a = np.clip((d - 8) / 150, 0, 1)
    rgb = np.where(a[..., None] > 0, K + (im - K) / np.maximum(a, 0.05)[..., None], 0).clip(0, 255)
    return rgb, a


def main():
    pieces, frames = [], []
    for nm, fn, boxes, low in PARTS:
        im = np.array(Image.open(S + fn).convert('RGB')).astype(float)[3:-3, 3:-3]
        rgb, a = key(im)
        for x0, y0, x1, y1 in boxes: a[max(0, y0 - 3):y1 - 3, max(0, x0 - 3):x1 - 3] = 0
        m = a > 0.04
        lab, n = ndi.label(m, structure=np.ones((3, 3)))
        areas = ndi.sum(m, lab, range(1, n + 1))
        a = np.where(np.isin(lab, 1 + np.where(areas >= 3)[0]), a, 0)  # 압축 티끌
        ys, xs = np.where(a > 0.04)
        by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        # 바닥 고리 가운데: 아래쪽 밝은 금빛 픽셀 범위의 가운데
        H = by1 - by0
        g = (a > 0.6) & (rgb[..., 0] > 180) & (rgb[..., 2] < 170)
        g[:by0 + int(H * low)] = False
        gy, gx = np.where(g)
        ax, ay = (gx.min() + gx.max()) / 2, (gy.min() + gy.max()) / 2
        pieces.append((nm, np.dstack([rgb, a * 255])[by0:by1, bx0:bx1].astype(np.uint8), round(ax - bx0), round(ay - by0)))
    W = sum(p.shape[1] + 2 for _, p, _, _ in pieces); Hh = max(p.shape[0] for _, p, _, _ in pieces)
    atlas = np.zeros((Hh, W, 4), np.uint8); x = 0
    for nm, p, ax, ay in pieces:
        atlas[:p.shape[0], x:x + p.shape[1]] = p
        frames.append(f'{nm}: [{x},0,{p.shape[1]},{p.shape[0]},{ax},{ay}]')
        x += p.shape[1] + 2
    Image.fromarray(atlas, 'RGBA').save(OUT, 'WEBP', quality=90)
    print('frames: { ' + ', '.join(frames) + ' }')


if __name__ == '__main__':
    main()

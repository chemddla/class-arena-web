# 음유시인 노래 스킬을 받은 아군 머리 위에 떠오르는 표식 샘플(세로 3판, 어두운 판 배경) → 이펙트 아틀라스 assets/sprites/fx/bard_song_buff_fx.webp
# 사용: python tools/bard_song_buff_fx_build.py   (샘플 assets/sprites/fx/samples/bard_song_buff_src.png)
#   anthem = 불타는 검 (전투의 노래) · ballad = 육각 빛 그물 위 방패 (수호의 선율) · swift = 초록 바람 날개 (질풍의 리듬)
# 샘플 정리: 판 위 칸 번호 글씨("#2" 등)는 판 밖이라 잘라 낼 때 빠짐. 판 배경색(가장자리 중앙값)과 얼마나 다른지로 투명도를 정하고
#   배경색을 빼서 빛 색을 되살림 (방패 둘레 푸른 빛·바람 끝은 반투명)
# 프레임 [x, y, w, h, 기준점x, 기준점y]: 기준점 = 그림 가운데
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SRC = 'assets/sprites/fx/samples/bard_song_buff_src.png'
OUT = 'assets/sprites/fx/bard_song_buff_fx.webp'
PARTS = [('anthem', 4, 20, 169, 188), ('ballad', 4, 228, 169, 408), ('swift', 4, 440, 169, 619)]  # (이름, 판 안쪽 x0, y0, x1, y1)


def main():
    src = np.array(Image.open(SRC).convert('RGB')).astype(float)
    pieces, frames = [], []
    for nm, x0, y0, x1, y1 in PARTS:
        im = src[y0:y1, x0:x1]
        ring = np.concatenate([im[:3].reshape(-1, 3), im[-3:].reshape(-1, 3), im[:, :3].reshape(-1, 3), im[:, -3:].reshape(-1, 3)])
        K = np.median(ring, axis=0)
        d = np.abs(im - K).max(axis=2)
        a = np.clip((d - 10) / 90, 0, 1)
        rgb = np.where(a[..., None] > 0, K + (im - K) / np.maximum(a, 0.05)[..., None], 0).clip(0, 255)
        m = a > 0.04
        lab, n = ndi.label(m, structure=np.ones((3, 3)))
        areas = ndi.sum(m, lab, range(1, n + 1))
        a = np.where(np.isin(lab, 1 + np.where(areas >= 4)[0]), a, 0)
        ys, xs = np.where(a > 0.04)
        by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        pieces.append((nm, np.dstack([rgb, a * 255])[by0:by1, bx0:bx1].astype(np.uint8)))
    W = sum(p.shape[1] + 2 for _, p in pieces); H = max(p.shape[0] for _, p in pieces)
    atlas = np.zeros((H, W, 4), np.uint8); x = 0
    for nm, p in pieces:
        atlas[:p.shape[0], x:x + p.shape[1]] = p
        frames.append(f'{nm}: [{x},0,{p.shape[1]},{p.shape[0]},{p.shape[1] // 2},{p.shape[0] // 2}]')
        x += p.shape[1] + 2
    Image.fromarray(atlas, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('frames: { ' + ', '.join(frames) + ' }')


if __name__ == '__main__':
    main()

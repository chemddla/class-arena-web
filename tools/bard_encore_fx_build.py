# 음유시인 히든 [앙코르] 발동 이펙트 샘플(검은 배경 1장, 2개) → 이펙트 아틀라스 assets/sprites/fx/bard_encore_fx.webp
# 사용: python tools/bard_encore_fx_build.py [샘플 폴더]  (기본 assets/sprites/fx/samples, 파일 bard_encore_fx_src.webp)
#   왼쪽 = 금빛 소리 고리 위로 오선·음표가 펼쳐짐 (stage: 시전자 발밑에 크게) · 오른쪽 = 마법진·화살표·방패 (ally: 아군마다 발밑에)
# 샘플 정리:
#   - 빛나는 그림이라 검은 배경을 밝기로 뺌 (투명도 = 가장 밝은 채널, 색은 투명도로 나눠 복원)
#   - 오른쪽 아래 ✦ 워터마크 지움 (마법진 오른쪽 고리와 겹치지 않는 회색 픽셀만)
# 프레임 [x, y, w, h, 기준점x, 기준점y]: 기준점 = 바닥 고리(마법진) 가운데 → 유닛 발밑에 맞춤
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = 'assets/sprites/fx/bard_encore_fx.webp'
# (이름, x0, x1, 바닥 고리 가운데 x, y) — 샘플 좌표
PARTS = [('stage', 0, 494, 255, 430), ('ally', 494, 1024, 740, 425)]


def main(folder):
    im = np.array(Image.open(f'{folder}/bard_encore_fx_src.webp').convert('RGB')).astype(float)
    v = im.max(axis=2)
    a = np.clip((v - 18) / 200, 0, 1)
    rgb = np.where(a[..., None] > 0, im / np.maximum(v, 1)[..., None] * 255, 0).clip(0, 255)
    # ✦ 워터마크: 채도 낮은 회색 픽셀
    sat = im.max(axis=2) - im.min(axis=2)
    wm = np.zeros_like(a, bool); wm[462:510, 905:965] = True
    a[wm & (sat < 40)] = 0
    m = a > 0.05
    lab, n = ndi.label(m)
    areas = ndi.sum(m, lab, range(1, n + 1))
    a = np.where(np.isin(lab, 1 + np.where(areas >= 6)[0]), a, 0)
    pieces, frames = [], []
    for nm, x0, x1, cx, cy in PARTS:
        ys, xs = np.where(a[:, x0:x1] > 0.05)
        bx0, bx1, by0, by1 = xs.min() + x0, xs.max() + x0 + 1, ys.min(), ys.max() + 1
        pieces.append((nm, np.dstack([rgb, a * 255])[by0:by1, bx0:bx1].astype(np.uint8), cx - bx0, cy - by0))
    W = sum(p.shape[1] + 2 for _, p, _, _ in pieces); H = max(p.shape[0] for _, p, _, _ in pieces)
    atlas = np.zeros((H, W, 4), np.uint8); x = 0
    for nm, p, ax, ay in pieces:
        atlas[:p.shape[0], x:x + p.shape[1]] = p
        frames.append(f'{nm}: [{x},0,{p.shape[1]},{p.shape[0]},{ax},{ay}]')
        x += p.shape[1] + 2
    Image.fromarray(atlas, 'RGBA').save(OUT, 'WEBP', quality=90)
    print('frames: { ' + ', '.join(frames) + ' }')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/fx/samples')

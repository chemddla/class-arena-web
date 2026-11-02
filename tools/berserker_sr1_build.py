# 광전사 시크릿 레어(흑사자: 검은 갈기·붉은 눈·검은 판금·쌍도끼) 샘플 → 캐릭터 시트 assets/sprites/merc/berserker_sr1.webp
# 사용: python tools/berserker_sr1_build.py   (샘플은 assets/sprites/fx/samples/berserker_sr1_*_src.png)
# 칸 순서 (동작 샘플이 오는 대로 늘림): 0 대기
# 샘플 정리:
#   - 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움, 흰 배경과 섞인 2px 테두리는 흰색을 빼서 투명도·본래 색을 되살림 (berserker_build.load와 같음)
#   - 몸 안에 갇힌 흰 배경(팔과 도끼 자루 사이)도 지움
#   - 위쪽 제목 글씨("1. 대기 (Idle) - 1개")는 몸에서 떨어진 조각이라 지움
#   - 크기는 대기 자세 갈기 꼭대기~발을 광전사 0번 대기와 같은 키(TARGET_H)로
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/berserker_sr1_'
OUT = 'assets/sprites/merc/berserker_sr1.webp'
TARGET_H = 86  # 광전사 0번 대기와 같은 키

# (샘플 이름, 칸 이름, 대기 배율에 곱할 값)
FRAMES = [
    ('idle', 'idle', 1),
]


def load(name):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    # 몸 안에 갇힌 흰 배경 (팔과 도끼 자루 사이 등): 아주 하얀 8px 넘는 덩어리
    ids = np.arange(1, n + 1)
    bg |= np.isin(lab, ids[(ndi.sum(white, lab, ids) >= 8) & (ndi.mean(im.min(axis=2), lab, ids) > 235)])
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    # 가장 큰 덩어리(몸)만 (제목 글씨·티끌은 지움)
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m))
    big = np.argmax(ndi.sum(m, lab, range(1, n + 1))) + 1
    a = np.where(lab == big, a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # 발 가운데 (아래 8%의 불투명 픽셀 가운데)
    k = rgba[..., 3] > 0
    foot = np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()
    return rgba, foot


def main():
    cuts = {f[1]: load(f[0]) for f in FRAMES}
    base = TARGET_H / cuts['idle'][0].shape[0]
    pieces = []
    for src, name, k in FRAMES:
        rgba, foot = cuts[name]
        sc = base * k
        pieces.append((name, shrink(rgba, sc), foot * sc))
    L = max(int(np.ceil(c)) for _, _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 4
    H = max(p.shape[0] for _, p, _ in pieces) + 5
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = H - 2 - p.shape[0]
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'sr1 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)}')


if __name__ == '__main__':
    main()

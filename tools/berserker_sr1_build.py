# 광전사 시크릿 레어(흑사자: 검은 갈기·붉은 눈·검은 판금·쌍도끼) 샘플 → 캐릭터 시트 assets/sprites/merc/berserker_sr1.webp
# 사용: python tools/berserker_sr1_build.py   (샘플은 assets/sprites/fx/samples/berserker_sr1_*_src.png)
# 칸 순서 (동작 샘플이 오는 대로 늘림): 0 대기 · 1~3 걷기 · 4 피격 · 5~7 쓰러짐
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

# (샘플 이름, 칸 이름, 키를 대기와 같게 맞춘 뒤 곱할 값, 샘플 안 몇 번째 그림(왼쪽부터))
FRAMES = [
    ('idle', 'idle', 1, 0),
    ('walk_a', 'walk0', 1, 0), ('walk_b', 'walk1', 1, 0), ('walk_b', 'walk2', 1, 1),  # 걷기 3칸 (walk_b 한 장에 두 칸)
    ('hurt', 'hurt', 1, 0),
    ('down', 'down0', 1, 0), ('down', 'down1', 'down0', 1), ('down', 'down2', 'down0', 2),  # 쓰러짐 3칸: 누운 칸은 키로 못 재서 첫 칸(서 있음) 배율을 같이 씀
]


DROP = {'walk_b': [(0, 18, 140, 200)], 'down': [(0, 723, 147, 155)]}  # 지울 상자 (x0, x1, y0, y1): 걷기 샘플 왼쪽 끝에 잘려 들어온 앞 칸 도끼, 쓰러짐 샘플 아래 어두운 띠 (세 칸을 한 덩어리로 이어 붙였음)


def load(name, pick=0):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    # 몸 안에 갇힌 흰 배경 (팔과 도끼 자루 사이 등): 아주 하얀 3px 넘는 덩어리 (갑옷 하이라이트는 회색이라 남음)
    ids = np.arange(1, n + 1)
    bg |= np.isin(lab, ids[(ndi.sum(white, lab, ids) >= 3) & (ndi.mean(im.min(axis=2), lab, ids) > 232)])
    # 갇힌 틈 중 흰 배경과 섞여 조금 어두운 것(밝기 185 넘는 무채색 덩어리, 갑옷 하이라이트는 2px 안팎이라 빠짐)도 배경
    lt = (im.min(axis=2) > 185) & (im.max(axis=2) - im.min(axis=2) < 30) & ~bg
    lab2, n2 = ndi.label(lt)
    ids2 = np.arange(1, n2 + 1)
    bg |= np.isin(lab2, ids2[ndi.sum(lt, lab2, ids2) >= 4])
    for x0, x1, y0, y1 in DROP.get(name, ()): bg[y0:y1, x0:x1] = True
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    # 큰 덩어리(몸)만 (제목 글씨·옆 칸에서 잘려 들어온 도끼·티끌은 지움). 한 장에 여러 칸이면 왼쪽부터 pick번째
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m))
    sz = ndi.sum(m, lab, range(1, n + 1))
    bigs = [i + 1 for i in range(n) if sz[i] >= sz.max() * 0.3]
    bigs.sort(key=lambda i: np.where(lab == i)[1].mean())
    a = np.where(lab == bigs[pick], a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # 발 가운데 (아래 8%의 불투명 픽셀 가운데)
    k = rgba[..., 3] > 0
    foot = np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()
    return rgba, foot


def main():
    cuts = {f[1]: load(f[0], f[3]) for f in FRAMES}
    pieces = []
    scale = {}
    for src, name, k, _ in FRAMES:
        rgba, foot = cuts[name]
        # 샘플마다 그린 크기가 달라 칸마다 키(갈기 꼭대기~발)로 맞춤. k가 칸 이름이면 그 칸 배율을 그대로 (누운 칸)
        sc = scale[k] if isinstance(k, str) else TARGET_H / rgba.shape[0] * k
        scale[name] = sc
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

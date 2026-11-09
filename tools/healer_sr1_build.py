# 성녀 시크릿 레어 1 교체 (2026-11-09): 분홍 단발 천사 (후광·분홍빛 날개·연두 금빛 로브·날개 달린 하프 지팡이)
#   → assets/sprites/merc/healer_sr1.webp
# 사용: python tools/healer_sr1_build.py
# 샘플 (assets/sprites/merc/samples/healer_sr1_edit_*): 같은 그림을 흰 배경(1)·검은 배경(2)으로 받은 한 장 (1024×979, 동작 이름 글씨 포함)
#   대기 1 · 이동(비행) 4 · 일반공격(치유) 2 (지팡이 끝에 초록 빛 → 초록 거품을 앞으로 뿜음) · 피격 1 · 쓰러짐 2 (주저앉음 → 누움, 하프가 떨어짐)
# 칸 순서 (healer_sr1): 0 대기 · 1~4 비행 · 5~6 일반공격 (치유) · 7 피격 · 8~9 쓰러짐
#   스킬 샘플은 없어서 게임에서는 일반공격 두 칸을 씀 (index.html SECRET_SKIN_SHEETS.healer_sr1)
# 배경 지우기: 두 장은 같은 자리에 있지만 다시 그려져 윤곽이 조금씩 다름
#   흰 장이 하얗고 검은 장이 까만 곳 = 배경 · 두 장의 차이(흰 - 검은)로 알파를 구함 (치유 빛·거품의 반투명)
#   거의 불투명(0.85 넘음)한 덩어리는 작은 틈(다시 그린 윤곽 차이)을 메워 완전히 불투명 → 색은 흰 장, 반투명 곳의 색은 검은 장 / 알파
# 크기: 모든 동작이 한 장에 같은 크기로 그려져 있어 한 배율 (K)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from archer0_build import shrink_soft

D = 'assets/sprites/merc/samples/healer_sr1_edit_'
OUT = 'assets/sprites/merc/healer_sr1.webp'
K = 0.6   # 샘플 → 시트 배율 (대기 머리끝~발 약 100px, healer_0과 같은 키)
# (칸 이름, 상자 x0 y0 x1 y1 — 글씨는 상자 밖, 기준점 x 비율 (None = 발 가운데))
FRAMES = [
    ('idle', (52, 34, 282, 238), None),
    ('fly0', (58, 266, 292, 468), None),
    ('fly1', (303, 266, 524, 468), None),
    ('fly2', (540, 266, 762, 468), None),
    ('fly3', (772, 266, 994, 468), None),
    ('atk0', (36, 498, 298, 714), None),
    ('atk1', (298, 498, 712, 714), None),
    ('hurt', (44, 744, 234, 952), None),
    ('down0', (328, 748, 534, 955), 0.55),
    ('down1', (584, 824, 842, 968), 0.42),
]


def rgb(src):
    return np.array(Image.open(D + src).convert('RGB')).astype(float)


def matte(W, B):
    d = W - B
    a = np.clip(1 - d.mean(axis=2) / 255, 0, 1)
    bg = (W.min(axis=2) > 236) & (B.max(axis=2) < 26)
    # 동작 이름 글씨: 흰 장에선 검고 검은 장에선 하얀 곳 (그림에는 없음) + 둘레 2px
    bg |= ndi.binary_dilation((W.max(axis=2) < 110) & (B.min(axis=2) > 140), iterations=2)
    a[bg] = 0
    solid = ndi.binary_closing(a > 0.85, iterations=2) & ~bg
    solid = ndi.binary_opening(solid, iterations=1)
    # 작은 반투명 티끌(거품 가운데처럼 진한 점)만 불투명이 되지 않게: 30px 넘는 덩어리만 몸
    lab, n = ndi.label(solid)
    sz = ndi.sum(solid, lab, range(1, n + 1))
    solid = np.isin(lab, 1 + np.where(sz >= 30)[0])
    a = np.where(solid, 1.0, a)
    a = np.where(a < 0.05, 0, a)
    col = np.where(solid[..., None], W, (B / np.maximum(a, 1e-3)[..., None])).clip(0, 255)
    return np.dstack([col, a * 255]), solid


def foot_x(body):
    ys, xs = np.where(body)
    y1 = ys.max(); return xs[ys >= y1 - max(3, int((y1 - ys.min()) * 0.06))].mean(), y1


def main():
    W, B = rgb('1_white_src.webp'), rgb('2_black_src.webp')
    pieces = []
    for name, (x0, y0, x1, y1), fr in FRAMES:
        rgba, solid = matte(W[y0:y1, x0:x1], B[y0:y1, x0:x1])
        # 몸에서 떨어진 것: 큰 덩어리(몸)와 그 둘레 60px 안의 빛·거품만
        m = rgba[..., 3] > 0
        lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
        big = int(np.argmax(ndi.sum(solid, lab, range(1, n + 1)))) + 1
        near = ndi.binary_dilation(lab == big, iterations=60)
        keep = np.isin(lab, np.unique(lab[near & (lab > 0)]))
        rgba[..., 3] = np.where(keep, rgba[..., 3], 0); solid &= (lab == big)
        ys, xs = np.where(rgba[..., 3] > 0)
        sy0, sy1, sx0, sx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba, solid = rgba[sy0:sy1, sx0:sx1], solid[sy0:sy1, sx0:sx1]
        fx, fy = foot_x(solid)
        if fr is not None: fx = rgba.shape[1] * fr
        p = shrink_soft(rgba, solid, K)   # 두 장으로 알파를 구해 흰 테두리 찌꺼기가 없음 — defringe는 가는 흰 후광을 지워서 안 씀
        pieces.append((name, p, fx * K, fy * K))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} → {p.shape[1]}x{p.shape[0]}, 발 ({fx * K:.0f}, {fy * K:.0f})')
    L = max(int(np.ceil(fx)) for _, _, fx, _ in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - fx)) for _, p, fx, _ in pieces) + 3
    U = max(int(np.ceil(fy)) for _, _, _, fy in pieces) + 3
    Bm = max(int(np.ceil(p.shape[0] - fy)) for _, p, _, fy in pieces) + 2
    cw, ch = L + R, U + Bm
    sheet = np.zeros((ch, cw * len(pieces), 4), np.uint8)
    for i, (name, p, fx, fy) in enumerate(pieces):
        x = i * cw + L - int(round(fx)); y = U - int(round(fy))
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'healer_sr1 cellW={cw} cellH={ch} anchorX={L} anchorY={U} count={len(pieces)}')


if __name__ == '__main__':
    main()

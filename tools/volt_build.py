# 전격술사 기본 외형 0 (2026-11-10 사용자 샘플: 검은 후드 로브·금빛 번개 테두리·금빛 띠·검은 단발·노란 눈, 흰 배경) → assets/sprites/merc/volt_0.webp
# 사용: python tools/volt_build.py   (샘플 assets/sprites/fx/samples/volt0_*_src.png)
# 예전 기본 외형(비니·안경)은 시크릿 레어 1 → tools/volt_sr1_build.py
# 칸 순서: 0 대기 (몸 양옆 금빛 정전기) · 1~4 걷기 · 5 기본 공격 (두 손을 앞으로, 손 둘레 금빛 전기) · 6 피격 (뒤로 젖힘, 금빛 전기) · 7 쓰러짐 (누움)
#   · 8~9 방전 (두 주먹을 가슴 앞에 모음·금빛 전기 → 두 팔을 활짝 펴고 떠오름)
#   · 10~11 전자포 (옆구리에 금빛 구체를 모음 → 손바닥을 앞으로 내밂)
#   쓰러짐 = 피격 → 누움 (사용자: "쓰러짐은 피격 모션 같이 활용"). 스킬 샘플이 오기 전까지 스킬 자세는 기본 공격 칸
# 크기: 샘플이 모두 같은 확대 배율이라 (선 키 211~213, 얼굴 피부 넓이 제곱근 23~24.7로 ±5% 안) 한 배율을 씀
#   = 대기 자세 키(후드 꼭대기~신발 바닥)를 TARGET_H로. 얼굴 크기는 확인용으로만 찍음
#   방전·전자포 샘플은 더 작게 그려져 있어서 (얼굴 18.7·13.6) 얼굴 크기를 대기 자세에 맞춘 배율을 곱함 (FACE_SCALE)
#   → 모은 자세 선 키 172×1.23 = 212로 걷기 샘플과 같아서 얼굴 기준이 맞음
# 몸 둘레 금빛 전기 조각(몸과 떨어진 작은 덩어리)도 칸에 넣음. 한글 이름표(금빛이 없는 검은 덩어리)는 뺌
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
from pyro_build import prep, defringe

S = 'assets/sprites/fx/samples/'
OUT = 'assets/sprites/merc/volt_0.webp'
TARGET_H = 88

FRAMES = [
    ('idle', 'volt0_idle_src.png', 0),
    ('walk0', 'volt0_walk_src.png', 0), ('walk1', 'volt0_walk_src.png', 1),
    ('walk2', 'volt0_walk_src.png', 2), ('walk3', 'volt0_walk_src.png', 3),
    ('atk', 'volt0_atk_src.png', 0),
    ('hurt', 'volt0_hurt_src.png', 0),
    ('down', 'volt0_down_src.png', 0),
    ('dis0', 'volt0_dis0_src.png', 0), ('dis1', 'volt0_dis1_src.png', 0),
    ('rail0', 'volt0_rail0_src.png', 0), ('rail1', 'volt0_rail1_src.png', 0),
]
FACE_SCALE = {'dis0', 'dis1', 'rail0', 'rail1'}
LIFT = {'dis1': 6}   # 방전 터뜨림은 샘플에서 발이 떠 있어서 바닥보다 6px 위에 둠


def gold(c):
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    return (R > 150) & (G > 110) & (B < 110) & (R - B > 80)


def figures(path):
    im, a = prep(S + path)
    fg = a > 0.3
    bl, n = ndi.label(ndi.binary_dilation(fg, iterations=2))
    keep = np.zeros_like(fg)
    for i in range(1, n + 1):
        m = (bl == i) & fg
        if m.sum() > 150 and not (gold(im) & m).any(): continue   # 이름표 글자
        keep |= m
    fl, fn = ndi.label(ndi.binary_dilation(keep, iterations=9))
    out = []
    for i in range(1, fn + 1):
        m = (fl == i) & keep
        if m.sum() < 1500: continue
        out.append((np.where(m.any(axis=0))[0].min(), m))
    out.sort(key=lambda t: t[0])
    return im, a, [m for _, m in out]


def skin_mask(c, alpha):
    R, G, B = (c[..., i].astype(float) for i in range(3))
    return (alpha > 0.8) & (R > 170) & (R > G + 12) & (G > B + 5) & (B > 110)


def face_size(im, a, m):
    ys = np.where(m.any(axis=1))[0]
    sk = skin_mask(im, a) & m
    sk[ys.min() + int((ys.max() - ys.min()) * 0.5):] = False
    lb, nb = ndi.label(sk)
    if nb == 0: return None
    return float(np.sqrt(ndi.sum(sk, lb, range(1, nb + 1)).max()))


def main():
    cache, raw = {}, {}
    for name, path, idx in FRAMES:
        if path not in cache: cache[path] = figures(path)
        im, a, figs = cache[path]
        m = figs[idx]
        ys, xs = np.where(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.dstack([im, np.where(m, a, 0) * 255])[y0:y1, x0:x1]
        k = rgba[..., 3] > 128
        if name == 'down':
            cols = np.where(k.any(axis=0))[0]; foot = (cols.min() + cols.max()) / 2
        else:   # 발: 아래 8% 줄의 불투명 픽셀 가운데 (금빛 전기 조각은 빼고)
            body = k & ~gold(rgba[..., :3])
            foot = np.where(body[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()
        raw[name] = (rgba, face_size(im, a, m), foot)
        print(name, path, f'{rgba.shape[1]}x{rgba.shape[0]}', 'face', raw[name][1])
    base_f, base_sc = raw['idle'][1], TARGET_H / raw['idle'][0].shape[0]
    pieces = []
    for name, *_ in FRAMES:
        rgba, f, foot = raw[name]
        sc = base_sc * (base_f / f if name in FACE_SCALE else 1)
        p = shrink(rgba, sc)
        pieces.append((name, p, foot * sc))
        print(f'{name}: ×{sc:.3f} → {p.shape[1]}x{p.shape[0]}')
    L = max(int(np.ceil(c)) for _, _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 4
    H = max(p.shape[0] + LIFT.get(n, 0) for n, p, _ in pieces) + 5
    AY = H - 2
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c)); y = AY - p.shape[0] - LIFT.get(name, 0)
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = defringe(p)
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'volt_0 cellW={cw} cellH={H} anchorX={L} anchorY={AY} count={len(pieces)} 대기 키={pieces[0][1].shape[0]}')


if __name__ == '__main__':
    main()

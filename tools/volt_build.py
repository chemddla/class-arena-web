# 전격술사 기본 외형 0 (2026-11-10 사용자 샘플: 검은 후드 로브·금빛 번개 테두리·금빛 띠·검은 단발·노란 눈, 흰 배경) → assets/sprites/merc/volt_0.webp
# 사용: python tools/volt_build.py   (샘플 assets/sprites/fx/samples/volt0_*_src.png)
# 예전 기본 외형(비니·안경)은 시크릿 레어 1 → tools/volt_sr1_build.py
# 칸 순서: 0 대기 (몸 양옆 금빛 정전기) · 1~4 걷기 · 5 기본 공격 (두 손을 앞으로, 손 둘레 금빛 전기) · 6 피격 (뒤로 젖힘, 금빛 전기) · 7 쓰러짐 (누움)
#   · 8~9 방전 (두 주먹을 가슴 앞에 모음·금빛 전기 → 두 팔을 활짝 펴고 떠오름)
#   · 10~11 전자포 (옆구리에 금빛 구체를 모음 → 손바닥을 앞으로 내밂)
#   · 12 썬더볼트·체인 라이트닝 (손바닥을 앞으로) · 13~14 일렉트릭 필드 (웅크려 한 손으로 땅을 짚음 → 손가락을 펴 누름)
#   · 15~17 오버로드 (기 모으기 → 강한 전력 흡수 → 축전 상태 돌입, 샘플 아래 이름표 글자는 뺌)
#   쓰러짐 = 피격 → 누움 (사용자: "쓰러짐은 피격 모션 같이 활용"). 스킬 샘플이 오기 전까지 스킬 자세는 기본 공격 칸
# 크기·비율: 대기 자세가 기준 (키 = TARGET_H). 샘플 파일마다 확대 배율·머리 비율이 조금씩 달라서 묶음(SCALE_GROUP)마다 배율을 하나씩 정함
#   얼굴 배율 = 대기 얼굴(머리 쪽 가장 큰 피부 덩어리) 넓이의 제곱근 ÷ 묶음 얼굴 가운데값
#   키 배율 = 대기 키 ÷ 묶음에서 똑바로 선 그림(HEIGHT_REF)의 키. 둘 다 있으면 기하평균 (머리·키 차이를 반씩 나눔), 선 그림이 없는 묶음(웅크림)은 얼굴 배율
#   예: 걷기는 키가 대기와 같은데 얼굴이 5% 커서 얼굴만 맞추면 몸이 5% 작아지고, 썬더볼트·전자포는 얼굴을 맞추면 몸이 4% 길어짐 → 반씩
# 색: 피부·눈동자 픽셀의 밝기 순위를 대기 자세의 같은 순위 색으로 옮김 (피격·누움 피부가 조금 어둡고, 눈 색이 칸마다 조금씩 다름)
#   눈 = 얼굴 피부 상자 안의 금빛 픽셀. 눈을 감은 칸(피격·누움)은 눈이 없어서 피부만, 축전 상태(오버로드 마지막 칸)는 눈이 빛나는 연출이라 피부만
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
    ('bolt', 'volt0_bolt_src.png', 0),
    ('field0', 'volt0_field_src.png', 0), ('field1', 'volt0_field_src.png', 1),
    ('ovl0', 'volt0_overload_src.png', 0), ('ovl1', 'volt0_overload_src.png', 1), ('ovl2', 'volt0_overload_src.png', 2),
]
# 묶음 = 같은 확대 배율로 그린 샘플 (파일이 다르면 배율도 다름: 방전 모음·터뜨림은 따로 그린 그림이라 얼굴 18.7 대 13.6)
SCALE_GROUP = {'walk0': 'big', 'walk1': 'big', 'walk2': 'big', 'walk3': 'big', 'atk': 'big', 'hurt': 'big', 'down': 'big',
               'dis0': 'dis', 'dis1': 'dis1', 'rail0': 'rail', 'rail1': 'rail', 'bolt': 'rail',
               'field0': 'field', 'field1': 'field', 'ovl0': 'ovl', 'ovl1': 'ovl', 'ovl2': 'ovl'}
HEIGHT_REF = {'big': ('walk0', 'walk1', 'walk2', 'walk3'), 'dis': ('dis0',), 'rail': ('rail0', 'bolt')}
NO_EYE_MATCH = {'hurt', 'down', 'ovl2'}
CUT_BELOW = {'volt0_overload_src.png': 165}   # 오버로드 샘플: 발(161줄) 아래 이름표 글자 '1) 기 모으기' 등 (169줄부터)을 자름
LIFT = {'dis1': 6}   # 방전 터뜨림은 샘플에서 발이 떠 있어서 바닥보다 6px 위에 둠


def gold(c):
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    return (R > 150) & (G > 110) & (B < 110) & (R - B > 80)


def figures(path):
    im, a = prep(S + path)
    if path in CUT_BELOW: a[CUT_BELOW[path]:] = 0
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


def face_box(rgba):
    # 칸 그림에서 얼굴 피부 덩어리 (위쪽 절반에서 가장 큰 것) → 그 상자 안 금빛 = 눈
    c, al = rgba[..., :3].astype(float), rgba[..., 3] / 255
    sk = skin_mask(c, al)
    ys = np.where((al > 0).any(axis=1))[0]
    sk[ys.min() + int((ys.max() - ys.min()) * 0.5):] = False
    lb, nb = ndi.label(sk)
    if nb == 0: return None, None
    face = lb == (np.argmax(ndi.sum(sk, lb, range(1, nb + 1))) + 1)
    fy, fx = np.where(face)
    box = np.zeros_like(face); box[fy.min() + 1:fy.max() + 1, fx.min() + 1:fx.max()] = True
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    eye = box & (al > 0.8) & (R > 150) & (G > 100) & (B < 125) & (R - B > 60) & ~sk
    return sk, eye


def rank_match(rgba, m, ref):
    # m 픽셀의 밝기 순위를 ref 색 분포의 같은 순위 색으로
    if m.sum() < 3 or len(ref) < 3: return
    v = rgba[..., :3][m].astype(float)
    ref = ref[np.argsort(ref.mean(axis=1))]
    rank = np.argsort(np.argsort(v.mean(axis=1), kind='stable')) / max(len(v) - 1, 1)
    rgba[..., :3][m] = ref[np.round((0.02 + rank * 0.96) * (len(ref) - 1)).astype(int)].astype(np.uint8)


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
    base_h = raw['idle'][0].shape[0]
    gscale = {}
    for g in set(SCALE_GROUP.values()):
        names = [n for n, gg in SCALE_GROUP.items() if gg == g]
        kf = base_f / float(np.median([raw[n][1] for n in names]))
        kh = base_h / float(np.mean([raw[n][0].shape[0] for n in HEIGHT_REF[g]])) if g in HEIGHT_REF else None
        gscale[g] = np.sqrt(kf * kh) if kh else kf
        print(f'묶음 {g}: 얼굴 ×{kf:.3f} 키 ×{kh if kh is None else round(kh, 3)} → ×{gscale[g]:.3f}')
    pieces = []
    for name, *_ in FRAMES:
        rgba, f, foot = raw[name]
        g = SCALE_GROUP.get(name)
        sc = base_sc * (gscale[g] if g else 1)
        p = shrink(rgba, sc)
        pieces.append((name, p, foot * sc))
        print(f'{name}: ×{sc:.3f} → {p.shape[1]}x{p.shape[0]}')
    # 피부·눈동자 색을 대기 자세에 맞춤
    sk0, eye0 = face_box(pieces[0][1])
    skin_ref = pieces[0][1][..., :3][skin_mask(pieces[0][1][..., :3].astype(float), pieces[0][1][..., 3] / 255)].astype(float)
    eye_ref = pieces[0][1][..., :3][eye0].astype(float)
    print(f'대기 피부 {skin_ref.mean(axis=0).round()} ({len(skin_ref)}px) · 눈 {eye_ref.mean(axis=0).round()} ({len(eye_ref)}px)')
    for name, p, _ in pieces[1:]:
        sk, eye = face_box(p)
        if sk is None: continue
        before = (p[..., :3][skin_mask(p[..., :3].astype(float), p[..., 3] / 255)].mean(axis=0).round(), p[..., :3][eye].mean(axis=0).round() if eye.sum() else '-')
        rank_match(p, skin_mask(p[..., :3].astype(float), p[..., 3] / 255), skin_ref)
        if name not in NO_EYE_MATCH: rank_match(p, eye, eye_ref)
        print(f'  {name}: 피부 {before[0]} → {p[..., :3][skin_mask(p[..., :3].astype(float), p[..., 3] / 255)].mean(axis=0).round()} · 눈 {eye.sum()}px {before[1]}')
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

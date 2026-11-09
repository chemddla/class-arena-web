# 성녀 기본 외형(healer_0) 교체: 은발·흰 베일·흰 금빛 수도복·금빛 십자 지팡이 샘플 → assets/sprites/merc/healer_0.webp
# 사용: python tools/healer0_build.py
# 샘플 (assets/sprites/merc/samples/healer_edit_*):
#   흰 배경: 1_idle_src.webp (681×1024, 대기 1칸, 아주 크게 그려짐) · 2_walk_src.png (537×187, 걷기 3칸) · 3_attack_heal_src.png (181×180, 일반공격 = 치유 1칸, 반짝이 포함)
#           4_hurt_src.png (168×159, 피격 1칸) · 5_fall_src.png (514×159, 쓰러짐 2칸: 무릎 꿇음 → 엎드림, 지팡이는 따로 떨어져 있음)
#           6_skill_cast_src.png (스킬 시전 2칸 + 잘린 칸 — 8번 검은 배경 장에 다섯 칸이 다 있어서 안 씀)
#           7_hidden_skill_src.webp (783×749, 히든 스킬 [기적] 다섯 단계, 칸 아래 글씨)
#   검은 배경: 8_skill_hidden_black_src.webp (681×1024): 윗줄 스킬 시전 5칸 (준비 · 시작 · 시전 · 발동 · 마무리) / 아랫줄 히든 스킬 5단계 (7번과 같은 그림, 약 0.87배)
# 칸 순서 (healer_0): 0 대기 · 1~3 걷기 · 4 일반공격 (치유) · 5 피격 · 6~7 쓰러짐 · 8~12 스킬 (준비 · 시작 · 시전 · 발동 · 마무리)
# 히든 스킬 [기적] 시전 그림 → assets/sprites/fx/healer_miracle_cast.webp (HEALER_MIRACLE_FX, 5칸: 집중 · 상승 · 시전 · 연출 · 마무리)
# 배경 지우기
#   흰 배경 장: 가장자리에 이어진 흰색만 배경 (흰 수도복 속 새하얀 곳을 지우지 않게 갇힌 흰 배경은 GAP 상자로만)
#   검은 배경 스킬 칸: 몸 = 금빛이 아닌 덩어리를 채운 것 (+ 그 둘레 4px 안의 금빛 장식) → 불투명, 나머지(반짝이·발밑 금빛 고리)는 밝기를 알파로
#   히든 스킬: 흰 배경 장(7)과 검은 배경 장(8)을 맞대어 두 장이 맞는 곳에서 알파를 정확히 구함 (tools/archer0_build.py의 폭풍 시전과 같은 방식)
# 크기: 칸마다 얼굴(가장 큰 살색 덩어리) 크기를 대기 칸에 맞춤. 같은 장의 칸은 같은 배율 (쓰러짐은 피격 장, 히든 스킬은 검은 배경 스킬 줄과 같은 배율)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
from mage0_build import defringe
from archer0_build import shrink_soft

D = 'assets/sprites/merc/samples/healer_edit_'
OUT = 'assets/sprites/merc/healer_0.webp'
CAST_OUT = 'assets/sprites/fx/healer_miracle_cast.webp'
TRAP_DARK = 0.35   # 갇힌 흰 덩어리 둘레 중 검은 윤곽 비율이 이보다 크면 배경
IDLE_H = 100   # 대기 칸 키 (베일 꼭대기~발)
BLACK = '8_skill_hidden_black_src.webp'
WHITE7 = '7_hidden_skill_src.webp'

# (칸 이름, 샘플, 상자, 덩어리 고르기: 'one' 몸만 · 'all' 큰 덩어리 모두 · 'spark' 몸 + 둘레 반짝이, 배율 기준 장)
FRAMES = [
    ('idle', '1_idle_src.webp', None, 'one', 'idle'),
    ('walk0', '2_walk_src.png', (0, 0, 165, 187), 'one', 'walk'),
    ('walk1', '2_walk_src.png', (180, 0, 360, 187), 'one', 'walk'),
    ('walk2', '2_walk_src.png', (370, 0, 537, 187), 'one', 'walk'),
    ('atk', '3_attack_heal_src.png', None, 'spark', 'atk'),
    ('hurt', '4_hurt_src.png', None, 'one', 'hurt'),
    ('down0', '5_fall_src.png', (0, 0, 214, 159), 'one', 'hurt'),
    ('down1', '5_fall_src.png', (214, 0, 514, 159), 'all', 'hurt'),
]
SKILL_ROW = (62, 262)   # 검은 배경 장 윗줄 (y)
SKILL_NAMES = ['ready', 'start', 'cast', 'fire', 'end']
# 히든 스킬: (칸 이름, 흰 배경 상자, 검은 배경 상자) — 연출 칸 발밑의 회색 그림자 타원은 상자 밖으로 뺌
HIDDEN = [('focus', (20, 95, 240, 299), (14, 455, 210, 636)),
          ('rise', (255, 15, 458, 294), (220, 385, 405, 630)),
          ('chant', (462, 0, 716, 290), (405, 366, 630, 624)),
          ('show', (40, 355, 512, 661), (32, 688, 446, 955)),
          ('end', (560, 485, 742, 692), (492, 800, 650, 982))]


HIDDEN_LIFT = {}
# 발 자리 (검은 배경 장 좌표): 금빛 단·날개에 몸이 조각나 자동으로 못 잡는 칸만. 신발 바닥 가운데
#   연출은 떠 있는 자세 → 샘플의 그림자 타원(y 965)을 땅으로 (신발은 그보다 약 20px 위)
HIDDEN_FOOT = {'rise': (307, 618), 'chant': (520, 613), 'show': (240, 965)}


def rgb(src):
    return np.array(Image.open(D + src).convert('RGB')).astype(float)


def load_white(src, box, pick):
    im = rgb(src)
    if box:
        x0, y0, x1, y1 = box; im = im[y0:y1, x0:x1]
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), constant_values=255)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    # 갇힌 흰 배경 (지팡이·머리카락·팔 사이): 새하얗고, 둘레가 대부분 검은 윤곽인 덩어리
    #   (수도복 속 새하얀 곳은 둘레가 연회색 음영·금빛 장식이라 남음)
    dark = im.max(axis=2) < 90
    for i, sl in enumerate(ndi.find_objects(lab)):
        if sl is None or (i + 1) in edge: continue
        m = lab[sl] == i + 1
        if m.sum() < 12 or im[sl][m].min(axis=1).mean() < 244: continue
        ring = ndi.binary_dilation(np.pad(m, 3), iterations=3) & ~np.pad(m, 3)
        d = np.pad(dark[sl], 3)
        # 둘레 3px 안에 검은 윤곽이 얼마나 있는지 (덩어리 바깥 상자가 잘리지 않게 넓혀서 봄)
        y0, x0 = max(0, sl[0].start - 3), max(0, sl[1].start - 3)
        big = dark[y0:sl[0].stop + 3, x0:sl[1].stop + 3]
        mm = np.zeros_like(big); mm[sl[0].start - y0:sl[0].stop - y0, sl[1].start - x0:sl[1].stop - x0] = m
        rg = ndi.binary_dilation(mm, iterations=3) & ~mm
        if big[rg].mean() > TRAP_DARK: bg |= (lab == i + 1)
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    m = a > 0.3
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=3))
    sz = ndi.sum(m, lab, range(1, n + 1))
    big = int(np.argmax(sz)) + 1
    if pick == 'one':
        keep = lab == big
    elif pick == 'all':
        keep = np.isin(lab, 1 + np.where(sz >= 200)[0])
    else:   # 몸 + 몸 둘레 40px 안의 반짝이
        near = ndi.binary_dilation(lab == big, iterations=40)
        keep = np.isin(lab, np.unique(lab[near & (lab > 0)]))
    a = np.where(keep, a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    body = (rgba[..., 3] > 128) if pick != 'spark' else ((rgba[..., 3] > 128) & (lab == big)[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    return rgba, body


def face_size(rgba):
    # 얼굴 = 가장 큰 살색 덩어리 (가로·세로)
    c = rgba[..., :3] / 255; a = rgba[..., 3] > 200
    mx, mn = c.max(-1), c.min(-1); s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    skin = a & (mx > 0.75) & (s > 0.1) & (s < 0.45) & (r >= g) & (g >= b) & (r - b > 0.1) & (r - g < 0.2)
    lab, n = ndi.label(ndi.binary_closing(skin, iterations=2))
    big = int(np.argmax(ndi.sum(skin, lab, range(1, n + 1)))) + 1
    ys, xs = np.where(lab == big)
    return xs.max() - xs.min() + 1, ys.max() - ys.min() + 1


def foot_x(body):
    ys, xs = np.where(body)
    y1 = ys.max(); return xs[ys >= y1 - max(3, int((y1 - ys.min()) * 0.06))].mean(), y1


def gold(im):
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    return (r - b > 55) & (r >= g - 10)


def load_black_row():
    # 검은 배경 스킬 줄 → 5칸 (rgba, 몸, 발 x, 발 y)
    B = np.pad(rgb(BLACK)[SKILL_ROW[0]:SKILL_ROW[1]], ((6, 6), (6, 6), (0, 0)))
    fg = B.max(axis=2) > 24
    lab, n = ndi.label(fg, structure=np.ones((3, 3)))
    sz = ndi.sum(fg, lab, range(1, n + 1))
    core = fg & ~gold(B)
    clab, cn = ndi.label(core, structure=np.ones((3, 3)))
    csz = ndi.sum(core, clab, range(1, cn + 1))
    bodies = sorted([i + 1 for i in np.argsort(csz)[-5:]], key=lambda i: np.where(clab == i)[1].mean())
    dists = np.stack([ndi.distance_transform_edt(clab != i) for i in bodies])
    owner = np.argmin(dists, axis=0)
    out = []
    for fi, bi in enumerate(bodies):
        mine = np.zeros_like(fg)
        for ci in range(1, n + 1):
            m = lab == ci
            if sz[ci - 1] < 2: continue
            if np.bincount(owner[m], minlength=5).argmax() == fi: mine |= m
        filled = ndi.binary_fill_holes(ndi.binary_closing(clab == bi, iterations=2))
        body = ndi.binary_fill_holes(filled | (mine & ndi.binary_dilation(filled, iterations=4)))
        # 채운 곳 중 새까만 덩어리 (지팡이와 몸 사이 배경)는 다시 빼냄
        hole = body & (B.max(axis=2) <= 24)
        hl, hn = ndi.label(hole)
        body &= ~np.isin(hl, 1 + np.where(ndi.sum(hole, hl, range(1, hn + 1)) >= 6)[0])
        # 바깥 테두리의 검은 배경 섞인 어두운 픽셀 (밝은 배경에서 검은 띠로 보임) 두 겹 지움
        for _ in range(2):
            rim = body & ndi.binary_dilation(~body) & (B.max(axis=2) < 110)
            body &= ~rim
        a = np.where(body, 1.0, np.where(mine & ~ndi.binary_dilation(body, iterations=2) | (mine & (B.max(axis=2) > 150)), B.max(axis=2) / 255, 0))
        a = np.where(a < 0.08, 0, a)
        col = np.where(body[..., None], B, B / np.maximum(a, 1e-3)[..., None]).clip(0, 255)
        ys, xs = np.where(a > 0)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.dstack([col, a * 255])[y0:y1, x0:x1]; bd = body[y0:y1, x0:x1]
        fx, fy = foot_x(bd)
        out.append((SKILL_NAMES[fi], rgba, bd, fx, fy))
    return out


def opaque_body(im):
    dark = im.mean(axis=2) < 105
    body = ndi.binary_fill_holes(ndi.binary_closing(dark, iterations=2)) & ~((im.min(axis=2) > 228) & ~dark)
    lab, n = ndi.label(body)
    return np.isin(lab, 1 + np.where(ndi.sum(body, lab, range(1, n + 1)) >= 40)[0])


def load_pair(wbox, bbox, foot=None):
    # 흰 배경 장(7)과 검은 배경 장(8)을 맞대어 알파·색을 구함 (archer0_build.load_pair와 같음). 결과는 검은 배경 장 좌표
    import cv2
    W = rgb(WHITE7).astype(np.float32); x0, y0, x1, y1 = wbox; W = W[y0:y1, x0:x1]
    B = rgb(BLACK).astype(np.float32); x0, y0, x1, y1 = bbox; B = np.pad(B[y0:y1, x0:x1], ((8, 8), (8, 8), (0, 0)))
    body = opaque_body(W)
    best = None
    for s in np.arange(0.8, 0.95, 0.004):
        size = (round(W.shape[1] * s), round(W.shape[0] * s))
        if size[0] > B.shape[1] or size[1] > B.shape[0]: continue
        t = cv2.resize(W, size, interpolation=cv2.INTER_AREA)
        m = cv2.resize(body.astype(np.float32), size, interpolation=cv2.INTER_AREA)
        m = cv2.erode((m > 0.99).astype(np.uint8), np.ones((3, 3))).astype(np.float32)
        r = cv2.matchTemplate(B, t, cv2.TM_SQDIFF, mask=np.dstack([m] * 3))
        v, _, loc, _ = cv2.minMaxLoc(r); v /= max(m.sum(), 1)
        if best is None or v < best[0]: best = (v, s, loc, t)
    _, s, (ox, oy), t = best
    Wb = np.full_like(B, 255)
    h = min(t.shape[0], B.shape[0] - oy); w = min(t.shape[1], B.shape[1] - ox)
    Wb[oy:oy + h, ox:ox + w] = t[:h, :w]
    diff = Wb - B
    est = 1 - diff.mean(axis=2) / 255
    agree = (diff.std(axis=2) < 22) & (diff.min(axis=2) > -24)
    glow = B.max(axis=2) / 255
    a = np.where(agree, np.clip(est, 0, 1), glow)
    a = np.where(a < 0.06, 0, a)
    solid = ndi.binary_fill_holes(ndi.binary_opening(a > 0.93, iterations=1))
    lab, n = ndi.label(solid)
    sz = ndi.sum(solid, lab, range(1, n + 1))
    # 발 위치용 몸: 금빛(마법진·날개)을 뺀 불투명 덩어리 중 가장 큰 것
    nb = solid & ~(gold(B) & (B.max(axis=2) > 150))   # 갈색 신발은 몸 (밝은 금빛만 뺌)
    lab, n = ndi.label(nb)
    nsz = ndi.sum(nb, lab, range(1, n + 1))
    body = lab == int(np.argmax(nsz)) + 1
    # 신발은 금빛 단에 막혀 따로 떨어진 덩어리 → 몸 바로 아래(가로 가운데 쪽)의 15px 넘는 덩어리를 몸에 붙임
    ys, xs = np.where(body); cx, hw = xs.mean(), (xs.max() - xs.min()) * 0.3
    for i, sl in enumerate(ndi.find_objects(lab)):
        if nsz[i] < 6: continue
        if abs((sl[1].start + sl[1].stop) / 2 - cx) < hw and sl[0].start <= ys.max() + 16:
            body |= lab == i + 1
    a = np.where(solid, 1.0, a)
    col = (B / np.maximum(a, 1e-3)[..., None]).clip(0, 255)
    ys, xs = np.where(a > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([col, a * 255])[y0:y1, x0:x1]; solid = solid[y0:y1, x0:x1]; body = body[y0:y1, x0:x1]
    fx, fy = foot_x(body)
    if foot:   # 손으로 정한 발 자리 (검은 배경 장 좌표)
        fx, fy = foot[0] - bbox[0] + 8 - x0, foot[1] - bbox[1] + 8 - y0
    print(f'  위치 맞춤 ×{s:.3f} ({ox}, {oy}), 두 장이 맞는 곳 {agree[a > 0].mean():.0%}')
    return rgba, solid, fx, fy


def pack(pieces, out, label):
    # pieces: (이름, rgba, 발 x, 발 y). 발 자리를 칸마다 같은 기준점에
    L = max(int(np.ceil(fx)) for _, _, fx, _ in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - fx)) for _, p, fx, _ in pieces) + 3
    U = max(int(np.ceil(fy)) for _, _, _, fy in pieces) + 3
    Bm = max(int(np.ceil(p.shape[0] - fy)) for _, p, _, fy in pieces) + 2
    cw, ch = L + R, U + Bm
    sheet = np.zeros((ch, cw * len(pieces), 4), np.uint8)
    for i, (name, p, fx, fy) in enumerate(pieces):
        x = i * cw + L - int(round(fx)); y = U - int(round(fy))
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = np.maximum(sheet[y:y + p.shape[0], x:x + p.shape[1]], p)
    Image.fromarray(sheet, 'RGBA').save(out, 'WEBP', lossless=True)
    print(f'{label} cellW={cw} cellH={ch} anchorX={L} anchorY={U} count={len(pieces)}')
    return cw, ch, L, U


def main():
    loaded = [(f, *load_white(src, box, pick)) for f in FRAMES for (_, src, box, pick, _) in [f]]
    idle = loaded[0][1]
    ki = IDLE_H / idle.shape[0]
    fw0, fh0 = face_size(idle)
    print(f'대기: 샘플 키 {idle.shape[0]}, 얼굴 {fw0}x{fh0}')
    groups = {}
    for (name, src, box, pick, grp), rgba, body in loaded:
        if grp in groups: continue
        fw, fh = face_size(rgba)
        groups[grp] = ki * (fw0 / fw + fh0 / fh) / 2
        if grp == 'hurt': groups[grp] = (groups[grp] * groups['walk']) ** 0.5   # 피격 장은 표정 때문에 얼굴이 커 보임 → 걷기 배율과 반반
        print(f'  배율 {grp}: 얼굴 {fw}x{fh} → ×{groups[grp]:.3f}')
    pieces = []
    for (name, src, box, pick, grp), rgba, body in loaded:
        k = groups[grp]
        fx, fy = foot_x(body)
        if name == 'down1': fx = rgba.shape[1] * 0.42
        if name == 'down0': fx = rgba.shape[1] * 0.45
        p = defringe(shrink(rgba, k))
        pieces.append((name, p, fx * k, p.shape[0] - (rgba.shape[0] - 1 - fy) * k - 1))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{k:.3f} → {p.shape[1]}x{p.shape[0]}')
    # 스킬 줄 (검은 배경): 준비 칸 얼굴로 배율
    row = load_black_row()
    # 검은 배경에서는 머리카락·손이 살색과 섞여 얼굴을 못 잡음 → 준비 칸(똑바로 선 자세) 키를 걷기 칸 키에 맞춤
    walk_h = [r for (f, r, _) in loaded if f[0] == 'walk0'][0].shape[0]
    kb = groups['walk'] * walk_h / row[0][1].shape[0]
    print(f'  배율 검은 배경: 준비 칸 키 {row[0][1].shape[0]} → ×{kb:.3f}')
    for name, rgba, bd, fx, fy in row:
        p = shrink_soft(rgba, bd, kb)
        pieces.append((name, p, fx * kb, fy * kb))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{kb:.3f} → {p.shape[1]}x{p.shape[0]}')
    cell = pack(pieces, OUT, 'healer_0')
    hp = []
    for name, wbox, bbox in HIDDEN:
        rgba, solid, fx, fy = load_pair(wbox, bbox, HIDDEN_FOOT.get(name))
        p = shrink_soft(rgba, solid, kb)
        hp.append((name, p, fx * kb, fy * kb + HIDDEN_LIFT.get(name, 0)))
        print(f'{name}: 검은 배경 {rgba.shape[1]}x{rgba.shape[0]} ×{kb:.3f} → {p.shape[1]}x{p.shape[0]}')
    pack(hp, CAST_OUT, 'healer_miracle_cast')
    return cell


if __name__ == '__main__':
    main()

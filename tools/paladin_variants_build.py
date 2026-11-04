# 성기사 외형 0(paladin_0.webp)에서 색 조합 변형 시트 만들기 — 외형 1~5 (칸 구성·크기·기준점 모두 같음)
# 사용: python tools/paladin_variants_build.py                → assets/sprites/merc/paladin_1~5.webp
#       python tools/paladin_variants_build.py preview <경로>  → 외형 0~5 × 모든 칸 확인 그림 한 장
#       python tools/paladin_variants_build.py masks <경로>    → 부위 나누기 확인 그림 (머리 빨강·방패 초록·십자 노랑·눈 자홍·망치 금장식 주황)
# 색표·원칙: docs/paladin-skin-palette.md (대기 칸 거친 미리보기는 tools/paladin_palette_preview.py)
# 부위: 머리(땋은 머리 포함) · 눈동자 · 갑옷(은색 금속 전부 — 방패 테두리·망치 머리 포함) · 망토(파랑 천 — 망토·스카프·앞자락) · 방패 바탕 · 십자 · 망치 금장식
#   피부·검은 윤곽·흰자·가죽(허리띠·장갑)·이펙트(돌격 흙먼지)는 그대로
# 부위 나누기 (칸마다 자동, 안 되는 칸만 아래 표로 보정):
#   - 얼굴 = 가장 큰 살색 덩어리. 머리 = 얼굴 위쪽에 닿은 은빛 조각들(어두운 회색 선은 벽) + 이어진 작은 조각(땋은 머리 마디),
#     얼굴 상자 둘레로 자르고, 조각 사이 어두운 결까지 메움. 은발과 은 갑옷은 색조가 같아서 색으로는 못 가름
#   - 방패 = 파란 덩어리 중 밝은 은색 구멍(십자)을 품고 모양이 꽉 찬 것 (망토가 붙어 있으면 1~3겹 깎아서 뗌). 십자 = 방패 안 구멍
#   - 눈 = 얼굴 껍질 안 가운데 띠의 파란 덩어리 중 채도 0.3 넘는 것 2개까지 (이마 옆 푸른빛 머리카락은 0.2 아래)
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import ConvexHull

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb

SRC = 'assets/sprites/merc/paladin_0.webp'
W, H = 291, 154
K4 = ndi.generate_binary_structure(2, 1); K8 = np.ones((3, 3), bool)
YY, XX = np.mgrid[0:H, 0:W]

# 머리 덩어리가 팔·망치 자루에 가려 따로 떨어진 칸, 땋은 머리가 얼굴 상자 밖으로 뻗은 칸: 그 조각 안 한 점 (칸 안 x, y) — 상자로 자르지 않음
HAIR_SEEDS = {12: [(155, 47), (136, 70)]}   # 12 정수리·왼팔 옆으로 늘어진 땋은 머리
# 마디마다 어두운 선으로 끊겨 조각이 많은 땋은 머리: 이 상자 (x0, y0, x1, y1) 안 은색·회색은 모두 머리 (16 돌격 때 뒤로 날리는 땋은 머리)
HAIR_BOXES = {16: [(131, 79, 158, 88)]}
GOLD_XMIN = {16: 150}            # 돌격 칸의 흙먼지 꼬리(금빛 모래색)는 망치 장식이 아님 → 이 x보다 오른쪽 금색만
CLOSED_EYES = {5, 6, 7, 8, 17}   # 눈 감은 칸 (피격·쓰러짐·축성 기도): 눈동자가 없음 (이마 옆 푸른빛 머리카락을 눈으로 잡지 않게)
DIM_EYES = {18, 19}              # 불굴의 가호 칸: 눈동자가 흐린 회청색이라 채도 0.21까지 눈으로 봄 (다른 칸은 0.3)
EYE_KEEP = {18: [(166, 65, 176, 73)], 19: [(167, 57, 176, 65)]}  # 옆머리와 어두운 픽셀로 이어진 회색 눈 (x0, y0, x1, y1) → 머리색을 입히지 않음

# (번호, 이름, 부위별 목표 색) — 색표는 docs/paladin-skin-palette.md. 각 부위의 시트 전체 가운데 밝기·채도를 이 색에 맞추고 명암 차이는 살림. None = 그대로
#   목표 색은 '가운데' 색이라 원래 가운데 밝기(갑옷 0.48, 망토 0.34)를 생각해서 잡음: 1·5 갑옷은 은색 그대로, 4 상아 갑옷·크림 망토는 밝기를 낮춰 명암을 남김
VARIANTS = [
    (1, '진홍 성전단',   dict(hair='#e8c45a', eyes='#3a7bd5', armor=None, cape='#b8202c', shield='#ece8dc', cross='#b8202c', gold='#d9a63a')),
    (2, '칠흑 심판관',   dict(hair='#f2f2f0', eyes='#c9a033', armor='#3c3d48', cape='#4a2a7a', shield='#22222a', cross='#e2b545', gold='#8a8f9c')),
    (3, '숲의 수호자',   dict(hair='#8a3f26', eyes='#3f9a5a', armor='#9a7444', cape='#2d6b3c', shield='#2f7a46', cross='#d8dde2', gold='#b07a3a')),
    (4, '태양의 성전사', dict(hair='#2a2630', eyes='#d08a2a', armor='#aaa392', cape='#d4ccb4', shield='#e0a62a', cross='#f8f6ee', gold='#e2b23a')),
    (5, '장미 기사',     dict(hair='#f09ab8', eyes='#c84a7a', armor=None, cape='#b23a6a', shield='#c43b74', cross='#e8e8ec', gold='#d98a7a')),
]
PARTS = ('hair', 'eyes', 'armor', 'cape', 'shield', 'cross', 'gold')


def hull_fill(m):
    ys, xs = np.where(m)
    if len(xs) < 5: return m.copy()
    try: hull = ConvexHull(np.c_[xs, ys].astype(float))
    except Exception: return m.copy()
    out = np.ones(m.shape, bool)
    for a, b, c in hull.equations:  # a x + b y + c <= 0 이 안쪽
        out &= (a * XX + b * YY + c) <= 0.5
    return out


def pick_shield(blue, v, A):
    lb, nb = ndi.label(blue, K4); best = None; bestn = 0
    for i in range(1, nb + 1):
        comp = lb == i
        if comp.sum() < 80: continue
        # 망토가 붙어 있으면 깎아서 떼어 봄 (0~3겹)
        for k in range(0, 4):
            core = ndi.binary_erosion(comp, K8, iterations=k) if k else comp
            lc, nc = ndi.label(core, K8)
            for j in range(1, nc + 1):
                sub = lc == j
                part = comp & ndi.binary_dilation(sub, K8, iterations=k) if k else sub
                filled = ndi.binary_fill_holes(part)
                holes = filled & ~part & A
                if holes.sum() < 20 or (v[holes] > 0.62).mean() < 0.55: continue   # 십자는 밝은 은색 (망토 구멍은 어두운 갑옷)
                if filled.sum() / max(1, hull_fill(filled).sum()) < 0.88: continue  # 방패는 꽉 찬 모양 (망토는 들쭉날쭉)
                if holes.sum() > bestn: bestn = holes.sum(); best = part
            if best is not None: break
    return best if best is not None else np.zeros_like(blue)


def seg(f, idx=None):
    A = f[..., 3] > 0
    hsv = rgb2hsv(f[..., :3] / 255.); h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    outline = v < 0.16
    skin = A & (h > 8) & (h < 35) & (s > 0.12) & (s < 0.55) & (v > 0.55)
    for _ in range(2): skin |= A & ((h < 35) | (h > 340)) & (s > 0.12) & (s < 0.6) & (v > 0.4) & ndi.binary_dilation(skin)
    blue = A & (h > 195) & (h < 245) & (s > 0.3) & ~outline
    gold = A & (h > 28) & (h < 62) & (s > 0.28) & (v > 0.3)
    dust = gold & (XX < GOLD_XMIN[idx]) if idx in GOLD_XMIN else np.zeros_like(A)
    gold &= ~dust
    R = A & ~outline & ~skin & ~blue & ~gold & ~dust
    lab, n = ndi.label(skin, K8)
    face = None
    if n:
        sz = ndi.sum(skin, lab, range(1, n + 1)); face = lab == (1 + int(np.argmax(sz)))
    shield = pick_shield(blue, v, A)
    sh_full = ndi.binary_fill_holes(shield) if shield.any() else shield
    cross = sh_full & ~shield & A & ~outline
    eyes = np.zeros_like(A); hair = np.zeros_like(A)
    if face is not None:
        ys, xs = np.where(face); fy0, fy1 = ys.min(), ys.max(); fx0, fx1 = xs.min(), xs.max(); fh = fy1 - fy0
        # 눈: 얼굴 상자의 가운데 띠(키 33~80%) 안, 얼굴 껍질 안의 푸른 덩어리
        band = (XX >= fx0) & (XX <= fx1) & (YY >= fy0 + 0.33 * fh) & (YY <= fy0 + 0.8 * fh)
        cand = A & (h > 190) & (h < 275) & (s > 0.1) & ~outline & band & ~face
        fhull = ndi.binary_dilation(hull_fill(face), K8, iterations=1)
        le, ne = ndi.label(cand & fhull, K8)
        comps = []
        for j in range(1, ne + 1):
            c = le == j; xx = XX[c]
            if c.sum() >= 3 and fx0 + 3 <= xx.mean() <= fx1 - 1: comps.append((int(c.sum()), float(s[c].max()), c))  # 얼굴 가장자리에 붙은 목깃 파랑은 뺌
        th = 0.21 if idx in DIM_EYES else 0.3
        if idx not in CLOSED_EYES:
            for _, _, c in sorted([c for c in comps if c[1] >= th], key=lambda c: -c[0])[:2]: eyes |= c
        # 머리: 얼굴 위쪽에 닿은 은빛 조각들 + 거기 이어진 조각 (어두운 선은 벽, 방패 둘레는 뺌)
        Rb = R & (v >= 0.3) & ~eyes & ~ndi.binary_dilation(sh_full, iterations=4)
        # 눈 흰자·눈동자 회색 조각 (얼굴 안 가운데 띠에 들어 있는 작은 조각)은 머리가 아님
        lr0, nr0 = ndi.label(Rb, K4); inner = fhull & band
        for j in range(1, nr0 + 1):
            c = lr0 == j
            if c.sum() <= 30 and inner[c].mean() >= 0.8: Rb &= ~c
        box = np.zeros_like(A); box[max(0, fy0 - 40):fy1 + int(fh * 0.35) + 1, max(0, fx0 - 22):fx1 + 22] = True
        lr, nr = ndi.label(Rb, K4)
        upper = face & (YY < fy0 + 0.6 * fh)
        touch = [t for t in np.unique(lr[ndi.binary_dilation(upper, K8, iterations=2)]) if t]
        cx = int(np.median(xs[ys <= fy0 + 3]))   # 꼭대기 씨앗: 얼굴 꼭대기에서 곧장 위로
        for yy in range(fy0, max(0, fy0 - 12), -1):
            hit = [lr[yy, cx + dx] for dx in (0, -1, 1, -2, 2, -3, 3) if lr[yy, cx + dx]]
            if hit: touch.append(hit[0]); break
        hair = np.isin(lr, touch) & box
        seeded = np.zeros_like(A)
        for sx, sy in HAIR_SEEDS.get(idx, []):
            if lr[sy, sx]: seeded |= lr == lr[sy, sx]
        for x0, y0, x1, y1 in HAIR_BOXES.get(idx, []): seeded[y0:y1 + 1, x0:x1 + 1] |= R[y0:y1 + 1, x0:x1 + 1]
        hair |= seeded; box = box | ndi.binary_dilation(seeded, K8, iterations=3)
        # 머리 덩어리에 이어진 작은 조각(땋은 머리 마디): 둘레 2px 안에서 닿고 거의 다 얼굴 상자 둘레 안에 있는 것
        for _ in range(4):
            near = np.unique(lr[ndi.binary_dilation(hair, K8, iterations=2) & Rb & ~hair])
            add = [t for t in near if t and (lr == t).sum() <= 60 and ((lr == t) & box).mean() > 0.9]
            if not add: break
            hair |= np.isin(lr, add) & box
        # 머리 덩어리 사이 어두운 결(진한 회색 선)도 머리로: 머리를 닫아서 생긴 틈
        hair |= R & ~eyes & ndi.binary_closing(hair, K8, iterations=2) & box
        keep = ndi.binary_dilation(eyes, K8, iterations=2)   # 눈 둘레 흰자·속눈썹 회색은 머리가 아님
        for x0, y0, x1, y1 in EYE_KEEP.get(idx, []): keep[y0:y1 + 1, x0:x1 + 1] = True
        hair &= ~keep
    # 작은 파란 점(8px 이하): 둘레가 머리면 머리(땋은 머리의 푸른 그늘), 은색 금속이면 갑옷(갑옷에 비친 파란빛) — 망토색으로 칠하면 점이 튐
    lb, nb = ndi.label(blue & ~shield & ~eyes, K8)
    for j in range(1, nb + 1):
        c = lb == j
        if c.sum() > 8: continue
        ring = ndi.binary_dilation(c, K8) & ~c & A & ~outline
        if not ring.any(): continue
        if hair[ring].mean() >= 0.5: hair |= c
        elif (R & ~hair & (s < 0.3))[ring].mean() >= 0.5: blue &= ~c; R |= c
    cape = blue & ~shield & ~eyes & ~hair
    armor = R & ~hair & ~eyes & ~cross & ((s < 0.3) | (blue_spec := (h > 195) & (h < 245)))   # 은색 금속: 채도 낮은 것만 (허리띠·장갑 가죽 갈색은 그대로) + 위에서 넘긴 파란 점
    return {'hair': hair, 'eyes': eyes, 'armor': armor, 'cape': cape, 'shield': shield, 'cross': cross, 'gold': gold, 'hsv': (h, s, v)}


def hex_hsv(c):
    c = c.lstrip('#'); rgb = np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)]) / 255.
    hh = rgb2hsv(rgb[None, None])[0, 0]
    return hh[0] * 360, hh[1], hh[2]


def map_v(v, mv, tv, lo, hi):
    # 가운데 밝기 mv → tv, 명암 차이는 그대로 옮기되 밝은 끝(hi, 95%)이 0.97 · 어두운 끝(lo, 5%)이 0.04를 넘지 않게만 줄임
    #   (비율로 옮기면 밝은 목표에서 명암이 뭉개지고 갑옷이 하얗게 날아갔음)
    c = min(1.0, (0.97 - tv) / max(1e-3, hi - mv), (tv - 0.04) / max(1e-3, mv - lo))
    return tv + (v - mv) * max(0.2, c)


def recolor(f, masks, spec, med):
    h, s, v = masks['hsv']
    out = f.copy()
    for k in PARTS:
        m = masks[k]
        if spec.get(k) is None or not m.any(): continue
        th, ts, tv = hex_hsv(spec[k]); ms, mv, lo, hi = med[k]
        vs, ss = v[m], s[m]
        nv = np.clip(map_v(vs, mv, tv, lo, hi), 0, 1)
        if ms < 0.12:   # 회색에서 오는 부위(머리·갑옷·십자): 채도를 새로 줌, 어두운 곳일수록 조금 짙게
            ns = np.clip(ts * (0.75 + 0.5 * (1 - vs)), 0, 1)
        else:
            ns = np.clip(ss * ts / max(1e-3, ms), 0, 1)
        rgb = hsv2rgb(np.stack([np.full(m.sum(), th / 360.), ns, nv], -1)[None])[0]
        out[m, :3] = (rgb * 255 + .5).clip(0, 255).astype(np.uint8)
    return out


def load():
    im = np.array(Image.open(SRC).convert('RGBA'))
    frames = [im[:, i * W:(i + 1) * W] for i in range(im.shape[1] // W)]
    masks = [seg(f, i) for i, f in enumerate(frames)]
    med = {}
    for k in PARTS:   # 부위별 시트 전체 가운데 채도·밝기 (칸마다 따로 맞추면 칸 사이 색이 달라짐)
        ss = np.concatenate([mk['hsv'][1][mk[k]] for mk in masks]); vv = np.concatenate([mk['hsv'][2][mk[k]] for mk in masks])
        med[k] = (float(np.median(ss)), float(np.median(vv)), float(np.percentile(vv, 5)), float(np.percentile(vv, 95)))
    return frames, masks, med


def preview(path, frames, masks, med):
    rows = [np.hstack(frames)] + [np.hstack([recolor(f, mk, spec, med) for f, mk in zip(frames, masks)]) for _, _, spec in VARIANTS]
    img = Image.fromarray(np.vstack(rows), 'RGBA'); bg = Image.new('RGBA', img.size, (58, 62, 70, 255)); bg.paste(img, (0, 0), img)
    bg.save(path)


def masks_sheet(path, frames, masks):
    cols = 5; sheet = Image.new('RGBA', (cols * W, ((len(frames) + cols - 1) // cols) * H))
    for i, (f, mk) in enumerate(zip(frames, masks)):
        o = f.copy()
        for k, c in (('hair', (255, 40, 40)), ('shield', (40, 200, 60)), ('cross', (255, 230, 0)), ('eyes', (255, 0, 255)), ('gold', (255, 140, 0))): o[mk[k], :3] = c
        t = Image.fromarray(o, 'RGBA'); bg = Image.new('RGBA', t.size, (58, 62, 70, 255)); bg.paste(t, (0, 0), t)
        ImageDraw.Draw(bg).text((3, 3), str(i), fill=(255, 255, 0)); sheet.paste(bg, ((i % cols) * W, (i // cols) * H))
    sheet.save(path)


def main():
    frames, masks, med = load()
    if len(sys.argv) > 2 and sys.argv[1] == 'preview': return preview(sys.argv[2], frames, masks, med)
    if len(sys.argv) > 2 and sys.argv[1] == 'masks': return masks_sheet(sys.argv[2], frames, masks)
    for num, label, spec in VARIANTS:
        sheet = np.hstack([recolor(f, mk, spec, med) for f, mk in zip(frames, masks)])
        Image.fromarray(sheet, 'RGBA').save(f'assets/sprites/merc/paladin_{num}.webp', 'WEBP', lossless=True)
        print(f'paladin_{num}.webp  {label}')


if __name__ == '__main__':
    main()

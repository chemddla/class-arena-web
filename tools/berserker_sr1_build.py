# 광전사 시크릿 레어(흑사자: 검은 갈기·붉은 눈·검은 판금·쌍도끼) 샘플 → 캐릭터 시트 assets/sprites/merc/berserker_sr1.webp
# 사용: python tools/berserker_sr1_build.py   (샘플은 assets/sprites/fx/samples/berserker_sr1_*_src.png)
# 칸 순서 (동작 샘플이 오는 대로 늘림): 0 대기 · 1~3 걷기 · 4 피격 · 5~7 쓰러짐 · 8~9 기본 공격 · 10~11 도끼 투척 · 12~13 야성의 포효 · 14 찍기 (마무리 일격·대지 가르기) · 15~16 마무리 일격 점프 · 17~18 불사의 분노 (시전 · 발동) · 19~20 광폭화 (시전 붉은 기운 · 발동 불길, 반투명)
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

THROW1_BODY_H = 172  # 던짐 칸: 갈기 꼭대기~발 (샘플 px)을 190으로 맞추면 머리가 대기보다 작아 보여서 1.1배
IDLE_SRC_H = 163  # 대기 샘플 갈기~발 키 (샘플 px). 키로 못 재는 칸은 눈 사이 거리를 대기 샘플과 비교해 이것의 몇 배로 그렸는지로 맞춤
LIFT = {'jump0': 14, 'jump1': 20}  # 땅에서 띄워 그릴 높이 (칸 px) — 점프 샘플엔 그림자가 없어서
RAGE_BODY_H = 151  # 광폭화 샘플의 사자 몸 키 (기운·불길을 뺀 어두운 몸, 샘플 px)
ATK0_FIX = 0.8   # 기 모으기 칸은 같은 샘플 안에서도 X자 칸보다 크게 그려짐 (사자가 대기보다 25% 커 보였음)
ATK_BODY_H = 287  # 공격 샘플의 사자 몸 키 (X자 칸 갈기 꼭대기~발, 샘플 px). 치켜든 도끼·X자 때문에 그림 키로는 못 맞춰서 두 칸 모두 이 값으로
# (샘플 이름, 칸 이름, 키를 대기와 같게 맞춘 뒤 곱할 값, 샘플 안 몇 번째 그림(왼쪽부터))
FRAMES = [
    ('idle', 'idle', 1, 0),
    ('walk_a', 'walk0', 1, 0), ('walk_b', 'walk1', 1, 0), ('walk_b', 'walk2', 1, 1),  # 걷기 3칸 (walk_b 한 장에 두 칸)
    ('hurt', 'hurt', 1, 0),
    ('down', 'down0', 1, 0), ('down', 'down1', 'down0', 1), ('down', 'down2', 'down0', 2),  # 쓰러짐 3칸: 누운 칸은 키로 못 재서 첫 칸(서 있음) 배율을 같이 씀
    ('atk', 'atk0', ('h', ATK_BODY_H / ATK0_FIX), (0, 462)), ('atk', 'atk1', ('h', ATK_BODY_H), (472, 1024)),
    ('throw_a', 'throw0', 1, 0), ('throw_b', 'throw1', ('h', THROW1_BODY_H), 0),  # 도끼 투척: 치켜듦 → 던짐 (던진 쪽 왼쪽 도끼는 지움)
    ('howl_a', 'howl0', 1, 0), ('howl_b', 'howl1', 1, 0),  # 야성의 포효: 이를 악묾 → 포효
    ('slam', 'slam', ('h', IDLE_SRC_H * 1.7), (0, 368)),  # 마무리 일격·대지 가르기 찍기 (불꽃·흙덩이는 그림 그대로)
    ('jump', 'jump0', ('h', IDLE_SRC_H * 1.1), 0), ('jump', 'jump1', ('h', IDLE_SRC_H * 1.1), 1),  # 마무리 일격 점프 (땅에서 띄움 — LIFT)
    ('und_a', 'ucast', 1, 0), ('und_b', 'ufire', 1, 0),  # 히든 불사의 분노: 시전 → 발동
    ('rage', 'rage0', ('h', RAGE_BODY_H), (0, 166)), ('rage', 'rage1', ('h', RAGE_BODY_H), (166, 375)),  # 광폭화: 시전(붉은 기운) → 발동(불길)  # 기본 공격: 기 모으기 → X자 베기 (X자 이펙트는 그림 그대로)
]


HAFT_ERASE = {'throw_b': [(50, 82, 98, 142)]}  # 지운 도끼 자루가 몸으로 이어지는 상자
DROP = {'walk_b': [(0, 18, 140, 200)], 'down': [(0, 723, 147, 155)],
        'atk': [(460, 472, 0, 454), (120, 330, 425, 454), (655, 870, 424, 454)],
        'throw_b': [(0, 52, 20, 140)]}  # 던짐 칸 왼쪽 끝 도끼 머리·붉은 기운  # 지울 상자 (x0, x1, y0, y1): 걷기 샘플 왼쪽 끝에 잘려 들어온 앞 칸 도끼, 쓰러짐 샘플 아래 어두운 띠 (세 칸을 한 덩어리로 이어 붙였음),
#   공격 샘플의 칸 사이 세로선·아래 제목 글씨·맨 아래 띠


# 공격 샘플의 도끼 날이 원본(대기)과 달리 가시처럼 삐죽해서, 날 상자 안에서 가시 사이를 메우고 튀어나온 가시를 깎아 매끈한 초승달 날로
#   (x0, x1, y0, y1) — 기 모으기: 왼쪽 날·갈기 뒤 위쪽 날, X자 베기: 아래 왼쪽 날·아래 오른쪽 날
NO_GAP = {'atk': [(700, 1024, 0, 345)]}  # 갇힌 흰·밝은 틈을 지우지 않을 상자 (x0, x1, y0, y1): X자 이펙트 (밝은 속이 지워졌음)
AXE_FIX = {}  # 예전 공격 샘플은 날이 가시 모양이라 다듬었지만, 새 샘플은 원본 도끼 그대로라 안 씀


def smooth_blade(im, bg, box):
    # 상자 둘레 PADpx 여백까지 같이 보고 계산 (상자 밖을 배경으로 보면 상자 경계를 따라 날이 잘렸음), 바꾸는 건 상자 안쪽만
    from frost_variants_build import rgb2hsv
    P = 6
    x0, x1, y0, y1 = box
    X0, X1, Y0, Y1 = max(0, x0 - P), min(im.shape[1], x1 + P), max(0, y0 - P), min(im.shape[0], y1 + P)
    sub = im[Y0:Y1, X0:X1]
    sil = ~bg[Y0:Y1, X0:X1]
    inbox = np.zeros(sil.shape, bool); inbox[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = True
    # 날 상자 안의 아주 밝은 무채색 = 흰 배경이 섞인 틈 (원본 도끼에는 이렇게 밝은 곳이 없음) → 배경으로
    sil &= ~(inbox & (sub.min(axis=2) > 180) & (sub.max(axis=2) - sub.min(axis=2) < 30))
    hsv = rgb2hsv(sub / 255.)
    sat, val = hsv[..., 1], hsv[..., 2]
    haft = sil & (sat > 0.3) & (val > 0.2)  # 갈색 자루는 그대로
    disk = lambda r: (np.add.outer(np.arange(-r, r + 1) ** 2, np.arange(-r, r + 1) ** 2) <= r * r)
    smooth = ndi.binary_opening(ndi.binary_closing(sil, disk(4)), disk(2)) | haft
    add = smooth & ~sil & inbox            # 가시 사이 메울 곳
    cut = sil & ~smooth & inbox            # 깎을 가시
    new = (sil | add) & ~cut
    inner = sil & ~cut & ~haft & (val > 0.13) & (val < 0.38)  # 메울 색은 어두운 날 색에서만 (밝은 하이라이트를 가져오면 흰 얼룩처럼 보였음)
    _, (iy, ix) = ndi.distance_transform_edt(~inner, return_indices=True)
    out = sub.copy()
    out[add] = sub[iy[add], ix[add]]
    # 새로 생긴 바깥 테두리(배경과 닿은 곳)만 검은 윤곽 + 그 안 1px 밝은 날 테두리 (원본 대기 도끼 색)
    edge = new & ndi.binary_dilation(~new) & inbox & ~haft & (ndi.binary_dilation(add | cut, iterations=2))
    rim = new & ~edge & ndi.binary_dilation(edge) & inbox & ~haft
    out[edge] = [19, 15, 18]
    out[rim] = [120, 110, 110]
    im = im.copy(); bg = bg.copy()
    im[Y0:Y1, X0:X1] = out
    bg[Y0:Y1, X0:X1] = ~new
    return im, bg


GLOW = ('rage',)  # 흰 배경 위 반투명 붉은 기운·불길 샘플: 몸 바깥은 흰색을 빼서 투명도·본래 색을 되살림


def fix_x_rim(p):
    # 검붉은 X자 가장자리: 흰 배경과 섞였던 반투명 테두리가 너무 밝은 빨강(255, 55, 55)이나 회색으로 남음 → X자 안쪽 검붉은 색으로
    c = p.astype(int)
    op = c[..., 3] > 0
    bright = op & (c[..., 0] > 140) & (c[..., 1] < 100) & (c[..., 0] > c[..., 1] + 70)  # X자 색(빨강 124 이하)보다 밝은 빨강
    red = op & (c[..., 0] > c[..., 1] + 60) & ~bright
    grey = op & (c[..., :3].max(axis=2) - c[..., :3].min(axis=2) < 40) & (c[..., :3].mean(axis=2) > 150) & ndi.binary_dilation(red | bright, iterations=2)
    out = p.copy()
    out[bright | grey, :3] = [72, 13, 15]
    # 검은 윤곽선 + 안쪽으로 그라데이션: X자 둘레 1px = 검정, 2px = 검정 65%, 3px = 검정 35%, 그 안 = 지금 색
    x = red | bright | grey
    # X자 = 가장 큰 붉은 덩어리 (사자 눈·어깨 뿔은 작아서 빠짐), 안쪽 어두운 결·구멍까지 메움
    lab, n = ndi.label(x, np.ones((3, 3)))
    x = lab == np.argmax(ndi.sum(x, lab, range(1, n + 1))) + 1
    x = ndi.binary_fill_holes(ndi.binary_closing(x, np.ones((3, 3)), iterations=2)) & op
    d = ndi.distance_transform_cdt(x, metric='chessboard')
    o = out.astype(float)
    black = np.array([14, 6, 8], float)
    for dist, k in ((1, 1.0), (2, 0.65), (3, 0.35)):
        m = x & (d == dist)
        o[m, :3] = o[m, :3] * (1 - k) + black * k
    o[(d == 1) & x, 3] = 255  # 윤곽선은 불투명하게 (반투명이면 배경에 묻혀 안 보임)
    return o.clip(0, 255).astype(np.uint8)


def clean_specks(p):
    # 줄이면서 몸 안에 1~3px 흰 점으로 남은 반짝임(검은 갑옷에 어울리지 않음) → 가까운 어두운 몸 색으로
    c = p.astype(int)
    white = (c[..., 3] > 0) & (c[..., :3].min(axis=2) > 200)
    lab, n = ndi.label(white, np.ones((3, 3)))
    if not n: return p
    sz = ndi.sum(white, lab, range(1, n + 1))
    speck = np.isin(lab, 1 + np.where(sz <= 3)[0])
    src = (c[..., 3] > 0) & ~white
    _, (iy, ix) = ndi.distance_transform_edt(~src, return_indices=True)
    out = p.copy()
    out[speck, :3] = p[iy[speck], ix[speck], :3]
    return out


def shrink_soft(rgba, sc):
    # 반투명 빛을 살린 채 줄이기 (shrink는 가장자리를 딱딱하게 해서 붉은 기운이 사라졌음). 몸(불투명)은 그대로 또렷
    h, w = rgba.shape[:2]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    a = np.array(Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * sc)), max(1, round(h * sc))), Image.LANCZOS)).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    a[..., 3:] = np.where(al > 235, 255, np.where(al < 12, 0, al))
    return a.clip(0, 255).astype(np.uint8)


def load_glow(name, pick):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    full_w = im.shape[1]
    im = im[:, pick[0]:pick[1]]
    dark = im.max(axis=2) < 110
    lab, n = ndi.label(ndi.binary_dilation(dark, iterations=2))
    body = (lab == np.argmax(ndi.sum(dark, lab, range(1, n + 1))) + 1) & dark
    # 몸 = 어두운 픽셀 덩어리를 닫고 구멍을 메운 것 + 둘레 1px 중 밝지 않은 것 (밝은 분홍 가장자리까지 몸으로 잡으면 흰 테두리가 남았음)
    body = ndi.binary_fill_holes(ndi.binary_closing(body, iterations=2))
    body |= ndi.binary_dilation(body) & (im.max(axis=2) < 120)
    # 몸 바깥: 흰색에 섞인 만큼 투명 (초록·파랑이 255에서 줄어든 만큼 = 붉은 빛의 진하기)
    a = np.clip((255 - im[..., 1:].min(axis=2)) / 220, 0, 1)
    a = np.where(a < 0.06, 0, a)
    al = np.maximum(a, 1e-3)[..., None]
    rgb = np.where(body[..., None], im, ((im - 255 * (1 - al)) / al).clip(0, 255))
    a = np.where(body, 1.0, a)
    ys = np.where(body.any(axis=1))[0]
    bot = ys.max()
    a[bot + 1:] = 0  # 발 아래로 번진 빛은 자름 (발 = 칸 기준점)
    # 한 장에서 두 칸을 자른 경계 쪽 12px은 빛을 서서히 옅게 (세로로 잘린 자국이 보였음)
    W = a.shape[1]
    left = np.arange(W) + (12 if pick[0] == 0 else 0)            # 샘플 왼쪽 끝이면 옅게 하지 않음
    right = W - 1 - np.arange(W) + (12 if pick[1] >= full_w else 0)
    ramp = np.clip(np.minimum(left, right) / 12, 0, 1)
    a = np.where(body, a, a * ramp[None, :])
    yy, xx = np.where(a > 0)
    rgba = np.dstack([rgb, a * 255])[yy.min():bot + 1, xx.min():xx.max() + 1]
    bx = np.where(body[bot - 6:bot + 1].any(axis=0))[0]
    return rgba, (bx.min() + bx.max()) / 2 - xx.min()


# 흑사자 X자 베기의 회색 X자 → 검붉은 색 (흑사자 마무리 일격 이펙트 색감을 어둡게, 밝기 단계별)
X_RECOLOR = {'atk': [(690, 1024, 0, 368)]}
X_RAMP_L = np.array([40, 95, 135, 170, 205, 240])
X_RAMP = np.array([[22, 3, 5], [45, 7, 9], [64, 11, 13], [84, 16, 18], [102, 24, 25], [124, 36, 36]], float)  # 검붉은 색 (거의 검은 핏빛)


def recolor_x(im, bg, box):
    # 상자 안 무채색 덩어리 중 큰 것(X자 이펙트)만: 도끼 날 하이라이트는 작은 조각이라 빠짐
    x0, x1, y0, y1 = box
    sub = im[y0:y1, x0:x1]
    grey = ~bg[y0:y1, x0:x1] & (sub.max(axis=2) - sub.min(axis=2) < 28) & (sub.mean(axis=2) > 95)
    # 사자 몸 테두리의 회색(검은 몸에 바로 닿은 곳)은 X자가 아님 — 붉게 칠하면 머리 둘레가 붉은 선으로 물들었음
    grey &= ~(ndi.binary_dilation(sub.max(axis=2) < 60, iterations=2) & (sub.mean(axis=2) < 150))
    lab, n = ndi.label(grey, np.ones((3, 3)))
    if not n: return im
    sz = ndi.sum(grey, lab, range(1, n + 1))
    x = np.isin(lab, 1 + np.where(sz >= 200)[0])
    L = sub.mean(axis=2)
    out = sub.copy()
    for ch in range(3):
        out[..., ch] = np.where(x, np.interp(L, X_RAMP_L, X_RAMP[:, ch]), sub[..., ch])
    im = im.copy(); im[y0:y1, x0:x1] = out
    return im


def load(name, pick=0):
    if name in GLOW: return load_glow(name, pick)
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    # 몸 안에 갇힌 흰 배경 (팔과 도끼 자루 사이 등): 아주 하얀 3px 넘는 덩어리 (갑옷 하이라이트는 회색이라 남음)
    ids = np.arange(1, n + 1)
    gap = np.isin(lab, ids[(ndi.sum(white, lab, ids) >= 3) & (ndi.mean(im.min(axis=2), lab, ids) > 232)])
    keep = np.zeros_like(gap)
    for x0, x1, y0, y1 in NO_GAP.get(name, ()): keep[y0:y1, x0:x1] = True  # X자 이펙트 속(밝은 회색)은 남김 — 아주 하얀 틈은 X자 상자 안에서도 배경
    bg |= gap
    # 갇힌 틈 중 흰 배경과 섞여 조금 어두운 것(밝기 185 넘는 무채색 덩어리, 갑옷 하이라이트는 2px 안팎이라 빠짐)도 배경
    lt = (im.min(axis=2) > 185) & (im.max(axis=2) - im.min(axis=2) < 30) & ~bg & ~keep
    lab2, n2 = ndi.label(lt)
    ids2 = np.arange(1, n2 + 1)
    bg |= np.isin(lab2, ids2[ndi.sum(lt, lab2, ids2) >= 4])
    for x0, x1, y0, y1 in DROP.get(name, ()): bg[y0:y1, x0:x1] = True
    for x0, x1, y0, y1 in HAFT_ERASE.get(name, ()):
        # 지운 도끼의 갈색 자루: 상자 안 갈색 픽셀을 지우고, 몸 안쪽에 난 구멍은 가까운 어두운 몸 색으로 메움
        sub, sb = im[y0:y1, x0:x1], bg[y0:y1, x0:x1]
        brown = ~sb & (sub[..., 0] > sub[..., 2] + 12) & (sub[..., 0] > 55)
        keep = ~sb & ~brown
        fill = ndi.binary_closing(keep, np.ones((5, 5))) & brown
        dark = keep & (sub.max(axis=2) < 80)
        _, (iy, ix) = ndi.distance_transform_edt(~dark, return_indices=True)
        sub[fill] = sub[iy[fill], ix[fill]]
        sb |= brown & ~fill
    for box in AXE_FIX.get(name, ()):
        im, bg = smooth_blade(im, bg, box)
    for box in X_RECOLOR.get(name, ()):
        im = recolor_x(im, bg, box)
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
    if isinstance(pick, tuple):  # (x0, x1): 이 범위 안의 큰 덩어리 모두 (X자처럼 몸에서 떨어진 이펙트도 남김)
        cx = ndi.center_of_mass(m, lab, range(1, n + 1))
        keep = [i + 1 for i in range(n) if sz[i] >= 20 and pick[0] <= cx[i][1] < pick[1]]
        a = np.where(np.isin(lab, keep), a, 0)
    else:
        a = np.where(lab == bigs[pick], a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # 발 가운데 (아래 8%의 불투명 픽셀 가운데)
    k = rgba[..., 3] > 0
    foot = np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()
    return rgba, foot


OUT_UCAST_FX = 'assets/sprites/fx/berserker_sr1_ucast.webp'


def build_ucast_fx():
    # 히든 불사의 분노 시전 때 몸을 감싸는 붉은 반구: 흰 배경에 섞인 만큼 투명 (초록·파랑이 255에서 줄어든 만큼), 흰색을 빼서 본래 색으로
    im = np.array(Image.open(f'{D}ucast_fx_src.png').convert('RGB')).astype(float)
    a = np.clip((255 - im[..., 1:].min(axis=2)) / 225, 0, 1)
    a = np.where(a < 0.05, 0, a)
    al = np.maximum(a, 1e-3)[..., None]
    rgb = ((im - 255 * (1 - al)) / al).clip(0, 255)
    ys, xs = np.where(a > 0)
    out = np.dstack([rgb, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Image.fromarray(out.clip(0, 255).astype(np.uint8), 'RGBA').save(OUT_UCAST_FX, 'WEBP', lossless=True)
    print(f'ucast fx {out.shape[1]}x{out.shape[0]}')


OUT_UFIRE_FX = 'assets/sprites/fx/berserker_sr1_ufire.webp'
UFIRE_FOOT = (85, 100)   # 발동 이펙트 샘플에서 사자 발(핏빛 웅덩이 가운데) 자리
UFIRE_BODY_H = 95        # 갈기 꼭대기~발 키 (샘플 px) — 게임에서 이 키를 캐릭터 키에 맞춤


def build_ufire_fx():
    # 히든 불사의 분노 발동: 붉은 사자 실루엣 + 핏빛 웅덩이. 흰 배경에 섞인 만큼 투명, 흰색을 빼서 본래 색으로
    im = np.array(Image.open(f'{D}ufire_fx_src.png').convert('RGB')).astype(float)
    a = np.clip((255 - im[..., 1:].min(axis=2)) / 225, 0, 1)
    a = np.where(a < 0.05, 0, a)
    al = np.maximum(a, 1e-3)[..., None]
    rgb = ((im - 255 * (1 - al)) / al).clip(0, 255)
    ys, xs = np.where(a > 0)
    y0, x0 = ys.min(), xs.min()
    out = np.dstack([rgb, a * 255])[y0:ys.max() + 1, x0:xs.max() + 1]
    Image.fromarray(out.clip(0, 255).astype(np.uint8), 'RGBA').save(OUT_UFIRE_FX, 'WEBP', lossless=True)
    print(f'ufire fx {out.shape[1]}x{out.shape[0]} foot=({UFIRE_FOOT[0] - x0},{UFIRE_FOOT[1] - y0}) bodyH={UFIRE_BODY_H}')


OUT_EXEC_FX = 'assets/sprites/fx/berserker_sr1_slam.webp'


def build_exec_fx():
    # 흑사자 마무리 일격 폭발: 흰 배경(가장자리에서 이어진 것)만 지우고 둘레 2px은 흰색을 빼서 반투명, 날아가는 돌 조각도 남김
    im = np.array(Image.open(f'{D}exec_fx_src.png').convert('RGB')).astype(float)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    bg |= (im.min(axis=2) > 238) & (im.max(axis=2) - im.min(axis=2) < 15)  # 불꽃 사이에 갇힌 흰 배경
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    rgb = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    ys, xs = np.where(a > 0.05)
    out = np.dstack([rgb, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Image.fromarray(out.clip(0, 255).astype(np.uint8), 'RGBA').save(OUT_EXEC_FX, 'WEBP', lossless=True)
    print(f'exec fx {out.shape[1]}x{out.shape[0]}')


def main():
    cuts = {f[1]: load(f[0], f[3]) for f in FRAMES}
    pieces = []
    scale = {}
    for src, name, k, _ in FRAMES:
        rgba, foot = cuts[name]
        # 샘플마다 그린 크기가 달라 칸마다 키(갈기 꼭대기~발)로 맞춤. k가 칸 이름이면 그 칸 배율을 그대로 (누운 칸)
        sc = scale[k] if isinstance(k, str) else (TARGET_H / k[1] if isinstance(k, tuple) else TARGET_H / rgba.shape[0] * k)
        scale[name] = sc
        p = shrink_soft(rgba, sc) if src in GLOW else shrink(rgba, sc)
        if src not in GLOW: p = clean_specks(p)  # X자 칸도 (X자가 붉어져서 흰 점 정리에 안 걸림)
        if name == 'atk1': p = fix_x_rim(p)
        pieces.append((name, p, foot * sc))
    L = max(int(np.ceil(c)) for _, _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 4
    H = max(p.shape[0] + LIFT.get(n, 0) for n, p, _ in pieces) + 5
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = H - 2 - p.shape[0] - LIFT.get(name, 0)
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'sr1 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)}')


if __name__ == '__main__':
    main()
    build_ucast_fx()
    build_ufire_fx()
    build_exec_fx()

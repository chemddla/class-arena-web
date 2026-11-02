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

ATK0_FIX = 0.8   # 기 모으기 칸은 같은 샘플 안에서도 X자 칸보다 크게 그려짐 (사자가 대기보다 25% 커 보였음)
ATK_BODY_H = 287  # 공격 샘플의 사자 몸 키 (X자 칸 갈기 꼭대기~발, 샘플 px). 치켜든 도끼·X자 때문에 그림 키로는 못 맞춰서 두 칸 모두 이 값으로
# (샘플 이름, 칸 이름, 키를 대기와 같게 맞춘 뒤 곱할 값, 샘플 안 몇 번째 그림(왼쪽부터))
FRAMES = [
    ('idle', 'idle', 1, 0),
    ('walk_a', 'walk0', 1, 0), ('walk_b', 'walk1', 1, 0), ('walk_b', 'walk2', 1, 1),  # 걷기 3칸 (walk_b 한 장에 두 칸)
    ('hurt', 'hurt', 1, 0),
    ('down', 'down0', 1, 0), ('down', 'down1', 'down0', 1), ('down', 'down2', 'down0', 2),  # 쓰러짐 3칸: 누운 칸은 키로 못 재서 첫 칸(서 있음) 배율을 같이 씀
    ('atk', 'atk0', ('h', ATK_BODY_H / ATK0_FIX), (0, 462)), ('atk', 'atk1', ('h', ATK_BODY_H), (472, 1024)),  # 기본 공격: 기 모으기 → X자 베기 (X자 이펙트는 그림 그대로)
]


DROP = {'walk_b': [(0, 18, 140, 200)], 'down': [(0, 723, 147, 155)],
        'atk': [(460, 472, 0, 454), (120, 330, 425, 454), (655, 870, 424, 454)]}  # 지울 상자 (x0, x1, y0, y1): 걷기 샘플 왼쪽 끝에 잘려 들어온 앞 칸 도끼, 쓰러짐 샘플 아래 어두운 띠 (세 칸을 한 덩어리로 이어 붙였음),
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


def load(name, pick=0):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    # 몸 안에 갇힌 흰 배경 (팔과 도끼 자루 사이 등): 아주 하얀 3px 넘는 덩어리 (갑옷 하이라이트는 회색이라 남음)
    ids = np.arange(1, n + 1)
    gap = np.isin(lab, ids[(ndi.sum(white, lab, ids) >= 3) & (ndi.mean(im.min(axis=2), lab, ids) > 232)])
    keep = np.zeros_like(gap)
    for x0, x1, y0, y1 in NO_GAP.get(name, ()): keep[y0:y1, x0:x1] = True  # X자 이펙트 속은 남김
    gap &= ~keep
    bg |= gap
    # 갇힌 틈 중 흰 배경과 섞여 조금 어두운 것(밝기 185 넘는 무채색 덩어리, 갑옷 하이라이트는 2px 안팎이라 빠짐)도 배경
    lt = (im.min(axis=2) > 185) & (im.max(axis=2) - im.min(axis=2) < 30) & ~bg & ~keep
    lab2, n2 = ndi.label(lt)
    ids2 = np.arange(1, n2 + 1)
    bg |= np.isin(lab2, ids2[ndi.sum(lt, lab2, ids2) >= 4])
    for x0, x1, y0, y1 in DROP.get(name, ()): bg[y0:y1, x0:x1] = True
    for box in AXE_FIX.get(name, ()):
        im, bg = smooth_blade(im, bg, box)
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


def main():
    cuts = {f[1]: load(f[0], f[3]) for f in FRAMES}
    pieces = []
    scale = {}
    for src, name, k, _ in FRAMES:
        rgba, foot = cuts[name]
        # 샘플마다 그린 크기가 달라 칸마다 키(갈기 꼭대기~발)로 맞춤. k가 칸 이름이면 그 칸 배율을 그대로 (누운 칸)
        sc = scale[k] if isinstance(k, str) else (TARGET_H / k[1] if isinstance(k, tuple) else TARGET_H / rgba.shape[0] * k)
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

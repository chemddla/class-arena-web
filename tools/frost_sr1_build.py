# 빙결술사 시크릿 레어(얼음 여왕·옥좌) 샘플(초록 배경) → 캐릭터 시트 assets/sprites/merc/frost_sr1.webp + 전용 이펙트 assets/sprites/fx/frost_sr_fx.webp
# 사용: python tools/frost_sr1_build.py   (샘플은 assets/sprites/fx/samples/frost_sr1_*_src.*)
# 칸 순서는 frost_0과 같음: 0 대기 · 1~4 걷기 · 5~7 공격 · 8~9 피격 · 10~12 쓰러짐 · 13~15 아이스애로우 · 16~17 배리어 · 18~21 프리즈 · 22~24 동결 · 25~27 스케이팅
# 이펙트: shard = 공격 칸에서 날아가는 얼음 조각(기본 공격 투사체, 기준점 = 앞 끝), circle = 아이스애로우 마법진, dome = 배리어 얼음 돔,
#   star = 동결 반짝임 (circle·dome·star 기준점 = 한가운데)
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

D = 'assets/sprites/fx/samples/frost_sr1_'
OUT = 'assets/sprites/merc/frost_sr1.webp'
OUT_FX = 'assets/sprites/fx/frost_sr_fx.webp'
SCALE = 0.7           # 샘플 옥좌 꼭대기~바닥 약 143px → 게임 약 100px
BG = np.array([29, 240, 14], float)
SRC = {}


def load(n):
    if n not in SRC:
        f = D + n + ('_src.webp' if n == '1' else '_src.png')
        SRC[n] = np.array(Image.open(f).convert('RGB')).astype(float)
    return SRC[n]


def key(rgb):
    # 초록 우세도로 불투명도. 캐릭터 색(파랑·흰색·살색)은 초록이 가장 높지 않아서 초록 넘침은 r·b 최댓값으로 깎아도 안전
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    gd = g - np.maximum(r, b)
    a = np.clip(1 - (gd - 20) / 170, 0, 1)
    col = (rgb - (1 - a[..., None]) * BG) / np.maximum(a[..., None], 0.05)
    col = np.clip(col, 0, 255)
    col[..., 1] = np.minimum(col[..., 1], np.maximum(col[..., 0], col[..., 2]) + 12)
    return col, a


def cut(n, x0, x1, y0, y1, minpiece=12, drop_dark=False):
    rgb = load(n)[y0:y1, x0:x1]
    col, a = key(rgb)
    m = a > 0.5
    lab, k = ndi.label(ndi.binary_dilation(m, iterations=2))
    keep = np.zeros_like(m)
    for i in range(1, k + 1):
        p = m & (lab == i)
        if p.sum() < minpiece: continue
        if drop_dark and col[p].mean() < 60: continue  # 옆 칸에서 넘어온 검은 조각
        keep |= lab == i
    a = a * keep
    return np.dstack([col, a * 255])


def shrink(rgba, soft=False, scale=SCALE):
    h, w = rgba.shape[:2]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    sm = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    a = np.array(sm).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    if not soft: a[..., 3:] = np.where(al > 110, 255, np.where(al > 50, al * 1.6, 0))  # 도트 느낌: 가장자리를 딱딱하게
    return a.clip(0, 255).astype(np.uint8)


def trim(p):
    ys, xs = np.where(p[..., 3] > 0)
    return p[ys.min():ys.max() + 1, xs.min():xs.max() + 1], xs.min(), ys.min()


def dome_split():
    # 배리어 돔 칸: 돔이 캐릭터 위에 반투명 흰빛으로 덮여 있음 → 돔 빛깔(흰 섞임 비율 t, 색 w)을 돔 안 빈 곳에서 재고
    # 캐릭터 자리는 섞임을 되돌려 캐릭터만 꺼냄. 돔 이펙트는 캐릭터 자리를 평균 돔 빛으로 메움
    rgb = load('3')[0:144, 152:345]
    # 돔 안 빈 곳(초록이 비치는 곳)에서 섞임 추정: out = (1-t)*BG + t*W
    gd = rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2])
    inside = (gd > 20) & (gd < 150)
    W = np.array([225, 245, 250], float)
    t = np.clip((BG[1] - np.maximum(BG[0], BG[2]) - gd) / (BG[1] - np.maximum(BG[0], BG[2]) - (W[1] - max(W[0], W[2]))), 0, 1)
    tin = np.median(t[inside & (np.arange(rgb.shape[0])[:, None] > 60)])
    return rgb, t, tin, W


def main():
    P = {}
    # 기본 동작 시트 (1024×572, 왼쪽 라벨은 x<200)
    P['move0'] = cut('1', 205, 352, 0, 143)
    P['move1'] = cut('1', 395, 530, 0, 143)
    P['atk0'] = cut('1', 225, 345, 144, 288)
    P['atk1'] = cut('1', 400, 528, 144, 288)
    P['atk2'] = cut('1', 615, 745, 144, 288)
    P['hurt0'] = cut('1', 205, 350, 284, 430)
    P['hurt1'] = cut('1', 398, 520, 284, 430)
    P['down0'] = cut('1', 198, 382, 430, 572)
    P['down1'] = cut('1', 410, 572, 430, 572)
    P['down2'] = cut('1', 605, 792, 490, 572)
    P['arrow'] = cut('2', 0, 104, 3, 146)
    P['bar0'] = cut('3', 0, 140, 0, 144)
    P['nova0'] = cut('5', 8, 112, 0, 149, drop_dark=True)
    P['nova1'] = cut('5', 140, 325, 0, 149)
    P['df0'] = cut('6', 0, 125, 0, 137)
    P['df1'] = cut('6', 180, 330, 0, 137)
    P['skate'] = cut('4', 0, 198, 0, 147)
    # 배리어 2: 돔에 덮인 캐릭터는 흰빛이 짙어 되살리면 색이 탁해서, 링 없이 팔짱 낀 같은 자세(배리어 1)를 한 번 더 씀
    rgb, t, tin, W = dome_split()
    gd = rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2])

    order = ['move0', 'move0', 'move1', 'move0', 'move1', 'atk0', 'atk1', 'atk2', 'hurt0', 'hurt1', 'down0', 'down1', 'down2',
             'move0', 'arrow', 'arrow', 'bar0', 'bar0', 'nova0', 'nova0', 'nova1', 'nova1', 'df0', 'df1', 'df0', 'skate', 'skate', 'skate']
    # 기준점 x = 옥좌 받침 가운데 (원본 칸 안 x). 누운 칸은 몸 가운데
    CX = {'move0': 85, 'move1': 67, 'atk0': 60, 'atk1': 63, 'atk2': 62, 'hurt0': 77, 'hurt1': 58, 'down0': 88, 'down1': 70, 'down2': 92,
          'arrow': 55, 'bar0': 66, 'nova0': 44, 'nova1': 96, 'df0': 62, 'df1': 78, 'skate': 140}
    pieces = {}
    for nm, rgba in P.items():
        s = shrink(rgba)
        ys, xs = np.where(s[..., 3] > 0)
        cx = CX[nm] * SCALE
        foot = ys.max() + 1
        pieces[nm] = (s, cx, foot)
    L = max(int(np.ceil(c)) for s, c, f in pieces.values()) + 2
    R = max(int(np.ceil(s.shape[1] - c)) for s, c, f in pieces.values()) + 2
    H = max(f for s, c, f in pieces.values()) - min(np.where(s[..., 3] > 0)[0].min() for s, c, f in pieces.values()) + 4
    cellW = L + R
    sheet = np.zeros((H, cellW * len(order), 4), np.uint8)
    for i, nm in enumerate(order):
        s, c, foot = pieces[nm]
        x = i * cellW + L - int(round(c))
        y = H - 2 - foot
        y0 = max(0, -y)
        sheet[y + y0:y + foot, x:x + s.shape[1]] = np.where(s[y0:foot, :, 3:] > 0, s[y0:foot], sheet[y + y0:y + foot, x:x + s.shape[1]])
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    top = np.where(sheet[:, :cellW, 3].any(axis=1))[0].min()
    print(f'cellW={cellW} cellH={H} anchorX={L} anchorY={H - 2} topH={H - 2 - top}')

    # ===== 전용 이펙트 =====
    fx = {}
    shard = cut('1', 748, 890, 160, 265, minpiece=4)
    fx['shard'] = trim(shrink(shard, soft=True, scale=0.6))[0]
    circ = cut('2', 104, 155, 3, 146, minpiece=2)
    fx['circle'] = trim(shrink(circ, soft=True, scale=1.0))[0]
    star = cut('6', 128, 180, 30, 90, minpiece=2)
    fx['star'] = trim(shrink(star, soft=True, scale=1.0))[0]
    # 돔: 테두리(바깥 8px)와 반짝임·눈꽃은 샘플 그대로, 안쪽은 캐릭터가 비치지 않게 고른 돔 빛으로 메움
    dome = ndi.binary_fill_holes(gd <= 205)
    inner = ndi.binary_erosion(dome, iterations=8)
    dome_a = np.where(dome, t, 0)
    dcol = (rgb - (1 - dome_a[..., None]) * BG) / np.maximum(dome_a[..., None], 0.05)
    sparkle = inner & (rgb.min(axis=2) > 225)  # 하얀 반짝임·눈꽃
    fill = inner & ~ndi.binary_dilation(sparkle, iterations=1)
    # 안쪽 빛: 가운데는 거의 투명, 테두리로 갈수록 짙어지는 유리 구슬 느낌 (위쪽은 조금 더 밝게)
    dist = ndi.distance_transform_edt(dome)
    q = np.clip(dist / dist.max(), 0, 1)
    yy = np.linspace(1, 0, rgb.shape[0])[:, None]
    glass = 0.08 + 0.42 * (1 - q) ** 2.2 + 0.06 * yy
    dome_a = np.where(fill, glass, dome_a)
    dcol = np.where(fill[..., None], np.array([200, 236, 252], float), dcol)
    dcol = np.clip(dcol, 0, 255)
    dcol[..., 1] = np.minimum(dcol[..., 1], np.maximum(dcol[..., 0], dcol[..., 2]) + 12)
    fx['dome'] = trim(shrink(np.dstack([dcol, dome_a * 255]), soft=True, scale=1.0))[0]
    names = ['shard', 'circle', 'dome', 'star']
    FW = sum(fx[n].shape[1] + 2 for n in names)
    FH = max(fx[n].shape[0] for n in names)
    atlas = np.zeros((FH, FW, 4), np.uint8)
    x = 0
    for n in names:
        p = fx[n]
        atlas[:p.shape[0], x:x + p.shape[1]] = p
        ax = p.shape[1] - 1 if n == 'shard' else p.shape[1] / 2
        print(f"{n}: [{x},0,{p.shape[1]},{p.shape[0]},{ax},{p.shape[0] / 2}]")
        x += p.shape[1] + 2
    Image.fromarray(atlas, 'RGBA').save(OUT_FX, 'WEBP', lossless=True)


if __name__ == '__main__':
    main()

# 주술사 시크릿 레어(역병 의사: 새부리 가면·검은 후드·보라 구슬 지팡이) 샘플 → 캐릭터 시트 assets/sprites/merc/curse_sr1.webp
# 사용: python tools/curse_sr1_build.py   (샘플은 assets/sprites/fx/samples/curse_sr1_*_src.*)
# 칸 순서는 curse_0과 같음: 0 대기 · 1~4 걷기 · 5~6 공격 · 7~8 피격 · 9~11 쓰러짐 · 12 저주 · 13~14 쇠약 · 15~16 파쇄
#   · 17~19 흡혼 · 20~21 저주의 늪
# 샘플:
#   idle·attack·hurt·death = 초록 배경 (idle 왼쪽 위에 검은 글씨 라벨 박힘 → 지움)
#   walk·skill1·skill2 = 회색 판 위에 그린 것 (판마다 위에 칸 번호 글씨). 판 가장자리에서 판 색을 채워 나가 배경을 지움
#   (검은 외곽선이 있어서 어두운 망토도 배경으로 새지 않음)
# 샘플 정리:
#   - 걷기는 3칸이라 1~4 = 1, 2, 3, 2번째 칸
#   - 공격 2번째 칸(지팡이 내지르기)은 skill1의 '#6 발동' 칸
#   - 피격은 1칸 + 쓰러짐 샘플 첫 칸(뒤로 젖힌 자세), 쓰러짐 = 쓰러짐 샘플 3칸
#   - ✦ 워터마크·라벨 글씨 지움
#   - 샘플마다 캐릭터 크기가 달라서 후드 꼭대기~발 키를 대기 자세에 맞춰 샘플별 배율을 씀
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

D = 'assets/sprites/fx/samples/curse_sr1_'
OUT = 'assets/sprites/merc/curse_sr1.webp'
TARGET_H = 86   # 대기 자세 후드 꼭대기~옷자락 끝 (게임 칸 px). curse_0 칸 높이 안에 들어가는 크기


def load(name):
    return np.array(Image.open(D + name).convert('RGB')).astype(float)


def key_green(rgb):
    # 초록 우세도로 불투명도, 반투명 가장자리는 배경색을 빼서 복원 (frost_sr1_build.py와 같은 방식)
    bg = np.median(np.concatenate([rgb[:4].reshape(-1, 3), rgb[-4:].reshape(-1, 3)]), axis=0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    gd = g - np.maximum(r, b)
    a = np.clip(1 - (gd - 20) / 170, 0, 1)
    col = (rgb - (1 - a[..., None]) * bg) / np.maximum(a[..., None], 0.05)
    col = np.clip(col, 0, 255)
    col[..., 1] = np.minimum(col[..., 1], np.maximum(col[..., 0], col[..., 2]) + 12)
    return col, a


def key_panel(rgb, tol=13):
    # 판 가장자리에서 판 색과 비슷한 곳을 채워 나가 배경으로 봄
    edge = np.concatenate([rgb[:3].reshape(-1, 3), rgb[-3:].reshape(-1, 3), rgb[:, :3].reshape(-1, 3), rgb[:, -3:].reshape(-1, 3)])
    pc = np.median(edge, axis=0)
    near = np.abs(rgb - pc).max(-1) < tol
    lab, _ = ndi.label(near)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, border[border > 0])
    a = (~bg).astype(float)
    # 판 색이 살짝 섞인 가장자리 1px은 지움
    fringe = (a > 0) & ndi.binary_dilation(bg, iterations=1) & (np.abs(rgb - pc).max(-1) < 24)
    a[fringe] = 0
    return rgb, a


def clean(col, a, minpiece=20, erase=()):
    for x0, x1, y0, y1 in erase: a[y0:y1, x0:x1] = 0
    m = a > 0.5
    lab, k = ndi.label(ndi.binary_dilation(m, iterations=2))
    areas = ndi.sum(m, lab, range(1, k + 1))
    a = a * np.isin(lab, 1 + np.where(areas >= minpiece)[0])
    return np.dstack([col, a * 255])


def green(name, box=None, erase=()):
    rgb = load(name)
    if box: rgb = rgb[box[2]:box[3], box[0]:box[1]]
    col, a = key_green(rgb)
    # 쓰러짐 샘플 아래·오른쪽 가장자리에 박힌 흰 테두리: 가장자리와 이어진 흰색은 지움
    lab, _ = ndi.label(rgb.min(-1) > 200)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    a = np.where(np.isin(lab, edge[edge > 0]), 0, a)
    return clean(col, a, erase=erase)


def panel(name, box, erase=()):
    rgb = load(name)[box[2]:box[3], box[0]:box[1]]
    col, a = key_panel(rgb)
    return clean(col, a, erase=erase)


def shrink(rgba, scale):
    h, w = rgba.shape[:2]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    sm = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    a = np.array(sm).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    a[..., 3:] = np.where(al > 110, 255, np.where(al > 50, al * 1.6, 0))  # 도트 느낌: 가장자리를 딱딱하게
    return a.clip(0, 255).astype(np.uint8)


def pieces():
    P = {}
    P['idle'] = green('idle_src.png', erase=[(0, 75, 0, 78)])
    W = [(7, 343, 51, 378), (350, 685, 51, 378), (692, 1024, 51, 378)]
    P['walk0'] = panel('walk_src.png', W[0])
    P['walk1'] = panel('walk_src.png', W[1])
    P['walk2'] = panel('walk_src.png', W[2], erase=[(225, 290, 220, 290)])
    P['atk0'] = green('attack_src.png')
    P['hurt0'] = green('hurt_src.png')
    P['down0'] = green('death_src.png', (0, 185, 0, 161))
    P['down1'] = green('death_src.png', (185, 392, 0, 161))
    P['down2'] = green('death_src.png', (392, 593, 0, 161), erase=[(125, 180, 25, 95)])
    S1 = [(0, 302, 41, 336), (308, 612, 41, 336), (0, 302, 386, 680), (308, 612, 386, 680), (0, 302, 730, 1024), (308, 612, 730, 1024)]
    for nm, b in zip(['hex0', 'atk1', 'weak0', 'weak1', 'shat0', 'shat1'], S1):
        P[nm] = panel('skill1_src.webp', b)
    S2 = [(8, 338, 46, 366), (345, 675, 46, 366), (682, 1012, 46, 366), (8, 338, 420, 740), (345, 676, 420, 740)]
    for nm, b in zip(['sip0', 'sip1', 'sip2', 'swamp0', 'swamp1'], S2):
        P[nm] = panel('skill2_src.webp', b)
    return P


ORDER = ['idle', 'walk0', 'walk1', 'walk2', 'walk1', 'atk0', 'atk1', 'hurt0', 'down0', 'down0', 'down1', 'down2',
         'hex0', 'weak0', 'weak1', 'shat0', 'shat1', 'sip0', 'sip1', 'sip2', 'swamp0', 'swamp1']
# 칸별 (샘플에서 서 있을 때 후드 꼭대기~옷자락 끝 키, 발 y, 기준점 x). 키로 배율을 정해 샘플마다 다른 캐릭터 크기를 맞춤
# 숙이거나 누운 칸은 같은 샘플의 서 있는 키를 씀. 발 y·기준점 x는 옷자락 끝·두 발 가운데 (이펙트가 발밑에 깔린 칸은 눈으로 잼)
FIT = {
    'idle': (228, 286, 120),
    'walk0': (207, 283, 145), 'walk1': (207, 282, 150), 'walk2': (207, 283, 152),
    'atk0': (143, 150, 52), 'hurt0': (143, 154, 80),
    'down0': (143, 152, 80), 'down1': (143, 151, 115), 'down2': (143, 152, 95),
    'hex0': (168, 252, 128), 'atk1': (168, 250, 127), 'weak0': (168, 266, 135), 'weak1': (168, 262, 125),
    'shat0': (168, 253, 128), 'shat1': (168, 250, 120),
    'sip0': (170, 268, 140), 'sip1': (170, 269, 132), 'sip2': (170, 272, 142),
    'swamp0': (196, 272, 140), 'swamp1': (170, 274, 145),
}


def main():
    P = pieces()
    fitted = {}
    for nm, rgba in P.items():
        h, foot, cx = FIT[nm]
        sc = TARGET_H / h
        s = shrink(rgba, sc)
        fitted[nm] = (s, cx * sc, foot * sc)
    L = max(int(np.ceil(c)) for s, c, f in fitted.values()) + 2
    R = max(int(np.ceil(s.shape[1] - c)) for s, c, f in fitted.values()) + 2
    up = max(int(np.ceil(f - np.where(s[..., 3] > 0)[0].min())) for s, c, f in fitted.values()) + 2
    down = max(int(np.ceil(np.where(s[..., 3] > 0)[0].max() + 1 - f)) for s, c, f in fitted.values()) + 1
    cellW, H = L + R, up + max(down, 2)
    sheet = np.zeros((H, cellW * len(ORDER), 4), np.uint8)
    for i, nm in enumerate(ORDER):
        s, c, f = fitted[nm]
        x = i * cellW + L - int(round(c))
        y = up - int(round(f))
        y0, y1 = max(0, -y), min(s.shape[0], H - y)
        tgt = sheet[y + y0:y + y1, x:x + s.shape[1]]
        sheet[y + y0:y + y1, x:x + s.shape[1]] = np.where(s[y0:y1, :, 3:] > 0, s[y0:y1], tgt)
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    idle = sheet[:, :cellW, 3] > 0
    top = np.where(idle.any(axis=1))[0].min()
    hx = np.where(idle[top:top + 15].any(axis=0))[0]
    print(f'cellW={cellW} cellH={H} anchorX={L} anchorY={up} count={len(ORDER)} topH={up - top} portraitCX={int(hx.mean())}')


if __name__ == '__main__':
    main()

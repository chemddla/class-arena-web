# 음유시인 원형 샘플(초록 배경 도트 4장) → 캐릭터 시트 assets/sprites/merc/bard_0.webp
# 사용: python tools/bard_build.py [샘플 폴더]  (기본 assets/sprites/fx/samples, 파일 bard_src1~4.png)
#   1 = 대기 1칸 + 걷기 4칸 (왼쪽 한글 라벨, 오른쪽 위 공유·복사·저장 버튼 박힘), 2 = 기본 공격, 3 = 피격, 4 = 쓰러짐 3칸
#   5~7 = 전투의 노래 (5 류트 튕기며 음표 = 시전, 맨 위 흰 줄은 뺌, 6 발밑 불꽃 = 발동, 7 불꽃·음표·화살표 = 고양)
#   8~10 = 수호의 선율 (8 발밑 빛기둥 = 시전, 9 빛의 돔 = 발동, 10 음표·물결 = 선율)
#   11~13 = 불협화음 (11 발밑 보랏빛 번개·파편 = 시전, 12 몸 양옆 번개 = 발동, 13 번개 폭발·깨진 음표 = 침묵)
#   14~16 = 질풍의 리듬 (14 류트 옆 바람 한 줄, 15 몸을 감는 바람·화살표, 16 바람 소용돌이·음표 — 시전 없이 바로 씀)
#   20~22 = 히든 앙코르 (20 시전 두 칸: 금빛 고리·음표 / 고리·화살표·별, 21 시전: 오선·음표 물결 (큰 그림, webp, 연한 초록 ✦ 워터마크 2개 지움), 22 발동: 류트를 치켜든 자세)
# 캐릭터 칸 순서: 0 대기 · 1~4 걷기 · 5 공격 · 6 피격 · 7~9 쓰러짐 · 10~12 전투의 노래 · 13~15 수호의 선율 · 16~18 불협화음 · 19~21 질풍의 리듬 · 22~24 앙코르 시전 · 25 앙코르 발동 (모든 칸 크기 같음, 오른쪽을 봄, 발 = 기준점)
# 샘플 정리:
#   - 배경은 밝은 초록 두 가지(바깥 / 칸 안쪽)라 색 하나로 빼지 않고 "밝고 초록이 강한" 픽셀을 배경으로 봄. 베레모·조끼 초록은 어두워서 남음
#   - 공격 칸 둘레에 떠 있는 음표는 기본 공격 구슬로 따로 그리므로 지움 (가장 큰 덩어리 + 몸통의 4% 넘는 조각만 남김)
#   - 쓰러짐 칸에서 날아간 모자·류트는 남기고, 옆 반짝임(✦)처럼 작은 조각은 지움
#   - 전투의 노래 칸은 자기 주변 기술이라 음표·불꽃·화살표를 그대로 남김. 불꽃이 발보다 넓고 아래로 퍼져서 발 위치는 불꽃 색을 뺀 부츠로 잼
#   - 수호의 선율 칸은 배경이 순수 초록(0,240,0)이고 그 위에 반투명 청록 빛이 겹쳐 있음 → 밝은 픽셀은 초록이 얼마나 남았는지로 투명도를 정하고
#     배경색을 빼서 빛 색을 복원 (빛을 불투명 덩어리로 두거나 잘라 내지 않음). 도트 가장자리 딱딱하게 만들기도 이 칸들은 건너뜀
#   - 샘플마다 그린 크기가 달라 베레모 폭을 대기 자세에 맞춰 배율을 따로 씀. 전투의 노래 칸은 음표·불꽃이 베레모에 붙어 있어 폭 대신 부츠~베레모 키로 맞춤
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT_CHAR = 'assets/sprites/merc/bard_0.webp'
TARGET_H = 84  # 대기 자세 모자 끝~발 → 게임 칸 키

# (시트, 이름, x0, x1, y0, y1)
FRAMES = [
    (1, 'idle',  100, 262,   0, 184),
    (1, 'walk0', 100, 262, 184, 384), (1, 'walk1', 262, 432, 184, 384),
    (1, 'walk2', 432, 604, 184, 384), (1, 'walk3', 604, 775, 184, 384),
    (2, 'atk0',    0, 210,   0, 193),
    (3, 'hurt0',   0, 172,   0, 176),
    (4, 'down0',   0, 212,   0, 178), (4, 'down1', 218, 436, 0, 178), (4, 'down2', 440, 640, 0, 178),  # 아래·오른쪽 끝 흰 테두리는 뺌
    (5, 'song0', 0, 153, 3, 152), (6, 'song1', 0, 220, 0, 201), (7, 'song2', 0, 272, 0, 216),
    (8, 'guard0', 0, 197, 0, 209), (9, 'guard1', 0, 274, 0, 209), (10, 'guard2', 0, 270, 0, 205),
    (11, 'disso0', 0, 222, 0, 195), (12, 'disso1', 0, 181, 0, 193), (13, 'disso2', 0, 299, 0, 202),
    (14, 'tempo0', 0, 191, 0, 211), (15, 'tempo1', 0, 275, 0, 202), (16, 'tempo2', 0, 250, 0, 212),
    (20, 'enc0', 0, 272, 0, 204), (20, 'enc1', 272, 539, 0, 204), (21, 'enc2', 0, 1024, 0, 723),  # 20번 맨 아래 어두운 줄은 뺌
    (22, 'cheer', 0, 177, 0, 204),  # 맨 아래 어두운 줄은 뺌
]
BERET_FROM = {1: 'idle', 2: 'atk0', 3: 'hurt0'}
STAND_H = {20: 184, 21: 588, 22: 191}  # 앙코르 샘플의 베레모 꼭대기~발바닥 키 (금빛 고리가 베레모 폭 재기를 방해해서 키로 맞춤, 대기 샘플은 183)  # 시트마다 베레모 폭을 잴 칸. 쓰러짐 시트는 기울어진 몸이라 폭을 못 재서 대기 시트 배율을 그대로 씀 (얼굴 크기가 같게 그려져 있음)
SRC = {}
BODY_H = {}  # 이펙트 칸(전투의 노래·수호의 선율)의 부츠~베레모 키 (cut에서 잼)
FX_FRAMES = ('song', 'guard', 'disso', 'tempo', 'enc')  # 이펙트를 시트에 그대로 남기는 칸
FOOT = {'tempo2': (110, 202), 'enc0': (125, 201), 'enc1': (402, 201), 'enc2': (480, 660)}  # 소용돌이가 다리를 가려 몸통을 못 찾는 칸: 샘플 좌표의 부츠 가운데·발바닥 (배율은 tempo1과 같게 씀)
GLOW_SHEETS = (8, 9, 10, 14, 15, 16, 20, 21)  # 반투명 빛·바람이 겹친 샘플 (질풍의 리듬 소용돌이 안쪽 초록 바람은 배경과 색이 가까워 옅게 남음)


def load(sheet, folder):
    if sheet not in SRC:
        path = f'{folder}/bard_src{sheet}.webp' if sheet == 21 else f'{folder}/bard_src{sheet}.png'
        im = np.array(Image.open(path).convert('RGB')).astype(float)
        r, g, b = im[..., 0], im[..., 1], im[..., 2]
        bg = (g > 135) & (g - np.maximum(r, b) > 50)  # 베레모·조끼 초록은 G 120 안팎이라 남음
        a = np.where(bg, 0.0, 1.0)
        # 배경과 맞닿은 2px 띠의 초록 번짐 억제 (베레모·조끼 안쪽은 그대로)
        near = ndi.binary_dilation(bg, iterations=2) & ~bg
        rgb = im.copy()
        lift = near & (g - np.maximum(r, b) > 30)
        rgb[..., 1] = np.where(lift, np.maximum(r, b) + 20, g)
        if sheet in GLOW_SHEETS:
            K = np.array([0.0, 240.0, 0.0])
            ex = g - np.maximum(r, b)
            a = np.where(g > 190, np.clip(1 - (ex - 20) / 180, 0, 1), 1.0)  # 베레모·조끼(G 120 안팎)는 불투명 그대로
            # 푸른 기가 없는 반투명 픽셀 = 몸 윤곽과 배경이 섞인 테두리 → 빛으로 살리지 않고 배경처럼 지움 (몸에 초록 띠가 남지 않게)
            a = np.where((a < 1) & (b < r + 30) & (b < 90), np.where(bg, 0.0, 1.0), a)
            al = np.maximum(a, 1e-3)[..., None]
            rgb = np.where((a < 1)[..., None], K + (im - K) / al, im).clip(0, 255)
        if sheet == 21:  # 연한 초록 ✦ 워터마크 2개 (류트 머리 뒤 · 오른쪽 아래): 초록이 강한 픽셀만 지워서 류트·금빛 바람은 남김
            for y0, y1, x0, x1 in ((265, 370, 590, 690), (595, 650, 895, 950)):
                box = (g[y0:y1, x0:x1] - np.maximum(r, b)[y0:y1, x0:x1]) > 40
                a[y0:y1, x0:x1][box] = 0
        if sheet == 1:
            a[:, :100] = 0           # 왼쪽 라벨 글자
            a[:60, 600:] = 0         # 공유·복사·저장 버튼
        SRC[sheet] = (rgb, a)
    return SRC[sheet]


def cut(folder, f):
    sheet, name, x0, x1, y0, y1 = f
    rgb, a = load(sheet, folder)
    rgb, a = rgb[y0:y1, x0:x1].copy(), a[y0:y1, x0:x1].copy()
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=1))
    areas = ndi.sum(m, lab, range(1, n + 1))
    big = np.argmax(areas) + 1
    keep = m & (lab == big)
    if name[:4] == 'down':  # 날아간 모자·류트는 남김
        for i in range(1, n + 1):
            if i != big and areas[i - 1] >= areas[big - 1] * 0.04: keep |= m & (lab == i)
    if name.startswith(FX_FRAMES):  # 음표·불꽃·화살표·빛은 모두 남기고 압축 티끌만 지움
        keep = m & np.isin(lab, 1 + np.where(areas >= 12)[0])
    a = np.where(keep, a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([rgb, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 0
    low = k[int(k.shape[0] * 0.75):] if name[:4] != 'down' else k
    cx = np.where(low.any(axis=0))[0].mean()
    below = 0  # 발바닥 아래로 내려간 픽셀 수
    if name.startswith(FX_FRAMES):
        R, G, B = rgba[..., 0], rgba[..., 1], rgba[..., 2]
        fire = (R > 170) & (R > B + 70)  # 불꽃·음표·화살표 (주황·노랑·빨강)
        glow = (B > R + 40) & (G > R + 40)  # 청록 빛·음표
        bolt = (B > G + 50) & (R > G + 30)  # 보랏빛 번개·화살표
        bolt |= (B > R + 60) & (B > G + 20)  # 파란 화살표
        body = (rgba[..., 3] > 250) & ~ndi.binary_dilation(fire | glow | bolt, iterations=2)
        lab, n = ndi.label(body)
        body = lab == np.argmax(ndi.sum(body, lab, range(1, n + 1))) + 1
        ys = np.where(body.any(axis=1))[0]; foot = ys.max()
        cx = np.where(body[foot - (foot - ys.min()) // 4:foot + 1].any(axis=0))[0].mean()
        below = rgba.shape[0] - 1 - foot
        BODY_H[name] = foot - ys.min() + 1
    if name in FOOT:
        y_top, x_left = np.where(keep)[0].min(), np.where(keep)[1].min()
        cx = FOOT[name][0] - x0 - x_left
        below = rgba.shape[0] - 1 - (FOOT[name][1] - y0 - y_top)
    return rgba, cx, below


def beret_w(rgba):
    # 위쪽 1/3에서 어두운 초록(베레모) 폭
    top = rgba[:rgba.shape[0] // 3]
    R, G, B, A = (top[..., i] for i in range(4))
    m = (A > 0) & (G > R + 25) & (G > B + 20)
    xs = np.where(m.any(axis=0))[0]
    return xs.max() - xs.min() + 1


def shrink(rgba, sc, hard=True):
    h, w = rgba.shape[:2]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    sm = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * sc)), max(1, round(h * sc))), Image.LANCZOS)
    a = np.array(sm).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    if hard: a[..., 3:] = np.where(al > 90, 255, np.where(al > 40, al * 2, 0))  # 도트 느낌: 반투명 가장자리를 딱딱하게
    return a.clip(0, 255).astype(np.uint8)


def main(folder):
    cuts = {f[1]: cut(folder, f) for f in FRAMES}
    base = TARGET_H / cuts['idle'][0].shape[0]
    bw_idle = beret_w(cuts['idle'][0])
    scale = {s: base * bw_idle / beret_w(cuts[nm][0]) for s, nm in BERET_FROM.items()}
    scale[4] = scale[1]
    for sh, nm in ((5, 'song0'), (6, 'song1'), (7, 'song2'), (8, 'guard0'), (9, 'guard1'), (10, 'guard2'), (11, 'disso0'), (12, 'disso1'), (13, 'disso2'), (14, 'tempo0'), (15, 'tempo1')): scale[sh] = base * cuts['idle'][0].shape[0] / BODY_H[nm]
    scale[16] = scale[15]
    for sh, h in STAND_H.items(): scale[sh] = scale[1] * 183 / h
    print('scales', {s: round(v, 3) for s, v in scale.items()})
    pieces = []
    for f in FRAMES:
        rgba, cx, below = cuts[f[1]]
        sc = scale[f[0]]
        pieces.append((f[1], shrink(rgba, sc, f[0] not in GLOW_SHEETS), cx * sc, int(round(below * sc))))
    L = max(int(np.ceil(c)) for _, _, c, _ in pieces) + 2
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c, _ in pieces) + 2
    B = max(d for _, _, _, d in pieces)
    H = max(p.shape[0] - d for _, p, _, d in pieces) + B + 3
    cellW = L + R
    sheet = np.zeros((H, cellW * len(pieces), 4), np.uint8)
    for i, (name, p, c, d) in enumerate(pieces):
        x = i * cellW + L - int(round(c))
        y = H - 2 - B - p.shape[0] + d   # 발 = 기준점 (칸 아래에서 B + 2px 위)
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT_CHAR, 'WEBP', lossless=True)
    idle = pieces[0][1]
    hx = np.where(idle[:int(idle.shape[0] * 0.5), :, 3].any(axis=0))[0]
    print(f'char cellW={cellW} cellH={H} anchorX={L} anchorY={H - 2 - B} count={len(pieces)} topH={idle.shape[0]} portraitCX={L - int(round(pieces[0][2])) + int(hx.mean())}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/fx/samples')

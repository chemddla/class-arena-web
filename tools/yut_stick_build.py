# 윷가락 한 개 던지기 도트 시트 → assets/sprites/fx/yut_stick.webp
# 사용: python tools/yut_stick_build.py [미리보기 폴더]
# 칸 40×84, 가로 16프레임(던짐→회전 비행→착지→튕김→멈춤), 세로 4줄 = 마지막 면
#   0: 평평한 면(앞) 1: 둥근 면(뒤) 2: 빽도 표시 윷의 평평한 면 3: 빽도 표시 윷의 둥근 면
# 첫 칸은 반대 면으로 놓인 채 시작, 마지막 칸이 결과 면. 화면에는 2배(image-rendering: pixelated)로 쓰면 됨.
import math, os, sys
import numpy as np
from PIL import Image

OUT = 'assets/sprites/fx/yut_stick.webp'
CW, CH = 40, 84          # 칸 크기
L, W = 34, 8             # 윷가락 길이·폭
T = 4                    # 두께(옆면이 보일 때 폭)
GX, GY = 20, 62          # 바닥에 놓인 윷가락 중심
PEAK = 40                # 가장 높이 뜬 높이
FRAMES = 16

C = lambda h, a=255: (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), a)
FLAT = [C('#d9b26f'), C('#ecc98b'), C('#f8e2b2'), C('#fdf0d0')]   # 가장자리 → 가운데
ROUND = [C('#5e2c0c'), C('#7f3d12'), C('#a2541a'), C('#c9732b')]
GRAIN = C('#d4a865')
MARK = C('#6e3012')
MARK_RED = C('#d42a2a')
OUTLINE = C('#3d1d08')
SHADOW = (70, 38, 14)
DUST = [C('#ffffff'), C('#c9a66b')]


def face_strip(kind, width, marked):
    """한 면을 width 폭으로 눌러 그린 L×width 조각 (가로=폭, 세로=길이)."""
    if width <= 0:
        return np.zeros((L, 0, 4), np.uint8)
    pal = FLAT if kind == 'flat' else ROUND
    s = np.zeros((L, width, 4), np.uint8)
    for x in range(width):
        # 가운데로 갈수록 밝게 (둥근 면은 원통 음영, 평평한 면은 살짝)
        d = abs((x + 0.5) / width - 0.5) * 2          # 0 가운데, 1 가장자리
        k = 3 - min(3, int(d * 4))
        if kind == 'round' and width >= 4 and x == int(width * 0.35):
            k = 3                                      # 둥근 면 반사광 한 줄
        s[:, x] = pal[k]
    if kind == 'flat' and width >= 4:
        for y in range(3, L - 3, 7):                   # 나뭇결
            s[y, 1 + (y // 7) % max(1, width - 2)] = GRAIN
    if kind == 'flat' and width >= 5:                  # ✕ 표시 두 개
        col = MARK_RED if marked else MARK
        cx = width // 2
        for cy in (int(L * 0.27), int(L * 0.73)):
            for t in (-1, 0, 1):
                s[cy + t, cx + t] = col
                s[cy + t, cx - t] = col
            if marked and cy == int(L * 0.27):
                s[L // 2 - 1:L // 2 + 1, cx - 1:cx + 1] = MARK_RED
            if width >= 7:
                s[cy - 2, cx - 2] = s[cy - 2, cx + 2] = s[cy + 2, cx - 2] = s[cy + 2, cx + 2] = col
    return s


def stick_tex(phi, marked):
    """phi=0 평평한 면, phi=π 둥근 면이 보임. 사이 각도는 주면 + 옆면 조각."""
    c, sn = math.cos(phi), abs(math.sin(phi))
    main = 'flat' if c >= 0 else 'round'
    other = 'round' if main == 'flat' else 'flat'
    wm = int(round(W * abs(c)))
    wo = int(round(T * sn))
    if wm + wo < 3:
        wo = 3 - wm
    a = face_strip(main, wm, marked)
    b = face_strip(other, wo, marked)
    if b.shape[1]:                                     # 옆면은 한 단계 어둡게
        b = b.copy(); b[..., :3] = (b[..., :3] * 0.82).astype(np.uint8)
    tex = np.concatenate([a, b] if math.sin(phi) >= 0 else [b, a], axis=1)
    # 양 끝 모서리 깎기
    w = tex.shape[1]
    if w >= 4:
        for y in (0, L - 1):
            tex[y, 0, 3] = 0; tex[y, w - 1, 3] = 0
    return tex


def paste_rotated(cell, tex, cx, cy, ang, scale=1.0, flat_color=None):
    """tex 가운데를 (cx,cy)에 두고 ang(도)만큼 돌려 찍음. 가장 가까운 점으로 뽑아 도트 유지."""
    h, w = tex.shape[:2]
    r = math.radians(ang)
    ca, sa = math.cos(r), math.sin(r)
    for y in range(CH):
        for x in range(CW):
            dx, dy = (x + 0.5 - cx) / scale, (y + 0.5 - cy) / scale
            u = ca * dx + sa * dy + w / 2
            v = -sa * dx + ca * dy + h / 2
            iu, iv = int(math.floor(u)), int(math.floor(v))
            if 0 <= iu < w and 0 <= iv < h and tex[iv, iu, 3]:
                cell[y, x] = flat_color if flat_color is not None else tex[iv, iu]


def outline(cell, mask):
    m = np.pad(mask, 1)
    ring = (m[:-2, 1:-1] | m[2:, 1:-1] | m[1:-1, :-2] | m[1:-1, 2:]) & ~mask
    cell[ring] = OUTLINE


def ease_out(t):
    return 1 - (1 - t) ** 2


def frame_params(i, end_phi):
    """프레임마다 (높이, 회전각, 뒤집힘 각, 먼지)"""
    FLY = 10                                           # 0..10 비행
    if i <= FLY:
        u = i / FLY
        h = PEAK * 4 * u * (1 - u)
        ang = 360 * ease_out(u) * (1 if end_phi == 0 else -1)
        phi = end_phi + 3 * math.pi * (1 - ease_out(u))
        return h, ang, phi, 0
    tail = {11: (0, 0, 2), 12: (5, 10, 1), 13: (0, -6, 0), 14: (1, 3, 0), 15: (0, 0, 0)}[i]
    return tail[0], tail[1], end_phi, tail[2]


def render_cell(i, end_phi, marked):
    h, ang, phi, dust = frame_params(i, end_phi)
    cell = np.zeros((CH, CW, 4), np.uint8)
    # 그림자: 바닥에 그대로, 높이 뜰수록 작고 옅게
    tex = stick_tex(phi, marked)
    k = h / PEAK
    sh = np.zeros_like(cell)
    paste_rotated(sh, np.dstack([tex[..., :3], (tex[..., 3] > 0) * 255]).astype(np.uint8),
                  GX + 2, GY + 3, ang, scale=1 - 0.45 * k, flat_color=SHADOW + (int(110 - 60 * k),))
    cell[:] = sh
    body = np.zeros_like(cell)
    paste_rotated(body, tex, GX, GY - h, ang)
    mask = body[..., 3] > 0
    cell[mask] = body[mask]
    outline(cell, mask)
    if dust:                                           # 착지 먼지
        rng = np.random.default_rng(7 + i)
        for end in (-1, 1):
            ey = GY + end * (L // 2)
            for _ in range(3 + dust * 2):
                dx = int(rng.integers(-7, 8)); dy = int(rng.integers(-2, 3)) + (dust == 1) * -2
                x, y = GX + dx, ey + dy
                if 0 <= x < CW - 1 and 0 <= y < CH - 1 and not cell[y, x, 3]:
                    col = DUST[int(rng.integers(0, 2))]
                    cell[y:y + 1 + (dust == 2), x:x + 1 + (dust == 2)] = col
    return cell


ROWS = [(0.0, False), (math.pi, False), (0.0, True), (math.pi, True)]


def build():
    sheet = np.zeros((CH * len(ROWS), CW * FRAMES, 4), np.uint8)
    for r, (end_phi, marked) in enumerate(ROWS):
        for i in range(FRAMES):
            sheet[r * CH:(r + 1) * CH, i * CW:(i + 1) * CW] = render_cell(i, end_phi, marked)
    return sheet


def preview(sheet, outdir):
    """4개 동시 던지기 GIF(걸·빽도·모) + 전체 프레임 확대본"""
    os.makedirs(outdir, exist_ok=True)
    S, PITCH, DELAY = 3, 30, 1                         # 확대, 윷 간격, 윷마다 1프레임 늦게
    bg = (254, 243, 199, 255)
    for name, rows in (('geol', [2, 0, 0, 1]), ('backdo', [2, 1, 1, 1]), ('mo', [3, 1, 1, 1])):
        frames = []
        n = FRAMES + DELAY * 3 + 10
        for t in range(n):
            img = Image.new('RGBA', (PITCH * 3 + CW + 16, CH + 8), bg)
            for k, r in enumerate(rows):
                i = min(FRAMES - 1, max(0, t - k * DELAY))
                cell = Image.fromarray(sheet[r * CH:(r + 1) * CH, i * CW:(i + 1) * CW], 'RGBA')
                img.alpha_composite(cell, (8 + k * PITCH, 4))
            frames.append(img.convert('RGB').resize((img.width * S, img.height * S), Image.NEAREST))
        frames[0].save(os.path.join(outdir, f'yut_throw_{name}.gif'), save_all=True, append_images=frames[1:],
                       duration=[50] * (n - 1) + [900], loop=0)
    big = Image.new('RGBA', (sheet.shape[1], sheet.shape[0]), bg)
    big.alpha_composite(Image.fromarray(sheet, 'RGBA'))
    big.convert('RGB').resize((big.width * 3, big.height * 3), Image.NEAREST).save(os.path.join(outdir, 'yut_stick_sheet_x3.png'))


if __name__ == '__main__':
    sheet = build()
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(OUT, sheet.shape[1], 'x', sheet.shape[0])
    if len(sys.argv) > 1:
        preview(sheet, sys.argv[1])

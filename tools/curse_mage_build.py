# 주술사 원형 샘플(초록 배경 도트 시트 4장, 한글 라벨 박힘) → 캐릭터 시트 assets/sprites/merc/curse_0.webp + 이펙트 아틀라스 assets/sprites/fx/curse_fx.webp
# 사용: python tools/curse_mage_build.py [샘플 폴더]  (기본 assets/sprites/fx/samples, 파일 curse_mage_1~4.webp)
#   1 = 기본 동작, 2 = 저주·쇠약·파쇄·흡혼, 3 = 옛 저주의 늪 (발이 잘려서 안 씀), 4 = 스킬 이펙트 6줄 × 3칸 (마지막 파멸의 의식 줄은 안 씀)
#   저주의 늪 시전 동작은 따로 받은 curse_swamp_src.png 두 칸 (불꽃 두르기 → 지팡이 꽂아 가시 늪)
#   쇠약 동작은 따로 받은 curse_weak_src.png 두 칸 (오른쪽 = 지팡이 내리는 시전 자세, 왼쪽 = 덩굴·핏물이 솟는 발동) — 옛 시트 2의 쇠약 줄은 잘린 자리가 어색해서 안 씀
#   히든 스킬 [파멸의 의식]은 따로 받은 샘플로 tools/curse_ruin_build.py가 만듦
# 캐릭터 칸 순서: 0 대기 · 1~4 걷기 · 5~7 공격 · 8~9 피격 · 10~12 쓰러짐 · 13~15 저주 · 16~17 쇠약 · 18~20 파쇄
#   · 21~23 흡혼 · 24~25 저주의 늪 (모든 칸 크기 같음, 오른쪽을 봄, 발 = 기준점. 저주의 늪 칸은 발밑 늪이 기준점 아래로 내려감)
# 샘플 오류 정리:
#   - 초록 배경이 쇠약 덩굴(어두운 초록)·흡혼 빛(반투명)과 겹침 → 밝은 초록만 배경으로 보고, 반투명 가장자리는 배경색을 빼서 복원
#   - 흡혼·저주의 늪 칸은 이펙트 때문에 커 보이지만 캐릭터 키(뿔~발 약 190px)는 다른 칸과 같아 배율은 하나로 씀
#   - 캐릭터 칸에 그려진 땅 장판·날아가는 해골·튀는 파편·회오리는 이펙트로 따로 그리므로 캐릭터에서 지움 (흡혼은 자기 주변 기술이라 유령·빛을 남김)
#   - 이펙트 시트 오른쪽 아래 ✦ 워터마크 지움
#   - 저주의 늪 샘플은 캐릭터가 커서(뿔 폭 56px, 대기 시트는 약 30px) 칸 배율을 따로 씀. 불꽃·가시 늪은 시전 동작의 일부라 그대로 둠
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT_CHAR = 'assets/sprites/merc/curse_0.webp'
OUT_FX = 'assets/sprites/fx/curse_fx.webp'
KEY = np.array([18.0, 238.0, 4.0])
SCALE = 0.45  # 대기 자세 뿔 끝~발 196px → 게임 칸 약 88px

# (시트, 이름, x0, x1, y0, y1, 정리 방식) — main = 가장 큰 덩어리만, body = 이펙트 색을 지운 뒤 가장 큰 덩어리, all = 모두
FRAMES = [
    (1, 'idle',   95, 765,   0, 212, 'main'),
    (1, 'walk0',  95, 264, 212, 416, 'main'), (1, 'walk1', 264, 430, 212, 416, 'main'),
    (1, 'walk2', 430, 597, 212, 416, 'main'), (1, 'walk3', 597, 765, 212, 416, 'main'),
    (1, 'atk0',   90, 308, 416, 620, 'body'), (1, 'atk1', 308, 585, 416, 620, 'main'), (1, 'atk2', 585, 765, 416, 620, 'main'),
    (1, 'hurt0',  95, 300, 620, 818, 'main'), (1, 'hurt1', 300, 765, 620, 818, 'main'),
    (1, 'down0',  90, 298, 818, 1024, 'main'), (1, 'down1', 298, 531, 818, 1024, 'main'), (1, 'down2', 531, 765, 818, 1024, 'main'),
    (2, 'hex0',   95, 270,   0, 236, 'main'), (2, 'hex1', 270, 517, 0, 236, 'main'), (2, 'hex2', 517, 687, 0, 236, 'main'),
    (6, 'weak0', 295, 504,   0, 237, 'all'), (6, 'weak1',   0, 294, 0, 237, 'all'),
    (2, 'shat0',  95, 275, 460, 730, 'main'), (2, 'shat1', 275, 490, 460, 730, 'body'), (2, 'shat2', 490, 687, 460, 730, 'main'),
    (2, 'sip0',   75, 282, 740, 1024, 'all'), (2, 'sip1', 282, 500, 740, 1024, 'all'), (2, 'sip2', 500, 687, 740, 1024, 'all'),
    (5, 'swamp0',   0, 160,   0, 175, 'all'), (5, 'swamp1', 180, 406, 0, 175, 'all'),
]
# 칸마다 배율 따로: 저주의 늪·쇠약 샘플은 뿔 폭을 대기 자세와 맞춤, 저주 칸은 샘플 캐릭터가 약 6% 작게 그려져 있어 키움
FRAME_SCALE = {'swamp0': 0.58, 'swamp1': 0.58, 'weak0': 0.42, 'weak1': 0.44, **{f'hex{i}': SCALE * 1.06 for i in range(3)}}
FOOT = {'swamp0': (82, 148), 'swamp1': (272, 143), 'weak0': (387, 202), 'weak1': (150, 200)}  # 샘플 좌표의 발 가운데·발바닥 (늪·불꽃이 발보다 넓고 아래로 퍼져서 직접 지정)
XMAX = {'atk1': 505, 'hex1': 415}  # 지팡이·손끝 앞으로 날아가는 해골은 투사체로, 지팡이 끝 덩굴 고리는 장판 이펙트로 따로 그림
YMIN = {}
SRC = {}


def load(sheet, folder):
    if sheet not in SRC:
        path = {5: f'{folder}/curse_swamp_src.png', 6: f'{folder}/curse_weak_src.png'}.get(sheet, f'{folder}/curse_mage_{sheet}.webp')
        im = np.array(Image.open(path).convert('RGB')).astype(float)
        r, g, b = im[..., 0], im[..., 1], im[..., 2]
        d = np.sqrt(((im - KEY) ** 2).sum(axis=2))
        # 밝은 초록만 배경 후보: 어두운 초록(쇠약 덩굴)은 그대로 불투명
        bright = (g > 165) & (g - np.maximum(r, b) > 40)
        a = np.where(bright, np.clip((d - 45) / 150, 0, 1), 1.0)
        # 반투명 가장자리: 배경색을 빼서 본래 색 복원 + 남은 초록 기운 억제
        al = np.maximum(a, 1e-3)[..., None]
        rgb = np.where(a[..., None] < 1, KEY + (im - KEY) / al, im)
        spill = bright & (a < 1)
        rgb[..., 1] = np.where(spill, np.minimum(rgb[..., 1], np.maximum(rgb[..., 0], rgb[..., 2]) + 10), rgb[..., 1])
        # 배경과 맞닿은 2px 띠의 초록 번짐(압축 때 섞인 어두운 초록 테두리)도 억제
        near = ndi.binary_dilation(a < 0.5, iterations=2) & (a >= 0.5)
        if sheet == 4: near[140:248] = False  # 쇠약 줄은 덩굴 자체가 초록이라 그대로
        green = rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2])
        rgb[..., 1] = np.where(near & (green > 8), np.maximum(rgb[..., 0], rgb[..., 2]) + 4, rgb[..., 1])
        rgb = rgb.clip(0, 255)
        if sheet < 5: a[:, :95 if sheet < 3 else 185] = 0  # 왼쪽 라벨 글자
        if sheet == 4: a[670:690, 912:930] = 0  # ✦ 워터마크
        SRC[sheet] = (rgb, a)
    return SRC[sheet]


def cut(folder, f):
    sheet, name, x0, x1, y0, y1, mode = f
    rgb, a = load(sheet, folder)
    rgb, a = rgb[y0:y1, x0:x1].copy(), a[y0:y1, x0:x1].copy()
    if name in XMAX: a[:, XMAX[name] - x0:] = 0
    m = a > 0.35
    if mode == 'body':
        # 몸 색은 채도가 낮음(뼈·가죽·검붉은 망토), 주황 피부만 예외. 채도 높은 보라·빨강·초록·연보라 유령 = 이펙트
        R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        chroma = rgb.max(axis=2) - rgb.min(axis=2)
        warm = (R >= G) & (G >= B - 6)
        eff = ((chroma > 62) & ~warm) | ((rgb.min(axis=2) > 140) & (B > G + 18)) | ((R > G + 110) & (R > 170))
        eff = ndi.binary_dilation(eff, iterations=1)
        m &= ~eff
        m = ndi.binary_opening(m, iterations=1)
    if mode != 'all':
        lab, n = ndi.label(ndi.binary_dilation(m, iterations=1))
        areas = ndi.sum(m, lab, range(1, n + 1))
        big = np.argmax(areas) + 1
        keep = m & (lab == big)
        # 몸통에서 떨어진 큰 조각(지팡이 끝 깃털 등)은 남기되, 몸통 크기의 4% 미만 조각은 지움
        for i in range(1, n + 1):
            if i != big and areas[i - 1] >= areas[big - 1] * 0.04 and mode == 'main': keep |= m & (lab == i)
        m = keep
        if mode == 'body':
            # 발밑 어두운 장판: 허리 높이 몸 폭 바깥으로 퍼진 아래쪽 픽셀은 지움
            ys = np.where(m.any(axis=1))[0]; top, bot = ys.min(), ys.max()
            hip = m[top + int((bot - top) * 0.6): top + int((bot - top) * 0.72)]
            hx = np.where(hip.any(axis=0))[0]
            low = top + int((bot - top) * 0.8)
            m[low:, :max(0, hx.min() - 10)] = False
            m[low:, hx.max() + 10:] = False
            # 발 높이의 보라·초록 장판 색 (부츠·지팡이는 갈색, 망토 자락은 검붉은색이라 남음)
            pool = ((B > G + 10) & (B >= R - 12)) | (G > R + 8)
            if name[:4] == 'weak': pool |= R > G + 64  # 쇠약 칸은 붉은 덩굴도 장판
            m[low:] &= ~ndi.binary_dilation(pool, iterations=1)[low:]
            if name in YMIN: m[:YMIN[name] - y0] = False
            lab, n = ndi.label(ndi.binary_dilation(m, iterations=1))
            areas = ndi.sum(m, lab, range(1, n + 1))
            m &= lab == np.argmax(areas) + 1
    a = np.where(m, a, 0)
    ys, xs = np.where(a > 0)
    b = (xs.min(), xs.max() + 1, ys.min(), ys.max() + 1)
    rgba = np.dstack([rgb, a * 255])[b[2]:b[3], b[0]:b[1]]
    k = rgba[..., 3] > 0
    low = k[int(k.shape[0] * 0.75):] if name[:4] != 'down' else k
    cx = np.where(low.any(axis=0))[0].mean()
    below = 0  # 발바닥 아래로 내려간 픽셀 수
    if name in FOOT:
        cx = FOOT[name][0] - x0 - b[0]
        below = b[2] + rgba.shape[0] - (FOOT[name][1] - y0)
    return rgba, cx, below


def contact(folder, out):
    tiles = [cut(folder, f)[:2] for f in FRAMES]
    W = sum(t.shape[1] + 6 for t, _ in tiles); H = max(t.shape[0] for t, _ in tiles)
    img = np.full((H, W, 3), 60.0); x = 0
    for t, c in tiles:
        h, w = t.shape[:2]; al = t[..., 3:] / 255
        img[H - h:, x:x + w] = t[..., :3] * al + img[H - h:, x:x + w] * (1 - al)
        img[:, x + int(c)] = [255, 0, 0]
        x += w + 6
    Image.fromarray(img.astype(np.uint8)).save(out)
    for f, (t, c) in zip(FRAMES, tiles): print(f[1], t.shape[1], t.shape[0])


FX_SCALE = 0.8  # 게임에서 범위에 맞춰 키우므로 너무 작게 줄이지 않음
# 이펙트 시트 4: (이름, x0, x1, y0, y1, 기준점) — bottom = 바닥 가운데, center = 그림 가운데, head = 오른쪽 끝(날아가는 해골 머리)
FX_COLS = [(190, 420), (420, 740), (740, 1024)]
FX_ROWS = [('hex', 0, 128, ('center', 'head', 'head')), ('weak', 128, 248, 'bottom'), ('shat', 248, 382, ('center', 'bottom', 'bottom')),
           ('sip', 382, 505, 'center'), ('swamp', 505, 606, 'bottom')]


def fx_pieces(folder):
    rgb, a = load(4, folder)
    out = []
    for nm, y0, y1, anc in FX_ROWS:
        for j, (x0, x1) in enumerate(FX_COLS):
            al = a[y0:y1, x0:x1].copy()
            m = al > 0.05
            lab, n = ndi.label(m)
            areas = ndi.sum(m, lab, range(1, n + 1))
            for i in range(1, n + 1):
                if areas[i - 1] < 8: al[lab == i] = 0  # 압축 티끌
            ys, xs = np.where(al > 0.05)
            b = (xs.min(), xs.max() + 1, ys.min(), ys.max() + 1)
            rgba = np.dstack([rgb[y0:y1, x0:x1], al * 255])[b[2]:b[3], b[0]:b[1]]
            kind = anc if isinstance(anc, str) else anc[j]
            h, w = rgba.shape[:2]
            if kind == 'bottom': ax, ay = w / 2, h - 4
            elif kind == 'head': ax, ay = w - 22, np.where(rgba[:, -30:, 3].any(axis=1))[0].mean()
            else: ax, ay = w / 2, h / 2
            out.append((f'{nm}{j}', rgba, ax, ay))
    return out


def shrink(rgba, sc, hard):
    h, w = rgba.shape[:2]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    sm = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * sc)), max(1, round(h * sc))), Image.LANCZOS)
    a = np.array(sm).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    if hard: a[..., 3:] = np.where(al > 90, 255, np.where(al > 40, al * 2, 0))  # 도트 느낌: 반투명 가장자리를 딱딱하게
    return a.clip(0, 255).astype(np.uint8)


def main(folder):
    pieces = []
    for f in FRAMES:
        rgba, cx, below = cut(folder, f)
        sc = FRAME_SCALE.get(f[1], SCALE)
        p = shrink(rgba, sc, f[6] != 'all')
        pieces.append((f[1], p, cx * sc, int(round(below * sc))))
    L = max(int(np.ceil(c)) for _, _, c, _ in pieces) + 2
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c, _ in pieces) + 2
    B = max(d for _, _, _, d in pieces)
    H = max(p.shape[0] - d for _, p, _, d in pieces) + B + 3
    cellW = L + R
    sheet = np.zeros((H, cellW * len(pieces), 4), np.uint8)
    for i, (name, p, c, d) in enumerate(pieces):
        x = i * cellW + L - int(round(c))
        y = H - 2 - B - p.shape[0] + d   # 발 = 기준점 (칸 아래에서 B + 2px 위)
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = np.where(p[..., 3:] > 0, p, sheet[y:y + p.shape[0], x:x + p.shape[1]])
    Image.fromarray(sheet, 'RGBA').save(OUT_CHAR, 'WEBP', lossless=True)
    idle = pieces[0][1]
    hx = np.where(idle[:int(idle.shape[0] * 0.5), :, 3].any(axis=0))[0]
    print(f'char cellW={cellW} cellH={H} anchorX={L} anchorY={H - 2 - B} count={len(pieces)} topH={idle.shape[0]} portraitCX={L - int(round(pieces[0][2])) + int(hx.mean())}')
    # 이펙트 아틀라스: 가로로 이어 붙이고 프레임 [x, y, w, h, 기준점x, 기준점y]
    fx = [(n, shrink(p, FX_SCALE, False), ax * FX_SCALE, ay * FX_SCALE) for n, p, ax, ay in fx_pieces(folder)]
    W = sum(p.shape[1] + 2 for _, p, _, _ in fx); FH = max(p.shape[0] for _, p, _, _ in fx)
    atlas = np.zeros((FH, W, 4), np.uint8); x = 0; frames = []
    for n, p, ax, ay in fx:
        atlas[:p.shape[0], x:x + p.shape[1]] = p
        frames.append(f'{n}: [{x},0,{p.shape[1]},{p.shape[0]},{round(ax)},{round(ay)}]')
        x += p.shape[1] + 2
    Image.fromarray(atlas, 'RGBA').save(OUT_FX, 'WEBP', lossless=True)
    print('fx frames: { ' + ', '.join(frames) + ' }')


if __name__ == '__main__' and len(sys.argv) <= 2:
    main(sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/fx/samples')
if __name__ == '__main__' and len(sys.argv) > 2 and sys.argv[2] == 'contact':
    contact(sys.argv[1], sys.argv[3])
if __name__ == '__main__' and len(sys.argv) > 2 and sys.argv[2] == 'dump':
    folder = sys.argv[1]
    for s in (1, 2, 3, 4):
        rgb, a = load(s, folder)
        bg = np.full_like(rgb, 60.0)
        out = rgb * a[..., None] + bg * (1 - a[..., None])
        Image.fromarray(out.astype(np.uint8)).save(f'{sys.argv[3]}/key{s}.png')

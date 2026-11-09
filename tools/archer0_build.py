# 궁수 기본 외형(archer_0) 교체: 금발 포니테일·초록 머리띠·초록 망토·갈색 가죽옷·나무 활 샘플 → assets/sprites/merc/archer_0.webp
# 사용: python tools/archer0_build.py
# 샘플 (흰 배경 한 장, 왼쪽에 동작 이름 글씨): assets/sprites/merc/samples/archer_edit_1_src.png (1024×765)
#   대기 1 · 걷기 4 · 일반공격 2 · 피격 1 · 쓰러짐 2 (누운 칸 옆에 떨어진 활이 따로 있음 → 같은 칸에 넣음)
# 칸 순서: 0 대기 · 1~4 걷기 · 5~6 공격 (시위 당김 → 화살 놓기 직전) · 7 피격 · 8~9 쓰러짐 (뒤로 비틀 → 누움 + 떨어진 활)
#   · 10 화살비 (하늘로 활을 겨눔) · 11 회피기동 (뒤로 뛰어오르며 쏨, 공중이라 발밑을 띄움)
#   다른 스킬은 공격 칸을 같이 씀. 화살은 게임이 따로 날림 → 시위에 걸린 화살은 그림에 남김 (쏘기 전 자세)
# 스킬 샘플 (따로 받은 장, 흰 배경): archer_edit_2_arrow_rain_src.png (142×124) · archer_edit_3_evasive_src.png (146×116)
#   첫 장보다 작게 그려져 있어 대기 칸 머리 크기에 맞춘 배율을 곱함 (head_scale: 대기 칸 머리를 기울이고 키우며 찾아 맞춤). 회피기동 오른쪽 끝의 날아가는 화살은 몸과 떨어져 있어 지워짐
# 크기: 대기 키(포니테일 꼭대기~발)를 IDLE_H로. 한 장에 같은 크기로 그려져 있어서 모든 칸이 같은 배율
#   (얼굴 크기로 칸마다 맞추는 마법사 방식은 금발·살색이 섞여 얼굴을 잘못 잡아 칸마다 10% 넘게 들쭉날쭉해짐)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
from mage0_build import defringe, pack

D = 'assets/sprites/merc/samples/archer_edit_'
SRC = '1_src'
OUT = 'assets/sprites/merc/archer_0.webp'
IDLE_H = 100
# 갇힌 흰 배경 (자동으로 못 잡는 작은 틈, 샘플 좌표 x0, y0, x1, y1): 피격 시위·몸 사이 · 뒤로 비틀 활·팔 사이
GAP = [(219, 560, 228, 578), (372, 687, 377, 693)]
# (칸 이름, 상자 (x0, y0, x1, y1), 몸 덩어리만 남길지[, 샘플, 첫 장 대비 배율, 발밑 띄우기 px])
FRAMES = [
    ('idle', (130, 0, 290, 165), True),
    ('walk0', (150, 160, 315, 320), True),
    ('walk1', (385, 160, 540, 320), True),
    ('walk2', (600, 160, 760, 320), True),
    ('walk3', (825, 160, 980, 320), True),
    ('atk0', (140, 318, 305, 478), True),
    ('atk1', (430, 318, 605, 478), True),
    ('hurt', (132, 478, 270, 626), True),
    ('down0', (270, 608, 420, 765), True),
    ('down1', (448, 680, 790, 765), False),   # 누운 몸 + 떨어진 활
    ('rain', None, True, '2_arrow_rain_src', 'head', 0),
    ('evade', None, True, '3_evasive_src', 'head', 8),
]


IDLE_HEAD = (172, 11, 228, 69)   # 대기 칸 머리 (머리띠·얼굴·앞머리, 첫 장 좌표). 다른 장의 크기를 이것으로 맞춤


def head_scale(im):
    # im(RGB 배열)에서 대기 칸 머리와 가장 닮은 곳의 크기 비율 (대기 머리 = 1). 고개를 든 칸(화살비)이 있어 ±30° 기울여 봄
    import cv2
    S1 = np.array(Image.open(f'{D}{SRC}.png').convert('RGB')).astype(np.float32)
    x0, y0, x1, y1 = IDLE_HEAD; T0 = S1[y0:y1, x0:x1]
    im = im.astype(np.float32); best = (-1, 1)
    for ang in range(-30, 31, 5):
        M = cv2.getRotationMatrix2D((T0.shape[1] / 2, T0.shape[0] / 2), ang, 1)
        R = cv2.warpAffine(T0, M, (T0.shape[1], T0.shape[0]), borderValue=(255, 255, 255))[8:-8, 8:-8]
        for sc in np.arange(0.6, 1.3, 0.005):
            t = cv2.resize(R, (round(R.shape[1] * sc), round(R.shape[0] * sc)), interpolation=cv2.INTER_AREA)
            if t.shape[0] > im.shape[0] or t.shape[1] > im.shape[1]: continue
            v = cv2.minMaxLoc(cv2.matchTemplate(im, t, cv2.TM_CCOEFF_NORMED))[1]
            if v > best[0]: best = (v, sc)
    # 기울이지 않은 대기 머리 자신의 값 (가장자리를 잘라서 1이 아님)으로 나눔
    return best[1] / SELF_HEAD


SELF_HEAD = 1.0


def load(box, one_blob, src=SRC):
    im = np.array(Image.open(f'{D}{src}.png').convert('RGB')).astype(float)
    gap = np.zeros(im.shape[:2], bool)
    if src == SRC:
        for gx0, gy0, gx1, gy1 in GAP: gap[gy0:gy1, gx0:gx1] = True
    x0, y0, x1, y1 = box or (0, 0, im.shape[1], im.shape[0]); im = im[y0:y1, x0:x1]; gap = np.pad(gap[y0:y1, x0:x1], 2)
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), constant_values=255)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0]) | (white & gap)
    ids = np.arange(1, n + 1)   # 갇힌 흰 배경 (활과 몸 사이·팔 사이): 아주 하얗고 30px 이상
    pure = (ndi.sum(white, lab, ids) >= 30) & (ndi.mean(im.min(axis=2), lab, ids) > 246)
    bg |= np.isin(lab, ids[pure])
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    m = a > 0.3
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=3))
    sz = ndi.sum(m, lab, range(1, n + 1))
    if one_blob:   # 몸 덩어리만 (이웃 칸 조각·글씨는 지움)
        keep = lab == int(np.argmax(sz)) + 1
    else:          # 큰 덩어리 모두 (누운 몸 + 활), 티끌은 지움
        keep = np.isin(lab, 1 + np.where(sz >= 200)[0])
    a = np.where(keep, a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    body = rgba[..., 3] > 128
    foot = np.where(body[int(body.shape[0] * 0.94):].any(axis=0))[0].mean()
    return rgba, foot


def main():
    idle, _ = load(FRAMES[0][1], True)
    k = IDLE_H / idle.shape[0]
    pieces = []
    for name, box, one, *extra in FRAMES:
        src, rel, lift = extra or (SRC, 1, 0)
        rgba, foot = load(box, one, src)
        if rel == 'head':
            hs = head_scale(np.array(Image.open(f'{D}{src}.png').convert('RGB')))
            rel = 1 / hs
            print(f'  {name}: 머리 크기 대기 칸의 {hs:.3f}배 → ×{rel:.3f}')
        kk = k * rel
        if name == 'down1': foot = 120   # 누운 칸: 엉덩이쯤(샘플 x)을 기준점으로, 활은 앞쪽에 떨어져 있음
        if name == 'evade': foot = rgba.shape[1] * 0.42   # 공중 자세: 몸 가운데쯤 (뒷발 끝이 아니라)
        p = defringe(shrink(rgba, kk))
        if lift: p = np.concatenate([p, np.zeros((lift, p.shape[1], 4), np.uint8)])   # 아래에 빈 줄 → 기준점보다 위에 뜸
        pieces.append((name, p, foot * kk))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{kk:.3f} → {p.shape[1]}x{p.shape[0]}, 발 {foot * kk:.1f}')
    pack(pieces, OUT, 'archer_0')



# 히든 스킬 [폭풍] 시전 그림 (기본 외형) → assets/sprites/fx/archer_storm_cast_0.webp (ARCHER_STORM_FX.base, 3칸)
#   흰 배경 샘플: archer_edit_4_storm_cast_src.png (371×223): 0 캐스팅 (x 0~172) · 1 쏘기 직전 (x 177~366, 아래 y 212부터는 다음 그림이라 버림)
#                 archer_edit_5_storm_after_src.png (198×204): 2 쏘고 난 뒤
#   검은 배경 샘플: archer_edit_6_storm_black_src.png (393×370): 같은 세 칸을 검은 배경에 다시 그린 것 (왼쪽 아래 효과 없는 그림은 안 씀)
#     흰 배경 장보다 약 0.9배 작고, 바람 줄기 모양·구체 속 색이 조금씩 다름 (같은 그림을 다시 뽑은 것)
# 배경 지우기 = 두 장 비교: 흰 배경 장을 검은 배경 장에 맞춰 줄이고 몸 색으로 위치를 맞춘 뒤(cv2.matchTemplate)
#   · 두 장이 맞는 곳: 흰 배경 − 검은 배경 = (1 − 알파) × 255 → 알파와 색을 정확히 구함 (몸은 알파 1)
#   · 두 장이 다른 곳 (다시 그리며 바뀐 바람 줄기 등): 검은 배경 장을 빛으로 보고 밝기를 알파로 (검은색 빼기)
#   크기는 몸 칸과 같은 배율(흰 배경 장이 첫 장과 같은 크기) → standH도 archer_0과 같은 96. 기준점 = 발밑 (마법진·구체는 발 아래로도 내려감)
STORM_OUT = 'assets/sprites/fx/archer_storm_cast_0.webp'
BLACK = '6_storm_black_src'
# (칸 이름, 흰 배경 샘플, 흰 상자, 검은 배경 상자)
STORM = [('cast', '4_storm_cast_src', (0, 0, 172, 212), (16, 0, 161, 203)),
         ('ready', '4_storm_cast_src', (177, 0, 366, 212), (197, 0, 369, 183)),
         ('after', '5_storm_after_src', (0, 0, 198, 204), (197, 189, 369, 358))]


def opaque_body(im):
    # 흰 배경 장의 몸 덩어리 (위치 맞추기에만 씀): 진한 윤곽(바람의 짙은 초록은 뺌)을 이어 속을 채움
    dark = (im.mean(axis=2) < 105) & ~(im[..., 1] > im[..., 0] + 40)
    body = ndi.binary_fill_holes(ndi.binary_closing(dark, iterations=2)) & ~((im.min(axis=2) > 228) & ~dark)
    lab, n = ndi.label(body)
    return np.isin(lab, 1 + np.where(ndi.sum(body, lab, range(1, n + 1)) >= 40)[0])


def load_pair(src, wbox, bbox):
    import cv2
    W = np.array(Image.open(f'{D}{src}.png').convert('RGB')).astype(np.float32)
    x0, y0, x1, y1 = wbox; W = W[y0:y1, x0:x1]
    B = np.array(Image.open(f'{D}{BLACK}.png').convert('RGB')).astype(np.float32)
    x0, y0, x1, y1 = bbox; B = np.pad(B[y0:y1, x0:x1], ((6, 6), (6, 6), (0, 0)))
    body = opaque_body(W)
    best = None
    for s in np.arange(0.84, 1.0, 0.005):
        size = (round(W.shape[1] * s), round(W.shape[0] * s))
        if size[0] > B.shape[1] or size[1] > B.shape[0]: continue
        t = cv2.resize(W, size, interpolation=cv2.INTER_AREA)
        m = cv2.resize(body.astype(np.float32), size, interpolation=cv2.INTER_AREA)
        m = cv2.erode((m > 0.99).astype(np.uint8), np.ones((3, 3))).astype(np.float32)
        r = cv2.matchTemplate(B, t, cv2.TM_SQDIFF, mask=np.dstack([m] * 3))
        v, _, loc, _ = cv2.minMaxLoc(r); v /= m.sum()
        if best is None or v < best[0]: best = (v, s, loc, t)
    _, s, (ox, oy), t = best
    Wb = np.full_like(B, 255); Wb[oy:oy + t.shape[0], ox:ox + t.shape[1]] = t   # 흰 배경 장을 검은 배경 장 좌표로 (바깥은 흰 배경)
    diff = Wb - B
    est = 1 - diff.mean(axis=2) / 255
    agree = (diff.std(axis=2) < 22) & (diff.min(axis=2) > -24)
    glow = B.max(axis=2) / 255                       # 검은 배경 장을 빛으로 볼 때의 알파
    a = np.where(agree, np.clip(est, 0, 1), glow)
    a = np.where(a < 0.05, 0, a)
    solid = ndi.binary_fill_holes(ndi.binary_opening(a > 0.93, iterations=1))
    lab, n = ndi.label(solid)
    sz = ndi.sum(solid, lab, range(1, n + 1))
    body = lab == int(np.argmax(sz)) + 1             # 발 위치용 몸 덩어리
    a = np.where(solid, 1.0, a)
    al = np.maximum(a, 1e-3)[..., None]
    rgb = (B / al).clip(0, 255)                      # 검은 배경 위 색 = 색 × 알파
    ys, xs = np.where(body)
    foot_y = ys.max()
    foot_x = xs[ys >= foot_y - max(3, int((ys.max() - ys.min()) * 0.06))].mean()
    hs = head_scale(W)
    print(f'  위치 맞춤 ×{s:.3f} ({ox}, {oy}), 두 장이 맞는 곳 {agree[a > 0].mean():.0%}, 흰 배경 장 머리 = 대기 칸의 {hs:.3f}배')
    return np.dstack([rgb, a * 255]), solid, foot_x, foot_y, s * hs


def shrink_soft(rgba, body, k):
    # 반투명을 살려서 줄임 (premultiplied). 몸 덩어리 안쪽은 불투명으로 다시 다짐
    h, w = rgba.shape[:2]; size = (max(1, round(w * k)), max(1, round(h * k)))
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    sm = np.array(Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize(size, Image.LANCZOS)).astype(float)
    bm = np.array(Image.fromarray((body * 255).astype(np.uint8)).resize(size, Image.BILINEAR)) > 128
    al = sm[..., 3:]
    sm[..., :3] = np.where(al > 0, sm[..., :3] * 255 / np.maximum(al, 1), 0)
    sm[..., 3] = np.where(bm & (sm[..., 3] > 60), 255, sm[..., 3])
    sm[..., 3] = np.where(sm[..., 3] < 8, 0, sm[..., 3])
    return sm.clip(0, 255).astype(np.uint8)


def build_storm(k):
    pieces = []
    for name, src, wbox, bbox in STORM:
        rgba, body, fx, fy, s = load_pair(src, wbox, bbox)
        kk = k / s                                    # s = 검은 배경 장 머리가 대기 칸 머리의 몇 배인지 (흰 배경 장과의 비 × 흰 배경 장 머리 크기)
        p = shrink_soft(rgba, body, kk)
        pieces.append((name, p, fx * kk, fy * kk))
        print(f'{name}: 검은 배경 {rgba.shape[1]}x{rgba.shape[0]} ×{kk:.3f} → {p.shape[1]}x{p.shape[0]}, 발 ({fx * kk:.1f}, {fy * kk:.1f})')
    L = max(int(np.ceil(fx)) for _, _, fx, _ in pieces) + 2
    R = max(int(np.ceil(p.shape[1] - fx)) for _, p, fx, _ in pieces) + 2
    U = max(int(np.ceil(fy)) for _, _, _, fy in pieces) + 2
    B = max(int(np.ceil(p.shape[0] - fy)) for _, p, _, fy in pieces) + 2
    cw, ch = L + R, U + B
    sheet = np.zeros((ch, cw * len(pieces), 4), np.uint8)
    for i, (name, p, fx, fy) in enumerate(pieces):
        x = i * cw + L - int(round(fx)); y = U - int(round(fy))
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(STORM_OUT, 'WEBP', lossless=True)
    print(f'archer_storm_cast_0 cellW={cw} cellH={ch} anchorX={L} anchorY={U} count={len(pieces)}')


if __name__ == '__main__':
    SELF_HEAD = 1.0
    x0, y0, x1, y1 = FRAMES[0][1]
    SELF_HEAD = head_scale(np.array(Image.open(f'{D}{SRC}.png').convert('RGB'))[y0:y1, x0:x1])
    print(f'대기 칸 머리 기준값 {SELF_HEAD:.3f}')
    idle, _ = load(FRAMES[0][1], True)
    main()
    build_storm(IDLE_H / idle.shape[0])

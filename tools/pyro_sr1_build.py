# 화염술사 시크릿 레어 1 (불사조: 불꽃 날개·불타는 깃털 몸·오른손 위 불길) 샘플 → assets/sprites/merc/pyro_sr1.webp
#   + 전용 메테오 이펙트 assets/sprites/fx/pyro_sr_meteor_fx.webp
# 사용: python tools/pyro_sr1_build.py
# 샘플 (흰 배경, assets/sprites/fx/samples/pyro_sr1_*):
#   idle_src.png (269×317): 대기 한 장뿐. 위쪽 "#08" 글씨는 지우고(CUT), 왼쪽 가장자리에 걸친 옆 그림 조각은 버림
#   meteor_fall_src.webp (1024×572): 연기 꼬리가 왼쪽 위로 길게 달린 불타는 운석 (날아오는 투사체)
#   meteor_hit_src.webp (1024×572): 착탄 순간 (운석이 땅에 박히며 불꽃이 튐) · meteor_boom_src.webp: 착탄 뒤 폭발
# 캐릭터 칸 순서 = 화염술사 0번과 같음: 0 대기 · 1~2 걷기 · 3 공격 준비 · 4 공격 발사 · 5 피격 · 6~7 쓰러짐 · 8 화염 시전 · 9 파이어볼 발사 · 10 화염 산탄 발사
#   대기 한 장만 받아서, 나머지 칸은 발 가운데를 축으로 기울이고(앞으로 숙임 · 뒤로 젖힘) 들썩임·밝기만 바꿔 만듦
# 크기: 머리 꼭대기~발(BODY_TOP~발)을 화염술사 0번 키(90)와 같게 → 날개는 그 위로 솟음
# 이펙트 시트 칸: fall (운석, 기준점 = 돌덩이 가운데) · hit (착탄, 기준점 = 바닥 가운데) · boom (폭발, 기준점 = 바닥 가운데)
#   꼬리가 그림 밖으로 잘린 왼쪽 위는 FADE 폭만큼 서서히 투명하게 (게임에서 잘린 끝이 보이지 않게)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/pyro_sr1_'
OUT = 'assets/sprites/merc/pyro_sr1.webp'
FX_OUT = 'assets/sprites/fx/pyro_sr_meteor_fx.webp'
CUT = [(122, 6, 170, 30)]   # "#08" 글씨
BODY_TOP = 98               # 샘플에서 머리(볏) 꼭대기 y — 이 높이~발을 TARGET_H로
TARGET_H = 90
FX_SCALE = 0.5              # 이펙트 시트 배율 (게임에서 반지름에 맞춰 다시 늘려 그림)
FALL_ANGLE = 36.5          # 샘플 운석이 내려오는 각도 (오른쪽 아래로 36.5°) — 게임도 이 각도로 떨어뜨림
FADE = 260                  # 이펙트 꼬리 끝 서서히 사라지는 폭 (샘플 px)

# (칸 이름, 기울기° (+ = 뒤로 젖힘), 위로 들썩 (샘플 px), 밝기, 붉은 기)
FRAMES = [
    ('idle', 0, 0, 1.0, 0), ('walk0', -2, 6, 1.0, 0), ('walk1', 2, 2, 1.0, 0),
    ('atk_ready', 5, 0, 1.06, 0), ('atk_fire', -7, 0, 1.08, 0),
    ('hurt', 12, 0, 1.0, 0.35), ('down0', 45, 0, 0.85, 0.15), ('down1', 88, 0, 0.7, 0),
    ('cast', 4, 4, 1.15, 0), ('fb', -10, 0, 1.12, 0), ('sc', -8, 0, 1.1, 0),
]


def white_bg(im, thr=222, tone=16):
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), constant_values=255)
    white = (im.min(axis=2) > thr) & (im.max(axis=2) - im.min(axis=2) < tone)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    return im[2:-2, 2:-2], a[2:-2, 2:-2]


def load_idle():
    im = np.array(Image.open(f'{D}idle_src.png').convert('RGB')).astype(float)
    for x0, y0, x1, y1 in CUT: im[y0:y1, x0:x1] = 255
    im, a = white_bg(im)
    m = a > 0.3
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    H, W = m.shape
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if xs.min() <= 1 or ys.min() <= 1 or xs.max() >= W - 2: a[lab == i] = 0   # 가장자리에 걸친 옆 그림 조각
    ys, xs = np.where(a > 0)
    y0 = ys.min()
    rgba = np.dstack([im, a * 255])[y0:ys.max() + 1, xs.min():xs.max() + 1]
    body = rgba[..., 3] > 200
    bot = np.where(body.any(axis=1))[0].max()
    foot = np.where(body[bot - 14:bot + 1].any(axis=0))[0].mean()   # 두 발 가운데
    return rgba, foot, bot, BODY_TOP - y0


def pose(rgba, foot, bot, ang, lift, bright, red):
    h, w = rgba.shape[:2]
    P = int(max(h, w) * 1.2)
    big = np.zeros((2 * P, 2 * P, 4))
    ox, oy = int(P - foot), int(P - bot)
    big[oy:oy + h, ox:ox + w] = rgba
    pm = big.copy(); pm[..., :3] *= pm[..., 3:] / 255
    img = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').rotate(ang, Image.BICUBIC, center=(P, P))
    r = np.array(img).astype(float)
    al = r[..., 3:]
    r[..., :3] = np.where(al > 0, r[..., :3] * 255 / np.maximum(al, 1), 0)
    r[..., :3] *= bright
    if red: r[..., :3] = r[..., :3] * (1 - red) + np.array([255, 70, 60]) * red
    r = np.clip(r, 0, 255)
    ys, xs = np.where(r[..., 3] > 8)
    x0, y0 = xs.min(), ys.min()
    crop = r[y0:max(ys.max() + 1, P + 1), x0:xs.max() + 1]
    if ang >= 30: return crop, P - x0, crop.shape[0]   # 쓰러짐: 가장 아래 닿는 곳을 바닥에
    return crop, P - x0, (P - y0) + lift   # 발 기준점 (칸 안 x, 바닥 y)


def build_char():
    rgba, foot, bot, top = load_idle()
    sc = TARGET_H / (bot - top)
    pieces = []
    for name, ang, lift, br, red in FRAMES:
        p, fx, fy = pose(rgba, foot, bot, ang, lift, br, red)
        s = shrink(p, sc)
        pieces.append((name, s, fx * sc, fy * sc))
    L = max(int(np.ceil(c)) for _, _, c, _ in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c, _ in pieces) + 3
    U = max(int(np.ceil(fy)) for _, _, _, fy in pieces) + 3
    Dn = max(int(np.ceil(p.shape[0] - fy)) for _, p, _, fy in pieces) + 2
    cw, ch = L + R, U + Dn
    sheet = np.zeros((ch, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c, fy) in enumerate(pieces):
        x = i * cw + L - int(round(c)); y = U - int(round(fy))
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    idle = pieces[0][1]
    print(f'배율 {sc:.3f}  pyro_sr1 cellW={cw} cellH={ch} anchorX={L} anchorY={U} count={len(pieces)}  대기 그림 키 {int(round(pieces[0][3]))}')
    # 손 위 불길 자리 (대기 칸, 발 기준): 몸 오른쪽 가장 밝은 노란 덩어리
    sm = shrink(rgba, sc).astype(int)
    hx = foot * sc
    yy, xx = np.where((sm[..., 3] > 0) & (sm[..., 0] > 235) & (sm[..., 1] > 200) & (np.arange(sm.shape[1])[None] > hx + 15))
    if len(xx): print(f'손 불길 = [{xx.mean() - hx:.0f}, {yy.mean() - sm.shape[0]:.0f}]')


def fx_piece(name, anchor):
    im = np.array(Image.open(f'{D}meteor_{name}_src.webp').convert('RGB')).astype(float)
    im, a = white_bg(im, thr=226, tone=22)
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W]
    # 왼쪽 위 꼬리 끝: 그림 왼쪽·위 가장자리에서 FADE 안쪽은 서서히 투명
    d = np.minimum(xx, yy * 1.6)
    a = a * np.clip(d / FADE, 0, 1) ** 1.3
    ys, xs = np.where(a > 0.02)
    x0, y0 = xs.min(), ys.min()
    rgba = np.dstack([im, a * 255])[y0:ys.max() + 1, x0:xs.max() + 1]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    img = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA')
    if name == 'fall':   # 투사체는 게임이 날아가는 각도로 돌려 그림 → 오른쪽(0°)을 향하게 미리 돌려 둠
        img = img.rotate(FALL_ANGLE, Image.BICUBIC, expand=True)
        img = img.crop(img.getbbox())
    pm = np.array(img).astype(float)
    al = pm[..., 3:]
    rgba = pm.copy(); rgba[..., :3] = np.where(al > 0, pm[..., :3] * 255 / np.maximum(al, 1), 0)
    ax, ay = anchor(rgba, rgba[..., 3] / 255)
    h, w = rgba.shape[:2]
    sm = img.resize((round(w * FX_SCALE), round(h * FX_SCALE)), Image.LANCZOS)
    r = np.array(sm).astype(float); al = r[..., 3:]
    r[..., :3] = np.where(al > 0, r[..., :3] * 255 / np.maximum(al, 1), 0)
    return r.clip(0, 255).astype(np.uint8), ax * FX_SCALE, ay * FX_SCALE


def rock_center(rgba, a):
    # 운석 돌덩이 = 오른쪽 아래의 어두운 덩어리
    dark = (a > 0.9) & (rgba[..., :3].max(axis=2) < 70)
    h, w = dark.shape
    dark[:, :int(w * 0.6)] = False
    ys, xs = np.where(dark)
    return xs.mean(), ys.mean()


def ground_center(rgba, a):
    # 바닥 = 맨 아래 줄 근처 그림의 가운데 · 기준점 y는 바닥 흙더미 가운데 높이
    h, w = a.shape
    ys = np.where((a > 0.5).any(axis=1))[0]
    bot = ys.max()
    xs = np.where((a[bot - 30:bot + 1] > 0.5).any(axis=0))[0]
    return (xs.min() + xs.max()) / 2, bot - 22


def build_fx():
    parts = [('fall',) + fx_piece('fall', rock_center), ('hit',) + fx_piece('hit', ground_center), ('boom',) + fx_piece('boom', ground_center)]
    W = sum(p.shape[1] for _, p, _, _ in parts) + 2 * (len(parts) - 1)
    H = max(p.shape[0] for _, p, _, _ in parts)
    sheet = np.zeros((H, W, 4), np.uint8)
    x = 0
    for name, p, ax, ay in parts:
        sheet[:p.shape[0], x:x + p.shape[1]] = p
        print(f"{name}: [[{x},0,{p.shape[1]},{p.shape[0]},{ax:.1f},{ay:.1f}]]")
        x += p.shape[1] + 2
    Image.fromarray(sheet, 'RGBA').save(FX_OUT, 'WEBP', quality=88)


if __name__ == '__main__':
    build_char()
    build_fx()

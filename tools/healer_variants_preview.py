# 성녀 새 기본 외형(healer_0, 2026-11-09 은발 성녀) 외형 1~5 후보 미리보기 — 피부·눈은 그대로, 나머지 채도·명도만 바꿈
# 사용: python tools/healer_variants_preview.py masks <경로>    → 그대로 둘 곳 (빨강: 피부, 파랑: 눈) 확인
#       python tools/healer_variants_preview.py preview <경로>  → 후보마다 대기 칸 크게 + 여러 칸 줄
# 색상(hue)은 그대로. 흰 수도복·베일·은발(무채색)과 금빛 장식·갈색 소매(유채색)를 따로 조절해서 더 다양하게:
#   무채색 채도를 올리면 은발·수도복 음영에 숨은 푸른 기운이 살아나 라벤더·푸른 은빛이 되고, 명도를 내리면 회색·검은 수도복
# 눈(흰자·눈동자·속눈썹) = 칸마다 얼굴(가장 큰 살색 덩어리)을 닫아 채웠을 때 안에 갇힌 살색 아닌 곳
# 13~16 (스킬별 색 이펙트 칸)은 미리보기에 안 넣음
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, 'tools')
import archer_variants_preview as A
from frost_variants_build import rgb2hsv, hsv2rgb

SRC = 'assets/sprites/merc/healer_0.webp'
CW = 170
SHOW = [0, 1, 4, 5, 7, 8, 11]   # 대기·걷기·공격·피격·쓰러짐·스킬 준비·발동
# (이름, (무채색 채도, 명도), (유채색 채도, 명도))
VARIANTS = [
    ('원본', (1, 1), (1, 1)),
    ('A 라벤더', (4, 0.98), (0.8, 1.05)),
    ('B 은장 성녀', (0.3, 1.0), (0.05, 1.12)),
    ('C 흑의 금장', (1, 0.32), (1.25, 1.05)),
    ('D 먹빛 은장', (0.4, 0.38), (0.05, 1.2)),
    ('E 회색 수녀', (1, 0.66), (0.45, 0.8)),
    ('F 황혼 남빛', (4, 0.78), (1.3, 0.85)),
    ('G 잿빛 금장', (0.2, 0.52), (1.4, 1.0)),
    ('H 바랜 청보라', (6, 0.9), (0.5, 0.8)),
    ('I 짙은 청회', (3, 0.5), (1.0, 0.62)),
    ('J 푸른 은빛', (6, 1.0), (0.15, 1.0)),
    ('K 백금 선명', (1, 1.04), (1.7, 1.1)),
    ('L 그림자', (1, 0.27), (0.4, 0.5)),
]


def skin_mask(im):
    hsv = rgb2hsv(im[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    al = im[..., 3] > 200
    core = al & (h >= 8) & (h <= 34) & (s >= 0.12) & (s <= 0.45) & (v > 0.78)
    lab, n = ndimage.label(core)
    sizes = ndimage.sum(core, lab, range(1, n + 1))
    keep = np.isin(lab, np.where(sizes >= 3)[0] + 1)
    broad = al & ((h <= 36) | (h >= 345)) & (s >= 0.12) & (s <= 0.55) & (v > 0.55)
    # 수도복 단의 따뜻한 음영까지 번지지 않게 핵심 살색에서 4px 안만
    return ndimage.binary_propagation(keep, mask=(broad & ndimage.binary_dilation(keep, iterations=4)) | keep)


def eye_mask(im, skin):
    out = np.zeros_like(skin)
    for i in range(im.shape[1] // CW):
        sl = (slice(None), slice(i * CW, (i + 1) * CW))
        lab, n = ndimage.label(skin[sl])
        if not n: continue
        face = lab == np.argmax(ndimage.sum(skin[sl], lab, range(1, n + 1))) + 1
        shut = ndimage.binary_fill_holes(ndimage.binary_closing(np.pad(face, 4), iterations=3))[4:-4, 4:-4]
        out[sl] = shut & ~face & (im[sl][..., 3] > 0)
    return out


def keep_mask(im):
    sk = skin_mask(im)
    return sk | eye_mask(im, sk)


def tone(im, keep, neu, col):
    hsv = rgb2hsv(im[..., :3] / 255.)
    m = (im[..., 3] > 0) & ~keep
    s0, v0 = hsv[..., 1].copy(), hsv[..., 2].copy()
    w = np.clip((s0 - 0.15) / 0.15, 0, 1)   # 0 = 무채색(흰 옷·은발), 1 = 유채색(금빛·갈색)
    # 무채색 채도를 크게 올릴 때 따뜻한 색조(빨강~주황) 음영은 빨간 점처럼 튀어서 1.5배까지만 (눈가 머리카락·수도복 단)
    hh = hsv[..., 0] * 360
    warm = (hh < 50) | (hh > 320)
    sn = np.where(warm, np.minimum(neu[0], 1.5), neu[0])
    sat = sn * (1 - w) + col[0] * w
    val = neu[1] * (1 - w) + col[1] * w
    hsv[..., 1] = np.where(m, np.clip(s0 * sat, 0, 1), s0)
    # 어둡게 할 때 밝은 금빛은 조금 덜 어둡게 (노랑이 어두워지면 탁한 올리브가 됨)
    glow = np.clip((v0 - 0.75) / 0.2, 0, 1) * np.clip((s0 - 0.3) / 0.3, 0, 1)
    k = np.where(val < 1, val + (1 - val) * glow * 0.5, val)
    hsv[..., 2] = np.where(m, np.clip(v0 * k, 0, 1), v0)
    out = im.copy()
    out[m, :3] = (hsv2rgb(hsv)[m] * 255 + .5).clip(0, 255).astype(np.uint8)
    return out


def masks(path):
    im = np.array(Image.open(SRC).convert('RGBA'))
    sk = skin_mask(im); ey = eye_mask(im, sk)
    vis = im.copy(); vis[sk] = [255, 0, 0, 255]; vis[ey] = [0, 120, 255, 255]
    cells = [A.on_bg(np.hstack([im[:, i * CW:(i + 1) * CW], vis[:, i * CW:(i + 1) * CW]])) for i in SHOW]
    out = Image.new('RGB', (cells[0].width * 2, cells[0].height * ((len(cells) + 1) // 2)))
    for i, c in enumerate(cells): out.paste(c, ((i % 2) * c.width, (i // 2) * c.height))
    out.resize((out.width * 2, out.height * 2), Image.NEAREST).save(path)


def preview(path):
    A.CW = CW
    im = np.array(Image.open(SRC).convert('RGBA'))
    kp = keep_mask(im)
    H = im.shape[0]; big = 2
    rows = []
    for name, neu, col in VARIANTS:
        rc = tone(im, kp, neu, col)
        c0 = A.crop_cell(rc, 0)
        idle = A.on_bg(c0).resize((c0.shape[1] * big, H * big), Image.NEAREST)
        strip = [A.on_bg(A.crop_cell(rc, i)) for i in SHOW[1:]]
        row = Image.new('RGB', (idle.width + 30 + sum(s.width + 6 for s in strip), H * big + 30), (36, 40, 48))
        d = ImageDraw.Draw(row)
        d.text((10, 4), f'{name}   옷·머리 채도 ×{neu[0]} 명도 ×{neu[1]} · 금빛 채도 ×{col[0]} 명도 ×{col[1]}', fill=(240, 240, 240), font=A.font(18))
        row.paste(idle, (10, 28))
        x = idle.width + 24
        for s_ in strip:
            row.paste(s_, (x, 28 + H * big - H)); x += s_.width + 6
        rows.append(row)
    # 두 줄로 나란히
    half = (len(rows) + 1) // 2
    W = max(r.width for r in rows); Hh = max(r.height for r in rows)
    out = Image.new('RGB', (W * 2 + 10, Hh * half), (36, 40, 48))
    for i, r in enumerate(rows): out.paste(r, ((i // half) * (W + 10), (i % half) * Hh))
    out.save(path)
    print(path, out.size)


if __name__ == '__main__':
    mode, p = sys.argv[1], sys.argv[2]
    {'masks': masks, 'preview': preview}[mode](p)

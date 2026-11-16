# 기공사 새 그림 샘플 다듬기 (사용자 샘플, 흰 배경) → 미리보기 _preview_qigong_sheet*.png
# 사용: python tools/qigong_sample_build.py
# 샘플: assets/sprites/fx/samples/qigong_*_src.png (2026-11-16 사용자가 준 그림)
#   idle 대기 · walk 걷기 4칸(한 장) · atk 일반 공격 2칸(한 장, 왼쪽 = 기 모으기) · atk2 일반 공격 내지르기(교체본)
#   hurtdown 피격 1칸 + 쓰러짐 2칸 (한 장, 왼쪽에 설명 글자) · hu1·hu2 기공후 · pa1·pa2 기공파 · tan 기공탄 2칸(위아래)
#   po1·po2 기공포 · 기공막 = po1 + hu2 다시 씀 · ok1~ok5 히든 기공옥 (모으기 → 떠오르며 모으기 → 최대 크기 → 시전 → 착지)
# 고르기 (사용자 규칙: 샘플은 필요한 칸만):
#   - 일반 공격 샘플의 오른쪽 내지르기는 atk2로 교체돼 안 씀
#   - 기공옥 ok2(떠오르며 모으기)는 ok3과 자세가 거의 같아 뺌. 떠오르는 높이는 게임에서 위치로 올림
# 맞추기 (대기 칸 기준):
#   - 흰 배경: brawler_sr1_build.cut (가장자리 흰색 + 갇힌 흰 구멍 + 테두리 찌꺼기) → 가장 큰 덩어리만 (대기의 금빛 가루도 빠짐)
#   - 크기·비율: 얼굴 살색 덩어리 넓이의 제곱근이 대기와 같아지게 배율을 정함 (그림마다 원본 크기가 제각각이라)
#   - 피부색·밝기: 얼굴 살색 평균이 대기와 같아지게 칸 전체 색에 채널별 배율을 곱함 (외곽선 검정은 그대로)
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from brawler_sr1_build import cut, shrink

D = 'assets/sprites/fx/samples/qigong_'
TARGET_H = 86   # 대기 자세 키 (다른 직업 칸과 같은 게임 px)
# 몸 길이 (턱 → 발, 게임 px) 맞추기: 샘플마다 머리 대비 몸 길이가 달라 (대기 57 · 걷기 46~48 · 기 모으기 45 · 기공옥 최대 크기 68)
#   머리 크기를 맞춘 뒤 몸만 늘이거나 줄여 대기 비율로. 무릎을 굽힌 걷기·공격 자세는 대기보다 조금 짧게, 공중에 떠서 발끝을 편 자세는 조금 길게
BODY = {('걷기', 0): 54, ('걷기', 1): 54, ('걷기', 2): 54, ('걷기', 3): 54, ('일반 공격', 0): 53, ('기공옥', 1): 60}
SAME = {('쓰러짐', 1): ('쓰러짐', 0)}   # 얼굴이 가려 못 재는 칸 → 같은 원본 장의 다른 칸 배율을 씀


def figs(name, n, axis=1):   # 한 장에 여러 칸 → 칸마다 다른 그림을 흰색으로 덮은 사본 (왼쪽→오른쪽, axis=0이면 위→아래)
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB'))
    fg = im.astype(int).min(axis=2) < 225
    lab, k = ndi.label(ndi.binary_dilation(fg, iterations=4))
    sz = ndi.sum(fg, lab, range(1, k + 1))
    big = sorted(np.argsort(-sz)[:n] + 1, key=lambda i: np.where(lab == i)[1 - axis].mean())
    out = []
    for i in big:
        o = im.copy(); o[lab != i] = 255
        out.append(o)
    return out


def one(name):
    return np.array(Image.open(f'{D}{name}_src.png').convert('RGB'))


def despeck(im, area=120):   # 몸에서 떨어진 작은 점(금빛 가루·티끌)을 흰색으로 덮음
    fg = im.astype(int).min(axis=2) < 225
    lab, n = ndi.label(fg, structure=np.ones((3, 3)))
    sz = ndi.sum(fg, lab, range(1, n + 1))
    o = im.copy(); o[np.isin(lab, 1 + np.where(sz < area)[0])] = 255
    return o


def skin_mask(rgba):
    c = rgba[..., :3].astype(int); r, g, b = c[..., 0], c[..., 1], c[..., 2]
    return (rgba[..., 3] > 0) & (r > 215) & (g > 160) & (g < 225) & (b > 125) & (b < 200) & (r - g > 28) & (r - g < 75) & (g - b > 15) & (g - b < 55)


def face(rgba):   # 그림 위쪽 60% 안의 가장 큰 살색 덩어리 = 얼굴 → (넓이, 평균색, 턱 y)
    m = skin_mask(rgba); m[int(rgba.shape[0] * .6):] = False
    lab, n = ndi.label(ndi.binary_closing(m, iterations=2) & m)
    if n == 0: return None
    sz = ndi.sum(m, lab, range(1, n + 1))
    f = lab == 1 + int(np.argmax(sz))
    return f.sum(), rgba[..., :3][f].astype(float).mean(axis=0), int(np.where(f)[0].max())


def stretch_body(fig, chin, factor):   # 턱 아래 몸만 위아래로 늘이거나 줄임 (머리 크기는 그대로). 원본 해상도에서 해서 축소 때 고르게 섞임
    top, bot = fig[:chin + 1], fig[chin + 1:]
    h = max(1, round(bot.shape[0] * factor))
    bot = np.array(Image.fromarray(bot.astype(np.uint8), 'RGBA').resize((bot.shape[1], h), Image.NEAREST))
    return np.concatenate([top.astype(np.uint8), bot], axis=0)


# (칸 이름, 원본 그림, 묶음 이름)
def frames():
    walk = figs('walk', 4); atk = figs('atk', 2); hd = figs('hurtdown', 3); tan = figs('tan', 2, axis=0)
    hdp = sorted(hd, key=lambda o: np.where(o.min(axis=2) < 225)[0].mean())   # 위 = 피격, 아래 두 칸 = 쓰러짐
    down = sorted(hdp[1:], key=lambda o: np.where(o.min(axis=2) < 225)[1].mean())
    return [
        ('대기', [one('idle')]),
        ('걷기', walk),
        ('일반 공격', [atk[0], one('atk2')]),
        ('피격', [hdp[0]]),
        ('쓰러짐', down),   # 누운 칸은 얼굴이 가려져 피격·쓰러짐 1과 같은 배율 (SAME)
        ('기공포', [one('po1'), one('po2')]),
        ('기공탄', tan),
        ('기공막', [one('po1'), one('hu2')]),
        ('기공후', [one('hu1'), one('hu2')]),
        ('기공파', [one('pa1'), one('pa2')]),
        ('기공옥', [one('ok1'), one('ok3'), one('ok4'), one('ok5')]),
    ]


def build():
    rows = []
    idle = cut(despeck(one('idle')))
    fa0, fc0, _ = face(idle)
    sc0 = TARGET_H / idle.shape[0]
    done = {}
    for label, ims in frames():
        cells = []
        for j, im in enumerate(ims):
            fig = cut(despeck(im))
            f = face(fig)
            if (label, j) in SAME:
                k, gain = done[SAME[(label, j)]]
            elif f is None:
                k, gain = 1.0, np.ones(3)
            else:
                k = np.sqrt(fa0 / f[0])
                gain = np.clip(fc0 / f[1], 0.8, 1.25)
            done[(label, j)] = (k, gain)
            if (label, j) in BODY:
                body = (fig.shape[0] - 1 - f[2]) * sc0 * k
                fig = stretch_body(fig, f[2], BODY[(label, j)] / body)
            fig = fig.astype(float)
            fig[..., :3] = (fig[..., :3] * gain).clip(0, 255)
            cells.append((shrink(fig.astype(np.uint8), sc0 * k), k, gain))
        rows.append((label, cells))
    return rows


def sheet(rows, bg, zoom=3, out='_preview_qigong_sheet.png'):
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 16 * zoom // 2)
    cw, chh, lw, pad = 110, 118, 70, 6
    W = lw + cw * max(len(c) for _, c in rows)
    H = chh * len(rows)
    canvas = Image.new('RGBA', (W, H), bg)
    for r, (label, cells) in enumerate(rows):
        y0 = r * chh
        for j, (c, _, _) in enumerate(cells):
            im = Image.fromarray(c, 'RGBA')
            x = lw + j * cw + (cw - im.width) // 2
            canvas.alpha_composite(im, (max(lw + j * cw, x), y0 + chh - pad - im.height))
    big = canvas.resize((W * zoom, H * zoom), Image.NEAREST)
    d = ImageDraw.Draw(big)
    fg = (40, 40, 40, 255) if sum(bg[:3]) > 380 else (230, 230, 230, 255)
    for r, (label, _) in enumerate(rows):
        d.text((8 * zoom, (r * chh + chh // 2) * zoom), label, font=font, fill=fg, anchor='lm')
        d.line([(0, (r + 1) * chh * zoom - 1), (W * zoom, (r + 1) * chh * zoom - 1)], fill=fg[:3] + (40,))
    big.save(out)
    return out


if __name__ == '__main__':
    rows = build()
    for label, cells in rows:
        print(label, [f'{c.shape[1]}x{c.shape[0]} k{k:.2f} g{tuple(np.round(g, 2))}' for c, k, g in cells])
    print(sheet(rows, (255, 255, 255, 255)))
    print(sheet(rows, (46, 50, 58, 255), out='_preview_qigong_sheet_dark.png'))

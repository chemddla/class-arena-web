# 무녀 시크릿 레어 1 샘플 다듬기 (사용자 샘플, 흰 배경) → 미리보기 _preview_miko_sr1*.png
# 사용: python tools/miko_sr1_sample_build.py
# 샘플: assets/sprites/fx/samples/miko_sr1_idle_src.png (2026-11-17 사용자가 준 대기 그림 한 장:
#   남색 철릭·붉은 치마·오색 띠·양손 부채, 땋은 머리)
#   miko_sr1_walk_src.png 걷기 4칸 한 장 (게임 걷기도 4칸이라 4장 다 씀). 4번째 칸 치마 위의 반짝이 워터마크는
#   원본에서 세로(주름 방향)로 위아래 치마 색을 이어 메꿔 둠
# 자르기·줄이기는 기본 무녀(miko_sample_build)와 같은 방식
# 크기: 얼굴 넓이로 맞추면 기본(2.5등신)과 등신이 달라 키 126이 되므로 키로 맞춤 — 어른 비율이라 기본 86보다 조금 큰 96
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
import miko_sample_build as base
from brawler_sr1_build import shrink

SRC = 'assets/sprites/fx/samples/miko_sr1_idle_src.png'
SR_H = 96


def clear_back(fig):   # 땋은 머리와 등·리본 사이에 갇힌 흰 배경: 이 그림의 흰색은 목 깃(가운데)·버선(아래)뿐이라
    # 그림 왼쪽 40%·위쪽 60% 안에 가운데가 있는 흰 덩어리는 배경으로 보고 지운 뒤, 둘레의 밝은 회색(배경과 외곽선이 섞인 색)도 2겹 벗김
    fig = fig.copy(); H, W = fig.shape[:2]
    c = fig[..., :3]; mn, ch = c.min(axis=2), c.max(axis=2) - c.min(axis=2)
    a = fig[..., 3] > 0
    lab, n = ndi.label(a & (mn > 200) & (ch < 25))
    gone = np.zeros_like(a)
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if xs.mean() < W * .4 and ys.mean() < H * .6: gone |= lab == i
    rim = (mn > 110) & (ch < 14) & a
    for _ in range(2):
        gone |= ndi.binary_dilation(gone) & rim
    fig[..., 3][gone] = 0
    return fig


def build():
    idle0 = base.clear_holes(base.cut(base.despeck(base.one('idle'))), ('대기', 0))
    fa0 = base.face(idle0)[0]
    sc0 = base.TARGET_H / idle0.shape[0]
    im = np.array(Image.open(SRC).convert('RGB'))
    fig = clear_back(base.cut(base.despeck(im)))
    f = base.face(fig)
    k = SR_H / fig.shape[0]
    print('sr1 face', f[0], 'base face', fa0, 'scale', round(k, 3), '(얼굴로 맞추면', round(sc0 * np.sqrt(fa0 / f[0]), 3), ')')
    # 걷기: 시크릿 레어 대기 칸과 얼굴 넓이를 맞춤. 한 장에 같은 크기로 그린 4칸이라 배율은 평균 하나로 (칸마다 다르면 걸을 때 몸이 커졌다 작아짐)
    wfs = [clear_back(base.cut(base.despeck(w))) for w in base.blobs('sr1_walk', 4)]
    kw = float(np.mean([k * np.sqrt(f[0] / base.face(wf)[0]) for wf in wfs]))
    print('walk scale', round(kw, 3), '→ 키', [round(wf.shape[0] * kw) for wf in wfs])
    walks = [shrink(wf.astype(np.uint8), kw) for wf in wfs]
    return shrink(idle0.astype(np.uint8), sc0), shrink(fig.astype(np.uint8), k), walks


def preview(cells, bg, out, zoom=4, names=None):
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 9 * zoom // 2)
    cw, chh = 120, 130
    canvas = Image.new('RGBA', (cw * len(cells), chh), bg)
    for j, c in enumerate(cells):
        im = Image.fromarray(c, 'RGBA')
        canvas.alpha_composite(im, (j * cw + (cw - im.width) // 2, chh - 18 - im.height))
    big = canvas.resize((canvas.width * zoom, chh * zoom), Image.NEAREST)
    d = ImageDraw.Draw(big)
    fg = (40, 40, 40, 255) if sum(bg[:3]) > 380 else (230, 230, 230, 255)
    for j, t in enumerate(names or ['기본 무녀 대기', '시크릿 레어 1 대기']):
        d.text(((j * cw + cw // 2) * zoom, (chh - 8) * zoom), t, font=font, fill=fg, anchor='mm')
    big.save(out)
    return out


if __name__ == '__main__':
    b, s, walks = build()
    print('sr1 cell', s.shape[1], 'x', s.shape[0], '/ base', b.shape[1], 'x', b.shape[0])
    names = ['기본 무녀 대기', 'SR1 대기'] + [f'SR1 걷기 {j + 1}' for j in range(len(walks))]
    print(preview([b, s] + walks, (255, 255, 255, 255), '_preview_miko_sr1.png', names=names))
    print(preview([b, s] + walks, (46, 50, 58, 255), '_preview_miko_sr1_dark.png', names=names))
    # 걷기 움직임 확인용 (게임 걷기 한 바퀴 0.56초 = 칸당 0.14초)
    fr = []
    for w in walks:
        c = Image.new('RGBA', (90, 110), (46, 50, 58, 255)); im = Image.fromarray(w, 'RGBA')
        c.alpha_composite(im, ((90 - im.width) // 2, 104 - im.height)); fr.append(c.resize((270, 330), Image.NEAREST))
    fr[0].save('_preview_miko_sr1_walk.gif', save_all=True, append_images=fr[1:], duration=140, loop=0)
    print('_preview_miko_sr1_walk.gif')

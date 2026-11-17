# 무녀 시크릿 레어 1 샘플 다듬기 (사용자 샘플, 흰 배경) → 미리보기 _preview_miko_sr1*.png
# 사용: python tools/miko_sr1_sample_build.py
# 샘플: assets/sprites/fx/samples/miko_sr1_idle_src.png (2026-11-17 사용자가 준 대기 그림 한 장:
#   남색 철릭·붉은 치마·오색 띠·양손 부채, 땋은 머리)
# 자르기·줄이기는 기본 무녀(miko_sample_build)와 같은 방식
# 크기: 얼굴 넓이로 맞추면 기본(2.5등신)과 등신이 달라 키 126이 되므로 키로 맞춤 — 어른 비율이라 기본 86보다 조금 큰 96
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import miko_sample_build as base
from brawler_sr1_build import shrink

SRC = 'assets/sprites/fx/samples/miko_sr1_idle_src.png'
SR_H = 96


def build():
    idle0 = base.clear_holes(base.cut(base.despeck(base.one('idle'))), ('대기', 0))
    fa0 = base.face(idle0)[0]
    sc0 = base.TARGET_H / idle0.shape[0]
    im = np.array(Image.open(SRC).convert('RGB'))
    fig = base.cut(base.despeck(im))
    f = base.face(fig)
    k = SR_H / fig.shape[0]
    print('sr1 face', f[0], 'base face', fa0, 'scale', round(k, 3), '(얼굴로 맞추면', round(sc0 * np.sqrt(fa0 / f[0]), 3), ')')
    return shrink(idle0.astype(np.uint8), sc0), shrink(fig.astype(np.uint8), k)


def preview(cells, bg, out, zoom=4):
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 9 * zoom // 2)
    cw, chh = 120, 130
    canvas = Image.new('RGBA', (cw * len(cells), chh), bg)
    for j, c in enumerate(cells):
        im = Image.fromarray(c, 'RGBA')
        canvas.alpha_composite(im, (j * cw + (cw - im.width) // 2, chh - 18 - im.height))
    big = canvas.resize((canvas.width * zoom, chh * zoom), Image.NEAREST)
    d = ImageDraw.Draw(big)
    fg = (40, 40, 40, 255) if sum(bg[:3]) > 380 else (230, 230, 230, 255)
    for j, t in enumerate(['기본 무녀 대기', '시크릿 레어 1 대기']):
        d.text(((j * cw + cw // 2) * zoom, (chh - 8) * zoom), t, font=font, fill=fg, anchor='mm')
    big.save(out)
    return out


if __name__ == '__main__':
    b, s = build()
    print('sr1 cell', s.shape[1], 'x', s.shape[0], '/ base', b.shape[1], 'x', b.shape[0])
    print(preview([b, s], (255, 255, 255, 255), '_preview_miko_sr1.png'))
    print(preview([b, s], (46, 50, 58, 255), '_preview_miko_sr1_dark.png'))

# 무녀 기본 외형(shaman_0.webp)에서 하카마·리본·머리·눈동자 색을 바꾼 외형 시트 만들기 (칸 구성·크기 모두 같음)
# 사용: python tools/shaman_variants_build.py [--preview 경로] [--all]  → assets/sprites/merc/shaman_1~5.webp (--preview면 비교 그림만)
# 규칙 (2026-11-17 사용자: "무녀 샘플 다른 외형 만들어봐. 눈동자 흰자 유지하면서"):
#   하카마·리본·끈 (빨강: 색상 335~15°, 채도 0.4↑) → 옷 색 (명암 순서 그대로). 얼굴 상자 안(눈·입)과 부적 위 붉은 글씨는 빼고
#   눈동자 = 얼굴 상자 위 1/4 ~ 70% 안의 어두운 붉은 갈색 (채도 0.4↑, 명도 0.15~0.55) → 눈 색
#   머리 = 어두운 무채색·푸른 회색이 빽빽한 큰 덩어리 → 머리 색. 몸 바깥과 맞닿은 가장자리는 어두운 외곽선으로 남김
#   그 밖은 모두 그대로: 피부 · 흰자 · 흰 저고리 · 버선 · 부적 · 외곽선
import os, sys, argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb
from volt_build import skin_mask

SRC = 'assets/sprites/merc/shaman_0.webp'
CELL_W = 101
# (번호, 이름, 옷 (색상°, 채도 배율, 명도 배율), 머리 (색상°, 채도, 가장 어두운 명도, 가장 밝은 명도), 눈 (색상°, 채도 배율, 명도 배율))
VARIANTS = [
    (1, '남빛 하카마 · 은청발 · 하늘 눈', (222, 0.85, 0.85), (215, 0.20, 0.38, 0.88), (205, 1.0, 1.5)),
    (2, '자줏빛 하카마 · 흑자발 · 보랏빛 눈', (295, 0.75, 0.85), (280, 0.40, 0.14, 0.42), (285, 1.0, 1.4)),
    (3, '비취 하카마 · 갈색 머리 · 비취 눈', (158, 0.75, 0.80), (24, 0.55, 0.20, 0.55), (150, 1.0, 1.4)),
    (4, '먹빛 하카마 · 백발 · 붉은 눈', (225, 0.12, 0.50), (40, 0.04, 0.58, 0.97), (355, 1.3, 1.6)),
    (5, '연분홍 하카마 · 적갈발 · 금안', (338, 0.55, 1.15), (8, 0.60, 0.22, 0.60), (42, 1.2, 1.9)),
]


def masks(rgba):
    hsv = rgb2hsv(rgba[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    al = rgba[..., 3] > 0
    skin = skin_mask(rgba[..., :3], rgba[..., 3] / 255.)
    face = np.zeros_like(al); eyezone = np.zeros_like(al)
    for k in range(rgba.shape[1] // CELL_W):
        sl = np.s_[:, k * CELL_W:(k + 1) * CELL_W]
        ys = np.where(al[sl].any(axis=1))[0]
        if not len(ys): continue
        sk = skin[sl].copy()
        lb, nb = ndi.label(sk)
        if nb == 0: continue
        # 얼굴 = 가장 큰 살색 덩어리 (누운 칸도 있어 위쪽 절반으로 자르지 않음)
        fy, fx = np.where(lb == np.argmax(ndi.sum(sk, lb, range(1, nb + 1))) + 1)
        face[sl][fy.min() - 1:fy.max() + 2, fx.min() - 1:fx.max() + 2] = True
        fh = fy.max() - fy.min()
        eyezone[sl][fy.min() + fh // 5:fy.min() + 70 * fh // 100 + 1, fx.min():fx.max() + 1] = True
    redish = ((h < 15) | (h > 335))
    # 눈동자: 얼굴 상자 안 어두운 붉은 갈색 (윤곽선은 명도 0.15↓라 빠지고, 입은 아래라 빠짐)
    eye = al & eyezone & ~skin & ((h < 25) | (h > 335)) & (s > 0.4) & (v >= 0.15) & (v < 0.55)
    # 옷 빨강: 얼굴 상자 밖 붉은 픽셀 (어두운 그늘까지)
    red = al & redish & (s > 0.4) & (v > 0.12) & ~face & ~skin
    # 부적 위 붉은 글씨: 작은 붉은 조각인데 둘레가 대부분 밝은 종이색 → 그대로
    lb, n = ndi.label(red, structure=np.ones((3, 3)))
    paper = al & (v > 0.6) & (s > 0.15) & (h >= 15) & (h < 55)
    for i in range(1, n + 1):
        c = lb == i
        if c.sum() > 40: continue
        ring = ndi.binary_dilation(c, structure=np.ones((3, 3))) & ~c
        if paper[ring].mean() > 0.4: red &= ~c
    # 붉은 그늘 (채도 낮은 어두운 적갈색): 옷에 붙어 있으면 옷으로
    shade = al & redish & (s > 0.25) & (v > 0.08) & (v < 0.5) & ~face & ~skin
    for _ in range(2):
        red |= shade & ndi.binary_dilation(red, structure=np.ones((3, 3)))
    # 손·발 윤곽 (살 2px 안의 흐린 적갈색, 채도 0.55↓): 옷 빨강은 채도 0.7 안팎이라 빼도 옷은 그대로
    red &= ~(ndi.binary_dilation(skin, iterations=2) & (s < 0.55))
    # 머리: 어두운 픽셀이 빽빽한 큰 덩어리
    dark = al & (v < 0.36) & ~skin & ~red & ~eye & ((s < 0.45) | (v < 0.1)) & ~(redish & (s > 0.3) & (v > 0.1))
    core = dark & (ndi.uniform_filter(dark.astype(float), 5) > 0.75)
    cand = (ndi.binary_dilation(core, structure=np.ones((3, 3)), iterations=2)) & dark
    lb, n = ndi.label(cand, structure=np.ones((3, 3)))
    idx = np.arange(n + 1)
    hair = ((ndi.sum(core, lb, idx) > 25))[lb] & cand
    hair |= ndi.binary_fill_holes(hair) & dark
    out_edge = ndi.binary_dilation(~al, structure=np.ones((3, 3)))
    # 얼굴 옆 가는 머리 가닥·뒷머리 끝: 빽빽하지 않아 빠진 어두운 픽셀 중 머리에 닿은 덩어리 (12px↑)
    lb, n = ndi.label(dark & ~hair, structure=np.ones((3, 3)))
    idx = np.arange(n + 1)
    nh = ndi.binary_dilation(hair, structure=np.ones((3, 3)))
    sz = ndi.sum(np.ones_like(dark), lb, idx); touchh = ndi.maximum(nh, lb, idx).astype(bool)
    inner = ndi.sum(~out_edge, lb, idx)   # 몸 바깥 외곽선만으로 된 덩어리는 빼기
    hair |= ((sz >= 12) & touchh & (inner >= 6))[lb] & (lb > 0)
    # 살·눈·흰자에 바로 붙은 선은 원본 그대로 (얼굴 윤곽)
    whites = al & (s < 0.25) & (v > 0.55) & face
    touch = ndi.binary_dilation(skin | eye | whites)
    hair &= ~(touch & (v < 0.2))
    rim = hair & out_edge
    return red, eye, hair, rim, hsv


def recolor(rgba, cloth_c, hair_c, eye_c):
    red, eye, hair, rim, hsv = masks(rgba)
    v0 = hsv[..., 2].copy()
    H, SM, VM = cloth_c
    hsv[..., 0] = np.where(red, H / 360, hsv[..., 0])
    hsv[..., 1] = np.where(red, np.clip(hsv[..., 1] * SM, 0, 1), hsv[..., 1])
    hsv[..., 2] = np.where(red, np.clip(v0 * VM, 0, 1), hsv[..., 2])
    H, S, LO, HI = hair_c
    # 검은 머리 명도(0.04~0.30)를 새 머리 색의 어두운~밝은 명도로 고르게 옮김
    t = np.clip((v0 - 0.04) / 0.26, 0, 1)
    vh = LO + (HI - LO) * t
    vh = np.where(rim, np.minimum(v0, 0.08) + LO * 0.25, vh)   # 몸 바깥 가장자리 = 어두운 외곽선
    hsv[..., 0] = np.where(hair, H / 360, hsv[..., 0])
    hsv[..., 1] = np.where(hair, np.clip(S * (1.15 - 0.3 * t), 0, 1), hsv[..., 1])
    hsv[..., 2] = np.where(hair, np.clip(vh, 0, 1), hsv[..., 2])
    H, SM, VM = eye_c
    hsv[..., 0] = np.where(eye, H / 360, hsv[..., 0])
    hsv[..., 1] = np.where(eye, np.clip(hsv[..., 1] * SM, 0, 1), hsv[..., 1])
    hsv[..., 2] = np.where(eye, np.clip(v0 * VM, 0, 1), hsv[..., 2])
    out = rgba.copy()
    m = red | eye | hair
    out[m, :3] = (hsv2rgb(hsv)[m] * 255).round().clip(0, 255).astype(np.uint8)   # 바꾼 픽셀만 씀
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--preview'); ap.add_argument('--all', action='store_true'); ap.add_argument('--masks'); args = ap.parse_args()
    src = np.array(Image.open(SRC).convert('RGBA'))
    if args.masks:   # 점검용: 옷=초록, 눈=노랑, 머리=파랑
        red, eye, hair, rim, _ = masks(src)
        o = src.copy(); o[red, :3] = (0, 220, 0); o[eye, :3] = (255, 255, 0); o[hair, :3] = (40, 90, 255); o[rim, :3] = (0, 0, 120)
        im = Image.fromarray(o).resize((src.shape[1] * 3, src.shape[0] * 3), Image.NEAREST)
        b = Image.new('RGBA', im.size, (60, 64, 74, 255)); b.alpha_composite(im); b.convert('RGB').save(args.masks); return
    sheets = [(0, '기본 (붉은 하카마)', src)] + [(n, name, recolor(src, rc, hc, ec)) for n, name, rc, hc, ec in VARIANTS]
    # 흰자 확인: 밝은 무채색(흰자·흰 저고리·버선)은 하나도 안 바뀌어야 함
    hsv0 = rgb2hsv(src[..., :3] / 255.)
    white = (src[..., 3] > 0) & (hsv0[..., 1] <= 0.15) & (hsv0[..., 2] > 0.6)
    for n, name, sh in sheets[1:]:
        assert not (sh[white] != src[white]).any(), f'{n} 흰자·흰 부분이 바뀜'
    if args.preview:
        frames = list(range(src.shape[1] // CELL_W)) if args.all else [0, 1, 5, 6, 10, 12]
        H = src.shape[0]; Z = 3
        img = Image.new('RGBA', (len(frames) * CELL_W * Z, len(sheets) * H * Z), (0, 0, 0, 0))
        for r, (_, _, sh) in enumerate(sheets):
            for c, f in enumerate(frames):
                cell = Image.fromarray(sh[:, f * CELL_W:(f + 1) * CELL_W]).resize((CELL_W * Z, H * Z), Image.NEAREST)
                img.paste(cell, (c * CELL_W * Z, r * H * Z))
        for bg, suf in [((236, 232, 220), '_light'), ((38, 42, 52), '_dark')]:
            b = Image.new('RGBA', img.size, bg + (255,)); b.alpha_composite(img); b.convert('RGB').save(args.preview + suf + '.png')
        return
    for n, name, sh in sheets[1:]:
        Image.fromarray(sh, 'RGBA').save(f'assets/sprites/merc/shaman_{n}.webp', 'WEBP', lossless=True)
        print(f'shaman_{n}.webp  {name}')


if __name__ == '__main__':
    main()

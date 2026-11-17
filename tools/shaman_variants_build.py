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

# 눈 뜬 칸의 눈동자 상자 (칸 안 x0, y0, x1, y1 · 끝 포함): 왼눈, 오른눈. 감은 눈 칸(6·7·8·11·12)은 없음 → 눈 색 안 넣음
EYE_BOXES = {
    0: [(46, 32, 49, 35), (56, 32, 58, 35)],
    1: [(48, 33, 51, 37), (59, 33, 61, 37)],
    2: [(50, 33, 53, 36), (60, 33, 62, 36)],
    3: [(49, 35, 52, 38), (59, 35, 60, 38)],
    4: [(50, 37, 54, 40), (60, 37, 63, 40)],
    5: [(51, 33, 55, 36), (62, 33, 65, 36)],
    9: [(49, 30, 52, 34), (60, 30, 62, 34)],
    10: [(49, 33, 52, 36), (59, 33, 61, 36)],
    13: [(51, 54, 54, 57), (61, 54, 63, 57)],
}

# 감은 눈 끝이 옆머리에 닿은 자리 (칸 안 x0, y0, x1, y1): 머리로 잡히면 밝은 머리색 얼룩이 얼굴에 생김 → 원본 그대로 둠
KEEP_BOXES = {7: [(67, 54, 70, 57)], 11: [(56, 35, 61, 37)], 12: [(60, 28, 63, 31)]}


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
    # 눈동자: 칸마다 지정한 상자 안에서 흰자·살·아주 어두운 속눈썹(명도 0.1↓)·밝은 살빛(0.65↑)을 뺀 픽셀
    #   (색으로만 고르면 눈썹·위 눈꺼풀 적갈색 줄·볼 윤곽까지 잡히고, 어두운 눈동자는 일부만 잡혀 얼룩이 됨)
    eyebox = np.zeros_like(al)
    for k, boxes in EYE_BOXES.items():
        for x0, y0, x1, y1 in boxes:
            eyebox[y0:y1 + 1, k * CELL_W + x0:k * CELL_W + x1 + 1] = True
    keep = np.zeros_like(al)
    for k, boxes in KEEP_BOXES.items():
        for x0, y0, x1, y1 in boxes:
            keep[y0:y1 + 1, k * CELL_W + x0:k * CELL_W + x1 + 1] = True
    eye = eyebox & al & ~skin & ~((s < 0.25) & (v > 0.55)) & (v >= 0.1) & (v < 0.65)
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
    # 옷 안에 홀로 남은 붉은 점(둘레 8칸 중 4칸↑이 옷): 새 옷 색 사이에서 붉은 점으로 튀어 보임 → 옷으로
    lone = al & ((h < 25) | (h > 330)) & (s > 0.3) & (v > 0.1) & ~skin & ~face & ~red & ~ndi.binary_dilation(skin, iterations=3)
    for _ in range(2):
        red |= lone & (ndi.convolve(red.astype(int), np.ones((3, 3), int), mode='constant') >= 4)
    # 조리 끈·끈 끝처럼 옷 빨강에 이어진 흐린 빨강·분홍빛 윤기(채도 0.16↑, 흰 부분은 0.15↓라 안 걸림): 일부만 바뀌면 빨강·새 색이 섞임 → 둘레 2칸↑이 옷이면 따라감 (살 3px 안은 빼기)
    faint = al & ((h < 25) | (h > 335)) & (s > 0.16) & (v > 0.08) & ~skin & ~face & ~red & ~ndi.binary_dilation(skin, iterations=3)
    for _ in range(4):
        red |= faint & (ndi.convolve(red.astype(int), np.ones((3, 3), int), mode='constant') >= 2)
    # 머리 속 작은 붉은 조각(가르마·볼 옆 머리결의 적갈색): 살 3px 안이고 12px 이하면 옷이 아님 → 옷 색 점이 됨
    lb, n = ndi.label(red, structure=np.ones((3, 3)))
    if n:
        idx = np.arange(n + 1)
        near_sk = ndi.maximum(ndi.binary_dilation(skin, iterations=3), lb, idx).astype(bool)
        red &= ~(((ndi.sum(red, lb, idx) <= 12) & near_sk)[lb] & (lb > 0))
    # 옷 테두리 검붉은 선 (색상 285~15°의 보랏빛·검붉은, 채도 0.2↑, 명도 0.4↓): 검은 머리(색상 200~250°)와 색으로 갈리는데
    #   채도·밝기가 낮아 옷으로 안 잡히고 머리로 들어가 머리색이 되면 끈·리본 둘레가 얼룩 → 옷 빨강에 이어진 것은 옷 윤곽
    maroon = al & ~skin & ~face & ~red & ((h >= 285) | (h < 15)) & (s > 0.2) & (v < 0.4)
    mar = np.zeros_like(al)
    for _ in range(3):
        mar |= maroon & ndi.binary_dilation(red | mar, structure=np.ones((3, 3)))
    # 머리: 어두운 픽셀이 빽빽한 큰 덩어리
    dark = al & (v < 0.36) & ~skin & ~red & ~mar & ~eye & ((s < 0.45) | (v < 0.1)) & ~(redish & (s > 0.3) & (v > 0.1))
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
    hair &= ~(touch & (v < 0.2)) & ~eyebox & ~keep
    # 얼굴 안쪽에 떨어져 있는 어두운 조각(감은 눈꼬리·속눈썹 끝): 얼굴 밖 머리와 이어지지 않으면 머리가 아님 → 원본 그대로
    #   (밝은 머리색이 되면 얼굴 위에 밝은 얼룩)
    inner_face = ndi.binary_erosion(face, iterations=2)
    hin = hair & inner_face
    lb, n = ndi.label(hin, structure=np.ones((3, 3)))
    if n:
        outer = ndi.binary_dilation(hair & ~inner_face, structure=np.ones((3, 3)))
        linked = ndi.maximum(outer, lb, np.arange(n + 1)).astype(bool)
        hair &= ~((~linked)[lb] & hin)
    # 윤곽선: 옷·머리 곁 어두운 선(명도 0.3↓) 중 바뀌지 않은 것(검붉은·아주 어두운 픽셀)이 새 색 사이에 섞이면 깨져 보임
    #   → 둘레 8칸에 옷이 더 많으면 옷 윤곽, 머리가 더 많으면 머리 윤곽으로 함께 칠함. 살·눈·흰자에 닿은 선은 원본 그대로
    ln = al & (v < 0.3) & ~red & ~hair & ~eye & ~eyebox & ~keep & ~skin & ~ndi.binary_dilation(skin | eye | whites, structure=np.ones((3, 3)))
    k3 = np.ones((3, 3), int)
    nr = ndi.convolve(red.astype(int), k3, mode='constant'); nhh = ndi.convolve(hair.astype(int), k3, mode='constant')
    cloth_ln = ln & (nr > 0) & (nr >= nhh)
    hair_ln = ln & (nhh > 0) & (nhh > nr)
    hair |= hair_ln
    # 머리 → 피부 경계 윤곽선: 원본은 검정·적갈색이 섞인 선인데, 일부만 머리색으로 바뀌면 얼룩지고 끊겨 보임
    #   → 피부에 상하좌우로 닿고 머리에 닿은 어두운 픽셀(명도 0.45↓)을 모두 같은 머리색 윤곽(몸 바깥 윤곽과 같은 색)으로
    skin_edge = al & ~skin & ~eyebox & ~keep & (v < 0.45) & ndi.binary_dilation(skin) & ~whites
    hair_edge = skin_edge & (hair | ndi.binary_dilation(hair, structure=np.ones((3, 3))))
    # 얼굴 윤곽선 (2026-11-17 사용자: "얼굴 윤곽선과 눈썹 부분도 얼룩 제거", "더 얇게",
    #   "눈썹 위에 부분은 머리카락이 아니라 피부 음영진거야"):
    #   얼굴 상자 안의 적갈색 중간 밝기(명도 0.22↑) = 앞머리 그늘이 진 피부·눈썹 → 원본 그대로 (머리색·옷 색 어느 쪽으로도 안 칠함)
    #   짙은 선(명도 0.22↓) 중 피부·그늘에 상하좌우로 닿은 한 줄 = 윤곽선 → 머리 윤곽 색 하나로 (원본 검정·적갈색이 반반 바뀌던 얼룩 해결)
    #   눈 바로 위 검은 속눈썹(명도 0.12↓)은 원본 검정 그대로 (눈매가 흐려지지 않게)
    lash = ndi.binary_dilation(eyebox, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 0, 0]], bool), iterations=2) & (v < 0.12)
    facebox = ndi.binary_dilation(face, iterations=1)
    shade = facebox & al & ~skin & ~eye & ~eyebox & ((h < 35) | (h > 330)) & (s > 0.2) & (v >= 0.22)
    fl = facebox & al & ~skin & ~shade & ~whites & ~eye & ~eyebox & ~keep & ~lash & (v < 0.22) & ndi.binary_dilation(skin | shade)
    #   입·코·감은 눈 선처럼 얼굴 안에 따로 떨어진 선은 빼기: 머리나 몸 바깥에 이어진 덩어리만
    lb, n = ndi.label(fl, structure=np.ones((3, 3)))
    if n:
        link = ndi.binary_dilation(hair | out_edge, structure=np.ones((3, 3)))
        fl &= ndi.maximum(link, lb, np.arange(n + 1)).astype(bool)[lb]
    hair = (hair | hair_edge | fl) & ~shade
    hair_edge &= ~shade; hair_ln &= ~shade; cloth_ln &= ~shade
    hair &= ~mar; hair_ln &= ~mar; hair_edge &= ~mar; cloth_ln |= mar & ~red
    red &= ~shade & ~fl
    # 머리와 옷(흰 저고리·하카마·옷 윤곽)이 맞닿는 검은 경계선: 머리 속으로 치면 밝은 머리색(백발)이 돼 옷 윤곽이 하얗게 사라짐 → 짙은 윤곽
    cloth_near = ndi.binary_dilation(((s < 0.25) & (v > 0.55) & ~face) | red | cloth_ln, structure=np.ones((3, 3)))
    hair_cloth = hair & cloth_near & (v < 0.2)
    #   (사용자: "백발 샘플은 아직도 흰색 얼룩이 윤곽선에") 저고리·피부·귀·리본 등 머리가 아닌 것에 8방향으로 닿은 짙은 머리 픽셀(명도 0.3↓)은 모두 경계 윤곽
    hair_cloth |= hair & (v < 0.3) & ndi.binary_dilation(al & ~hair, structure=np.ones((3, 3)))
    rim = (hair & out_edge) | hair_ln | hair_edge | fl | hair_cloth
    brow = np.zeros_like(al)   # (예전 눈썹 둘째 줄 처리: 피부 그늘이라 이제 원본 그대로)
    return red, eye, hair, rim, hsv, cloth_ln, brow


def recolor(rgba, cloth_c, hair_c, eye_c):
    red, eye, hair, rim, hsv, cloth_ln, brow = masks(rgba)
    v0 = hsv[..., 2].copy(); s0 = hsv[..., 1].copy()
    H, SM, VM = cloth_c
    # 옷 윤곽선: 아주 어두운 픽셀은 채도 값이 들쭉날쭉해서 옷 그늘 채도(0.6)로 고르게
    hsv[..., 1] = np.where(cloth_ln, 0.6, hsv[..., 1])
    red = red | cloth_ln
    hsv[..., 0] = np.where(red, H / 360, hsv[..., 0])
    hsv[..., 1] = np.where(red, np.clip(hsv[..., 1] * SM, 0, 1), hsv[..., 1])
    hsv[..., 2] = np.where(red, np.clip(v0 * VM, 0, 1), hsv[..., 2])
    H, S, LO, HI = hair_c
    # 검은 머리 명도(0.04~0.30)를 새 머리 색의 어두운~밝은 명도로 고르게 옮김
    t = np.clip((v0 - 0.04) / 0.26, 0, 1)
    vh = LO + (HI - LO) * t
    vh = np.where(rim, np.minimum(v0, 0.08) + LO * 0.25, vh)
    # 눈썹 둘째 줄: 밝은 머리색이면 눈 위에 흰 줄처럼 보임 (백발) → 윤곽선보다 조금 밝은 짙은 머리색, 원본 명암 순서는 살림
    vh = np.where(brow, np.minimum(v0, 0.08) + LO * 0.25 + 0.35 * np.clip(v0 - 0.08, 0, 0.5), vh)   # 몸 바깥 가장자리 = 어두운 외곽선
    hsv[..., 0] = np.where(hair, H / 360, hsv[..., 0])
    hsv[..., 1] = np.where(hair, np.clip(S * (1.15 - 0.3 * t), 0, 1), hsv[..., 1])
    hsv[..., 2] = np.where(hair, np.clip(vh, 0, 1), hsv[..., 2])
    H, SM, VM = eye_c
    hsv[..., 0] = np.where(eye, H / 360, hsv[..., 0])
    hsv[..., 1] = np.where(eye, np.clip(np.maximum(hsv[..., 1], 0.45) * SM, 0, 1), hsv[..., 1])
    hsv[..., 2] = np.where(eye, np.clip(v0 * VM, 0, 1), hsv[..., 2])
    out = rgba.copy()
    m = red | eye | hair
    out[m, :3] = (hsv2rgb(hsv)[m] * 255).round().clip(0, 255).astype(np.uint8)   # 바꾼 픽셀만 씀
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--preview'); ap.add_argument('--all', action='store_true'); ap.add_argument('--masks'); args = ap.parse_args()
    src = np.array(Image.open(SRC).convert('RGBA'))
    if args.masks:   # 점검용: 옷=초록, 눈=노랑, 머리=파랑
        red, eye, hair, rim, _, cl, _ = masks(src)
        o = src.copy(); o[red, :3] = (0, 220, 0); o[cl, :3] = (0, 110, 0); o[eye, :3] = (255, 255, 0); o[hair, :3] = (40, 90, 255); o[rim, :3] = (0, 0, 120)
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

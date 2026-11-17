# 기공사 기본 외형(qigong_0.webp)에서 도포·머리·눈동자 색을 바꾼 외형 시트 만들기 (칸 구성·크기 모두 같음)
# 사용: python tools/qigong_variants_build.py [--preview 경로] [--all]  → assets/sprites/merc/qigong_1~5.webp (--preview면 비교 그림만)
# 규칙 (2026-11-17 사용자: "눈동자 흰자 살려서", "머리색, 눈색도 변경해봐 어울리게"):
#   도포·신발·띠 (금빛: 색상 27~62°, 채도 0.42↑) → 도포 색 (명암 순서 그대로)
#   눈동자 = 얼굴 상자 위 1/4 ~ 85%(위 머리핀·아래 깃 자리 빼고)에 다 들어가는 24px 이하 금갈색 조각 + 붙은 어두운 테 → 눈 색 (도포와 따로)
#   머리 = 어두운 무채색이 빽빽한 곳 중 얼굴 곁 덩어리(masks 안 설명) → 머리 색. 덩어리 가장자리 외곽선은 어둡게 남김
#   그 밖은 모두 그대로: 피부 · 흰자 · 흰 속옷·바지 · 외곽선
import os, sys, argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb
from volt_build import skin_mask

SRC = 'assets/sprites/merc/qigong_0.webp'
CELL_W = 103
# (번호, 이름, 도포 (색상°, 채도 배율, 명도 배율), 머리 (색상°, 채도, 가장 어두운 명도, 가장 밝은 명도), 눈 (색상°, 채도 배율))
VARIANTS = [
    (1, '청람 도포 · 은청발 · 하늘 눈', (212, 0.85, 0.95), (212, 0.22, 0.36, 0.86), (205, 1.0)),
    (2, '주홍 도포 · 적발 · 금안', (6, 0.95, 0.95), (4, 0.62, 0.22, 0.62), (45, 1.0)),
    (3, '비취 도포 · 청록발 · 비취 눈', (150, 0.75, 0.88), (172, 0.48, 0.16, 0.50), (150, 1.0)),
    (4, '자줏빛 도포 · 은백발 · 보랏빛 눈', (282, 0.7, 0.9), (275, 0.10, 0.48, 0.93), (285, 0.9)),
    (5, '먹빛 도포 · 백발 · 붉은 눈', (220, 0.15, 0.55), (40, 0.04, 0.55, 0.97), (355, 1.1)),
]


def masks(rgba):
    hsv = rgb2hsv(rgba[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    al = rgba[..., 3] > 0
    robe = al & (h >= 27) & (h < 62) & (s > 0.42)
    # 얼굴 상자 = 칸마다 그림 위쪽 절반의 가장 큰 살색 덩어리 (손·발 곁 도포 조각은 안 건드리게)
    skin = skin_mask(rgba[..., :3], rgba[..., 3] / 255.)
    # 그늘진 살 (귀 안쪽 등 피부로 안 잡힌 따뜻한 색): 머리로 먹히면 귀가 머리색이 됨
    skinish = al & ~robe & (s > 0.12) & (s < 0.65) & ((((h < 40) | (h > 340)) & (v > 0.45)) | (((h < 25) | (h > 340)) & (v > 0.3)))
    face = np.zeros_like(robe); face_low = np.zeros_like(robe); head = np.zeros_like(robe)
    for k in range(rgba.shape[1] // CELL_W):
        sl = np.s_[:, k * CELL_W:(k + 1) * CELL_W]
        ys = np.where(al[sl].any(axis=1))[0]
        if not len(ys): continue
        sk = skin[sl].copy(); sk[ys.min() + (ys.max() - ys.min()) // 2:] = False
        lb, nb = ndi.label(sk)
        if nb == 0: continue
        fy, fx = np.where(lb == np.argmax(ndi.sum(sk, lb, range(1, nb + 1))) + 1)
        face[sl][fy.min():fy.max() + 1, fx.min() - 1:fx.max() + 2] = True
        head[sl][:fy.max() + 1] = True   # 턱 위 (머리핀 자리)
        face_low[sl][fy.min() + (fy.max() - fy.min()) // 4:fy.min() + 85 * (fy.max() - fy.min()) // 100 + 1, fx.min() - 1:fx.max() + 2] = True
    lb, n = ndi.label(robe)
    idx = np.arange(n + 1)
    small = ndi.sum(robe, lb, idx) <= 24
    inside = ndi.minimum(face, lb, idx).astype(bool)
    low = ndi.minimum(face_low, lb, idx).astype(bool)   # 얼굴 위 1/4 ~ 85% (이마 위 금빛 머리핀·턱 밑 깃 조각은 눈동자가 아니라 도포 색으로)
    eye = (small & inside & low)[lb] & robe   # 눈동자 (얼굴 상자 안에 다 들어가는 작은 금갈색 조각)
    # 눈동자 위쪽 어두운 테 (명도 0.12~0.5, 채도가 조금 낮아 위에서 빠짐): 눈동자에 붙은 갈색은 눈동자로 — 안 그러면 테만 갈색으로 남음
    for _ in range(2):
        eye |= ndi.binary_dilation(eye, structure=np.ones((3, 3))) & al & ~skin & (h >= 25) & (h < 62) & (s > 0.3) & (v > 0.12) & (v < 0.5)   # 얼굴 윤곽(붉은 갈색 5~20°)으로 번지지 않게
    # 머리: 검은 머리는 그늘진 곳이 외곽선만큼 어두워서 밝기로는 못 가름 → 어두운 픽셀이 빽빽한 곳(5×5 안 75%↑)을 머리로,
    #   가는 외곽선은 빽빽하지 않아 빠짐. 그중 얼굴 곁에 닿은 40px 넘는 덩어리 + 거기서 5px 안의 덩어리(팔에 가린 뒷머리)
    # 아주 어두운 픽셀(명도 0.12↓)은 채도 값이 들쭉날쭉해서(0.01 명도에 채도 0.67 등) 채도와 상관없이 어두운 쪽으로
    # (검은 머리의 푸른 회색 윤기 0.32~0.45는 여기 넣지 않음 — 팔 윤곽선까지 머리로 이어짐. 머리에 둘러싸인 윤기는 아래 loose로 들어감)
    dark = al & (((v < 0.32) & (s < 0.35)) | (v < 0.12)) & ~skin & ~robe & ~eye
    core = dark & (ndi.uniform_filter(dark.astype(float), 5) > 0.75)
    cand = (ndi.binary_dilation(core, structure=np.ones((3, 3))) | (v >= 0.09)) & dark   # 빽빽한 그늘 + 밝은 머리결
    lb, n = ndi.label(cand, structure=np.ones((3, 3)))
    idx = np.arange(n + 1)
    big = ndi.sum(cand, lb, idx) > 40
    solid = ndi.sum(core, lb, idx) > 15   # 빽빽한 그늘이 큰 덩어리 = 이 그림에선 머리뿐 (소매에 가려 머리와 끊긴 뒷머리)
    hair = ((ndi.maximum(ndi.binary_dilation(face, iterations=4), lb, idx).astype(bool) | solid) & big)[lb] & cand
    for _ in range(3):
        hair = (ndi.maximum(ndi.binary_dilation(hair, iterations=5), lb, idx).astype(bool) & big)[lb] & cand
    hair |= ndi.binary_fill_holes(hair) & dark   # 머리 안에 갇힌 아주 어두운 머리결 선·점
    out_edge = ndi.binary_dilation(~al, structure=np.ones((3, 3)))
    loose = al & ~skin & ~skinish & ~robe & ~eye & (v < 0.5) & (s < 0.6)   # 머리결 사이 중간 밝기 갈색 선(가르마·머리결)도 둘러싸이면 머리
    for _ in range(3):   # 머리를 가로지르는 어두운 머리결 선 (갇히진 않았지만 둘레 8칸 중 5칸↑이 머리, 몸 바깥 외곽선은 빼고)
        hair |= loose & ~out_edge & (ndi.convolve(hair.astype(int), np.ones((3, 3), int), mode='constant') >= 5)
    hair = ndi.binary_opening(hair, structure=np.ones((2, 2))) | (hair & ndi.binary_dilation(core, iterations=1))   # 띠·옷 그늘의 1px 낱점 빼기
    # 머리 가장자리 금빛 낱점(눈동자로 잘못 잡힘): 둘레 1px의 40%↑가 머리면 눈동자에서 빼고 도포 색으로
    lb, n = ndi.label(eye, structure=np.ones((3, 3)))
    for i in range(1, n + 1):
        c = lb == i; ring = ndi.binary_dilation(c, structure=np.ones((3, 3))) & ~c
        if hair[ring].mean() > 0.4: eye &= ~c
    hair &= ~eye & ~skinish
    # 머리 속 금빛 윤기 (턱 위, 둘레 1px의 40%↑가 머리인 40px 이하 도포색 조각): 도포 색이면 밝은 머리에서 검은 구멍 → 머리 (밝은 머리결)
    lb, n = ndi.label(robe & ~eye, structure=np.ones((3, 3)))
    for i in range(1, n + 1):
        c = lb == i
        if c.sum() > 40: continue
        ring = ndi.binary_dilation(c, structure=np.ones((3, 3))) & ~c
        if hair[ring].mean() > 0.4 and head[c].all(): robe &= ~c; hair |= c   # 턱 위만 (긴 머리에 닿은 소매 조각은 도포 색)
    # 머리 안쪽 선: 머리에 3칸↑ 닿은 아주 어두운 선(앞머리 가닥 사이·얼굴과의 경계) — 검정 그대로면 밝은 머리에서 검은 점이 섞여 깨져 보임
    line = al & (v < 0.12) & ~hair & ~eye & ~out_edge & (ndi.convolve(hair.astype(int), np.ones((3, 3), int), mode='constant') >= 3)
    # 머리 위 금빛 윤기 (턱 위·얼굴 밖에서 머리에 닿은 30px 이하 흐린 금갈색 덩어리): 반은 머리·반은 그대로면 얼룩덜룩 → 통째로 머리 (밝은 머리결): 그대로면 밝은 머리에서 갈색 얼룩 → 또렷한 금빛 장식으로 밝힘
    pc = head & ~ndi.binary_dilation(face, iterations=1) & al & ~eye & ~robe & ~skin & (v > 0.13) & (h >= 30) & (h < 62) & (s > 0.25)
    lbp, npn = ndi.label(pc, structure=np.ones((3, 3)))
    nh = ndi.binary_dilation(hair & ~pc, structure=np.ones((3, 3)))
    pin = np.zeros_like(pc)
    for i in range(1, npn + 1):
        c = lbp == i
        if c.sum() <= 30 and (c & nh).any(): pin |= c
    hair |= pin; line &= ~pin
    # 도포 그늘·윤곽 (채도가 조금 낮은 금빛 · 갈색 그늘 12~27°): 도포에 붙어 있으면 도포로 — 빠지면 새 도포 색 위에 갈색 점으로 남음 (얼굴 상자 안은 빼서 턱선 그대로)
    shade_c = al & (h >= 12) & (h < 62) & (s > 0.3) & (v > 0.08) & (v < 0.6) & ~skin & ~hair & ~eye & ~pin & ~ndi.binary_dilation(face, iterations=1)
    for _ in range(3):
        robe |= shade_c & ndi.binary_dilation(robe, structure=np.ones((3, 3)))
    # 얼굴·손 윤곽선 (살에 닿은 어두운 선, 명도 0.3↓): 머리·도포 색으로 칠하면 얼굴 테두리가 옷·머리 색이 됨 → 원본 검정·갈색 그대로
    #   살 = 피부 + 그늘진 살(귀 안쪽 등 피부로 안 잡힌 따뜻한 밝은 색) + 눈동자 + 얼굴 곁 흰자 (눈꼬리 속눈썹은 살이 아니라 눈에 닿아 있음)
    whites = al & (s < 0.25) & (v > 0.6) & ndi.binary_dilation(face, iterations=2)
    #   1px만: 살에 상하좌우로 바로 붙은 진한 선(명도 0.2↓)만 검정으로 — 대각선·조금 밝은 픽셀까지 남기면 머리 쪽으로 두 겹이 돼 두꺼워 보임
    touch = ndi.binary_dilation(skin | (skinish & ~robe) | eye | whites)   # 기본 구조 = 십자 (상하좌우)
    outline = touch & ((v < 0.2) | hair | line)   # 살에 바로 붙은 머리 픽셀은 밝기와 상관없이 원본(어두운 선) — 밝히면 윤곽선 사이에 머리색·흰 점이 끼어 끊겨 보임
    robe &= ~outline; line &= ~outline; hair &= ~outline
    return robe & ~eye, eye, hair, line, hsv


def recolor(rgba, robe_c, hair_c, eye_c):
    robe, eye, hair, line, hsv = masks(rgba)
    v0 = hsv[..., 2].copy(); al = rgba[..., 3] > 0
    H, SM, VM = robe_c
    hsv[..., 0] = np.where(robe, H / 360, hsv[..., 0])
    hsv[..., 1] = np.where(robe, np.clip(hsv[..., 1] * SM, 0, 1), hsv[..., 1])
    hsv[..., 2] = np.where(robe, np.clip(v0 * VM, 0, 1), hsv[..., 2])
    H, S, LO, HI = hair_c
    # 검은 머리 명도(0.06~0.26)를 새 머리 색의 어두운~밝은 명도로 고르게 옮김 (밝기를 더하기만 하면 어두운 머리결 선이 검은 점으로 남아 깨져 보임)
    #   몸 바깥과 맞닿은 가장자리는 모두 같은 어두운 외곽선 (원본은 0.05·0.12가 섞여 있어 밝히면 점선이 됨)
    t = np.clip((v0 - 0.06) / 0.20, 0, 1)
    vh = LO + (HI - LO) * t
    rim = hair & ndi.binary_dilation(~al, structure=np.ones((3, 3)))
    vh = np.where(rim, np.minimum(v0, 0.08) + LO * 0.25, vh)
    hsv[..., 0] = np.where(hair, H / 360, hsv[..., 0])
    hsv[..., 1] = np.where(hair, S * (1.15 - 0.3 * t), hsv[..., 1])
    hsv[..., 2] = np.where(hair, np.clip(vh, 0, 1), hsv[..., 2])
    hsv[..., 0] = np.where(line, H / 360, hsv[..., 0])   # 안쪽 선 = 머리 색의 짙은 그늘
    hsv[..., 1] = np.where(line, min(1, S * 1.2), hsv[..., 1])
    hsv[..., 2] = np.where(line, LO * 0.8, hsv[..., 2])
    H, SM = eye_c
    hsv[..., 0] = np.where(eye, H / 360, hsv[..., 0])
    hsv[..., 1] = np.where(eye, np.clip(hsv[..., 1] * SM, 0, 1), hsv[..., 1])
    out = rgba.copy()
    m = robe | eye | hair | line
    out[m, :3] = (hsv2rgb(hsv)[m] * 255).round().clip(0, 255).astype(np.uint8)   # 바꾼 픽셀만 씀
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--preview'); ap.add_argument('--all', action='store_true'); args = ap.parse_args()
    src = np.array(Image.open(SRC).convert('RGBA'))
    sheets = [(0, '기본 (금빛 도포)', src)] + [(n, name, recolor(src, rc, hc, ec)) for n, name, rc, hc, ec in VARIANTS]
    # 흰자 확인: 밝은 무채색(흰자·흰 옷)은 하나도 안 바뀌어야 함
    hsv0 = rgb2hsv(src[..., :3] / 255.)
    white = (src[..., 3] > 0) & (hsv0[..., 1] <= 0.15) & (hsv0[..., 2] > 0.6)
    for n, name, sh in sheets[1:]:
        assert not (sh[white] != src[white]).any(), f'{n} 흰자·흰 부분이 바뀜'
    if args.preview:
        frames = list(range(src.shape[1] // CELL_W)) if args.all else [0, 1, 6, 7, 11, 19]
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
        Image.fromarray(sh, 'RGBA').save(f'assets/sprites/merc/qigong_{n}.webp', 'WEBP', lossless=True)
        print(f'qigong_{n}.webp  {name}')


if __name__ == '__main__':
    main()

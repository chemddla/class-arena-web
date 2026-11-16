# 기계공 기본 외형(engineer_0.webp)에서 작업복·고글 렌즈 색만 바꾼 외형 시트 만들기 (칸 구성·크기 모두 같음)
# 사용: python tools/engineer_variants_build.py [--preview 경로]   → assets/sprites/merc/engineer_1~5.webp (--preview면 비교 그림만)
# 규칙 (2026-11-16 사용자: "눈동자 흰자 부분 유지", "머리 색도 바꿔봐"):
#   머리 (갈색, 얼굴 위쪽에서 시작하는 덩어리만 — hair_mask) → 머리 색. 눈동자(흰자 둘레 2px)는 그대로
#   작업복 (올리브: 색상 38~80°, 채도 0.12↑, 명도 0.12↑) → 작업복 색 (명암 순서 그대로)
#   고글 렌즈 (청록: 색상 150~200°, 채도 0.15↑) → 렌즈 색
#   그 밖은 모두 그대로: 피부·머리·가죽 가방·장화(주황~갈색 0~38°) · 흰자·셔츠(밝은 무채색) · 외곽선·쇠붙이(무채색)
import os, sys, argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb
from volt_build import skin_mask

SRC = 'assets/sprites/merc/engineer_0.webp'
CELL_W = 119
# (번호, 이름, 작업복 (색상°, 채도, 명도 배율, 명도 더함), 렌즈 (색상°, 채도 배율), 머리 (색상°, 채도, 명도 배율, 명도 더함))
VARIANTS = [
    (1, '남색 정비복 · 호박 렌즈 · 흑발',   (218, 0.45, 1.05, 0.02), (38, 1.3),  (225, 0.30, 0.55, 0.0)),
    (2, '주황 안전복 · 청록 렌즈 · 금발',   (24, 0.70, 1.45, 0.10),  (175, 1.0), (44, 0.62, 1.35, 0.18)),
    (3, '회색 도시복 · 빨간 렌즈 · 은발',   (210, 0.08, 1.15, 0.04), (355, 1.3), (215, 0.08, 1.25, 0.28)),
    (4, '빨간 레이서복 · 금빛 렌즈 · 적발', (352, 0.78, 1.25, 0.0),  (48, 1.4),  (4, 0.72, 1.3, 0.04)),
    (5, '흰 우주복 · 하늘 렌즈 · 하늘빛 머리', (40, 0.06, 0.75, 0.55), (200, 1.2), (198, 0.45, 1.3, 0.12)),
]


def masks(rgba):
    hsv = rgb2hsv(rgba[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    al = rgba[..., 3] > 0
    suit = al & (h >= 38) & (h < 80) & (s > 0.12) & (v > 0.12) & (v < 0.6)   # 0.6 위 = 크림색 셔츠, 그대로
    # 바지 그늘(갈색 쪽으로 기운 어두운 올리브)은 작업복 덩어리에 붙어 있을 때만 끌어들임 — 가방·장화 갈색은 안 건드림
    shade = al & (h >= 30) & (h < 38) & (s > 0.12) & (v > 0.12) & (v < 0.35)
    suit |= shade & ndi.binary_dilation(suit, iterations=1)
    lb, nb = ndi.label(suit)
    suit &= (ndi.sum(suit, lb, range(nb + 1)) >= 4)[lb]   # 얼굴·가방의 낱점은 빼기
    lens = al & (h >= 150) & (h < 200) & (s > 0.15)
    return suit, lens, hair_mask(rgba, h, s, v, al), hsv


def hair_mask(rgba, h, s, v, al):
    # 머리 = 칸마다 얼굴(위쪽 절반의 가장 큰 살색 덩어리) 위쪽에서 시작하는 갈색 덩어리, 얼굴 둘레 ±14px·턱 위로 자름
    # (가방·장갑·장화도 같은 갈색이라 자리로 가름) · 눈동자(흰자에 붙은 갈색)는 빼서 그대로
    skin = skin_mask(rgba[..., :3], rgba[..., 3] / 255.)
    # 앞머리 밑 그늘진 피부(살색보다 어둡고 붉은 갈색)는 빼기: 머리카락은 명도 0.5 아래, 0.38 위의 밝은 머리는 노란 기(색상 18° 이상)
    cand = al & (h < 45) & (s > 0.25) & (v > 0.08) & (v < 0.5) & ~((v >= 0.38) & (h < 18)) & ~skin
    white = al & (s <= 0.12) & (v > 0.6)
    hair = np.zeros_like(cand)
    for k in range(rgba.shape[1] // CELL_W):
        x0 = k * CELL_W; sl = np.s_[:, x0:x0 + CELL_W]
        ys = np.where(al[sl].any(axis=1))[0]
        if not len(ys): continue
        sk = skin[sl].copy(); sk[ys.min() + (ys.max() - ys.min()) // 2:] = False
        lb, nb = ndi.label(sk)
        if nb == 0: continue
        fy, fx = np.where(lb == np.argmax(ndi.sum(sk, lb, range(1, nb + 1))) + 1)
        top, bot = fy.min(), fy.max()
        c = cand[sl]; lb, nb = ndi.label(c)
        hm = np.zeros_like(c)
        for i in range(1, nb + 1):
            py, px = np.where(lb == i)
            if py.min() < top + 0.35 * (bot - top) and px.max() >= fx.min() - 12 and px.min() <= fx.max() + 12:
                hm |= lb == i
        hm[bot + 1:] = False
        hm[:, :max(0, fx.min() - 14)] = False; hm[:, fx.max() + 15:] = False
        # 눈 = 얼굴 안 흰자 상자 (위아래 1px·옆 2px 둘레): 눈동자·속눈썹은 그대로, 그 위 눈썹은 머리 색
        wy, wx = np.where(white[sl] & (np.arange(len(hm))[:, None] >= top) & (np.arange(len(hm))[:, None] <= bot)
                          & (np.arange(CELL_W)[None, :] >= fx.min()) & (np.arange(CELL_W)[None, :] <= fx.max()))
        if len(wy): hm[wy.min() - 1:wy.max() + 2, wx.min() - 2:wx.max() + 3] = False
        for bx0, by0, bx1, by1, on in HAIR_FIX.get(k, []):
            hm[by0:by1, bx0:bx1] = c[by0:by1, bx0:bx1] if on else False
        hair[sl] = hm
    return hair


HAIR_FIX = {   # 쓰러짐 칸은 머리가 가방 곁으로 내려와 자리 규칙이 안 맞음
    10: [(58, 44, 82, 49, False)],                            # 피격: 질끈 감은 눈 (흰자가 없어 눈 상자로 못 가림)
    11: [(0, 0, 60, 106, False)],                             # 쓰러짐 1: 머리 왼쪽 가방 윗면
    12: [(0, 0, 70, 106, False), (92, 72, 104, 100, True)],   # 쓰러짐 2: 가방 윗면 · 누운 머리 뒤쪽 머리카락
}   # 칸 번호: [(x0, y0, x1, y1, True = 머리로 칠함 / False = 칠하지 않음)] (칸 안 좌표)


def shade(hsv, m, c, dark_fade=False):
    H, S, VM, VA = c
    if dark_fade:   # 어두운 픽셀(눈썹·구레나룻·귀 둘레 선)은 덜 밝혀 곁의 검은 선과 이어지게 — 안 그러면 밝은 점이 얼룩처럼 뜸
        VA = VA * np.clip((hsv[..., 2] - 0.1) / 0.25, 0, 1)
    hsv[..., 0] = np.where(m, H / 360, hsv[..., 0])
    hsv[..., 1] = np.where(m, S * (0.6 + 0.4 * (1 - hsv[..., 2])), hsv[..., 1])
    edge = m & ~ndi.binary_erosion(m, structure=np.ones((3, 3)))   # 가장자리는 덜 밝혀 윤곽 유지
    hsv[..., 2] = np.where(m, np.clip(hsv[..., 2] * VM + VA * (1 - 0.45 * edge), 0, 1), hsv[..., 2])


def recolor(rgba, suit_c, lens_c, hair_c):
    suit, lens, hair, hsv = masks(rgba)
    shade(hsv, hair, hair_c, dark_fade=True)
    shade(hsv, suit, suit_c)
    LH, LS = lens_c
    hsv[..., 0] = np.where(lens, LH / 360, hsv[..., 0])
    hsv[..., 1] = np.where(lens, np.clip(hsv[..., 1] * LS, 0, 1), hsv[..., 1])
    out = rgba.copy()
    m = suit | lens | hair   # 바꾼 픽셀만 씀 (나머지는 색 변환 반올림도 안 타게 원본 그대로)
    out[m, :3] = (hsv2rgb(hsv)[m] * 255).round().clip(0, 255).astype(np.uint8)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--preview'); ap.add_argument('--all', action='store_true'); args = ap.parse_args()
    src = np.array(Image.open(SRC).convert('RGBA'))
    sheets = [(0, '기본 (올리브 작업복)', src)] + [(n, name, recolor(src, sc, lc, hc)) for n, name, sc, lc, hc in VARIANTS]
    # 흰자 확인: 바뀐 픽셀이 밝은 무채색(흰자·셔츠)에 하나도 없어야 함
    hsv0 = rgb2hsv(src[..., :3] / 255.)
    white = (src[..., 3] > 0) & (hsv0[..., 1] <= 0.12) & (hsv0[..., 2] > 0.6)
    for n, name, sh in sheets[1:]:
        assert not (sh[white] != src[white]).any(), f'{n} 흰자·흰 부분이 바뀜'
    if args.preview:
        frames = list(range(src.shape[1] // CELL_W)) if args.all else [0, 1, 6, 9, 10]   # 대기 · 걷기 · 쏨 · 설치 · 피격 (--all = 모든 칸)
        H = src.shape[0]; Z = 3
        img = Image.new('RGBA', (len(frames) * CELL_W * Z, len(sheets) * H * Z), (0, 0, 0, 0))
        for r, (_, _, sh) in enumerate(sheets):
            for c, f in enumerate(frames):
                cell = Image.fromarray(sh[:, f * CELL_W:(f + 1) * CELL_W]).resize((CELL_W * Z, H * Z), Image.NEAREST)
                img.paste(cell, (c * CELL_W * Z, r * H * Z))
        for bg, suf in [((236, 232, 220), '_light'), ((38, 42, 52), '_dark')]:
            b = Image.new('RGBA', img.size, bg + (255,)); b.alpha_composite(img); b.convert('RGB').save(args.preview + suf + '.png')
        for n, name, _ in sheets: print(n, name)
        return
    for n, name, sh in sheets[1:]:
        Image.fromarray(sh, 'RGBA').save(f'assets/sprites/merc/engineer_{n}.webp', 'WEBP', lossless=True)
        print(f'engineer_{n}.webp  {name}')


if __name__ == '__main__':
    main()

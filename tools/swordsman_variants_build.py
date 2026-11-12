# 검사 기본 외형(swordsman_0.webp)에서 도복 색만 바꾼 외형 시트 만들기 (칸 구성·크기 모두 같음)
# 사용: python tools/swordsman_variants_build.py [--preview 경로]   → assets/sprites/merc/swordsman_1~5.webp (--preview면 비교 그림만)
# 규칙 (2026-11-12 사용자: "피부색, 흰자 두고"):
#   도복 (남색: 색상 195~255°, 채도 0.2↑, 명도 0.07~0.45) → 도복 색 (색상·채도를 바꾸고 명도를 올려 색이 보이게, 명암 순서는 그대로)
#   그 밖은 모두 그대로: 피부·흰자(따뜻한 색·밝은 무채색이라 남색 범위 밖) · 검은 머리·하카마·외곽선(명도 0.07 아래·무채색) · 칼날(밝은 하늘색, 명도 0.45 위)
import os, sys, argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb
from volt_build import skin_mask

SRC = 'assets/sprites/merc/swordsman_0.webp'
CELL_W = 172
# (번호, 이름, 도복 (색상°, 채도, 명도 배율, 명도 더함))
VARIANTS = [   # 무협 느낌 (2026-11-12 사용자): 백의·청삼·홍의·자의·황삼, 채도는 낮춰 비단·무명 빛
    (1, '백의 (상아빛 흰 옷)', (42, 0.08, 0.8, 0.60)),
    (2, '청삼 (옥빛 청록)',   (172, 0.45, 1.5, 0.12)),
    (3, '홍의 (진사 주홍)',   (6, 0.62, 1.7, 0.12)),
    (4, '자의 (짙은 자색)',   (288, 0.42, 1.5, 0.08)),
    (5, '황삼 (황토빛)',      (38, 0.52, 1.7, 0.16)),
]

FIX = {   # 칸 번호: [(x0, y0, x1, y1, True = 도복으로 칠함 / False = 칠하지 않음)]
    1: [(34, 44, 47, 56, False)],    # 피격: 뒤로 늘어진 머리카락
    2: [(45, 58, 78, 66, True)],     # 쓰러짐 1: 어깨 윗단
    3: [(14, 88, 42, 111, False), (66, 64, 78, 90, True), (50, 82, 80, 90, True)],   # 쓰러짐 2: 누운 머리(얼굴 규칙이 안 맞음) · 위로 솟은 칼집
    5: [(52, 41, 78, 50, True)],     # 발도: 뒤로 뻗은 팔 소매 윗단
    12: [(86, 34, 100, 42, True)],   # 심검: 머리 위 칼자루 끝 (다른 칸처럼 칼집·자루도 도복 색)
    18: [(35, 90, 80, 111, False)],  # 무참 6: 남색 기 도는 하카마 자락
    19: [(40, 92, 60, 108, False), (66, 52, 104, 58, True)],   # 무참 7: 하카마 자락 · 앞으로 뻗은 소매 윗단
    20: [(58, 50, 86, 56, True)],    # 일섬 1: 뻗은 팔 소매 윗단
    22: [(52, 28, 72, 36, True)],    # 일섬 3: 어깨
}


def robe_mask(rgba):
    hsv = rgb2hsv(rgba[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    m = (rgba[..., 3] > 0) & (h >= 195) & (h <= 255) & (s > 0.2) & (v >= 0.07) & (v < 0.45)
    # 머리카락도 남색 기가 있어 빼야 함: 칸마다 얼굴(위쪽 절반의 가장 큰 살색 덩어리) 기준으로 머리 자리를 지움
    skin = skin_mask(rgba[..., :3], rgba[..., 3] / 255.)
    for k in range(rgba.shape[1] // CELL_W):
        sl = np.s_[:, k * CELL_W:(k + 1) * CELL_W]
        ys = np.where((rgba[sl][..., 3] > 0).any(axis=1))[0]
        if not len(ys): continue
        sk = skin[sl].copy(); sk[ys.min() + (ys.max() - ys.min()) // 2:] = False
        lb, nb = ndi.label(sk)
        if nb == 0: continue
        face = lb == np.argmax(ndi.sum(sk, lb, range(1, nb + 1))) + 1
        fy, fx = np.where(face)
        mid = fy.min() + int((fy.max() - fy.min()) * 0.6)
        m[sl][:mid] = False   # 얼굴 위쪽 60% 높이보다 위 = 머리 (팔을 들어도 소매는 그 아래)
        m[sl][:fy.max() + 1, max(0, fx.min() - 2):fx.max() + 3] = False   # 얼굴 옆 머리카락
    # 칸마다 손으로 고친 상자 (칸 안 좌표 x0, y0, x1, y1): 얼굴 높이로 든 소매는 도복으로, 남색 기 도는 하카마는 빼기
    raw = (rgba[..., 3] > 0) & (h >= 195) & (h <= 255) & (s > 0.2) & (v >= 0.07) & (v < 0.45)
    for k, boxes in FIX.items():
        for x0, y0, x1, y1, on in boxes:
            sl = np.s_[y0:y1, k * CELL_W + x0:k * CELL_W + x1]
            m[sl] = raw[sl] if on else False
    # 하카마(검정) 속 남색 기 낀 낱점은 빼기: 6픽셀 아래 덩어리 (흰 도복에서 하카마에 흰 점이 찍히지 않게)
    lb, nb = ndi.label(m)
    m &= (ndi.sum(m, lb, range(nb + 1)) >= 6)[lb]
    return m, hsv


def recolor(rgba, robe):
    m, hsv = robe_mask(rgba)
    H, S, VM, VA = robe
    hsv[..., 0] = np.where(m, H / 360, hsv[..., 0])
    hsv[..., 1] = np.where(m, S * (0.6 + 0.4 * (1 - hsv[..., 2])), hsv[..., 1])
    # 도복 가장자리(남색 아닌 픽셀에 닿은 곳)는 덜 밝힘: 밝은 도복에서도 옷 윤곽이 남게
    edge = m & ~ndi.binary_erosion(m, structure=np.ones((3, 3)))
    hsv[..., 2] = np.where(m, np.clip(hsv[..., 2] * VM + VA * (1 - 0.45 * edge), 0, 1), hsv[..., 2])
    out = rgba.copy()
    out[..., :3] = (hsv2rgb(hsv) * 255).clip(0, 255).astype(np.uint8)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--preview'); args = ap.parse_args()
    src = np.array(Image.open(SRC).convert('RGBA'))
    sheets = [(0, '기본 (남색 도복)', src)] + [(n, name, recolor(src, r)) for n, name, r in VARIANTS]
    if args.preview:
        frames = [0, 6, 5, 12, 20]   # 대기 · 걷기 · 발도 · 심검 · 일섬
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
        Image.fromarray(sh, 'RGBA').save(f'assets/sprites/merc/swordsman_{n}.webp', 'WEBP', lossless=True)
        print(f'swordsman_{n}.webp  {name}')


if __name__ == '__main__':
    main()

# 전격술사 기본 외형(volt_0.webp)에서 로브·테두리 색만 바꾼 외형 시트 만들기 (칸 구성·크기 모두 같음)
# 사용: python tools/volt_variants_build.py [--preview 경로]   → assets/sprites/merc/volt_1~5.webp (2026-11-10: 6 하늘색은 빼 달라고 함) (--preview면 비교 그림만)
# 규칙 (2026-11-10 사용자: "눈동자 흰자, 피부색 유지하고 색감 다양하게" · "로브의 노란색 번개색은 그대로"):
#   지킴 = 피부 · 눈(얼굴 피부 상자 안의 금빛 눈동자와 흰자) · 머리카락(얼굴 둘레 어두운 픽셀 = 후드 안쪽 머리·그림자)
#   로브 (어두운 무채색: 로브·바지·신발) → 로브 색 (HSV: 색상·채도를 바꾸고 명도를 올려 색이 보이게, 명암 순서는 그대로)
#   테두리 (금빛: 번개 무늬·띠·몸 둘레 정전기) → 테두리 색 (색상을 바꾸고 채도 배율, 명도 그대로)
import os, sys, argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb
from volt_build import skin_mask

SRC = 'assets/sprites/merc/volt_0.webp'
CELL_W = 108
OUTLINE_PX = 1
# (번호, 이름, 로브 (색상°, 채도, 명도 배율, 명도 더함), 테두리 (색상°, 채도 배율, 명도 배율) 또는 None = 금빛 그대로)
VARIANTS = [   # 번개 테두리는 모두 금빛 그대로 (사용자: 번개 이펙트가 노란색이라 테두리 번개색은 유지) → 로브 색만 다양하게
    (1, '남색 로브',     (224, 0.62, 1.40, 0.07), None),
    (2, '진홍 로브',     (352, 0.70, 1.35, 0.06), None),
    (3, '흰 로브',       (40, 0.05, 0.45, 0.66), None),
    (4, '보라 로브',     (272, 0.55, 1.40, 0.07), None),
    (5, '숲빛 로브',     (148, 0.50, 1.30, 0.06), None),
]


def regions(rgba):
    c = rgba[..., :3].astype(float); al = rgba[..., 3] > 0
    hsv = rgb2hsv(c / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    skin = skin_mask(c, rgba[..., 3] / 255.)
    gold = al & (h >= 28) & (h <= 68) & (s > 0.35) & (v > 0.3) & ~skin
    dark = al & (v < 0.55) & ((s < 0.4) | (v < 0.22)) & ~skin
    keep = np.zeros_like(al)
    W = rgba.shape[1] // CELL_W
    for k in range(W):   # 칸마다 얼굴: 위쪽 절반의 가장 큰 피부 덩어리
        sl = np.s_[:, k * CELL_W:(k + 1) * CELL_W]
        sk = skin[sl].copy(); a = al[sl]
        if not a.any(): continue
        ys = np.where(a.any(axis=1))[0]
        sk[ys.min() + int((ys.max() - ys.min()) * 0.5):] = False
        lb, nb = ndi.label(sk)
        if nb == 0: continue
        face = lb == (np.argmax(ndi.sum(sk, lb, range(1, nb + 1))) + 1)
        fy, fx = np.where(face)
        fh, fw = fy.max() - fy.min() + 1, fx.max() - fx.min() + 1
        box = np.zeros_like(face)
        # 눈: 얼굴 상자 안 (금빛 눈동자·흰자)
        box[fy.min():fy.max() + 1, fx.min():fx.max() + 1] = True
        eyes = box & ~sk & ((gold[sl]) | ((v[sl] > 0.85) & (s[sl] < 0.2)))
        # 머리카락: 얼굴 상자를 위로 0.7배·옆으로 0.25배 넓힌 곳의 어두운 픽셀 (후드 안쪽)
        hb = np.zeros_like(face)
        hb[max(0, fy.min() - int(fh * 0.7)):fy.max() + 1, max(0, fx.min() - int(fw * 0.25)):fx.max() + 1 + int(fw * 0.25)] = True
        hair = hb & dark[sl]
        # 후드 테두리(금빛) 바깥은 머리가 아님: 금빛 테두리로 막힌 안쪽(얼굴과 이어진 곳)만
        inner = ndi.binary_propagation(face, mask=(hb & ~gold[sl] & a))
        keep[sl] |= eyes | (hair & inner)
    # 손·얼굴의 피부 그림자(손가락 사이 등): 밝은 피부에 이어진 따뜻한 색(붉은~주황, 채도 0.18↑, 명도 0.25↑) 픽셀은 피부로 봄
    #   로브 검정은 채도 0.08·명도 0.13 안팎이라 빠짐
    warm = al & ((h <= 40) | (h >= 330)) & (s >= 0.18) & (v >= 0.25) & ~gold
    skin_all = ndi.binary_propagation(skin, mask=skin | warm)
    # 피부 윤곽선(손·얼굴·목을 두른 어두운 선)도 원래 색: 피부에서 OUTLINE_PX 안의 어두운 픽셀 (로브 색이 손 윤곽에 번지지 않게)
    keep |= (dark | warm) & ndi.binary_dilation(skin_all, structure=np.ones((3, 3)), iterations=OUTLINE_PX)
    keep |= skin_all
    # 금빛 무늬 가장자리: 무늬에 붙은 어두운 금갈색(색상 15~70°, 채도 0.25↑) 픽셀은 무늬의 일부라 원래 색 (밝은 로브에서 무늬 선이 끊기지 않게)
    trim_edge = dark & ndi.binary_dilation(gold, structure=np.ones((3, 3))) & (h >= 15) & (h <= 70) & (s >= 0.25)
    keep |= trim_edge
    return skin, gold & ~keep, dark & ~keep, keep


def recolor(rgba, robe, trim):
    out = rgba.copy().astype(float)
    skin, gold, dark, keep = regions(rgba)
    hsv = rgb2hsv(out[..., :3] / 255.)
    if robe:
        H, S, VM, VA = robe
        hsv[..., 0] = np.where(dark, H / 360, hsv[..., 0])
        hsv[..., 1] = np.where(dark, S * (0.6 + 0.4 * (1 - hsv[..., 2])), hsv[..., 1])
        # 외곽선(원래 아주 어두운 픽셀)은 밝은 로브에서도 진하게 남김: 더하는 명도를 외곽선일수록 줄임 (흰·하늘색 로브가 흐려 보이지 않게)
        line = np.clip((0.16 - hsv[..., 2]) / 0.1, 0, 1)
        # 금빛 무늬를 감싼 선(무늬 바로 옆 로브 픽셀)도 진하게: 밝은 로브에서 무늬 윤곽이 사라지지 않게
        line = np.maximum(line, ndi.binary_dilation(gold, structure=np.ones((3, 3))) * 0.85)
        hsv[..., 2] = np.where(dark, np.clip(hsv[..., 2] * VM + VA * (1 - 0.6 * line), 0, 1), hsv[..., 2])
    if trim:
        H, SM, VM = trim
        hsv[..., 0] = np.where(gold, H / 360, hsv[..., 0])
        hsv[..., 1] = np.where(gold, np.clip(hsv[..., 1] * SM, 0, 1), hsv[..., 1])
        hsv[..., 2] = np.where(gold, np.clip(hsv[..., 2] * VM, 0, 1), hsv[..., 2])
    out[..., :3] = hsv2rgb(hsv) * 255
    return out.clip(0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--preview'); args = ap.parse_args()
    src = np.array(Image.open(SRC).convert('RGBA'))
    sheets = [(0, '기본 (검은 로브·금빛 번개)', src)] + [(n, name, recolor(src, r, t)) for n, name, r, t in VARIANTS]
    if args.preview:
        frames = [0, 2, 5, 12, 17]   # 대기 · 걷기 · 기본 공격 · 썬더볼트 · 축전 상태
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
        Image.fromarray(sh, 'RGBA').save(f'assets/sprites/merc/volt_{n}.webp', 'WEBP', lossless=True)
        print(f'volt_{n}.webp  {name}')


if __name__ == '__main__':
    main()

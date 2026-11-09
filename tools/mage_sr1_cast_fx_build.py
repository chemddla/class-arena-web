# 마법사 시크릿 레어 히든 스킬 [원소 융합] 시전 이펙트 (마력 집중 마법진 3종) → assets/sprites/fx/mage_fusion_sr_cast_fx.webp
# 사용: python tools/mage_sr1_cast_fx_build.py
# 샘플 (assets/sprites/fx/samples/):
#   mage_sr1_cast_fx_black_src.png (733×206): 검은 배경판 — 이걸 씀. 맨 위 '2. 마력 집중' 글씨(y < 18)는 버림
#   mage_sr1_cast_fx_white_src.png (779×232): 같은 그림의 흰 배경판 (참고용. 빛 그림이라 검은 판만으로 충분)
# 빛 그림이라 검은 배경판을 '더하기' 그림으로 바꿈: 투명도 = 가장 밝은 채널, 색 = 원래 색 / 투명도
#   → 게임에서 'lighter'로 그리면 검은 판을 더한 것과 똑같고, 보통으로 그려도 흰 테·검은 테 없이 빛만 남음
# 칸: 0 땅 마법진 (원형 문양진) · 1 고리 두른 별빛 구체 · 2 네 갈래 별과 고리. 칸마다 그림 한가운데가 기준점, 칸 크기는 모두 같음
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SRC = 'assets/sprites/fx/samples/mage_sr1_cast_fx_black_src.png'
OUT = 'assets/sprites/fx/mage_fusion_sr_cast_fx.webp'
SCALE = 0.8   # 게임에선 지름 키의 1.3~1.9배(약 110~160px)로 그려서 원본보다 조금 줄여 받는 양을 아낌
BOXES = [(20, 18, 240, 206), (258, 18, 490, 206), (505, 10, 720, 206)]   # 샘플 좌표 (x0, y0, x1, y1)


def main():
    im = np.array(Image.open(SRC).convert('RGB')).astype(float)
    im[:18] = 0   # 제목 글씨
    pieces = []
    for x0, y0, x1, y1 in BOXES:
        c = im[y0:y1, x0:x1]
        a = c.max(axis=2) / 255
        a = np.where(a < 0.06, 0, a)   # 캡처 잡티·검은 배경의 미세한 밝기
        # 그림에서 떨어진 작은 티끌 지움
        m = a > 0
        lab, n = ndi.label(ndi.binary_dilation(m, iterations=3))
        sz = ndi.sum(m, lab, range(1, n + 1))
        a = np.where(np.isin(lab, 1 + np.where(sz >= 20)[0]), a, 0)
        col = np.where(a[..., None] > 0, c / np.maximum(a, 1e-3)[..., None], 0).clip(0, 255)
        ys, xs = np.where(a > 0)
        rgba = np.dstack([col, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255   # 투명도를 곱한 채로 줄여야 가장자리에 검은 테가 안 생김
        h, w = pm.shape[:2]
        sm = np.array(Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((round(w * SCALE), round(h * SCALE)), Image.LANCZOS)).astype(float)
        al = sm[..., 3:]
        sm[..., :3] = np.where(al > 0, sm[..., :3] * 255 / np.maximum(al, 1), 0)
        sm[..., 3:] = np.where(al < 10, 0, al)
        rgba = sm
        pieces.append(rgba)
        print(f'칸 {len(pieces) - 1}: {rgba.shape[1]}x{rgba.shape[0]}')
    cw = max(p.shape[1] for p in pieces) + 2
    ch = max(p.shape[0] for p in pieces) + 2
    sheet = np.zeros((ch, cw * len(pieces), 4), np.uint8)
    for i, p in enumerate(pieces):
        x = i * cw + (cw - p.shape[1]) // 2
        y = (ch - p.shape[0]) // 2
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p.clip(0, 255).astype(np.uint8)
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'mage_fusion_sr_cast_fx cell={cw}x{ch} count={len(pieces)}')


if __name__ == '__main__':
    main()

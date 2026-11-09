# 마법사 외형 1~5 (2026-11-09 새 기본 외형에 색만 바꿈): mage_0.webp → mage_1~5.webp, mage_fusion_cast.webp → mage_fusion_1~5.webp
# 사용: python tools/mage_variants_build.py   (기본 외형을 다시 만들었으면 tools/mage0_build.py 다음에)
# 색 조합은 tools/mage0_palette_preview.py VARIANTS 1~5 (사용자가 고름):
#   1 칠흑 (검은 로브·진홍 장식·붉은 수정) · 2 진홍 (붉은 로브·검은 장식·금발·호박 수정) · 3 에메랄드 (초록 로브·청록 장식·초록 수정)
#   4 새벽 (연하늘 로브·분홍 장식·분홍 머리) · 5 순백 (흰 로브·금빛 장식·금발)
# 피부·얼굴·윤곽은 그대로, 흰자는 흰색. 칸 구성·기준점은 기본 외형과 같음
import os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import mage0_palette_preview as PP

JOBS = [('assets/sprites/merc/mage_0.webp', 'assets/sprites/merc/mage_{}.webp', 172),
        ('assets/sprites/fx/mage_fusion_cast.webp', 'assets/sprites/fx/mage_fusion_{}.webp', 113)]


def main():
    for src, out, cw in JOBS:
        im = np.array(Image.open(src).convert('RGBA')).astype(float)
        h, s, v = PP.hsv_arrays(im)
        P = PP.parts_of(im, h, s, v, cw)
        for n in range(1, 6):
            name, spec = PP.VARIANTS[n]
            rc = PP.recolor(im, h, s, v, P, spec)
            rc[..., 3] = im[..., 3]
            Image.fromarray(rc.clip(0, 255).round().astype(np.uint8), 'RGBA').save(out.format(n), 'WEBP', lossless=True)
            print(out.format(n), name)


if __name__ == '__main__':
    main()

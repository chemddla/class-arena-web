# 성녀 외형 1~5 (2026-11-09 은발 성녀 기본 외형 healer_0의 색 변형) 만들기 — 칸 구성·크기·색상(hue)은 기본 외형과 같고 채도·명도만 바꿈
# 사용: python tools/healer_variants_build.py   (tools/healer0_build.py로 기본 외형을 다시 만들었으면 그다음에)
#   assets/sprites/merc/healer_0.webp → healer_1~5.webp (17칸)
# 규칙: 피부·눈(흰자·눈동자·속눈썹)은 그대로 (tools/healer_variants_preview.py의 keep_mask).
#   흰 수도복·베일·은발(무채색)과 금빛 장식·갈색 소매(유채색)를 따로 조절
#   13~16 (스킬별 색 이펙트 칸)의 초록·푸른·노란·흰 이펙트는 그대로 → 발동 칸(11)과 다른 픽셀 = 이펙트
# 예전 23칸 그림(HEALER_OLD_SHEET)은 예전 학생 디자인만
import sys, os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import healer_variants_preview as P

# (번호, 이름, (옷·머리 채도, 명도), (금빛 채도, 명도)) — 2026-11-09 후보 12개 중 사용자가 고른 B·C·J·G·D
VARIANTS = [
    (1, '은장 성녀', (0.3, 1.0), (0.05, 1.12)),
    (2, '흑의 금장', (1, 0.32), (1.25, 1.05)),
    (3, '푸른 은빛', (6, 1.0), (0.15, 1.0)),
    (4, '잿빛 금장', (0.2, 0.52), (1.4, 1.0)),   # 후보 G
    (5, '먹빛 은장', (0.4, 0.38), (0.05, 1.2)),  # 후보 D
]
BODY = 'assets/sprites/merc/healer_%s.webp'
CW = P.CW
FX_CELLS = range(13, 17)
RELEASE = 11


def fx_mask(im):
    out = np.zeros(im.shape[:2], bool)
    base = im[:, RELEASE * CW:(RELEASE + 1) * CW].astype(int)
    for i in FX_CELLS:
        c = im[:, i * CW:(i + 1) * CW].astype(int)
        diff = (np.abs(c[..., :3] - base[..., :3]).max(axis=2) > 20) | (np.abs(c[..., 3] - base[..., 3]) > 20) | (base[..., 3] < 200)
        out[:, i * CW:(i + 1) * CW] = diff & (c[..., 3] > 0)
    return out


def main():
    im = np.array(Image.open(BODY % 0).convert('RGBA'))
    keep = P.keep_mask(im) | fx_mask(im)
    for n, name, neu, col in VARIANTS:
        Image.fromarray(P.tone(im, keep, neu, col), 'RGBA').save(BODY % n, 'WEBP', lossless=True, method=6)
        print(f'외형 {n} {name}: 옷·머리 채도 ×{neu[0]} 명도 ×{neu[1]} · 금빛 채도 ×{col[0]} 명도 ×{col[1]}')


if __name__ == '__main__':
    main()

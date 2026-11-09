# 창병 이펙트의 청록·하늘색을 회색으로 (2026-11-09 사용자 요청: 새 기본 외형에 맞춰 청록 이펙트를 회색 계열로)
# 사용: python tools/lancer_fx_grey.py   (여러 번 돌려도 같은 결과 — 이미 회색이면 그대로)
#   창병만 쓰는 그림은 제자리에서 바꿈: lancer_thrust · lancer_pierce · lancer_javelin_fx · lancer_javelin(창 뒤 바람) · lancer_musou_fx(청록 부분만)
#   다른 직업과 같이 쓰는 그림(lancer_sweep = 성기사 휘두르기, lancer_rampage = 전사 회전베기)은 index.html이 불러올 때 회색 사본을 만들어 창병에만 씀
#   몸 시트(lancer_0)·무쌍난무 자세(lancer_musou_cast)는 tools/lancer0_build.py가 만들 때 grey()를 거침
import numpy as np
from PIL import Image

KEEP = 0.06   # 남길 채도 (0 = 완전한 회색). 아주 조금 남겨 차가운 회색으로
FILES = ['lancer_thrust', 'lancer_pierce', 'lancer_javelin_fx', 'lancer_javelin', 'lancer_musou_fx']


def teal_mask(rgba):
    # 청록·하늘·파랑 기운이 있는 픽셀 (초록이나 파랑이 빨강보다 뚜렷이 큼). 살색·갈색 창대·금빛은 빨강이 커서 빠짐
    c = rgba[..., :3].astype(int)
    return (rgba[..., 3] > 0) & (np.maximum(c[..., 1], c[..., 2]) - c[..., 0] > 6)


def grey(rgba, mask=None):
    # 밝기(사람 눈 기준)는 그대로 두고 채도만 KEEP으로 줄임
    p = rgba.copy()
    m = teal_mask(rgba) if mask is None else mask
    c = p[..., :3].astype(float)
    L = (c @ np.array([0.299, 0.587, 0.114]))[..., None]
    out = (L + (c - L) * KEEP).clip(0, 255).astype(np.uint8)
    p[..., :3] = np.where(m[..., None], out, p[..., :3])
    return p


if __name__ == '__main__':
    for f in FILES:
        path = f'assets/sprites/fx/{f}.webp'
        a = np.array(Image.open(path).convert('RGBA'))
        m = teal_mask(a)
        Image.fromarray(grey(a, m), 'RGBA').save(path, 'WEBP', lossless=True)
        print(f'{f}: {m.sum()} px 회색으로 ({m.sum() / max(1, (a[..., 3] > 0).sum()):.0%})')

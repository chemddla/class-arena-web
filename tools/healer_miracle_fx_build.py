# 성녀 히든 스킬 [기적] 이펙트 그림 색 맞춤 (2026-11-09)
#   원본: assets/sprites/fx/healer_miracle_fx.webp (진한 금색 · 마법진 · 빛기둥 · 구체 · 화살표, 게임에서는 안 씀)
#   → assets/sprites/fx/healer_miracle_fx_soft.webp : 기본 외형 — 시전 그림(healer_miracle_cast)에 붙은 연한 크림·금빛
#   → assets/sprites/fx/healer_miracle_fx_sr1.webp  : 시크릿 레어 1 (천사) — 시전 그림(healer_miracle_cast_sr1)의 민트 초록, 마법진은 연두 금빛
# 사용: python tools/healer_miracle_fx_build.py
# 방법 (pixelfx 작법: 밝기 단계만 남기고 팔레트를 바꿈): 원본 밝기를 0~1로 펴서 샘플에서 뽑은 색 단계(어두움 → 밝음)에 대응
#   샘플 이펙트는 원본보다 훨씬 밝음 (원본 L 0.3~0.8, 샘플 L 0.8~1) → 밝은 쪽으로 당김 (감마 0.7)
import numpy as np
from PIL import Image

SRC = 'assets/sprites/fx/healer_miracle_fx.webp'
# 칸 상자 (index.html HEALER_MIRACLE_FX.frames 와 같음)
BOX = {'circle': (0, 129), 'pillar': (133, 234), 'sphere': (238, 335), 'arrows': (339, 419)}
# 샘플 이펙트에서 뽑은 색 단계 (밝기 순, 맨 끝은 빛 가운데 흰빛)
RAMP_BASE = ['7a6745', 'dbbe7f', 'f4dd92', 'fdf0a7', 'fffbe0']          # 기본 외형 시전 그림의 금빛 날개·불꽃
RAMP_SR_GREEN = ['5e734b', '98dc95', 'bbefa7', 'e2fbb6', 'f6ffe8']      # 천사 회오리·마무리 반짝이
RAMP_SR_CIRCLE = ['726b4a', 'c2c794', 'e3e5a2', 'f4f3b2', 'fffde6']     # 천사 금빛 마법진
OUT = {
    'assets/sprites/fx/healer_miracle_fx_soft.webp': {k: RAMP_BASE for k in BOX},
    'assets/sprites/fx/healer_miracle_fx_sr1.webp': {'circle': RAMP_SR_CIRCLE, 'pillar': RAMP_SR_GREEN, 'sphere': RAMP_SR_GREEN, 'arrows': RAMP_SR_GREEN},
}


def ramp_color(t, ramp):
    cols = np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in ramp], float)
    pos = t * (len(cols) - 1)
    i = np.clip(np.floor(pos).astype(int), 0, len(cols) - 2)
    f = (pos - i)[..., None]
    return cols[i] * (1 - f) + cols[i + 1] * f


def main():
    src = np.array(Image.open(SRC).convert('RGBA')).astype(float)
    L = (src[..., :3] @ [0.3, 0.59, 0.11]) / 255
    t = np.clip((L - 0.22) / (0.85 - 0.22), 0, 1) ** 0.7
    for path, ramps in OUT.items():
        out = src.copy()
        for name, (x0, x1) in BOX.items():
            out[:, x0:x1, :3] = ramp_color(t[:, x0:x1], ramps[name])
        Image.fromarray(out.clip(0, 255).astype(np.uint8), 'RGBA').save(path, 'WEBP', lossless=True)
        print(path)


if __name__ == '__main__':
    main()

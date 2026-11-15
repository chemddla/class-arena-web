# 기계공 시크릿 레어 최종병기 레이저 충전·맞은 자리 그림 (보라) → assets/sprites/fx/engineer_titan_sr1_laser_fx.webp
# 사용: python tools/engineer_titan_sr1_laser_fx_build.py   (2026-11-15 사용자 요청: 로봇 샘플의 레이저 빔 색(남보라)에 맞춰 보라 계열로)
#   기본 레이저 그림(assets/sprites/fx/engineer_laser_fx.webp, tools/engineer_laser_fx_build.py)을 밝기 → 보라 사다리(RAMP)로 그대로 바꿔 칠함
#   칸 배치·기준점은 기본과 같음 (index.html ENG_LASER_FX를 그대로 씀)
import numpy as np
from PIL import Image

SRC = 'assets/sprites/fx/engineer_laser_fx.webp'
OUT = 'assets/sprites/fx/engineer_titan_sr1_laser_fx.webp'
RAMP = ['#140a33', '#2e1d78', '#4b34b8', '#6a55e6', '#8f7dff', '#b9adff', '#e2dcff', '#ffffff']   # 어두움 → 밝음 (샘플 빔 #6d78c8 근처를 보라 쪽으로)


def rgb(h):
    h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def main():
    a = np.array(Image.open(SRC).convert('RGBA')).astype(float)
    lum = (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]) / 255
    ramp = np.array([rgb(c) for c in RAMP], float)
    t = np.clip(lum, 0, 1) ** 1.6 * (len(RAMP) - 1)   # 밝은 곳도 보라가 남게 (1.6제곱: 아주 밝은 심만 흰색)
    i0 = np.floor(t).astype(int); i1 = np.minimum(i0 + 1, len(RAMP) - 1); f = (t - i0)[..., None]
    out = a.copy()
    out[..., :3] = ramp[i0] * (1 - f) + ramp[i1] * f
    Image.fromarray(out.astype(np.uint8), 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('저장', OUT, a.shape)


if __name__ == '__main__':
    main()

# 궁수 히든 스킬 [폭풍] 코드 이펙트를 기본 외형(2026-11-09 금발 궁수) 시전 그림 색에 맞춤
# 사용: python tools/archer_storm_fx_recolor.py   (시전 그림을 다시 만들었으면 tools/archer0_build.py 다음에)
#   archer_storm_wind.webp (시전 중 몸 둘레·날아가는 화살 둘레 바람 고리) → archer_storm_wind_0.webp
#   storm_arrow.webp (나선 돌풍 화살) → storm_arrow_0.webp
# 예전 그림은 청록(색조 약 155°, 밝기 가운데 0.5~0.7)이고 새 시전 그림의 바람은 연두(약 110°, 밝기 가운데 0.95)라서,
#   초록·청록·파랑 픽셀만 골라 색조를 새 그림 범위로 옮기고(차이는 0.68배로 줄임) 밝기·채도를 새 그림 분포에 맞춤.
#   금빛 조각·잎(노랑·갈색)은 새 그림에도 금빛이 있어 그대로 둠. 투명도는 그대로
# 외형 1~5·시크릿 레어는 예전 청록 시전 그림이라 예전 이펙트를 계속 씀
import colorsys
import numpy as np
from PIL import Image

CAST = 'assets/sprites/fx/archer_storm_cast_0.webp'
JOBS = [('assets/sprites/fx/archer_storm_wind.webp', 'assets/sprites/fx/archer_storm_wind_0.webp'),
        ('assets/sprites/fx/storm_arrow.webp', 'assets/sprites/fx/storm_arrow_0.webp')]


def hsv(rgb):
    flat = rgb.reshape(-1, 3)
    return np.array([colorsys.rgb_to_hsv(*p) for p in flat]).reshape(rgb.shape)


def target():
    # 새 시전 그림의 반투명 바람(초록 쪽) 색 분포
    a = np.array(Image.open(CAST).convert('RGBA')).astype(float) / 255
    m = (a[..., 3] > 0.15) & (a[..., 3] < 0.99)
    q = hsv(a[..., :3][m][None])[0]
    g = (q[:, 0] * 360 > 70) & (q[:, 0] * 360 < 170)
    return (np.median(q[g, 0]) * 360, np.median(q[g, 1]), np.percentile(q[g, 2], [10, 50, 90]))


def main():
    th, ts, tv = target()
    print(f'새 시전 그림 바람: 색조 {th:.0f}° 채도 {ts:.2f} 밝기 {tv.round(2)}')
    for src, out in JOBS:
        im = np.array(Image.open(src).convert('RGBA')).astype(float)
        q = hsv(im[..., :3] / 255)
        h, s, v = q[..., 0] * 360, q[..., 1], q[..., 2]
        sel = (im[..., 3] > 0) & (h > 95) & (h < 240) & (s > 0.12)
        hm = np.median(h[sel & (im[..., 3] > 40)])
        sm = np.median(s[sel & (im[..., 3] > 40)])
        vp = np.percentile(v[sel & (im[..., 3] > 40)], [10, 50, 90])
        nh = np.clip(th + (h - hm) * 0.68, 75, 150) / 360
        ns = np.clip(s * ts / sm, 0, 1)
        nv = np.interp(v, [0, vp[0], vp[1], vp[2], 1], [0, tv[0], min(tv[1], 0.93), 0.99, 1])
        rgb = np.array([colorsys.hsv_to_rgb(a_, b_, c_) for a_, b_, c_ in zip(nh[sel], ns[sel], nv[sel])]) * 255
        res = im.copy(); res[..., :3][sel] = rgb
        Image.fromarray(res.clip(0, 255).round().astype(np.uint8), 'RGBA').save(out, 'WEBP', lossless=True)
        print(f'{out}: 바꾼 픽셀 {sel.sum()} · 색조 {hm:.0f}°→{th:.0f}° · 밝기 {vp.round(2)} → {tv.round(2)}')


if __name__ == '__main__':
    main()

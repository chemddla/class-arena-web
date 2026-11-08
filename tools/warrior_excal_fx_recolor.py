# 엑스칼리버 이펙트 시트 색감을 외형 시전 모션에 맞춤 (밝기 → 색띠, pixelfx처럼 어두울수록 색이 짙어지는 단계 색띠)
#  - 기본 외형(은빛 갑옷, 시전 때 하늘색 불꽃) → assets/sprites/fx/warrior_excalibur_fx.webp 를 남색·하늘색·흰빛으로
#  - 시크릿 레어(금빛 갑옷·붉은 망토, 시전 때 붉은 불꽃) → assets/sprites/fx/warrior_excalibur_sr_fx.webp 의 고리·베기·검기·폭발을 진홍·주황·금빛으로
# 쓰는 법: python tools/warrior_excal_fx_recolor.py <기본 원본.webp> <시크릿 원본.webp>
#  (원본 = 다시 칠하기 전 그림. 예: git show 92d637f:assets/sprites/fx/warrior_excalibur_fx.webp > base_src.webp)
import sys
from PIL import Image

BASE_OUT = 'assets/sprites/fx/warrior_excalibur_fx.webp'
SR_OUT = 'assets/sprites/fx/warrior_excalibur_sr_fx.webp'

# 밝기 0 → 1 순서
BASE_RAMP = ['#0c1f4f', '#123f8f', '#1f6fd1', '#29a3ec', '#56d4f5', '#a5f0fb', '#e3fcff', '#ffffff']
SR_RAMP = ['#3a0610', '#7a0d16', '#b8141c', '#e0361c', '#f6731d', '#fbb33a', '#fde58a', '#fffbe6']

# 시크릿 시트에서 다시 칠할 칸 (x 시작, x 끝). 바닥 고리 먼지·꽂힌 검은 지금 안 써서 그대로 둠
SR_RANGES = [(0, 897)]


def hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def ramp_at(ramp, t):
    t = max(0.0, min(1.0, t)) * (len(ramp) - 1)
    i = min(int(t), len(ramp) - 2)
    f = t - i
    a, b = hex2rgb(ramp[i]), hex2rgb(ramp[i + 1])
    # 단계 사이를 아주 조금만 섞어 도트 색띠 느낌은 살리고 계단 줄무늬는 막음
    f = 0.0 if f < 0.35 else (1.0 if f > 0.65 else (f - 0.35) / 0.3)
    return tuple(round(a[k] + (b[k] - a[k]) * f) for k in range(3))


def recolor(img, ramp, ranges=None):
    img = img.convert('RGBA')
    px = img.load()
    W, H = img.size
    for x in range(W):
        if ranges and not any(a <= x <= b for a, b in ranges):
            continue
        for y in range(H):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            mn = min(r, g, b) / 255
            lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
            # 흰빛(세 색 모두 밝음)만 색띠 맨 끝, 금빛·주황처럼 밝아도 색이 진한 곳은 가운데로 → 하얗게 날아가지 않음
            t = (0.45 * lum + 0.55 * mn) ** 0.85
            nr, ng, nb = ramp_at(ramp, t)
            px[x, y] = (nr, ng, nb, a)
    return img


if __name__ == '__main__':
    base_src, sr_src = sys.argv[1], sys.argv[2]
    recolor(Image.open(base_src), BASE_RAMP).save(BASE_OUT, 'WEBP', lossless=True)
    recolor(Image.open(sr_src), SR_RAMP, SR_RANGES).save(SR_OUT, 'WEBP', lossless=True)
    print('ok')

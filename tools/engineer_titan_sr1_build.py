# 기계공 시크릿 레어 1 전용 '최종병기' (두 다리로 선 검은 강철 거대 로봇: 어깨 위 장포신 · 가슴 레이저 · 오른팔 개틀링) → 동작 칸 띠
# 사용: python tools/engineer_titan_sr1_build.py   (출력한 값을 index.html ENG_TITAN_SR_SHEET에 옮겨 적음)
#
# 샘플 assets/sprites/fx/samples/engineer_titan_sr1_src.png (1024×572, 흰 배경): 세 무기를 한꺼번에 쏘는 한 장
#   날아가는 포탄·레이저 빔·탄피·총알 꼬리·총구 불티는 게임이 따로 그리니까 지움 (빔은 포신 끝 오른쪽을 흰색으로 덮고, 나머지는 몸에서 떨어진 조각이라 몸 덩어리만 남김)
# 칸 순서는 기본 최종병기(ENG_TITAN_SHEET)와 같음: 0 평소 · 1 기관총 사격 · 2 박격포 발사 · 3 과열·폭주 · 4 내부 폭발 · 5 자폭 폭발 · 6 잔해
#   샘플이 한 장뿐이라 1·2는 평소와 같은 그림 (총알·포탄·빔이 나가는 것은 게임이 그림)
#   3 = 붉게 달아오름, 4 = 주황·흰빛으로 번쩍임, 5 = 거의 하얗게 타오름 (위에 핵폭발이 덮임), 6 = 검게 그을린 잔해 (낮게 주저앉음)
#   (자폭·잔해 전용 샘플이 오면 바꿀 것)
# 크기: 몸 키(포신 위~발끝)를 기본 최종병기와 같은 H(px)로. 그림은 RES배 크게 만들고 게임이 줄여 그림
# 기준점: 발끝 바닥 가운데. 그림은 무기가 오른쪽 = 오른쪽을 봄 (기본 최종병기와 반대 → index.html에서 faceR)
# 총구 3곳 (기준점 기준 게임 px, 그림이 오른쪽을 볼 때): 개틀링 끝(gun) · 장포신 끝(mortar) · 레이저 포신 끝(laser)
import os, sys, json
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
from engineer_turret_build import cut
from engineer_build import defringe
from engineer_titan_build import legs, H, RES

SRC = 'assets/sprites/fx/samples/engineer_titan_sr1_src.png'
OUT = 'assets/sprites/fx/engineer_titan_sr1.webp'
ERASE = [(672, 1024, 183, 222)]   # 레이저 빔 (포신 끝 x 672부터 오른쪽)
# 총구 (샘플 좌표): 미리보기로 잼
MUZZLE = {'gun': (778, 316), 'mortar': (745, 46), 'laser': (668, 202)}


def tint(s, mul, add=(0, 0, 0)):
    out = s.astype(float).copy()
    out[..., :3] = np.clip(out[..., :3] * np.array(mul) + np.array(add), 0, 255)
    return out.astype(np.uint8)


def main():
    src = np.array(Image.open(SRC).convert('RGBA')).astype(float)
    im, body = cut(src, (0, src.shape[1], 0, src.shape[0]), ERASE)
    im[..., 3] = np.where(body, im[..., 3], 0)   # 몸 덩어리만 (탄피·포탄·불티 지움)
    cx, w, by = legs(body)
    ys = np.where(body.any(axis=1))[0]
    sc = H * RES / (by - ys.min())
    s = defringe(shrink(im, sc), passes=4 * RES, light=200, outline=110, near=4 * RES)
    ys, xs = np.where(s[..., 3] > 0)
    x0, y0 = xs.min(), ys.min()
    s = s[y0:ys.max() + 1, x0:xs.max() + 1]
    ax, ay = cx * sc - x0, by * sc - y0   # 기준점 (칸 안 px)
    a = s[..., 3:] > 0
    g = s[..., :3].mean(axis=2, keepdims=True)
    gray = np.concatenate([g, g, g, s[..., 3:]], axis=2).astype(np.uint8)
    frames = [s, s, s,
              tint(s, (1.25, 0.55, 0.5), (60, 0, 0)),          # 3 과열: 붉게
              tint(s, (1.2, 0.95, 0.6), (90, 50, 0)),          # 4 내부 폭발: 주황 번쩍임
              tint(s, (0.5, 0.45, 0.35), (200, 170, 120)),     # 5 자폭 폭발: 하얗게 타오름
              None]
    # 6 잔해: 검게 그을리고 키 70%로 주저앉음 (발끝은 그대로)
    wreck = tint(gray, (0.45, 0.42, 0.42), (8, 5, 3))
    wh = int(round(wreck.shape[0] * 0.7))
    wreck = np.array(Image.fromarray(wreck, 'RGBA').resize((wreck.shape[1], wh), Image.LANCZOS))
    pad = np.zeros_like(s); pad[-wh:] = wreck
    frames[6] = pad
    for f in frames:
        f[..., 3] = np.where(a[..., 0], f[..., 3], 0) if f is not pad else f[..., 3]
    ch, cw = s.shape[0] + 2, s.shape[1] + 2
    strip = np.zeros((ch, cw * len(frames), 4), np.uint8)
    for i, f in enumerate(frames):
        strip[1:1 + f.shape[0], i * cw + 1:i * cw + 1 + f.shape[1]] = f
    Image.fromarray(strip, 'RGBA').save(OUT, 'WEBP', lossless=True)
    AX, AY = ax + 1, ay + 1
    mz = {k: [round((x - cx) * sc / RES, 1), round((y - by) * sc / RES, 1)] for k, (x, y) in MUZZLE.items()}
    print(json.dumps({'cw': cw, 'ch': ch, 'res': RES, 'ax': round(AX / RES, 2), 'ay': round(AY / RES, 2), 'n': len(frames), 'h': H, **mz}))


if __name__ == '__main__':
    main()

# 기계공 시크릿 레어 1 전용 '최종병기' (두 다리로 선 검은 강철 거대 로봇: 어깨 위 장포신 · 가슴 레이저 · 오른팔 개틀링) → 동작 칸 띠
# 사용: python tools/engineer_titan_sr1_build.py   (출력한 값을 index.html ENG_TITAN_SR_SHEET에 옮겨 적음)
#
# 샘플 assets/sprites/fx/samples/engineer_titan_sr1_src.png (1024×572, 흰 배경): 세 무기를 한꺼번에 쏘는 한 장
#   날아가는 포탄·레이저 빔·탄피·총알 꼬리·총구 불티는 게임이 따로 그리니까 지움 (빔은 포신 끝 오른쪽을 흰색으로 덮고, 나머지는 몸에서 떨어진 조각이라 몸 덩어리만 남김)
# 자폭 샘플 assets/sprites/fx/samples/engineer_titan_sr1_death_src.png (1024×572, 3×2 칸, 흰 배경):
#   전기 불꽃·연기 (과열) → 붉게 달아올라 빛이 터져 나옴 → 몸이 터지며 팔이 떨어져 나감 → 큰 불덩이 → 검은 연기·파편 → 연기 기둥 아래 잔해 더미
# 칸 순서: 0 평소 · 1 기관총 사격 · 2 박격포 발사 (1·2는 평소와 같은 그림: 총알·포탄·빔은 게임이 그림)
#   · 3 과열 · 4 내부 폭발 (자폭 준비 앞·뒤 절반, 기본 최종병기와 같은 번호) · 5~8 터짐 → 불덩이 → 연기·파편 → 잔해 (eng_wreck이 차례로)
#   자폭 칸은 칸마다 연기·파편 조각도 남김. 크기는 다리 끝 폭을 평소 그림과 같게 (샘플마다 로봇 크기가 달라서), 기준점 = 그 칸의 다리 끝 바닥 가운데
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
DEATH = 'assets/sprites/fx/samples/engineer_titan_sr1_death_src.png'
PANELS = [(0, 310, 0, 281), (310, 652, 0, 281), (652, 1024, 0, 281), (0, 362, 281, 572), (362, 700, 281, 572), (700, 1024, 281, 572)]   # x0, x1, y0, y1 (칸 사이 빈 줄)
MUZZLE = {'gun': (778, 316), 'mortar': (745, 46), 'laser': (668, 202)}


def main():
    src = np.array(Image.open(SRC).convert('RGBA')).astype(float)
    im, body = cut(src, (0, src.shape[1], 0, src.shape[0]), ERASE)
    im[..., 3] = np.where(body, im[..., 3], 0)   # 몸 덩어리만 (탄피·포탄·불티 지움)
    cx, legw, by = legs(body)
    ys = np.where(body.any(axis=1))[0]
    sc = H * RES / (by - ys.min())
    placed = []   # (그림, 기준점 x, 기준점 y) — 칸 안 px
    def place(rgba, sc_, cx_, by_):
        t = defringe(shrink(rgba, sc_), passes=4 * RES, light=200, outline=110, near=4 * RES)
        yy, xx = np.where(t[..., 3] > 0)
        x0, y0 = xx.min(), yy.min()
        placed.append((t[y0:yy.max() + 1, x0:xx.max() + 1], cx_ * sc_ - x0, by_ * sc_ - y0))
    for _ in range(3):
        place(im, sc, cx, by)
    dsrc = np.array(Image.open(DEATH).convert('RGBA')).astype(float)
    sc_d = None
    for box in PANELS:
        dim, dbody = cut(dsrc, box, [])   # 연기·파편 조각도 남김 (cut은 12px 넘는 조각을 모두 남김)
        dcx, dw, dby = legs(dbody)
        if sc_d is None:   # 첫 칸(과열, 로봇이 온전함)의 다리 끝 폭을 평소 그림과 같게
            sc_d = sc * legw / dw
        place(dim, sc_d, dcx, dby)
    L = max(ax for t, ax, ay in placed); R = max(t.shape[1] - ax for t, ax, ay in placed)
    T = max(ay for t, ax, ay in placed); B = max(t.shape[0] - ay for t, ax, ay in placed)
    cw, ch, AX, AY = int(np.ceil(L + R)) + 2, int(np.ceil(T + B)) + 2, int(np.ceil(L)) + 1, int(np.ceil(T)) + 1
    strip = np.zeros((ch, cw * len(placed), 4), np.uint8)
    for i, (t, ax, ay) in enumerate(placed):
        x = i * cw + AX - int(round(ax)); y = AY - int(round(ay))
        h, w = t.shape[:2]
        strip[y:y + h, x:x + w] = t
    Image.fromarray(strip, 'RGBA').save(OUT, 'WEBP', lossless=True)
    mz = {k: [round((x - cx) * sc / RES, 1), round((y - by) * sc / RES, 1)] for k, (x, y) in MUZZLE.items()}
    print(json.dumps({'cw': cw, 'ch': ch, 'res': RES, 'ax': round(AX / RES, 2), 'ay': round(AY / RES, 2), 'n': len(placed), 'h': H, **mz}), 'death sc', round(sc_d, 3))


if __name__ == '__main__':
    main()

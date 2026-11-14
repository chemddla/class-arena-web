# 기계공 시크릿 레어 1 전용 '최종병기' (두 다리로 선 검은 강철 거대 로봇: 어깨 위 장포신 · 가슴 레이저 · 오른팔 개틀링) → 동작 칸 띠
# 사용: python tools/engineer_titan_sr1_build.py   (출력한 값을 index.html ENG_TITAN_SR_SHEET에 옮겨 적음)
#
# 샘플 assets/sprites/fx/samples/engineer_titan_sr1_src.png (1024×572, 흰 배경): 세 무기를 한꺼번에 쏘는 한 장
#   날아가는 포탄·레이저 빔·탄피·총알 꼬리·총구 불티는 게임이 따로 그리니까 지움 (빔은 포신 끝 오른쪽을 흰색으로 덮고, 나머지는 몸에서 떨어진 조각이라 몸 덩어리만 남김)
# 자폭 샘플 assets/sprites/fx/samples/engineer_titan_sr1_death_src.png (1024×572, 3×2 칸, 흰 배경):
#   전기 불꽃·연기 (과열) → 붉게 달아올라 빛이 터져 나옴 → 몸이 터지며 팔이 떨어져 나감 → 큰 불덩이 → 검은 연기·파편 → 연기 기둥 아래 잔해 더미
# 칸 순서: 0 평소 · 1 기관총 사격 · 2 박격포 발사 (1·2는 평소와 같은 그림: 총알·포탄·빔은 게임이 그림)
#   · 3 과열 · 4 내부 폭발 (자폭 준비 앞·뒤 절반, 기본 최종병기와 같은 번호) · 5~8 터짐 → 불덩이 → 연기·파편 → 잔해 (eng_wreck이 차례로)
#   · 9~14 등장 착지 (assets/sprites/fx/samples/engineer_titan_sr1_land_src.png, 3×2): 파란 분사로 내려옴 → 주황 분사·먼지 닿음 → 먼지 터짐
#     → 땅이 갈라지며 웅크림 → 일어섬 → 연기 속에 섬 (다음은 평소 칸). 무기 없는 그림이라 착지 동안은 쏘지 않음 (index.html engTitanLanding)
#     크기는 로봇(어두운 강철) 키를 자폭 첫 칸 로봇 키와 같게, 가로는 로봇 가운데, 세로는 칸의 땅 줄
#   · 15~16 기관총 진동 (GUN_BOX를 GUN_SHAKE만큼 옮긴 평소 칸)
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
LAND = 'assets/sprites/fx/samples/engineer_titan_sr1_land_src.png'
LAND_PANELS = [(0, 285, 0, 300), (285, 630, 0, 300), (630, 1024, 0, 300), (0, 356, 300, 572), (356, 683, 300, 572), (683, 1024, 300, 572)]
LAND_GROUND = [None, 276, 276, 272, 260, 261]   # 칸 안 땅 줄 (첫 칸은 공중이라 로봇 발끝을 땅으로: 게임이 높이를 따로 올림)
# 15·16 기관총 진동: 평소 칸에서 개틀링 총열(칸 안 상자 x0, x1, y0, y1)만 뒤로 밀고 위아래로 흔든 두 칸 — 쏘는 동안 번갈아 (2026-11-14 사용자 요청)
GUN_BOX = (410, 535, 196, 252)
GUN_SHAKE = [(-6, 0), (-3, 3)]   # (가로, 세로) 그림 px (res배)
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
    def steel(rgba):   # 로봇 몸 (어두운 강철, 먼지·불꽃·연기는 밝아서 빠짐) → 가장 큰 덩어리 상자
        from scipy import ndimage as ndi
        c = rgba[..., :3]
        m = (rgba[..., 3] > 0) & (c.max(axis=2) < 110)
        lab, n = ndi.label(m, structure=np.ones((3, 3)))
        sz = ndi.sum(m, lab, range(1, n + 1))
        yy, xx = np.where(lab == 1 + int(np.argmax(sz)))
        return xx.min(), xx.max(), yy.min(), yy.max()
    d0, _ = cut(dsrc, PANELS[0], [])
    _, _, dy0, dy1 = steel(d0)
    lsrc = np.array(Image.open(LAND).convert('RGBA')).astype(float)
    lims = [cut(lsrc, box, [])[0] for box in LAND_PANELS]
    st = [steel(li) for li in lims]
    sc_l = sc_d * (dy1 - dy0) / np.mean([b[3] - b[2] for b in st[4:]])   # 마지막 두 칸(곧게 섬)의 키로
    for li, (x0_, x1_, y0_, y1_), g in zip(lims, st, LAND_GROUND):
        place(li, sc_l, (x0_ + x1_) / 2, y1_ if g is None else g)
    L = max(ax for t, ax, ay in placed); R = max(t.shape[1] - ax for t, ax, ay in placed)
    T = max(ay for t, ax, ay in placed); B = max(t.shape[0] - ay for t, ax, ay in placed)
    cw, ch, AX, AY = int(np.ceil(L + R)) + 2, int(np.ceil(T + B)) + 2, int(np.ceil(L)) + 1, int(np.ceil(T)) + 1
    n = len(placed) + len(GUN_SHAKE)
    strip = np.zeros((ch, cw * n, 4), np.uint8)
    for i, (t, ax, ay) in enumerate(placed):
        x = i * cw + AX - int(round(ax)); y = AY - int(round(ay))
        h, w = t.shape[:2]
        strip[y:y + h, x:x + w] = t
    gx0, gx1, gy0, gy1 = GUN_BOX
    for j, (dx, dy) in enumerate(GUN_SHAKE):
        c0 = (len(placed) + j) * cw
        cell = strip[:, :cw].copy()
        barrel = cell[gy0:gy1, gx0:gx1].copy()
        cell[gy0:gy1, gx0:gx1] = 0
        y0, x0 = gy0 + dy, gx0 + dx
        reg = cell[y0:y0 + barrel.shape[0], x0:x0 + barrel.shape[1]]
        cell[y0:y0 + barrel.shape[0], x0:x0 + barrel.shape[1]] = np.where(barrel[..., 3:] > 0, barrel, reg)
        strip[:, c0:c0 + cw] = cell
    Image.fromarray(strip, 'RGBA').save(OUT, 'WEBP', lossless=True)
    mz = {k: [round((x - cx) * sc / RES, 1), round((y - by) * sc / RES, 1)] for k, (x, y) in MUZZLE.items()}
    print(json.dumps({'cw': cw, 'ch': ch, 'res': RES, 'ax': round(AX / RES, 2), 'ay': round(AY / RES, 2), 'n': n, 'h': H, **mz}), 'death sc', round(sc_d, 3), 'land sc', round(sc_l, 3))


if __name__ == '__main__':
    main()

# 기계공 히든 '최종병기' (다리 넷 달린 로봇 포탑: 왼쪽 기관총 · 위 박격포 · 오른쪽 레이저) → 동작 칸 띠
# 사용: python tools/engineer_titan_build.py   (출력한 값을 index.html ENG_TITAN_SHEET에 옮겨 적음)
#
# 샘플 (assets/sprites/fx/samples/engineer_titan_*_src.png, 모두 흰 배경 + 아래 설명 글자)
#   titan       : 평소 (1024×572)
#   titan_gun   : 기관총 사격 (왼쪽 끝 2px 검은 테두리 → 잘라 냄)
#   titan_mortar: 박격포 발사 (왼쪽 위로 날아가는 포탄은 지움: 포탄은 게임이 따로 그림)
#   titan_death : 2×2 칸 = 과열·폭주 / 내부 폭발 / 자폭 폭발 / 잔해 (칸마다 아래 글자)
#   titan_laser : 레이저 조사. 빔이 앞쪽(기관총 쪽)으로 몸을 가로질러 그려져 있어 칸으로는 안 씀
#                 → 레이저는 앞쪽으로 쏜다는 것만 따르고, 빔·렌즈 빛은 게임이 각도대로 그림
#
# 칸 순서: 0 평소 · 1 기관총 사격 · 2 박격포 발사 · 3 과열·폭주 · 4 내부 폭발 · 5 자폭 폭발 · 6 잔해
# 크기: 평소 그림의 몸 키(박격포 끝~다리 끝)를 H(px)로. 최종병기 크기 배율(2.2)일 때 그대로 그리게 키워 둠 (작게 줄였다 키우면 흐려짐)
#   다른 샘플은 레이저 렌즈(오른쪽 큰 청록 동그라미) 키가 평소와 같아지도록 줄이고, 렌즈 가운데를 평소 칸의 렌즈 자리에 맞춤
#   (다리 폭으로 맞추면 발밑 흙먼지·불꽃이 섞여 어긋남). 자폭 4칸은 한 장이라 첫 칸의 배율·위치를 같이 씀 (잔해 칸엔 렌즈가 없음)
# 기준점: 다리 끝 바닥 가운데. 그림은 기관총이 왼쪽 = 왼쪽을 봄 → 게임이 겨눈 쪽으로 좌우를 뒤집음
# 총구 3곳 (평소 칸, 기준점 기준 px): 기관총 끝(gun) · 박격포 입구(mortar) · 레이저 렌즈 가운데(laser)
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
from engineer_turret_build import cut, bbox
from engineer_build import defringe   # 테두리 흰 찌꺼기 정리 (포탑 외곽선은 짙은 갈색이라 outline=110, 흰 연기를 살리려고 외곽선 4px 안의 밝은 테두리만: near=4)

S = 'assets/sprites/fx/samples/engineer_'
OUT = 'assets/sprites/fx/engineer_titan.webp'
H = 116
MORTAR_FIX = [-11, -106]   # 박격포 입구 (기준점 기준 px, 미리보기로 잼: 맨 위 줄은 크레인 끝)
# (샘플, 자를 상자 x0,x1,y0,y1, 지울 상자들, 묶음) — 같은 묶음은 첫 칸의 배율·기준점 위치를 같이 씀
FRAMES = [
    ('titan', (0, 1024, 0, 548), [], 'idle'),
    ('titan_gun', (3, 572, 0, 356), [], 'gun'),
    ('titan_mortar', (0, 552, 14, 392), [(80, 140, 0, 60)], 'mortar'),
    ('titan_death', (0, 512, 0, 345), [], 'death'),
    ('titan_death', (512, 1024, 0, 345), [], 'death'),
    ('titan_death', (0, 512, 380, 732), [], 'death'),
    ('titan_death', (512, 1024, 380, 732), [], 'death'),
]


def legs(a):   # 다리 끝 줄들의 좌우 끝 → (가운데 x, 폭, 바닥 y)
    ys = np.where(a.any(axis=1))[0]
    y1 = ys.max() + 1
    rows = a[y1 - max(3, (y1 - ys.min()) // 16): y1]
    xs = np.where(rows.any(axis=0))[0]
    return (xs.min() + xs.max() + 1) / 2, xs.max() - xs.min() + 1, y1


def lens(im, a):   # 오른쪽 절반의 가장 큰 청록 덩어리 → (가운데 x, 가운데 y, 키)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    teal = (G > 120) & (B > 110) & (G - R > 50) & a
    teal[:, :a.shape[1] // 2] = False
    lab, n = ndi.label(teal)
    sizes = ndi.sum(teal, lab, range(1, n + 1))
    m = lab == 1 + int(np.argmax(sizes))
    ys, xs = np.where(m)
    return xs.mean(), ys.mean(), ys.max() - ys.min() + 1


def main():
    srcs, group = {}, {}
    placed = []
    sc_idle = None
    for name, box, er, grp in FRAMES:
        if name not in srcs:
            srcs[name] = np.array(Image.open(S + name + '_src.png').convert('RGBA')).astype(float)
        im, body = cut(srcs[name], box, er)
        a = im[..., 3] > 0
        if grp not in group:
            lx, ly, ld = lens(im, a)
            if sc_idle is None:   # 평소 칸: 다리 끝 바닥 가운데가 기준점, 몸 키로 배율
                cx, w, by = legs(body)
                ys = np.where(a.any(axis=1))[0]
                sc_idle = H / (by - ys.min()); sc = sc_idle
                lens_rel = ((lx - cx) * sc, (ly - by) * sc); ld_idle = ld * sc
            else:                 # 렌즈 키로 배율, 렌즈 가운데에서 기준점을 거꾸로 셈
                sc = ld_idle / ld
                cx, by = lx - lens_rel[0] / sc, ly - lens_rel[1] / sc
            group[grp] = (sc, cx, by)
        sc, cx, by = group[grp]
        s = defringe(shrink(im, sc), passes=4, light=200, outline=110, near=4)
        placed.append((s, cx * sc, by * sc))
        if grp == 'idle':
            idle_im, idle_a = im, a
    L = max(ax for s, ax, ay in placed); R = max(s.shape[1] - ax for s, ax, ay in placed)
    T = max(ay for s, ax, ay in placed); B = max(s.shape[0] - ay for s, ax, ay in placed)
    cw, ch, AX, AY = int(np.ceil(L + R)) + 2, int(np.ceil(T + B)) + 2, int(np.ceil(L)) + 1, int(np.ceil(T)) + 1
    strip = np.zeros((ch, cw * len(placed), 4), np.uint8)
    for i, (s, ax, ay) in enumerate(placed):
        x = i * cw + AX - int(round(ax)); y = AY - int(round(ay))
        h, w = s.shape[:2]
        reg = strip[y:y + h, x:x + w]
        strip[y:y + h, x:x + w] = np.where(s[..., 3:] > 0, s, reg)
    Image.fromarray(strip, 'RGBA').save(OUT, 'WEBP', lossless=True)
    # 평소 칸 총구 (기준점 기준)
    sc, cx, by = group['idle']
    ys = np.where(idle_a[:, :6].any(axis=1))[0]; xs0 = np.where(idle_a.any(axis=0))[0].min()
    ys = np.where(idle_a[:, xs0:xs0 + 6].any(axis=1))[0]
    gun = [round((xs0 - cx) * sc, 1), round((ys.mean() - by) * sc, 1)]
    R_, G_, B_ = idle_im[..., 0], idle_im[..., 1], idle_im[..., 2]
    teal = (G_ > 120) & (B_ > 110) & (G_ - R_ > 50) & idle_a
    teal[:, :idle_a.shape[1] // 2] = False
    lab, n = ndi.label(teal)
    sizes = ndi.sum(teal, lab, range(1, n + 1))
    ly, lx = ndi.center_of_mass(teal, lab, 1 + int(np.argmax(sizes)))
    laser = [round((lx - cx) * sc, 1), round((ly - by) * sc, 1)]
    print(json.dumps({'cw': cw, 'ch': ch, 'ax': AX, 'ay': AY, 'n': len(placed), 'gun': gun, 'mortar': MORTAR_FIX, 'laser': laser}))


if __name__ == '__main__':
    main()

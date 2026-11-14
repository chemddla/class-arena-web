# 기계공 히든 '최종병기' 샘플(다리 넷 달린 로봇 포탑: 왼쪽 기관총 · 위 박격포 · 오른쪽 레이저, 흰 배경, 아래 설명 글자) → 그림 한 장
# 사용: python tools/engineer_titan_build.py   (출력한 값을 index.html ENG_TITAN_SHEET에 옮겨 적음)
# - 아래 설명 글자 줄(553~)은 잘라 냄, 흰 배경 지우기는 engineer_turret_build.cut 그대로
# - 크기: 몸 키(박격포 끝~다리 끝)를 H(px)로. 최종병기 크기 배율(ENG_TURRET_DEFS.titan.size 2.2)일 때 그대로 그리게 키워 둠 (작게 줄였다 크게 키우면 흐려짐)
# - 기준점: 다리 끝 바닥 가운데. 그림은 기관총이 왼쪽 = 왼쪽을 봄 → 게임이 겨눈 쪽으로 좌우를 뒤집음
# - 총구 3곳 (기준점 기준 px): 기관총 끝(gun) · 박격포 입구(mortar) · 레이저 렌즈 가운데(laser)
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
from engineer_turret_build import cut, bbox

SRC = 'assets/sprites/fx/samples/engineer_titan_src.png'
OUT = 'assets/sprites/fx/engineer_titan.webp'
H = 116
MORTAR_FIX = [-11, -106]   # 박격포 입구 (기준점 기준 px, 미리보기로 잼: 맨 위 줄은 크레인 끝)


def main():
    rgba = np.array(Image.open(SRC).convert('RGBA')).astype(float)
    im, body = cut(rgba, (0, 1024, 0, 548), [])
    a = im[..., 3] > 0
    x0, x1, y0, y1 = bbox(a)
    im = im[y0:y1, x0:x1]; a = a[y0:y1, x0:x1]
    sc = H / (y1 - y0)
    # 기준점: 다리 끝 바닥 가운데 (아래 6% 줄의 좌우 끝 가운데)
    rows = a[-max(3, a.shape[0] // 16):]
    xs = np.where(rows.any(axis=0))[0]
    ax, ay = (xs.min() + xs.max() + 1) / 2, a.shape[0]
    # 기관총 끝: 그림 맨 왼쪽 열의 가운데
    ys = np.where(a[:, :6].any(axis=1))[0]
    gun = (0, ys.mean())
    # 박격포 입구: 맨 위 줄 덩어리의 가운데
    xs = np.where(a[:8].any(axis=0))[0]
    mortar = (xs.mean(), 4)   # (맨 위는 크레인 끝이라 실제 입구는 아래에서 직접 적음: MORTAR_FIX)
    # 레이저 렌즈: 오른쪽 절반의 가장 큰 청록 덩어리 가운데
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    teal = (G > 120) & (B > 110) & (G - R > 50) & a
    teal[:, :a.shape[1] // 2] = False
    lab, n = ndi.label(teal)
    sizes = ndi.sum(teal, lab, range(1, n + 1))
    cy, cx = ndi.center_of_mass(teal, lab, 1 + int(np.argmax(sizes)))
    laser = (cx, cy)
    out = shrink(im, sc)
    Image.fromarray(out, 'RGBA').save(OUT, 'WEBP', lossless=True)
    rel = lambda p: [round((p[0] - ax) * sc, 1), round((p[1] - ay) * sc, 1)]
    print(json.dumps({'w': out.shape[1], 'h': out.shape[0], 'ax': round(ax * sc, 1), 'ay': out.shape[0],
                      'gun': rel(gun), 'mortar': MORTAR_FIX, 'laser': rel(laser)}))


if __name__ == '__main__':
    main()

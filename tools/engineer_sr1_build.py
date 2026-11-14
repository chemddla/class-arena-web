# 기계공 시크릿 레어 1 (흰 가운·검은 뿔테 안경·남색 넥타이·갈색 바지, 손에 푸른 홀로그램 판, 흰 배경) → assets/sprites/merc/engineer_sr1.webp
# 사용: python tools/engineer_sr1_build.py   (샘플 assets/sprites/fx/samples/engineer_sr1_*_src.png, 배경 따기·찌꺼기 깎기는 engineer_build 그대로)
# 칸 순서는 기본 외형(engineer_0)과 같게 맞출 것: 0 대기 · 1~4 걷기 · 5~6 리벳총 (겨눔 → 쏨) · 7~8 수리 · 9 설치 · 10 피격 · 11~12 쓰러짐
#   2026-11-14 대기·걷기 샘플을 받음 → 아직 게임에는 연결하지 않음 (SECRET_MERC_SKINS에 engineer 없음)
#   걷기는 샘플 한 장에 다섯 칸(왼쪽부터, 오른쪽 끝 잘린 여섯째 조각은 버림) → 0번(네 칸)과 달리 1~5 걷기라 연결할 때 anims를 따로 적을 것
#   동작 샘플이 오는 대로 FRAMES에 늘리고, 13칸이 다 차면 index.html SECRET_MERC_SKINS에 engineer: [1]을 넣음
# 크기: 대기 키(머리털 끝~발)를 기본 외형 대기와 같은 98px로. 걷기는 머리 너비(head_w)를 대기 칸과 같게 (보폭 때문에 키는 조금 작아짐)
# 위치: 발은 바닥선(anchorY), 가로는 머리 가운데를 대기 칸 머리 가운데에 (head_cx)
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import engineer_build as eb
from berserker_build import shrink

eb.D = 'assets/sprites/fx/samples/engineer_sr1_'
OUT = 'assets/sprites/merc/engineer_sr1.webp'
FRAMES = ['idle', 'walk1', 'walk2', 'walk3', 'walk4', 'walk5']
# 한 장에 여러 칸인 샘플: 칸 이름 → (샘플 이름, 가로 x0, x1) — 인물 사이 빈 세로줄에서 자름
CROP = {f'walk{i + 1}': ('walk', x0, x1) for i, (x0, x1) in enumerate([(0, 209), (209, 390), (390, 570), (570, 742), (742, 920)])}
CELL_W, CELL_H, ANCHOR_X, ANCHOR_Y = eb.CELL_W, eb.CELL_H, eb.ANCHOR_X, eb.ANCHOR_Y
TARGET_H = eb.TARGET_H


def load(f):
    if f not in CROP:
        return eb.load(f)
    src, x0, x1 = CROP[f]
    tmp = f'{eb.D}_crop_src.png'
    im = Image.open(f'{eb.D}{src}_src.png').convert('RGB')
    im.crop((x0, 0, x1, im.height)).save(tmp)
    try:
        return eb.load('_crop')
    finally:
        os.remove(tmp)


def head_w(rgba):   # 머리 너비: 몸 키의 2~10% 줄에서 가장 넓은 폭 (걸을 때 다리 폭이 키를 줄여도 머리는 그대로)
    a = rgba[..., 3] > 0
    h = a.shape[0]
    return max(np.ptp(np.where(a[y])[0]) for y in range(int(h * 0.02), int(h * 0.10)))


def head_cx(rgba):   # 머리 가로 가운데 (몸 키의 2~10% 줄)
    a = rgba[..., 3] > 0
    h = a.shape[0]
    xs = np.where(a[int(h * 0.02):int(h * 0.10)].any(axis=0))[0]
    return (xs.min() + xs.max()) / 2


def main():
    srcs = {f: load(f) for f in FRAMES}
    sc_idle = TARGET_H / srcs['idle'].shape[0]
    head_t = head_w(srcs['idle']) * sc_idle
    walk = [f for f in FRAMES if f.startswith('walk')]
    sc_walk = head_t / np.mean([head_w(srcs[f]) for f in walk])
    scs = {f: (sc_walk if f in walk else sc_idle) for f in FRAMES}
    sheet = np.zeros((CELL_H, CELL_W * len(FRAMES), 4), np.uint8)
    heights = []
    for i, f in enumerate(FRAMES):
        s = eb.defringe(shrink(srcs[f], scs[f]))
        ys, xs = np.where(s[..., 3] > 0)
        s = s[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        h, w = s.shape[:2]
        heights.append(h)
        if w > CELL_W or h > ANCHOR_Y:
            raise SystemExit(f'{f}: 칸보다 큼 {w}x{h}')
        if f == 'idle':
            x0 = ANCHOR_X - w // 2
            head_x = x0 + head_cx(s)   # 대기 칸 머리 가운데 (칸 안 x)
        else:
            x0 = int(round(head_x - head_cx(s)))   # 머리가 제자리에 있게 (걸어도 머리가 좌우로 튀지 않음)
        x0 = min(max(x0, 0), CELL_W - w) + i * CELL_W
        sheet[ANCHOR_Y - h:ANCHOR_Y, x0:x0 + w] = s
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('저장', OUT, sheet.shape, '키', heights, {f: round(float(v), 4) for f, v in scs.items()})


if __name__ == '__main__':
    main()

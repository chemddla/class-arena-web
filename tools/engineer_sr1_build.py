# 기계공 시크릿 레어 1 (흰 가운·검은 뿔테 안경·남색 넥타이·갈색 바지, 손에 푸른 홀로그램 판, 흰 배경) → assets/sprites/merc/engineer_sr1.webp
# 사용: python tools/engineer_sr1_build.py   (샘플 assets/sprites/fx/samples/engineer_sr1_*_src.png, 배경 따기·찌꺼기 깎기는 engineer_build 그대로)
# 칸 순서는 기본 외형(engineer_0)과 같게 맞출 것: 0 대기 · 1~4 걷기 · 5~6 리벳총 (겨눔 → 쏨) · 7~8 수리 · 9 설치 · 10 피격 · 11~12 쓰러짐
#   2026-11-14 대기 샘플만 받음 → 지금은 대기 한 칸만 만들고 게임에는 아직 연결하지 않음 (SECRET_MERC_SKINS에 engineer 없음)
#   동작 샘플이 오는 대로 FRAMES에 늘리고, 13칸이 다 차면 index.html SECRET_MERC_SKINS에 engineer: [1]을 넣음
# 크기: 대기 키(머리털 끝~발)를 기본 외형 대기와 같은 98px로. 다른 동작은 안경 렌즈나 얼굴 크기로 대기 칸에 맞출 예정
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import engineer_build as eb
from berserker_build import shrink

eb.D = 'assets/sprites/fx/samples/engineer_sr1_'
OUT = 'assets/sprites/merc/engineer_sr1.webp'
FRAMES = ['idle']
CELL_W, CELL_H, ANCHOR_X, ANCHOR_Y = eb.CELL_W, eb.CELL_H, eb.ANCHOR_X, eb.ANCHOR_Y
TARGET_H = eb.TARGET_H


def main():
    srcs = {f: eb.load(f) for f in FRAMES}
    sc = TARGET_H / srcs['idle'].shape[0]
    sheet = np.zeros((CELL_H, CELL_W * len(FRAMES), 4), np.uint8)
    for i, f in enumerate(FRAMES):
        s = eb.defringe(shrink(srcs[f], sc))
        ys, xs = np.where(s[..., 3] > 0)
        s = s[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        h, w = s.shape[:2]
        if w > CELL_W or h > ANCHOR_Y:
            raise SystemExit(f'{f}: 칸보다 큼 {w}x{h}')
        x0 = min(max(ANCHOR_X - w // 2, 0), CELL_W - w) + i * CELL_W
        sheet[ANCHOR_Y - h:ANCHOR_Y, x0:x0 + w] = s
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('저장', OUT, sheet.shape, '배율', round(sc, 4))


if __name__ == '__main__':
    main()

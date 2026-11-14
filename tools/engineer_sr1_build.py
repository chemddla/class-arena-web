# 기계공 시크릿 레어 1 (흰 가운·검은 뿔테 안경·남색 넥타이·갈색 바지, 손에 푸른 홀로그램 판, 흰 배경) → assets/sprites/merc/engineer_sr1.webp
# 사용: python tools/engineer_sr1_build.py   (샘플 assets/sprites/fx/samples/engineer_sr1_*_src.png, 배경 따기·찌꺼기 깎기는 engineer_build 그대로)
# 칸 (19칸, 기본 외형과 순서가 달라 index.html engineer_101에 anims를 따로 적음):
#   0 대기 · 1~5 걷기 · 6~7 공격 · 8~11 시전·수리 · 12~15 히든스킬 · 16 피격 · 17~18 쓰러짐
#   일반공격 샘플(두 칸: 총구 불꽃과 함께 쏨 → 반동으로 총을 치켜듦) → 6 겨눔(불꽃 지움) · 7 쏨(반동). 6 → 7로 바뀔 때 총알이 나감 (muzzle = 7칸 총구 끝)
#   스킬 시전·수리 샘플(네 칸: 홀로그램 판을 손가락으로 두드림 → 반짝임 → 밀어 넘김 → 다시 두드림) → 8~11.
#     기본 외형의 렌치질(7~8)·설치(9) 대신 쓸 것: 수리 = 8~11 반복, 설치·시전 = 10 (밀어 넘김). 판 옆 작은 반짝임 점은 떨어진 조각이라 빠짐
#   히든스킬(최종병기) 샘플(네 칸: 커다란 홀로그램 화면을 가리킴 → 위를 누름 → 앞으로 나서며 아래를 누름 → 두 손으로 조작) → 12~15.
#     화면은 인물과 붙은 한 덩어리라 같이 남음
#   피격 샘플(입을 벌리고 놀라 몸을 젖힘, 판은 든 채) → 16. 곧게 선 자세라 키를 대기 칸과 같게
#   쓰러짐 샘플 두 장(비틀거리며 판을 놓침 → 옆으로 누움, 안경·판이 바닥에) → 17~18. 둘째 샘플은 사용자가 워터마크를 지운 것
#   걷기는 샘플 한 장에 다섯 칸(왼쪽부터, 오른쪽 끝 잘린 여섯째 조각은 버림)
# 크기: 대기 키(머리털 끝~발)를 기본 외형 대기와 같은 98px로. 걷기·공격·시전은 묶음마다 머리 너비(head_w)를 대기 칸과 같게 (보폭 때문에 키는 조금 작아짐)
# 위치: 발은 바닥선(anchorY), 가로는 머리 가운데를 대기 칸 머리 가운데에 (head_cx)
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import engineer_build as eb
from berserker_build import shrink

eb.D = 'assets/sprites/fx/samples/engineer_sr1_'
OUT = 'assets/sprites/merc/engineer_sr1.webp'
FRAMES = ['idle', 'walk1', 'walk2', 'walk3', 'walk4', 'walk5', 'attack1', 'attack2', 'cast1', 'cast2', 'cast3', 'cast4', 'hidden1', 'hidden2', 'hidden3', 'hidden4', 'hurt', 'down1', 'down2']
# 한 장에 여러 칸인 샘플: 칸 이름 → (샘플 이름, 가로 x0, x1) — 인물 사이 빈 세로줄에서 자름
#   (두 인물이 가로로 겹치면 상자에 옆 사람 조각이 들어오지만 가장 큰 덩어리만 남겨 빠짐)
CROP = {f'walk{i + 1}': ('walk', x0, x1) for i, (x0, x1) in enumerate([(0, 209), (209, 390), (390, 570), (570, 742), (742, 920)])}
CROP.update({'attack1': ('attack', 0, 196), 'attack2': ('attack', 196, 386)})
CROP.update({f'hidden{i + 1}': ('hidden', x0, x1) for i, (x0, x1) in enumerate([(0, 209), (209, 394), (394, 593), (593, 778)])})
CROP.update({f'cast{i + 1}': ('cast', x0, x1) for i, (x0, x1) in enumerate([(30, 284), (284, 533), (533, 780), (780, 1024)])})
# 샘플에 그려진 총구 불꽃: 게임이 리벳탄 총구 섬광을 따로 그리니까 흰색으로 덮어 지움 (샘플 좌표 x0, y0, x1, y1). 탄피는 떨어진 덩어리라 저절로 빠짐
ERASE = {'attack1': [(183, 70, 196, 130)]}
STAND = {'cast1', 'hurt'}   # 이 칸이 첫 칸인 묶음은 키를 대기 칸과 같게
GROUPS = {'walk': [f'walk{i}' for i in range(1, 6)], 'attack': ['attack1', 'attack2'], 'cast': [f'cast{i}' for i in range(1, 5)], 'hidden': [f'hidden{i}' for i in range(1, 5)], 'hurt': ['hurt']}
SCREEN = {'hidden1'}   # 이 칸이 첫 칸인 묶음은 머리 위로 화면이 솟아 있어서, 머리털(어두운 무채색) 꼭대기~발 길이를 대기 키에 맞추고 가로는 머리털 가운데로
# 쓰러짐: 몸에서 떨어진 소품(날아가는 판, 바닥의 안경·판)도 남김 — 샘플에서 KEEP_MIN px 넘는 덩어리는 모두. 작은 점(워터마크를 지운 자국 등)은 빠짐
#   크기는 머리털 덩어리 넓이를 피격 칸과 같게 (두 샘플의 해상도가 피격 샘플과 비슷하고, 누우면 키를 잴 수 없음)
#   가로는 몸(가장 큰 덩어리) 가운데를 기준점에 (기본 외형 쓰러짐처럼)
DOWN = ['down1', 'down2']
# 쓰러짐 2: 안경이 바닥에 떨어져 있으니 얼굴에 쓴 안경을 지움 (2026-11-14 사용자 요청). 줄인 뒤 칸 안 좌표(x, y)에 직접 색을 칠함
#   (원본 크기에서 덮으면 네모나게 티가 나서 최종 크기에서 몇 픽셀만). 샘플·배율·위치가 바뀌면 좌표를 다시 잡을 것
_SK, _SD, _EYE, _HAIR = (0xe3, 0xa9, 0x84), (0xc8, 0x92, 0x76), (0x7d, 0x5a, 0x52), (0x2a, 0x24, 0x29)
PAINT = {'down2': [((96, y), _SK) for y in range(73, 80)] + [((97, y), _SK) for y in range(73, 80)] + [((98, y), _SK) for y in range(73, 80)]
         + [((97, 76), _EYE), ((97, 77), _EYE)]   # 렌즈 1 → 피부 + 감은 눈
         + [((94, 81), _SK), ((94, 82), _SK), ((95, 82), _SK)] + [((x, y), _SK) for x in (96, 97) for y in range(82, 85)] + [((98, 83), _SK), ((98, 84), _SK)]
         + [((x, 85), _SD) for x in (96, 97, 98)] + [((96, 83), _EYE), ((96, 84), _EYE)]   # 렌즈 2 → 피부 + 감은 눈
         + [((x, y), _HAIR) for x, y in [(99, 80), (99, 81), (100, 81), (101, 78), (102, 79), (101, 82), (101, 83), (102, 83), (102, 84), (103, 84), (100, 82), (99, 83), (98, 81)]]}   # 머리카락 위 안경다리
KEEP_MIN = 300
CELL_W, CELL_H, ANCHOR_X, ANCHOR_Y = eb.CELL_W, eb.CELL_H, eb.ANCHOR_X, eb.ANCHOR_Y
TARGET_H = eb.TARGET_H


def load_keep(f):   # eb.load와 같은 배경 따기, 덩어리는 KEEP_MIN px 넘는 것 모두 남김 → (그림, 몸 상자 가로 가운데)
    from scipy import ndimage as ndi
    im = np.array(Image.open(f'{eb.D}{f}_src.png').convert('RGBA')).astype(float)
    rgb = im[..., :3]
    white = (rgb.min(axis=2) > 232) & (rgb.max(axis=2) - rgb.min(axis=2) < 18)
    lab, _ = ndi.label(white)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = ndi.binary_dilation(np.isin(lab, list(edge)), iterations=3) & (rgb.min(axis=2) > 150)
    im[..., 3] = np.where(bg, 0, 255)
    body, n = ndi.label(im[..., 3] > 0, structure=np.ones((3, 3)))
    sizes = ndi.sum(im[..., 3] > 0, body, range(1, n + 1))
    keep = [i + 1 for i in range(n) if sizes[i] >= KEEP_MIN]
    im[..., 3] = np.where(np.isin(body, keep), im[..., 3], 0)
    ys, xs = np.where(im[..., 3] > 0)
    y0, x0 = ys.min(), xs.min()
    _, bx = np.where(body == 1 + int(np.argmax(sizes)))
    return im[y0:ys.max() + 1, x0:xs.max() + 1], (bx.min() + bx.max()) / 2 - x0


def hair_area(rgba):   # 가장 큰 머리털 덩어리 넓이
    from scipy import ndimage as ndi
    m = hair(rgba)
    lab, n = ndi.label(m)
    return float(ndi.sum(m, lab, range(1, n + 1)).max())


def load(f):
    if f not in CROP:
        return eb.load(f)
    src, x0, x1 = CROP[f]
    tmp = f'{eb.D}_crop_src.png'
    im = Image.open(f'{eb.D}{src}_src.png').convert('RGB')
    im = im.copy()
    for box in ERASE.get(f, []):
        im.paste((255, 255, 255), box)
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


def hair(rgba):   # 머리털 픽셀: 어둡고 푸른 기가 없음 (홀로그램 화면 외곽선은 청록이라 빠짐)
    c = rgba[..., :3].astype(int)
    return (rgba[..., 3] > 0) & (c.max(axis=2) < 110) & (c[..., 0] >= c[..., 2] - 5)


def hair_top(rgba):
    return int(np.where(hair(rgba).any(axis=1))[0].min())


def hair_cx(rgba):   # 머리털 꼭대기에서 아래로 몸 키 6%까지의 가로 가운데
    m = hair(rgba)
    t = hair_top(rgba)
    xs = np.where(m[t:t + max(2, int((rgba.shape[0] - t) * 0.06))].any(axis=0))[0]
    return (xs.min() + xs.max()) / 2


def main():
    body_cx = {}
    srcs = {}
    for f in FRAMES:
        if f in DOWN:
            srcs[f], body_cx[f] = load_keep(f)
        else:
            srcs[f] = load(f)
    sc_idle = TARGET_H / srcs['idle'].shape[0]
    head_t = head_w(srcs['idle']) * sc_idle
    scs = {'idle': sc_idle}
    for names in GROUPS.values():   # 묶음마다 머리 너비 평균을 대기 칸 머리 너비에 맞춤
        if names[0] in SCREEN:
            sc = TARGET_H / np.mean([srcs[f].shape[0] - hair_top(srcs[f]) for f in names])
        elif names[0] in STAND:   # 대기처럼 곧게 선 묶음은 키로 (머리 너비로 재면 2% 크게 나옴)
            sc = TARGET_H / np.mean([srcs[f].shape[0] for f in names])
        else:
            sc = head_t / np.mean([head_w(srcs[f]) for f in names])
        scs.update({f: sc for f in names})
    for f in DOWN:
        scs[f] = scs['hurt'] * np.sqrt(hair_area(srcs['hurt']) / hair_area(srcs[f]))
    sheet = np.zeros((CELL_H, CELL_W * len(FRAMES), 4), np.uint8)
    heights = []
    for i, f in enumerate(FRAMES):
        s = eb.defringe(shrink(srcs[f], scs[f]))
        ys, xs = np.where(s[..., 3] > 0)
        s = s[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        cut_x = xs.min()
        h, w = s.shape[:2]
        heights.append(h)
        if w > CELL_W or h > ANCHOR_Y:
            raise SystemExit(f'{f}: 칸보다 큼 {w}x{h}')
        if f == 'idle':
            x0 = ANCHOR_X - w // 2
            head_x = x0 + head_cx(s)   # 대기 칸 머리 가운데 (칸 안 x)
        elif f in DOWN:
            x0 = int(round(ANCHOR_X - (body_cx[f] * scs[f] - cut_x)))
        else:
            x0 = int(round(head_x - (hair_cx(s) if f.startswith('hidden') else head_cx(s))))   # 머리가 제자리에 있게 (걸어도 머리가 좌우로 튀지 않음)
        x0 = min(max(x0, 0), CELL_W - w) + i * CELL_W
        sheet[ANCHOR_Y - h:ANCHOR_Y, x0:x0 + w] = s
        for (px, py), col in PAINT.get(f, []):
            sheet[py, i * CELL_W + px, :3] = col
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('저장', OUT, sheet.shape, '키', heights, {f: round(float(v), 4) for f, v in scs.items()})


if __name__ == '__main__':
    main()

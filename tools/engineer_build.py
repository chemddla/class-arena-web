# 기계공 전용 샘플(갈색 머리·고글·갈색 배낭·국방색 멜빵바지, 흰 배경) → 캐릭터 시트 assets/sprites/merc/engineer_0.webp
# 사용: python tools/engineer_build.py   (샘플은 assets/sprites/fx/samples/engineer_*_src.png, 동작 샘플이 오는 대로 FRAMES에 늘림)
# 칸 순서: 0 대기 · 1~4 걷기 (받은 순서 그대로) · 5~6 리벳총 기본 공격 (5 겨눔 → 6 쏨) · 7~8 수리 (쪼그려 앉아 렌치질, 두 칸 번갈아)
#   · 9 포탑 설치 (앉아서 두 손에 렌치를 듦) · 10 피격 (눈을 질끈 감고 몸을 젖힘) · 11~12 쓰러짐 (무릎 꿇음 → 엎드려 누움)
#   쓰임: 수리 칸(7~8)은 E 수리 모드 고치기와 스킬 '긴급 수리'에 같이 씀 · 설치 칸(9)은 포탑·드론·최종병기 설치 스킬
#   수리 샘플은 한 장에 두 칸 → 가운데 빈 세로줄(141)에서, 쓰러짐 샘플도 두 칸 → 빈 세로줄(345)에서 나눠 저장함
# 칸 크기·기준점은 격투가 시트와 같음 (cellW 119 · cellH 106 · anchorX 63 · anchorY 104)
#
# 크기 통일 (대기 자세 기준): 고글 렌즈 하나의 크기(높이·폭 평균)를 대기 칸과 같게 맞춤
#   - 렌즈 높이 / 몸 키는 서 있는 칸 모두 0.052~0.056으로 거의 같음 → 렌즈 크기가 몸 크기를 잘 대변함
#     (몸이 옆으로 돌아도 렌즈 높이는 그대로라 고글 전체 폭보다 정확함. 예전엔 고글 폭·키로 맞춰 쪼그린 칸·피격·쓰러짐이 11~22% 크게 나왔음)
#   - 같은 묶음(GROUP)은 렌즈 크기 평균으로 한 배율 → 칸끼리 크기가 튀지 않게
#   - 엎드려 누운 칸(down2)은 렌즈가 비스듬해 무릎 꿇은 칸(down1)에서만 잼 (MEASURE_FIRST)
# 위치 통일: 발은 모두 바닥선(anchorY)에. 가로는 고글 가운데를 대기 칸의 고글 가운데와 같은 x에 둠 (머리가 제자리)
#   - 쓰러짐 칸은 머리가 몸 끝에 있어 몸 상자 가운데를 기준점에 둠 · 칸을 넘치면 칸 안으로 밀어 넣음
# 샘플 정리 (칸마다):
#   1) 흰 배경: 가장자리에서 이어진 흰 픽셀 + 외곽선 밖 밝은 번짐 3px (샘플이 흐리게 키운 그림이라)
#   2) 가장 큰 덩어리만 남김 (옆 칸 조각·글자·티끌)
#   3) 줄인 뒤 테두리에 남은 흰 찌꺼기·외곽선 밖 연회색 번짐을 2번 깎음 (defringe)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/engineer_'
OUT = 'assets/sprites/merc/engineer_0.webp'
FRAMES = ['idle', 'walk1', 'walk2', 'walk3', 'walk4', 'attack1', 'attack2', 'repair1', 'repair2', 'build1', 'hurt1', 'down1', 'down2']
GROUP = {'walk1': 'walk', 'walk2': 'walk', 'walk3': 'walk', 'walk4': 'walk', 'repair1': 'repair', 'repair2': 'repair', 'down1': 'down', 'down2': 'down'}   # 같은 배율을 쓰는 묶음 (없으면 칸 이름이 곧 묶음)
MEASURE_FIRST = {'down'}   # 렌즈 크기를 묶음 첫 칸에서만 잼
BODY_CENTER = {'down1', 'down2'}   # 가로 위치를 고글 대신 몸 상자 가운데로
CELL_W, CELL_H, ANCHOR_X, ANCHOR_Y = 119, 106, 63, 104
TARGET_H = 98   # 대기 칸 몸 키 (머리털 끝~발)


def load(name):
    im = np.array(Image.open(D + name + '_src.png').convert('RGBA')).astype(float)
    rgb = im[..., :3]
    white = (rgb.min(axis=2) > 232) & (rgb.max(axis=2) - rgb.min(axis=2) < 18)
    lab, _ = ndi.label(white)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    bg = ndi.binary_dilation(bg, iterations=3) & (rgb.min(axis=2) > 150)   # 샘플이 흐리게 키운 그림이라 외곽선 밖 밝은 번짐 3px까지 배경으로
    im[..., 3] = np.where(bg, 0, 255)
    body, n = ndi.label(im[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndi.sum(im[..., 3] > 0, body, range(1, n + 1))
        im[..., 3] = np.where(body == 1 + int(np.argmax(sizes)), im[..., 3], 0)
    ys, xs = np.where(im[..., 3] > 0)
    return im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def defringe(rgba, passes=2, light=185, gray=40, halo=110, outline=90, near=0):
    """테두리(투명한 곳과 맞닿은 픽셀)의 흰 배경 찌꺼기를 passes번 안쪽으로 깎음.
    - 밝고(최소 채널 light 이상) 색이 없는 픽셀 = 흰 배경 그대로 남은 것
    - 연회색(halo 이상) 무채색인데 바로 안쪽에 검은 외곽선(가장 밝은 채널 outline 이하)이 붙은 픽셀 = 흰 배경과 외곽선이 섞인 번짐
      (총·렌치 같은 진짜 회색은 검은 외곽선 안쪽이라 테두리에 오지 않음)
    - near > 0: 밝은 픽셀은 외곽선에서 near px 안에 있을 때만 지움 (외곽선과 떨어진 흰 연기는 남김)"""
    out = rgba.copy()
    cross = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    for _ in range(passes):
        a = out[..., 3] > 0
        edge = a & ndi.binary_dilation(~a, structure=cross)
        c = out[..., :3].astype(int)
        mn, sat = c.min(axis=2), c.max(axis=2) - c.min(axis=2)
        dark = a & (c.max(axis=2) <= outline)
        lit = mn >= light
        if near:
            lit &= ndi.binary_dilation(dark, iterations=near)
        junk = edge & (sat <= gray) & (lit | ((mn >= halo) & ndi.binary_dilation(dark, structure=cross)))
        if not junk.any():
            break
        out[junk] = 0
    return out


def lens(rgba):   # 가장 큰 고글 렌즈(청록) 덩어리 → 크기(높이·폭 평균)
    r, g, b, a = [rgba[..., i].astype(float) for i in range(4)]
    m = (a > 0) & (g > 110) & (b > 100) & (g - r > 40)
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1))
    ys, xs = np.where(lab == 1 + int(np.argmax(sizes)))
    return ((ys.max() - ys.min() + 1) + (xs.max() - xs.min() + 1)) / 2


def goggle_cx(rgba):   # 고글 렌즈(청록) 두 개를 합친 가로 가운데
    r, g, b, a = [rgba[..., i].astype(float) for i in range(4)]
    m = (a > 0) & (g > 110) & (b > 100) & (g - r > 40)
    xs = np.where(m.any(axis=0))[0]
    return (xs.max() + xs.min()) / 2


def main():
    srcs = {f: load(f) for f in FRAMES}
    grp_of = lambda f: GROUP.get(f, f)
    sc_idle = TARGET_H / srcs['idle'].shape[0]
    lens_t = lens(srcs['idle']) * sc_idle   # 맞출 렌즈 크기 (px)
    scs = {}
    for g in dict.fromkeys(grp_of(f) for f in FRAMES):
        names = [f for f in FRAMES if grp_of(f) == g]
        if g in MEASURE_FIRST:
            names = names[:1]
        scs[g] = sc_idle if g == 'idle' else lens_t / np.mean([lens(srcs[f]) for f in names])
    sheet = np.zeros((CELL_H, CELL_W * len(FRAMES), 4), np.uint8)
    head_x = None
    for i, f in enumerate(FRAMES):
        s = defringe(shrink(srcs[f], scs[grp_of(f)]))
        ys, xs = np.where(s[..., 3] > 0)   # 깎은 뒤 다시 꼭 맞게 자름
        s = s[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        h, w = s.shape[:2]
        if w > CELL_W or h > ANCHOR_Y:
            raise SystemExit(f'{f}: 칸보다 큼 {w}x{h}')
        if f == 'idle':
            x0 = ANCHOR_X - w // 2
            head_x = x0 + goggle_cx(s)   # 대기 칸 고글 가운데 (칸 안 x)
        elif f in BODY_CENTER:
            x0 = ANCHOR_X - w // 2
        else:
            x0 = int(round(head_x - goggle_cx(s)))
        x0 = min(max(x0, 0), CELL_W - w) + i * CELL_W
        y0 = ANCHOR_Y - h
        sheet[y0:y0 + h, x0:x0 + w] = s
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('저장', OUT, sheet.shape, '렌즈', round(lens_t, 2), {k: round(float(v), 3) for k, v in scs.items()})


if __name__ == '__main__':
    main()

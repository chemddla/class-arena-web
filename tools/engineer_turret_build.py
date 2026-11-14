# 기계공 포탑·드론 그림 → 동작 칸 띠 (가로로 칸을 이어 붙임)
# 사용: python tools/engineer_turret_build.py   (결과 칸 크기·기준점·총구 자리를 출력 → index.html ENG_TURRET_SHEET에 옮겨 적음)
#
# 샘플 (assets/sprites/fx/samples/)
#   engineer_turret_motion_src.png : 포탑 발사 동작표 (줄마다 기관포탑·박격포탑·레이저탑, 칸 5개, 아래 칸 이름 글자)
#       칸 경계는 칸 이름 글자 가운데(88·236·384·532·682)의 가운데 → COLS. 줄 제목 글자('1. 기관포 탑' 등)는 상자로 지움
#   engineer_laser_start_src.png      : 레이저탑 발사 시작 (크게)
#   engineer_laser_sustain_cool_src.png : 레이저탑 지속 발사(왼쪽) + 냉각(오른쪽) (크게)
#       → 레이저 빔은 어느 각도로든 쏘므로 그림에서 지우고(렌즈 둘레 빛만 남김) 게임이 각도에 맞춰 그림
#       → 동작표의 레이저 3~5칸은 빔이 옆 칸까지 넘어가 있어 큰 그림을 씀
#   engineer_drone_{idle,fire,dive}_src.png : 드론 평소·사격·자폭 돌진 (드론은 왼쪽을 봄)
#
# 칸 순서
#   기관포탑 0 준비 · 1 회전 시동 · 2 사격 · 3 지속 사격 · 4 반동·복귀(연기)
#   박격포탑 0 준비 · 1 장전·압축 · 2 발사(불꽃) · 3 강한 반동(연기) · 4 재장전·복귀
#   레이저탑 0 준비 · 1 충전 · 2 발사 시작 · 3 지속 발사 · 4 냉각·잔상
#   드론     0 평소 · 1 사격 · 2 자폭 돌진
#
# 크기: 0번 칸(효과 없는 몸)의 키를 BODY_H(px)로 줄이고, 같은 샘플에서 나온 칸은 같은 배율.
#   다른 샘플(큰 레이저·드론 사격/자폭)은 몸 기준 폭(BASE: 포탑은 받침 폭, 드론은 앞 철판 폭)이 0번 칸과 같아지도록 줄임
# 기준점: 포탑은 받침 바닥 가운데, 드론은 몸(가장 큰 덩어리)의 가운데
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

S = 'assets/sprites/fx/samples/engineer_'
OUT = 'assets/sprites/fx/engineer_turret_{}.webp'
COLS = [0, 162, 310, 458, 606, 765]
ROW = {'gatling': (92, 290), 'mortar': (372, 645), 'laser': (790, 985)}
TITLE = {'gatling': (0, 200, 92, 128), 'mortar': (0, 200, 372, 418)}   # 줄 제목 글자 (x0, x1, y0, y1)
BODY_H = {'gatling': 46, 'mortar': 50, 'laser': 54, 'drone': 34}
# 칸: (샘플, 자를 상자 x0,x1,y0,y1, 지울 상자들)
MARGIN = 70   # 동작표 칸은 양옆으로 넓게 잘라 낸 뒤, 덩어리 가운데가 이 칸 경계 안에 있는 것만 남김 (불꽃·연기가 경계를 넘어가도 잘리지 않게)
BALL = (505, 552, 360, 412)   # 박격포 발사 칸 위로 날아가는 포탄 (옆 칸 자리에 있어 지움, 포탄은 게임이 따로 그림)


GAT_COLS = [0, 165, 305, 460, 607, 765]
GAT_EXT = 25   # 기관포 칸 오른쪽으로 더 잘라 넘어간 자기 총구 불꽃을 살림 (더 자른 곳에선 불꽃 색만 남김)   # 기관포 줄: 칸 경계 = 탄약통 왼쪽 끝 (불꽃이 옆 칸 탄약통과 붙어 있어 덩어리로 못 가름, 옆으로 넓게 자르지 않음)


def sheet(kind, i):
    y0, y1 = ROW[kind]
    if kind == 'gatling':
        return ('turret_motion', (GAT_COLS[i], min(765, GAT_COLS[i + 1] + GAT_EXT), y0, y1), [TITLE[kind]], 'gat')
    er = ([TITLE[kind]] if kind in TITLE else []) + ([BALL] if kind == 'mortar' else [])
    return ('turret_motion', (max(0, COLS[i] - MARGIN), min(765, COLS[i + 1] + MARGIN), y0, y1), er, (COLS[i], COLS[i + 1]))
FRAMES = {
    'gatling': [sheet('gatling', i) for i in range(5)],
    'mortar': [sheet('mortar', i) for i in range(5)],
    'laser': [sheet('laser', 0), sheet('laser', 1),
              ('laser_start', (0, 1024, 0, 930), [(780, 1024, 0, 1024)], None),
              ('laser_sustain_cool', (0, 640, 0, 515), [(415, 640, 0, 572)], None),
              ('laser_sustain_cool', (640, 1024, 0, 515), [(985, 1024, 470, 572)], None)],
    'drone': [('drone_idle', (0, 358, 0, 357), [], None), ('drone_fire', (0, 563, 0, 470), [], None), ('drone_dive', (0, 349, 0, 433), [], None)],
}
SAME_SCALE = {'drone'}   # 샘플 세 장의 해상도가 같음 (앞 철판 폭 80·79px) → 한 배율
DRONE_ANCHOR = {'drone_idle': (97, 173), 'drone_fire': (267, 193), 'drone_dive': (136, 251)}   # 앞 철판 가운데 (샘플 px) = 기준점
MUZZLE0 = {'gatling': (0.5, 0.36), 'mortar': (0.3, 0.12), 'laser': (0.37, 0.27), 'drone': (-0.42, 0.88)}   # 0번 칸 몸 상자 기준 (가운데에서 폭의 몇 배, 위에서 키의 몇 배)


def load(name):
    return np.array(Image.open(S + name + '_src.png').convert('RGBA')).astype(float)


def cut(rgba, box, erase, own=None):
    x0, x1, y0, y1 = box
    im = rgba.copy()
    for ex0, ex1, ey0, ey1 in erase:
        im[ey0:ey1, ex0:ex1, :3] = 255
    im = im[y0:y1, x0:x1]
    if own == 'gat':
        R, G, B = im[..., 0], im[..., 1], im[..., 2]
        fire = (R > 190) & (B < 150) & (R - B > 70)   # 총구 불꽃 (주황·노랑·빨강)
        ext = np.zeros(fire.shape, bool); ext[:, -GAT_EXT:] = True if x1 < 765 else False
        lft = np.zeros(fire.shape, bool); lft[:, :40] = True   # 칸 왼쪽 40px의 불꽃 색 = 앞 칸 불꽃 끝
        im[..., :3] = np.where(((ext & ~fire) | (lft & fire))[..., None], 255, im[..., :3])
    rgb = im[..., :3]
    white = (rgb.min(axis=2) > 232) & (rgb.max(axis=2) - rgb.min(axis=2) < 18)
    lab, _ = ndi.label(white)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    sizes = ndi.sum(white, lab, range(1, lab.max() + 1))
    bg |= np.isin(lab, 1 + np.where(sizes >= 40)[0])   # 사슬 고리·전선 사이에 갇힌 흰 배경
    bg = ndi.binary_dilation(bg, iterations=2) & (rgb.min(axis=2) > 150)
    a = np.where(bg, 0, 255)
    body, n = ndi.label(a > 0, structure=np.ones((3, 3)))
    sizes = ndi.sum(a > 0, body, range(1, n + 1))
    ok = sizes >= 12   # 탄피·불티·연기도 남김 (12px 미만 티끌만 지움)
    if own == 'gat':   # 자른 상자 왼쪽 끝에 닿은 조각 = 앞 칸 불꽃·탄피 → 지움 (몸 = 가장 큰 덩어리는 남김)
        ok &= np.array([not (body[:, :22] == i).any() for i in range(1, n + 1)])   # 왼쪽 22px 안에 걸친 조각
        ok[int(np.argmax(sizes))] = True
    elif own:
        cx = ndi.center_of_mass(a > 0, body, range(1, n + 1))
        ok &= np.array([own[0] <= c[1] + x0 < own[1] for c in cx])
    big = 1 + int(np.argmax(np.where(ok, sizes, 0)))
    a = np.where(np.isin(body, 1 + np.where(ok)[0]), a, 0)
    im[..., 3] = a
    return im, body == big   # 그림, 몸(가장 큰 덩어리)


def bbox(m):
    ys, xs = np.where(m)
    return xs.min(), xs.max() + 1, ys.min(), ys.max() + 1


def base_w(kind, body):   # 크기 맞출 기준 폭
    x0, x1, y0, y1 = bbox(body)
    if kind == 'drone':
        return x1 - x0
    rows = body[y1 - max(3, (y1 - y0) // 12): y1]   # 받침 아래쪽 줄들
    xs = np.where(rows.any(axis=0))[0]
    return xs.max() - xs.min() + 1


def anchor(kind, body):
    x0, x1, y0, y1 = bbox(body)
    if kind == 'drone':
        return (x0 + x1) / 2, (y0 + y1) / 2
    rows = body[y1 - max(3, (y1 - y0) // 12): y1]
    xs = np.where(rows.any(axis=0))[0]
    return (xs.min() + xs.max() + 1) / 2, y1


def main():
    srcs = {}
    info = {}
    for kind, frames in FRAMES.items():
        cuts = []
        for src, box, er, own in frames:
            if src not in srcs:
                srcs[src] = load(src)
            cuts.append((src,) + cut(srcs[src], box, er, own) + (box,))
        s0, im0, b0, box0 = cuts[0]
        anc = lambda src, body, box: ((DRONE_ANCHOR[src][0] - box[0], DRONE_ANCHOR[src][1] - box[2]) if src in DRONE_ANCHOR else anchor(kind, body))
        bx0, bx1, by0, by1 = bbox(b0)
        sc0 = BODY_H[kind] / (by1 - by0)
        bw0 = base_w(kind, b0) * sc0
        placed = []
        for src, im, body, box in cuts:
            sc = sc0 if (src == s0 or kind in SAME_SCALE) else bw0 / base_w(kind, body)
            ax, ay = anc(src, body, box)
            s = shrink(im, sc)
            placed.append((s, ax * sc, ay * sc))
        L = max(ax for s, ax, ay in placed); R = max(s.shape[1] - ax for s, ax, ay in placed)
        T = max(ay for s, ax, ay in placed); B = max(s.shape[0] - ay for s, ax, ay in placed)
        cw, ch, AX, AY = int(np.ceil(L + R)) + 2, int(np.ceil(T + B)) + 2, int(np.ceil(L)) + 1, int(np.ceil(T)) + 1
        strip = np.zeros((ch, cw * len(placed), 4), np.uint8)
        for i, (s, ax, ay) in enumerate(placed):
            x = i * cw + AX - int(round(ax)); y = AY - int(round(ay))
            h, w = s.shape[:2]
            region = strip[y:y + h, x:x + w]
            strip[y:y + h, x:x + w] = np.where(s[..., 3:] > 0, s, region)
        Image.fromarray(strip, 'RGBA').save(OUT.format(kind), 'WEBP', lossless=True)
        # 0번 칸 몸 상자 (기준점 기준 좌표)
        a0 = anc(s0, b0, box0)
        bl, bt = (bx0 - a0[0]) * sc0, (by0 - a0[1]) * sc0
        bwid, bhei = (bx1 - bx0) * sc0, (by1 - by0) * sc0
        mx, my = MUZZLE0[kind]
        muzzle = [round(bl + bwid / 2 + bwid * mx, 1), round(bt + bhei * my, 1)]
        info[kind] = {'cw': cw, 'ch': ch, 'ax': AX, 'ay': AY, 'n': len(placed), 'h': BODY_H[kind], 'muzzle': muzzle}
    print(json.dumps(info))


if __name__ == '__main__':
    main()

# 창병 히든 스킬 [무쌍난무] 외형 1~5 자세 그림 가공
# 샘플(외형마다 윗줄·아랫줄 두 장, 어두운 배경·노란 제목·한글 라벨·✦) → 기본 외형 cast와 같은 순서의 10칸 투명 webp
# 사용: python tools/lancer_musou_skins_build.py <샘플 폴더> <외형>:<윗줄 파일>:<아랫줄 파일> ...
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = 'assets/sprites/fx/'
REF = np.array(Image.open(OUT + 'lancer_musou_cast.webp').convert('RGBA'))[..., 3] / 255
RW, RH, RAX, RAY, RSTAND = 236, 138, 71, 125, 80  # 기본 외형 cast 칸·발 기준점·서 있는 키
GHOST_FIX = {'1', '3', '4'}  # 찌르기 잔상이 다른 사람(어두운 피부·다른 머리색)으로 그려진 외형


def unblend(im, bg):
    # 배경과의 차이로 불투명도를 매기고 색을 되살림 (어두운 쪽은 0, 밝은 쪽은 255까지의 거리로 나눔)
    up = (im - bg) / np.maximum(255 - bg, 1)
    dn = (bg - im) / np.maximum(bg, 1)
    a = np.maximum(up, dn).max(axis=2).clip(0, 1)
    a = np.where(a < 0.06, 0, a)  # 압축 얼룩
    rgb = np.where(a[..., None] > 0, (im - (1 - a[..., None]) * bg) / np.maximum(a[..., None], 1e-3), 0)
    return rgb.clip(0, 255), a


def clean(path):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    H, W, _ = im.shape
    bg = np.median(np.concatenate([im[:, 0], im[:, -1], im[-1]]), axis=0)
    d = np.abs(im - bg).max(axis=2)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    # 라벨 띠: 맨 아래에서 처음 만나는 글자 줄 (그 위 빈 줄까지)
    rows = (d > 40).sum(axis=1)
    y = H - 1
    while y > 0 and rows[y] == 0: y -= 1
    while y > 0 and rows[y] > 0: y -= 1
    band = y + 1
    kill = np.zeros((H, W), bool)
    lab, n = ndi.label(ndi.binary_dilation(d > 18, iterations=2))
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        if sl[0].start >= band - 3: kill |= lab == i
    # 노란 제목 (왼쪽 위 줄)
    yellow = (r > 110) & (g > 80) & (r - b > 60) & (g - b > 30)
    yellow[30:] = False; yellow[:, 380:] = False
    kill |= ndi.binary_dilation(yellow, iterations=2) & ~((mn := im.min(axis=2)) > 150)
    # ✦ 워터마크 (오른쪽 아래, 납작한 중간 회색 별 — 초승달에 붙어 있어도 두꺼운 회색 덩어리로 찾음)
    mid = (np.abs(r - g) < 10) & (b - r >= 0) & (b - r <= 22) & (r >= 70) & (r <= 140)
    mid[:, :900] = False; mid[:80] = False
    lab2, _ = ndi.label(ndi.binary_opening(mid, iterations=2))
    for i, sl in enumerate(ndi.find_objects(lab2), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if 13 <= hh <= 22 and 13 <= ww <= 22 and abs(hh - ww) <= 3 and (lab2[sl] == i).sum() >= 100:
            kill |= ndi.binary_dilation(lab2 == i, iterations=5) & (im.max(axis=2) < 165) & (im.max(axis=2) - im.min(axis=2) < 30)
    im[kill] = bg
    # 제목 자리에 남은 부스러기: 왼쪽 위 띠 안에서만 끝나는 작은 덩어리
    lab4, _ = ndi.label(np.abs(im - bg).max(axis=2) > 10)
    for i, sl in enumerate(ndi.find_objects(lab4), 1):
        if sl[0].stop <= 32 and sl[1].stop <= 400 and (lab4[sl] == i).sum() < 300: im[lab4 == i] = bg
    soft_rgb, soft_a = unblend(im, bg)
    # 바깥 배경: 가장자리에서 배경색(차이 6 미만)으로 이어진 곳
    d = np.abs(im - bg).max(axis=2)
    # (창·바람 줄기·회전 고리가 둘러싼 배경 웅덩이도 10px 넘으면 바깥으로 봄)
    lab3, _ = ndi.label(d < 6)
    edge = np.unique(np.concatenate([lab3[0], lab3[-1], lab3[:, 0], lab3[:, -1]]))
    sizes = np.bincount(lab3.ravel())
    ext = np.isin(lab3, edge[edge > 0]) | ((sizes[lab3] >= 10) & (lab3 > 0))
    # 바깥에서 2px 넘게 떨어진 안쪽은 원래 색 그대로 불투명 (배경과 비슷한 어두운 망토·바지도),
    # 바깥 가장자리 2px(바람 줄기·초승달의 흐린 테두리)만 배경과의 차이로 불투명도를 매김
    solid = ndi.distance_transform_edt(~ext) > 2
    # 배경 얼룩(압축·그러데이션): 진한 그림에서 4px 넘게 떨어진 흐린 픽셀은 지움
    near = ndi.binary_dilation(soft_a > 0.35, iterations=4)
    soft_a = np.where(near & (soft_a >= 0.1), soft_a, 0)
    rgb, a = soft_rgb.copy(), soft_a.copy()
    rgb[solid] = im[solid]; a[solid] = 1
    a[band - 2:] = 0; soft_a[band - 2:] = 0
    return rgb, a, soft_rgb, soft_a


def split(a, n=5):
    # 칸 나누기: 예상 경계 근처에서 가장 비어 있는 세로줄
    W = a.shape[1]; col = a.sum(axis=0)
    cuts = [0]
    for k in range(1, n):
        c = W * k // n
        cuts.append(c - 60 + int(np.argmin(col[c - 60:c + 60])))
    cuts.append(W)
    return cuts


def bbox(a, t=0.3):
    ys, xs = np.where(a > t)
    return xs.min(), ys.min(), xs.max(), ys.max()


def resize(rgb, a, s):
    # 곱해진 알파로 축소 (가장자리 검은 번짐 방지)
    h, w = a.shape; nw, nh = max(1, round(w * s)), max(1, round(h * s))
    pm = np.dstack([rgb * a[..., None], a * 255])
    sm = np.stack([np.array(Image.fromarray(pm[..., k].astype(np.float32), 'F').resize((nw, nh), Image.LANCZOS)) for k in range(4)], axis=2)
    al = (sm[..., 3] / 255).clip(0, 1)
    out = np.where(al[..., None] > 0.01, sm[..., :3] / np.maximum(al[..., None], 0.01), 0).clip(0, 255)
    return out, np.where(al < 0.02, 0, al)


def fix_ghost(rgb, a, soft_rgb, soft_a, x0, x1):
    # 찌르기 잔상(주인공 오른쪽 뒤 x0~x1)이 다른 사람(어두운 피부·다른 머리색)으로 그려진 외형:
    # 머리·피부색을 지운 반투명한 차가운 남색 그림자로 (바람 줄기·불꽃·주인공 손은 그대로)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    fx = ((mn > 140) & (mx - mn < 70)) | ((r > 160) & (g > 140) & (r - b > 40))
    region = np.zeros_like(a, bool); region[:, x0:x1] = True
    lum = 0.3 * r + 0.55 * g + 0.15 * b
    edge_gray = (mx - mn < 22) & (lum > 80)  # 바람 줄기 흐린 테두리
    ghost = region & (a > 0) & (soft_a < 0.88) & ~fx & ~edge_gray
    new = (np.array([60, 70, 100])[None, None] * (0.45 + lum[..., None] / 255 * 1.3)).clip(0, 255)
    rgb[ghost] = new[ghost]
    a[ghost] = np.minimum(a[ghost], 0.62)
    return int(ghost.sum())


GHOST_X0 = {'1': 0.40, '3': 0.37, '4': 0.38}  # 잔상이 시작하는 칸 안 가로 비율 (주인공 머리를 건드리지 않게)
STAND = 108  # 시트 속 서 있는 키 (시크릿 레어 시트와 같음)
REF_H = {0: 79, 7: 72}  # 기본 외형 cast: 서 있음·돌진 칸의 머리 꼭대기~발


def head_top(a):
    # 머리 꼭대기: 가운데 몸 부분에서 불투명 10px 넘는 줄이 6줄 넘게 이어지기 시작하는 곳 (가는 창대·바람 줄기 제외)
    W = a.shape[1]
    m = (a[:, int(W * 0.25):int(W * 0.7)] > 0.6).sum(axis=1) >= 10
    for y in range(len(m) - 6):
        if m[y:y + 6].all(): return y
    return 0


def feet_y(a):
    # 발 높이: 가운데 몸 부분 중 불투명한 맨 아래 줄
    W = a.shape[1]
    ys = np.where((a[:, int(W * 0.25):int(W * 0.7)] > 0.6).any(axis=1))[0]
    return ys.max()


def body_mask(rgb, a):
    # 겹침 비교용 몸: 불투명하고 흰 바람 줄기가 아닌 곳
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    return (a > 0.85) & ~((mn > 150) & (mx - mn < 60))


def row(path, name, top):
    rgb, a, srgb, sa = clean(path)
    cuts = split(a)
    if top and name in GHOST_FIX:  # 찌르기 칸 잔상
        c0, c1 = cuts[3], cuts[4]; w = c1 - c0
        fix_ghost(rgb, a, srgb, sa, c0 + int(w * GHOST_X0[name]), c0 + int(w * 0.70))
    cells = [(rgb[:, cuts[i]:cuts[i + 1]], a[:, cuts[i]:cuts[i + 1]]) for i in range(5)]
    # 줄마다 크기: 윗줄은 서 있음, 아랫줄은 돌진 칸의 키를 기본 외형과 같은 비율로
    k = 0 if top else 2
    h = feet_y(cells[k][1]) - head_top(cells[k][1])
    s = STAND * REF_H[0 if top else 7] / 79 / h
    feet = int(np.median([feet_y(c[1]) for c in cells]))
    return cells, s, feet


def main():
    src = sys.argv[1]
    K = STAND / RSTAND
    ref = Image.fromarray((REF * 255).astype(np.uint8)).resize((round(REF.shape[1] * K), round(REF.shape[0] * K)), Image.BILINEAR)
    ref = np.array(ref) / 255 > 0.5
    rcw = round(RW * K)
    built = {}
    for job in sys.argv[2:]:
        name, top, bot = job.split(':')
        frames = []
        for path, is_top in ((f'{src}/{top}', True), (f'{src}/{bot}', False)):
            cells, s, feet = row(path, name, is_top)
            print(name, path[-6:], 'scale', round(s, 3), 'feet', feet)
            for i, (rgb, a) in enumerate(cells):
                rr, ra = resize(rgb, a, s)
                frames.append((rr, ra, feet * s))
        # 칸마다 기본 외형 같은 칸과 몸이 가장 많이 겹치는 자리 (세로는 줄 발 높이 ±8)
        placed = []
        for k, (rr, ra, fy) in enumerate(frames):
            rk = ref[:, k * rcw:(k + 1) * rcw]
            ax, ay = RAX * K, RAY * K
            bm = body_mask(rr, ra)
            ys, xs = np.where(bm)
            best = (-1, 0, 0)
            ry_, rx_ = np.where(rk)
            cx = round(rx_.mean() - xs.mean())  # 무게중심을 맞춘 자리 근처만 찾음
            for dy in range(-8, 9):
                oy = round(ay - fy) + dy
                for ox in range(cx - 45, cx + 46):
                    yy, xx = ys + oy, xs + ox
                    ok = (yy >= 0) & (yy < rk.shape[0]) & (xx >= 0) & (xx < rk.shape[1])
                    sc = rk[yy[ok], xx[ok]].sum() - 0.5 * abs(dy)
                    if sc > best[0]: best = (sc, ox, oy)
            placed.append((rr, ra, best[1] - ax, best[2] - ay))  # 기준점 기준 위치
        built[name] = placed
    # 모든 외형이 같은 칸 크기·기준점을 쓰게
    L = U = Rr = D = 0
    for placed in built.values():
        for rr, ra, px, py in placed:
            ys, xs = np.where(ra > 0.02)
            L = max(L, -(px + xs.min())); U = max(U, -(py + ys.min()))
            Rr = max(Rr, px + xs.max() + 1); D = max(D, py + ys.max() + 1)
    AX, AY = int(np.ceil(L)) + 2, int(np.ceil(U)) + 2
    CW, CH = AX + int(np.ceil(Rr)) + 2, AY + int(np.ceil(D)) + 2
    print('cell', CW, CH, 'anchor', AX, AY, 'standH', STAND)
    for name, placed in built.items():
        sheet = Image.new('RGBA', (CW * 10, CH), (0, 0, 0, 0))
        for k, (rr, ra, px, py) in enumerate(placed):
            im = Image.fromarray(np.dstack([rr, ra * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
            sheet.alpha_composite(im, (k * CW + AX + round(px), AY + round(py)))
        sheet.save(f'{OUT}lancer_musou_{name}.webp', lossless=True)
        print('saved', name, sheet.size)


if __name__ == '__main__':
    main()

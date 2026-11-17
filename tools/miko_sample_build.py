# 무녀 그림 샘플 다듬기 (사용자 샘플, 흰 배경) → 미리보기 _preview_miko_sheet*.png
# 사용: python tools/miko_sample_build.py
# 샘플: assets/sprites/fx/samples/miko_*_src.png (2026-11-17 사용자가 준 그림)
#   idle 대기 · walk 걷기 3칸(한 장) · atkdown 일반 공격 2칸(위) + 피격 1칸(가운데) + 쓰러짐 2칸(아래)
#   skill 부적 소환 (왼쪽 = 시전, 오른쪽 = 캐스팅) · hid1~3 히든 (캐스팅 → 떠오르며 시전 → 착지)
# 고르기: 그림에 같이 그려진 날아가는 부적·속도선·머리 위 부적·바닥 부적은 캐릭터에서 떨어진 덩어리라 빠짐
#   (투사체·소환 부적은 게임에서 이펙트로 따로 그림)
# 맞추기 (대기 칸 기준, qigong_sample_build와 같은 방식):
#   - 흰 배경: brawler_sr1_build.cut (가장자리 흰색 + 갇힌 흰 구멍 + 테두리 찌꺼기) → 가장 큰 덩어리만
#     무녀는 옷이 흰색이라 배경과 붙은 흰 옷이 같이 지워지지 않게, 옷 안쪽 흰색은 외곽선에 막혀 남는지 확인
#   - 크기·비율: 얼굴 살색 덩어리 넓이의 제곱근이 대기와 같아지게 배율 (HEAD_FIX로 눈대중 보정)
#   - 피부색·밝기: 얼굴 살색 평균이 대기와 같아지게 채널별 배율, 하카마 빨강 평균도 대기와 같아지게 빨간 부분만 한 번 더
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from brawler_sr1_build import cut, shrink

D = 'assets/sprites/fx/samples/miko_'
TARGET_H = 86   # 대기 자세 키 (다른 직업 칸과 같은 게임 px)
HEAD_FIX = {('히든', 1): 0.87, ('히든', 2): 0.86}   # 눈대중: 대기 칸과 나란히 놓고 머리 폭이 같아지게 (흐린 원본이라 얼굴 살색이 작게 잡힘)
POSE_SCALE = {}
SHARPEN = {}
CLEAR_BELOW = {'hid3': 161}   # 착지: 손·발 아래 바닥에 깔린 부적 (원본 y) — 손끝 159, 부적 162부터. 부적은 이펙트로 따로
SAME = {('쓰러짐', 1): ('쓰러짐', 0)}   # 누운 칸은 얼굴이 작게 보여 같은 원본의 다른 칸 배율을 씀


def blobs(name, n, rows=1):   # 한 장에 여러 칸 → 칸마다 다른 그림을 흰색으로 덮은 사본 (줄 → 왼쪽부터)
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB'))
    fg = im.astype(int).min(axis=2) < 225
    lab, k = ndi.label(ndi.binary_dilation(fg, iterations=3))
    sz = ndi.sum(fg, lab, range(1, k + 1))
    big = list(np.argsort(-sz)[:n] + 1)
    cy = {i: np.where(lab == i)[0].mean() for i in big}
    cx = {i: np.where(lab == i)[1].mean() for i in big}
    H = im.shape[0]
    big.sort(key=lambda i: (int(cy[i] / H * rows), cx[i]))
    out = []
    for i in big:
        o = im.copy(); o[lab != i] = 255
        out.append(o)
    return out


def one(name):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB'))
    if name in CLEAR_BELOW: im[CLEAR_BELOW[name]:] = 255
    return im


def sharpen(fig, amt):
    rgb = Image.fromarray(fig[..., :3].clip(0, 255).astype(np.uint8)).filter(ImageFilter.UnsharpMask(2, amt, 2))
    out = fig.copy(); out[..., :3] = np.array(rgb); return out


def despeck(im, area=150):   # 몸에서 떨어진 작은 점(티끌)을 흰색으로 덮음
    fg = im.astype(int).min(axis=2) < 225
    lab, n = ndi.label(fg, structure=np.ones((3, 3)))
    sz = ndi.sum(fg, lab, range(1, n + 1))
    o = im.copy(); o[np.isin(lab, 1 + np.where(sz < area)[0])] = 255
    return o


def skin_mask(rgba):
    c = rgba[..., :3].astype(int); r, g, b = c[..., 0], c[..., 1], c[..., 2]
    return (rgba[..., 3] > 0) & (r > 150) & (r - g > 18) & (r - g < 80) & (g - b > 10) & (g - b < 60) & (g > 110)


def red_mask(rgba):   # 하카마·리본 빨강 (히든 2·3의 검붉은 하카마까지: 밝기 대신 색 비율로)
    c = rgba[..., :3].astype(int); r, g, b = c[..., 0], c[..., 1], c[..., 2]
    return (rgba[..., 3] > 0) & (r > 60) & (r > g * 1.7) & (r > b * 1.6)


def match_hist(src, ref):   # 빨간 픽셀들의 채널별 밝기 순위를 대기 칸 빨강 분포에 그대로 옮김 (어두운 주름·밝은 면 단계 유지)
    out = np.empty_like(src)
    q = np.linspace(0, 100, 101)
    for ch in range(3):
        rank = np.argsort(np.argsort(src[:, ch])) / max(1, len(src) - 1) * 100
        out[:, ch] = np.interp(rank, q, np.percentile(ref[:, ch], q))
    return out


def face(rgba):   # 그림 위쪽 60% 안의 가장 큰 살색 덩어리 = 얼굴 → (넓이, 평균색, 턱 y)
    m = skin_mask(rgba); m[int(rgba.shape[0] * .6):] = False
    lab, n = ndi.label(ndi.binary_closing(m, iterations=2) & m)
    if n == 0: return None
    sz = ndi.sum(m, lab, range(1, n + 1))
    f = lab == 1 + int(np.argmax(sz))
    return f.sum(), rgba[..., :3][f].astype(float).mean(axis=0), int(np.where(f)[0].max())


def cut_closed(im, gap=None):   # 흰 옷용 배경 지우기: 흰 옷이 배경과 같은 254~255라 색으로는 못 가름
    # 1) 외곽선(밝지 않은 픽셀)을 gap만큼 부풀려 틈을 막고, 가장자리에서 이어진 흰 곳만 배경으로 채움
    # 2) 부풀린 만큼 깎인 배경 가장자리를 되돌림: 배경에 닿은 흰 픽셀을 gap+1번 넓힘 (외곽선은 안 넘음)
    # 3) 테두리 찌꺼기: 배경에 닿은 밝은 회색(흰 배경과 외곽선이 섞인 색) 2겹 벗김
    # 4) 가장 큰 덩어리만 (떨어진 부적·속도선 빠짐)
    im = im.astype(float)
    mn, ch = im.min(axis=2), im.max(axis=2) - im.min(axis=2)
    if gap is None: gap = max(1, round(max(im.shape[:2]) / 160))
    line = mn < 200
    wall = ndi.binary_dilation(line, iterations=gap)
    lab, n = ndi.label(~wall)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    white = (mn > 222) & (ch < 20)
    for _ in range(gap + 1):
        bg |= ndi.binary_dilation(bg) & white
    rimc = (mn > 110) & (ch < 12)
    for _ in range(2):
        bg |= ndi.binary_dilation(bg) & rimc
    m = ~bg
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
    sz = ndi.sum(m, lab, range(1, n + 1))
    m &= lab == 1 + int(np.argmax(sz))
    ys, xs = np.where(m)
    return np.dstack([im, m * 255.0])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


cut = cut_closed

# 외곽선 안에 갇힌 흰 덩어리 중 배경인 것 (2026-11-17 칸마다 번호 붙여 확대 점검)
#   자동 1) 바깥(투명)에 닿은 60픽셀 이하 흰 덩어리 = 외곽 찌꺼기·머리카락 끝 틈 (발밑 7%는 버선이라 제외)
#   자동 2) 위쪽 20% 안에서 둘레 30% 이상이 진한 선인 흰 덩어리 = 리본 고리 안 구멍 (리본 빨강이 둘레를 채워 진한 선 비율이 낮은 칸도 있음)
#   지정) 자동으로 못 잡는 머리카락·팔 사이 틈: 잘라낸 그림 좌표 (x, y) — 그 점이 든 흰 덩어리를 지움
HOLE_PTS = {
    ('걷기', 1): [(31, 146)],
    ('일반 공격', 0): [(30, 103), (55, 117), (57, 122)],
    ('일반 공격', 1): [(37, 129)],
    ('피격', 0): [(105, 27), (131, 34), (137, 48), (145, 72), (20, 76), (112, 95)],
    ('쓰러짐', 0): [(11, 88), (18, 140), (111, 103)],
    ('쓰러짐', 1): [(187, 107), (103, 107)],
    ('부적 소환', 0): [(21, 67), (34, 124)],
    ('부적 소환', 1): [(36, 140), (33, 124)],
    ('히든', 0): [(32, 137)],
    ('히든', 2): [(30, 105), (91, 89)],
}


def white_blobs(fig):
    a = fig[..., 3] > 0; c = fig[..., :3]
    mn = c.min(axis=2); ch = c.max(axis=2) - mn
    return ndi.label(a & (mn > 215) & (ch < 25))


def clear_holes(fig, key):
    fig = fig.copy()
    a = fig[..., 3] > 0; mn = fig[..., :3].min(axis=2); H = fig.shape[0]
    lab, n = white_blobs(fig)
    kill = np.zeros(n + 1, bool)
    for k in range(1, n + 1):
        m = lab == k; s = m.sum(); ys = np.where(m)[0]
        ring = ndi.binary_dilation(m, iterations=2) & ~m
        if s <= 60 and (~a[ring]).any() and ys.mean() < H * .93: kill[k] = True
        if ys.mean() < H * .2 and (mn[ring] < 110).mean() >= .3: kill[k] = True
    for x, y in HOLE_PTS.get(key, []):
        win = lab[max(0, y - 3):y + 4, max(0, x - 3):x + 4]
        for k in np.unique(win[win > 0]): kill[k] = True
    gone = kill[lab]
    # 지운 구멍 둘레의 밝은 회색(흰 배경과 외곽선이 섞인 색)도 2겹 벗김
    rim = (mn > 110) & ((fig[..., :3].max(axis=2) - mn) < 12) & a
    for _ in range(2):
        gone |= ndi.binary_dilation(gone) & rim
    fig[..., 3] = np.where(gone, 0, fig[..., 3])
    return fig


def frames():
    walk = blobs('walk', 3)
    ad = blobs('atkdown', 5, rows=3)   # 위 2 공격 · 가운데 1 피격 · 아래 2 쓰러짐
    sk = blobs('skill', 2)             # 왼쪽 = 시전 · 오른쪽 = 캐스팅
    return [
        ('대기', [one('idle')]),
        ('걷기', walk),
        ('일반 공격', ad[0:2]),
        ('피격', ad[2:3]),
        ('쓰러짐', ad[3:5]),
        ('부적 소환', [sk[1], sk[0]]),   # 캐스팅 → 시전
        ('히든', [one('hid1'), one('hid2'), one('hid3')]),
    ]


def build(verbose=False):
    rows = []
    idle = clear_holes(cut(despeck(one('idle'))), ('대기', 0))
    fa0, fc0, _ = face(idle)
    red0 = idle[..., :3][red_mask(idle)].astype(float)
    sc0 = TARGET_H / idle.shape[0]
    done = {}
    for label, ims in frames():
        cells = []
        for j, im in enumerate(ims):
            fig = clear_holes(cut(despeck(im)), (label, j))
            f = face(fig)
            if (label, j) in SAME:
                k, gain, rgain = done[SAME[(label, j)]]
            else:
                k = np.sqrt(fa0 / f[0]) * HEAD_FIX.get((label, j), 1.0) if f else 1.0
                gain = np.clip(fc0 / f[1], 0.75, 1.4) if f else np.ones(3)
                rgain = None
            done[(label, j)] = (k, gain, rgain)
            k *= POSE_SCALE.get((label, j), 1.0)
            fig = fig.astype(float)
            fig[..., :3] = (fig[..., :3] * gain).clip(0, 255)
            rm = red_mask(fig)
            if label != '대기' and rm.sum() > 50:
                fig[..., :3][rm] = match_hist(fig[..., :3][rm], red0)
            if label in SHARPEN:   # 흐린 원본: 줄이기 전에 윤곽을 또렷하게
                fig = sharpen(fig, SHARPEN[label])
            cells.append((shrink(fig.astype(np.uint8), sc0 * k), k, gain, rgain))
            if verbose:
                print(label, j, 'face', f[0] if f else None, 'k', round(sc0 * k, 3), 'g', np.round(gain, 2))
        rows.append((label, cells))
    return rows


def sheet(rows, bg, zoom=3, out='_preview_miko_sheet.png'):
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 16 * zoom // 2)
    cw, chh, lw, pad = 110, 118, 80, 6
    W = lw + cw * max(len(c) for _, c in rows)
    H = chh * len(rows)
    canvas = Image.new('RGBA', (W, H), bg)
    for r, (label, cells) in enumerate(rows):
        y0 = r * chh
        for j, (c, *_r) in enumerate(cells):
            im = Image.fromarray(c, 'RGBA')
            x = lw + j * cw + (cw - im.width) // 2
            canvas.alpha_composite(im, (max(lw + j * cw, x), y0 + chh - pad - im.height))
    big = canvas.resize((W * zoom, H * zoom), Image.NEAREST)
    d = ImageDraw.Draw(big)
    fg = (40, 40, 40, 255) if sum(bg[:3]) > 380 else (230, 230, 230, 255)
    for r, (label, _) in enumerate(rows):
        d.text((8 * zoom, (r * chh + chh // 2) * zoom), label, font=font, fill=fg, anchor='lm')
        d.line([(0, (r + 1) * chh * zoom - 1), (W * zoom, (r + 1) * chh * zoom - 1)], fill=fg[:3] + (40,))
    big.save(out)
    return out


if __name__ == '__main__':
    rows = build(verbose=True)
    print(sheet(rows, (255, 255, 255, 255)))
    print(sheet(rows, (46, 50, 58, 255), out='_preview_miko_sheet_dark.png'))

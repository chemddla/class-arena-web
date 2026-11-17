# 무녀 시크릿 레어 1 샘플 다듬기 (사용자 샘플, 흰 배경) → 미리보기 _preview_miko_sr1_sheet*.png · _preview_miko_sr1_walk.gif
# 사용: python tools/miko_sr1_sample_build.py
# 샘플: assets/sprites/fx/samples/miko_sr1_idle_src.png (2026-11-17 사용자가 준 대기 그림 한 장:
#   남색 철릭·붉은 치마·오색 띠·양손 부채, 땋은 머리)
#   miko_sr1_walk_src.png 걷기 4칸 한 장 (게임 걷기도 4칸이라 4장 다 씀). 4번째 칸 치마 위의 반짝이 워터마크는
#   원본에서 세로(주름 방향)로 위아래 치마 색을 이어 메꿔 둠
#   miko_sr1_hurt_src.png 피격 1칸 · miko_sr1_death_src.png 쓰러짐 2칸 (넘어짐 → 누움)
#   miko_sr1_atk_src.png 일반 공격 3장 → 게임 일반 공격은 2칸이라 1번(부적 들기)·3번(팔 뻗기)만 씀.
#   2번의 날아가는 부적은 떼어서 시크릿 레어 부적 투사체 그림으로 (2026-11-17 사용자: "부적 투사체는 일반공격에 있는 부적 써")
#   miko_sr1_cast_src.png 부적 소환 캐스팅 (두 손 들기) · miko_sr1_skill_src.png 시전 (두 팔 펴기, 둘레에 부적 고리)
#   부적 소환 두 칸은 둘레에 떠 있는 부적을 샘플 그대로 남김 (2026-11-17 사용자: "떠다니는 부적 삭제하지 말고 그대로") → cut_keep.
#   크기·기준점은 부적을 뺀 몸(가장 큰 덩어리)으로 잼 (BODY). remove_charms는 이제 안 씀
#   miko_sr1_naerim_src.png 히든 내림굿 5칸 한 장: 1 준비 자세 · 2~4 시전 막대 동안 굿 동작 · 5 시전. 부채·방울은 손에 든 소품이라 남김
#   3·4번 칸 부채와 소매가 가까워 칸 나누기는 1px만 부풀림
# 자르기·줄이기는 기본 무녀(miko_sample_build)와 같은 방식
# 크기: 대기 칸은 키 96 (기본 무녀 86보다 조금 큼, 어른 비율). 다른 칸은 대기 기준으로 맞춤 (scales)
# 색: 피부·철릭 남색·치마 빨강을 대기 칸에 맞춤 (recolor)
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
import miko_sample_build as base
from brawler_sr1_build import shrink

SRC = 'assets/sprites/fx/samples/miko_sr1_idle_src.png'
SR_H = 96


FEET = {'sr1_death': [(.85, 1, 0, 1), (0, .12, 0, 1)]}   # 버선 자리 (x0, x1, y0, y1 비율): 넘어짐은 오른쪽 끝, 누움은 왼쪽 끝


def clear_back(fig, feet=((0, 1, .88, 1),)):   # 두 번: 첫 번째에 둘레 회색을 벗기면 바깥에 새로 닿는 흰 덩어리가 생김
    return clear_back1(clear_back1(fig, feet), feet)


def clear_back1(fig, feet):   # 몸 사이에 갇힌 흰 배경 (땋은 머리와 등, 목과 팔, 오색 띠 둘레, 소매와 몸 사이)
    # 흰 덩어리마다 평균 밝기를 봄: 배경은 거의 순백(평균 246~253), 목 깃은 그늘이 져서 232 안팎 → 평균 243 이상·15픽셀 이상이면 배경
    # 버선(평균 243~245)은 발 자리(feet) 안에 가운데가 있으면 남김. 지운 뒤 둘레의 밝은 회색(배경과 외곽선이 섞인 색)도 2겹 벗김
    fig = fig.copy(); H, W = fig.shape[:2]
    c = fig[..., :3]; mn, ch = c.min(axis=2), c.max(axis=2) - c.min(axis=2)
    a = fig[..., 3] > 0
    lab, n = ndi.label(a & (mn > 200) & (ch < 25))
    gone = np.zeros_like(a)
    skin = base.skin_mask(fig)
    collar = np.zeros_like(a)   # 목 깃 자리: 턱 바로 밑 ~ 얼굴 높이 1.2배 아래, 얼굴 폭 양옆 절반씩 (목은 그늘져 살색으로 안 잡혀서 따로 보호)
    sk = skin.copy(); sk[int(H * .6):] = False
    sl, sn = ndi.label(ndi.binary_closing(sk, iterations=2) & sk)
    if sn:
        F = sl == 1 + int(np.argmax(ndi.sum(sk, sl, range(1, sn + 1))))
        fy, fx = np.where(F); fw, fh = fx.max() - fx.min() + 1, fy.max() - fy.min() + 1
        collar[max(0, fy.max() - 3):fy.max() + int(fh * 1.2), max(0, fx.min() - fw // 2):fx.max() + fw // 2] = True
    for i in range(1, n + 1):
        m = lab == i; ys, xs = np.where(m)
        fx, fy = xs.mean() / W, ys.mean() / H
        if any(x0 <= fx <= x1 and y0 <= fy <= y1 for x0, x1, y0, y1 in feet): continue
        # 가는 틈(띠와 옷 사이, 땋은 머리 끝)·바깥 테두리의 옅은 흰 줄은 배경과 섞여 어둡게 나옴 → 바깥 투명에 닿아 있으면 평균 205 이상이면 배경
        #   (칸마다 흰빛을 초록으로 칠한 점검표 _preview_miko_sr1_white.png로 확인: 목 깃·눈 하이라이트는 바깥에 안 닿고, 버선은 발 자리)
        touch = (ndi.binary_dilation(m) & ~a).any()
        # 외곽선 두 줄 사이에 갇힌 가는 흰 줄(소매와 몸 사이, 얼굴 옆 끊긴 조각): 굵기 2.5px 이하·4px 이상·평균 215 이상이고 살색에 안 닿으면 배경
        #   (목 깃도 가는 흰 줄이지만 목 살색에 붙어 있음, 눈 하이라이트도 눈가 살색에 닿음)
        thin = len(ys) >= 4 and ndi.distance_transform_edt(m).max() <= 2.5
        near_skin = (ndi.binary_dilation(m, iterations=2) & skin).any()
        if (len(ys) >= 15 and mn[m].mean() >= 243) or (touch and mn[m].mean() >= 205)                 or (thin and not near_skin and not collar[m].mean() > .5 and mn[m].mean() >= 215): gone |= m
    rim = (mn > 110) & (ch < 14) & a
    for _ in range(2):
        gone |= ndi.binary_dilation(gone) & rim
    fig[..., 3][gone] = 0
    return fig


SKILL_CLEAR = [(0, 18, 92, 130, 0), (18, 26, 88, 100, 200), (40, 46, 112, 118, 150), (62, 82, 22, 48, 225)]   # 부적 뗀 시전 칸 (x0, x1, y0, y1, 밝기): 왼손 아래 부적 끄트머리(전부) · 땋은 머리 옆 흰 점(밝은 것만)


def clear_boxes(fig, boxes):
    fig = fig.copy()
    for x0, x1, y0, y1, lo in boxes:
        sub = fig[y0:y1, x0:x1]
        sub[..., 3][sub[..., :3].min(axis=2) >= lo] = 0
    m = fig[..., 3] > 0
    lab, n = ndi.label(m)
    fig[..., 3][lab != 1 + int(np.argmax(ndi.sum(m, lab, range(1, n + 1))))] = 0
    ys, xs = np.where(fig[..., 3] > 0)
    return fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def split(name, n, grow=1):   # base.blobs와 같되 덜 부풀려서 가까운 칸이 붙지 않게 (왼쪽부터)
    im = np.array(Image.open(f'{base.D}{name}_src.png').convert('RGB'))
    fg = im.astype(int).min(axis=2) < 225
    lab, k = ndi.label(ndi.binary_dilation(fg, iterations=grow), structure=np.ones((3, 3)))
    sz = ndi.sum(fg, lab, range(1, k + 1))
    big = sorted(np.argsort(-sz)[:n] + 1, key=lambda i: np.where(lab == i)[1].mean())
    out = []
    for i in big:
        o = im.copy(); o[lab != i] = 255
        out.append(o)
    return out


def remove_charms(fig, min_px=120):   # 몸에 닿거나 겹친 노란 부적 떼기
    # 1) 노랑~주황 덩어리 중 min_px 이상 (오색 띠의 작은 노란 칸은 빠짐), 부풀려 붉은 글씨·외곽선까지 덮음
    # 2) 떼는 픽셀마다 같은 세로줄에서 위·아래로 가장 가까운 남은 픽셀을 봄: 둘 다 몸이면 옷 위에 겹친 부적 → 가까운 쪽 색
    #    (오색 띠·치마 주름이 세로라 이어짐), 하나라도 배경이면 허공(몸 밖으로 삐져나온 부분 포함) → 투명
    fig = fig.astype(float).copy()
    c = fig[..., :3]; r, g, b = c[..., 0], c[..., 1], c[..., 2]
    a = fig[..., 3] > 0
    y = a & (r > 150) & (g > 85) & (b < 120) & (r - b > 80) & (r - g < 120)
    lab, n = ndi.label(y, structure=np.ones((3, 3)))
    keep = np.zeros_like(y)
    for i in range(1, n + 1):
        if (lab == i).sum() >= min_px: keep |= lab == i
    R = ndi.binary_fill_holes(ndi.binary_dilation(keep, iterations=4)) & a
    H, W = R.shape
    src = fig.copy()
    for x in np.unique(np.where(R)[1]):
        col = R[:, x]
        for yy in np.where(col)[0]:
            up = yy
            while up > 0 and col[up]: up -= 1
            dn = yy
            while dn < H - 1 and col[dn]: dn += 1
            if col[up] or col[dn] or src[up, x, 3] == 0 or src[dn, x, 3] == 0:
                fig[yy, x, 3] = 0
            else:
                fig[yy, x] = src[up if yy - up <= dn - yy else dn, x]
    m = fig[..., 3] > 0   # 떼고 나서 몸에서 떨어진 조각 정리: 가장 큰 덩어리만
    lab, n = ndi.label(m)
    fig[..., 3][lab != 1 + int(np.argmax(ndi.sum(m, lab, range(1, n + 1))))] = 0
    ys, xs = np.where(fig[..., 3] > 0)
    print('charms removed', int(keep.sum()), 'px')
    return fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def cut_keep(im, min_px=120):   # base.cut(흰 옷용 배경 지우기)과 같되 가장 큰 덩어리만이 아니라 min_px 이상 덩어리(떠 있는 부적)를 모두 남김
    im = im.astype(float)
    mn, ch = im.min(axis=2), im.max(axis=2) - im.min(axis=2)
    gap = max(1, round(max(im.shape[:2]) / 160))
    wall = ndi.binary_dilation(mn < 200, iterations=gap)
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
    m &= np.isin(lab, 1 + np.where(sz >= min_px)[0])
    ys, xs = np.where(m)
    return np.dstack([im, m * 255.0])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def body_box(f):   # 몸 = 가장 큰 덩어리의 (y0, y1, x0, x1) — 떠 있는 부적은 빠짐
    a = f[..., 3] > 0
    lab, n = ndi.label(ndi.binary_dilation(a, iterations=2))
    big = lab == 1 + int(np.argmax(ndi.sum(a, lab, range(1, n + 1))))
    ys, xs = np.where(big & a)
    return ys.min(), ys.max() + 1, xs.min(), xs.max() + 1


BODY = {}   # (줄, 칸) → 몸 상자 (떠 있는 부적이 있는 칸만)
META = {}   # (줄, 칸) → 줄인 칸 안의 (기준점 x, 발 y) — 떠 있는 부적이 있는 칸만 (build가 채움)


def navy_mask(f):   # 철릭 남색
    c = f[..., :3].astype(int); r, g, b = c[..., 0], c[..., 1], c[..., 2]
    return (f[..., 3] > 0) & (b > r + 12) & (b < 150) & (r < 110)


def head(f):   # 얼굴 살색 덩어리의 (폭, 높이) — 위쪽 60% 안의 가장 큰 살색 덩어리
    sk = base.skin_mask(f); sk[int(f.shape[0] * .6):] = False
    lab, n = ndi.label(ndi.binary_closing(sk, iterations=2) & sk)
    if not n: return None
    F = lab == 1 + int(np.argmax(ndi.sum(sk, lab, range(1, n + 1))))
    ys, xs = np.where(F)
    return xs.max() - xs.min() + 1, ys.max() - ys.min() + 1


def frames():   # (줄 이름, 칸 번호, 원본 크기 그림, 배율 묶음, 서 있는 칸인지) — 한 장에 그린 칸들은 같은 묶음 = 같은 배율
    out = [('대기', 0, clear_back(base.cut(base.despeck(np.array(Image.open(SRC).convert('RGB'))))), 'idle', True)]
    for j, w in enumerate(base.blobs('sr1_walk', 4)): out.append(('걷기', j, clear_back(base.cut(base.despeck(w))), 'walk', True))
    out.append(('피격', 0, clear_back(base.cut(base.despeck(base.blobs('sr1_hurt', 1)[0]))), 'hurt', False))
    for j, w in enumerate(base.blobs('sr1_death', 2)):
        out.append(('쓰러짐', j, clear_back(base.cut(base.despeck(w)), FEET['sr1_death'][j:j + 1]), 'death', False))
    at = base.blobs('sr1_atk', 3)
    for j, i in enumerate([0, 2]): out.append(('일반 공격', j, clear_back(base.cut(base.despeck(at[i]))), 'atk', True))
    for j, nm in enumerate(['sr1_cast', 'sr1_skill']):   # 떠 있는 부적까지 그대로
        f = clear_back(cut_keep(base.despeck(base.one(nm), area=60)))
        BODY[('부적 소환', j)] = body_box(f)
        out.append(('부적 소환', j, f, 'cast' if j == 0 else 'skill', True))
    for j, w in enumerate(split('sr1_naerim', 5)): out.append(('내림굿', j, clear_back(base.cut(base.despeck(w))), 'naerim', j in (0, 4)))
    return out


def scales(fr):   # 대기 칸 기준 배율 (묶음마다 하나)
    # 대기: 키 96. 다른 묶음: 얼굴(폭·높이 평균)이 대기와 같아지는 배율을 묶음 안 칸들 평균으로 →
    #   서 있는 칸이 있으면 그 칸들의 키 96 배율과 기하평균 (샘플마다 머리 비율이 조금 달라, 얼굴만 맞추면 키가, 키만 맞추면 얼굴이 어긋남 → 둘 다 4% 안)
    #   누운 칸(쓰러짐 2)은 얼굴이 옆으로 누워 같은 묶음 첫 칸 기준
    idle = fr[0][2]; k0 = SR_H / idle.shape[0]; h0 = np.array(head(idle)) * k0
    groups = {}
    for lb, j, f, g, standing in fr:
        if (lb, j) in BODY: y0, y1, x0, x1 = BODY[(lb, j)]; f = f[y0:y1, x0:x1]   # 떠 있는 부적을 뺀 몸으로 잼
        groups.setdefault(g, []).append((lb, j, f, standing))
    K = {'idle': k0}
    for g, items in groups.items():
        if g == 'idle': continue
        hs = [np.mean(h0 / np.array(head(f))) for lb, j, f, st in items if head(f) and not (lb == '쓰러짐' and j == 1)]
        kf = float(np.mean(hs))
        st = [SR_H / f.shape[0] for lb, j, f, s_ in items if s_]
        K[g] = float(np.sqrt(kf * np.mean(st))) if st else kf
        print(f'{g:7s} 얼굴 기준 {kf:.3f}' + (f' · 키 기준 {np.mean(st):.3f}' if st else '') + f' → {K[g]:.3f}')
    return K


def deep_red(f):   # 치마·고름·리본 빨강 (부채·부적의 주황은 빼려고 초록이 빨강의 40% 미만인 것만)
    c = f[..., :3].astype(float)
    return base.red_mask(f) & (c[..., 1] < c[..., 0] * .4)


def recolor(f, ref):   # 피부·남색은 채널별 배율로, 빨강은 대기 칸 빨강 밝기 분포에 그대로 옮김 (주름 단계 유지)
    f = f.astype(float).copy()
    for mask in (base.skin_mask, navy_mask):
        m = mask(f); r = mask(ref)
        if m.sum() > 20:
            gain = np.clip(ref[..., :3][r].mean(axis=0) / np.maximum(f[..., :3][m].mean(axis=0), 1), .8, 1.25)
            f[..., :3][m] = (f[..., :3][m] * gain).clip(0, 255)
    m = deep_red(f)
    if m.sum() > 50: f[..., :3][m] = base.match_hist(f[..., :3][m], ref[..., :3][deep_red(ref)].astype(float))
    return f


def check_sheet(fr, out='_preview_miko_sr1_white.png'):   # 흰 배경 점검: 칸마다 원본 크기로, 남은 흰빛(밝기 200↑·무채색) 픽셀을 초록으로
    cells = []
    for lb, j, f, g, st in fr:
        c = f[..., :3].astype(np.uint8).copy(); a = f[..., 3] > 0
        mn = c.min(axis=2).astype(int); ch = c.max(axis=2).astype(int) - mn
        c[~a] = (46, 50, 58); c[a & (mn > 200) & (ch < 25)] = (0, 255, 0)
        cells.append((f'{lb} {j + 1}', Image.fromarray(c)))
    W = sum(im.width + 20 for _, im in cells[:9]); H = max(im.height for _, im in cells) + 30
    canvas = Image.new('RGB', (max(W, sum(im.width + 20 for _, im in cells[9:])), H * 2), (46, 50, 58))
    d = ImageDraw.Draw(canvas); font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 16)
    x = 0
    for i, (t, im) in enumerate(cells):
        if i == 9: x = 0
        y = (i >= 9) * H
        canvas.paste(im, (x, y + 24)); d.text((x + 4, y + 2), t, font=font, fill=(230, 230, 230)); x += im.width + 20
    canvas.save(out)
    return out


def build():
    idle0 = base.clear_holes(base.cut(base.despeck(base.one('idle'))), ('대기', 0))
    fr = frames()
    K = scales(fr)
    print(check_sheet(fr))
    ref = fr[0][2].astype(float)
    rows, ka = [], None
    META.clear()
    for lb, j, f, g, st in fr:
        if j == 0: rows.append((lb, []))
        if g != 'idle': f = recolor(f, ref)
        cell = shrink(f.astype(np.uint8), K[g])
        if (lb, j) in BODY:   # 몸 상자 → 칸 안 기준점 (치마 가운데 x, 발 y). 조립 도구가 씀
            y0, y1, x0, x1 = BODY[(lb, j)]
            bm = f[y0:y1, x0:x1, 3] > 0; h = y1 - y0
            cx = x0 + np.where(bm[int(h * .6):int(h * .9)])[1].mean()
            META[(lb, j)] = (cx * K[g], y1 * K[g])
        hd = head(f)
        print(f'{lb} {j + 1}: 키 {cell.shape[0]} 폭 {cell.shape[1]}' + (f' · 얼굴 {hd[0] * K[g]:.1f}×{hd[1] * K[g]:.1f}' if hd else ''))
        rows[-1][1].append(cell)
    sc0 = base.TARGET_H / idle0.shape[0]
    return shrink(idle0.astype(np.uint8), sc0), rows[0][1][0], rows[1:], charm(K['atk'])


def charm(kk):   # 일반 공격 2번 장의 날아가는 부적 (캐릭터와 떨어진 덩어리) → 투사체 그림, 캐릭터와 같은 배율
    im = np.array(Image.open(base.D + 'sr1_atk_src.png').convert('RGB'))
    fg = im.astype(int).min(axis=2) < 225
    lab, n = ndi.label(ndi.binary_dilation(fg, iterations=2))
    best = None
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if 300 < len(ys) < 6000 and 450 < xs.mean() < 600 and (best is None or len(ys) > best[0]): best = (len(ys), ys, xs)
    _, ys, xs = best
    crop = im[ys.min() - 4:ys.max() + 5, xs.min() - 4:xs.max() + 5].copy()
    cf = base.cut(crop)
    print('charm src', cf.shape[1], 'x', cf.shape[0], '→', round(cf.shape[1] * kk), 'x', round(cf.shape[0] * kk))
    return shrink(cf.astype(np.uint8), kk), cf.astype(np.uint8)


def preview(cells, bg, out, zoom=4, names=None):
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 9 * zoom // 2)
    cw, chh = 120, 130
    canvas = Image.new('RGBA', (cw * len(cells), chh), bg)
    for j, c in enumerate(cells):
        im = Image.fromarray(c, 'RGBA')
        canvas.alpha_composite(im, (j * cw + (cw - im.width) // 2, chh - 18 - im.height))
    big = canvas.resize((canvas.width * zoom, chh * zoom), Image.NEAREST)
    d = ImageDraw.Draw(big)
    fg = (40, 40, 40, 255) if sum(bg[:3]) > 380 else (230, 230, 230, 255)
    for j, t in enumerate(names or ['기본 무녀 대기', '시크릿 레어 1 대기']):
        d.text(((j * cw + cw // 2) * zoom, (chh - 8) * zoom), t, font=font, fill=fg, anchor='mm')
    big.save(out)
    return out


def sheet(rows, bg, out, zoom=3):   # 동작마다 한 줄 (왼쪽에 이름), 칸은 바닥선에 맞춤
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 8 * zoom)
    lw, cw = 80, max(c.shape[1] for _, cs in rows for c in cs) + 10
    hs = [max(c.shape[0] for c in cs) + 12 for _, cs in rows]
    W = lw + cw * max(len(cs) for _, cs in rows)
    canvas = Image.new('RGBA', (W, sum(hs)), bg)
    y0 = 0
    for (lb, cs), h in zip(rows, hs):
        for j, c in enumerate(cs):
            im = Image.fromarray(c, 'RGBA')
            canvas.alpha_composite(im, (lw + j * cw + (cw - im.width) // 2, y0 + h - 6 - im.height))
        y0 += h
    big = canvas.resize((W * zoom, sum(hs) * zoom), Image.NEAREST)
    d = ImageDraw.Draw(big)
    fg = (40, 40, 40, 255) if sum(bg[:3]) > 380 else (230, 230, 230, 255)
    y0 = 0
    for (lb, _), h in zip(rows, hs):
        d.text((6 * zoom, (y0 + h // 2) * zoom), lb, font=font, fill=fg, anchor='lm')
        y0 += h
        d.line([(0, y0 * zoom - 1), (W * zoom, y0 * zoom - 1)], fill=fg[:3] + (50,))
    big.save(out)
    return out


if __name__ == '__main__':
    b, s, rows, (ch_small, ch_big) = build()
    rows = [('대기', [b, s])] + rows + [('부적 투사체', [ch_small])]   # 대기 줄: 기본 무녀 대기 · SR1 대기
    print(sheet(rows, (255, 255, 255, 255), '_preview_miko_sr1_sheet.png'))
    print(sheet(rows, (46, 50, 58, 255), '_preview_miko_sr1_sheet_dark.png'))
    # 걷기 움직임 확인용 (게임 걷기 한 바퀴 0.56초 = 칸당 0.14초)
    fr = []
    for w in rows[1][1]:
        c = Image.new('RGBA', (90, 110), (46, 50, 58, 255)); im = Image.fromarray(w, 'RGBA')
        c.alpha_composite(im, ((90 - im.width) // 2, 104 - im.height)); fr.append(c.resize((270, 330), Image.NEAREST))
    fr[0].save('_preview_miko_sr1_walk.gif', save_all=True, append_images=fr[1:], duration=140, loop=0)
    print('_preview_miko_sr1_walk.gif')

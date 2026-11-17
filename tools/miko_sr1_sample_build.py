# 무녀 시크릿 레어 1 샘플 다듬기 (사용자 샘플, 흰 배경) → 미리보기 _preview_miko_sr1*.png
# 사용: python tools/miko_sr1_sample_build.py
# 샘플: assets/sprites/fx/samples/miko_sr1_idle_src.png (2026-11-17 사용자가 준 대기 그림 한 장:
#   남색 철릭·붉은 치마·오색 띠·양손 부채, 땋은 머리)
#   miko_sr1_walk_src.png 걷기 4칸 한 장 (게임 걷기도 4칸이라 4장 다 씀). 4번째 칸 치마 위의 반짝이 워터마크는
#   원본에서 세로(주름 방향)로 위아래 치마 색을 이어 메꿔 둠
#   miko_sr1_hurt_src.png 피격 1칸 · miko_sr1_death_src.png 쓰러짐 2칸 (넘어짐 → 누움)
#   miko_sr1_atk_src.png 일반 공격 3장 → 게임 일반 공격은 2칸이라 1번(부적 들기)·3번(팔 뻗기)만 씀.
#   2번의 날아가는 부적은 떼어서 시크릿 레어 부적 투사체 그림으로 (2026-11-17 사용자: "부적 투사체는 일반공격에 있는 부적 써")
# 자르기·줄이기는 기본 무녀(miko_sample_build)와 같은 방식
# 크기: 얼굴 넓이로 맞추면 기본(2.5등신)과 등신이 달라 키 126이 되므로 키로 맞춤 — 어른 비율이라 기본 86보다 조금 큰 96
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
import miko_sample_build as base
from brawler_sr1_build import shrink

SRC = 'assets/sprites/fx/samples/miko_sr1_idle_src.png'
SR_H = 96
FACE_FIX = 1.09   # 공격 칸에서 얼굴 넓이로 잰 배율(0.254)이 키로 잰 배율(0.277)보다 9% 작게 나옴 → 키로 못 재는 피격·쓰러짐에 같은 보정


FEET = {'sr1_death': [(.85, 1, 0, 1), (0, .12, 0, 1)]}   # 버선 자리 (x0, x1, y0, y1 비율): 넘어짐은 오른쪽 끝, 누움은 왼쪽 끝


def clear_back(fig, feet=((0, 1, .88, 1),)):   # 몸 사이에 갇힌 흰 배경 (땋은 머리와 등, 목과 팔, 오색 띠 둘레, 소매와 몸 사이)
    # 흰 덩어리마다 평균 밝기를 봄: 배경은 거의 순백(평균 246~253), 목 깃은 그늘이 져서 232 안팎 → 평균 243 이상·15픽셀 이상이면 배경
    # 버선(평균 243~245)은 발 자리(feet) 안에 가운데가 있으면 남김. 지운 뒤 둘레의 밝은 회색(배경과 외곽선이 섞인 색)도 2겹 벗김
    fig = fig.copy(); H, W = fig.shape[:2]
    c = fig[..., :3]; mn, ch = c.min(axis=2), c.max(axis=2) - c.min(axis=2)
    a = fig[..., 3] > 0
    lab, n = ndi.label(a & (mn > 200) & (ch < 25))
    gone = np.zeros_like(a)
    for i in range(1, n + 1):
        m = lab == i; ys, xs = np.where(m)
        if len(ys) < 15 or mn[m].mean() < 243: continue
        fx, fy = xs.mean() / W, ys.mean() / H
        if any(x0 <= fx <= x1 and y0 <= fy <= y1 for x0, x1, y0, y1 in feet): continue
        gone |= m
    rim = (mn > 110) & (ch < 14) & a
    for _ in range(2):
        gone |= ndi.binary_dilation(gone) & rim
    fig[..., 3][gone] = 0
    return fig


def build():
    idle0 = base.clear_holes(base.cut(base.despeck(base.one('idle'))), ('대기', 0))
    fa0 = base.face(idle0)[0]
    sc0 = base.TARGET_H / idle0.shape[0]
    im = np.array(Image.open(SRC).convert('RGB'))
    fig = clear_back(base.cut(base.despeck(im)))
    f = base.face(fig)
    k = SR_H / fig.shape[0]
    print('sr1 face', f[0], 'base face', fa0, 'scale', round(k, 3), '(얼굴로 맞추면', round(sc0 * np.sqrt(fa0 / f[0]), 3), ')')
    # 걷기: 시크릿 레어 대기 칸과 얼굴 넓이를 맞춤. 한 장에 같은 크기로 그린 4칸이라 배율은 평균 하나로 (칸마다 다르면 걸을 때 몸이 커졌다 작아짐)
    wfs = [clear_back(base.cut(base.despeck(w))) for w in base.blobs('sr1_walk', 4)]
    kw = float(np.mean([k * np.sqrt(f[0] / base.face(wf)[0]) for wf in wfs]))
    print('walk scale', round(kw, 3), '→ 키', [round(wf.shape[0] * kw) for wf in wfs])
    walks = [shrink(wf.astype(np.uint8), kw) for wf in wfs]
    rows = [('걷기', walks)]

    def pose(name, n, rows_=1, pick=None, same=False, height=None):   # 얼굴 넓이를 SR 대기 칸에 맞춤 (same = 한 장 안 칸들은 첫 칸 배율 하나로)
        figs = [clear_back(base.cut(base.despeck(w)), *([FEET[name][j:j + 1]] if name in FEET else [])) for j, w in enumerate(base.blobs(name, n, rows_))]
        if pick: figs = [figs[i] for i in pick]
        out, ks = [], []
        for wf in figs:
            ff = base.face(wf)
            kk = ks[0] if (same and ks) or not ff else (height / wf.shape[0] if height else k * np.sqrt(f[0] / ff[0]) * FACE_FIX)
            ks.append(kk)
            print(name, 'face', ff[0] if ff else None, 'scale', round(kk, 3), '→ 키', round(wf.shape[0] * kk), '폭', round(wf.shape[1] * kk))
            out.append(shrink(wf.astype(np.uint8), kk))
        return out, ks

    hurt, _ = pose('sr1_hurt', 1)
    death, _ = pose('sr1_death', 2, same=True)   # 누운 칸은 얼굴이 옆으로 작게 잡혀 넘어지는 칸 배율을 같이 씀
    atk, ka = pose('sr1_atk', 3, pick=[0, 2], same=True, height=SR_H)   # 서 있는 자세라 키로 맞춤 (얼굴로 재면 88로 작아 보임)
    rows += [('피격', hurt), ('쓰러짐', death), ('일반 공격', atk)]
    return shrink(idle0.astype(np.uint8), sc0), shrink(fig.astype(np.uint8), k), rows, charm(ka[0])


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


if __name__ == '__main__':
    b, s, rows, (ch_small, ch_big) = build()
    walks = rows[0][1]
    print('sr1 cell', s.shape[1], 'x', s.shape[0], '/ base', b.shape[1], 'x', b.shape[0])
    names = ['기본 무녀 대기', 'SR1 대기'] + [f'SR1 걷기 {j + 1}' for j in range(len(walks))]
    print(preview([b, s] + walks, (255, 255, 255, 255), '_preview_miko_sr1.png', names=names))
    print(preview([b, s] + walks, (46, 50, 58, 255), '_preview_miko_sr1_dark.png', names=names))
    cells = [c for _, cs in rows[1:] for c in cs] + [ch_small]
    names = [f'{lb} {j + 1}' for lb, cs in rows[1:] for j in range(len(cs))] + ['부적 투사체']
    for bg, out in [((255, 255, 255, 255), '_preview_miko_sr1_moves.png'), ((46, 50, 58, 255), '_preview_miko_sr1_moves_dark.png')]:
        cw = max(120, max(c.shape[1] for c in cells) + 10)
        canvas = Image.new('RGBA', (cw * len(cells), 130), bg)
        for j, c in enumerate(cells):
            im = Image.fromarray(c, 'RGBA'); canvas.alpha_composite(im, (j * cw + (cw - im.width) // 2, 112 - im.height))
        big = canvas.resize((canvas.width * 3, 390), Image.NEAREST); d = ImageDraw.Draw(big)
        font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 14)
        for j, t in enumerate(names):
            d.text(((j * cw + cw // 2) * 3, 370), t, font=font, fill=(40, 40, 40, 255) if bg[0] > 128 else (230, 230, 230, 255), anchor='mm')
        big.save(out); print(out)
    # 걷기 움직임 확인용 (게임 걷기 한 바퀴 0.56초 = 칸당 0.14초)
    fr = []
    for w in walks:
        c = Image.new('RGBA', (90, 110), (46, 50, 58, 255)); im = Image.fromarray(w, 'RGBA')
        c.alpha_composite(im, ((90 - im.width) // 2, 104 - im.height)); fr.append(c.resize((270, 330), Image.NEAREST))
    fr[0].save('_preview_miko_sr1_walk.gif', save_all=True, append_images=fr[1:], duration=140, loop=0)
    print('_preview_miko_sr1_walk.gif')

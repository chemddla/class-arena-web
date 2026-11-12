# 검사 시크릿 레어 1 (은발 긴 머리·회색 도복·회색 하카마·갈색 칼집, 흰 배경) → assets/sprites/merc/swordsman_sr1.webp
# 사용: python tools/swordsman_sr1_build.py   (샘플 assets/sprites/fx/samples/swordsman_sr1_*_src.png, 배경 따기는 swordsman_build.load 그대로)
# 칸: 0 대기 · 1~4 걷기 (샘플 한 장에 네 칸, 왼쪽부터) · 5 일반공격 1 (서서 칼자루를 쥠) · 6 일반공격 2 (낮게 앉아 칼자루를 쥠)
#   · 7 스킬 시전 (다리를 넓게 벌리고 몸을 숙여 칼자루를 쥠)
#   · 11~17 무참 1~7 (받은 순서: 서서 숙여 칼끝을 아래로 · 달리며 칼을 뒤로 · 낮게 앉아 칼을 앞 아래로 · 칼을 머리 위로 치켜듦
#     · 넓게 벌려 칼을 앞 위로 · 숙여 칼을 앞 아래로 · 아주 낮게 웅크림). 캡처 테두리(아래 회색 띠·옆 줄)는 CARD로 잘라 냄
#   · 18 발도 (낮게 벌려 앉아 칼을 뒤로 뽑아 든 자세): 발도·섬단·극참 발동 자세이자 무참 여덟째 자세.
#     2026-11-12 같은 자세의 깨끗한 새 샘플(1450×1085, 워터마크 없음)로 교체
#   · 19 심검·패링 (칼을 얼굴 앞에 비스듬히 들어 막는 자세). 대기와 같은 배율, 배경의 흐린 ✦ 워터마크는 몸과 떨어져 있어 큰 덩어리만 고르면 빠짐
#   · 20 피격 (고개를 젖히고 두 팔을 듦) · 21~22 쓰러짐 (무릎 꿇음 → 엎드려 누움): 한 장(번호·이름 글자 포함)에서 상자로 잘라 냄 (CARD), 셋 다 쓰러짐 1 배율
#   · 23 극참 마지막 일격 준비 (칼을 머리 위로 가로로 들어 기를 모음, 2026-11-12)
#   · 8~10 일섬 1~3 (0번 20~22와 같은 순서: 칼을 뒤로 뻗음 · 앞으로 내지름 · 숙여 칼끝을 아래로). 칼날 칸은 외톨이 점만 지움
#   일반공격 샘플은 양 옆 칸 조각이 붙어 있어 가장 큰 덩어리만. 동작 샘플이 오는 대로 FRAMES에 늘리고 index.html swordsman_sr1 anims를 고침
# 크기: 대기 키(머리 꼭대기~발)를 기본 외형 대기와 같은 TARGET_H로. 이 그림은 머리가 커서 얼굴을 맞추면 키가 64px로 너무 작아짐
#   다른 동작은 샘플마다 해상도가 달라 얼굴(살색) 키·넓이가 대기 칸과 같아지게 (face_scale, 2026-11-12 눈으로 맞춘 배율은 15% 작았음). 못 재는 칸은 SAME_SC
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(__file__))
import swordsman_build as sb
from berserker_build import shrink

OUT = 'assets/sprites/merc/swordsman_sr1.webp'
sb.CARD['sr1_cast'] = (2, 211, 0, 245)   # 시전 샘플: 캡처 테두리(왼쪽 2px 세로줄 · 아래 4px 가로줄)가 흰 배경을 가둬서 잘라 냄
MUCHAM_CARD = {1: 273, 2: 254, 3: 207, 4: 282, 5: 279, 6: 246, 7: 137}   # 샘플 아래 회색 띠가 시작하는 줄
for i, y1 in MUCHAM_CARD.items():
    w = Image.open(f'{sb.D}sr1_mucham{i}_src.png').width
    sb.CARD[f'sr1_mucham{i}'] = (3, w - 3, 3, y1)   # 둘레 3px (옆 캡처 줄)도 함께
# (피격 머리 속 흰 점은 머리카락 하이라이트라 지우면 머리에 구멍이 남 — 넣지 말 것)
# 몸에 둘러싸여 남은 흰 배경 (잘라 낸 뒤 샘플 px 한 점): 일섬 1 소매 아래 (WHITEN) · 무참 2 턱 밑 머리카락 사이 · 무참 3 칼날과 다리 사이 · 무참 7 두 칼날 사이
sb.HOLES.update({'sr1_issen1': [(91, 80)], 'sr1_mucham2': [(188, 97)], 'sr1_mucham3': [(115, 170), (178, 183), (208, 191)], 'sr1_mucham7': [(104, 105), (83, 108)]})
# 하카마 위 회색 ✦ 워터마크 (샘플 이름 → 상자 x0, x1, y0, y1 · 이 줄부터 아래는 검은 외곽선 · 덮을 하카마 색)
STARS = {'mind': (640, 672, 898, 935, 999, (66, 69, 63))}


# 흐린 흰 틈 (샘플 이름 → 상자 x0, x1, y0, y1): 상자 안의 밝은 픽셀(가장 어두운 채널 > 190)을 완전한 흰색으로 칠해 HOLES가 한 덩어리로 지우게 함
#   일섬 1: 앞으로 뻗은 소매 아래로 비친 배경
WHITEN = {'issen1': (88, 98, 75, 82)}


def scrub_stars():   # 별(과 흐린 둘레 1px)을 하카마 색으로, 외곽선 줄은 검정으로 덮음 + WHITEN (원본 샘플 파일에 한 번 적용: --scrub-star)
    for name, (x0, x1, y0, y1) in WHITEN.items():
        p = f'{sb.D}sr1_{name}_src.png'
        a = np.array(Image.open(p).convert('RGB'))
        box = a[y0:y1, x0:x1]
        box[box.min(axis=2) > 190] = 255
        Image.fromarray(a).save(p)
    for name, (x0, x1, y0, y1, black_y, col) in STARS.items():
        p = f'{sb.D}sr1_{name}_src.png'
        a = np.array(Image.open(p).convert('RGB'))
        box = a[y0:y1, x0:x1].astype(int)
        star = ndi.binary_dilation((box.min(axis=2) > 95) & (box.max(axis=2) < 235), iterations=1)
        ys = np.arange(y0, y1)[:, None].repeat(box.shape[1], 1)
        box[star] = np.where((ys[star] >= black_y)[:, None], [0, 0, 0], list(col))
        a[y0:y1, x0:x1] = box
        Image.fromarray(a.astype(np.uint8)).save(p)


# 배율을 얼굴로 재지 않고 다른 칸을 따라가는 샘플: 심검은 칼이 얼굴을 가림 (대기와 같은 해상도) · 피격은 고개를 젖힘 · 누운 쓰러짐은 얼굴이 안 보임 (셋 다 쓰러짐 1과 한 장)
FIXED_SC = {'sr1_gkcharge': 0.50}   # 얼굴 재기가 안 맞는 샘플: 극참 준비는 머리 옆 두 손을 얼굴로 잡아 1.5배로 커짐 → 몸 키를 대기와 눈으로 맞춤
SAME_SC = {'sr1_mind': 'sr1_idle', 'sr1_hurt': 'sr1_down1', 'sr1_down2': 'sr1_down1'}


def face(rgba):   # 얼굴 (넓이, 키) 샘플 px: 몸 위쪽 절반 안의 가장 큰 살색 덩어리
    c = rgba.astype(float); r, g, b, a = c[..., 0], c[..., 1], c[..., 2], c[..., 3]
    mx, mn = c[..., :3].max(axis=2), c[..., :3].min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1)
    skin = (a > 200) & (r >= g) & (g >= b - 5) & (sat > 0.15) & (sat < 0.6) & (mx > 150) & (r - b > 30)
    ys = np.where((a > 127).any(axis=1))[0]
    lab, n = ndi.label(skin)
    best = (0, 0)
    for j in range(1, n + 1):
        yy = np.where(lab == j)[0]
        if yy.mean() <= ys.min() + 0.5 * (ys.max() - ys.min() + 1) and len(yy) > best[0]: best = (len(yy), yy.max() - yy.min() + 1)
    return best


def face_scale(rgba, ref):   # 얼굴 넓이가 대기 칸(ref)과 같아지는 배율 (얼굴 키는 손·목이 붙으면 커져서 안 씀: 무참 4는 10% 크게 나옴)
    return (ref[0] / face(rgba)[0]) ** 0.5
# 테두리 정리(sb.DEFRINGE)는 쓰지 않음: 흰 머리 가장자리까지 깎아서 피격 머리에 구멍이 남. 흰 점은 fill_specks가 정리
sb.CARD.update({'sr1_hurt': (44, 178, 28, 207), 'sr1_down1': (50, 200, 238, 388), 'sr1_down2': (212, 414, 300, 388), 'sr1_gkcast': (0, 219, 0, 218)})   # 극참 시전: 아래 회색 줄   # 글자 줄 · 옆 그림 빼고
FRAMES = [('sr1_idle', 'big')] + [('sr1_walk', i) for i in range(4)] + [('sr1_atk0', 'big'), ('sr1_atk1', 'big'), ('sr1_cast', 'big')] + [(f'sr1_issen{i}', 'big') for i in (1, 2, 3)] + [(f'sr1_mucham{i}', 'big') for i in range(1, 8)] + [('sr1_draw', 'big'), ('sr1_mind', 'big'), ('sr1_hurt', 'big'), ('sr1_down1', 'big'), ('sr1_down2', 'big'), ('sr1_gkcharge', 'big'), ('sr1_gkcast', 'big')]


def fill_specks(p):   # 어두운 옷 위에 박힌 흰 점 (흰 배경이 비친 것): 밝은 이웃이 1개 이하인 밝은 점을 이웃 불투명 색의 중앙값으로 (칼날·머리카락은 이웃도 밝아서 그대로)
    q = p.copy(); H, W = p.shape[:2]
    lum = p[..., :3].min(axis=2).astype(int); op = p[..., 3] > 0
    for y, x in zip(*np.where(op & (lum > 190))):
        ys, xs = slice(max(0, y - 1), y + 2), slice(max(0, x - 1), x + 2)
        nb = op[ys, xs].copy(); nb[min(y, 1), min(x, 1)] = False
        if (lum[ys, xs][nb] > 160).sum() > 1: continue
        if p[y, x, 3] < 200: q[y, x, 3] = 0   # 반투명 테두리의 흰 점은 지움
        elif nb.sum() >= 5: q[y, x, :3] = np.median(p[ys, xs][nb][:, :3], axis=0)
    return q


def main():
    pieces = []
    scales = {}
    for src, pick in FRAMES + [('sr1_down1', 'big')]:   # 쓰러짐 1 배율은 피격보다 먼저 알아야 해서 한 번 더 잼
        if src in scales and src in SAME_SC.values(): continue
        rgba, _, h = sb.load(src, pick)
        if src == 'sr1_idle':
            scales[src] = sb.TARGET_H / h; area, fh = face(rgba); ref = (area * scales[src] ** 2, fh * scales[src])
        elif src not in SAME_SC: scales[src] = face_scale(rgba, ref)
    for src, pick in FRAMES:
        rgba, foot, h = sb.load(src, pick)
        sc = scales[SAME_SC.get(src, src)]
        if src in FIXED_SC: sc = FIXED_SC[src]
        p = fill_specks(sb.drop_light_edge(shrink(rgba, sc), src.startswith(('sr1_issen', 'sr1_mucham', 'sr1_draw', 'sr1_mind', 'sr1_gkcharge'))))   # 칼날의 밝은 회색을 지우지 않게
        pieces.append((p, foot * sc))
        print(f'{src}: 샘플 키 {h} ×{sc:.3f} → {p.shape[1]}x{p.shape[0]}')
    L = max(int(np.ceil(c)) for _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for p, c in pieces) + 4
    H = max(p.shape[0] for p, _ in pieces) + 5
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c)); y = H - 2 - p.shape[0]
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'swordsman_sr1 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} topH={pieces[0][0].shape[0]} count={len(pieces)}')


if __name__ == '__main__':
    if '--scrub-star' in sys.argv: scrub_stars()
    main()

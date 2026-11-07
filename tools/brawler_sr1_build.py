# 격투가 시크릿 레어 외형 1 (백호: 흰 줄무늬 호랑이·붉은 염주·붕대 손발·검은 바지·붉은 띠, 흰 배경 샘플)
#   → 나중에 캐릭터 시트 assets/sprites/merc/brawler_sr1.webp (칸 순서는 brawler_0과 같아야 함, tools/brawler_build.py 참고)
# 사용: python tools/brawler_sr1_build.py   (동작 샘플이 다 모일 때까지는 미리보기만 만듦: _preview_brawler_sr1_walk.gif)
# 샘플: assets/sprites/fx/samples/brawler_sr1_*_src.*
#   - idle_src.png  대기 (팔짱 낀 자세)
#   - walkA_src.webp · walkB_src.webp  걷기 후보 10장씩 (5×2 칸, 아래 번호 글자). A는 작고 팔 모양이 칸마다 들쑥날쑥(4·7·9 팔 들어 올림)
#     B는 그림이 크고 팔 모양이 일정함. B9·B10은 팔짱으로 넘어가는 칸이라 걷기엔 안 씀 (B10엔 발 쪽 회색 별 무늬도 있음)
#     B2~B5는 꼬리가 아래로 늘어지고 B6~B8은 꼬리를 말아 올려서, 섞으면 걸음마다 꼬리가 위아래로 튐 → 꼬리가 같은 B2~B5만 씀
#     → 걷기 = B2 (보폭 최대, 두 발 디딤) → B3 (보폭 줄며 몸이 내려감) → B4 (뒷발 들어 앞으로) → B5 (뒷발이 몸 밑을 지나감) → 다시 B2
#   - dash_src.png  대시 (앞으로 몸을 숙이고 달려 나감). 어두운 회색 배경(59,63,67) + 양옆에 옆 칸 조각
#     → 배경색과 8 이내인 픽셀을 가장자리부터 지우고 가장 큰 덩어리만 남김. 시트에선 brawler_0 칸 뒤에 한 칸 더 붙여 dashRun으로 씀
#       (불사조 SR처럼 대시 동안 이 칸, 기본 격투가는 대시 때 걷기 칸)
#   - armor_src.png  금강 두 칸 (연회색 배경 238~250). 기본 격투가는 슈퍼아머 1칸(24)이라 24 = 2번(힘줌), 1번(팔 모음)은 뒤에 한 칸 더 붙여
#     SR만 armor: [팔 모음, 24]로 씀 (두 팔 사이 갇힌 배경 구멍도 지움)
#   - down1_src.png · down2_src.png  쓰러짐 (흰 배경): 1 = 앞으로 고꾸라지며 한 손·무릎을 짚음 · 2 = 엎어져 누움(머리 오른쪽)
#     기본 격투가 6·7번 자리에 그대로 (둘 다 앞으로 넘어가 방향이 이어져서 뒤집지 않음)
#   - duel_src.png  결투 (한 주먹을 높이 치켜들고 포효, 어두운 회색 배경 + 왼쪽 아래 옆 칸 흙먼지 조각) → 25번 자리
#   - counter_src.png  반격 자세 (흰 배경, 낮게 서서 두 손을 갈고리처럼 앞에 모음) → 30번 자리. 귀 줄 폭으로 대기와 맞춤
#   - annprep_src.png  멸식 - 격 마무리 날아 차기 전 준비 자세 (흰 배경, 다리를 넓게 벌리고 낮게 웅크림)
#     기본 격투가는 멸식 마무리 준비에 섬각 준비(26)를 같이 씀 → SR은 뒤에 한 칸 더 붙여 anims.annPrep으로 따로 씀
#     (게임: brawlerPickFrame의 멸식 마무리 a.kick[0] → (a.annPrep || a.kick)[0])
#   - combo12_src.png  연격 1·2타 (흰 배경, 두 칸이 가로로 살짝 겹쳐 그려짐 → split_figs로 덩어리별로 나눔)
#     1 = 앞손 잽 (팔을 쭉 뻗음) → 8번 자리 · 2 = 뒷손을 끌어올리며 가드한 채 힘줌 → 10번 자리 (기본 연격 1타 [8] · 2타 [10])
#   - combo3_src.png  연격 3타 (흰 배경, 허리를 틀며 뒷손 정권 지르기). 기본 3타는 [21, 9] 두 칸 → SR은 한 칸이라 brawlChain을 SR용으로 따로 둠
#     배율: 원본 크기가 1·2타 샘플과 같아(키 143 vs 142) 1·2타 배율을 그대로 씀 (귀 줄 폭으론 ×0.54라 머리가 작아짐)
#   - combo4a_src.png · combo4b_src.png  연격 4타 두 칸 (흰 배경): a = 무릎을 높이 당겨 올림 · b = 중단 돌려차기 (다리를 쭉 뻗음)
#     기본 4타는 [22] 한 칸 → SR은 [a, b] 두 칸. a 왼쪽 끝 옆 칸 조각(0~6열)이 꼬리에 닿아 있어 그 열을 흰색으로 덮고 자름
#     배율: 둘 다 귀 줄 폭 (a ×0.62 = 1·2타와 같음 · b ×0.54는 차는 다리로 그림이 커져 원본 머리가 작게 그려진 것)
#   - combo5a_src.png · combo5b_src.png  연격 5타 두 칸 (흰 배경): a = 무릎을 가슴까지 당김(가드) · b = 앞차기 (두 손 가드를 턱에 붙인 채 다리를 비스듬히 위로 뻗음, 2026-11-08 교체)
#     b 오른쪽 끝 옆 칸 꼬리 조각은 떨어져 있어 가장 큰 덩어리만 남기면 빠짐. 배율은 귀 줄 폭
#   - combo6_src.png  연격 6타 두 칸 (흰 배경, 한 장에 나란히, 등을 보이며 돎): a = 등 돌려 무릎 듦 · b = 뒤돌려 옆차기
#     한 장에 같은 크기로 그린 것이라 두 칸 모두 a의 귀 줄 폭 배율을 같이 씀
#   - combo7a_src.png · combo7b_src.png  연격 7타 두 칸 (흰 배경): a = 몸을 웅크리며 무릎 당김 · b = 몸을 뒤로 젖히며 상단 뒤꿈치 차올리기
#     a는 귀 줄 폭. b는 차올린 발이 맨 위라 귀 줄로 못 재서 머리·디딘 다리 길이가 a와 같아지는 고정 배율 COMBO7B_SC
#   - combo8a_src.png · combo8b_src.png  연격 8타 두 칸 (흰 배경, 살짝 뛰어올라 침): a = 뛰기 전 발끝으로 웅크림 · b = 공중 앞차기
#     a 오른쪽 아래 번호 글자 '06'·b 오른쪽 끝 옆 칸 조각은 떨어져 있어 가장 큰 덩어리만 남기면 빠짐. 배율은 귀 줄 폭
#     b는 LIFT['c8b']만큼 바닥에서 띄움 (기본 격투가 날아 차기 10보다 낮게 '살짝')
# 흰 배경: 가장자리에서 이어진 흰 픽셀 + 꼬리·팔 사이에 갇힌 새하얀 구멍(무채색 253 안팎) 을 지움
#   (호랑이 흰 털은 푸른 기가 돌고(파랑이 빨강보다 ~6 높음) 238 안팎이라 남음)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/brawler_sr1_'
TARGET_H = 86   # 대기 자세 키 → brawler_0과 같은 칸 키
WALK = ['B2', 'B3', 'B4', 'B5']
ARMOR_SC = 0.50   # 금강은 정면이라 귀 줄 폭으로 재면 귀 끝 사이만 잡혀 얼굴이 커짐(×0.55). 같은 크기로 그린 대시 샘플 배율(×0.50)에 맞춘 고정값
ARMOR = [(0, 127), (127, 286)]
DUEL_SC = 0.45   # 결투 배율: 치켜든 주먹이 맨 위라 귀 줄로 못 재서, 머리·어깨~발 길이가 대기와 같아지는 값
ANNPREP_SC = 0.45   # 멸식 준비: 귀 줄 폭(×0.37)은 숙인 어깨가 섞여 머리가 작아짐 → 머리·염주 크기가 대기와 같아지는 값
COMBO7B_SC = 0.42
LIFT = {'c8b': 6}   # 칸 이름 → 바닥에서 띄울 높이 (게임 px)
DOWN_SC = 0.45   # 쓰러짐 두 칸 배율: 염주 알·머리 크기가 대기 칸과 같아지는 값 (누워 있어 귀 줄 폭으로는 못 잼)   # 금강 샘플 가로 범위: 1 = 두 팔을 머리 위로 모음 · 2 = 주먹 쥐고 양팔에 힘줌 (왼쪽 끝 옆 칸 조각은 가장 큰 덩어리만 남겨 빠짐)


def cells(name):   # 여러 칸 샘플 → {'B1': 그림, ...} (큰 덩어리를 줄·칸 순서로)
    im = np.array(Image.open(f'{D}walk{name}_src.webp').convert('RGB'))
    fg = im.min(axis=2) < 215
    lab, k = ndi.label(ndi.binary_dilation(fg, iterations=3))
    sz = ndi.sum(fg, lab, range(1, k + 1))
    objs = ndi.find_objects(lab)
    big = sorted([objs[i] for i in range(k) if sz[i] > 2000], key=lambda o: (o[0].start // 150, o[1].start))
    return {f'{name}{j + 1}': im[sl] for j, sl in enumerate(big)}


def cut(im):   # 흰 배경 지우고 가장 큰 덩어리(캐릭터)만 → RGBA, 외곽은 흰색과 섞인 만큼 반투명으로 풀어 줌
    im = im.astype(float)
    white = (im.min(axis=2) > 222) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    bgc = im[bg].mean(axis=0)
    for i in range(1, n + 1):   # 꼬리·팔 사이에 갇힌 배경 구멍 = 가장자리 배경과 색이 거의 같고 색차가 작은 곳
        m = lab == i
        if not bg[m].any() and m.sum() >= 20:   # 털은 푸른 기(색차 6~10)라 안 걸림. 금강 1 머리 위 구멍은 배경처럼 살짝 푸른 연회색(색차 3.8)
            px = im[m]
            if np.abs(px.mean(axis=0) - bgc).max() < 5 and (px.max(axis=1) - px.min(axis=1)).mean() < 4.5: bg |= m
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
    sz = ndi.sum(m, lab, range(1, n + 1))
    a = np.where(lab == 1 + int(np.argmax(sz)), a, 0)
    a = np.where(a < 0.12, 0, a)
    ys, xs = np.where(a > 0)
    return np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def cut_dark(im, bgc=(59, 63, 67), tol=8):   # 어두운 단색 배경 샘플 (외곽선이 배경보다 훨씬 어두워 반투명 처리 없이 딱 자름)
    im = im.astype(int)
    near = np.abs(im - bgc).max(axis=2) <= tol
    lab, n = ndi.label(near)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    for i in range(1, n + 1):   # 꼬리·팔 사이에 갇힌 배경
        m = lab == i
        if not bg[m].any() and m.sum() >= 15: bg |= m
    lab, n = ndi.label(~bg)
    keep = lab == 1 + int(np.argmax(ndi.sum(~bg, lab, range(1, n + 1))))
    ys, xs = np.where(keep)
    return np.dstack([im, keep * 255]).astype(float)[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def split_figs(im, n=2):   # 한 장에 붙어 그린 여러 칸 → 칸마다 다른 그림을 흰색으로 덮은 사본 (왼쪽부터). 칸끼리 가로로 겹쳐도 덩어리로 나눔
    fg = im.astype(int).min(axis=2) < 230
    lab, k = ndi.label(fg)
    sz = ndi.sum(fg, lab, range(1, k + 1))
    big = sorted(np.argsort(-sz)[:n] + 1, key=lambda i: np.where(lab == i)[1].mean())
    out = []
    for i in big:
        o = im.copy(); o[ndi.binary_dilation(fg & (lab != i), iterations=2) & ~(lab == i)] = 255
        out.append(o)
    return out


def head(rgba):   # 귀 높이 줄(위 2~7%)의 최대 폭 · 가운데 x. 더 내려가면 숙인 자세(대시)에서 어깨·팔이 섞여 머리가 크게 잡힘
    k = rgba[..., 3] > 127
    rows = [np.where(k[y])[0] for y in range(int(k.shape[0] * .02), int(k.shape[0] * .07) + 1)]
    rows = [r for r in rows if len(r)]
    return max(r.max() - r.min() + 1 for r in rows), float(np.mean([(r.max() + r.min()) / 2 for r in rows]))


def main():
    idle = cut(np.array(Image.open(f'{D}idle_src.png').convert('RGB')))
    sc0 = TARGET_H / idle.shape[0]
    hw0 = head(idle)[0] * sc0
    src = {**cells('A'), **cells('B')}
    frames = []
    for nm in WALK:   # 걷기는 머리 폭을 대기와 같게, 기준점은 머리 가운데 (걸을 때 몸이 좌우로 흔들리지 않게)
        r = cut(src[nm]); hw, hcx = head(r); sc = hw0 / hw
        frames.append((shrink(r, sc), hcx * sc))
        print(f'{nm}: {r.shape[1]}x{r.shape[0]} ×{sc:.3f}')
    preview(frames, '_preview_brawler_sr1_walk.gif')
    r = cut_dark(np.array(Image.open(f'{D}dash_src.png').convert('RGB')))
    hw, hcx = head(r); sc = hw0 / hw
    print(f'dash: {r.shape[1]}x{r.shape[0]} ×{sc:.3f} → {shrink(r, sc).shape[:2]}')
    preview(frames + [(shrink(r, sc), hcx * sc)] * 3, '_preview_brawler_sr1_dash.gif')   # 걷다가 대시
    full = np.array(Image.open(f'{D}armor_src.png').convert('RGB'))
    arm = []
    for x0, x1 in ARMOR:
        r = cut(full[:, x0:x1]); hcx = head(r)[1]; sc = ARMOR_SC
        arm.append((shrink(r, sc), hcx * sc))
        print(f'armor {x0}~{x1}: {r.shape[1]}x{r.shape[0]} ×{sc:.3f} → {arm[-1][0].shape[:2]}')
    idle_p = shrink(idle, sc0)
    preview([(idle_p, head(idle)[1] * sc0)] * 2 + arm[:1] * 2 + arm[1:] * 6, '_preview_brawler_sr1_armor.gif')   # 대기 → 팔 들어 기 모음 → 힘줌
    down = []
    for n in ('down1', 'down2'):   # 기준점 = 엉덩이(띠) 자리 대신 그림 가로 가운데 · 쓰러질 때 몸이 앞으로 밀려 나가 보이게
        r = cut(np.array(Image.open(f'{D}{n}_src.png').convert('RGB')))
        p = shrink(r, DOWN_SC); down.append((p, p.shape[1] / 2))
        print(f'{n}: {r.shape[1]}x{r.shape[0]} → {p.shape[:2]}')
    preview([(idle_p, head(idle)[1] * sc0)] * 2 + down[:1] * 2 + down[1:] * 6, '_preview_brawler_sr1_down.gif')
    r = cut_dark(np.array(Image.open(f'{D}duel_src.png').convert('RGB')), tol=10)
    p = shrink(r, DUEL_SC)
    k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]   # 기준점 = 두 발 가운데
    print(f'duel: {r.shape[1]}x{r.shape[0]} → {p.shape[:2]}')
    preview([(idle_p, head(idle)[1] * sc0)] * 2 + [(p, (xs.min() + xs.max()) / 2)] * 4, '_preview_brawler_sr1_duel.gif')
    r = cut(np.array(Image.open(f'{D}counter_src.png').convert('RGB')))
    hw, hcx = head(r); sc = hw0 / hw
    print(f'counter: {r.shape[1]}x{r.shape[0]} ×{sc:.3f} → {shrink(r, sc).shape[:2]}')
    preview([(idle_p, head(idle)[1] * sc0)] * 2 + [(shrink(r, sc), hcx * sc)] * 4, '_preview_brawler_sr1_counter.gif')
    r = cut(np.array(Image.open(f'{D}annprep_src.png').convert('RGB')))
    p = shrink(r, ANNPREP_SC)
    k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]   # 기준점 = 두 발 가운데
    print(f'annprep: {r.shape[1]}x{r.shape[0]} → {p.shape[:2]}')
    preview([(idle_p, head(idle)[1] * sc0)] * 2 + [(p, (xs.min() + xs.max()) / 2)] * 4, '_preview_brawler_sr1_annprep.gif')
    combo = {}
    for nm, f in zip(('c1', 'c2'), split_figs(np.array(Image.open(f'{D}combo12_src.png').convert('RGB')))):
        r = cut(f); hw = head(r)[0]; sc = hw0 / hw; p = shrink(r, sc)
        k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]   # 기준점 = 두 발 가운데
        combo[nm] = (p, (xs.min() + xs.max()) / 2)
        print(f'{nm}: {r.shape[1]}x{r.shape[0]} ×{sc:.3f} → {p.shape[:2]}')
    r = cut(np.array(Image.open(f'{D}combo3_src.png').convert('RGB'))); p = shrink(r, sc)   # sc = 1·2타 배율
    k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]
    combo['c3'] = (p, (xs.min() + xs.max()) / 2)
    print(f'c3: {r.shape[1]}x{r.shape[0]} ×{sc:.3f} → {p.shape[:2]}')
    for nm in ('4a', '4b', '5a', '5b', '8a', '8b'):
        im = np.array(Image.open(f'{D}combo{nm}_src.png').convert('RGB'))
        if nm == '4a': im[:, :7] = 255
        r = cut(im); sc4 = hw0 / head(r)[0]; p = shrink(r, sc4)
        k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]   # 기준점 = 디딘 발 (한 발 들어서 맨 아래 줄 = 디딘 발)
        combo['c' + nm] = (p, (xs.min() + xs.max()) / 2, LIFT.get('c' + nm, 0))
        print(f'c{nm}: {r.shape[1]}x{r.shape[0]} ×{sc4:.3f} → {p.shape[:2]}')
    for nm in ('7a', '7b'):
        r = cut(np.array(Image.open(f'{D}combo{nm}_src.png').convert('RGB')))
        sc7 = hw0 / head(r)[0] if nm == '7a' else COMBO7B_SC; p = shrink(r, sc7)
        k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]
        combo['c' + nm] = (p, (xs.min() + xs.max()) / 2)
        print(f'c{nm}: {r.shape[1]}x{r.shape[0]} ×{sc7:.3f} → {p.shape[:2]}')
    sc6 = None
    for nm, f in zip(('6a', '6b'), split_figs(np.array(Image.open(f'{D}combo6_src.png').convert('RGB')))):
        r = cut(f); sc6 = sc6 or hw0 / head(r)[0]; p = shrink(r, sc6)
        k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]
        combo['c' + nm] = (p, (xs.min() + xs.max()) / 2)
        print(f'c{nm}: {r.shape[1]}x{r.shape[0]} ×{sc6:.3f} → {p.shape[:2]}')
    preview([(idle_p, head(idle)[1] * sc0)] * 2 + [combo['c1']] * 2 + [combo['c2']] * 2 + [combo['c3']] * 3 + [combo['c4a']] * 2 + [combo['c4b']] * 3 + [combo['c5a']] * 2 + [combo['c5b']] * 3 + [combo['c6a']] * 2 + [combo['c6b']] * 3 + [combo['c7a']] * 2 + [combo['c7b']] * 3 + [combo['c8a']] * 2 + [combo['c8b']] * 3, '_preview_brawler_sr1_combo.gif')


def preview(frames, out):   # frames: (그림, 기준점 x[, 바닥에서 띄울 높이])
    frames = [f if len(f) == 3 else (*f, 0) for f in frames]
    L = max(c for _, c, _ in frames) + 6; R = max(p.shape[1] - c for p, c, _ in frames) + 6
    H = max(p.shape[0] + lift for p, _, lift in frames) + 4
    gif = []
    for p, c, lift in frames:
        cv = Image.new('RGBA', (int(L + R), H), (70, 90, 70, 255))
        cv.alpha_composite(Image.fromarray(p), (int(round(L - c)), H - 2 - p.shape[0] - lift))
        gif.append(cv.resize((cv.width * 3, cv.height * 3), Image.NEAREST).convert('RGB'))
    gif[0].save(out, save_all=True, append_images=gif[1:], duration=150, loop=0)


if __name__ == '__main__':
    main()

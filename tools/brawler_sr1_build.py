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
#   - finprep_src.webp · finkick_src.webp  멸식 - 격 마지막 일격 (SR 전용, 흰 배경 큰 그림, 뒷모습): 막타 뒤 한 번 더 주먹을 당긴 준비 자세 → 강하게 날아 차기
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
#   - combo9a_src.png  연격 9타 첫 칸: 8타 점프에서 내려와 자세를 잡음 (어두운 회색 배경). 9타 지르기 그림은 3타 샘플과 똑같아(픽셀 차이 0) 3타 칸을 다시 씀
#     배율 COMBO9A_SC: 귀 줄 폭(×0.54)은 머리만 잘라 비교하면 대기보다 작아 0.58
#   - combo10_src.png  연격 10타 (막타) 공중 날아 차기 (투명 배경 PNG → load_flat으로 흰색 위에 깔고 자름). 2026-11-08 교체본, LIFT 20 (기본 날아 차기 10의 두 배)
#   - land_src.png  막타 뒤 착지 (흰 배경, 낮게 웅크려 내려앉음) → 33번 자리. 10타 날아 차기 → 착지 → 평소 자세
#     배율: 머리만 잘라 대기와 맞춤 (날아 차기 KICK10_SC 0.56 · 착지 FINISH_SC 0.62, 착지 귀 줄 폭 ×0.59는 살짝 작음)
# 게임 반영 때 할 일 (사용자 지시, 2026-11-08):
#   - 연격 9타: 착지(9a) → 지르기(3타 칸)로 치면서 대상을 뚫고 지나가, 10타를 칠 거리만큼 멀리 이동
#     (기본 격투가는 10타 날아 차기에서 관통함 = BRAWLER_PASS_DIST·BRAWLER_PASS_TICKS. SR은 9타에서 관통 → 10타는 그 거리에서 다시 들어오며 침)
# 흰 배경: 가장자리에서 이어진 흰 픽셀 + 꼬리·팔 사이에 갇힌 새하얀 구멍(무채색 253 안팎) 을 지움
#   (호랑이 흰 털은 푸른 기가 돌고(파랑이 빨강보다 ~6 높음) 238 안팎이라 남음)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))


def shrink(rgba, sc):   # 축소: 색은 LANCZOS(얇은 검은 외곽선이 살아남음), 모양(알파)은 면적 평균 절반 이상인 칸만
    # berserker_build.shrink처럼 알파까지 LANCZOS로 정하면 외곽선 바깥에 밝은 고리가 남아 흰 테두리처럼 보이고,
    # 색까지 면적 평균으로 하면 1~2px 외곽선이 털 색에 묻혀 흰 털이 그대로 테두리가 됨
    h, w = rgba.shape[:2]
    size = (max(1, round(w * sc)), max(1, round(h * sc)))
    pm = rgba.astype(float).copy(); pm[..., :3] *= pm[..., 3:] / 255
    pim = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA')
    lz = np.array(pim.resize(size, Image.LANCZOS)).astype(float)
    bx = np.array(pim.resize(size, Image.BOX)).astype(float)
    out = np.zeros_like(lz)
    la = lz[..., 3:]
    out[..., :3] = np.where(la > 8, lz[..., :3] * 255 / np.maximum(la, 1), bx[..., :3] * 255 / np.maximum(bx[..., 3:], 1))
    out[..., 3] = np.where(bx[..., 3] >= 128, 255, 0)
    bxc = bx[..., :3] * 255 / np.maximum(bx[..., 3:], 1)
    edge = (out[..., 3] > 0) & ndi.binary_dilation(out[..., 3] == 0)   # 맨 바깥 줄만: 두 색 중 어두운 쪽 (LANCZOS 알파가 얇은 칸은 색이 부풀어 흰 점이 됨)
    out[..., :3] = np.where(edge[..., None], np.minimum(out[..., :3], bxc), out[..., :3])
    for _ in range(2):   # 바깥으로 1칸 튀어나온 밝은 픽셀(이웃 불투명 1칸 이하) 제거
        op = out[..., 3] > 0
        nb = ndi.convolve(op.astype(int), np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]), mode='constant')
        out[..., 3] = np.where(op & (nb <= 1) & (out[..., :3].min(axis=2) > 100), 0, out[..., 3])
    op = out[..., 3] > 0   # 맨 바깥 줄의 밝은 픽셀(흰 찌꺼기·외곽선이 묻힌 흰 털) → 외곽선 색(33,34,35) 쪽으로 어둡게 (모양은 그대로)
    edge = op & ndi.binary_dilation(~op)
    lit = edge & (out[..., :3].min(axis=2) > 100)
    out[..., :3] = np.where(lit[..., None], out[..., :3] * 0.3 + np.array([33, 34, 35]) * 0.7, out[..., :3])
    op = out[..., 3] > 0   # 3픽셀 이하 떨어진 티끌 제거
    lab, n = ndi.label(op, structure=np.ones((3, 3)))
    sizes = ndi.sum(op, lab, range(1, n + 1))
    out[..., 3] = np.where(np.isin(lab, 1 + np.where(sizes <= 3)[0]), 0, out[..., 3])
    return out.clip(0, 255).astype(np.uint8)


D = 'assets/sprites/fx/samples/brawler_sr1_'
TARGET_H = 86   # 대기 자세 키 → brawler_0과 같은 칸 키
WALK = ['B2', 'B3', 'B4', 'B5']
ARMOR = [(0, 127), (127, 286)]   # 금강 샘플 가로 범위: 1 = 두 팔을 머리 위로 모음 · 2 = 주먹 쥐고 양팔에 힘줌
LIFT = {'c8b': 6, 'c10': 20, 'finkick': 16}   # 칸 이름 → 바닥에서 띄울 높이 (게임 px)
# 칸별 배율 (원본 px → 게임 px) — 얼굴 크기를 대기 칸과 같게 (2026-11-08 '크기 비율 통일')
#   재는 법: 대기 칸 머리(염주 위)를 본으로 잘라 배율·좌우·기울기를 바꿔 가며 정규화 상호상관이 가장 큰 배율을 찾음
#   (확신 0.8 이상이면 그 값, 낮은 칸은 귀 줄 폭 값과 같은 원본에서 그린 칸의 값으로 정함). 귀 줄 폭은 대체로 맞았고
#   눈대중으로 고쳤던 칸(멸식 준비·3타·9타 착지·10타·쓰러짐)이 10~20% 크게 들어가 있었음
SCALE = {
    'armor1': 0.562, 'armor2': 0.562,        # 금강 2 머리 일치 0.90 · 금강 1은 같은 장에 같은 크기로 그림
    'down1': 0.383, 'down2': 0.383,          # 쓰러짐 1 기울인 본 일치 0.64 · 2는 같은 묶음 샘플
    'duel': 0.45,                            # 머리를 젖혀 일치 낮음 → 허리·띠 본 일치 0.70 값
    'finprep': 0.125, 'finkick': 0.125,      # 멸식 마지막 일격 (뒷모습, 1024×765 큰 샘플): 머리 일치 낮음(0.41) → 귀 줄 0.123 · 같은 뒷모습 6타와 머리·몸통 비교
    'counter': 0.445, 'annprep': 0.371, 'hurt': 0.47,   # 피격: 머리 일치 0.93 (귀 줄 0.467)
    'c1': 0.607, 'c2': 0.607, 'c3': 0.545, 'c4a': 0.607, 'c4b': 0.539, 'c5a': 0.475, 'c5b': 0.365,
    'c6a': 0.59, 'c6b': 0.59,                # 뒷모습이라 본 일치 낮음 → 귀 줄 폭(0.604)에서 앞모습 칸들의 차이(-2.5%)만큼
    'c7a': 0.43, 'c7b': 0.43,                # 7a 귀 줄 0.453 · 기울인 본 0.408의 가운데, 7b 머리 일치 0.73
    'c8a': 0.598, 'c8b': 0.607, 'c9a': 0.536, 'c10': 0.462, 'land': 0.589,
}


def cells(name):   # 여러 칸 샘플 → {'B1': 그림, ...} (큰 덩어리를 줄·칸 순서로)
    im = np.array(Image.open(f'{D}walk{name}_src.webp').convert('RGB'))
    fg = im.min(axis=2) < 215
    lab, k = ndi.label(ndi.binary_dilation(fg, iterations=3))
    sz = ndi.sum(fg, lab, range(1, k + 1))
    objs = ndi.find_objects(lab)
    big = sorted([objs[i] for i in range(k) if sz[i] > 2000], key=lambda o: (o[0].start // 150, o[1].start))
    return {f'{name}{j + 1}': im[sl] for j, sl in enumerate(big)}


def load_flat(path):   # 투명 PNG도 흰 배경 위에 깐 RGB로
    im = Image.open(path).convert('RGBA'); bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
    return np.array(bg.convert('RGB'))


def cut(im):   # 흰 배경 지우고 가장 큰 덩어리(캐릭터)만 → RGBA (도트 그림이라 반투명 없이 딱 자름)
    # 1) 가장자리에서 이어진 흰 배경
    # 2) 갇힌 큰 배경 구멍: 가장자리 배경과 색이 거의 같고 색차가 작은 곳 (털은 푸른 기 색차 6~10이라 안 걸림, 금강 1 머리 위 구멍은 색차 3.8)
    #    (색이 아니라 '검은 선에 갇힌 밝은 덩어리'로 찾으면 줄무늬 사이 흰 털까지 지워짐 — 4타 무릎 칸 머리 털이 무채색 흰색)
    #    + 색차 3.5 미만 무채색 구멍 중 둘레 40% 이상이 검은 선인 것 (털은 푸른 기 4 이상이거나 둘레가 털이라 안 걸림)
    # 3) 테두리·구멍 둘레 찌꺼기: 배경에 닿은 밝은 무채색 2겹 벗김
    im = im.astype(float)
    mn, ch = im.min(axis=2), im.max(axis=2) - im.min(axis=2)
    white = (mn > 222) & (ch < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    bgc = im[bg].mean(axis=0)
    for i in range(1, n + 1):
        m = lab == i
        if not bg[m].any() and m.sum() >= 4:   # 다리·팔 사이 작은 구멍까지
            px = im[m]
            pch = (px.max(axis=1) - px.min(axis=1)).mean()
            if np.abs(px.mean(axis=0) - bgc).max() < 5 and pch < 4.5: bg |= m
            elif pch < 3.5:   # 배경색보다 살짝 어두운 무채색 구멍(다리·팔 사이, 249 vs 254 등): 둘레 2px의 40% 이상이 검은 외곽선이면 배경
                ring = ndi.binary_dilation(m, iterations=2) & ~m
                if (mn[ring] < 100).mean() >= 0.4: bg |= m
    rimc = (mn > 110) & (ch < 7)   # 흰 배경과 외곽선이 섞인 회색
    for _ in range(2):
        bg |= ndi.binary_dilation(bg) & rimc
    a = np.where(bg, 0.0, 1.0)
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
    sz = ndi.sum(m, lab, range(1, n + 1))
    a = np.where(lab == 1 + int(np.argmax(sz)), a, 0)
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
    idle_p = shrink(idle, sc0)
    ki = idle_p[..., 3] > 127; fx = np.where(ki[int(ki.shape[0] * .9):].any(axis=0))[0]
    idle_c = (fx.min() + fx.max()) / 2   # 대기 기준점 = 두 발 가운데
    dx = head(idle)[1] * sc0 - idle_c    # 대기 칸의 머리 가운데 - 발 가운데 (머리 기준 칸들은 머리가 이만큼 앞에 오게)
    F = {'idle': (idle_p, idle_c, 0)}    # 시트에 넣을 칸: 이름 → (그림, 기준점 x, 띄울 높이)
    src = {**cells('A'), **cells('B')}
    frames = []
    for nm in WALK:   # 걷기는 머리 폭을 대기와 같게, 기준점은 머리 가운데 (걸을 때 몸이 좌우로 흔들리지 않게)
        r = cut(src[nm]); hw, hcx = head(r); sc = hw0 / hw
        frames.append((shrink(r, sc), hcx * sc - dx))
        print(f'{nm}: {r.shape[1]}x{r.shape[0]} ×{sc:.3f}')
    for i, f in enumerate(frames): F[f'walk{i + 1}'] = (*f, 0)
    preview(frames, '_preview_brawler_sr1_walk.gif')
    r = cut_dark(np.array(Image.open(f'{D}dash_src.png').convert('RGB')))
    hw, hcx = head(r); sc = hw0 / hw
    print(f'dash: {r.shape[1]}x{r.shape[0]} ×{sc:.3f} → {shrink(r, sc).shape[:2]}')
    F['dash'] = (shrink(r, sc), hcx * sc - dx, 0)
    preview(frames + [F['dash']] * 3, '_preview_brawler_sr1_dash.gif')   # 걷다가 대시
    full = np.array(Image.open(f'{D}armor_src.png').convert('RGB'))
    arm = []
    for x0, x1 in ARMOR:
        r = cut(full[:, x0:x1]); hcx = head(r)[1]; sc = SCALE[f'armor{len(arm) + 1}']
        arm.append((shrink(r, sc), hcx * sc - dx))
        F[f'armor{len(arm)}'] = (*arm[-1], 0)
        print(f'armor {x0}~{x1}: {r.shape[1]}x{r.shape[0]} ×{sc:.3f} → {arm[-1][0].shape[:2]}')
    preview([F['idle']] * 2 + arm[:1] * 2 + arm[1:] * 6, '_preview_brawler_sr1_armor.gif')   # 대기 → 팔 들어 기 모음 → 힘줌
    down = []
    for n in ('down1', 'down2'):   # 기준점 = 엉덩이(띠) 자리 대신 그림 가로 가운데 · 쓰러질 때 몸이 앞으로 밀려 나가 보이게
        r = cut(np.array(Image.open(f'{D}{n}_src.png').convert('RGB')))
        p = shrink(r, SCALE[n]); down.append((p, p.shape[1] / 2)); F[n] = (*down[-1], 0)
        print(f'{n}: {r.shape[1]}x{r.shape[0]} → {p.shape[:2]}')
    preview([F['idle']] * 2 + down[:1] * 2 + down[1:] * 6, '_preview_brawler_sr1_down.gif')
    r = cut_dark(np.array(Image.open(f'{D}duel_src.png').convert('RGB')), tol=10)
    p = shrink(r, SCALE['duel'])
    k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]   # 기준점 = 두 발 가운데
    print(f'duel: {r.shape[1]}x{r.shape[0]} → {p.shape[:2]}')
    F['duel'] = (p, (xs.min() + xs.max()) / 2, 0)
    preview([F['idle']] * 2 + [F['duel']] * 4, '_preview_brawler_sr1_duel.gif')
    r = cut(np.array(Image.open(f'{D}counter_src.png').convert('RGB')))
    hcx = head(r)[1]; sc = SCALE['counter']
    print(f'counter: {r.shape[1]}x{r.shape[0]} ×{sc:.3f} → {shrink(r, sc).shape[:2]}')
    F['counter'] = (shrink(r, sc), hcx * sc - dx, 0)
    preview([F['idle']] * 2 + [F['counter']] * 4, '_preview_brawler_sr1_counter.gif')
    r = cut(np.array(Image.open(f'{D}annprep_src.png').convert('RGB')))
    p = shrink(r, SCALE['annprep'])
    k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]   # 기준점 = 두 발 가운데
    print(f'annprep: {r.shape[1]}x{r.shape[0]} → {p.shape[:2]}')
    F['annprep'] = (p, (xs.min() + xs.max()) / 2, 0)
    preview([F['idle']] * 2 + [F['annprep']] * 4, '_preview_brawler_sr1_annprep.gif')
    combo = {}
    for nm, f in zip(('c1', 'c2'), split_figs(np.array(Image.open(f'{D}combo12_src.png').convert('RGB')))):
        r = cut(f); sc = SCALE[nm]; p = shrink(r, sc)
        k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]   # 기준점 = 두 발 가운데
        combo[nm] = (p, (xs.min() + xs.max()) / 2)
        print(f'{nm}: {r.shape[1]}x{r.shape[0]} ×{sc:.3f} → {p.shape[:2]}')
    sc = SCALE['c3']; r = cut(np.array(Image.open(f'{D}combo3_src.png').convert('RGB'))); p = shrink(r, sc)
    k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]
    combo['c3'] = (p, (xs.min() + xs.max()) / 2)
    print(f'c3: {r.shape[1]}x{r.shape[0]} ×{sc:.3f} → {p.shape[:2]}')
    for nm in ('4a', '4b', '5a', '5b', '8a', '8b'):
        im = np.array(Image.open(f'{D}combo{nm}_src.png').convert('RGB'))
        if nm == '4a': im[:, :7] = 255
        r = cut(im); sc4 = SCALE['c' + nm]; p = shrink(r, sc4)
        k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]   # 기준점 = 디딘 발 (한 발 들어서 맨 아래 줄 = 디딘 발)
        combo['c' + nm] = (p, (xs.min() + xs.max()) / 2, LIFT.get('c' + nm, 0))
        print(f'c{nm}: {r.shape[1]}x{r.shape[0]} ×{sc4:.3f} → {p.shape[:2]}')
    for nm in ('7a', '7b'):
        r = cut(np.array(Image.open(f'{D}combo{nm}_src.png').convert('RGB')))
        sc7 = SCALE['c' + nm]; p = shrink(r, sc7)
        k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]
        combo['c' + nm] = (p, (xs.min() + xs.max()) / 2)
        print(f'c{nm}: {r.shape[1]}x{r.shape[0]} ×{sc7:.3f} → {p.shape[:2]}')
    r = cut_dark(np.array(Image.open(f'{D}combo9a_src.png').convert('RGB')), tol=10); p = shrink(r, SCALE['c9a'])
    k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]
    combo['c9a'] = (p, (xs.min() + xs.max()) / 2)
    print(f'c9a: {r.shape[1]}x{r.shape[0]} ×{SCALE['c9a']:.3f} → {p.shape[:2]}')
    for nm, f in (('c10', 'combo10'), ('land', 'land')):
        sc10 = SCALE[nm]
        r = cut(load_flat(f'{D}{f}_src.png')); p = shrink(r, sc10)
        k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]
        combo[nm] = (p, (xs.min() + xs.max()) / 2 if nm == 'land' else p.shape[1] / 2, LIFT.get(nm, 0))
        print(f'{nm}: {r.shape[1]}x{r.shape[0]} ×{sc10:.3f} → {p.shape[:2]}')
    sc6 = None
    for nm, f in zip(('6a', '6b'), split_figs(np.array(Image.open(f'{D}combo6_src.png').convert('RGB')))):
        r = cut(f); sc6 = SCALE['c' + nm]; p = shrink(r, sc6)
        k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]
        combo['c' + nm] = (p, (xs.min() + xs.max()) / 2)
        print(f'c{nm}: {r.shape[1]}x{r.shape[0]} ×{sc6:.3f} → {p.shape[:2]}')
    preview([F['idle']] * 2 + [combo['c1']] * 2 + [combo['c2']] * 2 + [combo['c3']] * 3 + [combo['c4a']] * 2 + [combo['c4b']] * 3 + [combo['c5a']] * 2 + [combo['c5b']] * 3 + [combo['c6a']] * 2 + [combo['c6b']] * 3 + [combo['c7a']] * 2 + [combo['c7b']] * 3 + [combo['c8a']] * 2 + [combo['c8b']] * 3 + [combo['c9a']] * 2 + [combo['c3']] * 3 + [combo['c10']] * 3 + [combo['land']] * 3, '_preview_brawler_sr1_combo.gif')
    for k_, v in combo.items(): F[k_] = v if len(v) == 3 else (*v, 0)
    im = load_flat(f'{D}hurt_src.png').copy(); im[:70, :4] = 255; im[:62, 4:6] = 255   # 왼쪽 끝 옆 칸 조각 (꼬리 끝에 닿아 있음)
    r = cut(im); p = shrink(r, SCALE['hurt'])   # 피격 (몸을 젖히며 한 손을 들어 막음, 흰 배경)
    k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]
    F['hurt'] = (p, (xs.min() + xs.max()) / 2, 0)
    print(f'hurt: {r.shape[1]}x{r.shape[0]} ×{SCALE["hurt"]:.3f} → {p.shape[:2]}')
    for nm in ('finprep', 'finkick'):   # 멸식 마지막 일격 (SR 전용): 한 번 더 준비 자세 → 강하게 날아 차기
        r = cut(load_flat(f'{D}{nm}_src.webp')); p = shrink(r, SCALE[nm])
        k = p[..., 3] > 127; xs = np.where(k[int(k.shape[0] * .9):].any(axis=0))[0]
        F[nm] = (p, (xs.min() + xs.max()) / 2 if nm == 'finprep' else p.shape[1] / 2, LIFT.get(nm, 0))
        print(f'{nm}: {r.shape[1]}x{r.shape[0]} ×{SCALE[nm]:.3f} → {p.shape[:2]}')
    build_sheet(F)


# 시트 칸 순서 (brawler_0과 같은 번호 + 뒤에 SR 전용 칸). 아직 샘플이 없는 동작은 가장 비슷한 백호 칸으로 채움
SHEET = ['idle', 'walk1', 'walk2', 'walk3', 'walk4',
         'hurt',                    # 5 피격
         'down1', 'down2',
         'c1', 'c2', 'c3', 'c4a', 'c4b', 'c5a', 'c5b', 'c6a', 'c6b', 'c7a', 'c7b', 'c8a', 'c8b', 'c9a',   # 8~21 연격 (SR brawlChain)
         'c1', 'c2',                # 22~23 안 씀 (0번 칸 수 맞춤)
         'armor2', 'duel',          # 24 금강(힘줌) · 25 결투
         'annprep', 'c10',          # 26 섬각 준비(샘플 없음 → 멸식 준비 웅크림) · 27 날아 차기 (섬각·반격·연격 10타)
         'c2', 'c3',                # 28~29 붕권: 샘플 없음 → 2타(주먹 당김) → 3타(정권)
         'counter', 'armor2',       # 30 반격 · 31 멸식 시전: 샘플 없음 → 금강 힘줌
         'c10', 'land',             # 32 멸식 마무리 날아 차기 · 33 착지
         'armor1', 'annprep', 'dash',   # 34 금강 팔 모음 · 35 멸식 마무리 준비 (annPrep) · 36 대시 (dashRun)
         'finprep', 'finkick']          # 37 멸식 마지막 일격 준비 (annPrep2) · 38 마지막 일격 날아 차기 (annFinal)
OUT = 'assets/sprites/merc/brawler_sr1.webp'


def build_sheet(F):
    pieces = [F[n] for n in SHEET]
    L = int(np.ceil(max(c for _, c, _ in pieces))) + 3
    R = int(np.ceil(max(p.shape[1] - c for p, c, _ in pieces))) + 3
    H = max(p.shape[0] + lift for p, _, lift in pieces) + 4
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (p, c, lift) in enumerate(pieces):
        x = i * cw + L - int(round(c)); y = H - 2 - p.shape[0] - lift
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = np.maximum(sheet[y:y + p.shape[0], x:x + p.shape[1]], p)
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    ip = F['idle'][0]; topH = ip.shape[0]
    print(f'시트 {OUT}: 칸 {len(pieces)}개 · cellW {cw} · cellH {H} · anchorX {L} · anchorY {H - 2} · 대기 키 {topH}')


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

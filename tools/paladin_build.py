# 성기사 전용 샘플(은발 땋은 머리·파란 십자 방패·전쟁 망치, 흰 배경 한 장씩) → 캐릭터 시트 assets/sprites/merc/paladin_0.webp
# 사용: python tools/paladin_build.py   (샘플은 assets/sprites/fx/samples/paladin_*_src.png, 동작 샘플이 오는 대로 FRAMES에 늘림)
# 칸 순서 (동작 샘플이 오는 대로 늘림): 0 대기 · 1~4 걷기 · 5 피격 · 6~8 쓰러짐 (서서 뒤로 젖힘 → 무릎 꿇음 → 엎어짐) · 9~10 기본 공격 (망치 치켜들기 → 내리치기) · 11~13 심판 (망치 뒤로 당김 → 머리 위로 치켜듦 → 땅에 내리찍음) · 14~15 신성 보호 (방패를 앞으로 → 방패를 머리 위로 들어 올림) · 16 성스러운 돌격 (방패를 앞세워 달림, 발 뒤 흙먼지 꼬리 포함) · 17 축성 (두 손 모아 기도) · 18~19 불굴의 가호 (망치 치켜들고 버팀 = 시전 막대 동안 → 방패를 머리 위로 들고 외침 = 발동)
# 이펙트: 심판 금빛 빛기둥 + 땅 폭발 → assets/sprites/fx/paladin_judgment.webp (어두운 배경 샘플, build_judgment_fx)
#   성스러운 돌격 충돌 폭발 → fx/paladin_charge_hit.webp, 멈춘 자리 흙먼지·반짝임 → fx/paladin_charge_dust.webp (build_charge_fx)
#   축성 시전 막대 동안 금빛 마법진 → fx/paladin_consec_cast.webp, 발동 때 빛줄기·깃털 → fx/paladin_consec_burst.webp (build_consecrate_fx)
#   신성 보호 바닥 마법진 → fx/paladin_hs_circle.webp, 시전자 보호막(문양 반구) → fx/paladin_hs_cast.webp, 아군 보호막(맑은 반구) → fx/paladin_hs_ally.webp (build_holy_shield_fx)
#   불굴의 가호 시전 앞쪽 마법진 → fx/paladin_aegis_cast0.webp, 시전 뒤쪽 날개·검 → fx/paladin_aegis_cast1.webp, 발동 빛기둥 → fx/paladin_aegis_burst.webp,
#     가호 받은 아군 불꽃 반구 → fx/paladin_aegis_ally.webp (흰 배경 샘플, build_aegis_fx)
#   - 불굴의 가호 동작 샘플(275×513, 위 = 시전 · 아래 = 발동, "불굴의 가호" 제목)은 aegis_a·aegis_b로 잘라 둠. 머리 폭이 대기의 0.65배 → 1.55배
# 크기 통일: 대기 샘플의 머리 꼭대기~발 키(IDLE_SRC_H)를 TARGET_H로 줄이는 배율이 기준. 다른 동작은 같은 배율(k=1)로 줄이고,
#   샘플마다 캐릭터를 다르게 그려 왔으면 그 칸의 몸 키(머리 꼭대기~발, 샘플 px)를 ('h', 키)로 적어 대기와 같은 키가 되게 맞춤
# 샘플 정리:
#   - 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움 (갑옷·방패 십자의 흰 하이라이트는 남김). 몸 안에 갇힌 흰 배경(공격 치켜들기의 망치와 방패 사이,
#     대기의 망치 자루와 옷 사이)은 GAP 상자 안의 아주 하얀 덩어리만 배경으로 (가슴 갑옷·부츠 하이라이트도 똑같이 하얘서 상자로 자리를 정함), 배경과 섞인 2px 테두리는 흰색을 빼서 투명도·본래 색을 되살림
#   - 대기 샘플(168×195)은 카드 화면을 잘라 온 것이라 오른쪽 4px·아래 1px 회색 테두리와 왼쪽 위 "#2" 번호 글씨가 박혀 있음 → 지움 (CARD, LABEL)
#   - 발은 잘리지 않았음 (부츠 바닥 윤곽선 뒤 1px 연한 띠까지 있음)
#   - 걷기 샘플(753×240, "2. 걷기" 제목 글씨)은 캐릭터가 대기보다 9% 크게 그려짐(키 177px, 머리 폭 77 vs 대기 69) → 몸 키로 대기와 같게
#   - 기본 공격 샘플 2장(113×143 치켜들기, 151×140 내리치기)은 캐릭터가 대기의 0.815배로 작게 그려짐(방패·얼굴·머리 폭 모두) → 1.23배로 키움
#   - 심판 샘플 3장(139×133, 125×161, 128×126)은 공격 샘플과 같은 크기(얼굴 폭 같음) → 같은 1.23배
#   - 심판 이펙트 샘플(186×150)은 어두운 배경(35, 39, 43)에 위 6줄 "Impact (Judgement..." 글씨 → 글씨 지우고, 배경색을 빼서 투명도·본래 색을 되살림.
#     바위 조각(어두운 갈색)은 배경과 밝기가 비슷해서 배경(푸르스름)보다 붉은 정도로 불투명도를 줌
#   - 신성 보호 샘플 2장(137×139, 144×143): 두 번째 장 위에 "…신성 보호막…" 글씨가 방패 윗선과 붙어 있음 → 0~6행 전부, 7~8행은 방패 오른쪽(x 46~)만 지움.
#     방패는 잘리지 않았음(윗선 8행). 얼굴은 공격 샘플보다 조금 크게(첫 장 7%) 그려져 첫 장 1.15배, 둘째 장 1.23배
#   - 신성 보호 이펙트 2장(129×79 마법진, 335×145 보호막 둘)은 어두운 배경(35, 39, 43) — 빛 더하기용으로 배경을 뺀 밝기만 남김 (glow_dark, 게임에서 'lighter')
#   - 성스러운 돌격 샘플(210×93): 발 뒤 흙먼지 꼬리가 몸과 붙어 있고 떨어진 먼지 조각도 있음 → 조각까지 남김. 먼지 물결 사이 갇힌 흰 배경 1곳 지움.
#     먼지가 발보다 넓게 깔려 발 기준점은 두 발 가운데(샘플 x 135)로 직접. 캐릭터가 작게 그려져(머리 폭이 대기의 0.65배) 1.75배
#   - 돌격 이펙트 샘플(335×114, 어두운 배경): 왼쪽 금빛 폭발(x 0~177) · 오른쪽 흙먼지+반짝임(x 196~) → 배경색을 빼서 투명하게 (흙먼지는 빛이 아니라 'lighter'로 안 그림)
#   - 축성 샘플(104×133): 은발 머리 폭 55px(대기 69) → 1.25배. 다리 사이 밝은 점 두 곳은 부츠 하이라이트라 남김
#   - 축성 이펙트 샘플(356×130, 어두운 배경): 왼쪽 금빛 마법진+반짝임(시전 막대 동안) · 오른쪽 빛줄기+깃털+은빛 마법진(발동) → 빛 더하기용(glow_dark)
#   - 피격·쓰러짐 샘플(931×178, 제목 글씨 2개)은 얼굴은 대기와 같은데 방패가 15% 작게 그려짐 → 중간값 1.08배로 키움. 무릎 꿇음·엎어짐 칸은 키로 못 재서 첫 칸 배율 그대로
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/paladin_'
OUT = 'assets/sprites/merc/paladin_0.webp'
TARGET_H = 110   # 대기 자세 머리 꼭대기~발 → 게임 칸 키. 게임에선 standH 90(기사와 같음)으로 1.22배 크게 그려 머리·얼굴이 다른 직업만큼 보이게 함
                 #   (샘플은 다른 직업보다 머리가 작은 6등신쯤: 키 165px에 머리 폭 69px. 전사는 키 82에 머리 폭 59)
IDLE_SRC_H = 163 # 대기 샘플 머리 꼭대기~발 키 (샘플 px)

# (샘플 이름, 칸 이름, 배율: 1 = 대기와 같은 배율 · ('h', 몸 키) = 그 키를 TARGET_H로 · 칸 이름 = 그 칸 배율 그대로, 샘플 안 몇 번째 그림(왼쪽부터) 또는 (x0, x1))
FRAMES = [
    ('idle', 'idle', 1, 0),
    ('walk', 'walk0', ('h', 177), 0), ('walk', 'walk1', ('h', 177), 1), ('walk', 'walk2', ('h', 177), 2), ('walk', 'walk3', ('h', 177), 3),
    ('hurt_down', 'hurt', 1.08, 0),
    ('hurt_down', 'down0', 1.08, 1), ('hurt_down', 'down1', 'down0', 2), ('hurt_down', 'down2', 'down0', 3),
    ('atk_a', 'atk0', 1.23, 0), ('atk_b', 'atk1', 1.23, 0),
    ('judge_a', 'judge0', 1.23, 0), ('judge_b', 'judge1', 1.23, 0), ('judge_c', 'judge2', 1.23, 0),
    ('hshield_a', 'hs0', 1.15, 0), ('hshield_b', 'hs1', 1.23, 0),
    ('charge', 'charge', 1.75, (0, 210)),
    ('consec', 'consec', 1.25, 0),
    ('aegis_a', 'aegis0', 1.55, 0), ('aegis_b', 'aegis1', 1.55, 0),
]
FOOTX = {'charge': 135}   # 발 가운데를 샘플 x로 직접 (먼지 꼬리가 발보다 아래·뒤로 깔림)
CARD = {'idle': (163, 194)}   # 카드 테두리를 빼고 쓸 (너비, 높이)
LABEL = {'idle': [(0, 45, 0, 16)], 'hshield_b': [(0, 144, 0, 7), (46, 144, 7, 9)]}   # 지울 상자 (x0, x1, y0, y1): 번호 글씨
GAP = {'atk_a': [(15, 60, 35, 75)], 'idle': [(95, 140, 130, 175)], 'charge': [(60, 92, 66, 82)]}   # 갇힌 흰 배경을 지울 상자 (x0, x1, y0, y1)
LIFT = {}   # 땅에서 띄워 그릴 높이 (칸 px)
SRC = {}


def load(name, pick=0):
    im = np.array(Image.open(f'{D}{name}_src.png').convert('RGB')).astype(float)
    if name in CARD:
        w, h = CARD[name]; im = im[:h, :w]
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    for x0, x1, y0, y1 in LABEL.get(name, ()): bg[y0:y1, x0:x1] = True
    if name in GAP:
        box = np.zeros_like(bg)
        for x0, x1, y0, y1 in GAP[name]: box[y0:y1, x0:x1] = True
        ids = np.arange(1, n + 1)
        gap = np.isin(lab, ids[(ndi.sum(white & box, lab, ids) >= 3) & (ndi.mean(im.min(axis=2), lab, ids) > 238)]) & box
        bg |= gap
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    # 큰 덩어리(몸)만 (글씨·티끌은 지움). 한 장에 여러 칸이면 왼쪽부터 pick번째
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m))
    sz = ndi.sum(m, lab, range(1, n + 1))
    if isinstance(pick, tuple):
        cx = ndi.center_of_mass(m, lab, range(1, n + 1))
        keep = [i + 1 for i in range(n) if sz[i] >= 20 and pick[0] <= cx[i][1] < pick[1]]
        a = np.where(np.isin(lab, keep), a, 0)
    else:
        bigs = [i + 1 for i in range(n) if sz[i] >= sz.max() * 0.3]
        bigs.sort(key=lambda i: np.where(lab == i)[1].mean())
        a = np.where(lab == bigs[pick], a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 0
    foot = np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()   # 발 가운데 (아래 8%의 불투명 픽셀 가운데)
    if name in FOOTX: foot = FOOTX[name] - xs.min()
    return rgba, foot


def main():
    pieces, scale = [], {}
    for src, name, k, pick in FRAMES:
        rgba, foot = load(src, pick)
        sc = scale[k] if isinstance(k, str) else (TARGET_H / k[1] if isinstance(k, tuple) else TARGET_H / IDLE_SRC_H * k)
        scale[name] = sc
        p = shrink(rgba, sc)
        pieces.append((name, p, foot * sc))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{sc:.3f} → {p.shape[1]}x{p.shape[0]}')
    L = max(int(np.ceil(c)) for _, _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 4
    H = max(p.shape[0] + LIFT.get(n, 0) for n, p, _ in pieces) + 5
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = H - 2 - p.shape[0] - LIFT.get(name, 0)
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'paladin_0 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)}')


OUT_JUDGE_FX = 'assets/sprites/fx/paladin_judgment.webp'
JUDGE_FX_BG = np.array([35.0, 39.0, 43.0])
JUDGE_FX_LABEL_ROWS = 6


def key_dark(src, x0=0, x1=None, label_rows=0, warm_keep=False, out=None, fade=None):
    # 어두운 배경 이펙트 샘플: 배경색과 떨어진 만큼 불투명, 배경색을 빼서 본래 색으로 (빛 가장자리·반투명 반구 속까지 살림)
    im = np.array(Image.open(f'{D}{src}_src.png').convert('RGB')).astype(float)[:, x0:x1]
    d = np.sqrt(((im - JUDGE_FX_BG) ** 2).sum(axis=2))
    a = np.clip((d - 8) / 70, 0, 1)
    if warm_keep:
        warm = np.clip((im[..., 0] - im[..., 2] - 3) / 8, 0, 1)   # 바위 조각: 배경은 푸르스름(파랑 > 빨강), 조각은 갈색
        a = np.maximum(a, warm * (d > 10))
    a[:label_rows] = 0
    al = np.maximum(a, 1e-3)[..., None]
    rgb = ((im - JUDGE_FX_BG * (1 - al)) / al).clip(0, 255)
    a = np.where(a < 0.04, 0, a)
    ys, xs = np.where(a > 0)
    o = np.dstack([rgb, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    if fade:   # 샘플 테두리에서 잘린 빛줄기: 그 가장자리 쪽으로 서서히 투명하게 (fade = {'top': 폭 px, 'right': 폭 px ...})
        hh, ww = o.shape[:2]
        yy, xx = np.mgrid[0:hh, 0:ww].astype(float)
        dist = {'top': yy, 'bottom': hh - 1 - yy, 'left': xx, 'right': ww - 1 - xx}
        m = np.ones((hh, ww))
        for side, wpx in fade.items():
            t = np.clip(dist[side] / wpx, 0, 1)
            m *= t * t * (3 - 2 * t)   # smoothstep
        o[..., 3] *= m
    Image.fromarray(o.clip(0, 255).astype(np.uint8), 'RGBA').save(out, 'WEBP', lossless=True)
    print(f'{out} {o.shape[1]}x{o.shape[0]}')


def build_judgment_fx():
    key_dark('judge_fx', label_rows=JUDGE_FX_LABEL_ROWS, warm_keep=True, out=OUT_JUDGE_FX)


def glow_dark(src, x0=0, x1=None, out=None, gain=1.15):
    # 빛 더하기용(게임에서 'lighter'로 그림): 배경색을 뺀 밝기만 남김. 불투명도 = 가장 밝은 채널, 색은 그 비율로 나눠 둠
    #   (배경을 빼서 투명하게 하는 방식은 반구 속 어두운 푸른빛이 회색 막처럼 남았음)
    im = np.array(Image.open(f'{D}{src}_src.png').convert('RGB')).astype(float)[:, x0:x1]
    add = ((im - JUDGE_FX_BG) * gain).clip(0, 255)
    add = np.where(add.max(axis=2, keepdims=True) < 6, 0, add)
    a = add.max(axis=2)
    rgb = np.where(a[..., None] > 0, add * 255 / np.maximum(a, 1)[..., None], 0)
    ys, xs = np.where(a > 0)
    o = np.dstack([rgb, a])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Image.fromarray(o.clip(0, 255).astype(np.uint8), 'RGBA').save(out, 'WEBP', lossless=True)
    print(f'{out} {o.shape[1]}x{o.shape[0]}')


def build_charge_fx():
    key_dark('charge_fx', 0, 186, out='assets/sprites/fx/paladin_charge_hit.webp', fade={'top': 26, 'right': 34})  # 금빛 충돌 폭발 (돌 조각 포함). 위·오른쪽 끝에서 잘린 빛기둥·빛줄기는 끝으로 갈수록 흐리게
    key_dark('charge_fx', 186, None, warm_keep=True, out='assets/sprites/fx/paladin_charge_dust.webp')  # 흙먼지 + 반짝임 (두꺼운 쪽이 왼쪽)


def build_consecrate_fx():
    glow_dark('consec_fx', 0, 175, out='assets/sprites/fx/paladin_consec_cast.webp')     # 금빛 마법진 + 반짝임
    glow_dark('consec_fx', 175, None, out='assets/sprites/fx/paladin_consec_burst.webp') # 빛줄기 + 깃털 + 은빛 마법진
    for k in ('cast', 'burst'):  # 바닥 원의 가운데 높이 (게임에서 발에 맞춤): 원 = 가로로 가장 넓은 줄
        a = np.array(Image.open(f'assets/sprites/fx/paladin_consec_{k}.webp'))[..., 3] > 40
        w = [np.ptp(np.where(r)[0]) if r.any() else 0 for r in a]
        print(f'  consec {k}: {a.shape[1]}x{a.shape[0]} 원 가운데 y={int(np.argmax(w))}')


def glow_white(src, box, out, gain=1.5, pw=0.75, cut=0.05):
    # 흰 배경 빛 이펙트 → 빛 더하기용(게임에서 'lighter'): 흰색에서 떨어진 만큼(가장 어두운 채널) 불투명, 색은 샘플 그대로
    #   (흰색을 빼서 본래 색으로 되살려 덮어 그리면 옅은 금빛이 배경과 섞여 탁해졌음. 대신 하얀 빛기둥 한가운데는 흰 배경과 같아서 비어 보임)
    x0, y0, x1, y1 = box
    im = np.array(Image.open(f'{D}{src}_src.png').convert('RGB')).astype(float)[y0:y1, x0:x1]
    a = ((254 - im.min(axis=2)) / 234 * gain).clip(0, 1) ** pw
    a = np.where(a < cut, 0, a)
    ys, xs = np.where(a > 0)
    o = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Image.fromarray(o.clip(0, 255).astype(np.uint8), 'RGBA').save(out, 'WEBP', lossless=True)
    w = [np.ptp(np.where(r)[0]) if r.any() else 0 for r in (o[..., 3] > 60)]   # 바닥 원 = 가로로 가장 넓은 줄
    print(f'{out} {o.shape[1]}x{o.shape[0]} 가장 넓은 줄 y={int(np.argmax(w))}')


def build_aegis_fx():
    # 불굴의 가호 (흰 배경 1024×705, 2×2): 위 왼쪽 = 시전 앞쪽 마법진+소용돌이 · 위 오른쪽 = 시전 뒤쪽 날개·검·방패·빛 구슬 ·
    #   아래 왼쪽 = 발동 빛기둥+날개+방패 · 아래 오른쪽 = 가호 받은 아군에게 씌우는 불꽃 반구
    glow_white('aegis_fx', (0, 0, 510, 322), 'assets/sprites/fx/paladin_aegis_cast0.webp')
    glow_white('aegis_fx', (510, 0, 1024, 322), 'assets/sprites/fx/paladin_aegis_cast1.webp')
    glow_white('aegis_fx', (0, 322, 510, 705), 'assets/sprites/fx/paladin_aegis_burst.webp')
    glow_white('aegis_fx', (510, 322, 1024, 705), 'assets/sprites/fx/paladin_aegis_ally.webp')


def build_holy_shield_fx():
    glow_dark('hshield_circle', out='assets/sprites/fx/paladin_hs_circle.webp')
    glow_dark('hshield_domes', 0, 188, out='assets/sprites/fx/paladin_hs_cast.webp')     # 왼쪽: 십자·방패 문양 반구 (시전자)
    glow_dark('hshield_domes', 188, None, out='assets/sprites/fx/paladin_hs_ally.webp')  # 오른쪽: 맑은 반구 + 빛 알갱이 (보호막 받은 아군)
    # 수호 서약: 전용 이펙트 대신 신성 보호의 마법진·시전자 반구를 금빛으로 바꿔 씀 (색상만 파랑 → 노랑, 밝기·투명도는 그대로)
    for k in ('circle', 'cast'):
        recolor_gold(f'assets/sprites/fx/paladin_hs_{k}.webp', f'assets/sprites/fx/paladin_vow_{k}.webp')


def recolor_gold(src, out, hue=42):
    im = Image.open(src).convert('RGBA')
    h, s, v = [np.array(c, float) for c in im.convert('RGB').convert('HSV').split()]
    h = np.full_like(h, hue / 360 * 255)   # 파랑 계열이 대부분이라 색상을 통째로 금빛으로
    s = (s * 1.1).clip(0, 255)
    rgb = Image.merge('HSV', [Image.fromarray(c.astype(np.uint8)) for c in (h, s, v)]).convert('RGB')
    o = Image.merge('RGBA', (*rgb.split(), im.split()[3]))
    o.save(out, 'WEBP', lossless=True)
    print(f'{out} {o.width}x{o.height}')


if __name__ == '__main__':
    main()
    build_judgment_fx()
    build_holy_shield_fx()
    build_charge_fx()
    build_consecrate_fx()
    build_aegis_fx()

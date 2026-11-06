# 화염술사 시크릿 레어 1 (불사조: 불꽃 날개·불타는 깃털 몸·오른손 위 불길) 샘플 → assets/sprites/merc/pyro_sr1.webp
#   + 전용 메테오 이펙트 assets/sprites/fx/pyro_sr_meteor_fx.webp
# 사용: python tools/pyro_sr1_build.py            (캐릭터·이펙트 둘 다)  ·  python tools/pyro_sr1_build.py char  (캐릭터만)
# 샘플 (assets/sprites/fx/samples/pyro_sr1_*):
#   idle_src.png (269×317, 흰 배경): 대기. 위쪽 "#08" 글씨는 지우고(CUT), 왼쪽 가장자리에 걸친 옆 그림 조각은 버림
#   walk_ab_src.png (302×183, 흰 배경): 걷기 2칸 (왼쪽·오른쪽 반). 위에 잘린 제목 글씨는 지움 (WALK_AB_TEXT)
#   walk_c_src.png (155×167, 흰 배경·회색 카드 테두리): 걷기 3번째. 테두리에 잘린 날개 끝·볏(위)과 발끝(아래)은
#     잘린 줄에 가까울수록 좁아지게 깎아 뾰족하게 다듬고(TAPER), 새로 생긴 가장자리에 진한 윤곽색을 칠함
#   sheet_src.png (708×560, 어두운 배경·칸 테두리·한글 이름표): 공격 2칸 (손 위 불꽃 → 손을 뻗어 불덩이 발사) · 피격 · 쓰러짐 2칸 (무릎 꿇음 → 재가 되어 엎드림)
#     공격 발사 칸의 칸 밖 불덩이는 게임이 투사체로 따로 그리므로 버림 (A2_MAX_X), 쓰러짐 2칸 오른쪽 위 반짝이 표시는 지움 (D2_ERASE)
#   cast_src.webp (1024×572, 어두운 배경·아래 이름표): 메테오 시전 앞 (머리 위 불덩이) · 메테오 시전 끝 (주먹 앞 불꽃) · 플레임 링 시전 (발밑 불꽃 고리)
#     오른쪽 아래 반짝이 표시가 고리에 겹쳐 있어 그 상자 안의 채도 낮은 점만 지움 (CAST_WM)
#   fb_src.png (222×219, 어두운 배경): 파이어볼 발사 (날개를 펴고 뛰어오르며 손을 뻗음)
#   fbcast_src.png (236×339): 파이어볼·플레어 시전 (두 손 사이 불덩이, 아래 이름표는 버림) · flare_src.png (257×234): 플레어 발사
#   combust_src.png (454×289): 왼쪽 = 익스플로전 시전 (주먹을 치켜듦, 발밑 불길 → 기준점 밑으로) · 오른쪽 = 익스플로전 발동 (불티가 사방으로)
#     파이어볼 발사 샘플과 같은 해상도라 다섯 장 모두 한 배율(sc_fb, 파이어볼 시전 칸 몸 키 = 대기 몸 키)을 씀
#   dash_src.png (276×235): 돌진(대쉬) — 몸을 눕혀 날아가며 앞쪽에 불꽃 고리. 아래 이름표·반짝이는 버림, 고리 안쪽 배경도 지움
#     날아가는 자세라 발이 없어서 기준점 x는 몸통 가운데(DASH_FOOT_X), 맨 아래가 바닥
#   ignite_src.png (197×348): 이그나이트 (한 손에 불꽃을 쥠). 아래 이름표는 버림
#   rb_egg / rb_swirl / rb_crouch / rb_roar _src.png (약 200×263~249×320): 특수 패시브 [불사조의 부활] — 알 · 불꽃의 응축(태동) · 공중 웅크리기(부활 직전) · 공중 포효(부활)
#     아래 이름표·반짝이는 버림, 불꽃 소용돌이 안쪽 배경도 지움
#   meteor_fall_src.webp (1024×572): 연기 꼬리가 왼쪽 위로 길게 달린 불타는 운석 (날아오는 투사체)
#   meteor_hit_src.webp (1024×572): 착탄 순간 (운석이 땅에 박히며 불꽃이 튐) · meteor_boom_src.webp: 착탄 뒤 폭발
# 캐릭터 칸 순서: 0 대기 · 1~2 걷기 · 3 공격 준비 · 4 공격 발사 · 5 피격 · 6~7 쓰러짐 · 8 파이어볼·플레어 시전 · 9 (예전 파이어볼, = 공격 발사) · 10 플레어 발사 · 11 걷기 3
#   · 12 메테오 시전 앞 · 13 메테오 시전 끝 · 14 플레임 링 시전 · 15 파이어볼 발사 · 16 익스플로전 시전 · 17 익스플로전 발동 · 18 대쉬 · 19 이그나이트 · 20 알 · 21 불꽃의 응축 · 22 공중 웅크리기 · 23 공중 포효
# 크기: 대기 머리 꼭대기~발(BODY_TOP~발) = TARGET_H. 다른 샘플은 몸 덩어리 키를 대기와 같게 맞춘 배율 (쓰러짐은 같은 장 공격·피격 칸 배율)
# 이펙트 시트 칸: fall (운석, 기준점 = 돌덩이 가운데) · hit (착탄) · boom (폭발) — 둘 다 기준점 = 착탄 그림 속 운석 가운데
#   꼬리가 그림 밖으로 잘린 왼쪽 위는 FADE 폭만큼 서서히 투명하게 (게임에서 잘린 끝이 보이지 않게)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/pyro_sr1_'
OUT = 'assets/sprites/merc/pyro_sr1.webp'
FX_OUT = 'assets/sprites/fx/pyro_sr_meteor_fx.webp'
CUT = [(122, 6, 170, 30)]   # "#08" 글씨
BODY_TOP = 98               # 대기 샘플에서 머리(볏) 꼭대기 y — 이 높이~발을 TARGET_H로
TARGET_H = 90
SHEET_BG = np.array([30, 34, 43], float)
SHEET_BOX = {'a1': (242, 6, 433, 182), 'a2': (444, 6, 637, 182), 'hurt': (242, 193, 433, 370), 'd1': (242, 381, 433, 552), 'd2': (444, 381, 637, 552)}
A2_MAX_X = 630                         # 공격 발사 칸: 이 x부터는 날아가는 불덩이 (버림)
D2_ERASE = [(588, 440, 637, 498)]      # 쓰러짐 2 반짝이 표시
WALK_AB_TEXT = (40, 0, 240, 9)         # 걷기 샘플 위 잘린 제목 글씨
WALK_C_BOX = (6, 6, 152, 161)          # 카드 테두리 안쪽
TAPER = {'top': 24, 'bottom': 4}       # 잘린 줄에서 이 높이만큼 점점 좁혀 뾰족하게 (위는 늘린 높이 + 이 값)
STRETCH_BAND = 40                      # 걷기 3 위쪽에서 위로 늘리는 띠 높이 (샘플 px)
CAST_BG = np.array([49, 52, 62], float)
CAST_BOX = {'m0': (16, 0, 328, 495), 'm1': (336, 0, 704, 495), 'ring': (712, 0, 1000, 495)}
CAST_WM = (912, 460, 960, 505)         # 반짝이 표시 (고리 위에 겹침)
DARK_SRC = {'fbcast': ('fbcast', (0, 0, 236, 300)), 'flare': ('flare', None), 'cb_cast': ('combust', (0, 0, 210, 289)), 'cb_go': ('combust', (210, 0, 454, 289)), 'dash': ('dash', (0, 0, 276, 174)), 'ignite': ('ignite', (0, 0, 197, 258)),
            'rb_egg': ('rb_egg', (0, 0, 200, 210)), 'rb_swirl': ('rb_swirl', (0, 0, 202, 207)), 'rb_crouch': ('rb_crouch', (0, 0, 196, 210)), 'rb_roar': ('rb_roar', (0, 0, 249, 267))}
RB_ZOOM = 1.3       # 웅크리기·포효 샘플은 불사조를 둥근 불꽃 안에 작게 그려서 몸 크기를 대기와 비슷하게 키움
# 칸별 크기 보정: 대기 칸 옆에 놓고 머리·몸통 크기를 눈으로 맞춘 배율 (몸 키로 맞추면 자세마다 머리 크기가 달라짐)
SIZE_FIX = {'walk0': 0.91, 'walk1': 0.91, 'walk2': 0.91,
            'atk_ready': 0.82, 'atk_fire': 0.82, 'hurt': 0.82, 'down0': 0.82, 'down1': 0.82,
            'ring': 1.15, 'rb_roar': 0.8, 'rb_crouch': 0.92}
DASH_FOOT_X = 125   # 대쉬 칸 기준점 x (몸통 가운데, 잘라 낸 그림 기준 샘플 px)
GROUND_DROP = {'ring': 27, 'cb_cast': 16}             # 바닥 고리가 발보다 이만큼(샘플 px) 아래까지 내려옴 → 발을 바닥에 맞추고 고리 앞쪽은 기준점 밑으로
FB_BG = np.array([50, 53, 62], float)
OUTLINE = np.array([96, 22, 12], float)
FX_SCALE = 0.5              # 이펙트 시트 배율 (게임에서 다시 늘려 그림)
FALL_ANGLE = 36.5           # 샘플 운석이 내려오는 각도 (오른쪽 아래로 36.5°) — 게임도 이 각도로 떨어뜨림
FADE = 260                  # 이펙트 꼬리 끝 서서히 사라지는 폭 (샘플 px)


def white_bg(im, thr=222, tone=16, enclosed=False):
    """흰 배경 지우기. enclosed=True (캐릭터): 바깥과 이어지지 않은 흰 틈(깃털·다리 사이)과 가장자리의 연회색 찌꺼기도 지움
    (메테오 이펙트는 불꽃 한가운데가 흰색이라 enclosed=False)"""
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), constant_values=255)
    white = (im.min(axis=2) > thr) & (im.max(axis=2) - im.min(axis=2) < tone)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    if enclosed:
        pale = (im.min(axis=2) > 200) & (im.max(axis=2) - im.min(axis=2) < 40)   # 갇힌 흰 틈 (조금 덜 하얀 것까지)
        bg |= pale
        for _ in range(2):   # 배경과 맞닿은 연회색·분홍빛 흰 점 (흰 배경과 섞인 찌꺼기)
            rim0 = ~bg & ndi.binary_dilation(bg)
            bg |= rim0 & (im.min(axis=2) > 165) & (im.max(axis=2) - im.min(axis=2) < 70)
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    return im[2:-2, 2:-2], a[2:-2, 2:-2]


def finish(im, a, drop_edge=True):
    """작은 티끌·가장자리 조각 정리 → (잘라 낸 rgba, 발 x, 몸 덩어리 키, 잘라 낸 위쪽 y)"""
    m = a > 0.3
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    sz = ndi.sum(m, lab, range(1, n + 1))
    body = 1 + int(np.argmax(sz))
    H, W = m.shape
    for i in range(1, n + 1):
        if i == body: continue
        ys, xs = np.where(lab == i)
        dark_bit = sz[i - 1] < 40 and im[ys, xs].max(axis=1).mean() < 110   # 잘린 글씨 조각 (어둡고 작은 덩어리)
        if sz[i - 1] < 3 or dark_bit or (drop_edge and (xs.min() <= 1 or ys.min() <= 1 or xs.max() >= W - 2)): a[lab == i] = 0
    ys, xs = np.where(a > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([im, a * 255])[y0:y1, x0:x1]
    bm = (lab == body)[y0:y1, x0:x1]
    rows = np.where(bm.any(axis=1))[0]
    bot = rows.max()
    foot = np.where(bm[bot - max(4, int(len(rows) * 0.07)):bot + 1].any(axis=0))[0].mean()
    return rgba, foot, rows.max() - rows.min() + 1, y0


def load_idle():
    im = np.array(Image.open(f'{D}idle_src.png').convert('RGB')).astype(float)
    for x0, y0, x1, y1 in CUT: im[y0:y1, x0:x1] = 255
    im, a = white_bg(im, enclosed=True)
    rgba, foot, h, y0 = finish(im, a)
    return rgba, foot, h, rgba.shape[0] - 1 - (BODY_TOP - y0)


def load_walk_ab(half):
    im = np.array(Image.open(f'{D}walk_ab_src.png').convert('RGB')).astype(float)
    x0, y0, x1, y1 = WALK_AB_TEXT; im[y0:y1, x0:x1] = 255
    im = im[:, :151] if half == 0 else im[:, 151:]
    im, a = white_bg(im, enclosed=True)
    return finish(im, a, drop_edge=False)


def taper(im, a, side, T):
    """잘린 줄(side = 'top' | 'bottom')에 닿은 덩어리를 그 줄에 가까울수록 좁혀 뾰족하게 + 새 가장자리에 윤곽색"""
    H, W = a.shape
    for d in range(T):   # 덩어리마다 제 폭을 기준으로 잘린 줄 쪽으로 갈수록 좁힘 → 불꽃 끝처럼 뾰족
        y = d if side == 'top' else H - 1 - d
        row = a[y] > 0.3
        if not row.any(): continue
        lab, n = ndi.label(row)
        for i in range(1, n + 1):
            xs = np.where(lab == i)[0]
            w = int(round(len(xs) * ((d + 1) / T) ** 1.5))
            mid = (xs[0] + xs[-1]) / 2 + (len(xs) * 0.15 if side == 'top' else 0)   # 끝은 살짝 오른쪽(바람 방향)으로
            keep = xs[np.abs(xs - mid) <= w / 2]
            a[y, xs] = 0; a[y, keep] = 1
    after = a > 0.3
    edge = after & ~ndi.binary_erosion(after, structure=np.ones((3, 3)))
    band = np.zeros_like(after)
    if side == 'top': band[:T + 1] = True
    else: band[H - T - 1:] = True
    im[edge & band] = OUTLINE
    return im, a


def load_walk_c(target_h):
    """걷기 3: 카드 테두리에 잘린 윗부분(날개 끝·볏)을 다른 걷기 칸 키(target_h)만큼 위로 늘려 세우고 끝을 뾰족하게"""
    im = np.array(Image.open(f'{D}walk_c_src.png').convert('RGB')).astype(float)
    x0, y0, x1, y1 = WALK_C_BOX
    im, a = white_bg(im[y0:y1, x0:x1], enclosed=True)
    a[:2] = 0; a[-2:] = 0   # white_bg가 덧댄 여백 때문에 남는 테두리 줄
    rows = np.where((a > 0.3).any(axis=1))[0]
    im, a = im[rows.min():rows.max() + 1], a[rows.min():rows.max() + 1]
    ext = max(0, int(round(target_h - a.shape[0])))
    if ext:   # 위쪽 STRETCH_BAND 줄을 band + ext 줄로 세로로 늘림 (불꽃이 위로 솟게)
        K = STRETCH_BAND
        idx = np.minimum((np.arange(K + ext) * K / (K + ext)).astype(int), K - 1)
        im = np.concatenate([im[idx], im[K:]]); a = np.concatenate([a[idx], a[K:]])
    im, a = taper(im, a, 'top', ext + TAPER['top'])
    im, a = taper(im, a, 'bottom', TAPER['bottom'])
    return finish(im, a, drop_edge=False)


def key_dark(im, bg, tol=16, enclosed_min=0):
    """어두운 배경 지우기: 가장자리에서 이어진 배경색 덩어리 + (enclosed_min > 0이면) 그 크기 이상으로 갇힌 배경색 덩어리 (고리 안쪽)"""
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), mode='edge')
    near = np.abs(im - bg).max(axis=2) < tol
    lab, n = ndi.label(near)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bgm = np.isin(lab, edge[edge > 0])
    if enclosed_min:
        sz = ndi.sum(near, lab, range(1, n + 1))
        bgm |= np.isin(lab, 1 + np.where(sz >= enclosed_min)[0])
    # 가장자리 테두리: 배경과 맞닿은 2px 안에서 배경과 섞여 남색으로 뜬 어두운 점은 지움 (불사조 색은 빨강이 파랑보다 셈 · 재 색 밝은 회색은 남김)
    rim = ~bgm & ndi.binary_dilation(bgm, iterations=2)
    fringe = rim & (im[..., 2] > im[..., 0] + 4) & (im.max(axis=2) < 110)
    bgm |= fringe
    rim2 = ~bgm & ndi.binary_dilation(bgm, iterations=1)   # 한 번 더 (지운 자리 바깥에 새로 드러난 점)
    bgm |= rim2 & (im[..., 2] > im[..., 0] + 4) & (im.max(axis=2) < 110)
    a = np.where(bgm, 0.0, 1.0)[2:-2, 2:-2]
    return im[2:-2, 2:-2], a


def load_sheet(name):
    im = np.array(Image.open(f'{D}sheet_src.png').convert('RGB')).astype(float)
    for x0, y0, x1, y1 in (D2_ERASE if name == 'd2' else ()): im[y0:y1, x0:x1] = SHEET_BG
    x0, y0, x1, y1 = SHEET_BOX[name]
    if name == 'a2': x1 = A2_MAX_X
    return finish(*key_dark(im[y0:y1, x0:x1], SHEET_BG), drop_edge=False)


def load_cast(name):
    im = np.array(Image.open(f'{D}cast_src.webp').convert('RGB')).astype(float)
    x0, y0, x1, y1 = CAST_WM
    box = im[y0:y1, x0:x1]
    gray = (box.max(axis=2) - box.min(axis=2) < 60) | (np.abs(box - CAST_BG).max(axis=2) < 40)
    box[gray] = CAST_BG
    x0, y0, x1, y1 = CAST_BOX[name]
    return finish(*key_dark(im[y0:y1, x0:x1], CAST_BG, 20, 40), drop_edge=False)


def load_dark(key):
    f, box = DARK_SRC[key]
    im = np.array(Image.open(f'{D}{f}_src.png').convert('RGB')).astype(float)
    if box: im = im[box[1]:box[3], box[0]:box[2]]
    return finish(*key_dark(im, im[2, 2].copy(), 20, 40), drop_edge=False)


def load_fb():
    im = np.array(Image.open(f'{D}fb_src.png').convert('RGB')).astype(float)
    return finish(*key_dark(im, FB_BG, 20), drop_edge=False)


def build_char():
    idle, ifoot, ih, itop_h = load_idle()
    sc_idle = TARGET_H / itop_h
    ref_h = ih * sc_idle   # 대기 몸 덩어리 키 (게임 px) — 다른 샘플은 이 키에 맞춤
    wa, wb = load_walk_ab(0), load_walk_ab(1)
    wc = load_walk_c((wa[2] + wb[2]) / 2)
    sh = {k: load_sheet(k) for k in SHEET_BOX}
    sc_walk = ref_h / ((wa[2] + wb[2]) / 2)
    sc_sheet = ref_h / ((sh['a1'][2] + sh['a2'][2] + sh['hurt'][2]) / 3)
    ca = {k: load_cast(k) for k in CAST_BOX}
    fb = load_fb()
    sc_cast = ref_h / ca['m1'][2]   # 메테오 시전 끝 (날개를 세우고 선 모습)의 몸 키를 대기와 같게
    sc_fb = ref_h / fb[2]
    dk = {k: load_dark(k) for k in DARK_SRC}
    sc_fb = ref_h / dk['fbcast'][2]   # 날개를 세우고 선 파이어볼 시전 칸의 몸 키를 대기와 같게 (같은 해상도인 파이어볼 발사·플레어·익스플로전도 이 배율)
    print('몸 키: ' + ' '.join(f'{k} {v[2]}' for k, v in dk.items()))
    print(f'몸 키: 메테오 {ca["m0"][2]} {ca["m1"][2]} 링 {ca["ring"][2]} 파이어볼 {fb[2]}')
    print(f'몸 키: 대기 {ih} 걷기 {wa[2]} {wb[2]} {wc[2]} 공격 {sh["a1"][2]} {sh["a2"][2]} 피격 {sh["hurt"][2]}')
    src = [('idle', (idle, ifoot, ih, 0), sc_idle), ('walk0', wa, sc_walk), ('walk1', wb, sc_walk),
           ('atk_ready', sh['a1'], sc_sheet), ('atk_fire', sh['a2'], sc_sheet), ('hurt', sh['hurt'], sc_sheet),
           ('down0', sh['d1'], sc_sheet), ('down1', sh['d2'], sc_sheet),
           ('cast', dk['fbcast'], sc_fb), ('fb', sh['a2'], sc_sheet), ('sc', dk['flare'], sc_fb),
           ('walk2', wc, sc_walk),
           ('meteor0', ca['m0'], sc_cast), ('meteor1', ca['m1'], sc_cast), ('ring', ca['ring'], sc_cast), ('fb_release', fb, sc_fb),
           ('cb_cast', dk['cb_cast'], sc_fb), ('cb_go', dk['cb_go'], sc_fb),
           ('dash', (dk['dash'][0], DASH_FOOT_X) + dk['dash'][2:], sc_fb), ('ignite', dk['ignite'], sc_fb),
           ('rb_egg', dk['rb_egg'], sc_fb), ('rb_swirl', dk['rb_swirl'], sc_fb), ('rb_crouch', dk['rb_crouch'], sc_fb * RB_ZOOM), ('rb_roar', dk['rb_roar'], sc_fb * RB_ZOOM)]
    pieces = []
    for name, (rgba, foot, _, _), k in src:
        k *= SIZE_FIX.get(name, 1)
        p = shrink(rgba, k)
        pieces.append((name, p, foot * k, int(round(GROUND_DROP.get(name, 0) * k))))
    L = max(int(np.ceil(c)) for _, _, c, _ in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c, _ in pieces) + 3
    U = max(p.shape[0] - dr for _, p, _, dr in pieces) + 3
    cw, ch = L + R, U + 2 + max(dr for *_, dr in pieces)
    sheet = np.zeros((ch, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c, dr) in enumerate(pieces):
        x = i * cw + L - int(round(c)); y = U - p.shape[0] + dr
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'배율 대기 {sc_idle:.3f} 걷기 {sc_walk:.3f} 시트 {sc_sheet:.3f} 시전 {sc_cast:.3f} 파이어볼 {sc_fb:.3f}  pyro_sr1 cellW={cw} cellH={ch} anchorX={L} anchorY={U} count={len(pieces)}')
    # 손 자리 (발 기준): 공격 발사 칸 오른쪽 끝 · 공격 준비 칸 손 위 불꽃 (몸 오른쪽의 가장 밝은 노란 덩어리)
    for i, label in ((4, '발사 손끝'), (15, '파이어볼 손끝'), (10, '플레어 손끝'), (3, '준비 손 불꽃')):
        p, c = pieces[i][1].astype(int), pieces[i][2]
        al = p[..., 3] > 0
        if i in (4, 15, 10):
            xr = np.where(al.any(axis=0))[0].max()
            yy = np.where(al[:, xr - 3:xr + 1].any(axis=1))[0].mean()
            print(f'{label} = [{xr - c:.0f}, {yy - p.shape[0]:.0f}]')
        else:
            yy, xx = np.where(al & (p[..., 0] > 235) & (p[..., 1] > 200) & (np.arange(p.shape[1])[None] > c + 10))
            if len(xx): print(f'{label} = [{xx.mean() - c:.0f}, {yy.mean() - p.shape[0]:.0f}]')


def fx_piece(name, anchor):
    im = np.array(Image.open(f'{D}meteor_{name}_src.webp').convert('RGB')).astype(float)
    im, a = white_bg(im, thr=226, tone=22)
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W]
    # 왼쪽 위 꼬리 끝: 그림 왼쪽·위 가장자리에서 FADE 안쪽은 서서히 투명
    d = np.minimum(xx, yy * 1.6)
    a = a * np.clip(d / FADE, 0, 1) ** 1.3
    ys, xs = np.where(a > 0.02)
    x0, y0 = xs.min(), ys.min()
    rgba = np.dstack([im, a * 255])[y0:ys.max() + 1, x0:xs.max() + 1]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    img = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA')
    if name == 'fall':   # 투사체는 게임이 날아가는 각도로 돌려 그림 → 오른쪽(0°)을 향하게 미리 돌려 둠
        img = img.rotate(FALL_ANGLE, Image.BICUBIC, expand=True)
        img = img.crop(img.getbbox())
    pm = np.array(img).astype(float)
    al = pm[..., 3:]
    rgba = pm.copy(); rgba[..., :3] = np.where(al > 0, pm[..., :3] * 255 / np.maximum(al, 1), 0)
    ax, ay = anchor(rgba, rgba[..., 3] / 255)
    h, w = rgba.shape[:2]
    sm = img.resize((round(w * FX_SCALE), round(h * FX_SCALE)), Image.LANCZOS)
    r = np.array(sm).astype(float); al = r[..., 3:]
    r[..., :3] = np.where(al > 0, r[..., :3] * 255 / np.maximum(al, 1), 0)
    return r.clip(0, 255).astype(np.uint8), ax * FX_SCALE, ay * FX_SCALE


def rock_center(rgba, a):
    # 운석 돌덩이 = 오른쪽 아래의 어두운 덩어리
    dark = (a > 0.9) & (rgba[..., :3].max(axis=2) < 70)
    h, w = dark.shape
    dark[:, :int(w * 0.6)] = False
    ys, xs = np.where(dark)
    return xs.mean(), ys.mean()


HIT_ROCK_NEAR = (600, 410)   # 착탄 그림 속 운석이 있는 대략의 자리 (잘라 낸 샘플 px) — 이 둘레 RANGE 안의 검붉은 덩어리 가운데를 기준점으로
HIT_ROCK_RANGE = 70


def rock_in_hit(rgba, a):
    # 착탄 그림 속 운석 돌덩이 가운데 (둘레의 파편·보랏빛 연기는 빼고 HIT_ROCK_NEAR 둘레만 봄)
    c = rgba[..., :3]
    h, w = a.shape
    dark = (a > 0.9) & (c.max(axis=2) < 90) & (c[..., 0] >= c[..., 2])
    cx, cy = HIT_ROCK_NEAR
    win = np.zeros_like(dark)
    win[max(0, cy - HIT_ROCK_RANGE):cy + HIT_ROCK_RANGE, max(0, cx - HIT_ROCK_RANGE):cx + HIT_ROCK_RANGE] = True
    dark &= win
    lab, n = ndi.label(dark, structure=np.ones((3, 3)))
    sz = ndi.sum(dark, lab, range(1, n + 1)); i = 1 + int(np.argmax(sz))
    ys, xs = np.where(lab == i)
    return xs.mean(), ys.mean()


def ground_center(rgba, a):
    # 바닥 = 맨 아래 줄 근처 그림의 가운데 · 기준점 y는 바닥 흙더미 가운데 높이
    ys = np.where((a > 0.5).any(axis=1))[0]
    bot = ys.max()
    xs = np.where((a[bot - 30:bot + 1] > 0.5).any(axis=0))[0]
    return (xs.min() + xs.max()) / 2, bot - 22


def build_fx():
    # 착탄·폭발 기준점 = 착탄 그림 속 운석 가운데 (두 샘플은 같은 구도라 같은 자리) → 떨어지던 운석(fall 기준점)이 멈춘 자리에 그대로 겹침
    hit = fx_piece('hit', rock_in_hit)
    boom = fx_piece('boom', lambda r, a: (hit[1] / FX_SCALE, hit[2] / FX_SCALE))
    assert boom[0].shape == hit[0].shape, '착탄·폭발 샘플 구도가 다름'
    parts = [('fall',) + fx_piece('fall', rock_center), ('hit',) + hit, ('boom',) + boom]
    W = sum(p.shape[1] for _, p, _, _ in parts) + 2 * (len(parts) - 1)
    H = max(p.shape[0] for _, p, _, _ in parts)
    sheet = np.zeros((H, W, 4), np.uint8)
    x = 0
    for name, p, ax, ay in parts:
        sheet[:p.shape[0], x:x + p.shape[1]] = p
        print(f"{name}: [[{x},0,{p.shape[1]},{p.shape[0]},{ax:.1f},{ay:.1f}]]")
        x += p.shape[1] + 2
    Image.fromarray(sheet, 'RGBA').save(FX_OUT, 'WEBP', quality=88)


if __name__ == '__main__':
    build_char()
    if 'char' not in sys.argv[1:]: build_fx()

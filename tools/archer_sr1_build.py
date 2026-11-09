# 궁수 시크릿 레어 1 교체 (2026-11-09): 은발 엘프 궁수 (은빛 판금·남색 망토·청록 허리천·얼음빛 활)
#   → assets/sprites/merc/archer_sr1.webp (archer_0과 같은 14칸 구성) + assets/sprites/fx/archer_storm_cast_sr1.webp (히든 스킬 [폭풍] 시전 3칸)
# 사용: python tools/archer_sr1_build.py
# 샘플 (흰 배경, assets/sprites/merc/samples/archer_sr1_edit_*):
#   1 대기·걷기 4 (한 장, 왼쪽에 동작 이름 글씨) · 2 피격 · 3 화살비 (하늘로 겨눔, 왼쪽 위 글씨) · 4 화살비를 쏜 뒤 (글씨)
#   5 일반 공격 (시위를 끝까지 당김) · 6 쏜 뒤 · 7 회피기동 (오른쪽 끝 날아가는 화살은 지움) · 8 쓰러짐 2칸 (380×219 한 장, 제목 글씨·가운데 칸 선)
#   9 히든 스킬 겨누기 2칸 (망토가 가만히 → 망토가 바람에 날림) · 10 히든 스킬 쏜 뒤
# 칸 순서 (archer_0과 같음): 0 대기 · 1~4 걷기 · 5~6 공격 (샘플이 한 장이라 같은 그림) · 7 피격 · 8~9 쓰러짐 · 10 화살비 · 11 회피기동
#   · 12 화살비를 쏜 뒤 · 13 쏜 뒤
# 크기: 샘플마다 따로 그려져 크기가 다름 → 대기 칸 머리(머리띠·얼굴·앞머리)를 기울이고 키우며 찾아 같은 크기로 맞춤 (archer0_build.head_scale과 같은 방식)
#   쓰러짐 2칸은 같은 장이라 같은 배율 (머리가 기울고 눈을 감아 찾지 못해서 눈으로 맞춤). 누운 칸은 archer_0처럼 머리가 왼쪽이 되게 좌우로 뒤집음
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
from mage0_build import defringe, pack

D = 'assets/sprites/merc/samples/archer_sr1_edit_'
OUT = 'assets/sprites/merc/archer_sr1.webp'
CAST_OUT = 'assets/sprites/fx/archer_storm_cast_sr1.webp'
IDLE_H = 96            # 대기 키 (머리끝~발). 포니테일이 없어 archer_0 standH(96)와 같게
IDLE_HEAD = (125, 45, 182, 100)   # 첫 장 대기 칸 머리 (머리띠·얼굴·앞머리)
# (칸 이름, 샘플, 상자 또는 None, 남길 덩어리 'one' | 최소 크기, {옵션})
#   옵션: erase = 지울 상자들 (샘플 좌표) · scale = 다른 칸 배율을 같이 씀 · flip · lift = 발밑 띄우기 · foot = 기준점 x 비율
FRAMES = [
    ('idle', '1_idle_walk_src.png', (66, 12, 256, 240), 'one', {}),
    ('walk0', '1_idle_walk_src.png', (70, 240, 247, 449), 'one', {}),
    ('walk1', '1_idle_walk_src.png', (247, 240, 414, 449), 'one', {}),
    ('walk2', '1_idle_walk_src.png', (414, 240, 584, 449), 'one', {}),
    ('walk3', '1_idle_walk_src.png', (584, 240, 753, 449), 'one', {}),
    ('atk0', '5_attack_draw_src.png', None, 'one', {}),
    ('atk1', '5_attack_draw_src.png', None, 'one', {}),
    ('hurt', '2_hurt_src.webp', None, 'one', {}),
    ('down0', '8_fall_src.png', (2, 24, 183, 217), 'one', {'rel': 1.12}),   # 머리가 기울고 눈을 감아 못 찾음 → 눈으로 맞춘 배율
    ('down1', '8_fall_src.png', (188, 24, 377, 217), 60, {'scale': 'down0', 'flip': True, 'foot': 0.5}),
    ('rain', '3_rain_draw_src.webp', None, 60, {'erase': [(10, 120, 340, 195)], 'rel': 0.275}),   # 고개를 들어 머리를 작게 잡음(1.3배 크게 나옴) → 눈으로 맞춤
    ('evade', '7_evasive_src.webp', None, 'one', {'lift': 8, 'foot': 0.42, 'fix': 0.92}),   # 머리를 찾은 배율로는 조금 커 보임
    ('rainEnd', '4_rain_release_src.webp', None, 'one', {'erase': [(10, 120, 340, 195)], 'scale': 'rain'}),
    ('atkEnd', '6_attack_release_src.webp', None, 'one', {}),
]
# 히든 스킬 [폭풍] 시전 3칸: 0 겨누기 (시전 막대 앞 2/3) · 1 바람에 망토가 날림 (마지막 1/3) · 2 쏜 뒤 (발동 직후)
#   머리를 찾은 배율보다 대기 칸 옆에서 조금 커 보여 ×0.93 (fix)
#   이펙트는 그림에 없음 → 게임이 pixelfx 작법으로 겹쳐 그림 (index.html drawStormSrCastFx). 화살촉 자리를 출력함
CAST = [
    ('aim', '9_hidden_shot_src.png', (0, 0, 180, 184), 'one', {'fix': 0.93}),
    ('aimWind', '9_hidden_shot_src.png', (180, 0, 415, 184), 'one', {'fix': 0.93}),
    ('after', '10_hidden_cast_src.png', None, 'one', {'fix': 0.93}),
]


def rgb(src):
    im = Image.open(D + src).convert('RGBA')
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
    return np.array(bg.convert('RGB')).astype(float)


def load(src, box, keep, erase=()):
    im = rgb(src)
    for x0, y0, x1, y1 in erase: im[y0:y1, x0:x1] = 255
    x0, y0, x1, y1 = box or (0, 0, im.shape[1], im.shape[0]); im = im[y0:y1, x0:x1]
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), constant_values=255)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    ids = np.arange(1, n + 1)   # 갇힌 흰 배경 (활과 시위 사이·팔 사이): 아주 하얗고 30px 이상
    pure = (ndi.sum(white, lab, ids) >= 30) & (ndi.mean(im.min(axis=2), lab, ids) > 246)
    bg |= np.isin(lab, ids[pure])
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    m = a > 0.3
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=3))
    sz = ndi.sum(m, lab, range(1, n + 1))
    if keep == 'one':
        k = lab == int(np.argmax(sz)) + 1
    else:
        k = np.isin(lab, 1 + np.where(sz >= keep)[0])
    a = np.where(k, a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    body = rgba[..., 3] > 128
    foot = np.where(body[int(body.shape[0] * 0.94):].any(axis=0))[0].mean()
    return rgba, foot


TEMPLATE = None


def head_scale(rgba):
    # rgba(투명 배경)에서 대기 칸 머리와 가장 닮은 곳의 크기 비율 (대기 머리 = 1)
    import cv2
    im = rgba[..., :3] * (rgba[..., 3:] / 255) + 255 * (1 - rgba[..., 3:] / 255)
    pre = 240 / max(im.shape[:2])   # 샘플마다 크기가 많이 달라서 먼저 대기 칸쯤으로 줄이고 찾음
    im = cv2.resize(im.astype(np.float32), (round(im.shape[1] * pre), round(im.shape[0] * pre)), interpolation=cv2.INTER_AREA)
    T0 = TEMPLATE; best = (-1, 1)
    for ang in range(-30, 31, 5):
        M = cv2.getRotationMatrix2D((T0.shape[1] / 2, T0.shape[0] / 2), ang, 1)
        R = cv2.warpAffine(T0, M, (T0.shape[1], T0.shape[0]), borderValue=(255, 255, 255))[6:-6, 6:-6]
        for sc in np.arange(0.4, 1.8, 0.01):
            t = cv2.resize(R, (round(R.shape[1] * sc), round(R.shape[0] * sc)), interpolation=cv2.INTER_AREA)
            if t.shape[0] > im.shape[0] or t.shape[1] > im.shape[1]: continue
            v = cv2.minMaxLoc(cv2.matchTemplate(im, t, cv2.TM_CCOEFF_NORMED))[1]
            if v > best[0]: best = (v, sc)
    return best[1] / pre, best[0]


def build(frames, k, label):
    pieces, scales = [], {}
    for name, src, box, keep, opt in frames:
        rgba, foot = load(src, box, keep, opt.get('erase', ()))
        if 'scale' in opt:
            kk = scales[opt['scale']]
        elif 'rel' in opt:
            kk = k * opt['rel']
        else:
            hs, v = head_scale(rgba)
            kk = k / hs * SELF_HEAD * opt.get('fix', 1)
            print(f'  {name}: 머리 {hs / SELF_HEAD:.3f}배 (닮음 {v:.2f})')
        scales[name] = kk
        if opt.get('flip'):
            rgba = rgba[:, ::-1]
        if 'foot' in opt: foot = rgba.shape[1] * opt['foot']
        p = defringe(shrink(rgba, kk))
        if opt.get('lift'): p = np.concatenate([p, np.zeros((opt['lift'], p.shape[1], 4), np.uint8)])
        pieces.append((name, p, foot * kk))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{kk:.3f} → {p.shape[1]}x{p.shape[0]}, 발 {foot * kk:.1f}')
    return pieces


SELF_HEAD = 1.0

if __name__ == '__main__':
    S1 = rgb('1_idle_walk_src.png').astype(np.float32)
    x0, y0, x1, y1 = IDLE_HEAD; TEMPLATE = S1[y0:y1, x0:x1].copy()
    idle, _ = load(FRAMES[0][1], FRAMES[0][2], 'one')
    k = IDLE_H / idle.shape[0]
    SELF_HEAD, _ = head_scale(idle)   # 대기 칸 자신의 값 (가장자리를 잘라 1이 아님)
    print(f'대기 칸 {idle.shape[1]}x{idle.shape[0]} ×{k:.3f}')
    pieces = build(FRAMES, k, 'archer_sr1')
    pack(pieces, OUT, 'archer_sr1')
    cast = build(CAST, k, 'cast')
    pack(cast, CAST_OUT, 'archer_storm_cast_sr1')
    # 화살촉 (겨누기 두 칸의 가장 오른쪽 불투명 점) — 칸 안 좌표는 pack 뒤 시트에서 다시 잼
    sheet = np.array(Image.open(CAST_OUT))
    cw = sheet.shape[1] // len(cast)
    for i, (name, *_ ) in enumerate(cast):
        a = sheet[:, i * cw:(i + 1) * cw, 3] > 128
        ys, xs = np.where(a)
        tip_x = xs.max(); tip_y = ys[xs >= tip_x - 1].mean()
        print(f'  {name}: 맨 오른쪽 점 ({tip_x}, {tip_y:.0f}) 머리끝 y {ys.min()}')

# 마법사 기본 외형(mage_0) 교체: 은발·파란 모자·로브·푸른 수정 지팡이 샘플 → assets/sprites/merc/mage_0.webp
# 사용: python tools/mage0_build.py
# 샘플 (흰 배경, assets/sprites/merc/samples/):
#   mage_edit_1_src.png (196×202): 대기 1칸 (맨 위 3줄은 화면 캡처 회색 줄 → 버림)
#   mage_edit_2_walk_src.png (454×199): "2. 걷기" 2칸 (왼쪽 글씨는 버림)
#   mage_edit_3_attack_hurt_death_src.png (720×622): "3. 일반공격" 2칸 · "4. 피격" 1칸 · "5. 쓰러짐" 2칸
#     공격 둘째 칸 수정 끝의 얼음 물보라는 지움 (마법사 투사체는 게임이 따로 그림)
#   mage_edit_4_skill_src.png (196×197): 스킬 1 (지팡이를 들고 수정 둘레에 푸른 소용돌이)
#   mage_edit_5_skill_src.png (379×210): 스킬 2 (지팡이를 내지름 + 큰 얼음 광선) → 광선은 수정 끝(x 197)에서 자름
#     (스킬마다 화염·얼음·번개 투사체를 따로 그려서 광선을 남기면 겹침)
# 칸 순서: 0 대기 · 1 걷기A · 2 대기 · 3 걷기B (걷기 2칸이라 대기를 사이에 끼움, 첫 페이지 카드가 0~3칸을 돌림)
#   · 4~5 공격 · 6~7 스킬 · 8 피격 · 9~10 쓰러짐
# 크기: 대기 키(모자 꼭대기~발)를 TARGET_H로. 모든 칸이 같은 배율 (샘플들이 같은 크기로 그려져 있음)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/merc/samples/mage_edit_'
OUT = 'assets/sprites/merc/mage_0.webp'
IDLE_H = 106   # 대기 칸 키(모자 꼭대기~발). 다른 칸은 얼굴 크기(살색 덩어리 가로·세로)를 대기 칸과 같게 맞춰 배율을 정함
#   (샘플마다 그려 온 크기가 5~20% 달라서 키나 한 장 배율로는 칸마다 얼굴이 커졌다 작아졌다 함)
SAME_K = {'down1': 'down0'}
# 똑바로 선 칸은 얼굴만으로 맞추면 샘플마다 머리·몸 비율이 조금씩 달라 걷기 칸 키가 대기보다 커짐(걸을 때 들썩임)
#   → 키(모자 꼭대기~발)로 맞춘 배율과 반반 섞음
UPRIGHT = {'walk0', 'walk1', 'atk0', 'hurt', 'skill0', 'hold'}   # 누운 칸은 얼굴이 옆으로 누워 재기 어려워 바로 앞 칸 배율을 씀
# 스킬 2: 수정 앞에서 퍼지는 광선 고리는 수정(y 100~122) 위아래로 x 168부터 나옴 → 그 자리를 지움
# 원소 융합 둘째 장: 오른쪽 끝에 다음 그림(모자 챙·망토)이 걸려 있음 → 수정 끝(x 445) 오른쪽과 모자 높이의 x 426~ 를 지움
CLEAR = {'5_skill_src': [(166, 0, 379, 99), (166, 123, 379, 210)],
         '7_fusion_src': [(426, 0, 458, 140), (446, 0, 458, 297)]}
# 갇힌 흰 배경 (30px보다 작거나 덜 하얘서 자동으로 못 잡는 곳, 샘플 좌표 x0, y0, x1, y1): 이 상자 안 흰 픽셀은 배경
#   대기 손 아래 지팡이·로브 사이 · 걷기A 지팡이·부츠 사이 · 걷기B 지팡이 옆 · 원소 융합 내지르기 머리카락·지팡이 사이
GAP = {'1_src': [(124, 135, 131, 148)], '2_walk_src': [(377, 169, 383, 178), (395, 141, 400, 147)],
       '7_fusion_src': [(263, 163, 266, 172)]}

# (칸 이름, 샘플, 상자 (x0, y0, x1, y1))
FRAMES = [
    ('idle', '1_src', (0, 3, 196, 202)),
    ('walk0', '2_walk_src', (130, 0, 297, 199)),
    ('idle2', '1_src', (0, 3, 196, 202)),
    ('walk1', '2_walk_src', (297, 0, 454, 199)),
    ('atk0', '3_attack_hurt_death_src', (180, 0, 375, 214)),
    ('atk1', '3_attack_hurt_death_src', (380, 0, 610, 214)),
    ('skill0', '4_skill_src', None),
    ('skill1', '5_skill_src', (0, 0, 197, 210)),
    ('hurt', '3_attack_hurt_death_src', (145, 214, 345, 422)),
    ('down0', '3_attack_hurt_death_src', (145, 422, 382, 622)),
    ('down1', '3_attack_hurt_death_src', (382, 422, 700, 622)),
]

# 히든 스킬 [원소 융합] 시전 그림 → assets/sprites/fx/mage_fusion_cast.webp (MAGE_FUSION_FX, 3칸)
#   mage_edit_6_fusion_src.png (211×276): 0 모으기 — 지팡이를 가로로 두 손에 쥠
#   mage_edit_7_fusion_src.png (458×297): 1 지팡이를 머리 위로 치켜듦 · 2 내지르기 (양 끝에 이웃 그림 조각이 걸려 있어 상자·CLEAR로 버림)
#   배율: 모으기 = 서 있는 키를 대기 칸 키에, 7번 장 = 내지르기 키를 기본 공격 내지르기 칸 키에 맞춤 (얼굴 크기가 시트와 같게)
FUSION_OUT = 'assets/sprites/fx/mage_fusion_cast.webp'
FUSION = [
    ('hold', '6_fusion_src', None, 'idle'),
    ('raise', '7_fusion_src', (0, 0, 214, 297), 'atk1'),
    ('thrust', '7_fusion_src', (205, 0, 458, 297), 'atk1'),
]


def load(src, box):
    im = np.array(Image.open(f'{D}{src}.png').convert('RGB')).astype(float)
    if src in CLEAR:   # 광선 고리 조각: 흰색으로 덮음 (샘플 좌표)
        for x0, y0, x1, y1 in CLEAR[src]: im[y0:y1, x0:x1] = 255
    gap = np.zeros(im.shape[:2], bool)
    for x0, y0, x1, y1 in GAP.get(src, ()): gap[y0:y1, x0:x1] = True
    if box:
        x0, y0, x1, y1 = box; im = im[y0:y1, x0:x1]; gap = gap[y0:y1, x0:x1]
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), constant_values=255)
    gap = np.pad(gap, 2)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0]) | (white & gap)
    # 갇힌 흰 배경 (머리카락·지팡이·팔 사이): 아주 하얗고 30px 이상인 덩어리
    ids = np.arange(1, n + 1)
    pure = (ndi.sum(white, lab, ids) >= 30) & (ndi.mean(im.min(axis=2), lab, ids) > 246)
    bg |= np.isin(lab, ids[pure])
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    # 몸 덩어리(3px 안에 붙은 조각까지)만 남김 → 이웃 칸·글씨·떨어져 나간 물보라는 지움
    m = a > 0.3
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=3))
    sz = ndi.sum(m, lab, range(1, n + 1))
    big = int(np.argmax(sz)) + 1
    a = np.where(lab == big, a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    body = rgba[..., 3] > 128
    # 발 가운데: 몸 아래 6% 줄 (갈색 부츠)
    foot = np.where(body[int(body.shape[0] * 0.94):].any(axis=0))[0].mean()
    return rgba, foot


def face_size(rgba):
    # 얼굴 = 가장 큰 살색 덩어리. 포즈마다 키는 달라도 얼굴 크기는 같아야 해서 칸마다 배율을 이것으로 맞춤
    rgb = rgba[..., :3] / 255; a = rgba[..., 3] > 200
    mx, mn = rgb.max(-1), rgb.min(-1); s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    skin = a & (mx > 0.72) & (s > 0.08) & (s < 0.45) & (r >= g) & (g >= b) & (r - b > 0.08)
    lab, n = ndi.label(ndi.binary_closing(skin, iterations=2))
    big = int(np.argmax(ndi.sum(skin, lab, range(1, n + 1)))) + 1
    ys, xs = np.where(lab == big)
    return xs.max() - xs.min() + 1, ys.max() - ys.min() + 1


def defringe(p):
    # 줄인 뒤 바깥 테두리에 남은 흰 배경 찌꺼기: 투명한 칸에 닿은 밝은 무채색 픽셀(윤곽 바깥 회색 띠)을 두 겹까지 지움
    #   (수정·소용돌이처럼 색이 도는 밝은 픽셀은 남김)
    for _ in range(2):
        a = p[..., 3] > 0
        edge = a & ndi.binary_dilation(~a)
        c = p[..., :3].astype(int)
        light = (c.min(-1) > 110) & (c.max(-1) - c.min(-1) < 45)
        kill = edge & light
        if not kill.any(): break
        p[kill] = 0
    return p


def pack(pieces, out, label):
    L = max(int(np.ceil(c)) for _, _, c in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 3
    AY = max(p.shape[0] for _, p, _ in pieces) + 3
    H = AY + 2
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = AY - p.shape[0]
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(out, 'WEBP', lossless=True)
    print(f'{label} cellW={cw} cellH={H} anchorX={L} anchorY={AY} count={len(pieces)} 첫 칸 키={pieces[0][1].shape[0]}')


def main():
    idle, _ = load(FRAMES[0][1], FRAMES[0][2])
    ki = IDLE_H / idle.shape[0]
    fw0, fh0 = face_size(idle)
    ks = {}

    def scale_of(name, rgba):
        if name in SAME_K: return ks[SAME_K[name]]
        fw, fh = face_size(rgba)
        ks[name] = ki * (fw0 / fw + fh0 / fh) / 2
        if name in UPRIGHT: ks[name] = (ks[name] * IDLE_H / rgba.shape[0]) ** 0.5
        return ks[name]

    pieces = []
    for name, src, box in FRAMES:
        rgba, foot = load(src, box)
        k = scale_of(name, rgba)
        if name == 'down1': foot = rgba.shape[1] * 0.45   # 누운 칸은 몸 가운데쯤
        p = defringe(shrink(rgba, k))
        pieces.append((name, p, foot * k))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{k:.3f} → {p.shape[1]}x{p.shape[0]}, 발 {foot * k:.1f}')
    pack(pieces, OUT, 'mage_0')
    # 원소 융합: 같은 방식(얼굴 크기를 대기 칸에)으로 배율
    fpieces = []
    for name, src, box, _ in FUSION:
        rgba, foot = load(src, box)
        k = scale_of(name, rgba)
        p = defringe(shrink(rgba, k))
        fpieces.append((name, p, foot * k))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{k:.3f} → {p.shape[1]}x{p.shape[0]}, 발 {foot * k:.1f}')
    pack(fpieces, FUSION_OUT, 'mage_fusion_cast')


if __name__ == '__main__':
    main()

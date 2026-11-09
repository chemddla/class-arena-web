# 마법사 시크릿 레어 1 (mage_sr1) 교체: 갈색 긴 머리·분홍 리본·분홍 드레스·별 지팡이 마법소녀 샘플
#   → assets/sprites/merc/mage_sr1.webp (몸 시트) + assets/sprites/fx/mage_fusion_sr1.webp (히든 스킬 [원소 융합] 시전 3칸)
# 사용: python tools/mage_sr1_build.py
# 샘플 (흰 배경, assets/sprites/merc/samples/):
#   mage_sr1_edit_1_src.png (199×231): 대기 1칸 (맨 아래 회색 줄은 화면 캡처 테두리 → 버림)
#   mage_sr1_edit_2_walk_src.png (424×202): 걷기 3칸
#   mage_sr1_edit_3_walk_src.png (144×186): 걷기 1칸 (넷째 걸음)
#   mage_sr1_edit_4_attack_hurt_death_src.png (762×544): 일반공격 2칸 · 피격 1칸 · 쓰러짐 2칸 (왼쪽 글씨는 상자로 버림)
#     쓰러짐 둘째 칸의 떨어진 지팡이는 몸과 떨어져 있어도 남김 (상자 안 덩어리를 다 남김)
#   mage_sr1_edit_5_hidden_skill_src.png (642×314): 히든 스킬 기 모으기 · 마력 집중(마법진) · 스킬 해방(별빛 광선)
#     오른쪽 위의 회색 '이미지' 단추와 아래 글씨는 화면 캡처 조각 → 상자로 버림
# 칸 순서: 0 대기 · 1~4 걷기 · 5~6 공격 · 7 피격 · 8~9 쓰러짐 (일반 스킬 그림은 없어서 공격 칸을 같이 씀)
# 크기: 대기 칸 기준. 대기 키(리본 꼭대기~발)를 TARGET_H로 맞추고, 다른 칸은 얼굴 폭(살색 덩어리 폭)이 대기 칸과 같아지게 줄임
#   샘플 한 장 안의 칸들은 같은 크기로 그려져 있어서 장마다 배율 하나 (그 장 얼굴 폭의 가운뎃값 기준)
#   → 칸마다 키를 따로 맞추던 때보다 머리 크기·몸 비율이 대기 칸과 같고, 걸음마다 키가 오르내리는 것도 그대로 남음
# 흰 배경 찌꺼기: 몸 칸은 바깥 배경에서 옅은 색으로만 이어지는 테두리를 모두 배경으로 보고, 줄인 뒤에도 바깥 가장자리의
#   옅은 회백색 1~2px 테를 깎음. 소매·치마 앞자락의 흰 부분은 진한 윤곽 안쪽이라 남김 (갇힌 흰색을 지우면 소매가 뚫림)
# 히든 스킬 장의 이펙트(마법진·빛줄기)는 옅은 분홍 빛이라, 바깥 흰 배경에서 이어지는 옅은 색은 밝기만큼 반투명으로 남김
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/merc/samples/mage_sr1_edit_'
OUT = 'assets/sprites/merc/mage_sr1.webp'
FUSION_OUT = 'assets/sprites/fx/mage_fusion_sr1.webp'
TARGET_H = 92   # 리본 꼭대기~발 (예전 SR 시트 topH 92와 같은 키)

# (칸 이름, 샘플, 상자 (x0, y0, x1, y1)) — 배율은 샘플(장)마다 하나
FRAMES = [
    ('idle', '1_src', (0, 0, 199, 227)),
    ('walk0', '2_walk_src', (0, 0, 141, 202)),
    ('walk1', '2_walk_src', (141, 0, 283, 202)),
    ('walk2', '2_walk_src', (283, 0, 424, 202)),
    ('walk3', '3_walk_src', None),
    ('atk0', '4_attack_hurt_death_src', (185, 0, 365, 191)),
    ('atk1', '4_attack_hurt_death_src', (410, 0, 660, 191)),
    ('hurt', '4_attack_hurt_death_src', (200, 191, 400, 372)),
    ('down0', '4_attack_hurt_death_src', (215, 372, 405, 544)),
    ('down1', '4_attack_hurt_death_src', (405, 400, 720, 544)),
]
NO_FACE = {'down1', 'charge'}   # 얼굴이 옆으로 누웠거나(쓰러짐 둘째) 별·손에 가려서(기 모으기) 얼굴 폭을 재지 않음
# 히든 스킬: (칸 이름, 샘플, 상자, (안 씀: 예전 키 맞춤 값), 땅 자리 (x, y) 샘플 좌표) — 눈으로 잰 값
#   땅 자리가 칸 기준점(발밑)이 됨. 발밑 빛 고리는 기준점 아래로 조금 내려감
#   마력 집중은 마법진 앞에 떠 있는 그림이라 땅 자리 = 발밑 그림자 (아이는 그만큼 떠 보임)
FUSION = [
    ('charge', '5_hidden_skill_src', (120, 150, 250, 280), 104, (186, 262)),
    ('focus', '5_hidden_skill_src', (232, 18, 428, 268), 120, (330, 260)),
    ('release', '5_hidden_skill_src', (424, 100, 642, 268), 104, (466, 262)),
]
# 상자 안에 걸린 조각을 흰색으로 덮음 (샘플 좌표): 기 모으기 왼쪽의 'Powerful Skill' 글씨 끝 ·
#   기 모으기 상자 오른쪽 위에 걸린 마법진 왼쪽 끝 · 마력 집중 상자 왼쪽 아래에 걸린 기 모으기 빛 고리 오른쪽 끝
CLEAR = {'charge': [(100, 150, 137, 205), (236, 150, 250, 236)], 'focus': [(232, 236, 252, 268)]}
# 아이 몸통 상자 (샘플 좌표): 이 안의 갇힌 흰색은 소매·장갑·앞치마라 남김. 밖은 마법진·빛 고리 안쪽이라 지움
KEEP = {'charge': [(145, 175, 216, 248)], 'focus': [(298, 160, 352, 242), (352, 138, 378, 165)], 'release': [(438, 185, 520, 252)]}


def face_w(rgba):
    # 얼굴 살색 덩어리 폭 (볼·이마의 밝은 살구색)
    R, G, B = (rgba[..., i].astype(int) for i in range(3))
    m = (R > 235) & (G > 190) & (G < 235) & (B > 160) & (B < 215) & (R - B > 25) & (rgba[..., 3] > 200)
    lab, n = ndi.label(m)
    big = int(np.argmax(ndi.sum(m, lab, range(1, n + 1)))) + 1
    xs = np.where(lab == big)[1]
    return xs.max() - xs.min()


def defringe(p, passes=2):
    # 바깥 가장자리에 남은 옅은 회백색 테(흰 배경과 섞인 윤곽)를 깎음. 노란 별·분홍 리본처럼 색이 진한 건 남김
    p = p.copy()
    for _ in range(passes):
        a = p[..., 3] > 0
        rgb = p[..., :3].astype(int)
        mn, mx = rgb.min(axis=2), rgb.max(axis=2)
        edge = a & ndi.binary_dilation(~a, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]])
        pale = (mn > 175) & (mx - mn < 50)
        p[..., 3] = np.where(edge & pale, 0, p[..., 3])
    return p


def load(src, box, clear=(), fx=False, keep_boxes=()):
    im = np.array(Image.open(f'{D}{src}.png').convert('RGB')).astype(float)
    for x0, y0, x1, y1 in clear: im[y0:y1, x0:x1] = 255
    if box:
        x0, y0, x1, y1 = box; im = im[y0:y1, x0:x1]
    im = np.pad(im, ((2, 2), (2, 2), (0, 0)), constant_values=255)
    mn = im.min(axis=2)
    white = (mn > 214) & (im.max(axis=2) - mn < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    # 갇힌 흰색은 몸 칸에선 지우지 않음: 이 그림은 소매·치마 앞자락이 순백이라 지우면 구멍이 남 (몸 사이로 뚫린 배경 틈은 없음)
    # 히든 스킬 칸은 마법진·고리 안쪽의 갇힌 흰색이 배경. 아이 몸통(소매·장갑·앞치마·스타킹) 상자 안의 흰색만 남김 (KEEP, 샘플 좌표)
    if fx:
        bx, by = (box[0], box[1]) if box else (0, 0)
        keep = np.zeros_like(bg)
        for x0, y0, x1, y1 in keep_boxes: keep[y0 - by + 2:y1 - by + 2, max(0, x0 - bx + 2):x1 - bx + 2] = True
        for i, sl in enumerate(ndi.find_objects(lab), 1):
            if sl is None: continue
            comp = lab[sl] == i
            if bg[sl][comp].any() or comp.sum() < 12 or mn[sl][comp].mean() <= 244 or keep[sl][comp].mean() > 0.5: continue
            bg[sl] |= comp
    # 옅은 빛(이펙트 가장자리·반짝이): 배경에서 옅은 색으로만 이어지는 곳. 몸의 흰 장갑·레이스는 진한 윤곽에 둘러싸여 안 닿음
    light = mn > 175
    ll, _ = ndi.label(light | bg)
    reach = np.isin(ll, np.unique(ll[bg])) & ~bg
    if not fx:   # 몸 칸: 옅은 테두리는 이펙트가 아니라 흰 배경 번짐 → 배경
        bg |= reach; reach = np.zeros_like(bg)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(reach, np.clip((255 - mn) / 80, 0, 1), a)
    rim = ~bg & ~reach & ndi.binary_dilation(bg, iterations=2)
    a = np.where(rim, np.clip((235 - mn) / 150, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    soft = (rim | reach)[..., None]
    im = np.where(soft, (im - 255 * (1 - al)) / al, im).clip(0, 255)
    # 상자 안에서 너무 작은 티끌(15px 미만)만 지우고 나머지 덩어리는 모두 남김
    m = a > 0.3
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
    sz = ndi.sum(m, lab, range(1, n + 1))
    a = np.where(np.isin(lab, 1 + np.where(sz >= 15)[0]), a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    body = rgba[..., 3] > 128
    # 발 가운데: 그림 아래 6% 줄
    foot = np.where(body[int(body.shape[0] * 0.94):].any(axis=0))[0].mean()
    # 잘라낸 그림의 왼쪽 위 = 샘플 좌표 (ox, oy) (패딩 2px 빼고)
    ox, oy = (box[0] if box else 0) + xs.min() - 2, (box[1] if box else 0) + ys.min() - 2
    return rgba, foot, (ox, oy)


def pack(pieces, out, label):
    # pieces: (이름, 그림, 기준점 x, 기준점 y) — 기준점 y가 없으면 그림 맨 아래
    pieces = [(n, p, c, p.shape[0] if g is None else g) for n, p, c, g in pieces]
    L = max(int(np.ceil(c)) for _, _, c, _ in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c, _ in pieces) + 3
    AY = max(int(np.ceil(g)) for _, _, _, g in pieces) + 3
    H = AY + max(2, max(int(np.ceil(p.shape[0] - g)) for _, p, _, g in pieces) + 2)
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c, g) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = AY - int(round(g))
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(out, 'WEBP', lossless=True)
    print(f'{label} cellW={cw} cellH={H} anchorX={L} anchorY={AY} count={len(pieces)}')


def main():
    loaded = [(name, src) + load(src, box) for name, src, box in FRAMES]
    idle = loaded[0][2]
    k_idle = TARGET_H / idle.shape[0]
    ref = face_w(idle) * k_idle   # 시트에서 대기 칸 얼굴 폭 (px)
    ks = {}
    for src in dict.fromkeys(s for _, s, *_ in loaded):
        if src == FRAMES[0][1]: ks[src] = k_idle; continue
        ws = [face_w(r) for n, s, r, *_ in loaded if s == src and n not in NO_FACE]
        ks[src] = ref / float(np.median(ws))
        print(f'{src}: 얼굴 폭 {ws} → ×{ks[src]:.3f}')
    pieces = []
    for name, src, rgba, foot, _ in loaded:
        k = ks[src]
        if name == 'down1': foot = rgba.shape[1] * 0.4   # 누운 칸은 몸 가운데쯤 (지팡이는 오른쪽 끝에 떨어져 있음)
        if name == 'down0':   # 무릎 꿇은 칸: 바닥에 놓인 지팡이까지 발로 치지 않게 아래쪽 40% 몸통 무게중심
            lo = rgba[int(rgba.shape[0] * 0.6):, :, 3] > 128
            foot = np.where(lo)[1].mean() if lo.any() else foot
        p = defringe(shrink(rgba, k))
        pieces.append((name, p, foot * k, None))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{k:.3f} → {p.shape[1]}x{p.shape[0]}, 발 {foot * k:.1f}')
    pack(pieces, OUT, 'mage_sr1')
    floaded = [(name, load(src, box, CLEAR.get(name, ()), fx=True, keep_boxes=KEEP.get(name, ())), g) for name, src, box, _, g in FUSION]
    # 히든 스킬 장은 칸마다 아이 크기가 달라서(마력 집중이 조금 큼) 칸마다 얼굴 폭으로 맞춤. 기 모으기는 얼굴이 가려 스킬 해방 배율을 씀
    kf = {n: ref / face_w(r) for n, (r, _, _), _ in floaded if n not in NO_FACE}
    kf['charge'] = kf['release']
    fpieces = []
    for name, (rgba, _, (ox, oy)), (gx, gy) in floaded:
        k = kf[name]
        p = shrink(rgba, k)
        fpieces.append((name, p, (gx - ox) * k, (gy - oy) * k))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{k:.3f} → {p.shape[1]}x{p.shape[0]}, 땅 ({(gx - ox) * k:.1f}, {(gy - oy) * k:.1f})')
    pack(fpieces, FUSION_OUT, 'mage_fusion_sr1')


if __name__ == '__main__':
    main()

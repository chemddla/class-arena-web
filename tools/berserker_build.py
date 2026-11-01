# 광전사 원형 샘플(흰 배경 도트, 동작마다 한 장) → 캐릭터 시트 assets/sprites/merc/berserker_0.webp
# 사용: python tools/berserker_build.py [샘플 폴더]  (기본 assets/sprites/fx/samples, 파일 berserker_src1~.png)
#   1 = 대기 (흰 배경, 왼쪽 위 한글 라벨 "대기"), 5 = 피격 (라벨 "피격"), 6 = 쓰러짐 (누운 자세),
#   9 = 걷기 네 칸 (한 장에 나란히), 11 = 기본 공격 들어 올리기 (두 도끼를 머리 위로), 10 = 기본 공격 내려치기 (흰 섬광·궤적, 큰 그림),
#   16 = 기본 공격 X자 베기 (양옆에 옆 칸 도끼가 잘려 들어옴), 12 = 광폭화 세 칸 (불길이 솟음 · 불길 속 포효 · 광폭 대기 — 붉은 얼굴·빛나는 눈, 분홍 아지랑이 배경),
#   13 = 도끼 투척 세 칸 (위에 한글·영어 제목), 14 = 날아가는 도끼 두 칸 (흰 회오리 바람 포함)
# 캐릭터 칸 순서: 0 대기 · 1~4 걷기 · 5 피격 · 6 쓰러짐 · 7~8 기본 공격 (들어 올리기 → 내려치기) · 9~10 광폭화 시전 · 11~13 도끼 투척 (뒤로 젖힘 · 던짐 · 팔을 뻗은 마무리)
#   · 16 마무리 일격 내려치기 (예전 기본 공격 내려치기 샘플 10의 회색 섬광을 붉게 — redden_fx)
#   · 14~15 야성의 포효 (광폭화 시전 두 칸에서 불을 지우고, 불빛에 물든 하반신은 대기 자세 하반신 색으로 되돌림 — make_howl)
# 날아가는 도끼 assets/sprites/fx/berserker_axe.webp: 두 칸 (흰 회오리는 흰 정도만큼 반투명), 게임에서 빙글빙글 돌리며 날림 (build_axe_fx) (쓰러짐 동작은 피격 → 누운 자세 두 칸) (모든 칸 크기 같음, 오른쪽을 봄, 발 = 기준점)
# 광폭 시트 berserker_0_rage.webp: 칸 순서·크기가 같고, 대기 = 광폭 대기 샘플, 나머지 동작 = 광폭 대기의 붉은 얼굴·빛나는 눈·붉은 기운을 입힌 그림 (enrage),
#   광폭화 시전 두 칸도 붉은 얼굴·눈빛만 입힘 (불길이 있어 붉은 기운 테두리는 안 두름). 광폭(berserk) 상태 동안 게임이 이 시트로 바꿔 그림
# 샘플 정리:
#   - 배경 흰색은 가장자리에서 이어진 흰 픽셀만 지움 (몸 안쪽 해골·도끼 날의 흰 빛은 남김)
#   - 흰 배경과 섞인 밝은 테두리는 벗겨 냄 (윤곽이 하얗게 뜨지 않게)
#   - 라벨 글자처럼 몸에서 떨어진 조각은 지움 (가장 큰 덩어리 + 몸통의 4% 넘는 조각만 남김)
#   - 크기는 대기 자세 키(머리털 끝~발)를 TARGET_H에 맞춤. 샘플마다 그린 크기가 다르면 SCALE_FIX로 대기 자세와 같은 크기로 맞춤
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT_CHAR = 'assets/sprites/merc/berserker_0.webp'
OUT_RAGE = 'assets/sprites/merc/berserker_0_rage.webp'
TARGET_H = 86  # 대기 자세 머리털 끝~발 → 게임 칸 키

# (시트, 이름[, (x0, x1)]) — 한 장에 여러 칸이면 샘플 x 범위로 자름
FRAMES = [
    (1, 'idle'),
    (9, 'walk0', (0, 186)), (9, 'walk1', (186, 355)), (9, 'walk2', (355, 529)), (9, 'walk3', (529, 705)),
    (5, 'hurt'),
    (6, 'down'),
    (11, 'atk0'), (16, 'atk1'),  # 기본 공격: 들어 올리기 → X자로 베기 (회색 X자 이펙트는 그림 그대로)
    (12, 'rage0', (0, 148)), (12, 'rage1', (148, 332)),  # 광폭화 시전: 불길이 솟음 → 불길 속 포효 (불길은 그림 그대로)
    (13, 'throw0', (0, 174)), (13, 'throw1', (174, 355)), (13, 'throw2', (355, 486)),  # 도끼 투척 (던진 도끼는 build_axe_fx 그림으로 따로 날아감)
]
EXEC_SRC = (10, 'exec1')  # 마무리 일격 내려치기 (예전 기본 공격 내려치기 샘플, 회색 섬광을 붉게)
RAGE_IDLE = (12, 'ridle', (332, 470))  # 광폭 대기 (오른쪽 끝 회색 테두리는 뺌). 광폭 시트의 대기 칸이자 붉은 얼굴·눈·털 색의 기준
HOLE_KEEP = {10: [(700, 760, 700, 770)], 12: [(80, 100, 80, 90)]}  # 갇힌 흰 덩어리 중 남길 것 (x0, x1, y0, y1): 내려치기 섬광 아래쪽 흰 속, 광폭화 시전 첫 칸의 벌린 입 이빨
RIM = {10: 8}  # 흰색이 섞인 테두리 두께 (기본 2px). 내려치기는 4.6배 큰 흐린 그림이라 번진 띠도 넓음
DROP = {11: [(0, 40, 160, 260)], 12: [(470, 479, 0, 178)]}  # 지울 상자 (x0, x1, y0, y1): 들어 올리기 샘플 왼쪽 아래에 옆 칸 도끼가 잘려 들어옴, 광폭화 샘플 오른쪽 끝 회색 테두리
HOLE_SHEETS = (9, 10, 12, 13, 16)  # 몸 안에 갇힌 흰 배경도 지울 샘플 (걷기 셋째 칸·광폭 대기·광폭화 시전 둘째 칸·도끼 투척: 팔·손과 도끼 사이, 내려치기: 머리털·다리와 섬광 사이)
KEEP_SMALL = {'exec1': 500}  # 몸에서 떨어진 조각도 이 크기(px) 넘으면 남김: 섬광에서 떨어져 나간 빛살 (내려치기 샘플은 대기의 4.6배 크기)
# 얼굴로 가로 기준을 못 잡는 칸: 발 기준점으로 쓸 샘플 x. 쓰러짐 = 머리털 끝~발끝 가운데 (오른쪽 도끼는 뺌),
# 공격 = 장화 가운데 (내딛으며 몸이 앞으로 쏠려서 얼굴로 맞추면 발이 뒤로 미끄러짐)
RAGE_SCALE = 1.31  # 광폭화 샘플은 얼굴 키(34 vs 44)·머리털 폭(80 vs 106)이 대기의 0.76배 → 대기 배율의 1.31배 (키로 맞추면 5% 작았음)
RIDLE_FOOT = 394  # 광폭 대기 장화 가운데 (샘플 x)
FOOT_X = {'down': 150, 'atk0': 140, 'atk1': 84, 'exec1': 465, 'ridle': RIDLE_FOOT, 'throw0': 97, 'throw1': 261, 'throw2': 417}  # 광폭 대기는 얼굴이 붉어서 피부로 얼굴을 못 찾음
# 키로 못 맞추는 칸: 대기 배율에 곱하는 값 (얼굴·해골 크기를 대기와 같게). 피격·쓰러짐은 대기보다 5% 안팎,
# 들어 올리기는 1.3배, 내려치기는 4.6배 크게, 도끼 투척은 0.63배 작게 그려짐
SCALE_FIX = {'hurt': 1 / 1.05, 'down': 1 / 1.05, 'atk0': 1 / 1.3, 'atk1': 1, 'exec1': 1 / 4.6, 'throw0': 1.59, 'throw1': 1.59, 'throw2': 1.59,  # 도끼 투척은 얼굴이 대기의 0.63배로 작게 그려짐
             'walk0': 1.1, 'walk1': 1.1, 'walk2': 1.1, 'walk3': 1.1}  # 걷기는 키는 대기와 비슷한데 얼굴이 0.91배로 작게 그려짐 (키로 맞추면 얼굴이 6% 작았음)
PINK_SHEETS = (12,)  # 배경에 분홍 아지랑이가 낀 샘플: 밝은 분홍까지 배경으로 보고, 몸에 붙은 분홍 띠도 4겹까지 벗겨 냄
def _skin(c): return (c[..., 3] > 200) & (c[..., 0] > 120) & (c[..., 0] > c[..., 1] + 20) & (c[..., 1] > c[..., 2]) & (c[..., 0] - c[..., 2] < 130)


def load(sheet, folder):
    im = np.array(Image.open(f'{folder}/berserker_src{sheet}.png').convert('RGB')).astype(float)
    # 흰 배경 (조금 회색빛이 도는 흰색까지)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge_ids = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge_ids[edge_ids > 0])
    if sheet in PINK_SHEETS:
        R, G, B = im[..., 0], im[..., 1], im[..., 2]
        light = (R > 195) & (G > 150) & (B > 150) & (np.abs(G - B) < 25)
        lab, n = ndi.label(light | white)
        edge_ids = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
        bg = np.isin(lab, edge_ids[edge_ids > 0])
        pink = (R > 185) & (G > 130) & (B > 130) & (np.abs(G - B) < 30)
        for _ in range(4):
            bg |= pink & ndi.binary_dilation(bg)
        white = light | white
    if sheet in HOLE_SHEETS:  # 몸·도끼 자루 사이에 갇힌 흰 배경 (공격 샘플의 팔과 앞 도끼 사이, 주먹과 자루 사이): 아주 하얀 20px 넘는 덩어리도 배경
        ids = np.arange(1, n + 1)  # (다른 샘플은 도끼 날 빛·허리천이 이만큼 하얄 수 있어서 이 샘플에만 씀)
        big = ids[(ndi.sum(white, lab, ids) >= 20) & ((ndi.mean(im.min(axis=2), lab, ids) > 235) | (sheet in PINK_SHEETS))]  # 분홍 아지랑이 샘플은 갇힌 분홍빛도
        for x0, x1, y0, y1 in HOLE_KEEP.get(sheet, ()):  # 섬광 한가운데 흰빛은 남김
            big = [i for i in big if not (x0 <= ndi.center_of_mass(lab == i)[1] < x1 and y0 <= ndi.center_of_mass(lab == i)[0] < y1)]
        bg |= np.isin(lab, big)
    # 흰 배경과 맞닿은 2px 띠는 검은 윤곽과 흰 배경이 섞인 색 → 흰색을 빼서 투명도·본래 색을 되살림
    # (그대로 줄이면 윤곽 바깥에 흰 점이 줄지어 남음). 윤곽은 거의 검정이라 밝을수록 투명하게 봄
    rim = ~bg & ndi.binary_dilation(bg, iterations=RIM.get(sheet, 2))
    a = np.where(bg, 0.0, 1.0)
    ra = np.clip((255 - im.min(axis=2)) / 225, 0, 1)
    a = np.where(rim, ra, a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    return im, a


def cut(folder, f):
    sheet, name = f[:2]
    rgb, a = load(sheet, folder)
    for x0, x1, y0, y1 in DROP.get(sheet, ()): a[y0:y1, x0:x1] = 0
    ox = 0
    if len(f) > 2:
        ox = f[2][0]; rgb, a = rgb[:, f[2][0]:f[2][1]], a[:, f[2][0]:f[2][1]]
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=1))
    areas = ndi.sum(m, lab, range(1, n + 1))
    big = np.argmax(areas) + 1
    keep = m & np.isin(lab, [i + 1 for i in range(n) if i + 1 == big or areas[i] >= areas[big - 1] * 0.04 or areas[i] >= KEEP_SMALL.get(name, 1e9)])
    a = np.where(keep, a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([rgb, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 0
    # 가로 기준 = 얼굴 가운데 (발 높이에는 도끼 날·망토 자락이 걸려 칸마다 흔들림). 발과의 차이는 main에서 대기 자세로 더함
    h = rgba.shape[0]
    face = np.zeros(k.shape, bool); face[int(h * 0.2):int(h * 0.48)] = _skin(rgba)[int(h * 0.2):int(h * 0.48)]
    lab, n = ndi.label(face)
    face = lab == np.argmax(ndi.sum(face, lab, range(1, n + 1))) + 1
    cx = np.where(face.any(axis=0))[0].mean()
    low = k[int(h * 0.9):]
    fx = FOOT_X[name] - ox - xs.min() if name in FOOT_X else None
    return rgba, cx, 0, np.where(low.any(axis=0))[0].mean(), fx


ATTACK_RANGE_SPR = (78 - 16) * 81 / 54  # 광전사 공격 사거리 78(월드 px)에 서 있는 적의 앞쪽 몸 끝(몸 반지름 16 뺌)을 시트 px로 (게임에서 standH 81 → 54px로 그림)
FX_SPLIT = {'exec1': 'red'}  # 회색 타격 이펙트(섬광·베기 궤적)를 떼어 내 공격 사거리만큼 키워 다시 붙일 칸 (red = 붉게 바꿔서). X자 베기는 그림 그대로




def split_fx(rgba):
    # 내려치기 샘플의 회색 타격 이펙트 = 채도 낮고 밝은 픽셀(섬광 X자·베기 초승달) 덩어리
    #   가장 큰 덩어리 + 그 2% 넘는 덩어리 중 그림 가운데(35%)보다 오른쪽에 있는 것만 (왼쪽 뒤 도끼 날은 빼려고)
    rgb, a = rgba[..., :3], rgba[..., 3] / 255
    L = rgb.mean(axis=2); sat = rgb.max(axis=2) - rgb.min(axis=2)
    core = (a > 0.3) & (sat < 28) & (L > 120)
    lab, n = ndi.label(core, structure=np.ones((3, 3)))
    sizes = ndi.sum(core, lab, range(1, n + 1))
    cxs = [c[1] for c in ndi.center_of_mass(core, lab, range(1, n + 1))]
    keep = [i + 1 for i in range(n) if sizes[i] >= sizes.max() * 0.02 and cxs[i] > rgba.shape[1] * 0.35]
    fx = np.isin(lab, keep)
    # 바로 옆의 어두운 회색 윤곽(3px)까지 이펙트로 봄
    fx |= ndi.binary_dilation(fx, iterations=3) & (sat < 30) & (a > 0)
    # 이펙트 덩어리 중 큰 것만 (목걸이 이빨·도끼 가시의 밝은 빛 같은 작은 조각은 몸에 남김)
    lab, n = ndi.label(fx, structure=np.ones((3, 3)))
    if n:
        sizes = ndi.sum(fx, lab, range(1, n + 1))
        fx = np.isin(lab, 1 + np.where(sizes >= sizes.max() * 0.05)[0])
    fx_rgba = np.where(fx[..., None], rgba, 0)
    # 이펙트가 덮고 있던 몸 자리는 가장 가까운 몸 색(검은 윤곽 빼고)으로 메움, 몸 바깥은 비움
    body = (a > 0.5) & ~fx
    inside = fx & ndi.binary_closing(body, iterations=12)
    src = body & (L > 45)
    _, (iy, ix) = ndi.distance_transform_edt(~src, return_indices=True)
    out = rgba.copy()
    out[inside, :3] = rgb[iy[inside], ix[inside]]
    out[inside, 3] = 255
    out[fx & ~inside] = 0
    return out, fx_rgba


def redden_fx(fx_rgba):
    # 회색 타격 이펙트 → 붉은 이펙트 (마무리 일격): 밝기에 따라 검붉은 윤곽 → 진홍 → 밝은 분홍빛 속
    L = fx_rgba[..., :3].mean(axis=2)
    ramp_L = np.array([40, 120, 190, 245])
    ramp = np.array([[80, 8, 8], [185, 25, 20], [240, 70, 50], [255, 190, 170]], float)
    out = fx_rgba.copy()
    for ch in range(3):
        out[..., ch] = np.interp(L, ramp_L, ramp[:, ch])
    return out


def paste_fx(piece, cx, below, fx_src, sc, foot_src):
    # 떼어 낸 이펙트를 (발 x, 이펙트 가운데 y)를 축으로 키워서 끝이 사거리 끝에 선 적의 앞쪽 몸(발에서 ATTACK_RANGE_SPR)에 닿게 붙임
    ys, xs = np.where(fx_src[..., 3] > 0)
    py = ys.mean()
    k = ATTACK_RANGE_SPR / ((xs.max() - foot_src) * sc)
    f = shrink(fx_src, sc * k)
    ox, oy = int(round(foot_src * sc * (1 - k))), int(round(py * sc * (1 - k)))
    h, w = piece.shape[:2]
    x0, y0 = min(0, ox), min(0, oy)
    x1, y1 = max(w, ox + f.shape[1]), max(h, oy + f.shape[0])
    out = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    out[-y0:-y0 + h, -x0:-x0 + w] = piece
    reg = out[oy - y0:oy - y0 + f.shape[0], ox - x0:ox - x0 + f.shape[1]]
    reg[:] = np.where((f[..., 3] > 0)[..., None], f, reg)
    print(f'타격 이펙트 {k:.2f}배')
    return out, cx - x0, below + max(0, y1 - h)  # 이펙트가 발 아래로 내려간 만큼 below가 늘어남


def shrink(rgba, sc):
    h, w = rgba.shape[:2]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    sm = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * sc)), max(1, round(h * sc))), Image.LANCZOS)
    a = np.array(sm).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    a[..., 3:] = np.where(al > 90, 255, np.where(al > 40, al * 2, 0))  # 도트 느낌: 반투명 가장자리를 딱딱하게
    op = a[..., 3] > 0  # 몸에서 떨어진 3px 이하 티끌은 지움
    lab, n = ndi.label(op, structure=np.ones((3, 3)))
    sizes = ndi.sum(op, lab, range(1, n + 1))
    a[..., 3] = np.where(np.isin(lab, 1 + np.where(sizes <= 3)[0]), 0, a[..., 3])
    return a.clip(0, 255).astype(np.uint8)


def _rank_map(v, pal):
    # v의 밝기 순위와 같은 순위의 pal 색을 그대로 가져옴 (팔레트 양 끝 2%는 윤곽 섞임이라 안 씀)
    pal = pal[np.argsort(pal.mean(axis=1))]
    rank = np.argsort(np.argsort(v.mean(axis=1))) / max(len(v) - 1, 1)
    return pal[np.round((0.02 + rank * 0.96) * (len(pal) - 1)).astype(int)]


def _red_face(c):  # 광폭 대기의 붉어진 얼굴 피부
    R, G, B = c[..., 0].astype(int), c[..., 1].astype(int), c[..., 2].astype(int)
    return (c[..., 3] > 200) & (R > 140) & (R > G + 60) & (R > B + 60)


def _brown(c):  # 머리털·털가죽 갈색 (피부·붉은 얼굴 빼고)
    R, G, B = c[..., 0].astype(int), c[..., 1].astype(int), c[..., 2].astype(int)
    return (c[..., 3] > 200) & (R > G) & (G >= B - 4) & (R - B > 12) & (R > 35) & ((R + G + B) / 3 < 150) & ~_skin(c) & ~_red_face(c)


def _band(c, y0, y1):
    m = np.zeros(c.shape[:2], bool); m[int(c.shape[0] * y0):int(c.shape[0] * y1)] = True
    return m


def enrage(p, ridle):
    # 광폭 상태 그림: 광폭 대기 샘플(ridle)에서 딴 붉은 얼굴·눈빛·붉은 털 색을 입힘 (줄인 뒤 칸에 바로)
    #   얼굴 = 위쪽 피부 덩어리를 광폭 대기 붉은 얼굴 색으로 (밝기 순위대로), 몸 피부는 35%만 붉게
    #   머리털(위 35%)·털가죽 갈색 = 광폭 대기의 같은 부위 색으로 70%
    #   눈 = 얼굴 덩어리 안 눈높이의 어두운 픽셀을 빛나는 빨강으로 (가운데 가로줄은 더 밝게)
    p = p.astype(float).copy()
    face_pal = ridle[_red_face(ridle)][:, :3].astype(float)
    hair_pal = ridle[_brown(ridle) & _band(ridle, 0, 0.35)][:, :3].astype(float)
    fur_pal = ridle[_brown(ridle) & _band(ridle, 0.35, 1)][:, :3].astype(float)
    # 광폭 대기 얼굴 위 문신 색: 붉은 얼굴 상자 안에서 붉은 피부·갈색·검은 윤곽·눈빛이 아닌 픽셀
    rf = _red_face(ridle); ry, rx = np.where(rf)
    rbox = np.zeros(rf.shape, bool); rbox[ry.min():ry.max() + 1, rx.min():rx.max() + 1] = True
    rc = ridle.astype(int)
    paint_pal = ridle[rbox & ~rf & ~_brown(ridle) & (rc[..., :3].mean(axis=2) > 50) & (rc[..., 2] >= rc[..., 0] - 10) & (rc[..., 3] > 200)][:, :3].astype(float)
    skin = _skin(p)
    lab, n = ndi.label(skin & _band(p, 0.12, 0.55))
    face = np.zeros_like(skin)
    if n:
        face = lab == np.argmax(ndi.sum(skin, lab, range(1, n + 1))) + 1
        # 얼굴 덩어리에 이어진 피부(문신에 끊긴 뺨 조각)까지: 얼굴 상자 안 피부 전부
        ys, xs = np.where(face)
        box = np.zeros_like(skin); box[ys.min():ys.max() + 1, xs.min() - 1:xs.max() + 2] = True
        face = skin & box
    body = skin & ~face
    rgb = p[..., :3]
    if face.any(): rgb[face] = _rank_map(rgb[face], face_pal)
    if body.any(): rgb[body] = rgb[body] * 0.65 + _rank_map(rgb[body], face_pal) * 0.35
    hair = _brown(p) & _band(p, 0, 0.35)
    fur = _brown(p) & ~hair
    if hair.any(): rgb[hair] = rgb[hair] * 0.3 + _rank_map(rgb[hair], hair_pal) * 0.7
    if fur.any(): rgb[fur] = rgb[fur] * 0.3 + _rank_map(rgb[fur], fur_pal) * 0.7
    if face.any():
        ys, xs = np.where(face)
        y0, y1 = ys.min(), ys.max()
        # 얼굴 위 파란 문신: 광폭 대기처럼 붉은 얼굴에 눌린 어두운 보랏빛으로 (얼굴 상자 안 문신만, 몸 문신은 그대로)
        fbox = np.zeros_like(face); fbox[y0:y1 + 1, xs.min() - 1:xs.max() + 2] = True
        paint = fbox & (p[..., 3] > 200) & (rgb[..., 2] > rgb[..., 0] + 25)
        if paint.any() and paint_pal.size: rgb[paint] = _rank_map(rgb[paint], paint_pal)
        eye = np.zeros_like(face)
        eye[y0 + int((y1 - y0) * 0.2):y0 + int((y1 - y0) * 0.55) + 1, xs.min():xs.max() + 1] = True
        L = rgb.mean(axis=2)
        dark = eye & fbox & (L < 75) & (p[..., 3] > 200) & ~_brown(p)  # 문신 속 눈도 (얼굴 상자 안, 머리털 갈색은 빼고)
        lab, n = ndi.label(dark, structure=np.ones((3, 3)))
        dark &= np.isin(lab, 1 + np.where(ndi.sum(dark, lab, range(1, n + 1)) >= 2)[0])  # 혼자 떨어진 1px 점은 눈이 아님
        rgb[dark] = [225, 20, 20]
        # 눈 가운데 (가로로 이어진 안쪽)는 더 밝은 빨강, 눈 바로 옆 얼굴 1px은 붉은 번짐 (광폭 대기의 눈빛 줄기)
        core = dark & ndi.binary_erosion(dark, structure=np.array([[1, 1, 1]]))
        rgb[core] = [255, 90, 60]
        glow = ndi.binary_dilation(dark, structure=np.array([[1, 1, 1]])) & ~dark & face
        rgb[glow] = rgb[glow] * 0.4 + np.array([255, 40, 30]) * 0.6
    p[..., :3] = rgb
    return p.clip(0, 255).astype(np.uint8)


def add_aura(cell):
    # 붉은 기운: 몸 테두리 바깥 2px (1겹 진하게, 2겹 옅게), 몸 뒤에 깔림
    op = cell[..., 3] > 0
    r1 = ndi.binary_dilation(op) & ~op
    r2 = ndi.binary_dilation(op, iterations=2) & ~op & ~r1
    out = cell.copy()
    out[r1] = [200, 20, 20, 170]
    out[r2] = [220, 40, 30, 80]
    return out


HOWL_WAIST = 40  # 발에서 이 높이(칸 px)까지 = 하반신: 불빛에 붉게 물든 색을 대기 자세 하반신 색으로 되돌림


def _flame(c):
    # 광폭화 시전 칸의 불길: 빨강~주황 (빨강이 초록보다 70 넘게 큼) · 노랑 (파랑이 빨강의 45% 아래, 초록 140 넘음)
    R, G, B = (c[..., i].astype(int) for i in range(3))
    return (c[..., 3] > 0) & (((R - G > 70) & (R > 80)) | ((R > 200) & (G > 140) & (B < R * 0.45)))


def make_howl(rage_piece, idle_piece):
    # 야성의 포효: 광폭화 시전 칸 → 불길을 지우고 (몸 안쪽으로 파고든 불은 가까운 몸 색으로 메움),
    #   하반신(발에서 HOWL_WAIST까지)은 불빛에 붉게 물든 색을 대기 자세 하반신 색 중 가장 가까운 색으로 바꿈
    #   (가깝다 = 빨강을 빼고 초록·파랑·밝기로 비교 — 불빛은 빨강만 올려 놓음). 검은 윤곽·도끼 회색은 그대로
    name, r, rcx, rb = rage_piece
    _, ip, icx, ib = idle_piece
    r = r.astype(float).copy()
    fl = _flame(r)
    body = (r[..., 3] > 0) & ~fl
    inside = fl & ndi.binary_closing(body, iterations=4)
    src = body & (r[..., :3].mean(axis=2) > 45)
    _, (iy, ix) = ndi.distance_transform_edt(~src, return_indices=True)
    r[inside, :3] = r[iy[inside], ix[inside], :3]
    r[fl & ~inside, 3] = 0
    h = r.shape[0]
    foot = h - 1 - rb
    ifoot = ip.shape[0] - 1 - ib
    pal = ip[max(0, ifoot - HOWL_WAIST):ifoot + 1]
    pal = pal[pal[..., 3] > 200][:, :3].astype(float)
    feat = lambda c: np.stack([c[..., 1], c[..., 2], c[..., :3].mean(axis=-1) * 0.5], axis=-1)
    pf = feat(pal)
    low = np.zeros(r.shape[:2], bool); low[max(0, foot - HOWL_WAIST):] = True
    R, G, B = r[..., 0], r[..., 1], r[..., 2]
    L = r[..., :3].mean(axis=2)
    metal = (r[..., :3].max(axis=2) - r[..., :3].min(axis=2) < 22) & (L > 70)
    fix = low & (r[..., 3] > 0) & (L > 15) & ~metal & (R > G + 8)
    if fix.any():
        q = feat(r[fix][:, :3])
        d = ((q[:, None, :] - pf[None, :, :]) ** 2).sum(axis=2)
        r[fix, :3] = pal[np.argmin(d, axis=1)]
    # 하반신 밖에도 남은 불빛: 불길 윤곽이 남긴 검붉은 테두리·팔·머리털에 비친 붉은빛 (피부가 아닌 어둡고 붉은 픽셀)
    #   → 대기 자세 전체 색 중 가장 가까운 색으로 (같은 방법)
    allp = ip[ip[..., 3] > 200][:, :3].astype(float)
    R, G, B = r[..., 0], r[..., 1], r[..., 2]
    L = r[..., :3].mean(axis=2)
    red = (r[..., 3] > 0) & (R - G > 30) & (R - B > 25) & (L < 110) & ~_skin(r)
    if red.any():
        q = feat(r[red][:, :3])
        d = ((q[:, None, :] - feat(allp)[None, :, :]) ** 2).sum(axis=2)
        r[red, :3] = allp[np.argmin(d, axis=1)]
    out = r.clip(0, 255).astype(np.uint8)
    op = out[..., 3] > 0  # 불을 지우고 떨어져 나간 작은 조각은 지움
    lab, n = ndi.label(op, structure=np.ones((3, 3)))
    sizes = ndi.sum(op, lab, range(1, n + 1))
    out[..., 3] = np.where(np.isin(lab, 1 + np.where(sizes < sizes.max() * 0.03)[0]), 0, out[..., 3])
    return ('howl' + name[-1], out, rcx, rb)


def place(pieces, L, B, H, cellW):
    sheet = np.zeros((H, cellW * len(pieces), 4), np.uint8)
    for i, (name, p, c, d) in enumerate(pieces):
        x = i * cellW + L - int(round(c))
        y = H - 2 - B - p.shape[0] + d   # 발 = 기준점 (칸 아래에서 B + 2px 위)
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    return sheet


OUT_AXE = 'assets/sprites/fx/berserker_axe.webp'
AXE_FX_BOXES = ((0, 86), (86, 172))  # 날아가는 도끼 샘플 두 칸 (x 범위)


def build_axe_fx(folder):
    # 날아가는 도끼: 흰 배경을 흰 정도만큼 투명하게 (회오리 바람은 연회색이라 반투명으로 남고, 검은 윤곽·도끼는 그대로)
    im = np.array(Image.open(f'{folder}/berserker_src14.png').convert('RGB')).astype(float)
    a = np.clip((255 - im.min(axis=2)) / 110, 0, 1)
    al = np.maximum(a, 1e-3)[..., None]
    rgb = ((im - 255 * (1 - al)) / al).clip(0, 255)
    # 회오리 바깥에 흩어진 아주 옅은 점은 지움
    a = np.where(a < 0.08, 0, a)
    cells = []
    for x0, x1 in AXE_FX_BOXES:
        c = np.dstack([rgb[:, x0:x1], a[:, x0:x1] * 255])
        ys, xs = np.where(c[..., 3] > 0)
        cells.append(c[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    S = max(max(c.shape[:2]) for c in cells) + 2  # 정사각형 칸, 도끼를 가운데에 (가운데를 축으로 돌림)
    out = np.zeros((S, S * len(cells), 4))
    for i, c in enumerate(cells):
        y, x = (S - c.shape[0]) // 2, i * S + (S - c.shape[1]) // 2
        out[y:y + c.shape[0], x:x + c.shape[1]] = c
    Image.fromarray(out.clip(0, 255).astype(np.uint8), 'RGBA').save(OUT_AXE, 'WEBP', lossless=True)
    print(f'axe fx cell={S} count={len(cells)}')


def main(folder):
    cuts = {f[1]: cut(folder, f) for f in FRAMES + [RAGE_IDLE, EXEC_SRC]}
    base = TARGET_H / cuts['idle'][0].shape[0]
    rage_sc = base * RAGE_SCALE  # 광폭화 샘플 세 칸은 같은 크기로 그려져서 함께 맞춤
    foot_off = (cuts['idle'][3] - cuts['idle'][1]) * base  # 대기 자세 발 가운데 - 얼굴 가운데 (줄인 뒤 px)
    pieces = {}
    for f in FRAMES + [RAGE_IDLE, EXEC_SRC]:
        rgba, cx, below, _, fx = cuts[f[1]]
        # 대기는 키(머리털 끝~발)로 맞추고, 나머지 칸은 대기 배율에 SCALE_FIX(얼굴 크기를 대기와 같게)를 곱함
        sc = rage_sc if f[0] == 12 else base * SCALE_FIX[f[1]] if f[1] in SCALE_FIX else TARGET_H / rgba.shape[0]
        cx = fx * sc if fx is not None else cx * sc + foot_off
        if f[1] in FX_SPLIT:
            body, fxl = split_fx(rgba)
            if FX_SPLIT[f[1]] == 'red': fxl = redden_fx(fxl)
            p, c2, b = paste_fx(shrink(body, sc), cx, int(round(below * sc)), fxl, sc, fx)
            pieces[f[1]] = (f[1], p, c2, b)
            continue
        pieces[f[1]] = (f[1], shrink(rgba, sc), cx, int(round(below * sc)))
    ridle = pieces['ridle'][1]
    normal = [pieces[f[1]] for f in FRAMES]
    normal += [make_howl(pieces['rage0'], pieces['idle']), make_howl(pieces['rage1'], pieces['idle']), pieces['exec1']]
    rage = [pieces['ridle'] if n == 'idle' else (n, enrage(p, ridle), c, d) for n, p, c, d in normal]  # 시전 두 칸도 (광폭 상태가 걸린 뒤에 나옴)
    both = normal + rage
    L = max(int(np.ceil(c)) for _, _, c, _ in both) + 4  # 붉은 기운 2px 자리까지
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c, _ in both) + 4
    B = max(d for _, _, _, d in both)
    H = max(p.shape[0] - d for _, p, _, d in both) + B + 5
    cellW = L + R
    Image.fromarray(place(normal, L, B, H, cellW), 'RGBA').save(OUT_CHAR, 'WEBP', lossless=True)
    rs = place(rage, L, B, H, cellW)
    for i, (n, *_ ) in enumerate(rage):
        if not n.startswith('rage'): rs[:, i * cellW:(i + 1) * cellW] = add_aura(rs[:, i * cellW:(i + 1) * cellW])
    Image.fromarray(rs, 'RGBA').save(OUT_RAGE, 'WEBP', lossless=True)
    idle = normal[0][1]
    hx = np.where(idle[:int(idle.shape[0] * 0.3), :, 3].any(axis=0))[0]
    print(f'char cellW={cellW} cellH={H} anchorX={L} anchorY={H - 2 - B} count={len(normal)} topH={idle.shape[0]} portraitCX={L - int(round(normal[0][2])) + int(hx.mean())}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/fx/samples')
    build_axe_fx(sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/fx/samples')

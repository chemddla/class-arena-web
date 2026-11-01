# 광전사 원형 샘플(흰 배경 도트, 동작마다 한 장) → 캐릭터 시트 assets/sprites/merc/berserker_0.webp
# 사용: python tools/berserker_build.py [샘플 폴더]  (기본 assets/sprites/fx/samples, 파일 berserker_src1~.png)
#   1 = 대기 (흰 배경, 왼쪽 위 한글 라벨 "대기"), 5 = 피격 (라벨 "피격"), 6 = 쓰러짐 (누운 자세),
#   8 = 기본 공격 두 칸 (라벨 "일반공격", 들어 올리기 · 휘둘러 베기), 9 = 걷기 네 칸 (한 장에 나란히)
# 캐릭터 칸 순서: 0 대기 · 1~4 걷기 · 5 피격 · 6 쓰러짐 · 7~8 기본 공격 (들어 올리기 · 휘둘러 베기) (쓰러짐 동작은 피격 → 누운 자세 두 칸) (모든 칸 크기 같음, 오른쪽을 봄, 발 = 기준점)
# 샘플 정리:
#   - 배경 흰색은 가장자리에서 이어진 흰 픽셀만 지움 (몸 안쪽 해골·도끼 날의 흰 빛은 남김)
#   - 흰 배경과 섞인 밝은 테두리는 벗겨 냄 (윤곽이 하얗게 뜨지 않게)
#   - 라벨 글자처럼 몸에서 떨어진 조각은 지움 (가장 큰 덩어리 + 몸통의 4% 넘는 조각만 남김)
#   - 크기는 대기 자세 키(머리털 끝~발)를 TARGET_H에 맞춤. 샘플마다 그린 크기가 다르면 SCALE_FIX로 대기 자세와 같은 크기로 맞춤
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT_CHAR = 'assets/sprites/merc/berserker_0.webp'
TARGET_H = 86  # 대기 자세 머리털 끝~발 → 게임 칸 키

# (시트, 이름[, (x0, x1)]) — 한 장에 여러 칸이면 샘플 x 범위로 자름
FRAMES = [
    (1, 'idle'),
    (9, 'walk0', (0, 186)), (9, 'walk1', (186, 355)), (9, 'walk2', (355, 529)), (9, 'walk3', (529, 705)),
    (5, 'hurt'),
    (6, 'down'),
    (8, 'atk0', (150, 400)), (8, 'atk1', (400, 729)),  # 기본 공격 샘플 한 장에 두 칸 (들어 올리기 · 휘둘러 베기, 회색 궤적은 그림 그대로)
]
HOLE_SHEETS = (8, 9)  # 몸 안에 갇힌 흰 배경도 지울 샘플 (공격: 팔·주먹과 자루 사이, 걷기 셋째 칸: 팔과 도끼 사이)
KEEP_SMALL = {'atk1': 40}  # 몸에서 떨어진 조각도 이 크기(px) 넘으면 남김: 휘두른 궤적의 가는 줄
# 얼굴로 가로 기준을 못 잡는 칸: 발 기준점으로 쓸 샘플 x. 쓰러짐 = 머리털 끝~발끝 가운데 (오른쪽 도끼는 뺌),
# 공격 = 장화 가운데 (내딛으며 몸이 앞으로 쏠려서 얼굴로 맞추면 발이 뒤로 미끄러짐)
FOOT_X = {'down': 150, 'atk0': 280, 'atk1': 485}
SCALE_FIX = {'hurt': 1 / 1.05, 'down': 1 / 1.05, 'atk0': 1, 'atk1': 1}  # 키로 못 맞추는 칸: 대기 배율에 곱하는 값. 피격·쓰러짐은 해골·얼굴·도끼가 대기보다 5% 안팎 크게 그려짐, 공격은 얼굴 폭이 대기와 같음
def _skin(c): return (c[..., 3] > 200) & (c[..., 0] > 120) & (c[..., 0] > c[..., 1] + 20) & (c[..., 1] > c[..., 2]) & (c[..., 0] - c[..., 2] < 130)


def load(sheet, folder):
    im = np.array(Image.open(f'{folder}/berserker_src{sheet}.png').convert('RGB')).astype(float)
    # 흰 배경 (조금 회색빛이 도는 흰색까지)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge_ids = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge_ids[edge_ids > 0])
    if sheet in HOLE_SHEETS:  # 몸·도끼 자루 사이에 갇힌 흰 배경 (공격 샘플의 팔과 앞 도끼 사이, 주먹과 자루 사이): 아주 하얀 20px 넘는 덩어리도 배경
        ids = np.arange(1, n + 1)  # (다른 샘플은 도끼 날 빛·허리천이 이만큼 하얄 수 있어서 이 샘플에만 씀)
        big = ids[(ndi.sum(white, lab, ids) >= 20) & (ndi.mean(im.min(axis=2), lab, ids) > 235)]
        bg |= np.isin(lab, big)
    # 흰 배경과 맞닿은 2px 띠는 검은 윤곽과 흰 배경이 섞인 색 → 흰색을 빼서 투명도·본래 색을 되살림
    # (그대로 줄이면 윤곽 바깥에 흰 점이 줄지어 남음). 윤곽은 거의 검정이라 밝을수록 투명하게 봄
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    ra = np.clip((255 - im.min(axis=2)) / 225, 0, 1)
    a = np.where(rim, ra, a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    return im, a


def cut(folder, f):
    sheet, name = f[:2]
    rgb, a = load(sheet, folder)
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


def main(folder):
    cuts = {f[1]: cut(folder, f) for f in FRAMES}
    base = TARGET_H / cuts['idle'][0].shape[0]
    foot_off = (cuts['idle'][3] - cuts['idle'][1]) * base  # 대기 자세 발 가운데 - 얼굴 가운데 (줄인 뒤 px)
    pieces = []
    for f in FRAMES:
        rgba, cx, below, _, fx = cuts[f[1]]
        # 서 있는 칸(대기·걷기)은 키(머리털 끝~발)로 맞추고, 자세가 낮은 칸은 대기 배율에 SCALE_FIX를 곱함
        sc = base * SCALE_FIX[f[1]] if f[1] in SCALE_FIX else TARGET_H / rgba.shape[0]
        cx = fx * sc if fx is not None else cx * sc + foot_off
        pieces.append((f[1], shrink(rgba, sc), cx, int(round(below * sc))))
    L = max(int(np.ceil(c)) for _, _, c, _ in pieces) + 2
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c, _ in pieces) + 2
    B = max(d for _, _, _, d in pieces)
    H = max(p.shape[0] - d for _, p, _, d in pieces) + B + 3
    cellW = L + R
    sheet = np.zeros((H, cellW * len(pieces), 4), np.uint8)
    for i, (name, p, c, d) in enumerate(pieces):
        x = i * cellW + L - int(round(c))
        y = H - 2 - B - p.shape[0] + d   # 발 = 기준점 (칸 아래에서 B + 2px 위)
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT_CHAR, 'WEBP', lossless=True)
    idle = pieces[0][1]
    hx = np.where(idle[:int(idle.shape[0] * 0.3), :, 3].any(axis=0))[0]
    print(f'char cellW={cellW} cellH={H} anchorX={L} anchorY={H - 2 - B} count={len(pieces)} topH={idle.shape[0]} portraitCX={L - int(round(pieces[0][2])) + int(hx.mean())}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/fx/samples')

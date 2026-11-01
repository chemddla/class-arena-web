# 광전사 원형 샘플(흰 배경 도트, 동작마다 한 장) → 캐릭터 시트 assets/sprites/merc/berserker_0.webp
# 사용: python tools/berserker_build.py [샘플 폴더]  (기본 assets/sprites/fx/samples, 파일 berserker_src1~.png)
#   1 = 대기 (흰 배경, 왼쪽 위 한글 라벨 "대기"), 2·3·4 = 걷기 3칸 (2·3은 바둑판 배경 큰 그림, 4는 흰 배경), 5 = 피격 (라벨 "피격"), 6 = 쓰러짐 (누운 자세)
# 캐릭터 칸 순서: 0 대기 · 1~3 걷기 · 4 피격 · 5 쓰러짐 (쓰러짐 동작은 피격 → 누운 자세 두 칸) (모든 칸 크기 같음, 오른쪽을 봄, 발 = 기준점)
# 걷기 1·2(샘플 2·3)는 대기 원본과 다르게 뽑힘 → 대기에 맞춰 손봄:
#   색감 = 피부·머리털·문신·갈색 털가죽을 부위별로, 나머지를 전체로 대기 자세의 평균·퍼짐에 맞춤 (restyle)
#   비율 = 몸이 홀쭉해서 가로로 1.1배, 디자인 = 오른손 도끼 머리가 작아서 쥔 자리 기준 1.3배 (grow_axe)
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

# (시트, 이름) — 샘플 한 장에 동작 한 칸
FRAMES = [
    (1, 'idle'),
    (2, 'walk0'), (3, 'walk1'), (4, 'walk2'),
    (5, 'hurt'),
    (6, 'down'),
]
FOOT_X = {'down': 148}  # 얼굴로 가로 기준을 못 잡는 칸: 발 기준점으로 쓸 샘플 x (잘라 낸 뒤 좌표). 쓰러짐 = 머리털 끝~발끝 가운데 (오른쪽 도끼는 뺌)
SCALE_FIX = {'hurt': 1 / 1.05, 'down': 1 / 1.05}  # 키로 못 맞추는 칸: 대기 배율에 곱하는 값. 피격·쓰러짐은 해골·얼굴·도끼가 대기보다 5% 안팎 크게 그려짐
RESTYLE = {2: 1.1, 3: 1.1}  # 대기 원본과 다르게 뽑힌 샘플: 색감을 대기에 맞추고 가로로 늘릴 배율 (restyle)
REF = {}
AXE = {2: ((400, 300, 547, 500), (400, 425), 1.3), 3: ((385, 290, 540, 490), (385, 400), 1.3)}  # 걷기 1·2 오른손 도끼 머리가 대기보다 작게(키의 22%, 대기 29%) 뽑힘: (상자, 쥔 자리, 배율)
def _skin(c): return (c[..., 3] > 200) & (c[..., 0] > 120) & (c[..., 0] > c[..., 1] + 20) & (c[..., 1] > c[..., 2]) & (c[..., 0] - c[..., 2] < 130)
def _hair(c):  # 위쪽 30%의 갈색 (피부 빼고) = 머리털
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    top = (np.arange(c.shape[0]) < c.shape[0] * 0.30)[:, None]
    return (c[..., 3] > 200) & top & (R > G) & (G >= B) & (R > 45) & (R - B > 15) & ~_skin(c)
def _fur(c):  # 나머지 갈색 (털가죽 망토·어깨 가죽·바지·장화). 도끼 회색(채도 낮음)·뼈(밝음)·검은 윤곽은 뺌
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    return (c[..., 3] > 200) & (R >= G) & (G >= B - 4) & (R - B > 12) & (R > 40) & ((R + G + B) / 3 < 165) & ~_skin(c) & ~_hair(c)
PARTS = {  # 색을 따로 맞추는 부위
    'skin': _skin,
    'hair': _hair,
    'paint': lambda c: (c[..., 3] > 200) & (c[..., 2] > c[..., 0] + 30),
    'fur': _fur,
}


def load(sheet, folder):
    im = np.array(Image.open(f'{folder}/berserker_src{sheet}.png').convert('RGB')).astype(float)
    # 대기는 흰 배경, 걷기 1·2는 회색·흰색 바둑판 배경(228~255, 채도 거의 없음)
    white = (im.min(axis=2) > 214) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge_ids = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge_ids[edge_ids > 0])
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
    sheet, name = f
    rgb, a = load(sheet, folder)
    if sheet in AXE: rgb, a = grow_axe(rgb, a, *AXE[sheet])
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=1))
    areas = ndi.sum(m, lab, range(1, n + 1))
    big = np.argmax(areas) + 1
    keep = m & np.isin(lab, [i + 1 for i in range(n) if i + 1 == big or areas[i] >= areas[big - 1] * 0.04])
    a = np.where(keep, a, 0)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([rgb, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    if sheet in RESTYLE: rgba = restyle(rgba, RESTYLE[sheet], folder)
    k = rgba[..., 3] > 0
    # 가로 기준 = 얼굴 가운데 (발 높이에는 도끼 날·망토 자락이 걸려 칸마다 흔들림). 발과의 차이는 main에서 대기 자세로 더함
    h = rgba.shape[0]
    face = np.zeros(k.shape, bool); face[int(h * 0.2):int(h * 0.48)] = _skin(rgba)[int(h * 0.2):int(h * 0.48)]
    lab, n = ndi.label(face)
    face = lab == np.argmax(ndi.sum(face, lab, range(1, n + 1))) + 1
    cx = np.where(face.any(axis=0))[0].mean()
    low = k[int(h * 0.9):]
    return rgba, cx, 0, np.where(low.any(axis=0))[0].mean()


def grow_axe(rgb, a, box, pivot, k):
    # 오른손 도끼(쥔 손 위쪽)를 쥔 자리 기준으로 k배 키움: 원래 도끼는 지우고 키운 도끼를 그 자리에 붙임 (자루는 쥔 자리에서 이어짐)
    P = 80
    rgb = np.pad(rgb, ((P, P), (P, P), (0, 0)), constant_values=255); a = np.pad(a, P)
    x0, y0, x1, y1 = (v + P for v in box); px, py = pivot[0] + P, pivot[1] + P
    piece = np.zeros_like(a); piece[y0:y1, x0:x1] = a[y0:y1, x0:x1]
    a = np.where(piece > 0, 0, a)
    pm = np.dstack([rgb * piece[..., None], piece * 255]).clip(0, 255).astype(np.uint8)
    h, w = a.shape
    T = Image.fromarray(pm, 'RGBA').transform((w, h), Image.AFFINE, (1 / k, 0, px - px / k, 0, 1 / k, py - py / k), Image.NEAREST)
    t = np.array(T).astype(float); ta = t[..., 3] / 255
    on = ta > 0
    rgb = np.where(on[..., None], t[..., :3] / np.maximum(ta, 1e-3)[..., None], rgb)
    a = np.where(on, np.maximum(a, ta), a)
    return rgb, a


def restyle(rgba, sx, folder):
    # 다르게 뽑힌 샘플을 대기 원본에 맞춤
    #   색감: 채도·대비가 높게 뽑혀 피부가 붉고 머리털이 주황빛, 문신이 튀어 보였음 → 아래처럼 대기 자세 색으로
    #   비율: 몸이 가로로 홀쭉하게 뽑혀서 가로로 sx배 늘림 (대기 자세의 다부진 체형)
    if 'idle_rgba' not in REF: REF['idle_rgba'] = cut(folder, (1, 'idle'))[0]
    # 부위마다(피부·머리털·문신) RGB 평균·퍼짐을 대기 자세의 같은 부위와 같게. 나머지(털가죽·도끼·뼈·윤곽)는 YCbCr 전체 통계로 맞춤
    #   (전체 통계 하나로 맞추면 털가죽이 많아 피부가 덜 붉고 머리털이 붉은 갈색으로 남았음)
    idle = REF['idle_rgba']
    parts = {k: f(rgba) for k, f in PARTS.items()}
    rest = (rgba[..., 3] > 200) & ~np.any(list(parts.values()), axis=0)
    rest_i = (idle[..., 3] > 200) & ~np.any([f(idle) for f in PARTS.values()], axis=0)
    ycc = np.array(Image.fromarray(rgba[..., :3].clip(0, 255).astype(np.uint8)).convert('YCbCr')).astype(float)
    ycc_i = np.array(Image.fromarray(idle[..., :3].clip(0, 255).astype(np.uint8)).convert('YCbCr')).astype(float)
    out = (ycc - ycc[rest].mean(0)) / np.maximum(ycc[rest].std(0), 1e-3) * ycc_i[rest_i].std(0) + ycc_i[rest_i].mean(0)
    rgb = np.array(Image.fromarray(out.clip(0, 255).astype(np.uint8), 'YCbCr').convert('RGB')).astype(float)
    new = np.where(rest[..., None], rgb, rgba[..., :3])
    for k, m in parts.items():
        v, vi = rgba[..., :3][m], idle[..., :3][PARTS[k](idle)]
        new[m] = (v - v.mean(0)) / np.maximum(v.std(0), 1e-3) * vi.std(0) + vi.mean(0)
    rgba = np.dstack([new.clip(0, 255), rgba[..., 3]])
    h, w = rgba.shape[:2]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    big = np.array(Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((round(w * sx), h), Image.LANCZOS)).astype(float)
    al = big[..., 3:]
    big[..., :3] = np.where(al > 0, big[..., :3] * 255 / np.maximum(al, 1), 0)
    return big


def shrink(rgba, sc):
    h, w = rgba.shape[:2]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    sm = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * sc)), max(1, round(h * sc))), Image.LANCZOS)
    a = np.array(sm).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    a[..., 3:] = np.where(al > 90, 255, np.where(al > 40, al * 2, 0))  # 도트 느낌: 반투명 가장자리를 딱딱하게
    op = a[..., 3] > 0  # 몸에서 떨어진 3px 이하 티끌은 지움 (도끼 키운 자리 테두리에서 생김)
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
        rgba, cx, below, _ = cuts[f[1]]
        # 서 있는 칸(대기·걷기)은 키(머리털 끝~발)로 맞추고, 자세가 낮은 칸은 대기 배율에 SCALE_FIX를 곱함
        sc = base * SCALE_FIX[f[1]] if f[1] in SCALE_FIX else TARGET_H / rgba.shape[0]
        cx = FOOT_X[f[1]] * sc if f[1] in FOOT_X else cx * sc + foot_off
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

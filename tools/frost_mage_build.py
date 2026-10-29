# 빙결술사 원형 샘플(흰 배경 도트 시트 2장, 한글·영어 라벨 박힘) → 캐릭터 시트 assets/sprites/merc/frost_0.webp (칸 크기 모두 같음, 오른쪽을 봄)
# 사용: python tools/frost_mage_build.py <샘플 폴더>  (샘플 폴더에 1.webp = 기본 동작, 2.webp = 스킬 동작)
# 칸 순서: 0 대기 · 1~4 걷기 · 5~7 공격 · 8~9 피격 · 10~12 쓰러짐 · 13~15 아이스애로우 · 16~17 배리어 · 18~21 프리즈 · 22~24 동결 · 25~27 스케이팅
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = 'assets/sprites/merc/frost_0.webp'
SCALE = 0.47          # 샘플 모자 끝~발 196px → 게임 칸 약 92px (마법사 topH 92)
LABEL_X = 165         # 왼쪽 라벨 글자 영역
# (시트, 이름, x0, x1, y0, y1, main) — main = 떨어져 나간 조각(반짝임·날아가는 얼음)은 지우고 몸통만 남김
FRAMES = [
    (1, 'idle',   165, 400,    0, 205, True),
    (1, 'walk0',  165, 390,  205, 415, True), (1, 'walk1', 390, 605, 205, 415, True),
    (1, 'walk2',  605, 820,  205, 415, True), (1, 'walk3', 820, 1019, 205, 415, True),
    (1, 'atk0',   165, 420,  415, 620, True), (1, 'atk1', 420, 690, 415, 620, True), (1, 'atk2', 690, 1019, 415, 620, True),
    (1, 'hurt0',  165, 440,  620, 822, True), (1, 'hurt1', 440, 700, 620, 822, True),
    (1, 'down0',  165, 418,  822, 1024, True), (1, 'down1', 418, 682, 822, 1024, True), (1, 'down2', 682, 1019, 822, 1024, True),
    (2, 'arrow0', 165, 360,    0, 205, True), (2, 'arrow1', 360, 625, 0, 205, True), (2, 'arrow2', 745, 1019, 0, 205, True),
    (2, 'bar0',   165, 403,  205, 412, True), (2, 'bar1', 403, 556, 205, 412, True),
    (2, 'frz0',   165, 395,  410, 620, False), (2, 'frz1', 395, 626, 410, 620, False),
    (2, 'frz2',   626, 848,  410, 620, False), (2, 'frz3', 848, 1019, 410, 620, False),
    (2, 'tgt0',   165, 455,  620, 822, True), (2, 'tgt1', 455, 758, 620, 822, True), (2, 'tgt2', 758, 1019, 620, 822, True),
    (2, 'skt0',   150, 380,  820, 1024, False), (2, 'skt1', 380, 598, 820, 1024, False), (2, 'skt2', 598, 834, 820, 1024, False),
]
XMAX = {'atk2': 928, 'arrow2': 942, 'tgt0': 412, 'tgt1': 672}  # 지팡이 끝 크리스탈이 끝나는 x
SRC = {}


def load(sheet, folder):
    if sheet not in SRC:
        im = np.array(Image.open(f'{folder}/{sheet}.webp').convert('RGB')).astype(int)
        bg = (255 - im).max(axis=2) < 14
        lab, _ = ndi.label(bg)
        edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
        m = ~np.isin(lab, edge[edge > 0])
        m[:, :LABEL_X] = False
        SRC[sheet] = (im, m)
    return SRC[sheet]


def cut(folder, f):
    sheet, name, x0, x1, y0, y1, main = f
    im, m = load(sheet, folder)
    sub = m[y0:y1, x0:x1].copy()
    if name in XMAX: sub[:, XMAX[name] - x0:] = False  # 지팡이 끝에 붙어 날아가는 얼음·마법진은 이펙트로 따로 그리므로 지움
    # 작은 얼룩·떨어진 조각 정리: 가까운 것끼리 한 덩어리로 보고, main이면 가장 큰 덩어리만 남김
    lab, n = ndi.label(ndi.binary_dilation(sub, iterations=1 if main else 7))
    areas = np.array([(sub & (lab == i)).sum() for i in range(1, n + 1)])
    keep = np.zeros_like(sub)
    for i in range(1, n + 1):
        if areas[i - 1] >= (250 if main else 60): keep |= sub & (lab == i)  # 모자 눈꽃 장식(약 600px)은 남기고 반짝임·날아가는 얼음은 지움
    rgb = im[y0:y1, x0:x1].astype(float)
    # 가장자리 흰 테두리(배경과 섞인 밝은 픽셀) 제거
    edge = keep & ~ndi.binary_erosion(keep)
    keep &= ~(edge & (rgb.min(axis=2) > 232))
    ys, xs = np.where(keep)
    b = (xs.min(), xs.max() + 1, ys.min(), ys.max() + 1)
    rgba = np.dstack([rgb, keep * 255.0])[b[2]:b[3], b[0]:b[1]]
    k = keep[b[2]:b[3], b[0]:b[1]]
    # 기준점 x: 몸통(아래쪽 30%) 가운데. 누워 있으면 전체 가운데
    low = k[int(k.shape[0] * 0.7):] if name[:4] != 'down' else k
    cx = np.where(low.any(axis=0))[0].mean()
    return rgba, cx


def main(folder):
    pieces = []
    for f in FRAMES:
        rgba, cx = cut(folder, f)
        h, w = rgba.shape[:2]
        # 알파 미리곱해 줄이기 (흰 테두리 번짐 방지)
        pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
        sm = Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * SCALE)), max(1, round(h * SCALE))), Image.LANCZOS)
        a = np.array(sm).astype(float)
        al = a[..., 3:]
        a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
        a[..., 3:] = np.where(al > 90, 255, np.where(al > 40, al * 2, 0))  # 도트 느낌: 반투명 가장자리를 딱딱하게
        pieces.append((f[1], a.clip(0, 255).astype(np.uint8), cx * SCALE))
    L = max(int(np.ceil(c)) for _, _, c in pieces) + 2
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 2
    H = max(p.shape[0] for _, p, _ in pieces) + 3
    cellW = L + R
    sheet = np.zeros((H, cellW * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cellW + L - int(round(c))
        y = H - 2 - p.shape[0]           # 발 = 칸 아래에서 2px 위
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    head = pieces[0]
    hx = np.where(head[1][:int(head[1].shape[0] * 0.5), :, 3].any(axis=0))[0]
    print(f'cellW={cellW} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)} topH={H - 2 - (H - 2 - head[1].shape[0])} portraitCX={L - int(round(head[2])) + int(hx.mean())}')
    for i, (name, p, c) in enumerate(pieces): print(i, name, p.shape[1], p.shape[0])


if __name__ == '__main__':
    main(sys.argv[1])

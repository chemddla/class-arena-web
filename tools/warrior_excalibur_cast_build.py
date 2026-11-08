# 전사 [엑스칼리버] 외형별 시전 그림 가공: 회색 배경 샘플(좌·우 두 자세) → 투명 webp 2칸
# ※ 옛 한손검 외형용. 2026-11-08부터 외형 1~5 시전 그림은 tools/warrior_variants_build.py가 만듦 (기본 4칸을 외형 색으로) — 이 도구를 다시 돌리면 덮어쓰니 주의
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
SRC = sys.argv[1]  # 샘플 폴더 (1.png 2.webp … 6.webp)
OUT = 'assets/sprites/fx/'
names = ['1', '2', '3', '4', '5', 'sr1']
files = ['1.png', '2.webp', '3.webp', '4.webp', '5.webp', '6.webp']
STAND = 81.0

def cut(path):
    im = np.array(Image.open(path).convert('RGB')).astype(int)
    H, W, _ = im.shape
    # 가운데 구분선
    lo = W // 2 - 30; col = im[:, lo: lo + 60].mean(axis=(0, 2))
    div = lo + int(np.argmax(col))
    bg = (np.abs(im - 40).max(axis=2) <= 12)
    bg[:, max(0, div - 6):div + 7] = True
    fg = ~bg
    lab, n = ndi.label(fg)
    sizes = ndi.sum(fg, lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    for i, s in enumerate(sizes, 1):
        if s > sizes.max() * 0.05: keep[i] = True
    fg = keep[lab]
    fg = ndi.binary_fill_holes(fg)
    rgba = np.dstack([im.clip(0, 255).astype(np.uint8), (fg * 255).astype(np.uint8)])
    return Image.fromarray(rgba, 'RGBA'), div

def bbox(a):
    ys, xs = np.where(np.array(a)[:, :, 3] > 40)
    return xs.min(), ys.min(), xs.max(), ys.max()

res = []
for n, f in zip(names, files):
    img, div = cut(SRC + '/' + f)
    W, H = img.size
    L = img.crop((0, 0, div, H)); R = img.crop((div, 0, W, H))
    x0, y0, x1, y1 = bbox(L)
    s = STAND / (y1 - y0 + 1)
    a = np.array(L)[:, :, 3]
    top = a[y0:y0 + int((y1 - y0) * 0.3)]  # 머리 쪽 가로 중심 = 기준 x
    xs = np.where((top > 40).any(axis=0))[0]
    # 머리 중심: 머리 윗부분(검 제외) 대신 윗 30% 중 가장 오른쪽 덩어리 기준이 아니라 단순 중앙
    hx = (xs.min() + xs.max()) / 2
    res.append((n, L, R, s, hx, y1))
    print(n, 'div', div, 'scale', round(s, 4), 'hx', hx, 'feet', y1)

# 기준점 기준 상하좌우 최대 범위
ext = [0, 0, 0, 0]  # left, up, right, down (스케일 후)
for n, L, R, s, hx, fy in res:
    for im in (L, R):
        x0, y0, x1, y1 = bbox(im)
        ext = [max(ext[0], (hx - x0) * s), max(ext[1], (fy - y0) * s), max(ext[2], (x1 - hx) * s), max(ext[3], (y1 - fy) * s)]
print('ext', ext)
M = 2
AX = int(np.ceil(ext[0])) + M; AY = int(np.ceil(ext[1])) + M
CW = AX + int(np.ceil(ext[2])) + M; CH = AY + int(np.ceil(ext[3])) + M
print('cell', CW, CH, 'anchor', AX, AY)
for n, L, R, s, hx, fy in res:
    sheet = Image.new('RGBA', (CW * 2, CH), (0, 0, 0, 0))
    for i, im in enumerate((L, R)):
        w, h = im.size
        # 비투명 가장자리 번짐 방지: 곱해진 알파로 축소
        arr = np.array(im).astype(float); al = arr[:, :, 3:4] / 255
        pm = np.dstack([arr[:, :, :3] * al, arr[:, :, 3:4]])
        t = Image.fromarray(pm.astype(np.float32)[:, :, 0], 'F')
        chans = [Image.fromarray(pm[:, :, k].astype(np.float32), 'F').resize((round(w * s), round(h * s)), Image.LANCZOS) for k in range(4)]
        sm = np.stack([np.array(c) for c in chans], axis=2)
        al2 = (sm[:, :, 3:4] / 255).clip(0, 1)
        rgb = np.where(al2 > 0.01, sm[:, :, :3] / np.maximum(al2, 0.01), 0).clip(0, 255)
        out = Image.fromarray(np.dstack([rgb, sm[:, :, 3:4]]).clip(0, 255).astype(np.uint8), 'RGBA')
        sheet.alpha_composite(out, (round(i * CW + AX - hx * s), round(AY - fy * s)))
    sheet.save(f'{OUT}warrior_excalibur_cast_{n}.webp', lossless=True)
    print('saved', n, sheet.size)
open('C:/Users/김성진/AppData/Local/Temp/claude/C--Users------claude-spares-spare-Ob22It/55637c53-be73-4328-8b94-7774d95b0fb0/scratchpad/dims.txt', 'w').write(f'{CW} {CH} {AX} {AY}')

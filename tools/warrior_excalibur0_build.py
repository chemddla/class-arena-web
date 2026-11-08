# 전사 기본 외형(대검 기사) [엑스칼리버] 시전 그림 → assets/sprites/fx/warrior_excalibur_cast.webp (4칸)
# 사용: python tools/warrior_excalibur0_build.py
# 샘플 (assets/sprites/fx/samples/): warrior_excal0_white_src.png · warrior_excal0_black_src.png
#   같은 그림을 흰 배경·검정 배경에 그린 두 장 (1024×268, 왼쪽 위 '기 모아서 강하게 베기' 글자)
# 칸: 0 낮게 웅크려 기를 모음 · 1 일어서며 푸른 기운이 감쌈 · 2 뛰어올라 검을 치켜듦 · 3 내려베기 (땅이 터지는 금빛 폭발·돌조각)
# 배경 제거: 두 배경 비교 → a = 1 - (흰 - 검정)/255, 색 = 검정 / a. 빛 번짐·번개·불티가 반투명 그대로 남음
#   검정 샘플은 가로 0.75px·세로 배율 1.0016 어긋나 있어 맞춰서 비교 (BLACK_FIT)
#   거의 불투명한 곳(몸)은 흰 샘플 색을 그대로 씀 (두 장이 미세하게 달라 생기는 얼룩 방지)
# 크기: 0칸 머리털 폭을 전사 시트 대기 칸 머리털 폭(게임 px)과 같게. 4칸 모두 같은 배율, 바닥 줄(샘플 y)을 그대로 맞춤
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

D = 'assets/sprites/fx/samples/warrior_excal0_'
OUT = 'assets/sprites/fx/warrior_excalibur_cast.webp'
BLACK_FIT = (1.0, 1.0016, 0.75, -0.25)   # 흰 샘플 x,y → 검정 샘플 sx·x + ox, sy·y + oy
HAIR_GAME = 110 * 0.526   # 전사 시트 대기 칸 머리털 폭 (샘플 110px × 시트 배율)
TEXT = [(0, 312, 0, 82), (0, 1024, 0, 9), (0, 30, 0, 268)]   # 지울 상자 (x0, x1, y0, y1): 글자 · 위 끝 옆 그림 조각 · 왼쪽 세로줄
GROUND = 252   # 샘플 바닥 줄 (서 있는 칸 발끝)


def hair_width(rgba):
    r, g, b, a = [rgba[..., i].astype(float) for i in range(4)]
    hair = (a > 230) & (r > g) & (g > b) & (r - b > 30) & (r < 200) & (r > 50)
    lab, n = ndi.label(ndi.binary_closing(hair, iterations=2))
    big = 1 + int(np.argmax(ndi.sum(hair, lab, range(1, n + 1))))
    xs = np.where((lab == big).any(axis=0))[0]
    return xs.max() - xs.min() + 1


def soft_shrink(rgba, sc):
    h, w = rgba.shape[:2]
    pm = rgba.astype(float); pm[..., :3] *= pm[..., 3:] / 255
    a = np.array(Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * sc)), max(1, round(h * sc))), Image.LANCZOS)).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    a[..., 3:] = np.where(al > 215, 255, np.where(al < 14, 0, al))
    return a.clip(0, 255).astype(np.uint8)


def main():
    Wi = Image.open(f'{D}white_src.png').convert('RGB')
    W = np.array(Wi).astype(float)
    sx, sy, ox, oy = BLACK_FIT
    B = np.array(Image.open(f'{D}black_src.png').convert('RGB').transform(Wi.size, Image.AFFINE, (sx, 0, ox, 0, sy, oy), Image.BILINEAR)).astype(float)
    a = np.clip(1 - (W - B).mean(axis=2) / 255, 0, 1)
    col = np.clip(B / np.maximum(a, 1e-3)[..., None], 0, 255)
    for x0, x1, y0, y1 in TEXT: a[y0:y1, x0:x1] = 0
    # 몸 = 흰 샘플에서 확실히 칠해진 곳 (밝기 205 미만) + 외곽선 안쪽의 작은 하이라이트 구멍
    #   두 장의 몸 그림이 미세하게 달라 비교값만 쓰면 몸이 반투명해짐 (특히 1칸) → 몸은 불투명·흰 샘플 색
    body = (W.mean(axis=2) < 205) & (a > 0.3)
    holes = ndi.binary_fill_holes(body) & ~body
    hl, hn = ndi.label(holes)
    hs = ndi.sum(holes, hl, range(1, hn + 1))
    body |= np.isin(hl, [j + 1 for j in range(hn) if hs[j] <= 80])
    col = np.where(body[..., None], W, col)
    a = np.where(body, 1.0, np.where(a < 0.06, 0, a))
    rgba = np.dstack([col, a * 255])
    # 칸 나누기: 네 그림은 서로 떨어진 큰 덩어리 넷. 작은 조각(불티·돌)은 가장 가까운 큰 덩어리 칸으로
    m = a > 0.1
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    sz = ndi.sum(m, lab, range(1, n + 1))
    big = sorted(np.argsort(-sz)[:4] + 1, key=lambda j: ndi.find_objects(lab)[j - 1][1].start)
    dist = [ndi.distance_transform_edt(lab != j) for j in big]
    owner = np.argmin(np.stack(dist), axis=0)
    near = np.min(np.stack(dist), axis=0) < 30   # 큰 덩어리에서 30px 넘게 떨어진 티끌은 버림

    cells, sc = [], None
    for i in range(4):
        keep = (owner == i) & near & (a > 0)
        xs = np.where(keep.any(axis=0))[0]
        x0, x1 = xs.min(), xs.max() + 1
        c = rgba[:, x0:x1].copy()
        c[..., 3] = np.where(keep[:, x0:x1], c[..., 3], 0)
        if sc is None: sc = HAIR_GAME / hair_width(c)
        k = c[..., 3] > 230
        if i == 2:   # 공중 칸: 몸 덩어리 가운데
            foot = np.where(k)[1].mean()
        else:
            rows = np.where(k.any(axis=1))[0]
            foot = np.where(k[GROUND - 12:GROUND + 1].any(axis=0))[0].mean()
        cells.append((c, foot))
        print(f'칸 {i}: 발 x {foot + x0:.0f}')
    print(f'배율 ×{sc:.3f}')
    pieces = []
    for c, foot in cells:
        ys, xs = np.where(c[..., 3] > 0)
        y0, x0 = ys.min(), xs.min()
        p = soft_shrink(c[y0:ys.max() + 1, x0:xs.max() + 1], sc)
        pieces.append((p, (foot - x0) * sc, (GROUND - y0) * sc))   # (그림, 기준점 x, 기준점 y: 그림 위에서 바닥까지)
    L = max(int(np.ceil(fx)) for _, fx, _ in pieces) + 2
    R = max(int(np.ceil(p.shape[1] - fx)) for p, fx, _ in pieces) + 2
    U = max(int(np.ceil(fy)) for _, _, fy in pieces) + 2
    Dn = max(int(np.ceil(p.shape[0] - fy)) for p, _, fy in pieces) + 2
    cw, ch = L + R, U + Dn
    sheet = np.zeros((ch, cw * len(pieces), 4), np.uint8)
    for i, (p, fx, fy) in enumerate(pieces):
        x, y = i * cw + L - int(round(fx)), U - int(round(fy))
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'warrior_excalibur_cast cellW={cw} cellH={ch} anchorX={L} anchorY={U} count={len(pieces)}')


if __name__ == '__main__':
    main()

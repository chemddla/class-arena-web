# 전사 기본 외형(warrior_0) 새 샘플 → 캐릭터 시트 assets/sprites/merc/warrior_0.webp
# 갈색 머리·은빛 판금 갑옷·붉은 목도리와 망토·어깨에 멘 대검 (흰 배경 샘플 4장, 2026-11-08)
# 사용: python tools/warrior_build.py
# 샘플 (assets/sprites/fx/samples/):
#   warrior_idle_src.png       대기 1장 (왼쪽 위 '대기 (Idle)' 글자)
#   warrior_walk_src.png       걷기 2장
#   warrior_attack_src.png     일반 공격 2장 (치켜듦 → 베기, 베기 칸의 푸른 궤적은 칼에 붙어 있어 남김, 왼쪽 글자)
#   warrior_hurt_down_src.png  위: 피격 1장 · 아래: 쓰러짐 2장 (넘어짐 → 누움), 왼쪽 글자·세로줄
#   warrior_whirl_src.png      회전베기 3장 (옆 → 뒷모습 → 앞으로 베기, 몸을 감는 푸른 바람 고리)
# 칸 순서: 0 대기 · 1~2 걷기 · 3 공격 치켜듦 · 4 공격 베기 · 5 피격 · 6~7 쓰러짐 · 8~10 회전베기
# 샘플 정리:
#   - 흰 배경은 가장자리에서 이어진 흰 픽셀만 지움 (흰 하이라이트는 검은 외곽선 안쪽이라 남음)
#   - 글자·피격 '!' 표시 = 작은 덩어리라 BOX 안에서 큰 덩어리만 남기면 빠짐
#   - 발밑 회색 그림자는 지움 (게임이 따로 그림): 그림 맨 아래 줄 색에서 시작해 비슷한 무채색 회색으로 이어진 곳만
#   - 누운 쓰러짐(2)은 머리가 오른쪽이라 좌우를 뒤집어 넘어짐(1)처럼 뒤로 넘어간 방향을 맞춤
# 크기: 대기 자세 머리털 끝~발을 TARGET_H로. 샘플 4장은 같은 배율이라 다른 칸도 대기 배율 그대로 (머리털 폭으로 확인만 함)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/warrior_'
OUT = 'assets/sprites/merc/warrior_0.webp'
# 이펙트 자리 표 (시트와 같은 크기, 흰색 = 몸이 아닌 이펙트): 흰·검정 비교로 만든 칸(회전베기·사자후·돌진)은 어디가 몸이고 어디가 이펙트인지 정확히 앎
#   → tools/warrior_variants_build.py가 외형 색을 칠할 때 바람 고리·바람 줄·흙먼지를 확실히 빼는 데 씀 (색만으로는 부츠·다리 갑옷과 갈리지 않음)
OUT_FX = 'assets/sprites/fx/samples/warrior_0_fxmask.png'
BODY = {}   # 칸 이름 → 몸 자리 (잘라 낸 그림과 같은 크기)
# 샘플 묶음별 크기 보정 (대기 칸 기준으로 통일, 2026-11-08): 샘플마다 화면 확대가 달라 같은 배율로 줄여도 머리 크기가 달랐음
#   잰 값 = 머리카락 면적의 제곱근을 대기 칸과 비교 (같은 샘플 안 칸들의 평균). 4% 안쪽은 자세 차이·재는 오차라 그대로 둠
#   걷기 0.966 (그대로) · 공격 0.939 · 피격·쓰러짐 0.950 · 회전베기 0.868 · 사자후·돌진 0.911 → 보정 = 1 / 잰 값
#   같은 샘플 안에서는 같은 배율이라 동작이 이어질 때 크기가 튀지 않음
SAMPLE_MUL = {'attack': 1 / 0.939, 'hurt_down': 1 / 0.950, 'whirl': 1 / 0.868, 'roar_charge': 1 / 0.911}
TARGET_H = 81

# (칸 이름, 샘플, 상자 x0 x1 y0 y1)
FRAMES = [
    ('idle',   'idle',      (0, 192, 0, 195)),
    ('walk1',  'walk',      (0, 167, 0, 171)),
    ('walk2',  'walk',      (167, 334, 0, 171)),
    ('atk1',   'attack',    (100, 380, 0, 178)),
    ('atk2',   'attack',    (390, 638, 0, 178)),
    ('hurt',   'hurt_down', (80, 300, 0, 168)),
    ('down1',  'hurt_down', (140, 380, 168, 337)),
    ('down2',  'hurt_down', (380, 667, 168, 337)),
    ('whirl1', 'whirl',     (0, 155, 0, 183)),
    ('whirl2', 'whirl',     (155, 340, 0, 183)),
    ('whirl3', 'whirl',     (340, 514, 0, 183)),
    ('roar1',  'roar_charge', (0, 256, 0, 262)),     # 사자후 1: 검을 내리고 숨을 들이쉼
    ('roar2',  'roar_charge', (256, 614, 0, 262)),   # 사자후 2: 주먹을 내밀며 포효. 샘플의 음파 고리는 빼고(BODY_ONLY), 3번째 그림은 쓰지 않음 (사용자 요청)
    ('dash1',  'roar_charge', (80, 370, 262, 502)),  # 돌진 1: 몸을 앞으로 숙이며 출발
    ('dash2',  'roar_charge', (370, 690, 262, 502)), # 돌진 2: 검을 앞세워 달림 (바람 줄·흙먼지)
    ('dash3',  'roar_charge', (690, 1024, 262, 502)),# 돌진 3: 멈춰 서며 검을 끌어내림 (발 뒤 흙먼지)
]
FLIP = {'down2'}
# 검정 배경 샘플이 같이 온 칸: 흰 배경·검정 배경 두 장을 비교해 투명도를 셈 (바람 고리처럼 반투명한 부분이 흰 테·잘림 없이 남음)
#   흰 배경 W = a·c + (1-a)·255, 검정 배경 B = a·c → a = 1 - (W - B)/255, c = B / a
#   검정 샘플은 크기·위치가 달라 칸마다 맞춘 값 (흰 샘플 x,y → 검정 샘플 sx·x + ox, sy·y + oy): 외곽선 차이가 가장 작은 값을 찾음
#   몸 안쪽(흰 배경 방식으로 확실히 불투명한 곳)은 흰 샘플 색 그대로, 발밑 그림자는 그대로 지움
BLACK = {'whirl': 'whirl_black'}
BLACK_FIT = {'whirl1': (2.011, 2.033, 0.0, -4.41), 'whirl2': (2.02, 1.975, 0.9, 1.89), 'whirl3': (2.0, 2.0285, 2.1, -3.46)}
# 사자후·돌진 샘플 (warrior_roar_charge_src.png + _black_src.png, 1024×502, 두 장이 픽셀 단위로 맞음): 몸은 흰 샘플에서 확실히 칠해진 곳(밝기 205 미만)과
#   외곽선 안쪽 작은 구멍을 불투명하게, 그 밖(음파·바람 줄·흙먼지)은 두 배경 비교값. 그림이 더 크게 그려져 사자후 1의 키(머리털 끝~발)를 TARGET_H로 맞춘 배율을 샘플 전체에 씀
MATTE = {'roar_charge': 'roar_charge_black'}
BODY_ONLY = {'roar2'}   # 몸 덩어리만 남김 (몸에서 떨어진 음파 고리·반투명 이펙트는 버림)
MATTE_CUT = {'roar_charge': [(0, 135, 0, 66), (0, 165, 262, 320), (915, 965, 395, 440)]}   # 지울 상자 (x0, x1, y0, y1): '사자후'·'돌진' 글자, 검정 샘플 오른쪽 아래 반짝이 표시


def hair_mask(rgba):
    r, g, b, a = [rgba[..., i].astype(float) for i in range(4)]
    return (a > 200) & (r > g) & (g > b) & (r - b > 30) & (r < 210) & (r > 60)


def load(src, box, flip, name=None):
    im = np.array(Image.open(f'{D}{src}_src.png').convert('RGB')).astype(float)
    full = im.shape
    x0, x1, y0, y1 = box
    im = im[y0:y1, x0:x1]
    if flip: im = im[:, ::-1]
    raw = im.copy()
    white = (im.min(axis=2) > 222) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    # 다리 사이·팔과 몸 사이에 갇힌 흰 배경: 가장자리와 안 이어져도 배경색(약 250)에 가깝고 40px 이상이면 배경
    #   (갑옷·칼날 하이라이트는 평균 230~243, 베기 궤적 안쪽은 245라 남음)
    for i in range(1, n + 1):
        if i in edge: continue
        m = lab == i
        if m.sum() >= 40 and im[m].mean() >= 247.5: bg |= m
    # 큰 덩어리만 (글자·'!' 표시 빼기)
    fg = ~bg
    lab, n = ndi.label(ndi.binary_dilation(fg, iterations=2))
    sz = ndi.sum(fg, lab, range(1, n + 1))
    keep = [i + 1 for i in range(n) if sz[i] >= sz.max() * 0.25]
    bg = bg | ~np.isin(lab, keep)
    # 발밑 그림자: 무채색 중간 회색, 맨 아래 줄에서 이어진 것
    grey = ~bg & (((im.max(axis=2) - im.min(axis=2) < 22) & (im.mean(axis=2) > 95) & (im.mean(axis=2) < 225)) | ((im.max(axis=2) - im.min(axis=2) < 10) & (im.mean(axis=2) > 60)))   # 그림자 윗선은 더 어두운 회색(약 70)
    ys = np.where((~bg).any(axis=1))[0]
    low = np.zeros_like(grey); low[int(ys.max() - (ys.max() - ys.min()) * 0.22):] = True
    glab, _ = ndi.label(grey & low)
    band = glab[ys.max() - 2:ys.max() + 1]   # 맨 아래 3줄에 닿는 회색 = 그림자
    seeds = np.unique(band[band > 0])
    shadow = np.isin(glab, seeds)
    # 그림자 둘레 흐린 테두리도 같이
    shadow = shadow | (ndi.binary_dilation(shadow, iterations=2) & low & (im.max(axis=2) - im.min(axis=2) < 30) & (im.mean(axis=2) > 80))
    bg = bg | shadow
    # 발 사이에 남은 그림자 윗가장자리 띠: 바로 아래가 배경인 회색(외곽선보다 밝은 무채색)을 아래에서 위로 몇 줄 걷어 냄
    #   (부츠는 검은 외곽선이 아래를 막고 있어 안 걷힘)
    hang = low & (im.max(axis=2) - im.min(axis=2) < 40) & (im.mean(axis=2) > 100)
    for _ in range(6):
        below = np.zeros_like(bg); below[:-1] = bg[1:]
        bg = bg | (hang & below & ~bg)
    lab, n = ndi.label(~bg)
    sz = ndi.sum(~bg, lab, range(1, n + 1))
    bg = bg | ~np.isin(lab, [i + 1 for i in range(n) if sz[i] >= sz.max() * 0.05])
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    if src in BLACK:
        sx, sy, ox, oy = BLACK_FIT[name]
        Bi = Image.open(f'{D}{BLACK[src]}_src.png').convert('RGB')
        B = np.array(Bi.transform((full[1], full[0]), Image.AFFINE, (sx, 0, ox, 0, sy, oy), Image.BILINEAR)).astype(float)[y0:y1, x0:x1]
        matte = np.clip(1 - (raw - B).mean(axis=2) / 255, 0, 1)
        core = ndi.binary_erosion(a >= 0.99, iterations=1) & (ndi.median_filter(matte, 3) > 0.8)
        col = np.clip(B / np.maximum(matte, 1e-3)[..., None], 0, 255)
        im = np.where(core[..., None], raw, col)
        a = np.where(core, 1.0, np.where(matte < 0.08, 0, matte))
        a[shadow] = 0
        lab, n = ndi.label(a > 0.3)   # 몸에서 떨어진 잡티 (정렬 어긋남) 지움
        sz = ndi.sum(a > 0.3, lab, range(1, n + 1))
        a = np.where(ndi.binary_dilation(np.isin(lab, [i + 1 for i in range(n) if sz[i] >= 30]), iterations=3), a, 0)
    a = np.where(a < 0.12, 0, a)
    ys, xs = np.where(a > 0)
    rgba = np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    if src in BLACK: BODY[name] = ndi.binary_dilation(core, iterations=2)[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 127
    rows = np.where(k.any(axis=1))[0]
    foot = np.where(k[int(rows.max() - (rows.max() - rows.min()) * 0.08):].any(axis=0))[0].mean()
    hm = hair_mask(rgba)
    hy, hx = np.where(hm)
    top = hy.min()
    return rgba, foot, rows.max() - top + 1, hx.max() - hx.min() + 1, hx.mean()


def load_matte(src, box, name=None):
    W = np.array(Image.open(f'{D}{src}_src.png').convert('RGB')).astype(float)
    B = np.array(Image.open(f'{D}{MATTE[src]}_src.png').convert('RGB')).astype(float)
    a = np.clip(1 - (W - B).mean(axis=2) / 255, 0, 1)
    col = np.clip(B / np.maximum(a, 1e-3)[..., None], 0, 255)
    for x0, x1, y0, y1 in MATTE_CUT.get(src, ()): a[y0:y1, x0:x1] = 0
    body = (W.mean(axis=2) < 205) & (a > 0.3)
    holes = ndi.binary_fill_holes(body) & ~body
    hl, hn = ndi.label(holes)
    hs = ndi.sum(holes, hl, range(1, hn + 1))
    body |= np.isin(hl, [j + 1 for j in range(hn) if hs[j] <= 80])
    col = np.where(body[..., None], W, col)
    a = np.where(body, 1.0, np.where(a < 0.06, 0, a))
    x0, x1, y0, y1 = box
    a, col, body = a[y0:y1, x0:x1], col[y0:y1, x0:x1], body[y0:y1, x0:x1]
    m = a > 0.1   # 가장 큰 덩어리(몸) + 그 곁 25px 안의 조각(흙먼지·음파)만
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    sz = ndi.sum(m, lab, range(1, n + 1))
    main = lab == 1 + int(np.argmax(sz))
    near = ndi.distance_transform_edt(~main) < 25
    keep = np.isin(lab, np.unique(lab[near & m]))
    keep = ndi.binary_dilation(keep, iterations=2) & (a > 0)
    a = np.where(keep, a, 0); body &= keep
    if name in BODY_ONLY:
        bl, bn = ndi.label(body, structure=np.ones((3, 3)))
        main_body = bl == 1 + int(np.argmax(ndi.sum(body, bl, range(1, bn + 1))))
        a = np.where(ndi.binary_dilation(main_body, iterations=1), a, 0)
        body &= main_body
    ys, xs = np.where(a > 0)
    sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    rgba = np.dstack([col, a * 255])[sl]
    body = body[sl]
    BODY[name] = ndi.binary_dilation(body)
    rows = np.where(body.any(axis=1))[0]
    gnd = rows.max()   # 몸(불투명) 맨 아래 = 바닥 줄 (음파·먼지는 더 아래로 내려갈 수 있음)
    foot = np.where(body[int(gnd - (gnd - rows.min()) * 0.08):gnd + 1].any(axis=0))[0].mean()
    hy, hx = np.where(hair_mask(rgba))
    return rgba, foot, gnd - hy.min() + 1, hx.max() - hx.min() + 1, hx.mean(), gnd


def trim_halo(sheet, passes=2):
    # 흰 배경 찌꺼기: 검은 외곽선 바깥에 남은 1px 연회색 테두리 (배경과 섞인 가장자리)
    #   투명한 곳에 닿아 있고 + 밝은 무채색 + 바로 옆에 어두운 외곽선이 있는 픽셀만 지움
    #   (외곽선이 없는 바람 고리·궤적·먼지·바람 줄은 어두운 이웃이 없어 남음)
    out = sheet.copy()
    k = np.ones((3, 3), bool)
    for _ in range(passes):
        a = out[..., 3].astype(int)
        rgb = out[..., :3].astype(int)
        lum = rgb.mean(axis=2)
        chroma = rgb.max(axis=2) - rgb.min(axis=2)
        clear = a < 40
        dark = (a > 200) & (lum < 75)
        halo = (a > 0) & ndi.binary_dilation(clear, structure=k) & ndi.binary_dilation(dark, structure=k) & (lum > 120) & (chroma < 50)
        out[halo] = 0
    return out


def soft_shrink(rgba, sc):   # 반투명을 살린 축소 (바람 고리용). 거의 불투명한 곳만 딱딱하게
    h, w = rgba.shape[:2]
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:] / 255
    a = np.array(Image.fromarray(pm.clip(0, 255).astype(np.uint8), 'RGBA').resize((max(1, round(w * sc)), max(1, round(h * sc))), Image.LANCZOS)).astype(float)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1), 0)
    a[..., 3:] = np.where(al > 215, 255, np.where(al < 14, 0, al))
    return a.clip(0, 255).astype(np.uint8)


def main():
    pieces = []
    sc, src_sc = None, {}
    for name, src, box in FRAMES:
        if src in MATTE:
            rgba, foot, bh, hw, hcx, gnd = load_matte(src, box, name)
        else:
            rgba, foot, bh, hw, hcx = load(src, box, name in FLIP, name)
            gnd = rgba.shape[0] - 1
        if sc is None: sc = TARGET_H / bh
        if src in MATTE and src not in src_sc: src_sc[src] = TARGET_H / bh   # 이 샘플 첫 칸(사자후 1)의 키로 샘플 배율
        s = src_sc.get(src, sc) * SAMPLE_MUL.get(src, 1)
        p = soft_shrink(rgba, s) if src in BLACK or src in MATTE else shrink(rgba, s)
        if name in BODY:   # 이펙트만 남긴 그림을 같은 배율로 줄여 이펙트 자리 표에 씀
            fxa = rgba.copy(); fxa[..., 3] = np.where(BODY[name], 0, fxa[..., 3])
            fx = soft_shrink(fxa, s)[..., 3]
            fx = np.where(fx.astype(int) * 2 >= p[..., 3].astype(int), fx, 0)[:p.shape[0], :p.shape[1]]   # 몸과 섞인 가장자리는 몸 쪽
        else:
            fx = np.zeros(p.shape[:2], np.uint8)
        pieces.append((name, p, foot * s, (gnd + 1) * s, fx))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} 키 {bh} 머리털 폭 {hw} ×{s:.3f} → {p.shape[1]}x{p.shape[0]}  발 {foot:.0f}')
    L = max(int(np.ceil(c)) for _, _, c, _, _ in pieces) + 3
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c, _, _ in pieces) + 3
    U = max(int(np.ceil(g)) for _, _, _, g, _ in pieces) + 1
    Dn = max(int(np.ceil(p.shape[0] - g)) for _, p, _, g, _ in pieces) + 2
    H = U + Dn
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    fxsheet = np.zeros((H, cw * len(pieces)), np.uint8)
    for i, (name, p, c, g, fx) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = U - int(round(g))
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
        fxsheet[y:y + fx.shape[0], x:x + fx.shape[1]] = np.where(fx > 0, 255, 0)
    sheet = trim_halo(sheet)
    fxsheet[sheet[..., 3] == 0] = 0
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    Image.fromarray(fxsheet, 'L').save(OUT_FX)
    print('cells:', ' '.join(f'{i}={n}' for i, (n, _, _) in enumerate(FRAMES)))
    print(f'warrior_0 cellW={cw} cellH={H} anchorX={L} anchorY={U} count={len(pieces)}')


if __name__ == '__main__':
    main()

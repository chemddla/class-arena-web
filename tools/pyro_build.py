# 화염술사 전용 샘플(붉은 포니테일·주홍 로브·손 위 불덩이, 흰 배경 한 장에 동작 8개 + 한글 이름표) → 캐릭터 시트 assets/sprites/merc/pyro_0.webp
# 사용: python tools/pyro_build.py   (샘플 assets/sprites/fx/samples/pyro_src.webp, 909×1024)
# 칸 순서: 0 대기 · 1~2 걷기 · 3 공격 준비 (손 앞에 불덩이와 불꽃 고리) · 4 공격 발사 (손을 뻗음, 날아가는 불덩이는 게임이 따로 그림)
#   · 5 피격 · 6~7 쓰러짐 (뒤로 넘어짐 → 누움) · 8 화염 시전 (두 손 사이에 불덩이를 모으고 불티가 흩날림, 파이어볼·화염 산탄)
#   · 9 파이어볼 발사 (주먹을 내지름) · 10 화염 산탄 발사 (손을 뻗음, 손 앞 불꽃 분출은 이펙트로 따로)
#   - 9·10번 샘플(FB_SRC 209×210, SC_SRC 443×261)은 8번 샘플과 같은 도트 크기라 8번 배율을 그대로 씀
#     · 파이어볼 샘플 왼쪽 끝 불덩이는 그림 밖으로 잘려 있어서 버림, 주먹 끝 작은 불꽃은 이펙트 flash
#     · 산탄 샘플은 손 끝(SC_HAND_X)부터 오른쪽이 불꽃 분출 → 이펙트 burst, 연기 꼬리가 달린 불덩이 하나(SC_BOLT_AT)는 산탄 투사체 bolt
#   · 11 대폭발 발동 (주먹 쥐고 버팀, 둘레에 불티가 흩날림) · 12 대폭발·메테오 시전 (한 손을 치켜듦, 머리 위 불길·발밑 불꽃 고리)
#   - 11·12번 샘플(178×150, 144×188)은 도트가 더 작게 그려져서 머리 크기를 대기 자세와 맞춘 배율 POSE_K를 씀
#     · 12번은 발밑 불길이 발보다 아래로 내려와 있어서 장화 바닥 줄(foot_y)을 기준점에 맞추고, 그 아래 불길은 기준점 아래로 그림
#     · 12번 다리 사이에 떠 있는 살구색 줄 하나는 지움 (CUT)
#   · 13 불의 고리 시전 (가슴 앞에 불꽃을 쥠, 발밑 불꽃 고리) · 14 불의 고리 발동 (허리 둘레에 큰 불꽃 고리)
#   - 13·14번 샘플(165×203, 299×214)은 발밑 연보라 그림자를 지움 (SHADOW: 그 줄 아래 연보라 픽셀 = 배경)
#   - 13번 발밑 불꽃 고리는 따로 떼어 이펙트 ring으로도 저장 (불의 고리가 유지되는 동안 발밑에 깔림, 기준점 = 고리 가운데)
#     · 몸에 가려 그려져 있지 않던 뒤쪽 가운데는 앞쪽 가운데 띠를 뒤집어 채움
# 불의 고리 이펙트 RING_OUT (샘플 RINGFX_SRC 825×1024 한 장에 여러 칸, ×RINGFX_K): 칸 이름 = RING_FRAMES 순서 (게임 PYRO_RING_FX.anims)
#   - in = 고리가 피어오름 (1줄 3칸) · loop = 허리 고리 + 발밑 고리가 함께 타오름 (2줄 오른쪽 3칸 + 3줄 첫 칸) · out = 흩어짐 (4줄 왼쪽)
#   - 칸마다 기준점 = 발밑 고리 가운데 (아래쪽 RING_LOW 비율 안 픽셀의 상자 가운데) → 칸이 바뀌어도 고리가 제자리
#   - 고리가 두 개인 칸(loop·out)은 위 고리(허리)와 발밑 고리를 나눠 '<이름>_hi'·'<이름>' 두 칸으로 저장
#     (게임에서 발밑 고리는 판정 범위 크기로 바닥에, 위 고리는 캐릭터 몸 크기로 허리에 따로 그림. _hi 기준점 = 위 고리 가운데)
#   - 3줄 가운데·4줄 오른쪽의 넓은 칸은 아래 고리 두 개가 한 칸에 겹쳐 있어 뺌
# 기본 공격 피격 이펙트 hit (샘플 HIT_SRC, 불티가 사방으로 튐, 기준점 = 가운데) → FX_OUT
# 이펙트 시트 FX_OUT: ember (기본 공격 불씨, 큰 샘플 ×FX_SCALE) · bolt · burst · flash (따로 받은 샘플 그대로 1배, 게임에서 배율을 곱해 그림)
#   - 8번은 따로 받은 샘플(CAST_SRC, 191×212)이라 크기가 달라서 키를 CAST_H로 맞춤. 몸에서 떨어진 불티 조각까지 모두 살림
# 샘플 정리:
#   - 흰 배경 = 가장자리에서 이어진 흰 픽셀 + 갇힌 흰 덩어리 중 ENCLOSED_MIN 이상 (불꽃 고리 안쪽·팔 사이 틈). 눈의 흰 하이라이트는 남김
#   - 그림마다 3px 넓힌 덩어리(손 위 불덩이·튀는 불티까지 한 덩어리)로 고르고, 그 아래 한글 이름표 줄은 잘라 냄 (CUT_Y)
#   - 발사 칸 오른쪽에 따로 떨어진 불덩이는 다른 덩어리라 캐릭터 칸에서는 빠지고, 기본 공격 불씨 투사체로 따로 저장 (FX_OUT, 기준점 = 앞 끝)
# 크기: 샘플은 모든 동작을 같은 크기로 그려서 대기 자세 키(머리카락 꼭대기~발)를 TARGET_H로 맞춘 배율 하나를 모든 칸에 씀
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

SRC = 'assets/sprites/fx/samples/pyro_src.webp'
OUT = 'assets/sprites/merc/pyro_0.webp'
FX_OUT = 'assets/sprites/fx/pyro_fx.webp'   # 기본 공격 불씨 (날아가는 불덩이)
EMBER_AT = (820, 523)   # 샘플에서 날아가는 불덩이 한 점
FX_SCALE = 0.5          # 투사체 시트 배율 (게임에서는 h로 다시 줄여 그림)
ENCLOSED_MIN = 15   # 갇힌 흰 덩어리가 이 px 이상이면 배경
CAST_SRC = 'assets/sprites/fx/samples/pyro_cast_src.png'
FB_SRC = 'assets/sprites/fx/samples/pyro_fireball_src.png'
SC_SRC = 'assets/sprites/fx/samples/pyro_scatter_src.png'
RINGFX_SRC = 'assets/sprites/fx/samples/pyro_ringfx_src.webp'
RING_OUT = 'assets/sprites/fx/pyro_ring_fx.webp'
RINGFX_K = 0.5
RING_LOW = 0.45
RING_FRAMES = [   # (이름, 샘플 상자 x0, x1, y0, y1)
    ('in0', 225, 396, 135, 246), ('in1', 427, 606, 110, 246), ('in2', 636, 813, 110, 246),
    ('loop0', 211, 404, 290, 503), ('loop1', 412, 618, 290, 503), ('loop2', 621, 823, 290, 503), ('loop3', 0, 202, 540, 768),
    ('out0', 0, 190, 830, 1024),
]
HIT_SRC = 'assets/sprites/fx/samples/pyro_hit_src.png'
POSE_K = 0.66   # 11·12번 샘플 → 칸 배율
# (칸 이름, 샘플, 장화 바닥 줄 (None = 그림 바닥), 지울 상자들 (x0, x1, y0, y1))
POSES = [
    ('combust', 'assets/sprites/fx/samples/pyro_combust_src.png', None, []),
    ('raise', 'assets/sprites/fx/samples/pyro_raise_src.png', 172, [(60, 82, 157, 161)]),
    ('ringcast', 'assets/sprites/fx/samples/pyro_ringcast_src.png', 184, [], 'ring'),
    ('ring', 'assets/sprites/fx/samples/pyro_ring_src.png', 196, [], 'ring'),
]
RING_K = 0.5    # 13·14번 샘플 → 칸 배율
SHADOW = {'ringcast': 140, 'ring': 150}   # 이 줄 아래 연보라 그림자 = 배경
RING_FX_TOP = 133   # 13번 샘플: 이 줄 아래 불꽃색 픽셀 = 발밑 고리 (치맛자락 상자 RING_FX_SKIP은 빼고)
RING_FX_SKIP = (45, 121, 0, 159)   # 치맛자락 (159줄 아래는 고리 뒤쪽이 다리 뒤로 지나감)
SC_BODY_X = 161          # 산탄 샘플: 캐릭터는 이 열 왼쪽까지 (161~163열은 손가락과 분출이 겹쳐서 양쪽 다 버림)
SC_HAND_X = 164          # 산탄 샘플: 이 열부터 오른쪽은 손 앞 불꽃 분출
SC_BOLT_AT = (340, 140)  # 산탄 샘플: 투사체로 쓸 불덩이(가운데 긴 것) 한 점
CAST_H = 86     # 시전 자세 키 (살짝 몸을 숙여서 대기 90보다 조금 작게)
TARGET_H = 90   # 대기 자세 키 → 게임 칸 키 (마법사 topH 92, 소환사 88과 비슷하게)

# (칸 이름, 덩어리를 고를 샘플 안 한 점 (x, y), 이 줄 아래는 이름표라 버림)
FRAMES = [
    ('idle', (150, 200), 334),
    ('walk0', (500, 200), 330), ('walk1', (760, 200), 330),
    ('atk0', (200, 550), 671), ('atk1', (600, 550), 671),
    ('hurt', (140, 850), 979),
    ('down0', (430, 870), 981), ('down1', (700, 950), 981),
]


def prep(path, shadow_y=None):
    # 흰 배경 지우기 → (색, 알파 0~1). shadow_y: 그 줄 아래 연보라 그림자도 배경
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    white = (im.min(axis=2) > 222) & (im.max(axis=2) - im.min(axis=2) < 26)
    if shadow_y is not None:
        sh = (im.min(axis=2) > 165) & (im.max(axis=2) - im.min(axis=2) < 45) & (im[..., 2] >= im[..., 0] - 10)
        sh |= (im.min(axis=2) > 180) & (np.abs(im[..., 1] - im[..., 2]) < 15)   # 불빛이 비친 분홍빛 그림자 가장자리 (피부·바지는 초록이 파랑보다 25 넘게 큼)
        sh[:shadow_y] = False
        white |= sh
    lab, _ = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    # 가장자리와 이어지지 않은 흰 덩어리도 15px 이상이면 배경 (공격 준비 칸 불꽃 고리 안쪽, 팔과 몸 사이로 비친 배경). 눈 하이라이트는 15px보다 작음
    sz = ndi.sum(white, lab, range(1, lab.max() + 1))
    bg |= np.isin(lab, 1 + np.where(sz >= ENCLOSED_MIN)[0]) & white
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 225, 0, 1), a)   # 흰 배경과 섞인 가장자리는 흰색을 빼고 반투명으로
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    return im, a


FX_EXTRA = {}


def main():
    im, a = prep(SRC)
    fg = a > 0.5
    blobs, _ = ndi.label(ndi.binary_dilation(fg, iterations=3))

    pieces, scale = [], None
    for name, (px, py), cut_y in FRAMES:
        near = blobs[py - 40:py + 40, px - 40:px + 40]
        ids, cnt = np.unique(near[near > 0], return_counts=True)
        bid = ids[np.argmax(cnt)]
        m = (blobs == bid) & (a > 0)
        m[cut_y + 1:] = False
        ys, xs = np.where(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.dstack([im, np.where(m, a, 0) * 255])[y0:y1, x0:x1]
        if scale is None:
            scale = TARGET_H / (y1 - y0)
        k = rgba[..., 3] > 128
        foot = np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()
        p = shrink(rgba, scale)
        pieces.append((name, p, foot * scale))
        print(f'{name}: 샘플 {x1 - x0}x{y1 - y0} ×{scale:.3f} → {p.shape[1]}x{p.shape[0]}  발 {foot:.0f}')
    # 8 화염 시전: 따로 받은 샘플 한 장 (그림 전체, 흩날리는 불티 포함)
    cim, ca = prep(CAST_SRC)
    ys, xs = np.where(ca > 0)
    rgba = np.dstack([cim, ca * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = rgba[..., 3] > 128
    big, _ = ndi.label(k)
    sizes = ndi.sum(k, big, range(1, big.max() + 1))
    body = big == 1 + int(np.argmax(sizes))
    bys = np.where(body.any(axis=1))[0]
    csc = CAST_H / (bys.max() - bys.min() + 1)   # 몸 키 (불티 조각 빼고)
    foot = np.where(body[int(bys.max() * 0.92):].any(axis=0))[0].mean()
    p = shrink(rgba, csc)
    pieces.append(('cast', p, foot * csc))
    print(f'cast: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{csc:.3f} → {p.shape[1]}x{p.shape[0]}  발 {foot:.0f}')

    def blob_of(a_, at):
        bl, _ = ndi.label(ndi.binary_dilation(a_ > 0.5, iterations=2))
        return (bl == bl[at[1], at[0]]) & (a_ > 0)

    def crop(im_, a_, m):
        ys, xs = np.where(m)
        return np.dstack([im_, np.where(m, a_, 0) * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1], xs.min(), ys.min()

    hands = {}
    # 9 파이어볼 발사: 가장 큰 덩어리 (몸), 주먹 끝 불꽃은 flash
    fim, fa = prep(FB_SRC)
    bl, n = ndi.label(ndi.binary_dilation(fa > 0.5, iterations=2))
    sz = ndi.sum(fa > 0.5, bl, range(1, n + 1))
    body = (bl == 1 + int(np.argmax(sz))) & (fa > 0)
    rgba, bx0, by0 = crop(fim, fa, body)
    k = rgba[..., 3] > 128
    foot = np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()
    pieces.append(('fb', shrink(rgba, csc), foot * csc))
    by1 = by0 + rgba.shape[0] - 2   # 발 높이 (샘플)
    flash_m = np.zeros_like(body)
    for i in range(n):   # 몸 오른쪽(주먹 끝) 작은 덩어리들 = 주먹 불꽃 (왼쪽 끝 잘린 불덩이는 빼고)
        ys, xs = np.where(bl == i + 1)
        if i + 1 != 1 + int(np.argmax(sz)) and xs.min() > fim.shape[1] * 0.7: flash_m |= (bl == i + 1) & (fa > 0)
    flash, fx0, fy0 = crop(fim, fa, flash_m)
    hands['fireHand'] = ((fx0 + flash.shape[1] / 2 - (bx0 + foot)) * csc, (fy0 + flash.shape[0] / 2 - by1) * csc)

    # 10 화염 산탄 발사: 몸 덩어리 중 손 끝 왼쪽만, 오른쪽은 burst
    sim_, sa = prep(SC_SRC)
    bl, n = ndi.label(ndi.binary_dilation(sa > 0.5, iterations=2))
    sz = ndi.sum(sa > 0.5, bl, range(1, n + 1))
    whole = (bl == 1 + int(np.argmax(sz))) & (sa > 0)
    body = whole.copy(); body[:, SC_BODY_X:] = False
    burst_m = whole.copy(); burst_m[:, :SC_HAND_X] = False
    rgba, bx0, by0 = crop(sim_, sa, body)
    k = rgba[..., 3] > 128
    foot = np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()
    pieces.append(('sc', shrink(rgba, csc), foot * csc))
    by1 = by0 + rgba.shape[0] - 2
    burst, ux0, uy0 = crop(sim_, sa, burst_m)
    bk = burst[..., 3] > 128
    burst_ay = np.where(bk[:, :4].any(axis=1))[0].mean()   # 분출 왼쪽 끝(손) 세로 가운데
    hands['scatterHand'] = ((ux0 - (bx0 + foot)) * csc, (uy0 + burst_ay - by1) * csc)
    bolt, _, _ = crop(sim_, sa, blob_of(sa, SC_BOLT_AT))
    tk = bolt[..., 3] > 128
    head = bolt[..., :3].sum(axis=2) * tk
    bolt_ay = np.average(np.arange(bolt.shape[0]), weights=head[:, -bolt.shape[1] // 4:].sum(axis=1) + 1e-6)   # 불덩이 머리(오른쪽 1/4) 밝기 가운데
    print('hands (칸 px, 발 기준):', {k_: (round(v[0], 1), round(v[1], 1)) for k_, v in hands.items()})
    FX_EXTRA.update(bolt=(bolt, bolt.shape[1] - 1, bolt_ay), burst=(burst, 0, burst_ay), flash=(flash, flash.shape[1] / 2, flash.shape[0] / 2))

    # 11·12: 그림 전체 (흩날리는 불티·불길 포함). drop = 기준점(발) 아래로 내려가는 칸 px
    drops = {}
    for name, path, foot_y, cuts, *opt in POSES:
        pk = RING_K if opt else POSE_K
        pim, pa = prep(path, SHADOW.get(name))
        if name == 'ringcast':   # 발밑 불꽃 고리만 따로 → 이펙트 ring
            r, g, b = pim[..., 0], pim[..., 1], pim[..., 2]
            fire = (r > 150) & (b < 150) & ((r > g * 1.6) | ((r > 200) & (g > 120)))
            fire[:RING_FX_TOP] = False
            x0, x1, y0, y1 = RING_FX_SKIP; fire[y0:y1, x0:x1] = False
            rm = fire & (pa > 0)
            bl, n = ndi.label(rm, structure=np.ones((3, 3)))   # 고리 안쪽에 섞인 장화·그림자 조각(작은 덩어리)은 버림
            rm &= np.isin(bl, 1 + np.where(ndi.sum(rm, bl, range(1, n + 1)) >= 30)[0])
            rys, rxs = np.where(rm)
            ring = np.dstack([pim, np.where(rm, pa, 0) * 255])[rys.min():rys.max() + 1, rxs.min():rxs.max() + 1]
            # 뒤쪽 가운데는 몸에 가려 그려져 있지 않음 → 앞쪽 가운데 띠(불꽃 혀 없이 매끈한 곳)를 위아래로 뒤집어 채움
            hh, w = ring.shape[0] // 2, ring.shape[1]
            xa, xb = int(w * 0.1), int(w * 0.9)
            flip = ring[::-1, xa:xb]
            top = ring[:hh, xa:xb]
            ring[:hh, xa:xb] = np.where(flip[:hh, :, 3:] > top[..., 3:], flip[:hh], top)
            FX_EXTRA['ring'] = (ring, ring.shape[1] / 2, ring.shape[0] / 2)
        for x0, x1, y0, y1 in cuts: pa[y0:y1, x0:x1] = 0
        ys, xs = np.where(pa > 0)
        rgba = np.dstack([pim, pa * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        k = rgba[..., 3] > 128
        bl, n = ndi.label(k)
        body = bl == 1 + int(np.argmax(ndi.sum(k, bl, range(1, n + 1))))
        fy = (foot_y - ys.min()) if foot_y is not None else body.shape[0] - 1
        foot = np.where(body[max(0, fy - 8):fy + 1].any(axis=0))[0].mean()
        p = shrink(rgba, pk)
        drops[len(pieces)] = int(round((rgba.shape[0] - 1 - fy) * pk))
        pieces.append((name, p, foot * pk))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{pk} → {p.shape[1]}x{p.shape[0]}  발 {foot:.0f} 아래로 {drops[len(pieces) - 1]}')

    L = max(int(np.ceil(c)) for _, _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 4
    D = max(drops.values() or [0])
    H = max(p.shape[0] - drops.get(i, 0) for i, (_, p, _) in enumerate(pieces)) + 5 + D
    AY = H - 2 - D   # 기준점(발) 줄
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = AY + drops.get(i, 0) - p.shape[0]
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)

    # 날아가는 불덩이 → 투사체 시트 (오른쪽으로 날아가는 그림, 기준점 = 오른쪽 끝 세로 가운데)
    m = (blobs == blobs[EMBER_AT[1], EMBER_AT[0]]) & (a > 0)
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    ember = shrink(np.dstack([im, np.where(m, a, 0) * 255])[y0:y1, x0:x1], FX_SCALE)
    # 불의 고리 이펙트 시트
    rim, ra = prep(RINGFX_SRC)
    rparts = []
    for name, x0, x1, y0, y1 in RING_FRAMES:
        m = np.zeros(ra.shape, bool); m[y0:y1, x0:x1] = ra[y0:y1, x0:x1] > 0
        ys, xs = np.where(m)
        q = np.dstack([rim, np.where(m, ra, 0) * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        k = q[..., 3] > 128
        low = k.copy(); low[:int(k.shape[0] * (1 - RING_LOW))] = False
        if not name.startswith('in'):   # 고리 두 개: 가운데쯤 가장 빈 줄에서 위·아래로 나눔
            rows = k.sum(axis=1)
            a0, a1 = int(k.shape[0] * 0.45), int(k.shape[0] * 0.8)
            cut = a0 + int(np.argmin(rows[a0:a1]))
            hi = q[:cut].copy()
            hk = hi[..., 3] > 128
            hys, hxs = np.where(hk)
            hi = hi[hys.min():hys.max() + 1, hxs.min():hxs.max() + 1]
            rparts.append((name + '_hi', shrink(hi, RINGFX_K), hi.shape[1] / 2 * RINGFX_K, hi.shape[0] / 2 * RINGFX_K, hi.shape[1] * RINGFX_K))
            q = q.copy(); q[:cut, :, 3] = 0
            k = q[..., 3] > 128
            ys2, xs2 = np.where(k)
            q = q[ys2.min():ys2.max() + 1, xs2.min():xs2.max() + 1]
            k = q[..., 3] > 128
            low = k
        lys, lxs = np.where(low)
        ax, ay = (lxs.min() + lxs.max()) / 2, (lys.min() + lys.max()) / 2
        rparts.append((name, shrink(q, RINGFX_K), ax * RINGFX_K, ay * RINGFX_K, (lxs.max() - lxs.min()) * RINGFX_K))
    W = sum(q.shape[1] for _, q, _, _, _ in rparts) + 2 * len(rparts)
    Hh = max(q.shape[0] for _, q, _, _, _ in rparts)
    atlas = np.zeros((Hh, W, 4), np.uint8)
    x, out = 0, []
    for name, q, ax, ay, lw in rparts:
        atlas[:q.shape[0], x:x + q.shape[1]] = q
        out.append(f"{name}: [[{x},0,{q.shape[1]},{q.shape[0]},{ax:.1f},{ay:.1f}]]")
        x += q.shape[1] + 2
    Image.fromarray(atlas, 'RGBA').save(RING_OUT, 'WEBP', lossless=True)
    print('PYRO_RING_FX anims: { ' + ', '.join(out) + ' }')
    print('발밑 고리 너비:', {n: round(lw, 1) for n, _, _, _, lw in rparts})

    him, ha = prep(HIT_SRC)
    ys, xs = np.where(ha > 0)
    hit = shrink(np.dstack([him, ha * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 0.5)
    FX_EXTRA['hit'] = (hit, hit.shape[1] / 2, hit.shape[0] / 2)

    # 이펙트 시트: 가로로 이어 붙임 (칸 사이 2px)
    parts = [('ember', ember, ember.shape[1] - 1, ember.shape[0] / 2)] + [(k_, *v) for k_, v in FX_EXTRA.items()]
    W = sum(q.shape[1] for _, q, _, _ in parts) + 2 * len(parts)
    Hh = max(q.shape[0] for _, q, _, _ in parts)
    atlas = np.zeros((Hh, W, 4), np.uint8)
    x, out = 0, []
    for k_, q, ax, ay in parts:
        atlas[:q.shape[0], x:x + q.shape[1]] = q
        out.append(f"{k_}: [[{x},0,{q.shape[1]},{q.shape[0]},{ax:.1f},{ay:.1f}]]")
        x += q.shape[1] + 2
    Image.fromarray(atlas, 'RGBA').save(FX_OUT, 'WEBP', lossless=True)
    print('PYRO_FX anims: { ' + ', '.join(out) + ' }')
    print(f'샘플 배율(9·10번 이펙트) = {csc:.4f}')
    print(f'pyro_0 cellW={cw} cellH={H} anchorX={L} anchorY={AY} count={len(pieces)} 대기 키={pieces[0][1].shape[0]}')


if __name__ == '__main__':
    main()

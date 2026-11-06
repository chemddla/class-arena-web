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
POSE_K = 0.66   # 11·12번 샘플 → 칸 배율
# (칸 이름, 샘플, 장화 바닥 줄 (None = 그림 바닥), 지울 상자들 (x0, x1, y0, y1))
POSES = [
    ('combust', 'assets/sprites/fx/samples/pyro_combust_src.png', None, []),
    ('raise', 'assets/sprites/fx/samples/pyro_raise_src.png', 172, [(60, 82, 157, 161)]),
]
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


def prep(path):
    # 흰 배경 지우기 → (색, 알파 0~1)
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    white = (im.min(axis=2) > 222) & (im.max(axis=2) - im.min(axis=2) < 26)
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
    for name, path, foot_y, cuts in POSES:
        pim, pa = prep(path)
        for x0, x1, y0, y1 in cuts: pa[y0:y1, x0:x1] = 0
        ys, xs = np.where(pa > 0)
        rgba = np.dstack([pim, pa * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        k = rgba[..., 3] > 128
        bl, n = ndi.label(k)
        body = bl == 1 + int(np.argmax(ndi.sum(k, bl, range(1, n + 1))))
        fy = (foot_y - ys.min()) if foot_y is not None else body.shape[0] - 1
        foot = np.where(body[max(0, fy - 8):fy + 1].any(axis=0))[0].mean()
        p = shrink(rgba, POSE_K)
        drops[len(pieces)] = int(round((rgba.shape[0] - 1 - fy) * POSE_K))
        pieces.append((name, p, foot * POSE_K))
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} ×{POSE_K} → {p.shape[1]}x{p.shape[0]}  발 {foot:.0f} 아래로 {drops[len(pieces) - 1]}')

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

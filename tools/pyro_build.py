# 화염술사 전용 샘플(붉은 포니테일·주홍 로브·손 위 불덩이, 흰 배경 한 장에 동작 8개 + 한글 이름표) → 캐릭터 시트 assets/sprites/merc/pyro_0.webp
# 사용: python tools/pyro_build.py   (샘플 assets/sprites/fx/samples/pyro_src.webp, 909×1024)
# 칸 순서: 0 대기 · 1~2 걷기 · 3 공격 준비 (손 앞에 불덩이와 불꽃 고리) · 4 공격 발사 (손을 뻗음, 날아가는 불덩이는 게임이 따로 그림)
#   · 5 피격 · 6~7 쓰러짐 (뒤로 넘어짐 → 누움) · 8 화염 시전 (두 손 사이에 불덩이를 모으고 불티가 흩날림, 파이어볼·화염 산탄)
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

    L = max(int(np.ceil(c)) for _, _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 4
    H = max(p.shape[0] for _, p, _ in pieces) + 5
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = H - 2 - p.shape[0]
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)

    # 날아가는 불덩이 → 투사체 시트 (오른쪽으로 날아가는 그림, 기준점 = 오른쪽 끝 세로 가운데)
    m = (blobs == blobs[EMBER_AT[1], EMBER_AT[0]]) & (a > 0)
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    ember = shrink(np.dstack([im, np.where(m, a, 0) * 255])[y0:y1, x0:x1], FX_SCALE)
    Image.fromarray(ember, 'RGBA').save(FX_OUT, 'WEBP', lossless=True)
    eh, ew = ember.shape[:2]
    print(f'pyro_fx ember: [0,0,{ew},{eh},{ew - 1},{eh / 2:g}]')
    print(f'pyro_0 cellW={cw} cellH={H} anchorX={L} anchorY={H - 2} count={len(pieces)} 대기 키={pieces[0][1].shape[0]}')


if __name__ == '__main__':
    main()

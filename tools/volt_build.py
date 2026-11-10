# 전격술사 전용 샘플(남색 비니·회색 단발·둥근 안경·카키 점퍼·체크 스커트·목에 건 헤드폰, 흰 배경) → 캐릭터 시트 assets/sprites/merc/volt_0.webp
# 사용: python tools/volt_build.py   (샘플 assets/sprites/fx/samples/volt_*_src.*)
# 칸 순서: 0 대기 (한 손 위에 하늘색 전기 불꽃) · 1~4 걷기 (양손을 주머니에) · 5 기본 공격 (두 손을 뻗음, 손 앞 전류 줄기는 이펙트로 따로)
#   · 6 피격 · 7~8 쓰러짐 (뒤로 넘어감 → 누움) · 9 썬더볼트·체인 라이트닝 (두 손 사이 전기 구체) · 10 일렉트릭 필드 (모은 손 위 전기 불꽃)
#   · 11~12 전자포 (당겨 모음 → 손바닥을 내밂) · 13~14 방전 (주먹 모음 → 두 팔을 활짝) · 15~16 오버로드 (무릎 꿇고 땅 짚음 → 일어나 주먹)
#   · 17 주먹 쥐고 버팀 (일렉트릭 필드 발동 · 오버로드 시전 중간)
# 크기: 샘플마다 그린 크기가 달라서, 비니(가장 큰 남색 덩어리) 넓이의 제곱근이 대기 자세와 같아지게 묶음(GROUP)마다 배율을 따로 씀
#   (비니 가로세로 비는 모든 샘플이 1.52~1.59로 같아서 가로·세로 비율은 그대로)
#   대기 자세 키(비니 꼭대기~운동화 바닥)를 TARGET_H로 맞춘 배율이 기준
# 피부: 작은 샘플(전자포·방전·오버로드·필드)은 피부가 더 어둡고 붉어서, 피부 픽셀의 밝기 순위를 대기 자세 피부 색에 그대로 옮김 (_skin_match)
# 기본 공격 전류 줄기: 손 끝(가장 오른쪽 비전기 픽셀) 오른쪽의 하늘색 픽셀 → 이펙트 시트 FX_OUT 'beam' (기준점 = 왼쪽 끝 세로 가운데)
# 모든 칸 마지막 정리(defringe): 흰 배경이 섞인 바깥 테두리 픽셀을 지움 (pyro_build와 같음)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink
from pyro_build import prep, defringe

S = 'assets/sprites/fx/samples/'
OUT = 'assets/sprites/merc/volt_0.webp'
FX_OUT = 'assets/sprites/fx/volt_fx.webp'
TARGET_H = 88   # 대기 자세 키 → 게임 칸 키 (격투가 86, 소환사 88과 비슷하게)

# (칸 이름, 샘플, 그 샘플에서 왼쪽부터 몇 번째 그림)
FRAMES = [
    ('idle', 'volt_idle_src.png', 0),
    ('walk0', 'volt_walk_src.webp', 0), ('walk1', 'volt_walk_src.webp', 1),
    ('walk2', 'volt_walk_src.webp', 2), ('walk3', 'volt_walk_src.webp', 3),
    ('atk', 'volt_atk_hurt_src.png', 0),
    ('hurt', 'volt_atk_hurt_src.png', 1),
    ('down0', 'volt_down_src.png', 0), ('down1', 'volt_down_src.png', 1),
    ('bolt', 'volt_bolt_src.png', 0),
    ('field', 'volt_field_src.png', 0),
    ('rail0', 'volt_rail_src.png', 0), ('rail1', 'volt_rail_src.png', 1),
    ('dis0', 'volt_discharge_src.png', 0), ('dis1', 'volt_discharge_src.png', 1),
    ('ovl0', 'volt_overload_src.png', 0), ('ovl1', 'volt_overload_src.png', 1),
    ('fist', 'volt_fist_src.png', 0),
]
# 같은 크기로 그려진 샘플 묶음: 묶음 안 그림들의 비니 크기 가운데값 하나로 배율을 정함
#   (그림 하나만 보면 머리 각도·가려짐 때문에 비니가 10%쯤 작게 재지는 그림이 있음 — 방전 1·오버로드 2가 그랬음)
GROUP = {'volt_walk_src.webp': 'walk', 'volt_atk_hurt_src.png': 'mid', 'volt_down_src.png': 'mid', 'volt_bolt_src.png': 'mid',
         'volt_field_src.png': 'small', 'volt_rail_src.png': 'small', 'volt_discharge_src.png': 'small', 'volt_overload_src.png': 'small'}
# 비율: 샘플마다 머리:몸 비율도 다름 (비니 너비 ÷ 선 키 = 대기 0.29, 전자포·방전 묶음 0.32, 주먹 샘플 0.34 — 뒤로 갈수록 머리가 큼)
#   비니만 맞추면 몸이 대기보다 10~17% 작아지고, 키만 맞추면 머리가 그만큼 커짐 → 두 배율의 기하평균을 씀 (머리·키 차이를 반씩 나눔)
#   키 배율 = 묶음에서 똑바로 선 그림(BODY_REF)의 키를 TARGET_H로
BODY_REF = {'walk': ('walk0', 'walk1', 'walk2', 'walk3'), 'mid': ('bolt',), 'small': ('field',), 'volt_fist_src.png': ('fist',), 'volt_idle_src.png': ('idle',)}
MIN_FIG = 1500   # 이보다 작은 덩어리 = 한글 이름표·티끌


def figures(path):
    # 샘플 한 장 → 왼쪽부터 그림 덩어리들 [(색, 알파)] (3px 넓혀 이은 덩어리, 손 위 전기 불꽃·튀는 줄기까지 한 덩어리)
    im, a = prep(S + path)
    fg = a > 0.5
    bl, n = ndi.label(ndi.binary_dilation(fg, iterations=3))
    sz = ndi.sum(fg, bl, range(1, n + 1))
    out = []
    for i in range(n):
        if sz[i] < MIN_FIG: continue
        m = (bl == i + 1) & (a > 0)
        xs = np.where(m.any(axis=0))[0]
        out.append((xs.min(), m))
    out.sort(key=lambda t: t[0])
    return im, a, [m for _, m in out]


def is_elec(c):
    # 하늘색 전기 (줄기·불꽃·구체): 초록·파랑이 둘 다 밝고 빨강보다 확실히 큼. 비니·헤드폰·운동화의 남색은 초록이 낮아서 빠짐
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    return (G > R + 25) & (B > R + 25) & (G > 140) & (np.abs(G - B) < 60)


def beanie_area(im, m):
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    blue = m & (B > R + 35) & (B >= G) & (B < 200) & (im.max(axis=2) < 190)
    lb, nb = ndi.label(blue)
    return ndi.sum(blue, lb, range(1, nb + 1)).max()


def skin_mask(c, alpha):
    # 피부: 붉은 살구색 (빨강 > 초록 > 파랑, 채도 중간). 카키 점퍼(초록이 큼)·회색 머리(채도 낮음)·비니 주황 패치(파랑이 아주 낮음)는 빠짐
    R, G, B = (c[..., i].astype(float) for i in range(3))
    mx, mn = np.maximum(np.maximum(R, G), B), np.minimum(np.minimum(R, G), B)
    sat = (mx - mn) / np.maximum(mx, 1)
    return (alpha > 200) & (R > G) & (G > B) & (R - G > 25) & (R - G < 80) & (sat > 0.2) & (sat < 0.5) & (mx > 120) & (B > 70)


def skin_palette(rgba):
    m = skin_mask(rgba[..., :3], rgba[..., 3])
    return rgba[..., :3][m].astype(float)


def skin_match(rgba, ref):
    # 피부 픽셀의 밝기 순위를 대기 자세 피부 색 분포의 같은 순위 색으로 바꿈
    rgba = rgba.copy()
    m = skin_mask(rgba[..., :3], rgba[..., 3])
    if m.sum() < 5: return rgba
    v = rgba[..., :3][m].astype(float)
    ref = ref[np.argsort(ref.mean(axis=1))]
    rank = np.argsort(np.argsort(v.mean(axis=1), kind='stable')) / max(len(v) - 1, 1)
    rgba[..., :3][m] = ref[np.round((0.02 + rank * 0.96) * (len(ref) - 1)).astype(int)].astype(np.uint8)
    return rgba


def main():
    cache, raw, fx = {}, [], {}
    for name, path, idx in FRAMES:
        if path not in cache: cache[path] = figures(path)
        im, a, figs = cache[path]
        m = figs[idx].copy()
        if name == 'atk':   # 손 앞 전류 줄기 떼기: 전기가 아닌 픽셀이 한 열에 4개 이상인 가장 오른쪽 열 = 손 끝, 그 오른쪽 전부 = 줄기
            el = is_elec(im) & m
            ne = (m & ~el & (a > 0.9)).sum(axis=0)
            body_x = np.where(ne >= 4)[0].max()
            beam = m.copy(); beam[:, :body_x + 1] = False
            m &= ~beam
            fx['beam_src'] = (im, a, beam)
        ys, xs = np.where(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.dstack([im, np.where(m, a, 0) * 255])[y0:y1, x0:x1]
        k = rgba[..., 3] > 128
        if name.startswith('down'):   # 누운 자세: 몸 가로 가운데
            cols = np.where(k.any(axis=0))[0]
            foot = (cols.min() + cols.max()) / 2
        else:
            foot = np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean()
        raw.append((name, GROUP.get(path, path), rgba, np.sqrt(beanie_area(im, m)), foot, x0, y1))

    base_b, base_sc = raw[0][3], TARGET_H / raw[0][2].shape[0]   # 대기 자세
    gmed = {}
    for _, g, _, b, *_ in raw: gmed.setdefault(g, []).append(b)
    gmed = {g: float(np.median(v)) for g, v in gmed.items()}
    href = {g: TARGET_H / np.mean([r[2].shape[0] for r in raw if r[0] in names]) for g, names in BODY_REF.items()}
    pieces = []
    for name, g, rgba, b, foot, x0, y1 in raw:
        sc = np.sqrt(base_sc * base_b / gmed[g] * href[g])
        p = shrink(rgba, sc)
        pieces.append((name, p, foot * sc))
        if name == 'atk': fx['sc'], fx['x0'], fx['y1'], fx['foot'] = sc, x0, y1, foot
        print(f'{name}: 샘플 {rgba.shape[1]}x{rgba.shape[0]} 비니 {b:.1f} (묶음 {gmed[g]:.1f}) ×{sc:.3f} → {p.shape[1]}x{p.shape[0]}')

    ref = skin_palette(pieces[0][1])
    print('대기 피부 평균', ref.mean(axis=0).round(), len(ref))
    pieces = [(n, p if i == 0 else skin_match(p, ref), c) for i, (n, p, c) in enumerate(pieces)]
    for n, p, _ in pieces:
        sp = skin_palette(p)
        print(f'  {n} 피부 {len(sp)}px 평균 {sp.mean(axis=0).round() if len(sp) else "-"}')

    L = max(int(np.ceil(c)) for _, _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for _, p, c in pieces) + 4
    H = max(p.shape[0] for _, p, _ in pieces) + 5
    AY = H - 2
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (name, p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c))
        y = AY - p.shape[0]
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = defringe(p)
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)

    # 기본 공격 전류 줄기 → 이펙트 시트 (오른쪽으로 뻗는 그림, 기준점 = 왼쪽 끝(손) 세로 가운데). 배율은 공격 칸과 같음
    im, a, beam = fx['beam_src']
    ys, xs = np.where(beam)
    q = np.dstack([im, np.where(beam, a, 0) * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    atk_sc = fx['sc']
    q = defringe(shrink(q, atk_sc))
    qk = q[..., 3] > 0
    ay = np.where(qk[:, :3].any(axis=1))[0].mean()
    Image.fromarray(q, 'RGBA').save(FX_OUT, 'WEBP', lossless=True)
    # 손 자리 (칸 px, 발 기준): 줄기 왼쪽 끝
    hand = ((xs.min() - (fx['x0'] + fx['foot'])) * atk_sc, (ys.min() + ay / atk_sc - (fx['y1'] - 1)) * atk_sc)
    print(f"VOLT_FX beam: [[0,0,{q.shape[1]},{q.shape[0]},0,{ay:.1f}]]  배율 {atk_sc:.4f}  beamHand [{hand[0]:.1f}, {hand[1]:.1f}]")
    print(f'volt_0 cellW={cw} cellH={H} anchorX={L} anchorY={AY} count={len(pieces)} 대기 키={pieces[0][1].shape[0]}')


if __name__ == '__main__':
    main()

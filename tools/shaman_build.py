# 무녀 외형 0 (2026-11-17 사용자 샘플: 흰 저고리·붉은 하카마·붉은 리본, 긴 검은 머리) → assets/sprites/merc/shaman_0.webp
# 사용: python tools/shaman_build.py
#   칸 그림은 tools/miko_sample_build.py의 build()가 다듬은 것을 그대로 씀 (흰 배경·찌꺼기 지움 · 얼굴 크기·피부색·하카마 빨강을 대기 칸에 맞춤)
#   여기서는 발 위치를 기준으로 한 줄 시트로 조립만 함
# 칸 (14칸): 0 대기 · 1~3 걷기 · 4 부적 치켜듦 (일반 공격 준비) · 5 부적 던지기 · 6 피격 · 7~8 쓰러짐 (무릎 → 누움)
#   · 9 부적 소환 캐스팅 (한 손을 머리 위로) · 10 부적 소환 시전 (손을 앞으로 뻗음)
#   · 11 내림굿 캐스팅 (손 모아 기도) · 12 내림굿 시전 (두 팔 벌리고 떠오름, 10px 떠 있음) · 13 내림굿 착지
#   날아가는 부적·머리 위 부적·바닥 부적은 그림에서 뺐음 (게임에서 이펙트로 그림)
import os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from miko_sample_build import build

OUT = 'assets/sprites/merc/shaman_0.webp'
ORDER = [('대기', [0]), ('걷기', [0, 1, 2]), ('일반 공격', [0, 1]), ('피격', [0]), ('쓰러짐', [0, 1]),
         ('부적 소환', [0, 1]), ('히든', [0, 1, 2])]
LIFT = {12: 10}   # 칸 번호 → 바닥에서 띄울 높이 (게임 px). 내림굿 시전은 공중에 뜬 그림
LYING = {8}       # 누운 칸: 발 대신 몸 가운데를 기준점에
THROW = 5         # 부적이 나가는 칸 (muzzle 재는 칸)


def foot_x(p, i):
    k = p[..., 3] > 127
    if i in LYING:
        cols = np.where(k.any(axis=0))[0]
        return (cols.min() + cols.max()) / 2
    return float(np.where(k[int(k.shape[0] * 0.92):].any(axis=0))[0].mean())


def main():
    rows = dict(build())
    pieces = []
    for label, idx in ORDER:
        for j in idx:
            p = rows[label][j][0]
            pieces.append((p, foot_x(p, len(pieces))))
    L = max(int(np.ceil(c)) for _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for p, c in pieces) + 4
    H = max(p.shape[0] + LIFT.get(i, 0) for i, (p, _) in enumerate(pieces)) + 5
    AY = H - 2
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c)); y = AY - p.shape[0] - LIFT.get(i, 0)
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    # 던지는 손끝: 던지기 칸의 가장 앞(오른쪽) 불투명 픽셀들 → 기준점에서 앞·위 (그림 px)
    p, c = pieces[THROW]
    k = p[..., 3] > 127
    xs = np.where(k.any(axis=0))[0]; tip = xs.max()
    ty = np.where(k[:, tip - 3:tip + 1].any(axis=1))[0].mean()
    fwd = tip - c; up = p.shape[0] - ty
    print(f'shaman_0 cellW={cw} cellH={H} anchorX={L} anchorY={AY} count={len(pieces)} 대기 키={pieces[0][0].shape[0]}'
          f' 손끝 앞 {fwd:.0f} 위 {up:.0f}')


if __name__ == '__main__':
    main()

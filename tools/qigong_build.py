# 기공사 외형 0 (2026-11-16 사용자 샘플: 금빛·흰 도포, 긴 검은 머리) → assets/sprites/merc/qigong_0.webp
# 사용: python tools/qigong_build.py
#   칸 그림은 tools/qigong_sample_build.py의 build()가 다듬은 것을 그대로 씀 (흰 배경 지움 · 얼굴 크기와 몸 길이·피부색을 대기 칸에 맞춤)
#   여기서는 발 위치를 기준으로 한 줄 시트로 조립만 함
# 칸 (22칸): 0 대기 · 1~4 걷기 · 5 기 모으기 (일반 공격 준비) · 6 내지르기 · 7 피격 · 8~9 쓰러짐 (무릎 → 누움)
#   · 10 기공포 모으기 (가슴 앞 두 손) · 11 기공포 쏘기 · 12 기공탄 준비 · 13 기공탄 던지기 · 14 기공후 모으기 · 15 기공후 터뜨리기 (두 팔 펴기)
#   · 16 기공파 모으기 · 17 기공파 쏘기 · 18 기공옥 지상 모으기 · 19 기공옥 최대 크기 (공중) · 20 기공옥 시전 · 21 기공옥 착지
#   기공막은 10 → 15를 다시 씀 (샘플 미리보기의 '기공막' 줄은 시트에 넣지 않음)
import os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from qigong_sample_build import build

OUT = 'assets/sprites/merc/qigong_0.webp'
# 미리보기 줄 이름 → 시트에 넣을 칸 (줄 안 번호)
ORDER = [('대기', [0]), ('걷기', [0, 1, 2, 3]), ('일반 공격', [0, 1]), ('피격', [0]), ('쓰러짐', [0, 1]),
         ('기공포', [0, 1]), ('기공탄', [0, 1]), ('기공후', [0, 1]), ('기공파', [0, 1]), ('기공옥', [0, 1, 2, 3])]
LIFT = {19: 8}   # 칸 번호 → 바닥에서 띄울 높이 (게임 px). 기공옥 최대 크기 자세는 공중에 뜬 그림
LYING = {9}      # 누운 칸: 발 대신 몸 가운데를 기준점에


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
    print(f'qigong_0 cellW={cw} cellH={H} anchorX={L} anchorY={AY} count={len(pieces)} 대기 키={pieces[0][0].shape[0]}')


if __name__ == '__main__':
    main()

# 무녀 시크릿 레어 1 (2026-11-17 사용자 샘플: 남색 철릭·붉은 치마·오색 띠·땋은 머리·부채) → assets/sprites/merc/shaman_sr1.webp
#   + 일반 공격 부적 투사체 그림 assets/sprites/fx/shaman_sr1_charm.webp
# 사용: python tools/shaman_sr1_build.py
#   칸 그림은 tools/miko_sr1_sample_build.py의 build()가 다듬은 것을 그대로 씀 (흰 배경 지움 · 크기·피부·남색·빨강을 대기 칸에 맞춤)
#   여기서는 기준점에 맞춰 한 줄 시트로 조립만 함
# 칸 (17칸): 0 대기 · 1~4 걷기 · 5 부적 들기 (일반 공격 준비) · 6 팔 뻗기 (던짐) · 7 피격 · 8~9 쓰러짐 (넘어짐 → 누움)
#   · 10 부적 소환 캐스팅 (두 손 들기) · 11 부적 소환 시전 (두 팔 펴기)
#   · 12 내림굿 준비 (부채·방울을 모아 듦) · 13~15 시전 막대 동안 굿 동작 · 16 내림굿 시전 (눈 감고 부채·방울을 모음)
#   떠 있는 부적 고리는 그림에서 뺐음 (게임에서 이펙트로 그림)
import os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from miko_sr1_sample_build import build
from miko_sample_build import skin_mask

OUT = 'assets/sprites/merc/shaman_sr1.webp'
CHARM_OUT = 'assets/sprites/fx/shaman_sr1_charm.webp'
# 부적 그림은 원본 크기 그대로 (줄이면 붉은 글씨가 뭉개짐). 화면에서는 drawMuProjectile이 기본 부적 크기에 맞춰 줄여 그림
ORDER = [('걷기', [0, 1, 2, 3]), ('일반 공격', [0, 1]), ('피격', [0]), ('쓰러짐', [0, 1]),
         ('부적 소환', [0, 1]), ('내림굿', [0, 1, 2, 3, 4])]
LYING = {9}   # 누운 칸: 몸 가운데를 기준점에
THROW = 6     # 부적이 나가는 칸 (muzzle 재는 칸)


def body_x(p, i):   # 기준점 x: 치마 가운데 (아래 60~90% 줄의 불투명 픽셀 평균). 발로 재면 걸을 때 보폭 따라 몸이 좌우로 흔들림
    k = p[..., 3] > 127
    if i in LYING:
        cols = np.where(k.any(axis=0))[0]
        return (cols.min() + cols.max()) / 2
    h = k.shape[0]
    return float(np.where(k[int(h * .6):int(h * .9)])[1].mean())


def main():
    _, idle, rows, (_, charm_big) = build()
    rows = dict(rows)
    pieces = [(idle, body_x(idle, 0))]
    for label, idx in ORDER:
        for j in idx:
            p = rows[label][j]
            pieces.append((p, body_x(p, len(pieces))))
    L = max(int(np.ceil(c)) for _, c in pieces) + 4
    R = max(int(np.ceil(p.shape[1] - c)) for p, c in pieces) + 4
    H = max(p.shape[0] for p, _ in pieces) + 5
    AY = H - 2
    cw = L + R
    sheet = np.zeros((H, cw * len(pieces), 4), np.uint8)
    for i, (p, c) in enumerate(pieces):
        x = i * cw + L - int(round(c)); y = AY - p.shape[0]
        sheet[y:y + p.shape[0], x:x + p.shape[1]] = p
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    # 던지는 손끝: 던지기 칸의 가장 앞(오른쪽) 불투명 픽셀들 → 기준점에서 앞·위 (그림 px)
    p, c = pieces[THROW]
    k = p[..., 3] > 127
    xs = np.where(k.any(axis=0))[0]; tip = xs.max()
    ty = np.where(k[:, tip - 3:tip + 1].any(axis=1))[0].mean()
    fwd = tip - c; up = p.shape[0] - ty
    # 초상화 가운데: 대기 칸 얼굴(위쪽 25% 줄의 살색 가운데)
    ip, ic = pieces[0]
    sk = skin_mask(ip); sk[int(ip.shape[0] * .25):] = False   # 부채 노랑이 섞이지 않게 살색 판별은 다듬기 도구와 같은 것
    pcx = L - int(round(ic)) + np.where(sk)[1].mean()
    print(f'portraitCX {pcx:.0f}')
    print(f'shaman_sr1 cellW={cw} cellH={H} anchorX={L} anchorY={AY} count={len(pieces)} 대기 키={ip.shape[0]}'
          f' 손끝 앞 {fwd:.0f} 위 {up:.0f} → muzzle [{fwd:.0f}, {up - 19:.0f}]'
          f' · 칸별 키 {[q.shape[0] for q, _ in pieces]}')
    # 부적 투사체: 일반 공격 2번 샘플에서 떼어 낸 날아가는 부적 (오른쪽을 향함)
    ch = charm_big
    Image.fromarray(ch, 'RGBA').save(CHARM_OUT, 'WEBP', lossless=True)
    print(f'charm {ch.shape[1]}x{ch.shape[0]} → {CHARM_OUT}')


if __name__ == '__main__':
    main()

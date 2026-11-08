# 백호(격투가 SR 1) 전용 타격 이펙트 4종 (검은 배경 흰 소용돌이 고리 샘플, 1024×1024)
#   → assets/sprites/fx/brawler_sr1_hit_<종류>.webp (밝기 = 불투명도, 색은 흰색) · 게임에서 그림 가운데 = 맞은 자리
#   basic   = 고리 + 불티 (연격 1~8타)
#   skill   = 안쪽 고리가 하나 더 (연격 9·10타, 붕권·섬각·반격 같은 스킬 타격)
#   barrage = 바깥으로 줄기가 길게 튐 (멸식 - 격 난타)
#   big     = 굵은 붓질이 사방으로 터짐 (멸식 막타·마지막 일격)
# 사용: python tools/brawler_sr1_hit_build.py
import numpy as np
from PIL import Image

D = 'assets/sprites/fx/samples/brawler_sr1_hit_'
SRC = {'basic': 'basic_src.png', 'skill': 'skill_src.png', 'barrage': 'barrage_src.webp', 'big': 'big_src.webp'}
BG, FULL = 18, 170   # 170 이상 밝은 곳은 완전 불투명 (2026-11-08 '투명도 낮춰' → 235에서 낮춤)
GAMMA = 0.7          # 1보다 작을수록 흐린 빛 부분도 진하게
OUT_W = 256


def build(kind, src):
    im = np.array(Image.open(D + src).convert('RGB')).astype(float)
    a = np.clip((im.max(axis=2) - BG) / (FULL - BG), 0, 1) ** GAMMA
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    a *= np.clip(np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]) / 40, 0, 1)   # 가장자리 잘린 티 없게
    rgb = np.clip(im / np.maximum(a[..., None], 1e-3), 0, 255)   # 검은 배경과 섞였던 만큼 밝기를 되돌림
    rgb = np.where(a[..., None] > 0.02, rgb, 255)
    out = Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), 'RGBA').resize((OUT_W, OUT_W), Image.LANCZOS)
    out.save(f'assets/sprites/fx/brawler_sr1_hit_{kind}.webp', 'WEBP', quality=90)
    print(kind, out.size)


if __name__ == '__main__':
    for k, s in SRC.items(): build(k, s)

# 소환사 시크릿 레어 전용 정령왕 (별빛 왕관·성운 머리 기사) → assets/sprites/monster/spirit_king_sr1.webp
#                                                    + 강림 빛기둥 assets/sprites/fx/spirit_king_sr1_burst.webp
#                                                    + 전용 마법진 assets/sprites/fx/spirit_king_sr1_circle.webp
# 사용: python tools/spirit_king_sr1_build.py   (샘플은 assets/sprites/fx/samples/spirit_king_sr1_*_src.png)
# 샘플은 미리 정리해 둔 것: 흰 배경을 흰색 비율만큼 투명하게 (테두리 흰 띠 없앰), 모든 칸 232x182 · 기준점(발) = (125, 178)
#   크기는 대기에 맞춤 (걷기 = 왕관~발 높이, 공격·강림·피격·쓰러짐 = 눈 사이 거리), 좌우는 얼굴 가운데
#   일반공격 2는 양옆 잘린 검기 조각 지움 · 쓰러짐 3은 원소로 흩어지는 정령 (눈은 남김)
# 칸 순서: 0 대기 · 1~4 걷기 · 5 공격 1 · 6 공격 2 (초승달 검기) · 7 강림 · 8 피격 · 9~11 쓰러짐
# 강림 빛기둥: 칸과 같은 px 단위 (게임에서 정령왕과 같은 배율로 그림). 바닥 기준점 (145, 397) = 정령왕 발, 몸통이 기둥 가운데
# 마법진: 위에서 본 바닥 타원 (원래 그림을 세로 58%로 눌러 게임 바닥 비율). 원 가운데 = (폭 51%, 높이 56%), 원 폭 = 그림 폭의 98%
import numpy as np
from PIL import Image

D = 'assets/sprites/fx/samples/spirit_king_sr1_'
OUT = 'assets/sprites/monster/spirit_king_sr1.webp'
OUT_BURST = 'assets/sprites/fx/spirit_king_sr1_burst.webp'
OUT_CIRCLE = 'assets/sprites/fx/spirit_king_sr1_circle.webp'
FRAMES = ['idle', 'walk_1', 'walk_2', 'walk_3', 'walk_4', 'attack_1', 'attack_2', 'descend', 'hit', 'death_1', 'death_2', 'death_3']
CIRCLE_W = 480  # 게임에서 그리는 폭쯤으로 줄여 둠


def main():
    cells = [np.array(Image.open(f'{D}{n}_src.png').convert('RGBA')) for n in FRAMES]
    h, w = cells[0].shape[:2]
    sheet = np.zeros((h, w * len(cells), 4), np.uint8)
    for i, c in enumerate(cells):
        sheet[:, i * w:(i + 1) * w] = c
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'spirit_king_sr1 cellW={w} cellH={h} count={len(cells)}')

    b = Image.open(f'{D}descend_fx_src.png').convert('RGBA')
    b.save(OUT_BURST, 'WEBP', lossless=True)
    print(f'burst {b.size}')

    c = Image.open(f'{D}circle_ground_src.png').convert('RGBA')
    c = c.resize((CIRCLE_W, round(c.height * CIRCLE_W / c.width)), Image.LANCZOS)
    c.save(OUT_CIRCLE, 'WEBP', lossless=True)
    print(f'circle {c.size}')


if __name__ == '__main__':
    main()

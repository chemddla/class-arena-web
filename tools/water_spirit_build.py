# 소환사 물 정령 샘플(물방울 아이, 흰 배경) → 몬스터 시트 assets/sprites/monster/water_spirit.webp
# 사용: python tools/water_spirit_build.py   (샘플은 assets/sprites/fx/samples/water_spirit_*_src.png, 정리 방식은 tools/wind_spirit_build.py)
# 칸 순서: 0 대기 · 1~3 걷기 · 4 치유 (두 손으로 물방울을 내밂, 연두빛 후광·하트) · 5 피격
#   · 6~8 사라짐 (녹아내림 → 물웅덩이에 주저앉음 → 웅덩이와 거품만, spirit_pop 이펙트가 그림)
# 샘플 정리:
#   - move·down 샘플은 칸마다 위에 이름 글자가 있어서 (x0, x1, y0, y1) 상자로 글자 줄을 빼고 자름
#   - 치유 칸의 연두빛 후광은 흰 배경 위에 옅게 그려져 있어서 반투명 빛으로 남김 ('glow')
#   - 마지막 칸의 속이 빈 거품은 흰 속까지 지움 ('allwhite')
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import wind_spirit_build as W

W.SPIRITS['water'] = (0.62, [
    ('move', 'idle', (40, 180, 32, 187), [], 1),
    ('move', 'walk0', (40, 180, 226, 387), [], 1), ('move', 'walk1', (215, 355, 226, 387), [], 1), ('move', 'walk2', (390, 528, 226, 387), [], 1),
    ('heal', 'heal', (0, 171, 0, 170), [], 1, 'glow'),
    ('down', 'hurt', (30, 205, 32, 200), [], 1),
    ('down', 'down0', (50, 250, 242, 414), [], 1), ('down', 'down1', (265, 490, 242, 414), [], 1), ('down', 'down2', (505, 700, 242, 414), [], 1, 'allwhite'),
])

if __name__ == '__main__':
    W.build('water')

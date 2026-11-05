# 소환사 시크릿 레어 전용 정령왕 (별빛 왕관·성운 머리 기사) → assets/sprites/monster/spirit_king_sr1.webp
#                                                    + 강림 빛기둥 assets/sprites/fx/spirit_king_sr1_burst.webp
#                                                    + 전용 마법진 assets/sprites/fx/spirit_king_sr1_circle.webp
# 사용: python tools/spirit_king_sr1_build.py   (샘플은 assets/sprites/fx/samples/spirit_king_sr1_*_src.png)
# 샘플은 미리 정리해 둔 것: 흰 배경을 흰색 비율만큼 투명하게 (테두리 흰 띠 없앰), 모든 칸 232x182 · 기준점(발) = (125, 178)
#   크기는 대기에 맞춤 (걷기 = 왕관~발 높이, 공격·강림·피격·쓰러짐 = 눈 사이 거리), 좌우는 얼굴 가운데
#   일반공격 2는 양옆 잘린 검기 조각 지움 · 쓰러짐 3은 원소로 흩어지는 정령 (눈은 남김)
# 칸 순서: 0 대기 · 1~4 걷기 · 5 공격 1 · 6 공격 2 (초승달 검기) · 7 강림 · 8 피격 · 9~11 쓰러짐
#          12 공격 B (몸을 돌려 휘감는 별빛 베기) · 13 공격 C (성운 검기 찌르기)
#   공격 B·C 샘플(*_raw.png)은 흰 배경 그대로라 여기서 정리: 가장자리와 이어진 흰 배경을 지우고 둘레 3px만 흰색 비율만큼 투명하게,
#   눈 사이 거리를 대기(22.5px)에 맞춰 줄이고, 눈 가운데를 x 125.5에, 발끝을 y 177에 (다른 칸과 같은 바닥)
#   휘감는 검기는 왼쪽으로, 찌르기 검기는 오른쪽으로 칸 밖까지 뻗어서 모든 칸 양옆을 PAD_L·PAD_R만큼 넓힘 (기준점 x = 125 + PAD_L)
# 강림 빛기둥: 칸과 같은 px 단위 (게임에서 정령왕과 같은 배율로 그림). 바닥 기준점 (145, 397) = 정령왕 발, 몸통이 기둥 가운데
# 마법진: 위에서 본 바닥 타원 (원래 그림을 세로 58%로 눌러 게임 바닥 비율). 원 가운데 = (폭 51%, 높이 56%), 원 폭 = 그림 폭의 98%
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

D = 'assets/sprites/fx/samples/spirit_king_sr1_'
OUT = 'assets/sprites/monster/spirit_king_sr1.webp'
OUT_BURST = 'assets/sprites/fx/spirit_king_sr1_burst.webp'
OUT_CIRCLE = 'assets/sprites/fx/spirit_king_sr1_circle.webp'
FRAMES = ['idle', 'walk_1', 'walk_2', 'walk_3', 'walk_4', 'attack_1', 'attack_2', 'descend', 'hit', 'death_1', 'death_2', 'death_3']
CIRCLE_W = 480  # 게임에서 그리는 폭쯤으로 줄여 둠
PAD_L, PAD_R = 50, 72
# (샘플, 배율, 원본에서 눈 가운데 x, 원본에서 발끝 y, 갇힌 흰 배경 (x, y))
#   갇힌 흰 배경 = 망토·검·검기 사이에 둘러싸여 가장자리와 안 이어진 배경 조각. 그 조각 안의 한 점을 적어 두면 같이 지움
#   (갑옷·검·검기의 흰 하이라이트도 같은 흰색이라 자동으로는 못 가름)
EXTRA = [('attack_3', 22.5 / 26.3, 211.3, 221, [(132, 131), (100, 150), (86, 170), (118, 176)]),
         ('attack_4', 1.0, 123.5, 167, [])]


def clean_raw(path, seeds=()):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    mn = im.min(2)
    white = (mn > 225) & (im.max(2) - mn < 25)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, np.concatenate([edge[edge > 0], [lab[y, x] for x, y in seeds if lab[y, x]]]))
    rim = ~bg & ndi.binary_dilation(bg, iterations=3)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - mn) / 120, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    return np.dstack([im, a * 255]).astype(np.uint8)


def place(rgba, k, ex, fy, w, h):
    im = Image.fromarray(rgba, 'RGBA')  # 부드러운 그림이라 가장자리를 딱딱하게 하지 않고 그대로 줄임 (Pillow가 알파를 곱해서 줄임)
    p = np.array(im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)) if k != 1 else rgba
    dx, dy = int(round(125.5 - ex * k)) + PAD_L, int(round(177 - fy * k))
    cell = np.zeros((h, w, 4), np.uint8)
    y0, x0 = max(0, -dy), max(0, -dx)
    y1, x1 = min(p.shape[0], h - dy), min(p.shape[1], w - dx)
    cell[y0 + dy:y1 + dy, x0 + dx:x1 + dx] = p[y0:y1, x0:x1]
    return cell


def main():
    cells = [np.pad(np.array(Image.open(f'{D}{n}_src.png').convert('RGBA')), ((0, 0), (PAD_L, PAD_R), (0, 0))) for n in FRAMES]
    h, w = cells[0].shape[:2]
    cells += [place(clean_raw(f'{D}{n}_raw.png', seeds), k, ex, fy, w, h) for n, k, ex, fy, seeds in EXTRA]
    sheet = np.zeros((h, w * len(cells), 4), np.uint8)
    for i, c in enumerate(cells):
        sheet[:, i * w:(i + 1) * w] = c
    Image.fromarray(sheet, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print(f'spirit_king_sr1 cellW={w} cellH={h} anchorX={125 + PAD_L} count={len(cells)}')

    b = Image.open(f'{D}descend_fx_src.png').convert('RGBA')
    b.save(OUT_BURST, 'WEBP', lossless=True)
    print(f'burst {b.size}')

    c = Image.open(f'{D}circle_ground_src.png').convert('RGBA')
    c = c.resize((CIRCLE_W, round(c.height * CIRCLE_W / c.width)), Image.LANCZOS)
    c.save(OUT_CIRCLE, 'WEBP', lossless=True)
    print(f'circle {c.size}')


if __name__ == '__main__':
    main()

# 고블린 맵 9장: ✦ 워터마크(오른쪽 아래, 흰색 k배 덮어씀)를 되돌리고 숲에 어울리는 4장은 assets/maps, 나머지(광산·절벽·해안·용암·설원)는 assets/maps/samples
# 사용: python tools/goblin-maps/build.py <원본 폴더(1.webp~9.webp)>
import sys, numpy as np, cv2
from PIL import Image
src = sys.argv[1]
CX, CY, R, K = 934.4, 483.4, 17.7, 0.31
def cover(h, w):
    ys, xs = np.mgrid[0:h, 0:w]
    c = np.zeros((h, w))
    for sy in range(4):
        for sx in range(4):
            dx = np.abs(xs + (sx + .5) / 4 - .5 - CX); dy = np.abs(ys + (sy + .5) / 4 - .5 - CY)
            c += (dx ** .8 + dy ** .8 <= R ** .8)
    return c / 16
OUT = {1: 'goblin_camp', 2: 'goblin_cave', 3: 'goblin_marsh', 4: 'goblin_stockade'}
for n in range(1, 10):
    a = np.asarray(Image.open(f'{src}/{n}.webp').convert('RGB')).astype(float)
    h, w, _ = a.shape
    cv = cover(h, w)[..., None] * K
    a = np.clip((a - cv * 255) / (1 - cv), 0, 255).astype(np.uint8)
    # 가장자리 남은 얇은 선: 덮인 곳의 테두리만 주변 색으로 메움
    c = cover(h, w)
    edge = ((c > 0.02) & (c < 0.98)).astype(np.uint8) * 255
    edge = cv2.dilate(edge, np.ones((2, 2), np.uint8))
    a = cv2.inpaint(a, edge, 2, cv2.INPAINT_TELEA)
    Image.fromarray(a).save(f'assets/maps/{OUT[n]}.webp' if n in OUT else f'assets/maps/samples/goblin_{n}.webp', quality=88, method=6)
    print(n, 'ok')

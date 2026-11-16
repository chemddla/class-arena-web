# 종족 맵: AI 그림 오른쪽 아래 ✦ 워터마크(흰색을 k배 덮어씀)를 되돌려 webp로 저장
# 사용: python tools/race-maps/build.py <원본 폴더> <번호>=<저장 경로>[@cx,cy,r] ...
# 고블린(2026-11-16): 1=assets/maps/goblin_camp.webp 2=..goblin_cave 3=..goblin_marsh 4=..goblin_stockade, 5~9 → assets/maps/samples/goblin_5~9.webp
# 야수족(2026-11-16): 10=beast_den@930,541,19.5 11=beast_canyon 12=beast_dry 14=beast_red 15=beast_river 16=beast_autumn 17=beast_glow 18=beast_lava, 13 → samples/beast_snow
import sys, numpy as np, cv2
from PIL import Image
K = 0.31
def cover(h, w, CX, CY, R):
    ys, xs = np.mgrid[0:h, 0:w]
    c = np.zeros((h, w))
    for sy in range(4):
        for sx in range(4):
            dx = np.abs(xs + (sx + .5) / 4 - .5 - CX); dy = np.abs(ys + (sy + .5) / 4 - .5 - CY)
            c += (dx ** .8 + dy ** .8 <= R ** .8)
    return c / 16
src = sys.argv[1]
for arg in sys.argv[2:]:
    n, rest = arg.split('=', 1)
    out, _, pos = rest.partition('@')
    CX, CY, R = map(float, pos.split(',')) if pos else (934.4, 483.4, 17.7)  # 1024×572 그림의 기본 자리
    a = np.asarray(Image.open(f'{src}/{n}.webp').convert('RGB')).astype(float)
    h, w, _ = a.shape
    c = cover(h, w, CX, CY, R)
    cv = c[..., None] * K
    a = np.clip((a - cv * 255) / (1 - cv), 0, 255).astype(np.uint8)
    edge = cv2.dilate(((c > 0.02) & (c < 0.98)).astype(np.uint8) * 255, np.ones((2, 2), np.uint8))  # 테두리에 남는 얇은 선만 주변 색으로 메움
    a = cv2.inpaint(a, edge, 2, cv2.INPAINT_TELEA)
    Image.fromarray(a).save(out, quality=88, method=6)
    print(n, '->', out)

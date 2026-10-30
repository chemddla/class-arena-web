# 주술사 히든 [파멸의 의식] 표식·폭발 샘플(초록 배경) 4장 → assets/sprites/fx/curse_ruin_mark_fx.webp
# 사용: python tools/curse_ruin_mark_build.py [샘플 폴더]  (기본 assets/sprites/fx/samples)
#   mark0·mark1 = curse_ruin_mark0/1_src.png  걸린 적 머리 위에 떠 있는 불타는 해골 (두 칸 번갈아, 기준점 = 그림 가운데)
#   vortex      = curse_ruin_vortex_src.png   터지기 직전 발밑 붉은 소용돌이 (기준점 = 소용돌이 가운데)
#   bolt        = curse_ruin_bolt_src.png     터질 때 내리꽂는 붉은 번개 (기준점 = 바닥 소용돌이 가운데)
#   circle0     = curse_ruin_circle0_src.png  시전 중 적 발밑에 깔리는 붉은 마법진 (기준점 = 마법진 가운데)
#   circle1     = curse_ruin_circle1_src.png  발동할 때 검은 불길이 솟는 마법진 (기준점 = 마법진 가운데)
#   마법진 샘플 모서리에 잘려 들어온 다른 그림 조각은 지움
# 번개 샘플: 좌우 끝에 잘려 들어온 연기 조각은 지우고, 위쪽에서 잘린 번개는 위로 갈수록 흐리게
# 프레임 [x, y, w, h, 기준점x, 기준점y]
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = 'assets/sprites/fx/curse_ruin_mark_fx.webp'
# (이름, 파일, 기준점(샘플 좌표, None = 가운데), 지울 왼쪽·오른쪽 x, 위 흐리기 px[, 지울 상자 (x0, y0, x1, y1) 목록])
SRC = [
    ('mark0', 'curse_ruin_mark0_src.png', None, None, 0),
    ('mark1', 'curse_ruin_mark1_src.png', None, None, 0),
    ('vortex', 'curse_ruin_vortex_src.png', (150, 117), None, 0),
    ('bolt', 'curse_ruin_bolt_src.png', (125, 210), (12, 238), 40),
    ('circle0', 'curse_ruin_circle0_src.png', (150, 135), None, 0, [(250, 0, 297, 30), (0, 180, 14, 204)]),
    ('circle1', 'curse_ruin_circle1_src.png', (100, 137), (0, 199), 0),
]


def cut(path, anchor, xclip, top_fade, erase=()):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    bright = (g > 140) & (g - np.maximum(r, b) > 50)
    key = np.median(im[bright], axis=0)
    d = np.sqrt(((im - key) ** 2).sum(axis=2))
    # 그림엔 초록이 없으니 초록 기운이 도는 픽셀은 모두 배경과 섞인 반투명 (번개 빛무리·해골 연기)
    greenish = g > np.maximum(r, b) - 12  # 붉은 빛무리가 초록과 섞인 올리브색까지
    a = np.where(greenish, np.clip((d - 40) / 150, 0, 1), 1.0)
    if 'circle' in path or 'bolt' in path or 'vortex' in path:
        # 붉은 그림: 원래 초록은 빨강의 1/4 이하라고 보고, 그보다 많은 초록만큼 배경과 섞인 반투명 (붉은 빛무리가 갈색으로 남지 않게)
        a = np.minimum(a, np.clip(1 - (g - 0.25 * r) / (key[1] - 0.25 * key[0]), 0, 1))
    if xclip: a[:, :xclip[0]] = 0; a[:, xclip[1]:] = 0
    if top_fade: a[:top_fade] *= np.linspace(0, 1, top_fade)[:, None]
    for x0, y0, x1, y1 in erase: a[y0:y1, x0:x1] = 0
    m = a > 0.05
    lab, n = ndi.label(m)
    areas = ndi.sum(m, lab, range(1, n + 1))
    a = np.where(np.isin(lab, 1 + np.where(areas >= 10)[0]), a, 0)  # 압축 티끌
    al = np.maximum(a, 1e-3)[..., None]
    rgb = np.where(a[..., None] < 1, key + (im - key) / al, im).clip(0, 255)
    rgb[..., 1] = np.minimum(rgb[..., 1], np.maximum(rgb[..., 0], rgb[..., 2]))  # 붉은·보라·검정뿐이라 초록 번짐은 모두 지움
    ys, xs = np.where(a > 0.05)
    t = np.dstack([rgb, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8)
    ax, ay = anchor if anchor else ((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2)
    return t, round(ax - xs.min()), round(ay - ys.min())


def main(folder):
    tiles = [(e[0],) + cut(f'{folder}/{e[1]}', *e[2:]) for e in SRC]
    W = sum(t.shape[1] + 2 for _, t, _, _ in tiles); H = max(t.shape[0] for _, t, _, _ in tiles)
    atlas = np.zeros((H, W, 4), np.uint8); x = 0; frames = []
    for nm, t, ax, ay in tiles:
        atlas[:t.shape[0], x:x + t.shape[1]] = t
        frames.append(f'{nm}: [{x},0,{t.shape[1]},{t.shape[0]},{ax},{ay}]')
        x += t.shape[1] + 2
    Image.fromarray(atlas, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('{ ' + ', '.join(frames) + ' }')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/fx/samples')

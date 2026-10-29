# 배리어 구체 두 장(frost_fx.webp 맨 앞 [0,0,70,60]·[72,0,82,60])에 구워져 있던 작은 눈꽃 점을 지우고 구체만 남김
# (눈꽃은 게임에서 눈꽃 모음 그림으로 따로 그림). 사용: python tools/frost_bubble_clean.py
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

PATH = 'assets/sprites/fx/frost_fx.webp'
im = Image.open(PATH).convert('RGBA')
a = np.array(im)
for x0, w in ((0, 70), (72, 82)):
    sub = a[:60, x0:x0 + w]
    lab, n = ndi.label(sub[..., 3] > 40)  # 옅은 알파 점도 떨어진 조각으로 취급
    if n > 1:
        keep = 1 + int(np.argmax(ndi.sum(sub[..., 3] > 10, lab, range(1, n + 1))))
        mask = ndi.binary_dilation(lab == keep, iterations=2)  # 구체 가장자리 번짐은 남김
        sub[~mask] = 0
    a[:60, x0:x0 + w] = sub
Image.fromarray(a, 'RGBA').save(PATH, 'WEBP', lossless=True)
print('ok')

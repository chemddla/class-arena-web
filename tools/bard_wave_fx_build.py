# 음유시인 [음파] 이펙트 샘플(초록 배경 3장) → 이펙트 아틀라스 assets/sprites/fx/bard_wave_fx.webp
# 사용: python tools/bard_wave_fx_build.py [샘플 폴더]  (기본 assets/sprites/fx/samples, 파일 bard_src17~19.png)
#   17 = 류트에서 터지는 소리 고리 (lute), 18 = 날아가는 초승달 음파 (wave, 오른쪽으로 볼록), 19 = 맞은 자리에서 퍼지는 음파·파편 (hit, 왼쪽에서 와서 오른쪽으로 퍼짐)
# 샘플 정리:
#   - 배경은 순수 초록(0,240,0)이고 그 위에 반투명한 연두·흰 음파 줄이 겹쳐 있음 → 밝은 픽셀은 초록이 얼마나 남았는지로 투명도를 정하고 배경색을 빼서 본래 색 복원
#     (주황·노랑 불꽃은 초록보다 빨강이 커서 불투명 그대로)
#   - 19번 왼쪽 아래 둥근 흰 모서리(캡처 테두리)는 지움
# 프레임 [x, y, w, h, 기준점x, 기준점y]: lute = 고리 가운데, wave = 초승달 가운데, hit = 음파가 꽂히는 앞쪽(그림 가운데보다 왼쪽)
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = 'assets/sprites/fx/bard_wave_fx.webp'
K = np.array([0.0, 240.0, 0.0])
PIECES = [('lute', 17), ('wave', 18), ('hit', 19)]
HIT_AX = 0.42  # hit 기준점 x = 그림 폭의 42% (음파 줄이 모이는 자리)


def load(path, sheet):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    ex = g - np.maximum(r, b)
    a = np.where(g > 150, np.clip(1 - (ex - 20) / 190, 0, 1), np.where(ex > 60, 0.0, 1.0))
    al = np.maximum(a, 1e-3)[..., None]
    rgb = np.where((a < 1)[..., None], K + (im - K) / al, im).clip(0, 255)
    if sheet == 19:  # 캡처 테두리의 둥근 흰 모서리
        white = im.min(axis=2) > 225
        lab, n = ndi.label(white)
        for i in range(1, n + 1):
            ys, xs = np.where(lab == i)
            if xs.min() == 0 or ys.max() == im.shape[0] - 1: a[lab == i] = 0
        a[183:, :28] = np.where(ex[183:, :28] > -10, 0, a[183:, :28])
    # 압축 티끌
    m = a > 0.08
    lab, n = ndi.label(m)
    areas = ndi.sum(m, lab, range(1, n + 1))
    a = np.where(np.isin(lab, 1 + np.where(areas >= 6)[0]), a, 0)
    ys, xs = np.where(a > 0.08)
    return np.dstack([rgb, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1].clip(0, 255).astype(np.uint8)


def main(folder):
    parts = [(nm, load(f'{folder}/bard_src{s}.png', s)) for nm, s in PIECES]
    W = sum(p.shape[1] + 2 for _, p in parts); H = max(p.shape[0] for _, p in parts)
    atlas = np.zeros((H, W, 4), np.uint8); x = 0; frames = []
    for nm, p in parts:
        h, w = p.shape[:2]
        atlas[:h, x:x + w] = p
        ax = round(w * HIT_AX) if nm == 'hit' else w // 2
        frames.append(f'{nm}: [{x},0,{w},{h},{ax},{h // 2}]')
        x += w + 2
    Image.fromarray(atlas, 'RGBA').save(OUT, 'WEBP', lossless=True)
    print('frames: { ' + ', '.join(frames) + ' }')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/fx/samples')

# 정령사·정령 시트에 남은 흰 배경 지우기 (각 *_build.py를 다시 돌린 뒤에 이것도 다시 돌릴 것)
# 사용: python tools/sprite_bg_cleanup.py
# - halo: 투명한 곳과 맞닿은 밝은 무채색 픽셀(샘플 흰 배경이 섞여 남은 테두리)을 2겹 지움
# - green: 초록(덩굴·잎) 가까이 있는 밝은 무채색 = 덩굴 고리 안에 갇힌 흰 배경
# - seeds: 그 점에서 이어진 밝은 무채색 덩어리 = 몸 사이에 갇힌 흰 배경 (눈 하이라이트·번개 빛은 건드리지 않게 콕 집어서)
# 무채색 = 가장 밝은 채널과 가장 어두운 채널 차이가 작음. 노란 번개 빛·크림색 불꽃은 차이가 커서 남음
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

JOBS = {
    'assets/sprites/monster/earth_spirit.webp': dict(halo=True, green=True),
    'assets/sprites/merc/summoner_0.webp': dict(halo=True, boxes=[(c * 113 + 30, 58, c * 113 + 42, 80) for c in range(5)]),   # 대기·걷기 칸: 왼쪽 머리카락 사이 흰·회색 줄
    'assets/sprites/monster/fire_spirit.webp': dict(halo_x=(0, 864), seeds=[(780, 100), (98, 79), (93, 87)]),   # 피격 칸 꼬리 사이 · 대기 칸 손과 불덩이 사이. 사라짐 칸(6~9)의 연기는 회색이라 테두리 정리에서 뺌
    'assets/sprites/monster/storm_spirit.webp': dict(seeds=[(1180, 45)]),                   # 굵은 번개 칸: 몸과 번개 사이
}


def light_neutral(rgb, lo=170, chroma=45):
    return (rgb.min(axis=2) > lo) & (rgb.max(axis=2) - rgb.min(axis=2) < chroma)


def clean(path, halo=False, halo_x=None, green=False, seeds=(), boxes=()):
    a = np.array(Image.open(path).convert('RGBA'))
    rgb = a[..., :3].astype(int)
    before = int((a[..., 3] > 0).sum())
    ln = light_neutral(rgb)
    if halo or halo_x:
        cols = np.zeros(a.shape[:2], bool)
        if halo_x:
            cols[:, halo_x[0]:halo_x[1]] = True
        else:
            cols[:] = True
        for _ in range(2):
            edge = ndi.binary_dilation(a[..., 3] < 40, structure=np.ones((3, 3))) & (a[..., 3] >= 40)
            a[edge & ln & cols, 3] = 0
    if green:
        g = (a[..., 3] > 128) & (rgb[..., 1] > rgb[..., 0] + 15) & (rgb[..., 1] > rgb[..., 2] + 15)
        near = ndi.binary_dilation(g, iterations=2)
        a[near & light_neutral(rgb, 150, 45), 3] = 0
    for x0, y0, x1, y1 in boxes:   # 이 네모 안의 밝은 무채색(회색 섞인 흰 배경)은 모두 지움
        box = np.zeros(a.shape[:2], bool)
        box[y0:y1, x0:x1] = True
        a[box & light_neutral(rgb, 110, 30), 3] = 0
    for sx, sy in seeds:
        m = (a[..., 3] > 0) & light_neutral(rgb, 200, 40)
        lab, _ = ndi.label(m, structure=np.ones((3, 3)))
        k = lab[sy, sx]
        if not k:
            ys, xs = np.where(m[max(0, sy - 6):sy + 7, max(0, sx - 6):sx + 7])
            if len(ys):
                k = lab[max(0, sy - 6) + ys[0], max(0, sx - 6) + xs[0]]
        if k:
            reg = ndi.binary_dilation(lab == k, iterations=1) & light_neutral(rgb, 170, 45)
            a[reg, 3] = 0
    Image.fromarray(a, 'RGBA').save(path, 'WEBP', lossless=True)
    print(f'{path}: {before - int((a[..., 3] > 0).sum())} px removed')


if __name__ == '__main__':
    for p, kw in JOBS.items():
        clean(p, **kw)

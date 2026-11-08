# 격투가 외형 0(brawler_0.webp)에서 도복·띠·머리 색만 바꾼 외형 시트 만들기 (칸 구성·크기 모두 같음)
# 사용: python tools/brawler_variants_build.py   → assets/sprites/merc/brawler_1~2.webp
# 규칙: 피부(얼굴·손·발과 그 테두리·그림자)와 눈(흰자·눈동자)·입은 그대로.
#   멸식 기운처럼 밝고 진한 빛, 흙먼지(따뜻한 색)는 도복으로 보지 않아 그대로 둠
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(__file__))
from frost_variants_build import rgb2hsv, hsv2rgb

SRC = 'assets/sprites/merc/brawler_0.webp'
# (번호, 이름, 방식, 값)
#   'tone'  = (도복 채도, 도복 명도, 머리 채도, 머리 명도) 배율 (색상은 그대로)
#   'paint' = (도복 색, 띠·깃 색, 머리 색) — None이면 원래 색. 원래 명암을 그 색의 그늘~밝은 면으로 옮겨 칠함
VARIANTS = [
    (1, '흑도복', 'tone', (1.5, 0.25, 0.5, 0.45)),
    (2, '주황 도복·검은 띠', 'paint', ('#e07a28', None, '#2a2020')),
]


def masks(im):
    """(피부·눈처럼 고정할 곳, 머리카락, 머리 테두리, 띠·깃)"""
    hsv = rgb2hsv(im[..., :3] / 255.)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    al = im[..., 3] > 0
    warm = al & ((h <= 45) | (h >= 345)) & (s >= 0.22)
    skin_core = warm & (v >= 0.6) & (s <= 0.55)
    dark = warm & (v < 0.6)
    # 머리카락: 굵은 어두운 갈색 덩어리 (살 테두리선은 빠짐)
    nb = ndimage.convolve(dark.astype(int), np.ones((3, 3), int), mode='constant')
    thick = dark & (nb >= 8)
    lab, n = ndimage.label(thick)
    sz = ndimage.sum(thick, lab, range(1, n + 1))
    thick = np.isin(lab, np.where(sz >= 40)[0] + 1)
    hair = ndimage.binary_dilation(thick) & dark
    hair &= ~(ndimage.binary_dilation(skin_core) & ~thick)
    # 얼굴 안 눈썹·눈 테두리: 살에 둘러싸인 어두운 점은 머리카락에서 뺌
    for _ in range(3):
        sk = ndimage.convolve(skin_core.astype(int), np.ones((5, 5), int), mode='constant')
        hn = ndimage.convolve(hair.astype(int), np.ones((5, 5), int), mode='constant')
        hair &= ~(sk > hn)
    skin = warm & ~hair
    # 머리 바깥 테두리의 밝은 갈색 칸 (살색으로 잡혀 머리를 바꾸면 주황 점으로 남던 곳)
    sk5 = ndimage.convolve(skin_core.astype(int), np.ones((5, 5), int), mode='constant')
    hair_edge = skin & ndimage.binary_dilation(hair) & ndimage.binary_dilation(~al) & (sk5 < 8)
    # 눈 흰자·눈동자·이: 머리 근처에서 살·머리카락에 둘러싸인 작은 조각 (어두운 테두리선으로 나눠서 봄)
    face = skin | hair
    rest = al & ~face & (v >= 0.3)
    lab, n = ndimage.label(rest)
    sizes = ndimage.sum(rest, lab, range(1, n + 1))
    eye = np.zeros_like(rest)
    for i in np.where(sizes <= 24)[0] + 1:
        c = lab == i
        ring = ndimage.binary_dilation(c, np.ones((3, 3), bool)) & ~c
        if (ring & (face | ~al)).sum() >= 0.6 * ring.sum() and (ring & face).sum() >= 0.4 * ring.sum():
            eye |= c
    dk = al & ~face & (v < 0.3)
    en = ndimage.convolve(eye.astype(int), np.ones((3, 3), int), mode='constant')
    eye |= dk & (en >= 2) & (ndimage.convolve((~al).astype(int), np.ones((3, 3), int), mode='constant') == 0)
    eye &= ndimage.binary_dilation(hair, iterations=12)
    skin = (skin & ~hair_edge) | eye
    # 머리 둘레의 옅은 회청 테두리·벌린 입의 이처럼 머리 근처에서 머리·살·바깥에 둘러싸인 작은 조각도 고정
    #   (도복 색으로 칠하면 머리 둘레에 주황 점이 생김)
    face = skin | hair | hair_edge
    rest = al & ~face
    lab, n = ndimage.label(rest, np.ones((3, 3), int))
    sizes = ndimage.sum(rest, lab, range(1, n + 1))
    near = ndimage.binary_dilation(hair, iterations=14)
    for i in np.where(sizes <= 30)[0] + 1:
        c = lab == i
        if not (c & near).any():
            continue
        ring = ndimage.binary_dilation(c, np.ones((3, 3), bool)) & ~c
        if (ring & (face | ~al)).sum() >= 0.85 * ring.sum():
            skin |= c
    # 머리 둘레 4칸 안, 바깥 가장자리(반투명 포함)의 회색 테두리선·머리끝 사이 칸 (몸 전체를 두르는 선에 이어져 있어 위 조각 검사로는 안 잡힘)
    halo = (al & ~skin & ~hair & ~hair_edge & ndimage.binary_dilation(hair | hair_edge, iterations=4) & (s < 0.2)
            & ((im[..., 3] < 255) | ndimage.binary_dilation(~al)))
    skin |= halo
    # 띠·깃: 도복 안의 굵은 검은 부분 (바깥 테두리선·1픽셀 주름선은 뺌)
    body = al & ~skin & ~hair & ~hair_edge
    dkb = body & (v < 0.3)
    nb = ndimage.convolve(dkb.astype(int), np.ones((3, 3), int), mode='constant')
    core = dkb & (nb >= 8)
    lab, n = ndimage.label(core)
    sz = ndimage.sum(core, lab, range(1, n + 1))
    core = np.isin(lab, np.where(sz >= 4)[0] + 1)
    trim = ndimage.binary_propagation(core, mask=dkb & ~ndimage.binary_dilation(~al))
    for _ in range(4):
        c = ndimage.convolve(trim.astype(int), np.ones((3, 3), int), mode='constant')
        trim &= ~(c <= 3) | core
    return skin, hair, hair_edge, trim


def tone(im, skin, hair, ds, dv, hs, hv):
    hsv0 = rgb2hsv(im[..., :3] / 255.)
    hsv = hsv0.copy()
    al = im[..., 3] > 0
    s0, v0 = hsv0[..., 1], hsv0[..., 2]
    # 멸식 기운처럼 밝고 진한 빛은 덜 바꿈
    glow = np.clip((v0 - 0.6) / 0.3, 0, 1) * np.clip((s0 - 0.3) / 0.25, 0, 1)
    body = al & ~skin & ~hair
    for m, sm, vm, g in ((body, ds, dv, glow), (hair, hs, hv, 0)):
        sk = sm + (1 - sm) * g
        vk = vm + (1 - vm) * g
        hsv[..., 1] = np.where(m, np.clip(s0 * sk, 0, 1), hsv[..., 1])
        hsv[..., 2] = np.where(m, np.clip(v0 * vk, 0, 1), hsv[..., 2])
    out = im.copy()
    ch = body | hair
    out[ch, :3] = (hsv2rgb(hsv)[ch] * 255 + .5).clip(0, 255).astype(np.uint8)
    return out


def _hex(c):
    return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)]) / 255.


def _paint(hsv, hsv0, m, color, lo, hi):
    th, ts, tv = rgb2hsv(_hex(color)[None, None])[0, 0]
    t = np.clip((hsv0[..., 2] - lo) / (hi - lo), 0, 1)
    # 흰색·밝은 무채색은 그늘 폭을 좁혀야 회색이 아니라 흰색으로 보임 (흰 띠)
    pale = np.clip((tv - 0.75) / 0.2, 0, 1) * np.clip(1 - ts / 0.25, 0, 1)
    floor = 0.42 + 0.4 * pale
    v = np.clip(tv * (floor + (1.1 - floor) * t), 0, 1)
    s = ts * (1 - 0.45 * np.clip((t - 0.85) / 0.15, 0, 1))  # 가장 밝은 칸은 살짝 색을 뺌 (광택)
    hsv[..., 0] = np.where(m, th, hsv[..., 0])
    hsv[..., 1] = np.where(m, s, hsv[..., 1])
    hsv[..., 2] = np.where(m, v, hsv[..., 2])


def paint(im, skin, hair, trim, dobok, belt, hair_c):
    hsv0 = rgb2hsv(im[..., :3] / 255.)
    hsv = hsv0.copy()
    h0, s0, v0 = hsv0[..., 0] * 360, hsv0[..., 1], hsv0[..., 2]
    al = im[..., 3] > 0
    fabric = al & ~skin & ~hair & ~trim & (((h0 >= 180) & (h0 <= 290)) | (s0 < 0.08)) & (s0 < 0.35) & (v0 >= 0.3)
    ch = np.zeros_like(al)
    if dobok:
        _paint(hsv, hsv0, fabric, dobok, 0.35, 1.0); ch |= fabric
    if belt:
        _paint(hsv, hsv0, trim, belt, 0.04, 0.3); ch |= trim
    if hair_c:
        _paint(hsv, hsv0, hair, hair_c, 0.05, 0.5); ch |= hair
    out = im.copy()
    out[ch, :3] = (hsv2rgb(hsv)[ch] * 255 + .5).clip(0, 255).astype(np.uint8)
    return out


def build(im):
    skin, hair, hair_edge, trim = masks(im)
    hair_all = hair | hair_edge
    res = {}
    for num, label, kind, p in VARIANTS:
        if kind == 'tone':
            res[num] = tone(im, skin, hair_all, *p)
        else:
            res[num] = paint(im, skin, hair_all if p[2] else hair, trim, *p)
    return res


def main():
    im = np.array(Image.open(SRC).convert('RGBA'))
    for num, out in build(im).items():
        Image.fromarray(out, 'RGBA').save(f'assets/sprites/merc/brawler_{num}.webp', 'WEBP', lossless=True)
        print(f'brawler_{num}.webp  {VARIANTS[num - 1][1]}')


if __name__ == '__main__':
    main()

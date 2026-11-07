# 격투가 시크릿 레어 외형 1 (백호: 흰 줄무늬 호랑이·붉은 염주·붕대 손발·검은 바지·붉은 띠, 흰 배경 샘플)
#   → 나중에 캐릭터 시트 assets/sprites/merc/brawler_sr1.webp (칸 순서는 brawler_0과 같아야 함, tools/brawler_build.py 참고)
# 사용: python tools/brawler_sr1_build.py   (동작 샘플이 다 모일 때까지는 미리보기만 만듦: _preview_brawler_sr1_walk.gif)
# 샘플: assets/sprites/fx/samples/brawler_sr1_*_src.*
#   - idle_src.png  대기 (팔짱 낀 자세)
#   - walkA_src.webp · walkB_src.webp  걷기 후보 10장씩 (5×2 칸, 아래 번호 글자). A는 작고 팔 모양이 칸마다 들쑥날쑥(4·7·9 팔 들어 올림)
#     B는 그림이 크고 팔 모양이 일정함. B9·B10은 팔짱으로 넘어가는 칸이라 걷기엔 안 씀 (B10엔 발 쪽 회색 별 무늬도 있음)
#     B2~B5는 꼬리가 아래로 늘어지고 B6~B8은 꼬리를 말아 올려서, 섞으면 걸음마다 꼬리가 위아래로 튐 → 꼬리가 같은 B2~B5만 씀
#     → 걷기 = B2 (보폭 최대, 두 발 디딤) → B3 (보폭 줄며 몸이 내려감) → B4 (뒷발 들어 앞으로) → B5 (뒷발이 몸 밑을 지나감) → 다시 B2
# 흰 배경: 가장자리에서 이어진 흰 픽셀 + 꼬리·팔 사이에 갇힌 새하얀 구멍(무채색 253 안팎) 을 지움
#   (호랑이 흰 털은 푸른 기가 돌고(파랑이 빨강보다 ~6 높음) 238 안팎이라 남음)
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from berserker_build import shrink

D = 'assets/sprites/fx/samples/brawler_sr1_'
TARGET_H = 86   # 대기 자세 키 → brawler_0과 같은 칸 키
WALK = ['B2', 'B3', 'B4', 'B5']


def cells(name):   # 여러 칸 샘플 → {'B1': 그림, ...} (큰 덩어리를 줄·칸 순서로)
    im = np.array(Image.open(f'{D}walk{name}_src.webp').convert('RGB'))
    fg = im.min(axis=2) < 215
    lab, k = ndi.label(ndi.binary_dilation(fg, iterations=3))
    sz = ndi.sum(fg, lab, range(1, k + 1))
    objs = ndi.find_objects(lab)
    big = sorted([objs[i] for i in range(k) if sz[i] > 2000], key=lambda o: (o[0].start // 150, o[1].start))
    return {f'{name}{j + 1}': im[sl] for j, sl in enumerate(big)}


def cut(im):   # 흰 배경 지우고 가장 큰 덩어리(캐릭터)만 → RGBA, 외곽은 흰색과 섞인 만큼 반투명으로 풀어 줌
    im = im.astype(float)
    white = (im.min(axis=2) > 222) & (im.max(axis=2) - im.min(axis=2) < 20)
    lab, n = ndi.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    for i in range(1, n + 1):   # 갇힌 새하얀 구멍
        m = lab == i
        if not bg[m].any() and m.sum() >= 20:
            px = im[m]
            if px.mean() > 248 and (px.max(axis=1) - px.min(axis=1)).mean() < 2: bg |= m
    rim = ~bg & ndi.binary_dilation(bg, iterations=2)
    a = np.where(bg, 0.0, 1.0)
    a = np.where(rim, np.clip((255 - im.min(axis=2)) / 200, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    im = np.where(rim[..., None], (im - 255 * (1 - al)) / al, im).clip(0, 255)
    m = a > 0.5
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
    sz = ndi.sum(m, lab, range(1, n + 1))
    a = np.where(lab == 1 + int(np.argmax(sz)), a, 0)
    a = np.where(a < 0.12, 0, a)
    ys, xs = np.where(a > 0)
    return np.dstack([im, a * 255])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def head(rgba):   # 머리 줄(위 4~20%)의 최대 폭 · 가운데 x
    k = rgba[..., 3] > 127
    rows = [np.where(k[y])[0] for y in range(int(k.shape[0] * .04), int(k.shape[0] * .2))]
    rows = [r for r in rows if len(r)]
    return max(r.max() - r.min() + 1 for r in rows), float(np.mean([(r.max() + r.min()) / 2 for r in rows]))


def main():
    idle = cut(np.array(Image.open(f'{D}idle_src.png').convert('RGB')))
    sc0 = TARGET_H / idle.shape[0]
    hw0 = head(idle)[0] * sc0
    src = {**cells('A'), **cells('B')}
    frames = []
    for nm in WALK:   # 걷기는 머리 폭을 대기와 같게, 기준점은 머리 가운데 (걸을 때 몸이 좌우로 흔들리지 않게)
        r = cut(src[nm]); hw, hcx = head(r); sc = hw0 / hw
        frames.append((shrink(r, sc), hcx * sc))
        print(f'{nm}: {r.shape[1]}x{r.shape[0]} ×{sc:.3f}')
    L = max(c for _, c in frames) + 6; R = max(p.shape[1] - c for p, c in frames) + 6
    H = max(p.shape[0] for p, _ in frames) + 4
    gif = []
    for p, c in frames:
        cv = Image.new('RGBA', (int(L + R), H), (70, 90, 70, 255))
        cv.alpha_composite(Image.fromarray(p), (int(round(L - c)), H - 2 - p.shape[0]))
        gif.append(cv.resize((cv.width * 3, cv.height * 3), Image.NEAREST).convert('RGB'))
    gif[0].save('_preview_brawler_sr1_walk.gif', save_all=True, append_images=gif[1:], duration=150, loop=0)


if __name__ == '__main__':
    main()

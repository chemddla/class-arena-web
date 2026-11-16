# 기공포 이펙트 시안(pixelfx 시트)을 새 기공사 그림(기공포 모으기·쏘기)과 과녁 둘에 합쳐 움직이는 미리보기
# 사용: python compose_cannon.py <pixelfx 폴더> <게임 폴더> <출력 폴더> 시안이름...
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FX, GAME, OUT = sys.argv[1:4]
NAMES = sys.argv[4:]
sys.path.insert(0, os.path.join(GAME, 'tools'))
os.chdir(GAME)
from qigong_sample_build import build

rows = dict(build())
idle = rows['대기'][0][0]
gather, shoot = rows['기공포'][0][0], rows['기공포'][1][0]
HURT = rows['피격'][0][0]
CHARGE, FLY, END, TARGETS, H = 0.6, 0.55, 270, [110, 200], 50
TITLES = {'qi-cannon-a': '기공포 A 큰 실타래 포', 'qi-cannon-b': '기공포 B 나선 실 포', 'qi-cannon-c': '기공포 C 고리 꼬리 포'}


def hand(fr):
    a = fr[..., 3] > 0
    a[int(fr.shape[0] * .7):] = False
    x = np.where(a.any(axis=0))[0].max()
    return x, int(np.where(a[:, x])[0].mean())


def foot(fr):
    a = fr[..., 3] > 0
    return np.where(a[int(fr.shape[0] * .92):].any(axis=0))[0].mean()


def frames_of(name):
    d = os.path.join(FX, 'records', 'qigong', name)
    j = json.load(open(os.path.join(d, f'{name}.json'), encoding='utf-8'))
    im = np.array(Image.open(os.path.join(d, f'{name}.png')).convert('RGBA')).astype(float)
    al = im[..., 3:4]
    im[..., :3] = np.where(al > 0, np.clip(im[..., :3] * 255 / np.maximum(al, 1), 0, 255), 0)   # 투명도가 미리 곱해진 색 되돌리기
    im = Image.fromarray(im.astype(np.uint8), 'RGBA')
    fr = j['frames']; fr = list(fr.values()) if isinstance(fr, dict) else fr
    return [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + f['frame']['w'], f['frame']['y'] + f['frame']['h'])) for f in fr], j['meta']['pixelfx']


def make(name):
    frames, meta = frames_of(name)
    fps = meta.get('fps', 30); px, py = meta['pivot']
    W, Hh = frames[0].size
    hx, hy = hand(shoot)
    hand_h = shoot.shape[0] - hy
    G = py + 6 + max(0, hand_h - H)
    cw, ch = W + 60, G + 10
    fxx, fxy = 40, G - py - (hand_h - H)
    fx0 = 40 + px - hx + foot(shoot)
    out = []
    for i in range(len(frames) + 10):
        t = i / fps
        bg = Image.new('RGBA', (cw, ch), (34, 36, 44, 255))
        ImageDraw.Draw(bg).line([(0, G), (cw, G)], fill=(60, 62, 72, 255))
        body = gather if t < CHARGE else shoot if t < CHARGE + FLY + 0.3 else idle
        bg.alpha_composite(Image.fromarray(body, 'RGBA'), (int(fx0 - foot(body)), G - body.shape[0]))
        for tx in TARGETS:
            pt = CHARGE + tx / END * FLY
            tb = HURT if pt <= t < pt + 0.3 else idle
            tg = Image.fromarray(tb, 'RGBA').transpose(Image.FLIP_LEFT_RIGHT)
            bg.alpha_composite(tg, (int(40 + px + tx + 4 - tg.width / 2), G - tg.height))
        if i < len(frames): bg.alpha_composite(frames[i], (fxx, fxy))
        out.append(bg)
    big = [g.resize((g.width * 3, g.height * 3), Image.NEAREST).convert('RGB') for g in out]
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 30)
    for g in big: ImageDraw.Draw(g).text((12, 8), TITLES.get(name, name), font=font, fill=(235, 235, 235))
    big[0].save(os.path.join(OUT, f'_preview_qigong_{name}.gif'), save_all=True, append_images=big[1:], duration=int(1000 / fps), loop=0)
    return big


if __name__ == '__main__':
    strips = []
    for nm in NAMES:
        big = make(nm)
        pick = [big[i] for i in (6, 14, 19, 22, 25, 29, 33, 38) if i < len(big)]
        strips.append(pick)
    w, h = strips[0][0].size
    s = Image.new('RGB', (w // 2 * 2, h // 2 * 4 * len(strips)), (20, 20, 26))
    for r, pick in enumerate(strips):
        for c, f in enumerate(pick):
            s.paste(f.resize((w // 2, h // 2), Image.NEAREST), ((c % 2) * (w // 2), (r * 4 + c // 2) * (h // 2)))
    s.save(os.path.join(OUT, '_preview_qigong_cannon_compare.png'))
    print('ok', s.size)

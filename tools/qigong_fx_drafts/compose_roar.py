# 기공후 이펙트 시안(pixelfx 시트)을 새 기공사 그림(모으기 → 펼치기 → 대기)과 합쳐 움직이는 미리보기
# 사용: python compose_barrier.py <pixelfx 폴더> <게임 폴더> <출력 폴더> 시안이름...
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
gather, spread = rows['기공후'][0][0], rows['기공후'][1][0]
CAST = 0.4
TITLES = {'qi-roar-a': '기공후 A 기압 물결', 'qi-roar-b': '기공후 B 고리 폭풍', 'qi-roar-c': '기공후 C 기운 숨결'}


def foot(fr):
    a = fr[..., 3] > 0
    return np.where(a[int(fr.shape[0] * .92):].any(axis=0))[0].mean()


def frames_of(name):
    d = os.path.join(FX, 'records', 'qigong', name)
    j = json.load(open(os.path.join(d, f'{name}.json'), encoding='utf-8'))
    im = np.array(Image.open(os.path.join(d, f'{name}.png')).convert('RGBA')).astype(float)
    al = im[..., 3:4]
    im[..., :3] = np.where(al > 0, np.clip(im[..., :3] * 255 / np.maximum(al, 1), 0, 255), 0)
    im = Image.fromarray(im.astype(np.uint8), 'RGBA')
    fr = j['frames']; fr = list(fr.values()) if isinstance(fr, dict) else fr
    return [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + f['frame']['w'], f['frame']['y'] + f['frame']['h'])) for f in fr], j['meta']['pixelfx']


def make(name):
    frames, meta = frames_of(name)
    fps = meta.get('fps', 30); px, py = meta['pivot']
    W, Hh = frames[0].size
    out = []
    for i in range(len(frames) + 6):
        t = i / fps
        bg = Image.new('RGBA', (W, Hh), (34, 36, 44, 255))
        ImageDraw.Draw(bg).line([(0, py), (W, py)], fill=(60, 62, 72, 255))
        body = gather if t < CAST else spread if t < CAST + 0.5 else idle
        bg.alpha_composite(Image.fromarray(body, 'RGBA'), (int(px - foot(body)), py - body.shape[0]))
        if i < len(frames): bg.alpha_composite(frames[i], (0, 0))
        out.append(bg)
    big = [g.resize((g.width * 2, g.height * 2), Image.NEAREST).convert('RGB') for g in out]
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 22)
    for g in big: ImageDraw.Draw(g).text((10, 6), TITLES.get(name, name), font=font, fill=(235, 235, 235))
    big[0].save(os.path.join(OUT, f'_preview_qigong_{name}.gif'), save_all=True, append_images=big[1:], duration=int(1000 / fps), loop=0)
    return big


if __name__ == '__main__':
    strips = []
    for nm in NAMES:
        big = make(nm)
        strips.append([big[i] for i in (4, 10, 13, 15, 18, 22, 27, 34) if i < len(big)])
    w, h = strips[0][0].size
    cols = 4; sw, sh = w // 2, h // 2
    s = Image.new('RGB', (sw * cols, sh * 2 * len(strips)), (20, 20, 26))
    for r, pick in enumerate(strips):
        for c, f in enumerate(pick):
            s.paste(f.resize((sw, sh), Image.NEAREST), ((c % cols) * sw, (r * 2 + c // cols) * sh))
    s.save(os.path.join(OUT, '_preview_qigong_roar_compare.png'))
    print('ok', s.size, len(big))

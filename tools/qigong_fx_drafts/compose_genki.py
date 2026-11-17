# 기공옥 이펙트 시안(pixelfx 시트)을 새 기공사 그림(땅에서 모으기 → 떠올라 치켜들기 → 던지기 → 대기)과 합쳐 움직이는 미리보기
# 캐릭터는 이펙트 크기(게임 px × 0.8)에 맞춰 반으로 줄이고, 떠오르는 높이는 시안의 lift01과 같게
# 사용: python compose_genki.py <pixelfx 폴더> <게임 폴더> <출력 폴더> 시안이름...
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FX, GAME, OUT = sys.argv[1:4]
NAMES = sys.argv[4:]
sys.path.insert(0, os.path.join(GAME, 'tools'))
os.chdir(GAME)
from qigong_sample_build import build

GROUND, RISE, THROW, FALL, LIFT = 1.0, 2.4, 3.75, 0.5, 88
rows = dict(build())
half = lambda a: Image.fromarray(a, 'RGBA').resize((a.shape[1] // 2, a.shape[0] // 2), Image.NEAREST)
idle = half(rows['대기'][0][0])
ok1, ok3, ok4, ok5 = [half(f[0]) for f in rows['기공옥']]
TITLES = {'qi-genki-a': '기공옥 A 원기옥'}


def sstep(a, b, x):
    u = min(1, max(0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


def lift01(t):
    if t < GROUND: return 0
    if t < THROW: return sstep(GROUND, RISE, t)
    u = min(1, max(0, (t - THROW) / (FALL + 0.3)))
    return 1 - u * u


def foot(im):
    a = np.array(im)[..., 3] > 0
    return np.where(a[int(a.shape[0] * .92):].any(axis=0))[0].mean()


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
        body = ok1 if t < GROUND else ok3 if t < RISE else ok4 if t < THROW else ok5 if t < THROW + 0.6 else idle
        bg.alpha_composite(body, (int(px - foot(body)), int(py - body.height - LIFT * lift01(t))))
        if i < len(frames): bg.alpha_composite(frames[i], (0, 0))
        out.append(bg)
    big = [g.convert('RGB') for g in out]
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 22)
    for g in big: ImageDraw.Draw(g).text((10, 6), TITLES.get(name, name), font=font, fill=(235, 235, 235))
    big[0].save(os.path.join(OUT, f'_preview_qigong_{name}.gif'), save_all=True, append_images=big[1:], duration=int(1000 / fps), loop=0)
    return big


if __name__ == '__main__':
    for nm in NAMES:
        big = make(nm)
        pick = [big[i] for i in (100, 122, 129, 133, 138, 145, 155, 168, 182, 195) if i < len(big)]
        w, h = pick[0].size; cols = 2; sw, sh = w // 2, h // 2
        s = Image.new('RGB', (sw * cols, sh * ((len(pick) + 1) // 2)), (20, 20, 26))
        for c, f in enumerate(pick): s.paste(f.resize((sw, sh), Image.NEAREST), ((c % cols) * sw, (c // cols) * sh))
        s.save(os.path.join(OUT, f'_preview_qigong_{nm}_steps.png'))
        print('ok', s.size, len(big))

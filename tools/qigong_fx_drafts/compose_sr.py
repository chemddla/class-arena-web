# 기공사 SR 전용 이펙트 시안(pixelfx 시트, sr-*.js)을 SR 외형 그림(assets/sprites/merc/qigong_sr1.webp)과 합쳐 움직이는 미리보기
# 사용: python compose_sr.py <pixelfx 폴더> <게임 폴더> <출력 폴더> [시안이름...]  (이름을 빼면 sr-* 전부)
# 캐릭터: 시트 칸 = 그림 너비 / 24, 대기 칸 키가 86 게임 px가 되게 줄임. 발 자리는 대기 칸 기준으로 모든 칸에 같게 (기공옥 공중 칸은 떠 보임)
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FX, GAME, OUT = sys.argv[1:4]
NAMES = sys.argv[4:] or ['sr-atk', 'sr-cannon', 'sr-bullets', 'sr-barrier', 'sr-roar', 'sr-wave', 'sr-genki']
TARGET_H = 86

# 시안마다: 제목 · 그림 칸 시간표 [(끝나는 초, 칸)] · 허수아비 자리(발에서 앞으로 게임 px)
PLAN = {
    'sr-atk': ('일반 공격 · 청기탄', [(.22, 5), (.6, 6)], [213]),
    'sr-cannon': ('기공포 · 청기구', [(.6, 10), (1.1, 11)], [162, 252, 380]),
    'sr-bullets': ('기공탄 · 청기 다섯 알', [(.3, 12), (.75, 13)], [175, 245, 315]),
    'sr-barrier': ('기공막 · 청기막', [(.4, 14), (.75, 15)], []),
    'sr-roar': ('기공후 · 청기 파동', [(.4, 14), (.95, 15)], [-120, 130]),
    'sr-wave': ('기공파 · 청기파', [(1.2, 16), (2.5, 17), (4.15, 22)], [210, 310, 410]),
    'sr-genki': ('기공옥 · 청천옥', [(1.0, 18), (1.6, 23), (3.8, 19), (4.4, 20), (5.0, 21)], [120, 180, 310, 370, 440, 40]),
}

sheet = Image.open(os.path.join(GAME, 'assets/sprites/merc/qigong_sr1.webp')).convert('RGBA')
CW = sheet.width // 24
cell = lambda i: sheet.crop((i * CW, 0, (i + 1) * CW, sheet.height))
a0 = np.array(cell(0))[..., 3] > 100
ys = np.where(a0.any(1))[0]
SC = TARGET_H / (ys.max() - ys.min() + 1)
FOOT_Y = ys.max()
FOOT_X = np.where(a0[int(FOOT_Y - (FOOT_Y - ys.min()) * .08):FOOT_Y + 1].any(0))[0].mean()
_cache = {}


def body(i):
    if i not in _cache:
        c = cell(i)
        _cache[i] = c.resize((round(c.width * SC), round(c.height * SC)), Image.BOX)
    return _cache[i]


def frames_of(name):
    d = os.path.join(FX, 'records', 'qigong', name)
    j = json.load(open(os.path.join(d, f'{name}.json'), encoding='utf-8'))
    im = np.array(Image.open(os.path.join(d, f'{name}.png')).convert('RGBA')).astype(float)
    al = im[..., 3:4]
    im = Image.fromarray(im.astype(np.uint8), 'RGBA')   # 미리 곱한 알파 그대로 (옅은 곳을 되돌리면 색이 틀어져 회색·분홍 얼룩이 생김)
    fr = j['frames']; fr = list(fr.values()) if isinstance(fr, dict) else fr
    return [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + f['frame']['w'], f['frame']['y'] + f['frame']['h'])) for f in fr], j['meta']['pixelfx']


def dummy(d, x, g):
    d.ellipse([x - 9, g - 2, x + 9, g + 2], fill=(10, 14, 18, 255))
    d.rectangle([x - 1, g - 36, x + 1, g], fill=(78, 64, 52, 255))
    d.rectangle([x - 8, g - 30, x + 8, g - 28], fill=(123, 102, 80, 255))
    d.rectangle([x - 5, g - 27, x + 5, g - 13], fill=(106, 86, 64, 255))
    d.ellipse([x - 6, g - 48, x + 6, g - 34], fill=(139, 117, 88, 255))


def make(name):
    title, plan, dummies = PLAN[name]
    frames, meta = frames_of(name)
    fps = meta.get('fps', 30); px, py = meta['pivot']
    W, Hh = frames[0].size
    out = []
    for i in range(len(frames) + 8):
        t = i / fps
        bg = Image.new('RGBA', (W, Hh), (23, 31, 40, 255))
        d = ImageDraw.Draw(bg)
        d.rectangle([0, py, W, Hh], fill=(26, 37, 48, 255)); d.line([(0, py), (W, py)], fill=(43, 57, 70, 255))
        for x in dummies: dummy(d, px + x, py)
        d.ellipse([px - 16, py - 3, px + 16, py + 3], fill=(12, 16, 22, 255))
        f = next((fr for end, fr in plan if t < end), 0)
        b = body(f)
        bg.alpha_composite(b, (round(px - FOOT_X * SC), round(py - FOOT_Y * SC)))
        if i < len(frames):
            f_ = np.array(frames[i]).astype(float); g_ = np.array(bg).astype(float)
            g_[..., :3] = np.clip(f_[..., :3] + g_[..., :3] * (1 - f_[..., 3:4] / 255), 0, 255)
            bg = Image.fromarray(g_.astype(np.uint8), 'RGBA')
        out.append(bg)
    big = [g.resize((g.width * 2, g.height * 2), Image.NEAREST).convert('RGB') for g in out]
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 20)
    for g in big: ImageDraw.Draw(g).text((10, 6), f'SR {title}', font=font, fill=(220, 240, 248))
    big[0].save(os.path.join(OUT, f'_preview_qigong_{name}.gif'), save_all=True, append_images=big[1:], duration=int(1000 / fps), loop=0)
    return big


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for nm in NAMES:
        big = make(nm)
        pick = [big[int(len(big) * k)] for k in (.08, .2, .32, .45, .6, .75)]
        w, h = pick[0].size; sw, sh = w // 2, h // 2
        s = Image.new('RGB', (sw * 3, sh * 2))
        for c, f in enumerate(pick): s.paste(f.resize((sw, sh), Image.NEAREST), ((c % 3) * sw, (c // 3) * sh))
        s.save(os.path.join(OUT, f'_preview_qigong_{nm}_steps.png'))
        print('ok', nm, len(big))

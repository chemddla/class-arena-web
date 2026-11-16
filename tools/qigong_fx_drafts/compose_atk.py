# 기공사 일반 공격 이펙트 시안(pixelfx 시트)을 새 기공사 그림과 합쳐 움직이는 미리보기 만들기
# 사용: python compose_atk.py <pixelfx 폴더> <게임 폴더> <출력 폴더> 시안이름...
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
charge, thrust = rows['일반 공격'][0][0], rows['일반 공격'][1][0]
TARGET = rows['피격'][0][0]
CHARGE_T, HIT_T = 0.22, 0.52


def hand(fr):   # 내민 손 = 위쪽 70% 안에서 가장 오른쪽 불투명 칸
    a = fr[..., 3] > 0
    a[int(fr.shape[0] * .7):] = False
    xs = np.where(a.any(axis=0))[0]; x = xs.max()
    ys = np.where(a[:, x])[0]
    return x, int(ys.mean())


def foot(fr):
    a = fr[..., 3] > 0
    return np.where(a[int(fr.shape[0] * .92):].any(axis=0))[0].mean()


def sheet_frames(name):
    d = os.path.join(FX, 'records', 'qigong', name)
    j = json.load(open(os.path.join(d, f'{name}.json'), encoding='utf-8'))
    im = Image.open(os.path.join(d, f'{name}.png')).convert('RGBA')
    fr = j['frames']; fr = list(fr.values()) if isinstance(fr, dict) else fr
    meta = j['meta']['pixelfx']
    out = [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + f['frame']['w'], f['frame']['y'] + f['frame']['h'])) for f in fr]
    return out, meta


def make(name, title):
    frames, meta = sheet_frames(name)
    fps = meta.get('fps', 30); px, py = meta['pivot']['x'] if isinstance(meta['pivot'], dict) else meta['pivot'][0], meta['pivot']['y'] if isinstance(meta['pivot'], dict) else meta['pivot'][1]
    W, Hh = frames[0].size
    hx, hy = hand(thrust)
    hand_h = thrust.shape[0] - hy              # 손 높이 (발 위)
    G = py + 6 + max(0, hand_h - 50)           # 바닥 줄 (캔버스 y)
    canvas_w, canvas_h = W + 80, G + 10
    fxx, fxy = 40, G - py - (hand_h - 50)      # 이펙트 시트를 놓는 자리: 원점 손 높이 50 → 실제 손 높이에 맞춤
    foot_t = foot(thrust)
    gif = []
    for i in range(len(frames) + 12):
        t = i / fps
        bg = Image.new('RGBA', (canvas_w, canvas_h), (34, 36, 44, 255))
        ImageDraw.Draw(bg).line([(0, G), (canvas_w, G)], fill=(60, 62, 72, 255))
        body = charge if t < CHARGE_T else thrust if t < HIT_T + 0.35 else idle
        fx0 = 40 + px - hx + foot_t            # 발 가운데 x (모든 칸 같은 자리)
        bg.alpha_composite(Image.fromarray(body, 'RGBA'), (int(fx0 - foot(body)), G - body.shape[0]))
        tb = TARGET if HIT_T <= t < HIT_T + 0.3 else idle
        tg = Image.fromarray(tb, 'RGBA').transpose(Image.FLIP_LEFT_RIGHT)
        bg.alpha_composite(tg, (int(40 + px + 170 + 6 - tg.width / 2), G - tg.height))
        if i < len(frames): bg.alpha_composite(frames[i], (fxx, fxy))
        gif.append(bg)
    big = [g.resize((g.width * 3, g.height * 3), Image.NEAREST).convert('RGB') for g in gif]
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 30)
    for g in big:
        ImageDraw.Draw(g).text((12, 8), title, font=font, fill=(235, 235, 235))
    big[0].save(os.path.join(OUT, f'_preview_qigong_{name}.gif'), save_all=True, append_images=big[1:], duration=int(1000 / fps), loop=0)
    return big


if __name__ == '__main__':
    TITLES = {'atk-a': 'A 금빛 기탄', 'atk-b': 'B 장풍', 'atk-c': 'C 나선 기류', 'atk-d': 'D 삼연 기탄', 'atk-e': 'E 태극 기구슬', 'atk-f': 'F 실타래 기구슬',
              'atk-f-blue': 'F 실타래 기구슬 (하늘색)', 'qi-g': 'G 기운 덩어리', 'qi-h': 'H 기압 장풍', 'qi-i': 'I 기류 띠', 'qi-j': 'J 실타래 기구슬'}
    for nm in NAMES:
        make(nm, TITLES.get(nm, nm))
        print(nm)

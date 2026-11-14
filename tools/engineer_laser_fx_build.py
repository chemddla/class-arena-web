# 레이저탑 이펙트 (2026-11-14 사용자 선택: 후보 1 + 빔 2배 굵기 + 흐린 한 줄 조준선) → assets/sprites/fx/engineer_laser_fx.webp (두 줄)
# 사용: python tools/engineer_laser_fx_build.py
#   charge : pixelfx lightning/charge-up 5~45칸 (불티·빛이 렌즈로 모여듦, 41칸) — 조준선을 보이는 동안 조준이 찬 만큼 넘김
#   hit    : pixelfx explosions/plasma-explosion 0~15칸 (흰 섬광 → 빛 구슬 + 충격 고리) — 레이저에 맞은 대상마다
#   샘플 = assets/sprites/fx/samples/engineer_laser_{charge,hit}_src.png + .json (pixelfx --sheet --bg none --no-actor 기본 팔레트)
#   그림은 원본 크기 그대로 두고 게임이 0.35배로 줄여 그림 (줄일 때라 부드럽게 그려도 흐리지 않음)
# 빔·조준선은 각도마다 달라 게임이 직접 그림 (index.html drawEngineerEffect eng_laser)
import json
from PIL import Image

S = 'assets/sprites/fx/samples/engineer_laser_'
OUT = 'assets/sprites/fx/engineer_laser_fx.webp'
ROWS = [('charge', 5, 41, (133, 128)),   # (이름, 첫 칸, 칸 수, 기준점: 모이는 자리 / 폭발 가운데) · 충전 빛이 모이는 점(밝은 픽셀 가운데 139)에서 6px 왼쪽 = 게임에서 렌즈보다 2px 오른쪽 · y는 6px 아래(128) = 2px 위 (2026-11-14 사용자 "살짝 오른쪽", "살짝 위로")
        ('hit', 0, 16, (112, 100))]


def frames(name, s, n):
    im = Image.open(S + name + '_src.png').convert('RGBA')
    js = json.load(open(S + name + '_src.json', encoding='utf-8'))
    return [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + f['frame']['w'], f['frame']['y'] + f['frame']['h'])) for f in js['frames'][s:s + n]]


def main():
    rows, info, y = [], {}, 0
    for name, s, n, (ox, oy) in ROWS:
        fr = frames(name, s, n)
        box = None
        for f in fr:
            b = f.getbbox()
            if b: box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
        fr = [f.crop(box) for f in fr]
        rows.append((fr, y))
        info[name] = {'y': y, 'w': fr[0].width, 'h': fr[0].height, 'n': n, 'ox': ox - box[0], 'oy': oy - box[1]}
        y += fr[0].height
    W = max(len(fr) * fr[0].width for fr, _ in rows)
    sheet = Image.new('RGBA', (W, y), (0, 0, 0, 0))
    for fr, yy in rows:
        for i, f in enumerate(fr):
            sheet.alpha_composite(f, (i * f.width, yy))
    sheet.save(OUT, 'WEBP', lossless=True)
    print(json.dumps(info), sheet.size)


if __name__ == '__main__':
    main()

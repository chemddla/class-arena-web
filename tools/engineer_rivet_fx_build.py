# 기계공 기본 공격 '황동 리벳탄' 이펙트 → assets/sprites/fx/engineer_rivet_fx.webp (한 장에 세 줄)
# 사용: python tools/engineer_rivet_fx_build.py
# 샘플 = pixelfx(patch-gg/pixelfx) 렌더 시트 (assets/sprites/fx/samples/engineer_rivet_*_src.png + .json, --sheet --bg none --no-actor)
#   muzzle : projectiles/muzzle-pistol (기본 팔레트) → 앞 14칸(30fps, 0.47초)만: 기본 공격 주기 0.85초 안에 연기가 끝나게
#   tracer : projectiles/bullet-tracer {"length":40} → 18칸 반복. 총알 머리(184,18) 뒤쪽 꼬리만 남기게 오른쪽 70px만 자름
#   hit    : impacts/hit-spark (기본 팔레트) → 16칸
# 줄마다 칸 크기·기준점(섬광 자리 / 총알 머리 / 불꽃 자리)은 출력 → index.html ENG_RIVET_FX
# 그림 1px = 게임 1px (도트 그대로, 게임은 부드럽게 늘리지 않고 그림)
import json
from PIL import Image

S = 'assets/sprites/fx/samples/engineer_rivet_'
OUT = 'assets/sprites/fx/engineer_rivet_fx.webp'
ROWS = [  # (이름, 칸 수, 자를 상자(칸 안 x0, x1), 기준점(칸 안))
    ('muzzle', 14, (0, 96), (44, 40)),    # 섬광 자리 = 바닥 기준점(44,66)에서 총구 높이 26 위
    ('tracer', 18, (130, 200), (184, 18)),
    ('hit', 16, (0, 136), (44, 44)),      # 불꽃 자리 = 바닥 기준점(44,64)에서 높이 20 위
]


def frames(name):
    im = Image.open(S + name + '_src.png').convert('RGBA')
    js = json.load(open(S + name + '_src.json', encoding='utf-8'))
    return [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + f['frame']['w'], f['frame']['y'] + f['frame']['h'])) for f in js['frames']]


def main():
    rows, info, y = [], {}, 0
    for name, n, (x0, x1), (ox, oy) in ROWS:
        fr = [f.crop((x0, 0, x1, f.height)) for f in frames(name)[:n]]
        rows.append((fr, y))
        info[name] = {'y': y, 'w': x1 - x0, 'h': fr[0].height, 'n': n, 'ox': ox - x0, 'oy': oy}
        y += fr[0].height
    W = max(len(fr) * fr[0].width for fr, _ in rows)
    sheet = Image.new('RGBA', (W, y), (0, 0, 0, 0))
    for fr, yy in rows:
        for i, f in enumerate(fr):
            sheet.alpha_composite(f, (i * f.width, yy))
    sheet.save(OUT, 'WEBP', lossless=True)
    print(json.dumps(info))


if __name__ == '__main__':
    main()

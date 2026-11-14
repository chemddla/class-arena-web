# 기관포탑 총탄 이펙트 '얇은 금빛 예광선' → assets/sprites/fx/engineer_gatling_fx.webp (한 장에 두 줄)
# 사용: python tools/engineer_gatling_fx_build.py
#   tracer : 도트로 직접 그림 (1칸). 오른쪽 끝이 머리: 흰 머리 2px + 위아래 옅은 빛 → 1px 꼬리가 금빛 → 주황 → 붉게 식으며 투명해짐 (길이 26)
#            기본 공격 리벳탄(굵고 둥근 꼬리)과 다르게 가늘고 날카로운 기관포 총탄 (2026-11-14 사용자 선택: 후보 1)
#   hit    : pixelfx impacts/hit-spark (기본 팔레트) 16칸을 절반 크기로 (도트 그대로 NEAREST) → 작은 금빛 불티
#            샘플 = assets/sprites/fx/samples/engineer_rivet_hit_src.png (+ .json, 리벳탄과 같은 렌더)
# 출력한 칸 크기·기준점은 index.html ENG_GAT_FX
import json
from PIL import Image

OUT = 'assets/sprites/fx/engineer_gatling_fx.webp'
HIT = 'assets/sprites/fx/samples/engineer_rivet_hit_src'
RAMP = ['#fff3a6', '#ffe26b', '#ffc23d', '#ff8a2a', '#f2561d', '#c9281f']
LEN = 26


def rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def tracer():
    im = Image.new('RGBA', (LEN + 2, 5), (0, 0, 0, 0)); px = im.load()
    for d in range(LEN):
        u = d / (LEN - 1)
        c = rgb(RAMP[min(len(RAMP) - 1, int(u * len(RAMP)))])
        a = 255 if u <= 0.15 else int(255 * (1 - u) ** 0.7)
        px[LEN - d, 2] = (*c, a)
    px[LEN, 2] = px[LEN + 1, 2] = (255, 255, 255, 255)
    for dx, dy in ((0, -1), (0, 1), (1, -1), (1, 1)):
        px[LEN + dx, 2 + dy] = (*rgb(RAMP[0]), 110)
    return im, (LEN + 1, 2)


def hits():
    im = Image.open(HIT + '.png').convert('RGBA')
    js = json.load(open(HIT + '.json', encoding='utf-8'))
    fr = [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + f['frame']['w'], f['frame']['y'] + f['frame']['h'])) for f in js['frames']]
    return [f.resize((f.width // 2, f.height // 2), Image.NEAREST) for f in fr], (22, 22)   # 불꽃 자리 (44,44)의 절반


def main():
    tr, (tox, toy) = tracer()
    hs, (hox, hoy) = hits()
    W = max(tr.width, hs[0].width * len(hs))
    sheet = Image.new('RGBA', (W, tr.height + hs[0].height), (0, 0, 0, 0))
    sheet.alpha_composite(tr, (0, 0))
    for i, f in enumerate(hs):
        sheet.alpha_composite(f, (i * f.width, tr.height))
    sheet.save(OUT, 'WEBP', lossless=True)
    print(json.dumps({'tracer': {'y': 0, 'w': tr.width, 'h': tr.height, 'ox': tox, 'oy': toy},
                      'hit': {'y': tr.height, 'w': hs[0].width, 'h': hs[0].height, 'n': len(hs), 'ox': hox, 'oy': hoy}}))


if __name__ == '__main__':
    main()

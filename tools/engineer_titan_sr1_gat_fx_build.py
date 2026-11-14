# 기계공 시크릿 레어 최종병기 기관총 총탄 '청록 예광선' → assets/sprites/fx/engineer_titan_sr1_gat_fx.webp (한 장에 두 줄)
# 사용: python tools/engineer_titan_sr1_gat_fx_build.py   (2026-11-14 사용자 선택: 후보 3)
#   샘플은 pixelfx로 뽑은 시트 (색만 로봇 회로 빛 청록으로 바꿈):
#     tracer : projectiles/bullet-tracer --sheet --opts '{"palette":["#04161c","#073a46","#0b6b7c","#0fa3b8","#22d3ee","#5ee7f7","#a5f3fc","#e0fdff","#ffffff"]}'
#              → assets/sprites/fx/samples/engineer_titan_sr1_tracer_src.png (+ .json) 18칸 200×40, 기준점(머리) 184,18
#     hit    : impacts/hit-spark --sheet --opts '{"palette":["#073a46","#0b6b7c","#0fa3b8","#22d3ee","#7ff0ff","#cffaff","#ffffff"]}'
#              → assets/sprites/fx/samples/engineer_titan_sr1_hit_src.png (+ .json) 16칸 136×80, 기준점(불꽃 자리) 44,64
#     flash  : projectiles/muzzle-pistol --sheet (팔레트는 tracer와 같음) → assets/sprites/fx/samples/engineer_titan_sr1_flash_src.png (+ .json)
#              55칸 96×72 중 앞 4칸(섬광·불티)만, 뒤의 연기·탄피는 안 씀. 총구 = (44, 66 - height 26). 노란 탄피 점은 지움. 원래 크기 그대로
#              (2026-11-14 사용자 요청: 기관포를 쏠 때 총구에 이펙트)
#   tracer·hit은 절반 크기로 (도트 그대로 NEAREST, 기본 기관포 불티와 같은 크기)
# 출력한 칸 크기·기준점은 index.html ENG_GAT_SR_FX
import json
from PIL import Image

S = 'assets/sprites/fx/samples/engineer_titan_sr1_'
OUT = 'assets/sprites/fx/engineer_titan_sr1_gat_fx.webp'


def frames(name, half=True, first=None):
    im = Image.open(S + name + '_src.png').convert('RGBA')
    js = json.load(open(S + name + '_src.json', encoding='utf-8'))
    fr = [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + f['frame']['w'], f['frame']['y'] + f['frame']['h'])) for f in js['frames'][:first]]
    px, py = js['meta']['pixelfx']['pivot']
    if not half:
        return fr, (px, py)
    return [f.resize((f.width // 2, f.height // 2), Image.NEAREST) for f in fr], (px // 2, py // 2)


def no_brass(f):   # 노란 탄피 점 지움 (청록 팔레트엔 노랑이 없음)
    px = f.load()
    for y in range(f.height):
        for x in range(f.width):
            r, g, b, a = px[x, y]
            if a and r > 120 and b < r - 40:
                px[x, y] = (0, 0, 0, 0)
    return f


def main():
    tr, tp = frames('tracer')
    ht, hp = frames('hit')
    fl, fp = frames('flash', half=False, first=4)
    fl = [no_brass(f) for f in fl]
    fp = (fp[0], fp[1] - 26)
    W = max(len(tr) * tr[0].width, len(ht) * ht[0].width, len(fl) * fl[0].width)
    fy = tr[0].height + ht[0].height
    sheet = Image.new('RGBA', (W, fy + fl[0].height), (0, 0, 0, 0))
    for i, f in enumerate(fl):
        sheet.paste(f, (i * f.width, fy))
    for i, f in enumerate(tr):
        sheet.paste(f, (i * f.width, 0))
    for i, f in enumerate(ht):
        sheet.paste(f, (i * f.width, tr[0].height))
    sheet.save(OUT, 'WEBP', lossless=True)
    print(json.dumps({'tracer': {'y': 0, 'w': tr[0].width, 'h': tr[0].height, 'n': len(tr), 'ox': tp[0], 'oy': tp[1]},
                      'hit': {'y': tr[0].height, 'w': ht[0].width, 'h': ht[0].height, 'n': len(ht), 'ox': hp[0], 'oy': hp[1]},
                      'flash': {'y': fy, 'w': fl[0].width, 'h': fl[0].height, 'n': len(fl), 'ox': fp[0], 'oy': fp[1]}}))


if __name__ == '__main__':
    main()

# 기계공 시크릿 레어 최종병기 박격포(어깨 장포신) 이펙트 → assets/sprites/fx/engineer_titan_sr1_mortar_fx.webp (세 줄)
# 사용: python tools/engineer_titan_sr1_mortar_fx_build.py   (2026-11-14 사용자 설계: 포대에 에너지가 모임 → 발사 섬광 → 날아가는 포탄 없이 맞을 대상 자리에 포격)
#   샘플은 pixelfx로 뽑은 시트, 색은 로봇 회로 빛 청록 (palette ["#04161c","#073a46","#0b6b7c","#0fa3b8","#22d3ee","#7ff0ff","#cffaff","#ffffff"]):
#     charge : arcane/spell-charge --no-actor (48칸 120×86, 빛 구슬 가운데 58,53) — 빛살·티끌이 빨려 들며 고리가 조여드는 구슬. 게임이 충전하는 동안 점점 키움
#     fire   : projectiles/muzzle-shotgun (앞 24칸 160×88, 포구 44, 82-26=56) — 부채꼴 청록 섬광 → 흩어지는 탄 줄기 → 굴러 퍼지는 연기. 원래 크기
#              붉은 탄피 조각은 지움 (2026-11-15: 예전 rail-muzzle은 손바닥용이라 왼쪽이 일직선으로 잘려 보였음)
#     landzap: volt/discharge (23칸 1000×528, 몸 가운데 500,200) — 몸에서 터진 굵은 번개 줄기가 사방 바닥에 꽂힘. 착지 충격용, 절반 크기로
#              → 별도 파일 assets/sprites/fx/engineer_titan_sr1_land_fx.webp (한 줄로 넣으면 너무 넓어서)
#     tip    : volt/rail-tip (sparks ["#ffffff","#cffaff","#7ff0ff","#22d3ee"], 12칸 240×480, 포구 80,240) — 둥근 빛 머리 + 앞으로 뻗는 굵은 번개 갈래.
#              발사 순간 포구에 겹쳐 화려하게 (2026-11-15 사용자 요청). 절반 크기로
#     blast  : explosions/plasma-explosion (accent도 청록, 앞 40칸 224×200, 가운데 112,100) — 흰 섬광 → 빛 구슬 → 충격 고리·번개. 원래 크기
#   샘플 = assets/sprites/fx/samples/engineer_titan_sr1_{mcharge,mfire,mblast}_src.png + .json
# 출력한 칸 크기·기준점은 index.html ENG_TITAN_SR_MORTAR_FX
import json
from PIL import Image

S = 'assets/sprites/fx/samples/engineer_titan_sr1_'
OUT = 'assets/sprites/fx/engineer_titan_sr1_mortar_fx.webp'
ROWS = [('mcharge', 48, 1, (58, 53)), ('mfire', 24, 1, (44, 56)), ('mblast', 40, 1, (112, 100)), ('mtip', 12, 2, (80, 240))]   # (샘플, 쓸 칸 수, 줄이는 배수, 기준점)


def no_shell(f):   # 붉은·주황 탄피 조각 지움 (청록·회색 연기만 남김)
    px = f.load()
    for y in range(f.height):
        for x in range(f.width):
            r, g, b, a = px[x, y]
            if a and r > g + 30 and r > b + 30:
                px[x, y] = (0, 0, 0, 0)
    return f


def land():
    im = Image.open(S + 'landzap_src.png').convert('RGBA')
    js = json.load(open(S + 'landzap_src.json', encoding='utf-8'))
    fr = [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + f['frame']['w'], f['frame']['y'] + f['frame']['h'])).resize((500, 264), Image.LANCZOS) for f in js['frames']]
    out = Image.new('RGBA', (500 * len(fr), 264), (0, 0, 0, 0))
    for i, f in enumerate(fr):
        out.paste(f, (i * 500, 0))
    out.save('assets/sprites/fx/engineer_titan_sr1_land_fx.webp', 'WEBP', lossless=True)
    return {'w': 500, 'h': 264, 'n': len(fr), 'ox': 250, 'oy': 100}


def main():
    rows, meta = [], {}
    y = 0
    for name, n, div, (px, py) in ROWS:
        im = Image.open(S + name + '_src.png').convert('RGBA')
        js = json.load(open(S + name + '_src.json', encoding='utf-8'))
        fr = [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + f['frame']['w'], f['frame']['y'] + f['frame']['h'])) for f in js['frames'][:n]]
        if name == 'mfire':
            fr = [no_shell(f) for f in fr]
        if div > 1:
            fr = [f.resize((f.width // div, f.height // div), Image.LANCZOS) for f in fr]
        rows.append(fr)
        meta[name[1:]] = {'y': y, 'w': fr[0].width, 'h': fr[0].height, 'n': len(fr), 'ox': px // div, 'oy': py // div}
        y += fr[0].height
    W = max(len(r) * r[0].width for r in rows)
    sheet = Image.new('RGBA', (W, y), (0, 0, 0, 0))
    for r, (name, *_ ) in zip(rows, ROWS):
        for i, f in enumerate(r):
            sheet.paste(f, (i * f.width, meta[name[1:]]['y']))
    sheet.save(OUT, 'WEBP', lossless=True)
    meta['land'] = land()
    print(json.dumps(meta))


if __name__ == '__main__':
    main()

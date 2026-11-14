# 기계공 시크릿 레어 최종병기 박격포(어깨 장포신) 이펙트 → assets/sprites/fx/engineer_titan_sr1_mortar_fx.webp (세 줄)
# 사용: python tools/engineer_titan_sr1_mortar_fx_build.py   (2026-11-14 사용자 설계: 포대에 에너지가 모임 → 발사 섬광 → 날아가는 포탄 없이 맞을 대상 자리에 포격)
#   샘플은 pixelfx로 뽑은 시트, 색은 로봇 회로 빛 청록 (palette ["#04161c","#073a46","#0b6b7c","#0fa3b8","#22d3ee","#7ff0ff","#cffaff","#ffffff"]):
#     charge : arcane/spell-charge --no-actor (48칸 120×86, 빛 구슬 가운데 58,53) — 빛살·티끌이 빨려 들며 고리가 조여드는 구슬. 게임이 충전하는 동안 점점 키움
#     fire   : volt/rail-muzzle (12칸 200×480, 포구 72,240) — 포구에서 빛이 터지고 세로 빛 기둥이 가르는 에너지포 섬광. 절반 크기로
#     blast  : explosions/plasma-explosion (accent도 청록, 앞 40칸 224×200, 가운데 112,100) — 흰 섬광 → 빛 구슬 → 충격 고리·번개. 원래 크기
#   샘플 = assets/sprites/fx/samples/engineer_titan_sr1_{mcharge,mfire,mblast}_src.png + .json
# 출력한 칸 크기·기준점은 index.html ENG_TITAN_SR_MORTAR_FX
import json
from PIL import Image

S = 'assets/sprites/fx/samples/engineer_titan_sr1_'
OUT = 'assets/sprites/fx/engineer_titan_sr1_mortar_fx.webp'
ROWS = [('mcharge', 48, 1, (58, 53)), ('mfire', 12, 2, (72, 240)), ('mblast', 40, 1, (112, 100))]   # (샘플, 쓸 칸 수, 줄이는 배수, 기준점)


def main():
    rows, meta = [], {}
    y = 0
    for name, n, div, (px, py) in ROWS:
        im = Image.open(S + name + '_src.png').convert('RGBA')
        js = json.load(open(S + name + '_src.json', encoding='utf-8'))
        fr = [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + f['frame']['w'], f['frame']['y'] + f['frame']['h'])) for f in js['frames'][:n]]
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
    print(json.dumps(meta))


if __name__ == '__main__':
    main()

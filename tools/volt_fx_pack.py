# 전격술사 이펙트 묶기: pixelfx가 구운 시트(records/volt/<이름>/<이름>.png + .json) → 게임 시트 assets/sprites/fx/volt/<이름>.webp + 칸 정보 표
# 사용: node tools/volt_fx_build.mjs <pixelfx 폴더>  다음에  python tools/volt_fx_pack.py <pixelfx 폴더>
# - 색에 곱해진 투명도를 되돌림 (빛 번짐이 하늘색 반투명이 되게)
# - 모든 프레임에 공통으로 빈 가장자리를 잘라 냄 (기준점은 잘라 낸 만큼 옮김)
# - 칸 정보는 assets/sprites/fx/volt/volt_fx.json: { 이름: { src, w, h, cols, n, fps, loop, ax, ay } } — 칸 i는 (i % cols, i // cols)
#   ax, ay = 기준점 (칸 안 px): 발·손바닥·포 왼쪽 끝 등 효과마다 다름 (tools/volt_fx/<이름>.js 맨 위 설명)
import json, os, sys
import numpy as np
from PIL import Image

OUT = 'assets/sprites/fx/volt'


def load(pfx, name):
    vd = os.path.join(pfx, 'records', '_variants', name, 'volt')
    if os.path.isdir(vd):   # 옵션만 바꿔 구운 것: 안에 원래 효과 이름 폴더 하나
        base = os.listdir(vd)[0]
        d = os.path.join(vd, base)
        return Image.open(os.path.join(d, base + '.png')), json.load(open(os.path.join(d, base + '.json'), encoding='utf-8'))
    d = os.path.join(pfx, 'records', 'volt', name)
    return Image.open(os.path.join(d, name + '.png')), json.load(open(os.path.join(d, name + '.json'), encoding='utf-8'))


def main():
    pfx = sys.argv[1]
    names = sorted(n for n in os.listdir(os.path.join(pfx, 'records', 'volt')) if os.path.isdir(os.path.join(pfx, 'records', 'volt', n)))
    vroot = os.path.join(pfx, 'records', '_variants')
    names += sorted(os.listdir(vroot)) if os.path.isdir(vroot) else []
    os.makedirs(OUT, exist_ok=True)
    table = {}
    for name in names:
        im, js = load(pfx, name)
        a = np.array(im.convert('RGBA')).astype(float)
        # pixelfx 시트는 색에 투명도가 곱해져 있음 (빛 번짐 = 거의 검은색 + 낮은 투명도) → 게임은 보통 덮어 그리기라 검은 안개가 됨. 색을 나눠 되돌림
        al = a[..., 3:]
        a[..., :3] = np.where(al > 0, np.minimum(255, a[..., :3] * 255 / np.maximum(al, 1)), 0)
        a = a.round().astype(np.uint8)
        m = js['meta']['pixelfx']
        w, h = m['frameSize']
        frames = [a[f['frame']['y']:f['frame']['y'] + h, f['frame']['x']:f['frame']['x'] + w] for f in js['frames']]
        # 이어 붙이는 몸통은 가로를 자르지 않음 (120px 주기)
        al = np.max([f[..., 3] for f in frames], axis=0) > 0
        ys, xs = np.where(al)
        tile = name.startswith('rail-body')
        x0, x1 = (0, w) if tile else (max(0, xs.min() - 1), min(w, xs.max() + 2))
        y0, y1 = max(0, ys.min() - 1), min(h, ys.max() + 2)
        cw, ch, n = x1 - x0, y1 - y0, len(frames)
        cols = max(1, min(n, int(np.ceil(np.sqrt(n * ch / cw)))))
        while cols * cw > 16000: cols -= 1
        rows = (n + cols - 1) // cols
        sheet = np.zeros((rows * ch, cols * cw, 4), np.uint8)
        for i, f in enumerate(frames):
            sheet[(i // cols) * ch:(i // cols + 1) * ch, (i % cols) * cw:(i % cols + 1) * cw] = f[y0:y1, x0:x1]
        path = f'{OUT}/{name}.webp'
        Image.fromarray(sheet, 'RGBA').save(path, 'WEBP', lossless=True)
        ax, ay = int(m["pivot"][0] - x0), int(m["pivot"][1] - y0)
        table[name] = dict(src=path, w=int(cw), h=int(ch), cols=int(cols), n=n, fps=m['fps'], loop=m['loop'], ax=ax, ay=ay)
        print(f'{name}: {n}칸 {cw}x{ch} ({cols}열) 기준점 ({ax}, {ay})  {os.path.getsize(path) // 1024}KB')
    json.dump(table, open(f'{OUT}/volt_fx.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()

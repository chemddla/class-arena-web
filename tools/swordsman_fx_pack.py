# 검사 이펙트 묶기: pixelfx가 구운 시트(records/swordsman/<이름>/<이름>.png + .json) → 게임 시트 assets/sprites/fx/sword/<이름>.webp + 칸 정보
# 사용: node tools/swordsman_fx_build.mjs <pixelfx 폴더>  다음에  python tools/swordsman_fx_pack.py <pixelfx 폴더>
# - 색에 곱해진 투명도를 되돌림 (빛 번짐이 흰 반투명이 되게, 전격술사 묶기와 같음)
# - 모든 프레임에 공통으로 빈 가장자리를 잘라 냄 (기준점 = 칼자루 끝은 잘라 낸 만큼 옮김)
# - 칸 정보는 화면에 찍고 assets/sprites/fx/sword/sword_fx.json에도 씀: index.html의 SWORD_FXS 표를 이 값으로 바꿀 것
#   [칸 너비, 높이, 열 수, 프레임 수, fps, 기준점 x, y]
import json, os, sys
import numpy as np
from PIL import Image

OUT = 'assets/sprites/fx/sword'


def main():
    pfx = sys.argv[1]
    root = os.path.join(pfx, 'records', 'swordsman')
    names = sorted(n for n in os.listdir(root) if os.path.isdir(os.path.join(root, n)))
    os.makedirs(OUT, exist_ok=True)
    table = {}
    for name in names:
        d = os.path.join(root, name)
        im = Image.open(os.path.join(d, name + '.png'))
        js = json.load(open(os.path.join(d, name + '.json'), encoding='utf-8'))
        a = np.array(im.convert('RGBA')).astype(float)
        al = a[..., 3:]
        a[..., :3] = np.where(al > 0, np.minimum(255, a[..., :3] * 255 / np.maximum(al, 1)), 0)
        a = a.round().astype(np.uint8)
        m = js['meta']['pixelfx']
        w, h = m['frameSize']
        frames = [a[f['frame']['y']:f['frame']['y'] + h, f['frame']['x']:f['frame']['x'] + w] for f in js['frames']]
        alm = np.max([f[..., 3] for f in frames], axis=0) > 0
        ys, xs = np.where(alm)
        x0, x1 = max(0, xs.min() - 1), min(w, xs.max() + 2)
        y0, y1 = max(0, ys.min() - 1), min(h, ys.max() + 2)
        cw, ch, n = x1 - x0, y1 - y0, len(frames)
        cols = max(1, min(n, int(np.ceil(np.sqrt(n * ch / cw)))))
        rows = (n + cols - 1) // cols
        sheet = np.zeros((rows * ch, cols * cw, 4), np.uint8)
        for i, f in enumerate(frames):
            sheet[(i // cols) * ch:(i // cols + 1) * ch, (i % cols) * cw:(i % cols + 1) * cw] = f[y0:y1, x0:x1]
        path = f'{OUT}/{name}.webp'
        Image.fromarray(sheet, 'RGBA').save(path, 'WEBP', lossless=True)
        ax, ay = int(m['pivot'][0] - x0), int(m['pivot'][1] - y0)
        table[name] = [int(cw), int(ch), int(cols), n, m['fps'], ax, ay]
        print(f"      '{name}': {table[name]},   // {os.path.getsize(path) // 1024}KB")
    json.dump(table, open(f'{OUT}/sword_fx.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()

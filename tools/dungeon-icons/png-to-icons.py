# pxl로 그린 PNG(out/sprites)를 pixel-icons.js의 ICONS 형식(팔레트 글자 줄)으로 바꿔 new-icons.js에 씀
import json, os, re, sys
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1] if len(sys.argv) > 1 else 'icons'  # icons | redesign
src = open(os.path.join(here, name + '.px.js'), encoding='utf-8').read()
pal = {v.lower(): k for k, v in re.findall(r"(\w): '(#[0-9a-fA-F]{6})'", src[:src.index('})')])}
names = re.findall(r"^sprite\('(\w+)'", src, re.M)
out = [f'// tools/dungeon-icons/{name}.px.js에서 png-to-icons.py로 만든 파일 (직접 고치지 말고 px.js를 고친 뒤 다시 만들기)', 'module.exports = {']
for n in names:
    im = Image.open(os.path.join(here, 'out', 'sprites', n + '.png')).convert('RGBA')
    rows = []
    for y in range(im.height):
        row = ''
        for x in range(im.width):
            r, g, b, a = im.getpixel((x, y))
            row += '.' if a < 128 else pal['#%02x%02x%02x' % (r, g, b)]
        rows.append(row)
    assert all(len(r) == 16 for r in rows), (n, im.size)
    out.append(f'  {n}: [\n' + ',\n'.join("    '" + r + "'" for r in rows) + '\n  ],')
out.append('};')
open(os.path.join(here, 'new-icons.js' if name == 'icons' else name + '-icons.js'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('ok', names)

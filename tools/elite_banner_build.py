# 엘리트 보스 배너 그림: 보스별 맵(assets/maps/elite_*.webp) 윗부분(왕좌·깃발 띠)을 잘라 작은 배너로
# 탭을 열 때 맵 10장(1.5MB) 대신 배너 10장만 받게 (index.html ELITE_BANNER_SRC)
# 실행: python tools/elite_banner_build.py
import glob
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'banners')
W, H = 720, 210          # 배너 크기 (화면에서는 가로 꽉 채워 object-fit: cover)
TOP = 6                  # 맵 맨 위 테두리 조금 건너뜀

os.makedirs(OUT, exist_ok=True)
for src in sorted(glob.glob(os.path.join(ROOT, 'assets', 'maps', 'elite_*.webp'))):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    band = round(w * H / W)                  # 같은 비율로 자를 높이
    crop = im.crop((0, TOP, w, TOP + band)).resize((W, H), Image.LANCZOS)
    name = os.path.basename(src)
    dst = os.path.join(OUT, name)
    crop.save(dst, 'WEBP', quality=78, method=6)
    print(name, os.path.getsize(dst), 'B')

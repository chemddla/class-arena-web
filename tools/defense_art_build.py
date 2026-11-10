# 💎 수정 방어전 그림 → assets/maps/crystal_defense.webp · assets/sprites/fx/defense_towers.png · assets/sprites/fx/defense_crystal.png
# 사용: python tools/defense_art_build.py [미리보기 폴더]
#
# 모두 코드로 찍는 도트 그림. 작법 (pixelfx · 도트 기본기):
#  - 색 단계는 색조를 섞음 (그림자는 푸르고 보랏빛, 밝은 곳은 노랗게) · 빛은 늘 왼쪽 위
#  - 테두리는 검정 한 가지가 아니라 맞닿은 재질의 가장 어두운 색 (아래쪽 테두리가 더 어두움)
#  - 바위·흙·절벽은 높이 노이즈로 빛을 계산 (요철) · 그림자는 오른쪽 아래로 떨어짐
#  - 빛 웅덩이(수정·화로·횃불)는 단계로 끊고 바이어 디더로 섞음
# - 맵: 720×450 도트 (월드 2880×1800의 1/4). 게임은 다듬기 없이 4배.
#   길·동굴·받침돌·수정 좌표는 index.html의 DEFENSE_LANES · defenseMakeSlots · DEFENSE_CRYSTAL과 같음 (월드 ÷ 4).
# - 시설 시트: 칸 36×52, 가로 12칸 = 단계(1~3)마다 [평소 A, 평소 B, 공격 A, 공격 B],
#   세로 6줄 = 화살탑 · 마법탑 · 서리탑 · 방벽 · 덫 · 치유 토템.
#   방벽은 공격 칸 = 부서진 모습, 덫은 공격 칸 = 터진 뒤(빈 덫). 발 위치 = 칸 (18, 49). 게임에서 3배.
# - 수정 시트: 칸 32×60, 가로 6프레임(빛 흐름), 세로 3줄 = 성함 · 금 감(70% 아래) · 크게 금 감(30% 아래). 게임에서 3배.
import math, os, random, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_MAP = os.path.join(ROOT, 'assets/maps/crystal_defense.webp')
OUT_TOWERS = os.path.join(ROOT, 'assets/sprites/fx/defense_towers.png')
OUT_CRYSTAL = os.path.join(ROOT, 'assets/sprites/fx/defense_crystal.png')
PREVIEW = sys.argv[1] if len(sys.argv) > 1 else None
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def C(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def R(*hs):
    return [C(h) for h in hs]


# 색조를 섞은 단계 (어두움 → 밝음)
STONE = R('#1b1d2c', '#2b2f42', '#41475c', '#5b6377', '#7a8396', '#9ea7b6', '#c6cdd6', '#e9edf1')
WARMSTONE = R('#231d26', '#372d33', '#4d4144', '#685a57', '#87776d', '#a8977f', '#c9b99a')
WOOD = R('#24140f', '#3b2115', '#58331c', '#784824', '#9a612f', '#bd7f40', '#dca35a')
AMBER = R('#5a1f0c', '#93370f', '#c95a14', '#ec8a1d', '#f8b93c', '#fde382')
CLOTH_R = R('#3b0f1c', '#6b1526', '#a2232f', '#d2413a', '#f0754f')
PURPLE = R('#1a0c3a', '#33156d', '#5226a6', '#7b45d8', '#a77bf2', '#d2c1ff', '#ffffff')
ICE = R('#10224a', '#173d7a', '#1f63ad', '#3592d8', '#68c1f0', '#a8e4ff', '#e3f8ff', '#ffffff')
GREEN = R('#062b25', '#0a4a39', '#0f704e', '#1b9a63', '#45c47f', '#94e8b0', '#e0ffe9')
IRON = R('#121319', '#22242d', '#373a46', '#525866', '#77808e', '#a3abb6', '#d5dae0')
GOLD = R('#4a2508', '#7a4210', '#ad6a18', '#d99a27', '#f2c84a', '#fff0a6')
RUNEC = R('#0b2c44', '#145a80', '#1f8fc0', '#38bdf8', '#8fe0ff', '#e2f8ff')
RED = R('#3d0a10', '#7a1418', '#b8261f', '#e5532c', '#ff9248', '#ffd38a')
PAINT_R = C('#b8322a')
PAINT_T = C('#2aa198')


def darken(c, k=0.45, shift=(10, 0, 30)):
    """테두리·그림자용: 어둡게 + 푸른 보랏빛으로."""
    return (int(max(0, c[0] * k + shift[0] * (1 - k) * 0.4)), int(max(0, c[1] * k + shift[1] * (1 - k) * 0.4)),
            int(max(0, c[2] * k + shift[2] * (1 - k) * 0.6)), 255)


# ---------------------------------------------------------------- 스프라이트 도구
class Spr:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), np.uint8)

    def px(self, x, y, c):
        x, y = int(math.floor(x + 0.5)), int(math.floor(y + 0.5))
        if c is not None and 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = c

    def get(self, x, y):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            return tuple(int(v) for v in self.a[y, x])
        return (0, 0, 0, 0)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.px(x, y, c)

    def line(self, x0, y0, x1, y1, c):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            t = i / max(1, n)
            self.px(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, c)

    def cyl(self, x0, x1, y0, y1, pal, hi=0.22):
        """세로 원통 (기둥·통나무·탑 몸통): 왼쪽이 밝고 오른쪽 끝 어두움, 가장 밝은 줄 하나."""
        n = len(pal)
        w = max(1, x1 - x0)
        for x in range(int(x0), int(x1) + 1):
            u = (x - x0) / w
            lum = 1 - abs(u - hi) * 1.35 if u > hi else 0.75 + u / hi * 0.25
            lum = max(0.05, min(0.999, lum * 0.9 + 0.05))
            k = int(lum * (n - 1) + 0.5)
            self.rect(x, y0, x, y1, pal[max(0, min(n - 1, k))])

    def disc(self, cx, cy, r, pal, ry=None, light=(-0.6, -0.75), dither=True):
        n = len(pal)
        ry = ry or r
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / ry
                d = dx * dx + dy * dy
                if d > 1:
                    continue
                z = math.sqrt(1 - d)
                lum = max(0, (dx * light[0] + dy * light[1]) * 0.55 + z * 0.6)
                f = min(0.999, lum) * (n - 1)
                k = int(f)
                if dither and 0 <= y < self.h and 0 <= x < self.w and (f - k) > BAYER[y & 3, x & 3]:
                    k += 1
                self.px(x, y, pal[min(n - 1, k)])

    def outline(self, strong=False):
        """재질 테두리: 맞닿은 칸의 색을 어둡게 (아래·오른쪽은 더 어둡게)."""
        a = self.a
        op = a[:, :, 3] > 0
        out = a.copy()
        H, W = op.shape
        for y in range(H):
            for x in range(W):
                if op[y, x]:
                    continue
                best = None
                for dx, dy, k in ((0, 1, 0.42), (1, 0, 0.42), (0, -1, 0.3), (-1, 0, 0.36)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < W and 0 <= yy < H and op[yy, xx]:
                        c = darken(tuple(int(v) for v in a[yy, xx]), k if not strong else k * 0.7)
                        if best is None or sum(c[:3]) < sum(best[:3]):
                            best = c
                if best:
                    out[y, x] = best
        self.a = out

    def ao(self, y, x0, x1, c=None):
        """바닥 닿는 곳 그림자 한 줄."""
        for x in range(int(x0), int(x1) + 1):
            if self.a[y, x, 3]:
                self.a[y, x] = darken(tuple(int(v) for v in self.a[y, x]), 0.7)


def bricks(s, x0, x1, y0, y1, pal, bh=3, bw=5, seed=1, mossy=False):
    """벽돌 면: 벽돌마다 한 단씩 다른 밝기 + 위왼쪽 밝은 점 + 줄눈."""
    rnd = random.Random(seed)
    n = len(pal)
    for by in range(y0, y1 + 1, bh):
        off = (bw // 2) if ((by - y0) // bh) % 2 else 0
        for bx in range(x0 - off, x1 + 1, bw):
            # 원통처럼 가장자리 어둡게
            mid = (bx + bw / 2 - x0) / max(1, x1 - x0)
            base = 4 if mid < 0.3 else 3 if mid < 0.7 else 2
            base = max(1, min(n - 2, base + rnd.choice((-1, 0, 0, 0, 1))))
            for yy in range(by, min(by + bh - 1, y1) + 1):
                for xx in range(max(bx, x0), min(bx + bw - 2, x1) + 1):
                    s.px(xx, yy, pal[base])
            s.px(max(bx, x0), by, pal[min(n - 1, base + 1)])
            if mossy and rnd.random() < 0.18:
                s.px(max(bx, x0) + 1, by + bh - 2, C('#4c7a35'))
            # 줄눈
            for xx in range(max(bx, x0), min(bx + bw - 1, x1) + 1):
                s.px(xx, min(by + bh - 1, y1), pal[1])
            s.px(min(bx + bw - 1, x1), by, pal[1]); s.px(min(bx + bw - 1, x1), by + 1, pal[1])


def plinth(s, lv, trim=None):
    """둥근 돌 받침 (3/4 시점): 위 면 타원 + 앞 면 벽돌 + 바닥 그림자."""
    rx = 12 + lv
    cy, ry, bot = 41, 3, 48
    for y in range(cy, bot + 1):
        for x in range(18 - rx, 18 + rx + 1):
            s.px(x, y, STONE[3])
    bricks(s, 18 - rx, 18 + rx, cy + 1, bot, STONE, bh=3, bw=5, seed=lv * 13, mossy=True)
    # 앞 면 아래 둥글게 깎기
    for x in range(18 - rx, 18 + rx + 1):
        dx = (x - 18) / rx
        cut = int(round(ry * math.sqrt(max(0, 1 - dx * dx))))
        for y in range(bot + 1, bot + 1 + cut):
            s.px(x, y, STONE[2] if dx < 0.3 else STONE[1])
    # 위 면
    for y in range(cy - ry, cy + ry + 1):
        for x in range(18 - rx, 18 + rx + 1):
            dx, dy = (x - 18) / rx, (y - cy) / ry
            if dx * dx + dy * dy <= 1:
                k = 6 if dx < -0.2 and dy < 0 else 5
                s.px(x, y, STONE[k])
    if trim:
        for x in range(18 - rx + 1, 18 + rx):
            dx = (x - 18) / rx
            yy = cy + int(round(ry * math.sqrt(max(0, 1 - dx * dx)))) + 1
            s.px(x, yy, trim[4] if dx < -0.3 else trim[3] if dx < 0.4 else trim[2])
            if lv >= 3:
                s.px(x, yy + 3, trim[3] if dx < 0 else trim[2])
    # 풀포기 (받침 아래)
    for x in (18 - rx + 1, 18 - rx + 4, 18 + rx - 2):
        s.px(x, bot + 1, C('#3e6b33')); s.px(x - 1, bot + 1, C('#2c5230')); s.px(x, bot, C('#5d8f3e'))


# ---------------------------------------------------------------- 시설
def banner(s, x, y, w, h, pal, wave):
    """천 깃발: 물결(wave)로 아래 끝이 흔들림 · 접힌 그림자."""
    for i in range(h):
        sway = int(round(math.sin(i * 0.5 + wave * math.pi) * (i / h) * 1.5))
        for j in range(w):
            k = 3 if j < w * 0.35 else 2 if j < w * 0.8 else 1
            if (i + wave * 2) % 5 == 0:
                k = max(0, k - 1)
            s.px(x + j + sway, y + i, pal[k])
    # 아래 끝 V
    for j in range(w):
        if abs(j - w / 2 + 0.5) < w / 2 - 1:
            s.px(x + j + int(round(math.sin(h * 0.5 + wave * math.pi) * 1.5)), y + h + (1 if abs(j - w / 2 + 0.5) > 1 else 0), pal[1])


def arrow_tower(lv, f):
    s = Spr(36, 52)
    fire, alt = f >= 2, f % 2
    plinth(s, lv, trim=GOLD if lv >= 3 else IRON if lv >= 2 else None)
    if lv == 1:
        # 통나무 망루 + 천 지붕
        for x in (9, 25):
            s.cyl(x, x + 2, 18, 40, WOOD)
        s.cyl(14, 15, 20, 39, WOOD[:5]); s.cyl(20, 21, 20, 39, WOOD[:5])
        s.line(11, 23, 24, 37, WOOD[2]); s.line(24, 23, 11, 37, WOOD[3])
        s.line(11, 24, 24, 38, WOOD[1])
        s.rect(10, 31, 25, 31, WOOD[4])  # 가로 버팀
        # 판자 바닥 (위 면)
        s.rect(6, 16, 29, 19, WOOD[5]); s.rect(6, 19, 29, 20, WOOD[3])
        for x in range(7, 29, 3):
            s.px(x, 17, WOOD[4]); s.px(x, 18, WOOD[4])
        s.rect(6, 21, 29, 21, WOOD[1])
        # 천 지붕 (기둥 2개 위)
        s.cyl(7, 7, 5, 16, WOOD[:5]); s.cyl(28, 28, 5, 16, WOOD[:5])
        for y in range(2, 8):
            half = 13 - (7 - y) * 0 + (y - 2) * 0.6
            for x in range(int(18 - half), int(18 + half) + 1):
                sway = 1 if (alt and y == 7 and x % 3 == 0) else 0
                k = 4 if x < 16 else 3 if x < 24 else 2
                if y == 7:
                    k = 2 if (x // 2) % 2 else 3
                s.px(x, y + sway, AMBER[k])
        top = 15
    else:
        y0 = 22 if lv == 2 else 16
        s.cyl(9, 27, y0, 40, STONE[1:7])
        bricks(s, 10, 26, y0 + 2, 40, STONE, bh=3, bw=5, seed=lv * 7, mossy=lv == 2)
        # 화살 구멍 (어둠 + 빛 가장자리)
        s.rect(17, y0 + 6, 18, y0 + 11, C('#0d0e15')); s.px(16, y0 + 6, STONE[5])
        if lv >= 3:
            s.rect(17, y0 + 7, 18, y0 + 8, AMBER[4] if not alt else AMBER[3])  # 창문 불빛
        # 흉벽
        s.rect(7, y0 - 3, 29, y0 - 1, STONE[4]); s.rect(7, y0 - 3, 29, y0 - 3, STONE[6])
        for x in range(7, 30, 4):
            s.rect(x, y0 - 6, x + 1, y0 - 4, STONE[5] if x < 18 else STONE[4]); s.px(x, y0 - 6, STONE[6])
        if lv >= 3:
            for x in range(7, 30):
                s.px(x, y0 - 1, GOLD[4] if x < 15 else GOLD[3] if x < 25 else GOLD[2])
        s.rect(7, y0, 29, y0, STONE[1])
        # 매달린 깃발
        banner(s, 15, y0 + 13, 6, 9 if lv == 2 else 12, CLOTH_R if lv == 2 else [CLOTH_R[0], CLOTH_R[1], GOLD[3], GOLD[4]], alt)
        if lv >= 3:
            s.px(17, y0 + 16, GOLD[5]); s.px(18, y0 + 17, GOLD[5])
        top = y0 - 4
    # 노포 (위)
    by = top - 3
    s.rect(11, by + 1, 25, by + 2, WOOD[4]); s.rect(11, by + 3, 25, by + 3, WOOD[2])
    s.rect(16, by + 3, 19, by + 5, WOOD[3])
    bow = GOLD if lv >= 3 else IRON
    pull = 0 if fire else 1
    if not fire or f == 3:
        s.line(9, by - 4, 13, by + 1, bow[5]); s.line(27, by - 4, 23, by + 1, bow[3])
        s.line(9, by - 4, 17 - pull * 2, by + 1, C('#efe6cf')); s.line(27, by - 4, 17 - pull * 2, by + 1, C('#efe6cf'))
    else:
        s.line(9, by - 5, 12, by + 1, bow[5]); s.line(27, by - 5, 24, by + 1, bow[3])
        s.line(9, by - 5, 27, by - 5, C('#efe6cf'))
    if not fire:
        for k in range(2 if lv >= 3 else 1):
            yy = by - k * 2
            s.rect(16, yy, 30, yy, IRON[5]); s.px(31, yy, IRON[6]); s.px(30, yy - 1, IRON[4]); s.px(30, yy + 1, IRON[3])
            s.px(15, yy - 1, C('#f2f2f2')); s.px(15, yy + 1, C('#f2f2f2'))
    elif f == 2:
        # 쏜 순간: 섬광 + 연기
        for i, c in enumerate((AMBER[5], AMBER[4], AMBER[3], AMBER[2])):
            s.px(31 + i, by, c)
        for (dx, dy, c) in ((32, -1, AMBER[4]), (32, 1, AMBER[4]), (33, -2, AMBER[3]), (33, 2, AMBER[3]), (34, -3, AMBER[2]), (34, 3, AMBER[2])):
            s.px(dx, by + dy, c)
    else:
        for (dx, dy, c) in ((30, -1, STONE[6]), (31, 0, STONE[5]), (32, -2, STONE[4]), (29, 1, STONE[5])):
            s.px(dx, by + dy, c)
    s.outline()
    return s


def magic_tower(lv, f):
    s = Spr(36, 52)
    fire, alt = f >= 2, f % 2
    plinth(s, lv, trim=GOLD if lv >= 3 else PURPLE if lv >= 2 else None)
    y_top = 19 - (lv - 1) * 2
    # 오벨리스크 (가늘어지는 기둥, 면 두 개)
    for y in range(y_top, 41):
        t = (y - y_top) / (41 - y_top)
        half = 2.5 + t * 4.5
        for x in range(int(18 - half), int(18 + half) + 1):
            u = (x - (18 - half)) / (2 * half)
            k = 6 if u < 0.15 else 5 if u < 0.5 else 3 if u < 0.85 else 2
            s.px(x, y, STONE[k])
    s.px(18, y_top - 1, STONE[6]); s.px(18, y_top - 2, STONE[5])
    # 새긴 룬 (빛남)
    glow = PURPLE[5] if (fire or alt) else PURPLE[4]
    for i, y in enumerate(range(y_top + 4, 39, 4)):
        s.px(17 + (i % 2), y, glow); s.px(17, y + 1, PURPLE[3]); s.px(19, y + 1, PURPLE[3])
    if lv >= 2:
        # 돌 고리 받침
        for a in range(24):
            ang = a * math.pi / 12
            x, y = 18 + math.cos(ang) * 9, y_top - 9 + math.sin(ang) * 9
            if 0.2 < ang < 2.9:
                continue  # 아래 반쪽은 기둥 뒤
            s.px(x, y, (GOLD if lv >= 3 else STONE)[5 if math.cos(ang) < 0 else 3])
        s.line(14, y_top + 1, 10, y_top - 6, (GOLD if lv >= 3 else STONE)[4]); s.line(22, y_top + 1, 26, y_top - 6, (GOLD if lv >= 3 else STONE)[3])
    r = 4 if lv < 3 else 5
    bob = -1 if alt else 0
    oy = y_top - 9 + bob
    pal = PURPLE[1:] if fire else PURPLE[:6]
    s.disc(18, oy, r + (1 if f == 2 else 0), pal)
    # 구슬 안 소용돌이
    for i in range(5):
        ang = i * 1.3 + alt * 0.6
        s.px(18 + math.cos(ang) * (r - 2) * 0.7, oy + math.sin(ang) * (r - 2) * 0.7, PURPLE[5])
    s.px(16, oy - 2, PURPLE[6])
    if fire:
        rr = r + (4 if f == 2 else 6)
        for a in range(12):
            ang = a * math.pi / 6 + (0.26 if f == 3 else 0)
            s.px(18 + math.cos(ang) * rr, oy + math.sin(ang) * rr, PURPLE[5] if f == 2 else PURPLE[3])
    if lv >= 3:
        for a in (0.4, 2.5, 4.5):
            ang = a + alt * 0.5 + (1 if fire else 0)
            x, y = 18 + math.cos(ang) * (r + 7), oy + math.sin(ang) * (r + 3)
            s.px(x, y, GOLD[5]); s.px(x + 1, y, GOLD[3])
    s.outline()
    return s


def frost_tower(lv, f):
    s = Spr(36, 52)
    fire, alt = f >= 2, f % 2
    plinth(s, lv, trim=GOLD if lv >= 3 else ICE if lv >= 2 else None)
    # 받침 위 눈
    for x in range(8, 29):
        if (x * 7) % 5 < 3:
            s.px(x, 39, ICE[6]); s.px(x, 40, ICE[5])

    def shard(cx, top, bottom, half, lean=0):
        for y in range(top, bottom + 1):
            t = (y - top) / max(1, bottom - top)
            w = half * min(1, t * 2.6)
            ox = lean * (1 - t)
            for x in range(int(cx + ox - w), int(cx + ox + w) + 1):
                u = (x - (cx + ox - w)) / max(1, 2 * w)
                k = 6 if u < 0.2 else 5 if u < 0.45 else 3 if u < 0.75 else 2
                if fire:
                    k = min(7, k + 1)
                s.px(x, y, ICE[k])
            if w >= 2:
                s.px(cx + ox - w + 1, y, ICE[7] if (y + alt) % 6 == 0 else ICE[6])

    main_top = 12 - (lv - 1) * 3
    shard(12, 25 - lv, 41, 2.6, -2)
    shard(24, 27 - lv, 41, 2.6, 2)
    if lv >= 2:
        shard(8, 31, 41, 1.6, -2)
        shard(28, 30, 41, 1.6, 2)
    shard(18, main_top, 41, 4.2)
    if lv >= 3:
        for a in range(20):
            ang = a * math.pi / 10 + alt * 0.15
            x, y = 18 + math.cos(ang) * 10, main_top - 2 + math.sin(ang) * 3
            if math.sin(ang) > 0.3:
                continue
            s.px(x, y, ICE[6] if math.cos(ang) < 0 else ICE[4])
        s.px(18, main_top - 7, ICE[7]); s.px(17, main_top - 7, ICE[5]); s.px(19, main_top - 7, ICE[5]); s.px(18, main_top - 8, ICE[5]); s.px(18, main_top - 6, ICE[5])
    # 반짝임
    sp = [(9, main_top + 6), (27, main_top + 10), (15, main_top + 1), (23, main_top + 15)]
    for i, (x, y) in enumerate(sp):
        if fire or (i + alt) % 2 == 0:
            c = ICE[7]
            s.px(x, y, c)
            if fire:
                s.px(x - 1, y, ICE[5]); s.px(x + 1, y, ICE[5]); s.px(x, y - 1, ICE[5]); s.px(x, y + 1, ICE[5])
    s.outline()
    return s


def wall_seg(lv, f):
    s = Spr(36, 52)
    broken, alt = f >= 2, f % 2
    if broken:
        rnd = random.Random(lv * 7 + 1)
        pal = WOOD if lv == 1 else STONE
        for _ in range(18):
            x, y = rnd.randint(9, 26), rnd.randint(40, 47)
            s.disc(x, y, rnd.choice((1.6, 2.2, 2.8)), pal[1:6])
        if lv == 1:
            s.line(8, 45, 19, 37, WOOD[4]); s.line(8, 46, 19, 38, WOOD[2])
            s.line(20, 38, 28, 46, WOOD[3])
        else:
            s.rect(11, 34, 17, 40, STONE[4]); s.rect(11, 34, 17, 34, STONE[6])
        # 먼지
        if alt:
            for (x, y) in ((8, 38), (27, 36), (14, 33)):
                s.px(x, y, WARMSTONE[5])
        s.outline()
        return s
    x0, x1, top = 13, 23, 7
    if lv == 1:
        for i, x in enumerate(range(x0, x1 + 1, 3)):
            h = top + (i % 2) * 2
            s.cyl(x, x + 2, h, 48, WOOD)
            s.px(x + 1, h - 1, WOOD[5]); s.px(x + 1, h - 2, WOOD[6]); s.px(x, h - 1, WOOD[3])
        for y in (14, 36):
            s.rect(x0 - 1, y, x1 + 2, y, C('#b49a6a')); s.rect(x0 - 1, y + 1, x1 + 2, y + 1, C('#7d6845'))
    else:
        # 위 면 + 앞 면
        s.rect(x0, top, x1, top + 3, STONE[6]); s.rect(x0, top, x0 + 3, top + 3, STONE[7])
        s.rect(x0, top + 4, x1, 48, STONE[3])
        bricks(s, x0, x1, top + 4, 48, STONE, bh=4, bw=6, seed=lv * 31, mossy=True)
        for y in range(top - 3, top):
            for x in (x0, x0 + 4, x0 + 8):
                s.rect(x, y, x + 2, y, STONE[6] if x < 18 else STONE[5])
        # 이끼 줄기
        for y in range(top + 10, 47, 3):
            s.px(x0, y, C('#4c7a35') if y % 2 else C('#3a6130'))
        if lv >= 3:
            # 쇠판 + 가시 (몬스터 쪽 = 오른쪽)
            for y in range(top + 6, 47, 7):
                s.rect(x0 + 1, y, x1 - 1, y + 2, IRON[3]); s.rect(x0 + 1, y, x1 - 1, y, IRON[5])
                s.px(x0 + 2, y + 1, GOLD[5]); s.px(x1 - 2, y + 1, GOLD[3])
                s.rect(x1 + 1, y + 1, x1 + 5, y + 1, IRON[4]); s.px(x1 + 6, y + 1, IRON[6]); s.px(x1 + 1, y + 2, IRON[2])
    s.outline()
    return s


def trap(lv, f):
    s = Spr(36, 52)
    sprung, alt = f >= 2, f % 2
    cy, w = 44, 7 + lv
    # 땅에 박힌 판 (흙 테두리)
    for y in range(cy - 4, cy + 5):
        for x in range(18 - w - 2, 18 + w + 3):
            if ((x - 18) / (w + 2)) ** 2 + ((y - cy) / 4.5) ** 2 <= 1:
                s.px(x, y, C('#4a3322') if y > cy else C('#5c4129'))
    for y in range(cy - 3, cy + 4):
        for x in range(18 - w, 18 + w + 1):
            if ((x - 18) / w) ** 2 + ((y - cy) / 3.5) ** 2 <= 1:
                s.px(x, y, IRON[3] if y < cy else IRON[2])
    s.rect(18 - w + 2, cy, 18 + w - 2, cy, IRON[1])
    if lv >= 3:
        for a in range(8):
            ang = a * math.pi / 4
            s.px(18 + math.cos(ang) * (w - 2), cy + math.sin(ang) * 2, (RED[4] if alt else RED[3]) if not sprung else RED[1])
    if not sprung:
        for side in (-1, 1):
            for i in range(w - 1):
                x = 18 + side * (i + 1)
                tooth = i % 2 == 0
                s.px(x, cy - 3 - (2 if tooth else 1), IRON[6] if side < 0 else IRON[5])
                s.px(x, cy - 3, IRON[4]); s.px(x, cy - 2, IRON[3])
        s.disc(18, cy, 1.8, [RED[2], RED[3], RED[4], RED[5]] if lv >= 2 else IRON[3:7])
        if alt:
            s.px(18 - w + 2, cy - 5, C('#ffffff'))  # 반짝
        if lv >= 2:
            for x in (18 - w - 1, 18 + w + 1):
                s.rect(x, cy - 3, x, cy, IRON[4]); s.px(x, cy - 4, IRON[6])
    else:
        for i in range(-w + 2, w - 1):
            s.px(18 + i, cy - 3, IRON[4] if i % 2 else IRON[5]); s.px(18 + i, cy - 2, IRON[2])
        if not alt:
            for (x, y) in ((12, 38), (24, 37), (18, 35)):
                s.px(x, y, WARMSTONE[4])
    s.outline()
    return s


def totem(lv, f):
    s = Spr(36, 52)
    fire, alt = f >= 2, f % 2
    top = 17 - (lv - 1) * 3
    s.cyl(13, 23, top, 48, WOOD)
    # 얼굴 조각: 칠한 눈썹·눈·입 + 홈
    for i, fy in enumerate(range(top + 4, 46, 10)):
        s.rect(13, fy - 2, 23, fy - 2, WOOD[2])
        paint = PAINT_R if i % 2 == 0 else PAINT_T
        s.rect(14, fy, 16, fy, paint); s.rect(20, fy, 22, fy, paint)
        s.rect(15, fy + 1, 15, fy + 2, C('#120a06')); s.rect(21, fy + 1, 21, fy + 2, C('#120a06'))
        s.px(15, fy + 1, GREEN[5] if (fire or alt) else GREEN[4]); s.px(21, fy + 1, GREEN[5] if (fire or alt) else GREEN[4])
        s.rect(17, fy + 3, 19, fy + 4, WOOD[5]); s.px(18, fy + 3, WOOD[6])
        s.rect(15, fy + 6, 21, fy + 6, C('#120a06')); s.rect(16, fy + 7, 20, fy + 7, paint)
    # 깃털
    for i, (x, c) in enumerate(((12, CLOTH_R[3]), (24, PAINT_T))):
        for k in range(5):
            s.px(x + (-1 if x < 18 else 1) * (k // 2), top + 3 + k, c)
    # 날개 (잎)
    if lv >= 2:
        for side in (-1, 1):
            for i in range(7):
                x = 18 + side * (6 + i)
                y0 = top + 7 + i // 2 - (1 if alt and i > 3 else 0)
                for y in range(y0, y0 + 5 - i // 2):
                    s.px(x, y, GREEN[4] if y == y0 else GREEN[3] if side < 0 else GREEN[2])
            s.px(18 + side * 12, top + 10, GREEN[5])
    # 보석
    r = 3 + (1 if lv >= 3 else 0)
    s.disc(18, top - 3, r + (1 if f == 2 else 0), GREEN[1:7] if fire else GREEN[:6])
    s.px(17, top - 4, GREEN[6])
    s.rect(15, top - 1, 21, top, GOLD[3] if lv >= 3 else WOOD[4])
    if lv >= 3:
        for a in range(10):
            ang = a * math.pi / 5 + alt * 0.3
            s.px(18 + math.cos(ang) * 8, top - 3 + math.sin(ang) * 8, GOLD[5] if a % 2 else GOLD[3])
    if fire:
        for (x, y) in ((7, top + 3), (29, top + 5), (10, top - 9), (26, top - 8), (5, top + 14), (31, top + 16)):
            s.px(x, y - (f - 2) * 2, GREEN[6]); s.px(x, y + 1 - (f - 2) * 2, GREEN[4])
    s.outline()
    return s


def build_towers():
    makers = [arrow_tower, magic_tower, frost_tower, wall_seg, trap, totem]
    sheet = np.zeros((52 * 6, 36 * 12, 4), np.uint8)
    for r, mk in enumerate(makers):
        for lv in (1, 2, 3):
            for f in range(4):
                c = (lv - 1) * 4 + f
                sheet[r * 52:(r + 1) * 52, c * 36:(c + 1) * 36] = mk(lv, f).a
    return Image.fromarray(sheet, 'RGBA')


# ---------------------------------------------------------------- 수정
CRYS = R('#081a3d', '#0e2f6b', '#1650a0', '#2378cf', '#43a6ec', '#86d1fb', '#c8eeff', '#ffffff')
HURT = R('#2a0a2e', '#4d1350', '#7a1f6e', '#ad3487', '#d95aa3', '#f59ac8', '#ffd2e6', '#ffffff')


def crystal(frame, dmg):
    s = Spr(32, 60)
    cx, top, mid, bot, half = 16, 4, 25, 54, 11
    pal = CRYS if dmg < 2 else [CRYS[0], CRYS[1], HURT[2], CRYS[3], HURT[4], CRYS[5], HURT[6], CRYS[7]]
    band = 2 + frame * 9  # 빛 띠가 위에서 아래로
    for y in range(top, bot + 1):
        w = half * (y - top) / (mid - top) if y <= mid else half * (bot - y) / (bot - mid)
        w = max(0, w)
        for x in range(int(round(cx - w)), int(round(cx + w)) + 1):
            u = (x - (cx - w)) / max(1, 2 * w)
            # 면 4개: 바깥 왼쪽(밝음)·안 왼쪽·안 오른쪽·바깥 오른쪽(어둠)
            k = 6 if u < 0.18 else 5 if u < 0.48 else 3 if u < 0.78 else 2
            if y > mid:
                k -= 1
            # 안쪽 빛 (가운데 아래가 은은하게 밝음)
            if abs(x - cx) < 3 and mid - 4 < y < mid + 10:
                k += 1
            # 흐르는 빛 띠
            if abs((y - band) - (x - cx) * 0.5) < 1.6 and u < 0.75:
                k += 2
            s.px(x, y, pal[max(0, min(7, k))])
        if top + 2 < y < bot - 2:
            s.px(cx, y, pal[6] if y < mid else pal[4])
            s.px(cx - int(w * 0.55), y, pal[6] if y < mid - 2 else pal[5])  # 왼쪽 능선
    for x in range(cx - half + 1, cx + half):
        s.px(x, mid, pal[5] if x < cx else pal[3])
    # 반짝임 (+ 모양)
    sp = [(10, 15), (21, 31), (13, 40), (19, 9), (11, 27), (20, 20)][frame]
    s.px(*sp, pal[7])
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        s.px(sp[0] + dx, sp[1] + dy, pal[6])
    crack = C('#050b1d')
    if dmg >= 1:
        for seg in ((12, 16, 15, 23), (15, 23, 13, 28), (15, 23, 18, 25), (13, 28, 14, 31)):
            s.line(*seg, crack)
        s.px(14, 19, pal[7])
    if dmg >= 2:
        for seg in ((20, 30, 17, 37), (17, 37, 19, 44), (9, 28, 12, 34), (21, 12, 19, 18), (17, 37, 14, 40)):
            s.line(*seg, crack)
        s.px(18, 33, HURT[6]); s.px(10, 30, HURT[6])
    s.outline(strong=True)
    return s


def build_crystal():
    sheet = np.zeros((60 * 3, 32 * 6, 4), np.uint8)
    for d in range(3):
        for f in range(6):
            sheet[d * 60:(d + 1) * 60, f * 32:(f + 1) * 32] = crystal(f, d).a
    return Image.fromarray(sheet, 'RGBA')


# ---------------------------------------------------------------- 맵
W, H = 720, 450
LANES = [
    [[2620, 430], [1950, 430], [1350, 500], [920, 690], [660, 850]],
    [[2620, 920], [1850, 970], [1250, 900], [780, 920]],
    [[2620, 1420], [1950, 1410], [1350, 1340], [920, 1150], [660, 990]],
]
CRYSTAL = (560, 920)

GRASS = R('#15302d', '#1c3d32', '#254b34', '#305b37', '#3e6b3a', '#527d3f', '#6a9045', '#88a652', '#acbf68')
DIRT = R('#2e211f', '#43302a', '#5a3f2f', '#735235', '#8c663d', '#a57d4b', '#bf975e', '#d8b679')
CLIFF = R('#17141a', '#241f25', '#342c31', '#463b3d', '#5b4f4c', '#74675e', '#8f8172', '#ab9c88', '#c8baa3')
LEAF = R('#0a1a1a', '#0f2a24', '#16392b', '#1f4b31', '#2b6036', '#3b7539', '#518b3d', '#6ea145', '#93b955')
PINE = R('#081616', '#0c2322', '#123128', '#19412e', '#225234', '#2f653b', '#447a42')
WATER = R('#14243d', '#1b3656', '#26517a', '#3a7199', '#6aa0bf', '#b9dbe6')


def value_noise(w, h, cell, rnd):
    gw, gh = w // cell + 3, h // cell + 3
    g = np.array([[rnd.random() for _ in range(gw)] for _ in range(gh)])
    ys, xs = np.mgrid[0:h, 0:w]
    fx, fy = xs / cell, ys / cell
    x0, y0 = fx.astype(int), fy.astype(int)
    tx, ty = fx - x0, fy - y0
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a = g[y0, x0] * (1 - tx) + g[y0, x0 + 1] * tx
    b = g[y0 + 1, x0] * (1 - tx) + g[y0 + 1, x0 + 1] * tx
    return a * (1 - ty) + b * ty


def fbm(w, h, cells, rnd):
    out = np.zeros((h, w))
    amp, tot = 1.0, 0.0
    for c in cells:
        out += value_noise(w, h, c, rnd) * amp
        tot += amp
        amp *= 0.5
    return out / tot


def bump_light(hgt):
    """높이 지도 → 왼쪽 위 빛 (요철)."""
    gx = np.zeros_like(hgt); gy = np.zeros_like(hgt)
    gx[:, 1:-1] = hgt[:, 2:] - hgt[:, :-2]
    gy[1:-1, :] = hgt[2:, :] - hgt[:-2, :]
    return np.clip(0.5 - (gx * 0.7 + gy * 0.9) * 6, 0, 1)


def seg_dist(xs, ys, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1
    t = np.clip(((xs - ax) * dx + (ys - ay) * dy) / L2, 0, 1)
    return np.hypot(xs - (ax + dx * t), ys - (ay + dy * t)), t


def pal_idx(v, n, xs, ys):
    f = np.clip(v, 0, 0.9999) * (n - 1)
    k = f.astype(int)
    return np.where((f - k) > BAYER[ys & 3, xs & 3], np.minimum(n - 1, k + 1), k)


def lane_point(pts, frac):
    seg = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    total = sum(seg)
    d = max(0, min(1, frac)) * total
    for i, l in enumerate(seg):
        if d <= l or i == len(seg) - 1:
            t = min(1, d / l) if l else 0
            (ax, ay), (bx, by) = pts[i], pts[i + 1]
            ln = math.hypot(bx - ax, by - ay) or 1
            return ax + (bx - ax) * t, ay + (by - ay) * t, -(by - ay) / ln, (bx - ax) / ln
        d -= l
    return pts[0][0], pts[0][1], 0, 1


def slots_world():
    out = []
    for pts in LANES:
        for k, f in enumerate((0.2, 0.38, 0.56, 0.74)):
            x, y, nx, ny = lane_point(pts, f)
            side = 1 if k % 2 else -1
            out.append((round(x + nx * 105 * side), round(y + ny * 105 * side)))
    for dx, dy in ((-30, -200), (-30, 200)):
        out.append((CRYSTAL[0] + dx, CRYSTAL[1] + dy))
    return out


class Canvas:
    """맵 그리기: RGB 배열 + 물건 놓지 말 곳(keep) + 그림자 · 빛 겹."""

    def __init__(self):
        self.img = np.zeros((H, W, 3), np.float32)
        self.keep = np.zeros((H, W), bool)
        self.shadow = np.zeros((H, W), np.float32)  # 0~1 (어둡게)
        self.light = []  # (x, y, r, (r,g,b), 세기)

    def put(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H and c is not None:
            self.img[y, x] = c[:3]

    def shade(self, x, y, k):
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H:
            self.shadow[y, x] = max(self.shadow[y, x], k)

    def ellipse_shadow(self, cx, cy, rx, ry, k=0.45):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d < 1 and 0 <= x < W and 0 <= y < H:
                    kk = k if d < 0.6 else k * (0.6 if BAYER[y & 3, x & 3] < 0.5 else 0.3)
                    self.shade(x, y, kk)

    def blit(self, spr, x, y):
        """Spr(RGBA)를 맵에 찍음 (불투명 칸만)."""
        a = spr.a
        for yy in range(a.shape[0]):
            for xx in range(a.shape[1]):
                if a[yy, xx, 3] > 0:
                    self.put(x + xx, y + yy, a[yy, xx])


def build_map():
    rnd = random.Random(20261110)
    ys, xs = np.mgrid[0:H, 0:W]
    cv = Canvas()
    img = cv.img
    cr = (CRYSTAL[0] / 4, CRYSTAL[1] / 4)

    # ---- 1) 풀밭: 큰 무늬(밝은 빈터·어두운 수풀) + 높이 요철 + 따뜻한/차가운 얼룩
    big = fbm(W, H, [90, 45], rnd)
    mid = fbm(W, H, [16, 8], rnd)
    hgt = fbm(W, H, [12, 6, 3], rnd)
    bl = bump_light(hgt)
    sun = np.clip(1 - (xs / W) * 0.25 - (ys / H) * 0.15, 0, 1)  # 왼쪽 위가 조금 밝음
    v = 0.18 + big * 0.42 + mid * 0.16 + (bl - 0.5) * 0.22 + sun * 0.12
    gk = pal_idx(v, 8, xs, ys)
    img[:] = np.array(GRASS, np.float32)[gk][:, :, :3]

    # ---- 2) 길: 다져진 흙 (가운데 밝고 가장자리 어두움) · 바퀴 자국 · 자갈 · 웅덩이 · 수정 가까이는 돌길
    dist = np.full((H, W), 999.0)
    along = np.zeros((H, W))   # 수정에서 얼마나 먼지 (0 = 동굴, 1 = 수정)
    for pts in LANES:
        p = [(x / 4, y / 4) for x, y in pts] + [cr]
        seg_len = [math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1]) for i in range(len(p) - 1)]
        total = sum(seg_len)
        acc = 0
        for i in range(len(p) - 1):
            d, t = seg_dist(xs, ys, *p[i], *p[i + 1])
            better = d < dist
            dist = np.where(better, d, dist)
            along = np.where(better, (acc + t * seg_len[i]) / total, along)
            acc += seg_len[i]
    edge_n = fbm(W, H, [7, 3], rnd)
    rw = 12.5 + (edge_n - 0.5) * 4.5
    road = dist < rw
    dh = fbm(W, H, [5, 2], rnd)
    dlight = bump_light(dh)
    center = 1 - np.clip(dist / rw, 0, 1)
    dv = 0.25 + center * 0.3 + (dlight - 0.5) * 0.35 + dh * 0.15
    dk = pal_idx(dv, 7, xs, ys)
    img[road] = np.array(DIRT, np.float32)[dk][:, :, :3][road]
    # 가장자리: 어두운 흙 테 + 풀이 길 위로 비죽 (위쪽 테두리는 풀 그늘)
    rim = road & (dist > rw - 2.2)
    img[rim] = np.array(DIRT[1][:3], np.float32)
    lane_cells = road
    cv.keep |= dist < 18
    # 바퀴 자국
    for pts in LANES:
        p = [(x / 4, y / 4) for x, y in pts] + [cr]
        for i in range(len(p) - 1):
            (ax, ay), (bx, by) = p[i], p[i + 1]
            ln = math.hypot(bx - ax, by - ay)
            nx, ny = -(by - ay) / ln, (bx - ax) / ln
            for s_ in range(int(ln * 1.5)):
                t = s_ / (ln * 1.5)
                x, y = ax + (bx - ax) * t, ay + (by - ay) * t
                for off in (-4.5, 4.5):
                    px, py = int(x + nx * off), int(y + ny * off)
                    if 0 <= px < W and 0 <= py < H and road[py, px] and rnd.random() < 0.85:
                        img[py, px] = DIRT[2][:3]
                        if 0 <= py - 1 < H and road[py - 1, px]:
                            img[py - 1, px] = np.maximum(img[py - 1, px], np.array(DIRT[5][:3], np.float32))
    # 자갈 (빛 받는 점 + 그림자 점)
    for _ in range(1600):
        x, y = rnd.randint(0, W - 2), rnd.randint(0, H - 2)
        if road[y, x] and road[y + 1, x + 1]:
            img[y, x] = DIRT[7][:3] if rnd.random() < 0.5 else DIRT[6][:3]
            img[y + 1, x] = DIRT[1][:3]
    # 수정 가까이(along > 0.78): 깨진 돌길
    # 촘촘한 돌길: 5×4 판석을 엇갈려 깔고 줄눈 1px · 동굴 쪽 끝은 듬성듬성 빠져 흙과 섞임
    cob = road & (along > 0.72) & (dist < rw - 1.5)
    for gy in range(0, H, 4):
        for gx in range(0, W, 5):
            jx, jy = gx + (2 if (gy // 4) % 2 else 0), gy
            if not (0 <= jx < W - 4 and 0 <= jy < H - 3) or not cob[jy, jx]:
                continue
            if rnd.random() > (along[jy, jx] - 0.72) * 14:
                continue
            tone = rnd.choice((3, 4, 4, 5))
            for yy in range(3):
                for xx in range(4):
                    if (xx in (0, 3) and yy in (0, 2)) or not cob[jy + yy, jx + xx]:
                        continue
                    k = tone + (1 if (yy == 0 and xx < 3) else -1 if yy == 2 else 0)
                    img[jy + yy, jx + xx] = STONE[max(0, min(7, k))][:3]
            if jy + 3 < H:
                for xx in range(1, 3):
                    if cob[jy + 3, jx + xx]:
                        img[jy + 3, jx + xx] = STONE[1][:3]
    # 웅덩이 (가운데 길 2곳, 아래 길 1곳)
    for (px_, py_, rx, ry) in ((395, 235, 7, 3), (250, 226, 5, 2.5), (430, 340, 6, 2.5)):
        for y in range(int(py_ - ry - 1), int(py_ + ry + 2)):
            for x in range(int(px_ - rx - 1), int(px_ + rx + 2)):
                d = ((x - px_) / rx) ** 2 + ((y - py_) / ry) ** 2
                if d < 1 and road[y, x]:
                    k = 2 if d > 0.65 else 3 if y < py_ else 2
                    if y < py_ - ry * 0.3 and x < px_:
                        k = 4
                    img[y, x] = WATER[k][:3]
                elif d < 1.35 and road[y, x]:
                    img[y, x] = DIRT[1][:3]
        img[int(py_ - 1), int(px_ - rx * 0.4)] = WATER[5][:3]

    # 풀이 길 위로 비죽 (가장자리 따라 풀포기)
    for _ in range(5000):
        x, y = rnd.randint(1, W - 2), rnd.randint(2, H - 2)
        if road[y, x] and not road[y - 2, x] and dist[y, x] > rw[y, x] - 2.5:
            for (dx, dy, k) in ((0, 0, 5), (0, -1, 6), (-1, -1, 4), (1, 0, 4)):
                if 0 <= x + dx < W:
                    img[y + dy, x + dx] = GRASS[k][:3]
        elif road[y, x] and not road[y + 2, x] and dist[y, x] > rw[y, x] - 2:
            img[y, x] = GRASS[3][:3]; img[y + 1, x] = GRASS[2][:3]

    # ---- 3) 풀 결: 수천 개 풀포기 (위 밝음, 아래 그늘)
    for _ in range(14000):
        x, y = rnd.randint(1, W - 2), rnd.randint(2, H - 2)
        if road[y, x] or cv.keep[y, x]:
            continue
        k = int(gk[y, x])
        hi = min(8, k + 2)
        img[y, x] = GRASS[min(8, k + 1)][:3]
        img[y - 1, x] = GRASS[hi][:3]
        if rnd.random() < 0.5:
            img[y - 1, x + (1 if rnd.random() < 0.5 else -1)] = GRASS[min(8, k + 1)][:3]
        img[y + 1, x] = GRASS[max(0, k - 1)][:3]

    # ---- 4) 오른쪽 절벽 (높은 바위 고원) · 요철 빛 · 층 무늬 · 아래 자갈
    cn = value_noise(1, H, 12, rnd)[:, 0]
    cliff_x = 640 + (cn - 0.5) * 22
    rock_h = fbm(W, H, [20, 9, 4, 2], rnd)
    rl = bump_light(rock_h * 1.6)
    strata = (np.sin((ys + rock_h * 25) * 0.55) + 1) * 0.5
    for y in range(H):
        x0 = int(cliff_x[y])
        for x in range(max(0, x0), W):
            depth = (x - x0)
            if depth < 7:
                # 서쪽을 보는 절벽 면: 어둡고 세로 결
                k = 2 + (1 if (x + y) % 3 == 0 else 0) + (1 if rl[y, x] > 0.6 else 0)
            else:
                k = int(np.clip(2 + rl[y, x] * 5 + strata[y, x] * 1.2 - 0.6, 1, 8))
            img[y, x] = CLIFF[k][:3]
        # 위 가장자리 밝은 턱
        if x0 + 7 < W:
            img[y, x0 + 7] = CLIFF[7][:3] if y % 2 else CLIFF[6][:3]
        # 절벽 발치 그림자
        for x in range(max(0, x0 - 6), x0):
            cv.shade(x, y, 0.45 * (1 - (x0 - x) / 6))
    # 고원 위 이끼·풀
    for _ in range(500):
        y = rnd.randint(0, H - 1)
        x = rnd.randint(int(cliff_x[y]) + 9, W - 1)
        if rnd.random() < 0.5:
            img[y, x] = C('#4b6e36')[:3]
            if x + 1 < W:
                img[y, x + 1] = C('#3a5a2f')[:3]
    # 발치 굴러떨어진 돌
    for _ in range(60):
        y = rnd.randint(55, H - 50)
        x = int(cliff_x[y]) - rnd.randint(3, 16)
        r = rnd.uniform(1.6, 3.6)
        if not road[min(H - 1, y), max(0, x)]:
            cv.ellipse_shadow(x + 1.5, y + r * 0.6, r + 1, r * 0.5, 0.4)
            for yy in range(int(y - r), int(y + r * 0.7) + 1):
                for xx in range(int(x - r), int(x + r) + 1):
                    d = ((xx - x) / r) ** 2 + ((yy - y) / (r * 0.8)) ** 2
                    if d < 1 and 0 <= xx < W and 0 <= yy < H:
                        lum = (-(xx - x) / r * 0.6 - (yy - y) / r * 0.8) * 0.5 + 0.55
                        img[yy, xx] = CLIFF[1 if d > 0.78 else int(np.clip(3 + lum * 4, 2, 8))][:3]

    # ---- 5) 동굴 입구: 돌 아치 + 나무 버팀목 + 안쪽 어둠 그라데이션 + 횃불 + 해골 깃발
    for li, pts in enumerate(LANES):
        mx, my = pts[0][0] / 4 + 6, pts[0][1] / 4
        rx, ry = 22, 27
        for y in range(int(my - ry - 8), int(my + ry + 6)):
            for x in range(int(mx - rx - 8), int(mx + rx + 14)):
                if not (0 <= x < W and 0 <= y < H):
                    continue
                e = ((x - mx) / rx) ** 2 + ((y - my) / ry) ** 2
                if e <= 1.0:
                    # 안쪽: 가운데로 갈수록 더 어두움 (디더)
                    k = 0 if e < 0.55 else 1 if e < 0.8 else 2
                    if 0.5 < e < 0.62 and BAYER[y & 3, x & 3] < 0.5:
                        k = 1
                    img[y, x] = R('#040306', '#0b080c', '#171116')[k][:3]
                elif e <= 1.55 and y < my + ry * 0.75:
                    # 아치 돌: 쐐기 돌 무늬
                    ang = math.atan2(y - my, x - mx)
                    block = int((ang + math.pi) / (math.pi / 7))
                    lum = (-(x - mx) * 0.5 - (y - my) * 0.9) / (rx + ry) + 0.5
                    k = int(np.clip(3 + lum * 4 + (block % 2) * 0.8, 2, 8))
                    if abs(((ang + math.pi) % (math.pi / 7)) - 0.01) < 0.06 or abs(e - 1.0) < 0.08:
                        k = 1
                    img[y, x] = CLIFF[k][:3]
        # 나무 버팀목 (양쪽 기둥 + 위 들보)
        for side in (-1, 1):
            bx = int(mx + side * (rx - 3))
            for y in range(int(my - ry + 8), int(my + ry - 2)):
                for dx, k in ((0, 5 if side < 0 else 3), (1, 4 if side < 0 else 2), (2, 2)):
                    img[y, bx + dx * side * -1 if side > 0 else bx + dx] = WOOD[k][:3]
        for x in range(int(mx - rx + 1), int(mx + rx - 1)):
            img[int(my - ry + 7), x] = WOOD[5][:3]; img[int(my - ry + 8), x] = WOOD[4][:3]; img[int(my - ry + 9), x] = WOOD[1][:3]
        # 안쪽 붉은 눈 세 쌍 (깊이마다 어둡게)
        for (ex, ey, c) in ((mx + 4, my - 4, '#ff5a3d'), (mx + 12, my + 6, '#c23a2a'), (mx - 6, my + 9, '#8a2a22')):
            img[int(ey), int(ex)] = C(c)[:3]; img[int(ey), int(ex) + 3] = C(c)[:3]
        # 횃불 (아치 왼쪽)
        tx, ty = int(mx - rx - 7), int(my - 6)
        for y in range(ty, ty + 9):
            img[y, tx] = WOOD[3][:3]; img[y, tx + 1] = WOOD[1][:3]
        for (dx, dy, c) in ((0, -1, RED[3]), (1, -1, RED[2]), (0, -2, AMBER[3]), (1, -2, RED[3]), (0, -3, AMBER[4]), (0, -4, AMBER[5]), (1, -3, AMBER[3])):
            img[ty + dy, tx + dx] = c[:3]
        cv.light.append((tx, ty - 3, 26, (255, 150, 60), 0.55))
        # 해골 깃발 (아치 위)
        fx, fy = int(mx + rx + 2), int(my - ry - 2)
        for y in range(fy, fy + 16):
            img[y, fx] = WOOD[2][:3]
        for y in range(fy + 1, fy + 8):
            for x in range(fx + 1, fx + 7 - (y - fy) // 3):
                img[y, x] = CLOTH_R[2 if x < fx + 4 else 1][:3]
        img[fy + 3, fx + 2] = C('#e8e2d0')[:3]; img[fy + 3, fx + 3] = C('#e8e2d0')[:3]; img[fy + 4, fx + 2] = C('#e8e2d0')[:3]
        # 입구 앞 흙 부채꼴은 길이 이미 있음. 뼈 몇 조각
        for _ in range(4):
            bx_, by_ = int(mx - rx - rnd.randint(4, 18)), int(my + rnd.randint(-14, 14))
            if road[by_, bx_]:
                img[by_, bx_] = C('#e2dccb')[:3]; img[by_, bx_ + 1] = C('#b9b19c')[:3]
        cv.keep[int(my - ry - 10):int(my + ry + 8), int(mx - rx - 20):] = True

    # ---- 6) 수정 광장: 돌 모자이크 (고리마다 엇갈린 판석, 판석마다 밝기 다름) · 갈라진 틈 사이 풀 · 룬 원 · 받침
    cx, cy = cr
    RP = 54
    d = np.hypot(xs - cx, ys - cy * 1.0)
    ang = np.arctan2(ys - cy, xs - cx)
    plaza = d < RP
    ri = np.floor(d / 8).astype(int)
    nseg = np.maximum(6, ri * 6)
    segi = np.floor(((ang + math.pi) / (2 * math.pi) * nseg + (ri % 2) * 0.5)).astype(int)
    segf = ((ang + math.pi) / (2 * math.pi) * nseg + (ri % 2) * 0.5) % 1
    arc = np.minimum(segf, 1 - segf) * (2 * math.pi * d / nseg)
    seam = ((arc < 0.75) & (ri >= 1)) | (np.abs(d - ri * 8) < 0.75)
    tile_rand = ((segi * 73 + ri * 151) % 7) / 6.0
    lit = np.clip(0.5 - ((xs - cx) * 0.5 + (ys - cy) * 0.8) / (RP * 2.2), 0, 1)
    pv = 0.25 + tile_rand * 0.28 + lit * 0.3 + (bump_light(fbm(W, H, [4, 2], rnd)) - 0.5) * 0.2
    pk = pal_idx(pv, 7, xs, ys)
    img[plaza] = np.array(STONE, np.float32)[pk][:, :, :3][plaza]
    # 판석 위 가장자리 밝게 (입체감)
    tile_top = plaza & (np.abs(d - ri * 8 - 1) < 0.6) & (ys < cy)
    img[tile_top] = STONE[6][:3]
    img[plaza & seam] = STONE[1][:3]
    # 틈 사이 풀
    for _ in range(140):
        a_ = rnd.uniform(0, 2 * math.pi); r_ = rnd.uniform(16, RP - 3)
        x, y = int(cx + math.cos(a_) * r_), int(cy + math.sin(a_) * r_)
        if seam[y, x]:
            img[y, x] = GRASS[5][:3]
            if rnd.random() < 0.5:
                img[y - 1, x] = GRASS[6][:3]
    # 깨진 판석 몇 장 (흙이 보임)
    for _ in range(6):
        a_ = rnd.uniform(0, 2 * math.pi); r_ = rnd.uniform(28, RP - 6)
        x0_, y0_ = int(cx + math.cos(a_) * r_), int(cy + math.sin(a_) * r_)
        for yy in range(-2, 3):
            for xx in range(-3, 4):
                if abs(xx) + abs(yy) < 4 and rnd.random() < 0.85:
                    img[y0_ + yy, x0_ + xx] = DIRT[2 if yy > 0 else 3][:3]
    # 바깥 테두리 (두 겹 돌 + 그림자)
    img[(d >= RP) & (d < RP + 1.6)] = STONE[1][:3]
    img[(d >= RP - 2) & (d < RP) & (ys < cy)] = STONE[6][:3]
    img[(d >= RP - 2) & (d < RP) & (ys >= cy)] = STONE[3][:3]
    for y in range(H):
        for x in range(int(cx - RP - 2), int(cx + RP + 6)):
            dd = math.hypot(x - cx - 2, y - cy - 3)
            if RP + 1 < dd < RP + 4 and 0 <= x < W:
                cv.shade(x, y, 0.3)
    # 룬 원 두 겹 + 글자
    img[(np.abs(d - 37) < 0.8) & plaza] = RUNEC[3][:3]
    img[(np.abs(d - 35) < 0.55) & plaza] = RUNEC[1][:3]
    img[(np.abs(d - 46) < 0.55) & plaza] = RUNEC[1][:3]
    for i in range(16):
        a_ = i * math.pi / 8 + 0.2
        gx_, gy_ = cx + math.cos(a_) * 41, cy + math.sin(a_) * 41
        glyph = [((0, -2), (0, -1), (0, 0), (0, 1), (0, 2)), ((-1, -1), (0, 0), (1, 1), (-1, 1), (1, -1)), ((-1, -2), (0, -2), (0, -1), (0, 0), (1, 0), (1, 1))][i % 3]
        for (gx2, gy2) in glyph:
            img[int(gy_ + gy2), int(gx_ + gx2)] = RUNEC[4 if (gx2, gy2) == (0, 0) else 3][:3]
    # 가운데 받침: 3단 육각
    for rr, k in ((15, 2), (13, 4), (10, 5), (7, 6)):
        for y in range(int(cy - rr), int(cy + rr) + 1):
            for x in range(int(cx - rr), int(cx + rr) + 1):
                hx, hy = abs(x - cx), abs(y - cy)
                if hx * 0.866 + hy * 0.5 <= rr * 0.866 and hy <= rr * 0.75:
                    kk = k + (1 if (x < cx and y < cy) else -1 if (x > cx + 2 and y > cy) else 0)
                    img[y, x] = STONE[max(0, min(7, kk))][:3]
    img[(np.abs(d - 4) < 0.7)] = RUNEC[4][:3]
    cv.light.append((cx, cy - 6, 70, (120, 210, 255), 0.6))
    cv.keep |= d < RP + 9

    # ---- 7) 광장 둘레 부서진 기둥 (홈 파인 원통 + 머리돌 + 덩굴 + 그림자) · 화로
    def pillar(px_, py_, h, broken, vine=False):
        px_, py_ = int(px_), int(py_)
        cv.ellipse_shadow(px_ + 5, py_ + 1, 8, 3, 0.5)
        s = Spr(13, h + 10)
        base = h + 6
        s.rect(1, base, 11, base + 2, STONE[3]); s.rect(1, base, 11, base, STONE[6])
        s.cyl(3, 9, 5, base - 1, STONE[1:8], hi=0.25)
        for x in (4, 6, 8):
            for y in range(6, base - 1):
                if (y + x) % 7:
                    s.px(x, y, darken(s.get(x, y), 0.8))
        if broken:
            for x in range(3, 10):
                cut = 5 + ((x * 5) % 4)
                for y in range(0, cut):
                    s.a[y, x] = 0
                s.px(x, cut, STONE[5])
        else:
            s.rect(1, 2, 11, 4, STONE[5]); s.rect(1, 2, 11, 2, STONE[7]); s.rect(2, 1, 10, 1, STONE[4])
        if vine:
            for y in range(8, base, 2):
                s.px(3 + (y // 2) % 3, y, C('#3f7a35')); s.px(4 + (y // 2) % 3, y + 1, C('#2e5c2c'))
        s.outline()
        cv.blit(s, px_ - 6, py_ - base - 2)
        cv.keep[py_ - base - 4:py_ + 5, px_ - 8:px_ + 10] = True

    for i, a_ in enumerate((-2.55, -1.95, -1.15, 1.15, 1.95, 2.55)):
        pillar(cx + math.cos(a_) * 63, cy + math.sin(a_) * 60, 16 if i % 3 else 10, i % 3 == 0, vine=i in (1, 4))

    def brazier(bx, by):
        bx, by = int(bx), int(by)
        cv.ellipse_shadow(bx + 2, by + 8, 6, 2, 0.5)
        s = Spr(11, 16)
        s.rect(1, 4, 9, 6, IRON[4]); s.rect(1, 4, 9, 4, IRON[6]); s.rect(2, 7, 8, 7, IRON[2])
        s.rect(4, 8, 6, 13, IRON[3]); s.rect(4, 8, 4, 13, IRON[5]); s.rect(2, 14, 8, 14, IRON[2])
        for (x, y, c) in ((5, 3, RED[3]), (4, 3, RED[2]), (6, 3, RED[2]), (5, 2, AMBER[4]), (4, 2, RED[4]), (6, 1, AMBER[4]), (5, 1, AMBER[5]), (5, 0, AMBER[3]), (3, 3, RED[1]), (7, 3, RED[1])):
            s.px(x, y, c)
        s.outline()
        cv.blit(s, bx - 5, by - 6)
        cv.light.append((bx, by - 4, 30, (255, 150, 60), 0.6))
        cv.keep[by - 8:by + 11, bx - 7:bx + 8] = True

    brazier(cx + 30, cy - 46)
    brazier(cx + 30, cy + 44)

    # ---- 8) 왼쪽 신전 터: 높은 단(위 면 + 남쪽 앞 면) · 광장 쪽 계단 · 기둥 줄 · 수호상 · 쓰러진 기둥
    tx0, tx1, ty0, ty1 = 18, 82, 176, 278
    front_h = 7
    for y in range(ty0, ty1):
        for x in range(tx0, tx1):
            # 판석 (6×6, 엇갈림)
            sx_, sy_ = (x - tx0 + (3 if ((y - ty0) // 6) % 2 else 0)) // 6, (y - ty0) // 6
            tone = 4 + ((sx_ * 7 + sy_ * 13) % 3) - 1
            if (x - tx0 + (3 if ((y - ty0) // 6) % 2 else 0)) % 6 == 0 or (y - ty0) % 6 == 0:
                tone = 2
            elif (y - ty0) % 6 == 1:
                tone += 1
            img[y, x] = WARMSTONE[max(0, min(6, tone))][:3]
    # 앞 면 (남쪽)
    for y in range(ty1, ty1 + front_h):
        for x in range(tx0, tx1):
            k = 2 if (y - ty1) % 3 == 0 else 3
            if (x + (y - ty1) // 3 * 3) % 8 == 0:
                k = 1
            img[y, x] = WARMSTONE[k][:3]
    img[ty1, tx0:tx1] = WARMSTONE[5][:3]
    for x in range(tx0, tx1 + 5):
        for y in range(ty1 + front_h, ty1 + front_h + 4):
            cv.shade(x, y, 0.4)
    # 동쪽 계단 (광장 쪽으로 내려감)
    for i in range(4):
        x0_ = tx1 + i * 3
        for y in range(198 + i * 2, 258 - i * 2):
            for x in range(x0_, x0_ + 3):
                img[y, x] = WARMSTONE[6 - i if x == x0_ else 4 - i // 2][:3]
        img[258 - i * 2:260 - i * 2, x0_:x0_ + 3] = WARMSTONE[1][:3]
    img[ty0, tx0:tx1] = WARMSTONE[6][:3]
    img[ty0:ty1, tx0] = WARMSTONE[5][:3]
    # 수호상 (날개 단 석상)
    st = Spr(18, 26)
    st.rect(4, 21, 13, 24, WARMSTONE[3]); st.rect(4, 21, 13, 21, WARMSTONE[6])
    st.cyl(6, 11, 9, 20, WARMSTONE[1:7])
    st.disc(8.5, 6, 3, WARMSTONE[2:7])
    for i in range(6):
        st.line(5 - i // 2, 10 + i, 1 + i // 3, 6 + i, WARMSTONE[5 - i // 3]); st.line(12 + i // 2, 10 + i, 16 - i // 3, 6 + i, WARMSTONE[4 - i // 3])
    st.rect(8, 12, 9, 18, WARMSTONE[2])
    st.px(8, 14, RUNEC[3]); st.px(9, 14, RUNEC[3])
    st.outline()
    cv.ellipse_shadow(47, 236, 9, 3, 0.45)
    cv.blit(st, 39, 210)
    cv.light.append((47, 222, 16, (120, 210, 255), 0.35))
    cv.keep[150:300, 0:100] = True
    for py_ in (190, 270):
        for px_ in (26, 44, 62):
            pillar(px_, py_, 26 if not (px_ == 62 and py_ == 270) else 12, px_ == 62 and py_ == 270, vine=px_ == 26)
    # 쓰러진 기둥 토막 (단 앞)
    for (lx, ly) in ((70, 296), (90, 300)):
        s = Spr(16, 8)
        for x in range(1, 15):
            for y in range(1, 7):
                k = 6 if y < 3 else 4 if y < 5 else 2
                s.px(x, y, STONE[k])
        s.disc(14, 4, 2.5, STONE[2:7])
        s.outline()
        cv.ellipse_shadow(lx + 9, ly + 7, 9, 2, 0.4)
        cv.blit(s, lx, ly)
        cv.keep[ly - 4:ly + 12, lx - 4:lx + 20] = True

    # ---- 9) 시설 받침돌 14개: 둥근 돌 단 (위 면 판석 고리 + 앞 면) · 희미한 룬 · 이끼
    for i, (wx, wy) in enumerate(slots_world()):
        sx, sy = wx / 4, wy / 4 + 4
        cv.ellipse_shadow(sx + 2, sy + 4, 13, 5, 0.45)
        s = Spr(26, 18)
        ocx, ocy = 13, 7
        for y in range(18):
            for x in range(26):
                e = ((x - ocx) / 12) ** 2 + ((y - ocy) / 6) ** 2
                e2 = ((x - ocx) / 12) ** 2 + ((y - ocy - 3) / 6) ** 2
                if e <= 1:
                    k = 6 if (x < ocx - 2 and y < ocy) else 5 if y < ocy else 4
                    if 0.55 < e < 0.72:
                        k = 3  # 안쪽 고리 홈
                    if e < 0.3:
                        k = 5 if x < ocx else 4
                    s.px(x, y, STONE[k])
                elif e2 <= 1 and y > ocy:
                    s.px(x, y, STONE[2] if x < ocx + 4 else STONE[1])
        for a_ in range(8):
            an = a_ * math.pi / 4 + 0.4
            s.px(ocx + math.cos(an) * 9.5, ocy + math.sin(an) * 4.7, RUNEC[2] if a_ % 2 else RUNEC[1])
        s.px(ocx, ocy, RUNEC[3])
        rr = random.Random(i)
        for _ in range(3):
            mx_, my_ = rr.randint(2, 23), rr.randint(6, 12)
            if s.a[my_, mx_, 3]:
                s.px(mx_, my_, C('#4c7a35')); s.px(mx_ + 1, my_, C('#3a6130'))
        s.outline()
        cv.blit(s, sx - 13, sy - 7)
        cv.keep[int(sy - 14):int(sy + 13), int(sx - 17):int(sx + 18)] = True

    # ---- 10) 숲 테두리: 둥근 나무(잎 덩어리 여러 개) · 전나무 · 덤불 (그림자는 오른쪽 아래로)
    def round_tree(tx, ty, r, seed):
        rr = random.Random(seed)
        cv.ellipse_shadow(tx + r * 0.5, ty + 2, r * 1.15, r * 0.45, 0.55)
        s = Spr(int(r * 3 + 6), int(r * 3 + 8))
        ox, oy = s.w / 2, s.h - 5
        s.cyl(ox - 2, ox + 1, oy - r * 0.8, oy, WOOD[1:6])
        s.px(ox - 3, oy, WOOD[2]); s.px(ox + 2, oy, WOOD[1])  # 뿌리
        blobs = [(0, -r * 1.35, r * 0.95)]
        for k in range(7):
            a_ = -math.pi * (0.1 + 0.8 * k / 6)
            blobs.append((math.cos(a_) * r * 0.85, -r * 1.15 + math.sin(a_) * r * 0.45 + rr.uniform(-1, 1), r * rr.uniform(0.5, 0.65)))
        blobs.sort(key=lambda b: b[1])
        for (bx_, by_, br) in blobs:
            ccx, ccy = ox + bx_, oy + by_
            for y in range(int(ccy - br - 1), int(ccy + br + 2)):
                for x in range(int(ccx - br - 1), int(ccx + br + 2)):
                    dx, dy = (x + 0.5 - ccx) / br, (y + 0.5 - ccy) / br
                    dd = dx * dx + dy * dy
                    if dd > 1 or not (0 <= x < s.w and 0 <= y < s.h):
                        continue
                    z = math.sqrt(1 - dd)
                    # 덩어리 자체 + 나무 전체(왼쪽 위 빛)
                    lum = (-dx * 0.5 - dy * 0.6) * 0.35 + z * 0.35 + (-(x - ox) / (r * 2) - (y - (oy - r * 1.2)) / (r * 2)) * 0.45 + 0.25
                    f = np.clip(lum, 0, 0.999) * 7
                    k = int(f) + (1 if (f - int(f)) > BAYER[y & 3, x & 3] else 0)
                    if rr.random() < 0.08:
                        k += rr.choice((-1, 1))  # 잎 결
                    s.px(x, y, LEAF[max(1, min(8, k))])
        s.outline()
        cv.blit(s, int(tx - ox), int(ty - oy))

    def pine(tx, ty, h, seed):
        cv.ellipse_shadow(tx + h * 0.25, ty + 2, h * 0.38, h * 0.14, 0.55)
        s = Spr(int(h * 0.8 + 6), int(h + 8))
        ox, oy = s.w / 2, s.h - 4
        s.rect(ox - 1, oy - 4, ox + 1, oy, WOOD[2]); s.px(ox - 1, oy - 4, WOOD[4])
        for layer in range(4):
            lt = oy - 4 - layer * h * 0.2 - h * 0.15
            lw = h * 0.38 * (1 - layer * 0.2)
            for y in range(int(lt - h * 0.28), int(lt) + 1):
                t = (y - (lt - h * 0.28)) / (h * 0.28)
                half = lw * t
                for x in range(int(ox - half), int(ox + half) + 1):
                    u = (x - (ox - half)) / max(1, 2 * half)
                    k = 5 if u < 0.3 else 4 if u < 0.6 else 2
                    if y == int(lt):
                        k = 1
                    if (x + y) % 5 == 0 and k > 2:
                        k -= 1
                    s.px(x, y, PINE[k])
            s.px(ox, int(lt - h * 0.28) - 1, PINE[6])
        s.outline()
        cv.blit(s, int(tx - ox), int(ty - oy))

    def bush(bx, by, r, berries=False):
        cv.ellipse_shadow(bx + 2, by + r * 0.4, r + 1, r * 0.4, 0.45)
        s = Spr(int(r * 2 + 6), int(r * 2 + 4))
        ox, oy = s.w / 2, s.h - r - 2
        for (dx, dy, rr_) in ((-r * 0.5, 0.3, r * 0.7), (r * 0.5, 0.3, r * 0.7), (0, -r * 0.3, r * 0.8)):
            s.disc(ox + dx, oy + dy, rr_, LEAF[2:8])
        if berries:
            for (dx, dy) in ((-2, -1), (2, 0), (0, 2)):
                s.px(ox + dx, oy + dy, C('#d9434b')); s.px(ox + dx, oy + dy - 1, C('#ff8a8a'))
        s.outline()
        cv.blit(s, int(bx - ox), int(by - oy - r))

    items = []
    for x in range(-8, 636, 13):
        items.append(('tree', x + rnd.uniform(-4, 4), rnd.uniform(30, 58), rnd.uniform(9, 13)))
        items.append(('tree' if rnd.random() < 0.7 else 'pine', x + rnd.uniform(-4, 4), rnd.uniform(14, 34), rnd.uniform(9, 12)))
        items.append(('tree', x + rnd.uniform(-4, 4), rnd.uniform(432, 458), rnd.uniform(10, 13)))
        if rnd.random() < 0.5:
            items.append(('pine', x + rnd.uniform(-4, 4), rnd.uniform(446, 462), rnd.uniform(20, 26)))
    for y in range(50, 440, 15):
        if not (150 < y < 310):
            items.append(('tree' if rnd.random() < 0.6 else 'pine', rnd.uniform(-4, 14), y + rnd.uniform(-5, 5), rnd.uniform(9, 12)))
    # 안쪽 몇 그루 (길 사이 빈터)
    for (x, y) in ((300, 150), (470, 168), (360, 300), (540, 300), (215, 330), (190, 128)):
        items.append(('tree', x + rnd.uniform(-6, 6), y + rnd.uniform(-6, 6), rnd.uniform(8, 10)))
    for _ in range(26):
        x, y = rnd.randint(60, 620), rnd.randint(70, 390)
        items.append(('bush', x, y, rnd.uniform(3, 5)))
    # 바위·쓰러진 통나무·그루터기·버섯·나무 상자(고블린 짐)
    for _ in range(30):
        items.append(('rock', rnd.randint(60, 625), rnd.randint(66, 392), rnd.uniform(2.2, 4.5)))
    for (x, y) in ((250, 100), (520, 380), (150, 370)):
        items.append(('log', x, y, 0))
    for (x, y) in ((330, 95), (585, 120), (600, 330), (120, 110)):
        items.append(('stump', x, y, 0))
    for (x, y) in ((610, 175), (618, 300), (604, 390)):
        items.append(('crate', x, y, 0))

    for (kind, x, y, r) in sorted(items, key=lambda it: it[2]):
        xi, yi = int(min(W - 1, max(0, x))), int(min(H - 1, max(0, y)))
        if kind in ('tree', 'pine'):
            if cv.keep[yi, xi] and 60 < y < 420:
                continue
            if kind == 'tree':
                round_tree(x, y, r, int(x * 7 + y))
            else:
                pine(x, y, r * 2.2, int(x + y))
            continue
        if cv.keep[max(0, yi - 6):yi + 6, max(0, xi - 8):xi + 8].any():
            continue
        if kind == 'bush':
            bush(x, y, r, berries=rnd.random() < 0.3)
        elif kind == 'rock':
            cv.ellipse_shadow(x + 2, y + r * 0.5, r + 1.5, r * 0.5, 0.45)
            for yy in range(int(y - r), int(y + r * 0.7) + 1):
                for xx in range(int(x - r - 1), int(x + r + 2)):
                    dx, dy = (xx - x) / r, (yy - y) / (r * 0.85)
                    dd = dx * dx + dy * dy
                    if dd > 1 or not (0 <= xx < W and 0 <= yy < H):
                        continue
                    lum = (-dx * 0.6 - dy * 0.8) * 0.45 + math.sqrt(1 - dd) * 0.45 + 0.1
                    k = int(np.clip(lum * 7, 1, 7))
                    img[yy, xx] = (CLIFF[1] if dd > 0.82 and (dy > 0 or dx > 0) else CLIFF[k])[:3]
                    if dy < -0.4 and dx < 0 and rnd.random() < 0.25:
                        img[yy, xx] = C('#4c7a35')[:3]  # 이끼
        elif kind == 'log':
            s = Spr(26, 9)
            s.rect(2, 1, 22, 6, WOOD[3]); s.rect(2, 1, 22, 2, WOOD[5]); s.rect(2, 5, 22, 6, WOOD[1])
            for xx in range(4, 21, 4):
                s.px(xx, 3, WOOD[2])
            s.disc(22, 3.5, 3, [WOOD[3], WOOD[5], WOOD[6]]); s.px(22, 3, WOOD[2])
            s.px(8, 0, C('#4c7a35')); s.px(14, 0, C('#4c7a35')); s.px(15, 0, C('#5d8f3e'))
            s.outline()
            cv.ellipse_shadow(x + 14, y + 7, 13, 2.5, 0.45)
            cv.blit(s, int(x), int(y))
        elif kind == 'stump':
            s = Spr(12, 10)
            s.cyl(2, 9, 3, 8, WOOD[1:6]); s.disc(5.5, 3, 3.5, [WOOD[4], WOOD[5], WOOD[6]], ry=1.8)
            s.px(5, 3, WOOD[3]); s.px(6, 3, WOOD[3])
            s.px(9, 8, C('#d9434b')); s.px(9, 7, C('#ffb0a8')); s.px(1, 8, C('#d9434b'))  # 버섯
            s.outline()
            cv.ellipse_shadow(x + 7, y + 9, 6, 2, 0.45)
            cv.blit(s, int(x), int(y))
        elif kind == 'crate':
            s = Spr(12, 12)
            s.rect(1, 1, 10, 3, WOOD[5]); s.rect(1, 4, 10, 10, WOOD[3])
            s.rect(1, 4, 1, 10, WOOD[4]); s.line(2, 5, 9, 10, WOOD[2]); s.rect(1, 7, 10, 7, WOOD[2])
            s.outline()
            cv.ellipse_shadow(x + 8, y + 11, 6, 2, 0.45)
            cv.blit(s, int(x), int(y))
    # 꽃·풀포기 무리
    for _ in range(80):
        x, y = rnd.randint(55, 625), rnd.randint(64, 395)
        col = rnd.choice(('#f4d35e', '#f28fb0', '#e8edf5', '#9ad0ff', '#c792ea'))
        for _k in range(rnd.randint(3, 7)):
            xx, yy = x + rnd.randint(-4, 4), y + rnd.randint(-3, 3)
            if 0 <= xx < W and 0 <= yy < H and not cv.keep[yy, xx] and not lane_cells[yy, xx]:
                img[yy, xx] = C(col)[:3]
                img[yy + 1 if yy + 1 < H else yy, xx] = GRASS[2][:3]

    # ---- 11) 그림자 → 빛 웅덩이 → 색 보정 · 비네트
    sh = cv.shadow[..., None]
    img *= (1 - sh * 0.75)
    img[..., 2] += sh[..., 0] * 18  # 그림자에 푸른기
    for (lx, ly, lr, col, power) in cv.light:
        dd = np.hypot(xs - lx, (ys - ly) * 1.25)
        k = np.clip(1 - dd / lr, 0, 1) ** 1.6 * power
        # 단계 + 디더 (도트 느낌)
        steps = np.floor(k * 5 + BAYER[ys & 3, xs & 3]) / 5
        img += steps[..., None] * (np.array(col, np.float32)[None, None, :] - img * 0.35) * 0.55
    # 해 질 녘 따뜻한 빛 (왼쪽 위) · 오른쪽 아래 서늘
    warm = np.clip(1 - (xs / W * 0.7 + ys / H * 0.5), 0, 1)
    img[..., 0] *= 0.96 + warm * 0.08
    img[..., 2] *= 1.02 - warm * 0.06
    vig = np.clip(1 - np.minimum.reduce([xs / 80, (W - xs) / 60, ys / 60, (H - ys) / 60]), 0, 1) ** 1.5 * 0.4
    img *= (1 - vig[..., None])
    out = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(out, 'RGB')


def main():
    os.makedirs(os.path.dirname(OUT_TOWERS), exist_ok=True)
    towers = build_towers()
    towers.save(OUT_TOWERS, optimize=True)
    cry = build_crystal()
    cry.save(OUT_CRYSTAL, optimize=True)
    m = build_map()
    m.save(OUT_MAP, 'WEBP', lossless=True, quality=100, method=6)
    print('towers', towers.size, os.path.getsize(OUT_TOWERS), 'crystal', cry.size, os.path.getsize(OUT_CRYSTAL), 'map', m.size, os.path.getsize(OUT_MAP))
    if PREVIEW:
        os.makedirs(PREVIEW, exist_ok=True)
        bg = Image.new('RGBA', (towers.width * 4, towers.height * 4), (52, 78, 56, 255))
        bg.alpha_composite(towers.resize((towers.width * 4, towers.height * 4), Image.NEAREST))
        bg.save(os.path.join(PREVIEW, '_preview_defense_towers.png'))
        bg = Image.new('RGBA', (cry.width * 4, cry.height * 4), (52, 78, 56, 255))
        bg.alpha_composite(cry.resize((cry.width * 4, cry.height * 4), Image.NEAREST))
        bg.save(os.path.join(PREVIEW, '_preview_defense_crystal.png'))
        m.resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(PREVIEW, '_preview_defense_map.png'))


if __name__ == '__main__':
    main()

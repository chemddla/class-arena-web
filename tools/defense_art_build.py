# 💎 수정 방어전 (3판 · 타워 디펜스) 그림 → assets/maps/crystal_defense.webp · assets/sprites/fx/defense_towers.png
# 사용: python tools/defense_art_build.py [미리보기 폴더]
#
# 모두 코드로 찍는 도트 그림. 작법 (pixelfx · 도트 기본기):
#  - 색 단계는 색조를 섞음 (그림자는 푸르고 보랏빛, 밝은 곳은 노랗게) · 빛은 늘 왼쪽 위
#  - 테두리는 검정 한 가지가 아니라 맞닿은 재질의 가장 어두운 색 (아래쪽 테두리가 더 어두움)
#  - 바위·흙은 높이 노이즈로 빛을 계산 (요철) · 그림자는 오른쪽 아래로 떨어짐
#  - 빛 웅덩이(횃불·화로·차원문)는 단계로 끊고 바이어 디더로 섞음
# - 맵: 720×450 도트 (월드 2880×1800의 1/4). 게임은 다듬기 없이 4배.
#   왼쪽 위 동굴 → 지그재그 흙길 한 줄(세 줄을 오가며 내려옴) → 오른쪽 아래 성문(차원문) · 길 사이 포탑 받침돌 22곳 · 숲 테두리
#   길·받침돌 좌표는 index.html의 DEFENSE_PATH · DEFENSE_PADS와 같음 (월드 ÷ 4).
# - 포탑 시트: 칸 36×52, 가로 12칸 = 그림 단계(1~3)마다 [평소 A, 평소 B, 공격 A, 공격 B],
#   세로 4줄 = 화살탑 · 대포탑 · 서리탑 · 마법탑 (index.html DEFENSE_TOWER_KEYS 순서). 발 위치 = 칸 (18, 49). 게임에서 3배.
#   포탑 강화 1~5단계 → 그림 단계 1·2·2·3·3.
import json, math, os, random, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_TOWERS = os.path.join(ROOT, 'assets/sprites/fx/defense_towers.png')
PREVIEW = sys.argv[1] if len(sys.argv) > 1 else None
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def C(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def R(*hs):
    return [C(h) for h in hs]


# 색조를 섞은 단계 (어두움 → 밝음)
STONE = R('#1b1d2c', '#2b2f42', '#41475c', '#5b6377', '#7a8396', '#9ea7b6', '#c6cdd6', '#e9edf1')
WOOD = R('#24140f', '#3b2115', '#58331c', '#784824', '#9a612f', '#bd7f40', '#dca35a')
AMBER = R('#5a1f0c', '#93370f', '#c95a14', '#ec8a1d', '#f8b93c', '#fde382')
CLOTH_R = R('#3b0f1c', '#6b1526', '#a2232f', '#d2413a', '#f0754f')
PURPLE = R('#1a0c3a', '#33156d', '#5226a6', '#7b45d8', '#a77bf2', '#d2c1ff', '#ffffff')
ICE = R('#10224a', '#173d7a', '#1f63ad', '#3592d8', '#68c1f0', '#a8e4ff', '#e3f8ff', '#ffffff')
IRON = R('#121319', '#22242d', '#373a46', '#525866', '#77808e', '#a3abb6', '#d5dae0')
GOLD = R('#4a2508', '#7a4210', '#ad6a18', '#d99a27', '#f2c84a', '#fff0a6')
BRONZE = R('#2a1608', '#4a2a10', '#6e4318', '#956024', '#bb8436', '#dcae5a', '#f6dc96')
RUNEC = R('#0b2c44', '#145a80', '#1f8fc0', '#38bdf8', '#8fe0ff', '#e2f8ff')
RED = R('#3d0a10', '#7a1418', '#b8261f', '#e5532c', '#ff9248', '#ffd38a')


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




def cannon_tower(lv, f):
    """대포탑: 1단계 나무 받침 위 청동 박격포 · 2단계 돌 보루 + 쇠 대포 · 3단계 금 테 보루 + 쌍포. 공격 칸 = 포구 섬광 → 연기."""
    s = Spr(36, 52)
    fire, alt = f >= 2, f % 2
    plinth(s, lv, trim=GOLD if lv >= 3 else IRON if lv >= 2 else None)
    if lv == 1:
        # 나무 받침대 (통나무 넷)
        for y in (33, 36):
            s.rect(8, y, 28, y + 2, WOOD[4]); s.rect(8, y, 28, y, WOOD[6]); s.rect(8, y + 2, 28, y + 2, WOOD[2])
            for x in range(10, 28, 5):
                s.px(x, y + 1, WOOD[3])
        base_y = 32
    else:
        # 둥근 돌 보루 (흉벽 + 벽돌)
        y0 = 27 if lv == 2 else 24
        s.cyl(7, 29, y0, 40, STONE[1:7])
        bricks(s, 8, 28, y0 + 2, 40, STONE, bh=3, bw=5, seed=lv * 11, mossy=lv == 2)
        s.rect(6, y0 - 2, 30, y0, STONE[4]); s.rect(6, y0 - 2, 30, y0 - 2, STONE[6])
        for x in range(6, 31, 5):
            s.rect(x, y0 - 5, x + 2, y0 - 3, STONE[5] if x < 18 else STONE[4]); s.px(x, y0 - 5, STONE[6])
        if lv >= 3:
            for x in range(6, 31):
                s.px(x, y0, GOLD[4] if x < 15 else GOLD[3] if x < 25 else GOLD[2])
        base_y = y0 - 3

    def barrel(cx, cy, length, rad, pal, kick):
        """비스듬히 위로 든 포신 (오른쪽 위를 봄) · 뒤로 밀림(kick)."""
        ang = -0.55
        dx, dy = math.cos(ang), math.sin(ang)
        nx, ny = -dy, dx
        cx -= dx * kick; cy -= dy * kick
        for t in np.linspace(0, length, int(length * 3)):
            r_ = rad * (1.15 if t > length - 2 else 1.0) * (1.2 if t < 2 else 1.0)
            for o in np.linspace(-r_, r_, int(r_ * 4) + 1):
                u = (o + r_) / (2 * r_)
                k = 5 if u < 0.25 else 4 if u < 0.5 else 3 if u < 0.8 else 2
                s.px(cx + dx * t + nx * o, cy + dy * t + ny * o, pal[k])
        # 포구 (어두운 구멍)
        mx, my = cx + dx * length, cy + dy * length
        s.px(mx, my, C('#0d0e15')); s.px(mx - nx * 0.8, my - ny * 0.8, C('#0d0e15'))
        return mx + dx * 2, my + dy * 2, dx, dy

    pal = BRONZE if lv == 1 else (GOLD + [C('#fff8d0')]) if lv >= 3 else IRON
    kick = 1.5 if f == 2 else 0
    muzzles = []
    if lv == 1:
        # 짧고 굵은 박격포 + 바퀴 없는 받침
        s.rect(12, base_y - 4, 24, base_y, WOOD[3]); s.rect(12, base_y - 4, 24, base_y - 4, WOOD[5])
        muzzles.append(barrel(15, base_y - 6, 9, 3.2, pal, kick))
        s.disc(14, base_y - 5, 3, IRON[2:7])
    elif lv == 2:
        muzzles.append(barrel(14, base_y - 3, 13, 2.8, pal, kick))
        s.disc(13, base_y - 2, 3.5, IRON[2:7])
    else:
        muzzles.append(barrel(12, base_y - 2, 13, 2.6, pal, kick))
        muzzles.append(barrel(17, base_y + 1, 13, 2.6, pal, kick * 0.6))
        s.disc(12, base_y - 1, 3.5, GOLD[1:6]); s.disc(17, base_y + 2, 3.2, GOLD[1:6])
    # 포탄 더미 (평소) / 섬광·연기 (공격)
    if not fire:
        for (bx, by) in ((25, 37), (28, 37), (26.5, 35)):
            if lv >= 2 or by > 36:
                s.disc(bx, by + (0 if lv >= 2 else -3), 1.6, IRON[1:6])
        if alt:
            s.px(29, base_y - 8, AMBER[4])  # 도화선 불티
    else:
        for (mx, my, dx, dy) in muzzles:
            if f == 2:
                for i, c in enumerate((AMBER[5], AMBER[4], AMBER[3], RED[3])):
                    s.px(mx + dx * i, my + dy * i, c)
                for (a, c) in ((-0.9, AMBER[4]), (0.9, AMBER[4]), (-1.6, AMBER[3]), (1.6, AMBER[3])):
                    s.px(mx + math.cos(math.atan2(dy, dx) + a) * 3, my + math.sin(math.atan2(dy, dx) + a) * 3, c)
                s.disc(mx + dx * 2, my + dy * 2, 2.2, [RED[3], AMBER[3], AMBER[4], AMBER[5]])
            else:
                for (ox, oy, rr) in ((2, -1, 2.4), (4, -4, 2.0), (6, -6, 1.5)):
                    s.disc(mx + ox, my + oy, rr, STONE[3:8])
    s.outline()
    return s


def build_towers():
    makers = [arrow_tower, cannon_tower, frost_tower, magic_tower]
    sheet = np.zeros((52 * len(makers), 36 * 12, 4), np.uint8)
    for r, mk in enumerate(makers):
        for lv in (1, 2, 3):
            for f in range(4):
                c = (lv - 1) * 4 + f
                sheet[r * 52:(r + 1) * 52, c * 36:(c + 1) * 36] = mk(lv, f).a
    return Image.fromarray(sheet, 'RGBA')


# ---------------------------------------------------------------- 맵
W, H = 720, 450
# 월드 좌표 (index.html DEFENSE_MAPS와 같음) · 맵마다 동굴은 길 첫 점(오른쪽을 봄), 성문은 끝 점
PATH = [[230, 560], [2250, 560], [2250, 920], [640, 920], [640, 1280], [2640, 1280]]
PADS = [(700, 400), (1150, 400), (1600, 400), (2050, 400),
        (440, 740), (760, 740), (1060, 740), (1360, 740), (1660, 740), (1960, 740), (2440, 740),
        (440, 1100), (900, 1100), (1200, 1100), (1500, 1100), (1800, 1100), (2100, 1100), (2440, 1100),
        (1000, 1440), (1450, 1440), (1900, 1440), (2350, 1440)]


def fx_blocked(fx, x, y):
    # 받침돌을 못 놓는 곳: 강(과 둑) · 큰 바위 둘레 · 고지대 절벽 가장자리 (고지대 윗면 안쪽은 됨)
    fx = fx or {}
    for rv in fx.get('river', ()):
        q = rv['pts']
        for i in range(len(q) - 1):
            (ax, ay), (bx, by) = q[i], q[i + 1]
            L = math.hypot(bx - ax, by - ay) or 1
            t = max(0, min(1, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / (L * L)))
            if math.hypot(ax + (bx - ax) * t - x, ay + (by - ay) * t - y) < rv['w'] / 2 + 80:
                return True
    if any(math.hypot(x - bx, y - by) < br + 90 for bx, by, br in fx.get('boulders', ())):
        return True
    for (x0, y0, x1, y1) in fx.get('plateau', ()):
        v = ((x - (x0 + x1) / 2) / ((x1 - x0) / 2)) ** 6 + ((y - (y0 + y1) / 2) / ((y1 - y0) / 2)) ** 6
        if 0.55 < v < 2.0:
            return True
    return False


def auto_pads(path, n=22, near=(120, 300), sep=(270, 230), avoid=(), fx=None):
    # 길에서 near만큼 떨어진 칸 중 사거리(380) 안에 길이 많이 지나는 곳부터, 서로(sep 타원)·avoid와 겹치지 않게 n곳
    paths = path if isinstance(path[0][0], (list, tuple)) else [path]
    pts = []
    for q in paths:
        for i in range(len(q) - 1):
            (ax, ay), (bx, by) = q[i], q[i + 1]
            L = math.hypot(bx - ax, by - ay)
            pts += [(ax + (bx - ax) * k / L, ay + (by - ay) * k / L) for k in range(0, int(L), 40)]
    pts = np.array(pts)
    ends = [q[0] for q in paths] + [q[-1] for q in paths]
    cand = []
    for y in range(380, 1460, 20):
        for x in range(380, 2520, 20):
            d = np.hypot(pts[:, 0] - x, pts[:, 1] - y)
            if near[0] <= d.min() <= near[1] and all(math.hypot(x - ex, y - ey) > 300 for ex, ey in ends) and not fx_blocked(fx, x, y):
                cand.append(((d < 380).sum(), x, y))
    cand.sort(key=lambda c: (-c[0], c[2], c[1]))
    out = []
    for _, x, y in cand:
        if all(((x - px) / sep[0]) ** 2 + ((y - py) / sep[1]) ** 2 >= 1 for px, py in out) and all(((x - px) / 150) ** 2 + ((y - py) / 110) ** 2 >= 1 for px, py in avoid):
            out.append((x, y))
        if len(out) >= n:
            break
    return sorted(out, key=lambda q: (q[1], q[0]))


# 맵 샘플 (판마다 하나를 고름, index.html DEFENSE_MAPS) · 받침돌은 auto_pads로 고르게 22곳 — 자리의 값어치는 길 모양이 정함
# (길이 겹쳐 지나가는 교차로·나선 한가운데·처음과 끝 길이 나란한 곳은 포탑 하나가 여러 번 쏘고, 외길 둘레는 한 번뿐)
LAYOUTS = [
    ('crystal_defense', 20261112, PATH, PADS),  # (예전 맵) 지그재그 · 지금은 판에 안 나옴
    # 8자 교차로: 가운데 줄을 지나간 길이 두 번 세로로 가로지름 → 교차로 두 곳이 핵심
    ('crystal_defense_cross', 20261118, [[230, 900], [2300, 900], [2300, 1360], [1450, 1360], [1450, 440], [600, 440], [600, 1360], [1050, 1360]], None),
    # 나선 탈출: 두 바퀴 감아 들어간 뒤 바깥 바퀴를 가로질러 왼쪽 성문으로 빠져나감 → 나선 한가운데와 가로지르는 곳이 핵심
    ('crystal_defense_vortex', 20261121, [[230, 1360], [2300, 1360], [2300, 440], [600, 440], [600, 1040], [1900, 1040], [1900, 740],
                                         [330, 740]], None),
    # 귀환: 맵을 한 바퀴 돌아 동굴 바로 옆 성문으로 돌아옴 → 동굴과 성문 사이는 처음과 끝을 함께 침
    ('crystal_defense_return', 20261123, [[230, 1360], [2450, 1360], [2450, 440], [1900, 440], [1900, 1040], [1300, 1040], [1300, 440],
                                         [700, 440], [700, 1040]], None),
    # 강과 다리 (블룬스 물 지형 · 식물 vs 좀비 수영장): 세로 강을 길이 다리로 세 번 건넘 → 강 위엔 못 지어 다리 목이 비고, 양쪽 둑에서 나눠 쏴야 함
    ('crystal_defense_river', 20261130, [[230, 500], [2400, 500], [2400, 900], [500, 900], [500, 1300], [2640, 1300]], None,
     {'river': [{'pts': [[1500, 100], [1380, 700], [1530, 1150], [1420, 1800]], 'w': 220}]}),
]

# 판에 안 나오는 후보 (그림 비교용 · ONLY=키 로만 그림): 길 모양 · 여러 길(게임에 여러 길 지원 필요) · 바위 시야·고지대(게임 규칙 필요)
CANDIDATES = [
    # 맞물림: 첫 길(위)과 마지막 길(성문 앞)이 나란히 붙어 달림 → 그 사이는 같은 몬스터를 두 번 침 · 오른쪽 기둥을 끝 길이 가로지름
    ('crystal_defense_interlock', 20261119, [[230, 440], [2300, 440], [2300, 1360], [500, 1360], [500, 700], [2640, 700]], None),
    # 외길과 미로: 아래 긴 외길(포탑 하나가 한 번만 닿음) 다음 성문 앞 촘촘한 굽이 → 앞에서 줄일지 성문 앞에서 막을지
    ('crystal_defense_gauntlet', 20261120, [[230, 1360], [2450, 1360], [2450, 440], [1700, 440], [1700, 1000], [1400, 1000], [1400, 440],
                                           [1100, 440], [1100, 1000], [800, 1000], [800, 440]], None),
    # 빗살 교차: 가운데 가로길을 세로 빗살 셋이 가로지름 → 교차로 세 곳
    ('crystal_defense_comb', 20261122, [[230, 900], [2400, 900], [2400, 440], [1900, 440], [1900, 1360], [1400, 1360], [1400, 440],
                                       [900, 440], [900, 1360], [500, 1360]], None),
    # X자 교차: 두 대각선이 한가운데서 엇갈림 → 가운데 한 곳이 최고 자리, 대각선 끝 쪽은 듬성듬성
    ('crystal_defense_cross_x', 20261124, [[230, 440], [2300, 1300], [2300, 440], [600, 1300], [1450, 1300]], None),
    # 격자: 가로 두 줄을 세로 길이 다섯 번 가로지름 → 교차로가 많아 어디를 먼저 잡을지 고름
    ('crystal_defense_grid', 20261125, [[230, 600], [2400, 600], [2400, 1200], [700, 1200], [700, 440], [1200, 440], [1200, 1400],
                                       [1700, 1400], [1700, 440], [2100, 440]], None),
    # ---- 여러 길 (킹덤 러시 식: 동굴 여럿·갈림길·성문 여럿) · 몬스터는 길을 번갈아 씀
    # 두 동굴 합류: 위·아래 동굴 길이 왼쪽에서 만나 한 길로 → 만나는 곳이 길목, 그 전엔 두 갈래를 따로 막아야 함
    ('crystal_defense_merge', 20261126, [[[230, 440], [900, 440], [900, 900], [1400, 900], [1400, 440], [1900, 440], [1900, 1360], [2400, 1360], [2400, 700], [2640, 700]],
                                         [[230, 1360], [900, 1360], [900, 900], [1400, 900], [1400, 440], [1900, 440], [1900, 1360], [2400, 1360], [2400, 700], [2640, 700]]], None),
    # 갈림길: 한 동굴에서 위·아래 두 길로 갈라졌다가 성문 앞에서 다시 만남 → 갈라지기 전·다시 만난 뒤가 길목, 가운데 들판은 둘 다 멂
    ('crystal_defense_fork', 20261127, [[[230, 900], [700, 900], [700, 440], [1300, 440], [1300, 700], [1900, 700], [1900, 440], [2250, 440], [2250, 900], [2640, 900]],
                                        [[230, 900], [700, 900], [700, 1360], [1300, 1360], [1300, 1100], [1900, 1100], [1900, 1360], [2250, 1360], [2250, 900], [2640, 900]]], None),
    # 두 성문: 굽이진 한 길이 가운데서 위·아래 성문으로 갈라짐 → 갈라지기 전에 끝낼지, 두 성문을 나눠 지킬지
    ('crystal_defense_twogate', 20261128, [[[230, 900], [600, 900], [600, 440], [1000, 440], [1000, 1360], [1400, 1360], [1400, 900], [1800, 900], [1800, 440], [2640, 440]],
                                           [[230, 900], [600, 900], [600, 440], [1000, 440], [1000, 1360], [1400, 1360], [1400, 900], [1800, 900], [1800, 1360], [2640, 1360]]], None),
    # 세 동굴: 왼쪽 위·가운데·아래 동굴 길이 한가운데 광장에서 모임 → 광장 둘레가 최고 자리, 대신 세 갈래 초반은 비어 있음
    ('crystal_defense_hub', 20261129, [[[230, 440], [1200, 440], [1200, 900], [1800, 900], [1800, 440], [2300, 440], [2300, 1360], [2640, 1360]],
                                       [[230, 900], [1200, 900], [1800, 900], [1800, 440], [2300, 440], [2300, 1360], [2640, 1360]],
                                       [[230, 1360], [1200, 1360], [1200, 900], [1800, 900], [1800, 440], [2300, 440], [2300, 1360], [2640, 1360]]], None),
    # 바위 시야 (블룬스 시야 가림): 길 사이 큰 바위가 건너편 길을 가림 → 같은 줄이라도 바위 뒤 자리는 반쪽짜리
    ('crystal_defense_boulder', 20261131, [[230, 560], [2250, 560], [2250, 920], [640, 920], [640, 1280], [2640, 1280]], None,
     {'boulders': [[1050, 740, 95], [1800, 740, 95], [1350, 1100, 95], [2050, 1100, 95], [600, 740, 80]]}),
    # 고지대 (명일방주 고지대 칸): 가운데 언덕을 길이 세 면으로 감쌈 → 언덕 위 몇 자리가 세 면을 다 봄, 대신 자리가 적음
    ('crystal_defense_plateau', 20261201, [[230, 440], [800, 440], [800, 1360], [2200, 1360], [2200, 440], [2640, 440]], None,
     {'plateau': [[1050, 640, 1950, 1160]], 'high_pads': [[1300, 820], [1700, 820], [1500, 1020]]}),
    # 세 줄 레인 (식물 vs 좀비): 동굴 셋·성문 셋, 가운데서 세 줄이 좁게 모였다가 다시 벌어짐 → 모인 곳은 한 번에 세 줄, 벌어진 곳은 줄마다 따로
    ('crystal_defense_lanes', 20261202, [[[230, 440], [900, 440], [900, 660], [1800, 660], [1800, 440], [2640, 440]],
                                         [[230, 900], [2640, 900]],
                                         [[230, 1360], [900, 1360], [900, 1140], [1800, 1140], [1800, 1360], [2640, 1360]]], None),
]

GRASS = R('#15302d', '#1c3d32', '#254b34', '#305b37', '#3e6b3a', '#527d3f', '#6a9045', '#88a652', '#acbf68')
DIRT = R('#2e211f', '#43302a', '#5a3f2f', '#735235', '#8c663d', '#a57d4b', '#bf975e', '#d8b679')
CLIFF = R('#17141a', '#241f25', '#342c31', '#463b3d', '#5b4f4c', '#74675e', '#8f8172', '#ab9c88', '#c8baa3')
LEAF = R('#0a1a1a', '#0f2a24', '#16392b', '#1f4b31', '#2b6036', '#3b7539', '#518b3d', '#6ea145', '#93b955')
PINE = R('#081616', '#0c2322', '#123128', '#19412e', '#225234', '#2f653b', '#447a42')
WATER = R('#14243d', '#1b3656', '#26517a', '#3a7199', '#6aa0bf', '#b9dbe6')
VOID = R('#07030f', '#140827', '#24104a', '#3c1a73', '#6a35b0', '#a77bf2', '#e2d4ff')


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


def build_map(PATH, PADS, seed, fx=None):
    # PATH: 길 하나 [[x, y], ...] 또는 여러 길 [[[x, y], ...], ...] (갈림길·여러 동굴·여러 성문)
    rnd = random.Random(seed)
    ys, xs = np.mgrid[0:H, 0:W]
    cv = Canvas()
    img = cv.img
    paths = PATH if isinstance(PATH[0][0], (list, tuple)) else [PATH]
    ps = [[(x / 4, y / 4) for x, y in q] for q in paths]
    p = ps[0]
    starts = list(dict.fromkeys(q[0] for q in ps))
    ends = list(dict.fromkeys(q[-1] for q in ps))

    # ---- 1) 풀밭: 큰 무늬(밝은 빈터·어두운 수풀) + 높이 요철 + 왼쪽 위가 조금 밝음
    big = fbm(W, H, [90, 45], rnd)
    mid = fbm(W, H, [16, 8], rnd)
    hgt = fbm(W, H, [12, 6, 3], rnd)
    bl = bump_light(hgt)
    sun = np.clip(1 - (xs / W) * 0.25 - (ys / H) * 0.15, 0, 1)
    v = 0.18 + big * 0.42 + mid * 0.16 + (bl - 0.5) * 0.22 + sun * 0.12
    gk = pal_idx(v, 8, xs, ys)
    img[:] = np.array(GRASS, np.float32)[gk][:, :, :3]

    # ---- 2) 지그재그 흙길 한 줄 (가운데 밝고 가장자리 어두움) · 바퀴 자국 · 자갈 · 성문 앞은 돌길
    dist = np.full((H, W), 999.0)
    along = np.zeros((H, W))
    for p in ps:
        seg_len = [math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1]) for i in range(len(p) - 1)]
        total = sum(seg_len)
        acc = 0
        for i in range(len(p) - 1):
            d, t = seg_dist(xs, ys, *p[i], *p[i + 1])
            better = d < dist
            dist = np.where(better, d, dist)
            along = np.where(better, (acc + t * seg_len[i]) / total, along)
            acc += seg_len[i]
    p = ps[0]
    edge_n = fbm(W, H, [7, 3], rnd)
    rw = 12.5 + (edge_n - 0.5) * 3.5
    road = dist < rw
    dh = fbm(W, H, [5, 2], rnd)
    dlight = bump_light(dh)
    center = 1 - np.clip(dist / rw, 0, 1)
    dv = 0.25 + center * 0.3 + (dlight - 0.5) * 0.35 + dh * 0.15
    dk = pal_idx(dv, 7, xs, ys)
    img[road] = np.array(DIRT, np.float32)[dk][:, :, :3][road]
    rim = road & (dist > rw - 2.2)
    img[rim] = np.array(DIRT[1][:3], np.float32)
    lane_cells = road
    cv.keep |= dist < 18
    for (ax, ay), (bx, by) in [(q[i], q[i + 1]) for q in ps for i in range(len(q) - 1)]:
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
    for _ in range(1800):
        x, y = rnd.randint(0, W - 2), rnd.randint(0, H - 2)
        if road[y, x] and road[y + 1, x + 1]:
            img[y, x] = DIRT[7][:3] if rnd.random() < 0.5 else DIRT[6][:3]
            img[y + 1, x] = DIRT[1][:3]
    # 성문 앞(마지막 12%): 판석 돌길
    cob = road & (along > 0.88) & (dist < rw - 1.5)
    for gy in range(0, H, 4):
        for gx in range(0, W, 5):
            jx, jy = gx + (2 if (gy // 4) % 2 else 0), gy
            if not (0 <= jx < W - 4 and 0 <= jy < H - 3) or not cob[jy, jx]:
                continue
            if rnd.random() > (along[jy, jx] - 0.88) * 30:
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
    # 웅덩이 두 곳 (길 가운데쯤)
    for frac, rx in ((0.3, 5), (0.62, 4)):
        x_, y_, _, _ = lane_point(p, frac)
        ry = 2.6
        for y in range(int(y_ - ry - 1), int(y_ + ry + 2)):
            for x in range(int(x_ - rx - 1), int(x_ + rx + 2)):
                d = ((x - x_) / rx) ** 2 + ((y - y_) / ry) ** 2
                if d < 1 and road[y, x]:
                    img[y, x] = WATER[4 if (y < y_ - ry * 0.3 and x < x_) else 2 if d > 0.65 else 3][:3]
                elif d < 1.35 and road[y, x]:
                    img[y, x] = DIRT[1][:3]
    # 풀이 길 위로 비죽
    for _ in range(6000):
        x, y = rnd.randint(1, W - 2), rnd.randint(2, H - 3)
        if road[y, x] and not road[y - 2, x] and dist[y, x] > rw[y, x] - 2.5:
            for (dx, dy, k) in ((0, 0, 5), (0, -1, 6), (-1, -1, 4), (1, 0, 4)):
                if 0 <= x + dx < W:
                    img[y + dy, x + dx] = GRASS[k][:3]
        elif road[y, x] and not road[y + 2, x] and dist[y, x] > rw[y, x] - 2:
            img[y, x] = GRASS[3][:3]; img[y + 1, x] = GRASS[2][:3]

    # ---- 2b) 지형 (fx, 다른 타워 디펜스 참고): 고지대(명일방주 고지대 칸) · 강과 다리(블룬스·식물 vs 좀비 물 지형) ·
    #          큰 바위(블룬스 시야 가림). fx가 없는 맵은 그림이 그대로 (난수를 따로 씀)
    fx = fx or {}
    frnd = random.Random(seed + 1)
    for (x0, y0, x1, y1) in fx.get('plateau', ()):
        cx_, cy_, rx_, ry_ = (x0 + x1) / 8, (y0 + y1) / 8, (x1 - x0) / 8, (y1 - y0) / 8
        sup = lambda dy=0: ((xs - cx_) / rx_) ** 6 + ((ys - dy - cy_) / ry_) ** 6
        top = sup() < 1
        face = ~top & np.any([sup(d) < 1 for d in range(1, 8)], axis=0)
        ph = fbm(W, H, [8, 4, 2], frnd)
        img[top] = np.array(GRASS, np.float32)[np.clip(gk + 1, 0, 8)][top][:, :3]
        edge_ = top & ~((sup(-1) < 1) & (sup(1) < 1) & (((xs - 1 - cx_) / rx_) ** 6 + ((ys - cy_) / ry_) ** 6 < 1) & (((xs + 1 - cx_) / rx_) ** 6 + ((ys - cy_) / ry_) ** 6 < 1))
        img[edge_] = GRASS[8][:3]  # 윗면 가장자리 밝은 테
        img[~top & ~face & np.any([sup(d) < 1 for d in (-1, 0)], axis=0)] = CLIFF[2][:3]
        fk = np.clip((2 + ph * 4 + (bump_light(ph) - 0.5) * 3).astype(int), 1, 7)
        img[face] = np.array(CLIFF, np.float32)[fk][face][:, :3]
        img[face & ~np.any([sup(d) < 1 for d in range(1, 7)], axis=0)] = CLIFF[1][:3]  # 절벽 밑동
        for yy, xx in zip(*np.where(face)):
            if frnd.random() < 0.06:
                img[yy, xx] = C('#4c7a35')[:3]
        for yy, xx in zip(*np.where(~top & ~face & np.any([sup(d) < 1 for d in range(8, 13)], axis=0))):
            cv.shade(xx, yy, 0.45)
        cv.keep |= top | face
    for river in fx.get('river', ()):
        pts_, wd = river['pts'], river['w'] / 8
        rd = np.full((H, W), 999.0)
        for i in range(len(pts_) - 1):
            d, _ = seg_dist(xs, ys, pts_[i][0] / 4, pts_[i][1] / 4, pts_[i + 1][0] / 4, pts_[i + 1][1] / 4)
            rd = np.minimum(rd, d)
        wn = fbm(W, H, [6, 3], frnd)
        ww = wd + (wn - 0.5) * 3
        water = rd < ww
        bank = (rd < ww + 2.2) & ~water
        img[bank & ~road] = DIRT[2][:3]
        depth = np.clip(rd / ww, 0, 1)
        wk = np.clip((1 + depth * 2.4 + (wn - 0.5) * 1.2).astype(int), 0, 5)
        img[water] = np.array(WATER, np.float32)[wk][water][:, :3]
        for _ in range(900):
            x, y = frnd.randint(0, W - 4), frnd.randint(0, H - 1)
            if water[y, x] and water[y, x + 3] and depth[y, x] < 0.75:
                img[y, x:x + 3] = WATER[4 if frnd.random() < 0.7 else 5][:3]  # 물결
        bridge = water & (dist < rw + 1.5)
        for yy, xx in zip(*np.where(bridge)):
            edge = dist[yy, xx] > rw[yy, xx] - 1
            img[yy, xx] = WOOD[1 if edge else 2 if xx % 3 == 0 else 4 if (yy + xx // 3) % 5 else 3][:3]
        for yy, xx in zip(*np.where(bridge & (dist > rw - 1))):
            if yy + 1 < H and water[yy + 1, xx] and not bridge[yy + 1, xx]:
                cv.shade(xx, yy + 1, 0.5); cv.shade(xx, yy + 2, 0.3)
        cv.keep |= water | bank
        lane_cells = lane_cells | water
    for (bx_, by_, br_) in fx.get('boulders', ()):
        x, y, r = bx_ / 4, by_ / 4, br_ / 4
        cv.ellipse_shadow(x + r * 0.4, y + r * 0.55, r * 1.15, r * 0.45, 0.55)
        bh = fbm(W, H, [5, 2], frnd)
        for yy in range(int(y - r * 1.25), int(y + r * 0.6) + 1):
            for xx in range(int(x - r - 1), int(x + r + 2)):
                dx, dy = (xx - x) / r, (yy - y + r * 0.3) / (r * 0.95)
                dd = dx * dx + dy * dy
                if dd > 1 or not (0 <= xx < W and 0 <= yy < H):
                    continue
                lum = (-dx * 0.6 - dy * 0.8) * 0.4 + math.sqrt(1 - dd) * 0.4 + (bh[yy, xx] - 0.5) * 0.5 + 0.15
                k = int(np.clip(lum * 8, 1, 8))
                if dd > 0.86 and (dy > 0 or dx > 0.2):
                    k = 1
                elif abs((dx * 3 + dy * 2 + bh[yy, xx] * 2) % 1.6 - 0.8) < 0.05:
                    k = max(1, k - 3)  # 금
                img[yy, xx] = CLIFF[k][:3]
                if dy < -0.45 and dx < 0.2 and frnd.random() < 0.35:
                    img[yy, xx] = C('#4c7a35' if frnd.random() < 0.6 else '#5d8f3e')[:3]  # 이끼
        cv.keep[max(0, int(y - r * 1.4)):int(y + r + 2), max(0, int(x - r - 4)):int(x + r + 4)] = True

    # ---- 3) 포탑 받침돌: 둥근 판석 (위 면 밝게 · 앞 면 두께 · 오른쪽 아래 그림자) + 네 귀퉁이 작은 룬 돌
    for (wx, wy) in PADS:
        cx, cy = wx / 4, wy / 4 + 4
        cv.ellipse_shadow(cx + 3, cy + 3, 15, 6, 0.5)
    for (wx, wy) in PADS:
        cx, cy = wx / 4, wy / 4 + 4
        rx_, ry_ = 13.5, 6.2
        for y in range(int(cy - ry_ - 1), int(cy + ry_ + 4)):
            for x in range(int(cx - rx_ - 1), int(cx + rx_ + 2)):
                dx, dy = (x + 0.5 - cx) / rx_, (y + 0.5 - cy) / ry_
                dd = dx * dx + dy * dy
                if dd <= 1:
                    # 위 면: 판석 넷 (줄눈 십자) · 왼쪽 위 밝음
                    k = 5 if dx < -0.15 and dy < 0.1 else 4 if dx < 0.4 else 3
                    if abs(x + 0.5 - cx) < 0.7 or abs(y + 0.5 - cy) < 0.6:
                        k = 2
                    elif ((int(x) * 7 + int(y) * 3) % 11) == 0:
                        k = min(7, k + 1)
                    if dd > 0.8:
                        k = 6 if dy < 0 and dx < 0.3 else 2
                    img[y, x] = STONE[k][:3]
                else:
                    # 앞 면 두께 (3줄)
                    dy2 = (y + 0.5 - cy - 3) / ry_
                    if dx * dx + dy2 * dy2 <= 1 and y > cy:
                        img[y, x] = STONE[3 if dx < -0.3 else 2 if dx < 0.5 else 1][:3]
        img[int(cy + ry_ + 3), int(cx - 6):int(cx + 7)] = STONE[1][:3]
        # 룬 점 (가운데)
        img[int(cy), int(cx)] = RUNEC[3][:3]
        img[int(cy) - 1, int(cx)] = RUNEC[4][:3]
        cv.keep[int(cy - 20):int(cy + 12), int(cx - 18):int(cx + 18)] = True

    # ---- 4) 들어오는 동굴 (왼쪽 위): 요철 바위 언덕 + 오른쪽을 보는 입 + 쐐기 돌 아치 + 횃불 두 개 + 해골 깃발
    rock_h = fbm(W, H, [16, 8, 4, 2], rnd)
    rl = bump_light(rock_h * 1.6)
    for (mx, my) in starts:  # 동굴은 길마다 첫 점 (같은 자리는 한 번)
        fx_, fy_ = 1.0, 0.0
        hx, hy = mx - 18, my
        hrx, hry = 40, 46
        edge = value_noise(64, 1, 6, rnd)[0]
        for y in range(int(hy - hry - 6), int(hy + hry + 6)):
            for x in range(int(hx - hrx - 6), int(hx + hrx + 6)):
                if not (0 <= x < W and 0 <= y < H):
                    continue
                a = math.atan2(y - hy, x - hx)
                rr = 1 + (edge[int((a + math.pi) / (2 * math.pi) * 63)] - 0.5) * 0.35
                e = ((x - hx) / (hrx * rr)) ** 2 + ((y - hy) / (hry * rr)) ** 2
                if e > 1:
                    if e < 1.25:
                        cv.shade(x + 2, y + 2, 0.4)
                    continue
                dome = math.sqrt(max(0, 1 - e))
                lum = rl[y, x] * 0.55 + (-(x - hx) / hrx * 0.25 - (y - hy) / hry * 0.35) + dome * 0.35
                k = int(np.clip(1 + lum * 6, 1, 8))
                if e > 0.86:
                    k = min(k, 2)
                img[y, x] = CLIFF[k][:3]
                if dome > 0.6 and rnd.random() < 0.05:
                    img[y, x] = C('#4b6e36')[:3]
        ox, oy = mx - 4, my
        rx, ry = 15, 20
        for y in range(int(oy - ry - 7), int(oy + ry + 8)):
            for x in range(int(ox - rx - 7), int(ox + rx + 8)):
                if not (0 <= x < W and 0 <= y < H):
                    continue
                e = ((x - ox) / rx) ** 2 + ((y - oy) / ry) ** 2
                toward = ((x - ox) * fx_ + (y - oy) * fy_) / max(1, math.hypot(x - ox, y - oy))
                if e <= 1:
                    k = 0 if e < 0.5 else 1 if e < 0.78 else 2
                    if 0.45 < e < 0.56 and BAYER[y & 3, x & 3] < 0.5:
                        k = 1
                    img[y, x] = R('#040306', '#0b080c', '#171116')[k][:3]
                elif e <= 1.6 and toward < 0.55:
                    an = math.atan2(y - oy, x - ox)
                    block = int((an + math.pi) / (math.pi / 8))
                    lum = (-(x - ox) * 0.5 - (y - oy) * 0.9) / (rx + ry) + 0.5
                    k = int(np.clip(3 + lum * 4 + (block % 2) * 0.8, 2, 8))
                    if abs(((an + math.pi) % (math.pi / 8)) - 0.01) < 0.07 or abs(e - 1.0) < 0.09:
                        k = 1
                    img[y, x] = CLIFF[k][:3]
        for i_, c in enumerate(('#ff5a3d', '#c23a2a', '#8a2a22')):
            ex, ey = ox - (3 + i_ * 4), oy + (i_ - 1) * 5
            img[int(ey), int(ex)] = C(c)[:3]
            img[int(ey), int(ex + 3)] = C(c)[:3]
        for side in (-1, 1):
            tx, ty = int(ox + 6), int(oy + side * (ry + 7))
            for y in range(ty, ty + 9):
                img[y, tx] = WOOD[3][:3]; img[y, tx + 1] = WOOD[1][:3]
            for (dx, dy, c) in ((0, -1, RED[3]), (1, -1, RED[2]), (0, -2, AMBER[3]), (1, -2, RED[3]), (0, -3, AMBER[4]), (0, -4, AMBER[5]), (1, -3, AMBER[3])):
                img[ty + dy, tx + dx] = c[:3]
            cv.light.append((tx, ty - 3, 24, (255, 150, 60), 0.5))
        fxp, fyp = int(hx - 6), int(hy - hry + 2)
        for y in range(fyp, fyp + 16):
            img[y, fxp] = WOOD[2][:3]
        for y in range(fyp + 1, fyp + 8):
            for x in range(fxp + 1, fxp + 7 - (y - fyp) // 3):
                img[y, x] = CLOTH_R[2 if x < fxp + 4 else 1][:3]
        img[fyp + 3, fxp + 2] = C('#e8e2d0')[:3]; img[fyp + 3, fxp + 3] = C('#e8e2d0')[:3]; img[fyp + 4, fxp + 2] = C('#e8e2d0')[:3]
        for _ in range(6):
            t_ = rnd.uniform(8, 34)
            bx_, by_ = int(ox + t_), int(oy + rnd.uniform(-8, 8))
            if 0 <= bx_ < W - 1 and 0 <= by_ < H and road[by_, bx_]:
                img[by_, bx_] = C('#e2dccb')[:3]; img[by_, bx_ + 1] = C('#b9b19c')[:3]
        cv.keep[max(0, int(hy - hry - 12)):int(hy + hry + 12), max(0, int(hx - hrx - 12)):int(hx + hrx + 12)] = True

    # ---- 5) 나가는 성문 (오른쪽 아래): 돌 아치 + 보랏빛 차원문 소용돌이 + 양옆 화로 · 몬스터가 여기로 빠져나가면 게이지가 깎임
    for (gx, gy) in ends:  # 성문은 길마다 끝 점
        gx -= 6
        # 문 기둥 둘 (벽돌) + 위 아치
        for side in (-1, 1):
            x0 = int(gx - 4 + side * 16) - 3
            cv.ellipse_shadow(x0 + 6, gy + 18, 7, 3, 0.5)
            s = Spr(9, 44)
            s.cyl(1, 7, 4, 43, STONE[1:7])
            bricks(s, 1, 7, 6, 42, STONE, bh=3, bw=4, seed=side + 5, mossy=True)
            s.rect(0, 0, 8, 3, STONE[5]); s.rect(0, 0, 8, 0, STONE[7])
            s.outline()
            cv.blit(s, x0, int(gy - 26))
        for a in range(0, 181, 3):
            ang = math.radians(180 + a)
            for rr_ in range(13, 19):
                x = gx - 4 + math.cos(ang) * rr_ * 1.05
                y = gy - 24 + math.sin(ang) * rr_ * 0.9
                k = 6 if rr_ > 16 and a < 90 else 5 if rr_ > 15 else 4 if a < 90 else 3
                if (a // 15) % 2 == 0 and rr_ in (13, 18):
                    k = 2
                cv.put(x, y, STONE[k])
        # 차원문 (문 안쪽 타원 소용돌이)
        for y in range(int(gy - 38), int(gy + 18)):
            for x in range(int(gx - 17), int(gx + 10)):
                dx, dy = (x + 0.5 - (gx - 4)) / 12.5, (y + 0.5 - (gy - 10)) / 27
                dd = dx * dx + dy * dy
                if dd > 1:
                    continue
                an = math.atan2(dy, dx)
                swirl = (an * 3 + math.sqrt(dd) * 9) % (2 * math.pi)
                k = int(np.clip((1 - dd) * 3 + (1.5 if swirl < 1.2 else 0) + BAYER[y & 3, x & 3] * 0.8, 0, 6))
                cv.put(x, y, VOID[k])
        cv.light.append((gx - 4, gy - 10, 60, (170, 120, 255), 0.55))
        for side in (-1, 1):
            bx, by = int(gx - 4 + side * 27), int(gy + 12)
            cv.ellipse_shadow(bx + 2, by + 8, 6, 2, 0.5)
            s = Spr(11, 16)
            s.rect(1, 4, 9, 6, IRON[4]); s.rect(1, 4, 9, 4, IRON[6]); s.rect(2, 7, 8, 7, IRON[2])
            s.rect(4, 8, 6, 13, IRON[3]); s.rect(4, 8, 4, 13, IRON[5]); s.rect(2, 14, 8, 14, IRON[2])
            for (x, y, c) in ((5, 3, RED[3]), (4, 3, RED[2]), (6, 3, RED[2]), (5, 2, AMBER[4]), (4, 2, RED[4]), (6, 1, AMBER[4]), (5, 1, AMBER[5]), (5, 0, AMBER[3])):
                s.px(x, y, c)
            s.outline()
            cv.blit(s, bx - 5, by - 6)
            cv.light.append((bx, by - 4, 30, (255, 150, 60), 0.55))
        cv.keep[int(gy - 48):int(gy + 30), int(gx - 40):W] = True


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


    # ---- 6) 숲 테두리 (위·아래·오른쪽 띠) · 싸움터 안쪽은 낮은 덤불·바위·꽃만 (유닛·포탑을 가리지 않게)
    items = []
    for x in range(-8, W + 8, 13):
        items.append(('tree', x + rnd.uniform(-4, 4), rnd.uniform(34, 56), rnd.uniform(9, 13)))
        items.append(('tree' if rnd.random() < 0.7 else 'pine', x + rnd.uniform(-4, 4), rnd.uniform(14, 32), rnd.uniform(9, 12)))
        items.append(('tree', x + rnd.uniform(-4, 4), rnd.uniform(436, 458), rnd.uniform(10, 13)))
        if rnd.random() < 0.5:
            items.append(('pine', x + rnd.uniform(-4, 4), rnd.uniform(446, 462), rnd.uniform(20, 26)))
    for y in range(60, 440, 15):
        items.append(('tree' if rnd.random() < 0.6 else 'pine', rnd.uniform(-4, 12), y + rnd.uniform(-5, 5), rnd.uniform(9, 12)))
        items.append(('tree' if rnd.random() < 0.6 else 'pine', rnd.uniform(708, 724), y + rnd.uniform(-5, 5), rnd.uniform(9, 12)))
    for (x, y) in ((40, 250), (52, 300), (30, 380), (110, 400), (690, 120), (685, 200), (600, 412), (300, 418)):
        items.append(('tree', x + rnd.uniform(-4, 4), y + rnd.uniform(-4, 4), rnd.uniform(8, 11)))
    for _ in range(40):
        items.append(('bush', rnd.randint(60, 650), rnd.randint(70, 400), rnd.uniform(2.6, 4)))
    for _ in range(36):
        items.append(('rock', rnd.randint(60, 650), rnd.randint(70, 400), rnd.uniform(2, 3.8)))
    for (x, y) in ((90, 200), (560, 410)):
        items.append(('log', x, y, 0))
    for (x, y) in ((140, 64), (480, 62), (70, 330)):
        items.append(('stump', x, y, 0))
    for (x, y) in ((92, 168), (100, 176), (205, 410)):
        items.append(('crate', x, y, 0))

    for (kind, x, y, r) in sorted(items, key=lambda it: it[2]):
        xi, yi = int(min(W - 1, max(0, x))), int(min(H - 1, max(0, y)))
        if kind in ('tree', 'pine'):
            if cv.keep[yi, xi]:
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
    tw = build_towers()
    tw.save(OUT_TOWERS, optimize=True)
    only = os.environ.get('ONLY')
    for key, seed, path, pads, *fx in LAYOUTS + (CANDIDATES if only else []):
        if only and key not in only.split(','):
            continue
        fx = fx[0] if fx else None
        if not pads:
            high = (fx or {}).get('high_pads', [])  # 고지대 위 자리 (길에서 멀어 사거리가 늘어야 쓸모 있음 → 게임에서 고지대 사거리 보너스)
            n = 22 - len(high)
            pads = auto_pads(path, n, avoid=high, fx=fx)
            if len(pads) < n:  # 자리가 모자라면 조금 촘촘히
                pads = auto_pads(path, n, sep=(240, 200), near=(115, 340), avoid=high, fx=fx)
            pads = sorted([list(q) for q in high] + [list(q) for q in pads], key=lambda q: (q[1], q[0]))
        # 용병 처음 자리 5곳: 받침돌 사이 길가
        spots = auto_pads(path, 5, near=(90, 220), sep=(320, 260), avoid=[(q[0], q[1]) for q in pads], fx=fx) if key != 'crystal_defense' else [[1210, 740], [1510, 740], [1350, 1100], [910, 740], [1650, 1100]]
        m = build_map(path, pads, seed, fx)
        out = os.path.join(ROOT, f'assets/maps/{key}.webp')
        m.save(out, 'WEBP', lossless=True, quality=100, method=6)
        print(key, m.size, os.path.getsize(out))
        print(f"  {{ key: '{key}', path: {json.dumps(path)}, pads: {json.dumps([list(q) for q in pads])}, mercs: {json.dumps([list(q) for q in spots])}{', fx: ' + json.dumps(fx) if fx else ''} }},  # {len(pads)}곳")
        if PREVIEW:
            m.resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(PREVIEW, f'_preview_{key}.png'))
    print('towers', tw.size, os.path.getsize(OUT_TOWERS))
    if PREVIEW:
        os.makedirs(PREVIEW, exist_ok=True)
        bg = Image.new('RGBA', (tw.width * 3, tw.height * 3), (52, 78, 56, 255))
        bg.alpha_composite(tw.resize((tw.width * 3, tw.height * 3), Image.NEAREST))
        bg.save(os.path.join(PREVIEW, '_preview_defense_towers.png'))


if __name__ == '__main__':
    main()

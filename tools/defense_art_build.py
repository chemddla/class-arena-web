# 💎 수정 방어전 그림 → assets/maps/crystal_defense.webp · assets/sprites/fx/defense_towers.png · assets/sprites/fx/defense_crystal.png
# 사용: python tools/defense_art_build.py [미리보기 폴더]
#
# 모두 코드로 찍는 도트 그림 (pixelfx 작법: 1px 어두운 테두리 · 왼쪽 위 빛 · 색 단계 4~5개 · 바이어 디더).
# - 맵: 720×450 도트 (월드 2880×1800의 1/4). 게임은 이미지 다듬기 끄고 4배로 그림 → 칸이 또렷함.
#   길·동굴·시설 받침돌·수정 광장 좌표는 index.html의 DEFENSE_LANES · defenseMakeSlots · DEFENSE_CRYSTAL과 같음 (월드 ÷ 4).
# - 시설 시트: 칸 36×52, 가로 6칸 = [1단계 평소, 1단계 공격, 2단계 평소, 2단계 공격, 3단계 평소, 3단계 공격],
#   세로 6줄 = 화살탑 · 마법탑 · 서리탑 · 방벽 · 덫 · 치유 토템. 방벽의 '공격' 칸 = 부서진 모습, 덫 = 터진 뒤(빈 덫).
#   발 위치 = 칸 (18, 49). 게임에서 3배.
# - 수정 시트: 칸 32×56, 가로 4프레임(빛 흐름), 세로 3줄 = 성함 · 금 감(70% 아래) · 크게 금 감(30% 아래). 게임에서 3배.
import math, os, random, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_MAP = os.path.join(ROOT, 'assets/maps/crystal_defense.webp')
OUT_TOWERS = os.path.join(ROOT, 'assets/sprites/fx/defense_towers.png')
OUT_CRYSTAL = os.path.join(ROOT, 'assets/sprites/fx/defense_crystal.png')
PREVIEW = sys.argv[1] if len(sys.argv) > 1 else None


def C(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def ramp(*hs):
    return [C(h) for h in hs]


OUTLINE = C('#15111d')
STONE = ramp('#24262f', '#3a3d4c', '#565b6e', '#7d8398', '#aab0c4', '#d3d7e3')
WOOD = ramp('#2e1a0b', '#4d2e14', '#71451f', '#99632f', '#c48a4a', '#e2b276')
AMBER = ramp('#6b2f07', '#b4570c', '#ef8f12', '#fbbf3c', '#fde9a6')
PURPLE = ramp('#24104f', '#4b1fa3', '#7c4ae0', '#ad8cf7', '#ddd0ff', '#ffffff')
ICE = ramp('#16325f', '#2361a6', '#3fa1e0', '#86d2f7', '#cdefff', '#ffffff')
GREEN = ramp('#053b2c', '#0b6b48', '#14a06a', '#4fd39a', '#b4f5d6', '#ffffff')
IRON = ramp('#1b1d24', '#33363f', '#555a66', '#8a909c', '#c8ccd4')
RED = ramp('#4a0b0b', '#8f1717', '#d83a2a', '#ff7a4a', '#ffd0a0')
GOLD = ramp('#5c3a06', '#9a6510', '#d39a22', '#f6cf4f', '#fff2b0')
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


# ---------------------------------------------------------------- 공용 그리기
class Spr:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), np.uint8)

    def px(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h and c is not None:
            self.a[y, x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.px(x, y, c)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def disc(self, cx, cy, r, pal, light=(-0.6, -0.7)):
        """공 모양: 왼쪽 위가 밝은 4~5단 음영."""
        n = len(pal)
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
                d = dx * dx + dy * dy
                if d > 1:
                    continue
                z = math.sqrt(max(0, 1 - d))
                lum = max(0, (dx * light[0] + dy * light[1]) * 0.7 + z * 0.55)
                k = min(n - 1, int(lum * (n - 0.01)))
                self.px(x, y, pal[k])

    def line(self, x0, y0, x1, y1, c):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            t = i / max(1, n)
            self.px(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, c)

    def outline(self, c=OUTLINE):
        a = self.a
        op = a[:, :, 3] > 0
        ring = np.zeros_like(op)
        ring[1:, :] |= op[:-1, :]
        ring[:-1, :] |= op[1:, :]
        ring[:, 1:] |= op[:, :-1]
        ring[:, :-1] |= op[:, 1:]
        ring &= ~op
        a[ring] = c

    def glow_dot(self, x, y, c):
        self.px(x, y, c)


# 돌 받침 (탑 공통): 사다리꼴, 벽돌 줄, 왼쪽 면 밝게
def plinth(s, lv, top=40, bottom=49, trim=None):
    half_b, half_t = 13 + lv, 11 + lv
    for y in range(top, bottom + 1):
        t = (y - top) / max(1, bottom - top)
        half = half_t + (half_b - half_t) * t
        for x in range(int(18 - half), int(18 + half) + 1):
            u = (x - (18 - half)) / (2 * half)
            k = 4 if u < 0.18 else 3 if u < 0.55 else 2 if u < 0.85 else 1
            if y == top:
                k = 5
            s.px(x, y, STONE[k])
    # 벽돌 줄
    for y in range(top + 3, bottom, 3):
        off = 0 if (y // 3) % 2 else 2
        for x in range(int(18 - half_b + 1), int(18 + half_b)):
            if s.a[y, x, 3] and (x + off) % 5 == 0:
                s.px(x, y, STONE[1])
        s.hline(18 - half_t, 18 + half_t, y, None)
    if trim:
        for x in range(18 - half_t, 18 + half_t + 1):
            s.px(x, top + 1, trim[3] if x < 18 else trim[2])
            if lv >= 3:
                s.px(x, bottom - 1, trim[2] if x < 18 else trim[1])


# ---------------------------------------------------------------- 시설
def arrow_tower(lv, fire):
    s = Spr(36, 52)
    plinth(s, lv, trim=GOLD if lv >= 3 else IRON if lv >= 2 else None)
    if lv == 1:
        # 나무 망루: 기둥 4개 + X 버팀대 + 판자 바닥
        for x in (9, 26):
            s.rect(x, 20, x + 1, 39, WOOD[3] if x < 18 else WOOD[2])
        for x in (13, 22):
            s.rect(x, 22, x, 39, WOOD[1])
        s.line(10, 24, 26, 37, WOOD[2])
        s.line(26, 24, 10, 37, WOOD[1])
        s.rect(7, 18, 28, 20, WOOD[4])
        s.hline(7, 28, 21, WOOD[1])
        for x in range(8, 28, 3):
            s.px(x, 19, WOOD[2])
        top = 18
    else:
        # 돌 탑 몸통
        y0 = 23 if lv == 2 else 19
        for y in range(y0, 40):
            for x in range(10, 27):
                u = (x - 10) / 16
                k = 4 if u < 0.2 else 3 if u < 0.6 else 2 if u < 0.9 else 1
                s.px(x, y, STONE[k])
        for y in range(y0 + 3, 40, 4):
            s.hline(10, 26, y, STONE[1])
            off = 0 if (y // 4) % 2 else 3
            for x in range(11 + off, 26, 6):
                s.vline(x, y - 3, y - 1, STONE[1])
        # 화살 구멍
        s.rect(17, y0 + 6, 18, y0 + 10, OUTLINE)
        # 흉벽 (톱니)
        s.rect(8, y0 - 3, 28, y0, STONE[3])
        for x in range(8, 29, 4):
            s.rect(x, y0 - 6, x + 1, y0 - 4, STONE[4] if x < 18 else STONE[2])
        s.hline(8, 28, y0, STONE[1])
        top = y0 - 3
        if lv == 2:
            # 아래는 나무 다리
            pass
    # 석궁/노포 (위)
    by = top - 4
    stock = WOOD
    s.rect(11, by, 25, by + 1, stock[3])
    s.hline(11, 25, by + 2, stock[1])
    bow = GOLD if lv >= 3 else IRON
    if not fire:
        s.line(9, by - 4, 13, by, bow[3]); s.line(27, by - 4, 23, by, bow[2])
        s.line(9, by - 4, 18, by + 1, C('#e9e2cf'))  # 당긴 시위
        s.line(27, by - 4, 18, by + 1, C('#e9e2cf'))
        s.hline(18, 30, by, IRON[4])  # 화살
        s.px(31, by, IRON[2]); s.px(30, by - 1, IRON[3]); s.px(30, by + 1, IRON[3])
        if lv >= 3:
            s.hline(18, 30, by - 2, IRON[4]); s.px(31, by - 2, IRON[2])
    else:
        s.line(9, by - 5, 12, by, bow[3]); s.line(27, by - 5, 24, by, bow[2])
        s.line(9, by - 5, 27, by - 5, C('#e9e2cf'))  # 놓은 시위
        for i, c in enumerate((AMBER[4], AMBER[3], AMBER[2])):  # 쏜 순간 섬광
            s.px(32 + i, by, c)
        s.px(33, by - 1, AMBER[3]); s.px(33, by + 1, AMBER[3]); s.px(34, by - 2, AMBER[2]); s.px(34, by + 2, AMBER[2])
    # 깃발
    if lv >= 2:
        ft = max(1, top - 13)
        s.vline(6, ft, top, WOOD[2])
        flag = AMBER
        for y in range(ft, ft + 6):
            w = 5 - (y - ft) // 2
            s.hline(7, 7 + w, y, flag[3] if y < ft + 3 else flag[2])
        s.px(7, ft, flag[4])
        if lv >= 3:
            s.px(9, ft + 2, GOLD[4]); s.px(10, ft + 2, GOLD[3])
    s.outline()
    return s


def magic_tower(lv, fire):
    s = Spr(36, 52)
    plinth(s, lv, trim=GOLD if lv >= 3 else PURPLE if lv >= 2 else None)
    # 가늘어지는 돌 첨탑
    y_top = 18 - (lv - 1) * 2
    for y in range(y_top, 40):
        t = (y - y_top) / (40 - y_top)
        half = 3 + t * 4
        for x in range(int(18 - half), int(18 + half) + 1):
            u = (x - (18 - half)) / (2 * half)
            k = 4 if u < 0.25 else 3 if u < 0.6 else 2 if u < 0.85 else 1
            s.px(x, y, STONE[k])
    # 룬 (빛나는 점)
    rune = PURPLE[4] if fire else PURPLE[3]
    for y in range(y_top + 4, 38, 5):
        s.px(18, y, rune); s.px(17, y + 1, PURPLE[2]); s.px(19, y + 1, PURPLE[2])
    # 받침 갈퀴
    if lv >= 2:
        claw = GOLD if lv >= 3 else STONE
        for sx in (-1, 1):
            s.line(18 + sx * 3, y_top + 2, 18 + sx * 8, y_top - 6, claw[3] if sx < 0 else claw[2])
            s.px(18 + sx * 8, y_top - 7, claw[4])
    # 떠 있는 구슬
    r = 4 + (1 if lv >= 3 else 0)
    oy = y_top - 7 - r // 2
    pal = PURPLE[1:] if fire else PURPLE[:5]
    s.disc(18, oy, r + (1 if fire else 0), pal)
    s.px(16, oy - 2, PURPLE[5])
    if fire:
        for a in range(8):
            ang = a * math.pi / 4
            for d in (r + 3, r + 4):
                s.px(18 + math.cos(ang) * d, oy + math.sin(ang) * d, PURPLE[4] if d == r + 3 else PURPLE[3])
    if lv >= 3:
        # 도는 반짝이 3개
        for a in (0.3, 2.4, 4.4):
            ang = a + (0.6 if fire else 0)
            s.px(18 + math.cos(ang) * (r + 6), oy + math.sin(ang) * (r + 3), GOLD[4])
    s.outline()
    return s


def frost_tower(lv, fire):
    s = Spr(36, 52)
    plinth(s, lv, trim=GOLD if lv >= 3 else ICE if lv >= 2 else None)

    def shard(cx, top, bottom, half):
        for y in range(top, bottom + 1):
            t = (y - top) / max(1, bottom - top)
            w = half * min(1, t * 3) if t < 0.33 else half
            for x in range(int(cx - w), int(cx + w) + 1):
                u = (x - (cx - w)) / max(1, 2 * w)
                k = 4 if u < 0.3 else 3 if u < 0.55 else 2 if u < 0.85 else 1
                if fire:
                    k = min(5, k + 1)
                s.px(x, y, ICE[k])
        s.vline(cx, top + 2, bottom - 2, ICE[5] if fire else ICE[4])

    main_top = 12 - (lv - 1) * 3
    shard(18, main_top, 40, 4)
    shard(12, 24 - lv, 40, 2)
    shard(24, 26 - lv, 40, 2)
    if lv >= 2:
        shard(9, 31, 40, 1)
        shard(27, 30, 40, 1)
    if lv >= 3:
        # 위에 떠 있는 얼음 고리
        for a in range(16):
            ang = a * math.pi / 8
            s.px(18 + math.cos(ang) * 9, main_top - 2 + math.sin(ang) * 3, ICE[4] if a < 8 else ICE[2])
        s.rect(14, 39, 22, 40, ICE[5])  # 눈 덮인 받침
    if fire:
        for (x, y) in ((8, main_top + 4), (29, main_top + 8), (18, main_top - 5), (6, main_top + 14), (31, main_top + 15)):
            s.px(x, y, ICE[5]); s.px(x - 1, y, ICE[3]); s.px(x + 1, y, ICE[3]); s.px(x, y - 1, ICE[3]); s.px(x, y + 1, ICE[3])
    s.outline()
    return s


def wall_seg(lv, broken):
    s = Spr(36, 52)
    if broken:
        # 무너진 잔해 더미
        rnd = random.Random(lv * 7 + 1)
        pal = WOOD if lv == 1 else STONE
        for _ in range(16):
            x = rnd.randint(10, 25); y = rnd.randint(40, 47); r = rnd.choice((1.5, 2, 2.5))
            s.disc(x, y, r, pal[1:5])
        if lv == 1:
            s.line(9, 44, 18, 38, WOOD[3]); s.line(20, 39, 27, 46, WOOD[2])
        s.outline()
        return s
    x0, x1 = 13, 23
    top = 6
    if lv == 1:
        # 나무 말뚝 울타리: 세로 판자 + 뾰족한 끝 + 가로 띠
        for x in range(x0, x1 + 1):
            col = (x - x0) % 3
            k = 4 if col == 0 else 3 if col == 1 else 2
            if x == x1:
                k = 1
            h = top + (0 if col == 1 else 2)
            s.vline(x, h, 48, WOOD[k])
            if col == 1:
                s.px(x, h - 1, WOOD[4]); s.px(x, h - 2, WOOD[5])
        for y in (14, 38):
            s.hline(x0 - 1, x1 + 1, y, WOOD[1]); s.hline(x0 - 1, x1 + 1, y + 1, WOOD[2])
    else:
        # 돌 벽: 위 면(밝음) + 앞 면 벽돌
        s.rect(x0, top, x1, top + 3, STONE[5])
        s.hline(x0, x1, top + 3, STONE[4])
        for y in range(top + 4, 49):
            for x in range(x0, x1 + 1):
                u = (x - x0) / (x1 - x0)
                k = 3 if u < 0.3 else 2 if u < 0.8 else 1
                s.px(x, y, STONE[k])
        for y in range(top + 7, 49, 4):
            s.hline(x0, x1, y, STONE[1])
            off = 0 if (y // 4) % 2 else 3
            for x in range(x0 + off, x1, 5):
                s.vline(x, y + 1, y + 3, STONE[1])
        # 흉벽
        for y in range(top - 3, top):
            for x in (x0, x0 + 4, x0 + 8):
                s.rect(x, y, x + 2, y, STONE[4] if x < 18 else STONE[3])
        if lv >= 3:
            # 오른쪽(몬스터 쪽) 쇠가시 + 금 리벳
            for y in range(top + 6, 47, 6):
                s.hline(x1 + 1, x1 + 5, y, IRON[3]); s.px(x1 + 6, y, IRON[4]); s.px(x1 + 1, y + 1, IRON[1])
            for y in range(top + 9, 47, 8):
                s.px(x0 + 2, y, GOLD[4]); s.px(x0 + 7, y, GOLD[3])
    s.outline()
    return s


def trap(lv, sprung):
    s = Spr(36, 52)
    cy = 44
    # 바닥 판
    w = 7 + lv
    for y in range(cy - 3, cy + 4):
        for x in range(18 - w, 18 + w + 1):
            if ((x - 18) / w) ** 2 + ((y - cy) / 3.5) ** 2 <= 1:
                s.px(x, y, IRON[1] if y > cy else IRON[2])
    if lv >= 3:
        for a in range(6):
            ang = a * math.pi / 3
            s.px(18 + math.cos(ang) * (w - 2), cy + math.sin(ang) * 2, RED[3] if not sprung else RED[1])
    if not sprung:
        # 벌린 톱니 턱 두 개
        for side in (-1, 1):
            for i in range(w - 1):
                x = 18 + side * (i + 1)
                s.px(x, cy - 3 - (1 if i % 2 == 0 else 0), IRON[4] if side < 0 else IRON[3])
                s.px(x, cy - 2, IRON[2])
        s.disc(18, cy, 1.6, [RED[2], RED[3], RED[4]] if lv >= 2 else IRON[2:5])
        if lv >= 2:
            s.px(18 - w, cy - 4, IRON[4]); s.px(18 + w, cy - 4, IRON[4])
    else:
        # 닫힌 턱 (다 쓴 덫)
        for i in range(-w + 2, w - 1):
            s.px(18 + i, cy - 2, IRON[2] if i % 2 else IRON[3])
            s.px(18 + i, cy - 3, IRON[1])
    s.outline()
    return s


def totem(lv, fire):
    s = Spr(36, 52)
    top = 16 - (lv - 1) * 3
    for y in range(top, 49):
        for x in range(14, 23):
            u = (x - 14) / 8
            k = 4 if u < 0.25 else 3 if u < 0.6 else 2 if u < 0.9 else 1
            s.px(x, y, WOOD[k])
    # 얼굴 조각 (위에서부터)
    for fy in range(top + 4, 46, 11):
        s.rect(15, fy, 16, fy + 1, OUTLINE); s.rect(20, fy, 21, fy + 1, OUTLINE)
        s.px(16, fy, GREEN[4] if fire else GREEN[3]); s.px(21, fy, GREEN[4] if fire else GREEN[3])
        s.hline(16, 20, fy + 4, WOOD[1]); s.hline(17, 19, fy + 5, OUTLINE)
        s.hline(14, 22, fy + 8, WOOD[1])
    # 날개(잎)
    if lv >= 2:
        for side in (-1, 1):
            for i in range(6):
                x = 18 + side * (5 + i)
                y0 = top + 6 + i // 2
                s.vline(x, y0, y0 + 4 - i // 2, GREEN[3] if side < 0 else GREEN[2])
            s.px(18 + side * 10, top + 9, GREEN[4])
    # 꼭대기 보석
    s.disc(18, top - 3, 3 + (1 if fire else 0), GREEN[1:6] if fire else GREEN[:5])
    s.px(17, top - 4, GREEN[5])
    if lv >= 3:
        for a in range(10):
            ang = a * math.pi / 5
            s.px(18 + math.cos(ang) * 7, top - 3 + math.sin(ang) * 7, GOLD[4] if a % 2 else GOLD[2])
    if fire:
        for (x, y) in ((8, top + 2), (28, top + 4), (11, top - 8), (25, top - 7)):
            s.px(x, y, GREEN[5]); s.px(x, y + 1, GREEN[3])
    s.outline()
    return s


def build_towers():
    makers = [arrow_tower, magic_tower, frost_tower, wall_seg, trap, totem]
    sheet = np.zeros((52 * 6, 36 * 6, 4), np.uint8)
    for r, mk in enumerate(makers):
        for lv in (1, 2, 3):
            for f in (0, 1):
                s = mk(lv, bool(f))
                c = (lv - 1) * 2 + f
                sheet[r * 52:(r + 1) * 52, c * 36:(c + 1) * 36] = s.a
    return Image.fromarray(sheet, 'RGBA')


# ---------------------------------------------------------------- 수정
CRYS = ramp('#0b2a55', '#124a8c', '#1f78c8', '#4fb3ee', '#a6e4ff', '#ffffff')
CRYS_HURT = ramp('#3a1240', '#6a1f63', '#a8337f', '#e06aa8', '#ffc0dc', '#ffffff')


def crystal(frame, dmg):
    s = Spr(32, 56)
    cx, top, mid, bot, half = 16, 3, 24, 50, 11
    pal = CRYS if dmg < 2 else [CRYS[0], CRYS[1], CRYS_HURT[2], CRYS[3], CRYS_HURT[4], CRYS[5]]
    band = 6 + frame * 7  # 빛 띠가 위에서 아래로 흐름
    for y in range(top, bot + 1):
        w = half * (y - top) / (mid - top) if y <= mid else half * (bot - y) / (bot - mid)
        for x in range(int(cx - w), int(cx + w) + 1):
            u = (x - (cx - w)) / max(1, 2 * w)
            # 면: 왼쪽 밝음 · 가운데 능선 · 오른쪽 어두움, 아래 절반은 한 단 어둡게
            k = 4 if u < 0.22 else 3 if u < 0.5 else 2 if u < 0.8 else 1
            if y > mid:
                k = max(0, k - 1)
            if abs(y - band - (x - cx) * 0.4) < 1.5 and 0.1 < u < 0.7:
                k = min(5, k + 2)
            s.px(x, y, pal[k])
        if top + 2 < y < bot - 2:
            s.px(cx, y, pal[4] if y < mid else pal[3])
    # 가로 능선
    for x in range(cx - half + 1, cx + half):
        s.px(x, mid, pal[3] if x < cx else pal[2])
    # 반짝임
    sp = [(10, 14), (21, 30), (13, 38), (19, 9)][frame]
    s.px(*sp, pal[5]); s.px(sp[0] - 1, sp[1], pal[4]); s.px(sp[0] + 1, sp[1], pal[4]); s.px(sp[0], sp[1] - 1, pal[4]); s.px(sp[0], sp[1] + 1, pal[4])
    # 금
    crack = C('#071226')
    if dmg >= 1:
        s.line(12, 16, 15, 22, crack); s.line(15, 22, 13, 27, crack); s.line(15, 22, 18, 24, crack)
    if dmg >= 2:
        s.line(20, 30, 17, 36, crack); s.line(17, 36, 19, 42, crack); s.line(10, 28, 13, 33, crack); s.line(21, 12, 19, 17, crack)
        s.px(19, 31, CRYS_HURT[4])
    s.outline(C('#061021'))
    return s


def build_crystal():
    sheet = np.zeros((56 * 3, 32 * 4, 4), np.uint8)
    for d in range(3):
        for f in range(4):
            sheet[d * 56:(d + 1) * 56, f * 32:(f + 1) * 32] = crystal(f, d).a
    return Image.fromarray(sheet, 'RGBA')


# ---------------------------------------------------------------- 맵
W, H = 720, 450
LANES = [
    [[2620, 430], [1950, 430], [1350, 500], [920, 690], [660, 850]],
    [[2620, 920], [1850, 970], [1250, 900], [780, 920]],
    [[2620, 1420], [1950, 1410], [1350, 1340], [920, 1150], [660, 990]],
]
CRYSTAL = (560, 920)


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


GRASS = [C('#1b3324'), C('#24462e'), C('#2f5a37'), C('#3d7040'), C('#52874a'), C('#73a65a')]
DIRT = [C('#3a2818'), C('#55391f'), C('#6f4c2a'), C('#8b6439'), C('#a77f4f'), C('#c9a374')]
ROCK = [C('#211d1c'), C('#36302d'), C('#4d4541'), C('#68605a'), C('#8c847c'), C('#b3aba2')]
LEAF = [C('#0c1d14'), C('#14301f'), C('#1e472b'), C('#2c6236'), C('#417f43'), C('#62a052')]
RUNE = [C('#0e3a52'), C('#1a6f93'), C('#38bdf8'), C('#a5e8ff')]


def value_noise(w, h, cell, rnd):
    gw, gh = w // cell + 2, h // cell + 2
    g = np.array([[rnd.random() for _ in range(gw)] for _ in range(gh)])
    ys, xs = np.mgrid[0:h, 0:w]
    fx, fy = xs / cell, ys / cell
    x0, y0 = fx.astype(int), fy.astype(int)
    tx, ty = fx - x0, fy - y0
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a = g[y0, x0] * (1 - tx) + g[y0, x0 + 1] * tx
    b = g[y0 + 1, x0] * (1 - tx) + g[y0 + 1, x0 + 1] * tx
    return a * (1 - ty) + b * ty


def seg_dist(xs, ys, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1
    t = np.clip(((xs - ax) * dx + (ys - ay) * dy) / L2, 0, 1)
    return np.hypot(xs - (ax + dx * t), ys - (ay + dy * t))


def pal_pick(pal, v, dither=True, xs=None, ys=None):
    """0~1 값을 색 단계로 (바이어 디더로 단계 사이를 섞음)."""
    n = len(pal)
    f = np.clip(v, 0, 0.999) * n
    k = f.astype(int)
    if dither:
        frac = f - k
        th = BAYER[ys & 3, xs & 3]
        k = np.where(frac > th, np.minimum(n - 1, k + 1), k)
    arr = np.array(pal, np.uint8)
    return arr[np.clip(k, 0, n - 1)]


def build_map():
    rnd = random.Random(20261110)
    ys, xs = np.mgrid[0:H, 0:W]
    img = np.zeros((H, W, 4), np.uint8)
    keep = np.zeros((H, W), bool)  # 장식을 놓으면 안 되는 곳 (길·광장·받침돌)

    # 1) 풀밭: 큰 무늬 + 잔무늬, 가장자리로 갈수록 어둡게
    n1 = value_noise(W, H, 48, rnd)
    n2 = value_noise(W, H, 9, rnd)
    edge = np.minimum.reduce([xs / 90, (W - xs) / 70, ys / 70, (H - ys) / 70])
    v = 0.22 + n1 * 0.32 + n2 * 0.14 + np.clip(edge, 0, 1) * 0.18
    img[:] = pal_pick(GRASS[:5], v, True, xs, ys)

    # 2) 길: 흙 + 바퀴 자국 + 풀 경계 디더
    cr = (CRYSTAL[0] / 4, CRYSTAL[1] / 4)
    dist = np.full((H, W), 999.0)
    for pts in LANES:
        p = [(x / 4, y / 4) for x, y in pts] + [cr]
        for i in range(len(p) - 1):
            dist = np.minimum(dist, seg_dist(xs, ys, *p[i], *p[i + 1]))
    nd = value_noise(W, H, 6, rnd)
    road = dist < 12.5 + (nd - 0.5) * 3
    dv = 0.35 + nd * 0.3 + (1 - np.clip(dist / 12, 0, 1)) * 0.15
    img[road] = pal_pick(DIRT[1:5], dv, True, xs, ys)[road]
    rim = (dist >= 11 + (nd - 0.5) * 3) & (dist < 14.5 + (nd - 0.5) * 3)
    rimmix = rim & (BAYER[ys & 3, xs & 3] < 0.5)
    img[rimmix] = DIRT[1]
    keep |= dist < 17
    # 바퀴 자국 + 자갈
    for pts in LANES:
        p = [(x / 4, y / 4) for x, y in pts] + [cr]
        for i in range(len(p) - 1):
            (ax, ay), (bx, by) = p[i], p[i + 1]
            ln = math.hypot(bx - ax, by - ay)
            nx, ny = -(by - ay) / ln, (bx - ax) / ln
            for s in range(int(ln)):
                t = s / ln
                x, y = ax + (bx - ax) * t, ay + (by - ay) * t
                for off in (-5, 5):
                    if rnd.random() < 0.75:
                        px, py = int(x + nx * off), int(y + ny * off)
                        if 0 <= px < W and 0 <= py < H:
                            img[py, px] = DIRT[1]
                if rnd.random() < 0.12:
                    o = rnd.uniform(-10, 10)
                    px, py = int(x + nx * o), int(y + ny * o)
                    if 0 <= px < W - 1 and 0 <= py < H - 1:
                        img[py, px] = DIRT[5]; img[py + 1, px] = DIRT[2]

    # 3) 오른쪽 바위 절벽 + 동굴 3곳
    cliff_x = 646 + (value_noise(1, H, 14, rnd)[:, 0] - 0.5) * 18
    for y in range(H):
        for x in range(int(cliff_x[y]), W):
            u = (x - cliff_x[y]) / 40
            k = 4 if u < 0.06 else 3 if u < 0.25 else 2 if (x + y * 3) % 11 else 1
            img[y, x] = ROCK[k]
        img[y, max(0, int(cliff_x[y]) - 1)] = ROCK[0]
    # 바위 결
    for _ in range(140):
        x, y = rnd.randint(650, W - 2), rnd.randint(0, H - 2)
        L = rnd.randint(3, 9)
        for i in range(L):
            if x + i < W:
                img[y, x + i] = ROCK[1]
                if y > 0:
                    img[y - 1, x + i] = ROCK[3] if rnd.random() < 0.5 else img[y - 1, x + i]
    for pts in LANES:
        mx, my = pts[0][0] / 4 + 4, pts[0][1] / 4
        for y in range(int(my - 30), int(my + 31)):
            for x in range(int(mx - 26), int(mx + 30)):
                e = ((x - mx) / 24) ** 2 + ((y - my) / 28) ** 2
                if e <= 1.0 and 0 <= x < W and 0 <= y < H:
                    img[y, x] = C('#07070b') if e < 0.72 else C('#120f12') if e < 0.86 else ROCK[1]
                elif e <= 1.35 and 0 <= x < W and 0 <= y < H:
                    img[y, x] = ROCK[4] if (y < my and x < mx) else ROCK[3] if y < my else ROCK[2]
        # 동굴 안 붉은 눈 두 쌍
        for (ex, ey) in ((mx + 6, my - 6), (mx + 14, my + 4)):
            img[int(ey), int(ex)] = C('#ff4d3d'); img[int(ey), int(ex) + 3] = C('#ff4d3d')
        # 입구 흙 부채꼴
        keep[int(my - 32):int(my + 32), int(mx - 30):] = True

    # 4) 수정 광장: 돌 타일 원 + 룬 원 + 받침
    cx, cy = cr
    R = 54
    d = np.hypot(xs - cx, ys - cy)
    ang = np.arctan2(ys - cy, xs - cx)
    plaza = d < R
    # 돌 타일: 9px 고리마다 바깥으로 갈수록 조각이 많아짐 (고리마다 반 칸씩 엇갈림)
    ri = np.floor(d / 9).astype(int)
    ring = ri % 2
    nseg = np.maximum(6, ri * 6)
    segf = ((ang + math.pi) / (2 * math.pi) * nseg + ring * 0.5) % 1
    arc = np.minimum(segf, 1 - segf) * (2 * math.pi * d / nseg)  # 가장 가까운 이음매까지 호 길이
    seam = ((arc < 0.7) & (ri >= 1)) | (np.abs(d - ri * 9) < 0.7)
    pv = 0.45 + value_noise(W, H, 5, rnd) * 0.25 - (d / R) * 0.12 + ring * 0.05
    img[plaza] = pal_pick(STONE[1:5], pv, True, xs, ys)[plaza]
    img[plaza & seam] = STONE[1]
    img[(d >= R) & (d < R + 2)] = STONE[0]
    img[(d >= R - 2) & (d < R)] = STONE[3]
    runering = (np.abs(d - 38) < 0.8)
    img[runering & plaza] = RUNE[2]
    img[(np.abs(d - 36) < 0.6) & plaza] = RUNE[1]
    for i in range(12):  # 룬 글자 (점과 짧은 선)
        a = i * math.pi / 6 + 0.26
        gx, gy = cx + math.cos(a) * 44, cy + math.sin(a) * 44
        for j in range(-2, 3):
            img[int(gy + j * math.cos(a) * 0.6), int(gx - j * math.sin(a) * 0.6)] = RUNE[1 + (i % 2)]
        img[int(gy), int(gx)] = RUNE[3]
    # 가운데 받침 (육각 돌)
    ped = d < 14
    img[ped] = STONE[4]
    img[ped & (ys > cy + 2)] = STONE[3]
    img[(d >= 13) & (d < 15)] = STONE[1]
    img[(np.abs(d - 9) < 0.7)] = RUNE[2]
    keep |= d < R + 8

    # 5) 광장 둘레 부서진 기둥 6개 + 화로 2개
    def pillar(px, py, h, broken):
        px, py = int(px), int(py)
        # 그림자
        for y in range(py, py + 4):
            for x in range(px - 4, px + 8):
                if 0 <= x < W and 0 <= y < H and ((x - px - 2) / 6) ** 2 + ((y - py - 1.5) / 2.5) ** 2 < 1:
                    img[y, x] = (np.array(img[y, x], int) * 0.6).astype(np.uint8)
        for y in range(py - h, py + 1):
            for x in range(px - 3, px + 4):
                u = (x - (px - 3)) / 6
                k = 4 if u < 0.3 else 3 if u < 0.7 else 2
                img[y, x] = STONE[k]
            img[y, px - 4] = STONE[0]; img[y, px + 4] = STONE[0]
        img[py - h - 1, px - 4:px + 5] = STONE[5] if not broken else STONE[3]
        img[py - h - 2, px - 3:px + 4] = STONE[0]
        if broken:
            for x in range(px - 3, px + 4):
                cut = py - h + ((x * 7) % 3)
                img[cut - 2:cut, x] = 0
                img[cut - 2, x] = STONE[0]
        else:
            img[py - h - 3, px - 5:px + 6] = STONE[0]
            img[py - h - 2, px - 4:px + 5] = STONE[4]
        img[py + 1, px - 4:px + 5] = STONE[0]
        keep[py - h - 4:py + 5, px - 7:px + 9] = True

    for i, a in enumerate((-2.6, -1.9, -1.0, 1.0, 1.9, 2.6)):
        pillar(cx + math.cos(a) * 64, cy + math.sin(a) * 60, 16 if i % 3 else 9, i % 3 == 0)

    def brazier(bx, by):
        bx, by = int(bx), int(by)
        img[by - 1:by + 3, bx - 3:bx + 4] = IRON[2]
        img[by + 3:by + 7, bx - 1:bx + 2] = IRON[1]
        img[by + 7, bx - 3:bx + 4] = IRON[0]
        for (x, y, c) in ((0, -2, RED[3]), (-1, -2, RED[2]), (1, -2, RED[2]), (0, -3, AMBER[3]), (-1, -3, RED[3]), (1, -4, AMBER[3]), (0, -5, AMBER[4]), (0, -6, AMBER[3])):
            img[by + y, bx + x] = c
        for y in range(by - 12, by + 10):
            for x in range(bx - 12, bx + 13):
                dd = math.hypot(x - bx, y - by + 3)
                if dd < 12 and 0 <= x < W and 0 <= y < H and not (abs(x - bx) <= 3 and by - 6 <= y <= by + 7):
                    k = (1 - dd / 12) * 0.25
                    img[y, x, :3] = np.minimum(255, img[y, x, :3] + np.array([60, 35, 5]) * k).astype(np.uint8)
        keep[by - 8:by + 10, bx - 6:bx + 7] = True

    brazier(cx + 30, cy - 46)
    brazier(cx + 30, cy + 44)

    # 6) 왼쪽 신전 터: 계단 + 큰 기둥 2개 + 부서진 아치
    for i, (x0, y0, x1, y1) in enumerate(((22, 178, 84, 284), (30, 186, 80, 276), (38, 194, 76, 268))):
        for y in range(y0, y1):
            for x in range(x0, x1):
                k = 2 + i if x - x0 > 2 else 4
                img[y, x] = STONE[min(5, k)]
        img[y0:y1, x1 - 1] = STONE[0]
        img[y1 - 1, x0:x1] = STONE[0]
        img[y0, x0:x1] = STONE[5]
    # 바닥 판석 줄눈 · 광장 쪽 계단 3칸 · 가운데 제단
    for y in range(198, 266, 7):
        img[y, 40:75] = STONE[2]
    for x in range(40, 76, 9):
        for y in range(195, 268):
            if (y // 7) % 2 == (x // 9) % 2:
                img[y, x] = STONE[2]
    for i, k in enumerate((5, 4, 3)):
        img[200:262, 84 + i * 3:87 + i * 3] = STONE[k]
        img[200:262, 86 + i * 3] = STONE[1]
        img[199, 84 + i * 3:87 + i * 3] = STONE[5]
    img[224:240, 50:64] = STONE[1]
    img[222:238, 51:63] = STONE[4]
    img[222, 51:63] = STONE[5]
    img[228:231, 56:58] = RUNE[2]
    keep[170:292, 0:96] = True
    pillar(30, 196, 30, False)
    pillar(30, 282, 30, False)
    pillar(66, 196, 22, True)
    pillar(66, 282, 18, True)
    # 무너진 아치 조각
    for a in np.linspace(math.pi * 0.55, math.pi * 1.0, 26):
        x, y = int(48 + math.cos(a) * 30), int(232 - math.sin(a) * 50)
        img[y:y + 3, x:x + 4] = STONE[3]
        img[y, x:x + 4] = STONE[5]

    # 7) 시설 받침돌 14개
    for (wx, wy) in slots_world():
        sx, sy = wx / 4, wy / 4 + 4
        for y in range(int(sy - 8), int(sy + 9)):
            for x in range(int(sx - 12), int(sx + 13)):
                e = ((x - sx) / 11) ** 2 + ((y - sy) / 6.5) ** 2
                if e > 1.25:
                    continue
                if e > 1.0:
                    img[y, x] = (np.array(img[y, x], int) * 0.55).astype(np.uint8)  # 그림자
                    img[y, x, 3] = 255
                    continue
                top = y < sy
                k = 4 if (top and x < sx) else 3 if top else 2
                if e > 0.78:
                    k = 1 if not top else 2
                img[y, x] = STONE[k]
        # 받침 가운데 희미한 룬 4점
        for (ox, oy) in ((-5, 0), (5, 0), (0, -3), (0, 3)):
            img[int(sy + oy), int(sx + ox)] = RUNE[1]
        keep[int(sy - 14):int(sy + 12), int(sx - 16):int(sx + 17)] = True

    # 8) 숲 테두리 (위·아래·왼쪽 귀퉁이)
    def tree(tx, ty, r):
        # 그림자
        for y in range(int(ty), int(ty + r * 0.7)):
            for x in range(int(tx - r), int(tx + r + 4)):
                if 0 <= x < W and 0 <= y < H and ((x - tx - 2) / (r + 1)) ** 2 + ((y - ty - r * 0.25) / (r * 0.45)) ** 2 < 1:
                    img[y, x, :3] = (img[y, x, :3] * 0.55).astype(np.uint8)
        # 줄기
        for y in range(int(ty - 2), int(ty + 3)):
            for x in range(int(tx - 1), int(tx + 2)):
                if 0 <= x < W and 0 <= y < H:
                    img[y, x] = WOOD[1] if x > tx else WOOD[2]
        # 잎 덩어리 3개
        for (ox, oy, rr) in ((0, -r * 0.9, r), (-r * 0.55, -r * 0.55, r * 0.7), (r * 0.55, -r * 0.5, r * 0.72)):
            ccx, ccy = tx + ox, ty + oy
            for y in range(int(ccy - rr - 1), int(ccy + rr + 2)):
                for x in range(int(ccx - rr - 1), int(ccx + rr + 2)):
                    if not (0 <= x < W and 0 <= y < H):
                        continue
                    dx, dy = (x - ccx) / rr, (y - ccy) / rr
                    dd = dx * dx + dy * dy
                    if dd > 1:
                        continue
                    lum = (-dx * 0.55 - dy * 0.75) * 0.5 + math.sqrt(1 - dd) * 0.6
                    k = int(np.clip(lum, 0, 0.999) * 5)
                    if BAYER[y & 3, x & 3] < (lum * 5 - k) and k < 5:
                        k += 1
                    img[y, x] = LEAF[min(5, max(1, k))]
                    if dd > 0.86:
                        img[y, x] = LEAF[0]

    trees = []
    for x in range(-6, 650, 15):
        trees.append((x + rnd.uniform(-4, 4), rnd.uniform(18, 46), rnd.uniform(10, 15)))
        trees.append((x + rnd.uniform(-4, 4), rnd.uniform(420, 452), rnd.uniform(11, 15)))
    for y in range(40, 430, 18):
        if not (165 < y < 300):
            trees.append((rnd.uniform(-2, 14), y + rnd.uniform(-5, 5), rnd.uniform(9, 13)))
    for (tx, ty, r) in sorted(trees, key=lambda t: t[1]):
        if keep[int(min(H - 1, max(0, ty))), int(min(W - 1, max(0, tx)))]:
            continue
        tree(tx, ty, r)

    # 9) 장식: 바위·덤불·꽃·풀포기 (길·광장·받침돌은 피함)
    def free(x, y, m=4):
        x0, x1, y0, y1 = max(0, x - m), min(W, x + m), max(0, y - m), min(H, y + m)
        return not keep[y0:y1, x0:x1].any()

    def rock(x, y, r):
        for yy in range(int(y - r), int(y + r * 0.7) + 1):
            for xx in range(int(x - r - 1), int(x + r + 2)):
                if not (0 <= xx < W and 0 <= yy < H):
                    continue
                dx, dy = (xx - x) / r, (yy - y) / (r * 0.75)
                dd = dx * dx + dy * dy
                if dd > 1:
                    continue
                lum = (-dx * 0.6 - dy * 0.8) * 0.5 + 0.5
                img[yy, xx] = ROCK[1 + min(4, int(lum * 4.99))]
                if dd > 0.8:
                    img[yy, xx] = ROCK[0]

    for _ in range(70):
        x, y = rnd.randint(60, 640), rnd.randint(60, 395)
        if free(x, y, 7):
            rock(x, y, rnd.uniform(2.5, 4.5)); keep[y - 5:y + 5, x - 5:x + 5] = True
    for _ in range(90):
        x, y = rnd.randint(55, 640), rnd.randint(58, 398)
        if free(x, y, 6):
            r = rnd.uniform(3, 5)
            for yy in range(int(y - r), int(y + r)):
                for xx in range(int(x - r), int(x + r)):
                    dd = ((xx - x) / r) ** 2 + ((yy - y) / r) ** 2
                    if dd < 1:
                        lum = (-(xx - x) / r * 0.5 - (yy - y) / r * 0.7) * 0.5 + 0.55
                        img[yy, xx] = GRASS[2 + min(3, int(lum * 3.99))] if dd < 0.75 else GRASS[0]
            if rnd.random() < 0.4:
                img[int(y - 1), int(x)] = C('#f4d35e') if rnd.random() < 0.5 else C('#f28fb0')
            keep[y - 4:y + 4, x - 4:x + 4] = True
    for _ in range(900):
        x, y = rnd.randint(50, 645), rnd.randint(55, 400)
        if free(x, y, 1):
            img[y, x] = GRASS[5] if rnd.random() < 0.4 else GRASS[4]
            if y > 0:
                img[y - 1, x] = GRASS[4]
    for _ in range(120):
        x, y = rnd.randint(50, 645), rnd.randint(55, 400)
        if free(x, y, 1):
            img[y, x] = rnd.choice((C('#f4d35e'), C('#f28fb0'), C('#e8edf5'), C('#9ad0ff')))

    # 10) 가장자리 어둡게 (비네트)
    vig = np.clip(1 - np.minimum.reduce([xs / 70, (W - xs) / 40, ys / 55, (H - ys) / 55]), 0, 1) * 0.35
    img[:, :, :3] = (img[:, :, :3] * (1 - vig[..., None])).astype(np.uint8)
    img[:, :, 3] = 255
    return Image.fromarray(img, 'RGBA')


def main():
    os.makedirs(os.path.dirname(OUT_TOWERS), exist_ok=True)
    towers = build_towers()
    towers.save(OUT_TOWERS, optimize=True)
    cry = build_crystal()
    cry.save(OUT_CRYSTAL, optimize=True)
    m = build_map()
    m.convert('RGB').save(OUT_MAP, 'WEBP', lossless=True, quality=100, method=6)
    print('towers', towers.size, os.path.getsize(OUT_TOWERS), 'crystal', cry.size, os.path.getsize(OUT_CRYSTAL), 'map', m.size, os.path.getsize(OUT_MAP))
    if PREVIEW:
        os.makedirs(PREVIEW, exist_ok=True)
        bg = Image.new('RGBA', (towers.width * 4, towers.height * 4), (58, 82, 60, 255))
        bg.alpha_composite(towers.resize((towers.width * 4, towers.height * 4), Image.NEAREST))
        bg.save(os.path.join(PREVIEW, '_preview_defense_towers.png'))
        bg = Image.new('RGBA', (cry.width * 4, cry.height * 4), (58, 82, 60, 255))
        bg.alpha_composite(cry.resize((cry.width * 4, cry.height * 4), Image.NEAREST))
        bg.save(os.path.join(PREVIEW, '_preview_defense_crystal.png'))
        m.resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(PREVIEW, '_preview_defense_map.png'))


if __name__ == '__main__':
    main()

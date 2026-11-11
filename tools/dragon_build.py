# 용족 샘플 (용인족 전사·궁수·주술사·사제·용비늘 기사·창기사·서리 용인족·전고수, 성난/화염/화염포 드레이크,
# 독꼬리/급습/저주 와이번, 탑 보스 심연마룡) → 몸 시트 + 투사체 아틀라스
# 사용: python tools/dragon_build.py            (모두 만들기)
#       python tools/dragon_build.py debug <폴더> [이름... | fx]   (칸 미리보기만)
# 자르기·배경 지우기는 tools/deepsea2_build.py의 cut2 그대로 (칸 테두리의 어두운 바탕색 묶음으로 지움)
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, 'tools')
import deepsea2_build as D  # noqa: E402
from deepsea_build import unwatermark  # noqa: E402

B = D.B
STD = D.STD
SAMPLES = {}

# 용인족 전사 (붉은 비늘·가시 어깨갑옷·톱날 검·나무 방패)
SAMPLES['dragonkin_warrior'] = {
    'wm': (590, 927, 20),
    'cells': {
        'idle': B(8, 228, 15, 256), 'walk_a': B(242, 452, 18, 256), 'walk_b': B(455, 670, 12, 252),
        'atk_a': B(2, 240, 328, 600), 'atk_b': B(232, 487, 342, 602, min=150), 'hurt': B(472, 674, 352, 602, min=150),
        'death_a': B(52, 302, 698, 962), 'death_b': B(342, 670, 798, 966),
    },
    'order': STD,
}
# 성난 드레이크 (초록 용, 맨손 할퀴기): 칸마다 패널, 칸 위 라벨. 대기 칸 콧김·걷기 칸 꼬리 움직임 선은 지움
SAMPLES['drake_warrior'] = {
    'wm': (934, 482, 20),
    'common': {'pocket': 120},
    'cells': {
        'idle': B(15, 250, 55, 282, drop=[(205, 250, 140, 192)]), 'walk_a': B(268, 505, 55, 282),
        'walk_b': B(522, 760, 55, 282, drop=[(522, 556, 165, 220)]), 'atk_a': B(778, 1015, 55, 282),
        'atk_b': B(12, 252, 345, 566), 'hurt': B(268, 505, 332, 566, lab=[(340, 430, 300, 352)]),
        'death_a': B(522, 760, 342, 566, lab=[(560, 720, 300, 352)]), 'death_b': B(778, 1015, 395, 566),
    },
    'order': STD,
}
# 독꼬리 와이번 (보라 날개·꼬리 끝 보라 불): 라벨이 칸 사이사이. 공격 칸 앞 보라 불덩이는 투사체 wyvern_breath
SAMPLES['wyvern_archer'] = {
    'wm': (589, 926, 20),
    'common': {'pocket': 150},
    'cells': {
        'idle': B(262, 432, 0, 172), 'walk_a': B(108, 302, 200, 372, lab=[(100, 185, 195, 214)]),
        'walk_b': B(380, 618, 205, 372, lab=[(378, 418, 212, 250)]),
        'atk_a': B(118, 292, 412, 602), 'atk_b': B(342, 674, 448, 602, drop=[(590, 674, 490, 572)]),
        'hurt': B(238, 412, 642, 802),
        'death_a': B(122, 352, 850, 1002, lab=[(118, 212, 848, 886)], min=120), 'death_b': B(372, 662, 896, 1012),
    },
    'order': STD,
}
# 용인족 궁수 (초록 비늘·뿔·화살통·활). 피격 칸은 활을 놓친 그림
SAMPLES['dragonkin_archer'] = {
    'wm': (662, 921, 20),
    'common': {'pocket': 150},
    'cells': {
        'idle': B(28, 248, 22, 282), 'walk_a': B(268, 502, 22, 282), 'walk_b': B(518, 742, 22, 282),
        'atk_a': B(12, 262, 358, 632), 'atk_b': B(270, 507, 352, 640), 'hurt': B(542, 748, 358, 634),
        'death_a': B(42, 302, 718, 948), 'death_b': B(352, 718, 798, 958),
    },
    'order': STD,
}
# 화염 드레이크 (불꽃 갈기 아기 용): 넓은 칸의 불줄기 뿜기를 공격 2로 (불줄기는 투사체 drake_breath).
# '5. 공격 ②' 칸은 대기와 같은 그림, 이름 없는 웅크린 칸은 안 씀. 쓰러짐 2 머리 위 연기는 지움
SAMPLES['drake_mage'] = {
    'wm': (915, 652, 20),
    'cells': {
        'idle': B(18, 252, 12, 228), 'walk_a': B(268, 507, 12, 228), 'walk_b': B(522, 762, 12, 228), 'atk_a': B(778, 1018, 12, 228),
        'atk_b': B(12, 500, 298, 502, drop_poly=[[(196, 360), (330, 343), (500, 325), (500, 450), (330, 425), (196, 400)]]),
        'hurt': B(268, 507, 515, 718), 'death_a': B(522, 762, 515, 718),
        'death_b': B(778, 1018, 538, 718, drop=[(922, 980, 538, 628)]),
    },
    'order': STD,
}
# 용인족 주술사 (주황 비늘·털 망토 검은 로브·해골 지팡이·꼬리 보라 불): 공격 칸 앞 보라 구슬은 투사체 dk_hex_orb
SAMPLES['dragonkin_mage'] = {
    'wm': (662, 921, 20),
    'cells': {
        'idle': B(28, 252, 22, 288), 'walk_a': B(258, 507, 22, 288), 'walk_b': B(508, 752, 22, 288),
        'atk_a': B(28, 252, 368, 628), 'atk_b': B(252, 548, 382, 628, drop=[(486, 548, 455, 532)], min=150),
        'hurt': B(550, 752, 382, 628),
        'death_a': B(58, 312, 688, 958), 'death_b': B(398, 748, 778, 962),
    },
    'order': STD,
}
# 용인족 사제 (흰·금빛 사제복·수정 지팡이): 공격 칸 앞 금빛 섬광은 투사체 dk_holy
SAMPLES['dragonkin_healer'] = {
    'cells': {
        'idle': B(18, 228, 55, 288), 'walk_a': B(288, 507, 68, 292), 'walk_b': B(502, 718, 68, 296),
        'atk_a': B(182, 422, 352, 582, glow=40, warm_glow=120, min=150), 'atk_b': B(425, 748, 352, 582, drop=[(622, 748, 395, 535)]),
        'hurt': B(178, 388, 592, 798),
        'death_a': B(172, 412, 802, 1002), 'death_b': B(428, 732, 838, 998),
    },
    'order': STD,
}
# 용비늘 기사 (푸른 비늘 갑옷·붉은 망토·비늘 방패·검)
SAMPLES['dragonkin_knight'] = {
    'wm': (662, 921, 20),
    'cells': {
        'idle': B(22, 272, 18, 288), 'walk_a': B(272, 522, 18, 288), 'walk_b': B(508, 762, 18, 288),
        'atk_a': B(12, 252, 358, 648), 'atk_b': B(262, 542, 378, 648), 'hurt': B(538, 752, 382, 648),
        'death_a': B(48, 332, 738, 982), 'death_b': B(392, 748, 808, 978),
    },
    'order': STD,
}
# 용인족 창기사 (가시 투구·비늘 갑옷·가시 창): 칸마다 패널, 아래 라벨 띠. 찌르기 칸 앞 바람 선은 그대로 둠.
# '피긱'(대기와 같은 그림)·이름 없는 기울어진 칸은 안 씀
SAMPLES['dragonkin_lancer'] = {
    'common': {'tol': 15},
    'cells': {
        'idle': B(12, 250, 8, 246), 'walk_a': B(266, 505, 8, 246), 'walk_b': B(521, 760, 8, 246), 'atk_a': B(776, 1018, 8, 246),
        'atk_b': B(28, 472, 300, 503), 'hurt': B(266, 505, 527, 724, erase_r=[(262, 304, 512, 553), (266, 505, 520, 539)]),
        'death_a': B(521, 760, 527, 724, erase_r=[(521, 760, 520, 539)]), 'death_b': B(776, 1018, 592, 724),
    },
    'order': STD,
}
# 화염포 드레이크 (등에 대포를 멘 붉은 용): 공격 칸 대포 앞 불길은 투사체 drake_cannon. 몸 가까운 조각만 남김
SAMPLES['drake_sniper'] = {
    'wm': (662, 922, 20),
    'cells': {
        'idle': B(12, 202, 12, 242), 'walk_a': B(202, 398, 12, 242), 'walk_b': B(398, 598, 12, 242), 'atk_a': B(582, 762, 12, 242),
        'atk_b': B(22, 452, 338, 602, drop=[(196, 452, 338, 447)], core=(22, 262, 330, 610)),
        'hurt': B(498, 708, 385, 602),
        'death_a': B(58, 308, 738, 938), 'death_b': B(438, 708, 748, 942),
    },
    'order': STD,
}
# 서리 용인족 (얼음 비늘·털 코트·얼음 지팡이): 칸마다 눈밭 그림. 눈 바닥선 아래는 어두운 부츠만 남김.
# '쓰러짐 1'은 대기와 같은 그림이라 안 쓰고 피격 → 쓰러짐 2로 이어 씀
SAMPLES['dragonkin_frost'] = {
    # 흰 바탕으로 다시 받은 샘플 (처음 샘플은 어두운 눈밭 패널이라 코트가 바탕과 같은 색이었음). 얼음 몸이 밝아서 tol을 낮게
    'common': {'tol': 12, 'pocket': 12, 'min': 120},
    'cells': {
        'idle': B(34, 218, 40, 248), 'walk_a': B(243, 425, 40, 248), 'walk_b': B(453, 635, 40, 248),
        'atk_a': B(34, 218, 340, 540), 'atk_b': B(243, 425, 340, 540), 'hurt': B(453, 635, 340, 540),
        'death_b': B(243, 425, 630, 797),
    },
    'order': ['idle', 'walk_a', 'walk_b', 'atk_a', 'atk_b', 'hurt', 'hurt', 'death_b'],
}
# 저주 와이번 (검보라 용·뼈 목걸이·보라 불): '일반공격 1'이 두 칸 (웅크림·입에 구슬 모으기) → 둘 다 씀.
# 공격 2 앞 보라 불길은 투사체 curse_breath. 칸 순서 = 대기, 걷기 A·B, 웅크림, 구슬 모으기, 불 뿜기, 피격, 쓰러짐 2장
SAMPLES['wyvern_curse'] = {
    'wm': (613, 924, 20),
    'common': {'tol': 10, 'pocket': 120},   # 날개·꼬리 사이에 갇힌 바탕도 지움
    'cells': {
        'idle': B(28, 238, 28, 252), 'walk_a': B(242, 452, 32, 252), 'walk_b': B(452, 692, 58, 252),
        'crouch': B(32, 338, 338, 482), 'atk_a': B(392, 652, 310, 482), 'atk_b': B(18, 402, 542, 728, drop=[(262, 402, 575, 715)]),
        'hurt': B(408, 652, 542, 728), 'death_a': B(52, 332, 782, 968), 'death_b': B(408, 668, 838, 968),
    },
    'order': ['idle', 'walk_a', 'walk_b', 'crouch', 'atk_a', 'atk_b', 'hurt', 'death_a', 'death_b'],
}
# 용인족 전고수 (깃털 머리장식·북·뼈 북채): 칸마다 둥근 테두리 패널, 칸 위 라벨
SAMPLES['dragonkin_bard'] = {
    'wm': (921, 663, 20),
    'cells': {
        'idle': B(24, 236, 72, 362), 'walk_a': B(278, 492, 72, 362), 'walk_b': B(533, 746, 72, 362), 'atk_a': B(788, 1002, 72, 362),
        'atk_b': B(24, 236, 452, 744), 'hurt': B(278, 492, 452, 744), 'death_a': B(533, 746, 452, 744), 'death_b': B(788, 1006, 520, 744),
    },
    'order': STD,
}
# 심연마룡 (용족 보스, 탑 91~100층 · 마법사 직업): 가시 왕관·해골 지팡이·검은 구슬·군기.
# 샘플의 걷기 두 칸은 지팡이·구슬·군기가 칸마다 바뀌어 안 쓰고, 소품이 같은 대기·공격 1 자세를 번갈아 걸음으로 씀.
# 공격 칸 앞 보라 광선은 투사체 dark_beam
SAMPLES['dark_dragon'] = {
    # 흰 바탕으로 다시 받은 샘플 (처음 샘플은 어두운 바탕이 검은 비늘과 비슷했음). 칸 네모는 그림이 안 잘리게 넉넉히, 라벨 글자는 바탕색으로 칠함
    'common': {'tol': 20, 'pocket': 12, 'min': 150},
    'cells': {
        'idle': B(22, 244, 12, 276, erase_r=[(15, 182, 12, 53)]), 'walk_a': B(288, 520, 12, 278, erase_r=[(288, 474, 12, 51)]),
        'walk_b': B(520, 744, 22, 278),
        'atk_a': B(34, 296, 368, 584), 'atk_b': B(296, 742, 322, 586, drop=[(506, 742, 376, 530)]),
        'hurt': B(38, 280, 588, 820, erase_r=[(15, 178, 586, 624)]),
        'death_a': B(86, 330, 812, 1018, erase_r=[(15, 262, 812, 848)]), 'death_b': B(422, 732, 866, 1024),
    },
    'order': ['idle', 'atk_a', 'atk_b', 'hurt', 'death_a', 'death_b',
              'dark_dragon_skill/dash_a', 'dark_dragon_skill/dash_b', 'dark_dragon_skill/fb_a', 'dark_dragon_skill/fb_b',
              'dark_dragon_skill/roar_a', 'dark_dragon_skill/roar_b', 'dark_dragon_skill/rain_a', 'dark_dragon_skill/rain_b',
              'dark_dragon_skill/tb_a', 'dark_dragon_skill/tb_b'],
}
# ── 다시 받은 칸 (2026-11-06). 그림 크기가 원래 샘플과 달라서 ref = (원래 샘플, 원래 칸, 이 샘플 칸)의 키를 맞춰 배율을 정함 ──
# 심연마룡 스킬 5종 × 2칸: 돌진(불꽃 웅크림·잔상 돌진) → charge, 파이어볼(손에 불덩이·던지기, 날아가는 불덩이는 투사체 dark_fireball),
# 사자후(포효·음파, 음파는 게임 이펙트가 깔려서 지움), 화살비(머리 위 어둠의 고리·구슬, 쏟아지는 화살은 지움),
# 썬더볼트(양손 번개·구슬, 번개 기둥은 게임 이펙트가 떨어져서 지움)
SAMPLES['dark_dragon_skill'] = {
    'skip': True, 'common': {'tol': 20, 'pocket': 12, 'min': 150}, 'ref': ('dark_dragon', 'atk_a', 'fb_a'),
    'cells': {
        'dash_a': B(28, 256, 46, 210, erase_r=[(15, 198, 8, 48)]), 'dash_b': B(372, 692, 22, 210),
        'fb_a': B(24, 266, 240, 412, erase_r=[(15, 282, 205, 242)]), 'fb_b': B(348, 559, 226, 412),
        'roar_a': B(22, 274, 446, 612), 'roar_b': B(348, 560, 420, 612, drop=[(511, 560, 420, 532), (537, 560, 532, 558), (511, 560, 558, 612)]),
        'rain_a': B(40, 246, 647, 820), 'rain_b': B(364, 536, 647, 820, core=(364, 527, 640, 830)),
        'tb_a': B(38, 352, 846, 1022, erase_r=[(15, 412, 812, 849)]), 'tb_b': B(358, 522, 846, 1022, erase_r=[(358, 412, 812, 849)]),
    },
}
# 성난 드레이크 걷기 2칸 (발밑 흙먼지)
SAMPLES['drake_warrior_walk'] = {
    'skip': True, 'ref': ('drake_warrior', 'walk_a', 'walk_a'),
    'cells': {'walk_a': B(4, 166, 28, 191, lab=[(25, 145, 0, 32)]), 'walk_b': B(184, 348, 28, 191, lab=[(200, 330, 0, 32)])},
}
SAMPLES['drake_warrior']['order'] = ['idle', 'drake_warrior_walk/walk_a', 'drake_warrior_walk/walk_b', 'atk_a', 'atk_b', 'hurt', 'death_a', 'death_b']
# 용인족 전사 걷기 ② (샘플 걷기 ②는 검이 빠져 있었음)
SAMPLES['dragonkin_warrior_walk'] = {
    'skip': True, 'ref': ('dragonkin_warrior', 'idle', 'walk_b'),
    'cells': {'walk_b': B(0, 233, 8, 268)},
}
SAMPLES['dragonkin_warrior']['order'] = ['idle', 'walk_a', 'dragonkin_warrior_walk/walk_b', 'atk_a', 'atk_b', 'hurt', 'death_a', 'death_b']
# 화염포 드레이크 걷기 2칸 (샘플 걷기 두 칸이 대기와 거의 같았음)
SAMPLES['drake_sniper_walk'] = {
    'skip': True, 'ref': ('drake_sniper', 'idle', 'walk_a'), 'ref_k': 0.93,
    'cells': {'walk_a': B(0, 333, 0, 302, min=150, drop=[(305, 333, 0, 40)]), 'walk_b': B(0, 333, 380, 747, min=150)},
}
SAMPLES['drake_sniper']['order'] = ['idle', 'drake_sniper_walk/walk_a', 'drake_sniper_walk/walk_b', 'atk_a', 'atk_b', 'hurt', 'death_a', 'death_b']
# 급습 와이번 (복면·남보라 날개·발톱 베기): 피격·쓰러짐 1은 반대쪽을 보고 뒤집혀 있어 좌우반전(~)해서 씀.
# 공격 2의 보라 발톱 궤적은 그림에 둠. 쓰러짐 2 뒤 검은 연기 얼룩은 그대로
SAMPLES['wyvern_rogue'] = {
    # 흰 바탕으로 다시 받은 샘플 (처음 샘플은 회색 바탕이 몸 색과 비슷했음). 날개·꼬리 사이에 갇힌 흰 바탕도 지움
    'common': {'pocket': 12, 'min': 150, 'tol': 40},
    'cells': {
        'idle': B(42, 218, 44, 202, drop=[(42, 70, 44, 125), (178, 202, 100, 152)]), 'walk_a': B(58, 322, 238, 396, erase_r=[(10, 205, 205, 250)]),
        'walk_b': B(378, 640, 225, 396),
        'atk_a': B(78, 302, 444, 602), 'atk_b': B(368, 698, 444, 610),
        'hurt': B(82, 332, 648, 806), 'death_a': B(106, 348, 848, 1008), 'death_b': B(458, 702, 842, 1010, drop=[(505, 648, 842, 893), (458, 500, 900, 960)]),   # 위로 피어오르는 연기 얼룩은 지움
    },
    'order': ['idle', 'walk_a', 'walk_b', 'atk_a', 'atk_b', 'hurt~', 'death_a~', 'death_b'],
}


def snow_fix(cfg):
    """눈밭 칸: 눈 바닥선(snow) 아래는 어두운 픽셀(부츠·코트)만 남김"""
    def fix(out, im):
        for k, o in cfg['cells'].items():
            sy = o.get('snow')
            if sy is None: continue
            r, ox, oy = out[k]
            r = r.copy()
            L = D.luma(r[..., :3])
            yy = np.arange(r.shape[0])[:, None] + oy
            r[..., 3][(yy >= sy) & (L >= 80)] = 0
            r[..., 3][np.broadcast_to(yy >= sy + 14, L.shape)] = 0
            out[k] = D.trim(r, ox, oy)
    return fix






# 투사체 (공격 칸에서 떼어 냄). 기준점 = 앞(오른쪽) 끝
FX = {
    'wyv_breath':  ('wyvern_archer', (594, 674, 492, 568), {}),        # 독꼬리 와이번 보라 불덩이
    'drake_flame': ('drake_mage', (190, 484, 330, 440), {}),           # 화염 드레이크 불줄기
    'hex_orb':     ('dragonkin_mage', (490, 548, 458, 530), {}),       # 용인족 주술사 보라 구슬
    'holy':        ('dragonkin_healer', (626, 748, 398, 535), {'glow': 40, 'warm_glow': 120}),  # 용인족 사제 금빛 섬광
    'cannon':      ('drake_sniper', (198, 448, 338, 452), {}),         # 화염포 드레이크 불길
    'curse_flame': ('wyvern_curse', (276, 402, 578, 712), {}),         # 저주 와이번 보라 불길
    'dark_beam':   ('dark_dragon', (508, 735, 380, 526), {}),          # 심연마룡 보라 광선
}
OUT_FX = 'assets/sprites/fx/dragon_fx.webp'


def build_fx(show=None):
    pieces = []
    ims = {}
    for k, (name, box, extra) in FX.items():
        if name not in ims:
            im = D.load(name)
            if 'wm' in SAMPLES[name]:
                bg = np.median(np.concatenate([im[:4].reshape(-1, 3), im[:, :4].reshape(-1, 3)]), 0)
                unwatermark(im, bg, *SAMPLES[name]['wm'])
            ims[name] = im
        o = {**SAMPLES[name].get('common', {}), **extra}
        r, _, _ = D.trim(D.cut2(ims[name], box, o), 0, 0)
        pieces.append((k, r))
    W = sum(p.shape[1] + 2 for _, p in pieces); H = max(p.shape[0] for _, p in pieces)
    sheet = Image.new('RGBA', (W, H)); x = 0; anims = {}
    for k, p in pieces:
        sheet.alpha_composite(Image.fromarray(np.clip(p, 0, 255).astype(np.uint8), 'RGBA'), (x, 0))
        h, w = p.shape[:2]
        ys = np.where(p[:, -max(4, w // 8):, 3].max(1) > 100)[0]
        anims[k] = [x, 0, w, h, w - 1, round(float(ys.mean()), 1)]
        x += w + 2
    out = f'{show}/dragon_fx.png' if show else OUT_FX
    sheet.save(out, **({} if show else {'format': 'WEBP', 'quality': 92, 'alpha_quality': 100, 'method': 6}))
    print(out, anims)


D.SAMPLES = SAMPLES
_palette0 = D.palette


def palette_near_bg(c):
    """칸 테두리 색 중 테두리 중앙값(바탕)에 가까운 것만으로 배경 색 묶음을 만듦 → 테두리에 닿은 몸 색(어두운 로브·갑옷)이 배경으로 안 섞임"""
    ring = np.concatenate([c[:3].reshape(-1, 3), c[-3:].reshape(-1, 3), c[:, :3].reshape(-1, 3), c[:, -3:].reshape(-1, 3)])
    med = np.median(ring, 0)
    keep = np.sqrt(((ring - med) ** 2).sum(1)) < 22
    ringk = ring[keep]
    k = min(6, len(np.unique(ringk.round(), axis=0)))
    from scipy.cluster.vq import kmeans2
    cent, _ = kmeans2(ringk, max(1, k), minit='++', seed=1)
    return cent[np.isfinite(cent).all(1)]


D.palette = palette_near_bg
for _cfg in SAMPLES.values():   # 몸 안 어두운 곳(로브·망토)을 '갇힌 배경'으로 지우지 않음
    _cfg['common'] = {'pocket': 10 ** 9, **_cfg.get('common', {})}

_cells_cache = {}


def cells(name):
    if name not in _cells_cache: _cells_cache[name] = D.cells_of(name)[0]
    return _cells_cache[name]


def frame_of(name, k):
    """한 칸 → (RGBA, 기준점 x, 기준점 y). 다른 샘플 칸은 ref 배율로 키움"""
    cfg = SAMPLES[name]
    flip = k.endswith('~'); k0 = k.rstrip('~')
    r, ox, oy = cells(name)[k0]
    o = cfg['cells'][k0]
    cx = o.get('cx')
    if cx is None:
        wsum = r[..., 3].sum(0)
        cx = ox + (wsum * np.arange(r.shape[1])).sum() / wsum.sum()
    ys = np.where((r[..., 3] > 128).any(1))[0]
    ay = ys.max() + 1 + o.get('dy', 0)
    ax = cx - ox
    if name.startswith('dark_dragon'): r = clean_white(r)   # 기준점은 지우기 전 그림으로 (칸마다 안 흔들리게)
    if 'ref' in cfg:
        main, mk, nk = cfg['ref']
        hm = cells(main)[mk][0].shape[0]; hn = cells(name)[nk][0].shape[0]
        s = hm / hn * cfg.get('ref_k', 1)
        img = Image.fromarray(np.clip(r, 0, 255).astype(np.uint8), 'RGBA')
        img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
        r = np.asarray(img).astype(float); ax *= s; ay *= s
    if flip: r = r[:, ::-1].copy(); ax = r.shape[1] - ax
    return r, ax, ay


def clean_white(rgba):
    """심연마룡: 흰 바탕 샘플에서 남은 흰 찌꺼기 지우기 (2026-11-11)
    ① 거의 흰 덩어리 중 투명한 곳에 닿거나 4px 이상인 것 (지팡이·날개 사이 틈, 불꽃 혀 사이). 둘레가 밝은 빛 속(번개·불덩이 심)은 남김
    ② 외곽 회색 테: 투명한 곳에 닿은 밝고 채도 낮은 테두리 픽셀을 2겹까지 벗김. 비늘은 훨씬 어둡고 불꽃·구슬·번개는 채도가 높아 안 걸림
    ③ 반투명 테두리에 섞인 흰빛은 빼서 어두운 원래 색으로"""
    from scipy import ndimage as ndi
    rgba = rgba.copy()
    c, A = rgba[..., :3], rgba[..., 3]
    lum = c.mean(2)
    wh = (c.min(2) >= 200) & (c.max(2) - c.min(2) <= 30) & (A > 0)
    lab, n = ndi.label(wh, structure=np.ones((3, 3)))
    if n:
        clear = ndi.binary_dilation(A < 128, iterations=1)
        areas = ndi.sum(wh, lab, range(1, n + 1))
        touch = ndi.maximum(clear, lab, range(1, n + 1))
        kill = np.zeros(n + 1, bool); kill[1:] = (areas >= 4) | (touch > 0)
        for i in np.where(kill)[0]:
            m = lab == i
            ring = ndi.binary_dilation(m, iterations=2) & ~m & (A > 100) & ~wh
            if ring.any() and lum[ring].mean() > 150: kill[i] = False
        A[kill[lab]] = 0
    for _ in range(2):
        edge = ndi.binary_dilation(A < 100, iterations=1) & (A > 0)
        pale = (lum >= 110) & (c.max(2) - c.min(2) <= 40)
        A[edge & pale] = 0
    edge = ndi.binary_dilation(A < 100, iterations=1) & (A > 0) & (A < 250)
    k = (A / 255.0)[..., None]
    dark = np.clip((c - 255 * (1 - k)) / np.maximum(k, 0.2), 0, 255)
    pale = edge & (lum >= 90)
    c[pale] = dark[pale]
    return rgba


def frames_of(name):
    fr = []
    for k in SAMPLES[name]['order']:
        if '/' in k:
            n2, k2 = k.split('/')
            fr.append(frame_of(n2, k2))
        else:
            fr.append(frame_of(name, k))
    return fr, None, None


D.frames_of = frames_of
FX['dark_fireball'] = ('dark_dragon_skill', (566, 722, 270, 360), {})   # 심연마룡 파이어볼 불덩이

if __name__ == '__main__':
    mains = [k for k in SAMPLES if not SAMPLES[k].get('skip')]
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        if sys.argv[3:] == ['fx']: build_fx(sys.argv[2])
        else:
            for n in (sys.argv[3:] or mains): D.preview(n, sys.argv[2])
    else:
        for n in mains: D.build(n)
        build_fx()

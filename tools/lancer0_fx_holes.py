# 창병 기본 외형 이펙트 손질 — tools/lancer0_build.py 끝에서 부름 (따로 돌려도 됨: python tools/lancer0_fx_holes.py [미리 보기 폴더])
# 2026-11-10 사용자 지적: 모션 샘플(exports/job-samples/lancer_0_motion.png)에 빨갛게 표시한 자리를
#   "비어 있던 곳은 채우고, 흰색 배경인 부분은 지우기". 표시 좌표는 칸 좌표로 옮겨 tools/lancer0_fx_marks.json에 둠
#   [시트, 칸, 'fill' | 'clear', [[y, x0, x1], ...] (표시 안쪽 픽셀 줄)]
#   - fill: 표시 안의 투명 픽셀이 속한 갇힌 투명 영역(사방이 그림으로 막힘)을 통째로, 가장 가까운 밝은 이펙트 색으로 채움
#     (휘두르기 올려 베기 7·낮게 휘두름 8·피어싱 초승달 13·바람 14·양쪽 초승달 19의 이펙트 속 구멍)
#   - clear: 표시 안의 흰 배경 찌꺼기(밝고 무채색, min ≥ 215)와 거기 이어진 흰 픽셀(표시 둘레 2px까지)을 투명하게
#     (이펙트 줄기 사이에 남은 흰 덩어리, 찌르기 당김 9 팔·쓰러짐 1(24) 창대 옆 흰 점)
#   - paint: 표시 안의 어두운 얼룩을 둘레 이펙트 색으로 (무쌍 회전 고리 2)
#   두 번째 표시(같은 날): 첫 번째 손질로 뚫린 구멍 자리는 그 지우기를 뺐고, 낮게 휘두름(8)의 채운 자리는 흰 배경이라 채우기를 빼고 지움
#   마지막에 피사체 테두리의 흰 배경 찌꺼기를 한 겹 지움 (trim_halo)
#   무쌍난무 자세 시트(lancer_musou_cast)의 돌진(7·8)·양쪽 초승달(9)은 lancer_0의 창돌격 돌진(21·22)·회전·난무 초승달(19)과 같은 그림 조각이라
#   같은 표시를 22px 위로 옮겨(기준점 147 → 125) 함께 씀. 회전·난무 고리(17)·머리 위(18)는 화면 표시 위치로 어림한 반경 5px 원
import json
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
# 시트 경로 · 표시를 만들 때의 칸 기준점 (빌드로 칸 크기·기준점이 바뀌면 표시를 그만큼 옮김. 칸 너비는 그림 크기에서 읽음)
SHEETS = {'lancer_0': ('assets/sprites/merc/lancer_0.webp', (82, 125), 26),
          'musou': ('assets/sprites/fx/lancer_musou_cast.webp', (82, 147), None)}


def region(c, rows):
    R = np.zeros(c.shape[:2], bool)
    for y, x0, x1 in rows:
        if 0 <= y < R.shape[0]: R[y, max(0, x0):min(R.shape[1], x1 + 1)] = True
    return R


def fill(c, R):
    a = c[..., 3] > 0
    lab, _ = ndi.label(~a)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])).tolist())
    ids = [i for i in set(lab[R & ~a].tolist()) if i and i not in edge]   # 갇힌 투명 영역만
    m = np.isin(lab, ids) | (R & ~a)   # + 표시 안의 투명 픽셀 (한쪽이 열린 틈)
    if not m.any(): return 0
    light = a & (c[..., :3].astype(int).min(-1) > 110)
    _, (iy, ix) = ndi.distance_transform_edt(~light, return_indices=True)
    c[m, :3] = c[iy[m], ix[m], :3]
    c[m, 3] = 255
    return int(m.sum())


def clear(c, R):
    rgb = c[..., :3].astype(int)
    white = (c[..., 3] > 0) & (rgb.min(-1) >= 215) & (rgb.max(-1) - rgb.min(-1) < 20)
    near = ndi.binary_dilation(R, iterations=2)
    lab, _ = ndi.label(white & near, structure=np.ones((3, 3)))
    m = np.isin(lab, [i for i in set(lab[R & white].tolist()) if i])
    c[m] = 0
    return int(m.sum())


def paint(c, R):
    # 이펙트 줄기 속에 남은 어두운 얼룩: 표시 안의 밝지 않은 불투명 픽셀을 가장 가까운 밝은 이펙트 색으로
    rgb = c[..., :3].astype(int)
    a = c[..., 3] > 0
    light = a & (rgb.min(-1) > 110)
    m = R & a & ~light
    if not m.any(): return 0
    _, (iy, ix) = ndi.distance_transform_edt(~light, return_indices=True)
    c[m, :3] = c[iy[m], ix[m], :3]
    return int(m.sum())


def trim_halo(im):
    # 피사체 테두리에 남은 흰 배경 찌꺼기 (2026-11-10 사용자 요청): 검은 윤곽선(가장 밝은 채널 < 60) 바로 바깥에 붙은
    #   무채색·옅은 회색 픽셀 한 겹 (투명과 맞닿은 가장자리). 두 번 돌려 두 겹짜리도 지움. 이펙트의 흰 가장자리는 윤곽선과 붙어 있지 않아서 그대로
    n = 0
    for _ in range(2):
        c = im.astype(int)
        a = c[..., 3] > 0
        rgb = c[..., :3]
        edge = a & ndi.binary_dilation(~a)
        outline = a & (rgb.max(-1) < 60)
        halo = edge & ~outline & (rgb.max(-1) - rgb.min(-1) < 35) & (rgb.mean(-1) >= 60) & ndi.binary_dilation(outline)
        im[halo] = 0
        n += int(halo.sum())
    return n


def main(out_dir=None, anchors=None):
    # out_dir를 주면 원본은 두고 그 폴더에 결과를 씀 (미리 보기용). anchors = 빌드가 만든 칸 기준점 {시트: (x, y)}
    marks = json.load(open(os.path.join(HERE, 'lancer0_fx_marks.json'), encoding='utf-8'))
    for key, (path, (ax0, ay0), count) in SHEETS.items():
        im = np.array(Image.open(path).convert('RGBA'))
        cw = im.shape[1] // (count or 11)   # 무쌍난무 자세 11칸 (10번 낮게 휩쓸기 추가)
        ax, ay = (anchors or {}).get(key, (ax0, ay0))
        dx, dy = ax - ax0, ay - ay0
        for sh, k, mode, rows in marks:
            if sh != key: continue
            c = im[:, k * cw:(k + 1) * cw]
            rows = [(y + dy, x0 + dx, x1 + dx) for y, x0, x1 in rows]
            n = {'fill': fill, 'clear': clear, 'paint': paint}[mode](c, region(c, rows))
            print(f'{key} 칸 {k}: {mode} {n}px')
        print(f'{key}: 테두리 흰 찌꺼기 {trim_halo(im)}px 지움')
        out = os.path.join(out_dir, os.path.basename(path)) if out_dir else path
        Image.fromarray(im, 'RGBA').save(out, 'WEBP', lossless=True)


if __name__ == '__main__':
    main(*sys.argv[1:])

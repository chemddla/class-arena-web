# 샘플 의자 (나무 틀 + 파란 쿠션) 요청문 — 3판

규격은 `chair`와 같은 `1×1×1.5`(캔버스 최대 64×92 도트).

## 결론부터

- **앞모습은 원본 그림을 그대로 `chair.webp`로 씁니다.** 다시 만들면 매번 화풍이 바뀝니다. 원본이 이미 원하는 그림이니 생성할 이유가 없습니다.
- 새로 만들 것은 **뒷모습 1장뿐**입니다. 원본을 첨부하고, 가능하면 "새로 그리기"가 아니라 **이미지 편집(수정) 모드**에서 원본을 고치게 하세요. 화풍이 덜 바뀝니다.

## 1·2판 결과가 원본과 달랐던 점 (픽셀 측정 기준)

| | 원본 | 1·2판 결과 |
|---|---|---|
| 선 | 바깥 테두리만 은은한 갈색, **면과 면 사이에 선이 없음** | 면마다 진한 갈색 `#704020` 선이 그어져 상자처럼 딱딱함 |
| 하이라이트 | **없음**, 면이 고르게 칠해짐 | 방석·등받이 모서리에 밝은 하이라이트 줄 |
| 색 | 탁하고 연함: 나무 `#cb9b6a`/`#a6785c`, 파랑 `#98bbd7`/`#7fa2c2` | 주황빛이 강하고 진함: 나무 `#c09050`/`#906040` |
| 등받이 | **두꺼운 판**. 나무는 위쪽과 오른쪽 옆면에만 보이고, 파란 쿠션이 왼쪽 끝까지 덮음 | 얇은 판. 왼쪽에도 나무 기둥이 보이는 액자 모양 |
| 좌석 | 방석이 나무판 끝까지 덮고, 그 아래 얇은 나무 띠 | 방석 둘레로 나무 턱이 드러남 |
| 다리 | 적당히 가늘고, 좌석 모서리보다 살짝 안쪽 | 굵고 각진 기둥 |

## 뒷모습 → `chair_b.webp` (원본 의자 그림 첨부)

```
Edit the attached image. It is a finished pixel art game asset of a chair, and
it is the style master: keep its exact art style, colors, pixel size, softness
and proportions. Only change the viewing side: show the SAME chair rotated 180
degrees, so its back is toward the viewer.

Style, copied from the attached image:
- Soft, low-contrast, slightly muted pixel art. Each face is filled with one
  flat color.
- Only the outer silhouette has a thin soft brown edge. NO dark lines between
  faces, NO inner outlines, NO bright highlight lines on edges, NO bevels.
- Colors: wood top/light face #e2b884, wood left face #cb9b6a, wood right face
  #a6785c, wood edge #6b4229; cushion top #98bbd7, cushion side #7fa2c2.
  Do not make the wood more orange or darker than this.
- Isometric 2:1 dimetric camera, same as the attached image. Plain flat white
  background. No shadow, no floor, no text.

What the back view shows:
- The backrest is now nearest the viewer, standing along the lower-left edge of
  the seat. We see its rear: ONE flat, plain wooden panel in #cb9b6a, as thick a
  slab as in the original (its top edge and right side show the thickness in
  #e2b884 and #a6785c). No frame lines, no inset panel, no rails, no grooves.
  No blue on this side.
- Behind it, to the upper-right, part of the blue seat cushion top and its right
  side show, with the thin wooden seat band under it — same thickness as the
  original.
- Four legs exactly like the original: same thickness, same short length, set
  slightly inside the seat corners. The two near legs are under the backrest.

Same size and footprint as the original: the chair fits a 1 x 1 x 1.5 cube box,
the lowest leg tip is at the bottom of the image, the overall width is the same.
Do not mirror the original — the backrest must move to the lower-left side.
```

## 혹시 앞모습도 다시 만들어야 할 때 (원본 첨부)

같은 세트로 다른 색 의자를 만들 때 등에 씁니다. `Object` 줄만 바꾸면 됩니다.

```
Recreate the attached pixel art chair exactly: same art style, colors, pixel
size, proportions and camera. Do not redesign it.

Style, copied from the attached image:
- Soft, low-contrast, slightly muted pixel art. Each face is filled with one
  flat color.
- Only the outer silhouette has a thin soft brown edge. NO dark lines between
  faces, NO inner outlines, NO bright highlight lines on edges, NO bevels.
- Colors: wood top/light face #e2b884, wood left face #cb9b6a, wood right face
  #a6785c, wood edge #6b4229; cushion top #98bbd7, cushion side #7fa2c2.
- Isometric 2:1 dimetric camera. Plain flat white background. No shadow, no
  floor, no text.

Object: wooden dining chair, front faces the bottom-left. Thick backrest slab
along the upper-right edge of the seat; its front is fully covered by a blue
cushion panel that reaches the left edge, and wood shows only on its top edge
and its right side. Seat cushion covers the seat board edge to edge, with a thin
wooden band under it. Four medium-thin square legs, slightly inside the seat
corners, about 0.5 cube visible. Fits a 1 x 1 x 1.5 cube box.
```

## 받은 그림 점검

- [ ] 면과 면 사이에 진한 선이 없는가 (원본처럼 면이 색만으로 구분되는가)
- [ ] 하이라이트 줄이 없는가
- [ ] 나무색이 원본만큼 연하고 탁한가 (주황으로 진해지지 않았는가)
- [ ] 등받이가 두꺼운 판인가, 뒤판에 장식이 없는가
- [ ] 다리 굵기·길이가 원본과 같은가
- [ ] 좌우 반전이 아니라 등받이가 왼쪽 아래로 왔는가

# 가구 그림 생성 요청문 (프롬프트) 가이드

규격 수치는 [README.md](README.md)와 같습니다. 이 문서는 **그림 생성 AI에 그대로 붙여 넣는 요청문**과, 크기(`w×d×h`)별로 요청문에 덧붙일 조건을 모아 둔 것입니다.

> AI는 도트 수를 정확히 못 맞춥니다. **비율·시점·방향·배경**만 정확히 요청하고, 정확한 크기 맞춤은 제가 후처리(배경 제거 → 칸에 맞춰 크기 조정 → 도트 격자 변환)로 합니다.

## 0. 먼저 알아둘 것

- **참고 이미지로 함께 첨부**: ① 빈 방 샘플, ② 이미 등록된 침대(앞·뒤). 화풍·시점·선 굵기를 맞추는 데 가장 효과가 큽니다.
- **상자 비유가 제일 잘 먹힙니다.** "이 가구는 정육면체 칸 `w × d × h`개 크기의 상자 안에 딱 들어간다"고 말하세요. (1칸 = 바닥 1칸 위에 올린 정육면체 1개, 높이 1층 = 그 정육면체의 높이.)
- **배경은 단색 흰색**으로 요청하세요. 단, 가구 안에 순수한 흰색을 쓰면 배경과 섞이니 "가구에 #ffffff 사용 금지, 흰 부분은 #f0f0f8 사용"을 꼭 넣으세요.
- 한 번에 **한 가구, 한 방향**씩. 앞모습을 받은 뒤 뒷모습을 따로 요청하고, 뒷모습에는 앞모습 이미지를 첨부하세요.

## 1. 공통 블록 (모든 요청문 맨 앞에 붙이기)

```
Pixel art game asset, isometric 2:1 dimetric view (every horizontal edge runs at
exactly 2 pixels across per 1 pixel down, i.e. 26.57 degrees), same camera as the
attached reference images. Crisp 1-pixel dots, no anti-aliasing, no blur, no
dithering noise, limited palette (max 24 colors), consistent pixel size across
the whole image. Soft pastel palette. Dark brown / muted purple outline, 1 pixel
thick, never pure black. Light comes from the upper left, shading is gentle.
Plain flat white background (#ffffff). Do NOT use pure white (#ffffff) or any
near-white inside the object; use #f0f0f8 for white parts. No ground shadow, no
cast shadow, no floor, no wall, no text, no logo, no watermark, no props that are
not part of the object. The whole object is fully visible, centered, with margin
around it.
```

## 2. 크기 지정 블록 (칸 수만 바꿔서 사용)

`{W}`=가로 칸, `{D}`=세로(깊이) 칸, `{H}`=높이 층

```
The object fits exactly inside a box that is {W} cubes wide, {D} cubes deep and {H}
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a {W} x {D} rectangle, ratio {W}:{D}. Its height is {H} times the
width of one floor tile edge. The footprint's long side ({W} side) runs along the
BACK-RIGHT wall direction (down-right to up-left... see below). Do not exceed the
box; nothing sticks out.
```

방향 문장(앞모습/뒷모습 중 하나를 덧붙임)은 3장에 있습니다.

## 3. 방향 블록

**앞모습 (`<id>.webp`)** — 원본 방향

```
Orientation: the object stands against the back-right wall; its FRONT faces the
bottom-left of the image. Its {W}-cube side runs from upper-left to lower-right
(along the right wall), its {D}-cube side runs from the upper-right to the
lower-left (toward the viewer).
```

**뒷모습 (`<id>_b.webp`)** — 앞모습 이미지를 함께 첨부

```
Same object, same size, same camera and same bounding box as the attached front
view, but rotated 180 degrees: now its BACK is toward the viewer at the lower-left
and its front faces the upper-right. The footprint position and the lowest corner
must stay identical to the attached image. Keep all colors identical.
```

앞뒤가 같은 가구(화분, 스탠드, 둥근 테이블, 소품)는 앞모습만 요청합니다.

## 4. 종류별 조건

### 4-1. 바닥 가구 (`floor`) — 예: 침대 `2×3×1.5`

덧붙일 조건:
- 캔버스 비율은 **너비 : 높이 ≈ (W+D)×32 : ((W+D)×16 + H×40)**. 아래 표 참고.
- 가구의 **가장 낮은 앞쪽 모서리(바닥 꼭짓점)가 이미지 맨 아래 가까이**에 오게 (여백 최소).
- 다리가 있으면 다리 끝이 바닥 마름모 안에 있어야 함.
- 윗면에 소품을 올릴 가구(책상·서랍장 등)는 **상판이 평평**하고 비어 있어야 함 (위에 물건 그리지 않기).

| 크기 | 예 | 요청문에 넣을 한 줄 |
|---|---|---|
| 1×1×1 | 낮은 테이블 | "fits a 1 x 1 x 1 cube box, as wide as it is deep and as tall as it is wide" |
| 1×1×1.5 | 의자, 서랍장 | "1 x 1 x 1.5 box: height is one and a half times its width" |
| 1×1×2 | 화장대 | "1 x 1 x 2 box: twice as tall as wide" |
| 1×1×3 | 책장, 스탠드 | "1 x 1 x 3 box: three times as tall as wide, tall and slim" |
| 2×1×1.5 | 책상, 소파 | "2 x 1 x 1.5 box: twice as long as deep, 1.5 cubes tall" |
| 2×1×3 | 옷장 | "2 x 1 x 3 box: wide and very tall, 3 cubes tall" |
| 2×2×1.5 | 큰 침대 | "2 x 2 x 1.5 box, square footprint" |
| 2×3×1.5 | 침대 | "2 x 3 x 1.5 box: 3 cubes long, 2 wide, headboard reaches 1.25 cubes" |

### 4-2. 러그 (`rug`) — 예: `3×2×0`

```
Flat rug lying on the floor, thickness at most 2 pixels, seen from the same
isometric camera. Its floor footprint is a {W} x {D} rectangle (or ellipse inside
that rectangle for a round rug). Nothing stands on it. The rug touches the bottom
corner of the image.
```

### 4-3. 소품 (`small`) — 예: 곰인형, 노트북, 컵케이크

```
Small prop that fits inside a 1 x 1 x 1 box but only fills about 60% of the tile
width and at most one cube tall. Seen from the same isometric camera. The
contact point with the table is at the bottom center of the image. Symmetric
enough to look fine when mirrored.
```

### 4-4. 벽 장식 (`wall`) — 예: 창문 `2×2`, 액자 `1×1`, 깃발 `3×0.5`

```
Flat wall decoration, drawn as if hung on the LEFT wall of an isometric room:
vertical lines stay vertical, horizontal lines slope DOWN toward the LEFT at 2
pixels across per 1 pixel down (the right end of the bottom edge is higher than
the left end). Width is {WW} tiles, height is {HH} cubes (one cube height = one
tile edge width). It is completely flat against the wall, no depth, no frame
sticking out, no wall background, no shadow.
```

크기별 한 줄: `1×1` 액자·시계 / `1×2` 세로 족자 / `2×0.5` 선반 / `2×2` 창문 / `3×0.5` 가랜드.

### 4-5. 벽지·바닥 무늬 (`wallpaper`, `flooring`)

```
Seamless tileable pixel art pattern, square, {64 or 128} x {64 or 128} pixels,
viewed flat (wallpaper: straight on; floor: straight down from above), soft
pastel colors, repeats perfectly on all four edges, no perspective, no shading
gradient, no objects crossing the edges.
```

## 5. 완성 요청문 예시 — 침대 앞모습

```
(공통 블록 1장)
Object: a double bed with a wooden headboard, blue blanket, a white pillow.
(크기 지정 블록: W=2, D=3, H=1.5)
(방향 블록: 앞모습)
The headboard stands at the upper-right end of the bed, against the back-right
wall direction; the foot of the bed points to the lower-left.
```

침대 뒷모습은 같은 요청문에 **뒷모습 방향 블록**과 앞모습 이미지 첨부를 추가합니다.

## 6. 받은 그림 점검표 (제가 후처리 전에 보는 것)

- [ ] 시점이 2:1인가 (변이 모두 평행한 2:1 계단, 원근 왜곡 없음)
- [ ] 비율이 `w:d:h` 와 대략 맞는가 (±15%는 제가 늘리기/줄이기로 보정)
- [ ] 바닥 그림자·배경 소품이 없는가
- [ ] 앞모습과 뒷모습의 바깥 틀(맨 아래 모서리, 폭)이 같은가
- [ ] 흰 배경과 섞이는 흰 부분이 없는가 (있으면 배경 제거가 구멍을 낼 수 있음)

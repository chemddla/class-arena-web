# 가구·소품 그림 생성 요청문 모음 (복사해서 바로 쓰기)

[PROMPTS.md](PROMPTS.md)의 공통 블록·크기 블록·방향 블록·종류별 조건을, 등록된 모든 항목에 대해 **숫자와 외형 묘사까지 채워 한 덩어리로 완성**한 것입니다. 코드블록 안의 영어 문장을 통째로 그림 생성 AI에 붙여 넣으면 됩니다. 규격 수치는 [README.md](README.md) 4장 표 기준입니다.

## 사용법

1. **참고 이미지 첨부**: ① 빈 방 샘플, ② 등록된 침대 앞·뒤(`bed_single.webp`, `bed_single_b.webp`)를 매번 함께 올립니다. 화풍·시점·선 굵기가 맞습니다.
2. **한 번에 한 항목, 한 방향.** 가구는 **앞모습 → 뒷모습 순서**로: 앞모습을 먼저 받은 뒤, 그 이미지를 첨부하고 *뒷모습 요청문*을 넣습니다. (뒷모습은 앞모습과 같은 상자·같은 맨 아래 모서리여야 해요.)
3. 결과가 마음에 들면 파일명을 `<id>.webp`(앞/단일), `<id>_b.webp`(뒷)로 저장해 넘겨 주세요. 크기가 정확히 안 맞아도 후처리로 맞춥니다.
4. 앞뒤가 같은 항목은 요청문이 **1장**뿐입니다(티 테이블·큰 화분·스탠드 조명·러그·소품).
5. 벽 장식·벽지·바닥은 방향 블록이 없습니다. 벽지·바닥은 **참고 이미지 없이** 만들어도 됩니다(정사각 이음매 무늬).
6. 각 요청문에는 흰 배경 / 가구 안 순수 흰색(#ffffff) 금지(#f0f0f8 사용) / 그림자·글자 금지 문장이 이미 들어 있습니다. 지우지 마세요.

## 세트 통일 규칙 (모든 요청문에 이미 반영됨)

**색 팔레트 (주색 4 + 보조)**

| 이름 | hex | 쓰임 |
|---|---|---|
| 파스텔 분홍 | `#fbd5e2` | 가구 본체·몸통 |
| 진한 분홍(포인트) | `#f7a8c4` | 포인트·리본·하트 |
| 연보라 | `#d7b8f5` | 쿠션·트림·다리 |
| 크림 | `#fff1e6` | 상판·받침·장식 |
| 보조: 밝은 나무 `#f1cfa6` · 분홍 철제 `#e98fb0` · 크림금 손잡이 `#f8d9a0` · 외곽선 `#6b4a5e` · 흰색 대용 `#f0f0f8` | | |

**공통 모티브**: 하트 모양 철제 장식(분홍 `#e98fb0`), 둥글고 말랑한 모서리, 크림금 동그란 손잡이, 파스텔 톤(순흰·순검정 금지).

각 요청문의 `Style:` 문단이 이 팔레트와 모티브를 그대로 담고 있습니다.

## 항목 한눈에 보기

| 종류 | 개수 | 요청문 장수 |
|---|---|---|
| 가구 | 12종 (침대는 완료) | 앞뒤 2장 8종 + 1장 3종 → 11종·19장 |
| 러그 | 3종 | 3장 |
| 소품 | 6종 | 6장 |
| 벽 장식 | 5종 | 5장 |
| 벽지 | 6종(하얀 벽지는 기본 무료) | 6장 |
| 바닥 | 5종(하얀 타일은 기본 무료) | 5장 |

---

## 1. 가구 (floor)

### 1-0. 포근 침대 `bed_single` — ✅ 그림 등록 완료 (`bed_single.webp`, `bed_single_b.webp`). 다시 만들 필요 없음. 규격 `2×3×1.5`.

### 1-1. 옷장 `wardrobe`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `wardrobe` | 옷장 | `2×1×3` | 96×168 도트 | 2장 (앞·뒤) |

**앞모습 요청문** → `wardrobe.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a tall two-door wardrobe in pastel pink (#fbd5e2) with a lavender (#d7b8f5) crown molding and a cream (#fff1e6) plinth. Two doors with soft rounded raised panels; on each door a heart-shaped pink wrought-iron ornament (#e98fb0) and a small cream-gold round knob. Short rounded feet. Flat top.
The object fits exactly inside a box that is 2 cubes wide, 1 cubes deep and 3
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 2 x 1 rectangle, ratio 2:1. Its height is 3 times the
width of one floor tile edge. 2 x 1 x 3 box: wide and very tall, 3 cubes tall. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image.

Orientation: the object stands against the back-right wall; its FRONT faces the
bottom-left of the image. Its 2-cube side runs from upper-left to lower-right
(along the right wall), its 1-cube side runs from the upper-right to the
lower-left (toward the viewer).
```

**뒷모습 요청문** (앞모습 이미지 첨부 필수) → `wardrobe_b.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: the back of the same wardrobe: a plain pastel pink (#fbd5e2) back panel with three subtle vertical plank lines, the lavender crown molding and cream plinth wrap around, no doors, no heart ornaments, no knobs.
(The attached front-view image shows the same object. Draw only what the back would look like: plain panel, same colors and outline.)

The object fits exactly inside a box that is 2 cubes wide, 1 cubes deep and 3
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 2 x 1 rectangle, ratio 2:1. Its height is 3 times the
width of one floor tile edge. 2 x 1 x 3 box: wide and very tall, 3 cubes tall. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image.

Same object, same size, same camera and same bounding box as the attached front
view, but rotated 180 degrees: now its BACK is toward the viewer at the lower-left
and its front faces the upper-right. The footprint position and the lowest corner
must stay identical to the attached image. Keep all colors identical.
```

### 1-2. 공부 책상 `desk`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `desk` | 공부 책상 | `2×1×1.5` | 96×108 도트 | 2장 (앞·뒤) |

**앞모습 요청문** → `desk.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a study desk with a flat, empty, cream-wood (#f1cfa6) tabletop whose surface is 1.4 cubes high, edged in pastel pink (#fbd5e2). On the front-left side a pastel pink drawer unit with two drawers, each with a cream-gold round knob; on the other side two slim lavender (#d7b8f5) legs with small heart-shaped wrought-iron braces (#e98fb0). Rounded corners.
The object fits exactly inside a box that is 2 cubes wide, 1 cubes deep and 1.5
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 2 x 1 rectangle, ratio 2:1. Its height is 1.5 times the
width of one floor tile edge. 2 x 1 x 1.5 box: twice as long as deep, 1.5 cubes tall. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image. The top surface is flat and completely empty (nothing placed on it).

Orientation: the object stands against the back-right wall; its FRONT faces the
bottom-left of the image. Its 2-cube side runs from upper-left to lower-right
(along the right wall), its 1-cube side runs from the upper-right to the
lower-left (toward the viewer).
```

**뒷모습 요청문** (앞모습 이미지 첨부 필수) → `desk_b.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: the back of the same desk: a pastel pink modesty panel covers the back between the legs with a small heart cut-out (#e98fb0 edge), the drawer unit seen from behind as a plain pink side, same tabletop, same legs.
(The attached front-view image shows the same object. The tabletop stays flat and empty.)

The object fits exactly inside a box that is 2 cubes wide, 1 cubes deep and 1.5
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 2 x 1 rectangle, ratio 2:1. Its height is 1.5 times the
width of one floor tile edge. 2 x 1 x 1.5 box: twice as long as deep, 1.5 cubes tall. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image. The top surface is flat and completely empty (nothing placed on it).

Same object, same size, same camera and same bounding box as the attached front
view, but rotated 180 degrees: now its BACK is toward the viewer at the lower-left
and its front faces the upper-right. The footprint position and the lowest corner
must stay identical to the attached image. Keep all colors identical.
```

### 1-3. 의자 `chair`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `chair` | 의자 | `1×1×1.5` | 64×92 도트 | 2장 (앞·뒤) |

**앞모습 요청문** → `chair.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a small cute chair: lavender (#d7b8f5) square seat cushion with a cream trim, pastel pink (#fbd5e2) wooden frame and four short legs, and a backrest that has a heart-shaped cut-out. The backrest stands at the upper-right back edge of the seat. Rounded corners.
The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 1.5
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 1.5 times the
width of one floor tile edge. 1 x 1 x 1.5 box: height is one and a half times its width. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image.

Orientation: the object stands against the back-right wall; its FRONT faces the
bottom-left of the image. Its 1-cube side runs from upper-left to lower-right
(along the right wall), its 1-cube side runs from the upper-right to the
lower-left (toward the viewer).
```

**뒷모습 요청문** (앞모습 이미지 첨부 필수) → `chair_b.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: the back of the same chair: the backrest seen from behind in pastel pink with the same heart cut-out and a small pink wrought-iron heart (#e98fb0) on the rail; the seat cushion is hidden behind it except its edge.
(The attached front-view image shows the same object. Backrest now faces the viewer.)

The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 1.5
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 1.5 times the
width of one floor tile edge. 1 x 1 x 1.5 box: height is one and a half times its width. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image.

Same object, same size, same camera and same bounding box as the attached front
view, but rotated 180 degrees: now its BACK is toward the viewer at the lower-left
and its front faces the upper-right. The footprint position and the lowest corner
must stay identical to the attached image. Keep all colors identical.
```

### 1-4. 말랑 소파 `sofa`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `sofa` | 말랑 소파 | `2×1×1.5` | 96×108 도트 | 2장 (앞·뒤) |

**앞모습 요청문** → `sofa.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a soft, puffy two-seater sofa in lavender (#d7b8f5) with round pillow-like armrests and a rounded backrest, two seat cushions with a slightly lighter lavender top, two small pink (#fbd5e2) heart-shaped throw cushions attached to the backrest, four short cream-wood (#f1cfa6) feet. Marshmallow-like rounded shapes.
The object fits exactly inside a box that is 2 cubes wide, 1 cubes deep and 1.5
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 2 x 1 rectangle, ratio 2:1. Its height is 1.5 times the
width of one floor tile edge. 2 x 1 x 1.5 box: twice as long as deep, 1.5 cubes tall. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image.

Orientation: the object stands against the back-right wall; its FRONT faces the
bottom-left of the image. Its 2-cube side runs from upper-left to lower-right
(along the right wall), its 1-cube side runs from the upper-right to the
lower-left (toward the viewer).
```

**뒷모습 요청문** (앞모습 이미지 첨부 필수) → `sofa_b.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: the back of the same sofa: a smooth lavender (#d7b8f5) backrest panel with a single vertical center seam and a small pink wrought-iron heart badge (#e98fb0) in the middle, rounded armrest backs, same feet.
(The attached front-view image shows the same object. The pillows are not visible from behind.)

The object fits exactly inside a box that is 2 cubes wide, 1 cubes deep and 1.5
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 2 x 1 rectangle, ratio 2:1. Its height is 1.5 times the
width of one floor tile edge. 2 x 1 x 1.5 box: twice as long as deep, 1.5 cubes tall. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image.

Same object, same size, same camera and same bounding box as the attached front
view, but rotated 180 degrees: now its BACK is toward the viewer at the lower-left
and its front faces the upper-right. The footprint position and the lowest corner
must stay identical to the attached image. Keep all colors identical.
```

### 1-5. 책장 `bookshelf`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `bookshelf` | 책장 | `1×1×3` | 64×152 도트 | 2장 (앞·뒤) |

**앞모습 요청문** → `bookshelf.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a tall slim bookshelf in cream-wood (#f1cfa6) with a pastel pink (#fbd5e2) frame and four open shelves filled with colorful pastel book spines (pink, lavender, mint #b9e2d0, cream) with no readable titles, and a few small decorations: one tiny heart-shaped bookend in pink wrought iron (#e98fb0). A cream plinth at the bottom.
The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 3
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 3 times the
width of one floor tile edge. 1 x 1 x 3 box: three times as tall as wide, tall and slim. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image.

Orientation: the object stands against the back-right wall; its FRONT faces the
bottom-left of the image. Its 1-cube side runs from upper-left to lower-right
(along the right wall), its 1-cube side runs from the upper-right to the
lower-left (toward the viewer).
```

**뒷모습 요청문** (앞모습 이미지 첨부 필수) → `bookshelf_b.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: the back of the same bookshelf: a plain pastel pink (#fbd5e2) back panel with two horizontal plank lines, the frame edges in cream-wood, no books visible.
(The attached front-view image shows the same object. Books are hidden from behind.)

The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 3
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 3 times the
width of one floor tile edge. 1 x 1 x 3 box: three times as tall as wide, tall and slim. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image.

Same object, same size, same camera and same bounding box as the attached front
view, but rotated 180 degrees: now its BACK is toward the viewer at the lower-left
and its front faces the upper-right. The footprint position and the lowest corner
must stay identical to the attached image. Keep all colors identical.
```

### 1-6. 서랍장 `dresser`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `dresser` | 서랍장 | `1×1×1.5` | 64×92 도트 | 2장 (앞·뒤) |

**앞모습 요청문** → `dresser.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a chest of drawers in pastel pink (#fbd5e2) with a flat, empty, cream (#fff1e6) top and three stacked drawers; each drawer has a heart-shaped cream-gold knob (#f8d9a0) and a lavender (#d7b8f5) trim line. Four short rounded feet.
The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 1.5
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 1.5 times the
width of one floor tile edge. 1 x 1 x 1.5 box: height is one and a half times its width. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image. The top surface is flat and completely empty (nothing placed on it).

Orientation: the object stands against the back-right wall; its FRONT faces the
bottom-left of the image. Its 1-cube side runs from upper-left to lower-right
(along the right wall), its 1-cube side runs from the upper-right to the
lower-left (toward the viewer).
```

**뒷모습 요청문** (앞모습 이미지 첨부 필수) → `dresser_b.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: the back of the same dresser: a plain pastel pink (#fbd5e2) back panel with a lavender trim line, flat cream top, no drawers, no knobs.
(The attached front-view image shows the same object. The top stays flat and empty.)

The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 1.5
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 1.5 times the
width of one floor tile edge. 1 x 1 x 1.5 box: height is one and a half times its width. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image. The top surface is flat and completely empty (nothing placed on it).

Same object, same size, same camera and same bounding box as the attached front
view, but rotated 180 degrees: now its BACK is toward the viewer at the lower-left
and its front faces the upper-right. The footprint position and the lowest corner
must stay identical to the attached image. Keep all colors identical.
```

### 1-7. 티 테이블 `tea_table`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `tea_table` | 티 테이블 | `1×1×1` | 64×72 도트 | 1장 (앞뒤 같음) |

**앞모습 요청문** → `tea_table.webp` (모든 방향 공용)

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a small round tea table with a flat, empty, round cream (#fff1e6) top edged in pastel pink (#fbd5e2), supported by three or four slim legs of pink wrought iron (#e98fb0) bent into heart-shaped curves, with a lavender (#d7b8f5) ring brace near the bottom. It looks identical from all four sides, so no front or back.
The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 1
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 1 times the
width of one floor tile edge. It fits a 1 x 1 x 1 cube box, as wide as it is deep and as tall as it is wide. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image. The top surface is flat and completely empty (nothing placed on it).

Orientation: the object stands against the back-right wall; its FRONT faces the
bottom-left of the image. Its 1-cube side runs from upper-left to lower-right
(along the right wall), its 1-cube side runs from the upper-right to the
lower-left (toward the viewer).

Because it is rotationally symmetric, this single image is used for every direction.
```

### 1-8. 하트 화장대 `vanity`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `vanity` | 하트 화장대 | `1×1×2` | 64×112 도트 | 2장 (앞·뒤) |

**앞모습 요청문** → `vanity.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a vanity dressing table: a lavender (#d7b8f5) base with one small drawer with a cream-gold knob, a flat cream (#fff1e6) tabletop at about half height (1 cube), and above it a large heart-shaped mirror in a pink wrought-iron frame (#e98fb0) with a pale lavender-blue reflective glass (#e6f3ff, no reflections of objects). Small cream-gold ball finials. The top of the mirror reaches 2 cubes.
The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 2
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 2 times the
width of one floor tile edge. 1 x 1 x 2 box: twice as tall as wide. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image.

Orientation: the object stands against the back-right wall; its FRONT faces the
bottom-left of the image. Its 1-cube side runs from upper-left to lower-right
(along the right wall), its 1-cube side runs from the upper-right to the
lower-left (toward the viewer).
```

**뒷모습 요청문** (앞모습 이미지 첨부 필수) → `vanity_b.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: the back of the same vanity: the back of the heart-shaped mirror as a plain pastel pink (#fbd5e2) heart-shaped board with a pink wrought-iron rim (#e98fb0), two thin support posts, and a plain lavender (#d7b8f5) back panel on the base.
(The attached front-view image shows the same object. Mirror glass is not visible from behind.)

The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 2
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 2 times the
width of one floor tile edge. 1 x 1 x 2 box: twice as tall as wide. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image.

Same object, same size, same camera and same bounding box as the attached front
view, but rotated 180 degrees: now its BACK is toward the viewer at the lower-left
and its front faces the upper-right. The footprint position and the lowest corner
must stay identical to the attached image. Keep all colors identical.
```

### 1-9. 큰 화분 `plant_big`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `plant_big` | 큰 화분 | `1×1×2.5` | 64×132 도트 | 1장 (앞뒤 같음) |

**앞모습 요청문** → `plant_big.webp` (모든 방향 공용)

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a large potted plant: a round pastel pink (#fbd5e2) ceramic pot with a lavender (#d7b8f5) rim band and a small heart-shaped pink wrought-iron (#e98fb0) plate on its side, holding a lush monstera-like plant with soft pastel green leaves (#9fd8a0 and #b9e2d0). The leaves may stick out at most 4 pixels beyond the box. Looks the same from every side, so no front or back.
The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 2.5
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 2.5 times the
width of one floor tile edge. 1 x 1 x 2.5 box: two and a half times as tall as wide. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image.

Orientation: the object stands against the back-right wall; its FRONT faces the
bottom-left of the image. Its 1-cube side runs from upper-left to lower-right
(along the right wall), its 1-cube side runs from the upper-right to the
lower-left (toward the viewer).
```

### 1-10. 스탠드 조명 `floor_lamp`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `floor_lamp` | 스탠드 조명 | `1×1×3` | 64×152 도트 | 1장 (앞뒤 같음) |

**앞모습 요청문** → `floor_lamp.webp` (모든 방향 공용)

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a floor standing lamp: a round pastel pink (#fbd5e2) base, a slim pink wrought-iron pole (#e98fb0) with a small heart-shaped ornament halfway up, and a round lampshade in warm cream-yellow (#fde39a) with a lavender (#d7b8f5) trim at the bottom, softly glowing but with no light rays or halo. Looks the same from every side, so no front or back.
The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 3
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 3 times the
width of one floor tile edge. 1 x 1 x 3 box: three times as tall as wide, tall and slim. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image.

Orientation: the object stands against the back-right wall; its FRONT faces the
bottom-left of the image. Its 1-cube side runs from upper-left to lower-right
(along the right wall), its 1-cube side runs from the upper-right to the
lower-left (toward the viewer).
```

### 1-11. 장난감 상자 `toy_box`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `toy_box` | 장난감 상자 | `1×1×1` | 64×72 도트 | 2장 (앞·뒤) |

**앞모습 요청문** → `toy_box.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a toy chest in peach-pink (#ffc7a0 blended with #fbd5e2) with a flat, empty lid edged in lavender (#d7b8f5); the front panel has a big heart-shaped pink wrought-iron latch plate (#e98fb0) with a cream-gold knob and a tiny star-shaped cut-out. Rounded corners, four small round feet.
The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 1
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 1 times the
width of one floor tile edge. It fits a 1 x 1 x 1 cube box, as wide as it is deep and as tall as it is wide. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image. The top surface is flat and completely empty (nothing placed on it).

Orientation: the object stands against the back-right wall; its FRONT faces the
bottom-left of the image. Its 1-cube side runs from upper-left to lower-right
(along the right wall), its 1-cube side runs from the upper-right to the
lower-left (toward the viewer).
```

**뒷모습 요청문** (앞모습 이미지 첨부 필수) → `toy_box_b.webp`

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: the back of the same toy chest: a plain peach-pink (#ffc7a0 blended with #fbd5e2) back panel with a lavender (#d7b8f5) trim line, two pink wrought-iron hinges (#e98fb0), flat lid, no latch.
(The attached front-view image shows the same object. The lid stays flat and empty.)

The object fits exactly inside a box that is 1 cubes wide, 1 cubes deep and 1
cubes tall (one cube = one floor tile wide, same height as its width). Its floor
footprint is a 1 x 1 rectangle, ratio 1:1. Its height is 1 times the
width of one floor tile edge. It fits a 1 x 1 x 1 cube box, as wide as it is deep and as tall as it is wide. Do not exceed the box; nothing sticks out.
The lowest front corner of the object touches the bottom of the image. The top surface is flat and completely empty (nothing placed on it).

Same object, same size, same camera and same bounding box as the attached front
view, but rotated 180 degrees: now its BACK is toward the viewer at the lower-left
and its front faces the upper-right. The footprint position and the lowest corner
must stay identical to the attached image. Keep all colors identical.
```

---

## 2. 러그 (rug)

### 2-1. 동글 러그 `rug_round`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `rug_round` | 동글 러그 | `2×2×0` | 128×64 도트 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a round (elliptical in this view) rug in soft pastel pink (#f9c6dc) with two concentric rings: an inner ring of deep pink (#f7a8c4) and an outer scalloped edge in cream (#fff1e6); a tiny lavender (#d7b8f5) heart in the center. Small fringe-free rounded edge.

Flat rug lying on the floor, thickness at most 2 pixels, seen from the same
isometric camera. Its floor footprint is a 2 x 2 rectangle (or ellipse inside
that rectangle for a round rug). Nothing stands on it. The rug touches the bottom
corner of the image.

Orientation: seen from the top-front in the same isometric camera; the 2-cube side runs from upper-left to lower-right and the 2-cube side runs from upper-right to lower-left.
```

### 2-2. 하트 러그 `rug_heart`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `rug_heart` | 하트 러그 | `3×2×0` | 160×80 도트 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a heart-shaped rug whose heart fits inside the 3 x 2 rectangle, deep pink (#f7a8c4) with a lighter pastel pink (#fbd5e2) inner heart and a cream (#fff1e6) dotted stitch line along the edge. The heart is left-right mirror symmetric along its long axis.

Flat rug lying on the floor, thickness at most 2 pixels, seen from the same
isometric camera. Its floor footprint is a 3 x 2 rectangle (or ellipse inside
that rectangle for a round rug). Nothing stands on it. The rug touches the bottom
corner of the image.

Orientation: seen from the top-front in the same isometric camera; the 3-cube side runs from upper-left to lower-right and the 2-cube side runs from upper-right to lower-left.
```

### 2-3. 줄무늬 러그 `rug_stripe`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `rug_stripe` | 줄무늬 러그 | `2×3×0` | 160×80 도트 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a rectangular rug with rounded corners and wide soft stripes running along the 3-cube length, alternating lavender (#cdb8f2), pastel pink (#fbd5e2) and cream (#fff1e6), with small cream fringe tassels on the two short ends.

Flat rug lying on the floor, thickness at most 2 pixels, seen from the same
isometric camera. Its floor footprint is a 2 x 3 rectangle (or ellipse inside
that rectangle for a round rug). Nothing stands on it. The rug touches the bottom
corner of the image.

Orientation: seen from the top-front in the same isometric camera; the 2-cube side runs from upper-left to lower-right and the 3-cube side runs from upper-right to lower-left.
```

---

## 3. 소품 (small)

소품은 책상·서랍장 같은 상판 위에 올라갑니다. 캔버스는 64×40 도트 이하, 앞뒤 구분 없이 1장입니다.

### 3-1. 곰인형 `teddy`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `teddy` | 곰인형 | `1×1×0.65` (≤1층) | 64×40 도트 이하 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a cute sitting teddy bear plush in warm caramel-brown (#d9a06b) with a lighter cream muzzle (#fff1e6), a pink (#f7a8c4) bow tie and small dot eyes, front view toward the lower-left but nearly symmetric.

Small prop that fits inside a 1 x 1 x 1 box but only fills about 60% of the tile
width and at most one cube tall. Seen from the same isometric camera. The
contact point with the table is at the bottom center of the image. Symmetric
enough to look fine when mirrored.
```

### 3-2. 노트북 `laptop`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `laptop` | 노트북 | `1×1×0.45` (≤1층) | 64×40 도트 이하 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a small open laptop with a pastel silver-blue body (#cfd8e6), a pink (#fbd5e2) keyboard area and a lavender-tinted blank screen (#e6e0f8) with no logo and no readable text, a tiny heart sticker (#f7a8c4) on the lid.

Small prop that fits inside a 1 x 1 x 1 box but only fills about 60% of the tile
width and at most one cube tall. Seen from the same isometric camera. The
contact point with the table is at the bottom center of the image. Symmetric
enough to look fine when mirrored.
```

### 3-3. 책 더미 `book_stack`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `book_stack` | 책 더미 | `1×1×0.4` (≤1층) | 64×40 도트 이하 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a neat stack of three closed books in pink (#f2b5a0), lavender (#d7b8f5) and cream (#fff1e6) with pastel page edges and a small pink heart bookmark ribbon (#f7a8c4); covers have no text.

Small prop that fits inside a 1 x 1 x 1 box but only fills about 60% of the tile
width and at most one cube tall. Seen from the same isometric camera. The
contact point with the table is at the bottom center of the image. Symmetric
enough to look fine when mirrored.
```

### 3-4. 컵케이크 `cupcake`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `cupcake` | 컵케이크 | `1×1×0.45` (≤1층) | 64×40 도트 이하 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a cupcake with a pastel pink (#ffd1e0) swirl of frosting, a lavender (#d7b8f5) paper liner, sprinkles in mint, lavender and cream, and a small red-pink (#f7a8c4) heart on top.

Small prop that fits inside a 1 x 1 x 1 box but only fills about 60% of the tile
width and at most one cube tall. Seen from the same isometric camera. The
contact point with the table is at the bottom center of the image. Symmetric
enough to look fine when mirrored.
```

### 3-5. 꽃병 `flower_vase`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `flower_vase` | 꽃병 | `1×1×0.65` (≤1층) | 64×40 도트 이하 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a small round vase in pastel pink (#fbd5e2) with a lavender band, holding a bouquet of pastel flowers (pink #ffb8d0, lavender #d7b8f5, cream #fff1e6) with soft green leaves (#9fd8a0).

Small prop that fits inside a 1 x 1 x 1 box but only fills about 60% of the tile
width and at most one cube tall. Seen from the same isometric camera. The
contact point with the table is at the bottom center of the image. Symmetric
enough to look fine when mirrored.
```

### 3-6. 알람 시계 `alarm_clock`

| id | 이름 | `w×d×h` | 캔버스(최대) | 그림 장수 |
|---|---|---|---|---|
| `alarm_clock` | 알람 시계 | `1×1×0.45` (≤1층) | 64×40 도트 이하 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a round twin-bell alarm clock in pastel sky blue (#bfe3f5) with two small pink (#f7a8c4) bells on top, a cream (#fff1e6) clock face with simple tick marks (no numbers) and two short hands, and two tiny pink feet.

Small prop that fits inside a 1 x 1 x 1 box but only fills about 60% of the tile
width and at most one cube tall. Seen from the same isometric camera. The
contact point with the table is at the bottom center of the image. Symmetric
enough to look fine when mirrored.
```

---

## 4. 벽 장식 (wall)

벽에 납작하게 붙은 모습입니다. 캔버스 너비 = ww×32, 높이 = hh×40 + ww×16. 그림 왼쪽 아래 모서리가 벽 사각형의 가장 낮은 모서리입니다.

### 4-1. 아치 창문 `window_arch`

| id | 이름 | `ww×hh` | z(바닥에서 띄운 층) | 캔버스 | 그림 장수 |
|---|---|---|---|---|---|
| `window_arch` | 아치 창문 | `2×2` | z=1 | 64×112 도트 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: an arched window: a pastel pink (#f4b8c8) frame with an arched top, cream (#fff1e6) cross muntins, soft sky-blue glass (#dff0fb) with one little cloud in #f0f0f8, and two lavender (#d7b8f5) curtains tied at the sides with pink ribbons. A small pink wrought-iron heart (#e98fb0) at the keystone of the arch.

Flat wall decoration, drawn as if hung on the LEFT wall of an isometric room:
vertical lines stay vertical, horizontal lines slope DOWN toward the LEFT at 2
pixels across per 1 pixel down (the right end of the bottom edge is higher than
the left end). Width is 2 tiles, height is 2 cubes (one cube height = one
tile edge width). It is completely flat against the wall, no depth, no frame
sticking out, no wall background, no shadow.

Canvas ratio about 64 : 112 (width : height).
```

### 4-2. 액자 `photo_frame`

| id | 이름 | `ww×hh` | z(바닥에서 띄운 층) | 캔버스 | 그림 장수 |
|---|---|---|---|---|---|
| `photo_frame` | 액자 | `1×1` | z=2 | 32×56 도트 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a picture frame with a pastel yellow-cream (#f8d9a0) frame with heart-shaped corner ornaments in pink wrought iron (#e98fb0), holding a simple pastel illustration of a pink heart and two clouds on a lavender sky; no text, no faces.

Flat wall decoration, drawn as if hung on the LEFT wall of an isometric room:
vertical lines stay vertical, horizontal lines slope DOWN toward the LEFT at 2
pixels across per 1 pixel down (the right end of the bottom edge is higher than
the left end). Width is 1 tiles, height is 1 cubes (one cube height = one
tile edge width). It is completely flat against the wall, no depth, no frame
sticking out, no wall background, no shadow.

Canvas ratio about 32 : 56 (width : height).
```

### 4-3. 벽 선반 `wall_shelf`

| id | 이름 | `ww×hh` | z(바닥에서 띄운 층) | 캔버스 | 그림 장수 |
|---|---|---|---|---|---|
| `wall_shelf` | 벽 선반 | `2×0.5` | z=2 | 64×52 도트 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a wall shelf board in cream-wood (#f1cfa6) with two pink wrought-iron heart-shaped brackets (#e98fb0) and a pastel pink (#fbd5e2) front edge; the shelf itself is empty (nothing on it).

Flat wall decoration, drawn as if hung on the LEFT wall of an isometric room:
vertical lines stay vertical, horizontal lines slope DOWN toward the LEFT at 2
pixels across per 1 pixel down (the right end of the bottom edge is higher than
the left end). Width is 2 tiles, height is 0.5 cubes (one cube height = one
tile edge width). It is completely flat against the wall, no depth, no frame
sticking out, no wall background, no shadow.

Canvas ratio about 64 : 52 (width : height).
```

### 4-4. 벽시계 `wall_clock`

| id | 이름 | `ww×hh` | z(바닥에서 띄운 층) | 캔버스 | 그림 장수 |
|---|---|---|---|---|---|
| `wall_clock` | 벽시계 | `1×1` | z=2 | 32×56 도트 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a round wall clock with a pastel pink (#fbd5e2) rim, a cream (#fff1e6) face with small tick marks (no numbers), two short lavender (#d7b8f5) hands, and a small pink wrought-iron heart (#e98fb0) at the top of the rim.

Flat wall decoration, drawn as if hung on the LEFT wall of an isometric room:
vertical lines stay vertical, horizontal lines slope DOWN toward the LEFT at 2
pixels across per 1 pixel down (the right end of the bottom edge is higher than
the left end). Width is 1 tiles, height is 1 cubes (one cube height = one
tile edge width). It is completely flat against the wall, no depth, no frame
sticking out, no wall background, no shadow.

Canvas ratio about 32 : 56 (width : height).
```

### 4-5. 삼각 깃발 장식 `bunting`

| id | 이름 | `ww×hh` | z(바닥에서 띄운 층) | 캔버스 | 그림 장수 |
|---|---|---|---|---|---|
| `bunting` | 삼각 깃발 장식 | `3×0.5` | z=3.5 | 96×68 도트 | 1장 |

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

Style: cute, cozy girly bedroom set. Palette shared by the whole set:
pastel pink #fbd5e2, deep pink accent #f7a8c4, lavender #d7b8f5, cream #fff1e6;
light wood #f1cfa6 only where wood is needed; outline #6b4a5e. Recurring motifs:
heart-shaped wrought-iron details in pink metal (#e98fb0), rounded soft corners,
small cream-gold knobs (#f8d9a0). No pure white, no pure black.

Object: a bunting garland: a string hanging in a gentle smile curve with seven triangular flags alternating pastel pink (#ffc4dd), lavender (#d7b8f5), cream (#fff1e6) and deep pink (#f7a8c4), and a small heart-shaped flag at the center; no letters on the flags.

Flat wall decoration, drawn as if hung on the LEFT wall of an isometric room:
vertical lines stay vertical, horizontal lines slope DOWN toward the LEFT at 2
pixels across per 1 pixel down (the right end of the bottom edge is higher than
the left end). Width is 3 tiles, height is 0.5 cubes (one cube height = one
tile edge width). It is completely flat against the wall, no depth, no frame
sticking out, no wall background, no shadow.

Canvas ratio about 96 : 68 (width : height).
```

---

## 5. 벽지 (wallpaper)

이음매 없이 이어지는 정사각 무늬입니다. 배경 흰색 문장 대신, 무늬가 캔버스를 가득 채우고 순수 흰색(#ffffff)을 쓰지 않는다는 문장이 들어 있습니다.

### 5-1. 하얀 벽지 `wall_white`

| id | 이름 | 크기 | 가격 | 그림 장수 |
|---|---|---|---|---|
| `wall_white` | 하얀 벽지 | 64×64 도트 | 0 | 1장 |

```
Pixel art game texture. Crisp 1-pixel dots, no anti-aliasing, no blur, no dithering
noise, limited palette (max 12 colors), consistent pixel size. The pattern fills the
entire square canvas edge to edge (there is no separate background and no border).
Do NOT use pure white (#ffffff) anywhere; use #f0f0f8 for white parts. No shadow, no
text, no logo, no watermark, no outline around the image.

Pattern: a soft off-white (#f6f4fc) wallpaper with very subtle tone-on-tone vertical panel lines in #e9e6ec every 16 pixels; almost plain. (Default free wallpaper.)

Seamless tileable pixel art pattern, square, 64 x 64 pixels,
viewed flat (straight on, as a flat wall surface), soft
pastel colors, repeats perfectly on all four edges, no perspective, no shading
gradient, no objects crossing the edges.
```

### 5-2. 크림 벽지 `wall_cream`

| id | 이름 | 크기 | 가격 | 그림 장수 |
|---|---|---|---|---|
| `wall_cream` | 크림 벽지 | 64×64 도트 | 200 | 1장 |

```
Pixel art game texture. Crisp 1-pixel dots, no anti-aliasing, no blur, no dithering
noise, limited palette (max 12 colors), consistent pixel size. The pattern fills the
entire square canvas edge to edge (there is no separate background and no border).
Do NOT use pure white (#ffffff) anywhere; use #f0f0f8 for white parts. No shadow, no
text, no logo, no watermark, no outline around the image.

Pattern: a warm cream (#fff1e6) wallpaper with a subtle quilted diamond texture in #ffe0cc and tiny dots at the diamond corners.

Seamless tileable pixel art pattern, square, 64 x 64 pixels,
viewed flat (straight on, as a flat wall surface), soft
pastel colors, repeats perfectly on all four edges, no perspective, no shading
gradient, no objects crossing the edges.
```

### 5-3. 핑크 줄무늬 `wall_stripe`

| id | 이름 | 크기 | 가격 | 그림 장수 |
|---|---|---|---|---|
| `wall_stripe` | 핑크 줄무늬 | 64×64 도트 | 400 | 1장 |

```
Pixel art game texture. Crisp 1-pixel dots, no anti-aliasing, no blur, no dithering
noise, limited palette (max 12 colors), consistent pixel size. The pattern fills the
entire square canvas edge to edge (there is no separate background and no border).
Do NOT use pure white (#ffffff) anywhere; use #f0f0f8 for white parts. No shadow, no
text, no logo, no watermark, no outline around the image.

Pattern: wide vertical stripes alternating very pale pink (#fff0f5) and pastel pink (#fbd3e3), 8 pixels per stripe, with a thin cream pin-stripe in the middle of the pale ones.

Seamless tileable pixel art pattern, square, 64 x 64 pixels,
viewed flat (straight on, as a flat wall surface), soft
pastel colors, repeats perfectly on all four edges, no perspective, no shading
gradient, no objects crossing the edges.
```

### 5-4. 물방울 라일락 `wall_dot`

| id | 이름 | 크기 | 가격 | 그림 장수 |
|---|---|---|---|---|
| `wall_dot` | 물방울 라일락 | 64×64 도트 | 400 | 1장 |

```
Pixel art game texture. Crisp 1-pixel dots, no anti-aliasing, no blur, no dithering
noise, limited palette (max 12 colors), consistent pixel size. The pattern fills the
entire square canvas edge to edge (there is no separate background and no border).
Do NOT use pure white (#ffffff) anywhere; use #f0f0f8 for white parts. No shadow, no
text, no logo, no watermark, no outline around the image.

Pattern: a pale lilac (#f1e8ff) background with evenly spaced polka dots in lavender (#d9c6fb), arranged in a half-drop pattern, dots about 6 pixels wide.

Seamless tileable pixel art pattern, square, 64 x 64 pixels,
viewed flat (straight on, as a flat wall surface), soft
pastel colors, repeats perfectly on all four edges, no perspective, no shading
gradient, no objects crossing the edges.
```

### 5-5. 구름 하늘 `wall_cloud`

| id | 이름 | 크기 | 가격 | 그림 장수 |
|---|---|---|---|---|
| `wall_cloud` | 구름 하늘 | 128×128 도트 | 600 | 1장 |

```
Pixel art game texture. Crisp 1-pixel dots, no anti-aliasing, no blur, no dithering
noise, limited palette (max 12 colors), consistent pixel size. The pattern fills the
entire square canvas edge to edge (there is no separate background and no border).
Do NOT use pure white (#ffffff) anywhere; use #f0f0f8 for white parts. No shadow, no
text, no logo, no watermark, no outline around the image.

Pattern: a pale sky-blue (#e6f3ff) background with soft fluffy pixel clouds in #f0f0f8 (not pure white) scattered in a half-drop pattern, a few tiny pink hearts (#f9a8c8) between the clouds.

Seamless tileable pixel art pattern, square, 128 x 128 pixels,
viewed flat (straight on, as a flat wall surface), soft
pastel colors, repeats perfectly on all four edges, no perspective, no shading
gradient, no objects crossing the edges.
```

### 5-6. 하트 핑크 `wall_heart`

| id | 이름 | 크기 | 가격 | 그림 장수 |
|---|---|---|---|---|
| `wall_heart` | 하트 핑크 | 64×64 도트 | 600 | 1장 |

```
Pixel art game texture. Crisp 1-pixel dots, no anti-aliasing, no blur, no dithering
noise, limited palette (max 12 colors), consistent pixel size. The pattern fills the
entire square canvas edge to edge (there is no separate background and no border).
Do NOT use pure white (#ffffff) anywhere; use #f0f0f8 for white parts. No shadow, no
text, no logo, no watermark, no outline around the image.

Pattern: a pale pink (#ffe4ee) background with small pink hearts (#f9a8c8), about 8 pixels wide, in a half-drop pattern, with tiny cream dots between them.

Seamless tileable pixel art pattern, square, 64 x 64 pixels,
viewed flat (straight on, as a flat wall surface), soft
pastel colors, repeats perfectly on all four edges, no perspective, no shading
gradient, no objects crossing the edges.
```

---

## 6. 바닥 (flooring)

이음매 없이 이어지는 정사각 무늬입니다. 배경 흰색 문장 대신, 무늬가 캔버스를 가득 채우고 순수 흰색(#ffffff)을 쓰지 않는다는 문장이 들어 있습니다.

### 6-1. 하얀 타일 `floor_white`

| id | 이름 | 크기 | 가격 | 그림 장수 |
|---|---|---|---|---|
| `floor_white` | 하얀 타일 | 64×64 도트 | 0 | 1장 |

```
Pixel art game texture. Crisp 1-pixel dots, no anti-aliasing, no blur, no dithering
noise, limited palette (max 12 colors), consistent pixel size. The pattern fills the
entire square canvas edge to edge (there is no separate background and no border).
Do NOT use pure white (#ffffff) anywhere; use #f0f0f8 for white parts. No shadow, no
text, no logo, no watermark, no outline around the image.

Pattern: large off-white (#f6f4fc) square floor tiles with thin grout lines (#b4b2c0), one tile per 32 pixels, and tiny subtle speckles. (Default free floor.)

Seamless tileable pixel art pattern, square, 64 x 64 pixels,
viewed flat (straight down from above, as a flat floor surface), soft
pastel colors, repeats perfectly on all four edges, no perspective, no shading
gradient, no objects crossing the edges.
```

### 6-2. 밝은 나무 `floor_wood`

| id | 이름 | 크기 | 가격 | 그림 장수 |
|---|---|---|---|---|
| `floor_wood` | 밝은 나무 | 64×64 도트 | 300 | 1장 |

```
Pixel art game texture. Crisp 1-pixel dots, no anti-aliasing, no blur, no dithering
noise, limited palette (max 12 colors), consistent pixel size. The pattern fills the
entire square canvas edge to edge (there is no separate background and no border).
Do NOT use pure white (#ffffff) anywhere; use #f0f0f8 for white parts. No shadow, no
text, no logo, no watermark, no outline around the image.

Pattern: light wooden floor planks running in one direction, in two warm tones (#f1cfa6 and #e6bb8a), plank width 8 pixels, thin darker joint lines, staggered end joints.

Seamless tileable pixel art pattern, square, 64 x 64 pixels,
viewed flat (straight down from above, as a flat floor surface), soft
pastel colors, repeats perfectly on all four edges, no perspective, no shading
gradient, no objects crossing the edges.
```

### 6-3. 체크 타일 `floor_check`

| id | 이름 | 크기 | 가격 | 그림 장수 |
|---|---|---|---|---|
| `floor_check` | 체크 타일 | 64×64 도트 | 400 | 1장 |

```
Pixel art game texture. Crisp 1-pixel dots, no anti-aliasing, no blur, no dithering
noise, limited palette (max 12 colors), consistent pixel size. The pattern fills the
entire square canvas edge to edge (there is no separate background and no border).
Do NOT use pure white (#ffffff) anywhere; use #f0f0f8 for white parts. No shadow, no
text, no logo, no watermark, no outline around the image.

Pattern: a checkerboard of cream (#fff6ee) and pastel pink (#f8c9d8) square tiles, 16 pixels per square, with thin lighter grout lines.

Seamless tileable pixel art pattern, square, 64 x 64 pixels,
viewed flat (straight down from above, as a flat floor surface), soft
pastel colors, repeats perfectly on all four edges, no perspective, no shading
gradient, no objects crossing the edges.
```

### 6-4. 분홍 카펫 `floor_carpet`

| id | 이름 | 크기 | 가격 | 그림 장수 |
|---|---|---|---|---|
| `floor_carpet` | 분홍 카펫 | 64×64 도트 | 500 | 1장 |

```
Pixel art game texture. Crisp 1-pixel dots, no anti-aliasing, no blur, no dithering
noise, limited palette (max 12 colors), consistent pixel size. The pattern fills the
entire square canvas edge to edge (there is no separate background and no border).
Do NOT use pure white (#ffffff) anywhere; use #f0f0f8 for white parts. No shadow, no
text, no logo, no watermark, no outline around the image.

Pattern: a soft pink carpet in two tones (#fbd5e2 and #f4aac6) with a fine woven dot texture and a subtle small diamond pattern.

Seamless tileable pixel art pattern, square, 64 x 64 pixels,
viewed flat (straight down from above, as a flat floor surface), soft
pastel colors, repeats perfectly on all four edges, no perspective, no shading
gradient, no objects crossing the edges.
```

### 6-5. 민트 타일 `floor_tile`

| id | 이름 | 크기 | 가격 | 그림 장수 |
|---|---|---|---|---|
| `floor_tile` | 민트 타일 | 64×64 도트 | 500 | 1장 |

```
Pixel art game texture. Crisp 1-pixel dots, no anti-aliasing, no blur, no dithering
noise, limited palette (max 12 colors), consistent pixel size. The pattern fills the
entire square canvas edge to edge (there is no separate background and no border).
Do NOT use pure white (#ffffff) anywhere; use #f0f0f8 for white parts. No shadow, no
text, no logo, no watermark, no outline around the image.

Pattern: mint green square floor tiles (#e2f6ee) with thin grout lines in a deeper mint (#b9e2d0), one tile per 32 pixels, each tile with a tiny lighter highlight in its upper-left corner.

Seamless tileable pixel art pattern, square, 64 x 64 pixels,
viewed flat (straight down from above, as a flat floor surface), soft
pastel colors, repeats perfectly on all four edges, no perspective, no shading
gradient, no objects crossing the edges.
```

---

## 7. 규격 불일치·참고 사항

- **w×d×h**: README 4장 표와 `HOME_CATALOG`(1층=80 단위)를 모두 대조했고, 가구 12종·러그 3종·벽 장식 5종의 칸·높이·z 값은 **서로 일치**합니다. 이 문서는 표 값을 썼습니다.
- **항목 수**: 요청 지시서는 벽지 5종·바닥 4종이었으나 `HOME_CATALOG`에는 **벽지 6종**(하얀 벽지 `wall_white` 포함)·**바닥 5종**(하얀 타일 `floor_white` 포함)이 있습니다. 두 개는 무료 기본값이지만 빠짐없이 요청문을 넣었습니다. 기본값은 엔진 내장 무늬로 충분하면 건너뛰어도 됩니다.
- **소품 높이**: README는 "1×1×(≤1)"만 적었고 카탈로그의 소품 높이는 게임 단위 30~52(=0.4~0.65층)입니다. 소품 표의 `1×1×0.4~0.65`는 카탈로그 값이며, 엔진은 최소 0.5층으로 표시합니다.
- **하트 화장대**: 표는 `1×1×2`, 카탈로그 상판(`surface`)은 100(=1.25층)입니다. 요청문에는 상판을 약 1층 높이로 적었으니, 어긋나 보이면 상판 높이는 후처리에서 맞춥니다.
- **책상 상판 높이**: README "상판 1.4층"(카탈로그 `surface: 110` = 1.375층)과 같은 값입니다.
- **PROMPTS.md 2장 크기 블록**의 "(down-right to up-left... see below)" 문장은 이어지지 않는 문구라 이 문서에서는 뺐고, 대신 "맨 아래 앞 모서리가 이미지 맨 아래에 닿게"(4-1 조건)를 넣었습니다. 방향 블록은 PROMPTS.md 3장 그대로입니다.
- **티 테이블**은 둥근 상판이라 앞뒤가 같다고 보고 1장으로 했습니다(`back: true` 불필요). 카탈로그에 `back: true`를 붙일 가구는 옷장·책상·의자·소파·책장·서랍장·화장대·장난감 상자입니다.
- **벽지·바닥 요청문**은 PROMPTS.md 4-5의 문장을 쓰되, 공통 블록의 "흰 배경" 문장은 타일에 맞지 않아 "캔버스를 가득 채움 + 순수 흰색 금지(#f0f0f8)"로 바꿨습니다.


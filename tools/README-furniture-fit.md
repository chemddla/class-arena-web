# 가구 그림 맞춤 도구 (`tools/furniture-fit.cjs`)

AI가 만든 가구 그림(흰 배경, 1024px 안팎)을 방 꾸미기 도트 규격([assets/furniture/README.md](../assets/furniture/README.md))에 맞춰 `assets/furniture/<id>.webp`로 만들어 줍니다. 설치된 `sharp`만 씁니다. `index.html`은 건드리지 않습니다.

## 사용법

```bash
# 앞모습 한 장 (권장: --legs — 원본 비율 그대로, 다리 끝만 칸 꼭짓점에 맞춤)
node tools/furniture-fit.cjs 앞모습.png --id chair --w 1 --d 1 --h 1.5 --legs --refine

# 앞·뒤 두 장 (→ bed_single.webp, bed_single_b.webp)
node tools/furniture-fit.cjs 앞.png 뒤.png --id bed_single --w 2 --d 3 --h 1.5
#   같은 뜻: node tools/furniture-fit.cjs 앞.png --back 뒤.png --id ...
```

- `--w` 가로 칸 · `--d` 세로 칸 · `--h` 높이 층(0.5 단위, 러그는 0)
- 결과 webp → `assets/furniture/`, 5배 확대 확인용 PNG → `tools/furniture-fit-out/<id>_x5.png` (빨간 선 = 규격 상자, 파란 점 = 앵커)
- 옵션: `--legs`(다리 기준 맞춤, 권장), `--refine`(도트 세분화: 샘플의 원래 도트 크기를 재서 되돌린 뒤 Scale2x로 다듬음 — 샘플마다 다른 도트 굵기를 촘촘하게 통일, 권장), `--dot N`(원래 도트 크기 직접 지정), `--out`, `--preview`(폴더), `--colors 26`, `--tol 10`(배경색 허용 오차), `--stretch`(세로를 늘리고 줄여 비율이 바뀜 — 쓰지 않기), `--clear-holes`, `--no-guide`, `--dry`(파일 안 쓰고 보고만), `--help`

## 하는 일

1. **배경 제거**: 가장자리와 이어진 흰색만 투명 처리. 가구 안의 흰색·옅은 색은 지우지 않음. 흰 부분이 배경과 이어져 파인 것 같으면 경고.
2. **상자에 맞추기**: 가구 영역을 잘라 가로 `(w+d)×64`도트로 조정(바닥 앞꼭짓점 `w×64`, 맨 아래 — 1칸 128×64 규격). 원본 바닥 가장자리 기울기·앞꼭짓점 위치·높이를 재어 규격과 15% 넘게 다르면 어느 쪽이 어긋났는지 경고(납작/가파름, w:d 비율, 키 큼). 자동 보정은 `--stretch`를 줄 때만.
3. **도트 격자**: lanczos로 정수 도트로 줄이고, 알파는 0/255, 색은 26색(디더 없음).
4. **앞/뒤 점검**: 실루엣 겹침·높이·너비·앞꼭짓점 x를 비교해 어긋나면 경고. 높이는 아래 기준으로 맞춰 저장.
5. **요약 출력**: 최종 크기, 앵커, 색 수, 경고, 그리고 `HOME_CATALOG`에 넣을 `art: true, back: true` 한 줄.

## 알아둘 것

- 배경은 **순백(#fff)** 이어야 함. 가구의 흰 부분은 #f0f0f8처럼 살짝 다르게 요청([PROMPTS.md](../assets/furniture/PROMPTS.md)). 옅은 색이 지워지면 `--tol`을 줄이세요.
- 바닥 그림자(회색 번짐)는 지우지 못함 — 그림 생성 때 "그림자 없음"으로 요청.
- 의자 다리 사이처럼 가구 안에 갇힌 진짜 빈 공간은 기본으로 남김 → 필요하면 `--clear-holes` (등받이 살 사이 같은 작은 틈과 그 가장자리 번짐까지 비움. 틈이 하얗게 남으면 `--tol 30`).
- 앞·뒤가 한 장에 붙어 온 샘플은 먼저 두 장으로 나눠서 넣으세요.
- 경고가 있으면 `_x5.png`를 눈으로 확인한 뒤, 이상하면 그림을 다시 만들거나 `--stretch`.
- `tools/furniture-fit-out/`은 확인용이라 커밋하지 않아도 됩니다.

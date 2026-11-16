# 기공사 일반 공격 이펙트 시안 (pixelfx)

- `atk-a` 금빛 기탄 · `atk-b` 장풍 · `atk-c` 나선 기류 · `atk-d` 삼연 기탄 · `atk-e` 태극 기구슬 · `atk-f` 실타래 기구슬 (`atk-f-blue`는 같은 모양의 하늘색 판)
- 2판 (반짝임 없음, 2026-11-16 사용자 지시 "기공이라 반짝반짝 빛나는 이펙트는 안 어울림"): `qi-g` 기운 덩어리 · `qi-h` 기압 장풍 · `qi-i` 기류 띠 · `qi-j` 실타래 기구슬. 공용 `_qi.js` (별빛·번쩍·불꽃 가루 대신 안개·압력 고리·먼지)
- 1판 `atk-*`는 반짝임이 들어가 있어 참고용으로만 남김
- 기공포 시안 (일반 공격 J 바탕, `_jcore.js` 공용): `qi-cannon-a` 큰 실타래 포 · `qi-cannon-b` 나선 실 포 · `qi-cannon-c` 고리 꼬리 포. 모으기 0.6초(실이 감겨 들어옴) → 꿰뚫으며 날아감(적마다 작은 압력 고리) → 사거리 끝에서 크게 터짐. 미리보기는 `compose_cannon.py`
- 공통 시간: 기 모으기 0.22초 → 날아감 0.3초 → 맞음. 손 높이 50, 맞는 자리는 손에서 앞으로 170 (게임 그림 px)

다시 그리는 법:

1. pixelfx(https://github.com/patch-gg/pixelfx)를 따로 내려받고, 이 폴더의 `.js` 파일을 그 안의 `src/fx/qigong/`에 복사
2. pixelfx 폴더에서 `node tools/render.mjs "qigong/atk-*" --no-actor --sheet --bg none`
3. `python compose_atk.py <pixelfx 폴더> <게임 폴더> <출력 폴더> atk-a atk-b ...` → 새 기공사 그림과 합친 `_preview_qigong_<시안>.gif`

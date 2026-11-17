# 기공사 일반 공격 이펙트 시안 (pixelfx)

- `atk-a` 금빛 기탄 · `atk-b` 장풍 · `atk-c` 나선 기류 · `atk-d` 삼연 기탄 · `atk-e` 태극 기구슬 · `atk-f` 실타래 기구슬 (`atk-f-blue`는 같은 모양의 하늘색 판)
- 2판 (반짝임 없음, 2026-11-16 사용자 지시 "기공이라 반짝반짝 빛나는 이펙트는 안 어울림"): `qi-g` 기운 덩어리 · `qi-h` 기압 장풍 · `qi-i` 기류 띠 · `qi-j` 실타래 기구슬. 공용 `_qi.js` (별빛·번쩍·불꽃 가루 대신 안개·압력 고리·먼지)
- 1판 `atk-*`는 반짝임이 들어가 있어 참고용으로만 남김
- 기공포 시안 (일반 공격 J 바탕, `_jcore.js` 공용): `qi-cannon-a` 큰 실타래 포 · `qi-cannon-b` 나선 실 포 · `qi-cannon-c` 고리 꼬리 포. 모으기 0.6초(실이 감겨 들어옴) → 꿰뚫으며 날아감(적마다 작은 압력 고리) → 사거리 끝에서 크게 터짐. 미리보기는 `compose_cannon.py`
- 기공후 시안 (`qi-roar-a.js` 공용, 기공막 B·실타래 구슬 바탕): `qi-roar-a` 기압 물결 · `qi-roar-b` 고리 폭풍 · `qi-roar-c` 기운 숨결. 모으기 0.4초(실이 가슴으로 감겨 듦, 발밑 기운이 빨려 듦) → 터뜨리기(가슴 구슬이 터지며 바닥 납작 타원 0.55로 0.55초 동안 퍼짐). 미리보기는 `compose_roar.py`, 결과는 `docs/qi-roar/`
- 기공파 시안 (`qi-wave-a.js` 공용, 에네르기파 + 전격술사 전자포 결 무늬 + 실타래 구슬·실 고리): `qi-wave-a` 금빛 기포 (속이 가장 밝음) · `qi-wave-b` 결 기포 (속은 짙고 테두리가 밝음). 모으기 1.5초 → 쏘기 1.9초(미리보기) → 손 쪽부터 가늘어지며 끝. 미리보기는 `compose_wave.py`, 결과는 `docs/qi-wave/`
- 기공옥 시안 (`qi-genki-a`, 원기옥 느낌): 사방에서 휘어 드는 기운 줄기로 머리 위 거대한 구체(속 소용돌이·실타래·밝은 테두리)를 키움 → 겨눈 자리로 내리꽂힘 → 반구 기운 돔·바닥 물결 두 겹·기운 줄·위로 솟는 기둥. 미리보기는 시간을 줄이고 캐릭터를 반으로 줄임(게임 px × 0.8), 터지는 반지름은 게임보다 작게. `compose_genki.py`, 결과는 `docs/qi-genki/`
- 공통 시간: 기 모으기 0.22초 → 날아감 0.3초 → 맞음. 손 높이 50, 맞는 자리는 손에서 앞으로 170 (게임 그림 px)

다시 그리는 법:

1. pixelfx(https://github.com/patch-gg/pixelfx)를 따로 내려받고, 이 폴더의 `.js` 파일을 그 안의 `src/fx/qigong/`에 복사
2. pixelfx 폴더에서 `node tools/render.mjs "qigong/atk-*" --no-actor --sheet --bg none`
3. `python compose_atk.py <pixelfx 폴더> <게임 폴더> <출력 폴더> atk-a atk-b ...` → 새 기공사 그림과 합친 `_preview_qigong_<시안>.gif`

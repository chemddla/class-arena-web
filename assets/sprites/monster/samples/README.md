# 몬스터 스프라이트 샘플 (아직 게임에 미적용)

탑에 해당 몬스터가 생기면 `MONSTER_SPRITE_DEFS`에 연결해서 쓸 시트 모음.

| 파일 | 몬스터 | 구성 |
| --- | --- | --- |
| `goblin_bomber_src.webp` | 고블린 폭탄꾼 원본 | 1024×434, 10프레임 5×2 (대기, 걷기 1·2, 일반공격 1·2, 스킬(파이어볼) 1·2, 피격, 쓰러짐 1·2). 배경 단색(29,35,49)·바닥 그림자·한글 라벨 박혀 있음 |
| `goblin_bomber.webp` | 고블린 폭탄꾼 정리본 | 890×92, 10칸 (칸 89×92, 발 기준점 (43.5, 88)). 칸 순서 = 원본 순서 그대로. 그림자·라벨 지움, 일반공격 2의 날아가는 폭탄과 스킬 2의 파이어볼은 투사체로 따로 날리려고 지움 |
| `kraken_idle_src.webp` | 심해의 폭군 크라켄 원본 1 (2026-11-03) | 1024×572 RGB, 한 자세(정면, 촉수 8개 펼침, 붉은 눈). 흰 배경, 주변에 물방울 조각 흩어짐. 나머지 모션은 사용자가 이어서 올릴 예정 → 모이면 한 시트로 정리. 게임에는 이미 `kraken`(MONSTER_BODY_SIZE 2.5)·`elite_kraken`(9단계 보스)이 있음 |
| `kraken_walk_src.webp` | 크라켄 원본 2: 걷기 (2026-11-03) | 1024×506 RGB, 2프레임 가로 배치(걷기 1·2, 왼쪽을 보며 촉수로 걸음). 흰 배경, 물방울 조각 흩어짐 |
| `kraken_walk2_src.png` | 크라켄 원본 2-2: 걷기 추가 (2026-11-03) | 504×139 RGB, 2프레임 가로 배치. 아래 라벨은 IDLE·WALK 2지만 사용자는 "걷기 모션 더 추가"로 보냄 → 둘 다 걷기 사이클에 넣기(첫 칸은 대기로도 쓸 수 있음). 정면에 가까운 자세, 흰 배경, 라벨 지우기 |
| `kraken_attack_src.png` | 크라켄 원본 3: 일반공격 (2026-11-03) | 652×189 RGB, 2프레임 가로 배치(공격 1: 오른쪽으로 촉수 뻗기, 공격 2: 촉수로 내려쳐 물보라). **오른쪽을 봄**(걷기는 왼쪽). 흰 배경, 위에 영어/한글 라벨 박힘. 촉수 끝 일부가 바닥선(y≈180)에서 평평하게 잘려 있음 → 시트 정리 때 끝을 둥글게 다듬기 (사용자 요청) |
| `kraken_hurt_src.png` | 크라켄 원본 5: 피격 (2026-11-03) | 251×192 RGB, 1프레임(뒤로 젖혀지며 물방울 튐). 흰 배경, 위 라벨 지우기 |
| `kraken_skill1_src.webp` | 크라켄 원본 6: 스킬 4종 (2026-11-03) | 1024×572 RGB, 4스킬×2단계 = 8칸(2×2 묶음). 심해 소용돌이(기 모으기·물 소용돌이 방출) → `earthquake`, 촉수 휩쓸기(조준·흙먼지 휩쓸기) → `shield_rush`, 촉수 회오리(회전 준비·물 회오리 방출) → `whirlwind`, 심해 압착(포착·물기둥 압착) → `stun_strike`. 흰 배경, 한글 제목·단계 라벨 지우기, 압착 2단계 오른쪽 아래 ✦ 워터마크 지우기. 해일 포효 그림은 아직 없음 |
| `kraken_skill2_src.png` | 크라켄 원본 7: 촉수 휘감기 (2026-11-03) | 681×173 RGB, 3칸(1단계 웅크림, 중간 촉수 들어올림, 2단계 오른쪽으로 촉수 뻗어 휘감기) → `provoke`. 흰 배경, 위 한글 라벨 지우기 |
| `kraken_skill3_src.png` | 크라켄 원본 8: 먹물 폭탄 (2026-11-03) | 693×179 RGB, 3칸(1단계 웅크림, 먹물 구슬 모으기, 2단계 오른쪽으로 먹물 폭탄 발사) → `poison_boom`. 2단계의 날아가는 먹물탄은 투사체로 따로 날리려면 지울 것. 폭발 이펙트는 `fx/samples/kraken_ink_bomb_fx_src.png`. 흰 배경, 라벨 지우기 |
| `kraken_death_src.png` | 크라켄 원본 4: 쓰러짐 (2026-11-03) | 480×168 RGB, 2프레임 가로 배치(쓰러짐 1: 주저앉음, 쓰러짐 2: 납작하게 엎드림). 오른쪽을 봄. 흰 배경, 위·아래에 라벨 박힘 → 지우기 |
| `lich_robe_src.webp` | 망자의 군주 리치 원본 1 (2026-11-03) | 1024×572 RGB, 8프레임 4×2 (대기, 걷기 1·2, 일반공격 1·2, 피격, 쓰러짐 1·2). 보랏빛 로브·가시 왕관·해골 지팡이, 왼손에 푸른 불꽃. 일반공격 2의 푸른 불덩이는 투사체로 따로 날리려면 지울 것. 흰 배경, 한글·영어 라벨 지우기. **게임의 `lich.webp`(판금 갑옷·대검, 언데드 종족 보스)와 다른 그림** → 엘리트 7단계 `elite_lich`에만 씀: `python tools/lich_elite_build.py` → `monster/lich_elite.webp`(17칸, MONSTER_SPRITE_DEFS.elite_lich). 스킬은 아래 원본 2 |
| `lich_robe_skill_src.webp` | 망자의 군주 리치 원본 2: 스킬 3종 (2026-11-03) | 1024×765 RGB, 3×3 (영혼 서리 → `ice_arrow`, 역병 폭탄 → `poison_boom`, 죽음의 저주 → `hex_bolt` × 기 모으기·기운 두름·방출). 흰 배경, 한글 라벨 지움. 방출 칸의 얼음 가시·역병 구름·해골 망령은 칸 안에 그대로 둠. `lich_elite.webp` 9~17번째 칸 |
| `lich_robe_skill2_src.webp` | 망자의 군주 리치 원본 3: 스킬 3종 (2026-11-03) | 1024×765 RGB. 망령 이동 4칸(그대로·망령화·잔상 이동·재출현, 뒤 두 칸은 그림이 겹쳐 무게중심으로 나눔) → `teleport`, 불사의 의식 4칸(주문·금빛 마법진·불꽃 든 손·불길) → `purify`, 망자의 늪 3칸(집중·발밑 늪·늪 펼쳐 소환) → `curse_field`. 흰 배경, 라벨 지움. `lich_elite.webp` 18~28번째 칸 |
| `ifrit_elite_src.webp` | 겁화의 이프리트 원본 1 (2026-11-03) | 1024×572 RGB. 대기 · 걷기 1·2 / 일반공격 1·2 · 피격 / 쓰러짐 1·2. 대기 아래 다리만 있는 조각은 안 씀. 일반공격 2의 불덩이는 잘라 내서 기본 공격 투사체로 씀. 대기 칸만 크게 그려져 있음(0.8배). **게임의 `ifrit.webp`(화염 대검, 화염족 보스)와 다른 그림** → 엘리트 8단계 `elite_ifrit`에만 씀: `python tools/ifrit_elite_build.py` → `monster/ifrit_elite.webp`(22칸, MONSTER_SPRITE_DEFS.elite_ifrit) |
| `ifrit_elite_skill_src.webp` | 겁화의 이프리트 원본 2: 스킬 3종 (2026-11-03) | 1024×765 RGB, 0.84배로 줄여 씀. 겁화구 2칸(모으기·발사, 날아가는 겁화구는 투사체로 따로) → `fireball`, 화염 폭발 3칸(모으기·불길·불꽃 돔) → `roar`, 불비 3칸(의식·내려다봄·운석 강우, 날아오는 운석은 지우고 한 개를 장판 운석으로 씀) → `arrow_rain`. 라벨 지움 |
| `ifrit_elite_skill2_src.webp` | 겁화의 이프리트 원본 3: 스킬 3종 (2026-11-03) | 1024×572 RGB, 작게 그려져 있어 1.2배로 키워 씀. 용암 분출 2칸 → `earthquake`, 불꽃 순간이동 2칸(사라짐·출현, 오른쪽 라벨은 '불꽃 분출'로 잘못 적혀 있음) → `teleport`, 불꽃 분노 2칸(포효·양옆 불길) → `warcry`. 라벨 지움 |
| `crab_warrior_src.webp` | 심해족 집게 전사 원본 (2026-11-06) | 765×1024 RGB, 3·3·2칸 (대기, 걷기 1·2 / 일반공격 1·2, 피격 / 쓰러짐 1·2). 남색 배경, 한글 라벨, 쓰러짐 2 소라 방패에 ✦ 워터마크 → `python tools/deepsea_build.py` → `monster/crab_warrior.webp` |
| `merfolk_archer_src.webp` | 심해족 인어 작살수 원본 (2026-11-06) | 765×1024 RGB, 같은 배치. 걷기 2·피격 칸은 작살이 빠져 있어 대기 칸 작살을 쥐여 줌. 쓰러짐 2 얼굴 위 ✦ 워터마크. 작살은 투사체 `fx/deepsea_fx.webp` harpoon |
| `octopus_archer_src.webp` | 심해족 먹물 저격 문어 원본 (2026-11-06) | 1024×765 RGB, 같은 배치. 일반공격 2의 물방울은 투사체 squirt로 떼어 냄. 쓰러짐 2 소라 위 ✦ 워터마크 |
| `octopus_mage_src.webp` | 심해족 먹물폭탄 문어 원본 (2026-11-06) | 765×1024 RGB, 3·2·3칸 (대기, 걷기 1·2 / 일반공격 1·2 / 피격, 쓰러짐 1·2). 대기 칸 먹물 방울은 지움, 일반공격 2의 날아가는 폭탄은 투사체 bomb. 쓰러짐 2 촉수 위 ✦ 워터마크 |
| `merfolk_mage_src.webp` | 심해족 인어 주술사 원본 (2026-11-06) | 874×1024, 산호·해초 그려진 바닷속 장면 배경·바닥 그림자. 대기, 걷기 3, 공격 2(물살은 투사체), 3줄의 '일반공격 1' 칸은 안 씀, 피격, 쓰러짐 1칸 → `python tools/deepsea2_build.py` |
| `merfolk_healer_src.webp` | 심해족 인어 사제 원본 (2026-11-06) | 825×1024. 걷기·공격 칸이 서로 겹쳐 그려짐, 피격 칸 큰 폭발 그림·구슬 둘레 누런 빛은 지움, 빛줄기는 투사체 |
| `octopus_rogue_src.webp` | 심해족 먹물 암살 문어 원본 (2026-11-06) | 765×1024, 위에 제목. 몸 무늬가 배경색과 가까워 갇힌 배경 찾기를 끔 |
| `crab_knight_src.webp` | 심해족 집게 방패기사 원본 (2026-11-06) | 765×1024, 줄 제목·칸 이름 글자가 그림에 붙어 있음 (지울 네모로 칠함) |
| `merfolk_lancer_src.webp` | 심해족 인어 창기병 원본 (2026-11-06) | 687×1024, 해마를 탄 인어. 걷기 3칸('3. 걷기 2'가 두 번), 라벨이 칸 위에 붙음 |
| `merfolk_sniper_src.webp` | 심해족 인어 작살 저격수 원본 (2026-11-06) | 765×1024, 회색 바탕, 라벨은 왼쪽 |
| `merfolk_frost_src.webp` | 심해족 심해 빙결 인어 원본 (2026-11-06) | 1024×765, 칸 테두리선. 피격 칸의 주황·파랑 불꽃은 잘못 그려진 것이라 지움, 얼음 창 다발은 투사체 |
| `octopus_curse_src.webp` | 심해족 저주 먹물 문어 원본 (2026-11-06) | 1024×687, 칸마다 체크무늬 패널. 보라 탄은 투사체 |
| `merfolk_bard_src.webp` | 심해족 세이렌 가수 원본 (2026-11-06) | 687×1024, 작은 그림. 음파는 투사체 |
| `kraken_tower_src.webp` · `kraken_tower_skill_src.webp` | 탑 심해족 보스 크라켄 원본 (2026-11-06) | 814×1024 동작 8칸 + 1024×765 스킬 5칸(회전공격·지진·강타·포이즌 붐·사자후), 격자 바탕. `monster/kraken_tower.webp` = `MONSTER_SPRITE_DEFS.kraken_lancer` (엘리트 9단계 `kraken.webp`와 다른 그림) |

`goblin_bomber.webp` 연결 예시 (전투에서 확인한 값):

```js
{
  src: 'assets/sprites/monster/goblin_bomber.webp',
  cellW: 89, cellH: 92, anchorX: 43.5, anchorY: 88, standH: 52, topH: 74, count: 10,
  anims: { idle: [0], walk: [1, 0, 2, 0], attack: [3, 4, 4], skill: [5, 6, 6], hurt: [7], death: [8, 9] },
  skillAnims: { fireball: { anim: 'skill', tpf: 7, dur: 28 } },
  castFrames: { fireball: 5 },
  projFx: { magic_orb: 'bomb', fireball_proj: 'goblin_fireball' } // 폭탄·불꽃 파이어볼 = GOBLIN_BOMB_FX
}
```
(파일을 `assets/sprites/monster/`로 옮기고 src를 맞출 것)

## 몬스터 크기 (새 시트를 넣을 때)

`standH`는 **몸 크기 1일 때 용병과 같은 키**가 되게 잡는다. 몬스터마다 다른 덩치(작은 임프 0.75, 오우거 1.5, 종족 보스 2.2~2.6 등)는
`index.html`의 `MONSTER_BODY_SIZE` 표가 정하고, 그림·토큰·맞는 범위·근접 사거리·스킬 범위가 모두 그 배율을 따른다.
보스라고 standH를 작게 해서 키우지 말 것. 표에 없는 몬스터를 새로 넣으면 크기를 적어 둔다 (없으면 보스 2.2, 나머지 1).

**크라켄 게임 적용**: `python tools/kraken_build.py` → `monster/kraken.webp`(27칸, MONSTER_SPRITE_DEFS.kraken · 심해족 보스와 엘리트 9단계 공용) + `fx/kraken_fx.webp`(KRAKEN_FX: 먹물 4칸·해일 4칸). 샘플마다 크기가 달라 머리 길이(정수리~눈)로 배율을 맞춤. 대기 = 첫 샘플(정면), 걷기 = 걷기 샘플 2칸 + 추가 2칸을 펴기·웅크리기로 번갈아. 해일 포효 샘플의 큰 파도 칸은 안 씀(파도는 이펙트로 범위에 깔림).

## 용족 (2026-11-06)

`python tools/dragon_build.py` → `monster/<이름>.webp` 14장 + 투사체 `fx/dragon_fx.webp` (DRAGON_FX). 배경 지우기는 `deepsea2_build.cut2`를 그대로 쓰되,
칸 테두리 색 중 바탕(중앙값)에 가까운 것만 배경 색으로 삼고 '갇힌 배경' 지우기는 끔 (어두운 로브·갑옷·망토가 지워지지 않게).

| 파일 | 몬스터 | 메모 |
| --- | --- | --- |
| `dragonkin_warrior_src.webp` · `dragonkin_warrior_walk_src.webp` | 용인족 전사 | 처음 샘플의 걷기 ②는 검이 빠져 있어 다시 받은 칸으로 바꿈 |
| `drake_warrior_src.webp` · `drake_warrior_walk_src.webp` | 성난 드레이크 | 걷기 2칸(흙먼지)은 다시 받은 칸, 원래 샘플보다 작아 키워 씀 |
| `wyvern_archer_src.webp` | 독꼬리 와이번 | 보라 불덩이 = 투사체 |
| `dragonkin_archer_src.webp` | 용인족 궁수 | 피격 칸은 활을 놓친 그림 |
| `drake_mage_src.webp` | 화염 드레이크 | 넓은 칸의 불줄기 뿜기를 공격 2로, '공격 ②'(대기와 같음)·이름 없는 웅크린 칸은 안 씀 |
| `dragonkin_mage_src.webp` | 용인족 주술사 | 보라 구슬 = 투사체 |
| `dragonkin_healer_src.webp` | 용인족 사제 | 금빛 섬광 = 투사체 |
| `wyvern_rogue_src.webp` | 급습 와이번 | 흰 바탕으로 다시 받은 샘플 (회색 바탕 처음 샘플은 git 기록에). 피격·쓰러짐 1이 반대쪽을 보며 뒤집혀 있어 좌우반전, 날개·꼬리 사이 갇힌 흰 바탕은 지움 |
| `dragonkin_knight_src.webp` | 용비늘 기사 | |
| `dragonkin_lancer_src.webp` | 용인족 창기사 | '피긱'(대기와 같음)·이름 없는 기울어진 칸은 안 씀, 칸 위 라벨 띠는 지움 |
| `drake_sniper_src.webp` · `drake_sniper_walk_src.webp` | 화염포 드레이크 | 걷기 2칸은 다시 받은 칸(대기 크기에 맞춰 0.93배 더 줄임), 대포 불길 = 투사체 |
| `dragonkin_frost_src.webp` | 서리 용인족 | 흰 바탕으로 다시 받은 샘플 (처음 어두운 눈밭 패널 샘플은 git 기록에). '쓰러짐 1'이 대기와 같은 그림이라 피격 → 쓰러짐 2 |
| `wyvern_curse_src.webp` | 저주 와이번 | '일반공격 1' 두 칸(웅크림·구슬 모으기) 다 씀, 보라 불길 = 투사체. 날개·꼬리 사이 갇힌 바탕도 지움 |
| `dragonkin_bard_src.webp` | 용인족 전고수 | |
| `dark_dragon_src.webp` · `dark_dragon_skill_src.webp` | 심연마룡 (탑 보스) | 흰 바탕으로 다시 받은 샘플 두 장 (처음 어두운 바탕 샘플은 git 기록에). 걷기 두 칸은 소품이 칸마다 바뀌어 안 씀. 스킬 5종(돌진·파이어볼·사자후·화살비·썬더볼트) × 2칸은 1.5배로 키워 붙임 |

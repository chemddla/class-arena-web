# 과제: 수업 중 실제 트래픽을 재서 줄이기 (Firebase 실시간 DB)

전제: 실시간 컨텐츠(결투·관전·보스 레이드·던전·펫 러닝·미니게임)는 지금처럼 매끄럽게 유지한다.
화면 보내는 간격(`LIVE_FRAME_INTERVAL_MS` 150ms, 펫 러닝 8Hz)을 늘리는 것은 마지막 수단이다.

## 1. 재기 (학생들이 접속해 있는 수업 시간에)

1. 이 저장소를 최신으로 받고 로컬 미리보기를 띄운다 (`.claude/launch.json`의 `class-arena-local`, 포트 5173).
2. `http://localhost:5173/?dev=student&mute=1` 을 열고 콘솔에서:

```js
(0, eval)(await (await fetch('/tools/traffic-measure.js')).text());
const L = await TM.login('ARENA3');   // 접속할 때 받는 양
const R = await TM.live('ARENA3', 300); // 5분 동안의 변경량 (탭을 앞에 둔 채로)
```

- 읽기 전용: 앱은 빈 샘플 학급(ARENA1)에 머물고, 스크립트는 ARENA3 경로에 측정용 구독만 건다. 정리·보상 같은 쓰기는 일어나지 않는다.
- `R.rows`: 경로별 B/s. `students/칸이름`은 학생 기록에서 바뀐 칸, `pvp_live/방/frame`은 그 방 화면(참가자·관전자 한 명이 받는 양).
- `R.alwaysBpsPerDevice × 접속 수` = 반 전체가 받는 양 (늘 구독하는 경로는 접속한 학생 모두가 받음).
- 레이드·관전·펫 러닝이 실제로 돌고 있을 때 재야 의미가 있다. 가능하면 2~3번 (쉬는 시간·컨텐츠 중) 잰다.
- 전투 화면 칸별 크기는 로컬 전투로도 잴 수 있다: `tests/battle-sim.js`를 불러 5:5를 돌리며 가상 시계로 `publishLiveBattleFrame`을 부르고 칸별 JSON 길이를 더한다 (f4e1e09 커밋 메시지의 측정 방식).

## 2. 2026-11-05 저녁에 잰 기준값 (ARENA3, 23명, 접속 1명)

| 항목 | 크기 |
|---|---|
| 학생 기기 한 대 접속 | 약 211KB |
| students | 202KB (roster 82KB · defenseFormation 50KB · mercStorage 12KB · home 8KB · petBox 8KB) |
| world_boss | 3.5KB |
| invites / profiles / auctions | 2.0 / 1.6 / 1.5KB |

- defenseFormation(50KB)·students 안의 mercStorage·avatarBox(15KB)는 6a8e443 이후 지워질 예전 칸이다. 배포(11-05 16:08) 뒤 아무도 로그인하지 않아 남아 있었음. → **먼저 `L.legacyLeft`가 비었는지 확인.** 남아 있으면 `cleanDerivedLegacy`·studentPrivate 옮기기가 왜 안 돌았는지 본다. 지워지면 접속 크기 약 145KB 예상.
- 실시간 변경량은 접속자가 없어 못 쟀다 (이 과제의 핵심).

## 3. 이미 한 것 (다시 하지 않기)

- 6a8e443: 진형 사본 저장 안 함, mercStorage·avatarBox를 studentPrivate로
- 7c796d7: 로비방 슬림·바뀐 칸만 쓰기, 게스트 입력은 바뀐 칸만
- 5d68526 / f56cb99: 전투 화면 바뀐 칸만(d) · 투사체·이펙트 반올림 · 숨은 탭 관전자 일시정지
- f4e1e09: 보스 레이드 hb·피해 2초마다 묶음, 체력은 `current/hp`만 transaction, 끝난 보스 기록 정리, 선물함은 내 칸만 구독, 선물 정산은 바뀐 칸만, 전투 화면 바라보는 각도(칸 7) 데드밴드
- 2026-11-08 (점검 패치): 펫 러닝 관전 화면의 물체·글자 목록은 바뀌었을 때·0.5초마다만 통째로 보내고 그 사이는 null (`PETRUN_LIVE.objsFullMs`·`deltaFrom` 2026-11-09 00:00 KST부터, 받는 쪽은 앞 화면 목록을 advance로 이어 씀) · 받는 쪽 CPU: 학급 students 소식은 자식(학생별) 이벤트로 바뀐 학생만 다시 정리(`classDirtyStudents`), 전투·관전 중엔 탭 다시 그리기를 미룸(`classTabRefreshDeferred`), 이 기기 localStorage 저장·백업은 묶어서(`scheduleLocalStateSave`, doPush 안 백업)

## 4. 고칠 후보 (재 본 숫자로 우선순위를 정함)

1. **펫 러닝 관전** (`PetRunLive.encode`): 8Hz로 화면 전체(젤리·장애물 목록)를 JSON 문자열로 매번 보냄, 장당 350~800B → 보는 사람당 최대 6KB/s. 일정하게 흘러가기만 하는 젤리·아이템은 생길 때·전체 화면에만 보내고 받는 쪽이 `advance`로 흘려 보내게. 형식이 바뀌므로 옛 탭 대비 기준 시각(다음 날 아침)을 둔다 (9d03e5f·5d68526 방식).
2. **전투 화면 잔여분** (`publishLiveBattleFrame`): 장판 `zn`은 남은 시간이 매 화면 바뀌어 통째로 감(받는 쪽이 줄여 예측 가능) · 마나(칸 4) 매 화면 · 머리 `at`/`b`/`ep` 약 44B. 합쳐서 5~10%. 이것도 형식 변경 → 기준 시각 필요.
3. **늘 구독하는 경로 중 `R.rows` 상위**: 특히 `students/<칸>`이 자주 바뀌면 그 칸을 바꾸는 저장이 너무 잦은 것 (예: 시각·카운터 칸). 학생 기록 한 칸 변경은 접속한 모두에게 간다.
4. **쌓이는 노드**: auctions·tradeOffers·invites·skins에 지난 항목이 계속 남는지 (`L.nodes`를 며칠 간격으로 비교).
5. **pvp_live 잔여**: 11-02의 `raidcast_rush_…` 한 방(44KB, frame·init·handoff)이 지워지지 않고 남음. 지금은 아무도 구독하지 않아 트래픽은 없지만 러쉬 계산 넘기기 뒤 정리 경로를 확인 (`publishLiveBattleResult`의 20초 뒤 remove, handoff 경로).

## 5. 고칠 때 지킬 것

- 매끄러움 확인: `tests/mock-rtdb.js` + `tests/spectate-harness.js`로 관전 탭의 화면 도착 간격·끊김(`__spec.report()`)을 바꾸기 전과 비교.
- 형식을 바꾸면 옛 탭(배포 전에 연 탭)이 읽을 수 있는지, 아니면 기준 시각을 둘지 정한다.
- `node tests/*.test.cjs ../index.html` 통과, 바꾼 뒤 `TM.live`로 다시 재서 커밋 메시지에 전/후 숫자를 남긴다.
- 같은 폴더에서 다른 세션이 index.html을 고치므로 커밋 전 `git diff`에 내 변경만 있는지 확인.

## 6. 예전 탭 정리 (minBuild)

형식을 바꾸는 배포 뒤, 그 전에 연 탭을 새로고침시키려면:

1. `https://class-arena.pages.dev/version.json`의 `buildAt`(ms)을 확인한다.
2. `MSYS_NO_PATHCONV=1 firebase database:set /classes/ARENA3/meta/minBuild <buildAt> --project class-arena-b4ee3` (학급마다).
3. 그보다 오래된 탭(빌드 시각이 들어간 2026-11-06 이후 버전)은 안내 띠를 띄우고, 전투 중이 아닐 때 탭으로 돌아오면 새로고침한다. 그 전 버전 탭에는 이 장치가 없다.

2026-11-06 측정: 예전 주소(web.app)가 11-05 오전 버전으로 남아 있던 탓에(안내 페이지 배포 실패, 2d89243에서 고침) `raid_rooms`가 기기당 12.5KB/s(반 전체 약 210KB/s)였다.

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

- 2026-11-08 (4차): 유닛 목록(init·다시 보내기)에서 받는 쪽이 쓰지 않는 임시 칸(AI 대상·이전 좌표·애니 틱·상태·쿨타임·속도 등 `LIVE_INIT_DROP`)을 빼고 좌표를 반올림 → 유닛당 약 1.9KB → 0.8KB. 로컬 5:5 시뮬(가상 시계, 소환사·도적 포함 4판 평균): 화면 약 5.1KB/s, 유닛 목록 다시 보내기(정령·분신)가 판당 2~4번 · 한 번에 10~24유닛이라 1.4~1.6KB/s(전체의 약 1/4)였음 → 임시 칸 제거 뒤 같은 횟수 기준 약 45% 감소. 남은 후보: 추가된 유닛만 보내기(`initAdd`, 형식 변경·늦게 들어온 관전자용 전체 목록 유지 필요)
- 2026-11-08 (5차, 화면 형식 v2 · `LIVE_FRAME_V2_FROM` 2026-11-09 00:00 KST부터): 이펙트 종류 이름 → `LIVE_FX_TYPES` 표 번호(끝에만 추가할 것), 투사체는 전체 화면·처음 볼 때만 통째로(+번호), 그 뒤엔 [x, y, 각도, 번호, vx, vy]만. 받는 쪽은 두 형식 다 읽음. 로컬 5:5 루프백: 투사체 항목의 84%가 짧은 꼴, 이펙트 97%가 번호 · 화면 전송량 약 8~13% 감소. 그 전에 연 탭이 월요일 0시를 넘겨 관전하면 그 탭에서만 이펙트·투사체 일부가 안 보임 (minBuild로 새로고침 유도 가능)
- 2026-11-08 (6차, 측정만): 바뀐 유닛 칸(d, 전체의 36%) 안에서 자리(x·y 칸 0·1)가 d 바이트의 41%(전체의 약 15%)로 가장 큼 · 그 다음 체력(2)·마나(4)·각도(7)·시전(18)·상태(16)·쿨타임(17)이 각 3% 안팎. 머리 칸(at·b·ep·t·bt)은 합쳐 8%. 자리를 더 줄이려면 [x,y] 한 칸으로 묶기(약 5%)나 속도 예측이 필요한데 둘 다 형식 변경이라 보류. 미니게임 10종은 AI 상대 자동 플레이로 예외 없음 확인
- 2026-11-08 (8차, 직접 연결 뒤): 1:1 결투에서 직접 연결(WebRTC)로 도전자에게 잘 보내는 중(`LiveRtc.lastSentAt` 0.3초 안·밀린 양 4KB 아래)이고 보는 친구(`pvp_rooms/방/spectators`, 결투 관전자가 원래 적는 칸 · 9차에서 8차의 중복 watchers 등록을 걷어냄)가 없으면 서버 화면은 0.5초마다만(`liveServerFrameInterval`, `LIVE_RTC_SERVER_THROTTLE_FROM` 2026-11-09 00:00 KST부터) → 도전자 기기가 안 쓰고 내려받던 서버 화면이 약 1/3. 링크가 막히면 바로 0.15초로 돌아오고, 관전자가 들어오면 전체 화면 한 장부터 다시 0.15초. 방장 탭이 뒤로 가 있을 때도 직접 연결 화면을 계속 보냄(예전엔 서버 화면만 → 도전자가 0.6초 뒤 서버 화면으로 떨어졌음). 직접 연결 보내기 직전의 JSON 복사(0.05초마다 두 번 직렬화) 제거
- 2026-11-08 (10차): `live_battle_events`(학급 전체가 limitToLast(10) child_added로 구독하던 대시 이벤트) 구독·쓰기 제거. 화면 동기화 전 방식이라 받는 쪽은 `sim.netRole`이 있으면 늘 무시했고, 보내는 쪽은 netRole이 없는 전투(혼자 하는 엘리트 토벌·연습 친구 결투·AI뿐인 팀전)의 수동 대시마다 학급 전체 탭에 이벤트(약 150B)와 20초 뒤 삭제를 내려보냈음. 서버 규칙의 `live_battle_events` 항목은 예전 탭이 올리는 것을 위해 남겨 둠
- 2026-11-08 (11차): 몬스터 러쉬 화면의 라운드 상태 `rs`(숫자 11칸, 약 40B)를 매 화면 → 전체 화면·바뀌었을 때만(`rushStateForFrame`, 틱 카운터 칸의 자연 감소는 바뀜으로 안 봄). 받는 쪽은 예전부터 rs가 없는 화면을 그냥 넘기고 절대 틱(nextAt·roundStartTick)으로 남은 시간을 세므로 형식 변경 없음. 장판 `zn`은 받는 쪽이 life를 스스로 줄이지 않아 그대로 둠
- 2026-11-08 (12차): 서버 화면 0.5초 간격(`liveServerFrameInterval`)을 팀전·협동 레이드·던전에도: 사람 팀원 모두가 원활한 직접 연결(`LiveRtcHub.peers`, mode 'rtc'·0.3초 안 전송·밀림 4KB 아래)로 받고 있고 보는 친구가 없을 때(팀전방은 spectators · 레이드/던전은 계산 담당이 새로 구독하는 중계 자리 watchers). 한 명이라도 서버 화면을 보면 그대로 0.15초. 5:5 팀전에서 팀원 4명이 안 쓰고 내려받던 서버 화면(각 약 5KB/s)이 약 1/3로
- 2026-11-08 (13차, ARENA3 노드 크기 읽기 전용 측정): students 150KB(23명, 탭마다 접속 때 통째로 한 번) · studentPrivate 122KB(학생은 자기 칸만 구독) · profiles 1.6KB · auctions 2.2KB · invites 2.4KB(TTL 정리 있음) · minigames 5KB(끝난 판 17개 — `{방}_pc`·`{방}_vl` 실시간 노드가 방 삭제 때 안 지워짐) · pvp_live 92KB(끝난 러쉬 중계 2개 `raidcast_rush_…`, 아무도 구독하지 않아 트래픽은 없음) · 나머지 0~0.5KB. 고침: 레이드·러쉬·던전 방 삭제 때 그 방의 중계 자리도 지우고(`removeRaidRoomData`), 계산을 이어받은 친구가 예전 담당 자리를 20초 뒤 지움, 미니게임 방 삭제 때 `_pc`·`_vl`도 지움. 남아 있는 옛 노드는 `firebase database:remove /classes/ARENA3/pvp_live/<id>`로 한 번 치우면 됨. 남은 큰 항목은 접속 때 students 통째 내려받기(150KB)인데, 바뀐 학생만 받으려면 updatedAt 색인·삭제 감지가 필요해 보류
- 2026-11-08 (14차, ARENA3 학생 기록 150KB 분해): roster 90KB(용병 163명, 한 명 약 550B: skillSlots 12KB · statVariance 10KB · statPoints 7KB · id 5KB · traitName 5KB · targetRule/behaviorRule 7KB …) · capParts 9.6KB(4명, 픽셀 아트) · petBox 9KB · home 8.5KB · avatar 5.7KB(17명). 픽셀 아트·집·펫은 실제 데이터라 못 줄임. 고침: 올릴 때 `traitName`(traitId로 정해짐)과 0뿐인 `statPoints`를 빼고(`slimMercForUpload`, `MERC_SLIM_FROM` 2026-11-09 00:00 KST부터) 받는 쪽 `normalizeMercForSync`가 되살림 → 접속 때 내려받기 약 11KB(7%)·용병 한 명 갱신 약 60B 감소. skillsRevealed(0을 빼면 받는 쪽이 다른 값으로 채움)·skinVariant(직접 읽는 곳 있음)·statVariance(형식 변경)는 그대로
- 2026-11-08 (15차): 학생 기록은 학생마다 따로 구독(`attachClassStudentSubs`, students/<id>). Firebase는 재접속 때 구독마다 받아 둔 값의 해시를 보내 안 바뀐 구독은 다시 내려주지 않으므로, 학급 전체 한 구독이던 때는 끊겼던 사이 한 명만 저장돼도 약 140KB가 전부 다시 왔고 이제는 바뀐 학생 것만 옴 (처음 접속·평소 소식량은 같음). id 목록은 접속 때 REST shallow(약 1KB)로 키만 받고 이름표(profiles)에 새로 생기는 id를 더함 · 키를 못 받으면 예전처럼 전체 한 구독. 모든 학생의 첫 값이 올 때까지 적용을 미뤄 일부만 받은 채 학생 목록을 덮어쓰지 않음
- 2026-11-09 (펫 배구): 두 기기 직접 연결 `VolleyLink`(WebRTC, 신호는 `minigames/{방}_vl/rtc`) — 열려 있으면 펫 위치 20Hz·공 타격을 직접 보내고 서버로는 0.25초마다만(`VOLLEY.linkFbMs`) → 배구 중 서버 쓰기 약 1/5. 표시 지연의 왕복 추정은 최솟값 대신 상위 80%(`rttHi`). 안 열리면 예전처럼 서버로만
- 2026-11-09 (로딩): 배포 페이지 2.49MB(압축 0.7MB, 캐시 없음·ETag 없음 → 접속마다 내려받음) · assets 149MB/1310개는 1시간 캐시였음. 모든 그림·소리 주소가 내용 해시(?v=)라 `/assets/*`를 1년 immutable로 (Cloudflare 전송량·접속 속도, Firebase와 무관). 낱말 사전 1.9MB는 끝말잇기를 열 때만 받음

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

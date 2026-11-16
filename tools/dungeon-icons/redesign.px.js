// 던전 아이콘 다시 그리기 (후보). 같은 팔레트·16칸·1px k 테두리, 빛은 왼쪽 위
// 만들기: node ~/.claude/skills/pxl-pixel-art/bin/pxl.js build tools/dungeon-icons/redesign.px.js
pal({
  k: '#1b1424', K: '#3a3346', G: '#6e6880', L: '#b9b4c8', W: '#ffffff',
  r: '#a8321c', R: '#e0602a', o: '#ffb347', c: '#fff2c4',
  y: '#b8701c', Y: '#f0a92a', h: '#ffd84a', H: '#fff4b0',
  b: '#1e3a6e', B: '#2f74b8', i: '#5cc0f0', I: '#bdeaff',
  p: '#3b1a6e', P: '#6d3fc0', v: '#a875f0', V: '#dcc4ff',
  e: '#0f5132', E: '#1f8f5a', n: '#4ade80', N: '#bbf7d0',
  m: '#7a1730', M: '#d03a5a', q: '#ff7a9a', Q: '#ffd0dc',
  d: '#5a3a20', D: '#8a5a30', t: '#c08a50', T: '#e8c090'
})

// 시작 방: 벽 횃불
sprite('dgTorch', { mx: true, outline: 'k' }, `
  ......o
  .....oR
  ....oRo
  ....Roc
  ....Rcc
  .....ch
  ....DDD
  ....GLL
  .....DD
  .....dD
  .....dD
  .....dD
  ....GLL
  .....GG`)

// 일반 방: 엇갈린 두 칼 (칼끝 위, 손잡이 아래)
sprite('dgFight', { mx: true, outline: 'k' }, `
  WL.....
  LWL....
  .LWL...
  ..LWL..
  ...LWL.
  ....LWL
  .....LW
  ....LWL
  ...LWL.
  .hYLL..
  ..Yh...
  .d.Yh..
  dD.....
  Dd.....`)

// 정예 방: 뿔 달린 붉은 해골
sprite('dgElite', { mx: true, outline: 'k' }, `
  T......
  tT.....
  .tT....
  .tTLLLL
  ..LWWWW
  .LWLLLL
  .LLLLLL
  .LkkkLL
  .LkMkkL
  .LLkkLL
  ..GLLLk
  ...LGLG
  ...GkGk`)

// 파수꾼 방: 쇠 방패 + 붉은 눈
sprite('dgGuard', { mx: true, outline: 'k' }, `
  GGGGGGG
  GLLLLLL
  GLWLLLL
  GLLGGGG
  GLGkkkk
  GLGkMqq
  GLGkkkk
  GLLGGGG
  GLLLLLL
  .GLLLLL
  .GLLLLL
  ..GLLLL
  ...GGLL
  ....GGG`)

// 보물 방: 쇠띠 두른 나무 상자 + 금 자물쇠
sprite('dgChest', { mx: true, outline: 'k' }, `
  ..ttttt
  .tTTTTT
  tTTTTTT
  tttttTT
  GLtttkk
  kkkkkkh
  DDGDDYh
  DtLtDYY
  DtLtDDk
  DDGDDDD
  dDGDDDD
  ddGdddd`)

// 기믹 방: 쇠 화로에 타는 불
sprite('dgBrazier', { mx: true, outline: 'k' }, `
  ......R
  .....Ro
  ....RRo
  ..R.Roc
  ..RRocc
  ..Roccc
  GLLLLLL
  .GGGGGG
  ..GLLLL
  ...GGLL
  ....GLL
  ...GLLL
  ..GG..G`)

// 빈 방: 발자국 두 쌍
sprite('dgSteps', { outline: 'k' }, `
  ........TTT...
  .......TTTTT..
  .......TTTTt..
  .......TtTtt..
  ........ttt...
  ..TTT.........
  .TTTTT..TTt...
  .TTTTt..Ttt...
  .TTTtt...t....
  ..ttt.........
  ..............
  ...TTt........
  ...Ttt........
  ....t.........`)

// 보스 방: 왕관 쓴 해골
sprite('dgBoss', { mx: true, outline: 'k' }, `
  .h...h.
  .Hh.hYh
  .hYhYMY
  .YYYYYY
  .yyyyyy
  ..LWWWW
  .LWLLLL
  .LkkkLL
  .LkMkkL
  .LLkkLL
  ..GLLLk
  ...LGLG
  ...GkGk`)

// 계단 방: 돌 아치 문 안으로 내려가는 계단
sprite('dgStairs', { mx: true, outline: 'k' }, `
  ....GGG
  ..GGLLL
  .GLLKkk
  .GLKkkk
  GLKkkGG
  GLKkkKK
  GLKkGLL
  GLKkKGG
  GLKGLLL
  GLKKGGG
  GLGLLLL
  GLKGGGG
  GLLLLLL
  GGGGGGG`)

// 신비한 방(회복의 샘): 돌 그릇에 솟는 물
sprite('dgFount', { mx: true, outline: 'k' }, `
  ......I
  .....iI
  ...i.iI
  ..i...i
  ..i..LL
  GLLLLLL
  GBBBiiI
  .GBBBBB
  ..GGGGG
  ....LLL
  ....GLL
  ...GLLL
  ..GGGGG`)

// 힘의 제단: 돌 받침 위 떠 있는 보랏빛 구슬
sprite('dgAltar', { mx: true, outline: 'k' }, `
  .....PP
  ....PvV
  ....PVW
  ....Pvv
  .....PP
  ..v....
  .GLLLLL
  .GGGGGG
  ...GLLL
  ...GLPv
  ...GLLL
  .GGLLLL
  GGGGGGG`)

// 지혜의 서재: 펼친 책 위 반짝임
sprite('dgBook', { outline: 'k' }, `
  ......h.......
  .....hHh......
  ......h.......
  ..............
  .WWWW....WWWW.
  bWLLWW..WWLLWb
  bWWWWWWWWWWWWb
  bWLLLWWWWLLLWb
  bWWWWWWWWWWWWb
  bWLLLWWWWLLLWb
  bWWWWWLLWWWWWb
  bBBBBBBBBBBBBb
  .bbbbbbBBbbbb.`)

// 함정: 바닥에서 솟은 가시
sprite('dgSpike', { mx: true, outline: 'k' }, `
  ......W
  .W....L
  .L...LL
  .L...LG
  LL...LG
  LG..LLG
  LG..LGG
  LG..LGG
  kkkkkkk
  KKKKKKK
  GLLGLLL
  GGGGGGG`)

// 거미줄: 구석에 친 줄 + 매달린 거미
sprite('dgWeb', { outline: 'k' }, `
  LLLLLLLLLLLLLL
  LL..L...L...G.
  L.L..L..L..G..
  L..LL.L.L.G...
  LL..LLLLLL....
  L.L..L..L.....
  L..L..L.L.....
  LLLLLL.L......
  L..L..L.......
  L...L.L...k...
  L....L..k.k.k.
  LL...L...pPp..
  L...L...kpvpk.
  L.......k.p.k.`)

// 열린 보물 상자 (dgChest와 같은 몸통)
sprite('dgChestOpen', { mx: true, outline: 'k' }, `
  ..ttttt
  .tddddd
  tdddddd
  kkkkkkk
  ..H..hH
  .hYhhYh
  YhhhYhh
  kkkkkkk
  DDGDDYh
  DtLtDYY
  DDGDDDD
  ddGdddd`)

// 잠긴 문: 아치 나무문 + 쇠 자물쇠
sprite('dgLocked', { mx: true, outline: 'k' }, `
  ...GGGG
  .GGDDDD
  .GDtDDt
  GDtDDtD
  GDtDDtD
  GDtDDGG
  GDtDGLL
  GDtDGLk
  GDtDLLL
  GDtDLLk
  GDtDGLk
  GDtDDGG
  GDtDDtD
  GGGGGGG`)

// 회복 물약: 붉은 하트 물약
sprite('dgPotion', { mx: true, outline: 'k' }, `
  .....dT
  .....dt
  .....LW
  .....LL
  ....LLL
  ...LMMM
  ..LWqMM
  .LWMqMQ
  .LMqQQQ
  .LMMqQQ
  .LmMMqM
  ..LmmMM
  ...LLLL`)

sheet('dungeon_sheet', ['dg*'], { pad: 2 })

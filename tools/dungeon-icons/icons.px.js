// 던전 새 도트 아이콘 (pixel-icons.js와 같은 팔레트·16칸·1px k 테두리)
// 만들기: node ~/.claude/skills/pxl-pixel-art/bin/pxl.js build tools/dungeon-icons/icons.px.js
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

// 🕳️ 계단: 돌 테두리 구멍 안으로 계단이 내려가고 바닥은 보랏빛
sprite('stairs', { mx: true, outline: 'k' }, `
  ...GGGG
  .GGLLLL
  GLLGGGG
  GLKkkkk
  GLkLLLL
  GLkGGGG
  GLkkLLL
  GLkkGGG
  GLkkkLL
  GGkkkGG
  .GkkPPv
  ..GGPvV
  ...GGGG`)

// 📭 열린 상자: 닫힌 상자(box)와 같은 몸통, 뚜껑이 뒤로 열리고 금빛
sprite('boxOpen', { mx: true, outline: 'k' }, `
  ..ttttt
  .tdddDd
  tdddddd
  tdddddd
  kkkkkkk
  .hYH.hH
  YhhhYhh
  kkkkkkk
  tTTTTTh
  ttttttY
  ttTTttY
  tttttth
  DDDDDDD`)

// 🪤 덫: 벌어진 이빨 + 가운데 붉은 발판
sprite('trap', { mx: true, outline: 'k' }, `
  ....GGG
  ..GGLLL
  .GLLWKW
  .GLKLKL
  GLWKKKK
  GLLKKrR
  GLWKrRo
  GLLKrRR
  GLWKKrr
  GLLKKKK
  .GLKLKL
  .GLLWKW
  ..GGLLL
  ....GGG`)

// 🕸️ 거미줄: 바퀴살(밝게) + 고리(어둡게) + 작은 거미
sprite('web', {}, `
  L.....GLG.....L.
  .L...G.L.G...L..
  ..LGG..L..GGL...
  ..GL...L...LG...
  .G..L.GLG.L..G..
  .G...LGLGL...G..
  GLLLLLLkLLLLLLLL
  .G...LGkGL...G..
  .G..L.kkk.L..G..
  ..GL..vkv..LG...
  ..LGG..L..GGL...
  .L...G.L.G...L..
  L.....GLG.....L.`)

// ⛲ 회복의 샘: 돌 받침 + 물줄기
sprite('fountain', { mx: true, outline: 'k' }, `
  ......I
  ....iII
  ...i..I
  ..i..LL
  .i..LGG
  ...GGLL
  LLLLLLL
  LBBiBBB
  GLLLLLL
  .GGGGGG
  ...LLLL
  ...GGGG
  ..GGGGG`)

// 🗿 힘의 제단: 돌 받침 위에 떠 있는 보랏빛 구슬, 기둥에 룬
sprite('altar', { mx: true, outline: 'k' }, `
  .....PP
  ....PvV
  ....PVW
  ....Pvv
  .....PP
  ..GGGGG
  .GLLLLL
  .GGGGGG
  ...GLLL
  ...GLLP
  ...GLLv
  ...GLLL
  .GGLLLL
  GGGGGGG`)

// 🧪 물약: 둥근 플라스크, 왼쪽 위 유리 반짝임
sprite('potion', { outline: 'k' }, `
  .....dDTT.....
  .....dttt.....
  ......LLW.....
  ......LLL.....
  .....LLLLL....
  ....LnNNNnL...
  ...LWnnnNnnL..
  ..LWnnnnnnnEL.
  ..LnnnnnnnnEL.
  ..LnnnnnnnnEL.
  ..LEnnnnnnEEL.
  ...LEEEnnEEL..
  ....LLLLLLL...`)

// ⭕ 정답: 채점 동그라미
sprite('ring', { w: 14, h: 14, outline: 'k' },
  circ(6.5, 6.5, 6.5, 'M'),
  circ(6.5, 6.5, 3.5, '_'),
  (c) => { for (const [x, y] of [[3, 1], [2, 2], [1, 3], [4, 1], [1, 4], [5, 0], [0, 5]]) c.px(x, y, 'q') })


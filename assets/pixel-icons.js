/* 도트 아이콘 — 화면 글자 속 이모지를 게임 팔레트로 그린 16×16 픽셀 아이콘으로 바꿔 보여 줌
 *   icon-design 스킬 규칙: 이모지 대신 아이콘, 뜻(개념)에 맞춰 고르기, 같은 크기(1.15em), 같은 화풍(1px 진한 테두리 + 3~4단 색)
 *   색은 pixelfx 팔레트 램프(index.html PFX_RAMPS, assets/pixelfx-lite.js)와 같은 값
 *   원래 이모지 글자는 <span class="pxi"> 안에 그대로 남김 → textContent 비교·복사·화면 낭독은 예전과 같음
 *   끄기: 주소에 ?noicons=1 · 특정 영역 제외: class="no-pxi"
 */
(function () {
  'use strict';
  // 한 글자 = 한 색 ('.' = 투명)
  const PAL = {
    k: '#1b1424', K: '#3a3346', G: '#6e6880', L: '#b9b4c8', W: '#ffffff',
    r: '#a8321c', R: '#e0602a', o: '#ffb347', c: '#fff2c4',            // 불
    y: '#b8701c', Y: '#f0a92a', h: '#ffd84a', H: '#fff4b0',            // 금
    b: '#1e3a6e', B: '#2f74b8', i: '#5cc0f0', I: '#bdeaff',            // 얼음·물
    p: '#3b1a6e', P: '#6d3fc0', v: '#a875f0', V: '#dcc4ff',            // 비전
    e: '#0f5132', E: '#1f8f5a', n: '#4ade80', N: '#bbf7d0',            // 치유
    m: '#7a1730', M: '#d03a5a', q: '#ff7a9a', Q: '#ffd0dc',            // 붉은 계열
    d: '#5a3a20', D: '#8a5a30', t: '#c08a50', T: '#e8c090'             // 나무·가죽
  };

  const ICONS = {
    warn: [
      '.......kk.......',
      '......kYYk......',
      '......kYYk......',
      '.....kYhhYk.....',
      '.....kYkkYk.....',
      '....kYhkkhYk....',
      '....kYhkkhYk....',
      '...kYhhkkhhYk...',
      '...kYhhkkhhYk...',
      '..kYhhhhhhhhYk..',
      '..kYhhhkkhhhYk..',
      '.kYhhhhkkhhhhYk.',
      '.kYhhhhhhhhhhYk.',
      'kYYYYYYYYYYYYYYk',
      'kkkkkkkkkkkkkkkk'
    ],
    fire: [
      '.......k........',
      '......kok.......',
      '......kRok......',
      '.....kRRok..k...',
      '....kRRoRok.kk..',
      '...kRRRooRkkRk..',
      '...kRRooooRRRk..',
      '..kRRRocooRRRRk.',
      '..kRRoccccoRRRk.',
      '.krRoccccccoRRk.',
      '.krRoccWWccoRrk.',
      '.krRocWWWWcoRrk.',
      '.krrRocWWcoRrrk.',
      '..krrRoooRRrrk..',
      '...kkrrrrrrkk...',
      '.....kkkkkk.....'
    ],
    live: [
      '....k.....k.....',
      '.....k...k......',
      '......k.k.......',
      '.kkkkkkkkkkkkkk.',
      '.kGGGGGGGGGGGGk.',
      '.kGbbbbbbbbbbGk.',
      '.kGbBBBBBBBMMGk.',
      '.kGbBiiBBBBMMGk.',
      '.kGbBiBBBBBBBGk.',
      '.kGbBBBBBBBBBGk.',
      '.kGbBBBBBBBBBGk.',
      '.kGbbbbbbbbbbGk.',
      '.kGGGGGGGGGGGGk.',
      '.kkkkkkkkkkkkkk.',
      '...kk......kk...'
    ],
    swords: [
      'kk............kk',
      'kWLk........kLWk',
      '.kWLk......kLWk.',
      '..kWLk....kLWk..',
      '...kWLk..kLWk...',
      '....kWLkkLWk....',
      '.....kWLLWk.....',
      '......kLLk......',
      '.....kLkkLk.....',
      '..k.kLk..kLk.k..',
      '..kYYk....kYYk..',
      '...kYk....kYk...',
      '..kDkYk..kYkDk..',
      '.kDk.kk..kk.kDk.',
      'khk..........khk',
      'kk............kk'
    ],
    shield: [
      '..kkkkkkkkkkkk..',
      '.kYhhhhhhhhhhYk.',
      '.khBBBBhhBBBBhk.',
      '.khBiiBhhBBBBhk.',
      '.khBiBBhhBBBBhk.',
      '.khBBBBhhBBBBhk.',
      '.khhhhhhhhhhhhk.',
      '.khhhhhhhhhhhhk.',
      '.khBBBBhhBBBBhk.',
      '.kYhBBBhhBBBhYk.',
      '..kYhBBhhBBhYk..',
      '..kYhBBhhBBhYk..',
      '...kYhBhhBhYk...',
      '....kYhhhhYk....',
      '.....kYhhYk.....',
      '......kkkk......'
    ],
    crown: [
      '................',
      '................',
      '.k.....kk.....k.',
      'kMk...kMMk...kMk',
      'kYk...kYYk...kYk',
      'kYYk.kYhhYk.kYYk',
      'kYhYkYhhhhYkYhYk',
      'kYhhYhhhhhhYhhYk',
      'kYhhhhhhhhhhhhYk',
      'kYhhhMhhhhMhhhYk',
      'kYhhMMMhhMMMhhYk',
      'kYhhhMhhhhMhhhYk',
      'kyYYYYYYYYYYYYyk',
      'kyyyyyyyyyyyyyyk',
      '.kkkkkkkkkkkkkk.'
    ],
    bolt: [
      '.........kkkkk..',
      '........kHhhYk..',
      '.......kHhhYk...',
      '......kHhhYk....',
      '.....kHhhYk.....',
      '....kHhhYkkkkk..',
      '...kHhhhhhhhYk..',
      '..kkkkkkHhhYk...',
      '.......kHhYk....',
      '......kHhYk.....',
      '.....kHhYk......',
      '....kHYk........',
      '...kHYk.........',
      '..kYk...........',
      '..kk............'
    ],
    door: [
      '...kkkkkkkkkk...',
      '..kddddddddddk..',
      '..kdDDDDDDDDdk..',
      '..kdDttDDttDdk..',
      '..kdDttDDttDdk..',
      '..kdDttDDttDdk..',
      '..kdDDDDDDDDdk..',
      '..kdDDDDDDhhdk..',
      '..kdDDDDDDhydk..',
      '..kdDDDDDDDDdk..',
      '..kdDttDDttDdk..',
      '..kdDttDDttDdk..',
      '..kdDDDDDDDDdk..',
      '..kddddddddddk..',
      '.kkkkkkkkkkkkkk.'
    ],
    check: [
      '................',
      '.kkkkkkkkkkkkkk.',
      'kNnnnnnnnnnnnnnk',
      'knnnnnnnnnnnnnEk',
      'knnnnnnnnnnWWnEk',
      'knnnnnnnnnWWWnEk',
      'knnnnnnnnWWWnnEk',
      'knnWWnnnWWWnnnEk',
      'knnWWWnWWWnnnnEk',
      'knnnWWWWWnnnnnEk',
      'knnnnWWWnnnnnnEk',
      'knnnnnWnnnnnnnEk',
      'knnnnnnnnnnnnnEk',
      'kEEEEEEEEEEEEEEk',
      '.kkkkkkkkkkkkkk.'
    ],
    cross: [
      '.kkk........kkk.',
      'kqMMk......kMMMk',
      'kMMMMk....kMMMMk',
      '.kMMMMk..kMMMMk.',
      '..kMMMMkkMMMMk..',
      '...kMMMMMMMMk...',
      '....kMMMMMMk....',
      '....kMMMMMMk....',
      '...kMMMMMMMMk...',
      '..kMMMMkkMMMMk..',
      '.kMMMMk..kMMMMk.',
      'kMMMMk....kMMMmk',
      'kMMmk......kmmmk',
      '.kkk........kkk.'
    ],
    lock: [
      '.....kkkkkk.....',
      '....kLLLLLLk....',
      '...kLkkkkkkLk...',
      '...kLk....kLk...',
      '...kLk....kLk...',
      '...kGk....kGk...',
      '.kkkkkkkkkkkkkk.',
      '.kYhhhhhhhhhhYk.',
      '.kYhHhhkkhhhhYk.',
      '.kYhhhhkkhhhhYk.',
      '.kYhhhhkkhhhhYk.',
      '.kYhhhhhkhhhhYk.',
      '.kYhhhhhhhhhhYk.',
      '.kyYYYYYYYYYYyk.',
      '.kkkkkkkkkkkkkk.'
    ],
    gem: [
      '................',
      '...kkkkkkkkkk...',
      '..kWIIiIIiIIik..',
      '.kWIIiiIIiiIiik.',
      'kkkkkkkkkkkkkkkk',
      'kIIiiiBiiBiiiBBk',
      '.kIiiiBiiBiiBBk.',
      '..kIiiBiiBiBBk..',
      '...kIiBiiBBBk...',
      '....kIiBiBBk....',
      '.....kIBBBk.....',
      '......kBBk......',
      '.......kk.......'
    ],
    trophy: [
      '..kkkkkkkkkkkk..',
      '.kkYhhhhhhhhYkk.',
      'kYkYhHhhhhhhYkYk',
      'kYkYhHhhhhhhYkYk',
      'kYkYhhhhhhhhYkYk',
      '.kYYhhhhhhhhYYk.',
      '..kkYhhhhhhYkk..',
      '....kYhhhhYk....',
      '.....kYhhYk.....',
      '......kYYk......',
      '......kYYk......',
      '.....kYhhYk.....',
      '....kkkkkkkk....',
      '....kDDDDDDk....',
      '....kkkkkkkk....'
    ],
    castle: [
      '................',
      '.kk.kk....kk.kk.',
      '.kLkLk....kLkLk.',
      '.kLLLk.kk.kLLLk.',
      '.kLGLkkLLkkLGLk.',
      '.kLLLLLLLLLLLLk.',
      '.kLLLLLLLLLLLLk.',
      '.kLGLLkkkkLLGLk.',
      '.kLLLkddddkLLLk.',
      '.kLLLkdDDdkLLLk.',
      '.kLLLkdDDdkLLLk.',
      '.kLLLkdDDdkLLLk.',
      '.kGGGkdDDdkGGGk.',
      '.kkkkkkkkkkkkkk.'
    ],
    target: [
      '.....kkkkkk.....',
      '...kkMMMMMMkk...',
      '..kMMWWWWWWMMk..',
      '.kMWWMMMMMMWWMk.',
      '.kMWMMWWWWMMWMk.',
      'kMWMWWMMMMWWMWMk',
      'kMWMWMMMMMMWMWMk',
      'kMWMWMMkkMMWMWMk',
      'kMWMWMMkkMMWMWMk',
      'kMWMWMMMMMMWMWMk',
      'kMWMWWMMMMWWMWMk',
      '.kMWMMWWWWMMWMk.',
      '.kMWWMMMMMMWWMk.',
      '..kMMWWWWWWMMk..',
      '...kkMMMMMMkk...',
      '.....kkkkkk.....'
    ],
    boom: [
      '.......k........',
      '..k...kok...k...',
      '..kok.kRok.kok..',
      '...kRkRRRokRk...',
      '.k.kRRRooRRRk.k.',
      '.kokRRoccoRRkok.',
      '..kRRocWWcoRRk..',
      'kkRRocWWWWcoRRkk',
      'kRRRocWWWWcoRRRk',
      '..kRRocWWcoRRk..',
      '.kokRRoccoRRkok.',
      '.k.kRRRooRRRk.k.',
      '...kRkRRRRkRk...',
      '..kok.kRRk.kok..',
      '..k....kk....k..'
    ],
    bot: [
      '.......kk.......',
      '......kMMk......',
      '.......kk.......',
      '..kkkkkkkkkkkk..',
      '.kLLLLLLLLLLLLk.',
      '.kLGGGGGGGGGGLk.',
      '.kLGiiGGGGiiGLk.',
      '.kLGiiGGGGiiGLk.',
      '.kLGGGGGGGGGGLk.',
      '.kLGGkkkkkkGGLk.',
      '.kLGGGGGGGGGGLk.',
      '.kLLLLLLLLLLLLk.',
      '..kkkkkkkkkkkk..',
      '....kGGGGGGk....',
      '...kLLLLLLLLk...',
      '...kkkkkkkkkk...'
    ],
    users: [
      '................',
      '...kkkk.........',
      '..kTTTTk..kkkk..',
      '..kTTTTk.kTTTTk.',
      '..kTTTTk.kTTTTk.',
      '...kkkk..kTTTTk.',
      '..kkkkkk..kkkk..',
      '.kBBBBBBkkkkkkk.',
      '.kBiBBBBkPvPPPPk',
      '.kBiBBBBkPvPPPPk',
      '.kBBBBBBkPPPPPPk',
      '.kBBBBBBkPPPPPPk',
      '.kkkkkkkkkkkkkkk'
    ],
    hourglass: [
      '..kkkkkkkkkkkk..',
      '..kDDDDDDDDDDk..',
      '...kIhhhhhhIk...',
      '...kIhhhhhhIk...',
      '....kIhhhhIk....',
      '.....kIhhIk.....',
      '......kIhk......',
      '......kIhk......',
      '.....kIIhIk.....',
      '....kIIIhIIk....',
      '...kIIIhhhIIk...',
      '...kIhhhhhhIk...',
      '..kDDDDDDDDDDk..',
      '..kkkkkkkkkkkk..'
    ],
    sparkle: [
      '.....k..........',
      '....khk.........',
      '....khk.........',
      '...khHhk......k.',
      '.kkhHWHhkk...khk',
      'khhHWWWHhhk...k.',
      '.kkhHWHhkk......',
      '...khHhk........',
      '....khk.....k...',
      '....khk....khk..',
      '.....k....khHhk.',
      '.........khHWHhk',
      '..........khHhk.',
      '...........khk..',
      '............k...'
    ],
    skull: [
      '....kkkkkkkk....',
      '...kWWWWWWWWk...',
      '..kWWWWWWWWWWk..',
      '.kWWWWWWWWWWLLk.',
      '.kWWkkkWWkkkWLk.',
      '.kWkkkkWWkkkkLk.',
      '.kWkkkkWWkkkkLk.',
      '.kWWkkWWWWkkWLk.',
      '..kWWWWkkWWWLk..',
      '...kLWWWWWWLk...',
      '...kWkWkWkWLk...',
      '...kkWkWkWkkk...',
      '....kkkkkkkk....'
    ],
    box: [
      '................',
      '..kkkkkkkkkkkk..',
      '.kTTTTThhTTTTTk.',
      'kTTTTTThhTTTTTTk',
      'kkkkkkkkkkkkkkkk',
      'ktttttthhttttttk',
      'ktttttthhttttttk',
      'ktttttthhttttttk',
      'kttTTtthhttttttk',
      'ktttttthhttttttk',
      'ktttttthhttttttk',
      'kDDDDDDDDDDDDDDk',
      'kkkkkkkkkkkkkkkk'
    ],
    star: [
      '.......kk.......',
      '......khhk......',
      '......khhk......',
      '.....khHhhk.....',
      '.....khHhhk.....',
      'kkkkkkhHhhkkkkkk',
      'khhhhhhhhhhhhhYk',
      '.khhhhhhhhhhhYk.',
      '..khhhhhhhhhYk..',
      '...khhhhhhhYk...',
      '...khhhhhhhYk...',
      '..khhhhkkhhhYk..',
      '..khhhk..khhYk..',
      '.khhk......kYYk.',
      '.kkk........kkk.'
    ],
    heart: [
      '................',
      '..kkkk....kkkk..',
      '.kMMMMk..kMMMMk.',
      'kMQWMMMkkMMMMMMk',
      'kMWMMMMMMMMMMMMk',
      'kMMMMMMMMMMMMMMk',
      'kMMMMMMMMMMMMMmk',
      '.kMMMMMMMMMMMmk.',
      '..kMMMMMMMMMmk..',
      '...kMMMMMMMmk...',
      '....kMMMMMmk....',
      '.....kMMMmk.....',
      '......kMmk......',
      '.......kk.......'
    ],
    heartPink: [
      '................',
      '..kkkk....kkkk..',
      '.kqqqqk..kqqqqk.',
      'kqWWqqqkkqqqqqqk',
      'kqWqqqqqqqqqqqqk',
      'kqqqqqqqqqqqqqqk',
      'kqqqqqqqqqqqqqMk',
      '.kqqqqqqqqqqqMk.',
      '..kqqqqqqqqqMk..',
      '...kqqqqqqqMk...',
      '....kqqqqqMk....',
      '.....kqqqMk.....',
      '......kqMk......',
      '.......kk.......'
    ],
    snow: [
      '.......k........',
      '......kIk.......',
      '....k.kIk.k.....',
      '...kIkkIkkIk....',
      '....kIkIkIk.....',
      '.k...kIIIk...k..',
      'kIkkkkIWIkkkkIk.',
      'kIIIIIWWWIIIIIk.',
      'kIkkkkIWIkkkkIk.',
      '.k...kIIIk...k..',
      '....kIkIkIk.....',
      '...kIkkIkkIk....',
      '....k.kIk.k.....',
      '......kIk.......',
      '.......k........'
    ],
    drop: [
      '.......kk.......',
      '......kiik......',
      '......kiik......',
      '.....kiiiik.....',
      '.....kiiiik.....',
      '....kiiiiiik....',
      '...kiWiiiiiik...',
      '...kiWiiiiiBk...',
      '..kiWiiiiiiiBk..',
      '..kiWiiiiiiiBk..',
      '..kiiiiiiiiiBk..',
      '..kiiiiiiiiBBk..',
      '...kiiiiiiBBk...',
      '....kBBBBBBk....',
      '.....kkkkkk.....'
    ],
    blood: [
      '.......kk.......',
      '......kMMk......',
      '......kMMk......',
      '.....kMMMMk.....',
      '.....kMMMMk.....',
      '....kMMMMMMk....',
      '...kMQMMMMMMk...',
      '...kMQMMMMMmk...',
      '..kMQMMMMMMMmk..',
      '..kMQMMMMMMMmk..',
      '..kMMMMMMMMMmk..',
      '..kMMMMMMMMmmk..',
      '...kMMMMMMmmk...',
      '....kmmmmmmk....',
      '.....kkkkkk.....'
    ],
    key: [
      '................',
      '..kkkk..........',
      '.kYhhYk.........',
      'kYhkkhYk........',
      'kYk..kYkkkkkkkk.',
      'kYk..kYhhhhhhhYk',
      'kYhkkhYkkkkYkYk.',
      '.kYhhYk...kYkYk.',
      '..kkkk.....kkkk.'
    ],
    clock: [
      '.kk..........kk.',
      'kMMk.kkkkkk.kMMk',
      'kMkkkWWWWWWkkkMk',
      '.kkWWWWkWWWWWkk.',
      '.kWWWWWkWWWWWLk.',
      '.kWWWWWkWWWWWLk.',
      'kWWWWWWkWWWWWWLk',
      'kWWWWWWkWWWWWWLk',
      'kWWWWWWkkkkWWWLk',
      'kWWWWWWWWWWWWWLk',
      '.kWWWWWWWWWWWLk.',
      '.kLWWWWWWWWWLLk.',
      '..kLLWWWWWLLLk..',
      '...kkLLLLLLkk...',
      '..kk.kkkkkk.kk..'
    ],
    dice: [
      '.kkkkkkkkkkkkkk.',
      'kWWWWWWWWWWWWWLk',
      'kWkkWWWWWWWWkkLk',
      'kWkkWWWWWWWWkkLk',
      'kWWWWWWWWWWWWWLk',
      'kWWWWWWWWWWWWWLk',
      'kWWWWWWMMWWWWWLk',
      'kWWWWWWMMWWWWWLk',
      'kWWWWWWWWWWWWWLk',
      'kWWWWWWWWWWWWWLk',
      'kWkkWWWWWWWWkkLk',
      'kWkkWWWWWWWWkkLk',
      'kWWWWWWWWWWWWWLk',
      'kLLLLLLLLLLLLLLk',
      '.kkkkkkkkkkkkkk.'
    ],
    gamepad: [
      '................',
      '................',
      '...kkkk..kkkk...',
      '..kGGGGkkGGGGk..',
      '.kGGGGGGGGGGGGk.',
      'kGGkGGGGGGGGMGGk',
      'kGkkkGGGGGGiGnGk',
      'kGGkGGGkkGGGhGGk',
      'kGGGGGGGGGGGGGGk',
      'kGGGGkkkkkkGGGGk',
      '.kGGk......kGGk.',
      '..kk........kk..'
    ],
    coin: [
      '.....kkkkkk.....',
      '...kkYYYYYYkk...',
      '..kYhhhhhhhhYk..',
      '.kYhHhhhhhhhhYk.',
      '.kYhHhhkkhhhhYk.',
      'kYhHhhkhhkhhhhYk',
      'kYhhhhkhhhhhhhYk',
      'kYhhhhhkkhhhhhYk',
      'kYhhhhhhhkhhhhYk',
      'kYhhhhkhhkhhhhYk',
      '.kYhhhhkkhhhhYk.',
      '.kYhhhhhhhhhhYk.',
      '..kYYhhhhhhYYk..',
      '...kkyyyyyykk...',
      '.....kkkkkk.....'
    ],
    orb: [
      '.....kkkkkk.....',
      '...kkPPPPPPkk...',
      '..kPvVVvvvvvPk..',
      '.kPvVWVvvvvvvPk.',
      '.kPvVVvvvvvvvPk.',
      'kPvvvvvvvvvvvvPk',
      'kPvvvvvvvvvvvPPk',
      'kPvvvvvvvvvvvPPk',
      'kPPvvvvvvvvvPPPk',
      '.kPPvvvvvvvPPpk.',
      '.kpPPPvvvPPPppk.',
      '..kppPPPPPpppk..',
      '...kkkkkkkkkk...',
      '..kyYYYYYYYYyk..',
      '.kkkkkkkkkkkkkk.'
    ],
    gift: [
      '...kk.....kk....',
      '..kMMk...kMMk...',
      '...kMMk.kMMk....',
      '.kkkkkkkkkkkkkk.',
      '.kQqqqqhhqqqqqk.',
      '.kqqqqqhhqqqqqk.',
      '.kkkkkkkkkkkkkk.',
      '..kMMMMhhMMMMk..',
      '..kMMMMhhMMMMk..',
      '..kMMMMhhMMMMk..',
      '..kMMMMhhMMMMk..',
      '..kmMMMhhMMMmk..',
      '..kmmmmyymmmmk..',
      '..kkkkkkkkkkkk..'
    ],
    chat: [
      '................',
      '.kkkkkkkkkkkkkk.',
      'kWWWWWWWWWWWWWLk',
      'kWWWWWWWWWWWWWLk',
      'kWWkkWWkkWWkkWLk',
      'kWWkkWWkkWWkkWLk',
      'kWWWWWWWWWWWWWLk',
      'kLLLLLLLLLLLLLLk',
      '.kkkkLLkkkkkkkk.',
      '....kLk.........',
      '....kk..........'
    ],
    hammer: [
      '...kkkkkkk......',
      '..kLLLLLLLkk....',
      '.kWLLLLLLLLLk...',
      '.kLLLLLLLLLGk...',
      '..kGGGGGGGGk....',
      '...kkkkkkdkk....',
      '........kdDk....',
      '.......kdDk.....',
      '......kdDk......',
      '.....kdDk.......',
      '....kdDk........',
      '...kdDk.........',
      '..kdDk..........',
      '..kdk...........',
      '..kk............'
    ],
    medal: [
      '.kkkk....kkkk...',
      '.kBBBk..kMMMk...',
      '..kBBBkkMMMk....',
      '...kBBBMMMk.....',
      '....kkkkkk......',
      '...kkYYYYkk.....',
      '..kYhhhhhhYk....',
      '.kYhHhhhhhhYk...',
      '.kYhHhhkhhhYk...',
      '.kYhhhkkhhhYk...',
      '.kYhhhhkhhhYk...',
      '.kYhhhhkhhhYk...',
      '..kYhhhhhhYk....',
      '...kkYYYYkk.....',
      '.....kkkk.......'
    ],
    megaphone: [
      '...........kk...',
      '.........kkMk...',
      '.......kkMMMk...',
      '.kkkkkkMMMMMk.k.',
      'kLLLLkMMMMMMk..k',
      'kLLLLkMMMMMMk.k.',
      'kLLLLkMMMMMMk...',
      'kGGGGkMMMMMMk.kk',
      '.kkkkkkMMMMMk...',
      '..kLk..kkmMMk.k.',
      '..kLk....kkmk..k',
      '..kkk......kk...'
    ],
    // ✏️·📝
    pencil: [
      '...........kkk..',
      '..........kMMMk.',
      '.........kLkMMk.',
      '........khhLkk..',
      '.......khhhhk...',
      '......khhhhk....',
      '.....khhhhk.....',
      '....khhhhk......',
      '...kThhhk.......',
      '..kTTThk........',
      '..kTTTk.........',
      '.kKTk...........',
      '.kkk............'
    ],
    // 🔨는 망치, 🪓 도끼
    axe: [
      '......kkkk......',
      '....kkLLLLk.....',
      '...kWLLLLLkk....',
      '..kWLLLLkkdk....',
      '..kLLLLkkdDk....',
      '..kLLLLkdDk.....',
      '...kGGkdDk......',
      '....kkdDk.......',
      '.....kdDk.......',
      '....kdDk........',
      '...kdDk.........',
      '..kdDk..........',
      '.kdDk...........',
      '.kdk............',
      '.kk.............'
    ],
    // 🎒 가방 · 🛒 장보기는 따로 그리지 않음
    bag: [
      '.....kkkkkk.....',
      '....kDk..kDk....',
      '..kkkkkkkkkkkk..',
      '.kTTTTTTTTTTTTk.',
      '.ktTTTTTTTTTTtk.',
      '.ktkkkkkkkkkktk.',
      '.ktkDDDhhDDDktk.',
      '.ktkDDDyyDDDktk.',
      '.ktkkkkkkkkkktk.',
      '.kttttttttttttk.',
      '.kttttttttttttk.',
      '.kDDDDDDDDDDDDk.',
      '..kkkkkkkkkkkk..'
    ],
    dagger: [
      '.............kk.',
      '............kWk.',
      '...........kWLk.',
      '..........kWLk..',
      '.........kWLk...',
      '........kWLk....',
      '.......kWLk.....',
      '..k...kWLk......',
      '..kYk.kLk.......',
      '...kYkkk........',
      '....kYYk........',
      '...kDkkYk.......',
      '..kDk...kk......',
      '.khk............',
      '.kk.............'
    ],
    scroll: [
      '..kkkkkkkkkkk...',
      '.kTtkcccccccck..',
      '.kTtkcccccccck..',
      '..kkcckkkkkcck..',
      '...kcccccccck...',
      '...kcckkkkkcck..',
      '...kccccccccck..',
      '...kcckkkkcccck.',
      '...kccccccccccck',
      '..kkkkkkkkkkkkkk',
      '.kTtttttttttttTk',
      '..kkkkkkkkkkkkk.'
    ]
  };

  // 이모지 → 아이콘 이름 (변형 선택자 FE0F는 떼고 적음)
  const MAP = {
    '⚠': 'warn', '🔥': 'fire', '📺': 'live', '⚔': 'swords', '🛡': 'shield', '👑': 'crown',
    '⚡': 'bolt', '🚪': 'door', '✅': 'check', '✔': 'check', '❌': 'cross', '❎': 'cross',
    '🔒': 'lock', '🔐': 'lock', '💎': 'gem', '🏆': 'trophy', '🏰': 'castle', '🎯': 'target',
    '💥': 'boom', '🤖': 'bot', '👥': 'users', '⏳': 'hourglass', '⌛': 'hourglass',
    '✨': 'sparkle', '💀': 'skull', '☠': 'skull', '📦': 'box', '🌟': 'star', '⭐': 'star',
    '❤': 'heart', '💔': 'heart', '💗': 'heartPink', '💖': 'heartPink', '💕': 'heartPink',
    '❄': 'snow', '🧊': 'snow', '💧': 'drop', '🩸': 'blood', '🔑': 'key', '🗝': 'key',
    '⏰': 'clock', '⏱': 'clock', '🕐': 'clock', '🎲': 'dice', '🎮': 'gamepad',
    '🪙': 'coin', '💰': 'coin', '🔮': 'orb', '🎁': 'gift', '💬': 'chat', '🔨': 'hammer',
    '🏅': 'medal', '🥇': 'medal', '📢': 'megaphone', '📣': 'megaphone', '✏': 'pencil', '📝': 'pencil',
    '🪓': 'axe', '🎒': 'bag', '🗡': 'dagger', '📜': 'scroll'
  };

  function svgOf(rows) {
    // 색마다 path 하나 (가로로 이어진 칸은 한 번에) → 아이콘 하나에 1~2KB
    const paths = {};
    rows.forEach((row, y) => {
      for (let x = 0; x < row.length;) {
        const ch = row[x];
        let w = 1;
        while (row[x + w] === ch) w++;
        if (ch !== '.' && PAL[ch]) paths[ch] = (paths[ch] || '') + `M${x} ${y}h${w}v1h-${w}z`;
        x += w;
      }
    });
    const top = Math.floor((16 - rows.length) / 2);
    let body = '';
    for (const ch in paths) body += `<path fill="${PAL[ch]}" d="${paths[ch]}"/>`;
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 ${-top} 16 16" shape-rendering="crispEdges">${body}</svg>`;
  }

  const api = { PAL, ICONS, MAP, svgOf };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof document === 'undefined') return;
  window.PixelIcons = api;
  try { if (/[?&]noicons=1/.test(location.search)) return; } catch (e) { }

  // ── 스타일: 아이콘마다 class 하나 ──
  let css = '.pxi{display:inline-block;width:1.15em;height:1.15em;vertical-align:-0.2em;line-height:1.15em;'
    + 'background:no-repeat center/contain;image-rendering:pixelated;color:transparent!important;-webkit-text-fill-color:transparent!important;'
    + 'text-shadow:none!important;overflow:hidden;white-space:nowrap;text-indent:-99em;font-style:normal}'
    + '.pxe-x{display:none!important}';
  for (const name in ICONS) css += `.pxi-${name}{background-image:url("data:image/svg+xml,${encodeURIComponent(svgOf(ICONS[name]))}")}`;
  const style = document.createElement('style');
  style.id = 'pixel-icons-css';
  style.textContent = css;
  (document.head || document.documentElement).appendChild(style);

  // ── 글자 속 이모지 찾아 바꾸기 ──
  const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const keys = Object.keys(MAP).sort((a, b) => b.length - a.length);
  const RE = new RegExp('(?:' + keys.map(esc).join('|') + ')\\uFE0F?', 'gu');
  const TEST = new RegExp(RE.source, 'u');
  const SKIP = 'script,style,textarea,input,select,option,svg,canvas,title,noscript,[contenteditable],.pxi,.pxe-x,.no-pxi';

  // 문구 옆에 붙은 이모지는 도트 아이콘이 있든 없든 숨김 (글자는 span 안에 남겨 textContent 검사는 그대로)
  //   이모지만 있는 버튼·링크 같은 곳(꼭 필요한 것)만 남기고, 그건 도트 아이콘으로 보여 줌
  const EMO = String.raw`(?:\p{Emoji_Presentation}|\p{Extended_Pictographic}\uFE0F)(?:\u200D\p{Extended_Pictographic}\uFE0F?)*[\u{1F3FB}-\u{1F3FF}]?`;
  const ALL = new RegExp('(?:' + keys.map(esc).join('|') + ')' + String.raw`\uFE0F?|` + EMO, 'gu');
  const ANY = new RegExp(EMO + '|(?:' + keys.map(esc).join('|') + ')', 'u');
  const STRIP = new RegExp(EMO + String.raw`|[\uFE0F\u200D\s]`, 'gu');
  const hasWords = el => !!el && (el.textContent || '').replace(STRIP, '').length > 0;
  function nextToText(node) {
    if (node.nodeValue.replace(STRIP, '').length) return true;
    let el = node.parentElement;
    for (let i = 0; i < 2 && el; i++) {
      if (el.matches('button,a,[role=button],label,option')) return hasWords(el);
      if (hasWords(el)) return true;
      el = el.parentElement;
    }
    return false;
  }

  function convertText(node) {
    const s = node.nodeValue;
    if (!s || !ANY.test(s)) return;
    const parent = node.parentElement;
    if (!parent || parent.closest(SKIP)) return;
    const hideRaw = nextToText(node);
    const frag = document.createDocumentFragment();
    let last = 0, changed = false;
    ALL.lastIndex = 0;
    for (let m; (m = ALL.exec(s));) {
      const base = m[0].replace('️', '');
      const icon = MAP[base];
      if (!icon && !hideRaw) continue;
      if (m.index > last) frag.appendChild(document.createTextNode(s.slice(last, m.index)));
      const span = document.createElement('span');
      if (icon && !hideRaw) {
        span.className = 'pxi pxi-' + icon;
        span.setAttribute('role', 'img');
        span.setAttribute('aria-label', base);
      } else {
        span.className = 'pxe-x';
        span.setAttribute('aria-hidden', 'true');
      }
      span.textContent = m[0];
      frag.appendChild(span);
      last = m.index + m[0].length;
      changed = true;
    }
    if (!changed) return;
    if (last < s.length) frag.appendChild(document.createTextNode(s.slice(last)));
    node.parentNode.replaceChild(frag, node);
  }

  function scan(root) {
    if (!root) return;
    if (root.nodeType === 3) { convertText(root); return; }
    if (root.nodeType !== 1 && root.nodeType !== 11) return;
    if (root.nodeType === 1 && root.closest(SKIP)) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const list = [];
    for (let n; (n = walker.nextNode());) if (ANY.test(n.nodeValue)) list.push(n);
    list.forEach(convertText);
  }

  // 바뀐 곳만 모아서 한 번에 처리 (화면을 자주 다시 그려도 가볍게)
  let pending = new Set(), queued = false;
  function flush() {
    queued = false;
    const items = pending; pending = new Set();
    items.forEach(n => { if (n.isConnected) scan(n); });
  }
  const obs = new MutationObserver(muts => {
    for (const m of muts) {
      if (m.type === 'characterData') pending.add(m.target);
      else m.addedNodes.forEach(n => pending.add(n));
    }
    if (!queued && pending.size) { queued = true; (window.queueMicrotask || setTimeout)(flush); }
  });
  function start() {
    scan(document.body);
    obs.observe(document.body, { childList: true, subtree: true, characterData: true });
  }
  if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
})();

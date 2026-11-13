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

  // ── 두 번째 묶음 ──
  Object.assign(ICONS, {
    hand: [
      '.......kk.kk....',
      '....kkkTTkTTk...',
      '...kTTkTTkTTkkk.',
      '...kTTkTTkTTkTTk',
      '...kTTkTTkTTkTTk',
      'kk.kTTkTTkTTkTTk',
      'kTkkTTkTTkTTkTTk',
      'kTTkTTTTTTTTTTTk',
      '.kTTTTTTTTTTTTtk',
      '.kTTTTTTTTTTTtk.',
      '..kTTTTTTTTTttk.',
      '...kTTTTTTTttk..',
      '....kttttttttk..',
      '....kkkkkkkkkk..'
    ],
    wave: [
      '.....kkkkk......',
      '...kkiiIIik.....',
      '..kiiBkkkIik....',
      '.kiBk...kWik....',
      '.kiBk....kk.....',
      'kiBBk...........',
      'kiBBBk.....kk...',
      'kiBBBBkkkkkiik..',
      'kBBiiBBBBiiIIik.',
      'kBBBBiiiiIIWWIik',
      'kbBBBBBBBBBBBBBk',
      'kbbBBBBBBBBBBBbk',
      'kkkkkkkkkkkkkkkk'
    ],
    dash: [
      '.......kkkk.....',
      '......kWWWWk....',
      '....kkWWWWWLkk..',
      'kkkkWWWWWWWWWLk.',
      'kLLkWWWWWWWWWLLk',
      'kkkkLWWWWWWWLLLk',
      '....kLLLLLLLLLk.',
      'kkk..kkkkkkkkk..',
      'kLLkkkk.........',
      'kkkLLLLk........',
      '...kkkkk........'
    ],
    globe: [
      '.....kkkkkk.....',
      '...kkBBnnBBkk...',
      '..kBBnnnnBBBBk..',
      '.kBnnnnnBBBnnBk.',
      '.kBnnnnBBBnnnBk.',
      'kBBBnnBBBBBnnBBk',
      'kBBBBnBBBBBBnBBk',
      'kBBBBBBnnBBBBBBk',
      'kBBBBBnnnnnBBBBk',
      'kBnBBBnnnnnBBBBk',
      '.kBnBBBnnnBBBBk.',
      '.kBBBBBBnBBBBBk.',
      '..kBBBBBBBBBBk..',
      '...kkBBBBBBkk...',
      '.....kkkkkk.....'
    ],
    scale: [
      '.......kk.......',
      '......kYYk......',
      '.kkkkkkYYkkkkkk.',
      '.kYYYYYYYYYYYYk.',
      '.kkk..kYYk..kkk.',
      '..k...kYYk...k..',
      '.k.k..kYYk..k.k.',
      'k...k.kYYk.k...k',
      'kkkkk.kYYk.kkkkk',
      'kYhYk.kYYk.kYhYk',
      '.kkk..kYYk..kkk.',
      '.....kYYYYk.....',
      '....kYhhhhYk....',
      '...kkkkkkkkkk...'
    ],
    swirl: [
      '....kkkkkkk.....',
      '..kkiiiiiiikk...',
      '.kiikkkkkkkiik..',
      'kiik.......kiik.',
      'kik..kkkkk..kik.',
      'kik.kiiiiik.kik.',
      'kik.kik.kik.kik.',
      'kik.kik..kk.kik.',
      'kik.kiik....kik.',
      'kik..kiikkkkiik.',
      'kiik..kkiiiiik..',
      '.kiik..kkkkkk...',
      '..kiikk.........',
      '...kkiikkkk.....',
      '.....kkiiiik....',
      '.......kkkkk....'
    ],
    palette: [
      '...kkkkkkkk.....',
      '..kTTTTTTTTkk...',
      '.kTMMTTTnnTTTk..',
      'kTTMMTTTnnTTTTk.',
      'kTTTTTTTTTTiiTk.',
      'kThhTTTTTTTiiTk.',
      'kThhTTkkTTTTTTk.',
      'kTTTTk..kTTvvTk.',
      '.kTTTk..kTTvvTk.',
      '..kTTTkkTTTTTk..',
      '...kkTTTTTTkk...',
      '.....kkkkkk.....'
    ],
    sprout: [
      '..kkk.....kkk...',
      '.knnnk...knnnk..',
      'kNnnnEk.kEnnnNk.',
      '.kEnnnEkEnnnEk..',
      '..kkEEnEnEEkk...',
      '....kkkEkkk.....',
      '......kEk.......',
      '......kEk.......',
      '..kkkkkkkkkkk...',
      '.kDtDDtDDDtDDk..',
      '.kdDDDDDtDDDdk..',
      '..kkkkkkkkkkk...'
    ],
    house: [
      '.......kk.......',
      '......kMMk......',
      '.....kMMMMk.....',
      '....kMMMMMMk....',
      '...kMMMMMMMMk...',
      '..kMMMMMMMMMMk..',
      '.kmmmmmmmmmmmmk.',
      'kkkTTTTTTTTTTkkk',
      '..kTTTTTTTTTTk..',
      '..kTkkkTkkkkTk..',
      '..kTkikTkDDkTk..',
      '..kTkkkTkDDkTk..',
      '..kTTTTTkDhkTk..',
      '..ktttttkDDktk..',
      '..kkkkkkkkkkkk..'
    ],
    rock: [
      '.....kkkkk......',
      '...kkLLLGGkk....',
      '..kLLLLGGGGGk...',
      '.kLLWLGGGGGGKk..',
      '.kLLLGGGGGGKKk..',
      'kGLLGGGGGGKKKKk.',
      'kGGGGGGGKKKKKKk.',
      'kKGGGGKKKKKKKKk.',
      '.kkkkkkkkkkkkk..'
    ],
    up: [
      '.......kk.......',
      '......knnk......',
      '.....knNnnk.....',
      '....knNnnnnk....',
      '...knNnnnnnnk...',
      '..knnnnnnnnnnk..',
      '.kkkkknnnnkkkkk.',
      '.....knnnEk.....',
      '.....knnnEk.....',
      '.....knnnEk.....',
      '.....knnnEk.....',
      '.....knnnEk.....',
      '.....kkkkkk.....'
    ],
    diamond: [
      '.......kk.......',
      '......kIik......',
      '.....kIiiik.....',
      '....kIiiiiBk....',
      '...kIiiiiiBBk...',
      '..kIiiiiiiiBBk..',
      '.kIiiiiiiiiiBBk.',
      '..kBiiiiiiiBbk..',
      '...kBiiiiiBbk...',
      '....kBiiiBbk....',
      '.....kBiBbk.....',
      '......kBbk......',
      '.......kk.......'
    ],
    anger: [
      '....kk....kk....',
      '...kMk....kMk...',
      '...kMk....kMk...',
      '.kkkMk....kMkkk.',
      '.kMMMk....kMMMk.',
      '.kkkk......kkkk.',
      '................',
      '.kkkk......kkkk.',
      '.kMMMk....kMMMk.',
      '.kkkMk....kMkkk.',
      '...kMk....kMk...',
      '...kMk....kMk...',
      '....kk....kk....'
    ],
    sleep: [
      '........kkkkkkkk',
      '........kVVVVVVk',
      '........kkkkkVVk',
      '...........kVVk.',
      '..........kVVk..',
      '.........kVVk...',
      '........kVVkkkkk',
      'kkkkkk..kVVVVVVk',
      'kVVVVk..kkkkkkkk',
      'kkkVkk..........',
      '..kVk...........',
      '.kVk............',
      'kkVkkk..........',
      'kVVVVk..........',
      'kkkkkk..........'
    ],
    paw: [
      '....kk....kk....',
      '...kDDk..kDDk...',
      '...kDDk..kDDk...',
      '.kk.kk....kk.kk.',
      'kDDk........kDDk',
      'kDDk..kkkk..kDDk',
      '.kk..kDDDDk..kk.',
      '....kDDDDDDk....',
      '...kDDDDDDDDk...',
      '...kDDDDDDDDk...',
      '...kdDDDDDDdk...',
      '....kkddddkk....',
      '......kkkk......'
    ],
    clipboard: [
      '.....kkkkkk.....',
      '...kkkLGGLkkk...',
      '..kDDkkkkkkDDk..',
      '..kDWWWWWWWWDk..',
      '..kDWkkkkkkWDk..',
      '..kDWWWWWWWWDk..',
      '..kDWkkkkkWWDk..',
      '..kDWWWWWWWWDk..',
      '..kDWkkkkkkWDk..',
      '..kDWWWWWWWWDk..',
      '..kDWkkkWWWWDk..',
      '..kDWWWWWWWWDk..',
      '..kDDDDDDDDDDk..',
      '..kkkkkkkkkkkk..'
    ],
    flagCheck: [
      'kk..............',
      'kLkkkkkkkkkkkkk.',
      'kLkWWKKWWKKWWKk.',
      'kLkWWKKWWKKWWKk.',
      'kLkKKWWKKWWKKWk.',
      'kLkKKWWKKWWKKWk.',
      'kLkWWKKWWKKWWKk.',
      'kLkWWKKWWKKWWKk.',
      'kLkkkkkkkkkkkkk.',
      'kLk.............',
      'kLk.............',
      'kLk.............',
      'kLk.............',
      'kLk.............',
      'kGk.............',
      'kkk.............'
    ],
    flag: [
      'kk..............',
      'kLkkkkkkkkkkkkk.',
      'kLkWWWWWWWWWWWk.',
      'kLkWWWWWWWWWWWk.',
      'kLkWWWWWWWWWWLk.',
      'kLkWWWWWWWWWWLk.',
      'kLkWWWWWWWWWLLk.',
      'kLkLLLLLLLLLLLk.',
      'kLkkkkkkkkkkkkk.',
      'kLk.............',
      'kLk.............',
      'kLk.............',
      'kLk.............',
      'kLk.............',
      'kGk.............',
      'kkk.............'
    ],
    books: [
      '..kkkkkkkkkkkk..',
      '..kMMMMMMMMMMWk.',
      '..kmmmmmmmmmmWk.',
      '.kkkkkkkkkkkkkk.',
      '.kBBBBBBBBBBBWk.',
      '.kbbbbbbbbbbbWk.',
      'kkkkkkkkkkkkkkk.',
      'knnnnnnnnnnnnWk.',
      'kEEEEEEEEEEEEWk.',
      'kkkkkkkkkkkkkkk.'
    ],
    rocket: [
      '...........kkkk.',
      '.........kkWWWk.',
      '........kWWWLLk.',
      '.......kWWLiiLk.',
      '......kWWLiBiLk.',
      '..kk.kWWLLiiLk..',
      '.kMkkWWLLLLLk...',
      '.kMMkWLLLLLk....',
      '..kkWLLLLLk.....',
      '...kkLLLLkMk....',
      '..kRokLLkMMk....',
      '.kRoookkkMk.....',
      '.kRcok...kk.....',
      'kRcok...........',
      'kkkk............'
    ],
    gear: [
      '.......kk.......',
      '..kk..kLLk..kk..',
      '.kLLkkLLLLkkLLk.',
      '.kLLLLLLLLLLLLk.',
      '..kLLLGGGGLLLk..',
      '..kLLGkkkkGLLk..',
      'kkLLGk....kGLLkk',
      'kLLLGk....kGLLLk',
      'kLLLGk....kGLLLk',
      'kkLLGk....kGLLkk',
      '..kLLGkkkkGLLk..',
      '..kLLLGGGGLLLk..',
      '.kGLLLLLLLLLLGk.',
      '.kGGkkGLLGkkGGk.',
      '..kk..kGGk..kk..',
      '.......kk.......'
    ],
    search: [
      '...kkkkkk.......',
      '..kLLLLLLk......',
      '.kLIWIIIILk.....',
      'kLIWIIIIIILk....',
      'kLIIIIIIIILk....',
      'kLIIIIIIIILk....',
      'kLIIIIIIIILk....',
      'kLiIIIIIIiLk....',
      '.kLiIIIIiLk.....',
      '..kLLLLLLkkk....',
      '...kkkkkkDDk....',
      '.........kDDk...',
      '..........kDDk..',
      '...........kDDk.',
      '............kkk.'
    ],
    magnet: [
      '..kkkkk..kkkkk..',
      '..kWWLk..kWWLk..',
      '..kLLGk..kLLGk..',
      '..kkkkk..kkkkk..',
      '..kMMmk..kMMmk..',
      '..kMMmk..kMMmk..',
      '..kMMmkkkkMMmk..',
      '..kMMMMMMMMMmk..',
      '...kMMMMMMMmk...',
      '....kmmmmmmk....',
      '.....kkkkkk.....'
    ],
    mic: [
      '.....kkkkkk.....',
      '....kGLLLLGk....',
      '....kLkLkLLk....',
      '....kGLLLLGk....',
      '....kLkLkLLk....',
      '....kGGGGGGk....',
      '.....kkkkkk.....',
      '.......kk.......',
      '......kDDk......',
      '......kDDk......',
      '......kDDk......',
      '.....kDDDDk.....',
      '.....kkkkkk.....'
    ],
    candle: [
      '.......k........',
      '......kok.......',
      '......kRok......',
      '......kRck......',
      '.......kk.......',
      '.....kkkkkk.....',
      '.....kWWWLk.....',
      '.....kWWWLk.....',
      '.....kWWWLk.....',
      '.....kWWWLk.....',
      '.....kWWWLk.....',
      '...kkkkkkkkkk...',
      '...kYhhhhhhYk...',
      '...kkkkkkkkkk...'
    ],
    bulb: [
      '.....kkkkkk.....',
      '....khhHHhhk....',
      '...khhHWWHhhk...',
      '...khHWHhhhhk...',
      '...khhHhhhhhk...',
      '...khhhhhhhYk...',
      '....khhhhhYk....',
      '.....khhhYk.....',
      '.....kLLLLk.....',
      '.....kGGGGk.....',
      '.....kLLLLk.....',
      '......kkkk......'
    ],
    bomb: [
      '..........k..o..',
      '.........k.kRk..',
      '........k...o...',
      '.......kk.......',
      '......kGGk......',
      '....kkKKKKkk....',
      '...kKGGKKKKKk...',
      '..kKGWKKKKKKKk..',
      '..kKGKKKKKKKKk..',
      '..kKKKKKKKKKKk..',
      '..kKKKKKKKKKKk..',
      '...kKKKKKKKKk...',
      '....kkKKKKkk....',
      '......kkkk......'
    ],
    moon: [
      '......kkkk......',
      '....kkhhhk......',
      '...khhhkk.......',
      '..khhhk.........',
      '..khhk..........',
      '.khhhk..........',
      '.khhhk..........',
      '.khhhk..........',
      '.khhhhk.........',
      '..khhhhk......k.',
      '..khhhhhkk..kkk.',
      '...khhhhhhkkhk..',
      '....kkhhhhhhk...',
      '......kkkkkk....'
    ],
    music: [
      '.....kkkkkkkkk..',
      '.....kvvvvvvvk..',
      '.....kvkkkkkvk..',
      '.....kvk...kvk..',
      '.....kvk...kvk..',
      '.....kvk...kvk..',
      '..kkkkvk.kkkvk..',
      '.kvvvvvkkvvvvk..',
      '.kvvvvvkvvvvvk..',
      '.kPvvvPkvPvvPk..',
      '..kkkkk.kkkkk...'
    ],
    egg: [
      '......kkkk......',
      '.....kWWWLk.....',
      '....kWWWWWLk....',
      '...kWWWWWWWLk...',
      '...kWWWWWWWLk...',
      '..kWWWWWWWWWLk..',
      '..kWWWWWWWWWLk..',
      '..kWWWWWWWWWLk..',
      '..kLWWWWWWWLLk..',
      '...kLWWWWWLLk...',
      '....kkLLLLkk....',
      '......kkkk......'
    ],
    plus: [
      '.....kkkkkk.....',
      '.....knNnnk.....',
      '.....knnnnk.....',
      '.....knnnnk.....',
      'kkkkkknnnnkkkkkk',
      'knNnnnnnnnnnnnnk',
      'knnnnnnnnnnnnnnk',
      'kEEEEEnnnnEEEEEk',
      'kkkkkknnnnkkkkkk',
      '.....knnnnk.....',
      '.....knnnnk.....',
      '.....kEEEEk.....',
      '.....kkkkkk.....'
    ]
  });
  // 위 절반만 그리고 180도 돌려 붙임 (돌아가는 두 화살표)
  const rot180 = rows => rows.slice().reverse().map(r => r.padEnd(16, '.').split('').reverse().join(''));
  const refreshTop = [
    '.....kkkkkk.....',
    '...kkBBBBBBkk.k.',
    '..kBBkkkkkkBBkBk',
    '.kBk......kBBBBk',
    '.kBk.....kBBBBBk',
    'kBk......kkkkkk.',
    'kBk.............',
    'kBk.............'
  ];
  ICONS.refresh = refreshTop.concat(rot180(refreshTop));
  // 같은 그림 색만 바꾸기
  const recolor = (rows, m) => rows.map(r => r.replace(/./g, c => m[c] || c));
  ICONS.heartGreen = recolor(ICONS.heart, { M: 'n', m: 'E', Q: 'N', W: 'W' });
  ICONS.heartBlue = recolor(ICONS.heart, { M: 'B', m: 'b', Q: 'I' });
  ICONS.heartPurple = recolor(ICONS.heart, { M: 'v', m: 'P', Q: 'V' });
  ICONS.medalSilver = recolor(ICONS.medal, { Y: 'G', h: 'L', H: 'W' });
  ICONS.medalBronze = recolor(ICONS.medal, { Y: 'd', h: 't', H: 'T' });
  ICONS.flagRed = recolor(ICONS.flag, { W: 'M', L: 'm' });
  ICONS.moonDark = recolor(ICONS.moon, { h: 'P' });
  // 색 동그라미 (🔴🟢 …): 원을 계산으로 그림
  const dot = (f, s, hi) => {
    const out = [];
    for (let y = 0; y < 12; y++) {
      let r = '..';
      for (let x = 0; x < 12; x++) {
        const dx = x - 5.5, dy = y - 5.5, d = Math.hypot(dx, dy);
        if (d >= 6) r += '.';
        else if (d >= 4.8) r += 'k';
        else if (dx < -1 && dy < -1 && d > 1.8 && d < 3.6) r += hi;
        else r += (dx + dy > 3.5 ? s : f);
      }
      out.push(r + '..');
    }
    return out;
  };
  Object.assign(ICONS, {
    dotRed: dot('M', 'm', 'Q'), dotGreen: dot('n', 'E', 'N'), dotBlue: dot('B', 'b', 'I'),
    dotYellow: dot('h', 'Y', 'H'), dotPurple: dot('v', 'P', 'V'), dotOrange: dot('R', 'r', 'o'),
    dotWhite: dot('W', 'L', 'W'), dotBlack: dot('K', 'k', 'G')
  });

  // ── 세 번째 묶음: 웹앱 화면에 실제로 많이 보이는 것 (2026-11-13 탭별 집계) ──
  const put = (rows, pts, ch) => rows.map((r, y) => r.padEnd(16, '.').split('').map((c, x) => pts.some(p => p[0] === x && p[1] === y) ? ch : c).join(''));
  const vflip = rows => rows.slice().reverse();
  const hflip = rows => rows.map(r => r.padEnd(16, '.').split('').reverse().join(''));
  const FACE = [
    '....kkkkkkkk....',
    '..kkhhhhhhhhkk..',
    '.khhHHhhhhhhhhk.',
    '.khHhhhhhhhhhhk.',
    'khhhhhhhhhhhhhhk',
    'khhhhhhhhhhhhhhk',
    'khhhhhhhhhhhhhhk',
    'khhhhhhhhhhhhhhk',
    'khhhhhhhhhhhhhhk',
    'khhhhhhhhhhhhhhk',
    'khhhhhhhhhhhhhYk',
    '.khhhhhhhhhhhYk.',
    '.kYhhhhhhhhhYYk.',
    '..kkYYYYYYYYkk..',
    '....kkkkkkkk....'
  ];
  // 3×5 글자 타일 (🔢 1234 · 🔤 ABCD)
  const GLYPH = {
    1: ['.W.', 'WW.', '.W.', '.W.', 'WWW'], 2: ['WW.', '..W', '.W.', 'W..', 'WWW'],
    3: ['WW.', '..W', '.W.', '..W', 'WW.'], 4: ['W.W', 'W.W', 'WWW', '..W', '..W'],
    A: ['.W.', 'W.W', 'WWW', 'W.W', 'W.W'], B: ['WW.', 'W.W', 'WW.', 'W.W', 'WW.'],
    C: ['.WW', 'W..', 'W..', 'W..', '.WW'], D: ['WW.', 'W.W', 'W.W', 'W.W', 'WW.']
  };
  const tile = (bg, a, b, c, d) => {
    const line = (g1, g2, i) => '.k' + bg + bg + GLYPH[g1][i].replace(/\./g, bg) + bg + bg + GLYPH[g2][i].replace(/\./g, bg) + bg + bg + 'k.';
    const blank = '.k' + bg.repeat(12) + 'k.';
    const out = ['.kkkkkkkkkkkkkk.', blank];
    for (let i = 0; i < 5; i++) out.push(line(a, b, i));
    out.push(blank);
    for (let i = 0; i < 5; i++) out.push(line(c, d, i));
    out.push(blank, '.kkkkkkkkkkkkkk.');
    return out;
  };
  // 비스듬한 막대 두 개 (🥢), 이중 나선 (🧬)
  const chopsticks = Array.from({ length: 14 }, (_, y) => {
    const r = Array(16).fill('.');
    for (const off of [0, 4]) {
      const x = 13 - y + off - 3;
      [[x - 1, 'k'], [x, 'T'], [x + 1, 't'], [x + 2, 'k']].forEach(([px, c]) => { if (px >= 0 && px < 16 && r[px] === '.') r[px] = c; });
    }
    return r.join('');
  });
  const dna = Array.from({ length: 16 }, (_, y) => {
    const r = Array(16).fill('.');
    const s = Math.sin(y * 0.62), a = Math.round(7.5 + 5 * s), b = Math.round(7.5 - 5 * s);
    if (y % 2 === 0 && Math.abs(a - b) > 2) for (let x = Math.min(a, b) + 1; x < Math.max(a, b); x++) r[x] = 'L';
    const dot = (x, c) => { r[x - 1] = r[x - 1] === '.' ? 'k' : r[x - 1]; r[x] = c; r[x + 1] = r[x + 1] === '.' ? 'k' : r[x + 1]; };
    if (s >= 0) { dot(b, 'M'); dot(a, 'B'); } else { dot(a, 'B'); dot(b, 'M'); }
    return r.join('');
  });
  const mail = [
    'kkkkkkkkkkkkkkkk',
    'kkLLLLLLLLLLLLkk',
    'kWkLLLLLLLLLLkWk',
    'kWWkLLLLLLLLkWWk',
    'kWWWkLLLLLLkWWWk',
    'kWWWWkLLLLkWWWWk',
    'kWWWWWkkkkWWWWWk',
    'kWWWWWWWWWWWWWWk',
    'kWWWWWWWWWWWWWWk',
    'kLWWWWWWWWWWWWLk',
    'kLLLLLLLLLLLLLLk',
    'kkkkkkkkkkkkkkkk'
  ];
  const playTop = [
    '..kk............',
    '..knkk..........',
    '..knnnkk........',
    '..knnnnnkk......',
    '..knNnnnnnkk....',
    '..knnnnnnnnnkk..',
    '..knnnnnnnnnnnk.'
  ];
  const play = playTop.concat(vflip(playTop.slice(0, 6)).map(r => r.replace(/n/g, 'E').replace('knE', 'knn')));
  Object.assign(ICONS, {
    mail,
    mailHeart: mail.map((r, y) => ({
      3: 'kWWkLkkLLkkLkWWk', 4: 'kWWWkMQkkMMkWWWk', 5: 'kWWWkMMMMMMkWWWk',
      6: 'kWWWWkMMMMkWWWWk', 7: 'kWWWWWkMMkWWWWWk', 8: 'kWWWWWWkkWWWWWWk'
    })[y] || r),
    tent: [
      '.......kk.......',
      '......kRRk......',
      '.....kRRoRk.....',
      '.....kRRoRk.....',
      '....kRRRooRk....',
      '....kRRRooRk....',
      '...kRRRkkoRRk...',
      '...kRRkddkoRk...',
      '..kRRRkddkoRRk..',
      '..kRRkdddDkoRk..',
      '.kRRRkddDDkoRRk.',
      '.kRRkdddDDDkoRk.',
      'kkkkkkkkkkkkkkkk'
    ],
    bow: [
      '.....kkk........',
      '....kDDLk.......',
      '...kDk.Lk.......',
      '..kDk..Lk.......',
      '..kDk..Lk.......',
      '.kDk...Lk.......',
      '.kDk...Lk....kk.',
      'kMDTTTTTTTTTTTWk',
      '.kDk...Lk....kk.',
      '.kDk...Lk.......',
      '..kDk..Lk.......',
      '..kDk..Lk.......',
      '...kDk.Lk.......',
      '....kDDLk.......',
      '.....kkk........'
    ],
    handshake: [
      'kkkk........kkkk',
      'kBBk........kMMk',
      'kBBkkkkkkkkkkMMk',
      'kBBkTTTTTTTTkMMk',
      'kBBkTkTkTkTTkMMk',
      'kBBkTTTTTTTTkMMk',
      'kBBkkTkTkTktkMMk',
      'kBBk.kkkkkkkkMMk',
      'kbbk........kmmk',
      'kkkk........kkkk'
    ],
    faceSmile: put(put(FACE, [[4, 5], [4, 6], [11, 5], [11, 6], [3, 8], [12, 8], [4, 9], [11, 9], [5, 10], [6, 10], [7, 10], [8, 10], [9, 10], [10, 10]], 'k'), [[5, 9], [6, 9], [7, 9], [8, 9], [9, 9], [10, 9]], 'M'),
    faceAngry: put(put(FACE, [[3, 4], [4, 5], [12, 4], [11, 5], [5, 6], [5, 7], [10, 6], [10, 7], [5, 10], [6, 10], [7, 10], [8, 10], [9, 10], [10, 10]], 'k'), [[2, 8], [3, 8], [12, 8], [13, 8]], 'R'),
    shoe: [
      '.....kkkk.......',
      '....kMMMMk......',
      '....kMWWMk......',
      '....kMMMMkkk....',
      '...kMMWMMMMMkk..',
      '..kMMMMWMMMMMMk.',
      '.kMMMMMMWMMMMMMk',
      'kMMMMMMMMMMMMMMk',
      'kWWWWWWWWWWWWWWk',
      'kLLLLLLLLLLLLLLk',
      '.kkkkkkkkkkkkkk.'
    ],
    chopsticks,
    dna,
    cone: [
      '.......kk.......',
      '......kRRk......',
      '......kRRk......',
      '.....kWWWWk.....',
      '.....kWWWWk.....',
      '....kRRRRRRk....',
      '....kRRRRRRk....',
      '...kWWWWWWWWk...',
      '...kWWWWWWWWk...',
      '..kRRRRRRRRRRk..',
      '..kRRRRRRRRRRk..',
      '.kkkkkkkkkkkkkk.',
      '.kGGGGGGGGGGGGk.',
      '.kkkkkkkkkkkkkk.'
    ],
    wizard: [
      '.........kk.....',
      '........kPPk....',
      '.......kPPk.....',
      '......kPPPk.....',
      '......kPhPk.....',
      '.....kPPPPPk....',
      '.....kPPPhPk....',
      '....kPPhPPPPk...',
      '....kPPPPPPPk...',
      '...kPPPPPPPPPk..',
      '.kkkhhhhhhhhhkk.',
      'kPPPPPPPPPPPPPPk',
      '.kkkkkkkkkkkkkk.'
    ],
    invader: [
      '....k.....k.....',
      '...kvk...kvk....',
      '....kvkkkvk.....',
      '...kvvvvvvvk....',
      '..kvvkvvvkvvk...',
      '.kvvvvvvvvvvvk..',
      '.kvkvvvvvvvkvk..',
      '.kvkvkkkkkvkvk..',
      '..k.kvvkvvk.k...',
      '.....kk.kk......'
    ],
    tag: [
      '...kkkkkkkkkkkk.',
      '..khhhhhhhhhhhk.',
      '.khhkkhhhhhhhhk.',
      'khhhkkhhhhhhhhk.',
      '.khhhhhhhhhhhYk.',
      '..kYYYYYYYYYYYk.',
      '...kkkkkkkkkkkk.'
    ],
    brain: [
      '....kkkkkkk.....',
      '..kkqqqqqqqkk...',
      '.kqqQqqkqqQqqk..',
      'kqqkqqqkqqqkqqk.',
      'kqQqqkqqkqqqqqk.',
      'kqqqqkqqkqQqkqk.',
      'kqkqqqqkqqqkqqk.',
      '.kqqkqqkqqkqqk..',
      '..kkqqqkqqqkk...',
      '....kkkkkkk.....'
    ],
    party: [
      '..h.....M...i...',
      '.....i.....h....',
      '...M.....k......',
      '........kk..i...',
      '.h....kkhhk.....',
      '.....khhYk..M...',
      '....khhYMk......',
      '...khYMhk...h...',
      '..khYMhk........',
      '..kYMhYk..i.....',
      '.kYhhYk.........',
      '.kMYYk..........',
      'kYYkk...........',
      'kkk.............'
    ],
    calendar: [
      '...kk......kk...',
      '.kkLLkkkkkkLLkk.',
      '.kMMMMMMMMMMMMk.',
      '.kMMMMMMMMMMMMk.',
      '.kkkkkkkkkkkkkk.',
      '.kWWWWWWWWWWWWk.',
      '.kWkWkWkWkWkWWk.',
      '.kWWWWWWWWWWWWk.',
      '.kWkWkWkWkWkWWk.',
      '.kWWWWWWWWWWWWk.',
      '.kWkWkWkWMMWWWk.',
      '.kWWWWWWWWWWWWk.',
      '.kLLLLLLLLLLLLk.',
      '.kkkkkkkkkkkkkk.'
    ],
    numbers: tile('B', 1, 2, 3, 4),
    letters: tile('P', 'A', 'B', 'C', 'D'),
    play,
    playBack: hflip(play),
    card: [
      '..kkkkkkkkkkkk..',
      '..kWWWWWWWWWWk..',
      '..kWMWWWWWWWWk..',
      '..kWWWWWWWWWWk..',
      '..kWWWWMMWWWWk..',
      '..kWWWMMMMWWWk..',
      '..kWWMMMMMMWWk..',
      '..kWWWMMMMWWWk..',
      '..kWWWWMMWWWWk..',
      '..kWWWWWWWWWWk..',
      '..kWWWWWWWWMWk..',
      '..kLLLLLLLLLLk..',
      '..kkkkkkkkkkkk..'
    ],
    divide: [
      '......kkkk......',
      '......kiik......',
      '......kiik......',
      '......kkkk......',
      '.kkkkkkkkkkkkkk.',
      '.kIiiiiiiiiiiik.',
      '.kiiiiiiiiiiiBk.',
      '.kkkkkkkkkkkkkk.',
      '......kkkk......',
      '......kiik......',
      '......kiBk......',
      '......kkkk......'
    ],
    pawn: [
      '......kkkk......',
      '.....kGGGGk.....',
      '.....kGLGGk.....',
      '.....kGGGGk.....',
      '......kkkk......',
      '.....kGGGGk.....',
      '......kGGk......',
      '......kGGk......',
      '.....kGGGGk.....',
      '....kGGGGGGk....',
      '...kkkkkkkkkk...',
      '...kGGGGGGGGk...',
      '...kkkkkkkkkk...'
    ],
    ball: [
      '.....kkkkkk.....',
      '...kkWWWWLLkk...',
      '..kWWWkkWWWLLk..',
      '.kWWWkWWkWWWLLk.',
      '.kWWkWWWWkWWWLk.',
      'kWWkWWWWWWkkkkLk',
      'kWkWWWWWWkWWWWLk',
      'kWkWWWWWkWWWWWLk',
      'kkkkWWWWkWWWWWLk',
      'kWWWkkWWkWWWWLLk',
      '.kWWWWkkWkWWWLk.',
      '.kWWWWWWkkkLLLk.',
      '..kLWWWWWWLLLk..',
      '...kkLLLLLLkk...',
      '.....kkkkkk.....'
    ],
    tree: [
      '.....kkkkkk.....',
      '...kknnnnnnkk...',
      '..knnNnnnnnnEk..',
      '.knnNnnnnnnnnEk.',
      '.knnnnnnnnnnEEk.',
      'kEnnnnnnnnnnnEEk',
      'kEnnnnnnnnnnEEEk',
      '.kEEnnnnnnEEEEk.',
      '..kkEEEEEEEEkk..',
      '....kkkDDkkk....',
      '......kDdk......',
      '......kDdk......',
      '.....kDDddk.....',
      '....kkkkkkkk....'
    ],
    save: [
      'kkkkkkkkkkkkkk..',
      'kBBkWWWWWWkBBBk.',
      'kBBkWWWWkWkBBBBk',
      'kBBkWWWWkWkBBBBk',
      'kBBkWWWWWWkBBBBk',
      'kBBBkkkkkkBBBBBk',
      'kBBBBBBBBBBBBBBk',
      'kBBkkkkkkkkkkBBk',
      'kBkLLLLLLLLLLkBk',
      'kBkLkkkkkkkkLkBk',
      'kBkLLLLLLLLLLkBk',
      'kBkLkkkkkLLLLkBk',
      'kBkLLLLLLLLLLkBk',
      'kkkkkkkkkkkkkkkk'
    ],
    trash: [
      '......kkkk......',
      '.kkkkkkLLkkkkkk.',
      '.kLLLLLLLLLLLLk.',
      '.kkkkkkkkkkkkkk.',
      '..kGLGLGLGLGLk..',
      '..kGLGLGLGLGLk..',
      '..kGLGLGLGLGLk..',
      '..kGLGLGLGLGLk..',
      '..kGLGLGLGLGLk..',
      '..kGLGLGLGLGLk..',
      '...kGGGGGGGGk...',
      '...kkkkkkkkkk...'
    ],
    person: [
      '.....kkkkkk.....',
      '....kTTTTTTk....',
      '....kTTTTTTk....',
      '....kTTTTTTk....',
      '....ktTTTTtk....',
      '.....kkkkkk.....',
      '...kkBBBBBBkk...',
      '..kBBBBBBBBBBk..',
      '.kBiBBBBBBBBBBk.',
      '.kBiBBBBBBBBBbk.',
      '.kBBBBBBBBBBBbk.',
      '.kkkkkkkkkkkkkk.'
    ],
    cart: [
      'kk..............',
      'kLk.............',
      '.kLkkkkkkkkkkkk.',
      '..kLWWWWWWWWWWk.',
      '..kLWkWkWkWkWLk.',
      '...kLWWWWWWWWk..',
      '...kLWkWkWkWLk..',
      '....kLLLLLLLLk..',
      '....kkkkkkkkkk..',
      '.....kLLLLLLLk..',
      '.....kkkkkkkkk..',
      '.....kGk...kGk..',
      '.....kkk...kkk..'
    ],
    chart: [
      'kk..............',
      'kLk.........kkk.',
      'kLk........knnk.',
      'kLk.......knnnk.',
      'kLk......knnkk..',
      'kLk.k...knnk....',
      'kLkkNk.knnk.....',
      'kLknnNkknk......',
      'kLkknnnnk.......',
      'kLk.kknk........',
      'kLk...k.........',
      'kLkkkkkkkkkkkkkk',
      'kLLLLLLLLLLLLLLk',
      'kkkkkkkkkkkkkkkk'
    ]
  });

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
    '🪓': 'axe', '🎒': 'bag', '🗡': 'dagger', '📜': 'scroll',
    // 두 번째 묶음
    '✋': 'hand', '👋': 'hand', '🖐': 'hand', '🔄': 'refresh', '🔁': 'refresh', '🔃': 'refresh',
    '🌊': 'wave', '💨': 'dash', '🌍': 'globe', '🌎': 'globe', '🌏': 'globe', '🗺': 'globe',
    '⚖': 'scale', '🌀': 'swirl', '🎨': 'palette', '🌱': 'sprout', '🌿': 'sprout',
    '🏠': 'house', '🏡': 'house', '🏫': 'house', '🪨': 'rock', '⬆': 'up', '🔼': 'up',
    '🔷': 'diamond', '🔹': 'diamond', '💢': 'anger', '💤': 'sleep', '🐾': 'paw',
    '📋': 'clipboard', '🏁': 'flagCheck', '🏳': 'flag', '🚩': 'flagRed', '📚': 'books', '📖': 'books',
    '🚀': 'rocket', '🥈': 'medalSilver', '🥉': 'medalBronze', '⚙': 'gear', '🔍': 'search', '🔎': 'search',
    '🧲': 'magnet', '🎤': 'mic', '🕯': 'candle', '💡': 'bulb', '💣': 'bomb', '🌙': 'moon', '🌑': 'moonDark',
    '🎶': 'music', '🎵': 'music', '🥚': 'egg', '➕': 'plus',
    '💚': 'heartGreen', '💙': 'heartBlue', '💜': 'heartPurple',
    '🔴': 'dotRed', '🟢': 'dotGreen', '🔵': 'dotBlue', '🟡': 'dotYellow', '🟣': 'dotPurple',
    '🟠': 'dotOrange', '⚪': 'dotWhite', '⚫': 'dotBlack',
    // 세 번째 묶음 (화면에 자주 보이는 것)
    '💌': 'mailHeart', '📬': 'mail', '📤': 'mail', '📥': 'mail', '📨': 'mail', '📮': 'mail', '✉': 'mail', '📧': 'mail',
    '⛺': 'tent', '🙋': 'hand', '🏹': 'bow', '🤝': 'handshake', '😤': 'faceAngry', '😠': 'faceAngry',
    '😄': 'faceSmile', '😀': 'faceSmile', '😁': 'faceSmile', '🙂': 'faceSmile', '😊': 'faceSmile', '😆': 'faceSmile',
    '🏃': 'shoe', '👟': 'shoe', '🥢': 'chopsticks', '📑': 'clipboard', '🧬': 'dna', '🚧': 'cone', '💫': 'sparkle',
    '🧙': 'wizard', '👾': 'invader', '🖌': 'pencil', '🏷': 'tag', '🧠': 'brain', '🎉': 'party', '🎊': 'party',
    '📅': 'calendar', '🗓': 'calendar', '📆': 'calendar', '🔢': 'numbers', '🔤': 'letters', '🔠': 'letters',
    '▶': 'play', '⏩': 'play', '⏭': 'play', '◀': 'playBack', '⏪': 'playBack', '⏮': 'playBack',
    '🃏': 'card', '➗': 'divide', '♟': 'pawn', '🏐': 'ball', '⤴': 'up', '🌳': 'tree', '🌲': 'tree',
    '💾': 'save', '🗑': 'trash', '👤': 'person', '🧍': 'person', '👨': 'person', '👦': 'person', '👧': 'person', '🧑': 'person',
    '🛒': 'cart', '📈': 'chart'
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
  // 아이콘 전부 숨기기 스위치 (2026-11-13 사용자 요청: "아이콘 다 빼봐, 삭제하지는 말고")
  //   true면 이모지·도트 아이콘(.pxi)·index.html의 픽셀 아이콘(.px-ico: 직업·자물쇠 등)을 화면에서만 감춤. 그림·연결표·코드는 그대로
  //   다시 보이게 하려면 false로 바꾸면 됨. 주소에 ?icons=1을 붙이면 이 스위치를 무시하고 예전처럼 보여 줌
  let HIDE_ALL = true;
  try { if (/[?&]icons=1/.test(location.search)) HIDE_ALL = false; } catch (e) { }

  // ── 스타일: 아이콘마다 class 하나 ──
  let css = '.pxi{display:inline-block;width:1.15em;height:1.15em;vertical-align:-0.2em;line-height:1.15em;'
    + 'background:no-repeat center/contain;image-rendering:pixelated;color:transparent!important;-webkit-text-fill-color:transparent!important;'
    + 'text-shadow:none!important;overflow:hidden;white-space:nowrap;text-indent:-99em;font-style:normal}'
    + '.pxe-x{display:none!important}'
    + (HIDE_ALL ? '.pxi,.px-ico{display:none!important}' : '');
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
    const hideRaw = HIDE_ALL || nextToText(node);
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

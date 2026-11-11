// 직업 아이콘 (16x16: 14x14 그림 + 자동 외곽선 1px)
// 빌드: node ~/.claude/skills/pxl-pixel-art/bin/pxl.js build tools/job-icons/job-icons.px.js
pal({
  k: "#2a1a10",
  w: "#ffffff", s: "#d6dde8", S: "#8e98a8",
  o: "#c9853f", O: "#8a5a2b",
  y: "#ffd23f", Y: "#d9a514",
  r: "#ef4a4f", R: "#a8283a",
  b: "#7cc7ff", B: "#3b82f6", N: "#1e4fa8",
  p: "#c39bff", P: "#7c3aed",
  g: "#6ee7a0", G: "#22a05a",
  f: "#ff9a3c", F: "#e25822",
  c: "#f4ecd6", C: "#c8b890",
  i: "#e6f8ff", I: "#7fd0ff",
  m: "#8ff5d6", M: "#22b8a0",
  e: "#7dff9a",
})
const O = { w: 14, h: 14, outline: "k" }

sprite("warrior", O, `
  ............ws
  ...........wsS
  ..........wssS
  .........wssS.
  ........wssS..
  .......wssS...
  ......wssS....
  ..y..wssS.....
  ..yywssS......
  ...yYsS.......
  ...rrYY.......
  ..rR..yY......
  .rR...........
  yY............`)

sprite("rogue", O, `
  ..............
  .w..........w.
  .sw........ws.
  ..sw......ws..
  ...sw....ws...
  ....sw..ws....
  .....swws.....
  .....pyyp.....
  ....O.pp.O....
  ...o......o...
  ..O........O..
  .p..........p.
  ..............
  ..............`)

sprite("mage", O, `
  .........pp...
  ........pwpp..
  .......pwpppP.
  .......pppppP.
  ........ppPP..
  .......y.PP...
  ......oy......
  .....oO.......
  ....oO........
  ...oO.........
  ..oO..........
  .oO...........
  oO............
  O.............`)

sprite("healer", O, `
  ..............
  .....wggG.....
  .....gggG.....
  .....gggG.....
  .....gggG.....
  .wgggggggggG..
  .gggggggggggG.
  .gggggggggggG.
  ..GGGGgggGGGG.
  .....gggG.....
  .....gggG.....
  .....gggG.....
  .....GGGG.....
  ..............`)

sprite("archer", O, `
  .......oS.....
  ......oO.S....
  .....oO...S...
  ....oO.....S..
  ...oO.......S.
  ...oO.......S.
  rr.oO.......w.
  .rrssoooooooww
  rr.oO.......w.
  ...oO.......S.
  ...oO.......S.
  ....oO.....S..
  .....oO...S...
  ......oO.S....`)

sprite("knight", { ...O, mx: true }, `
  .ssssss
  sNBBBBB
  sNbBBBy
  sNBBBBy
  sNByyyy
  sNByyyy
  sNBBBBy
  sNBBBBy
  .sNBBBy
  .sNBBBB
  ..sNBBB
  ...sNBB
  ....sNB
  .....ss`)

sprite("lancer", O, `
  ...........sww
  ..........swwS
  .........swwS.
  .........wwS..
  ........yYS...
  .......yY.....
  ......oOrr....
  .....oO.rR....
  ....oO..R.....
  ...oO.........
  ..oO..........
  .oO...........
  oO............
  O.............`)

sprite("sniper", { w: 13, h: 13, outline: "k" },
  ring(6, 6, 4, "r"),
  vline(6, 0, 4, "w"), vline(6, 9, 4, "w"), hline(0, 6, 4, "w"), hline(9, 6, 4, "w"),
  px(6, 6, "r"))

sprite("frost", { w: 13, h: 13, outline: "k" },
  vline(6, 0, 13, "I"), hline(0, 6, 13, "I"),
  line(2, 2, 10, 10, "I"), line(2, 10, 10, 2, "I"),
  px(5, 1, "I"), px(7, 1, "I"), px(5, 11, "I"), px(7, 11, "I"),
  px(1, 5, "I"), px(1, 7, "I"), px(11, 5, "I"), px(11, 7, "I"),
  vline(6, 1, 11, "i"), hline(1, 6, 11, "i"),
  px(5, 5, "w"), px(6, 5, "w"), px(7, 5, "w"), px(5, 6, "w"), px(6, 6, "w"), px(7, 6, "w"), px(5, 7, "w"), px(6, 7, "w"), px(7, 7, "w"))

sprite("curse", { ...O, mx: true }, `
  .......
  ...cccc
  .cccccc
  ccccccc
  ccccccc
  cckkkcc
  ckkekcc
  cckkkcc
  Cccccck
  .Cccccc
  ..CcCcC
  ..ckckc
  ..CCCCC
  .......`)

sprite("bard", O, `
  ....wyyyyyyyy.
  ....yYYYYYYYY.
  ....y.......y.
  ....y.......y.
  ....y.......y.
  ....y.......y.
  ....y.......y.
  ....y.......y.
  ....y....wyyy.
  ....y...yyyyY.
  .wyyy...yyyY..
  yyyyY.........
  yyyY..........
  ..............`)

sprite("berserker", { ...O, mx: true }, `
  ......r
  .sS...O
  ssss..O
  wssssso
  wssssso
  wssssso
  ssss..O
  .sS...O
  ......O
  ......O
  ......O
  ......O
  .....rr
  .....RR`)

sprite("paladin", { ...O, mx: true }, `
  .......
  .wyYyyy
  .yyYyyy
  .yyYyyb
  .yyYyyb
  .YYYYYY
  ......O
  ......o
  ......o
  ......O
  ......o
  ......O
  .....yy
  .....YY`)

sprite("summoner", O, `
  ....mmmmmm....
  ...mwwmmmmm...
  ..mwmmmmmmmM..
  ..mmmmmmmmmM..
  ..mmkmmmmkmM..
  ..mmkmmmmkmM..
  ..mmmmmmmmmM..
  ..MmmmmmmmMM..
  ...MmmmmmMM...
  ....MmmmmM....
  .....MmmmM....
  ......MmmM....
  .......MMM....
  .........M....`)

sprite("pyro", O, `
  .......F......
  ......FF......
  ......FfF.....
  .....FffF..F..
  ..F..FffF.FF..
  ..FF.FfyfFFfF.
  .FffFFfyffffF.
  .FfffffyyfffF.
  FffffyyyyyyffF
  FfffyywwyyyffF
  FffyywwwwyyffF
  .FfyywwwwyyfF.
  ..FfyyyyyyfF..
  ...FFFFFFFF...`)

sprite("brawler", O, `
  ...rrrrrrr....
  ..rwwrrrrrrr..
  .rwrrrrrrrrRr.
  .rrrrrrrrrrRR.
  rrrrrrrrrrrRR.
  rRRRRrrrrrrRR.
  rrrrrRrrrrrRR.
  rrrrrrRrrrrRR.
  .RrrrrrrrrRRR.
  ..RRRRRRRRRR..
  ..wwwwwwwwww..
  ..ssssssssss..
  ..SSSSSSSSSS..
  ..............`)

sprite("volt", O, `
  .......wyyyY..
  ......wyyyY...
  .....wyyyY....
  ....wyyyY.....
  ...wyyyyyyyY..
  ..yyyyyyyyY...
  ......yyyY....
  .....yyyY.....
  ....yyyY......
  ....yyY.......
  ...yyY........
  ...yY.........
  ..yY..........
  ..Y...........`)

sheet("job_icons", ["warrior", "rogue", "mage", "healer", "archer", "knight", "lancer", "sniper", "frost", "curse", "bard", "berserker", "paladin", "summoner", "pyro", "brawler", "volt"], { pad: 2 })

/* 3D 방 꾸미기 본체. three.js r128 + assets/village-pets.js가 먼저 있어야 함.
 * 쓰는 법: const api = VillageRoom.start(담을 요소, host) → api.pause() / api.resume() / api.dispose()
 * host: { me: { id, name, pet }, owner: { id, name }, canEdit(내 방이면 true),
 *         data: { lv(방 넓이 1~8), wall, floor, skins: ['wall:id', ...], items: [{ u, id, x, z, r, c, p }] },
 *         ca() → 지금 가진 CA, pay(값, 이유) → 냈으면 true, save(data), exit(),
 *         roommates: ['rabbit', ...](방 안을 돌아다니는 다른 펫, 셋까지), hour(시험용 시각, 없으면 실제 시계) }
 * 칸: 1칸 = 1(펫 키와 같음). 방은 가로 W × 세로 D칸, 가운데가 원점, 뒷벽이 -z. 가구는 앞면이 +z를 보게 만들고 r(0~3)만큼 90도씩 돌림.
 * 가구 x·z는 차지하는 칸의 왼쪽 뒤 모서리(0부터). 벽 장식은 뒷벽의 가로 칸(x)만 씀.
 */
(function () {
  const SIZES = [[6, 5], [7, 5], [7, 6], [8, 6], [8, 7], [9, 7], [10, 8], [12, 8]]; // lv 1~8
  const SIZE_PRICE = [0, 3000, 5000, 8000, 12000, 16000, 20000, 25000];            // 그 단계로 넓히는 값 (예전 방 넓히기와 같음)
  const WOOD = '#c99560', DARK = '#8a5a34', WHITE = '#fff8ee', STEEL = '#c9ccd2';

  // ── 가구: build(k, c) — k = 만들기 도구(box·cyl·ball·cone), c = 고른 색 묶음. 바닥 가운데가 (0,0,0)
  // cat: floor(바닥 가구) · rug(깔개) · top(올려놓는 소품) · wall(벽 장식). seat = 앉는 높이, lie = 눕는 높이, surface = 윗면 높이(소품을 올림), light = 켜지는 불
  const CATALOG = [
    { id: 'bed', name: '포근 침대', cat: 'floor', w: 2, d: 3, price: 1500, lie: 0.62, colors: [['#f7b8cf', '#fff3f6'], ['#a9d4f5', '#f1f8ff'], ['#b9e3b0', '#f4fbf0']],
      build(k, c) { k.box(1.9, 0.3, 2.9, WOOD, 0, 0.15, 0); k.rbox(1.8, 0.26, 2.7, WHITE, 0, 0.42, 0.05, 0.1); k.rbox(1.86, 0.2, 1.8, c[0], 0, 0.5, 0.5, 0.09); k.box(1.9, 0.95, 0.14, WOOD, 0, 0.47, -1.4); k.ball(0.32, c[1], -0.42, 0.62, -0.95, 1.2, 0.4, 0.8); k.ball(0.32, c[1], 0.42, 0.62, -0.95, 1.2, 0.4, 0.8); } },
    { id: 'chair', name: '나무 의자', cat: 'floor', w: 1, d: 1, price: 400, seat: 0.5, colors: [[WOOD, '#f2c6a0'], ['#fff8ee', '#ffd1dc'], [DARK, '#9fc9ef']],
      build(k, c) { [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([x, z]) => k.box(0.09, 0.45, 0.09, c[0], x * 0.3, 0.225, z * 0.3)); k.rbox(0.74, 0.11, 0.74, c[1], 0, 0.49, 0, 0.05); k.rbox(0.74, 0.6, 0.1, c[0], 0, 0.83, -0.33, 0.045); } },
    { id: 'stool', name: '통나무 의자', cat: 'floor', w: 1, d: 1, price: 300, seat: 0.4, colors: [['#b9824e', '#ecc28c']],
      build(k, c) { k.cyl(0.34, 0.37, 0.4, c[0], 0, 0.2, 0); k.cyl(0.31, 0.31, 0.03, c[1], 0, 0.41, 0); } },
    { id: 'sofa', name: '말랑 소파', cat: 'floor', w: 2, d: 1, price: 1000, seat: 0.46, colors: [['#d7b8f5', '#efe0ff'], ['#ffc9a8', '#fff0e2'], ['#9fd6c8', '#e6f7f2']],
      build(k, c) { k.rbox(1.9, 0.36, 0.88, c[0], 0, 0.22, 0.02, 0.1); k.rbox(1.9, 0.6, 0.28, c[0], 0, 0.62, -0.3, 0.12); [-1, 1].forEach(s => { k.rbox(0.24, 0.46, 0.88, c[0], s * 0.83, 0.48, 0.02, 0.1); k.rbox(0.72, 0.18, 0.6, c[1], s * 0.37, 0.44, 0.1, 0.08); }); } },
    { id: 'armchair', name: '안락의자', cat: 'floor', w: 1, d: 1, price: 700, seat: 0.44, colors: [['#f2b36a', '#fff0d6'], ['#8fb8e8', '#eaf3ff'], ['#f29aa8', '#ffe9ee']],
      build(k, c) { k.rbox(0.92, 0.34, 0.88, c[0], 0, 0.2, 0.02, 0.1); k.rbox(0.92, 0.64, 0.26, c[0], 0, 0.64, -0.31, 0.12); [-1, 1].forEach(s => k.rbox(0.2, 0.44, 0.88, c[0], s * 0.36, 0.48, 0.02, 0.09)); k.rbox(0.52, 0.16, 0.6, c[1], 0, 0.42, 0.1, 0.07); } },
    { id: 'table', name: '둥근 식탁', cat: 'floor', w: 2, d: 2, price: 900, surface: 0.78, colors: [[WOOD, '#e8c8a0'], [WHITE, '#ffe3ea'], [DARK, '#c99560']],
      build(k, c) { k.cyl(0.95, 0.95, 0.1, c[0], 0, 0.73, 0); k.cyl(0.12, 0.16, 0.68, c[0], 0, 0.34, 0); k.cyl(0.5, 0.56, 0.08, c[0], 0, 0.04, 0); k.cyl(0.8, 0.8, 0.02, c[1], 0, 0.79, 0); } },
    { id: 'desk', name: '공부 책상', cat: 'floor', w: 2, d: 1, price: 900, surface: 0.8, colors: [[WOOD, WHITE], [WHITE, '#bfe0ff'], [DARK, '#e8c8a0']],
      build(k, c) { k.box(1.9, 0.1, 0.86, c[0], 0, 0.75, 0); [-1, 1].forEach(s => k.box(0.1, 0.7, 0.8, c[0], s * 0.86, 0.35, 0)); k.box(0.6, 0.5, 0.78, c[0], 0.56, 0.46, 0); [0.34, 0.58].forEach(y => { k.box(0.5, 0.18, 0.04, c[1], 0.56, y, 0.4); k.ball(0.03, '#f2c53a', 0.56, y, 0.43); }); } },
    { id: 'sidetable', name: '협탁', cat: 'floor', w: 1, d: 1, price: 400, surface: 0.62, colors: [[WOOD, WHITE], [WHITE, '#ffd1dc'], [DARK, '#e8c8a0']],
      build(k, c) { k.box(0.8, 0.58, 0.76, c[0], 0, 0.31, 0); k.box(0.86, 0.06, 0.82, c[0], 0, 0.6, 0); k.box(0.62, 0.2, 0.04, c[1], 0, 0.4, 0.39); k.ball(0.035, '#f2c53a', 0, 0.4, 0.42); } },
    { id: 'bookshelf', name: '책장', cat: 'floor', w: 2, d: 1, price: 1100, colors: [[WOOD], [WHITE], [DARK]],
      build(k, c) { k.box(1.9, 2.0, 0.7, c[0], 0, 1.0, -0.05); const bk = ['#e0685a', '#5b8fd8', '#e8a13a', '#4fae6a', '#b06fc8', '#f29aa8', '#3fb0a8']; [0.3, 0.86, 1.42].forEach((y, r) => { k.box(1.72, 0.46, 0.06, '#5a3a22', 0, y + 0.2, 0.3); for (let i = 0; i < 9; i++) k.box(0.15, 0.3 + ((i * 7 + r * 3) % 4) * 0.035, 0.36, bk[(i + r * 2) % 7], -0.72 + i * 0.18, y + 0.14 + ((i * 7 + r * 3) % 4) * 0.017, 0.2); }); } },
    { id: 'dresser', name: '서랍장', cat: 'floor', w: 2, d: 1, price: 800, surface: 0.92, colors: [[WOOD, '#e8c8a0'], [WHITE, '#d6ecff'], ['#f7c6d0', WHITE]],
      build(k, c) { k.box(1.86, 0.86, 0.8, c[0], 0, 0.45, 0); k.box(1.92, 0.06, 0.86, c[0], 0, 0.9, 0); [0.26, 0.62].forEach(y => [-0.46, 0.46].forEach(x => { k.box(0.82, 0.28, 0.04, c[1], x, y, 0.41); k.ball(0.035, '#f2c53a', x, y, 0.44); })); } },
    { id: 'wardrobe', name: '옷장', cat: 'floor', w: 2, d: 1, price: 1300, colors: [[WOOD, '#e8c8a0'], [WHITE, '#ffe3ea'], [DARK, WOOD]],
      build(k, c) { k.box(1.86, 2.1, 0.82, c[0], 0, 1.05, 0); k.box(1.94, 0.1, 0.9, c[0], 0, 2.12, 0); [-0.46, 0.46].forEach(x => { k.box(0.84, 1.8, 0.04, c[1], x, 1.08, 0.42); k.ball(0.04, '#f2c53a', x - Math.sign(x) * 0.32, 1.1, 0.45); }); } },
    { id: 'tv', name: 'TV 거실장', cat: 'floor', w: 2, d: 1, price: 1400, play: 'tv', colors: [[WOOD, '#2f3440'], [WHITE, '#2f3440']],
      build(k, c) { k.box(1.9, 0.5, 0.7, c[0], 0, 0.25, 0); k.rbox(1.5, 0.9, 0.12, c[1], 0, 1.05, -0.05, 0.05); k.box(1.36, 0.76, 0.02, '#2a3040', 0, 1.05, 0.01); k.box(0.3, 0.12, 0.3, c[1], 0, 0.56, -0.05); [-0.5, 0.5].forEach(x => k.box(0.7, 0.22, 0.03, '#e8c8a0', x, 0.25, 0.36)); } },
    { id: 'floorlamp', name: '키다리 스탠드', cat: 'floor', w: 1, d: 1, price: 600, light: [0, 1.7, 0], colors: [['#56606c', '#fff0b8'], [WOOD, '#ffd9e2'], [WHITE, '#d6f0ff']],
      build(k, c) { k.cyl(0.28, 0.3, 0.06, c[0], 0, 0.03, 0); k.cyl(0.035, 0.035, 1.5, c[0], 0, 0.78, 0); k.cyl(0.2, 0.36, 0.42, c[1], 0, 1.7, 0); } },
    { id: 'plant', name: '큰 화분', cat: 'floor', w: 1, d: 1, price: 500, colors: [['#d9825a', '#4fb85a'], [WHITE, '#63c466'], ['#8fb8e8', '#46a853']],
      build(k, c) { k.cyl(0.3, 0.22, 0.42, c[0], 0, 0.21, 0); k.cyl(0.05, 0.05, 0.6, DARK, 0, 0.7, 0); [[0, 1.25, 0, 0.42], [0.28, 1.0, 0.1, 0.3], [-0.26, 1.05, -0.08, 0.3], [0.05, 0.95, -0.27, 0.26], [-0.05, 1.5, 0.05, 0.28]].forEach(b => k.ball(b[3], c[1], b[0], b[1], b[2])); } },
    { id: 'piano', name: '피아노', cat: 'floor', w: 2, d: 1, price: 2200, play: 'piano', colors: [['#3a3340', WHITE], ['#8a5a34', WHITE], [WHITE, '#3a3340']],
      build(k, c) { k.box(1.86, 1.1, 0.5, c[0], 0, 0.55, -0.2); k.box(1.86, 0.12, 0.4, c[0], 0, 0.68, 0.22); k.box(1.7, 0.03, 0.3, '#fffdf6', 0, 0.75, 0.24); for (let i = 0; i < 10; i++) k.box(0.07, 0.04, 0.18, '#2a2630', -0.72 + i * 0.16, 0.77, 0.19); [-1, 1].forEach(s => k.box(0.1, 0.62, 0.1, c[0], s * 0.86, 0.31, 0.36)); } },
    { id: 'fridge', name: '레트로 냉장고', cat: 'floor', w: 1, d: 1, price: 1300, colors: [['#f29aa8', STEEL], ['#9fd6c8', STEEL], ['#fff3d6', STEEL]],
      build(k, c) { k.rbox(0.86, 1.7, 0.8, c[0], 0, 0.9, 0, 0.14); k.box(0.88, 0.03, 0.03, c[1], 0, 1.2, 0.41); k.box(0.05, 0.36, 0.05, c[1], -0.32, 1.45, 0.43); k.box(0.05, 0.5, 0.05, c[1], -0.32, 0.85, 0.43); k.cyl(0.4, 0.43, 0.06, c[1], 0, 0.03, 0); } },
    { id: 'counter', name: '주방 조리대', cat: 'floor', w: 2, d: 1, price: 1000, surface: 0.92, colors: [[WHITE, '#9fd6c8', STEEL], [WOOD, WHITE, STEEL]],
      build(k, c) { k.box(1.9, 0.84, 0.82, c[0], 0, 0.42, 0); k.box(1.96, 0.08, 0.9, c[1], 0, 0.88, 0); k.box(0.6, 0.02, 0.5, c[2], 0.5, 0.93, 0); k.cyl(0.03, 0.03, 0.3, c[2], 0.5, 1.07, -0.3); [-0.47, 0.47].forEach(x => { k.box(0.84, 0.56, 0.03, c[1], x, 0.42, 0.42); k.ball(0.035, c[2], x + 0.3 * Math.sign(-x), 0.42, 0.45); }); } },
    { id: 'tent', name: '캠핑 텐트', cat: 'floor', w: 2, d: 2, price: 1800, colors: [['#f2a65a', '#fff0d6'], ['#7fb8e8', '#eef6ff'], ['#8fcf7a', '#f2fbe8']],
      build(k, c) { const t = k.cone(1.25, 1.5, c[0], 0, 0.75, 0, 4); t.rotation.y = Math.PI / 4; k.box(0.6, 0.9, 0.04, '#3a3340', 0, 0.45, 0.86); k.box(0.3, 0.9, 0.05, c[1], -0.24, 0.45, 0.88).rotation.z = 0.12; k.box(0.3, 0.9, 0.05, c[1], 0.24, 0.45, 0.88).rotation.z = -0.12; } },
    { id: 'cattower', name: '캣타워', cat: 'floor', w: 1, d: 1, price: 1200, surface: 1.72, colors: [['#e8c8a0', '#f7b8cf'], ['#c9ccd2', '#a9d4f5']],
      build(k, c) { k.box(0.86, 0.08, 0.86, c[0], 0, 0.04, 0); k.cyl(0.09, 0.09, 1.6, '#d9b98a', -0.2, 0.86, -0.2); k.cyl(0.09, 0.09, 0.9, '#d9b98a', 0.24, 0.5, 0.2); k.box(0.56, 0.07, 0.56, c[1], 0.18, 0.96, 0.18); k.box(0.62, 0.07, 0.62, c[1], -0.1, 1.68, -0.1); k.ball(0.07, '#e0685a', 0.42, 0.74, 0.42); } },
    { id: 'aquarium', name: '어항', cat: 'floor', w: 2, d: 1, price: 1600, colors: [[WOOD, '#8fd8f5'], [WHITE, '#8fd8f5']],
      build(k, c) { k.box(1.86, 0.7, 0.8, c[0], 0, 0.35, 0); k.box(1.7, 0.8, 0.66, c[1], 0, 1.12, 0); k.box(1.76, 0.06, 0.72, '#56606c', 0, 1.55, 0); k.box(1.6, 0.1, 0.56, '#f1dfae', 0, 0.78, 0); [['#f2913a', -0.4, 1.2, 0.34], ['#f2c53a', 0.3, 1.0, 0.34], ['#e0685a', 0.55, 1.3, 0.34]].forEach(f => k.ball(0.08, f[0], f[1], f[2], f[3], 1.5, 0.9, 0.3)); k.ball(0.1, '#4fb85a', -0.6, 0.92, 0.2, 0.5, 2, 0.5); } },
    { id: 'toybox', name: '장난감 상자', cat: 'floor', w: 1, d: 1, price: 500, colors: [['#f29aa8', '#ffd23a'], ['#8fb8e8', '#ff9db8'], ['#9fd6c8', '#f2913a']],
      build(k, c) { k.rbox(0.86, 0.5, 0.7, c[0], 0, 0.25, 0, 0.07); k.rbox(0.9, 0.1, 0.74, c[1], 0, 0.52, -0.02, 0.045); k.ball(0.16, '#ffd23a', -0.2, 0.66, 0.05); k.box(0.22, 0.22, 0.22, '#5b8fd8', 0.2, 0.66, 0.0).rotation.y = 0.5; k.cone(0.12, 0.26, '#e0685a', 0.05, 0.7, -0.2); } },
    { id: 'fireplace', name: '벽난로', cat: 'floor', w: 2, d: 1, price: 2000, light: [0, 0.5, 0.3], colors: [['#d9cfbf', '#8a5a34'], ['#c97a5a', '#fff8ee']],
      build(k, c) { k.box(1.9, 1.3, 0.7, c[0], 0, 0.65, -0.1); k.box(2.0, 0.1, 0.84, c[1], 0, 1.34, -0.06); k.box(0.9, 0.7, 0.3, '#2a2630', 0, 0.38, 0.14); k.box(0.7, 0.14, 0.2, '#6a4326', 0, 0.1, 0.2); k.ball(0.2, '#ff8a3a', 0, 0.3, 0.2, 1, 1.4, 0.7); k.ball(0.12, '#ffd23a', 0, 0.28, 0.24, 1, 1.5, 0.7); } },
    { id: 'arcade', name: '오락기', cat: 'floor', w: 1, d: 1, price: 1700, colors: [['#5b6fd8', '#ffd23a'], ['#e0685a', '#8fd8f5']],
      build(k, c) { k.rbox(0.84, 1.0, 0.8, c[0], 0, 0.5, 0, 0.06); k.rbox(0.84, 0.8, 0.5, c[0], 0, 1.4, -0.15, 0.08); k.box(0.64, 0.5, 0.03, '#1f2a44', 0, 1.42, 0.11); k.box(0.5, 0.36, 0.02, '#7ff0c0', 0, 1.42, 0.13); k.box(0.84, 0.1, 0.4, c[1], 0, 1.03, 0.2); k.cyl(0.03, 0.03, 0.16, '#2a2630', -0.2, 1.14, 0.2); k.ball(0.05, '#e0685a', -0.2, 1.24, 0.2); k.ball(0.045, '#ffd23a', 0.14, 1.1, 0.24); k.ball(0.045, '#4fae6a', 0.28, 1.1, 0.16); } },
    { id: 'bathtub', name: '거품 욕조', cat: 'floor', w: 2, d: 1, price: 1500, colors: [[WHITE, '#bfe6fb'], ['#ffd1dc', '#fff3f6'], ['#bfe8d8', WHITE]],
      build(k, c) { k.rbox(1.9, 0.62, 0.9, c[0], 0, 0.36, 0, 0.2); k.rbox(1.6, 0.1, 0.62, c[1], 0, 0.66, 0, 0.05); [[-0.4, 0.74, 0.1, 0.16], [0.1, 0.76, -0.1, 0.19], [0.5, 0.73, 0.08, 0.14], [-0.1, 0.72, 0.2, 0.12]].forEach(b => k.ball(b[3], WHITE, b[0], b[1], b[2])); k.cyl(0.03, 0.03, 0.3, STEEL, 0.78, 0.85, 0); k.ball(0.05, STEEL, 0.7, 0.98, 0); [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([x, z]) => k.ball(0.08, STEEL, x * 0.7, 0.07, z * 0.3)); } },
    { id: 'vanity', name: '거울 화장대', cat: 'floor', w: 1, d: 1, price: 900, colors: [[WHITE, '#ffd1dc'], [WOOD, WHITE], ['#e6d6ff', WHITE]],
      build(k, c) { k.box(0.86, 0.1, 0.6, c[0], 0, 0.7, -0.05); [-1, 1].forEach(s => k.box(0.08, 0.66, 0.5, c[0], s * 0.38, 0.33, -0.05)); k.box(0.6, 0.16, 0.04, c[1], 0, 0.58, 0.24); const fr = k.cyl(0.33, 0.33, 0.06, c[0], 0, 1.2, -0.3, 24); fr.rotation.x = Math.PI / 2; const gl = k.cyl(0.27, 0.27, 0.02, '#cfeeff', 0, 1.2, -0.26, 24); gl.rotation.x = Math.PI / 2; k.ball(0.05, '#ff9db8', -0.2, 0.8, 0); k.cyl(0.035, 0.035, 0.12, '#b9a0e8', 0.18, 0.81, 0.02); } },
    { id: 'cushion', name: '방석', cat: 'floor', w: 1, d: 1, price: 250, seat: 0.14, colors: [['#ffd23a', '#fff6c8'], ['#f29aa8', '#ffe9ee'], ['#8fcfb8', '#e8f8f2']],
      build(k, c) { k.rbox(0.8, 0.16, 0.8, c[0], 0, 0.08, 0, 0.08); k.ball(0.05, c[1], 0, 0.16, 0, 1, 0.5, 1); } },
    // 깔개
    { id: 'rug_round', name: '둥근 러그', cat: 'rug', w: 2, d: 2, price: 500, colors: [['#ffd1dc', '#fff3f6'], ['#bfe0ff', '#f1f8ff'], ['#ffe9a8', '#fffbe6']],
      build(k, c) { k.cyl(0.98, 0.98, 0.03, c[0], 0, 0.015, 0, 40); k.cyl(0.72, 0.72, 0.034, c[1], 0, 0.018, 0, 40); k.cyl(0.4, 0.4, 0.038, c[0], 0, 0.02, 0, 32); } },
    { id: 'rug_rect', name: '줄무늬 러그', cat: 'rug', w: 3, d: 2, price: 700, colors: [['#f2a65a', '#fff0d6'], ['#8fcfb8', '#f0fbf6'], ['#b9a0e8', '#f4eeff']],
      build(k, c) { k.rbox(2.9, 0.04, 1.9, c[0], 0, 0.016, 0, 0.018); for (let i = 0; i < 5; i++) k.box(0.22, 0.034, 1.9, c[1], -1.1 + i * 0.55, 0.017, 0); } },
    { id: 'rug_star', name: '별 매트', cat: 'rug', w: 2, d: 2, price: 600, colors: [['#5b6fd8', '#ffd23a'], ['#f29aa8', WHITE]],
      build(k, c) { k.box(1.9, 0.03, 1.9, c[0], 0, 0.015, 0); for (let i = 0; i < 5; i++) { const a = i / 5 * 6.283; const p = k.box(0.24, 0.036, 0.7, c[1], Math.sin(a) * 0.3, 0.018, Math.cos(a) * 0.3); p.rotation.y = a; } k.cyl(0.3, 0.3, 0.037, c[1], 0, 0.019, 0, 10); } },
    // 올려놓는 소품
    { id: 'lamp', name: '탁상 스탠드', cat: 'top', w: 1, d: 1, price: 350, light: [0, 0.42, 0], colors: [['#f2c53a', '#fff0b8'], ['#f29aa8', '#ffe3ea'], ['#8fb8e8', '#e6f2ff']],
      build(k, c) { k.cyl(0.14, 0.16, 0.05, c[0], 0, 0.025, 0); k.cyl(0.025, 0.025, 0.3, c[0], 0, 0.19, 0); k.cyl(0.12, 0.22, 0.24, c[1], 0, 0.42, 0); } },
    { id: 'flower', name: '꽃 화분', cat: 'top', w: 1, d: 1, price: 200, colors: [['#d9825a', '#ff7fa6'], [WHITE, '#ffcf3a'], ['#8fb8e8', '#f2473f']],
      build(k, c) { k.cyl(0.14, 0.1, 0.18, c[0], 0, 0.09, 0); [[0, 0.42, 0], [0.1, 0.34, 0.05], [-0.1, 0.36, -0.03]].forEach(p => { k.cyl(0.012, 0.012, p[1] - 0.16, '#4fae4a', p[0], (p[1] + 0.16) / 2, p[2]); k.ball(0.07, c[1], p[0], p[1], p[2], 1, 1.2, 1); }); } },
    { id: 'books', name: '책 더미', cat: 'top', w: 1, d: 1, price: 150, colors: [['#e0685a', '#5b8fd8', '#e8a13a'], ['#b06fc8', '#4fae6a', '#f29aa8']],
      build(k, c) { c.forEach((col, i) => { const b = k.box(0.42 - i * 0.04, 0.08, 0.3, col, 0, 0.04 + i * 0.085, 0); b.rotation.y = i * 0.25 - 0.2; }); } },
    { id: 'teddy', name: '곰 인형', cat: 'top', w: 1, d: 1, price: 400, colors: [['#c99560', '#f2d6b0'], ['#f7b8cf', '#fff3f6'], [WHITE, '#f2d6b0']],
      build(k, c) { k.ball(0.17, c[0], 0, 0.17, 0, 1, 1.05, 0.9); k.ball(0.14, c[0], 0, 0.42, 0.01); [-1, 1].forEach(s => { k.ball(0.055, c[0], s * 0.11, 0.54, 0); k.ball(0.06, c[0], s * 0.17, 0.2, 0.06, 1, 1.5, 1); k.ball(0.065, c[0], s * 0.1, 0.05, 0.12, 1, 0.8, 1.4); k.ball(0.018, '#2a2630', s * 0.05, 0.45, 0.13); }); k.ball(0.055, c[1], 0, 0.39, 0.12, 1.1, 0.8, 0.7); k.ball(0.02, '#2a2630', 0, 0.41, 0.16); } },
    { id: 'globe', name: '지구본', cat: 'top', w: 1, d: 1, price: 450, colors: [['#5b9fe0', '#6cc46a', WOOD]],
      build(k, c) { k.cyl(0.13, 0.15, 0.04, c[2], 0, 0.02, 0); k.cyl(0.02, 0.02, 0.12, c[2], 0, 0.1, 0); k.ball(0.17, c[0], 0, 0.32, 0); [[0.1, 0.36, 0.1, 0.08], [-0.09, 0.3, 0.12, 0.07], [0.02, 0.4, -0.13, 0.07], [-0.12, 0.36, -0.07, 0.06]].forEach(b => k.ball(b[3], c[1], b[0], b[1], b[2], 1, 1, 1)); } },
    { id: 'fishbowl', name: '금붕어 어항', cat: 'top', w: 1, d: 1, price: 400, colors: [['#bfe6fb', '#f2913a']],
      build(k, c) { k.ball(0.2, c[0], 0, 0.2, 0, 1, 0.9, 1); k.cyl(0.12, 0.14, 0.04, '#8fd0f5', 0, 0.37, 0); k.ball(0.06, c[1], 0.04, 0.2, 0.17, 1.4, 0.9, 0.4); k.ball(0.03, c[1], -0.05, 0.2, 0.18, 1, 1.4, 0.3); } },
    { id: 'cake', name: '딸기 케이크', cat: 'top', w: 1, d: 1, price: 300, colors: [[WHITE, '#f2473f', '#ffd1dc'], ['#8a5a34', '#f2473f', '#fff3d6']],
      build(k, c) { k.cyl(0.26, 0.26, 0.02, '#e8e8e8', 0, 0.01, 0); k.cyl(0.2, 0.2, 0.16, c[2], 0, 0.1, 0); k.cyl(0.21, 0.21, 0.05, c[0], 0, 0.2, 0); for (let i = 0; i < 6; i++) { const a = i / 6 * 6.283; k.ball(0.04, c[1], Math.cos(a) * 0.14, 0.25, Math.sin(a) * 0.14, 1, 1.2, 1); } k.ball(0.045, c[1], 0, 0.26, 0, 1, 1.2, 1); } },
    // 벽 장식 (뒷벽에 붙음: z=0이 벽면)
    { id: 'frame', name: '액자', cat: 'wall', w: 1, d: 1, price: 300, colors: [[WOOD, '#bfe6f5', '#6cc46a'], [WHITE, '#ffd9a0', '#f29aa8'], [DARK, '#2f4178', '#fff6a0']],
      build(k, c) { k.box(0.8, 0.64, 0.06, c[0], 0, 0, 0.03); k.box(0.66, 0.5, 0.02, c[1], 0, 0, 0.065); k.ball(0.14, c[2], 0.12, -0.08, 0.07, 1.6, 0.8, 0.15); k.ball(0.07, '#fffbe0', -0.18, 0.12, 0.07, 1, 1, 0.15); } },
    { id: 'clock', name: '벽시계', cat: 'wall', w: 1, d: 1, price: 350, colors: [[WOOD, WHITE], ['#f29aa8', WHITE], ['#5b8fd8', WHITE]],
      build(k, c) { const a = k.cyl(0.32, 0.32, 0.07, c[0], 0, 0, 0.035, 28); a.rotation.x = Math.PI / 2; const b = k.cyl(0.26, 0.26, 0.02, c[1], 0, 0, 0.075, 28); b.rotation.x = Math.PI / 2; k.box(0.03, 0.2, 0.02, '#2a2630', 0, 0.08, 0.09); k.box(0.14, 0.03, 0.02, '#2a2630', 0.06, 0, 0.09); } },
    { id: 'garland', name: '삼각 가랜드', cat: 'wall', w: 3, d: 1, price: 400, colors: [['#f29aa8', '#ffd23a', '#8fd0f5'], ['#b9a0e8', '#9fd6c8', '#ffb68a']],
      build(k, c) { for (let i = 0; i < 7; i++) { const x = -1.2 + i * 0.4, y = 0.3 - Math.sin(i / 6 * Math.PI) * 0.22; const t = k.cone(0.16, 0.3, c[i % 3], x, y - 0.15, 0.03, 3); t.rotation.x = Math.PI; t.scale.z = 0.2; } k.box(2.6, 0.02, 0.02, '#8a5a34', 0, 0.26, 0.02); } },
    { id: 'poster', name: '무지개 포스터', cat: 'wall', w: 1, d: 1, price: 250, colors: [[WHITE, '#bfe6fb']],
      build(k, c) { k.box(0.7, 0.9, 0.02, c[0], 0, 0, 0.012); k.box(0.62, 0.82, 0.01, c[1], 0, 0, 0.025); ['#f2473f', '#ffcf3a', '#4fae6a', '#5b8fd8'].forEach((col, i) => { const r = k.cyl(0.26 - i * 0.05, 0.26 - i * 0.05, 0.012 + i * 0.004, col, 0, -0.1, 0.03, 20); r.rotation.x = Math.PI / 2; }); k.box(0.62, 0.3, 0.03, c[1], 0, -0.26, 0.032); k.ball(0.07, '#fffbe0', -0.2, 0.25, 0.03, 1.5, 0.8, 0.2); } },
    { id: 'mirror', name: '벽 거울', cat: 'wall', w: 1, d: 1, price: 400, colors: [[WOOD, '#cfeeff'], [WHITE, '#cfeeff'], ['#f2c53a', '#cfeeff']],
      build(k, c) { k.rbox(0.66, 1.1, 0.06, c[0], 0, 0, 0.03, 0.03); k.rbox(0.54, 0.98, 0.02, c[1], 0, 0, 0.062, 0.01); k.box(0.06, 0.4, 0.01, WHITE, -0.12, 0.15, 0.075).rotation.z = -0.5; } },
    { id: 'walllamp', name: '별 벽등', cat: 'wall', w: 1, d: 1, price: 450, light: [0, 0, 0.16], colors: [['#f2c53a', '#fff6c8'], ['#f29aa8', '#ffe9ee']],
      build(k, c) { k.box(0.16, 0.16, 0.06, c[0], 0, 0, 0.03); for (let i = 0; i < 5; i++) { const a = i / 5 * 6.283, pt = k.cone(0.1, 0.22, c[1], Math.sin(a) * 0.16, Math.cos(a) * 0.16, 0.14, 4); pt.rotation.z = -a; pt.scale.z = 0.4; } const m = k.cyl(0.17, 0.17, 0.07, c[1], 0, 0, 0.14, 10); m.rotation.x = Math.PI / 2; } },
    { id: 'window', name: '창문', cat: 'wall', w: 2, d: 1, price: 600, glow: true, colors: [[WHITE, '#ffd1dc'], [WOOD, '#bfe0ff']],
      build(k, c) { k.box(1.5, 1.1, 0.08, c[0], 0, 0, 0.04); k.box(0.06, 1.0, 0.1, c[0], 0, 0, 0.05); k.box(1.4, 0.06, 0.1, c[0], 0, 0, 0.05); [-1, 1].forEach(s => k.box(0.34, 1.16, 0.06, c[1], s * 0.68, 0, 0.11)); k.box(1.74, 0.06, 0.1, DARK, 0, 0.62, 0.1); } },
  ];
  const DEF = Object.fromEntries(CATALOG.map(d => [d.id, d]));

  // ── 벽지·바닥: paint(g, s) — s×s 크기의 한 칸 무늬
  const stripes = (a, b, n) => (g, s) => { g.fillStyle = a; g.fillRect(0, 0, s, s); g.fillStyle = b; for (let i = 0; i < n; i++) g.fillRect(i * s / n, 0, s / n / 2, s); };
  const dots = (a, b) => (g, s) => { g.fillStyle = a; g.fillRect(0, 0, s, s); g.fillStyle = b; [[0.25, 0.25], [0.75, 0.75]].forEach(p => { g.beginPath(); g.arc(p[0] * s, p[1] * s, s * 0.09, 0, 6.29); g.fill(); }); };
  const planks = (a, b, line) => (g, s) => { g.fillStyle = a; g.fillRect(0, 0, s, s); for (let r = 0; r < 4; r++) { g.fillStyle = r % 2 ? b : a; g.fillRect(0, r * s / 4, s, s / 4); g.fillStyle = line; g.fillRect(0, r * s / 4, s, 2); g.fillRect(((r * 37) % 100) / 100 * s, r * s / 4, 2, s / 4); } };
  const checker = (a, b) => (g, s) => { g.fillStyle = a; g.fillRect(0, 0, s, s); g.fillStyle = b; g.fillRect(0, 0, s / 2, s / 2); g.fillRect(s / 2, s / 2, s / 2, s / 2); };
  const WALLS = [
    { id: 'cream', name: '크림 벽지', price: 0, paint: (g, s) => { g.fillStyle = '#fff3dc'; g.fillRect(0, 0, s, s); } },
    { id: 'pinkstripe', name: '분홍 줄무늬', price: 800, paint: stripes('#ffe9ee', '#ffd3dd', 4) },
    { id: 'mintdot', name: '민트 물방울', price: 800, paint: dots('#e2f6ee', '#bfe8d8') },
    { id: 'skystripe', name: '하늘 줄무늬', price: 800, paint: stripes('#e6f3ff', '#cfe6fb', 4) },
    { id: 'lemoncheck', name: '레몬 체크', price: 1000, paint: checker('#fff8d6', '#ffefb0') },
    { id: 'woodpanel', name: '원목 판벽', price: 1200, paint: (g, s) => { g.fillStyle = '#e8c9a0'; g.fillRect(0, 0, s, s); g.fillStyle = '#d9b488'; for (let i = 0; i < 4; i++) g.fillRect(i * s / 4, 0, 3, s); } },
    { id: 'brick', name: '벽돌', price: 1200, paint: (g, s) => { g.fillStyle = '#e9d9cc'; g.fillRect(0, 0, s, s); g.fillStyle = '#d58f6f'; for (let r = 0; r < 4; r++) for (let i = -1; i < 2; i++) g.fillRect(i * s / 2 + (r % 2 ? s / 4 : 0) + 2, r * s / 4 + 2, s / 2 - 4, s / 4 - 4); } },
    { id: 'night', name: '별밤', price: 1500, paint: (g, s) => { g.fillStyle = '#35407a'; g.fillRect(0, 0, s, s); g.fillStyle = '#ffe98a'; [[0.2, 0.3, 3], [0.7, 0.2, 2], [0.5, 0.7, 3], [0.85, 0.8, 2], [0.15, 0.85, 2]].forEach(p => { g.beginPath(); g.arc(p[0] * s, p[1] * s, p[2], 0, 6.29); g.fill(); }); } },
  ];
  const FLOORS = [
    { id: 'wood', name: '밝은 나무', price: 0, paint: planks('#e9c79a', '#e2bd8d', '#c99f6c') },
    { id: 'darkwood', name: '짙은 나무', price: 800, paint: planks('#a9764c', '#9d6b43', '#7a5030') },
    { id: 'tile', name: '흰 타일', price: 800, paint: (g, s) => { g.fillStyle = '#f6f6f2'; g.fillRect(0, 0, s, s); g.strokeStyle = '#d9dbd6'; g.lineWidth = 3; g.strokeRect(0, 0, s / 2, s / 2); g.strokeRect(s / 2, 0, s / 2, s / 2); g.strokeRect(0, s / 2, s / 2, s / 2); g.strokeRect(s / 2, s / 2, s / 2, s / 2); } },
    { id: 'checker', name: '체크 타일', price: 1000, paint: checker('#fff6ea', '#f2c9b0') },
    { id: 'pinkcarpet', name: '분홍 카펫', price: 1000, paint: dots('#ffdbe4', '#ffcbd8') },
    { id: 'tatami', name: '풀빛 돗자리', price: 1200, paint: (g, s) => { g.fillStyle = '#cfe0a0'; g.fillRect(0, 0, s, s); g.fillStyle = '#b9cf88'; for (let i = 0; i < 16; i++) g.fillRect(0, i * s / 16, s, 1); g.fillStyle = '#5a7a3a'; g.fillRect(0, 0, s, 3); g.fillRect(0, 0, 3, s); } },
  ];
  const SKIN = { wall: Object.fromEntries(WALLS.map(w => [w.id, w])), floor: Object.fromEntries(FLOORS.map(w => [w.id, w])) };

  const CSS = `
  .vroom { position: relative; overflow: hidden; background: linear-gradient(#cfe9f7, #f3e7d6); font-family: 'Pretendard', 'Malgun Gothic', system-ui, sans-serif; color: #2f4a35; user-select: none; -webkit-user-select: none; }
  .vroom * { box-sizing: border-box; }
  .vroom canvas.vr-gl { position: absolute; inset: 0; width: 100%; height: 100%; display: block; touch-action: none; }
  .vroom .vr-labels { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
  .vroom .tag { position: absolute; left: 0; top: 0; padding: 2px 9px; border-radius: 999px; background: #3f9a5a; border: 2px solid #2f7a45; color: #fff; font-size: 12px; font-weight: 800; white-space: nowrap; }
  .vroom .tag.say { background: #fff; border-color: #f0b84a; color: #5a4320; }
  .vroom .vr-prompt { position: absolute; left: 0; top: 0; padding: 4px 11px; border-radius: 12px; background: #fff8d8; border: 2px solid #f0c24a; font-size: 13px; font-weight: 800; color: #5a4320; white-space: nowrap; display: none; }
  .vroom .vr-prompt kbd { font: inherit; background: #f0c24a; color: #fff; border-radius: 6px; padding: 0 6px; margin-right: 5px; }
  .vroom .vr-hud { position: absolute; left: 10px; top: 10px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; max-width: calc(100% - 20px); }
  .vroom .pill, .vroom button { font: inherit; font-size: 13px; font-weight: 800; padding: 6px 12px; border-radius: 999px; border: 2px solid #d9c9a8; background: rgba(255, 255, 255, .94); color: #4a3a22; line-height: 1.2; }
  .vroom button { cursor: pointer; }
  .vroom button.on { background: #3f9a5a; border-color: #2f7a45; color: #fff; }
  .vroom button:disabled { opacity: .45; cursor: default; }
  .vroom .vr-acts { position: absolute; right: 12px; bottom: 14px; display: flex; gap: 8px; }
  .vroom .vr-acts button { font-size: 15px; padding: 12px 16px; }
  .vroom .vr-tool { position: absolute; left: 50%; transform: translateX(-50%); bottom: 190px; display: none; gap: 6px; padding: 6px; border-radius: 999px; background: rgba(255, 255, 255, .94); border: 2px solid #d9c9a8; }
  .vroom .vr-panel { position: absolute; left: 8px; right: 8px; bottom: 8px; height: 172px; display: none; flex-direction: column; gap: 6px; padding: 8px; border-radius: 16px; background: rgba(255, 252, 244, .96); border: 2px solid #d9c9a8; }
  .vroom .vr-tabs { display: flex; gap: 6px; align-items: center; }
  .vroom .vr-tabs .sp { flex: 1; }
  .vroom .vr-list { flex: 1; min-height: 0; align-items: stretch; display: flex; gap: 8px; overflow-x: auto; overflow-y: hidden; padding-bottom: 2px; }
  .vroom .vr-card { flex: 0 0 96px; display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 4px; border-radius: 12px; border: 2px solid #e6d9bf; background: #fff; cursor: pointer; }
  .vroom .vr-card img { width: 54px; height: 54px; object-fit: contain; border-radius: 8px; }
  .vroom .vr-card b { font-size: 11px; line-height: 1.15; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
  .vroom .vr-card span { font-size: 11px; font-weight: 800; color: #b9822a; }
  .vroom .vr-card.dim { opacity: .5; }
  .vroom .vr-chips { flex: 0 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 4px; align-content: center; }
  .vroom .vr-chips button { font-size: 11px; padding: 4px 8px; }
  .vroom .vr-card.sel { border-color: #3f9a5a; background: #eefaf0; }
  .vroom .vr-empty { align-self: center; font-size: 13px; font-weight: 700; color: #8a7a5a; padding: 0 12px; }
  .vroom .vr-toast { position: absolute; left: 50%; top: 56px; transform: translateX(-50%); padding: 6px 14px; border-radius: 999px; background: rgba(60, 50, 30, .88); color: #fff; font-size: 13px; font-weight: 800; opacity: 0; transition: opacity .25s; pointer-events: none; white-space: nowrap; }`;
  const HTML = `
  <canvas class="vr-gl" data-v="gl"></canvas>
  <div class="vr-labels" data-v="labels"><div class="vr-prompt" data-v="prompt"></div></div>
  <div class="vr-hud">
    <span class="pill" data-v="title"></span>
    <span class="pill" data-v="caPill">💰 <b data-v="ca">0</b> CA</span>
    <button data-v="decoBtn">🛋️ 꾸미기</button>
    <button data-v="viewBtn">🔄 방 돌리기</button>
    <button data-v="soundBtn">소리: 끔</button>
    <button data-v="exitBtn">🚪 나가기</button>
  </div>
  <div class="vr-toast" data-v="toast"></div>
  <div class="vr-tool" data-v="tool"><button data-v="rotBtn">⟳ 돌리기</button><button data-v="colBtn">🎨 색</button><button data-v="storeBtn">📦 넣기</button></div>
  <div class="vr-acts" data-v="acts"><button data-v="waveBtn">👋 인사</button><button data-v="doBtn">하기</button></div>
  <div class="vr-panel" data-v="panel">
    <div class="vr-tabs"><button data-tab="inv">📦 보관함</button><button data-tab="shop">🛒 가구 상점</button><button data-tab="skin">🧱 벽지·바닥</button><button data-tab="size">📐 방 넓히기</button><span class="sp"></span><button data-v="doneBtn" class="on">✔ 꾸미기 끝</button></div>
    <div class="vr-list" data-v="list"></div>
  </div>`;

  function start(root, host) {
    const T = window.THREE, Pets = window.VillagePets;
    if (!document.getElementById('vroomStyle')) { const st = document.createElement('style'); st.id = 'vroomStyle'; st.textContent = CSS; document.head.appendChild(st); }
    root.classList.add('vroom'); root.innerHTML = HTML;
    const $ = id => root.querySelector('[data-v="' + id + '"]');
    const data = host.data; data.items = (data.items || []).filter(it => it && DEF[it.id]); data.skins = data.skins || [];
    if (!SKIN.wall[data.wall]) data.wall = 'cream'; if (!SKIN.floor[data.floor]) data.floor = 'wood';
    const lvOf = () => Math.max(1, Math.min(8, data.lv || 1));
    let W = SIZES[lvOf() - 1][0], D = SIZES[lvOf() - 1][1];
    let running = true, mode = 'walk', tab = 'inv', shopCat = 'all';

    // ── 장면·빛
    const canvas = $('gl');
    const renderer = new T.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    renderer.shadowMap.enabled = true; renderer.shadowMap.type = T.PCFSoftShadowMap;
    const scene = new T.Scene(), camera = new T.PerspectiveCamera(30, 1, 0.1, 100);
    const hemi = new T.HemisphereLight(0xfffaf0, 0xe8d9c0, 0.68); scene.add(hemi);
    const sun = new T.DirectionalLight(0xfff0d0, 0.42); sun.position.set(-5, 12, 7); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0006; sun.shadow.normalBias = 0.04; scene.add(sun); scene.add(sun.target);
    const lampLights = [0, 1, 2].map(() => { const l = new T.PointLight(0xffd88a, 0, 6, 1.6); scene.add(l); return l; }); // 켜진 스탠드 가운데 셋까지 실제로 방을 비춤
    const grad = new T.DataTexture(new Uint8Array([165, 215, 255]), 3, 1, T.LuminanceFormat); grad.minFilter = grad.magFilter = T.NearestFilter; grad.needsUpdate = true;
    const mats = {}, M = c => mats[c] || (mats[c] = new T.MeshToonMaterial({ color: new T.Color(c), gradientMap: grad }));
    const vcMat = new T.MeshToonMaterial({ vertexColors: true, gradientMap: grad });
    const vcLine = new T.MeshBasicMaterial({ vertexColors: true, side: T.BackSide });
    const PET_LINE = new T.Color(0x5c3f30);
    const glowMat = new T.MeshBasicMaterial({ color: 0xfff3c0 }), haloTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.45, 'rgba(255,255,255,.5)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new T.CanvasTexture(c); })();
    const aoMat = new T.MeshBasicMaterial({ map: haloTex, color: 0x4a3a22, transparent: true, opacity: 0.3, depthWrite: false });
    const texOf = (paint, rx, ry) => { const c = document.createElement('canvas'); c.width = c.height = 128; paint(c.getContext('2d'), 128); const t = new T.CanvasTexture(c); t.wrapS = t.wrapT = T.RepeatWrapping; t.repeat.set(rx, ry); t.anisotropy = renderer.capabilities.getMaxAnisotropy(); return t; };

    // ── 방 (바닥·세 벽·창문 빛·현관 매트)
    const shell = new T.Group(); scene.add(shell);
    const WALL_H = 3.2;
    const wallG = {}; // N(뒷벽)·S(현관 쪽)·W·E → 벽 묶음과 바깥쪽 방향
    function buildShell() {
      while (shell.children.length) shell.remove(shell.children[0]);
      W = SIZES[lvOf() - 1][0]; D = SIZES[lvOf() - 1][1];
      const floor = new T.Mesh(new T.PlaneGeometry(W, D), new T.MeshToonMaterial({ map: texOf(SKIN.floor[data.floor].paint, W, D), gradientMap: grad })); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; shell.add(floor);
      const trim = '#fff8ee', TH = 0.22;
      const side = (name, len, x, z, ry, out) => { // 벽 한 면: 벽지 + 두께 + 걸레받이 (안쪽이 +z를 보게 만들어 돌려 세움)
        const g = new T.Group(), put = (m, px, py, pz) => { m.position.set(px, py, pz); m.receiveShadow = true; g.add(m); return m; };
        put(new T.Mesh(new T.PlaneGeometry(len, WALL_H), new T.MeshToonMaterial({ map: texOf(SKIN.wall[data.wall].paint, len, WALL_H), gradientMap: grad })), 0, WALL_H / 2, 0);
        put(new T.Mesh(new T.BoxGeometry(len + TH * 2, WALL_H, TH), M(trim)), 0, WALL_H / 2, -TH / 2 - 0.002);
        put(new T.Mesh(new T.BoxGeometry(len, 0.2, 0.06), M('#e8d9c0')), 0, 0.1, 0.03);
        if (name === 'S') { put(new T.Mesh(new T.BoxGeometry(1.3, 2.1, 0.08), M('#a06a3c')), 0, 1.05, 0.04); put(new T.Mesh(new T.BoxGeometry(1.5, 2.2, 0.05), M('#8a5a34')), 0, 1.1, 0.02); put(new T.Mesh(new T.SphereGeometry(0.07, 10, 8), M('#f2c53a')), 0.42, 1.0, 0.1); } // 현관문
        g.position.set(x, 0, z); g.rotation.y = ry; shell.add(g); wallG[name] = { g, out };
      };
      side('N', W, 0, -D / 2, 0, [0, -1]); side('S', W, 0, D / 2, Math.PI, [0, 1]);
      side('W', D, -W / 2, 0, Math.PI / 2, [-1, 0]); side('E', D, W / 2, 0, -Math.PI / 2, [1, 0]);
      const base = new T.Mesh(new T.BoxGeometry(W + TH * 2, 0.3, D + TH * 2), M('#d9c3a0')); base.position.y = -0.151; base.receiveShadow = true; shell.add(base);
      const mat = new T.Mesh(new T.BoxGeometry(1.6, 0.03, 0.7), M('#e0685a')); mat.position.set(0, 0.015, D / 2 - 0.4); mat.receiveShadow = true; shell.add(mat); // 현관 매트: 여기서 나감
      const mat2 = new T.Mesh(new T.BoxGeometry(1.3, 0.034, 0.44), M('#fff3d6')); mat2.position.set(0, 0.017, D / 2 - 0.4); shell.add(mat2);
      const sh = new T.Mesh(new T.PlaneGeometry(W + 6, D + 6), new T.MeshBasicMaterial({ map: haloTex, color: 0x6a5a40, transparent: true, opacity: 0.35, depthWrite: false })); sh.rotation.x = -Math.PI / 2; sh.position.y = -0.31; shell.add(sh);
      const far = Math.max(W, D) / 2 + 3;
      Object.assign(sun.shadow.camera, { left: -far, right: far, top: far, bottom: -far, near: 1, far: 40 }); sun.shadow.camera.updateProjectionMatrix();
      fitCamera();
    }
    let zoom = 1, view = 0, viewAng = 0; // view: 보는 방향(90도씩), viewAng: 지금 카메라 각도(부드럽게 따라감)
    function fitCamera() {
      const odd = Math.round(viewAng / (Math.PI / 2)) % 2 !== 0, We = odd ? D : W, De = odd ? W : D, deco = mode === 'deco';
      const asp = Math.max(0.5, canvas.clientWidth / Math.max(1, canvas.clientHeight)), dist = Math.max((We + 2.5) / asp * 0.95, De * 1.55 + 4) * (deco ? 1.08 : 1) * zoom + 3;
      const y = dist * (deco ? 0.95 : 0.74), back = De / 2 + dist * (deco ? 0.52 : 0.72), lz = deco ? 0.6 : -De * 0.05, c = Math.cos(viewAng), sn = Math.sin(viewAng);
      camera.position.set(sn * back, y, c * back); camera.lookAt(sn * lz, 0.7, c * lz);
      Object.keys(wallG).forEach(k => { const w = wallG[k]; w.g.visible = w.out[0] * sn + w.out[1] * c < 0.5; }); // 카메라 쪽 벽은 숨김
      if (typeof itemsG !== 'undefined') itemsG.children.forEach(g => { if (g.userData.cat === 'wall') g.visible = wallG[g.userData.wall || 'N'].g.visible; });
    }
    function turnView() { view++; if (ghost && DEF[ghost.it.id].cat === 'wall' && !ghost.fresh) cancelGhost(); }

    // ── 가구 만들기: 도구로 조각을 쌓은 뒤 한 덩어리 + 테두리로 합침
    const rboxCache = {};
    function roundBox(w, h, d, r) { // 상자의 꼭짓점을 안쪽 상자에서 r만큼 떨어진 곳으로 옮겨 모서리를 둥글림
      const key = [w, h, d, r].join('/'); if (rboxCache[key]) return rboxCache[key];
      r = Math.min(r, w / 2, h / 2, d / 2);
      const g = new T.BoxGeometry(w, h, d, 6, 6, 6), pos = g.attributes.position, nor = g.attributes.normal, v = new T.Vector3(), c = new T.Vector3(), hx = w / 2 - r, hy = h / 2 - r, hz = d / 2 - r;
      for (let i = 0; i < pos.count; i++) {
        v.fromBufferAttribute(pos, i); c.set(Math.max(-hx, Math.min(hx, v.x)), Math.max(-hy, Math.min(hy, v.y)), Math.max(-hz, Math.min(hz, v.z)));
        v.sub(c); if (v.lengthSq() > 1e-12) v.setLength(r); nor.setXYZ(i, v.x / r, v.y / r, v.z / r); v.multiplyScalar(1).add(c); pos.setXYZ(i, v.x, v.y, v.z);
      }
      return (rboxCache[key] = g);
    }
    function kit(g) {
      const put = (m, x, y, z) => { m.position.set(x, y, z); g.add(m); return m; };
      return {
        rbox: (w, h, d, c, x, y, z, r) => put(new T.Mesh(roundBox(w, h, d, r || 0.08), M(c)), x, y, z), // 모서리가 둥근 상자 (이불·쿠션·소파)
        box: (w, h, d, c, x, y, z) => put(new T.Mesh(new T.BoxGeometry(w, h, d), M(c)), x, y, z),
        cyl: (rt, rb, h, c, x, y, z, seg) => put(new T.Mesh(new T.CylinderGeometry(rt, rb, h, seg || 20), M(c)), x, y, z),
        cone: (r, h, c, x, y, z, seg) => put(new T.Mesh(new T.ConeGeometry(r, h, seg || 16), M(c)), x, y, z),
        ball: (r, c, x, y, z, sx = 1, sy = 1, sz = 1) => { const m = put(new T.Mesh(new T.SphereGeometry(1, 16, 11), M(c)), x, y, z); m.scale.set(r * sx, r * sy, r * sz); return m; },
      };
    }
    function buildFurniture(def, ci) {
      const g = new T.Group(), c = def.colors[(ci || 0) % def.colors.length];
      def.build(kit(g), c);
      Pets.merge(T, g, { vertexMaterial: vcMat, outlineMaterial: vcLine, thickness: 0.018, minSize: 0.07, accept: () => true });
      g.traverse(o => { if (o.isMesh) { o.castShadow = !o.userData.noShadow; o.receiveShadow = !o.userData.noShadow && def.cat !== 'wall'; } });
      if (def.cat === 'floor') { // 밑동의 옅은 그늘: 가구가 바닥에 붙어 보이게
        const ao = new T.Mesh(new T.PlaneGeometry(def.w + 0.7, def.d + 0.7), aoMat); ao.rotation.x = -Math.PI / 2; ao.position.y = 0.012; ao.userData.noShadow = true; ao.raycast = () => {}; g.add(ao); // 누르기 판정에서는 뺌
      }
      if (def.glow) { // 창문: 유리(낮엔 하늘빛, 밤엔 어둡게)와 바닥에 떨어지는 햇살
        const glass = new T.Mesh(new T.PlaneGeometry(1.36, 0.98), new T.MeshBasicMaterial({ color: 0xbfe6fb })); glass.position.set(0, 0, 0.012); g.add(glass);
        const beam = new T.Mesh(new T.PlaneGeometry(1.7, 2.3), new T.MeshBasicMaterial({ map: haloTex, color: 0xfff0b0, transparent: true, opacity: 0, depthWrite: false, blending: T.AdditiveBlending })); beam.rotation.x = -Math.PI / 2; beam.position.set(0.25, -1.93, 1.5); beam.raycast = () => {}; g.add(beam);
        g.userData.glass = glass; g.userData.beam = beam;
      }
      if (def.play === 'tv') { const sc = new T.Mesh(new T.PlaneGeometry(1.34, 0.74), new T.MeshBasicMaterial({ color: 0x8fd0f5 })); sc.position.set(0, 1.05, 0.024); sc.visible = false; sc.raycast = () => {}; g.add(sc); g.userData.screen = sc; } // 켜면 보이는 화면
      if (def.light) { // 불빛: 전구 자리의 밝은 공과 번짐
        const b = new T.Mesh(new T.SphereGeometry(0.09, 10, 8), glowMat); b.position.fromArray(def.light); g.add(b);
        const h = new T.Mesh(new T.PlaneGeometry(1.15, 1.15), new T.MeshBasicMaterial({ map: haloTex, color: 0xffd98a, transparent: true, opacity: 0, depthWrite: false, blending: T.AdditiveBlending })); h.position.fromArray(def.light); h.raycast = () => {}; g.add(h);
        g.userData.bulb = b; g.userData.halo = h;
      }
      return g;
    }

    // ── 놓인 가구
    const itemsG = new T.Group(); scene.add(itemsG);
    const meshOf = {}; // u → 묶음
    const dimsOf = (def, r) => (r % 2 ? { w: def.d, d: def.w } : { w: def.w, d: def.d });
    const placed = () => data.items.filter(it => it.p);
    const cellsOf = it => { const def = DEF[it.id], m = dimsOf(def, it.r || 0), out = []; for (let i = 0; i < m.w; i++) for (let j = 0; j < m.d; j++) out.push((it.x + i) + ',' + (it.z + j)); return out; };
    function surfaceAt(x, z, skipU) { // 그 칸에 소품을 올릴 수 있는 윗면 높이 (없으면 null = 바닥, 막힌 가구면 -1)
      let y = null;
      placed().forEach(it => { const def = DEF[it.id]; if (def.cat !== 'floor' || it.u === skipU) return; if (cellsOf(it).includes(x + ',' + z)) y = def.surface != null ? def.surface : -1; });
      return y;
    }
    const wallLen = sd => (sd === 'N' ? W : D);
    const wallPose = (sd, x, w) => sd === 'W' ? { px: -W / 2, pz: -D / 2 + x + w / 2, ry: Math.PI / 2 } : sd === 'E' ? { px: W / 2, pz: -D / 2 + x + w / 2, ry: -Math.PI / 2 } : { px: -W / 2 + x + w / 2, pz: -D / 2, ry: 0 };
    function plateOnWall(g, w) { plate.rotation.set(0, g.rotation.y, 0); plate.scale.set(w, 1.1, 1); plate.position.set(g.position.x + Math.sin(g.rotation.y) * 0.02, 1.95, g.position.z + Math.cos(g.rotation.y) * 0.02); }
    function fits(it, cand) { // cand: { x, z, r, s } — 놓을 수 있는 자리인지
      const def = DEF[it.id], m = dimsOf(def, cand.r || 0);
      if (def.cat === 'wall') { const sd = cand.s || 'N'; if (cand.x < 0 || cand.x + def.w > wallLen(sd)) return false; return !placed().some(o => o.u !== it.u && DEF[o.id].cat === 'wall' && (o.s || 'N') === sd && cand.x < o.x + DEF[o.id].w && o.x < cand.x + def.w); }
      if (cand.x < 0 || cand.z < 0 || cand.x + m.w > W || cand.z + m.d > D) return false;
      const mine = []; for (let i = 0; i < m.w; i++) for (let j = 0; j < m.d; j++) mine.push((cand.x + i) + ',' + (cand.z + j));
      if (def.cat === 'floor' && mine.some(k => { const [cx, cz] = k.split(',').map(Number); return cz === D - 1 && Math.abs(cx + 0.5 - W / 2) < 1; })) return false; // 현관 매트 위는 비움
      if (def.cat === 'top') { const s = surfaceAt(cand.x, cand.z); if (s === -1) return false; return !placed().some(o => o.u !== it.u && DEF[o.id].cat === 'top' && o.x === cand.x && o.z === cand.z); }
      return !placed().some(o => { if (o.u === it.u) return false; const od = DEF[o.id]; if (od.cat !== def.cat && !(def.cat === 'floor' && od.cat === 'top' && surfaceAt(o.x, o.z) == null)) return false; if (od.cat === 'wall') return false; const oc = cellsOf(o); return mine.some(k => oc.includes(k)); });
    }
    function poseItem(it, g, cand) {
      const def = DEF[it.id], c = cand || it, m = dimsOf(def, c.r || 0);
      if (def.cat === 'wall') { const sd = c.s || 'N', wp = wallPose(sd, c.x, def.w); g.position.set(wp.px, 1.95, wp.pz); g.rotation.y = wp.ry; g.userData.wall = sd; if (wallG[sd]) g.visible = wallG[sd].g.visible; return; }
      const y = def.cat === 'top' ? Math.max(0, surfaceAt(c.x, c.z, it.u) || 0) : 0;
      g.position.set(-W / 2 + c.x + m.w / 2, y, -D / 2 + c.z + m.d / 2); g.rotation.y = -(c.r || 0) * Math.PI / 2;
    }
    function syncItems() { // 저장된 목록대로 방 안 가구를 다시 맞춤
      Object.keys(meshOf).forEach(u => { const it = data.items.find(i => String(i.u) === u); if (!it || !it.p || meshOf[u].userData.sig !== it.id + ':' + (it.c || 0)) { itemsG.remove(meshOf[u]); delete meshOf[u]; } });
      placed().forEach(it => { let g = meshOf[it.u]; if (!g) { g = meshOf[it.u] = buildFurniture(DEF[it.id], it.c); g.userData.sig = it.id + ':' + (it.c || 0); g.userData.u = it.u; g.userData.cat = DEF[it.id].cat; itemsG.add(g); } poseItem(it, g); });
      fitCamera();
    }
    const save = () => host.save(data);
    const newU = () => { let u; do { u = Math.floor(Math.random() * 9e5 + 1e5); } while (data.items.some(i => i.u === u)); return u; };

    // ── 내 캐릭터
    const labels = $('labels');
    const pet = Pets.build(T, Pets.SPECS[host.me.pet] ? host.me.pet : 'guest', { material: M, vertexMaterial: vcMat, outline: vcLine, outlineColor: PET_LINE });
    const meG = new T.Group(); meG.add(pet.group); scene.add(meG); meG.traverse(o => { if (o.isMesh) o.castShadow = !o.userData.noShadow; });
    meG.rotation.order = 'YXZ'; // 눕힐 때 몸의 방향을 먼저 돌리고 그 자리에서 뒤로 눕힘
    const me = { x: 0, z: D / 2 - 1.2, face: Math.PI, moving: false, wave: 0, target: null, sit: null, hop: 0 };
    const tag = document.createElement('div'); tag.className = 'tag'; tag.textContent = host.me.name; labels.appendChild(tag);
    const R = 0.3, SPEED = 3.0;
    function blockers() { return placed().filter(it => DEF[it.id].cat === 'floor' || (DEF[it.id].cat === 'top' && surfaceAt(it.x, it.z) == null)).map(it => { const m = dimsOf(DEF[it.id], it.r || 0); return { x0: -W / 2 + it.x + 0.06, x1: -W / 2 + it.x + m.w - 0.06, z0: -D / 2 + it.z + 0.06, z1: -D / 2 + it.z + m.d - 0.06 }; }); }
    let blk = [];
    function stepMe(dx, dz) {
      let x = me.x + dx, z = me.z + dz;
      blk.forEach(b => { const cx = Math.max(b.x0, Math.min(b.x1, x)), cz = Math.max(b.z0, Math.min(b.z1, z)), ex = x - cx, ez = z - cz, d = Math.hypot(ex, ez); if (d < R) { if (d > 1e-4) { x = cx + ex / d * R; z = cz + ez / d * R; } else { x = me.x; z = me.z; } } });
      me.x = Math.max(-W / 2 + R, Math.min(W / 2 - R, x)); me.z = Math.max(-D / 2 + R, Math.min(D / 2 - R + 0.1, z));
    }
    function unstick() { for (let i = 0; i < 40 && blk.some(b => me.x > b.x0 - R && me.x < b.x1 + R && me.z > b.z0 - R && me.z < b.z1 + R); i++) { me.z += 0.25; if (me.z > D / 2 - R) { me.z = D / 2 - R; me.x += 0.3; } } }

    const mates = (host.roommates || []).filter(t => Pets.SPECS[t]).slice(0, 3).map((type, i) => {
      const p = Pets.build(T, type, { material: M, vertexMaterial: vcMat, outline: vcLine, outlineColor: PET_LINE }), g = new T.Group();
      g.add(p.group); g.scale.setScalar(0.82); g.traverse(o => { if (o.isMesh) o.castShadow = !o.userData.noShadow; }); scene.add(g);
      return { p, g, x: -1 + i * 1.2, z: D / 2 - 1.6, face: 0, target: null, wait: 1 + i, moving: false };
    });
    const hitsBlock = (x, z) => blk.some(b => x > b.x0 - R && x < b.x1 + R && z > b.z0 - R && z < b.z1 + R);
    function tickMates(dt, t) {
      mates.forEach(a => {
        a.g.visible = mode !== 'deco'; if (mode === 'deco') return;
        a.moving = false;
        if (hitsBlock(a.x, a.z)) { for (let i = 0; i < 30 && hitsBlock(a.x, a.z); i++) { a.x = (Math.random() - 0.5) * (W - 1); a.z = (Math.random() - 0.5) * (D - 1); } a.target = null; } // 가구가 놓인 자리에 끼면 빈 곳으로
        if (a.wait > 0) a.wait -= dt;
        else if (!a.target) { const tx = (Math.random() - 0.5) * (W - 1), tz = (Math.random() - 0.5) * (D - 1); if (!hitsBlock(tx, tz)) a.target = { x: tx, z: tz, left: 4 }; }
        else {
          const dx = a.target.x - a.x, dz = a.target.z - a.z, d = Math.hypot(dx, dz), sp = Math.min(d, 1.3 * dt), nx = a.x + dx / (d || 1) * sp, nz = a.z + dz / (d || 1) * sp;
          a.target.left -= dt;
          if (d < 0.1 || a.target.left < 0 || hitsBlock(nx, nz)) { a.target = null; a.wait = 1.5 + Math.random() * 4; }
          else { a.x = nx; a.z = nz; a.face = Math.atan2(dx, dz); a.moving = true; }
        }
        a.g.position.set(a.x, 0, a.z); let dd = a.face - a.g.rotation.y; dd = Math.atan2(Math.sin(dd), Math.cos(dd)); a.g.rotation.y += dd * Math.min(1, dt * 10);
        a.p.update(t, { moving: a.moving, wave: false, sit: !a.moving && a.wait > 2.5 });
      });
    }

    // ── 할 수 있는 일
    const center = it => { const m = dimsOf(DEF[it.id], it.r || 0); return { x: -W / 2 + it.x + m.w / 2, z: -D / 2 + it.z + m.d / 2 }; };
    function nearby() {
      if (mode !== 'walk') return null;
      if (me.sit) return { kind: 'stand', label: '일어나기' };
      let best = null, bd = 1.5;
      placed().forEach(it => { const def = DEF[it.id]; if (def.seat == null && def.lie == null && !def.light && !def.play) return; const c = center(it), m = dimsOf(def, it.r || 0), d = Math.max(0, Math.hypot(me.x - c.x, me.z - c.z) - Math.max(m.w, m.d) / 2 + 0.5); if (d < bd) { bd = d; best = it; } });
      if (best) { const def = DEF[best.id]; if (def.play) return { kind: 'play', it: best, label: def.play === 'piano' ? '🎹 연주하기' : tvOn[best.u] ? '📺 TV 끄기' : '📺 TV 켜기' }; return { kind: def.lie != null ? 'lie' : def.seat != null ? 'sit' : 'light', it: best, label: def.lie != null ? '🛏️ 눕기' : def.seat != null ? '🪑 앉기' : (lightOn(best) ? '💡 불 끄기' : '💡 불 켜기') }; }
      if (Math.abs(me.x) < 1 && me.z > D / 2 - 1.0) return { kind: 'exit', label: '🚪 나가기' };
      return null;
    }
    const lightState = {}, tvOn = {}; let night = 0, sayT = 0, sayText = '';
    let audio = null, soundOn = false; // 소리는 기본 끔 (수업 중)
    function tone(f, d, when, type) { if (!soundOn || !audio) return; const o = audio.createOscillator(), g = audio.createGain(), t0 = audio.currentTime + (when || 0); o.type = type || 'triangle'; o.frequency.setValueAtTime(f, t0); g.gain.setValueAtTime(0.14, t0); g.gain.exponentialRampToValueAtTime(0.001, t0 + d); o.connect(g); g.connect(audio.destination); o.start(t0); o.stop(t0 + d + 0.02); }
    const TUNES = [[523, 587, 659, 523, 659, 784], [659, 587, 523, 587, 659, 659], [392, 523, 659, 784, 659, 523]]; let tuneI = 0;
    const lightOn = it => (lightState[it.u] != null ? lightState[it.u] : night > 0.4);
    function interact() {
      const c = nearby(); if (!c) return;
      if (c.kind === 'stand') { const s = me.sit; me.sit = null; me.x = s.ex; me.z = s.ez; blk = blockers(); unstick(); return; }
      if (c.kind === 'exit') return host.exit();
      if (c.kind === 'light') { lightState[c.it.u] = !lightOn(c.it); tone(880, 0.06); return; }
      if (c.kind === 'play') {
        const ctr = center(c.it); me.face = Math.atan2(ctr.x - me.x, ctr.z - me.z);
        if (DEF[c.it.id].play === 'piano') { TUNES[tuneI++ % TUNES.length].forEach((f, i) => tone(f, 0.32, i * 0.22)); sayText = soundOn ? '🎵 🎶 🎵' : '🎵 (소리 버튼을 켜면 들려요)'; sayT = 1.8; me.wave = 1.4; }
        else { tvOn[c.it.u] = !tvOn[c.it.u]; tone(tvOn[c.it.u] ? 660 : 330, 0.1); }
        return;
      }
      const def = DEF[c.it.id], ctr = center(c.it), r = c.it.r || 0, fx = Math.sin(-r * Math.PI / 2), fz = Math.cos(-r * Math.PI / 2); // 가구 앞쪽 방향
      let sx = ctr.x, sz = ctr.z;
      if (c.kind === 'sit' && def.w === 2) { const side = ((me.x - ctr.x) * fz - (me.z - ctr.z) * fx) > 0 ? 0.48 : -0.48; sx += fz * side; sz += -fx * side; }
      me.sit = { x: sx, z: sz, y: c.kind === 'lie' ? def.lie : def.seat, face: -r * Math.PI / 2, lie: c.kind === 'lie', ex: me.x, ez: me.z }; me.target = null;
    }
    function toast(msg) { const t = $('toast'); t.textContent = msg; t.style.opacity = 1; clearTimeout(toast.t); toast.t = setTimeout(() => { t.style.opacity = 0; }, 1600); }

    // ── 꾸미기 모드
    let sel = null, ghost = null; // ghost: { it, x, z, r, ok, fresh(보관함·상점에서 막 꺼냄), drag }
    const plate = new T.Mesh(new T.PlaneGeometry(1, 1), new T.MeshBasicMaterial({ color: 0x4fd06a, transparent: true, opacity: 0.45, depthWrite: false })); plate.rotation.x = -Math.PI / 2; plate.visible = false; scene.add(plate);
    const grid = new T.Group(); grid.visible = false; scene.add(grid);
    function buildGrid() { while (grid.children.length) grid.remove(grid.children[0]); const m = new T.LineBasicMaterial({ color: 0x8a7a5a, transparent: true, opacity: 0.35 }), pts = []; for (let i = 0; i <= W; i++) pts.push(new T.Vector3(-W / 2 + i, 0.012, -D / 2), new T.Vector3(-W / 2 + i, 0.012, D / 2)); for (let j = 0; j <= D; j++) pts.push(new T.Vector3(-W / 2, 0.012, -D / 2 + j), new T.Vector3(W / 2, 0.012, -D / 2 + j)); grid.add(new T.LineSegments(new T.BufferGeometry().setFromPoints(pts), m)); }
    function showGhost() {
      if (!ghost) { plate.visible = false; return; }
      const it = ghost.it, def = DEF[it.id], g = meshOf[it.u], m = dimsOf(def, ghost.r);
      ghost.ok = fits(it, ghost);
      poseItem(it, g, ghost); if (def.cat !== 'wall') g.position.y += 0.12;
      plate.visible = true; plate.material.color.set(ghost.ok ? 0x4fd06a : 0xf0584a);
      if (def.cat === 'wall') plateOnWall(g, def.w);
      else { plate.rotation.set(-Math.PI / 2, 0, 0); plate.scale.set(m.w, m.d, 1); plate.position.set(g.position.x, 0.02, g.position.z); }
    }
    function beginGhost(it, fresh) {
      if (!meshOf[it.u]) { const g = meshOf[it.u] = buildFurniture(DEF[it.id], it.c); g.userData.sig = it.id + ':' + (it.c || 0); g.userData.u = it.u; g.userData.cat = DEF[it.id].cat; itemsG.add(g); }
      const def = DEF[it.id], m = dimsOf(def, it.r || 0);
      if (fresh && placed().length >= 80) { toast('방에는 80개까지 놓을 수 있어요'); return; }
      ghost = { it, x: fresh ? Math.floor((W - m.w) / 2) : it.x, z: fresh ? Math.floor((D - m.d) / 2) : it.z, r: it.r || 0, s: it.s || 'N', fresh, drag: false };
      if (fresh && def.cat === 'wall') { let found = false; ['N', 'W', 'E'].filter(sd => wallG[sd].g.visible).forEach(sd => { for (let x = 0; x <= wallLen(sd) - def.w && !found; x++) if (fits(it, { x, s: sd })) { ghost.x = x; ghost.s = sd; found = true; } }); } // 보이는 벽의 빈자리
      else if (fresh) { let found = false; for (let z = 0; z < D && !found; z++) for (let x = 0; x < W && !found; x++) if (fits(it, { x, z, r: ghost.r })) { ghost.x = x; ghost.z = z; found = true; } } // 빈자리를 찾아 올려 둠
      sel = it; showGhost(); renderTool(); renderList();
    }
    function commitGhost() {
      if (!ghost) return false;
      if (!ghost.ok) { toast('여기에는 놓을 수 없어요'); return false; }
      const it = ghost.it; it.x = ghost.x; it.z = ghost.z; it.r = ghost.r; it.p = 1; if (DEF[it.id].cat === 'wall') it.s = ghost.s; ghost = null; plate.visible = false;
      syncItems(); if (meshOf[it.u]) meshOf[it.u].userData.pop = 1; save(); renderList(); renderTool(); return true;
    }
    function cancelGhost() { if (!ghost) return; const it = ghost.it; ghost = null; plate.visible = false; if (!it.p) sel = null; syncItems(); renderTool(); renderList(); }
    function storeSel() { if (!sel) return; if (ghost) { ghost = null; plate.visible = false; } sel.p = 0; sel = null; syncItems(); save(); renderTool(); renderList(); }
    function rotateSel() { if (!sel || DEF[sel.id].cat === 'wall') return; if (!ghost) beginGhost(sel, false); ghost.r = (ghost.r + 1) % 4; showGhost(); if (ghost.ok && !ghost.fresh) commitGhost(), beginSelect(sel); }
    function colorSel() { if (!sel) return; const n = DEF[sel.id].colors.length; if (n < 2) return toast('이 가구는 색이 하나예요'); sel.c = ((sel.c || 0) + 1) % n; const g = ghost; if (meshOf[sel.u]) { itemsG.remove(meshOf[sel.u]); delete meshOf[sel.u]; } if (g) { const gg = meshOf[sel.u] = buildFurniture(DEF[sel.id], sel.c); gg.userData.sig = sel.id + ':' + sel.c; gg.userData.u = sel.u; gg.userData.cat = DEF[sel.id].cat; itemsG.add(gg); showGhost(); } else syncItems(); thumbs = {}; save(); renderList(); }
    function beginSelect(it) { sel = it; renderTool(); }
    function showSel() { // 고른 가구 밑에 노란 판 (옮기는 중에는 초록·빨강 판이 대신함)
      if (ghost) return; const it = mode === 'deco' ? sel : null;
      if (!it || !it.p || !meshOf[it.u]) { plate.visible = false; return; }
      const def = DEF[it.id], m = dimsOf(def, it.r || 0), g = meshOf[it.u]; plate.visible = true; plate.material.color.set(0xffd23a);
      if (def.cat === 'wall') plateOnWall(g, def.w);
      else { plate.rotation.set(-Math.PI / 2, 0, 0); plate.scale.set(m.w, m.d, 1); plate.position.set(g.position.x, 0.02, g.position.z); }
    }
    function renderTool() { showSel(); const t = $('tool'); t.style.display = mode === 'deco' && sel ? 'flex' : 'none'; if (sel) { $('rotBtn').disabled = DEF[sel.id].cat === 'wall'; $('colBtn').disabled = DEF[sel.id].colors.length < 2; $('storeBtn').textContent = ghost && ghost.fresh ? '✖ 취소' : '📦 넣기'; } }
    function setMode(m) {
      if (m === mode) return; if (ghost) cancelGhost();
      mode = m; sel = null; me.sit = null; me.target = null;
      $('panel').style.display = m === 'deco' ? 'flex' : 'none'; $('acts').style.display = m === 'deco' ? 'none' : 'flex'; $('decoBtn').classList.toggle('on', m === 'deco');
      grid.visible = m === 'deco'; meG.visible = m !== 'deco'; tag.style.display = m === 'deco' ? 'none' : '';
      if (m === 'walk') { blk = blockers(); unstick(); }
      renderTool(); renderList(); fitCamera();
    }

    // ── 목록(보관함·상점·벽지·넓히기): 카드 그림은 작은 화면에 한 번씩 그려 둠
    let thumbs = {}, thumbR = null;
    function thumb(def, ci) {
      const key = def.id + ':' + (ci || 0); if (thumbs[key]) return thumbs[key];
      if (!thumbR) { thumbR = { r: new T.WebGLRenderer({ antialias: true, alpha: true }), s: new T.Scene(), c: new T.PerspectiveCamera(28, 1, 0.1, 50) }; thumbR.r.setSize(112, 112); thumbR.s.add(new T.HemisphereLight(0xffffff, 0xe8d9c0, 0.8)); const d = new T.DirectionalLight(0xfff0d0, 0.45); d.position.set(-2, 4, 3); thumbR.s.add(d); }
      const g = buildFurniture(def, ci); thumbR.s.add(g);
      const size = Math.max(def.w, def.d, def.cat === 'wall' ? 1.2 : 1.6), cy = def.cat === 'wall' ? 0 : 0.7;
      thumbR.c.position.set(size * 1.5, cy + size * 1.5, size * 2.5); thumbR.c.lookAt(0, cy, 0);
      thumbR.r.render(thumbR.s, thumbR.c); thumbs[key] = thumbR.r.domElement.toDataURL(); thumbR.s.remove(g);
      return thumbs[key];
    }
    const skinThumb = sk => { const c = document.createElement('canvas'); c.width = c.height = 56; sk.paint(c.getContext('2d'), 56); return c.toDataURL(); };
    const fmt = n => Number(n).toLocaleString();
    function renderList() {
      $('ca').textContent = fmt(host.ca());
      if (mode !== 'deco') return;
      root.querySelectorAll('[data-tab]').forEach(b => b.classList.toggle('on', b.dataset.tab === tab));
      const list = $('list'); let html = '';
      if (tab === 'inv') {
        const inv = data.items.filter(it => !it.p);
        html = inv.length ? inv.map(it => `<div class="vr-card${sel === it ? ' sel' : ''}" data-inv="${it.u}"><img src="${thumb(DEF[it.id], it.c)}" alt=""><b>${DEF[it.id].name}</b><span>놓기</span></div>`).join('') : '<div class="vr-empty">보관함이 비었어요. 가구 상점에서 사거나, 방의 가구를 눌러 [넣기]로 넣을 수 있어요.</div>';
      } else if (tab === 'shop') {
        const cats = [['all', '전체'], ['floor', '가구'], ['rug', '깔개'], ['top', '소품'], ['wall', '벽 장식']];
        html = `<div class="vr-chips">${cats.map(c => `<button data-cat="${c[0]}"${shopCat === c[0] ? ' class="on"' : ''}>${c[1]}</button>`).join('')}</div>`
          + CATALOG.filter(d => shopCat === 'all' || d.cat === shopCat).map(d => `<div class="vr-card${host.ca() < d.price ? ' dim' : ''}" data-buy="${d.id}"><img src="${thumb(d, 0)}" alt=""><b>${d.name}</b><span>${fmt(d.price)} CA</span></div>`).join('');
      } else if (tab === 'skin') {
        const card = (part, sk) => { const own = sk.price === 0 || data.skins.includes(part + ':' + sk.id), use = data[part] === sk.id; return `<div class="vr-card${use ? ' sel' : ''}${!own && host.ca() < sk.price ? ' dim' : ''}" data-skin="${part}:${sk.id}"><img src="${skinThumb(sk)}" alt=""><b>${sk.name}</b><span>${use ? '쓰는 중' : own ? '바꾸기' : fmt(sk.price) + ' CA'}</span></div>`; };
        html = WALLS.map(s => card('wall', s)).join('') + FLOORS.map(s => card('floor', s)).join('');
      } else {
        const lv = lvOf();
        html = `<div class="vr-empty">지금 방: ${W}×${D}칸 (${lv}단계)</div>` + (lv < 8 ? `<div class="vr-card${host.ca() < SIZE_PRICE[lv] ? ' dim' : ''}" data-size="1" style="flex-basis:150px;justify-content:center"><b>${SIZES[lv][0]}×${SIZES[lv][1]}칸으로 넓히기</b><span>${fmt(SIZE_PRICE[lv])} CA</span></div>` : '<div class="vr-empty">가장 넓은 방이에요!</div>');
      }
      list.innerHTML = html;
    }
    $('list').addEventListener('click', e => {
      const chip = e.target.closest('[data-cat]'); if (chip) { shopCat = chip.dataset.cat; renderList(); return; }
      const c = e.target.closest('.vr-card'); if (!c || !host.canEdit) return;
      if (c.dataset.inv) { if (ghost) cancelGhost(); const it = data.items.find(i => String(i.u) === c.dataset.inv); if (it) beginGhost(it, true); }
      else if (c.dataset.buy) { const d = DEF[c.dataset.buy]; if (!host.pay(d.price, '가구: ' + d.name)) return toast('CA가 모자라요'); if (ghost) cancelGhost(); const it = { u: newU(), id: d.id, x: 0, z: 0, r: 0, c: 0, p: 0 }; data.items.push(it); save(); toast(d.name + '을(를) 샀어요! 놓을 자리를 눌러요'); beginGhost(it, true); }
      else if (c.dataset.skin) { const [part, id] = c.dataset.skin.split(':'), sk = SKIN[part][id], key = part + ':' + id; if (sk.price && !data.skins.includes(key)) { if (!host.pay(sk.price, (part === 'wall' ? '벽지: ' : '바닥: ') + sk.name)) return toast('CA가 모자라요'); data.skins.push(key); } data[part] = id; buildShell(); save(); renderList(); }
      else if (c.dataset.size) { const lv = lvOf(); if (lv >= 8) return; if (!host.pay(SIZE_PRICE[lv], '방 넓히기 ' + (lv + 1) + '단계')) return toast('CA가 모자라요'); if (ghost) cancelGhost(); const ox = Math.floor((SIZES[lv][0] - W) / 2); data.lv = lv + 1; data.items.forEach(it => { if (DEF[it.id].cat !== 'wall' || (it.s || 'N') === 'N') it.x += ox; /* 옆벽 장식은 뒤에서부터 세므로 그대로 */ }); buildShell(); buildGrid(); syncItems(); save(); renderList(); toast('방이 넓어졌어요!'); }
    });
    root.querySelectorAll('[data-tab]').forEach(b => { b.onclick = () => { tab = b.dataset.tab; renderList(); }; });
    $('decoBtn').onclick = () => setMode(mode === 'deco' ? 'walk' : 'deco'); $('doneBtn').onclick = () => setMode('walk');
    $('exitBtn').onclick = () => host.exit(); $('viewBtn').onclick = turnView;
    $('soundBtn').onclick = () => { soundOn = !soundOn; if (soundOn && !audio) { const AC = window.AudioContext || window.webkitAudioContext; if (AC) audio = new AC(); } $('soundBtn').textContent = '소리: ' + (soundOn ? '켬' : '끔'); tone(740, 0.12); };
    $('rotBtn').onclick = rotateSel; $('colBtn').onclick = colorSel; $('storeBtn').onclick = () => { if (ghost && ghost.fresh) cancelGhost(); else storeSel(); };
    $('waveBtn').onclick = () => { me.wave = 1.6; }; $('doBtn').onclick = interact;
    $('title').textContent = '🏠 ' + (host.canEdit ? '내 방' : host.owner.name + '의 방');
    if (!host.canEdit) { $('decoBtn').style.display = 'none'; $('caPill').style.display = 'none'; }

    // ── 누르기·끌기
    const ray = new T.Raycaster(), hit = new T.Vector3(), floorPlane = new T.Plane(new T.Vector3(0, 1, 0), 0), wallPlane = new T.Plane(new T.Vector3(0, 0, 1), 0);
    const aim = e => { const rc = canvas.getBoundingClientRect(); ray.setFromCamera({ x: (e.clientX - rc.left) / rc.width * 2 - 1, y: -((e.clientY - rc.top) / rc.height) * 2 + 1 }, camera); };
    function ghostTo(e) {
      aim(e); const def = DEF[ghost.it.id], m = dimsOf(def, ghost.r);
      if (def.cat === 'wall') { // 보이는 벽 가운데 가리킨 곳과 가장 가까운 벽에 붙임
        let best = null;
        [['N', new T.Plane(new T.Vector3(0, 0, 1), D / 2), h => h.x + W / 2], ['W', new T.Plane(new T.Vector3(1, 0, 0), W / 2), h => h.z + D / 2], ['E', new T.Plane(new T.Vector3(-1, 0, 0), W / 2), h => h.z + D / 2]].forEach(([sd, pl, along]) => {
          if (!wallG[sd].g.visible || !ray.ray.intersectPlane(pl, hit)) return; const a = along(hit), dist = hit.distanceTo(ray.ray.origin);
          if (hit.y < -0.5 || hit.y > WALL_H + 1 || a < -1 || a > wallLen(sd) + 1) return; if (!best || dist < best.dist) best = { sd, a, dist };
        });
        if (!best) return; ghost.s = best.sd; ghost.x = Math.max(0, Math.min(wallLen(best.sd) - def.w, Math.round(best.a - def.w / 2))); ghost.z = -1;
      }
      else { if (!ray.ray.intersectPlane(floorPlane, hit)) return; ghost.x = Math.max(0, Math.min(W - m.w, Math.round(hit.x + W / 2 - m.w / 2))); ghost.z = Math.max(0, Math.min(D - m.d, Math.round(hit.z + D / 2 - m.d / 2))); }
      showGhost();
    }
    function pickItem(e) { aim(e); const hits = ray.intersectObjects(itemsG.children, true); for (const h of hits) { let o = h.object; while (o && o.userData.u == null) o = o.parent; if (o) return data.items.find(i => i.u === o.userData.u) || null; } return null; }
    canvas.addEventListener('pointerdown', e => {
      if (mode === 'walk') { aim(e); if (ray.ray.intersectPlane(floorPlane, hit)) { if (me.sit) interact(); me.target = { x: Math.max(-W / 2 + R, Math.min(W / 2 - R, hit.x)), z: Math.max(-D / 2 + R, Math.min(D / 2 - R, hit.z)), stuck: 0 }; } return; }
      if (!host.canEdit) return;
      try { canvas.setPointerCapture(e.pointerId); } catch (err) {}
      if (ghost && ghost.fresh) { ghostTo(e); ghost.drag = true; return; }
      const it = pickItem(e);
      if (ghost && (!it || it !== ghost.it)) cancelGhost();
      if (it) { beginGhost(it, false); ghost.drag = true; } else { sel = null; renderTool(); }
    });
    canvas.addEventListener('pointermove', e => { if (mode === 'deco' && ghost && (ghost.drag || ghost.fresh)) ghostTo(e); });
    canvas.addEventListener('pointerup', e => {
      if (mode !== 'deco' || !ghost || !ghost.drag) return; ghost.drag = false; const it = ghost.it;
      if (ghost.ok) { commitGhost(); beginSelect(it); } else if (!ghost.fresh) { toast('여기에는 놓을 수 없어요'); cancelGhost(); beginSelect(it); }
    });
    canvas.addEventListener('wheel', e => { e.preventDefault(); zoom = Math.max(0.6, Math.min(1.4, zoom * (e.deltaY > 0 ? 1.07 : 0.94))); fitCamera(); }, { passive: false });
    const keys = {};
    const onKeyDown = e => { if (!running || /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable) return; keys[e.code] = true; if (e.code === 'Space') { e.preventDefault(); me.wave = 1.6; } if (e.code === 'KeyE') interact(); if (e.code === 'KeyR' && mode === 'deco') rotateSel(); if (e.code === 'KeyQ') turnView(); if (e.code.startsWith('Arrow')) e.preventDefault(); };
    const onKeyUp = e => { keys[e.code] = false; };
    window.addEventListener('keydown', onKeyDown); window.addEventListener('keyup', onKeyUp);

    // ── 매 프레임
    const v = new T.Vector3(), prompt = $('prompt');
    let prev = performance.now(), autoPaused = false, lastW = 0, lastH = 0;
    function frame(now) {
      if (!running) return;
      if (!root.isConnected || root.getClientRects().length === 0) { api.pause(); autoPaused = true; const iv = setInterval(() => { if (!root.isConnected || !autoPaused) return clearInterval(iv); if (root.getClientRects().length) { clearInterval(iv); autoPaused = false; api.resume(); } }, 700); return; }
      const t = now / 1000, dt = Math.min(0.05, (now - prev) / 1000); prev = now;
      const w = canvas.clientWidth, h = canvas.clientHeight;
      if (w !== lastW || h !== lastH) { lastW = w; lastH = h; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); fitCamera(); }
      // 시간대: 실제 시계 (host.hour가 있으면 그 값 — 시험판에서 낮·밤 바꿔 보기)
      const d = new Date(), hr = host.hour != null ? host.hour : d.getHours() + d.getMinutes() / 60, tn = hr < 5.5 || hr >= 19.5 ? 1 : hr < 7 || hr >= 17.5 ? 0.45 : 0;
      night += (tn - night) * Math.min(1, dt * 2);
      hemi.intensity = 0.68 - night * 0.26; hemi.color.setRGB(1 - night * 0.3, 0.98 - night * 0.26, 0.94 - night * 0.02); sun.intensity = 0.42 - night * 0.3; sun.color.setRGB(1 - night * 0.35, 0.94 - night * 0.2, 0.82 + night * 0.18);
      root.style.background = night > 0.7 ? 'linear-gradient(#1f2a5a, #3a3a5a)' : night > 0.2 ? 'linear-gradient(#f5b98a, #f3d9c0)' : '';
      let li = 0;
      placed().forEach(it => { const g = meshOf[it.u]; if (!g || !g.userData.bulb) return; const on = lightOn(it); g.userData.halo.material.opacity = on ? 0.35 + night * 0.4 : 0; g.userData.bulb.visible = on; if (on) g.userData.halo.quaternion.copy(g.quaternion).invert().multiply(camera.quaternion); if (on && li < 3) { const L = lampLights[li++]; g.userData.bulb.getWorldPosition(L.position); L.intensity = 0.25 + night * 0.75; } });
      for (; li < 3; li++) lampLights[li].intensity = 0;
      Object.keys(meshOf).forEach(u => { const g = meshOf[u]; // 창문 빛, 놓을 때 통통 튀는 효과
        if (g.userData.screen) { const on = Boolean(tvOn[u]); g.userData.screen.visible = on; if (on) g.userData.screen.material.color.setHSL((t * 0.12) % 1, 0.55, 0.72); }
        if (g.userData.glass) { g.userData.glass.material.color.setRGB(0.75 - night * 0.6, 0.9 - night * 0.68, 0.98 - night * 0.55); g.userData.beam.material.opacity = Math.max(0, 0.34 - night * 0.6); }
        if (g.userData.pop > 0) { g.userData.pop = Math.max(0, g.userData.pop - dt * 3.2); const k = g.userData.pop, sq = Math.sin(k * Math.PI * 2.5) * 0.14 * k; g.scale.set(1 - sq * 0.5, 1 + sq, 1 - sq * 0.5); }
      });

      { const ta = view * Math.PI / 2; if (Math.abs(ta - viewAng) > 0.001) { viewAng += (ta - viewAng) * Math.min(1, dt * 7); if (Math.abs(ta - viewAng) < 0.004) viewAng = ta; fitCamera(); } }
      tickMates(dt, t);
      me.moving = false;
      if (mode === 'walk') {
        const kx = (keys.KeyD || keys.ArrowRight ? 1 : 0) - (keys.KeyA || keys.ArrowLeft ? 1 : 0), kz = (keys.KeyS || keys.ArrowDown ? 1 : 0) - (keys.KeyW || keys.ArrowUp ? 1 : 0);
        if (me.sit && (kx || kz)) interact();
        if (!me.sit) {
          if (kx || kz) { const l = Math.hypot(kx, kz), ca = Math.cos(viewAng), sa = Math.sin(viewAng), wx = (kx * ca + kz * sa) / l, wz = (-kx * sa + kz * ca) / l; stepMe(wx * SPEED * dt, wz * SPEED * dt); me.face = Math.atan2(wx, wz); me.moving = true; me.target = null; }
          else if (me.target) { const dx = me.target.x - me.x, dz = me.target.z - me.z, dd = Math.hypot(dx, dz); if (dd < 0.1) me.target = null; else { const px = me.x, pz = me.z, s = Math.min(dd, SPEED * dt); stepMe(dx / dd * s, dz / dd * s); me.face = Math.atan2(dx, dz); me.moving = true; if (Math.hypot(me.x - px, me.z - pz) < s * 0.25 && (me.target.stuck += dt) > 0.5) me.target = null; } }
        }
      }
      if (me.sit) { meG.position.set(me.sit.x, me.sit.y, me.sit.z); me.face = me.sit.face; meG.rotation.x = me.sit.lie ? -Math.PI / 2 : 0; if (me.sit.lie) { meG.position.y += 0.2; meG.position.x += Math.sin(me.sit.face) * 0.05; meG.position.z += Math.cos(me.sit.face) * 0.05; } }
      else { meG.rotation.x = 0; meG.position.set(me.x, 0, me.z); }
      let dd = me.face - meG.rotation.y; dd = Math.atan2(Math.sin(dd), Math.cos(dd)); meG.rotation.y += dd * Math.min(1, dt * 12);
      if (me.wave > 0) me.wave -= dt;
      pet.update(t, { moving: me.moving, wave: me.wave > 0, sit: Boolean(me.sit && !me.sit.lie) });
      if (sayT > 0) sayT -= dt;
      const tagText = sayT > 0 ? sayText : me.sit && me.sit.lie ? '💤 ' + host.me.name : host.me.name + (me.wave > 0 ? ' 👋' : ''); if (tagText !== tag.textContent) { tag.textContent = tagText; tag.classList.toggle('say', sayT > 0); }
      if (ghost && meshOf[ghost.it.u]) meshOf[ghost.it.u].position.y += Math.sin(t * 6) * 0.0015;
      // 이름표·안내
      meG.getWorldPosition(v); if (me.sit && me.sit.lie) { v.y += 0.55; v.x -= Math.sin(me.sit.face) * 0.6; v.z -= Math.cos(me.sit.face) * 0.6; } else v.y += me.sit ? 1.1 : 1.25; v.project(camera);
      tag.style.transform = `translate(-50%, -100%) translate(${((v.x + 1) / 2 * w).toFixed(1)}px, ${((1 - v.y) / 2 * h).toFixed(1)}px)`;
      const c = nearby(), label = c ? c.label : '';
      if (label !== prompt.dataset.l) { prompt.dataset.l = label; prompt.innerHTML = label ? '<kbd>E</kbd>' + label : ''; prompt.style.display = label ? 'block' : 'none'; $('doBtn').textContent = label || '하기'; $('doBtn').style.opacity = label ? 1 : 0.5; }
      if (label) prompt.style.transform = `translate(-50%, -100%) translate(${((v.x + 1) / 2 * w).toFixed(1)}px, ${((1 - v.y) / 2 * h - 30).toFixed(1)}px)`;
      sun.target.position.set(0, 0, 0);
      renderer.render(scene, camera);
      requestAnimationFrame(frame);
    }

    buildShell(); buildGrid(); syncItems(); blk = blockers(); unstick(); renderList();
    const api = {
      host, frame,
      pause() { autoPaused = false; if (!running) return; running = false; Object.keys(keys).forEach(k => { keys[k] = false; }); },
      resume() { if (running) return; running = true; prev = performance.now(); requestAnimationFrame(frame); },
      dispose() { api.pause(); window.removeEventListener('keydown', onKeyDown); window.removeEventListener('keyup', onKeyUp); try { renderer.dispose(); renderer.forceContextLoss(); if (thumbR) { thumbR.r.dispose(); thumbR.r.forceContextLoss(); } } catch (e) {} root.innerHTML = ''; root.classList.remove('vroom'); },
      debug: { me, data, DEF, fits, tvOn, turnView, setMode, beginGhost, commitGhost, storeSel, rotateSel, colorSel, interact, nearby, renderer, camera, meshOf, get mode() { return mode; }, get ghost() { return ghost; }, get sel() { return sel; }, get size() { return [W, D]; }, set tab(x) { tab = x; renderList(); } },
    };
    requestAnimationFrame(frame);
    return api;
  }

  window.VillageRoom = { start, CATALOG, WALLS, FLOORS, SIZES, SIZE_PRICE };
})();

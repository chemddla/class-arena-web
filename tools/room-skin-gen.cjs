#!/usr/bin/env node
// 샘플 그림 없이 코드로 무늬를 그려 벽지·바닥 그림을 만듦 (assets/room/<part>_<id>.webp + 목록용 *_t.webp).
//   node tools/room-skin-gen.cjs [id ...]   (id를 안 주면 전부)
// 규격은 tools/room-skin.cjs와 같음: 캔버스 960×856, 8×6×4칸, 1칸 128×64, 1층 80도트.
// 벽: 몰딩(h 318~339)·걸레받이(h 0~20)·벽 끝 단면(16도트)은 기존 벽지와 같은 모양으로 그리고, 가운데 벽지 면만 무늬 함수로 채움.
//    무늬 좌표 (u, h): u = 모서리에서 벽을 따라 잰 거리(양쪽 벽이 모서리 기준 거울 대칭 → V자로 만남), h = 바닥선에서 위로 잰 높이.
//    왼쪽 벽은 0.94배 그늘. 넓힌 방에서 칸(64도트) 단위로 이어 붙이므로 u 방향 반복 간격은 64의 약수.
// 바닥: 바닥 평면 좌표 (p, q) = (X칸×128, Y칸×128)로 무늬를 그리고 2:1 투영. 앞 옆면(두께 16도트)은 어둡게.
//    넓힌 방에서 칸 단위로 이어 붙이므로 반복 간격은 1칸(128) 또는 2칸(256).
const path = require('path');
const fs = require('fs');
let sharp;
try { sharp = require('sharp'); } catch (e) { console.error('sharp가 필요해요 (npm i sharp)'); process.exit(1); }

const ROOM_X = 8, ROOM_Y = 6, ROOM_Z = 4, CW = 64, CH = 32, FH = 80, PAD = 32, THICK = 16, CAP = 16;
const OX = PAD + ROOM_Y * CW, OY = PAD + ROOM_Z * FH + 8;
const CANVAS_W = PAD * 2 + (ROOM_X + ROOM_Y) * CW, CANVAS_H = OY + (ROOM_X + ROOM_Y) * CH + THICK + PAD;
const iso = (X, Y, Z = 0) => ({ x: OX + (X - Y) * CW, y: OY + (X + Y) * CH - Z * FH });
const Lr = iso(0, ROOM_Y), Rr = iso(ROOM_X, 0), Or = iso(0, 0), Fr = iso(ROOM_X, ROOM_Y);
const lineY = (p, q) => x => p.y + (q.y - p.y) * (x - p.x) / ((q.x - p.x) || 1);
const lo = lineY(Lr, Or), or_ = lineY(Or, Rr), lf = lineY(Lr, Fr), fr = lineY(Fr, Rr);
const backEdge = x => Math.round(x + 0.5 <= Or.x ? lo(x + 0.5) : or_(x + 0.5));
const frontEdge = x => Math.round(x + 0.5 <= Fr.x ? lf(x + 0.5) : fr(x + 0.5));
const HB = 21, HT = 318, HTOP = 340; // 걸레받이 위 · 몰딩 아래 · 몰딩 꼭대기
const OUT = 'assets/room';

const hex = s => [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16)];
const mix = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
const mul = (a, k) => a.map(v => Math.min(255, v * k));
const hash = (i, j, k = 0) => { let h = (i * 374761393 + j * 668265263 + k * 2147483647) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); h ^= h >>> 16; return (h >>> 0) / 4294967296; };
const mod = (n, m) => ((n % m) + m) % m;

// 기존 벽지(wall_cream)에서 잰 걸레받이·몰딩 색 (h별)
const BASEBOARD = ['#785b48', '#785b48', '#725541', '#836651', '#a3846f', '#bc9b86', '#c7a58e', '#caa891', '#cba891', '#cba890', '#cca890', '#cca890', '#cba891', '#cba992', '#c8a790', '#bb9b86', '#a1846f', '#896e5a', '#836b58', '#9d8976', '#c7b6a3'].map(hex);
const MOLDING = (() => { // h = HT..HTOP-1
  const m = [];
  for (let h = HT; h < HTOP; h++) {
    const t = h - HT;
    m.push(hex(t < 2 ? '#efe1d1' : t < 5 ? '#e2cab9' : t < 8 ? '#c9a995' : t < 14 ? '#c7a28d' : t < 17 ? '#d9b59c' : t < 20 ? '#e2bca4' : '#7b614e'));
  }
  return m;
})();

// ───────── 벽지 무늬 (u, h) → [r,g,b] ─────────
const WALLS = {
  // 크림 바탕에 부드러운 세로 줄무늬 (줄 12도트, 간격 32)
  stripe_cream: (u, h) => {
    const base = hex('#f8f1e3'), st = hex('#ece0c9');
    const m = mod(u, 32);
    return m < 12 ? (m === 0 || m === 11 ? mix(st, base, 0.5) : st) : base;
  },
  // 아래쪽 크림 웨인스코팅 판자 + 위쪽 세이지
  wainscot_sage: (u, h) => {
    const sage = hex('#bccbb3'), cream = hex('#f6f1e6'), inset = hex('#ebe3d3'), shadow = hex('#c9bfae'), lite = hex('#fbf8f1');
    if (h >= 132) { // 위쪽 세이지: 아주 옅은 가로 결
      return mod(h, 4) === 0 ? mix(sage, lite, 0.06) : sage;
    }
    if (h >= 124) return h === 131 ? mul(shadow, 0.9) : h >= 128 ? lite : cream; // 윗 가로대(체어레일)
    if (h === 123) return shadow;
    const m = mod(u, 64);
    if (m < 8 || m >= 56) return m === 7 || m === 56 ? shadow : cream; // 세로 틀
    if (h < 28) return h === 27 ? shadow : cream; // 아래 가로대
    if (h >= 116) return h === 116 ? lite : cream; // 위 가로대
    // 패널 안쪽: 테두리 1도트 그늘/빛
    if (m === 8 || h === 115) return shadow;
    if (m === 55 || h === 28) return lite;
    return inset;
  },
  // 화이트 벽돌 (벽돌 32×14, 줄눈 2도트, 줄마다 반칸 엇갈림)
  brick_white: (u, h) => {
    const mortar = hex('#dcd6cc');
    const row = Math.floor(h / 16), hh = mod(h, 16);
    if (hh < 2) return mortar;
    const off = row % 2 ? 16 : 0, col = Math.floor((u + off) / 32), uu = mod(u + off, 32);
    if (uu < 2) return mortar;
    const r = hash(col, row), c = r < 0.33 ? hex('#f6f2ec') : r < 0.66 ? hex('#efe9e0') : hex('#f9f6f1');
    if (hh === 2 || uu === 2) return mix(c, hex('#ffffff'), 0.5); // 윗·왼쪽 빛
    if (hh === 15 || uu === 31) return mix(c, mortar, 0.6);     // 아랫·오른쪽 그늘
    if (hash(col, row, 7) < 0.08 && hash(u, h, 3) < 0.15) return mix(c, mortar, 0.5); // 거친 점
    return c;
  },
  // 네이비 바탕에 작은 크림 별·점 (64×64 반복)
  star_navy: (u, h) => {
    const base = hex('#2f3f6a'), star = hex('#f2e6c8'), dot = hex('#8fa0c8');
    const uu = mod(u, 64), hh = mod(h, 64);
    const stars = [[10, 12], [42, 24], [26, 46], [58, 56]], dots = [[30, 8], [8, 34], [50, 40], [40, 60]];
    for (const [sx, sy] of stars) {
      const dx = Math.abs(uu - sx), dy = Math.abs(hh - sy);
      if ((dx === 0 && dy <= 2) || (dy === 0 && dx <= 2)) return dx + dy === 0 ? hex('#fff8e6') : star;
      if (dx === 1 && dy === 1) return mix(base, star, 0.35);
    }
    for (const [sx, sy] of dots) if (uu === sx && hh === sy) return dot;
    return base;
  },
  // 네이비·머스터드 타탄 체크 (64 반복)
  tartan_navy: (u, h) => {
    const base = hex('#2f4a7a'), must = hex('#e8c43a'), cream = hex('#f3ead2');
    const uu = mod(u, 64), hh = mod(h, 64);
    const bu = uu < 10, bh = hh < 10; // 굵은 띠
    let c = base;
    if (bu && bh) c = mix(base, must, 0.92);
    else if (bu || bh) c = mix(base, must, 0.62);
    // 띠 안 짜임 결
    if ((bu || bh) && !(bu && bh) && mod(uu + hh, 2) === 0) c = mix(c, base, 0.25);
    if (uu === 36 || hh === 36) c = mix(c, cream, 0.55); // 가는 크림 선
    if (uu === 37 || hh === 37) c = mix(c, cream, 0.2);
    return c;
  },
  // 가로 원목 판자 (판자 높이 32, 가구 나무색과 맞춤)
  wood_panel: (u, h) => {
    const row = Math.floor(h / 32), hh = mod(h, 32);
    const tones = ['#d9a86c', '#d2a066', '#e0b074', '#cc9a60'].map(hex);
    const c = tones[Math.floor(hash(row, 0) * 4)];
    if (hh === 0) return hex('#8a5a30');
    if (hh === 1) return mix(c, hex('#fff2d8'), 0.4);
    if (hh === 31) return mix(c, hex('#8a5a30'), 0.4);
    const end = mod(u + (row % 2) * 64, 128); // 판자 끝 (줄마다 반 칸 엇갈림)
    if (end === 0) return hex('#8a5a30');
    if (end === 1) return mix(c, hex('#fff2d8'), 0.35);
    // 나뭇결: 판자마다 다른 위상의 긴 물결 선
    const seg = Math.floor((u + (row % 2) * 64) / 128);
    for (let g = 0; g < 3; g++) {
      const gy = 5 + g * 9 + Math.round(2 * Math.sin((u + hash(seg, row, g) * 200) / 23));
      if (hh === gy && hash(u, row, g + 10) < 0.8) return mix(c, hex('#8a5a30'), 0.25);
    }
    if (hash(u, h, 5) < 0.03) return mix(c, hex('#8a5a30'), 0.12);
    return c;
  },
  // 하늘·구름과 흰 울타리 (마당 가구용)
  sky_fence: (u, h) => {
    const top = hex('#a9d8f5'), bot = hex('#e4f4fc'), cloud = hex('#ffffff'), cloudS = hex('#dcecf7');
    let c = mix(bot, top, Math.min(1, Math.max(0, (h - 80) / 240)));
    // 구름: 128 반복, 둥근 덩어리 몇 개
    const uu = mod(u, 128);
    const blobs = [[34, 236, 26, 9], [20, 244, 14, 9], [50, 246, 16, 10], [40, 252, 10, 7], [100, 168, 20, 8], [90, 176, 12, 8], [112, 174, 11, 7]];
    for (const [bx, by, rx, ry] of blobs) {
      const d = ((uu - bx) / rx) ** 2 + ((h - by) / ry) ** 2;
      if (d <= 1) c = d > 0.72 && h < by ? cloudS : cloud;
    }
    if (h >= 100) return c;
    // 울타리: 기둥 16 간격, 널 10도트, 끝은 뾰족
    const pk = hex('#fbfbf8'), pkS = hex('#d8d8d0'), pkD = hex('#b9b9b0');
    const m = mod(u, 16), tip = 100 - Math.abs(m - 4.5) * 2; // 끝이 뾰족
    const rail = (h >= 30 && h < 40) || (h >= 66 && h < 76);
    if (m < 10 && h < tip) {
      if (h === Math.floor(tip) - 1 || m === 0) return pkS;
      if (m === 9) return pkD;
      return pk;
    }
    if (rail) return (h === 30 || h === 66) ? pkD : (h === 39 || h === 75) ? pkS : pk;
    return mix(c, hex('#9fd27a'), h < 26 ? 0.6 : 0); // 울타리 사이 풀
  },
};

// ── 2차 추가 벽지 ──
Object.assign(WALLS, {
  // 욕실: 아래 민트 타일(32×16) + 위 흰 벽
  tile_bath_mint: (u, h) => {
    const grout = hex('#cfe3dc'), white = hex('#f8f8f4');
    if (h >= 150) return hash(u, h, 1) < 0.02 ? mix(white, hex('#e8ece8'), 0.5) : white;
    if (h >= 144) return h === 149 ? hex('#b7cfc6') : h === 144 ? hex('#8fb3a8') : hex('#dcebe5'); // 윗 테두리 띠
    const row = Math.floor(h / 16), hh = mod(h, 16), off = row % 2 ? 16 : 0, uu = mod(u + off, 32), col = Math.floor((u + off) / 32);
    if (hh < 2 || uu < 2) return grout;
    const c = hash(col, row) < 0.85 ? hex('#a9dccb') : hex('#8ccbb6');
    if (hh === 2 || uu === 2) return mix(c, hex('#ffffff'), 0.45);
    if (hh === 15 || uu === 31) return mix(c, grout, 0.5);
    return c;
  },
  // 크림 지하철 타일 (전면, 64×32, 반칸 엇갈림)
  subway_cream: (u, h) => {
    const grout = hex('#d9d2c6');
    const row = Math.floor(h / 32), hh = mod(h, 32), off = row % 2 ? 32 : 0, uu = mod(u + off, 64), col = Math.floor((u + off) / 64);
    if (hh < 3 || uu < 3) return grout;
    const c = hash(col, row) < 0.8 ? hex('#f7f0e2') : hex('#f1e7d4');
    if (hh === 3 || uu === 3) return mix(c, hex('#ffffff'), 0.6);
    if (hh === 31 || uu === 63) return mix(c, grout, 0.6);
    if (hh === 4 || uu === 4) return mix(c, hex('#ffffff'), 0.25);
    return c;
  },
  // 분홍 하트 (64×64 반복, 엇갈림)
  heart_pink: (u, h) => {
    const base = hex('#fbe3ea'), heart = hex('#f28ca8'), dark = hex('#e5708f');
    const uu = mod(u, 64), hh = mod(h, 64);
    const pts = ['.XX...XX.', 'XXXX.XXXX', 'XXXXXXXXX', 'XXXXXXXXX', '.XXXXXXX.', '..XXXXX..', '...XXX...', '....X....'];
    const drawHeart = (cx, cy) => { // 도트 하트를 2배로 키워 18×16
      const x = Math.floor((uu - cx + 9) / 2), y = Math.floor((cy - hh + 8) / 2);
      if (y < 0 || y >= pts.length || x < 0 || x >= 9) return null;
      if (pts[y][x] !== 'X') return null;
      if (y === 1 && x === 2) return hex('#ffd6e0'); // 반짝임
      return y >= 5 ? dark : heart;
    };
    return drawHeart(16, 16) || drawHeart(48, 48) || ((uu === 48 && hh === 16) || (uu === 16 && hh === 48) ? hex('#f7c6d4') : base);
  },
  // 머스터드 셰브론 (지그재그, 가로 64 반복)
  chevron_mustard: (u, h) => {
    const a = hex('#e8c43a'), b = hex('#f6e6a8'), line = hex('#d4ad2a');
    const uu = mod(u, 64), zig = uu < 32 ? uu : 64 - uu; // 0..32..0
    const v = mod(h - zig, 32); // 지그재그 따라 흐르는 띠
    if (v === 0 || v === 16) return line;
    return v < 16 ? a : b;
  },
  // 보라 은하수 (게임방·오락기용)
  galaxy_purple: (u, h) => {
    const top = hex('#2a1b4e'), bot = hex('#4a2a73');
    let c = mix(bot, top, Math.min(1, Math.max(0, (h - 40) / 260)));
    const n = hash(u >> 3, h >> 3, 2); if (n < 0.25) c = mix(c, hex('#6a3fa0'), 0.25 * (1 - n * 4)); // 성운
    const r = hash(u, h, 3);
    if (r < 0.006) return hex('#fff7d6');
    if (r < 0.012) return hex('#c9b8ff');
    if (r < 0.016) return hex('#8a7ad8');
    // 큰 별 (128×128 반복): 십자 반짝임
    const uu = mod(u, 128), hh = mod(h, 128);
    for (const [sx, sy] of [[24, 40], [90, 96], [70, 20], [110, 60]]) {
      const dx = Math.abs(uu - sx), dy = Math.abs(hh - sy);
      if ((dx === 0 && dy <= 3) || (dy === 0 && dx <= 3)) return dx + dy <= 1 ? hex('#ffffff') : hex('#e6dcff');
    }
    // 작은 행성 하나 (반복 128)
    const d = ((uu - 50) / 7) ** 2 + ((hh - 110) / 7) ** 2;
    if (d < 1) return d > 0.7 ? hex('#c96a8a') : mod(uu + hh, 5) === 0 ? hex('#f0a0b8') : hex('#e58aa6');
    if (Math.abs(((uu - 50) / 14) ** 2 + ((hh - 110) / 4) ** 2 - 1) < 0.12 && hh < 110) return hex('#f5d6a0');
    return c;
  },
  // 세이지 바탕 보타닉 잎 (64×64 반복)
  leaf_forest: (u, h) => {
    const base = hex('#d9e4cf'), leaf = hex('#6f9a5c'), leafL = hex('#8fb57a'), stem = hex('#5a7f4a');
    const uu = mod(u, 128), hh = mod(h, 128);
    const leafAt = (cx, cy, flip) => {
      const dx = (uu - cx) * (flip ? -1 : 1), dy = hh - cy; // 잎: 비스듬한 타원 + 줄기
      const a = (dx + dy) / 24, b = (dx - dy) / 9;
      if (a * a + b * b <= 1) {
        if (Math.abs(dx - dy) <= 1) return stem; // 잎맥
        if (mod(dx + dy, 8) === 0 && b * (dx - dy) > 0) return mix(b > 0 ? leafL : leaf, stem, 0.35); // 곁맥
        return a * a + b * b > 0.85 ? mix(b > 0 ? leafL : leaf, stem, 0.3) : (b > 0 ? leafL : leaf);
      }
      if (dx >= -26 && dx <= -17 && Math.abs(dy - dx) <= 1) return stem; // 줄기 꼬리
      return null;
    };
    return leafAt(34, 30, false) || leafAt(98, 94, true) || leafAt(100, 26, true) || leafAt(36, 98, false) || (hash(uu >> 2, hh >> 2, 9) < 0.03 ? mix(base, leaf, 0.25) : base);
  },
  // 회색 성벽 돌 (큰 돌 64×32, 반칸 엇갈림)
  stone_castle: (u, h) => {
    const mortar = hex('#6f6a66');
    const row = Math.floor(h / 32), hh = mod(h, 32), off = row % 2 ? 32 : 0, uu = mod(u + off, 64), col = Math.floor((u + off) / 64);
    if (hh < 3 || uu < 3) return mortar;
    const tones = ['#a9a4a0', '#b4afaa', '#9e9995', '#aba39c'].map(hex);
    const c = tones[Math.floor(hash(col, row) * 4)];
    if (hh === 3 || uu === 3) return mix(c, hex('#ffffff'), 0.3);
    if (hh === 31 || uu === 63) return mix(c, mortar, 0.5);
    if (hash(uu >> 1, hh >> 1, col * 31 + row) < 0.08) return mix(c, mortar, 0.3); // 거친 질감
    return c;
  },
  // 파스텔 무지개 가로 줄무늬 (16도트씩, 바닥선과 나란히)
  rainbow_pastel: (u, h) => {
    const pal = ['#f9c5c5', '#fbdcb4', '#fbf3b8', '#cfeac6', '#c6e3f6', '#dccdf3'].map(hex);
    const i = Math.floor(h / 16), c = pal[mod(i, pal.length)];
    return mod(h, 16) === 0 ? mix(c, hex('#ffffff'), 0.5) : c;
  },
});

// ───────── 바닥 무늬 (p, q) → [r,g,b] ─────────
const OAK = ['#d6a46e', '#cc9862', '#deae78', '#c7925c'].map(hex), OAK_D = hex('#8c5f36'), OAK_L = hex('#f3d6ad');
const FLOORS = {
  // 헤링본 원목 (널 32×64)
  herringbone: (p, q) => {
    const W = 32, i = Math.floor(p / W), j = Math.floor(q / W), k = mod(i - j, 4);
    let lx, ly, id;
    if (k < 2) { lx = p - i * W + k * W; ly = q - j * W; id = [i - k, j]; }
    else { lx = p - i * W; ly = q - j * W + (3 - k) * W; id = [i, j - (3 - k)]; }
    const c = OAK[Math.floor(hash(id[0], id[1]) * 4)];
    const L = k < 2 ? 64 : 32, H = k < 2 ? 32 : 64;
    if (lx === 0 || ly === 0) return OAK_D;
    if (lx === 1 || ly === 1) return mix(c, OAK_L, 0.35);
    if (lx === L - 1 || ly === H - 1) return mix(c, OAK_D, 0.3);
    // 결: 긴 방향으로 가는 선
    const along = k < 2 ? lx : ly, across = k < 2 ? ly : lx;
    for (let g = 0; g < 2; g++) {
      const gy = 8 + g * 13 + Math.round(1.5 * Math.sin((along + hash(id[0], id[1], g) * 100) / 9));
      if (across === gy && hash(along, id[0] * 7 + id[1], g) < 0.7) return mix(c, OAK_D, 0.2);
    }
    return c;
  },
  // 밝은 오크 긴 널 (X 방향, 널 폭 32, 길이 256, 줄마다 엇갈림)
  oak: (p, q) => {
    const row = Math.floor(q / 32), qq = mod(q, 32), off = (row % 2) * 128;
    const seg = Math.floor((p + off) / 256), pp = mod(p + off, 256);
    const tones = ['#e4bd8c', '#dcb382', '#ebc796', '#d7ad7c'].map(hex);
    const c = tones[Math.floor(hash(seg, row) * 4)];
    if (qq === 0 || pp === 0) return hex('#9a6b40');
    if (qq === 1 || pp === 1) return mix(c, OAK_L, 0.4);
    if (qq === 31 || pp === 255) return mix(c, hex('#9a6b40'), 0.3);
    for (let g = 0; g < 3; g++) {
      const gy = 6 + g * 9 + Math.round(2 * Math.sin((pp + hash(seg, row, g) * 300) / 31));
      if (qq === gy && hash(pp, row, g + 3) < 0.75) return mix(c, hex('#9a6b40'), 0.18);
    }
    if (hash(seg, row, 9) < 0.3) { // 옹이
      const kx = 40 + hash(seg, row, 11) * 170, ky = 10 + hash(seg, row, 12) * 12, d = ((pp - kx) / 5) ** 2 + ((qq - ky) / 3) ** 2;
      if (d < 1) return mix(c, hex('#9a6b40'), d < 0.3 ? 0.5 : 0.25);
    }
    return c;
  },
  // 크림·차콜 체커보드 (64 타일, 줄눈 2도트)
  checker: (p, q) => {
    const i = Math.floor(p / 64), j = Math.floor(q / 64), pp = mod(p, 64), qq = mod(q, 64);
    const grout = hex('#bfb8ad');
    if (pp < 2 || qq < 2) return grout;
    const dark = (i + j) % 2 === 0, c = dark ? hex('#484850') : hex('#f2ece0');
    if (pp === 2 || qq === 2) return mix(c, hex('#ffffff'), dark ? 0.12 : 0.5);
    if (pp === 63 || qq === 63) return mix(c, grout, 0.35);
    if (hash(p >> 1, q >> 1, 2) < 0.06) return mix(c, dark ? hex('#5a5a64') : hex('#e4dccb'), 0.8); // 돌 질감 점
    return c;
  },
  // 네이비 카펫 (보풀 질감)
  carpet_navy: (p, q) => {
    const base = hex('#35497a');
    const n = hash(p >> 1, q >> 1, 1), c = mul(base, 0.94 + n * 0.12);
    if (hash(p, q, 4) < 0.05) return mix(c, hex('#6f84b8'), 0.6);
    if (hash(p, q, 6) < 0.03) return mix(c, hex('#223055'), 0.6);
    return c;
  },
  // 파스텔 모자이크 타일 (32 타일, 줄눈 2도트)
  tile_pastel: (p, q) => {
    const i = Math.floor(p / 32), j = Math.floor(q / 32), pp = mod(p, 32), qq = mod(q, 32);
    const grout = hex('#e9e2d6');
    if (pp < 2 || qq < 2) return grout;
    const r = hash(i, j), c = hex(r < 0.55 ? '#f7f1e6' : r < 0.75 ? '#cfe9dc' : r < 0.9 ? '#f6d3da' : '#fbeec2');
    if (pp === 2 || qq === 2) return mix(c, hex('#ffffff'), 0.5);
    if (pp === 31 || qq === 31) return mix(c, grout, 0.5);
    if (pp >= 4 && pp <= 7 && qq >= 4 && qq <= 5) return mix(c, hex('#ffffff'), 0.45); // 유약 반사
    return c;
  },
  // 잔디 마당 (풀잎·작은 꽃)
  grass: (p, q) => {
    const base = hex('#80bd60');
    const n = hash(p >> 2, q >> 2, 1);
    let c = mul(base, 0.93 + n * 0.12);
    const r = hash(p, q, 2);
    if (r < 0.07) c = hex('#5f9f44');
    else if (r < 0.12) c = hex('#a8dc80');
    if (hash(p, q, 3) < 0.004) return hex('#fff5c8');
    if (hash(p, q, 8) < 0.002) return hex('#f6a9c4');
    // 풀잎: 2도트 세로 선
    if (hash(p, q >> 1, 5) < 0.04) return hex('#5f9f44');
    return c;
  },
};

// ── 2차 추가 바닥 ──
Object.assign(FLOORS, {
  // 다다미 (1×2칸 돗자리, 짜임 결 + 짙은 테두리)
  tatami: (p, q) => {
    const j = Math.floor(q / 128), off = (j % 2) * 128; // 줄마다 반 칸 엇갈림
    const mp = mod(p + off, 256), mq = mod(q, 128), L = 256, H = 128;
    const edge = hex('#2f3a2a');
    if (mp < 5 || mq < 5 || mp >= L - 5 || mq >= H - 5) return mp === 5 || mq === 5 || mp === L - 6 || mq === H - 6 ? hex('#4a5a3a') : edge;
    const base = hex('#c9c37e');
    const along = mp, across = mq;
    let c = mod(across, 3) === 0 ? mix(base, hex('#a8a360'), 0.35) : base;
    if (mod(along, 6) === 0) c = mix(c, hex('#e0db9a'), 0.3);
    if (hash(p >> 1, q >> 1, 2) < 0.03) c = mix(c, hex('#a8a360'), 0.3);
    return c;
  },
  // 자갈길 (둥근 자갈, 64×64 반복)
  pebble: (p, q) => {
    const base = hex('#b9ada0');
    const pebs = [[14, 12, 9, 7], [40, 10, 11, 8], [58, 30, 8, 6], [26, 36, 12, 9], [50, 50, 9, 8], [8, 54, 10, 7], [36, 58, 7, 5], [4, 32, 6, 5]];
    const uu = mod(p, 64), vv = mod(q, 64), ci = Math.floor(p / 64), cj = Math.floor(q / 64);
    for (let k = 0; k < pebs.length; k++) {
      const [cx, cy, rx, ry] = pebs[k];
      const jx = Math.round(hash(ci, cj, k) * 4 - 2), jy = Math.round(hash(ci, cj, k + 20) * 4 - 2);
      for (const [ox, oy] of [[0, 0], [-64, 0], [64, 0], [0, -64], [0, 64]]) {
        const dx = uu - cx - jx - ox, dy = vv - cy - jy - oy, d = (dx / rx) ** 2 + (dy / ry) ** 2;
        if (d <= 1) {
          const tones = ['#d8cfc3', '#c7bcae', '#e0d8ce', '#b8ada2', '#cfc3b5'].map(hex), c = tones[Math.floor(hash(ci * 8 + k, cj, 5) * 5)];
          return d > 0.78 ? mix(c, hex('#8a7f73'), 0.45) : (dx < -rx * 0.3 && dy < -ry * 0.3 ? mix(c, hex('#ffffff'), 0.3) : c);
        }
      }
    }
    return hash(p, q, 7) < 0.08 ? mix(base, hex('#9a8f82'), 0.5) : base;
  },
  // 화이트 마블 (옅은 회색 결)
  marble_white: (p, q) => {
    const base = hex('#f3f1ec');
    const i = Math.floor(p / 128), j = Math.floor(q / 128), pp = mod(p, 128), qq = mod(q, 128);
    if (pp === 0 || qq === 0) return hex('#d4d0c8');
    if (pp === 1 || qq === 1) return hex('#fbfaf7');
    let c = base;
    for (let k = 0; k < 3; k++) {
      const ph = hash(i, j, k) * 100, amp = 6 + hash(i, j, k + 5) * 6;
      const vy = 20 + k * 40 + amp * Math.sin((pp + ph) / 13) + 3 * Math.sin((pp + ph) / 5);
      const d = Math.abs(qq - vy);
      if (d < 1) c = mix(c, hex('#b8b4ac'), 0.7); else if (d < 2.5) c = mix(c, hex('#d9d6cf'), 0.6);
    }
    if (hash(p >> 1, q >> 1, 3) < 0.05) c = mix(c, hex('#e4e1da'), 0.6);
    return c;
  },
  // 분홍·크림 체커 (64 타일)
  checker_pink: (p, q) => {
    const i = Math.floor(p / 64), j = Math.floor(q / 64), pp = mod(p, 64), qq = mod(q, 64);
    const grout = hex('#e3cfd3');
    if (pp < 2 || qq < 2) return grout;
    const pink = (i + j) % 2 === 0, c = pink ? hex('#f5c3cf') : hex('#fbf3e8');
    if (pp === 2 || qq === 2) return mix(c, hex('#ffffff'), 0.5);
    if (pp === 63 || qq === 63) return mix(c, grout, 0.5);
    return c;
  },
  // 다크 월넛 마루 (널 폭 32, 길이 256)
  wood_dark: (p, q) => {
    const row = Math.floor(q / 32), qq = mod(q, 32), off = (row % 2) * 128;
    const seg = Math.floor((p + off) / 256), pp = mod(p + off, 256);
    const tones = ['#5e3a26', '#684230', '#55331f', '#6e4834'].map(hex);
    const c = tones[Math.floor(hash(seg, row) * 4)];
    if (qq === 0 || pp === 0) return hex('#2e1a10');
    if (qq === 1 || pp === 1) return mix(c, hex('#a0735a'), 0.35);
    if (qq === 31 || pp === 255) return mix(c, hex('#2e1a10'), 0.4);
    for (let g = 0; g < 3; g++) {
      const gy = 6 + g * 9 + Math.round(2 * Math.sin((pp + hash(seg, row, g) * 300) / 29));
      if (qq === gy && hash(pp, row, g + 3) < 0.75) return mix(c, hex('#2e1a10'), 0.25);
    }
    return c;
  },
  // 분홍 카펫
  carpet_pink: (p, q) => {
    const base = hex('#f0b8c8');
    const n = hash(p >> 1, q >> 1, 1), c = mul(base, 0.95 + n * 0.09);
    if (hash(p, q, 4) < 0.05) return mix(c, hex('#ffffff'), 0.5);
    if (hash(p, q, 6) < 0.03) return mix(c, hex('#d98aa0'), 0.5);
    return c;
  },
  // 적벽돌 테라스 (벽돌 64×32, 엇갈림)
  brick_red: (p, q) => {
    const row = Math.floor(q / 32), qq = mod(q, 32), off = (row % 2) * 32, pp = mod(p + off, 64), col = Math.floor((p + off) / 64);
    const mortar = hex('#c9b9a6');
    if (qq < 3 || pp < 3) return mortar;
    const tones = ['#b9573f', '#a84d38', '#c4634a', '#9e4a36'].map(hex), c = tones[Math.floor(hash(col, row) * 4)];
    if (qq === 3 || pp === 3) return mix(c, hex('#e8a08a'), 0.35);
    if (qq === 31 || pp === 63) return mix(c, hex('#6e2e20'), 0.4);
    if (hash(p, q, 2) < 0.05) return mix(c, hex('#6e2e20'), 0.2);
    return c;
  },
  // 물결 타일 (파스텔 블루, 수영장용)
  wave_blue: (p, q) => {
    const base = hex('#bfe4f4'), wave = hex('#7fc4e6'), light = hex('#e8f6fc');
    const pp = mod(p, 64), qq = mod(q, 64);
    if (pp === 0 || qq === 0) return hex('#9fcfe6');
    const w = 32 + 9 * Math.sin(pp / 10.2); // 타일마다 물결 하나
    const d = qq - w;
    if (d >= 0 && d < 7) return d < 1 ? light : d < 5 ? wave : hex('#5fa9d4');
    if (d >= -22 && d < -16) return mix(base, wave, 0.45);
    if (hash(p, q, 3) < 0.02) return light;
    return base;
  },
});

// 벽 끝 단면 색 (바깥쪽부터): 벽지 평균색을 회색빛으로 눌러 기존 단면과 비슷하게
function capColors(avg) {
  const body = mix(mix(avg, hex('#d6d4de'), 0.55), hex('#dad1c1'), 0.3), cols = [];
  for (let i = 0; i < CAP - 1; i++) {
    cols.push(i === 0 ? mix(body, hex('#e8cbe0'), 0.5) : i === 1 ? mix(body, hex('#cfc3cc'), 0.4) : i >= 12 ? mix(body, hex('#ffffff'), (i - 11) * 0.22) : body);
  }
  return cols;
}

async function save(buf, part, id, by0) {
  const png = await sharp(buf, { raw: { width: CANVAS_W, height: CANVAS_H, channels: 4 } }).png().toBuffer();
  const file = path.join(OUT, `${part}_${id}.webp`);
  await sharp(png).webp({ lossless: true }).toFile(file);
  const crop = part === 'wall'
    ? { left: Or.x - 220, top: by0, width: 440, height: Or.y - by0 }
    : { left: Or.x - 200, top: Or.y + 100, width: 400, height: 260 };
  await sharp(png).extract(crop).resize({ width: 160, kernel: 'lanczos3' }).webp({ quality: 90 }).toFile(path.join(OUT, `${part}_${id}_t.webp`));
  console.log(`${file}  ${(fs.statSync(file).size / 1024).toFixed(0)}KB`);
}

function drawWall(id, pat) {
  const buf = Buffer.alloc(CANVAS_W * CANVAS_H * 4);
  // 평균색 (단면용)
  let avg = [0, 0, 0], n = 0;
  for (let u = 0; u < 128; u += 3) for (let h = HB; h < HT; h += 5) { const c = pat(u, h); avg = avg.map((v, i) => v + c[i]); n++; }
  avg = avg.map(v => v / n);
  const caps = capColors(avg);
  let by0 = CANVAS_H;
  const put = (x, y, c) => { const o = (y * CANVAS_W + x) * 4; buf[o] = Math.round(c[0]); buf[o + 1] = Math.round(c[1]); buf[o + 2] = Math.round(c[2]); buf[o + 3] = 255; if (y < by0) by0 = y; };
  for (let x = Lr.x - CAP; x < Rr.x + CAP; x++) {
    if (x < Lr.x || x >= Rr.x) { // 벽 끝 단면
      const left = x < Lr.x, i = left ? Lr.x - 1 - x : x - Rr.x, Ey = left ? Lr.y : Rr.y;
      if (i >= caps.length) continue;
      for (let y = Ey - HTOP + 1; y < Ey + THICK; y++) {
        const h = Ey - y;
        put(x, y, h >= HT ? MOLDING[h - HT] : h === HT - 1 ? mix(caps[i], hex('#7b614e'), 0.5) : caps[i]);
      }
      continue;
    }
    const yf = backEdge(x), left = x < Or.x, u = left ? Or.x - 1 - x : x - Or.x;
    for (let h = 0; h < HTOP; h++) {
      const y = yf - h;
      if (y < 0) continue;
      let c, k = left ? 0.94 : 1;
      if (h < HB) c = BASEBOARD[h];
      else if (h >= HT) c = MOLDING[h - HT];
      else {
        c = pat(u, h);
        if (x === Or.x - 1) k *= 0.86; else if (x === Or.x) k *= 0.93; // 모서리 그늘선
      }
      put(x, y, mul(c, k));
    }
  }
  return save(buf, 'wall', id, by0);
}

function drawFloor(id, pat) {
  const buf = Buffer.alloc(CANVAS_W * CANVAS_H * 4);
  const put = (x, y, c) => { const o = (y * CANVAS_W + x) * 4; buf[o] = Math.round(c[0]); buf[o + 1] = Math.round(c[1]); buf[o + 2] = Math.round(c[2]); buf[o + 3] = 255; };
  // 옆면 색: 무늬 평균
  let avg = [0, 0, 0], n = 0;
  for (let p = 0; p < 256; p += 3) for (let q = 0; q < 256; q += 3) { const c = pat(p, q); avg = avg.map((v, i) => v + c[i]); n++; }
  avg = avg.map(v => v / n);
  for (let x = Lr.x; x < Rr.x; x++) {
    const y0 = backEdge(x), y1 = frontEdge(x);
    for (let y = y0; y < y1 + THICK; y++) {
      if (y < y1) {
        const dx = x + 0.5 - OX, dy = y + 0.5 - OY;
        const a = (dx / CW + dy / CH) / 2, b = (dy / CH - dx / CW) / 2;
        const p = Math.max(0, Math.min(ROOM_X * 128 - 1, Math.floor(a * 128))), q = Math.max(0, Math.min(ROOM_Y * 128 - 1, Math.floor(b * 128)));
        let c = pat(p, q);
        if (y === y1 - 1) c = mix(c, hex('#ffffff'), 0.25); // 앞 모서리 빛
        put(x, y, c);
      } else {
        const r = y - y1, left = x + 0.5 <= Fr.x, side = mul(avg, left ? 0.8 : 0.72);
        const c = r === 0 ? mul(side, 1.06) : r < 11 ? side : r === 11 ? mul(side, 0.9) : r < 14 ? mul(side, 0.68) : r === 14 ? mul(side, 0.95) : mul(side, 1.12);
        put(x, y, c);
      }
    }
  }
  return save(buf, 'floor', id);
}

(async () => {
  const only = process.argv.slice(2);
  fs.mkdirSync(OUT, { recursive: true });
  for (const [id, pat] of Object.entries(WALLS)) if (!only.length || only.includes(id)) await drawWall(id, pat);
  for (const [id, pat] of Object.entries(FLOORS)) if (!only.length || only.includes(id)) await drawFloor(id, pat);
})();

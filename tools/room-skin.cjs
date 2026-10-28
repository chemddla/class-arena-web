#!/usr/bin/env node
// 방 샘플 그림(빈 방 틀 1024×876)에서 벽지·바닥을 떼어내 방 꾸미기 캔버스(960×856) 자리에 맞춘 그림으로 저장.
//   node tools/room-skin.cjs <샘플> --id <이름> [--part wall|floor|both] [--side left|right] [--out assets/room] [--colors 48]
//   --side: 벽지를 그쪽 벽 무늬 하나로 양쪽에 칠함 (벽지는 항상 양쪽 같은 무늬)
// 결과: <out>/wall_<id>.webp, <out>/floor_<id>.webp (캔버스와 같은 크기, 나머지는 투명) + 목록용 작은 그림 *_t.webp
// 샘플 방은 우리 방과 같은 8×6칸 모양이라, 바닥 세 꼭짓점(뒤·왼쪽·앞)으로 구한 1차 변환 하나로 그대로 옮김(비율 유지).
// 벽은 샘플의 몰딩·걸레받이·벽 끝 단면까지 통째로, 바닥은 바닥 판 두께(앞 옆면)까지 통째로 가져옴.
const path = require('path');
const fs = require('fs');
let sharp;
try { sharp = require('sharp'); } catch (e) { console.error('sharp가 필요해요 (npm i sharp 또는 NODE_PATH 지정)'); process.exit(1); }

// index.html HomeRoom 규격과 같은 값 (HOME_*)
const ROOM_X = 8, ROOM_Y = 6, ROOM_Z = 4, CW = 64, CH = 32, FH = 80, PAD = 32, THICK = 16;
const OX = PAD + ROOM_Y * CW, OY = PAD + ROOM_Z * FH + 8;
const CANVAS_W = PAD * 2 + (ROOM_X + ROOM_Y) * CW;
const CANVAS_H = OY + (ROOM_X + ROOM_Y) * CH + THICK + PAD;
const iso = (X, Y, Z = 0) => ({ x: OX + (X - Y) * CW, y: OY + (X + Y) * CH - Z * FH });

const args = process.argv.slice(2);
const opt = { part: 'both', out: 'assets/room', colors: 48,
  // 샘플 안 바닥 꼭짓점 (뒤 O, 왼쪽 L, 앞 F) — 빈 방 틀 1024×876 기준으로 잰 값
  o: '433,393', l: '44,588', f: '563,850' };
const files = [];
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a.startsWith('--')) opt[a.slice(2)] = args[++i]; else files.push(a);
}
if (!files.length || !opt.id) { console.error('사용법: node tools/room-skin.cjs <샘플> --id <이름> [--part wall|floor|both]'); process.exit(1); }
const pt = s => { const [x, y] = s.split(',').map(Number); return { x, y }; };

(async () => {
  const { data, info } = await sharp(files[0]).removeAlpha().raw().toBuffer({ resolveWithObject: true });
  const SW = info.width, SH = info.height;
  const sg = (x, y, c) => data[(Math.min(SH - 1, Math.max(0, y)) * SW + Math.min(SW - 1, Math.max(0, x))) * 3 + c];
  // 배경(분홍·보라 그라데이션)은 같은 줄 맨 왼쪽 색과 비슷한 픽셀
  const isBg = (x, y) => { let d = 0; for (let c = 0; c < 3; c++) d += Math.abs(sg(x, y, c) - sg(2, y, c)); return d < 36; };

  // 우리 캔버스 → 샘플 좌표: 칸 한 개의 X·Y 방향 벡터를 맞춤
  const O = pt(opt.o), L = pt(opt.l), F = pt(opt.f);
  const ex = { x: (F.x - L.x) / ROOM_X, y: (F.y - L.y) / ROOM_X }, ey = { x: (L.x - O.x) / ROOM_Y, y: (L.y - O.y) / ROOM_Y };
  // 우리 칸 벡터 (CW, CH)·(-CW, CH)의 역행렬
  const toS = (x, y) => {
    const dx = x - OX, dy = y - OY;
    const a = (dx / CW + dy / CH) / 2, b = (dy / CH - dx / CW) / 2; // X, Y 칸 수 (높이는 같은 1차 변환으로 따라감)
    return { x: O.x + a * ex.x + b * ey.x, y: O.y + a * ex.y + b * ey.y };
  };
  const bil = (sx, sy, c) => {
    const x0 = Math.floor(sx - 0.5), y0 = Math.floor(sy - 0.5), fx = sx - 0.5 - x0, fy = sy - 0.5 - y0;
    return sg(x0, y0, c) * (1 - fx) * (1 - fy) + sg(x0 + 1, y0, c) * fx * (1 - fy) + sg(x0, y0 + 1, c) * (1 - fx) * fy + sg(x0 + 1, y0 + 1, c) * fx * fy;
  };

  const Lr = iso(0, ROOM_Y), Rr = iso(ROOM_X, 0), Or = iso(0, 0);
  const lineY = (p, q) => x => p.y + (q.y - p.y) * (x - p.x) / ((q.x - p.x) || 1);
  const lo = lineY(Lr, Or), or_ = lineY(Or, Rr);
  // 엔진 diamond()와 같은 반올림: 바닥은 y >= round(뒤 모서리선(x+0.5))
  const backEdge = x => Math.round(x + 0.5 <= Or.x ? lo(x + 0.5) : or_(x + 0.5));
  const CAP = 16; // 벽 끝 단면 여유
  const which = (x, y) => {
    if (x < Lr.x - CAP || x >= Rr.x + CAP) return null;
    if (x < Lr.x || x >= Rr.x) return 'wall';
    return y < backEdge(x) ? 'wall' : 'floor';
  };

  fs.mkdirSync(opt.out, { recursive: true });
  const parts = opt.part === 'both' ? ['wall', 'floor'] : [opt.part];
  for (const part of parts) {
    const buf = Buffer.alloc(CANVAS_W * CANVAS_H * 4);
    let bx0 = CANVAS_W, by0 = CANVAS_H, bx1 = 0, by1 = 0;
    for (let y = 0; y < CANVAS_H; y++) for (let x = 0; x < CANVAS_W; x++) {
      if (which(x, y) !== part) continue;
      const s = toS(x + 0.5, y + 0.5);
      if (s.x < 0 || s.y < 0 || s.x >= SW || s.y >= SH || isBg(Math.floor(s.x), Math.floor(s.y))) continue;
      const o = (y * CANVAS_W + x) * 4;
      for (let c = 0; c < 3; c++) buf[o + c] = Math.round(bil(s.x, s.y, c));
      buf[o + 3] = 255;
      if (x < bx0) bx0 = x; if (x > bx1) bx1 = x; if (y < by0) by0 = y; if (y > by1) by1 = y;
    }
    // --side left|right: 한쪽 벽 무늬로 양쪽 벽을 칠함 (샘플 양쪽 벽지가 다르면 하나씩 따로 만듦)
    if (part === 'wall' && opt.side) {
      const src = Buffer.from(buf), S = opt.side, lenOf = s => (s === 'left' ? ROOM_Y : ROOM_X);
      const SHADE = Number(opt.shade || 0.94); // 왼쪽 벽은 그늘: 샘플에서 같은 벽지의 왼쪽/오른쪽 밝기 비
      buf.fill(0);
      for (let y = 0; y < CANVAS_H; y++) for (let x = 0; x < CANVAS_W; x++) {
        if (which(x, y) !== 'wall') continue;
        const d = (x + 0.5 - Or.x) / CW, T = d < 0 ? 'left' : 'right', a = Math.abs(d), lenT = lenOf(T);
        // 모서리에서 떨어진 거리 a를 원본 쪽 거리로: 6칸까지는 그대로, 오른쪽 벽 6~8칸은 거울처럼 되접음, 벽 끝 단면은 원본 벽 끝으로
        const a2 = a > lenT ? lenOf(S) + (a - lenT) : a <= ROOM_Y ? a : 2 * ROOM_Y - a;
        const sx = Math.floor(Or.x + (S === 'left' ? -a2 : a2) * CW), sy = Math.round(y + (a2 - a) * CH); // 바닥선에서 같은 높이
        if (sx < 0 || sx >= CANVAS_W || sy < 0 || sy >= CANVAS_H) continue;
        const so = (sy * CANVAS_W + sx) * 4, o = (y * CANVAS_W + x) * 4;
        if (!src[so + 3]) continue;
        const k = T === S ? 1 : T === 'left' ? SHADE : 1 / SHADE;
        for (let c = 0; c < 3; c++) buf[o + c] = Math.min(255, Math.round(src[so + c] * k));
        buf[o + 3] = 255;
      }
    }
    // 색 수를 줄여 압축 번짐을 정리 (투명은 그대로)
    const png = await sharp(buf, { raw: { width: CANVAS_W, height: CANVAS_H, channels: 4 } })
      .png({ palette: true, colours: Number(opt.colors), dither: 0 }).toBuffer();
    const file = path.join(opt.out, `${part}_${opt.id}.webp`);
    await sharp(png).webp({ lossless: true }).toFile(file);
    // 목록용 작은 그림: 벽은 안쪽 모서리 둘레, 바닥은 가운데
    const crop = part === 'wall'
      ? { left: Or.x - 220, top: by0, width: 440, height: Or.y - by0 }
      : { left: Or.x - 200, top: Or.y + 100, width: 400, height: 260 };
    await sharp(png).extract(crop).resize({ width: 160, kernel: 'lanczos3' }).webp({ quality: 90 }).toFile(path.join(opt.out, `${part}_${opt.id}_t.webp`));
    console.log(`${file}  (${bx0},${by0})-(${bx1},${by1})  ${(fs.statSync(file).size / 1024).toFixed(0)}KB`);
  }
})();

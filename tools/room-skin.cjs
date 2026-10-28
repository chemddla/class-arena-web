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
    // 벽 좌표: 열 x는 왼쪽 끝→모서리→오른쪽 끝으로 이어지는 벽 길이 방향, h는 바닥선에서 위로 잰 높이(도트)
    //  · 걸레받이(h < HB)·몰딩(h ≥ HT)은 원본 쪽 벽에서 높이별 대표색(중앙값)으로 반듯하게 다시 그림 → 끊김 없음
    //  · 벽지 면은 원본 쪽 벽에서 무늬 반복 간격 P를 재서 P씩 옮겨 붙임 → 모서리를 지나 반대쪽 벽까지 무늬가 그대로 이어짐
    //  · 벽 끝 단면은 원본 쪽 것을 반대쪽에 좌우 대칭으로, 모서리에는 얇은 그늘선
    if (part === 'wall' && opt.side) {
      const src = Buffer.from(buf), S = opt.side;
      const SHADE = Number(opt.shade || 0.94); // 왼쪽 벽은 그늘: 샘플에서 같은 벽지의 왼쪽/오른쪽 밝기 비
      const HB = Number(opt.hb || 21), HT = Number(opt.ht || 318); // 빈 방 틀의 걸레받이 위·몰딩 아래 높이
      const yf = x => backEdge(x); // 그 열의 첫 바닥 줄
      const px = (x, y) => (x < 0 || y < 0 || x >= CANVAS_W || y >= CANVAS_H) ? null : (o => src[o + 3] ? [src[o], src[o + 1], src[o + 2]] : null)((y * CANVAS_W + x) * 4);
      const tex = (x, h) => px(x, yf(x) - h);
      // 원본 쪽 벽에서 쓸 열 (끝 단면·모서리선 몇 도트 제외, 오른쪽 벽은 끝에 다른 판이 있을 수 있어 모서리에서 6칸까지)
      const s0 = S === 'left' ? Lr.x + 4 : Or.x + 4, s1 = S === 'left' ? Or.x - 4 : Or.x + ROOM_Y * CW - 4;
      // 높이별 대표색 (걸레받이·몰딩용)
      const prof = [];
      for (let h = 0; h <= 400; h++) {
        const cs = [[], [], []]; let n = 0, tot = 0;
        for (let x = s0; x < s1; x++) { tot++; const c = tex(x, h); if (c) { n++; c.forEach((v, i) => cs[i].push(v)); } }
        prof[h] = n > tot / 2 ? cs.map(a => a.sort((p, q) => p - q)[a.length >> 1]) : null;
      }
      const diff = (a, b) => (a && b ? Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]) : 999);
      // 무늬 반복 간격 P (짝수: 2:1 계단이라 P/2줄 위아래로 정확히 옮겨짐). 규칙 없는 무늬면 가장 덜 어긋나는 간격
      const OV = 20; // 이음매 찾는 폭 (양쪽 OV도트)
      let best = [], minE = Infinity;
      for (let P = 16; P <= Math.min(360, s1 - s0 - 2 * OV - 8); P += 2) {
        let e = 0, n = 0;
        for (let x = s0; x + P < s1; x += 2) for (let h = HB + 10; h < HT - 10; h += 4) { const d = diff(tex(x, h), tex(x + P, h)); if (d < 999) { e += d; n++; } }
        e = n ? e / n : Infinity; best.push([P, e]); minE = Math.min(minE, e);
      }
      const P = best.find(([, e]) => e <= minE * 1.15 + 2)[0];
      // 조각 k = 원본 열을 kP만큼 옮겨 붙인 것 (k=0은 원본 그대로). 조각 사이 이음매는 줄마다 무늬 차이가 가장 작은 곳을
      // 따라 구불구불 지나가게 함(이미지 퀼팅) → 규칙 없는 꽃무늬도 잘린 티가 덜 남
      // 촘촘하게 반복되는 무늬(간격 64도트 이하)는 패널 이음선 같은 튀는 줄이 없는 깨끗한 구간 하나(간격의 배수)로 벽 전체를 채움
      const periodic = P <= 64;
      const Pe = P * Math.max(1, Math.floor(160 / P));
      let a0 = s0;
      if (periodic) {
        const colErr = [];
        for (let x = s0; x < s1; x++) { let e = 0, n = 0; for (let h = HB + 6; h < HT - 6; h += 3) { const d = diff(tex(x, h), tex(x + P < s1 ? x + P : x - P, h)); if (d < 999) { e += d; n++; } } colErr[x] = n ? e / n : 999; }
        let bestA = Infinity;
        for (let a = s0; a + Pe <= s1; a += 2) { let e = 0; for (let x = a; x < a + Pe; x++) e = Math.max(e, colErr[x]); if (e < bestA) { bestA = e; a0 = a; } }
      }
      const tile = (k, x, h) => { const xs = x - k * P; return xs >= s0 && xs < s1 ? tex(xs, h) : null; };
      const seams = []; // { k: 왼쪽 조각, x0: 찾는 범위 시작, cut[h] }
      const addSeam = (k, xn) => {
        const x0 = xn - OV, W = 2 * OV + 1, H = HT - HB;
        const cost = (i, j) => diff(tile(k, x0 + i, HB + j), tile(k + 1, x0 + i, HB + j));
        let acc = Array.from({ length: W }, (_, i) => cost(i, 0)); const from = [];
        for (let j = 1; j < H; j++) {
          const nx = [], fr = [];
          for (let i = 0; i < W; i++) { let m = i; for (const t of [i - 1, i + 1]) if (t >= 0 && t < W && acc[t] < acc[m]) m = t; nx[i] = acc[m] + cost(i, j); fr[i] = m; }
          acc = nx; from[j] = fr;
        }
        const cut = new Array(H); let i = acc.indexOf(Math.min(...acc));
        for (let j = H - 1; j >= 0; j--) { cut[j] = x0 + i; if (j) i = from[j][i]; }
        seams.push({ k, cut, x0 });
      };
      // 원본 쪽 벽 끝(모서리 쪽)에서부터 오른쪽으로, 원본 시작에서부터 왼쪽으로 조각을 이어 붙임
      if (!periodic) for (let k = 0, xn = s1 - OV - 2; xn - OV < Rr.x; k++, xn += P) addSeam(k, xn);
      if (!periodic && Lr.x < s0 - 4) for (let k = -1, xn = s0 + OV + 1; xn + OV > Lr.x; k--, xn -= P) addSeam(k, xn);
      const tileAt = (x, h) => {
        let k = 0;
        for (const sm of seams) { const c = sm.cut[h - HB]; if (sm.k >= 0 ? x >= c && sm.k + 1 > k : x < c && sm.k < k) k = sm.k >= 0 ? sm.k + 1 : sm.k; }
        return k;
      };
      console.log(`  ${opt.id}: 무늬 반복 간격 ${P}도트 (어긋남 ${minE.toFixed(1)}), ${periodic ? `깨끗한 구간 ${a0}~${a0 + Pe}로 채움` : `이음매 ${seams.length}곳`}`);
      buf.fill(0);
      for (let y = 0; y < CANVAS_H; y++) for (let x = 0; x < CANVAS_W; x++) {
        if (which(x, y) !== 'wall') continue;
        const o = (y * CANVAS_W + x) * 4, T = x < Or.x ? 'left' : 'right';
        let c = null, k = T === S ? 1 : T === 'left' ? SHADE : 1 / SHADE;
        if (x < Lr.x || x >= Rr.x) {
          // 벽 끝 단면: 원본 쪽 단면을 그대로/좌우 대칭으로 (바닥선 높이 차이만큼 위아래로)
          const own = (x < Lr.x) === (S === 'left');
          if (own) c = px(x, y);
          else if (x >= Rr.x) c = px(Lr.x - 1 - (x - Rr.x), y - (Rr.y - Lr.y));
          else c = px(Rr.x + (Lr.x - 1 - x), y + (Rr.y - Lr.y));
          k = 1;
        } else {
          const h = yf(x) - y;
          if (h < HB || h >= HT) c = prof[h];
          else {
            if (periodic) c = tex(a0 + (((x - a0) % Pe) + Pe) % Pe, h);
            else { const t = tileAt(x, h); for (const kk of [t, t - 1, t + 1]) if ((c = tile(kk, x, h))) break; }
            if (!c) c = prof[h];
            if (x === Or.x - 1) k *= 0.86; else if (x === Or.x) k *= 0.93; // 모서리 그늘선
          }
        }
        if (!c) continue;
        for (let i = 0; i < 3; i++) buf[o + i] = Math.min(255, Math.round(c[i] * k));
        buf[o + 3] = 255;
      }
    }
    // 색 수를 줄여 압축 번짐을 정리 (투명은 그대로)
    const png = await sharp(buf, { raw: { width: CANVAS_W, height: CANVAS_H, channels: 4 } })
      .png(part === 'wall' && opt.side ? {} : { palette: true, colours: Number(opt.colors), dither: 0 }).toBuffer();
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

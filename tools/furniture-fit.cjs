// AI가 만든 가구 그림(흰 배경)을 방 꾸미기 도트 규격(assets/furniture/README.md)에 맞춰 줌
// 배경 제거 → 가구만 잘라 내기 → w×d×h 상자에 맞춰 크기 조정 → 도트 격자(이진 알파·24~28색)
// 사용법: node tools/furniture-fit.cjs --help
// index.html은 건드리지 않음. HOME_CATALOG에 넣을 한 줄만 출력함.
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const ROOT = path.resolve(__dirname, '..');
const CELL_W = 32, CELL_H = 16, FLOOR_H = 40; // 1칸 = 64×32 마름모, 1층 = 40도트

const HELP = `
가구 그림 → 방 꾸미기 도트 규격 변환

사용법
  node tools/furniture-fit.cjs <앞모습.png> [<뒷모습.png>] --id <id> --w <칸> --d <칸> --h <층> [옵션]

필수
  --id <이름>      영문 소문자·숫자·밑줄 (출력 파일 이름)
  --w <칸>         가로(벽을 따라가는 변) 칸 수
  --d <칸>         세로(벽에서 나오는 깊이) 칸 수
  --h <층>         높이 층 수 (0.5 단위, 러그는 0)

뒷모습
  --back <파일>    뒷모습 그림 (입력을 두 장 주는 것과 같음)

옵션
  --out <폴더>      결과 webp 폴더 (기본 assets/furniture)
  --preview <폴더>  5배 확대 확인용 PNG 폴더 (기본 tools/furniture-fit-out)
  --colors <수>     색 수 (기본 26, 24~28 권장)
  --tol <수>        배경색 허용 오차 0~255 (기본 10). 가구의 흰 부분이 #f0f0f8처럼 옅으면 작게
  --stretch         비율이 규격과 다를 때 자동으로 늘리기/줄이기 (기본은 보고만 함)
  --clear-holes     가구 안쪽에 갇힌 배경색 영역(의자 다리 사이 등)도 투명하게
  --no-guide        확인용 PNG에 규격 상자 선을 그리지 않음
  --dry             파일을 쓰지 않고 보고만
  --help            이 도움말
`;

// ───────── 인자 읽기 ─────────
function parseArgs(argv) {
  const o = { files: [], colors: 26, tol: 10, out: path.join(ROOT, 'assets', 'furniture'),
    preview: path.join(ROOT, 'tools', 'furniture-fit-out'), guide: true };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const val = () => { if (i + 1 >= argv.length) throw new Error(a + ' 뒤에 값이 필요해요'); return argv[++i]; };
    if (a === '--help' || a === '-h') o.help = true;
    else if (a === '--id') o.id = val();
    else if (a === '--w') o.w = Number(val());
    else if (a === '--d') o.d = Number(val());
    else if (a === '--h') o.h = Number(val());
    else if (a === '--back') { const n = argv[i + 1]; if (n && !n.startsWith('--')) o.back = argv[++i]; else o.backFlag = true; }
    else if (a === '--out') o.out = path.resolve(val());
    else if (a === '--preview') o.preview = path.resolve(val());
    else if (a === '--colors') o.colors = Number(val());
    else if (a === '--tol') o.tol = Number(val());
    else if (a === '--stretch') o.stretch = true;
    else if (a === '--clear-holes') o.clearHoles = true;
    else if (a === '--no-guide') o.guide = false;
    else if (a === '--dry') o.dry = true;
    else if (a.startsWith('--')) throw new Error('모르는 옵션: ' + a);
    else o.files.push(a);
  }
  return o;
}

function validate(o) {
  if (!/^[a-z0-9_]+$/.test(o.id || '')) throw new Error('--id 는 영문 소문자·숫자·밑줄만 써요');
  for (const k of ['w', 'd']) if (!(o[k] >= 1) || o[k] % 1) throw new Error(`--${k} 는 1 이상의 정수(칸)`);
  if (!(o.h >= 0) || (o.h * 2) % 1) throw new Error('--h 는 0 이상, 0.5 단위(층)');
  if (o.backFlag && !o.back && o.files.length < 2) throw new Error('--back 을 쓰려면 뒷모습 파일도 주세요 (--back 뒷모습.png)');
  if (o.back) o.files.push(o.back);
  if (o.files.length < 1) throw new Error('입력 그림 파일이 필요해요');
  if (o.files.length > 2) throw new Error('입력은 앞모습 1장 + 뒷모습 1장까지');
  for (const f of o.files) if (!fs.existsSync(f)) throw new Error('파일이 없어요: ' + f);
  if (!(o.colors >= 2 && o.colors <= 255)) throw new Error('--colors 범위 오류');
}

// ───────── 마스크 도구 ─────────
// 정사각 창 안의 1 개수 (가장자리는 이미지 안쪽만 셈)
function boxCount(m, W, H, r) {
  const tmp = new Int32Array(W * H), out = new Int32Array(W * H);
  for (let y = 0; y < H; y++) {
    let s = 0; const row = y * W;
    for (let x = 0; x <= Math.min(r, W - 1); x++) s += m[row + x];
    for (let x = 0; x < W; x++) {
      tmp[row + x] = s;
      if (x + r + 1 < W) s += m[row + x + r + 1];
      if (x - r >= 0) s -= m[row + x - r];
    }
  }
  for (let x = 0; x < W; x++) {
    let s = 0;
    for (let y = 0; y <= Math.min(r, H - 1); y++) s += tmp[y * W + x];
    for (let y = 0; y < H; y++) {
      out[y * W + x] = s;
      if (y + r + 1 < H) s += tmp[(y + r + 1) * W + x];
      if (y - r >= 0) s -= tmp[(y - r) * W + x];
    }
  }
  return out;
}
function dilate(m, W, H, r) { const c = boxCount(m, W, H, r), o = new Uint8Array(W * H); for (let i = 0; i < o.length; i++) o[i] = c[i] > 0 ? 1 : 0; return o; }
function erode(m, W, H, r) { // 이미지 밖은 1로 침
  const inv = new Uint8Array(W * H); for (let i = 0; i < inv.length; i++) inv[i] = m[i] ? 0 : 1;
  const c = boxCount(inv, W, H, r), o = new Uint8Array(W * H);
  for (let i = 0; i < o.length; i++) o[i] = c[i] === 0 ? 1 : 0;
  return o;
}

// 4방향으로 이어진 덩어리 번호 매기기 (mask가 1인 곳만). 반환 {label, areas}
function components(mask, W, H) {
  const label = new Int32Array(W * H), areas = [0];
  const stack = new Int32Array(W * H);
  for (let s = 0; s < W * H; s++) {
    if (!mask[s] || label[s]) continue;
    const id = areas.length; let n = 0, sp = 0;
    stack[sp++] = s; label[s] = id;
    while (sp) {
      const p = stack[--sp]; n++;
      const x = p % W, y = (p - x) / W;
      if (x > 0 && mask[p - 1] && !label[p - 1]) { label[p - 1] = id; stack[sp++] = p - 1; }
      if (x < W - 1 && mask[p + 1] && !label[p + 1]) { label[p + 1] = id; stack[sp++] = p + 1; }
      if (y > 0 && mask[p - W] && !label[p - W]) { label[p - W] = id; stack[sp++] = p - W; }
      if (y < H - 1 && mask[p + W] && !label[p + W]) { label[p + W] = id; stack[sp++] = p + W; }
    }
    areas.push(n);
  }
  return { label, areas };
}

function bboxOf(mask, W, H) {
  let x0 = W, y0 = H, x1 = -1, y1 = -1;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (mask[y * W + x]) {
    if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
  }
  return x1 < 0 ? null : { x0, y0, x1, y1, w: x1 - x0 + 1, h: y1 - y0 + 1 };
}

// ───────── 1단계: 배경 제거 ─────────
async function loadRGBA(file) {
  const { data, info } = await sharp(file).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  return { rgba: data, W: info.width, H: info.height };
}

function removeBackground(img, opt, warnings, notes) {
  const { rgba, W, H } = img, N = W * H;
  const transparent = new Uint8Array(N); // 처음부터 투명인 곳
  const rgb = new Uint8Array(N * 3);
  for (let i = 0; i < N; i++) {
    const a = rgba[i * 4 + 3];
    if (a < 128) transparent[i] = 1;
    for (let c = 0; c < 3; c++) rgb[i * 3 + c] = a >= 255 ? rgba[i * 4 + c] : Math.round((rgba[i * 4 + c] * a + 255 * (255 - a)) / 255);
  }
  // 배경색: 테두리 불투명 픽셀의 중앙값
  const border = [];
  for (let x = 0; x < W; x++) { border.push(x, (H - 1) * W + x); }
  for (let y = 0; y < H; y++) { border.push(y * W, y * W + W - 1); }
  const solid = border.filter(p => !transparent[p]);
  let bg = [255, 255, 255];
  if (solid.length) bg = [0, 1, 2].map(c => { const v = solid.map(p => rgb[p * 3 + c]).sort((a, b) => a - b); return v[v.length >> 1]; });
  const dist = p => Math.max(Math.abs(rgb[p * 3] - bg[0]), Math.abs(rgb[p * 3 + 1] - bg[1]), Math.abs(rgb[p * 3 + 2] - bg[2]));
  if (bg.some(v => v < 225)) warnings.push(`배경이 흰색이 아니에요 (테두리 색 rgb(${bg.join(',')})). 흰 배경으로 다시 만드는 게 안전해요`);
  const isBg = p => transparent[p] || dist(p) <= opt.tol;

  // 가장자리에서 이어진 배경만 flood fill
  const removed = new Uint8Array(N), stack = new Int32Array(N); let sp = 0;
  const push = p => { if (!removed[p] && isBg(p)) { removed[p] = 1; stack[sp++] = p; } };
  for (let x = 0; x < W; x++) { push(x); push((H - 1) * W + x); }
  for (let y = 0; y < H; y++) { push(y * W); push(y * W + W - 1); }
  while (sp) {
    const p = stack[--sp], x = p % W, y = (p - x) / W;
    if (x > 0) push(p - 1); if (x < W - 1) push(p + 1); if (y > 0) push(p - W); if (y < H - 1) push(p + W);
  }
  // 가장자리 번짐(옅은 테두리) 한 겹 걷어 내기
  const fringeTol = Math.max(opt.tol * 2.5, 24);
  const grow = [];
  for (let p = 0; p < N; p++) {
    if (removed[p]) continue;
    const x = p % W, y = (p - x) / W;
    const near = (x > 0 && removed[p - 1]) || (x < W - 1 && removed[p + 1]) || (y > 0 && removed[p - W]) || (y < H - 1 && removed[p + W]);
    if (near && dist(p) <= fringeTol) grow.push(p);
  }
  for (const p of grow) removed[p] = 1;

  let fg = new Uint8Array(N); for (let p = 0; p < N; p++) fg[p] = removed[p] ? 0 : 1;

  // 가구 안쪽에 갇힌 배경색 영역
  const bgLike = new Uint8Array(N);
  for (let p = 0; p < N; p++) if (fg[p] && dist(p) <= opt.tol) bgLike[p] = 1;
  const holes = components(bgLike, W, H);
  const fgArea0 = fg.reduce((a, b) => a + b, 0);
  const bigHoles = [];
  for (let id = 1; id < holes.areas.length; id++) if (holes.areas[id] >= Math.max(30, fgArea0 * 0.002)) bigHoles.push(id);
  if (bigHoles.length) {
    const total = bigHoles.reduce((a, id) => a + holes.areas[id], 0);
    if (opt.clearHoles) {
      const set = new Set(bigHoles);
      for (let p = 0; p < N; p++) if (set.has(holes.label[p])) { fg[p] = 0; removed[p] = 1; }
      notes.push(`안쪽에 갇힌 배경색 영역 ${bigHoles.length}곳(가구의 ${(total / fgArea0 * 100).toFixed(1)}%)을 투명하게 했어요 (--clear-holes)`);
    } else {
      notes.push(`가구 안쪽에 배경색(흰색) 영역 ${bigHoles.length}곳(가구의 ${(total / fgArea0 * 100).toFixed(1)}%)이 있어 그대로 두었어요. 의자 다리 사이처럼 진짜 빈 공간이면 --clear-holes`);
    }
  }

  // 작은 먼지 덩어리 정리: 가장 큰 덩어리의 2% 미만은 버림
  const comp = components(fg, W, H);
  const maxA = Math.max(...comp.areas.slice(1), 0);
  let dust = 0;
  for (let p = 0; p < N; p++) if (fg[p] && comp.areas[comp.label[p]] < maxA * 0.02) { fg[p] = 0; dust++; }
  if (dust) notes.push(`잔점 ${dust}픽셀 제거`);
  if (!maxA) throw new Error('가구를 찾지 못했어요 (전부 배경으로 판정됨). --tol 을 줄여 보세요');

  // 구멍(누수) 점검: 가구를 닫기 연산으로 메웠을 때 안쪽에 들어오는 배경 = 흰 부분이 배경과 이어져 지워진 흔적
  const bb = bboxOf(fg, W, H);
  const r = Math.max(4, Math.round(0.02 * Math.max(bb.w, bb.h)));
  const closed = erode(dilate(fg, W, H, r), W, H, r);
  let leak = 0, lx0 = W, ly0 = H, lx1 = -1, ly1 = -1;
  for (let p = 0; p < N; p++) if (closed[p] && !fg[p] && removed[p] && !transparent[p]) {
    leak++; const x = p % W, y = (p - x) / W;
    if (x < lx0) lx0 = x; if (x > lx1) lx1 = x; if (y < ly0) ly0 = y; if (y > ly1) ly1 = y;
  }
  const fgArea = fg.reduce((a, b) => a + b, 0);
  if (leak > fgArea * 0.004) {
    warnings.push(`가구 안쪽이 배경과 이어져 지워졌을 가능성: 의심 영역 ${leak}픽셀(가구의 ${(leak / fgArea * 100).toFixed(1)}%), 원본 좌표 x ${lx0}~${lx1}, y ${ly0}~${ly1}. `
      + `흰 부분의 윤곽선이 끊겼는지 확인하고, 흰 부분을 #f0f0f8로 다시 요청하거나 --tol 을 줄여 보세요`);
  }
  return { fg, rgb, bg, W, H, bb };
}

// ───────── 2단계: 바닥 마름모 측정 ─────────
function measure(fg, W, H, bb) {
  // 열마다 가장 아래 가구 픽셀
  const bot = new Int32Array(bb.w).fill(-1);
  for (let x = 0; x < bb.w; x++) for (let y = bb.y1; y >= bb.y0; y--) if (fg[y * W + bb.x0 + x]) { bot[x] = y; break; }
  const tolY = Math.max(2, Math.round(bb.h * 0.004));
  let first = -1, last = -1;
  for (let x = 0; x < bb.w; x++) if (bot[x] >= bb.y1 - tolY) { if (first < 0) first = x; last = x; }
  const x0 = (first + last) / 2;
  // 바닥 가장자리 기울기: 앞꼭짓점에서 양옆으로 10~70% 구간을 직선에 맞춤
  const slope = (dir, ext) => {
    if (ext < 12) return null;
    const pts = [];
    for (let t = Math.round(ext * 0.1); t <= Math.round(ext * 0.7); t++) {
      const x = Math.round(x0 + dir * t); if (x < 0 || x >= bb.w || bot[x] < 0) continue;
      pts.push([t, bot[Math.round(x0)] - bot[x]]);
    }
    if (pts.length < 4) return null;
    const n = pts.length, sx = pts.reduce((a, p) => a + p[0], 0), sy = pts.reduce((a, p) => a + p[1], 0);
    const sxx = pts.reduce((a, p) => a + p[0] * p[0], 0), sxy = pts.reduce((a, p) => a + p[0] * p[1], 0);
    const den = n * sxx - sx * sx; return den ? (n * sxy - sx * sy) / den : null;
  };
  const Lx = x0, Rx = bb.w - 1 - x0;
  return { x0, Lx, Rx, kL: slope(-1, Lx), kR: slope(1, Rx) };
}

// ───────── 3단계: 크기 조정 ─────────
async function fitToBox(fgres, spec, opt, warnings, notes, label) {
  const { fg, rgb, W, H, bb } = fgres;
  const { w, d, h } = spec;
  const boxW = (w + d) * CELL_W, boxH = (w + d) * CELL_H + h * FLOOR_H;
  const m = measure(fg, W, H, bb);

  // 잘라 낸 RGBA (배경은 알파 0)
  const crop = Buffer.alloc(bb.w * bb.h * 4);
  for (let y = 0; y < bb.h; y++) for (let x = 0; x < bb.w; x++) {
    const p = (bb.y0 + y) * W + bb.x0 + x, q = (y * bb.w + x) * 4;
    if (fg[p]) { crop[q] = rgb[p * 3]; crop[q + 1] = rgb[p * 3 + 1]; crop[q + 2] = rgb[p * 3 + 2]; crop[q + 3] = 255; }
  }

  // 규격과 비교
  const s = boxW / bb.w; // 가로 기준 균일 배율
  const kAvg = [m.kL, m.kR].filter(v => v != null);
  const slopeAvg = kAvg.length ? kAvg.reduce((a, b) => a + b, 0) / kAvg.length : null;
  const diff = (a, b) => Math.abs(a / b - 1);
  const tag = label ? `[${label}] ` : '';
  const issues = [];
  if (slopeAvg != null) {
    const r = slopeAvg / 0.5;
    if (Math.abs(r - 1) > 0.15) issues.push(`바닥 마름모가 규격보다 ${r < 1 ? '납작해요(가로로 넓음)' : '가팔라요(세로로 큼)'} — 가장자리 기울기 ${slopeAvg.toFixed(2)} (규격 0.50). 세로를 ${(1 / r).toFixed(2)}배로 ${r < 1 ? '늘려' : '줄여'}야 맞음`);
  }
  const wantL = w * CELL_W, gotL = m.x0 * s;
  if (diff(Math.max(gotL, 1), wantL) > 0.15 || diff(Math.max(boxW - gotL, 1), d * CELL_W) > 0.15) {
    const lenL = m.x0 / (m.x0 + m.Rx) * (w + d); // 원본 비율을 칸 수로
    issues.push(`가로:세로 비율이 달라요 — 원본은 약 ${lenL.toFixed(1)}:${(w + d - lenL).toFixed(1)}칸 모양, 규격은 ${w}:${d}. `
      + (gotL > wantL ? `왼쪽(w) 변이 너무 길고 오른쪽(d) 변이 짧아요` : `왼쪽(w) 변이 너무 짧고 오른쪽(d) 변이 길어요`));
  }
  const floorV = (m.kL != null && m.kR != null) ? (m.kL * m.Lx + m.kR * m.Rx) * s : (w + d) * CELL_H;
  const boxHeightEst = bb.h * s - floorV;
  if (h > 0) {
    const r = boxHeightEst / (h * FLOOR_H);
    if (r > 1.15) issues.push(`가구가 규격보다 키가 커요 — 높이 약 ${(boxHeightEst / FLOOR_H).toFixed(2)}층 (규격 ${h}층, ${((r - 1) * 100).toFixed(0)}% 초과)`);
    else if (r < 0.6) notes.push(`${tag}높이가 규격 ${h}층보다 많이 낮아요 (약 ${(boxHeightEst / FLOOR_H).toFixed(2)}층). 가구가 상자보다 낮은 거라면 괜찮아요`);
  }
  for (const t of issues) warnings.push(tag + t + (opt.stretch ? ' → --stretch 로 보정함' : ' (그대로 진행. 보정하려면 --stretch)'));

  // 목표 크기
  let leftW = Math.round(m.x0 * s), rightW = boxW - leftW, outH = Math.round(bb.h * s), splitX = Math.round(m.x0);
  if (opt.stretch) {
    leftW = w * CELL_W; rightW = d * CELL_W; splitX = Math.round(m.x0);
    const fL = leftW / Math.max(m.Lx, 1), fR = rightW / Math.max(m.Rx, 1);
    const sy = [m.kL != null ? CELL_H / CELL_W * fL / m.kL : null, m.kR != null ? CELL_H / CELL_W * fR / m.kR : null].filter(v => v != null);
    const syAvg = sy.length ? sy.reduce((a, b) => a + b, 0) / sy.length : s;
    outH = Math.round(bb.h * syAvg);
  }
  splitX = Math.min(Math.max(splitX, 1), bb.w - 1);
  leftW = Math.min(Math.max(leftW, 1), boxW - 1); rightW = boxW - leftW;
  outH = Math.max(outH, 1);

  const part = (left, width, tw) => sharp(crop, { raw: { width: bb.w, height: bb.h, channels: 4 } })
    .extract({ left, top: 0, width, height: bb.h })
    .resize(tw, outH, { fit: 'fill', kernel: 'lanczos3' }).raw().toBuffer();
  const [pl, pr] = await Promise.all([part(0, splitX, leftW), part(splitX, bb.w - splitX, rightW)]);
  const out = Buffer.alloc(boxW * outH * 4);
  for (let y = 0; y < outH; y++) {
    pl.copy(out, y * boxW * 4, y * leftW * 4, (y + 1) * leftW * 4);
    pr.copy(out, (y * boxW + leftW) * 4, y * rightW * 4, (y + 1) * rightW * 4);
  }
  return { rgba: out, W: boxW, H: outH, boxH, srcBB: bb, scale: s, frontX: m.x0 * (leftW / splitX) };
}

// ───────── 4단계: 도트 격자 (이진 알파 + 팔레트) ─────────
async function dotify(fit, colors) {
  const { rgba, W, H } = fit;
  const buf = Buffer.from(rgba);
  for (let i = 0; i < W * H; i++) {
    const o = i * 4;
    if (buf[o + 3] >= 128) buf[o + 3] = 255; else { buf[o] = buf[o + 1] = buf[o + 2] = 0; buf[o + 3] = 0; }
  }
  const png = await sharp(buf, { raw: { width: W, height: H, channels: 4 } })
    .png({ palette: true, colours: colors, dither: 0, effort: 10 }).toBuffer();
  const { data } = await sharp(png).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  const set = new Set();
  for (let i = 0; i < W * H; i++) {
    const o = i * 4;
    if (data[o + 3] >= 128) { data[o + 3] = 255; set.add((data[o] << 16) | (data[o + 1] << 8) | data[o + 2]); }
    else { data[o] = data[o + 1] = data[o + 2] = 0; data[o + 3] = 0; }
  }
  return { rgba: data, W, H, colorCount: set.size };
}

// 위쪽을 투명으로 채워 높이를 맞춤 (아래 기준)
function padTop(img, newH) {
  if (img.H === newH) return img;
  const out = Buffer.alloc(img.W * newH * 4);
  img.rgba.copy(out, (newH - img.H) * img.W * 4);
  return { ...img, rgba: out, H: newH };
}

// ───────── 앞/뒤 비교 ─────────
function compareFrontBack(f, b, spec, warnings) {
  const alphaOf = im => { const m = new Uint8Array(im.W * im.H); for (let i = 0; i < m.length; i++) m[i] = im.rgba[i * 4 + 3] ? 1 : 0; return m; };
  const H = Math.max(f.H, b.H), F = alphaOf(padTop(f, H)), B = alphaOf(padTop(b, H));
  let inter = 0, uni = 0;
  for (let i = 0; i < F.length; i++) { if (F[i] && B[i]) inter++; if (F[i] || B[i]) uni++; }
  const iou = uni ? inter / uni : 0;
  const bf = bboxOf(F, f.W, H), bbk = bboxOf(B, b.W, H);
  const msg = [];
  if (Math.abs(f.H - b.H) > 3) msg.push(`높이가 달라요 (앞 ${f.H} / 뒤 ${b.H}도트)`);
  if (bf && bbk && Math.abs(bf.w - bbk.w) > 3) msg.push(`가구 너비가 달라요 (앞 ${bf.w} / 뒤 ${bbk.w}도트)`);
  // 맨 아래 줄의 가운데 = 앞꼭짓점 위치
  const vx = (m, im, H) => { let a = -1, c = -1; for (let x = 0; x < im.W; x++) if (m[(H - 1) * im.W + x]) { if (a < 0) a = x; c = x; } return a < 0 ? null : (a + c) / 2; };
  const ax = vx(F, f, H), bx = vx(B, b, H);
  if (ax != null && bx != null && Math.abs(ax - bx) > 3) msg.push(`바닥 앞꼭짓점 위치가 달라요 (앞 x=${ax.toFixed(0)} / 뒤 x=${bx.toFixed(0)})`);
  if (iou < 0.85) msg.push(`겉모양(실루엣)이 많이 달라요 (겹침 ${(iou * 100).toFixed(0)}%) — 같은 상자·같은 앵커가 아닐 수 있어요`);
  if (msg.length) warnings.push('앞/뒤 불일치: ' + msg.join('; '));
  return { iou, ax, bx };
}

// ───────── 확인용 5배 PNG ─────────
async function writePreview(img, spec, file, guide) {
  const Z = 5, { W, H } = img, { w, d, h } = spec;
  const boxH = (w + d) * CELL_H + h * FLOOR_H, canvasH = Math.max(H, boxH) + 2;
  const up = await sharp(img.rgba, { raw: { width: W, height: H, channels: 4 } })
    .resize(W * Z, H * Z, { kernel: 'nearest' }).png().toBuffer();
  const cw = W * Z, ch = canvasH * Z, bot = canvasH * Z; // 이미지 아래 = 캔버스 아래
  const layers = [{ input: up, left: 0, top: ch - H * Z }];
  if (guide) {
    const P = (x, y) => `${(x * Z).toFixed(1)},${((canvasH - y) * Z).toFixed(1)}`; // y는 아래에서 위로
    const fl = [[w * 32, 0], [0, w * 16], [d * 32, (w + d) * 16], [W, d * 16]], up2 = fl.map(([x, y]) => [x, y + h * 40]);
    // 앞→왼→뒤→오른 순서로 이어야 마름모가 됨
    const poly = pts => pts.map(p => P(p[0], p[1])).join(' ');
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${cw}" height="${ch}"><g fill="none" stroke="#e5484d" stroke-width="2" opacity="0.8">`
      + `<polygon points="${poly(fl)}"/><polygon points="${poly(up2)}"/>`
      + [0, 1, 3].map(i => `<line x1="${fl[i][0] * Z}" y1="${(canvasH - fl[i][1]) * Z}" x2="${up2[i][0] * Z}" y2="${(canvasH - up2[i][1]) * Z}"/>`).join('')
      + `</g><circle cx="${w * 32 * Z}" cy="${bot}" r="7" fill="#2f6df6"/></svg>`;
    layers.push({ input: Buffer.from(svg), left: 0, top: 0 });
  }
  const bg = await sharp({ create: { width: cw, height: ch, channels: 3, background: { r: 226, g: 232, b: 224 } } }).png().toBuffer();
  fs.mkdirSync(path.dirname(file), { recursive: true });
  await sharp(bg).composite(layers).png().toFile(file);
}

// ───────── 한 장 처리 ─────────
async function processOne(file, spec, opt, label) {
  const warnings = [], notes = [];
  const img = await loadRGBA(file);
  const fgres = removeBackground(img, opt, warnings, notes);
  const fit = await fitToBox(fgres, spec, opt, warnings, notes, label);
  const dot = await dotify(fit, opt.colors);
  return { file, src: img, bb: fgres.bb, fit, dot, warnings, notes };
}

function fmt(n) { return Number.isInteger(n) ? String(n) : n.toFixed(1); }

async function main() {
  const o = parseArgs(process.argv.slice(2));
  if (o.help || process.argv.length <= 2) { console.log(HELP); return; }
  validate(o);
  const spec = { w: o.w, d: o.d, h: o.h };
  const hasBack = o.files.length === 2;
  const results = [await processOne(o.files[0], spec, o, hasBack ? '앞' : '')];
  if (hasBack) results.push(await processOne(o.files[1], spec, o, '뒤'));

  // 앞뒤 높이 맞추기 (아래 기준, 위쪽 투명 채움)
  const warnings = results.flatMap(r => r.warnings), notes = results.flatMap(r => r.notes);
  let cmp = null;
  if (hasBack) {
    cmp = compareFrontBack(results[0].dot, results[1].dot, spec, warnings);
    const H = Math.max(results[0].dot.H, results[1].dot.H);
    results.forEach(r => { r.dot = padTop(r.dot, H); });
  }
  const boxW = (o.w + o.d) * CELL_W, boxH = (o.w + o.d) * CELL_H + o.h * FLOOR_H;
  results.forEach((r, i) => {
    const tag = hasBack ? (i ? '[뒤] ' : '[앞] ') : '';
    if (r.dot.H > boxH + 4) warnings.push(`${tag}그림 높이 ${r.dot.H}도트가 상자 높이 ${boxH}도트(+허용 4)를 넘어요`);
    if (r.dot.colorCount > 28) warnings.push(`${tag}색이 ${r.dot.colorCount}개예요 (24~28 권장). --colors 를 줄여 보세요`);
  });

  // 저장
  const names = [o.id + '.webp', o.id + '_b.webp'];
  const written = [];
  if (!o.dry) {
    fs.mkdirSync(o.out, { recursive: true });
    for (let i = 0; i < results.length; i++) {
      const r = results[i], base = names[i].replace('.webp', '');
      const outFile = path.join(o.out, names[i]);
      await sharp(r.dot.rgba, { raw: { width: r.dot.W, height: r.dot.H, channels: 4 } }).webp({ lossless: true, effort: 6 }).toFile(outFile);
      await writePreview(r.dot, spec, path.join(o.preview, base + '_x5.png'), o.guide);
      written.push(outFile, path.join(o.preview, base + '_x5.png'));
    }
  }

  // 요약
  console.log(`\n=== ${o.id}  ${o.w}×${o.d}×${fmt(o.h)} (캔버스 너비 ${boxW}, 상자 높이 ${boxH}) ===`);
  results.forEach((r, i) => {
    const name = hasBack ? (i ? '뒷모습' : '앞모습') : '그림';
    const anchorX = Math.round(r.fit.frontX);
    console.log(`${name}: 원본 ${r.src.W}×${r.src.H} → 가구 ${r.bb.w}×${r.bb.h} → 최종 ${r.dot.W}×${r.dot.H}도트 (배율 ${r.fit.scale.toFixed(3)}${o.stretch ? ', 늘리기 적용' : ''})`);
    console.log(`  앵커(바닥 앞꼭짓점): x=${anchorX}, 맨 아래 (규격 x=${o.w * CELL_W}, 차이 ${anchorX - o.w * CELL_W >= 0 ? '+' : ''}${anchorX - o.w * CELL_W})  /  색 ${r.dot.colorCount}개  /  반투명 도트 0`);
  });
  if (cmp) console.log(`앞/뒤 점검: 실루엣 겹침 ${(cmp.iou * 100).toFixed(0)}%` + (cmp.ax != null && cmp.bx != null ? `, 앞꼭짓점 x ${cmp.ax.toFixed(0)} / ${cmp.bx.toFixed(0)}` : ''));
  if (notes.length) { console.log('\n참고'); notes.forEach(n => console.log('  · ' + n)); }
  console.log('\n경고 ' + (warnings.length ? warnings.length + '건' : '없음'));
  warnings.forEach(w => console.log('  ! ' + w));
  if (o.dry) console.log('\n(--dry: 파일을 쓰지 않았어요)');
  else { console.log('\n저장'); written.forEach(f => console.log('  ' + path.relative(process.cwd(), f))); }
  console.log(`\nHOME_CATALOG 줄에 넣을 것 (index.html은 직접 고치세요):\n  art: true${hasBack ? ', back: true' : ''}`);
}

main().catch(e => { console.error('오류: ' + e.message); process.exit(1); });

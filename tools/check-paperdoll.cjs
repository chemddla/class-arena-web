// 페이퍼돌 그림 검수: docs/paperdoll-base-body-spec.md 6장 검수 기준을 자동으로 검사
// 준비: npm install --no-save --no-audit --no-fund sharp@0.33.5
// 사용법: node tools/check-paperdoll.cjs [데이터 폴더] [--root 그림 경로 기준 폴더]
//   - 데이터 폴더(기본 assets/sprites/paperdoll)에 base.json, items.json이 있어야 함
//   - JSON 속 그림 경로는 index.html과 같이 저장소 루트 기준. --root로 바꿀 수 있음
// 틀린 곳이 하나라도 있으면 종료 코드 1
const fs = require('fs');
const path = require('path');

let sharp;
try { sharp = require('sharp'); } catch (e) {
  console.error('sharp가 없습니다. 먼저 실행: npm install --no-save --no-audit --no-fund sharp@0.33.5');
  process.exit(2);
}

const REPO = path.resolve(__dirname, '..');
const CELL_W = 160, CELL_H = 100, COUNT = 31, SHARED = 14, ANCHOR_Y = 96;
const SHEET_W = CELL_W * COUNT;
const SKULL_TOP = 19, NECK = { x: 82, y: 59 }, TOLERANCE = 1;
const STANDING = [0, 1, 2, 3, 4, 5, 6, 7, 14, 15, 16, 17, 18, 19, 20, 21]; // idle, walk, attack, skill
const SETS = ['melee', 'staff', 'bow'];
const SLOTS = ['body', 'face', 'hair', 'hat', 'outfit', 'legs', 'shoes', 'cape', 'weapon', 'offhand', 'backItem'];
const KINDS = ['frame', 'head', 'hand'];
const HEAD_POSES = ['N', 'T', 'B', 'L'];
const FIXED_COLORS = ['#1c0c10', '#ffffff', '#100808']; // 규격서 5-2 고정색: 외곽선, 흰자, 동공
const MAX_LAYER_COLORS = 32, MAX_OWN_COLORS = 8;

// ---------- 인자 ----------
const args = process.argv.slice(2);
let dataDir = path.join(REPO, 'assets/sprites/paperdoll');
let root = REPO;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--root') root = path.resolve(args[++i]);
  else dataDir = path.resolve(args[i]);
}

// 키 색은 index.html의 PD_KEY_RAMPS를 그대로 읽음 (색은 한 곳에서만 관리)
function readKeyRamps() {
  const html = fs.readFileSync(path.join(REPO, 'index.html'), 'utf8');
  const m = html.match(/const PD_KEY_RAMPS = (\{[\s\S]*?\n\s*\});/);
  if (!m) throw new Error('index.html에서 PD_KEY_RAMPS를 찾지 못했습니다');
  return Function(`return (${m[1]})`)();
}
const KEY_RAMPS = readKeyRamps();
const KEY_SLOT_OF = new Map(); // '#rrggbb' → 슬롯
Object.entries(KEY_RAMPS).forEach(([slot, ramp]) => ramp.forEach(c => KEY_SLOT_OF.set(c.toLowerCase(), slot)));
const FIXED = new Set(FIXED_COLORS);

// ---------- 결과 모음 ----------
const CHECKS = {
  0: '정의 파일 (base.json, items.json)',
  1: '시트 크기',
  2: '투명도 0 / 255만',
  3: '색 (키 색 + 고정색 + 고유색 8개 이하, 레이어당 32색 이하)',
  4: '서 있는 프레임의 발바닥 = y 96',
  5: 'idle 0번 두개골 꼭대기 y 19, 목 회전점 (82, 59)',
  6: '0 ~ 13번 칸이 세 세트에서 같음',
  7: '관절 JSON',
  8: '머리카락·모자가 두개골을 빈틈 없이 덮음',
  9: '이펙트가 몸·옷 레이어에 없음'
};
const problems = Object.fromEntries(Object.keys(CHECKS).map(k => [k, []]));
const fail = (check, msg) => problems[check].push(msg);

// ---------- 그림 읽기 ----------
const images = new Map();
async function loadImage(src) {
  if (!images.has(src)) {
    const file = path.resolve(root, src);
    images.set(src, fs.existsSync(file)
      ? sharp(file).ensureAlpha().raw().toBuffer({ resolveWithObject: true })
        .then(({ data, info }) => ({ src, data, w: info.width, h: info.height }))
        .catch(e => ({ src, error: e.message }))
      : Promise.resolve({ src, error: `파일 없음: ${file}` }));
  }
  return images.get(src);
}
const alphaAt = (img, x, y) => img.data[(y * img.w + x) * 4 + 3];
const hexAt = (img, i) => '#' + [img.data[i], img.data[i + 1], img.data[i + 2]].map(v => v.toString(16).padStart(2, '0')).join('');
// 31칸 시트 좌표를 사람이 읽기 쉽게
function where(img, x, y) {
  if (img.w !== SHEET_W) return `(${x}, ${y})`;
  return `칸 ${Math.floor(x / CELL_W)}, 행 ${Math.floor(y / CELL_H)}, 칸 안 (${x % CELL_W}, ${y % CELL_H})`;
}
// 시트의 한 칸·한 행에서 칠해진 픽셀 목록 (칸 좌표)
function cellPixels(img, frame, row) {
  const out = [];
  if (!img || img.error || (row + 1) * CELL_H > img.h) return out;
  for (let y = 0; y < CELL_H; y++) for (let x = 0; x < CELL_W; x++) {
    if (alphaAt(img, frame * CELL_W + x, row * CELL_H + y)) out.push([x, y]);
  }
  return out;
}
function cellsEqual(a, b, frame) {
  if (!a || !b || a.error || b.error || a.h !== b.h) return false;
  for (let y = 0; y < a.h; y++) {
    const start = (y * a.w + frame * CELL_W) * 4, end = start + CELL_W * 4;
    if (Buffer.compare(a.data.subarray(start, end), b.data.subarray(start, end)) !== 0) return false;
  }
  return true;
}

function readJson(name) {
  const file = path.join(dataDir, name);
  if (!fs.existsSync(file)) { fail(0, `${file} 이 없습니다`); return null; }
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch (e) { fail(0, `${name}: JSON 형식 오류 (${e.message})`); return null; }
}
const isRect = r => Array.isArray(r) && r.length === 6 && r.every(Number.isInteger);
const isInt = v => Number.isInteger(v);

async function main() {
  const base = readJson('base.json');
  const itemsDoc = readJson('items.json');
  if (!base || !itemsDoc) return;
  const items = itemsDoc.items || {};

  // ---------- 0. 정의 파일 ----------
  if (!base.sets) fail(0, 'base.json에 sets가 없습니다');
  SETS.forEach(set => {
    if (!base.sets || !base.sets[set]) fail(0, `base.json: ${set} 세트가 없습니다`);
    else if (!base.sets[set].src) fail(0, `base.json: ${set} 세트에 마네킹 시트(src)가 없습니다`);
  });
  Object.entries(items).forEach(([id, item]) => {
    if (!SLOTS.includes(item.slot)) fail(0, `${id}: 알 수 없는 slot "${item.slot}"`);
    if (!KINDS.includes(item.kind)) fail(0, `${id}: 알 수 없는 kind "${item.kind}"`);
    if (!item.src) fail(0, `${id}: src가 없습니다`);
    if (item.kind === 'frame' && item.src && typeof item.src === 'object') {
      Object.keys(item.src).forEach(k => { if (k !== 'common' && !SETS.includes(k)) fail(0, `${id}: src에 알 수 없는 세트 "${k}"`); });
    }
    if (item.kind === 'head' && !item.poses) fail(0, `${id}: poses가 없습니다`);
    if (item.kind === 'hand' && !item.angles && !item.rect) fail(0, `${id}: angles도 rect도 없습니다`);
    if (item.slot === 'hat' && item.hair && !['show', 'capped', 'hidden'].includes(item.hair)) fail(0, `${id}: hair 값은 show / capped / hidden 중 하나`);
    (item.palette || []).forEach(s => { if (!KEY_RAMPS[s]) fail(0, `${id}: palette에 없는 슬롯 "${s}"`); });
  });

  // 검사할 레이어 목록: 마네킹 3장 + 아이템
  const mannequin = {};
  for (const set of SETS) {
    const src = base.sets && base.sets[set] && base.sets[set].src;
    if (src) mannequin[set] = await loadImage(src);
  }
  const layers = [];
  SETS.forEach(set => { if (mannequin[set]) layers.push({ id: `마네킹 ${set}`, kind: 'frame', palette: ['skin'], srcs: [base.sets[set].src], isBody: true }); });
  Object.entries(items).forEach(([id, item]) => {
    if (!item.src) return;
    const srcs = typeof item.src === 'string' ? [item.src] : Object.values(item.src);
    layers.push({ id, kind: item.kind, palette: item.palette, srcs, item });
  });
  for (const l of layers) l.imgs = await Promise.all(l.srcs.map(loadImage));

  // ---------- 1. 시트 크기 / 2. 투명도 / 3. 색 ----------
  for (const l of layers) {
    const colors = new Map(); // 색 → 첫 위치
    for (const img of l.imgs) {
      if (img.error) { fail(1, `${l.id}: ${img.error}`); continue; }
      if (l.kind === 'frame') {
        const okH = l.isBody ? img.h === 300 : [100, 200, 300].includes(img.h);
        if (img.w !== SHEET_W || !okH) {
          fail(1, `${l.id} (${img.src}): ${img.w}×${img.h} → 너비 ${SHEET_W}, 높이 ${l.isBody ? '300' : '100·200·300'}이어야 함`);
        }
      } else {
        const rects = [];
        if (l.kind === 'head') {
          const walk = o => { if (isRect(o)) rects.push(o); else if (o && typeof o === 'object') Object.values(o).forEach(walk); };
          walk(l.item.poses);
        } else {
          if (l.item.rect) rects.push(l.item.rect);
          Object.values(l.item.angles || {}).forEach(r => rects.push(r));
        }
        rects.forEach(r => {
          if (!isRect(r)) fail(1, `${l.id}: 사각형 ${JSON.stringify(r)}은 정수 6개 [x, y, w, h, 붙는점x, 붙는점y]여야 함`);
          else if (r[0] < 0 || r[1] < 0 || r[0] + r[2] > img.w || r[1] + r[3] > img.h) fail(1, `${l.id}: 사각형 ${JSON.stringify(r)}이 그림(${img.w}×${img.h}) 밖으로 나감`);
        });
      }
      let semi = 0, firstSemi = null;
      for (let i = 0; i < img.data.length; i += 4) {
        const a = img.data[i + 3];
        if (a !== 0 && a !== 255) { semi++; if (!firstSemi) firstSemi = i / 4; }
        if (a === 0) continue;
        const hex = hexAt(img, i);
        if (!colors.has(hex)) colors.set(hex, `${img.src} ${where(img, (i / 4) % img.w, Math.floor(i / 4 / img.w))}`);
      }
      if (semi) fail(2, `${l.id} (${img.src}): 반투명 픽셀 ${semi}개, 첫 위치 ${where(img, firstSemi % img.w, Math.floor(firstSemi / img.w))}`);
    }
    const own = [], wrongSlot = [];
    colors.forEach((at, hex) => {
      if (FIXED.has(hex)) return;
      const slot = KEY_SLOT_OF.get(hex);
      if (!slot) own.push(hex);
      else if (l.palette && !l.palette.includes(slot)) wrongSlot.push(`${hex}(${slot}) ${at}`);
    });
    if (colors.size > MAX_LAYER_COLORS) fail(3, `${l.id}: 색 ${colors.size}개 (최대 ${MAX_LAYER_COLORS})`);
    if (own.length > MAX_OWN_COLORS) {
      fail(3, `${l.id}: 키 색·고정색이 아닌 색 ${own.length}개 (최대 ${MAX_OWN_COLORS}): ${own.slice(0, 6).map(h => `${h} ${colors.get(h)}`).join(' / ')}${own.length > 6 ? ' …' : ''}`);
    }
    if (wrongSlot.length) fail(3, `${l.id}: palette에 없는 슬롯의 키 색 (색이 안 바뀜): ${wrongSlot.slice(0, 4).join(' / ')}`);
  }

  // ---------- 4. 발바닥 / 5. 두개골·목 ----------
  for (const set of SETS) {
    const img = mannequin[set];
    if (!img || img.error || img.w !== SHEET_W) continue;
    const off = [];
    STANDING.forEach(f => {
      let bottom = -1;
      for (let row = 0; row < 3; row++) cellPixels(img, f, row).forEach(([, y]) => { bottom = Math.max(bottom, y); });
      if (bottom !== ANCHOR_Y) off.push(`${f}번(${bottom < 0 ? '빈 칸' : `y ${bottom}`})`);
    });
    if (off.length) fail(4, `마네킹 ${set}: 발바닥이 y ${ANCHOR_Y}이 아닌 프레임 ${off.join(', ')}`);

    const body = cellPixels(img, 0, 1);
    const top = body.length ? Math.min(...body.map(([, y]) => y)) : null;
    if (top === null) fail(5, `마네킹 ${set}: idle 0번 몸(1행)이 비어 있음`);
    else if (Math.abs(top - SKULL_TOP) > TOLERANCE) fail(5, `마네킹 ${set}: idle 0번 두개골 꼭대기 y ${top} (기준 ${SKULL_TOP} ±${TOLERANCE})`);
    const head = base.sets[set].frames && base.sets[set].frames[0] && base.sets[set].frames[0].head;
    if (head && (Math.abs(head.x - NECK.x) > TOLERANCE || Math.abs(head.y - NECK.y) > TOLERANCE)) {
      fail(5, `${set}: idle 0번 목 회전점 (${head.x}, ${head.y}) (기준 (${NECK.x}, ${NECK.y}) ±${TOLERANCE})`);
    }
  }

  // ---------- 6. 0~13번 같은 그림 ----------
  const [first, ...rest] = SETS.filter(s => mannequin[s] && !mannequin[s].error);
  rest.forEach(set => {
    const diff = [];
    for (let f = 0; f < SHARED; f++) if (!cellsEqual(mannequin[first], mannequin[set], f)) diff.push(f);
    if (diff.length) fail(6, `마네킹 ${set}: ${first}와 다른 칸 ${diff.join(', ')}`);
  });
  for (const l of layers) {
    if (l.isBody || l.kind !== 'frame' || typeof l.item.src !== 'object' || l.item.src.common) continue;
    const setImgs = SETS.filter(s => l.item.src[s]).map(s => [s, l.imgs[l.srcs.indexOf(l.item.src[s])]]);
    for (let i = 1; i < setImgs.length; i++) {
      const diff = [];
      for (let f = 0; f < SHARED; f++) if (!cellsEqual(setImgs[0][1], setImgs[i][1], f)) diff.push(f);
      if (diff.length) fail(6, `${l.id}: ${setImgs[i][0]} 시트가 ${setImgs[0][0]}와 다른 칸 ${diff.join(', ')} (같은 그림이면 src.common으로 빼기)`);
    }
  }
  const sameJoint = (a, b) => JSON.stringify(a || null) === JSON.stringify(b || null);
  SETS.slice(1).forEach(set => {
    const fa = base.sets.melee && base.sets.melee.frames, fb = base.sets[set] && base.sets[set].frames;
    if (!Array.isArray(fa) || !Array.isArray(fb)) return;
    const diff = [];
    for (let f = 0; f < SHARED; f++) {
      if (!sameJoint(fa[f] && fa[f].head, fb[f] && fb[f].head) || !sameJoint(fa[f] && fa[f].back, fb[f] && fb[f].back)) diff.push(f);
    }
    if (diff.length) fail(6, `관절: ${set}의 head·back 값이 melee와 다른 칸 ${diff.join(', ')}`);
  });

  // ---------- 7. 관절 JSON ----------
  const checkPoint = (set, f, key, p) => {
    if (p === null || p === undefined) return;
    if (!isInt(p.x) || !isInt(p.y)) { fail(7, `${set} ${f}번 ${key}: x, y는 정수`); return; }
    if (p.x < 0 || p.x >= CELL_W || p.y < 0 || p.y >= CELL_H) fail(7, `${set} ${f}번 ${key}: (${p.x}, ${p.y})가 칸 밖`);
    if (key === 'head' && p.pose !== undefined && !HEAD_POSES.includes(p.pose)) fail(7, `${set} ${f}번 head.pose "${p.pose}"는 N·T·B·L 중 하나`);
    if ((key === 'handF' || key === 'handB') && p.a !== undefined && typeof p.a !== 'number') fail(7, `${set} ${f}번 ${key}.a는 숫자(도)`);
    if (key === 'handF' && p.z !== undefined && !['front', 'back'].includes(p.z)) fail(7, `${set} ${f}번 handF.z는 front 또는 back`);
  };
  SETS.forEach(set => {
    const s = base.sets && base.sets[set];
    if (!s) return;
    if (!Array.isArray(s.frames) || s.frames.length !== COUNT) { fail(7, `${set}: frames가 ${COUNT}개여야 함 (지금 ${Array.isArray(s.frames) ? s.frames.length : '없음'})`); return; }
    const img = mannequin[set];
    s.frames.forEach((fr, f) => {
      const drawn = img && !img.error && img.w === SHEET_W && [0, 1, 2].some(row => cellPixels(img, f, row).length);
      if (fr === null) { if (drawn) fail(7, `${set} ${f}번: 관절이 null인데 마네킹이 그려져 있음 (머리·무기가 안 붙음)`); return; }
      if (!fr.head) fail(7, `${set} ${f}번: head가 없음`);
      ['head', 'handF', 'handB', 'back'].forEach(k => checkPoint(set, f, k, fr[k]));
    });
  });

  // ---------- 8. 머리 덮기 ----------
  // 두개골 = 마네킹 1행에서 목 회전점보다 위의 픽셀. 위쪽 가장자리(누운 자세 L은 오른쪽 가장자리)가 모두 덮여야 함
  const headItems = slot => Object.entries(items).filter(([, it]) => it.slot === slot && it.kind === 'head');
  const rectOf = (item, variant, pose, part) => {
    const byVariant = (variant && item.poses[variant]) || item.poses.full || item.poses.normal || item.poses;
    const p = byVariant[pose] || byVariant.N;
    return p ? p[part] : null;
  };
  const combos = [];
  headItems('hair').forEach(([hid, hair]) => combos.push({ name: hid, parts: [[hair, 'full']] }));
  headItems('hat').forEach(([tid, hat]) => {
    if (hat.hair === 'hidden' || hat.hair === 'show') combos.push({ name: tid, parts: [[hat, null]] });
    else headItems('hair').forEach(([hid, hair]) => combos.push({ name: `${hid} + ${tid}`, parts: [[hair, 'capped'], [hat, null]] }));
  });
  for (const combo of combos) {
    const gaps = new Map(); // 자세 → [칸 번호]
    for (const set of SETS) {
      const img = mannequin[set], frames = base.sets && base.sets[set] && base.sets[set].frames;
      if (!img || img.error || img.w !== SHEET_W || !Array.isArray(frames)) continue;
      for (let f = 0; f < COUNT; f++) {
        const head = frames[f] && frames[f].head;
        if (!head) continue;
        const pose = head.pose || 'N';
        const skull = cellPixels(img, f, 1).filter(([x, y]) => y < head.y && Math.abs(x - head.x) <= 40);
        if (!skull.length) continue;
        // 덮는 그림 픽셀 (칸 좌표)
        const cover = new Set();
        for (const [item, variant] of combo.parts) {
          const himg = await loadImage(item.src);
          if (himg.error) continue;
          for (const part of ['back', 'front']) {
            const r = rectOf(item, variant, pose, part);
            if (!isRect(r)) continue;
            for (let y = 0; y < r[3]; y++) for (let x = 0; x < r[2]; x++) {
              if (alphaAt(himg, r[0] + x, r[1] + y)) cover.add(`${head.x - r[4] + x},${head.y - r[5] + y}`);
            }
          }
        }
        const edge = new Map();
        skull.forEach(([x, y]) => {
          if (pose === 'L') { if (!edge.has(y) || x > edge.get(y)) edge.set(y, x); }
          else if (!edge.has(x) || y < edge.get(x)) edge.set(x, y);
        });
        const bare = [...edge].filter(([a, b]) => !cover.has(pose === 'L' ? `${b},${a}` : `${a},${b}`)).length;
        if (bare) gaps.set(pose, [...(gaps.get(pose) || []), `${set} ${f}번(${bare}px)`]);
      }
    }
    gaps.forEach((list, pose) => fail(8, `${combo.name} · 자세 ${pose}: 두개골 가장자리가 드러남 ${list.slice(0, 5).join(', ')}${list.length > 5 ? ' …' : ''}`));
  }
}

main().then(() => {
  let failed = 0;
  Object.entries(CHECKS).forEach(([k, title]) => {
    if (k === '9') { console.log(`[9] ${title} — 자동 판별 불가, 그림을 눈으로 확인하세요`); return; }
    const list = problems[k];
    console.log(`[${k}] ${title} ${list.length ? '✘' : '✔'}`);
    list.forEach(msg => console.log(`    - ${msg}`));
    failed += list.length;
  });
  console.log(failed ? `\n틀린 곳 ${failed}개` : '\n모든 자동 검사 통과');
  process.exit(failed ? 1 : 0);
}).catch(e => { console.error(e); process.exit(2); });

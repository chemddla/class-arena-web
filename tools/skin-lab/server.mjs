// 학생 외형 디자인 검토실 (선생님 PC에서만 실행)
//   node tools/skin-lab/server.mjs  →  http://127.0.0.1:5180
// 학생이 도감 [🎨 학급 디자인]에서 낸 그림을 학급 서버에서 받아 와서 제미나이로 다듬고 동작 시트를 만든 뒤,
// 선생님이 보고 [출시]하면 assets/sprites/merc/<직업>_st<번호>.webp와 index.html의 STUDENT_DESIGN_SKINS에 넣음.
// 학생 그림·작업 파일은 skin-lab-work/ (git에 올라가지 않음). 출시 후 커밋·푸시하면 배포됨
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { ROOT, JOBS, loadBaseDef, motionGroups, refine, motion, assemble, apiKey, imageModel } from './pipeline.mjs';

const PORT = Number(process.env.SKIN_LAB_PORT) || 5180;
const WORK = path.join(ROOT, 'skin-lab-work');
const INDEX_HTML = path.join(ROOT, 'index.html');
const DB_URL = 'https://class-arena-b4ee3-default-rtdb.firebaseio.com';
fs.mkdirSync(WORK, { recursive: true });

// ---------- 작업 기록 (디자인마다 폴더 하나 + meta.json) ----------
const dirOf = id => path.join(WORK, id.replace(/[^\w-]/g, ''));
const metaPath = id => path.join(dirOf(id), 'meta.json');
const readMeta = id => JSON.parse(fs.readFileSync(metaPath(id), 'utf8'));
const writeMeta = m => fs.writeFileSync(metaPath(m.id), JSON.stringify(m, null, 2));
const busy = {}; // id → 지금 하는 일

function listDesigns() {
  return fs.readdirSync(WORK).filter(d => fs.existsSync(path.join(WORK, d, 'meta.json'))).map(d => {
    const m = readMeta(d);
    const def = loadBaseDef(m.job);
    const groups = motionGroups(def).map(g => ({ ...g, done: fs.existsSync(path.join(dirOf(m.id), `motion_${g.key}.png`)) }));
    const v = f => fs.existsSync(path.join(dirOf(m.id), f)) ? fs.statSync(path.join(dirOf(m.id), f)).mtimeMs : 0;
    return { ...m, busy: busy[m.id] || '', groups, def, files: { design: v(m.designFile), refined: v('refined.png'), sheet: v('sheet.webp') } };
  }).sort((a, b) => (b.at || 0) - (a.at || 0));
}

function saveDataUrl(dir, dataUrl, base) {
  const m = /^data:image\/(png|jpe?g|webp|gif);base64,(.+)$/.exec(dataUrl || '');
  if (!m) throw new Error('그림 형식이 아님');
  const file = `${base}.${m[1] === 'jpeg' ? 'jpg' : m[1]}`;
  fs.writeFileSync(path.join(dir, file), Buffer.from(m[2], 'base64'));
  return file;
}

function addDesign({ id, classCode, studentId, designer, job, title, note, image, at }) {
  if (!JOBS[job]) throw new Error('직업이 이상함');
  if (fs.existsSync(metaPath(id))) return false;
  fs.mkdirSync(dirOf(id), { recursive: true });
  const designFile = saveDataUrl(dirOf(id), image, 'design');
  writeMeta({ id, classCode, studentId, designer: String(designer || '').slice(0, 40), job, title: String(title || '').slice(0, 20), note: String(note || '').slice(0, 120), at: at || Date.now(), designFile, status: 'new', log: [] });
  return true;
}

// 학급 서버에서 새 디자인 받아 오기 (학급 데이터는 학급 코드로 읽을 수 있음)
async function fetchClass(code) {
  code = String(code || '').trim().toUpperCase();
  if (!/^[A-Z0-9_-]{3,16}$/.test(code)) throw new Error('학급 코드가 이상함');
  const res = await fetch(`${DB_URL}/classes/${code}/skinDesigns.json`);
  if (!res.ok) throw new Error(`학급 서버 오류 ${res.status}`);
  const all = (await res.json()) || {};
  let added = 0;
  for (const [studentId, items] of Object.entries(all)) {
    for (const [id, d] of Object.entries(items || {})) {
      if (d && addDesign({ id, classCode: code, studentId, designer: d.name, job: d.job, title: d.title, note: d.note, image: d.image, at: d.at })) added++;
    }
  }
  return added;
}

function log(m, text) { m.log = [...(m.log || []), `${new Date().toLocaleString('ko-KR')} ${text}`].slice(-30); }

// 오래 걸리는 일은 뒤에서 하고 화면은 2초마다 상태를 다시 읽음
function runJob(id, label, fn) {
  if (busy[id]) throw new Error('이미 작업 중');
  busy[id] = label;
  (async () => {
    try { await fn(); }
    catch (e) { const m = readMeta(id); log(m, `❌ ${label}: ${e.message}`); writeMeta(m); console.error(e); }
    finally { delete busy[id]; }
  })();
}

async function doRefine(id) {
  const m = readMeta(id);
  const r = await refine({ job: m.job, title: m.title, note: m.note, designPath: path.join(dirOf(id), m.designFile), outPath: path.join(dirOf(id), 'refined.png') });
  m.chroma = r.chroma;
  m.status = 'refined';
  log(m, `✅ 다듬기 (${r.model})`);
  writeMeta(m);
}
async function doMotion(id, keys) {
  const m = readMeta(id);
  const refinedPath = path.join(dirOf(id), 'refined.png');
  if (!fs.existsSync(refinedPath)) throw new Error('먼저 다듬기를 해 주세요');
  const groups = motionGroups(loadBaseDef(m.job)).filter(g => !keys || keys.includes(g.key));
  for (const g of groups) {
    busy[id] = `동작 그리는 중: ${g.key}`;
    await motion({ job: m.job, group: g, refinedPath, outPath: path.join(dirOf(id), `motion_${g.key}.png`), chroma: m.chroma });
    const mm = readMeta(id); log(mm, `✅ 동작 ${g.key}`); writeMeta(mm);
  }
  await doAssemble(id);
}
async function doAssemble(id) {
  const m = readMeta(id);
  const groupFiles = {};
  motionGroups(loadBaseDef(m.job)).forEach(g => { groupFiles[g.key] = path.join(dirOf(id), `motion_${g.key}.png`); });
  const r = await assemble({ job: m.job, groupFiles, outPath: path.join(dirOf(id), 'sheet.webp') });
  m.status = 'made';
  m.warnings = r.warnings;
  log(m, `✅ 시트 조립${r.warnings.length ? ` (알림 ${r.warnings.length}개)` : ''}`);
  writeMeta(m);
}

// ---------- 출시: 그림 복사 + index.html 목록에 한 줄 ----------
const LIST_START = 'const STUDENT_DESIGN_SKINS = [';
function releasedSkins(html) {
  const i = html.indexOf(LIST_START);
  if (i < 0) throw new Error('index.html에서 STUDENT_DESIGN_SKINS를 찾지 못함');
  const end = html.indexOf('\n    ];', i);
  const body = html.slice(i + LIST_START.length, end);
  return { i, end, list: [...body.matchAll(/^\s*\{ job: '(\w+)', n: (\d+),.*designId: '([\w-]+)'/gm)].map(m => ({ job: m[1], n: Number(m[2]), designId: m[3] })) };
}
function release(id) {
  const m = readMeta(id);
  const sheet = path.join(dirOf(id), 'sheet.webp');
  if (!fs.existsSync(sheet)) throw new Error('시트가 아직 없음');
  let html = fs.readFileSync(INDEX_HTML, 'utf8');
  const { end, list } = releasedSkins(html);
  if (list.some(s => s.designId === m.id)) throw new Error('이미 출시됨');
  const n = Math.max(0, ...list.filter(s => s.job === m.job).map(s => s.n)) + 1;
  fs.copyFileSync(sheet, path.join(ROOT, `assets/sprites/merc/${m.job}_st${n}.webp`));
  const q = v => `'${String(v).replace(/[\\'<>"`]/g, '')}'`;
  const line = `\n      { job: '${m.job}', n: ${n}, classCode: ${q(m.classCode)}, designer: ${q(m.designer)}, title: ${q(m.title)}, designId: ${q(m.id)} },`;
  html = html.slice(0, end) + line + html.slice(end);
  fs.writeFileSync(INDEX_HTML, html);
  m.status = 'released';
  m.released = { n, file: `assets/sprites/merc/${m.job}_st${n}.webp` };
  log(m, `🎉 출시: ${m.released.file}`);
  writeMeta(m);
  return m.released;
}

// ---------- HTTP ----------
const TYPES = { '.html': 'text/html; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.json': 'application/json' };
// base 폴더 밖(../)으로 나가는 경로는 막음
function inside(base, rel) {
  const file = path.resolve(base, rel);
  return file.startsWith(base + path.sep) ? file : '';
}
function sendFile(res, file) {
  if (!file || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
  fs.createReadStream(file).pipe(res);
}
const readBody = req => new Promise((ok, bad) => {
  let s = ''; req.on('data', d => { s += d; if (s.length > 15e6) req.destroy(); });
  req.on('end', () => { try { ok(s ? JSON.parse(s) : {}); } catch (e) { bad(e); } });
});
const json = (res, code, v) => { res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(v)); };

http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  const p = decodeURIComponent(url.pathname);
  try {
    if (req.method === 'GET') {
      if (p === '/') return sendFile(res, path.join(ROOT, 'tools/skin-lab/review.html'));
      if (p.startsWith('/work/')) return sendFile(res, inside(WORK, p.slice(6)));
      if (p.startsWith('/assets/')) return sendFile(res, inside(path.join(ROOT, 'assets'), p.slice(8)));
      if (p === '/api/designs') return json(res, 200, { designs: listDesigns(), hasKey: Boolean(apiKey()), jobs: JOBS });
      if (p === '/api/model') return json(res, 200, { model: await imageModel() });
      res.writeHead(404); return res.end();
    }
    if (req.method !== 'POST') { res.writeHead(405); return res.end(); }
    // 다른 사이트에서 이 주소로 몰래 요청하지 못하게
    if (req.headers['x-skin-lab'] !== '1') return json(res, 403, { error: 'forbidden' });
    const b = await readBody(req);
    if (p === '/api/fetch') return json(res, 200, { added: await fetchClass(b.classCode) });
    if (p === '/api/import') {
      const id = 'd_local_' + Date.now().toString(36);
      addDesign({ id, classCode: String(b.classCode || '').toUpperCase(), studentId: '', designer: b.designer, job: b.job, title: b.title, note: b.note, image: b.image });
      return json(res, 200, { id });
    }
    const id = String(b.id || '');
    if (!fs.existsSync(metaPath(id))) return json(res, 404, { error: '디자인 없음' });
    if (p === '/api/refine') { runJob(id, '다듬는 중', () => doRefine(id)); return json(res, 200, { ok: true }); }
    if (p === '/api/motion') { runJob(id, '동작 그리는 중', () => doMotion(id, b.keys)); return json(res, 200, { ok: true }); }
    if (p === '/api/assemble') { runJob(id, '조립 중', () => doAssemble(id)); return json(res, 200, { ok: true }); }
    if (p === '/api/reject') { const m = readMeta(id); m.status = b.undo ? 'new' : 'rejected'; log(m, b.undo ? '↩️ 반려 취소' : '🚫 반려'); writeMeta(m); return json(res, 200, { ok: true }); }
    if (p === '/api/release') return json(res, 200, release(id));
    res.writeHead(404); res.end();
  } catch (e) {
    console.error(e);
    json(res, 400, { error: e.message });
  }
}).listen(PORT, '127.0.0.1', () => {
  console.log(`🎨 디자인 검토실: http://127.0.0.1:${PORT}`);
  if (!apiKey()) console.log('⚠️ GEMINI_API_KEY가 없어요. tools/skin-lab/.env 에 GEMINI_API_KEY=... 를 넣어 주세요.');
});

#!/usr/bin/env node
/*
 * 최신 main 테스트 서버 (내 컴퓨터 전용)
 *
 * 다른 세션들이 worktree에서 origin/main에 바로 푸시해도, 작업 폴더(Class Arena)는 pull 하기 전까지 옛 코드라
 * /test 에서 새 변경을 바로 못 봄. 이 서버는 전용 worktree(.claude/worktrees/live-main)를
 * 몇 초마다 origin/main으로 맞추고 그 폴더를 그대로 보여 줌 → 푸시하자마자(배포 Actions를 기다리지 않고) 테스트 가능.
 *
 *   node tools/live-main-server.cjs            → http://localhost:5190/test
 *   PORT=5191 LIVE_POLL_MS=5000 node tools/live-main-server.cjs
 *
 * - 작업 폴더의 파일은 건드리지 않음 (전용 worktree만 강제로 origin/main에 맞춤 → 거기서는 편집하지 말 것)
 * - /__live/version : 지금 보여 주는 커밋 (test/index.html이 이걸 보고 "새 버전 도착" 안내를 띄움)
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');

const REPO = path.resolve(__dirname, '..');
const WT = path.join(REPO, '.claude', 'worktrees', 'live-main');
const PORT = Number(process.env.PORT) || 5190;

// --log <파일>: 화면 없이 켤 때(작업 스케줄러) 기록을 파일로 남김. 켤 때마다 새로 씀
const logArg = process.argv.indexOf('--log');
if (logArg > 0 && process.argv[logArg + 1]) {
  const logFile = process.argv[logArg + 1];
  fs.mkdirSync(path.dirname(logFile), { recursive: true });
  const out = fs.createWriteStream(logFile, { flags: 'w' });
  for (const k of ['log', 'warn', 'error']) {
    const orig = console[k].bind(console);
    console[k] = (...a) => { orig(...a); out.write(a.map(String).join(' ') + '\n'); };
  }
  process.on('uncaughtException', (e) => { console.error('[live] 멈춤:', e && e.stack || e); setTimeout(() => process.exit(1), 200); });
}
const POLL_MS = Math.max(2000, Number(process.env.LIVE_POLL_MS) || 5000);

const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.cjs': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8', '.md': 'text/plain; charset=utf-8', '.csv': 'text/csv; charset=utf-8',
  '.png': 'image/png', '.webp': 'image/webp', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
  '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.wav': 'audio/wav',
  '.m4a': 'audio/mp4', '.mp4': 'video/mp4', '.webm': 'video/webm', '.woff': 'font/woff', '.woff2': 'font/woff2',
  '.ttf': 'font/ttf', '.wasm': 'application/wasm',
};

function git(args, cwd = REPO) {
  return new Promise((resolve, reject) => {
    execFile('git', args, { cwd, windowsHide: true, maxBuffer: 1 << 20 }, (err, stdout, stderr) => {
      if (err) { err.message += '\n' + String(stderr || '').trim(); reject(err); } else resolve(String(stdout).trim());
    });
  });
}

let live = { commit: '', subject: '', updatedAt: 0, lastError: '' };

async function ensureWorktree() {
  if (fs.existsSync(path.join(WT, '.git'))) return;
  await git(['fetch', '--quiet', 'origin', 'main']);
  await git(['worktree', 'add', '--detach', '--force', WT, 'origin/main']);
  console.log('[live] 전용 worktree를 만들었음:', WT);
}

let syncing = false;
async function sync() {
  if (syncing) return;
  syncing = true;
  try {
    // 다른 세션이 동시에 fetch하면 잠금 오류가 날 수 있음 → 다음 주기에 다시 시도
    await git(['fetch', '--quiet', 'origin', 'main'], WT);
    const target = await git(['rev-parse', 'origin/main'], WT);
    const head = await git(['rev-parse', 'HEAD'], WT);
    if (target !== head) {
      await git(['checkout', '--quiet', '--force', '--detach', target], WT);
      await git(['clean', '-fdq'], WT);
    }
    if (target !== live.commit) {
      const subject = await git(['log', '-1', '--format=%s', target], WT);
      live = { commit: target, subject, updatedAt: Date.now(), lastError: '' };
      console.log(`[live] ${new Date().toLocaleTimeString()} → ${target.slice(0, 7)} ${subject}`);
    } else live.lastError = '';
  } catch (e) {
    live.lastError = String(e.message || e).split('\n').slice(0, 3).join(' ');
    console.warn('[live] 동기화 실패 (다음 주기에 다시):', live.lastError);
  } finally {
    syncing = false;
  }
}

function send(res, code, body, type = 'text/plain; charset=utf-8') {
  res.writeHead(code, { 'Content-Type': type, 'Cache-Control': 'no-store' });
  res.end(body);
}

const server = http.createServer((req, res) => {
  let urlPath;
  try { urlPath = decodeURIComponent(new URL(req.url, 'http://x').pathname); } catch { return send(res, 400, 'bad url'); }

  if (urlPath === '/__live/version') {
    return send(res, 200, JSON.stringify({ ...live, short: live.commit.slice(0, 7) }), MIME['.json']);
  }

  const file = path.normalize(path.join(WT, urlPath));
  if (!file.startsWith(WT)) return send(res, 403, 'forbidden');
  if (/[\\/]\.git([\\/]|$)/.test(file.slice(WT.length))) return send(res, 404, 'not found');

  fs.stat(file, (err, st) => {
    if (!err && st.isDirectory()) {
      if (!urlPath.endsWith('/')) {
        const q = req.url.includes('?') ? req.url.slice(req.url.indexOf('?')) : '';
        res.writeHead(301, { Location: urlPath + '/' + q });
        return res.end();
      }
      return serveFile(path.join(file, 'index.html'), res);
    }
    if (err) return send(res, 404, 'not found');
    serveFile(file, res);
  });
});

function serveFile(file, res) {
  fs.readFile(file, (err, buf) => {
    if (err) return send(res, 404, 'not found');
    res.writeHead(200, {
      'Content-Type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream',
      'Cache-Control': 'no-store', // 새 커밋이 오면 그림·소리도 바로 새로 받게
    });
    res.end(buf);
  });
}

(async () => {
  await ensureWorktree();
  await sync();
  setInterval(sync, POLL_MS);
  // localhost가 IPv6(::1)로 먼저 연결되는 브라우저가 있어 둘 다 받음 (127.0.0.1만 열면 "사이트에 연결할 수 없음")
  server.listen(PORT, '127.0.0.1', () => {
    console.log(`[live] 최신 main 테스트 서버: http://localhost:${PORT}/test  (origin/main을 ${POLL_MS / 1000}초마다 확인)`);
  });
  const server6 = http.createServer((req, res) => server.emit('request', req, res));
  server6.on('error', (e) => console.warn('[live] IPv6(::1)로는 열지 못함:', e.code || e.message));
  server6.listen(PORT, '::1');
})().catch((e) => { console.error('[live] 시작 실패:', e); process.exit(1); });

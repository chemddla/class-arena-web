// 배포본 그림·소리 주소에 파일 내용 해시를 붙임: node tools/stamp-asset-versions.cjs public
//
// 왜: 배포 사이트는 assets/를 1시간 캐시함(deploy.yml _headers). 그림을 고쳐 칸 크기·배치가 바뀌었는데 주소가 그대로면,
//     브라우저는 옛 그림을 쓰고 게임(index.html, 캐시 안 함)은 새 칸 크기로 잘라서 동작이 깨짐 (2026-11-06 화염술사 등 여러 번).
//     예전에는 그림을 고칠 때마다 손으로 ?v=N을 올렸는데 자주 빠뜨림 → 배포할 때 자동으로.
//
// 하는 일:
//   1. public/assets 아래 모든 파일의 내용 해시(sha1 앞 10자리)를 셈
//   2. public/index.html 안에 글자 그대로 적힌 'assets/....webp' 같은 주소(손으로 붙인 ?v=N 포함)를 'assets/....webp?v=<해시>'로 바꿈
//   3. 코드로 조립하는 주소(`assets/sprites/merc/${job}_sr${n}.webp` 등)는 글자로 찾을 수 없으므로
//      파일 → 해시 표를 window.__ASSET_V로 <head> 맨 앞에 넣음. index.html의 assetVer()가 그림을 불러오는 순간 붙임
// 파일 내용이 그대로면 해시도 그대로라, 바뀐 그림만 새로 받고 나머지는 계속 캐시를 씀.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const root = process.argv[2] || 'public';
const htmlFile = path.join(root, 'index.html');
const assetDir = path.join(root, 'assets');
const EXT = 'webp|png|jpe?g|gif|svg|mp3|ogg|wav|m4a|json|txt|js|css|woff2?';

const hashes = {};
(function walk(dir) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(full);
    else hashes[path.relative(root, full).split(path.sep).join('/')] = crypto.createHash('sha1').update(fs.readFileSync(full)).digest('hex').slice(0, 10);
  }
})(assetDir);

let html = fs.readFileSync(htmlFile, 'utf8');
let stamped = 0;
const literal = new RegExp(`(assets/[A-Za-z0-9_\\-./]+\\.(?:${EXT}))(?:\\?v=[A-Za-z0-9]+)?(?![A-Za-z0-9_\\-./?])`, 'g');
html = html.replace(literal, (all, p) => {
  if (!hashes[p]) return all; // 없는 파일(오타·지워진 그림)은 그대로 둠
  stamped++;
  return `${p}?v=${hashes[p]}`;
});

if (!html.includes('<head>')) throw new Error('index.html에서 <head>를 찾지 못함');
html = html.replace('<head>', `<head>\n<script>window.__ASSET_V=${JSON.stringify(hashes)};</script>`);
fs.writeFileSync(htmlFile, html);
console.log(`그림·소리 ${Object.keys(hashes).length}개 해시 · 글자 그대로 적힌 주소 ${stamped}곳에 ?v=해시를 붙임`);

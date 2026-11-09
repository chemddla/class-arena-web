// 학생 기록 '바뀐 칸만 올리기' 점검 (addSyncDiffPaths): 용병 목록 순서가 바뀌면 처음 어긋난 칸부터만 (2026-11-09)
// node sync-diff.test.cjs [../index.html]
const fs = require('fs'); const assert = require('assert');
const src = fs.readFileSync((process.argv[2] || '../index.html'), 'utf8');
const grab = (from, to) => { const a = src.indexOf(from); const b = src.indexOf(to, a); if (a < 0 || b < 0) throw new Error(from); return src.slice(a, b); };
const fn = grab('    const SYNC_DIFF_MAX_DEPTH', '    // Firebase는 빈 배열');
const canon = grab('    function syncCanon', '    function syncSig') + grab('    function syncSig', '\n    }\n') + '\n    }\n';
const f = new Function('const toFirebaseValue = v => JSON.parse(JSON.stringify(v)); const slimMercForUpload = m => m; const slimUploadValue = v => v;' + canon + fn + ';return { addSyncDiffPaths };')();
let n = 0; const t = (name, fn) => { fn(); n++; console.log('ok', name); };
const m = (id, lv = 1) => ({ id, job: 'mage', level: lv });
const diff = (prev, cur) => { const u = {}; f.addSyncDiffPaths(u, 'r', prev, cur, 1); return u; };
// 서버 사본에 updates를 적용한 결과 (Firebase 배열: 0..n-1 칸)
const apply = (prev, u) => { const o = { ...prev }; Object.entries(u).forEach(([k, v]) => { const i = k.split('/')[1]; if (k === 'r') { Object.keys(o).forEach(x => delete o[x]); Object.assign(o, v); } else if (v === null) delete o[i]; else o[i] = v; }); return Object.keys(o).sort((a, b) => a - b).map(i => o[i]); };

t('끝에 붙이면 그 한 명만', () => assert.deepStrictEqual(diff([m('a'), m('b')], [m('a'), m('b'), m('c')]), { 'r/2': m('c') }));
t('끝에서 빼면 null 한 칸', () => assert.deepStrictEqual(diff([m('a'), m('b'), m('c')], [m('a'), m('b')]), { 'r/2': null }));
t('가운데를 빼면 그 뒤만', () => {
  const prev = [m('a'), m('b'), m('c'), m('d')], cur = [m('a'), m('c'), m('d')];
  const u = diff(prev, cur);
  assert.deepStrictEqual(Object.keys(u), ['r/1', 'r/2', 'r/3']);
  assert.deepStrictEqual(apply(prev, u), cur);
});
t('맨 앞이 바뀌면 예전처럼 통째로', () => assert.deepStrictEqual(Object.keys(diff([m('a'), m('b')], [m('b')])), ['r']));
t('순서가 같으면 바뀐 용병만 (예전 그대로)', () => assert.deepStrictEqual(diff([m('a'), m('b')], [m('a'), m('b', 2)]), { 'r/1': m('b', 2) }));
t('앞쪽 칸 레벨이 바뀌고 끝에 붙여도 둘 다', () => {
  const prev = [m('a'), m('b')], cur = [m('a', 3), m('b'), m('c')];
  const u = diff(prev, cur);
  assert.deepStrictEqual(u, { 'r/2': m('c') , 'r/0': m('a', 3) }); // k=0이 아니므로 칸별
  assert.deepStrictEqual(apply(prev, u), cur);
});
console.log('all', n);

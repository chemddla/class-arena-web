// 러쉬·던전방 AI 자리(rushFill) 저장 점검: 넣기·빼기 때 그 자리 하나만 쓰는지, 예전 배열도 읽는지 (2026-11-09)
// node rush-fill.test.cjs [../index.html]
const fs = require('fs'); const assert = require('assert');
const src = fs.readFileSync((process.argv[2] || '../index.html'), 'utf8');
const grab = (from, to) => { const a = src.indexOf(from); const b = src.indexOf(to, a); if (a < 0 || b < 0) throw new Error(from); return src.slice(a, b); };
const consts = grab('    const ROOM_CLAIM_KEYS', '    function mergeRoomState');
const diff = grab('    function roomDiffPatch', '    async function mergeWriteRoom');
const fill = grab('    const rushFillEntries', '    const RUSH_AI_ADD_GAP_MS');
const f = new Function(consts + diff + fill + ';return { roomDiffPatch, rushFillEntries, rushFillOf, rushFillKeep, rushFillSnap };')();
let n = 0; const t = (name, fn) => { fn(); n++; console.log('ok', name); };
const clone = o => JSON.parse(JSON.stringify(o));
const seat = id => ({ id, name: id, power: 1000, merc: { id: 'm_' + id, job: 'mage' }, snap: { id, name: id, num: 1 } });

t('예전 배열도 순서대로 읽음', () => {
  assert.deepStrictEqual(f.rushFillOf({ rushFill: [seat('a'), null, seat('b')] }).map(x => x.id), ['a', 'b']);
});
t('묶음은 키 글자순(넣은 순서)', () => {
  assert.deepStrictEqual(f.rushFillOf({ rushFill: { tb: seat('b'), ta: seat('a'), a0: seat('z') } }).map(x => x.id), ['z', 'a', 'b']);
});
t('넣기는 새 자리 하나만 씀', () => {
  const base = { roomId: 'r', status: 'waiting', rushFill: { ta: seat('a') } };
  const mine = clone(base); mine.rushFill.tb = seat('b');
  assert.deepStrictEqual(f.roomDiffPatch(base, mine), { 'rushFill/tb': seat('b') });
});
t('빼기는 그 자리만 null', () => {
  const base = { roomId: 'r', rushFill: { ta: seat('a'), tb: seat('b') } };
  const mine = clone(base); mine.rushFill = f.rushFillKeep(base, x => x.id !== 'a');
  assert.deepStrictEqual(f.roomDiffPatch(base, mine), { 'rushFill/ta': null });
});
t('마지막 자리를 빼면 null', () => {
  assert.strictEqual(f.rushFillKeep({ rushFill: { ta: seat('a') } }, () => false), null);
});
t('출발 때 넘친 자리는 키를 지킨 채 자름', () => {
  assert.deepStrictEqual(Object.keys(f.rushFillKeep({ rushFill: { tc: seat('c'), ta: seat('a'), tb: seat('b') } }, () => true, 2)), ['ta', 'tb']);
});
t('예전 배열 → 묶음은 처음 한 번 통째로', () => {
  const base = { roomId: 'r', rushFill: [seat('a')] };
  const mine = clone(base); mine.rushFill = { ...Object.fromEntries(f.rushFillEntries(base)), tb: seat('b') };
  assert.deepStrictEqual(Object.keys(f.roomDiffPatch(base, mine)), ['rushFill']);
});
t('스냅샷 roster는 merc로 채움 (예전 roster는 그대로)', () => {
  const s = seat('a');
  assert.deepStrictEqual(f.rushFillSnap(s).roster, [s.merc]);
  const old = { ...s, snap: { ...s.snap, roster: [{ id: 'x' }] } };
  assert.strictEqual(f.rushFillSnap(old), old.snap);
  assert.strictEqual(f.rushFillSnap({ merc: {} }), null);
});
console.log('all', n);

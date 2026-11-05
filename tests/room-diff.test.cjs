// 방 저장 '바뀐 칸만 update' 점검 (roomDiffPatch): 겨룰 수 있는 변경(자리 차지·players)은 null → transaction으로
// node room-diff.test.cjs [../index.html]
const fs = require('fs'); const assert = require('assert');
const src = fs.readFileSync((process.argv[2] || '../index.html'), 'utf8');
const grab = (from, to) => { const a = src.indexOf(from); const b = src.indexOf(to, a); if (a < 0 || b < 0) throw new Error(from); return src.slice(a, b); };
const consts = grab('    const ROOM_CLAIM_KEYS', '    function mergeRoomState');
const fn = grab('    function roomDiffPatch', '    async function mergeWriteRoom');
const f = new Function(consts + fn + ';return { roomDiffPatch };')();
let n = 0; const t = (name, fn) => { fn(); n++; console.log('ok', name); };
const base = { roomId: 'r', hostId: 'h', guestId: null, status: 'waiting', guestReady: false, gone: { a: 1 }, members: { h: { ready: false }, g: { ready: true } } };
const clone = o => JSON.parse(JSON.stringify(o));

t('준비완료 토글은 그 칸만', () => {
  const mine = clone(base); mine.guestReady = true;
  assert.deepStrictEqual(f.roomDiffPatch(base, mine), { guestReady: true });
});
t('아무것도 안 바뀌면 빈 patch', () => assert.deepStrictEqual(f.roomDiffPatch(base, clone(base)), {}));
t('빈 자리 차지는 transaction으로 (null)', () => {
  const mine = clone(base); mine.guestId = 'A'; mine.guestName = 'A';
  assert.strictEqual(f.roomDiffPatch(base, mine), null);
});
t('자리에서 나가는 것은 update로 (null 값)', () => {
  const b = clone(base); b.guestId = 'A'; b.guestName = 'A';
  const mine = clone(b); mine.guestId = null; delete mine.guestName;
  assert.deepStrictEqual(f.roomDiffPatch(b, mine), { guestId: null, guestName: null });
});
t('players 변경은 transaction으로', () => {
  const b = { ...clone(base), players: [{ id: 'h' }] };
  const mine = clone(b); mine.players.push({ id: 'g' });
  assert.strictEqual(f.roomDiffPatch(b, mine), null);
});
t('학생별 칸(gone·members)은 학생마다 따로', () => {
  const mine = clone(base); delete mine.gone.a; mine.members.h.ready = true; mine.members.x = { ready: false };
  assert.deepStrictEqual(f.roomDiffPatch(base, mine), { 'gone/a': null, 'members/h': { ready: true }, 'members/x': { ready: false } });
});
t('상태 바꾸기(출발)는 바뀐 칸들만', () => {
  const mine = clone(base); mine.status = 'in_battle'; mine.startedAt = 5; mine.fighting = { h: true };
  assert.deepStrictEqual(f.roomDiffPatch(base, mine), { status: 'in_battle', startedAt: 5, 'fighting/h': true });
});
console.log('all', n);

// 실시간 전투 화면의 유닛 칸 '바뀐 값만 보내기' 점검: 방장이 보낸 변화분(d)을 받는 쪽이 되살리면 전체 화면과 똑같아야 함
// node live-delta.test.cjs [../index.html]
const fs = require('fs'); const assert = require('assert');
const src = fs.readFileSync((process.argv[2] || '../index.html'), 'utf8');
const grab = (from, to) => { const a = src.indexOf(from); const b = src.indexOf(to, a); if (a < 0 || b < 0) throw new Error(from); return src.slice(a, b); };
const codec = grab('    function packLiveStatuses(st)', '    function packLiveUnit(u)');
const keys = grab("    const LIVE_UNIT_ST_KEYS = [", "\n");
const mk = new Function(`const liveNum=v=>(typeof v==='number'&&isFinite(v)?v:0);
${keys}
${codec}
return {packLiveStatuses,unpackLiveStatuses,predictLiveUnit,packLiveUnitDelta,unpackLiveUnitDelta,LIVE_UNIT_TICK_DOWN,LIVE_KEYFRAME_MS};`);
const C = mk();
let n = 0; const t = (m, f) => { f(); n++; console.log('ok', m); };

// 유닛 한 명: packLiveUnit과 같은 꼴 (33칸)
const unit = (over = {}) => Object.assign([100.5, 200, 1500, 0, 70, 1, 1, 0.32, 1, 25, 0, '', 6, 0, 12, 0, '2:30,11:573', [1773, 0, 30, 0, 0], 0, 0, 0, 40, 0, 0, 5, 0, 0, 0, 1, 1500, -1, -1, 0], over);
// 방장 쪽: 바탕에서 dt틱 지난 '진짜' 다음 화면 (예측대로 줄어든 것 + 몇 칸은 다르게)
const roundTrip = (base, next, dt) => {
  const d = {}; next.forEach((a, i) => { const c = C.packLiveUnitDelta(C.predictLiveUnit(base[i], dt), a); if (c) d[i] = c; });
  const wire = JSON.parse(JSON.stringify(Object.keys(d).length ? d : null)); // 서버를 거친 꼴
  return { d, got: C.unpackLiveUnitDelta(base, wire, dt) };
};

t('예측대로만 줄어든 화면은 아무것도 보내지 않음', () => {
  const base = [unit(), unit({ 9: 0, 16: '' })];
  const next = [unit({ 9: 19, 12: 0, 14: 6, 16: '2:24,11:567', 17: [1767, 0, 24, 0, 0], 21: 34 }), unit({ 9: 0, 12: 0, 16: '', 14: 6, 17: [1767, 0, 24, 0, 0], 21: 34 })];
  const { d, got } = roundTrip(base, next, 6);
  assert.deepStrictEqual(d, {});
  assert.deepStrictEqual(got, next);
});
t('바뀐 칸만 담아도 되살린 화면이 전체와 같음', () => {
  const base = [unit(), unit()];
  const next = [unit({ 0: 130.2, 1: 190, 2: 1320, 9: 19, 12: 0, 14: 6, 16: '2:24', 17: [1767, 0, 24, 0, 0], 21: 34, 11: 'sniper_stealth', 18: [40, 50, '🏹', 'volley'] }),
    unit({ 5: 0, 9: 19, 12: 0, 14: 6, 16: '2:24,11:567', 17: [1767, 0, 24, 0, 0], 21: 34 })];
  const { d, got } = roundTrip(base, next, 6);
  assert.deepStrictEqual(Object.keys(d[0]).sort(), ['0', '1', '11', '16', '18', '2'].sort());
  assert.deepStrictEqual(Object.keys(d[1]), ['5']);
  assert.deepStrictEqual(got, next);
});
t('Firebase가 번호 키를 배열로 바꿔 줘도(null 칸) 되살림', () => {
  const base = [unit()];
  const next = [unit({ 0: 101, 2: 1400, 9: 25 })]; // dt=0 → 0·2 바뀜 (1은 그대로)
  const d = { 0: { 0: 101, 2: 1400 } };
  const asArray = [[101, null, 1400]]; // 서버가 {0:..,2:..}를 배열로 돌려준 꼴
  assert.deepStrictEqual(C.unpackLiveUnitDelta(base, asArray, 0), next);
  assert.deepStrictEqual(C.unpackLiveUnitDelta(base, d, 0), next);
});
t('dt가 0이거나 바탕이 없을 때도 안전', () => {
  assert.deepStrictEqual(C.predictLiveUnit(unit(), 0), unit());
  assert.deepStrictEqual(C.predictLiveUnit(null, 5), []);
  assert.deepStrictEqual(C.unpackLiveUnitDelta([unit()], null, 3)[0][9], 22);
});
t('상태 틱은 0이 되면 글자에서 빠짐 · 불사 실루엣은 늘어남', () => {
  const p = C.predictLiveUnit(unit({ 16: '2:3,11:50', 31: 10 }), 5);
  assert.strictEqual(p[16], '11:45');
  assert.strictEqual(p[31], 15);
  assert.strictEqual(C.predictLiveUnit(unit({ 31: -1 }), 5)[31], -1);
});
t('죽은 유닛은 아무 칸도 줄지 않음 · 죽는 순간의 값은 그대로 보내짐', () => {
  const dead = unit({ 5: 0, 9: 25, 12: 6, 16: '2:30', 17: [1773, 0, 30, 0, 0] });
  assert.deepStrictEqual(C.predictLiveUnit(dead, 6), dead);
  const { d, got } = roundTrip([unit()], [unit({ 5: 0, 2: 0 })], 6); // 살아 있다가 죽음: 멈춘 칸들이 명시적으로 실림
  assert.deepStrictEqual(got, [unit({ 5: 0, 2: 0 })]);
  assert.ok(Object.keys(d[0]).includes('5') && Object.keys(d[0]).includes('9'));
});
console.log('all', n);

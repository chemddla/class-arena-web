// 거래소(경매·거래 제안) 동기화 점검 (2026-11-10): 목록을 항목(id)별로 올리고 받는지, 겹쳐 누른 거래가 한쪽만 성공하는지
// 가짜 서버 하나에 '기기' 여러 대를 붙여, index.html에서 꺼낸 실제 코드(올리기·받기·marketItemTx)를 그대로 돌림
// node market-sync.test.cjs [../index.html]
const fs = require('fs'); const assert = require('assert');
const src = fs.readFileSync((process.argv[2] || '../index.html'), 'utf8');
const grab = (from, to) => { const a = src.indexOf(from); const b = src.indexOf(to, a); if (a < 0 || b < 0) throw new Error(from); return src.slice(a, b); };
const canon = grab('    function syncCanon', '    // ----- 입력값 정리');
const helpers = grab('    // ----- 경매·거래 제안 목록: 서버에는 항목마다', '    // 서버와 같아진 학생 기록을 기억');
const txCode = grab("    // ----- 경매·거래 제안 한 건을 '서버에서 확인하며'", '    const MARKET_BUSY_TEXT');
const pushCode = grab('        // 항목(id)마다 따로 올림', '        // (c-2) 친구에게 보내는');
const ackCode = grab('          Object.keys(pending.lists).forEach(k => {', '          syncCache.metaExists = true;');
const recvCode = grab('        // 3) 경매장 / 거래 제안: 항목(id)별로', '        if (keepActiveStudent && state.students.some');

const clone = v => (v === undefined || v === null ? null : JSON.parse(JSON.stringify(v)));
const CODE = 'T1';
// ----- 가짜 서버: classes/T1/{auctions,tradeOffers} · 빈 칸은 Firebase처럼 사라짐 -----
function makeServer() {
  const lists = { auctions: null, tradeOffers: null };
  const slot = path => { const p = path.split('/'); assert.strictEqual(p[0], 'classes'); assert.strictEqual(p[1], CODE); return { kind: p[2], key: p[3] }; };
  const put = (kind, key, v) => {
    if (key === undefined) { lists[kind] = v === null ? null : clone(v); return; } // 목록 전체 (예전 버전 탭)
    if (Array.isArray(lists[kind])) { const o = {}; lists[kind].forEach((x, i) => { if (x != null) o[i] = x; }); lists[kind] = o; }
    if (!lists[kind]) lists[kind] = {};
    if (v === null) delete lists[kind][key]; else lists[kind][key] = clone(v);
    if (!Object.keys(lists[kind]).length) lists[kind] = null;
  };
  const get = (kind, key) => (key === undefined ? lists[kind] : (lists[kind] ? lists[kind][key] : undefined));
  return {
    lists,
    writes: [],
    update(u) { this.writes.push(Object.keys(u)); Object.entries(u).forEach(([path, v]) => { const s = slot(path); put(s.kind, s.key, v); }); },
    read() { return { auctions: clone(lists.auctions), tradeOffers: clone(lists.tradeOffers) }; },
    oldTabWrites(kind, arr) { put(kind, undefined, arr); }, // 예전 버전 탭: 목록 전체를 배열로 덮어씀
    ids(kind) { const l = lists[kind]; return (l ? Object.values(l) : []).filter(Boolean).map(x => x.id).sort(); },
    item(kind, id) { const l = lists[kind]; return (l ? Object.values(l) : []).find(x => x && x.id === id) || null; },
    db: { ref: path => ({ transaction: async fn => { const s = slot(path); const next = fn(clone(get(s.kind, s.key))); if (next === undefined) return { committed: false }; put(s.kind, s.key, next); return { committed: true }; } }) }
  };
}
// ----- 기기 한 대: index.html의 코드를 그대로 넣어 만든 올리기(push)·받기(recv)·한 건 거래(tx) -----
const makeDevice = new Function('server', 'code', `
  let state = { auctions: [], tradeOffers: [], students: [] };
  let syncCache = { auctions: undefined, tradeOffers: undefined };
  let online = true;
  const normalizeMercForSync = m => m;
  const deepCleanStrings = o => (typeof o === 'string' ? o.replace(/[<>"'\`]/g, '') : Array.isArray(o) ? o.map(deepCleanStrings) : (o && typeof o === 'object' ? (Object.keys(o).forEach(k => { o[k] = deepCleanStrings(o[k]); }), o) : o));
  const StudentPw = { ready: () => online, code: () => code, db: () => server.db };
  ${canon}
  ${helpers}
  ${txCode}
  function push(creating = false) {
    const updates = {}, base = 'classes/' + code, pending = { lists: {} };
    ${pushCode}
    if (Object.keys(updates).length) server.update(updates);
    ${ackCode}
    return updates;
  }
  function recv(force = false) {
    const data = server.read();
    ${recvCode}
  }
  return { get state() { return state; }, get cache() { return syncCache; }, push, recv, tx: marketItemTx, setOnline(v) { online = v; }, ids: k => state[k].map(x => x.id).sort() };
`);
const device = (server, loaded = true) => { const d = makeDevice(server, CODE); if (loaded) d.recv(true); return d; };

let n = 0; const tests = [];
const t = (name, fn) => tests.push([name, fn]);
const auc = (id, extra = {}) => ({ id, sellerId: 's1', merc: { id: 'm_' + id, job: 'mage', level: 3, name: '용병' }, startBid: 200, currentBid: 200, highestBidderId: null, endsAt: 9e15, ...extra });
const offer = (id, extra = {}) => ({ id, buyerId: 'b1', sellerId: 's1', mercId: 'm1', offerPrice: 500, escrow: true, ...extra });
const bid = (who, amount) => cur => { const min = cur.highestBidderId ? cur.currentBid + 50 : cur.startBid; return amount < min ? undefined : { ...cur, currentBid: amount, highestBidderId: who }; };
const take = () => null;

t('두 학생이 거의 동시에 출품해도 둘 다 남음 (예전엔 나중 저장이 앞의 것을 지움)', () => {
  const S = makeServer(), A = device(S), B = device(S);
  A.state.auctions.unshift(auc('auc_a_1000')); B.state.auctions.unshift(auc('auc_b_2000'));
  A.push(); B.push();
  assert.deepStrictEqual(S.ids('auctions'), ['auc_a_1000', 'auc_b_2000']);
});
t('올릴 때 바뀐 항목 칸만 쓰고, 다시 올리면 아무것도 안 씀', () => {
  const S = makeServer(), A = device(S);
  A.state.auctions.unshift(auc('auc_a_1000')); A.state.auctions.unshift(auc('auc_a_1100'));
  assert.deepStrictEqual(Object.keys(A.push()).sort(), ['classes/T1/auctions/auc_a_1000', 'classes/T1/auctions/auc_a_1100']);
  assert.deepStrictEqual(A.push(), {});
  A.state.auctions.find(x => x.id === 'auc_a_1000').startBid = 300;
  assert.deepStrictEqual(Object.keys(A.push()), ['classes/T1/auctions/auc_a_1000']);
  A.state.auctions = A.state.auctions.filter(x => x.id !== 'auc_a_1100');
  assert.deepStrictEqual(A.push(), { 'classes/T1/auctions/auc_a_1100': null });
  assert.deepStrictEqual(S.ids('auctions'), ['auc_a_1000']);
});
t('한 학생이 자기 경매를 고치는 사이 다른 학생의 다른 경매 입찰이 지워지지 않음', () => {
  const S = makeServer(), A = device(S);
  A.state.auctions.push(auc('auc_a_1000'), auc('auc_b_2000', { sellerId: 's2' })); A.push();
  const B = device(S);
  A.state.auctions.find(x => x.id === 'auc_a_1000').endsAt = 123;       // A: 아직 안 올린 변경
  B.state.auctions.find(x => x.id === 'auc_b_2000').currentBid = 900; B.push(); // B: 그 사이 서버에 올림
  A.push();
  assert.strictEqual(S.item('auctions', 'auc_b_2000').currentBid, 900);
  assert.strictEqual(S.item('auctions', 'auc_a_1000').endsAt, 123);
});
t('받을 때: 내가 안 올린 변경은 지키고 나머지는 서버 값으로, 새 것이 앞에', () => {
  const S = makeServer(), A = device(S);
  A.state.auctions.push(auc('auc_a_1000'), auc('auc_b_2000')); A.push();
  const B = device(S);
  A.state.auctions.find(x => x.id === 'auc_a_1000').startBid = 333;   // 고침 (미전송)
  A.state.auctions.unshift(auc('auc_c_3000'));                         // 새로 올릴 것 (미전송)
  B.state.auctions.find(x => x.id === 'auc_b_2000').currentBid = 900; B.state.auctions.unshift(auc('auc_d_4000')); B.push();
  A.recv();
  assert.deepStrictEqual(A.state.auctions.map(x => x.id), ['auc_d_4000', 'auc_c_3000', 'auc_b_2000', 'auc_a_1000']);
  assert.strictEqual(A.state.auctions.find(x => x.id === 'auc_a_1000').startBid, 333);
  assert.strictEqual(A.state.auctions.find(x => x.id === 'auc_b_2000').currentBid, 900);
  assert.deepStrictEqual(Object.keys(A.push()).sort(), ['classes/T1/auctions/auc_a_1000', 'classes/T1/auctions/auc_c_3000']);
});
t('받을 때: 내가 지운 것(미전송)은 되살아나지 않고, 남이 지운 것은 사라짐', () => {
  const S = makeServer(), A = device(S);
  A.state.auctions.push(auc('auc_a_1000'), auc('auc_b_2000'), auc('auc_c_3000')); A.push();
  const B = device(S);
  A.state.auctions = A.state.auctions.filter(x => x.id !== 'auc_a_1000'); // 내가 지움 (미전송)
  B.state.auctions = B.state.auctions.filter(x => x.id !== 'auc_b_2000'); B.push(); // 남이 지움
  A.recv();
  assert.deepStrictEqual(A.ids('auctions'), ['auc_c_3000']);
  assert.deepStrictEqual(A.push(), { 'classes/T1/auctions/auc_a_1000': null });
  assert.deepStrictEqual(S.ids('auctions'), ['auc_c_3000']);
});
t('예전에 배열로 올라간 항목은 0·1 칸 그대로 고치고, 새 항목은 id 칸', () => {
  const S = makeServer(); S.oldTabWrites('auctions', [auc('auc_a_1000'), auc('auc_b_2000')]);
  const A = device(S);
  assert.deepStrictEqual(A.cache.auctions.keys, { auc_a_1000: '0', auc_b_2000: '1' });
  A.state.auctions.find(x => x.id === 'auc_b_2000').currentBid = 700; A.state.auctions.unshift(auc('auc_c_3000'));
  assert.deepStrictEqual(Object.keys(A.push()).sort(), ['classes/T1/auctions/1', 'classes/T1/auctions/auc_c_3000']);
  assert.deepStrictEqual(S.ids('auctions'), ['auc_a_1000', 'auc_b_2000', 'auc_c_3000']);
  const B = device(S);
  assert.deepStrictEqual(B.ids('auctions'), ['auc_a_1000', 'auc_b_2000', 'auc_c_3000']);
  assert.strictEqual(B.state.auctions.find(x => x.id === 'auc_b_2000').currentBid, 700);
});
t('서버 목록을 아직 못 받은 기기는 올리지 않음 (새 학급을 만들 때만 올림)', () => {
  const S = makeServer(); S.oldTabWrites('auctions', [auc('auc_a_1000')]);
  const A = device(S, false);
  A.state.auctions = [auc('auc_old_500')]; // 이 기기에 남아 있던 예전 목록
  assert.deepStrictEqual(A.push(), {});
  assert.deepStrictEqual(S.ids('auctions'), ['auc_a_1000']);
  const S2 = makeServer(), C = device(S2, false);
  C.state.auctions = [auc('auc_new_900')];
  assert.deepStrictEqual(Object.keys(C.push(true)), ['classes/T1/auctions/auc_new_900']);
});
t('칸 이름으로 못 쓰는 id는 올리지 않음', () => {
  const S = makeServer(), A = device(S);
  A.state.auctions.push(auc('bad/id'), auc('bad.id'), { ...auc('x'), id: 7 });
  assert.deepStrictEqual(A.push(), {});
});
t('같은 경매에 두 학생이 동시에 입찰: 한 명만 성공하고, 환불 기준(before)은 서버에 있던 입찰', async () => {
  const S = makeServer(), A = device(S);
  A.state.auctions.push(auc('auc_a_1000', { currentBid: 500, highestBidderId: 'c' })); A.push();
  const B = device(S), C = device(S); // 둘 다 500으로 알고 있음
  const r1 = await B.tx('auctions', 'auc_a_1000', bid('b', 600));
  const r2 = await C.tx('auctions', 'auc_a_1000', bid('d', 620)); // 서버는 이미 600 → 최소 650
  assert.strictEqual(r1.ok, true); assert.strictEqual(r1.before.highestBidderId, 'c'); assert.strictEqual(r1.before.currentBid, 500);
  assert.strictEqual(r2.ok, false);
  assert.strictEqual(S.item('auctions', 'auc_a_1000').highestBidderId, 'b');
  const r3 = await C.tx('auctions', 'auc_a_1000', bid('d', 700));
  assert.strictEqual(r3.ok, true); assert.strictEqual(r3.before.highestBidderId, 'b'); assert.strictEqual(r3.before.currentBid, 600); // b에게 600 환불
  assert.deepStrictEqual(B.push(), {}); assert.deepStrictEqual(C.push(), {}); // 거래한 항목을 저장이 다시 덮어쓰지 않음
});
t('구매자의 취소와 판매자의 수락이 겹치면 한쪽만 제안을 빼냄 (환불과 거래가 함께 일어나지 않음)', async () => {
  const S = makeServer(), A = device(S);
  A.state.tradeOffers.unshift(offer('offer_a_1000')); A.push();
  const buyer = device(S), seller = device(S);
  const r1 = await buyer.tx('tradeOffers', 'offer_a_1000', take);
  const r2 = await seller.tx('tradeOffers', 'offer_a_1000', take);
  assert.strictEqual(r1.ok, true); assert.strictEqual(r1.before.offerPrice, 500);
  assert.strictEqual(r2.ok, false); assert.strictEqual(r2.before, null);
  assert.deepStrictEqual(seller.ids('tradeOffers'), []); // 서버에 없음이 확인되면 내 목록에서도 치움
  assert.deepStrictEqual(seller.push(), {});
});
t('경매 취소와 입찰이 겹침: 입찰이 먼저면 취소가 그 입찰자를 받아 환불, 취소가 먼저면 입찰 실패', async () => {
  let S = makeServer(), A = device(S);
  A.state.auctions.push(auc('auc_a_1000')); A.push();
  let bidder = device(S), seller = device(S);
  await bidder.tx('auctions', 'auc_a_1000', bid('b', 300));
  let r = await seller.tx('auctions', 'auc_a_1000', take); // 판매자 화면은 입찰 없음으로 알고 있음
  assert.strictEqual(r.ok, true); assert.strictEqual(r.before.highestBidderId, 'b'); assert.strictEqual(r.before.currentBid, 300);
  S = makeServer(); A = device(S); A.state.auctions.push(auc('auc_a_1000')); A.push();
  bidder = device(S); seller = device(S);
  await seller.tx('auctions', 'auc_a_1000', take);
  r = await bidder.tx('auctions', 'auc_a_1000', bid('b', 300));
  assert.strictEqual(r.ok, false);
  assert.deepStrictEqual(S.ids('auctions'), []);
});
t('예전 버전 탭이 목록을 다시 써서 칸이 밀리면 엉뚱한 항목을 건드리지 않고, 다시 받은 뒤에는 됨', async () => {
  const S = makeServer(); S.oldTabWrites('auctions', [auc('auc_a_1000'), auc('auc_b_2000')]);
  const A = device(S); // auc_b_2000 = 칸 1
  S.oldTabWrites('auctions', [auc('auc_c_3000'), auc('auc_a_1000'), auc('auc_b_2000')]); // 칸 1 = auc_a_1000이 됨
  let r = await A.tx('auctions', 'auc_b_2000', bid('b', 300));
  assert.strictEqual(r.ok, false);
  assert.strictEqual(S.item('auctions', 'auc_a_1000').highestBidderId, null);
  A.recv();
  r = await A.tx('auctions', 'auc_b_2000', bid('b', 300));
  assert.strictEqual(r.ok, true);
  assert.strictEqual(S.item('auctions', 'auc_b_2000').highestBidderId, 'b');
});
t('서버 없는 학급(이 기기에서만)은 바로 처리', async () => {
  const S = makeServer(), A = device(S, false); A.setOnline(false);
  A.state.auctions = [auc('auc_a_1000')];
  const r = await A.tx('auctions', 'auc_a_1000', bid('b', 300));
  assert.strictEqual(r.ok, true); assert.strictEqual(r.before.currentBid, 200); assert.strictEqual(A.state.auctions[0].currentBid, 300);
  assert.strictEqual((await A.tx('auctions', 'auc_a_1000', bid('c', 310))).ok, false);
  assert.strictEqual((await A.tx('auctions', 'auc_a_1000', take)).ok, true);
  assert.deepStrictEqual(A.state.auctions, []);
  assert.deepStrictEqual(S.writes, []);
});
t('남이 보낸 글자의 < > 따옴표는 받을 때 지움', () => {
  const S = makeServer(); S.oldTabWrites('tradeOffers', [offer('offer_a_1000', { buyerName: '<img src=x onerror="a()">' })]);
  const A = device(S);
  assert.strictEqual(/[<>"'`]/.test(A.state.tradeOffers[0].buyerName), false);
});

(async () => {
  for (const [name, fn] of tests) { await fn(); n++; console.log('ok', name); }
  console.log('all', n);
})().catch(e => { console.error(e); process.exit(1); });

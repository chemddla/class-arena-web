// 학급 DB 변경 스트림 집계 (수업 중 트래픽 실측용)
// 받기: timeout 272 curl -s -N -H "Accept: text/event-stream" "https://class-arena-b4ee3-default-rtdb.firebaseio.com/classes/<학급코드>.json" > 파일
// 집계: node tools/traffic-sse-agg.js <파일> 270
const fs = require('fs');
const txt = fs.readFileSync(process.argv[2], 'utf8'); const secs = Number(process.argv[3]) || 270;
const evs = []; let ev = null;
txt.split(/\r?\n/).forEach(l => { if (l.startsWith('event:')) ev = { type: l.slice(6).trim() }; else if (l.startsWith('data:') && ev) { ev.raw = l.slice(5).trim(); evs.push(ev); ev = null; } });
const types = {}; evs.forEach(e => { types[e.type] = (types[e.type] || 0) + 1; });
const all = evs.filter(e => e.type === 'put' || e.type === 'patch').map(e => { let d; try { d = JSON.parse(e.raw); } catch (x) { return null; } d.bytes = Buffer.byteLength(e.raw); d.type = e.type; return d; }).filter(Boolean);
const root = all[0].data || {}, rest = all.slice(1);
const sz = v => (v == null ? 0 : Buffer.byteLength(JSON.stringify(v)));
const out = { types, snapshot: all[0].bytes, changes: rest.length, bytes: rest.reduce((s, d) => s + d.bytes, 0) };
out.bps = Math.round(out.bytes / secs);
out.nodes = Object.fromEntries(Object.keys(root).map(k => [k, sz(root[k])]).sort((a, b) => b[1] - a[1]));
out.students = Object.keys(root.students || {}).length;
out.minBuild = root.meta && root.meta.minBuild;
const shape = l => (l == null ? 'none' : Array.isArray(l) ? `array(${l.filter(Boolean).length})` : `object(${Object.keys(l).length})`);
out.auctions = shape(root.auctions); out.tradeOffers = shape(root.tradeOffers);
// 낱개 쓰기로 풀기: [경로, 값, 바이트, 시각]
const writes = [];
rest.forEach(d => { if (d.path === '/') Object.entries(d.data || {}).forEach(([k, v]) => writes.push([k.split('/').filter(Boolean), v, sz(v) + k.length + 4])); else writes.push([d.path.split('/').filter(Boolean), d.data, d.bytes]); });
const top = {};
const roomKind = id => String(id || '').replace(/_stu_.*$/, '').replace(/_\d{10,}.*$/, '').replace(/_[0-9a-z]{4,6}$/, '');
writes.forEach(([p, v, b]) => { const k = p[0] === 'pvp_live' ? `pvp_live/${roomKind(p[1])}/${p[2] || ''}` : p[0] === 'students' ? `students/*/${p[2] || '(통째)'}` : p[0] === 'studentPrivate' ? `studentPrivate/*/${p[2] || ''}` : p[0] === 'minigames' ? `minigames/${/_vl$/.test(p[1]) ? 'vl' : /_pc$/.test(p[1]) ? 'pc' : 'board'}` : p[0] + (p[1] && ['meta', 'world_boss'].includes(p[0]) ? '/' + p[1] : ''); const o = top[k] || (top[k] = { n: 0, b: 0 }); o.n++; o.b += b; });
out.top = Object.entries(top).sort((a, b) => b[1].b - a[1].b).slice(0, 26).map(([k, o]) => `${k}: ${o.n}건 ${o.b}B (${Math.round(o.b / secs)}B/s)`);
// 방별 화면
const rooms = {};
writes.forEach(([p, v, b]) => {
  if (p[0] !== 'pvp_live' || !p[1] || /_index$|^tower_help$/.test(p[1])) return;
  const r = rooms[p[1]] || (rooms[p[1]] = { frames: [], init: [], input: 0, inputB: 0, other: {}, stub: 0, sb: 0, book: 0, x35: 0, units: 0 });
  const c = p[2] || '(room)';
  if (c === 'frame' && p.length === 3 && v && typeof v === 'object') { r.frames.push({ at: v.at, b, key: Array.isArray(v.u), parts: v }); if (Array.isArray(v.u)) v.u.forEach(u => { if (Array.isArray(u)) { r.units++; if (u.length > 35 && u[35]) r.x35++; } }); }
  else if (c === 'init' && p.length === 3 && v) { r.init.push({ b, n: Array.isArray(v.units) ? v.units.length : 0 }); (v.units || []).forEach(u => { if (u && u.k === 1) r.stub++; if (u && u.sb) r.sb++; if (u && u.skillBook) r.book++; }); }
  else if (c === 'input' || c === 'inputs') { r.input++; r.inputB += b; }
  else { const o = r.other[c] || (r.other[c] = { n: 0, b: 0 }); o.n++; o.b += b; }
});
out.rooms = Object.entries(rooms).map(([id, r]) => {
  const f = r.frames.filter(x => typeof x.at === 'number').sort((a, b) => a.at - b.at);
  const gaps = f.slice(1).map((x, i) => x.at - f[i].at).filter(g => g > 0 && g < 5000);
  const hist = { '≤200': 0, '200~400': 0, '400~700': 0, '>700': 0 };
  gaps.forEach(g => { hist[g <= 200 ? '≤200' : g <= 400 ? '200~400' : g <= 700 ? '400~700' : '>700']++; });
  const span = f.length > 1 ? (f[f.length - 1].at - f[0].at) / 1000 : 0;
  const pb = {}; r.frames.forEach(x => Object.keys(x.parts).forEach(k => { pb[k] = (pb[k] || 0) + sz(x.parts[k]) + k.length + 3; }));
  const tot = Object.values(pb).reduce((s, v) => s + v, 0) || 1;
  return { room: id.slice(0, 34), frames: r.frames.length, sec: Math.round(span), avgFrame: r.frames.length ? Math.round(r.frames.reduce((s, x) => s + x.b, 0) / r.frames.length) : 0, key: r.frames.filter(x => x.key).length, gaps: hist,
    parts: Object.entries(pb).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([k, v]) => `${k} ${Math.round(v / tot * 100)}%`).join(' '),
    init: r.init.length ? `${r.init.length}번 평균 ${Math.round(r.init.reduce((s, x) => s + x.b, 0) / r.init.length)}B · 자리표시 ${r.stub} · sb ${r.sb} · skillBook ${r.book}` : '', x35: r.units ? `${r.x35}/${r.units}` : '',
    input: r.input ? `${r.input}건 평균 ${Math.round(r.inputB / r.input)}B (${(r.input / Math.max(1, span || secs)).toFixed(1)}건/s)` : '', other: Object.entries(r.other).map(([k, o]) => `${k} ${o.n}건 ${o.b}B`).join(' · ') };
}).sort((a, b) => b.frames - a.frames).slice(0, 14);
// 나만 쓰는 칸 누수 · 늘 받는 경로
const PRIV = ['recruitPool', 'codex', 'dailyEquipShop', 'mgRewardedIds', 'dailyMission', 'dailyRewards', 'quizBook', 'petDex', 'mercStorage', 'avatarBox'];
let leak = 0; const leakBy = {};
writes.filter(([p]) => p[0] === 'students').forEach(([p, v, b]) => { if (PRIV.includes(p[2])) { leak += b; leakBy[p[2]] = (leakBy[p[2]] || 0) + 1; } });
out.privateLeak = { bytes: leak, by: leakBy };
const always = ['students', 'profiles', 'auctions', 'tradeOffers', 'meta', 'pvp_rooms', 'raid_rooms', 'minigame_rooms', 'world_boss', 'invites', 'global_chat'];
const ab = {}; let at = 0;
writes.forEach(([p, v, b]) => { const k = p[0] === 'pvp_live' && /_index$|^tower_help$/.test(p[1] || '') ? `pvp_live/${p[1]}` : p[0]; if (always.includes(k) || /^pvp_live\//.test(k)) { ab[k] = (ab[k] || 0) + b; at += b; } });
out.always = { bps: Math.round(at / secs), by: Object.entries(ab).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${v}B`) };
// 이상 징후: 관전자 직접 연결·kf·rtc·경매 쓰기·큰 쓰기
const sig = { rtc: 0, kf: 0, kfI: 0, watchR: 0, auctionWrites: [], bigWrites: [], unknownTop: [] };
writes.forEach(([p, v, b]) => { const path = p.join('/');
  if (/\/rtc(\/|$)/.test(path)) sig.rtc++; if (/\/kf\//.test(path)) { if (/_i$/.test(path)) sig.kfI++; else sig.kf++; }
  if (/watchers|spectators/.test(path) && v && JSON.stringify(v).includes('"r":1')) sig.watchR++;
  if (p[0] === 'auctions' || p[0] === 'tradeOffers') sig.auctionWrites.push(`${p.slice(0, 3).join('/').slice(0, 50)} ${v === null ? '삭제' : b + 'B'}`);
  if (b > 20000) sig.bigWrites.push(`${path.replace(/stu_[0-9a-z_]+/g, '*').slice(0, 60)} ${b}B`);
  if (!['students', 'studentPrivate', 'profiles', 'auctions', 'tradeOffers', 'meta', 'pvp_rooms', 'raid_rooms', 'minigame_rooms', 'minigames', 'world_boss', 'world_boss_live', 'invites', 'global_chat', 'room_chats', 'pvp_live', 'transfers', 'home_live', 'pvp_squads', 'skinDesigns', 'skins', 'skinSheets'].includes(p[0])) sig.unknownTop.push(p[0]);
});
sig.unknownTop = [...new Set(sig.unknownTop)]; sig.bigWrites = sig.bigWrites.slice(0, 12); sig.auctionWrites = sig.auctionWrites.slice(0, 12);
out.signals = sig;
console.log(JSON.stringify(out, null, 1));

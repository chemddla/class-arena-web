// 테스트용 가짜 실시간 DB: 같은 브라우저의 탭끼리 BroadcastChannel로 값을 주고받음 (Firebase 없이 실시간 결투·관전을 시험할 때)
// 사용법(각 탭 콘솔): 이 파일 내용을 실행한 뒤 setupMockClassTab('학생id')
window.__mockDb = (() => {
  const ch = new BroadcastChannel('class-arena-mockdb');
  let tree = {};
  const listeners = [];
  const keys = p => String(p || '').split('/').filter(Boolean);
  const clone = v => (v === undefined || v === null ? null : JSON.parse(JSON.stringify(v)));
  const get = p => keys(p).reduce((o, k) => (o == null ? undefined : o[k]), tree);
  const snap = p => ({ val: () => clone(get(p)), exists: () => get(p) !== undefined, key: keys(p).pop() });
  const related = (a, b) => { const x = keys(a).join('/'), y = keys(b).join('/'); return x === y || x.startsWith(y + '/') || y.startsWith(x + '/') || !y || !x; };
  // child_added / child_changed: 바뀐 자식만 알림 (펫 배구·펫 러닝 협동이 씀) · value: 그 경로 전체
  const childSnap = (base, k) => { const cp = keys(base).concat(k).join('/'); return { key: k, val: () => clone(get(cp)), exists: () => get(cp) !== undefined }; };
  const fireChild = (l, p) => {
    const lk = keys(l.path), pk = keys(p);
    const obj = get(l.path);
    const names = pk.length > lk.length ? [pk[lk.length]] : Object.keys(obj && typeof obj === 'object' ? obj : {});
    names.forEach(k => {
      const exists = obj && typeof obj === 'object' && obj[k] !== undefined;
      const seen = l.seen.has(k);
      if (!exists) { l.seen.delete(k); return; }
      if (!seen) { l.seen.add(k); if (l.ev === 'child_added') l.cb(childSnap(l.path, k)); }
      else if (l.ev === 'child_changed') l.cb(childSnap(l.path, k));
    });
  };
  const fire = p => listeners.slice().forEach(l => { if (!related(p, l.path)) return; if (l.ev === 'child_added' || l.ev === 'child_changed') fireChild(l, p); else l.cb(snap(l.path)); });
  const putLocal = (p, v) => {
    const ks = keys(p);
    let o = tree;
    for (let i = 0; i < ks.length - 1; i++) {
      if (typeof o[ks[i]] !== 'object' || o[ks[i]] === null) o[ks[i]] = {};
      o = o[ks[i]];
    }
    if (v === null || v === undefined) delete o[ks[ks.length - 1]];
    else o[ks[ks.length - 1]] = clone(v);
  };
  const setLocal = (p, v) => { putLocal(p, v); fire(p); };
  // update는 Firebase처럼 한꺼번에: 모든 칸을 바꾼 뒤 한 번만 알림 (하나씩 알리면 status만 먼저 보고 startedAt 없이 시작하는 일이 생김)
  const updateLocal = (p, o) => { Object.entries(o || {}).forEach(([k, v]) => putLocal(keys(p).concat(keys(k)).join('/'), v)); fire(p); };
  ch.onmessage = e => {
    const m = e.data;
    if (m.t === 'set') setLocal(m.p, m.v);
    else if (m.t === 'upd') updateLocal(m.p, m.o);
    else if (m.t === 'req') ch.postMessage({ t: 'full', tree });
    else if (m.t === 'full' && !Object.keys(tree).length && m.tree && Object.keys(m.tree).length) {
      tree = m.tree;
      listeners.slice().forEach(l => { if (l.ev === 'child_added' || l.ev === 'child_changed') fireChild(l, l.path); else l.cb(snap(l.path)); });
    }
  };
  ch.postMessage({ t: 'req' });
  const ref = (p = '') => ({
    path: p,
    child: c => ref(keys(p).concat(keys(c)).join('/')),
    set(v) { setLocal(p, v); ch.postMessage({ t: 'set', p, v: clone(v) }); return Promise.resolve(); },
    remove() { return this.set(null); },
    update(o) { const v = clone(o) || {}; updateLocal(p, v); ch.postMessage({ t: 'upd', p, o: v }); return Promise.resolve(); },
    on(ev, cb) {
      const l = { path: p, cb, ev, seen: new Set() };
      listeners.push(l);
      setTimeout(() => { if (!listeners.includes(l)) return; if (ev === 'child_added' || ev === 'child_changed') fireChild(l, p); else cb(snap(p)); }, 0);
      return cb;
    },
    off() { for (let i = listeners.length - 1; i >= 0; i--) if (listeners[i].path === p) listeners.splice(i, 1); },
    once() { return Promise.resolve(snap(p)); },
    // Firebase transaction 흉내 (보스 레이드가 씀): fn이 undefined를 돌려주면 그대로 둠
    transaction(fn) { const next = fn(clone(get(p))); if (next === undefined) return Promise.resolve({ committed: false, snapshot: snap(p) }); return this.set(next).then(() => ({ committed: true, snapshot: snap(p) })); },
    limitToLast() { return this; },
    orderByChild() { return this; },
    onDisconnect: () => ({ remove: () => Promise.resolve(), set: () => Promise.resolve(), cancel: () => Promise.resolve() })
  });
  return { ref };
})();

window.setupMockClassTab = function (studentId) {
  suppressRemoteClassPush = true;
  RealtimePvpService.initFirebaseClientSafe = () => window.__mockDb;
  if (typeof armHostRoomAutoCleanup === 'function') armHostRoomAutoCleanup = () => {};
  state.activeStudentId = studentId;
  document.getElementById('mainAppShell').classList.remove('hidden');
  document.getElementById('landingPageView').classList.add('hidden');
  document.querySelector('[onclick="switchStudentTab(\'pvp\')"]')?.click();
  switchPvpSubMode('realtime');
  currentSubscribedSubCode = null;
  subscribeToInteractiveChannels(String(state.classCode || 'ARENA1').toUpperCase(), window.__mockDb);
  return getActiveStudent().name;
};

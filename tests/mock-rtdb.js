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
  const fire = p => listeners.slice().forEach(l => { if (related(p, l.path)) l.cb(snap(l.path)); });
  const setLocal = (p, v) => {
    const ks = keys(p);
    let o = tree;
    for (let i = 0; i < ks.length - 1; i++) {
      if (typeof o[ks[i]] !== 'object' || o[ks[i]] === null) o[ks[i]] = {};
      o = o[ks[i]];
    }
    if (v === null || v === undefined) delete o[ks[ks.length - 1]];
    else o[ks[ks.length - 1]] = clone(v);
    fire(p);
  };
  ch.onmessage = e => {
    const m = e.data;
    if (m.t === 'set') setLocal(m.p, m.v);
    else if (m.t === 'req') ch.postMessage({ t: 'full', tree });
    else if (m.t === 'full' && !Object.keys(tree).length && m.tree && Object.keys(m.tree).length) {
      tree = m.tree;
      listeners.slice().forEach(l => l.cb(snap(l.path)));
    }
  };
  ch.postMessage({ t: 'req' });
  const ref = (p = '') => ({
    path: p,
    child: c => ref(keys(p).concat(keys(c)).join('/')),
    set(v) { setLocal(p, v); ch.postMessage({ t: 'set', p, v: clone(v) }); return Promise.resolve(); },
    remove() { return this.set(null); },
    update(o) { Object.entries(o || {}).forEach(([k, v]) => this.child(k).set(v)); return Promise.resolve(); },
    on(ev, cb) { listeners.push({ path: p, cb }); setTimeout(() => cb(snap(p)), 0); return cb; },
    off() { for (let i = listeners.length - 1; i >= 0; i--) if (listeners[i].path === p) listeners.splice(i, 1); },
    once() { return Promise.resolve(snap(p)); },
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

// 컨텐츠별 관전 점검 도우미 (spectate-harness.js와 함께 각 탭 콘솔에서 씀)
// await (0,eval)(await (await fetch('/tests/spectate-scenarios.js')).text()); await __setup('학생id', { base: 80, jitter: 60 })
// - __setup: 페이지가 다 뜰 때까지 기다린 뒤 측정 도구·가짜 DB를 붙임
// - __tank(n): 방장 화면에서 모든 유닛 체력을 n배로 (전투가 금방 끝나지 않게) · 유닛 목록을 다시 보냄
// - __autoChoose(): 전투 방식 고르기 창이 뜨면 자동 전투로 고름
// - __measure(ms): 그동안 이 탭의 받은 화면(도전자·관전자) 측정값
(function () {
  window.__setup = async function (studentId, net) {
    await new Promise(r => { const c = () => (typeof state !== 'undefined' && state && state.students ? r() : setTimeout(c, 200)); c(); });
    if (!window.__spec) (0, eval)(await (await fetch('/tests/spectate-harness.js')).text());
    window.__net = net || { base: 0, jitter: 0 };
    window.__ends = [];
    if (!window.__endsHooked) {
      window.__endsHooked = true;
      const oa = abortLiveBattle;
      abortLiveBattle = function () { window.__ends.push(['abort', ...arguments]); return oa.apply(this, arguments); };
      const of = finishSimulation;
      finishSimulation = function () { window.__ends.push(['finish', sim.mode, sim.spectator]); return of.apply(this, arguments); };
    }
    return window.__loadMock(studentId);
  };
  window.__tank = function (n = 30) {
    sim.units.forEach(u => { u.maxHp *= n; u.hp = u.maxHp; });
    republishLiveUnits();
    if (liveNet.role === 'host' && liveNet.ref && !liveNet.towerCast) {
      const units = sim.units.map(u => JSON.parse(JSON.stringify(u, (k, v) => (k === 'manualAimTarget' ? undefined : v))));
      liveNet.ref.child('init').set(JSON.parse(JSON.stringify({ at: Date.now(), by: liveNet.myId || null, b: liveNet.bid, ep: liveNet.ep, units }))).catch(() => {});
    }
    return sim.units.length;
  };
  window.__autoChoose = function () {
    const box = document.getElementById('battleControlChooser');
    if (sim.running && box && !box.classList.contains('hidden')) { setBattleControlMode('auto', null); return true; }
    return false;
  };
  window.__measure = async function (ms) {
    window.__spec.reset();
    await new Promise(r => setTimeout(r, ms));
    return Object.assign(window.__spec.report(), { role: liveNet.role, spectator: sim.spectator, mode: sim.mode, pd: Math.round(liveNet.playDelay || 0), ends: window.__ends.slice() });
  };
})();

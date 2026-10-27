// 관전 점검용 (각 탭 콘솔에서 mock-rtdb.js 다음에 실행)
// 1) 숨은 창·배경 탭에서도 화면 그리기(requestAnimationFrame)를 60fps로 돌림 (작업자 타이머 기준)
// 2) 가짜 DB 소식에 인터넷 지연·흔들림을 넣음: __net = { base: 80, jitter: 60 } (ms, 순서는 지킴)
// 3) 관전 화면 측정: __spec.report() → 화면 도착 간격, 끊김(움직이던 용병이 멈춘 시간), 순간 튐, 버퍼 바닥남
(function () {
  window.__errs = window.__errs || [];
  window.addEventListener('error', e => window.__errs.push(String(e.message)));

  // ---- 타이머: 작업자 4ms 틱으로 지연 배달·화면 그리기 ----
  const w = new Worker(URL.createObjectURL(new Blob(['setInterval(() => postMessage(0), 4)'], { type: 'text/javascript' })));
  let rafQ = new Set();
  let lastRaf = 0;
  const later = [];
  window.requestAnimationFrame = cb => { rafQ.add(cb); return 1; };
  window.cancelAnimationFrame = () => {};
  window.__later = (fn, ms) => later.push({ at: performance.now() + ms, fn });
  window.__fps = { frames: 0, since: performance.now() };
  w.onmessage = () => {
    const now = performance.now();
    if (later.length) {
      later.sort((a, b) => a.at - b.at);
      while (later.length && later[0].at <= now) {
        const t = later.shift();
        try { t.fn(); } catch (e) { window.__errs.push('later: ' + e); }
      }
    }
    if (now - lastRaf >= 1000 / 60 - 1) {
      lastRaf = now;
      const q = rafQ; rafQ = new Set();
      window.__fps.frames++;
      q.forEach(cb => { try { cb(now); } catch (e) { window.__errs.push('raf: ' + (e && e.stack || e)); } });
    }
  };
  if (typeof animationLoop === 'function') requestAnimationFrame(animationLoop);

  // ---- 인터넷 지연 ----
  window.__net = window.__net || { base: 0, jitter: 0 };
  let lastDeliverAt = 0;
  window.__netDelay = fn => {
    const { base, jitter } = window.__net;
    if (!base && !jitter) { fn(); return; }
    const at = Math.max(performance.now() + base + Math.random() * jitter, lastDeliverAt + 0.1);
    lastDeliverAt = at;
    window.__later(fn, at - performance.now());
  };

  // 가짜 DB를 불러오되, 다른 탭에서 온 소식은 __netDelay를 거쳐 늦게 받음
  window.__loadMock = async function (studentId) {
    if (!window.__mockDb) {
      let src = await (await fetch('/tests/mock-rtdb.js')).text();
      src = src.replace("ch.postMessage({ t: 'req' });", "const __h0 = ch.onmessage; ch.onmessage = e => window.__netDelay(() => __h0(e)); ch.postMessage({ t: 'req' });");
      (0, eval)(src);
    }
    return setupMockClassTab(studentId);
  };

  // ---- 관전 화면 측정 ----
  const S = window.__spec = {
    reset() {
      Object.assign(S, { arrivals: [], frames: 0, stallMs: 0, maxStallMs: 0, curStall: 0, jumps: 0, maxJump: 0, underruns: 0, lastPos: null, lastT: 0, moveSum: 0, moveN: 0, startedAt: performance.now() });
    },
    report() {
      const gaps = S.arrivals.slice(1).map((t, i) => t - S.arrivals[i]).sort((a, b) => a - b);
      const pct = p => (gaps.length ? Math.round(gaps[Math.min(gaps.length - 1, Math.floor(gaps.length * p))]) : null);
      return {
        secs: Math.round((performance.now() - S.startedAt) / 100) / 10,
        fps: Math.round(S.frames / ((performance.now() - S.startedAt) / 1000)),
        framesIn: S.arrivals.length, gapP50: pct(0.5), gapP95: pct(0.95), gapMax: gaps.length ? Math.round(gaps[gaps.length - 1]) : null,
        stallTotalMs: Math.round(S.stallMs), stallMaxMs: Math.round(S.maxStallMs),
        jumps: S.jumps, maxJumpPx: Math.round(S.maxJump), avgMovePx: S.moveN ? Math.round(S.moveSum / S.moveN * 10) / 10 : 0,
        underruns: S.underruns, running: sim.running, buf: (liveNet.frameBuf || []).length, errs: window.__errs.slice(-5)
      };
    }
  };
  S.reset();
  const origApply = window.applyLiveFrame || applyLiveFrame;
  applyLiveFrame = function (val) { if (val && liveNet.role === 'guest') S.arrivals.push(performance.now()); return origApply.apply(this, arguments); };
  const origTick = applyLiveBattleFrameTick;
  applyLiveBattleFrameTick = function () {
    const r = origTick.apply(this, arguments);
    if (!sim.spectator || !sim.running || !liveNet.curFrame) return r;
    const now = performance.now();
    const dt = S.lastT ? now - S.lastT : 16;
    S.lastT = now;
    S.frames++;
    if (!(liveNet.frameBuf || []).length) S.underruns++;
    const pos = sim.units.map(u => [u.x, u.y, u.alive, u.isMoving]);
    if (S.lastPos && S.lastPos.length === pos.length) {
      let anyMoving = false, anyMoved = false;
      pos.forEach((p, i) => {
        const q = S.lastPos[i];
        if (!p[2] || !q[2]) return;
        const d = Math.hypot(p[0] - q[0], p[1] - q[1]);
        if (p[3]) { anyMoving = true; if (d > 0.05) anyMoved = true; S.moveSum += d; S.moveN++; }
        if (d > S.maxJump && d < 400) S.maxJump = d;
        if (d > 12 && d < 400) S.jumps++; // 한 화면(1/60초)에 12px 넘게 = 눈에 띄는 튐 (보통 걷기는 1~2px)
      });
      if (anyMoving && !anyMoved) { S.curStall += dt; S.stallMs += dt; S.maxStallMs = Math.max(S.maxStallMs, S.curStall); }
      else S.curStall = 0;
    }
    S.lastPos = pos;
    return r;
  };
})();

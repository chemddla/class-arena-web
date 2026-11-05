// 실제 학급의 Firebase 트래픽 재기 (읽기 전용) — docs/traffic-task.md 참고
// 로컬 미리보기(http://localhost:5173/?dev=student&mute=1, 앱은 빈 샘플 학급 ARENA1에 머묾)의 콘솔에서:
//   (0, eval)(await (await fetch('/tools/traffic-measure.js')).text());
//   await TM.login('ARENA3')        // 접속할 때 학생 기기 한 대가 받는 양 (노드별·students 칸별·용병 칸별)
//   await TM.live('ARENA3', 180)    // 180초 동안 서버가 보내는 변경량 (경로별 B/s · 라이브 전투는 방별)
// 측정용 구독만 따로 걸고 받기만 함: 앱 로직은 ARENA3를 모르므로 정리·보상 같은 쓰기를 하지 않음
(function () {
  const db = () => RealtimePvpService.initFirebaseClientSafe();
  const len = v => (v == null ? 0 : JSON.stringify(v).length);
  const kb = n => `${(n / 1024).toFixed(1)}KB`;
  // 학생 기기가 늘 구독하는 경로 (index.html: CLASS_SYNC_KEYS · subscribeClassExtras · subscribeToInteractiveChannels · WorldBoss · Presence)
  const ALWAYS = ['meta', 'students', 'profiles', 'auctions', 'tradeOffers', 'skins', 'pvp_live/tower_index', 'pvp_live/petrun_index',
    'pvp_rooms', 'raid_rooms', 'minigame_rooms', 'invites', 'world_boss'];
  // 들어갔을 때만 받는 경로 (관전·참가 중인 그 방 하나만 받음 → 여기서는 전부 받아 방별로 나눠 봄)
  const SOMETIMES = ['pvp_live', 'minigames', 'home_live', 'room_chats'];

  function breakdown(map, pick) {
    const by = {}, cnt = {};
    Object.values(map || {}).forEach(x => (pick(x) || []).forEach(o => o && typeof o === 'object' && Object.entries(o).forEach(([k, v]) => {
      by[k] = (by[k] || 0) + len(v) + k.length + 4; cnt[k] = (cnt[k] || 0) + 1;
    })));
    return Object.entries(by).sort((a, b) => b[1] - a[1]).slice(0, 25).map(([k, n]) => `${k}: ${n}B (${cnt[k]}개)`);
  }

  async function login(code) {
    code = String(code).toUpperCase();
    const out = { at: new Date().toLocaleString(), nodes: {} };
    for (const p of [...ALWAYS, 'transfers', 'studentPrivate', ...SOMETIMES]) {
      try { out.nodes[p] = len((await db().ref(`classes/${code}/${p}`).once('value')).val()); } catch (e) { out.nodes[p] = 'ERR ' + (e.code || e); }
    }
    const pres = (await db().ref(`presence/${code}`).once('value')).val() || {};
    out.online = Object.keys(pres).length;
    const stu = (await db().ref(`classes/${code}/students`).once('value')).val() || {};
    const priv = (await db().ref(`classes/${code}/studentPrivate`).once('value')).val() || {};
    const ids = Object.keys(stu);
    out.students = ids.length;
    out.loginTotal = ALWAYS.reduce((s, p) => s + (typeof out.nodes[p] === 'number' ? out.nodes[p] : 0), 0) + Math.round(len(priv) / Math.max(1, ids.length));
    out.loginTotalText = `학생 기기 한 대 접속 ≈ ${kb(out.loginTotal)} (늘 구독하는 노드 + 내 studentPrivate 평균)`;
    out.studentFields = breakdown(stu, s => [s]);
    out.rosterFields = breakdown(stu, s => (Array.isArray(s.roster) ? s.roster : Object.values(s.roster || {})));
    // 서버에 남은 예전 칸 (6a8e443 이후 지워져야 함: 진형 사본 · students 안의 나만 쓰는 칸)
    const legacy = {};
    ids.forEach(id => ['defenseFormation', 'defenseFormationLabel', ...(typeof STUDENT_PRIVATE_KEYS !== 'undefined' ? STUDENT_PRIVATE_KEYS : [])]
      .forEach(k => { if (stu[id] && stu[id][k] != null) legacy[k] = (legacy[k] || 0) + len(stu[id][k]); }));
    out.legacyLeft = legacy;
    console.table(out.nodes);
    return out;
  }

  // 서버가 보낸 데이터 메시지를 경로별로 셈 (firebase.database.enableLogging의 'handleServerMessage' 줄 · 실제 전송은 경로·틀 몇십 B가 더 붙음)
  async function live(code, sec = 180) {
    code = String(code).toUpperCase();
    const base = `/classes/${code}/`, pres = `/presence/${code}`;
    const bytes = {}, msgs = {};
    let total = 0;
    const keyOf = p => {
      if (p.startsWith(pres)) return 'presence';
      if (!p.startsWith(base)) return null;
      const parts = p.slice(base.length).split('/');
      if (parts[0] === 'pvp_live' && parts[1] && parts[1] !== 'tower_index' && parts[1] !== 'petrun_index') return `pvp_live/${parts[1]}/${parts[2] || ''}`; // 방별·칸별 (frame·init·inputs…)
      if (['pvp_live', 'minigames', 'home_live', 'room_chats', 'world_boss'].includes(parts[0])) return parts.slice(0, 2).join('/');
      return parts[0] === 'students' ? `students/${parts[2] || '(통째)'}` : parts[0]; // 학생 기록은 바뀐 칸 이름별
    };
    firebase.database.enableLogging(msg => {
      // 데이터는 'p:0: handleServerMessage d {"p":경로,"d":값}' (m = 여러 칸 한꺼번에) 줄로 찍힘
      const hit = /handleServerMessage ([dm]) (\{.*)$/.exec(String(msg));
      if (!hit) return;
      const body = hit[2].trim();
      let m; try { m = JSON.parse(body); } catch (e) { return; }
      if (!m || typeof m.p !== 'string') return;
      const p = '/' + m.p.replace(/^\//, '');
      const k = keyOf(p);
      if (!k) return;
      bytes[k] = (bytes[k] || 0) + body.length; msgs[k] = (msgs[k] || 0) + 1; total += body.length;
    }, false);
    const refs = [...ALWAYS, ...SOMETIMES].map(p => db().ref(`classes/${code}/${p}`)).concat(db().ref(`presence/${code}`));
    const noop = () => {};
    // 처음 받는 전체 값은 빼고 셈 (접속 크기는 TM.login이 잼)
    refs.forEach(r => r.on('value', noop, noop));
    await new Promise(r => setTimeout(r, 6000));
    Object.keys(bytes).forEach(k => { delete bytes[k]; delete msgs[k]; }); total = 0;
    const t0 = Date.now();
    console.log(`[TM] ${sec}초 재는 중… (이 탭을 앞에 둔 채로 두세요)`);
    await new Promise(r => setTimeout(r, sec * 1000));
    const s = (Date.now() - t0) / 1000;
    refs.forEach(r => r.off('value', noop));
    firebase.database.enableLogging(false);
    const online = Object.keys((await db().ref(`presence/${code}`).once('value')).val() || {}).length;
    const rows = Object.entries(bytes).sort((a, b) => b[1] - a[1]).map(([k, n]) => ({ 경로: k, 'B/s': Math.round(n / s), 메시지: msgs[k], '평균B': Math.round(n / msgs[k]) }));
    console.table(rows.slice(0, 40));
    // 늘 구독하는 경로의 변경은 접속한 학생 모두가 받음 → 반 전체 = B/s × 접속 수
    const alwaysBps = rows.filter(r => !SOMETIMES.some(p => r.경로.startsWith(p))).reduce((a, r) => a + r['B/s'], 0);
    return { sec: Math.round(s), online, totalBps: Math.round(total / s), alwaysBpsPerDevice: alwaysBps,
      note: `늘 구독하는 경로 ${alwaysBps}B/s × 접속 ${online}명 ≈ 반 전체 ${kb(alwaysBps * online)}/s · pvp_live 방별 값은 그 방 참가자·관전자 한 명이 받는 양`, rows };
  }

  window.TM = { login, live };
})();

// 콘텐츠별 밸런스 시뮬레이션 (브라우저 콘솔용, tests/battle-sim.js를 먼저 불러온 뒤)
//   await BS.duelLv([10, 40, 100], 6)          // 레벨별 직업 1:1 승률 (가로 평균만)
//   await BS.rand5Lv([40, 100], 300)           // 레벨별 무작위 5:5 (직업이 들어간 팀 승률)
//   await BS.towerJobs([10, 50, 100], 8)       // 층별 · 직업을 넣은 용병단 승률 (기본 조합 한 칸을 그 직업으로)
//   await BS.eliteSweep([1, 5, 10], [40, 80], 3) // 엘리트 보스 단계 × 레벨: 처치율 · 보스 체력 깎은 비율
//   await BS.eliteJobs(5, 70, 4)               // 한 단계에서 직업별 (둘 다 그 직업을 넣은 5+5)
//   await BS.rushJobs([40], 2, 60)             // 몬스터 러쉬: 직업별 버틴 라운드 (5인 파티)
//
// 밸런스 방향: 모든 콘텐츠에서 똑같을 필요는 없음. 직업마다 잘하는 분야가 있고, 격차가 너무 심할 때만 고침
//   BS.ROLES = 직업별로 강해도 되는 분야 · 약해도 되는 분야
//   BS.LIMITS = '너무 심함' 기준. BS.flags({ duel, rand5, tower })로 기준을 넘은 칸만 골라 봄
//   (약해도 되는 분야는 아래쪽 기준을 보지 않음 · 위쪽 기준은 모든 직업에 적용)
(function () {
  const isMain = u => !u.ownerId && !u.isClone;
  BS.ROLES = {
    warrior: { strong: '러쉬·탑 일반층 근접 딜', weak: [] },
    mage:    { strong: '탑 일반층 광역 딜', weak: [] },
    healer:  { strong: '5:5·레이드 유지력', weak: ['duel'] },
    archer:  { strong: '탑 안정 딜', weak: [] },
    rogue:   { strong: '1:1 결투', weak: ['tower'] },
    knight:  { strong: '팀 탱커', weak: ['duel', 'tower'] },
    lancer:  { strong: '1:1·근접전', weak: [] },
    sniper:  { strong: '보스 (탑 보스층·엘리트)', weak: [] },
    frost:   { strong: '제어 (5:5·1:1)', weak: [] },
    curse:   { strong: '탑 일반층 약화', weak: ['duel'] },
    bard:    { strong: '팀 버프', weak: ['duel'] },
    berserker: { strong: '근접 브루저 (러쉬·1:1)', weak: [] },
    paladin: { strong: '5:5·러쉬 앞줄 유지 (성녀 없는 팀의 유지력)', weak: ['duel'] },
    summoner: { strong: '수 싸움·몬스터 무리 (탑·러쉬)', weak: [] },
    pyro:    { strong: '몬스터 무리 다중 공격 (탑 일반층·러쉬·던전)', weak: ['duel'] }
  };
  // [아래, 위]: 이 밖이면 조정 대상
  BS.LIMITS = { duel: [20, 80], rand5: [40, 60], tower: [40, 88] };
  BS.flags = function (R) {
    const out = [];
    Object.entries(BS.LIMITS).forEach(([mode, [lo, hi]]) => {
      const tbl = R[mode];
      if (!tbl) return;
      Object.entries(tbl).forEach(([row, cols]) => BS.JOBS.forEach(j => {
        const v = parseInt(cols[j]);
        if (Number.isNaN(v)) return;
        const weakOk = (BS.ROLES[j].weak || []).includes(mode);
        if (v > hi || (v < lo && !weakOk)) out.push(`${mode} ${row} ${j} ${v}% (기준 ${lo}~${hi}%)`);
      }));
    });
    return out.length ? out.join('\n') : '기준을 넘은 칸 없음';
  };
  const BAL = ['knight', 'warrior', 'mage', 'healer', 'archer'];
  const pct = v => Math.round(v * 100) + '%';
  // 직업 비교용 조합: 기사·전사·마법사·성녀 + 다섯째 칸에 그 직업 (기본 조합에 있는 직업이면 둘이 됨)
  BS.feat = j => ['knight', 'warrior', 'mage', 'healer', j];
  // 용병 원본(merc) 목록: jobs를 앞줄·뒷줄로 세움
  BS.mercs = function (jobs, lv, rar = 'N') {
    const ps = BS.place(jobs);
    return jobs.map((j, i) => { const m = createMercenary(j, rar, lv, i, true, null); m.row = ps[i].r; m.col = ps[i].c; m.traitId = null; m.bsKey = j; return m; });
  };
  const tag = (u, m) => { u.bsKey = m.bsKey; return u; };
  const fake = id => ({ id, name: '시뮬', roster: [], relics: {}, inventory: [] });
  const hideResult = () => document.getElementById('battleResultOverlay')?.classList.add('hidden');

  // ----- 결투: 레벨별 1:1 · 5:5 -----
  BS.duelLv = async function (levels, runs = 6) {
    const out = {};
    for (const lv of levels) {
      const m = {};
      BS.JOBS.forEach(j => { m[j] = { w: 0, n: 0 }; });
      for (const a of BS.JOBS) for (const b of BS.JOBS) {
        if (a >= b) continue;
        for (let k = 0; k < runs; k++) {
          const flip = k % 2;
          const A = BS.mk({ job: a, lv }, flip ? 'red' : 'blue', 0, 'A:'), B = BS.mk({ job: b, lv }, flip ? 'blue' : 'red', 0, 'B:');
          const r = flip ? BS.fight([B], [A]) : BS.fight([A], [B]);
          const aWin = flip ? r.red && !r.blue : r.blue && !r.red, bWin = flip ? r.blue && !r.red : r.red && !r.blue;
          const w = aWin ? 1 : (bWin ? 0 : 0.5);
          m[a].w += w; m[a].n++; m[b].w += 1 - w; m[b].n++;
        }
        await BS.yieldNow();
      }
      out[lv] = Object.fromEntries(BS.JOBS.map(j => [j, pct(m[j].w / m[j].n)]));
    }
    hideResult();
    return out;
  };
  BS.rand5Lv = async function (levels, n = 300) {
    const out = {};
    for (const lv of levels) {
      const inc = {};
      BS.JOBS.forEach(j => { inc[j] = { w: 0, n: 0 }; });
      for (let i = 0; i < n; i++) {
        const rj = () => Array.from({ length: 5 }, () => BS.JOBS[Math.floor(Math.random() * BS.JOBS.length)]);
        const a = rj(), b = rj();
        const r = BS.fight(BS.team(a, 'blue', 'A:', { lv }), BS.team(b, 'red', 'B:', { lv }));
        const w = r.blue && !r.red ? 1 : (!r.blue && r.red ? 0 : 0.5);
        new Set(a).forEach(j => { inc[j].w += w; inc[j].n++; });
        new Set(b).forEach(j => { inc[j].w += 1 - w; inc[j].n++; });
        if (i % 5 === 4) await BS.yieldNow();
      }
      out[lv] = Object.fromEntries(BS.JOBS.map(j => [j, pct(inc[j].w / inc[j].n)]));
    }
    hideResult();
    return out;
  };

  // ----- 모험의 탑: 층과 같은 레벨 -----
  BS.towerRun = function (floor, jobs, lvOff = 0) {
    const floorObj = TOWER_FLOORS.find(t => t.floor === floor);
    const lv = Math.max(1, towerEnemySetup(floor).level + lvOff);
    const stu = fake('sim_stu');
    stu.roster = BS.mercs(jobs, lv);
    launchSimulation({ mode: 'tower', title: 'sim', blueStudent: stu, towerFloorObj: floorObj, customBlueUnits: stu.roster.map(m => tag(createSimUnit(m, stu, 'blue', 1.0), m)) });
    setBattleControlMode('auto', null, true);
    const alive = t => sim.units.some(u => u.team === t && u.alive && isMain(u));
    let n = 0;
    while (n < 200 * BATTLE_TICKS_PER_SEC && sim.running && alive('blue') && alive('red')) { stepSimulation(); n++; }
    const win = alive('blue') && !alive('red');
    sim.running = false;
    return { win, sec: n / BATTLE_TICKS_PER_SEC };
  };
  BS.towerJobs = async function (floors, runs = 8, jobs = BS.JOBS, lvOff = 0) {
    const out = {};
    for (const f of floors) {
      const row = out[f] = { boss: isTowerRaceBossFloor(f) };
      for (const j of jobs) {
        let w = 0;
        for (let k = 0; k < runs; k++) { w += BS.towerRun(f, BS.feat(j), lvOff).win ? 1 : 0; await BS.yieldNow(); }
        row[j] = pct(w / runs);
      }
    }
    hideResult();
    return out;
  };

  // ----- 엘리트 보스: 플레이어 2명 × 용병 5명 -----
  BS.eliteRun = function (stage, jobsA, jobsB, lv, hard = false) {
    const def = ELITE_BOSS_DEFS.find(b => b.stage === stage);
    const sa = fake('sim_a'), sb = fake('sim_b');
    sa.roster = BS.mercs(jobsA, lv); sb.roster = BS.mercs(jobsB || jobsA, lv);
    const blue = buildCoopRaidBlueUnits([{ stu: sa, mercs: sa.roster, label: 'A' }, { stu: sb, mercs: sb.roster, label: 'B' }]);
    blue.forEach((u, i) => { u.bsKey = (i < 5 ? sa.roster[i] : sb.roster[i - 5]).bsKey; });
    const boss = buildCenterEliteBoss(def, 2, hard);
    BS.stats = { dmg: {}, heal: {}, casts: {} };
    launchSimulation({ mode: 'elite_raid', title: 'sim', blueStudent: sa, redStudent: null, eliteBossId: def.id, eliteHard: hard, rewardMc: 0, customBlueUnits: blue, customRedUnits: [boss] });
    setBattleControlMode('auto', null, true);
    const b = sim.units.find(u => u.isEliteBoss);
    const aliveBlue = () => sim.units.some(u => u.team === 'blue' && u.alive && isMain(u));
    let n = 0;
    while (n < (ELITE_RAID_TIME_LIMIT_SEC + 15) * BATTLE_TICKS_PER_SEC && sim.running && aliveBlue() && b.alive) { stepSimulation(); n++; }
    const res = { win: !b.alive, dmg: 1 - Math.max(0, b.hp) / b.maxHp, sec: n / BATTLE_TICKS_PER_SEC, wipe: !aliveBlue(), byJob: {} };
    Object.entries(BS.stats.dmg).forEach(([k, o]) => { res.byJob[k] = Object.values(o).reduce((s, v) => s + v, 0) / b.maxHp; });
    BS.stats = null;
    sim.running = false;
    return res;
  };
  BS.eliteSweep = async function (stages, levels, runs = 3, jobs = BAL) {
    const out = {};
    for (const s of stages) for (const lv of levels) {
      let w = 0, d = 0, wipe = 0, sec = 0;
      for (let k = 0; k < runs; k++) { const r = BS.eliteRun(s, jobs, jobs, lv); w += r.win; d += r.dmg; wipe += r.wipe; sec += r.sec; await BS.yieldNow(); }
      out[`s${s} Lv${lv}`] = `처치 ${pct(w / runs)} · 체력 ${pct(d / runs)} · 전멸 ${pct(wipe / runs)} · ${Math.round(sec / runs)}초`;
    }
    hideResult();
    return out;
  };
  BS.eliteJobs = async function (stage, lv, runs = 4, jobs = BS.JOBS) {
    const out = {};
    for (const j of jobs) {
      let w = 0, d = 0, per = 0;
      for (let k = 0; k < runs; k++) { const r = BS.eliteRun(stage, BS.feat(j), BS.feat(j), lv); w += r.win; d += r.dmg; per += (r.byJob[j] || 0) / 2; await BS.yieldNow(); }
      out[j] = `처치 ${pct(w / runs)} · 팀 ${pct(d / runs)} · 그 직업 1명 ${(per / runs * 100).toFixed(1)}%`;
    }
    hideResult();
    return out;
  };

  // ----- 몬스터 러쉬: 1인 1용병, 최대 5명 -----
  BS.rushRun = function (jobs, lv, roundCap = RUSH.maxRound) {
    const stu = fake('sim_rush');
    const mercs = BS.mercs(jobs, lv);
    const rs = newRushState(rushStartFloorOf(mercs));
    launchSimulation({ mode: 'monster_rush', title: 'sim', blueStudent: stu, redStudent: null, rewardMc: 0, customBlueUnits: [], customRedUnits: buildRushWave(1, rs) });
    // buildRushBlueUnits와 같은 자리: 맵 왼쪽 세로 줄
    mercs.forEach((m, i) => {
      const u = createSimUnit({ ...m, row: 2, col: 1 }, stu, 'blue', 1.0);
      u.bsKey = m.bsKey; u.x = 640; u.y = Math.round(sim.worldH / 2 + (i - (mercs.length - 1) / 2) * 200); u.facingDir = 1; u.facingAngle = 0;
      sim.units.push(u);
    });
    rs.roundStartTick = sim.tickCount;
    rs.pending = rs.left = sim.units.filter(u => u.rushPending).length;
    sim.rush = rs;
    setBattleControlMode('auto', null, true);
    let n = 0;
    const cap = 4 * 3600 * BATTLE_TICKS_PER_SEC;
    while (n < cap && sim.running && rs.cleared < roundCap) { stepSimulation(); n++; }
    sim.running = false;
    return { cleared: rs.cleared, bosses: rs.bosses, startFloor: rs.startFloor, min: Math.round(n / BATTLE_TICKS_PER_SEC / 60) };
  };
  BS.rushJobs = async function (levels, runs = 2, roundCap = RUSH.maxRound, jobs = BS.JOBS) {
    const out = {};
    for (const lv of levels) {
      const row = out['Lv' + lv] = {};
      for (const j of jobs) {
        const rs = [];
        for (let k = 0; k < runs; k++) { rs.push(BS.rushRun(BS.feat(j), lv, roundCap).cleared); await BS.yieldNow(); }
        row[j] = rs.join('/');
      }
    }
    hideResult();
    return out;
  };

  // 오래 걸리는 시뮬을 백그라운드로: BS.bg('이름', () => BS.towerJobs(...)) → BS.jobs['이름']
  BS.jobs = BS.jobs || {};
  BS.bg = function (name, fn) {
    const j = BS.jobs[name] = { status: 'running', t0: Date.now() };
    fn().then(r => { j.status = 'done'; j.result = r; j.sec = Math.round((Date.now() - j.t0) / 1000); }, e => { j.status = 'error'; j.error = String(e && e.stack || e); });
    return name;
  };
})();

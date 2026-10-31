// 전투 밸런스 시뮬레이션 (브라우저 콘솔용): 실제 전투 엔진으로 여러 판을 자동으로 돌려 승률·직업별 피해·스킬별 피해를 봄
// 사용법: localhost에서 ?dev=student 로 연 뒤
//   const s = document.createElement('script'); s.src = 'tests/battle-sim.js'; document.head.appendChild(s);
//   await BS.duel(8)            // 직업 1:1 승률표
//   await BS.rand5(700)         // 무작위 5:5 (직업이 들어간 팀 승률 · 1인당 피해)
//   await BS.mono(20)           // 같은 직업 5명 vs 기본 조합
//   await BS.hidden(30)         // 히든 스킬 1명 보유 팀 vs 같은 조합
//   await BS.tower([10, 20], 12) // 모험의 탑 층별 승률 (기본 용병단)
(function () {
  const BS = window.BS = { results: {} };
  suppressRemoteClassPush = true;
  // 시뮬 중에는 소리 끔 (타격음·효과음)
  sfxEnabled = false;
  playCombatSfx = () => {};
  if (audioCtx) audioCtx.suspend().catch(() => {});
  document.querySelectorAll('audio, video').forEach(a => { a.muted = true; });
  BATTLE_TIME_LIMIT.practiceTicks = 180 * BATTLE_TICKS_PER_SEC;
  BS.JOBS = Object.keys(JOB_DEFS);
  BS.yieldNow = () => new Promise(res => { const ch = new MessageChannel(); ch.port1.onmessage = () => res(); ch.port2.postMessage(0); });

  // ----- 피해·치유·시전 기록 -----
  BS.stats = null;
  const origApplyDamage = applyDamage, origHeal = healAllyNow, origCast = beginSkillCast;
  applyDamage = function (a, d, raw, tag, col) {
    const before = d.hp + (d.shield || 0);
    const r = origApplyDamage(a, d, raw, tag, col);
    if (BS.stats) {
      const dealt = Math.max(0, before - (d.hp + (d.shield || 0)));
      const k = a ? (a.bsKey || a.job) : 'env';
      const kind = skillHitSource ? 'skill:' + ((a && a.bsLastSkill) || '?') : (basicHitKind ? 'basic' : 'dot');
      const o = BS.stats.dmg[k] = BS.stats.dmg[k] || {};
      o[kind] = (o[kind] || 0) + dealt;
    }
    return r;
  };
  healAllyNow = function (h, t, amt) {
    const b = t && t.hp;
    const r = origHeal(h, t, amt);
    if (BS.stats && t) { const k = h.bsKey || h.job; BS.stats.heal[k] = (BS.stats.heal[k] || 0) + (t.hp - b); }
    return r;
  };
  beginSkillCast = function (u, key, aim) {
    u.bsLastSkill = key;
    if (BS.stats) { const k = (u.bsKey || u.job) + '|' + key; BS.stats.casts[k] = (BS.stats.casts[k] || 0) + 1; }
    return origCast(u, key, aim);
  };

  // ----- 유닛 만들기 -----
  const POS = [{ r: 1, c: 2 }, { r: 3, c: 2 }, { r: 2, c: 1 }, { r: 1, c: 0 }, { r: 3, c: 0 }];
  const FRONT = ['warrior', 'knight', 'lancer', 'rogue'];
  // spec: { job, lv=40, rar='N', pos, hidden }  hidden이면 열린 스킬 한 칸을 히든 스킬로 바꿈
  BS.mk = function (spec, team, i, prefix = '') {
    const m = createMercenary(spec.job, spec.rar || 'N', spec.lv || 40, i, true, null);
    const p = spec.pos || POS[i % POS.length];
    m.row = p.r; m.col = p.c; m.traitId = null;
    const u = createSimUnit(m, null, team, 1.0);
    const h = spec.hidden && Object.keys(HIDDEN_SKILL_DEFS[spec.job] || {})[0];
    if (h) {
      const idx = Math.floor(Math.random() * u.unlockedSkills.length), old = u.unlockedSkills[idx];
      u.unlockedSkills[idx] = h;
      u.skillSlots = u.skillSlots.map(k => (k === old ? h : k));
      u.skillCooldowns[h] = 0;
    }
    u.bsKey = prefix + spec.job;
    return u;
  };
  // 근접은 앞줄, 원거리는 뒷줄
  BS.place = function (jobs) {
    const fr = [{ r: 1, c: 2 }, { r: 3, c: 2 }, { r: 2, c: 2 }, { r: 0, c: 2 }, { r: 4, c: 2 }];
    const bk = [{ r: 2, c: 0 }, { r: 1, c: 0 }, { r: 3, c: 0 }, { r: 0, c: 0 }, { r: 4, c: 0 }];
    let fi = 0, bi = 0;
    return jobs.map(j => (FRONT.includes(j) ? fr[fi++] : bk[bi++]));
  };
  BS.team = function (jobs, team, prefix, extra = {}) {
    const ps = BS.place(jobs);
    return jobs.map((j, i) => BS.mk({ job: j, pos: ps[i], ...(typeof extra === 'function' ? extra(j, i) : extra) }, team, i, prefix));
  };

  // ----- 한 판 -----
  const isMain = u => !u.ownerId;
  BS.fight = function (blue, red, maxSec = 180) {
    const fake = { id: 'sim', name: 'sim', roster: [], relics: {}, inventory: [] };
    launchSimulation({ mode: 'practice', title: 'sim', blueStudent: fake, redStudent: { ...fake, id: 'sim2' }, customBlueUnits: blue, customRedUnits: red });
    setBattleControlMode('auto', null, true);
    const alive = t => sim.units.some(u => u.team === t && u.alive && isMain(u));
    const lim = maxSec * BATTLE_TICKS_PER_SEC + 400;
    let n = 0;
    while (n < lim && alive('blue') && alive('red')) { stepSimulation(); n++; if (!sim.running && n > 10) break; }
    const res = {
      sec: n / BATTLE_TICKS_PER_SEC, blue: alive('blue'), red: alive('red'),
      units: sim.units.filter(isMain).map(u => ({ k: u.bsKey, team: u.team, alive: u.alive, dealt: u.damageDealt, taken: u.damageTaken, heal: u.healDone }))
    };
    sim.running = false;
    return res;
  };
  // jobs: () => { tag, blue, red } 목록. tag가 '|r'로 끝나면 A팀이 빨강 (승률은 A팀 기준으로 뒤집어 셈)
  BS.runBatch = async function (name, jobs) {
    const out = { done: 0, total: jobs.length, rows: [], stats: { dmg: {}, heal: {}, casts: {} } };
    BS.results[name] = out;
    for (const j of jobs) {
      BS.stats = out.stats;
      const { blue, red, tag } = j();
      const r = BS.fight(blue, red);
      const win = r.blue && !r.red ? 1 : (!r.blue && r.red ? 0 : 0.5);
      out.rows.push({ tag: tag.replace('|r', ''), win: tag.endsWith('|r') ? 1 - win : win, sec: r.sec, units: r.units });
      if (++out.done % 5 === 0) await BS.yieldNow();
    }
    BS.stats = null;
    document.getElementById('battleResultOverlay')?.classList.add('hidden');
    return out;
  };
  const pct = v => Math.round(v * 100) + '%';
  BS.byTag = function (R) {
    const m = {};
    R.rows.forEach(r => { const o = m[r.tag] = m[r.tag] || { w: 0, n: 0, s: 0 }; o.w += r.win; o.n++; o.s += r.sec; });
    return Object.entries(m).map(([t, o]) => `${t.padEnd(16)} ${pct(o.w / o.n).padStart(5)}  ${Math.round(o.s / o.n)}초`).join('\n');
  };
  // 양쪽을 번갈아 파랑·빨강으로
  const both = (tag, a, b) => k => (k % 2 ? () => ({ tag: tag + '|r', blue: b('blue', 'B:'), red: a('red', 'A:') }) : () => ({ tag, blue: a('blue', 'A:'), red: b('red', 'B:') }));
  const repeat = (n, f) => Array.from({ length: n }, (_, k) => f(k));
  const BAL = ['knight', 'warrior', 'mage', 'healer', 'archer'];
  const rj = () => Array.from({ length: 5 }, () => BS.JOBS[Math.floor(Math.random() * BS.JOBS.length)]);

  BS.duel = async function (runs = 8) {
    const jobs = [];
    BS.JOBS.forEach(a => BS.JOBS.forEach(b => { if (a <= b) jobs.push(...repeat(runs, both(a + '>' + b, (t, p) => [BS.mk({ job: a }, t, 0, p)], (t, p) => [BS.mk({ job: b }, t, 0, p)]))); }));
    const R = await BS.runBatch('duel', jobs);
    const m = {};
    R.rows.forEach(r => { const [a, b] = r.tag.split('>'); [[a, b, r.win], [b, a, 1 - r.win]].forEach(([x, y, w]) => { const o = (m[x] = m[x] || {})[y] = (m[x][y] || { w: 0, n: 0 }); o.w += w; o.n++; }); });
    let t = '         ' + BS.JOBS.map(j => j.slice(0, 6).padStart(7)).join('') + '   avg\n';
    BS.JOBS.forEach(a => { let s = 0; t += a.padEnd(9) + BS.JOBS.map(b => { const o = m[a][b], w = o.w / o.n; s += w; return pct(w).padStart(7); }).join('') + pct(s / BS.JOBS.length).padStart(6) + '\n'; });
    return t;
  };
  BS.rand5 = async function (n = 700) {
    const R = await BS.runBatch('rand5', repeat(n, () => () => { const a = rj(), b = rj(); return { tag: a.join(',') + '>' + b.join(','), blue: BS.team(a, 'blue', 'A:'), red: BS.team(b, 'red', 'B:') }; }));
    const inc = {}, cnt = {};
    BS.JOBS.forEach(j => { inc[j] = { w: 0, n: 0 }; cnt[j] = { dealt: 0, taken: 0, heal: 0, surv: 0, n: 0 }; });
    R.rows.forEach(r => {
      const [a, b] = r.tag.split('>').map(s => s.split(','));
      a.forEach(j => { inc[j].w += r.win; inc[j].n++; });
      b.forEach(j => { inc[j].w += 1 - r.win; inc[j].n++; });
      r.units.forEach(u => { const c = cnt[u.k.replace(/^[AB]:/, '')]; if (!c) return; c.dealt += u.dealt; c.taken += u.taken; c.heal += u.heal || 0; c.surv += u.alive ? 1 : 0; c.n++; });
    });
    return '직업     포함 팀 승률  1인당 피해 / 받은 피해 / 치유 / 생존\n' + BS.JOBS.map(j => [j, inc[j].w / inc[j].n]).sort((x, y) => y[1] - x[1])
      .map(([j, w]) => { const c = cnt[j]; return `${j.padEnd(9)} ${(w * 100).toFixed(1).padStart(5)}%   ${Math.round(c.dealt / c.n)} / ${Math.round(c.taken / c.n)} / ${Math.round(c.heal / c.n)} / ${pct(c.surv / c.n)}`; }).join('\n');
  };
  BS.mono = async function (runs = 20) {
    const jobs = [];
    BS.JOBS.forEach(j => jobs.push(...repeat(runs, both('5x' + j, (t, p) => BS.team([j, j, j, j, j], t, p), (t, p) => BS.team(BAL, t, p)))));
    return BS.byTag(await BS.runBatch('mono', jobs));
  };
  BS.hidden = async function (runs = 30) {
    const jobs = [];
    BS.JOBS.forEach(j => {
      const comp = BAL.includes(j) ? BAL : ['knight', 'warrior', 'mage', 'healer', j];
      jobs.push(...repeat(runs, both('hidden:' + j, (t, p) => BS.team(comp, t, p, x => ({ hidden: x === j })), (t, p) => BS.team(comp, t, p))));
    });
    return BS.byTag(await BS.runBatch('hidden', jobs));
  };
  BS.levels = async function (runs = 30) {
    const jobs = [];
    const pair = (tag, a, b) => jobs.push(...repeat(runs, both(tag, (t, p) => BS.team(BAL, t, p, a), (t, p) => BS.team(BAL, t, p, b))));
    pair('Lv45 vs Lv40', { lv: 45 }, { lv: 40 });
    pair('Lv40 vs Lv30', { lv: 40 }, { lv: 30 });
    pair('R vs N', { rar: 'R' }, { rar: 'N' });
    pair('SCR vs N', { rar: 'SCR' }, { rar: 'N' });
    pair('SCR40 vs N45', { rar: 'SCR', lv: 40 }, { rar: 'N', lv: 45 });
    pair('SCR40 vs N50', { rar: 'SCR', lv: 40 }, { rar: 'N', lv: 50 });
    return BS.byTag(await BS.runBatch('levels', jobs));
  };
  BS.skillTable = function (R) {
    const agg = {}, casts = {}, tot = {};
    Object.entries(R.stats.dmg).forEach(([k, o]) => { const j = k.replace(/^[AB]:/, ''); Object.entries(o).forEach(([kind, v]) => { agg[j + ' ' + kind] = (agg[j + ' ' + kind] || 0) + v; tot[j] = (tot[j] || 0) + v; }); });
    Object.entries(R.stats.casts).forEach(([k, v]) => { const [u, s] = k.split('|'); const kk = u.replace(/^[AB]:/, '') + ' skill:' + s; casts[kk] = (casts[kk] || 0) + v; });
    return Object.keys({ ...agg, ...casts }).sort().map(k => { const j = k.split(' ')[0], d = agg[k] || 0, c = casts[k] || 0; return `${k.padEnd(30)} ${String(Math.round(d)).padStart(9)} (${pct(d / tot[j]).padStart(4)})  시전 ${String(c).padStart(5)}  1회 ${c ? Math.round(d / c) : '-'}`; }).join('\n');
  };

  // ----- 모험의 탑: 층과 같은 레벨대의 기본 용병단(createDefaultSquad)으로 -----
  BS.tower = async function (floors, runs = 12, lvOff = 0) {
    const out = {};
    const fakeStu = { id: 'sim_stu', name: '시뮬', roster: [], relics: {}, inventory: [] };
    for (const f of floors) {
      const floorObj = TOWER_FLOORS.find(t => t.floor === f);
      if (!floorObj) continue;
      const lv = Math.max(1, Math.round(1 + f * 0.95) + lvOff);
      let wins = 0, ticks = 0;
      for (let r = 0; r < runs; r++) {
        const squad = createDefaultSquad(lv, 'standard');
        fakeStu.roster = squad;
        launchSimulation({ mode: 'tower', title: 'sim', blueStudent: fakeStu, towerFloorObj: floorObj, customBlueUnits: squad.map(m => createSimUnit(m, fakeStu, 'blue', 1.0)) });
        setBattleControlMode('auto', null, true);
        const alive = t => sim.units.some(u => u.team === t && u.alive && isMain(u));
        let n = 0;
        while (n < 20000 && sim.running && alive('blue') && alive('red')) { stepSimulation(); n++; }
        if (alive('blue') && !alive('red')) wins++;
        ticks += n;
        sim.running = false;
        await BS.yieldNow();
      }
      out[f] = { race: floorObj.race, boss: Boolean(floorObj.isRaceBoss), win: pct(wins / runs), sec: Math.round(ticks / runs / BATTLE_TICKS_PER_SEC) };
    }
    document.getElementById('battleResultOverlay')?.classList.add('hidden');
    return out;
  };
})();

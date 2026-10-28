/********************************************************************
 * 테스트 전장 (주소 /test, localhost 전용)
 * - index.html의 전투 엔진을 그대로 써서, 용병·몬스터·허수아비를 마음대로 놓고 행동·스킬·쿨타임을 시험함
 * - index.html의 applyLocalDevEntry()가 ?dev=sandbox 일 때 이 파일을 불러옴
 * - 엔진 쪽 연결: stepSimulation의 sandboxPreTick() · 전투 종료 판정 건너뛰기 · selectStrategicSkillToCast의 sbNoSkill/sbBlockSkills
 ********************************************************************/
(function () {
  const JOBS = Object.keys(JOB_DEFS);
  const RARITIES = [['N', '일반'], ['R', '레어'], ['SCR', '시크릿 레어']];
  const KINDS = [['merc', '용병'], ['monster', '몬스터'], ['scarecrow', '허수아비']];
  const PRESETS = [
    ['ai', '정상 AI', { move: 1, attack: 1, skill: 1, dash: 1 }],
    ['hold', '가만히', { move: 0, attack: 0, skill: 0, dash: 0 }],
    ['move', '이동만', { move: 1, attack: 0, skill: 0, dash: 1 }],
    ['atk', '제자리 평타', { move: 0, attack: 1, skill: 0, dash: 0 }],
    ['skill', '제자리 스킬', { move: 0, attack: 0, skill: 1, dash: 0 }],
    ['noskill', '스킬 없이', { move: 1, attack: 1, skill: 0, dash: 1 }]
  ];

  const SB = window.SB = { specs: [], sel: null, cd: true, seq: 0, placing: null, manual: null, mana: true, monList: [], mons: {} };

  // ----- 몬스터 목록: 모험의 탑 종족 편성에서 (몬스터, 직업, 이름, 스킬) -----
  TOWER_RACES.forEach(race => {
    const sq = TOWER_RACE_SQUADS[race.name];
    if (!sq) return;
    const group = { race: race.name, items: [] };
    Object.keys(sq).forEach(job => {
      if (job === 'boss') return;
      sq[job].forEach(([mon, name, skills]) => group.items.push({ key: `${mon}|${job}`, mon, job, name, skills, boss: false }));
    });
    const bm = MONSTER_DEFS[race.boss];
    if (bm) group.items.push({ key: `${race.boss}|boss`, mon: race.boss, job: 'warrior', name: `${bm.name} (보스)`, skills: sq.boss, boss: true });
    SB.monList.push(group);
    group.items.forEach(it => { SB.mons[it.key] = it; });
  });
  const firstMon = SB.monList[0].items[0].key;

  // ----- 새로고침해도 배치·설정 유지 (이 브라우저의 localStorage) -----
  const STORE_KEY = 'caSandboxV1';
  function saveState() {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify({ specs: SB.specs, cd: SB.cd, mana: SB.mana, form, sel: SB.sel }));
    } catch (e) {}
  }
  function loadState() {
    try {
      const d = JSON.parse(localStorage.getItem(STORE_KEY) || 'null');
      if (!d || !Array.isArray(d.specs)) return;
      SB.specs = d.specs.filter(sp => sp && JOB_DEFS[sp.job] && (sp.kind !== 'monster' || SB.mons[sp.mon]));
      SB.seq = SB.specs.reduce((m, sp) => Math.max(m, sp.id || 0), 0);
      if (typeof d.cd === 'boolean') SB.cd = d.cd;
      if (typeof d.mana === 'boolean') SB.mana = d.mana;
      if (d.form) Object.assign(form, d.form);
      SB.sel = SB.specs.some(sp => sp.id === d.sel) ? d.sel : null;
    } catch (e) {}
  }

  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const defBeh = () => ({ move: 1, attack: 1, skill: 1, dash: 1, block: {} });
  const form = { team: 'blue', kind: 'merc', job: 'warrior', rarity: 'N', level: 40, skin: 0, mon: firstMon, floor: 20, hp: 50000, atk: 4, def: 10, allSkills: 0 };

  // ----- 유닛 만들기 -----
  function freeCell(team) {
    const used = new Set(SB.specs.filter(s => s.team === team && s.x == null).map(s => `${s.col},${s.row}`));
    for (const col of [2, 1, 0]) for (const row of [2, 1, 3, 0, 4]) if (!used.has(`${col},${row}`)) return { col, row };
    return { col: 0, row: 2 };
  }
  function newSpec(over) {
    const cell = freeCell(over.team || form.team);
    return Object.assign({ id: ++SB.seq, name: '', col: cell.col, row: cell.row, x: null, y: null, beh: defBeh() }, form, over);
  }

  function buildUnit(sp, pos) {
    let u;
    if (sp.kind === 'scarecrow') {
      const m = createMercenary('warrior', 'N', 1, 0, true, 'whirlwind');
      Object.assign(m, { name: sp.name || '훈련용 허수아비', monsterType: 'scarecrow', isDarkMerc: false, row: sp.row, col: sp.col,
        overrideMaxHp: sp.hp, overrideAtk: sp.atk, overrideDef: sp.def, overrideMoveSpeed: 0.04 });
      u = createSimUnit(m, null, sp.team, 1.0);
    } else if (sp.kind === 'monster') {
      const ent = SB.mons[sp.mon] || SB.mons[firstMon];
      const setup = towerEnemySetup(sp.floor);
      const m = createMercenary(ent.job, 'N', setup.level, 0, true, ent.skills[0]);
      Object.assign(m, { name: sp.name || ent.name, monsterType: ent.mon, isDarkMerc: false, row: sp.row, col: sp.col });
      u = createSimUnit(m, null, sp.team, setup.scale);
      applyMonsterTraits(u, ent.mon, ent.boss, sp.floor);
      applyUnitSkillBook(u, sp.allSkills ? { ...JOB_SKILL_BOOK[ent.job] } : buildSkillBook(ent.skills));
    } else {
      const m = createMercenary(sp.job, sp.rarity, sp.level, 0, true, null);
      Object.assign(m, { skinVariant: sp.skin, row: sp.row, col: sp.col });
      if (sp.name) m.name = sp.name;
      u = createSimUnit(m, null, sp.team, 1.0);
      // 직업 스킬 + 히든 스킬을 레벨과 상관없이 전부 열어 둠
      const keys = Object.keys(JOB_SKILL_BOOK[sp.job]);
      u.skillSlots = keys;
      u.unlockedSkills = [...keys];
      u.skillCooldowns = {};
      keys.forEach(k => { u.skillCooldowns[k] = 0; });
    }
    const p = pos || (sp.x != null ? { x: sp.x, y: sp.y } : null);
    if (p) { u.x = p.x; u.y = p.y; }
    u._ix = u.x; u._iy = u.y;
    u.sbId = sp.id;
    u.sbBeh = sp.beh;
    return u;
  }
  const unitOf = id => sim.units.find(u => u.sbId === id);

  // ----- 수동 전투: 엔진의 직접 조종(WASD 이동 · 좌클릭/K 공격 · Space 대시 · 1~4 스킬)을 유닛 하나에 붙임 -----
  function setManual(id) {
    const u = id != null ? unitOf(id) : null;
    SB.manual = u ? id : null;
    if (u) setBattleControlMode('manual', u.id, true);
    else setBattleControlMode('auto', null, true);
  }

  function rebuildOne(sp, keepPos = true) {
    const old = unitOf(sp.id);
    let pos = null;
    if (old) {
      if (keepPos) pos = { x: old.x, y: old.y };
      sim.units = sim.units.filter(u => u !== old && u.ownerId !== old.id);
    }
    sim.units.push(buildUnit(sp, pos));
    renderLiveUnitStatus();
    if (SB.manual === sp.id) setManual(sp.id); // 새로 만든 유닛에 조종을 다시 붙임
  }
  function rebuildAll() {
    if (SB.manual != null) setManual(null);
    sim.units = [];
    sim.projectiles = []; sim.effects = []; sim.zones = []; sim.floatTexts = [];
    SB.specs.forEach(sp => sim.units.push(buildUnit(sp, null)));
    renderLiveUnitStatus();
  }

  // ----- 엔진이 매 틱 부르는 훅: 쿨타임 끄기 · 행동 제한 -----
  window.sandboxPreTick = function () {
    sim.units.forEach(u => {
      if (!u.alive) return;
      if (!SB.cd) {
        if (u.skillCooldowns) Object.keys(u.skillCooldowns).forEach(k => { u.skillCooldowns[k] = 0; });
        u.itemCd = 0;
        u.castLock = 0;
      }
      if (!SB.mana) u.mana = u.maxMana;
      const b = u.sbBeh;
      if (!b) return;
      if (u._sbMove === undefined) u._sbMove = u.baseMoveSpeed;
      u.baseMoveSpeed = b.move ? u._sbMove : 0;
      if (!b.dash) u.dashCooldown = Math.max(u.dashCooldown || 0, 30);
      if (!b.attack) u.cooldown = Math.max(u.cooldown || 0, 30);
      u.sbNoSkill = !b.skill;
      u.sbBlockSkills = b.block;
    });
  };

  // ----- 스킬 바로 쓰기 (직접 조종할 때와 같은 규칙: 마나·쿨타임·사거리) -----
  function castSkill(id, key) {
    const u = unitOf(id);
    if (!u || !u.alive) return;
    if (!SB.cd) {
      Object.keys(u.skillCooldowns).forEach(k => { u.skillCooldowns[k] = 0; });
      u.castLock = 0;
    }
    if (!SB.mana) u.mana = u.maxMana;
    const allies = sim.units.filter(a => a.alive && a.team === u.team);
    const enemies = sim.units.filter(e => e.alive && e.team !== u.team);
    tryManualSkill(u, allies, enemies, u.skillSlots.indexOf(key), {});
  }

  // ----- 화면 -----
  const selOpts = (list, cur) => list.map(([v, l]) => `<option value="${v}"${String(v) === String(cur) ? ' selected' : ''}>${esc(l)}</option>`).join('');
  const monOpts = cur => SB.monList.map(g => `<optgroup label="${esc(g.race)}">${g.items.map(it =>
    `<option value="${it.key}"${it.key === cur ? ' selected' : ''}>${esc(it.name)} (${esc(JOB_DEFS[it.job].name)})</option>`).join('')}</optgroup>`).join('');
  const skinOpts = (job, cur) => Array.from({ length: getMercSkinCount(job) }, (_, i) => [i, `외형 ${i + 1}`]);
  const cls = {
    in: 'bg-slate-800 border border-slate-600 rounded px-1.5 py-1 text-slate-100 text-xs w-full',
    btn: 'px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-100 text-xs font-bold',
    h: 'text-amber-300 font-extrabold text-xs mb-1.5',
    box: 'bg-slate-900 border border-slate-700 rounded-xl p-2.5 mb-2.5'
  };
  const field = (label, html) => `<label class="flex flex-col gap-0.5 text-[10px] text-slate-400">${label}${html}</label>`;
  const num = (val, onch, min, max) => `<input type="number" class="${cls.in}" value="${val}" min="${min}" max="${max}" onchange="${onch}">`;

  function unitIcon(sp) {
    if (sp.kind === 'scarecrow') return '🎯';
    if (sp.kind === 'monster') return (MONSTER_DEFS[(SB.mons[sp.mon] || {}).mon] || {}).icon || '👾';
    return getMercIconHTML(sp.job, sp.skin, 22);
  }
  function specTitle(sp) {
    if (sp.name) return sp.name;
    if (sp.kind === 'scarecrow') return '허수아비';
    if (sp.kind === 'monster') return (SB.mons[sp.mon] || {}).name || '몬스터';
    return `${JOB_DEFS[sp.job].name} Lv.${sp.level}`;
  }

  function addForm() {
    const f = form;
    return `<div class="${cls.box}"><div class="${cls.h}">➕ 유닛 추가</div>
      <div class="grid grid-cols-2 gap-1.5">
        ${field('진영', `<select class="${cls.in}" onchange="SBUI.form('team',this.value)">${selOpts([['blue', '🔵 아군'], ['red', '🔴 적']], f.team)}</select>`)}
        ${field('종류', `<select class="${cls.in}" onchange="SBUI.form('kind',this.value)">${selOpts(KINDS, f.kind)}</select>`)}
        ${f.kind === 'merc' ? `
          ${field('직업', `<select class="${cls.in}" onchange="SBUI.form('job',this.value)">${selOpts(JOBS.map(j => [j, JOB_DEFS[j].name]), f.job)}</select>`)}
          ${field('등급', `<select class="${cls.in}" onchange="SBUI.form('rarity',this.value)">${selOpts(RARITIES, f.rarity)}</select>`)}
          ${field('레벨', num(f.level, "SBUI.form('level',+this.value)", 1, 100))}
          ${field('외형', `<select class="${cls.in}" onchange="SBUI.form('skin',+this.value)">${selOpts(skinOpts(f.job), f.skin)}</select>`)}` : ''}
        ${f.kind === 'monster' ? `
          <div class="col-span-2">${field('몬스터', `<select class="${cls.in}" onchange="SBUI.form('mon',this.value)">${monOpts(f.mon)}</select>`)}</div>
          ${field('강도 (탑 층수)', num(f.floor, "SBUI.form('floor',+this.value)", 1, 200))}
          ${field('스킬', `<select class="${cls.in}" onchange="SBUI.form('allSkills',+this.value)">${selOpts([[0, '몬스터 고유 스킬'], [1, '직업 스킬 전부']], f.allSkills)}</select>`)}` : ''}
        ${f.kind === 'scarecrow' ? `
          ${field('체력', num(f.hp, "SBUI.form('hp',+this.value)", 1, 99999999))}
          ${field('공격력', num(f.atk, "SBUI.form('atk',+this.value)", 0, 99999))}
          ${field('방어력', num(f.def, "SBUI.form('def',+this.value)", 0, 99999))}` : ''}
      </div>
      <div class="flex gap-1.5 mt-2"><button class="${cls.btn} bg-emerald-600 hover:bg-emerald-500 flex-1" onclick="SBUI.add()">추가</button></div></div>`;
  }

  function editor(sp) {
    const u = unitOf(sp.id);
    const b = sp.beh;
    const chk = (k, l) => `<label class="flex items-center gap-1 text-[11px] text-slate-200"><input type="checkbox" ${b[k] ? 'checked' : ''} onchange="SBUI.beh(${sp.id},'${k}',this.checked)">${l}</label>`;
    let h = `<div class="mt-2 pt-2 border-t border-slate-700">
      <div class="grid grid-cols-2 gap-1.5">
        ${field('이름 (비우면 기본)', `<input class="${cls.in}" value="${esc(sp.name)}" onchange="SBUI.set(${sp.id},'name',this.value)">`)}
        ${field('진영', `<select class="${cls.in}" onchange="SBUI.set(${sp.id},'team',this.value)">${selOpts([['blue', '🔵 아군'], ['red', '🔴 적']], sp.team)}</select>`)}
        ${sp.kind === 'merc' ? `
          ${field('직업', `<select class="${cls.in}" onchange="SBUI.set(${sp.id},'job',this.value)">${selOpts(JOBS.map(j => [j, JOB_DEFS[j].name]), sp.job)}</select>`)}
          ${field('등급', `<select class="${cls.in}" onchange="SBUI.set(${sp.id},'rarity',this.value)">${selOpts(RARITIES, sp.rarity)}</select>`)}
          ${field('레벨', num(sp.level, `SBUI.set(${sp.id},'level',+this.value)`, 1, 100))}
          ${field('외형', `<select class="${cls.in}" onchange="SBUI.set(${sp.id},'skin',+this.value)">${selOpts(skinOpts(sp.job), sp.skin)}</select>`)}` : ''}
        ${sp.kind === 'monster' ? `
          <div class="col-span-2">${field('몬스터', `<select class="${cls.in}" onchange="SBUI.set(${sp.id},'mon',this.value)">${monOpts(sp.mon)}</select>`)}</div>
          ${field('강도 (탑 층수)', num(sp.floor, `SBUI.set(${sp.id},'floor',+this.value)`, 1, 200))}
          ${field('스킬', `<select class="${cls.in}" onchange="SBUI.set(${sp.id},'allSkills',+this.value)">${selOpts([[0, '몬스터 고유 스킬'], [1, '직업 스킬 전부']], sp.allSkills)}</select>`)}` : ''}
        ${sp.kind === 'scarecrow' ? `
          ${field('체력', num(sp.hp, `SBUI.set(${sp.id},'hp',+this.value)`, 1, 99999999))}
          ${field('공격력', num(sp.atk, `SBUI.set(${sp.id},'atk',+this.value)`, 0, 99999))}
          ${field('방어력', num(sp.def, `SBUI.set(${sp.id},'def',+this.value)`, 0, 99999))}` : ''}
        ${field('칸 (가로 0~2)', num(sp.col, `SBUI.set(${sp.id},'col',+this.value)`, 0, 2))}
        ${field('칸 (세로 0~4)', num(sp.row, `SBUI.set(${sp.id},'row',+this.value)`, 0, 4))}
      </div>
      <div class="flex gap-1.5 mt-2 flex-wrap">
        <button class="${cls.btn} ${SB.placing === sp.id ? 'bg-amber-600' : ''}" onclick="SBUI.place(${sp.id})">${SB.placing === sp.id ? '전장을 클릭하세요…' : '📍 전장 클릭으로 배치'}</button>
        <button class="${cls.btn} ${SB.manual === sp.id ? 'bg-indigo-600' : ''}" onclick="SBUI.manual(${sp.id})">${SB.manual === sp.id ? '🎮 조종 중 (끄기)' : '🎮 수동 조종'}</button>
        <button class="${cls.btn}" onclick="SBUI.dup(${sp.id})">복제</button>
        <button class="${cls.btn} bg-rose-700 hover:bg-rose-600" onclick="SBUI.del(${sp.id})">삭제</button>
      </div>
      <div class="mt-2 text-[10px] text-slate-400 font-bold">행동</div>
      <div class="flex gap-1 flex-wrap mt-1">${PRESETS.map(p => `<button class="${cls.btn} text-[10px]" onclick="SBUI.preset(${sp.id},'${p[0]}')">${p[1]}</button>`).join('')}</div>
      <div class="flex gap-3 flex-wrap mt-1.5">${chk('move', '이동')}${chk('attack', '기본공격')}${chk('skill', '스킬 자동사용')}${chk('dash', '대시')}</div>`;
    if (u) {
      const book = unitSkillBook(u);
      h += `<div class="mt-2 text-[10px] text-slate-400 font-bold">스킬 (▶ 지금 사용 · ☑ 자동 사용 허용)</div><div class="flex flex-col gap-1 mt-1">` +
        (u.skillSlots || []).map(k => {
          const s = book[k]; if (!s) return '';
          return `<div class="flex items-center gap-1.5 bg-slate-800 rounded px-1.5 py-1">
            <button class="${cls.btn} px-1.5" onclick="SBUI.cast(${sp.id},'${k}')">▶</button>
            <span class="text-xs text-slate-100 flex-1">${s.icon} ${esc(s.name)}</span>
            <span class="text-[10px] text-slate-400" data-cd="${k}">-</span>
            <input type="checkbox" title="자동 사용 허용" ${b.block[k] ? '' : 'checked'} onchange="SBUI.block(${sp.id},'${k}',this.checked)"></div>`;
        }).join('') + '</div>';
    }
    return h + '</div>';
  }

  function render() {
    const el = document.getElementById('sbPanel');
    if (!el) return;
    saveState();
    const scroll = el.scrollTop;
    const row = sp => `<div class="rounded-lg border ${SB.sel === sp.id ? 'border-amber-400 bg-slate-800' : 'border-slate-700 bg-slate-900'} p-1.5 mb-1">
      <div class="flex items-center gap-1.5 cursor-pointer" onclick="SBUI.select(${sp.id})">
        <span class="w-2 h-2 rounded-full ${sp.team === 'blue' ? 'bg-blue-500' : 'bg-rose-500'}"></span>
        <span class="w-6 flex justify-center">${unitIcon(sp)}</span>
        <span class="text-xs text-slate-100 font-bold flex-1">${esc(specTitle(sp))}</span>
        <span class="text-[10px] text-slate-500" data-hp="${sp.id}"></span></div>
      ${SB.sel === sp.id ? editor(sp) : ''}</div>`;
    el.innerHTML = `
      <div class="text-sm font-extrabold text-white mb-2">🧪 테스트 전장 <span class="text-[10px] text-slate-500 font-normal">/test</span></div>
      <div class="${cls.box}"><div class="${cls.h}">⚙️ 전투</div>
        <div class="flex items-center gap-2 flex-wrap">
          <label class="flex items-center gap-1 text-xs text-slate-200"><input type="checkbox" ${SB.cd ? 'checked' : ''} onchange="SBUI.cdToggle(this.checked)">⏳ 쿨타임 적용</label>
          <label class="flex items-center gap-1 text-xs text-slate-200"><input type="checkbox" ${SB.mana ? 'checked' : ''} onchange="SBUI.manaToggle(this.checked)">💧 마나 소모 적용</label>
          <label class="flex items-center gap-1 text-xs text-slate-200"><input type="checkbox" ${SB.manual != null ? 'checked' : ''} onchange="SBUI.manualToggle(this.checked)">🎮 수동 전투${SB.manual != null && byId(SB.manual) ? ` (${esc(specTitle(byId(SB.manual)))})` : ''}</label>
          <select class="${cls.in} !w-auto" onchange="sim.speed=+this.value">${selOpts([[0, '⏸ 일시정지'], [0.5, '0.5배'], [1, '1배'], [2, '2배'], [3, '3배']], sim.speed)}</select>
        </div>
        <div class="flex gap-1.5 flex-wrap mt-2">
          <button class="${cls.btn}" onclick="SBUI.healAll()">❤️ 체력·마나 회복</button>
          <button class="${cls.btn}" onclick="SBUI.reset()">🔄 처음 위치로 다시 시작</button>
          <button class="${cls.btn}" onclick="SBUI.clearFx()">✨ 이펙트 정리</button>
        </div>
        <div class="flex gap-1.5 flex-wrap mt-1.5">
          <button class="${cls.btn}" onclick="SBUI.team('red','hold')">🔴 적 전체 정지</button>
          <button class="${cls.btn}" onclick="SBUI.team('red','ai')">🔴 적 AI 켜기</button>
          <button class="${cls.btn}" onclick="SBUI.team('blue','hold')">🔵 아군 전체 정지</button>
          <button class="${cls.btn}" onclick="SBUI.team('blue','ai')">🔵 아군 AI 켜기</button>
        </div></div>
      ${addForm()}
      <div class="${cls.box}"><div class="flex items-center justify-between mb-1.5"><div class="${cls.h} !mb-0">📋 배치된 유닛 (${SB.specs.length})</div>
        <div class="flex gap-1"><button class="${cls.btn}" onclick="SBUI.preset5()">기본 5:5 허수아비</button><button class="${cls.btn} bg-rose-700 hover:bg-rose-600" onclick="SBUI.clearAll()">모두 비우기</button></div></div>
        ${SB.specs.map(row).join('') || '<div class="text-xs text-slate-500">유닛이 없어요. 위에서 추가하세요.</div>'}</div>
      <div class="text-[10px] text-slate-500 leading-relaxed">• 전투는 끝나지 않아요. 쓰러진 유닛은 ‘처음 위치로 다시 시작’이나 편집으로 되살려요.<br>• 수동 전투: WASD 이동 · 좌클릭/K 공격 · Space 대시 · 1~4 스킬 · 마우스로 조준.<br>• 마우스 드래그로 시점 이동, 휠로 확대·축소.</div>`;
    el.scrollTop = scroll;
  }

  // 0.25초마다: 선택한 유닛의 스킬 쿨타임·체력 표시만 갱신 (패널을 다시 그리지 않음)
  setInterval(() => {
    const el = document.getElementById('sbPanel');
    if (!el) return;
    SB.specs.forEach(sp => {
      const u = unitOf(sp.id);
      const t = el.querySelector(`[data-hp="${sp.id}"]`);
      if (t) t.textContent = !u ? '' : (u.alive ? `${Math.round(u.hp / u.maxHp * 100)}%` : '💀');
    });
    const u = SB.sel != null ? unitOf(SB.sel) : null;
    if (!u) return;
    el.querySelectorAll('[data-cd]').forEach(s => {
      const cd = u.skillCooldowns[s.dataset.cd] || 0;
      s.textContent = cd > 0 ? `${(cd / 60).toFixed(1)}초` : '준비';
      s.style.color = cd > 0 ? '#94a3b8' : '#fbbf24';
    });
  }, 250);

  // ----- 패널에서 부르는 동작 -----
  const byId = id => SB.specs.find(s => s.id === id);
  window.SBUI = {
    form(k, v) {
      form[k] = v;
      if (k === 'job') form.skin = 0;
      render();
    },
    add() {
      const sp = newSpec({});
      SB.specs.push(sp);
      SB.sel = sp.id;
      sim.units.push(buildUnit(sp, null));
      renderLiveUnitStatus();
      render();
    },
    select(id) { SB.sel = SB.sel === id ? null : id; render(); },
    set(id, k, v) {
      const sp = byId(id); if (!sp) return;
      sp[k] = v;
      if (k === 'job') sp.skin = 0;
      const moved = k === 'col' || k === 'row';
      if (moved) { sp.x = sp.y = null; sp.col = Math.max(0, Math.min(2, sp.col)); sp.row = Math.max(0, Math.min(4, sp.row)); }
      rebuildOne(sp, !moved);
      render();
    },
    del(id) {
      if (SB.manual === id) setManual(null);
      const old = unitOf(id);
      if (old) sim.units = sim.units.filter(u => u !== old && u.ownerId !== old.id);
      SB.specs = SB.specs.filter(s => s.id !== id);
      if (SB.sel === id) SB.sel = null;
      renderLiveUnitStatus(); render();
    },
    dup(id) {
      const src = byId(id); if (!src) return;
      const cell = freeCell(src.team);
      const sp = Object.assign({}, src, { id: ++SB.seq, col: cell.col, row: cell.row, x: null, y: null, beh: { ...src.beh, block: { ...src.beh.block } } });
      SB.specs.push(sp); SB.sel = sp.id;
      sim.units.push(buildUnit(sp, null));
      renderLiveUnitStatus(); render();
    },
    place(id) { SB.placing = SB.placing === id ? null : id; render(); },
    beh(id, k, v) { byId(id).beh[k] = v ? 1 : 0; saveState(); },
    block(id, k, allowed) { const b = byId(id).beh.block; if (allowed) delete b[k]; else b[k] = true; saveState(); },
    preset(id, name) {
      const sp = byId(id), p = PRESETS.find(x => x[0] === name);
      if (sp && p) Object.assign(sp.beh, p[2]);
      render();
    },
    team(team, name) {
      const p = PRESETS.find(x => x[0] === name);
      SB.specs.filter(s => s.team === team).forEach(s => Object.assign(s.beh, p[2]));
      render();
    },
    cast(id, key) { castSkill(id, key); },
    manual(id) { setManual(SB.manual === id ? null : id); render(); },
    manualToggle(on) {
      if (!on) setManual(null);
      else {
        const pick = byId(SB.sel) || SB.specs.find(s => s.team === 'blue' && unitOf(s.id));
        if (pick) setManual(pick.id);
      }
      render();
    },
    cdToggle(on) { SB.cd = on; saveState(); },
    manaToggle(on) { SB.mana = on; saveState(); },
    healAll() {
      sim.units.forEach(u => {
        if (!u.alive) return;
        u.hp = u.maxHp; u.mana = u.maxMana;
        Object.keys(u.statuses).forEach(k => { u.statuses[k] = 0; });
        Object.keys(u.skillCooldowns || {}).forEach(k => { u.skillCooldowns[k] = 0; });
      });
    },
    reset() { SB.specs.forEach(s => { s.x = s.y = null; }); rebuildAll(); render(); },
    clearFx() { sim.projectiles = []; sim.effects = []; sim.zones = []; sim.floatTexts = []; },
    clearAll() { SB.specs = []; SB.sel = null; rebuildAll(); render(); },
    preset5() {
      SB.specs = [];
      ['warrior', 'knight', 'mage', 'healer', 'archer'].forEach((job, i) =>
        SB.specs.push(newSpec({ team: 'blue', kind: 'merc', job, rarity: 'N', level: 40, skin: 0, col: [2, 2, 1, 0, 0][i], row: [1, 3, 2, 1, 3][i], name: '' })));
      for (let r = 0; r < 5; r++) SB.specs.push(newSpec({ team: 'red', kind: 'scarecrow', col: 2, row: r }));
      SB.sel = null; rebuildAll(); render();
    }
  };

  // ----- 전장 클릭으로 배치 -----
  document.getElementById('arenaCanvas').addEventListener('click', e => {
    if (SB.placing == null) return;
    const sp = byId(SB.placing), u = sp && unitOf(sp.id);
    SB.placing = null;
    if (sp && u) {
      const p = arenaCanvasPos(e.clientX, e.clientY), z = sim.camera.zoom || 1;
      sp.x = Math.max(200, Math.min(sim.worldW - 200, sim.camera.x + p.cx / z));
      sp.y = Math.max(260, Math.min(sim.worldH - 220, sim.camera.y + p.cy / z));
      u.x = u._ix = u.prevX = sp.x; u.y = u._iy = u.prevY = sp.y;
    }
    render();
  }, true);

  // ----- 화면 꾸리기: 전장을 전체 화면 덮개 안으로 옮기고 왼쪽에 패널 -----
  document.getElementById('mainAppShell').classList.remove('hidden'); // 전장이 보여야 전투 루프가 그림
  const arena = document.getElementById('arenaSection');
  const wrap = document.createElement('div');
  wrap.style.cssText = 'position:fixed;inset:0;z-index:9999;display:flex;background:#020617;';
  wrap.innerHTML = '<div id="sbPanel" style="width:400px;flex:none;overflow-y:auto;padding:10px;background:#0b1220;border-right:1px solid #1e293b"></div><div id="sbArena" style="flex:1;min-width:0;overflow-y:auto;padding:8px"></div>';
  document.body.appendChild(wrap);
  document.getElementById('sbArena').appendChild(arena);
  arena.classList.remove('hidden');
  document.getElementById('arenaCanvas').style.height = 'calc(100vh - 150px)';
  ['forfeitBattle', 'startPracticeSim', 'closeArenaOrForfeit'].forEach(fn => {
    const b = arena.querySelector(`[onclick^="${fn}"]`); if (b) b.style.display = 'none';
  });
  document.getElementById('arenaModeBadge').textContent = '🧪 테스트 전장';
  document.getElementById('arenaMatchTitle').textContent = '용병·몬스터·허수아비 마음대로 시험하기';
  document.getElementById('battleResultOverlay').classList.add('hidden');

  // ----- 전투 상태를 테스트용으로 시작 -----
  Object.assign(sim, { sandbox: true, mode: 'sandbox', running: true, speed: 1, tickCount: 0, netRole: null, myTeam: 'blue',
    controllers: {}, awaitingControlChoice: false, waitingForOpponent: false, meta: {}, eliteIntro: null, forfeitTeam: null,
    spectator: false, duel1v1: false, teamLive: false, towerWatch: null, raidWatch: null, raidLive: null });
  battleControl.mode = 'auto'; battleControl.unitId = null; battleControl.locked = true;
  loadState(); // 저장된 게 없으면 아무도 없는 빈 전장 (기본 5:5는 버튼으로)
  rebuildAll();
  render();
  resetArenaCamera('center');
})();

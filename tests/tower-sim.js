// 모험의 탑 난이도 측정 (브라우저 콘솔용): 층과 같은 레벨대의 기본 용병단으로 여러 번 싸워 승률을 봄
// 사용법: 이 파일을 불러온 뒤 await towerWinRates([1, 5, 10], 10, 0)
window.towerWinRates = async function (floors, runs = 10, levelOffset = 0) {
  suppressRemoteClassPush = true;
  // 시뮬 중에는 소리 끔
  sfxEnabled = false;
  playCombatSfx = () => {};
  const out = {};
  const fakeStu = { id: 'sim_stu', name: '시뮬', roster: [], relics: {}, inventory: [] };
  for (const f of floors) {
    const floorObj = TOWER_FLOORS.find(t => t.floor === f);
    if (!floorObj) continue;
    const lv = Math.max(1, Math.round(1 + f * 0.95) + levelOffset);
    let wins = 0, ticks = 0;
    for (let r = 0; r < runs; r++) {
      const squad = createDefaultSquad(lv, 'standard');
      // 10레벨마다 받는 SP를 골고루 나눠 둠 (학생들이 보통 하는 것처럼)
      squad.forEach(m => { const sp = Math.floor(lv / 10) * FIXED_SP_PER_10_LEVELS; m.statPoints = { hp: Math.ceil(sp / 2), atk: Math.floor(sp / 2), def: 0, spd: 0 }; });
      fakeStu.roster = squad;
      launchSimulation({
        mode: 'tower', title: 'sim', blueStudent: fakeStu, towerFloorObj: floorObj,
        customBlueUnits: squad.map(m => createSimUnit(m, fakeStu, 'blue', 1.0))
      });
      setBattleControlMode('auto', null, true);
      let n = 0;
      const alive = t => sim.units.some(u => u.team === t && u.hp > 0);
      while (n < 20000 && sim.running && alive('blue') && alive('red')) { stepSimulation(); n++; }
      if (alive('blue') && !alive('red')) wins++;
      ticks += n;
      sim.running = false;
      await new Promise(res => setTimeout(res, 0));
    }
    out[f] = { win: Math.round((wins / runs) * 100) + '%', avgSec: Math.round(ticks / runs / 60) };
  }
  document.getElementById('battleResultOverlay')?.classList.add('hidden');
  return out;
};

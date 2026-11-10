// 실시간 전투 화면의 투사체 '짧은 꼴' 점검 (2026-11-10): 보내는 쪽이 줄여 보낸 것을 받는 쪽이 매 화면 온전히 되살리는지
// (예전엔 받는 쪽 표가 매 화면 비워져, 서버 화면으로 보는 친구는 투사체가 발사된 첫 장만 보이고 사라졌음)
// node live-proj.test.cjs [../index.html]
const fs = require('fs'); const assert = require('assert');
const src = fs.readFileSync((process.argv[2] || '../index.html'), 'utf8');
const grab = (from, to) => { const a = src.indexOf(from); const b = src.indexOf(to, a); if (a < 0 || b < 0) throw new Error(from); return src.slice(a, b); };
const code = grab('    function packLiveProjectile(p)', '    function publishLiveBattleFrame');
const f = new Function(`const liveNum=v=>(typeof v==='number'&&isFinite(v)?v:0);
const liveR1=v=>Math.round(liveNum(v)*10)/10; const liveR2=v=>Math.round(liveNum(v)*100)/100;
const BATTLE_PROJECTILE_SPEED=1; let liveFrameV2=true; const liveNet={};
${code}
return { packLiveProjectile, packLiveProjectiles, expandLiveProjectiles, liveNet };`)();
// 서버를 거친 모양 (JSON 왕복)
const wire = v => (v === undefined ? undefined : JSON.parse(JSON.stringify(v)));
// 받는 쪽: applyLiveFrame이 하는 대로 — 전체 화면이면 표를 새로, 그 뒤 매 화면 되살림
const makeReceiver = () => { let table = null; return (p, keyframe) => { if (keyframe || !table) table = new Map(); return f.expandLiveProjectiles(wire(p), table); }; };
const norm = q => [q[0], q[1], q[2], q[3], q[4] || '', q[5] || 0, q[6], q[7], q[8] || ''];
const mk = (type, x, extra = {}) => ({ x, y: 500, angle: 0.5, projType: type, isDirectional: true, speed: 6, ...extra });
let n = 0; const t = (name, fn) => { fn(); n++; console.log('ok', name); };
const fresh = () => { Object.keys(f.liveNet).forEach(k => delete f.liveNet[k]); };

t('발사 뒤 여러 화면 동안 계속 보임 (짧은 꼴로 와도 종류·색·그림이 그대로)', () => {
  fresh(); const recv = makeReceiver();
  const a = mk('arrow_proj', 100, { color: '#f00', radius: 12, spr: 'storm' }), b = mk('magic_orb', 300);
  const frames = [[true, [a]], [false, [a]], [false, [a, b]], [false, [a, b]], [false, [b]]];
  frames.forEach(([key, list], i) => {
    list.forEach(q => { q.x += 9; });
    const sent = f.packLiveProjectiles(list, key);
    if (i === 1) assert.strictEqual(sent[0].length, 6, '두 번째 화면부터는 짧은 꼴'); // 보내는 쪽이 정말 줄여 보내는지
    const got = recv(sent, key);
    assert.strictEqual(got.length, list.length, `화면 ${i}: 투사체 수`);
    got.forEach((g, j) => assert.deepStrictEqual(norm(g), norm(f.packLiveProjectile(list[j])), `화면 ${i} 투사체 ${j}`));
  });
});
t('전체 화면이 다시 와도(4초마다) 끊기지 않음', () => {
  fresh(); const recv = makeReceiver();
  const a = mk('fireball_proj', 100, { radius: 30 });
  [[true], [false], [false], [true], [false], [false]].forEach(([key], i) => {
    const got = recv(f.packLiveProjectiles([a], key), key);
    assert.strictEqual(got.length, 1, `화면 ${i}`);
    assert.strictEqual(got[0][3], 'fireball_proj');
    assert.strictEqual(got[0][5], 30);
  });
});
t('도중에 들어온 친구: 모르는 번호는 건너뛰고, 다음 전체 화면부터 보임', () => {
  fresh(); const host = k => f.packLiveProjectiles([a], k); const a = mk('arrow_proj', 100);
  host(true); host(false);                       // 내가 들어오기 전
  const recv = makeReceiver();
  assert.strictEqual(recv(host(false), false).length, 0);
  assert.strictEqual(recv(host(true), true).length, 1);
  assert.strictEqual(recv(host(false), false).length, 1);
});
t('직접 연결·예전 형식(늘 통째 꼴)은 그대로 통과', () => {
  const recv = makeReceiver();
  const full = [f.packLiveProjectile(mk('arrow_proj', 100)), f.packLiveProjectile(mk('magic_orb', 200, { spr: 'teleport' }))];
  assert.deepStrictEqual(recv(full, true), wire(full));
  assert.deepStrictEqual(recv(full, false), wire(full));
  assert.strictEqual(recv(undefined, false), undefined); // 투사체가 없어 칸이 빠진 화면
});
console.log('all', n);

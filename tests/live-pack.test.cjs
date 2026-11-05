// 실시간 전투 화면의 투사체·이펙트 압축 점검: 줄어든 모양을 받는 쪽(예전·새 코드 모두)이 같은 값으로 읽는지
// node live-pack.test.cjs [../index.html]
const fs = require('fs'); const assert = require('assert');
const src = fs.readFileSync((process.argv[2] || '../index.html'), 'utf8');
const grab = (from, to) => { const a = src.indexOf(from); const b = src.indexOf(to, a); if (a < 0 || b < 0) throw new Error(from); return src.slice(a, b); };
const proj = grab('    function packLiveProjectile(p)', '    function publishLiveBattleFrame');
const eff = grab('    // 소수 열다섯 자리', '    const LIVE_INIT_DROP');
const f = new Function(`const liveNum=v=>(typeof v==='number'&&isFinite(v)?v:0);
const liveR1=v=>Math.round(liveNum(v)*10)/10; const liveR2=v=>Math.round(liveNum(v)*100)/100;
const BATTLE_PROJECTILE_SPEED=1; const isLiveUnitRef=v=>Boolean(v&&typeof v==='object'&&typeof v.id==='string'&&v.statuses&&typeof v.hp==='number');
${proj}
${eff}
return { packLiveProjectile, roundLiveNum, packLiveEffect, liveNum };`)();
// 받는 쪽 (index.html의 applyLiveFrameState와 같은 해석)
const cleanUserText = (v, n = 40) => String(v === undefined || v === null ? '' : v).replace(/[<>"'`]/g, '').trim().slice(0, n);
const recv = (q, lead = 0) => ({
  x: f.liveNum(q[0]) + f.liveNum(q[6]) * lead, y: f.liveNum(q[1]) + f.liveNum(q[7]) * lead, angle: f.liveNum(q[2]),
  projType: cleanUserText(q[3], 30), color: cleanUserText(q[4], 30) || undefined, radius: f.liveNum(q[5]) || undefined,
  vx: f.liveNum(q[6]), vy: f.liveNum(q[7]), spr: cleanUserText(q[8], 30) || undefined
});
let n = 0; const t = (m, fn) => { fn(); n++; console.log('ok', m); };
const old = p => { // 압축 전 모양
  const liveNum = v => (typeof v === 'number' && isFinite(v) ? v : 0), r1 = v => Math.round(liveNum(v) * 10) / 10, r2 = v => Math.round(liveNum(v) * 100) / 100;
  return [r1(p.x), r1(p.y), r2(p.angle), String(p.projType || ''), String(p.color || ''), liveNum(p.radius), r2(p.vx), r2(p.vy), String(p.spr || '')];
};
const sample = { x: 1565.83, y: 1044.31, angle: -3.2312, projType: 'magic_orb', isDirectional: true, speed: 1, radius: 0 };

t('투사체: 자리 정수·속도 한 자리·빈 그림 칸 생략', () => {
  const q = f.packLiveProjectile({ ...sample, isDirectional: true, speed: 7.25 });
  assert.strictEqual(q.length, 8); assert.ok(Number.isInteger(q[0]) && Number.isInteger(q[1]));
  assert.strictEqual(q[3], 'magic_orb');
});
t('투사체: 그림 이름이 있으면 9칸', () => {
  const q = f.packLiveProjectile({ ...sample, spr: 'teleport' });
  assert.strictEqual(q.length, 9); assert.strictEqual(q[8], 'teleport');
});
t('받는 쪽이 같은 값으로 읽음 (오차 1px 안)', () => {
  const p = { ...sample, speed: 7.25, angle: 0.66 };
  const a = recv(f.packLiveProjectile(p), 6);
  const vx = Math.cos(p.angle) * 7.25, vy = Math.sin(p.angle) * 7.25;
  assert.ok(Math.abs(a.x - (p.x + vx * 6)) < 1.5 && Math.abs(a.y - (p.y + vy * 6)) < 1.5, JSON.stringify(a));
  assert.strictEqual(a.projType, 'magic_orb'); assert.strictEqual(a.spr, undefined); assert.strictEqual(a.color, undefined);
});
t('투사체 크기가 줄어듦', () => {
  const p = { ...sample, speed: 7.25, angle: 0.66 };
  const before = JSON.stringify(old({ ...p, vx: Math.cos(p.angle) * 7.25, vy: Math.sin(p.angle) * 7.25 })).length;
  const after = JSON.stringify(f.packLiveProjectile(p)).length;
  assert.ok(after <= before - 8, `${before} -> ${after}`); console.log('   projectile', before, '->', after);
});
t('이펙트 반올림: 정수·문자열은 그대로, 긴 소수만 줄임', () => {
  assert.strictEqual(f.roundLiveNum(1880.94608679776), 1880.9);
  assert.strictEqual(f.roundLiveNum(1.0574712643678161), 1.06);
  assert.strictEqual(f.roundLiveNum(32), 32);
  assert.strictEqual(f.roundLiveNum('aoe_ring'), 'aoe_ring');
  assert.strictEqual(f.roundLiveNum(-3.141592653589), -3.14);
  assert.deepStrictEqual(f.roundLiveNum({ a: [1.234567, 12.3456], b: { c: 100.55555 } }), { a: [1.23, 12.3], b: { c: 100.6 } });
});
t('이펙트: 시전자 참조는 id로, 값만 반올림', () => {
  const unit = { id: 'u1', statuses: {}, hp: 5 };
  const out = f.packLiveEffect({ type: 'aoe_ring', x: 100.123456, y: 50.9876, r: 262.9068276024797, life: 40, owner: unit });
  assert.deepStrictEqual(out, { type: 'aoe_ring', x: 100.1, y: 51, r: 262.9, life: 40, oid: 'u1' });
});
console.log('all', n);

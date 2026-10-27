const fs=require('fs');
const src=fs.readFileSync((process.argv[2]||'../index.html'),'utf8');
const a=src.indexOf('const ROOM_CLAIM_KEYS'); const b=src.indexOf('// 방 통째로 덮어쓰지 않고');
const code=src.slice(a,b);
const f=new Function(code+';return {mergeRoomState,mergeRoomPlayers};')();
const assert=require('assert');
const clone=o=>JSON.parse(JSON.stringify(o));
let n=0; const t=(name,fn)=>{fn();n++;console.log('ok',name);};
// pvp 1v1: two guests race for guestId
const base={roomId:'r',hostId:'h',guestId:null,status:'waiting'};
const A=clone(base);A.guestId='A';A.guestName='A';
const B=clone(base);B.guestId='B';B.guestName='B';
const afterA=f.mergeRoomState(base,A,clone(base));
assert.equal(afterA.guestId,'A');
t('first guest claims',()=>{});
t('second guest rejected',()=>assert.equal(f.mergeRoomState(base,B,afterA),undefined));
// same guest idempotent
t('same guest again ok',()=>assert.equal(f.mergeRoomState(base,A,afterA).guestId,'A'));
// spectator add does not clobber guest ready
const cur1=clone(afterA);cur1.guestReady=true;
const spBase=clone(afterA);const spMine=clone(afterA);spMine.spectators={s1:{id:'s1'}};
t('spectator keeps guestReady',()=>{const o=f.mergeRoomState(spBase,spMine,cur1);assert.equal(o.guestReady,true);assert.ok(o.spectators.s1);});
// ready toggle doesn't remove spectator added concurrently
const curSp=clone(afterA);curSp.spectators={s1:{id:'s1'}};
const rb=clone(afterA);const rm=clone(afterA);rm.guestReady=true;
t('ready keeps spectator',()=>{const o=f.mergeRoomState(rb,rm,curSp);assert.equal(o.guestReady,true);assert.ok(o.spectators.s1);});
// gone clear by me only
const gb={...clone(afterA),gone:{A:123,h:456}};const gm=clone(gb);delete gm.gone.A;
t('gone clear per-id',()=>{const o=f.mergeRoomState(gb,gm,clone(gb));assert.deepEqual(o.gone,{h:456});});
// room removed on server -> abort
t('room gone abort',()=>assert.equal(f.mergeRoomState(base,A,null),undefined));
// minigame players race
const mb={roomId:'m',maxPlayers:2,players:[{id:'h',isHost:true,ready:true}],status:'waiting'};
const mA=clone(mb);mA.players.push({id:'A',ready:false});
const mC=clone(mb);mC.players.push({id:'C',ready:false});
const curA=f.mergeRoomState(mb,mA,clone(mb));
t('mg first joins',()=>assert.equal(curA.players.length,2));
t('mg full -> reject',()=>assert.equal(f.mergeRoomState(mb,mC,curA),undefined));
const mb3={...mb,maxPlayers:4};const m3A=clone(mb3);m3A.players.push({id:'A',ready:false});const m3C=clone(mb3);m3C.players.push({id:'C',ready:false});
const c3=f.mergeRoomState(mb3,m3A,clone(mb3));
t('mg both fit',()=>{const o=f.mergeRoomState(mb3,m3C,c3);assert.deepEqual(o.players.map(p=>p.id),['h','A','C']);});
// A toggles ready while C joined
const m3R=clone(mb3);m3R.players.push({id:'A',ready:false});
const baseWithA=clone(c3);const mineReady=clone(c3);mineReady.players.find(p=>p.id==='A').ready=true;
const curWithC=f.mergeRoomState(mb3,m3C,c3);
t('mg ready keeps C',()=>{const o=f.mergeRoomState(baseWithA,mineReady,curWithC);assert.deepEqual(o.players.map(p=>p.id),['h','A','C']);assert.equal(o.players[1].ready,true);});
// A leaves while C joins
const leave=clone(c3);leave.players=leave.players.filter(p=>p.id!=='A');
t('mg leave keeps C',()=>{const o=f.mergeRoomState(c3,leave,curWithC);assert.deepEqual(o.players.map(p=>p.id),['h','C']);});
// raid slots: guest vs guest2
const rbase={hostId:'h',guestId:null,guest2Id:null};
const r1=clone(rbase);r1.guestId='A';const r2=clone(rbase);r2.guestId='B';
const rc=f.mergeRoomState(rbase,r1,clone(rbase));
t('raid conflict',()=>assert.equal(f.mergeRoomState(rbase,r2,rc),undefined));
console.log('all',n);

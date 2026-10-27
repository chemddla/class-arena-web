const fs=require('fs');const assert=require('assert');
const src=fs.readFileSync((process.argv[2]||'../index.html'),'utf8');
const grab=(from,to)=>{const a=src.indexOf(from);const b=src.indexOf(to,a);if(a<0||b<0)throw new Error(from);return src.slice(a,b);};
const accept=grab('    function liveAcceptPayload(val)','    function stopLiveBattleNet');
const reset=grab('    function resetLiveFrameBuffer()','    function applyLiveFrame(val)');
const mk=new Function(`const liveNum=v=>(typeof v==='number'&&isFinite(v)?v:0);
const liveNet={bid:1000,ep:0,minAt:997,frameBuf:[1],curFrame:{at:5},lastFrameAt:0};
${reset}
${accept}
return {liveNet,liveAcceptPayload,resetLiveFrameBuffer};`);
const {liveNet,liveAcceptPayload}=mk();
let n=0;const t=(m,f)=>{f();n++;console.log('ok',m);};
t('same battle frame ok',()=>assert.ok(liveAcceptPayload({b:1000,ep:0,at:2000})));
t('old battle frame rejected',()=>assert.ok(!liveAcceptPayload({b:900,ep:0,at:99999})));
// new host clock far behind (at=10): previously rejected by minAt / curFrame.at
t('new host ep1 with slow clock adopted',()=>{assert.ok(liveAcceptPayload({b:1000,ep:1,at:10}));assert.equal(liveNet.ep,1);assert.equal(liveNet.frameBuf.length,0);assert.equal(liveNet.curFrame,null);assert.equal(liveNet.minAt,0);});
t('old host ep0 now stale',()=>assert.ok(!liveAcceptPayload({b:1000,ep:0,at:99999})));
t('legacy tower payload uses minAt',()=>{liveNet.minAt=500;assert.ok(!liveAcceptPayload({at:100}));assert.ok(liveAcceptPayload({at:600}));});
console.log('all',n);

// 가구 그림에서 틀·다리 사이에 갇혀 남은 흰 배경(닫힌 흰 덩어리)을 투명하게 지움.
//   node tools/furniture-bg-fix.cjs [최소픽셀=100] [dry]   (KEEP: 악보처럼 진짜 흰 부분은 덩어리 왼쪽 위 좌표로 제외)
const s=require('sharp'),fs=require('fs');
const MIN=Number(process.argv[2]||100), DRY=process.argv[3]==='dry';
const KEEP={ 'grand_piano.webp':[[87,104],[108,116]], 'easel_workbench_b.webp':[[109,47]], 'fireplace_console_b.webp':[[47,58]] }; // 악보처럼 진짜 흰 부분 (덩어리 왼쪽 위 좌표)
(async()=>{
for(const f of fs.readdirSync('assets/furniture').filter(f=>f.endsWith('.webp'))){
 const {data,info}=await s(fs.readFileSync('assets/furniture/'+f)).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const W=info.width,H=info.height; const seen=new Uint8Array(W*H); const kill=new Uint8Array(W*H); const log=[];
 const lum=i=>{const o=i*4;return [Math.min(data[o],data[o+1],data[o+2]),Math.max(data[o],data[o+1],data[o+2])-Math.min(data[o],data[o+1],data[o+2])];};
 const isW=i=>{if(!data[i*4+3])return false;const [m,sp]=lum(i);return m>=244&&sp<=8;};
 for(let st0=0;st0<W*H;st0++){ if(seen[st0]||!isW(st0))continue; const st=[st0],mem=[]; let x0=W,y0=H;
  while(st.length){const i=st.pop(); if(seen[i]||!isW(i))continue; seen[i]=1;mem.push(i);const x=i%W,y=(i/W)|0; x0=Math.min(x0,x);y0=Math.min(y0,y); if(x>0)st.push(i-1); if(x<W-1)st.push(i+1); if(y>0)st.push(i-W); if(y<H-1)st.push(i+W);}
  if(mem.length<MIN)continue; if((KEEP[f]||[]).some(([kx,ky])=>kx===x0&&ky===y0)){log.push('keep '+mem.length+'@'+x0+','+y0);continue;}
  mem.forEach(i=>kill[i]=1); log.push(mem.length+'@'+x0+','+y0);}
 if(!log.length)continue;
 // 지운 영역에 붙은 연한 흰 테두리도 같이 (밝기 228 이상·채도 낮음), 번질 때까지
 let grown=0,ch=true; while(ch){ch=false; for(let i=0;i<W*H;i++){ if(kill[i]||!data[i*4+3])continue; const x=i%W,y=(i/W)|0; const nb=[x>0&&kill[i-1],x<W-1&&kill[i+1],y>0&&kill[i-W],y<H-1&&kill[i+W]]; if(!nb.some(Boolean))continue; const [m,sp]=lum(i); if(m>=228&&sp<=12){kill[i]=1;grown++;ch=true;} } }
 console.log(f.padEnd(28), log.join(' | '), '+fringe', grown, DRY?'(dry)':'');
 if(DRY)continue;
 for(let i=0;i<W*H;i++) if(kill[i]){data[i*4]=0;data[i*4+1]=0;data[i*4+2]=0;data[i*4+3]=0;}
 await s(data,{raw:{width:W,height:H,channels:4}}).webp({lossless:true}).toBuffer().then(b=>fs.writeFileSync('assets/furniture/'+f,b));
}})();

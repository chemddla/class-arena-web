/* 우리 반 마을 (3D) 본체. three.js r128 + assets/village-pets.js가 먼저 있어야 함.
 * 쓰는 법: const api = Village.start(담을 요소, host) → api.pause() / api.resume() / api.dispose()
 * host(실제 마을): { db(Firebase DB, 없으면 혼자 보기), code(학급 코드), me: { id, name, pet(펫 종류|null) },
 *                    students: [{ id, name }](집 주인 순서), nameOf(id), visitHome(id) }
 * host를 안 주면 시험판(흉내 친구·펫 고르기·시간 버튼)으로 돎 — preview/village-test.html
 * 집·나무 위치는 정해진 난수(seed)로 만들어 모든 기기에서 같음.
 */
(function () {
  const CSS = `
  .vlg { position: relative; overflow: hidden; background: #a8dcf7; font-family: 'Pretendard', 'Malgun Gothic', system-ui, sans-serif; color: #2f4a35; user-select: none; -webkit-user-select: none; }
  .vlg.vlg-full { position: fixed !important; inset: 0; z-index: 9990; height: auto !important; border-radius: 0 !important; }
  .vlg * { box-sizing: border-box; }
  .vlg canvas.vlg-gl { position: absolute; inset: 0; width: 100%; height: 100%; display: block; touch-action: none; }
  .vlg .vlg-labels { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
  .vlg .tag { position: absolute; left: 0; top: 0; padding: 2px 9px; border-radius: 999px; background: rgba(255, 255, 255, .88); border: 2px solid #b7d6b0; font-size: 12px; font-weight: 800; white-space: nowrap; will-change: transform; color: #2f4a35; }
  .vlg .tag.me { background: #3f9a5a; border-color: #2f7a45; color: #fff; }
  .vlg .tag.say { background: #fff; border-color: #f0b84a; color: #5a4320; font-size: 13px; padding: 4px 11px; border-radius: 14px; }
  .vlg .vlg-prompt { position: absolute; left: 0; top: 0; padding: 4px 11px; border-radius: 12px; background: #fff8d8; border: 2px solid #f0c24a; font-size: 13px; font-weight: 800; color: #5a4320; white-space: nowrap; display: none; }
  .vlg .vlg-prompt kbd { font: inherit; background: #f0c24a; color: #fff; border-radius: 6px; padding: 0 6px; margin-right: 5px; }
  .vlg .pop { position: absolute; left: 0; top: 0; font-size: 18px; font-weight: 900; color: #e8483f; text-shadow: 0 2px 0 #fff, 0 -2px 0 #fff, 2px 0 0 #fff, -2px 0 0 #fff; animation: vlgPop 1s ease-out forwards; white-space: nowrap; }
  @keyframes vlgPop { from { opacity: 1; margin-top: 0; } to { opacity: 0; margin-top: -56px; } }
  .vlg .vlg-hud { position: absolute; left: 10px; top: 10px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; max-width: calc(100% - 20px); }
  .vlg .pill, .vlg select, .vlg button { font: inherit; font-size: 13px; font-weight: 800; padding: 6px 12px; border-radius: 999px; border: 2px solid #b7d6b0; background: rgba(255, 255, 255, .92); color: #2f4a35; line-height: 1.2; }
  .vlg button { cursor: pointer; }
  .vlg .vlg-viewbtn { background: #fff8d8; border-color: #f0c24a; color: #5a4320; }
  .vlg .vlg-acts { position: absolute; right: 12px; bottom: 14px; display: flex; gap: 8px; }
  .vlg .vlg-acts button { font-size: 15px; padding: 12px 16px; }
  .vlg .vlg-hint { position: absolute; left: 12px; bottom: 14px; font-size: 12px; font-weight: 700; background: rgba(255, 255, 255, .8); padding: 6px 10px; border-radius: 10px; max-width: 55%; }
  .vlg .vlg-mapbox { position: absolute; right: 12px; bottom: 74px; }
  .vlg .vlg-map { display: block; width: 240px; height: 221px; border-radius: 14px; border: 3px solid #fff; box-shadow: 0 2px 8px rgba(0, 0, 0, .18); background: #8fd07a; pointer-events: none; }
  .vlg .vlg-mapbox button { position: absolute; top: 7px; right: 7px; font-size: 12px; padding: 3px 9px; }
  .vlg .vlg-mapbox.off .vlg-map { display: none; }
  .vlg .vlg-mapbox.off button { position: static; font-size: 13px; padding: 6px 12px; }
  @media (max-width: 640px) { .vlg .vlg-hint { display: none; } .vlg .vlg-map { width: 160px; height: 147px; } }`;
  const HTML = `
  <canvas class="vlg-gl" data-v="gl"></canvas>
  <div class="vlg-labels" data-v="labels"><div class="vlg-prompt" data-v="prompt"></div></div>
  <div class="vlg-hud">
    <span class="pill">🏡 우리 반 마을 <span data-v="count"></span></span>
    <button data-v="viewBtn" class="vlg-viewbtn" style="display:none">🎥 원래 시점 (R)</button>
    <select data-v="petSel" data-demo aria-label="내 펫"></select>
    <span class="pill" data-demo>🍎 열매 <b data-v="fruitN">0</b></span>
    <button data-v="curveBtn" data-demo>둥근 땅: 켬</button>
    <button data-v="shadowBtn">그림자: 켬</button>
    <button data-v="timeBtn" data-demo>시간: 낮</button>
    <button data-v="outlineBtn">테두리: 켬</button>
    <button data-v="soundBtn">소리: 끔</button>
    <button data-v="fullBtn">⛶ 크게</button>
    <span class="pill"><b data-v="fpsN">–</b> fps · <span data-v="qN">화질 높음</span></span>
  </div>
  <div class="vlg-hint">이동: WASD·방향키 또는 땅 누르기 · 시점: 화면 끌기 · 원래 시점: R · 달리기: Shift · 인사: Space · 하기: E · 감정: 1·2 · 확대: 마우스 휠</div>
  <div class="vlg-mapbox" data-v="mapBox"><canvas class="vlg-map" data-v="map"></canvas><button data-v="mapBtn">▾ 내리기</button></div>
  <div class="vlg-acts"><button data-v="joyBtn" title="기쁨 (1)">😄</button><button data-v="heartBtn" title="하트 (2)">❤️</button><button data-v="waveBtn">👋 인사</button><button data-v="shakeBtn">🌳 흔들기</button></div>`;

  function start(root, host) {
  host = host || null; const demo = !host;
  if (!document.getElementById('vlgStyle')) { const st = document.createElement('style'); st.id = 'vlgStyle'; st.textContent = CSS; document.head.appendChild(st); }
  root.classList.add('vlg'); root.innerHTML = HTML;
  const $ = id => root.querySelector('[data-v="' + id + '"]');
  let running = true, autoPaused = false;
  // ── 기본 장면
  const canvas = $('gl');
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  const HORIZON = 0xb4e2fa;
  scene.fog = new THREE.Fog(HORIZON, 30, 64);
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 140);
  const hemi = new THREE.HemisphereLight(0xfffaf0, 0xc4e2a0, 0.63); scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xfff0d0, 0.47); scene.add(sun); scene.add(sun.target);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0006; sun.shadow.normalBias = 0.04;
  Object.assign(sun.shadow.camera, { left: -17, right: 17, top: 17, bottom: -17, near: 1, far: 60 }); sun.shadow.camera.updateProjectionMatrix();

  // 그림으로 쓰는 무늬 (파일 없이 그 자리에서 그림)
  function paint(size, fn, repeat) {
    const c = document.createElement('canvas'); c.width = c.height = size; const g = c.getContext('2d');
    // 타일 가장자리에서 끊기지 않게, 걸치는 무늬는 반대쪽에도 한 번 더 그림
    const tile = draw => { for (let ox = -1; ox <= 1; ox++) for (let oy = -1; oy <= 1; oy++) { g.save(); g.translate(ox * size, oy * size); draw(); g.restore(); } };
    fn(g, size, tile);
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; if (repeat) t.repeat.set(repeat, repeat); t.anisotropy = renderer.capabilities.getMaxAnisotropy(); return t;
  }
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const pick = a => a[Math.floor(rnd() * a.length)];
  // 하늘: 위·가운데·지평선 세 색을 시간대에 따라 다시 칠함
  const skyC = document.createElement('canvas'); skyC.width = 4; skyC.height = 256; const skyG = skyC.getContext('2d');
  const skyTex = new THREE.CanvasTexture(skyC); scene.background = skyTex;
  function paintSky(top, mid, bot) { const gr = skyG.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, top.getStyle()); gr.addColorStop(0.35, mid.getStyle()); gr.addColorStop(1, bot.getStyle()); skyG.fillStyle = gr; skyG.fillRect(0, 0, 4, 256); skyTex.needsUpdate = true; }
  // 시간대: 빛·하늘·안개 색, unlit = 빛을 안 받는 것(물·꽃잎·구름)에 곱하는 색, night = 밤 정도(불빛·별·반딧불)
  const C = h => new THREE.Color(h);
  const TIMES = {
    day:    { label: '낮',   hemiSky: C(0xfffaf0), hemiGround: C(0xc4e2a0), hemiI: 0.63, sunC: C(0xfff0d0), sunI: 0.47, sunPos: new THREE.Vector3(8, 15, 4),   sky: [C(0x3fa4ee), C(0x7cc8f6), C(0xb4e2fa)], fog: C(0xb4e2fa), unlit: C(0xffffff), night: 0 },
    sunset: { label: '노을', hemiSky: C(0xffd2b0), hemiGround: C(0xd8b48a), hemiI: 0.56, sunC: C(0xff9450), sunI: 0.5,  sunPos: new THREE.Vector3(15, 7, 3),   sky: [C(0x5a6fc8), C(0xf59a7a), C(0xffd6a0)], fog: C(0xffd0a8), unlit: C(0xffd6bc), night: 0.3 },
    night:  { label: '밤',   hemiSky: C(0x8ea4ea), hemiGround: C(0x48608c), hemiI: 0.56, sunC: C(0xa4baff), sunI: 0.24,  sunPos: new THREE.Vector3(-6, 15, 5),  sky: [C(0x0c1340), C(0x1e2e6c), C(0x384c8c)], fog: C(0x2e4076), unlit: C(0x6076b4), night: 1 },
  };
  const env = { key: 'day', unlit: C(0xffffff), sky: [C(0x3fa4ee), C(0x7cc8f6), C(0xb4e2fa)], sunPos: new THREE.Vector3(8, 15, 4), night: 0 };
  const unlitMats = []; // 빛을 안 받는 재질과 원래 색
  // 잔디: 밝고 어두운 세모 무늬
  const grassTex = paint(512, (g, s, tile) => {
    g.fillStyle = '#74cf52'; g.fillRect(0, 0, s, s);
    for (let i = 0; i < 920; i++) {
      const x = rnd() * s, y = rnd() * s, r = 5 + rnd() * 6, a = rnd() * 6.28, col = rnd() < 0.55 ? 'rgba(74,170,62,.4)' : 'rgba(168,232,110,.42)';
      tile(() => { g.fillStyle = col; g.beginPath(); for (let k = 0; k < 3; k++) g.lineTo(x + Math.cos(a + k * 2.094) * r, y + Math.sin(a + k * 2.094) * r); g.fill(); });
    }
  }, 42);
  // 벚꽃 뭉치: 다섯 장 꽃이 빽빽이 겹친 무늬
  const blossomTex = paint(256, (g, s, tile) => {
    g.fillStyle = '#f7b9c9'; g.fillRect(0, 0, s, s);
    for (let i = 0; i < 150; i++) {
      const x = rnd() * s, y = rnd() * s, r = 9 + rnd() * 7, a0 = rnd() * 6.28, light = rnd() < 0.5 ? '#fff1f5' : '#ffdbe5';
      tile(() => {
        g.fillStyle = light;
        for (let k = 0; k < 5; k++) { const a = a0 + k * 1.2566; g.beginPath(); g.ellipse(x + Math.cos(a) * r * 0.55, y + Math.sin(a) * r * 0.55, r * 0.52, r * 0.36, a, 0, 6.29); g.fill(); }
        g.fillStyle = '#f48fb0'; g.beginPath(); g.arc(x, y, r * 0.2, 0, 6.29); g.fill();
      });
    }
  }, 0);
  blossomTex.repeat.set(3, 2);
  // 잎 뭉치: 밝고 어두운 잎이 겹친 무늬
  const leafTex = paint(256, (g, s, tile) => {
    g.fillStyle = '#46ad54'; g.fillRect(0, 0, s, s);
    for (let i = 0; i < 190; i++) {
      const x = rnd() * s, y = rnd() * s, r = 10 + rnd() * 8, a = rnd() * 6.28, c = pick(['#5cc466', '#6fd272', '#52b95e', '#3c9e4b']);
      tile(() => { g.fillStyle = c; g.beginPath(); g.ellipse(x, y, r, r * 0.5, a, 0, 6.29); g.fill(); });
    }
  }, 0);
  leafTex.repeat.set(3, 2);
  // 길: 모래에 작은 자갈 점
  const sandTex = paint(128, (g, s, tile) => {
    g.fillStyle = '#f3e3b4'; g.fillRect(0, 0, s, s);
    for (let i = 0; i < 70; i++) { const x = rnd() * s, y = rnd() * s, r = 2 + rnd() * 4, c = rnd() < 0.5 ? 'rgba(255,250,225,.5)' : 'rgba(226,206,160,.32)'; tile(() => { g.fillStyle = c; g.beginPath(); g.ellipse(x, y, r, r * 0.7, 0, 0, 6.29); g.fill(); }); }
  }, 0);
  // 지붕: 비늘처럼 겹친 기와 (색은 집마다 따로 입힘)
  const roofTex = paint(128, (g, s) => {
    g.fillStyle = '#ffffff'; g.fillRect(0, 0, s, s);
    for (let row = 0; row < 5; row++) for (let i = -1; i < 5; i++) {
      const x = i * 32 + (row % 2 ? 16 : 0), y = row * 32 - 32;
      const gr = g.createLinearGradient(0, y, 0, y + 34); gr.addColorStop(0, 'rgba(0,0,0,.02)'); gr.addColorStop(1, 'rgba(0,0,0,.2)');
      g.fillStyle = gr; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 32, y); g.lineTo(x + 32, y + 18); g.arc(x + 16, y + 18, 16, 0, Math.PI); g.closePath(); g.fill();
      g.strokeStyle = 'rgba(0,0,0,.22)'; g.lineWidth = 2; g.beginPath(); g.arc(x + 16, y + 18, 16, 0, Math.PI); g.stroke();
    }
  }, 0);
  roofTex.repeat.set(8, 3);
  // 벽: 가로 널빤지 줄
  const wallTex = paint(64, (g, s) => { g.fillStyle = '#ffffff'; g.fillRect(0, 0, s, s); g.fillStyle = 'rgba(120,90,60,.16)'; g.fillRect(0, 0, s, 3); g.fillStyle = 'rgba(255,255,255,.5)'; g.fillRect(0, 3, s, 2); }, 0);
  wallTex.repeat.set(1, 6);
  // 나무껍질: 세로 결
  const barkTex = paint(64, (g, s, tile) => {
    g.fillStyle = '#ffffff'; g.fillRect(0, 0, s, s);
    for (let i = 0; i < 26; i++) { const x = rnd() * s, y = rnd() * s, l = 10 + rnd() * 30, c = rnd() < 0.6 ? 'rgba(70,40,20,.2)' : 'rgba(255,240,220,.3)'; tile(() => { g.fillStyle = c; g.fillRect(x, y, 2 + rnd() * 2, l); }); }
  }, 0);
  barkTex.repeat.set(3, 1);
  // 둥근 번짐 (바닥 음영·불빛 번짐에 씀): 가운데가 진하고 가장자리로 사라짐
  const softTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.45, 'rgba(255,255,255,.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
  // 물: 흐르는 물결 줄
  const waterTex = paint(128, (g, s, tile) => {
    { const gr = g.createLinearGradient(0, 0, 0, s); gr.addColorStop(0, '#8fdcf8'); gr.addColorStop(0.22, '#56bdee'); gr.addColorStop(0.5, '#3fa6e2'); gr.addColorStop(0.78, '#56bdee'); gr.addColorStop(1, '#8fdcf8'); g.fillStyle = gr; g.fillRect(0, 0, s, s); } g.lineCap = 'round';
    for (let i = 0; i < 16; i++) { const x = rnd() * s, y = rnd() * s, l = 14 + rnd() * 26, c = rnd() < 0.6 ? 'rgba(200,240,255,.75)' : 'rgba(60,160,225,.6)', w = 2 + rnd() * 2; tile(() => { g.strokeStyle = c; g.lineWidth = w; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + l / 2, y - 4, x + l, y); g.stroke(); }); }
  }, 0);

  // ── 둥글게 말리는 땅: 내 캐릭터에서 보는 방향 앞뒤로 멀어질수록 아래로 내려감. 그림자는 휘기 전 위치로 계산되므로 그대로 맞음
  const curve = { uCurve: { value: 0.0075 }, uFocus: { value: new THREE.Vector2() }, uDir: { value: new THREE.Vector2(0, -1) }, uTime: { value: 0 } }; // uDir: 카메라가 보는 쪽(땅에 눕힌 방향)
  function bend(m, sway, outline) {
    m.onBeforeCompile = sh => {
      sh.uniforms.uCurve = curve.uCurve; sh.uniforms.uFocus = curve.uFocus; sh.uniforms.uDir = curve.uDir; sh.uniforms.uTime = curve.uTime;
      sh.vertexShader = (sway ? '#define SWAY ' + sway.toFixed(4) + '\n' : '') + (outline ? '#define OUTLINE ' + outline.toFixed(4) + '\n' : '') + 'uniform float uCurve;\nuniform vec2 uFocus;\nuniform vec2 uDir;\nuniform float uTime;\n' + sh.vertexShader.replace('#include <project_vertex>', `
        vec4 wpB = vec4( transformed, 1.0 );
        #ifdef USE_INSTANCING
          wpB = instanceMatrix * wpB;
        #endif
        wpB = modelMatrix * wpB;
        #ifdef OUTLINE
          #ifdef USE_INSTANCING
            wpB.xyz += normalize( mat3( modelMatrix ) * mat3( instanceMatrix ) * normal ) * OUTLINE;
          #else
            wpB.xyz += normalize( mat3( modelMatrix ) * normal ) * OUTLINE;
          #endif
        #endif
        #ifdef SWAY
          wpB.x += sin( uTime * 1.8 + wpB.x * 1.3 + wpB.z * 1.7 ) * SWAY * wpB.y;
          wpB.z += cos( uTime * 1.3 + wpB.x * 0.9 ) * SWAY * 0.5 * wpB.y;
        #endif
        float dzB = dot( wpB.xz - uFocus, uDir );
        wpB.y -= uCurve * dzB * dzB;
        vec4 mvPosition = viewMatrix * wpB;
        gl_Position = projectionMatrix * mvPosition;`);
    };
    m.customProgramCacheKey = () => 'bend' + (sway || 0) + '/' + (outline || 0); // 흔들림 값이 다르면 셰이더도 따로
    return m;
  }
  const grad = new THREE.DataTexture(new Uint8Array([150, 208, 255]), 3, 1, THREE.LuminanceFormat); grad.minFilter = grad.magFilter = THREE.NearestFilter; grad.needsUpdate = true;
  const softGrad = new THREE.DataTexture(new Uint8Array([188, 226, 246, 255]), 4, 1, THREE.LuminanceFormat); softGrad.minFilter = softGrad.magFilter = THREE.NearestFilter; softGrad.needsUpdate = true; // 나무 뭉치용: 단계가 더 잘고 부드러움
  const toonMat = (o, sway) => bend(new THREE.MeshToonMaterial(Object.assign({ gradientMap: grad }, o)), sway);
  const M = VillagePets.toon(THREE, bend); // 색 → 툰 재질(둥근 땅 적용)
  // 빛을 안 받는 재질. glow: true면 스스로 빛나는 것(창문·등불)이라 시간대 색을 곱하지 않음
  const flat = (c, o) => { o = Object.assign({}, o); const glow = o.glow; delete o.glow; const m = bend(new THREE.MeshBasicMaterial(Object.assign({ color: c }, o))); if (!glow) unlitMats.push({ m, base: new THREE.Color(c) }); return m; };
  const winMat = flat(0xfff0b8, { glow: true }), DAY_WIN = C(0xfff0b8), NIGHT_WIN = C(0xffd24a);
  const mesh = (g, c) => new THREE.Mesh(g, typeof c === 'string' ? M(c) : c);
  const at = (o, x, y, z) => { o.position.set(x, y, z); return o; };
  const noShadow = o => { o.userData.noShadow = true; return o; };
  const floor = o => { o.userData.floor = true; return o; };

  // ── 땅·길·강
  const ground = floor(mesh(new THREE.PlaneGeometry(150, 150, 150, 150), toonMat({ map: grassTex, vertexColors: true }))); ground.rotation.x = -Math.PI / 2; scene.add(ground);
  { const pos = ground.geometry.attributes.position, cols = new Float32Array(pos.count * 3); // 꼭짓점마다 밝기를 살짝 다르게
    for (let i = 0; i < pos.count; i++) { const x = pos.getX(i), z = -pos.getY(i), n = Math.sin(x * 0.21 + 1.3) * Math.sin(z * 0.17 + 0.5) + 0.5 * Math.sin(x * 0.53 + z * 0.41), c = 1 + n * 0.065; cols[i * 3] = c * 0.97; cols[i * 3 + 1] = c; cols[i * 3 + 2] = c * 0.93; }
    ground.geometry.setAttribute('color', new THREE.BufferAttribute(cols, 3)); }
  const STREETS = [0, 10, 20, 30, 40].map(z => ({ z, len: 66 })); // 동서로 난 골목 (집은 골목 북쪽에 마당을 두고 섬)
  const onPath = (x, z, m) => Math.abs(x) < m || STREETS.some(st => Math.abs(z - st.z) < m && Math.abs(x) < st.len / 2 + m);
  const strip = (x, z, w, d, c, y) => { const m = floor(mesh(new THREE.PlaneGeometry(w, d, Math.max(1, Math.round(w)), Math.max(1, Math.round(d))), c)); m.rotation.x = -Math.PI / 2; scene.add(at(m, x, y, z)); return m; };
  const sandMat = (rx, ry) => { const t = sandTex.clone(); t.needsUpdate = true; t.repeat.set(rx, ry); return toonMat({ map: t }); };
  strip(0, 11, 2.46, 62.26, '#d6bd7e', 0.022); STREETS.forEach((st, i) => strip(0, st.z, st.len + 0.26, 2.46, '#d6bd7e', 0.023 + i * 0.0005)); // 길 테두리
  strip(0, 11, 2.2, 62, sandMat(1, 28), 0.03); STREETS.forEach((st, i) => strip(0, st.z, st.len, 2.2, sandMat(Math.round(st.len / 2.2), 1), 0.031 + i * 0.0005));
  // 광장: 회색 돌을 엇갈려 깐 바닥, 가장자리와 분수 둘레에 짙은 돌 띠
  const stoneTex = paint(256, (g, s) => { g.fillStyle = '#9d9a94'; g.fillRect(0, 0, s, s); const n = 4, w = s / n;
    for (let row = 0; row < n; row++) for (let i = -1; i < n; i++) { const x = i * w + (row % 2 ? w / 2 : 0), y = row * w;
      g.fillStyle = pick(['#d6d3cd', '#cbc8c1', '#dedbd5', '#c4c1ba', '#d1cdc5']); g.fillRect(x + 3, y + 3, w - 6, w - 6);
      g.fillStyle = 'rgba(255,255,255,.18)'; g.fillRect(x + 3, y + 3, w - 6, 4); } }, 5);
  const disc = (r0, r1, c, y) => { const m = floor(mesh(new THREE.RingGeometry(r0, r1, 64, 5), c)); m.rotation.x = -Math.PI / 2; scene.add(at(m, 0, y, 0)); return m; };
  disc(0, 4.6, '#8f8b84', 0.038); const plaza = disc(0, 4.4, toonMat({ map: stoneTex }), 0.045);
  disc(3.05, 3.25, '#aaa69e', 0.05); disc(2.05, 2.3, '#8f8b84', 0.05);
  // ── 강: 동서로 구불구불 흐르는 넓은 강. riverZ(x) = 그 자리의 강 한가운데 z
  const RIVER = { w: 4.6, bridge: 1.4 };
  const riverZ = x => -8.6 + 0.9 * Math.sin(x * 0.11 + 0.4) + 0.4 * Math.sin(x * 0.27);
  const riverDist = (x, z) => Math.abs(z - riverZ(x)) - RIVER.w / 2; // 0보다 작으면 물속
  const ribbon = (off, w, mat, y, rows) => { // 강을 따라 휘는 띠 (둥근 땅에 맞게 잘게 나눔)
    const N = 300, R = rows || 4, pos = [], uv = [], idx = [];
    for (let i = 0; i <= N; i++) { const x = -75 + i * 0.5; for (let j = 0; j <= R; j++) { pos.push(x, y, riverZ(x) + off + (j / R - 0.5) * w); uv.push(i / N, j / R); } }
    for (let i = 0; i < N; i++) for (let j = 0; j < R; j++) { const a = i * (R + 1) + j, b = a + R + 1; idx.push(a, a + 1, b, a + 1, b + 1, b); }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); geo.setIndex(idx); geo.computeVertexNormals();
    const m = floor(new THREE.Mesh(geo, typeof mat === 'string' ? M(mat) : mat)); scene.add(m); return m; };
  ribbon(0, RIVER.w + 1.1, '#ead9a0', 0.035);
  waterTex.repeat.set(41, 1); ribbon(0, RIVER.w, flat(0xffffff, { map: waterTex }), 0.05);
  [-1, 1].forEach(s => { noShadow(ribbon(s * (RIVER.w / 2 - 0.07), 0.14, flat(0xe9f8ff), 0.055, 1)).userData.floor = false; }); // 물가 흰 띠
  // ── 다리: 돌 아치 다리. 난간 끝 기둥마다 등불, 옆면에 아치 무늬. 걸으면 아치를 따라 오르내림
  const BR = { z: riverZ(0), half: 1.45, L: RIVER.w + 2.4, peak: 0.62 };
  const deckY = lz => 0.12 + BR.peak * Math.sin(Math.PI * Math.min(1, Math.max(0, (lz + BR.L / 2) / BR.L))); // 다리 위 높이 (lz: 다리 가운데 기준)
  const groundY = (x, z) => Math.abs(x) < BR.half && Math.abs(z - BR.z) < BR.L / 2 ? deckY(z - BR.z) + 0.08 : 0;
  const bridge = new THREE.Group();
  { const n = 14, seg = BR.L / n, b = (w, h, d, c, x, y, z, rx) => { const m = at(mesh(new THREE.BoxGeometry(w, h, d), c), x, y, z); m.rotation.x = rx || 0; bridge.add(m); return m; };
    for (let i = 0; i < n; i++) { const lz = -BR.L / 2 + (i + 0.5) * seg, y = deckY(lz), sl = -Math.atan2(deckY(lz + 0.01) - deckY(lz - 0.01), 0.02);
      b(BR.half * 2, 0.16, seg + 0.03, i % 2 ? '#e9e3d6' : '#ddd6c6', 0, y, lz, sl);
      [-1, 1].forEach(sd => { b(0.22, 0.5, seg + 0.03, '#d9d2c4', sd * BR.half, y + 0.33, lz, sl); b(0.32, 0.08, seg + 0.05, '#f4efe5', sd * BR.half, y + 0.62, lz, sl); }); }
    [-1, 1].forEach(sd => [-1, 1].forEach(ez => { const z = ez * (BR.L / 2 - 0.15), y = deckY(z); // 끝 기둥과 등불
      b(0.46, 1.05, 0.46, '#d9d2c4', sd * BR.half, y + 0.5, z); b(0.56, 0.1, 0.56, '#f4efe5', sd * BR.half, y + 1.05, z);
      b(0.28, 0.36, 0.28, '#3a3a44', sd * BR.half, y + 1.3, z); bridge.add(at(noShadow(mesh(new THREE.BoxGeometry(0.2, 0.28, 0.29), winMat)), sd * BR.half, y + 1.3, z));
      const cap = at(mesh(new THREE.ConeGeometry(0.24, 0.22, 4), '#3a3a44'), sd * BR.half, y + 1.59, z); cap.rotation.y = Math.PI / 4; bridge.add(cap); }));
    [-1, 1].forEach(sd => { const arc = at(mesh(new THREE.RingGeometry(BR.L / 2 - 0.85, BR.L / 2 - 0.25, 32, 1, 0, Math.PI), '#cfc7b6'), sd * (BR.half + 0.02), 0, 0); arc.rotation.y = Math.PI / 2; arc.scale.y = 0.2; bridge.add(arc); });
  }
  scene.add(at(bridge, 0, 0, BR.z));

  // ── 부딪히는 것(원) 목록
  const solids = [];
  const solid = (x, z, r, h) => solids.push({ x, z, r, h: h || 0 }); // h: 건물 높이 — 카메라가 그 안으로 들어가지 않게 (작은 소품은 0)

  // ── 분수·게시판
  // 분수: 팔각 돌 연못 + 2단 물그릇, 그릇 가장자리로 흘러내리는 물, 연못에 번지는 물결, 둘레 꽃덤불
  const fountain = new THREE.Group(), ripples = [];
  { const STONE = '#e6e0d3', EDGE = '#f4efe5', f = (geo, c, y) => { const m = at(mesh(geo, c), 0, y, 0); fountain.add(m); return m; };
    const cyl = (a, b, h, n, open) => new THREE.CylinderGeometry(a, b, h, n || 32, 1, open);
    f(cyl(1.8, 1.92, 0.5, 8), STONE, 0.25); f(cyl(1.95, 1.95, 0.1, 8), EDGE, 0.55); f(cyl(1.94, 1.94, 0.1, 8), '#5b9bd5', 0.3); // 연못 벽, 테, 파란 타일 띠
    f(cyl(1.6, 1.6, 0.05, 40), flat(0x7fd0f0), 0.5).userData.noShadow = true;
    f(cyl(0.26, 0.34, 1.05, 16), STONE, 1.02); f(cyl(0.36, 0.36, 0.1, 16), EDGE, 0.6); f(cyl(0.3, 0.3, 0.08, 16), EDGE, 1.2);
    f(cyl(0.9, 0.38, 0.26, 32), STONE, 1.52); f(cyl(0.92, 0.92, 0.06, 32), EDGE, 1.66); f(cyl(0.8, 0.8, 0.04, 32), flat(0x8fdcf8), 1.65).userData.noShadow = true;
    f(cyl(0.13, 0.18, 0.55, 12), STONE, 1.95); f(cyl(0.46, 0.2, 0.16, 24), STONE, 2.28); f(cyl(0.48, 0.48, 0.05, 24), EDGE, 2.37); f(cyl(0.4, 0.4, 0.03, 24), flat(0x8fdcf8), 2.37).userData.noShadow = true;
    const veil = flat(0xd4f2ff, { transparent: true, opacity: 0.5, side: THREE.DoubleSide, depthWrite: false }); // 흘러내리는 물
    noShadow(f(cyl(0.9, 1.0, 1.12, 32, true), veil, 1.1)); noShadow(f(cyl(0.47, 0.52, 0.7, 24, true), veil, 2.02));
    for (let k = 0; k < 3; k++) { const m = new THREE.Mesh(new THREE.RingGeometry(0.22, 0.27, 32), flat(0xffffff, { transparent: true, opacity: 0, depthWrite: false })); m.rotation.x = -Math.PI / 2; noShadow(m); fountain.add(at(m, 0, 0.54, 0)); ripples.push(m); }
    for (let k = 0; k < 8; k++) { const a = (k + 0.5) / 8 * Math.PI * 2, x = Math.sin(a) * 2.15, z = Math.cos(a) * 2.15; // 꽃덤불
      f(new THREE.SphereGeometry(0.3, 12, 9), '#5cbd50', 0.2).position.set(x, 0.2, z);
      [[0, 0.42, 0], [0.14, 0.36, 0.1], [-0.12, 0.38, -0.08]].forEach((o, j) => f(new THREE.SphereGeometry(0.075, 8, 6), ['#ff7fa6', '#ffcf3a', '#fff6e8', '#b06fc8'][(k + j) % 4], 0).position.set(x + o[0], o[1], z + o[2])); }
  }
  const spout = at(noShadow(mesh(new THREE.SphereGeometry(0.16, 12, 10), flat(0xd4f2ff))), 0, 2.48, 0); fountain.add(spout);
  scene.add(fountain); solid(0, 0, 2.3);
  const board = new THREE.Group(); // 마을 게시판: 지붕 달린 나무 틀, 코르크판에 압정 꽂은 쪽지들, 이름판, 등불, 꽃 상자
  { const b = (w, h, d, c, x, y, z) => { const m = at(mesh(new THREE.BoxGeometry(w, h, d), c), x, y, z); board.add(m); return m; };
    const WOOD = '#7a4a2e', LIGHT = '#b9824e';
    [-1.1, 1.1].forEach(x => { b(0.4, 0.22, 0.4, '#c9c3b8', x, 0.11, 0); b(0.16, 2.5, 0.16, WOOD, x, 1.35, 0); });
    b(2.2, 1.35, 0.08, '#d9a86a', 0, 1.45, 0); // 코르크판
    [[2.4, 0.12, 0, 2.17], [2.4, 0.12, 0, 0.73], [0.12, 1.56, -1.14, 1.45], [0.12, 1.56, 1.14, 1.45]].forEach(f => b(f[0], f[1], 0.14, WOOD, f[2], f[3], 0.02)); // 틀
    const nc = document.createElement('canvas'); nc.width = 256; nc.height = 56; const ng = nc.getContext('2d');
    ng.fillStyle = '#fbf3e2'; ng.fillRect(0, 0, 256, 56); ng.fillStyle = '#5a3520'; ng.font = "800 30px 'Malgun Gothic', sans-serif"; ng.textAlign = 'center'; ng.textBaseline = 'middle'; ng.fillText('📌 마을 게시판', 128, 30);
    b(1.5, 0.36, 0.08, WOOD, 0, 2.5, 0.02); board.add(at(noShadow(mesh(new THREE.PlaneGeometry(1.38, 0.28), flat(0xffffff, { map: new THREE.CanvasTexture(nc) }))), 0, 2.5, 0.07));
    [['#fff7d6', -0.62, 1.68, 0.08, 0.5, 0.56], ['#ffd6de', 0.05, 1.55, -0.06, 0.56, 0.48], ['#d6f0ff', 0.68, 1.72, 0.1, 0.48, 0.5], ['#e2f5d6', -0.35, 1.07, -0.05, 0.62, 0.36], ['#fff1c9', 0.55, 1.08, 0.07, 0.5, 0.38]].forEach(([c, x, y, rz, w, h], i) => {
      b(w, h, 0.02, c, x, y, 0.06).rotation.z = rz;
      for (let k = 0; k < 3; k++) b(w * (0.7 - k * 0.15), 0.03, 0.01, '#c7b7a0', x - w * 0.06 * k, y + h * 0.18 - k * 0.11, 0.075).rotation.z = rz; // 글씨 줄
      board.add(at(mesh(new THREE.SphereGeometry(0.045, 8, 6), ['#e0685a', '#5b8fd8', '#f2c53a', '#4fae6a', '#b06fc8'][i]), x - Math.sin(rz) * h * 0.42, y + h * 0.42, 0.1)); });
    [-1, 1].forEach(sd => { const rf = b(1.45, 0.08, 0.95, '#c2573f', sd * 0.62, 3.0, 0.02); rf.rotation.z = -sd * 0.42; }); // 박공지붕
    b(0.12, 0.12, 1, '#8a3f2e', 0, 3.26, 0.02);
    b(0.05, 0.3, 0.05, '#3a3a44', 1.42, 2.15, 0.12); b(0.22, 0.04, 0.05, '#3a3a44', 1.33, 2.3, 0.12); // 옆에 매단 등불
    b(0.2, 0.26, 0.2, '#3a3a44', 1.42, 1.88, 0.12); board.add(at(noShadow(mesh(new THREE.BoxGeometry(0.14, 0.18, 0.21), winMat)), 1.42, 1.88, 0.12));
    b(2.3, 0.3, 0.38, LIGHT, 0, 0.36, 0.3); for (let k = 0; k < 8; k++) board.add(at(mesh(new THREE.SphereGeometry(0.11, 8, 6), ['#ff7fa6', '#ffcf3a', '#fff6e8', '#ff8a3a'][k % 4]), -0.95 + k * 0.27, 0.58, 0.3)); // 꽃 상자
  }
  scene.add(at(board, 3.1, 0, -3.1)); board.rotation.y = -0.5; solid(3.1, -3.1, 1);

  // ── 집
  // 집터 32곳: 광장에서 가까운 순서. 학생 명단 순서대로 한 채씩 (남는 집은 빈 집). 집 앞(남쪽)에 울타리 마당, 그 앞이 골목
  const ROOFS = ['#e0685a', '#5b8fd8', '#e8a13a', '#4fae6a', '#b06fc8', '#3fb0a8', '#e07a9a', '#7a8fd8', '#9a6a4a', '#8fbf4a', '#f2c53a', '#6a7fa8'];
  const WALLS = ['#fff1dc', '#f4f0ff', '#fff6cf', '#eaf7e4', '#ffe9ee', '#e8f4ff', '#fde8d6', '#f1f1e6'];
  const HOUSES = [], lot = (x, z) => HOUSES.push([x, z]);
  [5, 15, 25, 35].forEach(z => [6.5, 13.5, 20.5, 27.5].forEach(x => { lot(-x, z); lot(x, z); })); // 골목(z+5)에서 마당만큼 물러남
  { // 벽·지붕 색과 지붕 모양을 섞음: 정해진 난수로 고르되 옆집·앞뒷집과는 겹치지 않게 (모든 기기에서 같음)
    let sd = 11; const rc = n => Math.floor((sd = (sd * 16807) % 2147483647) / 2147483647 * n);
    HOUSES.forEach((h, i) => { const d = o => Math.hypot(o[0] - h[0], o[1] - h[1]), prev = HOUSES.slice(0, i); // 지붕은 두 집 건너까지, 벽은 바로 옆집과 다르게
      let w, f, tries = 0; do { w = WALLS[rc(WALLS.length)]; f = ROOFS[rc(ROOFS.length)]; } while (++tries < 60 && prev.some(o => (d(o) < 15 && o[3] === f) || (d(o) < 11 && o[2] === w)));
      h.push(w, f, rc(2) === 1); }); // [x, z, 벽, 지붕, 박공지붕인지]
  }
  const texMat = (tex, hex) => toonMat({ map: tex, color: new THREE.Color(hex) });
  const barkMat = texMat(barkTex, '#a8744f');
  const haloMat = bend(new THREE.MeshBasicMaterial({ color: 0xffcf70, map: softTex, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending }));
  const halos = [];
  const halo = (size, x, y, z) => { const m = noShadow(new THREE.Mesh(new THREE.PlaneGeometry(size, size), haloMat)); m.rotation.x = -0.5; m.visible = false; halos.push(m); return at(m, x, y, z); };
  const houses = [];
  const prism = (g, w, d, h, y, mat) => { const o = new THREE.Group(), mid = new THREE.Group(), r0 = d / 1.732; // 세모 기둥을 눕힌 박공지붕
    const pr = mesh(new THREE.CylinderGeometry(r0, r0, w, 3), mat); pr.rotation.z = Math.PI / 2; mid.add(pr); mid.rotation.x = -Math.PI / 2;
    o.add(mid); o.scale.y = h / (1.5 * r0); g.add(at(o, 0, y + 0.5 * r0 * o.scale.y, 0)); };
  HOUSES.forEach(([x, z, wall, roof, gable]) => {
    const g = new THREE.Group(), b = (w, h, d, c, px, py, pz) => { const m = at(mesh(new THREE.BoxGeometry(w, h, d), c), px, py, pz); g.add(m); return m; };
    const B = 0.3, H = 2, TOP = B + H, F = 1.3; // F: 앞벽 z
    b(3.5, B, 2.9, '#cfc6b6', 0, B / 2, 0); // 돌 기단
    g.add(at(mesh(new THREE.BoxGeometry(3.2, H, 2.6), texMat(wallTex, wall)), 0, B + H / 2, 0));
    [-1, 1].forEach(sx => [-1, 1].forEach(sz => b(0.14, H, 0.14, '#ffffff', sx * 1.57, B + H / 2, sz * 1.27))); b(3.34, 0.12, 2.74, '#ffffff', 0, TOP - 0.04, 0); // 흰 모서리 기둥·띠
    if (gable) prism(g, 3.8, 3.2, 1.35, TOP + 0.08, texMat(roofTex, roof)); // 지붕: 박공·모임지붕 섞임
    else { const rf = at(mesh(new THREE.ConeGeometry(2.75, 1.6, 4), texMat(roofTex, roof)), 0, TOP + 0.88, 0); rf.rotation.y = Math.PI / 4; rf.scale.z = 0.86; g.add(rf); }
    b(3.5, 0.14, 2.9, roof, 0, TOP + 0.08, 0);
    b(0.42, 1.0, 0.42, '#b5654a', 0.9, TOP + 1.0, -0.3); b(0.54, 0.1, 0.54, '#8f4a36', 0.9, TOP + 1.52, -0.3); // 굴뚝
    b(0.84, 1.32, 0.1, '#a06a3c', 0, B + 0.66, F + 0.01); [-0.2, 0.2].forEach(dx => b(0.28, 0.5, 0.04, '#b9824e', dx, B + 0.5, F + 0.07)); // 문
    g.add(at(mesh(new THREE.SphereGeometry(0.06, 8, 6), '#f2c53a'), 0.27, B + 0.64, F + 0.09));
    const port = at(noShadow(mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.12, 14), winMat)), 0, B + 1.62, F + 0.02); port.rotation.x = Math.PI / 2; g.add(port);
    const ring = at(mesh(new THREE.TorusGeometry(0.18, 0.04, 6, 16), '#ffffff'), 0, B + 1.62, F + 0.05); g.add(ring);
    b(1.3, 0.08, 0.62, roof, 0, B + 1.42, F + 0.3).rotation.x = 0.32; [-0.55, 0.55].forEach(dx => b(0.06, 0.06, 0.4, '#ffffff', dx, B + 1.3, F + 0.2)); // 현관 지붕
    b(0.16, 0.22, 0.16, '#3a3a44', 0.62, B + 1.05, F + 0.1); g.add(at(noShadow(mesh(new THREE.BoxGeometry(0.11, 0.15, 0.17), winMat)), 0.62, B + 1.05, F + 0.1)); // 문 옆 등
    [-1, 1].forEach(sd => { const wx = sd * 1.05; // 창문: 흰 틀, 십자 창살, 지붕색 덧문, 꽃 상자
      b(0.74, 0.74, 0.06, '#ffffff', wx, B + 1.15, F); g.add(at(noShadow(mesh(new THREE.BoxGeometry(0.58, 0.58, 0.08), winMat)), wx, B + 1.15, F + 0.01));
      b(0.05, 0.58, 0.1, '#ffffff', wx, B + 1.15, F + 0.02); b(0.58, 0.05, 0.1, '#ffffff', wx, B + 1.15, F + 0.02);
      [-1, 1].forEach(s2 => b(0.16, 0.74, 0.05, roof, wx + s2 * 0.47, B + 1.15, F + 0.03));
      b(0.8, 0.16, 0.2, '#b9824e', wx, B + 0.72, F + 0.1); [-0.25, 0, 0.25].forEach((dx, j) => g.add(at(mesh(new THREE.SphereGeometry(0.09, 7, 6), ['#ff7fa6', '#ffcf3a', '#fff6e8'][(j + (sd > 0 ? 1 : 0)) % 3]), wx + dx, B + 0.85, F + 0.12)));
      g.add(halo(1.7, wx, B + 1.15, F + 0.2)); });
    b(1.2, 0.15, 0.5, '#d3c9ba', 0, 0.075, F + 0.42); // 계단
    // 마당: 잔디, 디딤돌, 흰 울타리(가운데 대문 자리는 비움), 우체통
    const yd = floor(mesh(new THREE.PlaneGeometry(5.6, 2.3, 6, 3), '#a5dc86')); yd.rotation.x = -Math.PI / 2; g.add(at(yd, 0, 0.02, F + 1.15));
    [F + 0.85, F + 1.5, F + 2.15].forEach(sz => { const st = at(mesh(new THREE.CylinderGeometry(0.27, 0.27, 0.05, 12), '#e6e0d3'), 0, 0.035, sz); g.add(st); });
    const fence = (x0, z0, x1, z1) => { const L = Math.hypot(x1 - x0, z1 - z0), n = Math.max(1, Math.round(L / 0.3)), alongX = Math.abs(x1 - x0) > 0.01;
      for (let i = 0; i <= n; i++) { const px = x0 + (x1 - x0) * i / n, pz = z0 + (z1 - z0) * i / n; b(alongX ? 0.09 : 0.06, 0.55, alongX ? 0.06 : 0.09, '#ffffff', px, 0.29, pz); }
      [0.2, 0.42].forEach(y => b(alongX ? L : 0.04, 0.05, alongX ? 0.04 : L, '#ffffff', (x0 + x1) / 2, y, (z0 + z1) / 2)); };
    const YB = F + 2.3; // 마당 앞 울타리 z
    fence(-2.8, F + 0.05, -2.8, YB); fence(2.8, F + 0.05, 2.8, YB); fence(-2.8, YB, -0.7, YB); fence(0.7, YB, 2.8, YB);
    [-0.7, 0.7].forEach(dx => { b(0.14, 0.75, 0.14, '#ffffff', dx, 0.38, YB); g.add(at(mesh(new THREE.SphereGeometry(0.08, 8, 6), '#ffffff'), dx, 0.8, YB)); }); // 대문 기둥
    b(0.06, 0.75, 0.06, '#8a5a34', 1.25, 0.38, YB - 0.3); b(0.36, 0.3, 0.46, roof, 1.25, 0.86, YB - 0.3); // 우체통
    houses.push({ x, z, g, show: 1 });
    scene.add(at(g, x, 0, z)); solid(x - 0.75, z, 1.55, 4.2); solid(x + 0.75, z, 1.55, 4.2); solid(x + 1.25, z + YB - 0.3, 0.2);
    [F + 0.3, F + 1, F + 1.7, YB].forEach(fz => [-2.8, 2.8].forEach(fx => solid(x + fx, z + fz, 0.16))); [1.0, 1.6, 2.2].forEach(fx => [-1, 1].forEach(sd => solid(x + sd * fx, z + YB, 0.16)));
  });

  // ── 마을사무소: 큰길 북쪽 끝, 광장을 바라봄. 갈색 목조 + 크림 회벽
  { const g = new THREE.Group(), OZ = -23, WOOD = '#6b4428', DARK = '#4a2d1a', ROOF = '#7a4a2e', PLASTER = '#f3e6cf';
    const box = (w, h, d, c, x, y, z) => g.add(at(mesh(new THREE.BoxGeometry(w, h, d), c), x, y, z));
    box(7.2, 0.36, 4.4, '#bfae92', 0, 0.18, 0); box(6.8, 0.1, 4, '#d6c7ab', 0, 0.41, 0); // 돌 기단
    g.add(at(mesh(new THREE.BoxGeometry(6.4, 2.9, 3.6), texMat(wallTex, PLASTER)), 0, 1.9, 0));
    [-3.15, -1.05, 1.05, 3.15].forEach(x => box(0.2, 2.9, 0.12, WOOD, x, 1.9, 1.82)); // 기둥 뼈대
    [0.6, 2.25, 3.3].forEach(y => box(6.6, 0.16, 0.14, WOOD, 0, y, 1.83));
    const rf = at(mesh(new THREE.ConeGeometry(4.8, 1.7, 4), texMat(roofTex, ROOF)), 0, 4.25, 0); rf.rotation.y = Math.PI / 4; rf.scale.z = 0.64; g.add(rf);
    box(6.9, 0.14, 4.1, DARK, 0, 3.42, 0);
    box(1.2, 1.3, 1.2, '#a8744f', 0, 5.05, 0); box(1.36, 0.12, 1.36, DARK, 0, 5.74, 0); // 시계탑
    const cap = at(mesh(new THREE.ConeGeometry(1, 0.95, 4), texMat(roofTex, ROOF)), 0, 6.27, 0); cap.rotation.y = Math.PI / 4; g.add(cap);
    g.add(at(mesh(new THREE.SphereGeometry(0.09, 10, 8), '#d9a441'), 0, 6.8, 0));
    const rim = at(mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.06, 28), '#d9a441'), 0, 5.05, 0.61); rim.rotation.x = Math.PI / 2; g.add(rim);
    const face = at(mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.06, 28), '#fbf3e2'), 0, 5.05, 0.64); face.rotation.x = Math.PI / 2; g.add(face);
    box(0.05, 0.26, 0.03, DARK, 0, 5.15, 0.68); box(0.2, 0.05, 0.03, DARK, 0.08, 5.05, 0.68);
    const sc = document.createElement('canvas'); sc.width = 320; sc.height = 72; const sg = sc.getContext('2d');
    sg.fillStyle = '#4a2d1a'; sg.fillRect(0, 0, 320, 72); sg.strokeStyle = '#d9a441'; sg.lineWidth = 4; sg.strokeRect(6, 6, 308, 60);
    sg.fillStyle = '#f6e7c8'; sg.font = "700 34px 'Malgun Gothic', sans-serif"; sg.textAlign = 'center'; sg.textBaseline = 'middle'; sg.fillText('마 을 사 무 소', 160, 38);
    g.add(at(noShadow(mesh(new THREE.PlaneGeometry(2.6, 0.58), flat(0xffffff, { map: new THREE.CanvasTexture(sc) }))), 0, 2.78, 1.92));
    box(1.7, 1.95, 0.08, DARK, 0, 1.43, 1.82); // 문틀과 양문, 위 채광창
    [-0.37, 0.37].forEach(x => { box(0.68, 1.5, 0.1, '#7d4f2e', x, 1.22, 1.86); box(0.5, 0.5, 0.04, '#6b4428', x, 1.42, 1.92); });
    [-0.1, 0.1].forEach(x => g.add(at(mesh(new THREE.SphereGeometry(0.05, 8, 6), '#d9a441'), x, 1.2, 1.93)));
    g.add(at(noShadow(mesh(new THREE.BoxGeometry(1.36, 0.26, 0.06), winMat)), 0, 2.12, 1.87));
    [-2.1, 2.1].forEach(x => { box(0.86, 0.96, 0.06, WOOD, x, 1.42, 1.85); g.add(at(noShadow(mesh(new THREE.BoxGeometry(0.66, 0.76, 0.08), winMat)), x, 1.42, 1.86)); box(0.05, 0.76, 0.1, WOOD, x, 1.42, 1.88); box(0.66, 0.05, 0.1, WOOD, x, 1.42, 1.88);
      [-1, 1].forEach(s => box(0.24, 0.96, 0.05, '#9a6a42', x + s * 0.58, 1.42, 1.87)); box(1, 0.14, 0.24, DARK, x, 0.88, 1.92); g.add(halo(1.6, x, 1.42, 2.05));
      [-0.3, 0, 0.3].forEach((dx, k) => g.add(at(mesh(new THREE.SphereGeometry(0.09, 7, 6), ['#e8a13a', '#fff6e8', '#e0685a'][k]), x + dx, 1.01, 1.95))); });
    [-2.1, 0, 2.1].forEach(x => { if (x) { box(0.9, 0.56, 0.06, WOOD, x, 2.8, 1.85); g.add(at(noShadow(mesh(new THREE.BoxGeometry(0.74, 0.42, 0.08), winMat)), x, 2.8, 1.86)); } });
    [-1.2, 1.2].forEach(x => { g.add(at(mesh(new THREE.CylinderGeometry(0.12, 0.14, 2.1, 10), '#8a5a34'), x, 1.5, 2.3)); box(0.36, 0.12, 0.36, '#bfae92', x, 0.5, 2.3); // 현관 기둥과 랜턴
      box(0.2, 0.26, 0.2, DARK, x, 1.9, 2.5); g.add(at(noShadow(mesh(new THREE.BoxGeometry(0.14, 0.18, 0.22), winMat)), x, 1.9, 2.5)); });
    const porch = at(mesh(new THREE.BoxGeometry(3, 0.14, 1.1), texMat(roofTex, ROOF)), 0, 2.6, 2.25); porch.rotation.x = 0.18; g.add(porch);
    box(2.8, 0.12, 1.1, '#bfae92', 0, 0.3, 2.65); box(2.4, 0.12, 0.6, '#cdbfa3', 0, 0.18, 3.2); // 계단
    scene.add(at(g, 0, 0, OZ)); [-2.2, 0, 2.2].forEach(x => solid(x, OZ, 1.9, 5));
  }
  // ── 슈퍼마켓: 마을사무소 오른쪽 1층 가게. 안은 마을 남쪽 바깥(SHOP.iz)에 따로 지어 두고, 문으로 오가면 그리로 옮겨 감
  const SHOP = { x: 13, z: -23, ix: 0, iz: 160, x0: -5.6, x1: 5.6, z0: 156.9, z1: 162.8, far: 100 }; // x0~z1: 안에서 걸을 수 있는 범위, far: z가 이보다 크면 가게 안
  { const g = new THREE.Group(), box = (w, h, d, c, x, y, z) => g.add(at(mesh(new THREE.BoxGeometry(w, h, d), c), x, y, z));
    box(7.4, 0.3, 4.4, '#cdbfa3', 0, 0.15, 0);
    g.add(at(mesh(new THREE.BoxGeometry(7, 2.6, 3.8), texMat(wallTex, '#fbf4e6')), 0, 1.6, 0));
    box(7.3, 0.5, 4.1, '#3f9a5a', 0, 3.05, 0); box(7.4, 0.12, 4.2, '#2f7a45', 0, 3.36, 0); // 평지붕과 난간
    const sc = document.createElement('canvas'); sc.width = 320; sc.height = 64; const sg = sc.getContext('2d');
    sg.fillStyle = '#2f7a45'; sg.fillRect(0, 0, 320, 64); sg.fillStyle = '#fff'; sg.font = "800 36px 'Malgun Gothic', sans-serif"; sg.textAlign = 'center'; sg.textBaseline = 'middle'; sg.fillText('🛒 슈퍼마켓', 160, 34);
    g.add(at(noShadow(mesh(new THREE.PlaneGeometry(3.4, 0.68), flat(0xffffff, { map: new THREE.CanvasTexture(sc) }))), 0, 3.06, 2.07));
    for (let i = 0; i < 10; i++) { const st = at(mesh(new THREE.BoxGeometry(0.7, 0.08, 1), i % 2 ? '#ffffff' : '#3f9a5a'), -3.15 + i * 0.7, 2.62, 2.3); st.rotation.x = 0.35; g.add(st); } // 줄무늬 차양
    [-2.2, 2.2].forEach(x => { box(2.3, 1.5, 0.06, '#2f7a45', x, 1.3, 1.91); g.add(at(noShadow(mesh(new THREE.BoxGeometry(2.1, 1.3, 0.08), winMat)), x, 1.3, 1.92)); box(0.05, 1.3, 0.1, '#2f7a45', x, 1.3, 1.95);
      [-0.6, 0, 0.6].forEach((dx, k) => box(0.36, 0.3, 0.1, ['#e0685a', '#e8a13a', '#5b8fd8'][k], x + dx, 0.8, 1.98)); g.add(halo(2.4, x, 1.3, 2.1)); });
    box(1.4, 2.1, 0.06, '#2f7a45', 0, 1.35, 1.91); [-0.33, 0.33].forEach(x => g.add(at(noShadow(mesh(new THREE.BoxGeometry(0.6, 1.9, 0.08), flat(0xcfeefc))), x, 1.3, 1.93))); // 유리문
    box(1.6, 0.06, 0.9, '#8a5a34', 0, 0.33, 2.5);
    [-3.1, 3.1].forEach(x => { box(0.5, 0.45, 0.5, '#b9824e', x, 0.53, 2.4); [-0.1, 0.1].forEach(dz => g.add(at(mesh(new THREE.SphereGeometry(0.11, 10, 8), x < 0 ? '#e8483f' : '#f2c53a'), x + dz, 0.82, 2.4 + dz))); }); // 문 앞 과일 상자
    scene.add(at(g, SHOP.x, 0, SHOP.z)); [-2.4, 0, 2.4].forEach(x => solid(SHOP.x + x, SHOP.z, 1.9, 3.6));
    strip(7.05, -19.9, 11.9, 1.6, sandMat(5, 1), 0.029); // 큰길에서 가게 앞까지 작은 길
    strip(6.45, -22.7, 1.8, 5.4, sandMat(1, 3), 0.028); // 사무소와 가게 사이로 뒤쪽 숲까지 가는 길
  }
  { // 가게 안: 앞쪽(남쪽)은 트여 있어 카메라가 들여다봄
    const g = new THREE.Group(), box = (w, h, d, c, x, y, z) => { const m = at(mesh(new THREE.BoxGeometry(w, h, d), c), x, y, z); g.add(m); return m; };
    const fl = paint(128, (c, s) => { c.fillStyle = '#f4ecdc'; c.fillRect(0, 0, s, s); c.fillStyle = '#dccbae'; c.fillRect(0, 0, s / 2, s / 2); c.fillRect(s / 2, s / 2, s / 2, s / 2); }, 6);
    const dark = floor(mesh(new THREE.PlaneGeometry(70, 40, 70, 40), flat(0x3a2a20))); dark.rotation.x = -Math.PI / 2; scene.add(at(dark, SHOP.ix, 0.02, SHOP.iz)); // 방 바깥은 어둡게
    const fm = floor(mesh(new THREE.PlaneGeometry(12, 8.4, 12, 9), toonMat({ map: fl }))); fm.rotation.x = -Math.PI / 2; g.add(at(fm, 0, 0.04, 0.05));
    noShadow(box(12.4, 5.5, 0.3, texMat(wallTex, '#e8f3e4'), 0, 2.75, -4.3)); [-1, 1].forEach(s => noShadow(box(0.3, 3.2, 8.6, texMat(wallTex, '#e8f3e4'), s * 6.2, 1.6, 0)));
    box(12.4, 0.5, 0.32, '#3f9a5a', 0, 3.4, -4.12);
    [-1, 1].forEach(s => box(4.6, 0.5, 0.25, '#3f9a5a', s * 3.85, 0.25, 4.2)); // 앞쪽 낮은 담 (가운데가 문)
    const goods = ['#e0685a', '#e8a13a', '#f2c53a', '#5b8fd8', '#4fae6a', '#b06fc8', '#ff8fb0', '#fff6e8'];
    const shelf = (x, z, w, h, rows, ry) => { const s = new THREE.Group(); s.add(at(mesh(new THREE.BoxGeometry(w, h, 0.6), '#c9905c'), 0, h / 2, 0));
      for (let r0 = 0; r0 < rows; r0++) { const y = 0.35 + r0 * (h - 0.3) / rows; s.add(at(mesh(new THREE.BoxGeometry(w + 0.04, 0.05, 0.66), '#8a5a34'), 0, y, 0));
        for (let k = 0; k < Math.floor(w / 0.32); k++) s.add(at(mesh(new THREE.BoxGeometry(0.22, 0.26, 0.22), goods[(k * 3 + r0 * 5 + Math.round(x)) % goods.length]), -w / 2 + 0.2 + k * 0.32, y + 0.16, 0.24)); }
      s.rotation.y = ry || 0; g.add(at(s, x, 0, z)); };
    shelf(-4.2, -3.75, 2.6, 2.2, 4); shelf(-1.2, -3.75, 2.6, 2.2, 4);
    box(3.2, 2.3, 0.7, '#dfe8ee', 3.6, 1.15, -3.75); g.add(at(noShadow(mesh(new THREE.BoxGeometry(2.9, 1.8, 0.06), flat(0xcfeefc))), 3.6, 1.2, -3.38)); // 음료 냉장고
    [0.6, 1.2, 1.8].forEach((y, r0) => { for (let k = 0; k < 7; k++) box(0.2, 0.36, 0.2, goods[(k + r0 * 2) % goods.length], 2.3 + k * 0.43, y, -3.3); });
    shelf(-2.6, -1.2, 3, 1.3, 2); shelf(-2.6, -1.2, 3, 1.3, 2, Math.PI); // 가운데 진열대(앞뒤 양면)
    box(2.8, 0.62, 0.9, '#b9824e', 3.6, 0.31, 0.3); box(3, 0.08, 1.05, '#8a5a34', 3.6, 0.66, 0.3); // 계산대
    box(0.55, 0.3, 0.45, '#56606c', 2.6, 0.85, 0.3); box(0.5, 0.22, 0.04, '#9fe0a0', 2.6, 0.95, 0.53);
    [-4.4, -3.3].forEach((x, i) => { box(0.9, 0.5, 0.7, '#c58f5c', x, 0.25, 1.4); for (let k = 0; k < 6; k++) g.add(at(mesh(new THREE.SphereGeometry(0.13, 10, 8), ['#e8483f', '#f2c53a'][i]), x - 0.28 + (k % 3) * 0.28, 0.6, 1.25 + Math.floor(k / 3) * 0.3)); }); // 과일 상자
    box(1.6, 0.04, 0.9, '#c94f4f', 0, 0.06, 3.6); // 나가는 문 깔개
    scene.add(at(g, SHOP.ix, 0, SHOP.iz));
    [[-2.6, -1.2, 0.75], [-3.8, -1.2, 0.75], [-1.4, -1.2, 0.75], [2.8, 0.3, 0.6], [4.4, 0.3, 0.6], [-3.85, 1.4, 0.75]].forEach(([x, z, r]) => solid(SHOP.ix + x, SHOP.iz + z, r));
  }

  // ── 놀이터: 강 아래 집들 맨 왼쪽 바깥. 그네 두 자리·미끄럼틀·시소·뺑뺑이·트램펄린, E로 탐 (탈 자리는 아래 seats 끝에 붙음)
  const PLAY = { x: -44, z: 12 }, movers = [], rides = [];
  strip(PLAY.x, PLAY.z, 17.6, 9, '#d9b878', 0.025); strip(PLAY.x, PLAY.z, 17, 8.4, sandMat(8, 4), 0.033);
  strip(-34.3, 10, 2.8, 2.2, sandMat(1, 1), 0.031); // 골목 끝에서 놀이터로
  { // 그네 두 자리
    const g = new THREE.Group(), gx = PLAY.x - 6, gz = PLAY.z - 2.2;
    [-1, 1].forEach(s => { g.add(at(mesh(new THREE.CylinderGeometry(0.09, 0.1, 2.7, 8), '#5b8fd8'), s * 2, 1.35, 0)); solid(gx + s * 2, gz, 0.3); });
    g.add(at(mesh(new THREE.BoxGeometry(4.3, 0.16, 0.16), '#e0685a'), 0, 2.65, 0));
    [-0.95, 0.95].forEach((dx, k) => { const pv = new THREE.Group();
      [-1, 1].forEach(s => pv.add(at(mesh(new THREE.CylinderGeometry(0.015, 0.015, 1.8, 4), '#e9dcc0'), s * 0.38, -0.9, 0)));
      pv.add(at(mesh(new THREE.BoxGeometry(0.95, 0.07, 0.32), ['#f2c53a', '#4fae6a'][k]), 0, -1.8, 0));
      g.add(at(pv, dx, 2.55, 0)); movers.push(pv);
      const q = { x: gx + dx, z: gz, face: 0, ox: 0, oz: 1.1, ride: '🎠 그네 타기', amp: 0.06, ph: k * 1.3 };
      q.tick = (t, dt, on) => { q.amp += ((on ? 0.6 : 0.06) - q.amp) * Math.min(1, dt * 2); pv.rotation.x = Math.sin(t * 1.9 + q.ph) * q.amp; };
      q.place = a => { const th = pv.rotation.x; a.g.position.set(q.x, 2.55 - 1.8 * Math.cos(th) + 0.04, q.z - 1.8 * Math.sin(th)); a.g.rotation.x = th; a.face = 0; };
      rides.push(q); });
    scene.add(at(g, gx, 0, gz));
  }
  { // 미끄럼틀: 사다리로 올라가 앞(남쪽)으로 미끄러져 내려옴
    const g = new THREE.Group(), sx = PLAY.x - 0.2, top = 1.6;
    [-1, 1].forEach(s => { [-0.45, 0.25].forEach(z => g.add(at(mesh(new THREE.CylinderGeometry(0.06, 0.06, top + 0.9, 8), '#5b8fd8'), s * 0.45, (top + 0.9) / 2, z))); });
    g.add(at(mesh(new THREE.BoxGeometry(1.05, 0.12, 0.85), '#f2c53a'), 0, top, -0.1));
    for (let i = 1; i < 5; i++) g.add(at(mesh(new THREE.BoxGeometry(0.85, 0.06, 0.08), '#e9dcc0'), 0, i * top / 5, -0.62)); // 사다리 칸
    [-1, 1].forEach(s => g.add(at(mesh(new THREE.BoxGeometry(0.06, top + 0.1, 0.06), '#5b8fd8'), s * 0.42, (top + 0.1) / 2, -0.62)));
    const L = Math.hypot(2.6, top - 0.15), ang = Math.atan2(top - 0.15, 2.6), ch = new THREE.Group();
    ch.add(at(mesh(new THREE.BoxGeometry(0.8, 0.06, L), '#e0685a'), 0, 0, 0)); [-1, 1].forEach(s => ch.add(at(mesh(new THREE.BoxGeometry(0.06, 0.2, L), '#e0685a'), s * 0.4, 0.1, 0)));
    ch.rotation.x = ang; g.add(at(ch, 0, (top + 0.15) / 2, 0.3 + 1.3));
    scene.add(at(g, sx, 0, PLAY.z - 2.1)); solid(sx, PLAY.z - 2.3, 0.65); solid(sx, PLAY.z - 0.9, 0.45);
    const z0 = PLAY.z - 2.1, q = { x: sx, z: z0 + 1.2, face: Math.PI, ox: 0, oz: 2.1, ride: '🛝 미끄럼틀 타기', reach: 1.9 };
    q.place = (a, t) => { // 0~0.9초 사다리 오르기 → 위에서 돌아앉기 → 1.3~2.1초 미끄러져 내려옴 → 끝나면 내림
      const u = t - a.sitAt; let y, z, f = Math.PI;
      if (u < 0.9) { const k = u / 0.9; y = k * top; z = z0 - 0.75 + k * 0.6; }
      else if (u < 1.3) { y = top; z = z0 - 0.1; f = (u - 0.9) / 0.4 * Math.PI + Math.PI; }
      else { const k = Math.min(1, (u - 1.3) / 0.8); y = top + 0.05 - k * (top - 0.15); z = z0 + 0.3 + k * 2.6; f = 0; }
      a.g.position.set(q.x, y, z); a.g.rotation.x = u > 1.3 ? -ang * 0.6 : 0; a.face = f;
      if (a === me && u > 2.2) { standUp(); me.hop = 0.4; }
    };
    rides.push(q);
  }
  { // 시소
    const g = new THREE.Group(), cx = PLAY.x + 5.4, cz = PLAY.z - 2, plank = new THREE.Group();
    g.add(at(mesh(new THREE.CylinderGeometry(0.22, 0.32, 0.55, 10), '#4fae6a'), 0, 0.27, 0));
    plank.add(at(mesh(new THREE.BoxGeometry(3.4, 0.1, 0.38), '#e8a13a'), 0, 0, 0));
    [-1, 1].forEach(s => { plank.add(at(mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.4, 6), '#e0685a'), s * 1.15, 0.22, 0)); plank.add(at(mesh(new THREE.BoxGeometry(0.06, 0.06, 0.4), '#e0685a'), s * 1.15, 0.42, 0)); });
    g.add(at(plank, 0, 0.58, 0)); movers.push(plank); scene.add(at(g, cx, 0, cz)); solid(cx, cz, 0.4);
    const pair = [-1, 1].map(s => ({ x: cx + s * 1.45, z: cz, face: s < 0 ? Math.PI / 2 : -Math.PI / 2, ox: 0, oz: 0.9, ride: '⚖️ 시소 타기', s }));
    let th = 0.2;
    pair[0].tick = (t, dt) => { const on = pair.some(q => actors.some(a => a.sit === q)); th += ((on ? Math.sin(t * 2.2) * 0.3 : 0.2) - th) * Math.min(1, dt * 4); plank.rotation.z = th; };
    pair.forEach(q => { q.place = a => { a.g.position.set(cx + q.s * 1.45 * Math.cos(th), 0.64 + q.s * 1.45 * Math.sin(th), cz); a.g.rotation.x = 0; a.face = q.face; }; rides.push(q); });
  }
  { // 뺑뺑이: 탄 사람이 있으면 빨리 돎
    const g = new THREE.Group(), cx = PLAY.x, cz = PLAY.z + 3, disc = new THREE.Group(); let spd = 0.25;
    g.add(at(mesh(new THREE.CylinderGeometry(0.25, 0.3, 0.3, 10), '#56606c'), 0, 0.15, 0));
    ['#e0685a', '#f2c53a', '#5b8fd8', '#4fae6a', '#b06fc8', '#ff8fb0'].forEach((c, k) => { const w = at(mesh(new THREE.CylinderGeometry(1.3, 1.3, 0.12, 6, 1, false, k * Math.PI / 3, Math.PI / 3), c), 0, 0, 0); disc.add(w); });
    disc.add(at(mesh(new THREE.CylinderGeometry(0.07, 0.07, 1, 8), '#e9dcc0'), 0, 0.5, 0));
    for (let k = 0; k < 3; k++) { const a = k * Math.PI * 2 / 3 + Math.PI / 3; const bar = at(mesh(new THREE.BoxGeometry(0.06, 0.06, 1.1), '#e9dcc0'), Math.sin(a) * 0.55, 0.95, Math.cos(a) * 0.55); bar.rotation.y = a; disc.add(bar); disc.add(at(mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.95, 6), '#e9dcc0'), Math.sin(a) * 1.1, 0.5, Math.cos(a) * 1.1)); }
    g.add(at(disc, 0, 0.36, 0)); movers.push(disc); scene.add(at(g, cx, 0, cz)); solid(cx, cz, 1.35);
    const trio = [0, 1, 2].map(k => ({ x: cx, z: cz, face: 0, ox: 0, oz: 2, ride: '🎡 뺑뺑이 타기', reach: 2.1, phi: k * Math.PI * 2 / 3 }));
    trio[0].tick = (t, dt) => { const on = trio.some(q => actors.some(a => a.sit === q)); spd += ((on ? 2 : 0.25) - spd) * Math.min(1, dt * 1.5); disc.rotation.y += spd * dt; };
    trio.forEach(q => { q.place = a => { const ang = disc.rotation.y + q.phi; a.g.position.set(cx + Math.sin(ang) * 0.85, 0.42, cz + Math.cos(ang) * 0.85); a.g.rotation.x = 0; a.face = ang; a.g.rotation.y = ang; }; rides.push(q); });
  }
  { // 트램펄린: 두 자리, 서로 엇박자로 통통 뜀. 내려앉을 때 그물이 쑥 들어감
    const g = new THREE.Group(), cx = PLAY.x + 5.4, cz = PLAY.z + 2.8, H = 0.55, mat = new THREE.Group();
    for (let k = 0; k < 6; k++) { const a = k / 6 * Math.PI * 2; g.add(at(mesh(new THREE.CylinderGeometry(0.05, 0.05, H, 6), '#56606c'), Math.sin(a) * 1.15, H / 2, Math.cos(a) * 1.15)); }
    const rim = at(mesh(new THREE.TorusGeometry(1.2, 0.13, 8, 36), '#4fae6a'), 0, H, 0); rim.rotation.x = Math.PI / 2; g.add(rim);
    for (let k = 0; k < 12; k++) { const a = k / 12 * Math.PI * 2, pad = at(mesh(new THREE.BoxGeometry(0.3, 0.05, 0.22), k % 2 ? '#f2c53a' : '#e0685a'), Math.sin(a) * 1.2, H + 0.13, Math.cos(a) * 1.2); pad.rotation.y = a; g.add(pad); }
    mat.add(at(mesh(new THREE.CylinderGeometry(1.08, 1.08, 0.04, 32), '#3a4a7a'), 0, 0, 0));
    g.add(at(mat, 0, H - 0.02, 0)); movers.push(mat); scene.add(at(g, cx, 0, cz)); solid(cx, cz, 1.3);
    const BOUNCE = 2.6, duo = [-1, 1].map(s => ({ x: cx, z: cz, face: 0, ox: 0, oz: 2, ride: '🤸 트램펄린 타기', reach: 2.1, stand: true, dx: s * 0.42, ph: s > 0 ? 0.5 : 0 }));
    const hop = (q, t) => { const u = (t * BOUNCE / Math.PI + q.ph) % 1; return Math.sin(u * Math.PI); }; // 0(바닥)~1(꼭대기)
    duo[0].tick = t => { let dip = 0; duo.forEach(q => { if (actors.some(a => a.sit === q)) dip = Math.max(dip, Math.max(0, 0.25 - hop(q, t)) * 0.6); }); mat.position.y = H - 0.02 - dip; };
    duo.forEach(q => { q.place = (a, t) => { const k = hop(q, t); a.g.position.set(cx + q.dx, H + k * 1.5 - Math.max(0, 0.25 - k) * 0.6, cz); a.g.rotation.x = 0; a.face = 0; }; rides.push(q); });
  }

  // ── 학교: 놀이터 위(북쪽). 2층 본관 + 가운데 시계탑, 현관 앞 돌길이 놀이터로 이어짐
  const SCH = { x: -44, z: -0.8 };
  { const g = new THREE.Group(), box = (w, h, d, c, x, y, z) => { const m = at(mesh(new THREE.BoxGeometry(w, h, d), c), x, y, z); g.add(m); return m; };
    const WALL = '#fff4e0', TRIM = '#6fbfa6', ROOF = '#d9604f', W = 12.4, D = 4.4, H = 4.6, B = 0.35, F = D / 2; // F: 앞면 z
    box(W + 0.6, B, D + 0.6, '#cdbfa3', 0, B / 2, 0); // 기단
    g.add(at(mesh(new THREE.BoxGeometry(W, H, D), texMat(wallTex, WALL)), 0, B + H / 2, 0));
    box(W + 0.12, 0.18, D + 0.12, TRIM, 0, B + 2.25, 0); box(W + 0.4, 0.24, D + 0.4, '#f6e7c8', 0, B + H + 0.08, 0); // 층 사이 띠, 처마
    const roof = (w, d, h, y, z, hex) => { const o = new THREE.Group(), mid = new THREE.Group(), r0 = d / 1.732; // 세모 기둥을 눕혀 박공지붕
      const pr = mesh(new THREE.CylinderGeometry(r0, r0, w, 3), texMat(roofTex, hex)); pr.rotation.z = Math.PI / 2; mid.add(pr); mid.rotation.x = -Math.PI / 2;
      o.add(mid); o.scale.y = h / (1.5 * r0); g.add(at(o, 0, y + 0.5 * r0 * o.scale.y, z)); };
    roof(W + 0.7, D + 0.9, 1.5, B + H + 0.2, 0, ROOF);
    // 1·2층 창문 (가운데 탑을 비우고 양쪽 날개에 셋씩)
    [2.45, 3.75, 5.05].forEach(ax => [-1, 1].forEach(sd => { const x = ax * sd;
      [B + 1.15, B + 3.3].forEach((y, fl) => { box(0.96, 1.12, 0.06, '#ffffff', x, y, F + 0.02); g.add(at(noShadow(mesh(new THREE.BoxGeometry(0.78, 0.94, 0.08), winMat)), x, y, F + 0.03));
        box(0.06, 0.94, 0.1, '#ffffff', x, y, F + 0.05); box(0.78, 0.06, 0.1, '#ffffff', x, y + 0.1, F + 0.05); box(1.08, 0.12, 0.14, TRIM, x, y + 0.62, F + 0.06);
        if (!fl) { box(1, 0.18, 0.26, '#b9824e', x, y - 0.66, F + 0.15); [-0.3, 0, 0.3].forEach((dx, k) => g.add(at(mesh(new THREE.SphereGeometry(0.1, 8, 6), ['#ff7fa6', '#ffcf3a', '#fff6e8'][(k + (sd > 0)) % 3]), x + dx, y - 0.52, F + 0.17))); g.add(halo(1.5, x, y, F + 0.2)); } }); }));
    // 가운데 시계탑과 현관
    const TW = 3.2, TH = 6.9, TF = F + 0.3;
    box(TW, TH, D + 0.6, '#fffaf0', 0, B + TH / 2, 0); box(TW + 0.14, 0.18, D + 0.74, TRIM, 0, B + 2.25, 0); box(TW + 0.3, 0.2, D + 0.9, '#f6e7c8', 0, B + TH + 0.06, 0);
    const cap = at(mesh(new THREE.ConeGeometry(2.55, 1.9, 4), texMat(roofTex, ROOF)), 0, B + TH + 1.1, 0); cap.rotation.y = Math.PI / 4; g.add(cap);
    box(0.08, 0.9, 0.08, '#d9a441', 0, B + TH + 2.4, 0); g.add(at(mesh(new THREE.SphereGeometry(0.13, 10, 8), '#d9a441'), 0, B + TH + 2.9, 0));
    const ring = at(mesh(new THREE.CylinderGeometry(0.75, 0.75, 0.08, 32), '#d9a441'), 0, B + 5.6, TF + 0.02); ring.rotation.x = Math.PI / 2; g.add(ring);
    const face = at(mesh(new THREE.CylinderGeometry(0.66, 0.66, 0.08, 32), '#fffdf6'), 0, B + 5.6, TF + 0.05); face.rotation.x = Math.PI / 2; g.add(face);
    for (let k = 0; k < 12; k++) { const a = k / 12 * Math.PI * 2; box(0.05, k % 3 ? 0.07 : 0.14, 0.03, '#56606c', Math.sin(a) * 0.54, B + 5.6 + Math.cos(a) * 0.54, TF + 0.1).rotation.z = -a; }
    box(0.06, 0.42, 0.03, '#3a3a44', 0, B + 5.78, TF + 0.12); const mh = box(0.05, 0.5, 0.03, '#3a3a44', 0.17, B + 5.6, TF + 0.12); mh.rotation.z = -1.2; mh.position.y += 0.08;
    const sc = document.createElement('canvas'); sc.width = 384; sc.height = 72; const sg = sc.getContext('2d');
    sg.fillStyle = '#2f6f5f'; sg.fillRect(0, 0, 384, 72); sg.strokeStyle = '#f6e7c8'; sg.lineWidth = 4; sg.strokeRect(6, 6, 372, 60);
    sg.fillStyle = '#fffaf0'; sg.font = "800 38px 'Malgun Gothic', sans-serif"; sg.textAlign = 'center'; sg.textBaseline = 'middle'; sg.fillText('햇살초등학교', 192, 38);
    g.add(at(noShadow(mesh(new THREE.PlaneGeometry(2.9, 0.54), flat(0xffffff, { map: new THREE.CanvasTexture(sc) }))), 0, B + 3.7, TF + 0.05));
    box(1.9, 2.2, 0.1, '#ffffff', 0, B + 1.1, TF + 0.02); [-0.44, 0.44].forEach(x => { box(0.8, 1.95, 0.1, '#5fa898', x, B + 0.98, TF + 0.05); box(0.5, 0.7, 0.04, '#cfeefc', x, B + 1.35, TF + 0.11); });
    const arch = at(mesh(new THREE.CylinderGeometry(0.95, 0.95, 0.1, 24, 1, false, -Math.PI / 2, Math.PI), '#ffffff'), 0, B + 2.2, TF + 0.02); arch.rotation.x = Math.PI / 2; g.add(arch);
    const fan = at(noShadow(mesh(new THREE.CylinderGeometry(0.8, 0.8, 0.12, 24, 1, false, -Math.PI / 2, Math.PI), winMat)), 0, B + 2.2, TF + 0.03); fan.rotation.x = Math.PI / 2; g.add(fan);
    box(3, 0.14, 1.1, TRIM, 0, B + 3.0, TF + 0.5); [-1.3, 1.3].forEach(x => { g.add(at(mesh(new THREE.CylinderGeometry(0.09, 0.1, 2.65, 10), '#ffffff'), x, B + 1.65, TF + 0.95)); });
    box(3.2, 0.16, 0.8, '#d6c7ab', 0, B + 0.08, TF + 0.55); box(3.6, 0.16, 0.6, '#cdbfa3', 0, 0.08, TF + 1.15); // 계단
    // 앞 화단(현관 앞은 비움)과 국기 게양대
    [-1, 1].forEach(sd => { box(4.2, 0.55, 0.6, '#5cbd50', sd * 4, 0.3, F + 0.95); for (let k = 0; k < 7; k++) g.add(at(mesh(new THREE.SphereGeometry(0.12, 8, 6), ['#ff7fa6', '#ffcf3a', '#fff6e8', '#ff8a3a'][k % 4]), sd * 4 - 1.8 + k * 0.6, 0.62, F + 1.05)); });
    g.add(at(mesh(new THREE.CylinderGeometry(0.05, 0.06, 5, 8), '#cbd5e1'), -7.4, 2.5, F + 1.4)); g.add(at(mesh(new THREE.SphereGeometry(0.1, 8, 6), '#d9a441'), -7.4, 5.05, F + 1.4));
    box(1.2, 0.75, 0.03, '#f2c53a', -6.78, 4.5, F + 1.4); box(0.36, 0.36, 0.04, '#e0685a', -6.78, 4.5, F + 1.41);
    scene.add(at(g, SCH.x, 0, SCH.z)); solid(SCH.x - 7.4, SCH.z + F + 1.4, 0.2); [-4.6, -2.3, 0, 2.3, 4.6].forEach(x => solid(SCH.x + x, SCH.z, 2.2, 7));
    strip(SCH.x, (SCH.z + TF + 1.45 + PLAY.z - 4.2) / 2, 2.2, PLAY.z - 4.2 - (SCH.z + TF + 1.45), sandMat(1, 2), 0.031); // 현관에서 놀이터까지 돌길
    strip(-34, 1.8, 2.8, 5.8, sandMat(1, 3), 0.0315); strip(-39.2, 3.9, 9.8, 1.6, sandMat(4, 1), 0.0312); // 분수 앞 골목 끝 → 학교 현관 앞
  }

  // ── 해변: 마을 맨 남쪽. 모래사장(BEACH.z0~z1)과 그 너머 바다, 야자나무·파라솔·비치볼
  const BEACH = { z0: 42.4, z1: 50.4 }; // z1: 물가(걸을 수 있는 끝)
  { const sandB = sandTex.clone(); sandB.needsUpdate = true; sandB.repeat.set(60, 4);
    strip(0, (BEACH.z0 + BEACH.z1) / 2 + 0.3, 150, BEACH.z1 - BEACH.z0 + 0.6, toonMat({ map: sandB, color: new THREE.Color('#fff3cf') }), 0.021);
    strip(0, BEACH.z1 + 0.4, 150, 0.9, '#e2c98f', 0.024); // 젖은 모래
    strip(0, 44, 2.2, 3.4, '#c9a06a', 0.032); for (let i = 0; i < 6; i++) strip(0, 42.6 + i * 0.6, 2.3, 0.08, '#a87e4c', 0.034); // 큰길 끝 나무 데크
  }
  const seaTex = waterTex.clone(); seaTex.needsUpdate = true; seaTex.repeat.set(30, 6);
  { const sea = floor(mesh(new THREE.PlaneGeometry(150, 34, 150, 34), flat(0xffffff, { map: seaTex }))); sea.rotation.x = -Math.PI / 2; scene.add(at(sea, 0, 0.028, BEACH.z1 + 17.8)); }
  const foam = noShadow(strip(0, BEACH.z1 + 0.75, 150, 0.35, flat(0xffffff, { transparent: true, opacity: 0.85 }), 0.04)); foam.userData.floor = false; // 밀려왔다 빠지는 물거품
  { // 야자나무: 휘어 올라간 줄기 마디, 늘어진 잎, 코코넛
    const palm = (x, z, lean, rot) => { const g = new THREE.Group(), segs = 7, h = 0.48;
      for (let i = 0; i < segs; i++) { const m = mesh(new THREE.CylinderGeometry(0.15 - i * 0.008, 0.19 - i * 0.008, h, 10), i % 2 ? '#b98a5a' : '#a87b4e'); m.rotation.z = -lean * i * 0.05; g.add(at(m, Math.sin(lean * i * 0.05) * 0 + lean * i * i * 0.012, h * (i + 0.5), 0)); }
      const top = new THREE.Group(), tx = lean * segs * segs * 0.012; top.position.set(tx, h * segs, 0); g.add(top);
      for (let k = 0; k < 8; k++) { const leaf = new THREE.Group(), mat = toonMat({ color: k % 2 ? 0x4fae5a : 0x3f9a4a }, 0.02); // 잎: 끝으로 갈수록 가늘고 아래로 휨
        [[0, 0.75, 0.32, 1.3, 0], [-0.12, 1.75, 0.22, 0.9, 0.5]].forEach(([y, z, w, len, rx]) => { const c = mesh(new THREE.ConeGeometry(w, len, 4), mat); c.rotation.x = Math.PI / 2 + rx; c.scale.set(1.6, 1, 0.18); c.position.set(0, y, z); leaf.add(c); });
        leaf.rotation.set(0.35 + (k % 2) * 0.15, k / 8 * Math.PI * 2, 0, 'YXZ'); top.add(leaf); }
      [[0.14, -0.12, 0.06], [-0.1, -0.14, 0.1], [0.02, -0.12, -0.14]].forEach(c => top.add(at(mesh(new THREE.SphereGeometry(0.12, 10, 8), '#7a4a2e'), c[0], c[1], c[2])));
      g.rotation.y = rot; scene.add(at(g, x, 0, z)); solid(x, z, 0.3); };
    [[-30, 45.5, 1, 0.3], [-23, 47.6, -1, 2.2], [-17.5, 44.6, 1, 4.1], [-9, 46.8, -1, 1.1], [-4.2, 44.2, 1, 5.2], [5.5, 47.2, -1, 0.6], [11, 44.8, 1, 3.3], [17.5, 47.8, -1, 2.7], [24, 45, 1, 5.9], [30.5, 47.2, -1, 1.7]].forEach(q => palm(...q));
    const umbrella = (x, z, c) => { const g = new THREE.Group(); g.add(at(mesh(new THREE.CylinderGeometry(0.04, 0.04, 2.1, 8), '#ffffff'), 0, 1.05, 0));
      for (let k = 0; k < 8; k++) { const w = mesh(new THREE.ConeGeometry(1.3, 0.45, 8, 1, true, k * Math.PI / 4, Math.PI / 4), k % 2 ? '#ffffff' : c); g.add(at(w, 0, 2.05, 0)); }
      const towel = at(mesh(new THREE.BoxGeometry(0.9, 0.03, 1.7), c), 0.9, 0.03, 0.4); towel.rotation.y = 0.2; g.add(towel); g.add(at(mesh(new THREE.BoxGeometry(0.9, 0.035, 0.25), '#ffffff'), 0.86, 0.035, -0.3));
      scene.add(at(g, x, 0, z)); solid(x, z, 0.15); };
    umbrella(-13, 47.5, '#e0685a'); umbrella(8.5, 46.5, '#5b8fd8'); umbrella(21, 46.2, '#f2c53a');
    const ball = new THREE.Group(); ['#e0685a', '#ffffff', '#5b8fd8', '#ffffff', '#f2c53a', '#ffffff'].forEach((c, k) => ball.add(mesh(new THREE.SphereGeometry(0.28, 12, 10, k * Math.PI / 3, Math.PI / 3), c))); scene.add(at(ball, -11.2, 0.28, 48.6));
    [[-6, 49.2, '#ff8a6a'], [14, 49.4, '#ffb347'], [-26, 49.1, '#ff7fa6']].forEach(([x, z, c]) => { const st = new THREE.Group(); for (let k = 0; k < 5; k++) { const hold = new THREE.Group(), arm = mesh(new THREE.ConeGeometry(0.07, 0.3, 6), c); arm.rotation.x = Math.PI / 2; arm.position.z = 0.15; arm.scale.z = 0.5; hold.add(arm); hold.rotation.y = k / 5 * Math.PI * 2; st.add(hold); } scene.add(at(st, x, 0.03, z)); }); // 불가사리
  }
  // ── 나무: 꽃·잎 뭉치는 한 번에 그리는 묶음(InstancedMesh)으로, 줄기와 열매만 따로
  const BLOB_MAX = 900;
  const mkBlobs = (tex, geo) => { const im = new THREE.InstancedMesh(geo || new THREE.SphereGeometry(1, 16, 11), bend(new THREE.MeshToonMaterial({ gradientMap: softGrad, map: tex }), 0.011), BLOB_MAX);
    im.count = 0; im.instanceColor = new THREE.BufferAttribute(new Float32Array(BLOB_MAX * 3), 3); scene.add(im); return im; }; // 색 칸은 미리 잡아 둠 (개수 0에서 넣으면 1개만 잡힘)
  const blobsPink = mkBlobs(blossomTex), blobsLeaf = mkBlobs(leafTex);
  const farBall = new THREE.SphereGeometry(1, 10, 7), blobsPinkFar = noShadow(mkBlobs(blossomTex, farBall)), blobsLeafFar = noShadow(mkBlobs(leafTex, farBall)); // 마을 바깥 배경 나무용: 면 수 적게, 그림자·테두리 없음
  const mtx = new THREE.Matrix4(), col = new THREE.Color(), dummy = new THREE.Object3D();
  const addBlob = (im, colors) => { const i = im.count++; im.setColorAt(i, col.set(pick(colors))); return i; };
  const PINK = ['#ffffff', '#fff2f5', '#ffe6ec', '#fff8fa'], LEAF = ['#ffffff', '#eaffe6', '#dff5d6', '#f4fff0'];
  const trees = [];
  const freeSpot = (x, z, pad) => z < BEACH.z0 - 1.5 && !onPath(x, z, 1.9 + pad) && Math.hypot(x, z) > 6.2 + pad && !(z > -26 && z < -17.8 && x > -0.5 && x < 17) && !(x < -31.5 && z > -2 && z < 5.5) 
    && riverDist(x, z) > 1.5 && HOUSES.every(h => Math.hypot(x - h[0], z - h[1]) > 4.2 + pad && !(Math.abs(x - h[0]) < 3.6 + pad && z > h[1] - 2 && z < h[1] + 4.4 + pad))
    && solids.every(s => Math.hypot(x - s.x, z - s.z) > s.r + 1.6 + pad) && trees.every(t => Math.hypot(x - t.x, z - t.z) > 2.6);
  function placeTree(tr) { // 줄기 묶음의 지금 위치·기울기대로 뭉치들을 옮김
    tr.g.updateMatrixWorld(true);
    tr.blobs.forEach(b => { dummy.position.set(b.x, b.y, b.z); dummy.scale.setScalar(b.r); dummy.rotation.set(b.rot[0], b.rot[1], b.rot[2]); dummy.updateMatrix(); tr.im.setMatrixAt(b.i, mtx.multiplyMatrices(tr.top.matrixWorld, dummy.matrix)); });
    tr.im.instanceMatrix.needsUpdate = true;
  }
  for (let i = 0, tries = 0; i < 36 && tries < 6000; tries++) {
    const x = (rnd() - 0.5) * 68, z = -22 + rnd() * 66;
    if (!freeSpot(x, z, 0)) continue;
    const kind = i % 5 < 3 ? 'blossom' : 'fruit', sc = 0.9 + rnd() * 0.35, cols = kind === 'blossom' ? PINK : LEAF;
    const g = new THREE.Group(), top = new THREE.Group(); top.position.y = 1.05; g.add(top);
    g.add(at(mesh(new THREE.CylinderGeometry(0.24, 0.36, 1.5, 18), barkMat), 0, 0.75, 0));
    g.add(at(mesh(new THREE.CylinderGeometry(0.34, 0.56, 0.36, 18), barkMat), 0, 0.18, 0));
    const im = kind === 'blossom' ? blobsPink : blobsLeaf;
    const list = [{ x: 0, y: 1.15, z: 0, r: 1.18 }, { x: 0.05, y: 1.95, z: 0.05, r: 0.78 }];
    for (let k = 0; k < 7; k++) { const a = k / 7 * 6.283 + rnd() * 0.4; list.push({ x: Math.cos(a) * 1.02, y: 0.62 + rnd() * 0.45, z: Math.sin(a) * 1.02, r: 0.6 + rnd() * 0.2 }); }
    for (let k = 0; k < 5; k++) { const a = k / 5 * 6.283 + rnd() * 0.5; list.push({ x: Math.cos(a) * 0.78, y: 1.5 + rnd() * 0.3, z: Math.sin(a) * 0.78, r: 0.56 + rnd() * 0.12 }); }
    for (let k = 0; k < 3; k++) { const a = rnd() * 6.283; list.push({ x: Math.cos(a) * 1.25, y: 1.05 + rnd() * 0.3, z: Math.sin(a) * 1.25, r: 0.42 }); }
    list.forEach(b => { b.i = addBlob(im, cols); b.rot = [rnd() * 6, rnd() * 6, rnd() * 6]; });
    const fruits = [];
    if (kind === 'fruit') [[0.95, 0.55, 0.95], [-0.8, 0.8, 0.9], [0.15, 1.45, 1.2], [1.25, 1.2, 0.2], [-1.2, 1.1, -0.1]].forEach(p => { const f = at(mesh(new THREE.SphereGeometry(0.19, 18, 13), '#e8483f'), p[0], p[1], p[2]); f.userData = { home: p.slice(), vy: 0, state: 'on' }; top.add(f); fruits.push(f); });
    g.scale.setScalar(sc); scene.add(at(g, x, 0, z));
    const tr = { x, z, g, top, fruits, blobs: list, im, kind, shake: 0, regrow: 0, sc };
    placeTree(tr); trees.push(tr); solid(x, z, 0.52 * sc); i++;
  }
  { const bg = [];
    for (let i = 0, tries = 0; i < 80 && tries < 5000; tries++) {
      const x = (rnd() - 0.5) * 112, z = -44 + rnd() * 100;
      if (!((Math.abs(x) > 36.5 && z < BEACH.z0 - 1) || z < -25.5) || riverDist(x, z) < 1.6 || bg.some(b => Math.hypot(x - b[0], z - b[1]) < 3.4) || (x < -31 && x > PLAY.x - 12 && z > SCH.z - 4.5 && z < PLAY.z + 7.5)) continue;
      bg.push([x, z]); i++;
      const sc = 1 + rnd() * 0.5, pinkTree = rnd() < 0.55, im = pinkTree ? blobsPinkFar : blobsLeafFar;
      scene.add(at(mesh(new THREE.CylinderGeometry(0.26 * sc, 0.4 * sc, 1.6 * sc, 12), barkMat), x, 0.8 * sc, z));
      [[0, 2.2, 0, 1.25], [0.9, 1.75, 0.2, 0.85], [-0.9, 1.8, -0.1, 0.85], [0.1, 1.7, 0.9, 0.8], [0, 1.75, -0.9, 0.8], [0.1, 3.0, 0, 0.8]].forEach(b => {
        dummy.position.set(x + b[0] * sc, b[1] * sc, z + b[2] * sc); dummy.scale.setScalar(b[3] * sc); dummy.rotation.set(rnd() * 6, rnd() * 6, rnd() * 6); dummy.updateMatrix(); im.setMatrixAt(addBlob(im, pinkTree ? PINK : LEAF), dummy.matrix); });
    } }
  // 덤불 (같은 뭉치 묶음에 얹음)
  [[-12.8, -3.8], [12.8, -3.8]].forEach(([x, z]) => {
    [[0, 0.38, 0, 0.55], [0.45, 0.3, 0.1, 0.4], [-0.42, 0.3, -0.08, 0.42]].forEach(b => { dummy.position.set(x + b[0], b[1], z + b[2]); dummy.scale.setScalar(b[3]); dummy.rotation.set(rnd() * 6, rnd() * 6, rnd() * 6); dummy.updateMatrix(); blobsLeaf.setMatrixAt(addBlob(blobsLeaf, LEAF), dummy.matrix); });
    solid(x, z, 0.55);
  });
  [blobsPink, blobsLeaf, blobsPinkFar, blobsLeafFar].forEach(im => { im.instanceMatrix.needsUpdate = true; im.instanceColor.needsUpdate = true; });
  // 벚꽃 나무 아래 떨어진 꽃잎
  { const bl = trees.filter(t => t.kind === 'blossom'), per = 16, im = noShadow(new THREE.InstancedMesh(new THREE.CircleGeometry(0.075, 5), flat(0xffffff), bl.length * per));
    bl.forEach((t, k) => { for (let j = 0; j < per; j++) { const a = rnd() * 6.283, r = 0.7 + rnd() * 2.1; dummy.position.set(t.x + Math.cos(a) * r, 0.055, t.z + Math.sin(a) * r); dummy.rotation.set(-Math.PI / 2, 0, rnd() * 6); dummy.scale.set(1, 0.7, 1); dummy.updateMatrix(); im.setMatrixAt(k * per + j, dummy.matrix); im.setColorAt(k * per + j, col.set(pick(['#ffd3de', '#ffe3ea', '#ffc2d2']))); } });
    scene.add(im); }

  // ── 튤립 꽃밭 (줄기·잎·꽃봉오리를 각각 한 묶음으로)
  const tulips = [], tulipParts = [];
  const TULIP = ['#f2473f', '#ffcf3a', '#fff6e8', '#ff8a3a', '#ff7fa6', '#f2473f', '#ffcf3a'];
  const bed = (cx, cz, nx, nz, gap, colorOf) => { for (let i = 0; i < nx; i++) for (let j = 0; j < nz; j++) tulips.push({ x: cx + (i - (nx - 1) / 2) * gap + (rnd() - 0.5) * 0.08, z: cz + (j - (nz - 1) / 2) * gap + (rnd() - 0.5) * 0.08, c: colorOf(i, j) }); };
  [-1, 1].forEach(s => bed(s * 1.75, 7.6, 1, 5, 0.62, (i, j) => TULIP[(j + (s > 0 ? 2 : 0)) % 5]));             // 남쪽 길가
  bed(-4.3, -1.9, 5, 2, 0.6, i => TULIP[i % 3]); bed(4.6, 1.9, 5, 2, 0.6, i => TULIP[(i + 2) % 5]);                 // 광장 옆
  HOUSES.forEach((h, k) => [-1, 1].forEach(sd => bed(h[0] + sd * 2.35, h[1] + 2.75, 1, 3, 0.55, (i, j) => TULIP[(j + k + (sd > 0 ? 2 : 0)) % 5]))); // 마당 울타리 안 꽃밭
  trees.filter((t, i) => i % 3 === 0).forEach((t, k) => { for (let a = 0; a < 7; a++) { const ang = a / 7 * 6.283, r = 1.25 * t.sc + 0.3; tulips.push({ x: t.x + Math.cos(ang) * r, z: t.z + Math.sin(ang) * r, c: TULIP[(a + k) % 5] }); } });
  { const n = tulips.length, white = () => toonMat({ color: 0xffffff }, 0.075);
    const stems = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.022, 0.03, 0.44, 5), toonMat({ color: 0x4fae4a }, 0.075), n);
    const leaves = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 6, 5), toonMat({ color: 0x5cbd50 }, 0.075), n * 2);
    const buds = new THREE.InstancedMesh(new THREE.SphereGeometry(0.115, 14, 10), white(), n);
    const tips = new THREE.InstancedMesh(new THREE.ConeGeometry(0.095, 0.13, 6), white(), n);
    tulips.forEach((t, i) => {
      const s = 0.68 + rnd() * 0.22, ry = rnd() * 6;
      dummy.rotation.set(0, 0, 0); dummy.scale.setScalar(s); dummy.position.set(t.x, 0.22 * s, t.z); dummy.updateMatrix(); stems.setMatrixAt(i, dummy.matrix);
      [-1, 1].forEach((d, k) => { dummy.position.set(t.x + Math.cos(ry) * 0.08 * d * s, 0.17 * s, t.z + Math.sin(ry) * 0.08 * d * s); dummy.rotation.set(0, -ry, -d * 0.5); dummy.scale.set(0.055 * s, 0.2 * s, 0.03 * s); dummy.updateMatrix(); leaves.setMatrixAt(i * 2 + k, dummy.matrix); });
      dummy.rotation.set(0, ry, 0); dummy.scale.set(s, s * 1.2, s); dummy.position.set(t.x, 0.5 * s, t.z); dummy.updateMatrix(); buds.setMatrixAt(i, dummy.matrix); buds.setColorAt(i, col.set(t.c));
      dummy.scale.setScalar(s); dummy.position.set(t.x, 0.63 * s, t.z); dummy.updateMatrix(); tips.setMatrixAt(i, dummy.matrix); tips.setColorAt(i, col.set(t.c));
    });
    [stems, leaves, buds, tips].forEach(m => scene.add(m)); tulipParts.push(buds, tips); }

  // 펫 테두리선 재질 (짙은 갈색)
  // 합쳐 그리기용 재질: 꼭짓점 색을 쓰는 툰 재질 하나와 테두리 재질 하나를 모든 펫·소품이 같이 씀
  const vcMat = toonMat({ vertexColors: true });
  const vcLine = bend(new THREE.MeshBasicMaterial({ color: 0xffffff, vertexColors: true, side: THREE.BackSide })); unlitMats.push({ m: vcLine, base: new THREE.Color(0xffffff) });
  const PET_LINE = new THREE.Color(0x5c3f30), petOpts = { material: M, vertexMaterial: vcMat, outline: vcLine, outlineColor: PET_LINE };
  let outlineOn = true, halosOn = false;
  // 풀 포기
  { const n = 420, im = new THREE.InstancedMesh(new THREE.ConeGeometry(0.05, 0.17, 4), toonMat({ color: 0xffffff }, 0.16), n);
    for (let i = 0; i < n; i++) { const x = (rnd() - 0.5) * 70, z = 6 + (rnd() - 0.5) * 60, s = 0.7 + rnd() * 0.9; const off = onPath(x, z, 1.4) || Math.hypot(x, z) < 4.7 || riverDist(x, z) < 0.4;
      dummy.position.set(x, off ? -5 : 0.08 * s, z); dummy.rotation.set(0, rnd() * 6, (rnd() - 0.5) * 0.4); dummy.scale.setScalar(s); dummy.updateMatrix(); im.setMatrixAt(i, dummy.matrix); im.setColorAt(i, col.set(pick(['#58b84f', '#66c458', '#4aa848']))); }
    im.userData.noShadow = true; scene.add(im); }
  for (let i = 0; i < 9; i++) { const x = (rnd() - 0.5) * 40, z = (rnd() - 0.5) * 40; if (!freeSpot(x, z, -0.6) || (z < -12 && x > 2 && x < 20)) continue; const r = 0.35 + rnd() * 0.3; const m = mesh(new THREE.DodecahedronGeometry(r, 0), '#c3c6ca'); m.scale.y = 0.7; scene.add(at(m, x, r * 0.4, z)); solid(x, z, r); }

  // ── 구름 (지평선 쪽에 떠서 천천히 흐름)·날리는 꽃잎
  const clouds = new THREE.Group(); scene.add(clouds);
  for (let i = 0; i < 7; i++) { const g = new THREE.Group(), m = flat(0xffffff, { fog: false }); [[0, 0, 1.6], [1.5, -0.2, 1.1], [-1.5, -0.25, 1.2], [0.6, 0.6, 1.0]].forEach(b => { const s = noShadow(at(new THREE.Mesh(new THREE.SphereGeometry(b[2], 10, 8), m), b[0], b[1], 0)); s.scale.y = 0.6; g.add(s); }); g.scale.setScalar(1.2 + rnd() * 1.3); clouds.add(at(g, -52 + i * 17 + rnd() * 6, 7 + rnd() * 6, -rnd() * 8)); }
  const PETALS = 90, petalIM = noShadow(new THREE.InstancedMesh(new THREE.PlaneGeometry(0.11, 0.075), flat(0xffd0dc, { side: THREE.DoubleSide }), PETALS)); scene.add(petalIM);
  const petals = Array.from({ length: PETALS }, () => ({ x: (rnd() - 0.5) * 26, y: rnd() * 4, z: 7 - rnd() * 20, p: rnd() * 6, v: 0.45 + rnd() * 0.5 }));

  // 가로등: 밤이 되면 등불과 바닥 불빛이 켜짐
  const lampMat = flat(0xfff6d8, { glow: true }), glowMat = flat(0xffd76a, { glow: true, map: softTex, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending });
  [[-2.7, 5.4], [2.7, 5.4], [-6.4, 1.7], [6.4, -1.7]].concat(...[0, 10, 20, 30].map(sz => [-24, -10, 10, 24].map(x => [x, sz + 1.6]))).forEach(([x, z]) => {
    const g = new THREE.Group();
    g.add(at(mesh(new THREE.CylinderGeometry(0.05, 0.07, 1.9, 8), '#56606c'), 0, 0.95, 0));
    g.add(at(mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.06, 8), '#56606c'), 0, 0.03, 0));
    g.add(at(mesh(new THREE.BoxGeometry(0.3, 0.05, 0.3), '#56606c'), 0, 1.92, 0));
    g.add(at(noShadow(mesh(new THREE.BoxGeometry(0.24, 0.3, 0.24), lampMat)), 0, 2.1, 0));
    const cap = at(mesh(new THREE.ConeGeometry(0.26, 0.2, 4), '#56606c'), 0, 2.35, 0); cap.rotation.y = Math.PI / 4; g.add(cap);
    g.add(halo(2.2, 0, 2.1, 0.2));
    const pool = noShadow(mesh(new THREE.PlaneGeometry(6.4, 6.4, 4, 4), glowMat)); pool.rotation.x = -Math.PI / 2; g.add(at(pool, 0, 0.08, 0));
    scene.add(at(g, x, 0, z)); solid(x, z, 0.18);
  });
  // 강물 속 물고기 그림자
  const fishMat = flat(0x1f5f9a, { transparent: true, opacity: 0.38, depthWrite: false });
  const fishes = Array.from({ length: 6 }, () => { const g = new THREE.Group(), body = noShadow(new THREE.Mesh(new THREE.CircleGeometry(0.2, 10), fishMat)), tail = noShadow(new THREE.Mesh(new THREE.CircleGeometry(0.11, 3), fishMat));
    body.scale.set(1.7, 0.75, 1); tail.position.x = -0.36; tail.rotation.z = Math.PI; g.add(body); g.add(tail); g.rotation.x = -Math.PI / 2; scene.add(g);
    return { g, tail, x: (rnd() - 0.5) * 66, off: (rnd() - 0.5) * 2.8, v: (0.5 + rnd() * 0.7) * (rnd() < 0.5 ? -1 : 1), ph: rnd() * 6, s: 0.7 + rnd() * 0.6 }; });
  // 별 (밤에만 지평선 위에 보임)·반딧불
  const starMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, fog: false, depthWrite: false });
  const stars = noShadow(new THREE.InstancedMesh(new THREE.CircleGeometry(0.16, 5), starMat, 110));
  for (let i = 0; i < 110; i++) { dummy.position.set((rnd() - 0.5) * 150, -30 + rnd() * 36, -62); dummy.rotation.set(0, 0, rnd() * 6); dummy.scale.setScalar(0.5 + rnd() * 1.3); dummy.updateMatrix(); stars.setMatrixAt(i, dummy.matrix); }
  scene.add(stars);
  const flyMat = flat(0xfff8a8, { glow: true, transparent: true, opacity: 0, depthWrite: false });
  const fireflies = Array.from({ length: 18 }, () => { const m = noShadow(new THREE.Mesh(new THREE.SphereGeometry(0.05, 6, 5), flyMat)); scene.add(m); return { m, x: (rnd() - 0.5) * 34, z: -4 + (rnd() - 0.5) * 30, ph: rnd() * 6 }; });

  // 나비: 튤립 둘레를 맴돎
  const butterflies = Array.from({ length: 9 }, (_, i) => {
    const home = tulips[Math.floor(rnd() * tulips.length)], g = new THREE.Group(), m = flat(pick([0xfff3a0, 0xffffff, 0xffb7d0, 0xa9dcff]), { side: THREE.DoubleSide });
    const wings = [-1, 1].map(sd => { const w = new THREE.Group(), pl = noShadow(new THREE.Mesh(new THREE.PlaneGeometry(0.13, 0.16), m)); pl.position.x = sd * 0.065; pl.rotation.x = -Math.PI / 2; w.add(pl); g.add(w); return w; });
    scene.add(g); return { g, wings, hx: home.x, hz: home.z, r: 0.5 + rnd() * 0.9, sp: 0.5 + rnd() * 0.6, ph: rnd() * 6 };
  });
  // 걸을 때 발밑 먼지
  const puffs = Array.from({ length: 10 }, () => { const m = noShadow(new THREE.Mesh(new THREE.SphereGeometry(0.11, 8, 6), flat(0xffffff, { transparent: true, opacity: 0, depthWrite: false }))); m.visible = false; scene.add(m); return { m, life: 0 }; });
  let puffAt = 0, puffI = 0;

  // ── 들꽃: 잔디에 흩어진 작은 흰 꽃 (그림자를 받는 납작한 꽃)
  { const n = 520, petal = floor(new THREE.InstancedMesh(new THREE.CircleGeometry(0.062, 7), toonMat({ color: 0xffffff }), n)), heart = floor(new THREE.InstancedMesh(new THREE.CircleGeometry(0.024, 6), toonMat({ color: 0xffd23a }), n));
    for (let i = 0; i < n; i++) { const x = (rnd() - 0.5) * 70, z = 6 + (rnd() - 0.5) * 60, off = onPath(x, z, 1.5) || Math.hypot(x, z) < 4.8 || riverDist(x, z) < 0.4, k = 0.7 + rnd() * 0.7;
      dummy.rotation.set(-Math.PI / 2, 0, rnd() * 6); dummy.scale.setScalar(k); dummy.position.set(x, off ? -5 : 0.052, z); dummy.updateMatrix(); petal.setMatrixAt(i, dummy.matrix); petal.setColorAt(i, col.set(pick(['#ffffff', '#ffffff', '#fff3c4', '#ffe1ea'])));
      dummy.position.y = off ? -5 : 0.058; dummy.updateMatrix(); heart.setMatrixAt(i, dummy.matrix); }
    scene.add(petal); scene.add(heart); }
  // ── 연잎: 강물 위에 떠서 살짝 흔들림 (몇 개는 분홍 꽃)
  const lilies = Array.from({ length: 10 }, (_, i) => {
    const g = new THREE.Group(), pad = floor(mesh(new THREE.CircleGeometry(0.34, 16, 0.35, 5.6), i % 2 ? '#4fb85a' : '#63c466')); pad.rotation.x = -Math.PI / 2; g.add(pad);
    if (i % 3 === 0) { g.add(at(mesh(new THREE.SphereGeometry(0.1, 10, 8), '#ff9db8'), 0.05, 0.07, 0)); for (let k = 0; k < 5; k++) { const a = k / 5 * 6.283, pt = mesh(new THREE.SphereGeometry(0.075, 8, 6), '#ffc4d4'); pt.scale.set(1, 0.5, 0.6); pt.rotation.y = -a; g.add(at(pt, 0.05 + Math.cos(a) * 0.1, 0.045, Math.sin(a) * 0.1)); } g.add(at(mesh(new THREE.SphereGeometry(0.04, 8, 6), '#ffd23a'), 0.05, 0.14, 0)); }
    let x = (rnd() - 0.5) * 64; if (Math.abs(x) < 2.2) x += x < 0 ? -3 : 3; // 다리 밑은 비움
    const q = { g, x, z: riverZ(x) + (rnd() - 0.5) * 3.2, ph: rnd() * 6, s: 0.8 + rnd() * 0.6 }; g.scale.setScalar(q.s); g.rotation.y = rnd() * 6; scene.add(at(g, q.x, 0.064, q.z)); return q;
  });
  // ── 물 반짝임
  const SPARK = 40, sparkIM = noShadow(new THREE.InstancedMesh(new THREE.PlaneGeometry(0.3, 0.3), flat(0xffffff, { map: softTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }), SPARK)); scene.add(sparkIM);
  const sparks = Array.from({ length: SPARK }, () => { const x = (rnd() - 0.5) * 68; return { x, z: riverZ(x) + (rnd() - 0.5) * 3.6, ph: rnd() * 6, sp: 1.2 + rnd() * 1.6 }; });
  // ── 굴뚝 연기 (집마다 세 덩이가 차례로 피어오름)
  const SMOKE = houses.length * 3, smokeIM = noShadow(new THREE.InstancedMesh(new THREE.SphereGeometry(0.17, 10, 8), flat(0xf6f3ee), SMOKE)); scene.add(smokeIM);
  // ── 분수 물방울
  const DROPS = 16, dropIM = noShadow(new THREE.InstancedMesh(new THREE.SphereGeometry(0.05, 7, 5), flat(0xd8f3ff), DROPS)); scene.add(dropIM);
  // ── 구름 그림자: 넓고 옅은 그늘이 땅 위를 천천히 지나감
  const cloudShadeMat = bend(new THREE.MeshBasicMaterial({ color: 0x1c3a2a, map: softTex, transparent: true, opacity: 0.14, depthWrite: false }));
  const SHADES = 5, shadeIM = noShadow(new THREE.InstancedMesh(new THREE.PlaneGeometry(2, 2, 12, 12), cloudShadeMat, SHADES)); shadeIM.renderOrder = 1; scene.add(shadeIM);
  const shades = Array.from({ length: SHADES }, (_, i) => ({ x: -40 + i * 19, z: (rnd() - 0.5) * 34, r: 7 + rnd() * 5, v: 0.5 + rnd() * 0.3 }));

  { const im = noShadow(new THREE.InstancedMesh(new THREE.PlaneGeometry(2, 2), bend(new THREE.MeshBasicMaterial({ color: 0x143016, map: softTex, transparent: true, opacity: 0.42, depthWrite: false })), solids.length));
    solids.forEach((c, i) => { const r = Math.min(2.5, c.r * 1.7 + 0.3); dummy.position.set(c.x, 0.066, c.z); dummy.rotation.set(-Math.PI / 2, 0, 0); dummy.scale.set(r, r, 1); dummy.updateMatrix(); im.setMatrixAt(i, dummy.matrix); });
    im.renderOrder = 1; scene.add(im); }

  // 누른 곳 표시
  const marker = noShadow(mesh(new THREE.RingGeometry(0.22, 0.32, 20), flat(0xffffff, { transparent: true, opacity: 0.85 }))); marker.rotation.x = -Math.PI / 2; marker.visible = false; scene.add(marker);
  const dress = root => root.traverse(o => { o.frustumCulled = false; if (o.isMesh) { o.castShadow = !o.userData.noShadow && !o.userData.floor; o.receiveShadow = Boolean(o.userData.floor); } });
  dress(scene); // 휜 뒤의 위치로는 화면 밖 판정이 틀리므로 끔 + 그림자 설정

  // ── 환경 테두리선: 물건마다 제 색을 어둡게 한 선을 두름
  const envOutlines = [];
  { // 집·소품·줄기를 묶음마다 한 덩어리로 합침 (따로 움직이는 그네 자리와 나무 윗부분은 건너뜀)
    const stop = new Set(movers.concat(trees.map(t => t.top)));
    const opt = () => ({ stop, vertexMaterial: vcMat, outlineMaterial: vcLine, thickness: 0.022, minSize: 0.15, minSecond: 0.06, accept: m => m.material === winMat || (m.material.isMeshToonMaterial && !m.userData.noShadow && !m.userData.floor) });
    const loose = new THREE.Group(); // 묶음 없이 놓인 것(배경 줄기·바위·집 기단)
    scene.children.slice().forEach(o => { if (o.isMesh && !o.isInstancedMesh && o.material.isMeshToonMaterial && !o.userData.floor && !o.userData.noShadow) loose.add(o); });
    scene.add(loose);
    scene.children.slice().concat(movers).forEach(o => { if (o.isGroup) VillagePets.merge(THREE, o, opt()).outlines.forEach(ol => envOutlines.push(ol)); });
    dress(scene);
  }
  const lineMats = {};
  const lineMat = (hex, sway, grow) => { // 뒷면만 그리는 어두운 재질 (시간대 색도 따라감)
    const key = hex + '/' + (sway || 0) + '/' + (grow || 0);
    if (!lineMats[key]) { const c = new THREE.Color(hex).multiplyScalar(0.42); const m = bend(new THREE.MeshBasicMaterial({ color: c, side: THREE.BackSide }), sway || 0, grow || 0); unlitMats.push({ m, base: c.clone() }); lineMats[key] = m; }
    return lineMats[key];
  };
  { // 집·소품·줄기·열매·바위: 같은 모양을 살짝 키운 껍데기를 덧씌움 (상자도 모서리가 끊기지 않음)
    const T = 0.022, list = [], size = new THREE.Vector3();
    scene.traverse(o => {
      if (!o.isMesh || o.isInstancedMesh || o.userData.floor || o.userData.noShadow || !o.material.isMeshToonMaterial) return;
      const t = o.geometry.type; if (o.userData.merged || t === 'PlaneGeometry' || t === 'CircleGeometry' || t === 'RingGeometry' || t === 'TorusGeometry') return;
      list.push(o);
    });
    list.forEach(o => {
      if (!o.geometry.boundingBox) o.geometry.computeBoundingBox();
      o.geometry.boundingBox.getSize(size); size.multiply(o.scale); size.set(Math.abs(size.x), Math.abs(size.y), Math.abs(size.z));
      const ext = [size.x, size.y, size.z].sort((a, b) => b - a);
      if (ext[0] < 0.3 || ext[1] < 0.06) return; // 손잡이·밧줄 같은 작은 것은 뺌
      const ol = new THREE.Mesh(o.geometry, lineMat('#' + o.material.color.getHexString()));
      ol.scale.set(1 + 2 * T / Math.max(size.x, 0.03), 1 + 2 * T / Math.max(size.y, 0.03), 1 + 2 * T / Math.max(size.z, 0.03));
      ol.frustumCulled = false; ol.userData.noShadow = true; o.add(ol); envOutlines.push(ol);
    });
  }
  { // 나무 뭉치·튤립: 같은 묶음을 한 번 더, 바깥으로 부풀려 그림 (위치는 원래 묶음과 함께 움직임)
    const twin = (im, hex, sway, grow, geo) => { const ol = new THREE.InstancedMesh(geo || im.geometry, lineMat(hex, sway, grow), im.count); ol.instanceMatrix = im.instanceMatrix; ol.count = im.count; ol.frustumCulled = false; ol.userData.noShadow = true; scene.add(ol); envOutlines.push(ol); };
    const lowBall = new THREE.SphereGeometry(1, 12, 8); // 테두리는 면 수를 줄여 가볍게
    twin(blobsPink, '#ff8fb0', 0.011, 0.03, lowBall); twin(blobsLeaf, '#3fae52', 0.011, 0.03, lowBall);
    tulipParts.forEach(im => twin(im, '#b0603a', 0.075, 0.011));
  }

  // ── 캐릭터 (나 + 돌아다니는 친구들)
  const labels = $('labels');
  const actors = [];
  function makeActor(type, name, x, z, me) {
    const pet = VillagePets.build(THREE, type, petOpts); pet.outlines.forEach(o => { o.visible = outlineOn; });
    const g = new THREE.Group(); g.add(pet.group); g.position.set(x, 0, z); dress(g); scene.add(g);
    const tag = document.createElement('div'); tag.className = 'tag' + (me ? ' me' : ''); tag.textContent = name; labels.appendChild(tag);
    const a = { type, name, pet, g, tag, x, z, face: 0, moving: false, wave: 0, target: null, wait: rnd() * 3, me };
    actors.push(a); return a;
  }
  function setPet(a, type) { a.g.remove(a.pet.group); a.type = type; a.pet = VillagePets.build(THREE, type, petOpts); a.pet.outlines.forEach(o => { o.visible = outlineOn; }); dress(a.pet.group); a.g.add(a.pet.group); }
  const petType = t => (t && VillagePets.SPECS[t] ? t : 'guest'); // 펫이 없으면 새싹 모습
  const me = makeActor(demo ? 'shiba' : petType(host.me.pet), demo ? '나' : host.me.name, (rnd() - 0.5) * 3, 4 + rnd() * 1.5, true);
  const sel = $('petSel');
  if (demo) { // 시험판: 흉내 친구 여섯과 펫 고르기
    [['ginger', '민준'], ['rabbit', '서연'], ['panda', '지호'], ['hedgehog', '하윤'], ['piglet', '도윤'], ['black', '수아']].forEach(([t, n], i) => makeActor(t, n, Math.cos(i) * 6, Math.sin(i * 1.7) * 5 + 3, false));
    Object.keys(VillagePets.SPECS).forEach(id => { const o = document.createElement('option'); o.value = id; o.textContent = VillagePets.SPECS[id].name; sel.appendChild(o); });
    sel.value = 'shiba'; sel.onchange = () => { setPet(me, sel.value); sel.blur(); };
  }
  // 슈퍼마켓 너구리 점원 둘 (나중에 물건 파는 역할)
  const clerks = [['🦝 도토리', 3.6, -0.6], ['🦝 솔방울', -2.1, 1.7]].map(([n, x, z]) => { const a = makeActor('raccoon', n, SHOP.ix + x, SHOP.iz + z, false); a.npc = true; a.wait = 1e9; a.face = 0; solid(a.x, a.z, 0.35); return a; });
  const ownerOf = i => demo ? actors.filter(a => !a.npc)[i + 1] : host.students[i]; // i번째 집 주인

  // ── 움직임·부딪힘
  const LX = 33, LZ0 = -25, LZ1 = BEACH.z1, SPEED = 3.3, RUN = 1.8, R = 0.32; // RUN: Shift 누르고 뛸 때 배수
  function step(a, dx, dz) {
    const pz = a.z; let x = a.x + dx, z = a.z + dz;
    solids.forEach(c => { const d = Math.hypot(x - c.x, z - c.z), min = c.r + R; if (d < min && d > 1e-4) { x = c.x + (x - c.x) / d * min; z = c.z + (z - c.z) / d * min; } });
    if (pz < SHOP.far && riverDist(x, z) < 0) { // 강: 다리 위에서만 건넘
      if (Math.abs(a.x) <= RIVER.bridge && riverDist(a.x, pz) < 0.05) x = Math.max(-RIVER.bridge + 0.25, Math.min(RIVER.bridge - 0.25, x));
      else if (Math.abs(x) > RIVER.bridge - 0.25) z = riverZ(x) + (pz >= riverZ(a.x) ? 1 : -1) * RIVER.w / 2;
    }
    if (x < -LX && pz < SHOP.far) { // 집들 왼쪽 바깥은 학교 앞마당·놀이터 안으로만 감
      const zMin = x > -35.4 ? -1.1 : SCH.z + 3.9; // 골목에서 꺾어 올라가는 길목은 학교 옆이라 더 아래까지 걸음
      if (a.x >= -LX && (z < -1.1 || z > PLAY.z + 4)) x = -LX;
      else if (x < -35.4 && a.x >= -35.4 && z < zMin) x = -35.4; // 학교 옆벽
      else z = Math.max(zMin, Math.min(PLAY.z + 4, z));
    }
    if (z < -21 && pz < SHOP.far) { // 사무소·가게 뒤로는 그 사이 길로만 들어감
      if (pz >= -21 && Math.abs(x - 6.45) > 0.9) z = -21; else x = Math.max(5.55, Math.min(7.35, x));
    }
    [a.x, a.z] = clampZone(x, z, pz > SHOP.far);
  }
  const clampZone = (x, z, inShop) => inShop ? [Math.max(SHOP.ix + SHOP.x0, Math.min(SHOP.ix + SHOP.x1, x)), Math.max(SHOP.z0, Math.min(SHOP.z1, z))] : [Math.max(PLAY.x - 8.2, Math.min(LX, x)), Math.max(LZ0, Math.min(LZ1, z))];
  const keys = {};
  const onKeyDown = e => {
    if (!running || /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable) return;
    keys[e.code] = true;
    if (e.code === 'Space') { e.preventDefault(); wave(); }
    if (e.code === 'KeyE') interact();
    if (e.code === 'KeyR') resetView();
    if (e.code === 'Digit1') emote('joy');
    if (e.code === 'Digit2') emote('heart');
    if (e.code.startsWith('Arrow')) e.preventDefault();
  };
  const onKeyUp = e => { keys[e.code] = false; };
  window.addEventListener('keydown', onKeyDown); window.addEventListener('keyup', onKeyUp);
  const ray = new THREE.Raycaster(), plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0), hit = new THREE.Vector3();
  // 시점: 화면을 끌면 좌우로 360도 돌고 위아래로 기울어짐 (위로 끌면 하늘 쪽을 봄). 끌지 않고 누르기만 하면 그 자리로 걸어감. 두 번 누르면 원래 시점
  const view = { yaw: 0, pitch: 0.567, drag: null }; // pitch: 내려다보는 각, 0.1보다 작아지면 고개를 들어 위를 봄
  const PITCH_MIN = -0.45, PITCH_MAX = 1.2;
  const bendDist = (x, z) => (x - me.x) * curve.uDir.value.x + (z - me.z) * curve.uDir.value.y;
  canvas.addEventListener('pointerdown', e => { view.drag = { x: e.clientX, y: e.clientY, moved: false, id: e.pointerId }; });
  canvas.addEventListener('pointermove', e => {
    const d = view.drag; if (!d || d.id !== e.pointerId) return;
    const dx = e.clientX - d.x, dy = e.clientY - d.y;
    if (!d.moved && Math.hypot(dx, dy) < 6) return;
    if (!d.moved) { d.moved = true; try { canvas.setPointerCapture(e.pointerId); } catch (err) {} }
    d.x = e.clientX; d.y = e.clientY;
    if (me.z > SHOP.far) return; // 가게 안은 앞이 트인 방이라 돌리지 않음
    view.yaw -= dx * 0.006; view.pitch = Math.max(PITCH_MIN, Math.min(PITCH_MAX, view.pitch + dy * 0.005));
  });
  const endDrag = e => {
    const d = view.drag; if (!d || d.id !== e.pointerId) return; view.drag = null;
    if (d.moved || e.type === 'pointercancel') return;
    const rc = canvas.getBoundingClientRect();
    ray.setFromCamera({ x: (e.clientX - rc.left) / rc.width * 2 - 1, y: -((e.clientY - rc.top) / rc.height) * 2 + 1 }, camera);
    if (!ray.ray.intersectPlane(plane, hit)) return;
    const [tx, tz] = clampZone(hit.x, hit.z, me.z > SHOP.far); me.target = { x: tx, z: tz, stuck: 0 };
    marker.position.set(me.target.x, 0.09, me.target.z); marker.visible = true;
  };
  canvas.addEventListener('pointerup', endDrag); canvas.addEventListener('pointercancel', endDrag);
  const resetView = () => { view.yaw = 0; view.pitch = 0.567; };
  canvas.addEventListener('dblclick', resetView);
  const viewBtn = $('viewBtn'); viewBtn.onclick = () => { resetView(); viewBtn.blur(); }; // 시점을 돌렸을 때만 보임
  // 소리: 파일 없이 그 자리에서 만드는 짧은 효과음 (기본은 끔)
  let audio = null, soundOn = false;
  function tone(f, d, type, when, vol, f2) {
    if (!soundOn || !audio) return;
    const o = audio.createOscillator(), g = audio.createGain(), t0 = audio.currentTime + (when || 0);
    o.type = type || 'sine'; o.frequency.setValueAtTime(f, t0); if (f2) o.frequency.exponentialRampToValueAtTime(f2, t0 + d);
    g.gain.setValueAtTime(vol || 0.12, t0); g.gain.exponentialRampToValueAtTime(0.001, t0 + d);
    o.connect(g); g.connect(audio.destination); o.start(t0); o.stop(t0 + d + 0.02);
  }
  const sfx = {
    wave: () => { tone(660, 0.12); tone(880, 0.16, 'sine', 0.1); },
    shake: () => { for (let i = 0; i < 5; i++) tone(170 + Math.random() * 130, 0.07, 'triangle', i * 0.06, 0.08); },
    pick: () => tone(520, 0.18, 'sine', 0, 0.14, 1040),
    knock: () => { tone(140, 0.08, 'square', 0, 0.1); tone(140, 0.08, 'square', 0.17, 0.1); },
    note: () => tone(740, 0.14, 'triangle', 0, 0.1),
  };
  const outlineBtn = $('outlineBtn');
  outlineBtn.onclick = () => { outlineOn = !outlineOn; outlineBtn.textContent = '테두리: ' + (outlineOn ? '켬' : '끔'); actors.forEach(a => a.pet.outlines.forEach(o => { o.visible = outlineOn; })); envOutlines.forEach(o => { o.visible = outlineOn; }); };
  const soundBtn = $('soundBtn');
  soundBtn.onclick = () => { soundOn = !soundOn; if (soundOn && !audio) { const AC = window.AudioContext || window.webkitAudioContext; if (AC) audio = new AC(); } soundBtn.textContent = '소리: ' + (soundOn ? '켬' : '끔'); if (soundOn) sfx.note(); };
  function say(a, text, sec) { a.say = text; a.sayT = sec || 1.8; }
  // 앉을 자리: y = 앉는 높이, face = 앉아서 보는 쪽, (ox, oz) = 일어날 때 내려서는 곳
  const seats = rides; // 순서는 친구 화면과 맞춰야 함 (번호로 주고받음)
  function emote(kind) { // 1 기쁨 · 2 하트: 가까운 친구들이 따라 함
    const text = kind === 'joy' ? '😄 야호!' : '❤️';
    const act = a => { say(a, text, 1.4); if (kind === 'joy') a.hop = 0.4; else popText('❤️', a.x, 1.9, a.z); };
    act(me); netEmote(kind === 'joy' ? 'j' : 'h'); if (kind === 'joy') sfx.pick(); else sfx.note();
    actors.forEach(a => { if (!a.me && !a.remote && Math.hypot(a.x - me.x, a.z - me.z) < 4.5) { a.target = null; a.wait = 2; a.lookAt = me; a.wave = 0.01; setTimeout(() => act(a), 350); } });
  }
  $('joyBtn').onclick = () => emote('joy');
  $('heartBtn').onclick = () => emote('heart');
  const prompt = $('prompt'), shakeBtn = $('shakeBtn');
  // 지금 내 곁에서 할 수 있는 일
  function nearby() {
    if (me.sit) return { kind: 'stand', label: me.sit.ride ? '내리기' : '일어나기' };
    const seat = seats.find(q => Math.hypot(me.x - q.x, me.z - q.z) < (q.reach || 1.3) && !actors.some(a => a !== me && a.sit === q)); // 빈 자리만
    if (seat) return { kind: 'seat', seat, label: seat.ride || '🪑 앉기' };
    for (let i = 0; i < houses.length; i++) { const h = houses[i]; if (Math.hypot(me.x - h.x, me.z - (h.z + 1.9)) < 1.2) return { kind: 'door', house: h, owner: ownerOf(i), label: !ownerOf(i) ? '🚪 빈 집' : demo ? '🚪 ' + ownerOf(i).name + '네 집 · 똑똑' : ownerOf(i).id === host.me.id ? '🚪 내 방 들어가기' : '🚪 ' + ownerOf(i).name + '네 집 놀러 가기' }; }
    if (Math.hypot(me.x - 3.1, me.z + 3.1) < 2) return { kind: 'board', label: '📋 게시판 보기' };
    if (Math.hypot(me.x - SHOP.x, me.z - (SHOP.z + 2.7)) < 1.4) return { kind: 'shopIn', label: '🛒 슈퍼마켓 들어가기' };
    if (Math.hypot(me.x - SHOP.ix, me.z - (SHOP.iz + 3)) < 1.1) return { kind: 'shopOut', label: '🚪 밖으로 나가기' };
    const clerk = clerks.find(a => Math.hypot(a.x - me.x, a.z - me.z) < 1.9);
    if (clerk) return { kind: 'clerk', clerk, label: '💬 ' + clerk.name.slice(3) + ' 점원과 이야기' };
    let best = null, bd = 2.4;
    trees.forEach(t => { const d = Math.hypot(t.x - me.x, t.z - me.z); if (d < bd) { bd = d; best = t; } });
    if (best) return { kind: 'tree', tree: best, label: best.fruits.some(f => f.userData.state === 'on') ? '🍎 열매 따기' : best.kind === 'blossom' ? '🌸 꽃잎 흔들기' : '🌳 나무 흔들기' };
    return null;
  }
  function standUp() { if (!me.sit) return; me.x = me.sit.x + me.sit.ox; me.z = me.sit.z + me.sit.oz; me.sit = null; }
  function interact() {
    const c = nearby(); if (!c) return;
    if (c.kind === 'tree') return shake();
    if (c.kind === 'stand') return standUp();
    if (c.kind === 'seat') { me.sit = c.seat; me.x = c.seat.x; me.z = c.seat.z; me.target = null; marker.visible = false; sfx.note(); return; }
    if (c.kind === 'door' && !demo) { // 실제 마을: 그 친구의 방(방 꾸미기)으로 들어감
      me.face = Math.PI; sfx.knock();
      if (!c.owner) { say(me, '아직 빈 집이야', 1.6); return; }
      me.hop = 0.3; say(me, '똑똑!', 0.8); const id = c.owner.id; setTimeout(() => { if (running) host.visitHome(id); }, 450); return;
    }
    if (c.kind === 'door') { me.face = Math.PI; me.hop = 0.3; say(me, '똑똑!', 1.2); sfx.knock(); const o = c.owner; if (o && Math.hypot(o.x - me.x, o.z - me.z) < 9) { say(o, '어서 와!', 2); o.wave = 1.8; o.target = null; o.wait = 2.2; o.lookAt = me; } return; }
    if (c.kind === 'shopIn') return goTo(SHOP.ix, SHOP.iz + 2.4, Math.PI);
    if (c.kind === 'shopOut') return goTo(SHOP.x, SHOP.z + 2.9, 0);
    if (c.kind === 'clerk') { const k = c.clerk; me.face = Math.atan2(k.x - me.x, k.z - me.z); k.face = Math.atan2(me.x - k.x, me.z - k.z); k.wave = 1.6; say(k, pick(['어서 오세요! 🛒', '곧 물건을 팔 거예요!', '천천히 둘러보세요 😊']), 2.2); sfx.note(); return; }
    if (c.kind === 'board') { me.face = Math.atan2(3.1 - me.x, -3.1 - me.z); say(me, '오늘의 공지: 사이좋게 놀기 😊', 2.6); sfx.note(); }
  }
  function goTo(x, z, face) { // 가게 안팎으로 옮겨 감: 카메라도 바로 따라감
    me.x = x; me.z = z; me.face = face; me.target = null; marker.visible = false; sfx.knock();
    view.yaw = 0; view.pitch = 0.567; camera.position.set(x, 5.6 * zoom, z + 8.8 * zoom); net.want = true;
  }
  function popText(text, x, y, z) { // 그 자리 위로 떠오르다 사라지는 글자
    const dz = bendDist(x, z); v.set(x, y - curve.uCurve.value * dz * dz, z).project(camera);
    const d = document.createElement('div'); d.className = 'pop'; d.textContent = text;
    d.style.transform = `translate(-50%, -100%) translate(${((v.x + 1) / 2 * canvas.clientWidth).toFixed(1)}px, ${((1 - v.y) / 2 * canvas.clientHeight).toFixed(1)}px)`;
    labels.appendChild(d); setTimeout(() => d.remove(), 1000);
  }
  let zoom = 1; // 마우스 휠로 가까이·멀리
  canvas.addEventListener('wheel', e => { e.preventDefault(); zoom = Math.max(0.6, Math.min(1.5, zoom * (e.deltaY > 0 ? 1.08 : 0.93))); }, { passive: false });
  // 자동 화질: 느리면 선명도 → 그림자 → 선명도 순으로 낮춤
  const quality = { lvl: 0, acc: 0, n: 0, low: 0, names: ['화질 높음', '화질 보통', '그림자 끔', '화질 낮음'] };
  function lowerQuality() {
    quality.lvl++;
    if (quality.lvl === 1) renderer.setPixelRatio(1);
    else if (quality.lvl === 2) { sun.castShadow = false; $('shadowBtn').textContent = '그림자: 끔'; envOutlines.forEach(o => { o.visible = false; }); } // 환경 테두리도 같이 끔
    else renderer.setPixelRatio(0.75);
    $('qN').textContent = quality.names[quality.lvl];
  }
  function wave() { sfx.wave(); me.wave = 1.6; netEmote('w'); actors.forEach(a => { if (!a.me && !a.remote && Math.hypot(a.x - me.x, a.z - me.z) < 4.5) { a.wave = 1.8; a.target = null; a.wait = 2.2; a.lookAt = me; } }); }
  let fruitN = 0, burst = 0;
  function shake() {
    let best = null, bd = 2.4;
    trees.forEach(t => { const d = Math.hypot(t.x - me.x, t.z - me.z); if (d < bd) { bd = d; best = t; } });
    if (!best) return;
    best.shake = 0.7; me.face = Math.atan2(best.x - me.x, best.z - me.z); sfx.shake();
    best.fruits.forEach(f => { if (f.userData.state === 'on') { f.userData.state = 'fall'; f.userData.vy = 0; } });
    if (best.fruits.length) best.regrow = 14;
    if (best.kind === 'blossom') for (let k = 0; k < 18; k++) { const p = petals[(burst++) % PETALS]; p.x = best.x + (rnd() - 0.5) * 2.4; p.z = best.z + (rnd() - 0.5) * 2.4; p.y = 1.6 + rnd() * 1.8; } // 벚꽃 나무는 꽃잎이 쏟아짐
  }
  $('waveBtn').onclick = wave;
  shakeBtn.onclick = () => { if (nearby()) interact(); };
  const curveBtn = $('curveBtn'); let curveOn = true;
  curveBtn.onclick = () => { curveOn = !curveOn; curveBtn.textContent = '둥근 땅: ' + (curveOn ? '켬' : '끔'); };
  const timeBtn = $('timeBtn');
  timeBtn.onclick = () => { const order = ['day', 'sunset', 'night']; env.key = order[(order.indexOf(env.key) + 1) % 3]; timeBtn.textContent = '시간: ' + TIMES[env.key].label; };
  const shadowBtn = $('shadowBtn');
  shadowBtn.onclick = () => { sun.castShadow = !sun.castShadow; shadowBtn.textContent = '그림자: ' + (sun.castShadow ? '켬' : '끔'); };

  function moveToward(a, tx, tz, dt) {
    const dx = tx - a.x, dz = tz - a.z, d = Math.hypot(dx, dz);
    if (d < 0.12) return true;
    const px = a.x, pz = a.z, s = Math.min(d, SPEED * (a.me ? me.run : a.remote ? (d > 4.5 ? RUN : 1) : 0.55) * dt);
    step(a, dx / d * s, dz / d * s);
    a.face = Math.atan2(dx, dz); a.moving = true;
    return Math.hypot(a.x - px, a.z - pz) < s * 0.25 ? 'stuck' : false;
  }


  // ── 친구 위치 주고받기: village/{학급}/{학생} = "x,z,목표x,목표z,앉은자리,감정,감정번호,펫"
  // 좌표를 계속 보내지 않고 "어디서 어디로 간다"만 방향이 바뀔 때 보냄 (키보드로 걸을 땐 0.8초마다 앞을 내다본 목적지를 갱신)
  const net = { ref: null, list: null, conn: null, key: '', lastAt: 0, want: false, n: 0, emo: '', remotes: {} };
  const f1 = v => (Math.round(v * 10) / 10).toString();
  function netEmote(k) { net.n = (net.n + 1) % 1000; net.emo = k; net.want = true; }
  function netTick(kx, kz, now) {
    if (!net.ref) return;
    const sit = me.sit ? seats.indexOf(me.sit) : '';
    const key = kx + ',' + kz + '|' + (me.target ? f1(me.target.x) + ',' + f1(me.target.z) : '') + '|' + sit + '|' + (me.moving ? 1 : 0) + '|' + net.n + '|' + me.type;
    if (key !== net.key) { net.key = key; net.want = true; } else if ((kx || kz) && now - net.lastAt > 800) net.want = true;
    if (!net.want || now - net.lastAt < 250) return;
    net.want = false; net.lastAt = now;
    let tx = me.x, tz = me.z;
    if (kx || kz) { const l = Math.hypot(kx, kz); tx = me.x + kx / l * SPEED * me.run * 1.1; tz = me.z + kz / l * SPEED * me.run * 1.1; } else if (me.target) { tx = me.target.x; tz = me.target.z; }
    net.ref.set([f1(me.x), f1(me.z), f1(tx), f1(tz), sit, net.emo, net.n, me.type].join(',')).catch(() => {});
  }
  function netApply(id, raw) {
    if (id === host.me.id || typeof raw !== 'string') return;
    const p = raw.split(','); if (p.length < 8) return;
    const x = +p[0], z = +p[1], tx = +p[2], tz = +p[3]; if (![x, z, tx, tz].every(isFinite)) return;
    const type = petType(p[7]);
    let a = net.remotes[id];
    if (!a) { a = net.remotes[id] = makeActor(type, host.nameOf(id), x, z, false); a.remote = true; a.id = id; a.emoN = p[6]; a.face = Math.PI * 2 * Math.random(); updateCount(); }
    else if (a.type !== type) setPet(a, type);
    const seat = p[4] === '' ? null : seats[+p[4]] || null;
    if (seat) { a.sit = seat; a.x = seat.x; a.z = seat.z; a.target = null; }
    else {
      if (a.sit) { a.sit = null; a.x = x; a.z = z; }
      if (Math.hypot(a.x - x, a.z - z) > 3.2) { a.x = x; a.z = z; } // 너무 벌어지면 바로 옮김
      a.target = Math.hypot(tx - a.x, tz - a.z) > 0.15 ? { x: tx, z: tz, stuck: 0 } : null;
    }
    if (p[6] !== a.emoN) { a.emoN = p[6]; // 새 감정 표현
      if (p[5] === 'w') a.wave = 1.6;
      else if (p[5] === 'j') { say(a, '😄 야호!', 1.4); a.hop = 0.4; }
      else if (p[5] === 'h') { say(a, '❤️', 1.4); popText('❤️', a.x, 1.9, a.z); }
    }
  }
  function netRemove(id) { const a = net.remotes[id]; if (!a) return; delete net.remotes[id]; scene.remove(a.g); a.tag.remove(); const i = actors.indexOf(a); if (i >= 0) actors.splice(i, 1); updateCount(); }
  function updateCount() { const el = $('count'); if (el) el.textContent = demo ? '' : (host.db ? `지금 ${Object.keys(net.remotes).length + 1}명` : '혼자 보기 (로그인하면 친구가 보여요)'); }
  function netJoin() {
    if (demo || !host.db || net.ref) return;
    const base = `village/${host.code}`;
    net.ref = host.db.ref(`${base}/${host.me.id}`); net.key = ''; net.want = true; net.lastAt = 0;
    net.list = host.db.ref(base);
    net.list.on('child_added', sn => netApply(sn.key, sn.val()));
    net.list.on('child_changed', sn => netApply(sn.key, sn.val()));
    net.list.on('child_removed', sn => netRemove(sn.key));
    // 끊기면 서버가 내 칸을 지움. 다시 연결되면 예약을 다시 걸고 위치를 다시 올림
    net.conn = host.db.ref('.info/connected');
    net.conn.on('value', sn => { if (sn && sn.val() === true && net.ref) { net.ref.onDisconnect().remove().catch(() => {}); net.key = ''; net.want = true; } });
  }
  function netLeave() {
    if (!net.ref) return;
    try { net.list.off(); net.conn.off(); net.ref.onDisconnect().cancel(); } catch (e) {}
    net.ref.remove().catch(() => {}); net.ref = net.list = net.conn = null;
    Object.keys(net.remotes).forEach(netRemove);
  }

  // ── 미니맵: 땅·길·강·집·나무는 한 번 그려 두고, 매 프레임 친구와 나만 점으로 올림
  const MAP = { x0: -54, x1: 34, z0: -25.5, z1: 56, s: 6 }, mapC = $('map');
  mapC.width = (MAP.x1 - MAP.x0) * MAP.s; mapC.height = (MAP.z1 - MAP.z0) * MAP.s;
  const mapG = mapC.getContext('2d'), mapBg = document.createElement('canvas'); mapBg.width = mapC.width; mapBg.height = mapC.height;
  const mx = x => (x - MAP.x0) * MAP.s, mz = z => (z - MAP.z0) * MAP.s;
  { const g = mapBg.getContext('2d'), S = MAP.s, rect = (x, z, w, d, c) => { g.fillStyle = c; g.fillRect(mx(x - w / 2), mz(z - d / 2), w * S, d * S); };
    g.fillStyle = '#8fd07a'; g.fillRect(0, 0, mapBg.width, mapBg.height);
    rect(-10, (BEACH.z0 + BEACH.z1) / 2, 100, BEACH.z1 - BEACH.z0, '#f6e6b4'); rect(-10, (BEACH.z1 + MAP.z1) / 2 + 0.5, 100, MAP.z1 - BEACH.z1 + 1, '#4fb3e8'); rect(-10, BEACH.z1 + 0.4, 100, 0.6, '#ffffff');
    [[-30, 45.5], [-23, 47.6], [-17.5, 44.6], [-9, 46.8], [-4.2, 44.2], [5.5, 47.2], [11, 44.8], [17.5, 47.8], [24, 45], [30.5, 47.2]].forEach(([x, z]) => { g.fillStyle = '#3f9a4a'; g.beginPath(); g.arc(mx(x), mz(z), 1.1 * S, 0, 6.29); g.fill(); });
    [[RIVER.w + 1.1, '#ead9a0'], [RIVER.w, '#56bdee']].forEach(([w, c]) => { g.strokeStyle = c; g.lineWidth = w * S; g.beginPath(); for (let x = MAP.x0; x <= MAP.x1; x += 0.5) g.lineTo(mx(x), mz(riverZ(x))); g.stroke(); });
    rect(0, 11, 2.2, 62, '#ead2a0'); STREETS.forEach(st => rect(0, st.z, st.len, 2.2, '#ead2a0'));
    rect(0, BR.z, BR.half * 2, BR.L, '#cfc7b6');
    g.fillStyle = '#cfccc5'; g.beginPath(); g.arc(mx(0), mz(0), 4.4 * S, 0, 6.29); g.fill();
    g.fillStyle = '#7fd0f0'; g.beginPath(); g.arc(mx(0), mz(0), 1.3 * S, 0, 6.29); g.fill();
    HOUSES.forEach(h => { rect(h[0], h[1] + 2.45, 5.6, 2.3, '#a5dc86'); rect(h[0], h[1], 3.2, 2.6, h[3]); });
    rect(0, -23, 6.4, 3.6, '#7a4a2e'); rect(0, -23, 1.2, 1.2, '#a8744f'); rect(SHOP.x, SHOP.z, 7, 3.8, '#3f9a5a'); rect(7.05, -19.9, 11.9, 1.6, '#ead2a0'); rect(6.45, -22.7, 1.8, 5.4, '#ead2a0'); rect(PLAY.x, PLAY.z, 17, 8.4, '#e9d9a8');
    rect(-34.3, 10, 2.8, 2.2, '#ead2a0'); rect(-34, 1.8, 2.8, 5.8, '#ead2a0'); rect(-39.2, 3.9, 9.8, 1.6, '#ead2a0'); rect(SCH.x, SCH.z, 12.4, 4.4, '#d9604f'); rect(SCH.x, SCH.z + 0.3, 3.2, 5, '#c24f40'); rect(SCH.x, (SCH.z + 3.95 + PLAY.z - 4.2) / 2, 2.2, PLAY.z - 4.2 - (SCH.z + 3.95), '#ead2a0');
    [[-6, -2.2, 4.2, 0.5, '#e0685a'], [-0.2, -1.4, 1, 3.4, '#e0685a'], [5.4, -2, 3.4, 0.5, '#e8a13a']].forEach(b => rect(PLAY.x + b[0], PLAY.z + b[1], b[2], b[3], b[4]));
    [[0, 3, '#5b8fd8'], [5.4, 2.8, '#4fae6a']].forEach(b => { g.fillStyle = b[2]; g.beginPath(); g.arc(mx(PLAY.x + b[0]), mz(PLAY.z + b[1]), 1.3 * S, 0, 6.29); g.fill(); });
    trees.forEach(t => { g.fillStyle = t.kind === 'blossom' ? '#ffc8d6' : '#3f9e4b'; g.beginPath(); g.arc(mx(t.x), mz(t.z), 1.2 * t.sc * S, 0, 6.29); g.fill(); });
  }
  const mapBox = $('mapBox'), mapBtn = $('mapBtn');
  const setMap = on => { mapBox.classList.toggle('off', !on); mapBtn.textContent = on ? '▾ 내리기' : '🗺 지도'; try { localStorage.setItem('vlgMap', on ? '1' : '0'); } catch (e) {} };
  try { setMap(localStorage.getItem('vlgMap') !== '0'); } catch (e) { setMap(true); }
  mapBtn.onclick = () => setMap(mapBox.classList.contains('off'));
  function drawMap() {
    if (mapBox.classList.contains('off')) return;
    mapG.drawImage(mapBg, 0, 0);
    const dot = (x, z, r, fill) => { mapG.fillStyle = fill; mapG.strokeStyle = '#fff'; mapG.lineWidth = 3; mapG.beginPath(); mapG.arc(mx(x), mz(z), r, 0, 6.29); mapG.fill(); mapG.stroke(); };
    const out = a => a.z > SHOP.far ? [SHOP.x, SHOP.z + 2.4] : [a.x, a.z]; // 가게 안에 있으면 가게 문 앞에 표시
    actors.forEach(a => { if (!a.me && !a.npc) dot(...out(a), 7, a.remote ? '#f0a83a' : '#8a94a6'); });
    const f = me.face, x = mx(out(me)[0]), z = mz(out(me)[1]); // 나: 바라보는 쪽을 가리키는 화살촉
    mapG.fillStyle = '#e8483f'; mapG.strokeStyle = '#fff'; mapG.lineWidth = 3; mapG.beginPath();
    mapG.moveTo(x + Math.sin(f) * 16, z + Math.cos(f) * 16); mapG.lineTo(x + Math.sin(f + 2.5) * 11, z + Math.cos(f + 2.5) * 11); mapG.lineTo(x + Math.sin(f - 2.5) * 11, z + Math.cos(f - 2.5) * 11); mapG.closePath(); mapG.fill(); mapG.stroke();
  }

  // ── 매 프레임
  const camPos = new THREE.Vector3(), v = new THREE.Vector3();
  let prev = performance.now();
  function frame(now) {
    if (!running) return;
    if (!root.isConnected || root.getClientRects().length === 0) { // 화면이 가려지면 스스로 멈추고, 다시 보이면 이어서 돎
      api.pause(); autoPaused = true;
      const iv = setInterval(() => { if (!root.isConnected || !autoPaused) return clearInterval(iv); if (root.getClientRects().length) { clearInterval(iv); autoPaused = false; api.resume(); } }, 700);
      return;
    }
    const t = now / 1000, raw = (now - prev) / 1000, dt = Math.min(0.05, raw); prev = now;
    if (raw < 0.25 && document.visibilityState === 'visible') { // 가려져 있을 때의 느린 프레임은 세지 않음
      quality.acc += raw; quality.n++;
      if (quality.acc >= 2) { const fps = quality.n / quality.acc; $('fpsN').textContent = Math.round(fps); quality.low = fps < 24 ? quality.low + 1 : 0; if (quality.low >= 2 && quality.lvl < 3) { lowerQuality(); quality.low = 0; } quality.acc = 0; quality.n = 0; }
    }
    const w = canvas.clientWidth, h = canvas.clientHeight, pr = renderer.getPixelRatio();
    if (canvas.width !== Math.floor(w * pr) || canvas.height !== Math.floor(h * pr)) { renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }

    // 나
    me.moving = false; me.run = keys.ShiftLeft || keys.ShiftRight ? RUN : 1;
    const ix = (keys.KeyD || keys.ArrowRight ? 1 : 0) - (keys.KeyA || keys.ArrowLeft ? 1 : 0), iz = (keys.KeyS || keys.ArrowDown ? 1 : 0) - (keys.KeyW || keys.ArrowUp ? 1 : 0);
    const cy = Math.cos(view.yaw), sy = Math.sin(view.yaw); // 화면 기준 방향키 → 땅 위 방향
    const kx = Math.round((ix * cy + iz * sy) * 100) / 100, kz = Math.round((iz * cy - ix * sy) * 100) / 100;
    if (me.sit && (kx || kz || me.target)) standUp(); // 움직이려 하면 일어남
    if (kx || kz) {
      const l = Math.hypot(kx, kz); step(me, kx / l * SPEED * me.run * dt, kz / l * SPEED * me.run * dt);
      me.face = Math.atan2(kx, kz); me.moving = true; me.target = null; marker.visible = false;
    } else if (me.target) {
      const r = moveToward(me, me.target.x, me.target.z, dt);
      if (r === 'stuck') me.target.stuck += dt;
      if (r === true || me.target.stuck > 0.6) { me.target = null; marker.visible = false; }
    }
    netTick(kx, kz, now);
    drawMap();
    // 친구들: 쉬다가 아무 데나 걸어감
    actors.forEach(a => {
      if (a.me) return;
      a.moving = false;
      if (a.npc) { if (a.wave <= 0 && Math.hypot(me.x - a.x, me.z - a.z) < 3.5) a.face = Math.atan2(me.x - a.x, me.z - a.z); return; } // 점원: 제자리, 다가오면 바라봄
      if (a.remote) { // 접속한 친구: 받은 목적지까지 같은 속도로 걸어감
        if (!a.sit && a.target) { const r = moveToward(a, a.target.x, a.target.z, dt); if (r === 'stuck') a.target.stuck += dt; if (r === true || a.target.stuck > 0.6) a.target = null; }
        return;
      }
      if (a.wait <= 0 && a.wave <= 0 && !(a.greetCd > t)) { // 친구끼리 마주치면 서로 인사
        const b = actors.find(o => !o.me && !o.remote && !o.npc && o !== a && o.wave <= 0 && !(o.greetCd > t) && Math.hypot(o.x - a.x, o.z - a.z) < 1.5);
        if (b) [[a, b], [b, a]].forEach(([p1, p2]) => { p1.wave = 1.4; p1.wait = 1.7; p1.target = null; p1.lookAt = p2; p1.greetCd = t + 14; });
      }
      if (a.wait > 0) { a.wait -= dt; if (a.lookAt && a.wave > 0) a.face = Math.atan2(a.lookAt.x - a.x, a.lookAt.z - a.z); return; }
      if (!a.target) a.target = { x: (rnd() - 0.5) * 22, z: -4 + rnd() * 16, stuck: 0 };
      const r = moveToward(a, a.target.x, a.target.z, dt);
      if (r === 'stuck') a.target.stuck += dt;
      if (r === true || a.target.stuck > 0.5) { a.target = null; a.wait = 1 + rnd() * 3.5; }
    });

    // 나무: 흔들림, 열매
    trees.forEach(tr => {
      const rot = tr.shake > 0 ? Math.sin(t * 34) * 0.07 * tr.shake / 0.7 : 0;
      if (tr.shake > 0) tr.shake = Math.max(0, tr.shake - dt);
      if (rot !== tr.top.rotation.z) { tr.top.rotation.z = rot; placeTree(tr); }
      tr.fruits.forEach(f => {
        const u = f.userData;
        if (u.state === 'fall') { u.vy -= 14 * dt; f.position.y += u.vy * dt; if (f.position.y < -1.05 + 0.19) { f.position.y = -0.86; u.state = 'ground'; u.timer = 1.1; } }
        else if (u.state === 'ground') { u.timer -= dt; if (u.timer <= 0) { u.state = 'gone'; f.visible = false; fruitN++; $('fruitN').textContent = fruitN; popText('+1 🍎', tr.x, 1.3, tr.z); me.hop = 0.4; sfx.pick(); } }
      });
      if (tr.regrow > 0) { tr.regrow -= dt; if (tr.regrow <= 0) tr.fruits.forEach(f => { f.userData.state = 'on'; f.visible = true; f.position.set(...f.userData.home); }); }
    });
    // 꽃잎: 내 둘레에서 계속 흩날림
    petals.forEach((p, i) => {
      p.y -= p.v * dt; p.x += Math.sin(t * 1.3 + p.p) * 0.5 * dt + 0.25 * dt; p.z += Math.cos(t * 1.1 + p.p) * 0.3 * dt;
      if (p.y < 0.03 || p.z > me.z + 4.5) { p.y = 2.4 + rnd() * 1.8; p.x = me.x + (rnd() - 0.5) * 26; p.z = me.z + 3 - rnd() * 20; }
      if (p.x - me.x > 14) p.x -= 28; else if (p.x - me.x < -14) p.x += 28;
      dummy.position.set(p.x, p.y, p.z); dummy.rotation.set(t * 2 + p.p, t * 1.4 + p.p * 2, p.p); dummy.scale.setScalar(1); dummy.updateMatrix(); petalIM.setMatrixAt(i, dummy.matrix);
    });
    petalIM.instanceMatrix.needsUpdate = true;
    curve.uTime.value = t;
    butterflies.forEach(b => {
      const a = t * b.sp + b.ph;
      b.g.position.set(b.hx + Math.cos(a) * b.r, 0.75 + Math.sin(t * 2.3 + b.ph) * 0.22, b.hz + Math.sin(a * 1.3) * b.r);
      b.g.rotation.y = -a; const flap = 0.25 + Math.abs(Math.sin(t * 16 + b.ph)) * 1.05;
      b.wings[0].rotation.z = flap; b.wings[1].rotation.z = -flap;
    });
    if (me.moving && t - puffAt > 0.2 / me.run) { puffAt = t; const pf = puffs[puffI++ % puffs.length]; pf.life = 0.5; pf.m.visible = true; pf.m.position.set(me.x - Math.sin(me.face) * 0.15, 0.1, me.z - Math.cos(me.face) * 0.15); }
    puffs.forEach(pf => { if (pf.life <= 0) return; pf.life -= dt; const k = Math.max(0, pf.life / 0.5); pf.m.material.opacity = k * 0.7; pf.m.scale.setScalar(0.6 + (1 - k) * 1.2); pf.m.position.y += dt * 0.25; if (pf.life <= 0) pf.m.visible = false; });
    lilies.forEach(q => { q.g.position.y = 0.064 + Math.sin(t * 1.4 + q.ph) * 0.006; q.g.rotation.y += Math.sin(t * 0.6 + q.ph) * 0.002; });
    sparks.forEach((q, i) => { const k = Math.pow(Math.max(0, Math.sin(t * q.sp + q.ph)), 6); dummy.position.set(q.x, 0.075, q.z); dummy.rotation.set(-Math.PI / 2, 0, 0); dummy.scale.setScalar(k * 1.3 + 0.0001); dummy.updateMatrix(); sparkIM.setMatrixAt(i, dummy.matrix); });
    sparkIM.instanceMatrix.needsUpdate = true;
    for (let i = 0; i < SMOKE; i++) { const hs = houses[Math.floor(i / 3)], u = (t * 0.28 + (i % 3) / 3 + hs.x * 0.13) % 1, k = hs.show > 0.5 ? Math.sin(u * Math.PI) * (0.6 + u * 0.9) : 0;
      dummy.position.set(hs.x + 0.9 + u * 0.7 + Math.sin(u * 6 + i) * 0.08, 3.9 + u * 1.9, hs.z - 0.3); dummy.rotation.set(0, 0, 0); dummy.scale.setScalar(k + 0.0001); dummy.updateMatrix(); smokeIM.setMatrixAt(i, dummy.matrix); }
    smokeIM.instanceMatrix.needsUpdate = true;
    for (let i = 0; i < DROPS; i++) { const a = i / DROPS * 6.283 + 0.3, u = (t * 0.85 + i * 0.37) % 1, r = 0.15 + u * 0.75;
      dummy.position.set(Math.cos(a) * r, 1.62 + u * 0.75 - u * u * 1.85, Math.sin(a) * r); dummy.rotation.set(0, 0, 0); dummy.scale.setScalar(1 - u * 0.4); dummy.updateMatrix(); dropIM.setMatrixAt(i, dummy.matrix); }
    dropIM.instanceMatrix.needsUpdate = true;
    shades.forEach((q, i) => { q.x += q.v * dt; if (q.x > 46) q.x = -46; dummy.position.set(q.x, 0.07, q.z); dummy.rotation.set(-Math.PI / 2, 0, 0); dummy.scale.set(q.r * 1.5, q.r, 1); dummy.updateMatrix(); shadeIM.setMatrixAt(i, dummy.matrix); });
    shadeIM.instanceMatrix.needsUpdate = true; cloudShadeMat.opacity = 0.14 * (1 - env.night);
    spout.scale.setScalar(1 + Math.sin(t * 6) * 0.12);
    ripples.forEach((m, i) => { const u = (t * 0.45 + i / 3) % 1; m.scale.setScalar(0.6 + u * 5); m.material.opacity = 0.55 * (1 - u); });
    rides.forEach(q => { if (q.tick) q.tick(t, dt, actors.some(a => a.sit === q)); });
    waterTex.offset.x = -t * 0.12; seaTex.offset.set(t * 0.02, -t * 0.05);
    foam.position.z = BEACH.z1 + 0.75 + Math.sin(t * 0.9) * 0.35; foam.material.opacity = 0.55 + Math.sin(t * 0.9 + 1) * 0.3;
    marker.rotation.z = t * 2;
    clouds.position.set(me.x - Math.sin(view.yaw) * 44 + Math.sin(t * 0.02) * 10, 0, me.z - Math.cos(view.yaw) * 44); clouds.rotation.y = view.yaw;

    // 해·카메라: 비스듬히 내려다보며 따라감
    if (!demo) { const d = new Date(), hr = d.getHours() + d.getMinutes() / 60; env.key = hr < 5.5 || hr >= 19.5 ? 'night' : hr < 7 || hr >= 17.5 ? 'sunset' : 'day'; }
    { const T = TIMES[env.key], k = Math.min(1, dt * 1.6);
      hemi.color.lerp(T.hemiSky, k); hemi.groundColor.lerp(T.hemiGround, k); hemi.intensity += (T.hemiI - hemi.intensity) * k;
      sun.color.lerp(T.sunC, k); sun.intensity += (T.sunI - sun.intensity) * k; env.sunPos.lerp(T.sunPos, k);
      env.sky.forEach((c, i) => c.lerp(T.sky[i], k)); paintSky(env.sky[0], env.sky[1], env.sky[2]);
      scene.fog.color.lerp(T.fog, k); env.unlit.lerp(T.unlit, k); env.night += (T.night - env.night) * k;
      unlitMats.forEach(u => u.m.color.copy(u.base).multiply(env.unlit));
      const n = env.night;
      winMat.color.copy(DAY_WIN).lerp(NIGHT_WIN, n); lampMat.color.setRGB(0.55 + 0.45 * n, 0.55 + 0.42 * n, 0.5 + 0.2 * n);
      glowMat.opacity = n * 0.5; haloMat.opacity = Math.max(0, n - 0.15) * 0.8; if ((n > 0.15) !== halosOn) { halosOn = n > 0.15; halos.forEach(m => { m.visible = halosOn; }); } starMat.opacity = Math.max(0, n - 0.35) * 1.5; flyMat.opacity = Math.max(0, n - 0.2) * 1.2;
      butterflies.forEach(b => { b.g.visible = n < 0.6; });
    }
    fireflies.forEach(f => { f.m.visible = env.night > 0.22; if (f.m.visible) { f.m.position.set(f.x + Math.sin(t * 0.5 + f.ph) * 1.4, 0.55 + Math.sin(t * 1.3 + f.ph * 2) * 0.35, f.z + Math.cos(t * 0.4 + f.ph) * 1.4); f.m.scale.setScalar(0.7 + Math.abs(Math.sin(t * 2.4 + f.ph)) * 0.9); } });
    fishes.forEach(f => { f.x += f.v * dt; if (f.x > 35) f.x = -35; else if (f.x < -35) f.x = 35; f.g.position.set(f.x, 0.062, riverZ(f.x) + f.off + Math.sin(t * 0.9 + f.ph) * 0.25); f.g.scale.set(f.s * Math.sign(f.v), f.s, 1); f.tail.rotation.z = Math.PI + Math.sin(t * 9 + f.ph) * 0.5; });
    stars.position.set(me.x, 0, me.z);
    { const fx = me.x - Math.sin(view.yaw) * 3, fz = me.z - Math.cos(view.yaw) * 3; sun.target.position.set(fx, 0, fz); sun.position.set(fx + env.sunPos.x, env.sunPos.y, fz + 3 + env.sunPos.z); } // 그림자 범위는 보는 쪽 앞을 중심으로
    curve.uCurve.value += ((curveOn ? 0.0075 : 0) - curve.uCurve.value) * Math.min(1, dt * 5);
    if (me.z > SHOP.far) { view.yaw = 0; view.pitch = Math.max(0.35, view.pitch); }
    { const off = Math.abs(Math.atan2(Math.sin(view.yaw), Math.cos(view.yaw))) > 0.02 || Math.abs(view.pitch - 0.567) > 0.02; if (String(off) !== viewBtn.dataset.on) { viewBtn.dataset.on = off; viewBtn.style.display = off ? '' : 'none'; } }
    { const sy = Math.sin(view.yaw), cy = Math.cos(view.yaw), el = Math.max(0.1, view.pitch), D = 10.43 * zoom;
      curve.uFocus.value.set(me.x, me.z); curve.uDir.value.set(-sy, -cy);
      camPos.set(me.x + sy * D * Math.cos(el), Math.max(0.7, D * Math.sin(el)), me.z + cy * D * Math.cos(el));
      // 카메라 자리 자체가 건물 속일 때만 밖으로 나올 만큼 당겨 옴 (지붕 위로 지나가는 건 그대로 둠), 당기고 놓는 건 부드럽게
      const inside = f => { const x = me.x + (camPos.x - me.x) * f, z = me.z + (camPos.z - me.z) * f, y = 0.95 + (camPos.y - 0.95) * f; return solids.some(o => o.h > y && Math.hypot(x - o.x, z - o.z) < o.r + 0.3); };
      let k = 1; while (k > 0.15 && inside(k)) k -= 0.05;
      view.k = (view.k || 1) + (k - (view.k || 1)) * Math.min(1, dt * (k < (view.k || 1) ? 10 : 3));
      if (view.k < 0.999) camPos.set(me.x + (camPos.x - me.x) * view.k, 0.95 + (camPos.y - 0.95) * view.k, me.z + (camPos.z - me.z) * view.k);
      camera.position.lerp(camPos, camera.position.lengthSq() < 1 ? 1 : Math.min(1, dt * 8));
      camera.lookAt(me.x, 0.95 + Math.max(0, 0.1 - view.pitch) * 5 * zoom, me.z); } // 0.1보다 더 올리면 바라보는 점이 하늘로 올라감

    // 캐릭터 모습·이름표
    actors.forEach(a => {
      if (a.hop > 0) a.hop -= dt;
      if (a.sit !== a.sitWas) { a.sitWas = a.sit; a.sitAt = t; } // 미끄럼틀처럼 탄 뒤 지난 시간으로 움직이는 것용
      if (a.sit && a.sit.place) a.sit.place(a, t); // 놀이터 기구
      else if (a.sit) { // 앉은 자리에 붙음
        const q = a.sit; a.g.position.set(q.x, q.y, q.z); a.g.rotation.x = 0; a.face = q.face;
      } else { a.g.rotation.x = 0; a.g.position.set(a.x, (a.hop > 0 ? Math.sin(Math.PI * (1 - a.hop / 0.4)) * 0.38 : 0) + groundY(a.x, a.z), a.z); }
      let d = a.face - a.g.rotation.y; d = Math.atan2(Math.sin(d), Math.cos(d)); a.g.rotation.y += d * Math.min(1, dt * 12);
      if (a.wave > 0) a.wave -= dt;
      if (a.sayT > 0) a.sayT -= dt;
      const label = a.sayT > 0 ? a.say : a.name + (a.wave > 0 ? ' 👋' : '');
      if (label !== a.label) { a.label = label; a.tag.textContent = label; a.tag.classList.toggle('say', a.sayT > 0); }
      a.pet.update(t, { moving: a.moving, wave: a.wave > 0.02, sit: Boolean(a.sit) && !a.sit.stand });
      const dz = bendDist(a.x, a.z);
      v.set(a.g.position.x, a.g.position.y + (a.sit ? 1.1 : 1.24) * (a.pet.height || 1) - curve.uCurve.value * dz * dz, a.g.position.z).project(camera);
      const on = v.z < 1 && Math.abs(v.x) < 1.1 && Math.abs(v.y) < 1.1;
      a.tag.style.display = on ? '' : 'none';
      if (!a.me) a.tag.style.opacity = a.sayT > 0 ? 1 : Math.max(0, Math.min(1, 1 - (Math.hypot(a.x - me.x, a.z - me.z) - 10) / 6)).toFixed(2); // 멀리 있는 친구 이름표는 흐리게
      if (on) a.tag.style.transform = `translate(-50%, -100%) translate(${((v.x + 1) / 2 * w).toFixed(1)}px, ${((1 - v.y) / 2 * h).toFixed(1)}px)`;
    });
    { const c = nearby(), label = c ? c.label : ''; // 할 수 있는 일 안내
      if (label !== prompt.dataset.l) { prompt.dataset.l = label; prompt.innerHTML = label ? '<kbd>E</kbd>' + label : ''; prompt.style.display = label ? 'block' : 'none'; shakeBtn.textContent = label || '🌳 흔들기'; shakeBtn.style.opacity = label ? 1 : 0.5; }
      if (label) { v.set(me.g.position.x, me.g.position.y + (me.sit ? 1.1 : 1.24) * (me.pet.height || 1), me.g.position.z).project(camera); v.y += 64 / h; /* 이름표 바로 위 */  prompt.style.transform = `translate(-50%, -100%) translate(${((v.x + 1) / 2 * w).toFixed(1)}px, ${((1 - v.y) / 2 * h).toFixed(1)}px)`; } }
    renderer.render(scene, camera);
    if (running) requestAnimationFrame(frame);
  }

  // ── 바깥에서 쓰는 손잡이: 멈춤(탭을 떠날 때)·다시 시작·치우기
  const api = {
    host, frame,
    pause() { autoPaused = false; if (!running) return; running = false; Object.keys(keys).forEach(k => { keys[k] = false; }); netLeave(); },
    resume() { if (running) return; running = true; prev = performance.now(); netJoin(); requestAnimationFrame(frame); },
    dispose() { api.pause(); window.removeEventListener('keydown', onKeyDown); window.removeEventListener('keyup', onKeyUp); try { renderer.dispose(); renderer.forceContextLoss(); } catch (e) {} root.innerHTML = ''; root.classList.remove('vlg', 'vlg-full'); },
    debug: { me, actors, trees, houses, env, envOutlines, quality, nearby, interact, emote, seats, keys, wave, shake, net, renderer, camera, get fruitN() { return fruitN; } },
  };
  { const fb = $('fullBtn'); if (fb) fb.onclick = () => { root.classList.toggle('vlg-full'); fb.textContent = root.classList.contains('vlg-full') ? '🗗 작게' : '⛶ 크게'; }; }
  if (!demo) root.querySelectorAll('[data-demo]').forEach(e => { e.style.display = 'none'; });
  updateCount(); netJoin();
  requestAnimationFrame(frame);
  return api;
  }

  window.Village = { start };
})();

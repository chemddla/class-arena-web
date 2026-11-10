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
  .vlg .vlg-acts { position: absolute; right: 12px; bottom: 14px; display: flex; gap: 8px; }
  .vlg .vlg-acts button { font-size: 15px; padding: 12px 16px; }
  .vlg .vlg-hint { position: absolute; left: 12px; bottom: 14px; font-size: 12px; font-weight: 700; background: rgba(255, 255, 255, .8); padding: 6px 10px; border-radius: 10px; max-width: 55%; }
  @media (max-width: 640px) { .vlg .vlg-hint { display: none; } }`;
  const HTML = `
  <canvas class="vlg-gl" data-v="gl"></canvas>
  <div class="vlg-labels" data-v="labels"><div class="vlg-prompt" data-v="prompt"></div></div>
  <div class="vlg-hud">
    <span class="pill">🏡 우리 반 마을 <span data-v="count"></span></span>
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
  <div class="vlg-hint">이동: WASD·방향키 또는 땅 누르기 · 인사: Space · 하기: E · 감정: 1·2 · 확대: 마우스 휠</div>
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

  // ── 둥글게 말리는 땅: 내 캐릭터에서 앞뒤(z)로 멀어질수록 아래로 내려감. 그림자는 휘기 전 위치로 계산되므로 그대로 맞음
  const curve = { uCurve: { value: 0.0075 }, uFocusZ: { value: 0 }, uTime: { value: 0 } };
  function bend(m, sway, outline) {
    m.onBeforeCompile = sh => {
      sh.uniforms.uCurve = curve.uCurve; sh.uniforms.uFocusZ = curve.uFocusZ; sh.uniforms.uTime = curve.uTime;
      sh.vertexShader = (sway ? '#define SWAY ' + sway.toFixed(4) + '\n' : '') + (outline ? '#define OUTLINE ' + outline.toFixed(4) + '\n' : '') + 'uniform float uCurve;\nuniform float uFocusZ;\nuniform float uTime;\n' + sh.vertexShader.replace('#include <project_vertex>', `
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
        float dzB = wpB.z - uFocusZ;
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
  const STREETS = [{ z: 0, len: 66 }, { z: 11.6, len: 66 }, { z: 20.6, len: 64 }, { z: 29.6, len: 32 }]; // 동서로 난 골목
  const onPath = (x, z, m) => Math.abs(x) < m || STREETS.some(st => Math.abs(z - st.z) < m && Math.abs(x) < st.len / 2 + m);
  const strip = (x, z, w, d, c, y) => { const m = floor(mesh(new THREE.PlaneGeometry(w, d, Math.max(1, Math.round(w)), Math.max(1, Math.round(d))), c)); m.rotation.x = -Math.PI / 2; scene.add(at(m, x, y, z)); return m; };
  const sandMat = (rx, ry) => { const t = sandTex.clone(); t.needsUpdate = true; t.repeat.set(rx, ry); return toonMat({ map: t }); };
  strip(0, 6, 2.46, 52.26, '#d6bd7e', 0.022); STREETS.forEach((st, i) => strip(0, st.z, st.len + 0.26, 2.46, '#d6bd7e', 0.023 + i * 0.0005)); // 길 테두리
  strip(0, 6, 2.2, 52, sandMat(1, 24), 0.03); STREETS.forEach((st, i) => strip(0, st.z, st.len, 2.2, sandMat(Math.round(st.len / 2.2), 1), 0.031 + i * 0.0005));
  { const rim = floor(mesh(new THREE.RingGeometry(0, 4.55, 48, 5), '#d6bd7e')); rim.rotation.x = -Math.PI / 2; scene.add(at(rim, 0, 0.038, 0)); }
  const plaza = floor(mesh(new THREE.RingGeometry(0, 4.4, 48, 5), '#f5e7bd')); plaza.rotation.x = -Math.PI / 2; scene.add(at(plaza, 0, 0.045, 0));
  const RIVER = { z0: -9.3, z1: -6.3, bridge: 1.15 };
  strip(0, -7.8, 150, 3.8, '#ead9a0', 0.035);
  waterTex.repeat.set(41, 1); strip(0, -7.8, 150, 3, flat(0xffffff, { map: waterTex }), 0.05);
  [-1, 1].forEach(s => { noShadow(strip(0, -7.8 + s * 1.45, 150, 0.14, flat(0xe9f8ff), 0.055)).userData.floor = false; }); // 물가 흰 띠
  const bridge = new THREE.Group();
  for (let i = 0; i < 8; i++) bridge.add(at(mesh(new THREE.BoxGeometry(2.4, 0.12, 0.44), i % 2 ? '#c58f5c' : '#b47d4c'), 0, 0.16 + Math.sin(i / 7 * Math.PI) * 0.22, -1.75 + i * 0.5));
  [-1, 1].forEach(s => { [-1.7, 0, 1.7].forEach(z => bridge.add(at(mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.75, 8), '#8a5a34'), s * 1.15, 0.55, z))); bridge.add(at(mesh(new THREE.BoxGeometry(0.09, 0.09, 3.6), '#8a5a34'), s * 1.15, 0.86, 0)); });
  scene.add(at(bridge, 0, 0, -7.8));

  // ── 부딪히는 것(원) 목록
  const solids = [];
  const solid = (x, z, r) => solids.push({ x, z, r });

  // ── 분수·게시판
  const fountain = new THREE.Group();
  fountain.add(at(mesh(new THREE.CylinderGeometry(1.3, 1.4, 0.45, 48), '#e3ddd0'), 0, 0.225, 0));
  fountain.add(at(noShadow(mesh(new THREE.CylinderGeometry(1.08, 1.08, 0.06, 48), flat(0x7fd0f0))), 0, 0.45, 0));
  fountain.add(at(mesh(new THREE.CylinderGeometry(0.16, 0.22, 1.1, 12), '#e3ddd0'), 0, 0.9, 0));
  fountain.add(at(mesh(new THREE.CylinderGeometry(0.5, 0.2, 0.16, 18), '#e3ddd0'), 0, 1.4, 0));
  const spout = at(noShadow(mesh(new THREE.SphereGeometry(0.2, 12, 10), flat(0xd4f2ff))), 0, 1.62, 0); fountain.add(spout);
  scene.add(fountain); solid(0, 0, 1.5);
  const board = new THREE.Group();
  [-0.7, 0.7].forEach(x => board.add(at(mesh(new THREE.CylinderGeometry(0.07, 0.07, 1.5, 8), '#8a5a34'), x, 0.75, 0)));
  board.add(at(mesh(new THREE.BoxGeometry(1.7, 1, 0.1), '#d19c62'), 0, 1.1, 0));
  [['#fff7d6', -0.45, 1.2], ['#ffd6de', 0.1, 1.05], ['#d6f0ff', 0.5, 1.25]].forEach(p => board.add(at(mesh(new THREE.BoxGeometry(0.4, 0.45, 0.02), p[0]), p[1], p[2], 0.06)));
  const boardRoof = at(mesh(new THREE.ConeGeometry(1.15, 0.35, 4), '#e0685a'), 0, 1.78, 0); boardRoof.scale.z = 0.28; boardRoof.rotation.y = Math.PI / 4; board.add(boardRoof);
  scene.add(at(board, 3.1, 0, -3.1)); board.rotation.y = -0.5; solid(3.1, -3.1, 0.8);

  // ── 집
  // 집터 32곳: 광장에서 가까운 순서. 학생 명단 순서대로 한 채씩 (남는 집은 빈 집)
  const ROOFS = ['#e0685a', '#5b8fd8', '#e8a13a', '#4fae6a', '#b06fc8', '#3fb0a8', '#e07a9a', '#7a8fd8'], WALLS = ['#fff1dc', '#f4f0ff', '#fff6cf', '#eaf7e4', '#ffe9ee'];
  const HOUSES = [], lot = (x, z) => HOUSES.push([x, z, WALLS[HOUSES.length % 5], ROOFS[HOUSES.length % 8]]);
  [10, 15.5, 21, 26.5].forEach(x => { lot(-x, -2.5); lot(x, -2.5); });
  [7.5, 13, 18.5, 24, 29.5].forEach(x => { lot(-x, 8); lot(x, 8); });
  [6, 11.5, 17, 22.5, 28].forEach(x => { lot(-x, 17); lot(x, 17); });
  [6, 11.5].forEach(x => { lot(-x, 26); lot(x, 26); });
  const texMat = (tex, hex) => toonMat({ map: tex, color: new THREE.Color(hex) });
  const barkMat = texMat(barkTex, '#a8744f');
  const haloMat = bend(new THREE.MeshBasicMaterial({ color: 0xffcf70, map: softTex, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending }));
  const halos = [];
  const halo = (size, x, y, z) => { const m = noShadow(new THREE.Mesh(new THREE.PlaneGeometry(size, size), haloMat)); m.rotation.x = -0.5; m.visible = false; halos.push(m); return at(m, x, y, z); };
  const houses = [];
  HOUSES.forEach(([x, z, wall, roof]) => {
    const g = new THREE.Group();
    g.add(at(mesh(new THREE.BoxGeometry(3.2, 2, 2.6), texMat(wallTex, wall)), 0, 1, 0));
    const rf = at(mesh(new THREE.ConeGeometry(2.75, 1.6, 4), texMat(roofTex, roof)), 0, 2.78, 0); rf.rotation.y = Math.PI / 4; rf.scale.z = 0.86; g.add(rf);
    g.add(at(mesh(new THREE.BoxGeometry(3.4, 0.14, 2.8), roof), 0, 2.02, 0));
    g.add(at(mesh(new THREE.BoxGeometry(0.4, 0.9, 0.4), '#d3c9ba'), 0.9, 2.9, -0.3));
    g.add(at(mesh(new THREE.BoxGeometry(0.78, 1.25, 0.1), '#a06a3c'), 0, 0.63, 1.31));
    g.add(at(mesh(new THREE.SphereGeometry(0.06, 8, 6), '#f2c53a'), 0.24, 0.62, 1.38));
    [-1, 1].forEach(s => { g.add(at(mesh(new THREE.BoxGeometry(0.74, 0.74, 0.06), '#ffffff'), s * 1.05, 1.2, 1.3)); g.add(at(noShadow(mesh(new THREE.BoxGeometry(0.58, 0.58, 0.08), winMat)), s * 1.05, 1.2, 1.31)); g.add(at(mesh(new THREE.BoxGeometry(0.06, 0.6, 0.1), '#ffffff'), s * 1.05, 1.2, 1.32)); });
    g.add(at(mesh(new THREE.BoxGeometry(1.1, 0.1, 0.6), '#d3c9ba'), 0, 0.05, 1.6));
    [-1, 1].forEach(s => g.add(halo(1.7, s * 1.05, 1.2, 1.5)));
    const arch = at(mesh(new THREE.CylinderGeometry(0.39, 0.39, 0.1, 16), '#a06a3c'), 0, 1.25, 1.31); arch.rotation.x = Math.PI / 2; g.add(arch);
    const port = at(noShadow(mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.12, 12), winMat)), 0, 1.22, 1.33); port.rotation.x = Math.PI / 2; g.add(port);
    [-1, 1].forEach(s => { g.add(at(mesh(new THREE.BoxGeometry(0.8, 0.16, 0.2), '#b9824e'), s * 1.05, 0.76, 1.4)); [-0.25, 0, 0.25].forEach((dx, k) => g.add(at(mesh(new THREE.SphereGeometry(0.09, 7, 6), ['#ff7fa6', '#ffcf3a', '#fff6e8'][(k + (s > 0 ? 1 : 0)) % 3]), s * 1.05 + dx, 0.89, 1.42))); });
    scene.add(at(mesh(new THREE.BoxGeometry(3.3, 0.24, 2.7), '#d9cfbf'), x, 0.12, z)); // 바닥 띠는 집이 숨어도 남아 자리를 알려 줌
    g.add(at(mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.8, 8), '#8a5a34'), 2.1, 0.4, 1.5)); // 우체통
    g.add(at(mesh(new THREE.BoxGeometry(0.34, 0.3, 0.5), roof), 2.1, 0.92, 1.5));
    houses.push({ x, z, g, show: 1 });
    scene.add(at(g, x, 0, z)); solid(x - 0.75, z, 1.55); solid(x + 0.75, z, 1.55); solid(x + 2.1, z + 1.5, 0.3);
  });

  // ── 마을사무소: 큰길 북쪽 끝, 광장을 바라봄
  { const g = new THREE.Group(), OZ = -23;
    g.add(at(mesh(new THREE.BoxGeometry(7, 0.3, 4.2), '#d9cfbf'), 0, 0.15, 0));
    g.add(at(mesh(new THREE.BoxGeometry(6.4, 3, 3.6), texMat(wallTex, '#fff6e6')), 0, 1.8, 0));
    const rf = at(mesh(new THREE.ConeGeometry(4.9, 1.9, 4), texMat(roofTex, '#3f7fc8')), 0, 4.25, 0); rf.rotation.y = Math.PI / 4; rf.scale.z = 0.62; g.add(rf);
    g.add(at(mesh(new THREE.BoxGeometry(6.7, 0.16, 3.9), '#3f7fc8'), 0, 3.32, 0));
    g.add(at(mesh(new THREE.BoxGeometry(1.1, 1.5, 1.1), '#fff6e6'), 0, 5.1, 0)); // 시계탑
    const cap = at(mesh(new THREE.ConeGeometry(0.95, 0.9, 4), '#3f7fc8'), 0, 6.3, 0); cap.rotation.y = Math.PI / 4; g.add(cap);
    const clock = at(mesh(new THREE.CylinderGeometry(0.38, 0.38, 0.06, 24), '#ffffff'), 0, 5.15, 0.56); clock.rotation.x = Math.PI / 2; g.add(clock);
    g.add(at(mesh(new THREE.BoxGeometry(0.05, 0.28, 0.04), '#334155'), 0, 5.25, 0.6)); g.add(at(mesh(new THREE.BoxGeometry(0.22, 0.05, 0.04), '#334155'), 0.09, 5.15, 0.6));
    const sc = document.createElement('canvas'); sc.width = 256; sc.height = 64; const sg = sc.getContext('2d');
    sg.fillStyle = '#2f5f9e'; sg.fillRect(0, 0, 256, 64); sg.fillStyle = '#fff'; sg.font = "800 36px 'Malgun Gothic', sans-serif"; sg.textAlign = 'center'; sg.textBaseline = 'middle'; sg.fillText('마을사무소', 128, 34);
    g.add(at(noShadow(mesh(new THREE.PlaneGeometry(2.6, 0.65), flat(0xffffff, { map: new THREE.CanvasTexture(sc) }))), 0, 2.85, 1.82));
    [-0.36, 0.36].forEach(x => g.add(at(mesh(new THREE.BoxGeometry(0.68, 1.6, 0.1), '#a06a3c'), x, 1.1, 1.81)));
    [-0.12, 0.12].forEach(x => g.add(at(mesh(new THREE.SphereGeometry(0.06, 8, 6), '#f2c53a'), x, 1.1, 1.88)));
    [-1.15, 1.15].forEach(x => g.add(at(mesh(new THREE.CylinderGeometry(0.11, 0.11, 2.2, 10), '#ffffff'), x, 1.4, 2.15))); // 현관 기둥과 차양
    g.add(at(mesh(new THREE.BoxGeometry(2.8, 0.14, 0.9), '#3f7fc8'), 0, 2.5, 2.1));
    g.add(at(mesh(new THREE.BoxGeometry(2.6, 0.12, 0.9), '#d3c9ba'), 0, 0.36, 2.15));
    [-2.25, -1.55, 1.55, 2.25].forEach(x => { g.add(at(mesh(new THREE.BoxGeometry(0.62, 0.8, 0.06), '#ffffff'), x, 1.35, 1.8)); g.add(at(noShadow(mesh(new THREE.BoxGeometry(0.48, 0.66, 0.08), winMat)), x, 1.35, 1.81)); g.add(halo(1.6, x, 1.35, 2)); });
    [-1.9, 0, 1.9].forEach(x => { if (x) { g.add(at(mesh(new THREE.BoxGeometry(0.9, 0.62, 0.06), '#ffffff'), x, 2.75, 1.8)); g.add(at(noShadow(mesh(new THREE.BoxGeometry(0.76, 0.48, 0.08), winMat)), x, 2.75, 1.81)); } });
    g.add(at(mesh(new THREE.CylinderGeometry(0.05, 0.05, 4.2, 8), '#cbd5e1'), 3.9, 2.1, 1.4)); // 깃발
    g.add(at(mesh(new THREE.BoxGeometry(1, 0.62, 0.03), '#ffd24a'), 4.42, 3.82, 1.4));
    scene.add(at(g, 0, 0, OZ)); [-2.2, 0, 2.2].forEach(x => solid(x, OZ, 1.9)); solid(3.9, OZ + 1.4, 0.2);
  }
  // ── 소품: 통나무 탁자, 줄무늬 의자, 그네
  const stump = (x, z, r, h) => { const g = new THREE.Group(); g.add(at(mesh(new THREE.CylinderGeometry(r, r * 1.08, h, 40), '#b9824e'), 0, h / 2, 0)); g.add(at(mesh(new THREE.CylinderGeometry(r * 0.93, r * 0.93, 0.03, 40), '#ecc28c'), 0, h + 0.012, 0)); g.add(at(mesh(new THREE.TorusGeometry(r * 0.5, 0.018, 4, 18), '#d7a66c'), 0, h + 0.03, 0)); g.children[2].rotation.x = Math.PI / 2; scene.add(at(g, x, 0, z)); solid(x, z, r); };
  stump(6.2, 3.6, 0.95, 0.55); stump(7.7, 3.2, 0.36, 0.34); stump(5.2, 4.7, 0.36, 0.34);
  { const g = new THREE.Group(), cols = ['#ff8f8f', '#ffd27a', '#fff3a8', '#9fe0a0', '#8fc8ff', '#c9a8f0'];
    cols.forEach((c, i) => { const p = at(mesh(new THREE.BoxGeometry(0.95, 0.03, 0.21), c), 0, 0.22 + i * 0.105, 0.55 - i * 0.2); p.rotation.x = 0.48; g.add(p); });
    [-1, 1].forEach(s => { const a = at(mesh(new THREE.BoxGeometry(0.06, 0.06, 1.6), '#b9824e'), s * 0.5, 0.48, 0.05); a.rotation.x = 0.48; g.add(a); const b = at(mesh(new THREE.BoxGeometry(0.06, 0.06, 1.1), '#b9824e'), s * 0.5, 0.3, -0.1); b.rotation.x = -0.55; g.add(b); });
    g.rotation.y = 0.5; scene.add(at(g, -5.4, 0, 3.4)); solid(-5.4, 3.4, 0.6); }
  const swingSeat = new THREE.Group();
  { const g = new THREE.Group();
    [-1, 1].forEach(s => g.add(at(mesh(new THREE.CylinderGeometry(0.08, 0.09, 2.6, 8), '#c58f5c'), s * 1.1, 1.3, 0)));
    g.add(at(mesh(new THREE.BoxGeometry(2.5, 0.14, 0.14), '#c58f5c'), 0, 2.6, 0));
    [-1, 1].forEach(s => swingSeat.add(at(mesh(new THREE.CylinderGeometry(0.015, 0.015, 1.8, 4), '#e9dcc0'), s * 0.38, -0.9, 0)));
    swingSeat.add(at(mesh(new THREE.BoxGeometry(0.95, 0.07, 0.32), '#e0685a'), 0, -1.8, 0));
    g.add(at(swingSeat, 0, 2.55, 0)); scene.add(at(g, -4.6, 0, -4.2)); solid(-5.7, -4.2, 0.3); solid(-3.5, -4.2, 0.3); }

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
  const freeSpot = (x, z, pad) => !onPath(x, z, 1.9 + pad) && Math.hypot(x, z) > 6.2 + pad
    && !(z > RIVER.z0 - 1.5 && z < RIVER.z1 + 1.5) && HOUSES.every(h => Math.hypot(x - h[0], z - h[1]) > 4.2 + pad)
    && solids.every(s => Math.hypot(x - s.x, z - s.z) > s.r + 1.6 + pad) && trees.every(t => Math.hypot(x - t.x, z - t.z) > 2.6);
  function placeTree(tr) { // 줄기 묶음의 지금 위치·기울기대로 뭉치들을 옮김
    tr.g.updateMatrixWorld(true);
    tr.blobs.forEach(b => { dummy.position.set(b.x, b.y, b.z); dummy.scale.setScalar(b.r); dummy.rotation.set(b.rot[0], b.rot[1], b.rot[2]); dummy.updateMatrix(); tr.im.setMatrixAt(b.i, mtx.multiplyMatrices(tr.top.matrixWorld, dummy.matrix)); });
    tr.im.instanceMatrix.needsUpdate = true;
  }
  for (let i = 0, tries = 0; i < 36 && tries < 6000; tries++) {
    const x = (rnd() - 0.5) * 68, z = -22 + rnd() * 56;
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
    const tr = { x, z, g, top, fruits, blobs: list, im, kind, shake: 0, regrow: 0, sc, show: 1, shown: 1 };
    placeTree(tr); trees.push(tr); solid(x, z, 0.52 * sc); i++;
  }
  { const bg = [];
    for (let i = 0, tries = 0; i < 60 && tries < 4000; tries++) {
      const x = (rnd() - 0.5) * 112, z = -44 + rnd() * 66;
      if (!(Math.abs(x) > 36.5 || z < -25.5) || (z > RIVER.z0 - 1.6 && z < RIVER.z1 + 1.6) || bg.some(b => Math.hypot(x - b[0], z - b[1]) < 3.4)) continue;
      bg.push([x, z]); i++;
      const sc = 1 + rnd() * 0.5, pinkTree = rnd() < 0.55, im = pinkTree ? blobsPinkFar : blobsLeafFar;
      scene.add(at(mesh(new THREE.CylinderGeometry(0.26 * sc, 0.4 * sc, 1.6 * sc, 12), barkMat), x, 0.8 * sc, z));
      [[0, 2.2, 0, 1.25], [0.9, 1.75, 0.2, 0.85], [-0.9, 1.8, -0.1, 0.85], [0.1, 1.7, 0.9, 0.8], [0, 1.75, -0.9, 0.8], [0.1, 3.0, 0, 0.8]].forEach(b => {
        dummy.position.set(x + b[0] * sc, b[1] * sc, z + b[2] * sc); dummy.scale.setScalar(b[3] * sc); dummy.rotation.set(rnd() * 6, rnd() * 6, rnd() * 6); dummy.updateMatrix(); im.setMatrixAt(addBlob(im, pinkTree ? PINK : LEAF), dummy.matrix); });
    } }
  // 덤불 (같은 뭉치 묶음에 얹음)
  [[-2.6, -5.6], [2.6, -5.6], [-12.8, -3.8], [12.8, -3.8], [-10.4, 6.4], [10.4, 6.4], [-3.2, -10.6], [3.2, -10.6]].forEach(([x, z]) => {
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
  HOUSES.forEach((h, k) => bed(h[0] - 1.05, h[1] + 1.75, 3, 1, 0.5, i => TULIP[(i + k) % 5]));                      // 집 창문 아래
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
    for (let i = 0; i < n; i++) { const x = (rnd() - 0.5) * 70, z = 6 + (rnd() - 0.5) * 60, s = 0.7 + rnd() * 0.9; const off = onPath(x, z, 1.4) || Math.hypot(x, z) < 4.7 || (z > RIVER.z0 - 0.4 && z < RIVER.z1 + 0.4);
      dummy.position.set(x, off ? -5 : 0.08 * s, z); dummy.rotation.set(0, rnd() * 6, (rnd() - 0.5) * 0.4); dummy.scale.setScalar(s); dummy.updateMatrix(); im.setMatrixAt(i, dummy.matrix); im.setColorAt(i, col.set(pick(['#58b84f', '#66c458', '#4aa848']))); }
    im.userData.noShadow = true; scene.add(im); }
  for (let i = 0; i < 9; i++) { const x = (rnd() - 0.5) * 40, z = (rnd() - 0.5) * 40; if (!freeSpot(x, z, -0.6)) continue; const r = 0.35 + rnd() * 0.3; const m = mesh(new THREE.DodecahedronGeometry(r, 0), '#c3c6ca'); m.scale.y = 0.7; scene.add(at(m, x, r * 0.4, z)); solid(x, z, r); }

  // ── 구름 (지평선 쪽에 떠서 천천히 흐름)·날리는 꽃잎
  const clouds = new THREE.Group(); scene.add(clouds);
  for (let i = 0; i < 7; i++) { const g = new THREE.Group(), m = flat(0xffffff, { fog: false }); [[0, 0, 1.6], [1.5, -0.2, 1.1], [-1.5, -0.25, 1.2], [0.6, 0.6, 1.0]].forEach(b => { const s = noShadow(at(new THREE.Mesh(new THREE.SphereGeometry(b[2], 10, 8), m), b[0], b[1], 0)); s.scale.y = 0.6; g.add(s); }); g.scale.setScalar(1.2 + rnd() * 1.3); clouds.add(at(g, -52 + i * 17 + rnd() * 6, 7 + rnd() * 6, -rnd() * 8)); }
  const PETALS = 90, petalIM = noShadow(new THREE.InstancedMesh(new THREE.PlaneGeometry(0.11, 0.075), flat(0xffd0dc, { side: THREE.DoubleSide }), PETALS)); scene.add(petalIM);
  const petals = Array.from({ length: PETALS }, () => ({ x: (rnd() - 0.5) * 26, y: rnd() * 4, z: 7 - rnd() * 20, p: rnd() * 6, v: 0.45 + rnd() * 0.5 }));

  // 가로등: 밤이 되면 등불과 바닥 불빛이 켜짐
  const lampMat = flat(0xfff6d8, { glow: true }), glowMat = flat(0xffd76a, { glow: true, map: softTex, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending });
  [[-2.7, 5.4], [2.7, 5.4], [-1.9, -4.6], [1.9, -4.6], [-6.4, 1.7], [6.4, -1.7], [-13, 1.6], [13, 1.6], [-24, 1.6], [24, 1.6], [-10, 13.1], [10, 13.1], [-21, 13.1], [21, 13.1], [-9, 22.1], [9, 22.1], [-20, 22.1], [20, 22.1]].forEach(([x, z]) => {
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
    return { g, tail, x: (rnd() - 0.5) * 66, z: -7.8 + (rnd() - 0.5) * 1.8, v: (0.5 + rnd() * 0.7) * (rnd() < 0.5 ? -1 : 1), ph: rnd() * 6, s: 0.7 + rnd() * 0.6 }; });
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
    for (let i = 0; i < n; i++) { const x = (rnd() - 0.5) * 70, z = 6 + (rnd() - 0.5) * 60, off = onPath(x, z, 1.5) || Math.hypot(x, z) < 4.8 || (z > RIVER.z0 - 0.4 && z < RIVER.z1 + 0.4), k = 0.7 + rnd() * 0.7;
      dummy.rotation.set(-Math.PI / 2, 0, rnd() * 6); dummy.scale.setScalar(k); dummy.position.set(x, off ? -5 : 0.052, z); dummy.updateMatrix(); petal.setMatrixAt(i, dummy.matrix); petal.setColorAt(i, col.set(pick(['#ffffff', '#ffffff', '#fff3c4', '#ffe1ea'])));
      dummy.position.y = off ? -5 : 0.058; dummy.updateMatrix(); heart.setMatrixAt(i, dummy.matrix); }
    scene.add(petal); scene.add(heart); }
  // ── 연잎: 강물 위에 떠서 살짝 흔들림 (몇 개는 분홍 꽃)
  const lilies = Array.from({ length: 10 }, (_, i) => {
    const g = new THREE.Group(), pad = floor(mesh(new THREE.CircleGeometry(0.34, 16, 0.35, 5.6), i % 2 ? '#4fb85a' : '#63c466')); pad.rotation.x = -Math.PI / 2; g.add(pad);
    if (i % 3 === 0) { g.add(at(mesh(new THREE.SphereGeometry(0.1, 10, 8), '#ff9db8'), 0.05, 0.07, 0)); for (let k = 0; k < 5; k++) { const a = k / 5 * 6.283, pt = mesh(new THREE.SphereGeometry(0.075, 8, 6), '#ffc4d4'); pt.scale.set(1, 0.5, 0.6); pt.rotation.y = -a; g.add(at(pt, 0.05 + Math.cos(a) * 0.1, 0.045, Math.sin(a) * 0.1)); } g.add(at(mesh(new THREE.SphereGeometry(0.04, 8, 6), '#ffd23a'), 0.05, 0.14, 0)); }
    let x = (rnd() - 0.5) * 64; if (Math.abs(x) < 2.2) x += x < 0 ? -3 : 3; // 다리 밑은 비움
    const q = { g, x, z: -7.8 + (rnd() - 0.5) * 2.0, ph: rnd() * 6, s: 0.8 + rnd() * 0.6 }; g.scale.setScalar(q.s); g.rotation.y = rnd() * 6; scene.add(at(g, q.x, 0.064, q.z)); return q;
  });
  // ── 물 반짝임
  const SPARK = 40, sparkIM = noShadow(new THREE.InstancedMesh(new THREE.PlaneGeometry(0.3, 0.3), flat(0xffffff, { map: softTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }), SPARK)); scene.add(sparkIM);
  const sparks = Array.from({ length: SPARK }, () => ({ x: (rnd() - 0.5) * 68, z: -7.8 + (rnd() - 0.5) * 2.5, ph: rnd() * 6, sp: 1.2 + rnd() * 1.6 }));
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
    const stop = new Set([swingSeat].concat(trees.map(t => t.top)));
    const opt = () => ({ stop, vertexMaterial: vcMat, outlineMaterial: vcLine, thickness: 0.022, minSize: 0.15, minSecond: 0.06, accept: m => m.material === winMat || (m.material.isMeshToonMaterial && !m.userData.noShadow && !m.userData.floor) });
    const loose = new THREE.Group(); // 묶음 없이 놓인 것(배경 줄기·바위·집 기단)
    scene.children.slice().forEach(o => { if (o.isMesh && !o.isInstancedMesh && o.material.isMeshToonMaterial && !o.userData.floor && !o.userData.noShadow) loose.add(o); });
    scene.add(loose);
    scene.children.slice().concat([swingSeat]).forEach(o => { if (o.isGroup) VillagePets.merge(THREE, o, opt()).outlines.forEach(ol => envOutlines.push(ol)); });
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
  const ownerOf = i => demo ? actors[i + 1] : host.students[i]; // i번째 집 주인

  // ── 움직임·부딪힘
  const LX = 33, LZ0 = -21, LZ1 = 32, SPEED = 3.3, R = 0.32;
  function step(a, dx, dz) {
    const pz = a.z; let x = a.x + dx, z = a.z + dz;
    solids.forEach(c => { const d = Math.hypot(x - c.x, z - c.z), min = c.r + R; if (d < min && d > 1e-4) { x = c.x + (x - c.x) / d * min; z = c.z + (z - c.z) / d * min; } });
    if (z > RIVER.z0 && z < RIVER.z1) { // 강: 다리 위에서만 건넘
      if (Math.abs(a.x) <= RIVER.bridge && pz > RIVER.z0 - 0.05 && pz < RIVER.z1 + 0.05) x = Math.max(-RIVER.bridge + 0.25, Math.min(RIVER.bridge - 0.25, x));
      else if (Math.abs(x) > RIVER.bridge - 0.25) z = pz >= RIVER.z1 ? RIVER.z1 : pz <= RIVER.z0 ? RIVER.z0 : z;
    }
    a.x = Math.max(-LX, Math.min(LX, x)); a.z = Math.max(LZ0, Math.min(LZ1, z));
  }
  const keys = {};
  const onKeyDown = e => {
    if (!running || /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable) return;
    keys[e.code] = true;
    if (e.code === 'Space') { e.preventDefault(); wave(); }
    if (e.code === 'KeyE') interact();
    if (e.code === 'Digit1') emote('joy');
    if (e.code === 'Digit2') emote('heart');
    if (e.code.startsWith('Arrow')) e.preventDefault();
  };
  const onKeyUp = e => { keys[e.code] = false; };
  window.addEventListener('keydown', onKeyDown); window.addEventListener('keyup', onKeyUp);
  const ray = new THREE.Raycaster(), plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0), hit = new THREE.Vector3();
  canvas.addEventListener('pointerdown', e => {
    const rc = canvas.getBoundingClientRect();
    ray.setFromCamera({ x: (e.clientX - rc.left) / rc.width * 2 - 1, y: -((e.clientY - rc.top) / rc.height) * 2 + 1 }, camera);
    if (!ray.ray.intersectPlane(plane, hit)) return;
    me.target = { x: Math.max(-LX, Math.min(LX, hit.x)), z: Math.max(LZ0, Math.min(LZ1, hit.z)), stuck: 0 };
    marker.position.set(me.target.x, 0.09, me.target.z); marker.visible = true;
  });
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
  // 앉을 자리: y = 앉는 높이, face = 앉아서 보는 쪽, (ox, oz) = 일어날 때 내려서는 곳, swing = 그네
  const seats = [
    { x: 7.7, z: 3.2, y: 0.36, face: Math.atan2(6.2 - 7.7, 3.6 - 3.2), ox: 0.2, oz: 0.8 },
    { x: 5.2, z: 4.7, y: 0.36, face: Math.atan2(6.2 - 5.2, 3.6 - 4.7), ox: -0.3, oz: 0.8 },
    { x: -5.4, z: 3.4, y: 0.42, face: 0.5, ox: 0.5, oz: 1.1 },
    { x: -4.6, z: -4.2, y: 0.78, face: 0, ox: 0, oz: 1.0, swing: true },
  ];
  let swingAmp = 0.12;
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
    if (me.sit) return { kind: 'stand', label: '일어나기' };
    const seat = seats.find(q => Math.hypot(me.x - q.x, me.z - q.z) < 1.3);
    if (seat) return { kind: 'seat', seat, label: seat.swing ? '🎠 그네 타기' : '🪑 앉기' };
    for (let i = 0; i < houses.length; i++) { const h = houses[i]; if (Math.hypot(me.x - h.x, me.z - (h.z + 1.9)) < 1.2) return { kind: 'door', house: h, owner: ownerOf(i), label: !ownerOf(i) ? '🚪 빈 집' : demo ? '🚪 ' + ownerOf(i).name + '네 집 · 똑똑' : ownerOf(i).id === host.me.id ? '🚪 내 방 들어가기' : '🚪 ' + ownerOf(i).name + '네 집 놀러 가기' }; }
    if (Math.hypot(me.x - 3.1, me.z + 3.1) < 2) return { kind: 'board', label: '📋 게시판 보기' };
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
    if (c.kind === 'board') { me.face = Math.atan2(3.1 - me.x, -3.1 - me.z); say(me, '오늘의 공지: 사이좋게 놀기 😊', 2.6); sfx.note(); }
  }
  function popText(text, x, y, z) { // 그 자리 위로 떠오르다 사라지는 글자
    const dz = z - me.z; v.set(x, y - curve.uCurve.value * dz * dz, z).project(camera);
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
    const px = a.x, pz = a.z, s = Math.min(d, SPEED * (a.me ? 1 : a.remote ? (d > 4.5 ? 1.35 : 1) : 0.55) * dt);
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
    if (kx || kz) { const l = Math.hypot(kx, kz); tx = me.x + kx / l * SPEED * 1.1; tz = me.z + kz / l * SPEED * 1.1; } else if (me.target) { tx = me.target.x; tz = me.target.z; }
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
    me.moving = false;
    const kx = (keys.KeyD || keys.ArrowRight ? 1 : 0) - (keys.KeyA || keys.ArrowLeft ? 1 : 0), kz = (keys.KeyS || keys.ArrowDown ? 1 : 0) - (keys.KeyW || keys.ArrowUp ? 1 : 0);
    if (me.sit && (kx || kz || me.target)) standUp(); // 움직이려 하면 일어남
    if (kx || kz) {
      const l = Math.hypot(kx, kz); step(me, kx / l * SPEED * dt, kz / l * SPEED * dt);
      me.face = Math.atan2(kx, kz); me.moving = true; me.target = null; marker.visible = false;
    } else if (me.target) {
      const r = moveToward(me, me.target.x, me.target.z, dt);
      if (r === 'stuck') me.target.stuck += dt;
      if (r === true || me.target.stuck > 0.6) { me.target = null; marker.visible = false; }
    }
    netTick(kx, kz, now);
    // 친구들: 쉬다가 아무 데나 걸어감
    actors.forEach(a => {
      if (a.me) return;
      a.moving = false;
      if (a.remote) { // 접속한 친구: 받은 목적지까지 같은 속도로 걸어감
        if (!a.sit && a.target) { const r = moveToward(a, a.target.x, a.target.z, dt); if (r === 'stuck') a.target.stuck += dt; if (r === true || a.target.stuck > 0.6) a.target = null; }
        return;
      }
      if (a.wait <= 0 && a.wave <= 0 && !(a.greetCd > t)) { // 친구끼리 마주치면 서로 인사
        const b = actors.find(o => !o.me && !o.remote && o !== a && o.wave <= 0 && !(o.greetCd > t) && Math.hypot(o.x - a.x, o.z - a.z) < 1.5);
        if (b) [[a, b], [b, a]].forEach(([p1, p2]) => { p1.wave = 1.4; p1.wait = 1.7; p1.target = null; p1.lookAt = p2; p1.greetCd = t + 14; });
      }
      if (a.wait > 0) { a.wait -= dt; if (a.lookAt && a.wave > 0) a.face = Math.atan2(a.lookAt.x - a.x, a.lookAt.z - a.z); return; }
      if (!a.target) a.target = { x: (rnd() - 0.5) * 22, z: -4 + rnd() * 16, stuck: 0 };
      const r = moveToward(a, a.target.x, a.target.z, dt);
      if (r === 'stuck') a.target.stuck += dt;
      if (r === true || a.target.stuck > 0.5) { a.target = null; a.wait = 1 + rnd() * 3.5; }
    });

    // 나무: 앞을 가리면 숨김, 흔들림, 열매
    trees.forEach(tr => {
      const front = tr.z - me.z, hide = front > 1.0 && front < 12 && Math.abs(tr.x - me.x) < 3.2 + front * 0.25;
      tr.show += ((hide ? 0 : 1) - tr.show) * Math.min(1, dt * 9);
      const rot = tr.shake > 0 ? Math.sin(t * 34) * 0.07 * tr.shake / 0.7 : 0;
      if (tr.shake > 0) tr.shake = Math.max(0, tr.shake - dt);
      if (Math.abs(tr.show - tr.shown) > 0.004 || rot !== tr.top.rotation.z) {
        tr.shown = tr.show; tr.top.rotation.z = rot;
        tr.g.visible = tr.show > 0.03; tr.g.scale.setScalar(tr.sc * Math.max(0.001, tr.show));
        placeTree(tr);
      }
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
    houses.forEach(hs => {
      const front = hs.z - me.z, hide = front > 0.6 && front < 12 && Math.abs(hs.x - me.x) < 3.6 + front * 0.3;
      hs.show += ((hide ? 0 : 1) - hs.show) * Math.min(1, dt * 9);
      hs.g.visible = hs.show > 0.04; hs.g.scale.y = Math.max(0.001, hs.show);
    });
    butterflies.forEach(b => {
      const a = t * b.sp + b.ph;
      b.g.position.set(b.hx + Math.cos(a) * b.r, 0.75 + Math.sin(t * 2.3 + b.ph) * 0.22, b.hz + Math.sin(a * 1.3) * b.r);
      b.g.rotation.y = -a; const flap = 0.25 + Math.abs(Math.sin(t * 16 + b.ph)) * 1.05;
      b.wings[0].rotation.z = flap; b.wings[1].rotation.z = -flap;
    });
    if (me.moving && t - puffAt > 0.2) { puffAt = t; const pf = puffs[puffI++ % puffs.length]; pf.life = 0.5; pf.m.visible = true; pf.m.position.set(me.x - Math.sin(me.face) * 0.15, 0.1, me.z - Math.cos(me.face) * 0.15); }
    puffs.forEach(pf => { if (pf.life <= 0) return; pf.life -= dt; const k = Math.max(0, pf.life / 0.5); pf.m.material.opacity = k * 0.7; pf.m.scale.setScalar(0.6 + (1 - k) * 1.2); pf.m.position.y += dt * 0.25; if (pf.life <= 0) pf.m.visible = false; });
    lilies.forEach(q => { q.g.position.y = 0.064 + Math.sin(t * 1.4 + q.ph) * 0.006; q.g.rotation.y += Math.sin(t * 0.6 + q.ph) * 0.002; });
    sparks.forEach((q, i) => { const k = Math.pow(Math.max(0, Math.sin(t * q.sp + q.ph)), 6); dummy.position.set(q.x, 0.075, q.z); dummy.rotation.set(-Math.PI / 2, 0, 0); dummy.scale.setScalar(k * 1.3 + 0.0001); dummy.updateMatrix(); sparkIM.setMatrixAt(i, dummy.matrix); });
    sparkIM.instanceMatrix.needsUpdate = true;
    for (let i = 0; i < SMOKE; i++) { const hs = houses[Math.floor(i / 3)], u = (t * 0.28 + (i % 3) / 3 + hs.x * 0.13) % 1, k = hs.show > 0.5 ? Math.sin(u * Math.PI) * (0.6 + u * 0.9) : 0;
      dummy.position.set(hs.x + 0.9 + u * 0.7 + Math.sin(u * 6 + i) * 0.08, 3.4 + u * 1.9, hs.z - 0.3); dummy.rotation.set(0, 0, 0); dummy.scale.setScalar(k + 0.0001); dummy.updateMatrix(); smokeIM.setMatrixAt(i, dummy.matrix); }
    smokeIM.instanceMatrix.needsUpdate = true;
    for (let i = 0; i < DROPS; i++) { const a = i / DROPS * 6.283 + 0.3, u = (t * 0.85 + i * 0.37) % 1, r = 0.15 + u * 0.75;
      dummy.position.set(Math.cos(a) * r, 1.62 + u * 0.75 - u * u * 1.85, Math.sin(a) * r); dummy.rotation.set(0, 0, 0); dummy.scale.setScalar(1 - u * 0.4); dummy.updateMatrix(); dropIM.setMatrixAt(i, dummy.matrix); }
    dropIM.instanceMatrix.needsUpdate = true;
    shades.forEach((q, i) => { q.x += q.v * dt; if (q.x > 46) q.x = -46; dummy.position.set(q.x, 0.07, q.z); dummy.rotation.set(-Math.PI / 2, 0, 0); dummy.scale.set(q.r * 1.5, q.r, 1); dummy.updateMatrix(); shadeIM.setMatrixAt(i, dummy.matrix); });
    shadeIM.instanceMatrix.needsUpdate = true; cloudShadeMat.opacity = 0.14 * (1 - env.night);
    spout.scale.setScalar(1 + Math.sin(t * 6) * 0.12);
    swingAmp += ((me.sit && me.sit.swing ? 0.55 : 0.12) - swingAmp) * Math.min(1, dt * 2);
    swingSeat.rotation.x = Math.sin(t * 1.9) * swingAmp;
    waterTex.offset.x = -t * 0.12;
    marker.rotation.z = t * 2;
    clouds.position.set(me.x * 0.6 + Math.sin(t * 0.02) * 10, 0, me.z - 44);

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
    fishes.forEach(f => { f.x += f.v * dt; if (f.x > 35) f.x = -35; else if (f.x < -35) f.x = 35; f.g.position.set(f.x, 0.062, f.z + Math.sin(t * 0.9 + f.ph) * 0.25); f.g.scale.set(f.s * Math.sign(f.v), f.s, 1); f.tail.rotation.z = Math.PI + Math.sin(t * 9 + f.ph) * 0.5; });
    stars.position.set(me.x, 0, me.z);
    sun.target.position.set(me.x, 0, me.z - 3); sun.position.set(me.x + env.sunPos.x, env.sunPos.y, me.z + env.sunPos.z);
    curve.uCurve.value += ((curveOn ? 0.0075 : 0) - curve.uCurve.value) * Math.min(1, dt * 5);
    curve.uFocusZ.value = me.z;
    camPos.set(me.x, 5.6 * zoom, me.z + 8.8 * zoom); camera.position.lerp(camPos, camera.position.lengthSq() < 1 ? 1 : Math.min(1, dt * 6));
    camera.lookAt(camera.position.x, 0.95, camera.position.z - 8.8 * zoom);

    // 캐릭터 모습·이름표
    actors.forEach(a => {
      if (a.hop > 0) a.hop -= dt;
      if (a.sit) { // 앉은 자리에 붙음 (그네는 줄을 따라 같이 흔들림)
        const q = a.sit, th = q.swing ? swingSeat.rotation.x : 0;
        a.g.position.set(q.x, q.swing ? 2.55 - 1.8 * Math.cos(th) + 0.04 : q.y, q.swing ? q.z - 1.8 * Math.sin(th) : q.z);
        a.g.rotation.x = th; a.face = q.face;
      } else { a.g.rotation.x = 0; a.g.position.set(a.x, a.hop > 0 ? Math.sin(Math.PI * (1 - a.hop / 0.4)) * 0.38 : 0, a.z); }
      let d = a.face - a.g.rotation.y; d = Math.atan2(Math.sin(d), Math.cos(d)); a.g.rotation.y += d * Math.min(1, dt * 12);
      if (a.wave > 0) a.wave -= dt;
      if (a.sayT > 0) a.sayT -= dt;
      const label = a.sayT > 0 ? a.say : a.name + (a.wave > 0 ? ' 👋' : '');
      if (label !== a.label) { a.label = label; a.tag.textContent = label; a.tag.classList.toggle('say', a.sayT > 0); }
      a.pet.update(t, { moving: a.moving, wave: a.wave > 0.02, sit: Boolean(a.sit) });
      const dz = a.z - me.z;
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

/* 마을용 3D 펫 모델 (Three.js r128 기준, 그림 파일 없이 공·원뿔·원기둥으로만 만듦)
 * 기존 도트 펫(assets/sprites/pet)의 색·귀·꼬리·소품을 그대로 옮긴 두 발로 서는 2.5등신 모델.
 * 쓰는 법: const pet = VillagePets.build(THREE, 'shiba', { material: VillagePets.toon(THREE), outline: 테두리 재질(선택) });
 * vertexMaterial(꼭짓점 색 재질)을 주면 부위별로 합쳐 그려 가벼워짐 — 이때 outline은 뒷면·꼭짓점 색 재질, outlineColor로 선 색 지정. scene.add(pet.group); 매 프레임 pet.update(초, { moving, wave })
 * 키는 약 1(size 배율 적용 전), 발바닥이 y=0, 앞이 +z.
 */
(function () {
  const RED = '#d94c4c', GREEN = '#3f9a5a', BLUE = '#3f6fc8', LEATHER = '#8a5a34', PINK = '#f2a0a8';

  // head: 머리 무늬 [색, 방향(x,y,z), 벌어진 각(라디안)] — 머리 겉면에 덧씌우는 둥근 조각
  const SPECS = {
    ginger: { name: '치즈 고양이', body: '#f0923a', belly: '#fbe3c0', ears: 'cat', earIn: '#f7b7a3', muzzle: '#fbe3c0', nose: '#e88a8a',
      stripes: '#c8641e', tail: 'long', tailTip: '#c8641e', acc: 'backpack', accColor: LEATHER, whiskers: true },
    calico: { name: '삼색 고양이', body: '#fbf7f0', belly: '#ffffff', ears: 'cat', earL: '#3a3a44', earR: '#f0923a', earIn: '#f7b7a3', muzzle: '#ffffff', nose: '#e88a8a',
      head: [['#3a3a44', [-0.75, 0.75, 0.25], 0.8], ['#f0923a', [0.75, 0.75, 0.25], 0.8]],
      bodyPatch: [['#f0923a', [-0.6, 0.3, -0.7], 0.8], ['#3a3a44', [0.7, 0.2, -0.6], 0.7]],
      tail: 'long', tailColor: '#3a3a44', tailTip: '#f0923a', acc: 'bowtie', accColor: RED, whiskers: true },
    black: { name: '검은 고양이', body: '#2d2b3a', belly: '#2d2b3a', ears: 'cat', earIn: '#5d4a72', nose: '#4a4558', eye: '#f5c63c',
      tail: 'long', acc: 'witchHat', whiskers: true, whiskerColor: '#8a86a0' },
    siberian: { name: '시베리안 고양이', body: '#9aa0a8', belly: '#f3f3f3', ears: 'cat', earIn: '#e9c3c3', muzzle: '#f6f6f6', nose: '#e88a8a',
      stripes: '#6f757d', head: [['#f3f3f3', [0, -0.75, 0.65], 0.8]], fluff: '#f3f3f3', fluffBack: '#9aa0a8',
      tail: 'bushy', tailColor: '#9aa0a8', tailTip: '#c9cdd3', acc: 'bell', accColor: RED, whiskers: true, chubby: 1.12 },
    shiba: { name: '시바견', body: '#eda83a', belly: '#fff3d6', ears: 'point', earIn: '#fff3d6', muzzle: '#fff3d6', nose: '#2d2b3a',
      head: [['#fff3d6', [-0.6, -0.5, 0.75], 0.62], ['#fff3d6', [0.6, -0.5, 0.75], 0.62], ['#fff3d6', [-0.36, 0.42, 1], 0.1], ['#fff3d6', [0.36, 0.42, 1], 0.1]],
      tail: 'curl', tailColor: '#fbe0a8', acc: 'bandana', accColor: GREEN },
    pomeranian: { name: '포메라니안', body: '#fbfbfb', belly: '#ffffff', ears: 'point', earScale: 0.75, earIn: '#f6c9cf', muzzle: '#ffffff', nose: '#2d2b3a',
      fluff: '#ffffff', fluffBack: '#f1f1f1', tongue: true, tail: 'puff', tailSize: 0.15, acc: 'bandana', accColor: RED, chubby: 1.08 },
    bulldog: { name: '불독', body: '#b9773f', belly: '#f6efe6', ears: 'flop', earColor: '#9a5e2e', muzzle: '#f6efe6', nose: '#2d2b3a', jowls: true, tongue: true,
      head: [['#f6efe6', [0, 0.35, 1], 0.3], ['#f6efe6', [0, 0.9, 0.5], 0.22]], tail: 'stub', acc: 'spikeCollar', accColor: RED, chubby: 1.18, headWide: 1.08 },
    collie: { name: '보더콜리', body: '#2f2f3a', belly: '#ffffff', ears: 'point', earIn: '#55556a', muzzle: '#ffffff', nose: '#2d2b3a', eyeRing: true,
      head: [['#ffffff', [0, 0.15, 1], 0.36], ['#ffffff', [0, 0.75, 0.7], 0.2], ['#ffffff', [0, -0.8, 0.6], 0.75]],
      tail: 'bushy', tailColor: '#2f2f3a', tailTip: '#ffffff', acc: 'bandana', accColor: BLUE },
    rabbit: { name: '갈색 토끼', body: '#a9764a', belly: '#dab98f', ears: 'long', earIn: '#e7b6a6', muzzle: '#dab98f', nose: '#d98a8a',
      tail: 'puff', tailColor: '#f3e3cc', tailSize: 0.075, acc: 'bandana', accColor: RED },
    squirrel: { name: '다람쥐', body: '#b5622e', belly: '#f3d3a0', ears: 'point', earScale: 0.6, earIn: '#f3d3a0', muzzle: '#f3d3a0', nose: '#3a2a22',
      head: [['#f3d3a0', [0, -0.7, 0.75], 0.85]], tail: 'squirrel', tailColor: '#b5622e', tailTip: '#d98a4a', acc: 'pouch', accColor: LEATHER },
    hamster: { name: '햄스터', body: '#f0a24a', belly: '#fde9c8', ears: 'round', earScale: 0.8, earIn: '#f6c0b0', muzzle: '#fde9c8', nose: '#e88a8a', blush: true,
      head: [['#fde9c8', [0, -0.6, 0.8], 1.05]], tail: 'none', acc: 'cap', accColor: '#3f7fd0', chubby: 1.22, headWide: 1.08, size: 0.92 },
    fennec: { name: '사막여우', body: '#f0cf95', belly: '#fff4dc', ears: 'big', earIn: '#f7c9b0', muzzle: '#fff4dc', nose: '#2d2b3a',
      head: [['#fff4dc', [0, -0.65, 0.8], 0.9]], tail: 'bushy', tailColor: '#f0cf95', tailTip: '#a9793f', acc: 'bandana', accColor: GREEN },
    panda: { name: '판다', body: '#fafafa', belly: '#ffffff', limb: '#26262e', ears: 'round', earColor: '#26262e', muzzle: '#ffffff', nose: '#26262e', eye2: '#f4f4f4',
      head: [['#26262e', [-0.4, 0.02, 1], 0.24], ['#26262e', [0.4, 0.02, 1], 0.24]], bodyPatch: [['#26262e', [0, 1, -0.15], 0.75]],
      tail: 'puff', tailSize: 0.06, acc: 'satchel', accColor: '#e8b83a', chubby: 1.2, headWide: 1.05 },
    otter: { name: '수달', body: '#7a5236', belly: '#c9a27a', ears: 'round', earScale: 0.55, earColor: '#6a452c', muzzle: '#d9b890', nose: '#2d2b3a',
      head: [['#c9a27a', [0, -0.7, 0.75], 0.9]], tail: 'otter', acc: 'bandana', accColor: BLUE, whiskers: true, whiskerColor: '#f3e3cc' },
    hedgehog: { name: '고슴도치', body: '#f0d9b5', belly: '#f8e9d0', ears: 'round', earScale: 0.6, earIn: '#e7b6a6', muzzle: '#f8e9d0', nose: '#2d2b3a', snout: true, blush: true,
      spines: '#7a5a3c', spineTip: '#c9a27a', tail: 'none', acc: 'backpack', accColor: LEATHER, size: 0.9, chubby: 1.1 },
    piglet: { name: '아기 돼지', body: '#f7a8b8', belly: '#fbc4cf', ears: 'pig', earIn: '#f08aa0', nose: '#f08aa0', pigSnout: true, blush: true,
      tail: 'pig', acc: 'bowtie', accColor: RED, chubby: 1.15 },
    raccoon: { name: '너구리', body: '#9a928a', belly: '#ece6dc', ears: 'round', earScale: 0.8, earColor: '#6a625c', earIn: '#e3d6cc', muzzle: '#f6f2ea', nose: '#2d2b3a', eye2: '#f4f4f4',
      head: [['#3a3432', [-0.4, 0.05, 1], 0.3], ['#3a3432', [0.4, 0.05, 1], 0.3], ['#f6f2ea', [0, 0.55, 0.85], 0.22]],
      tail: 'bushy', tailColor: '#9a928a', tailTip: '#3a3432', acc: 'cap', accColor: '#3f9a5a', whiskers: true, chubby: 1.1 },
    // 펫이 아직 없는 학생이 마을에서 쓰는 모습
    guest: { name: '새싹 (펫 없음)', body: '#fff3d8', belly: '#ffffff', ears: 'round', earScale: 0.7, earIn: '#f6c9b8', muzzle: '#ffffff', nose: '#c98a6a', blush: true,
      tail: 'puff', tailSize: 0.06, acc: 'none', chubby: 1.1, size: 0.95 },
  };

  /* 합쳐 그리기: root 아래의 여러 조각을 색(꼭짓점 색)째로 한 덩어리로 구워 그리기 횟수를 줄임.
   * o.stop: 따로 움직여야 해서 건너뛸 하위 묶음(Set), o.vertexMaterial: 꼭짓점 색을 쓰는 재질,
   * o.outlineMaterial: 테두리용(뒷면·꼭짓점 색) 재질, o.thickness: 테두리 두께, o.minSize·o.minSecond: 이보다 작은 조각은 테두리 없음,
   * o.lineColor(mesh): 테두리 색(안 주면 제 색을 어둡게), o.accept(mesh): 합칠 조각인지.
   * 무늬(map)가 있는 재질은 그 재질끼리 따로 합침. 돌려줌: { meshes, outlines } */
  function merge(THREE, root, o) {
    const stop = o.stop || new Set(), entries = [];
    const accept = o.accept || (m => m.material && m.material.isMeshToonMaterial && !m.userData.noShadow && !m.userData.floor);
    const walk = (node, mat) => node.children.slice().forEach(ch => {
      if (stop.has(ch)) return;
      ch.updateMatrix(); const m = new THREE.Matrix4().multiplyMatrices(mat, ch.matrix);
      if (ch.isMesh && !ch.isInstancedMesh && accept(ch)) entries.push({ mesh: ch, m });
      walk(ch, m);
    });
    walk(root, new THREE.Matrix4());
    if (!entries.length) return { meshes: [], outlines: [] };
    const v = new THREE.Vector3(), n = new THREE.Vector3(), nm = new THREE.Matrix3(), size = new THREE.Vector3(), ctr = new THREE.Vector3(), tmp = new THREE.Color();
    const bucket = (mat, useColor, useUv) => ({ mat, useColor, useUv, pos: [], nor: [], col: [], uv: [], idx: [] });
    const push = (b, g, m, color, grow) => { // grow: 법선 쪽으로 밀어낼 거리(관 모양 테두리용)
      const pos = g.attributes.position, nor = g.attributes.normal, uv = g.attributes.uv, base = b.pos.length / 3;
      nm.getNormalMatrix(m);
      for (let i = 0; i < pos.count; i++) {
        v.fromBufferAttribute(pos, i).applyMatrix4(m); n.fromBufferAttribute(nor, i).applyMatrix3(nm).normalize();
        if (grow) v.addScaledVector(n, grow);
        b.pos.push(v.x, v.y, v.z); b.nor.push(n.x, n.y, n.z);
        if (b.useColor) b.col.push(color.r, color.g, color.b);
        if (b.useUv) b.uv.push(uv ? uv.getX(i) : 0, uv ? uv.getY(i) : 0);
      }
      if (g.index) for (let k = 0; k < g.index.count; k++) b.idx.push(g.index.getX(k) + base); else for (let k = 0; k < pos.count; k++) b.idx.push(base + k);
    };
    const buckets = new Map(), line = o.outlineMaterial ? bucket(o.outlineMaterial, true, false) : null;
    entries.forEach(({ mesh, m }) => {
      const g = mesh.geometry, mat = mesh.material, key = mat.map ? mat.uuid : 'vc';
      if (!buckets.has(key)) buckets.set(key, mat.map ? bucket(mat, false, true) : bucket(o.vertexMaterial, true, false));
      push(buckets.get(key), g, m, mat.color);
      if (!line || mesh.userData.noOutline) return;
      if (!g.boundingBox) g.computeBoundingBox();
      g.boundingBox.getSize(size); g.boundingBox.getCenter(ctr);
      const e = m.elements, len = [Math.hypot(e[0], e[1], e[2]), Math.hypot(e[4], e[5], e[6]), Math.hypot(e[8], e[9], e[10])];
      const dims = [size.x * len[0], size.y * len[1], size.z * len[2]], sorted = dims.slice().sort((a, b) => b - a);
      if (sorted[0] < (o.minSize || 0) * 2 || sorted[1] < (o.minSecond || 0)) return;
      const c = o.lineColor ? o.lineColor(mesh) : tmp.copy(mat.color).multiplyScalar(0.42), T = o.thickness || 0.02;
      if (g.type === 'TubeGeometry' || g.type === 'TorusGeometry') { push(line, g, m, c, T); return; }
      // 같은 모양을 제 가운데에서 살짝 키운 껍데기 (상자도 모서리가 끊기지 않음)
      const f = dims.map(d => 1 + 2 * T / Math.max(d, 0.02));
      const shell = new THREE.Matrix4().makeTranslation(ctr.x, ctr.y, ctr.z).multiply(new THREE.Matrix4().makeScale(f[0], f[1], f[2])).multiply(new THREE.Matrix4().makeTranslation(-ctr.x, -ctr.y, -ctr.z));
      push(line, g, new THREE.Matrix4().multiplyMatrices(m, shell), c);
    });
    entries.forEach(e => { if (e.mesh.parent) e.mesh.parent.remove(e.mesh); });
    const make = b => {
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.Float32BufferAttribute(b.pos, 3)); geo.setAttribute('normal', new THREE.Float32BufferAttribute(b.nor, 3));
      if (b.useColor) geo.setAttribute('color', new THREE.Float32BufferAttribute(b.col, 3));
      if (b.useUv) geo.setAttribute('uv', new THREE.Float32BufferAttribute(b.uv, 2));
      geo.setIndex(b.pos.length / 3 > 65535 ? new THREE.Uint32BufferAttribute(b.idx, 1) : new THREE.Uint16BufferAttribute(b.idx, 1));
      const mesh = new THREE.Mesh(geo, b.mat); mesh.userData.merged = true; root.add(mesh); return mesh;
    };
    const meshes = []; buckets.forEach(b => meshes.push(make(b)));
    const outlines = [];
    if (line && line.pos.length) { const ol = make(line); ol.userData.noShadow = true; ol.userData.noOutline = true; outlines.push(ol); }
    return { meshes, outlines };
  }

  // 툰 셰이딩 재질 만들기: 밝기를 세 단계로 끊어 만화처럼 보이게 함. 돌려받은 함수(색 → 재질)를 build의 opts.material로 넘김
  function toon(THREE, wrap) {
    const g = new THREE.DataTexture(new Uint8Array([165, 215, 255]), 3, 1, THREE.LuminanceFormat);
    g.minFilter = g.magFilter = THREE.NearestFilter; g.needsUpdate = true;
    const cache = {};
    return c => cache[c] || (cache[c] = (wrap || (m => m))(new THREE.MeshToonMaterial({ color: new THREE.Color(c), gradientMap: g })));
  }

  // opts.material: 색 문자열 → 재질 (안 주면 기본 재질)
  function build(THREE, type, opts) {
    opts = opts || {};
    const S = SPECS[type] || SPECS.ginger;
    const V = (x, y, z) => new THREE.Vector3(x, y, z);
    const UP = V(0, 1, 0);
    const mats = {};
    const mat = c => mats[c] || (mats[c] = opts.material ? opts.material(c) : new THREE.MeshLambertMaterial({ color: new THREE.Color(c) }));
    const geo = { sph: new THREE.SphereGeometry(1, 28, 18), sphMid: new THREE.SphereGeometry(1, 16, 11), sphLow: new THREE.SphereGeometry(1, 12, 8) }; // 큰 덩어리만 촘촘하게
    const ball = (r, c, sx = 1, sy = 1, sz = 1, low) => { const m = new THREE.Mesh(low ? geo.sphLow : r * Math.max(sx, sy, sz) >= 0.13 ? geo.sph : geo.sphMid, mat(c)); m.scale.set(r * sx, r * sy, r * sz); return m; };
    const cone = (r, h, c, seg = 28) => new THREE.Mesh(new THREE.ConeGeometry(r, h, seg), mat(c));
    const at = (o, x, y, z) => { o.position.set(x, y, z); return o; };
    const grp = (...kids) => { const g = new THREE.Group(); kids.forEach(k => k && g.add(k)); return g; };
    // 타원체(반지름 R, 축 배율 sc) 겉면 위의 점과, 그 겉면에 덧씌우는 둥근 조각
    const surf = (R, sc, d, k = 1) => { const n = V(d[0], d[1], d[2]).normalize(); return V(n.x * sc.x * R * k, n.y * sc.y * R * k, n.z * sc.z * R * k); };
    const patch = (R, sc, c, d, ang, lift = 1.015) => {
      const m = new THREE.Mesh(new THREE.SphereGeometry(R * lift, 36, 16, 0, Math.PI * 2, 0, ang), mat(c)); m.userData.noOutline = true;
      m.quaternion.setFromUnitVectors(UP, V(d[0], d[1], d[2]).normalize());
      const h = grp(m); h.scale.copy(sc); return h;
    };
    const aim = (o, d) => { o.quaternion.setFromUnitVectors(UP, V(d[0], d[1], d[2]).normalize()); return o; };

    const chub = S.chubby || 1;
    const root = new THREE.Group();
    const rig = new THREE.Group(); root.add(rig);
    root.scale.setScalar(S.size || 1);
    const limbC = S.limb || S.body;

    // ── 다리
    const legs = [-1, 1].map(s => {
      const p = at(new THREE.Group(), s * 0.085 * chub, 0.17, 0);
      p.add(at(ball(0.062, limbC, 1, 1.5, 1), 0, -0.085, 0));
      p.add(at(ball(0.068, limbC, 1, 0.6, 1.35), 0, -0.135, 0.025));
      rig.add(p); return p;
    });

    // ── 몸통
    const BR = 0.19, bsc = V(chub, 1.02, 0.92 * (1 + (chub - 1) * 0.6));
    const body = at(new THREE.Group(), 0, 0.31, 0); rig.add(body);
    const bodyMesh = ball(BR, S.body); bodyMesh.scale.set(BR * bsc.x, BR * bsc.y, BR * bsc.z); body.add(bodyMesh);
    if (S.belly !== S.body) body.add(patch(BR, bsc, S.belly, [0, -0.25, 1], 0.95));
    (S.bodyPatch || []).forEach(p => body.add(patch(BR, bsc, p[0], p[1], p[2], 1.02)));

    // ── 팔 (어깨에서 돎)
    const arms = [-1, 1].map(s => {
      const p = at(new THREE.Group(), s * 0.165 * chub, 0.4, 0.02);
      p.add(at(ball(0.052, limbC, 1, 1.9, 1), 0, -0.085, 0));
      p.rotation.z = s * 0.35;
      rig.add(p); return p;
    });

    // ── 머리
    const HR = 0.255, hsc = V(1.12 * (S.headWide || 1), 0.94, 1);
    const head = at(new THREE.Group(), 0, 0.68, 0.01); rig.add(head);
    const headMesh = ball(HR, S.body); headMesh.scale.set(HR * hsc.x, HR * hsc.y, HR * hsc.z); head.add(headMesh);
    (S.head || []).forEach(p => head.add(patch(HR, hsc, p[0], p[1], p[2])));
    const hs = (d, k = 1) => surf(HR, hsc, d, k);

    // 줄무늬 (이마 세 줄 + 볼 두 줄)
    if (S.stripes) {
      [-0.2, 0, 0.2].forEach(x => { const m = ball(0.02, S.stripes, 1, 0.5, x ? 3 : 3.8); m.userData.noOutline = true; m.position.copy(hs([x, 1, 0.42], 1.0)); m.rotation.x = 0.4; head.add(m); });
      [-1, 1].forEach(s => [0.02, -0.18].forEach(y => { const m = ball(0.016, S.stripes, 3, 0.9, 0.6); m.userData.noOutline = true; m.position.copy(hs([s * 1, y, 0.42], 1.0)); m.rotation.y = s * 1.15; head.add(m); }));
    }
    // 가시 (고슴도치: 머리 뒤와 등을 덮음)
    const spikes = (target, R, sc, dir, ang, n, len) => {
      target.add(patch(R, sc, S.spines, dir, ang, 1.04));
      const c = V(dir[0], dir[1], dir[2]).normalize();
      for (let i = 0; i < n; i++) {
        const y = 1 - 2 * (i + 0.5) / n, r = Math.sqrt(1 - y * y), th = i * 2.399963;
        const d = V(Math.cos(th) * r, y, Math.sin(th) * r);
        if (d.angleTo(c) > ang - 0.12) continue;
        const sp = cone(0.03, len, i % 3 ? S.spines : S.spineTip, 5); sp.userData.noOutline = true;
        sp.position.copy(surf(R, sc, [d.x, d.y, d.z], 1.04 + len * 0.42 / R));
        aim(sp, [d.x * sc.x, d.y * sc.y + 0.25, d.z * sc.z - 0.2]);
        target.add(sp);
      }
    };
    if (S.spines) { spikes(head, HR, hsc, [0, 0.55, -0.85], 1.72, 120, 0.1); spikes(body, BR, bsc, [0, 0.1, -1], 1.5, 60, 0.09); }

    // 눈 (깜빡일 때 납작해짐)
    const eyes = [-1, 1].map(s => {
      const e = new THREE.Group(); e.position.copy(hs([s * 0.4, 0.02, 1], 0.99));
      if (S.eyeRing) e.add(at(ball(0.039, '#ffffff', 1, 1.12, 0.45), 0, 0, -0.003));
      if (S.eye) { e.add(ball(0.042, S.eye, 1, 1.05, 0.5)); e.add(at(ball(0.022, '#17151f', 0.55, 1.5, 0.5), 0, 0, 0.012)); }
      else e.add(ball(0.034, '#1f1b24', 1, 1.15, 0.55));
      if (S.eye2) e.add(at(ball(0.016, S.eye2, 1, 1, 0.5), 0, 0, 0.012));
      e.add(at(ball(0.011, '#ffffff', 1, 1, 0.5), s * -0.01 + 0.012, 0.014, 0.018));
      e.traverse(o => { o.userData.noOutline = true; });
      head.add(e); return e;
    });
    if (S.blush) [-1, 1].forEach(s => head.add(patch(HR, hsc, PINK, [s * 0.72, -0.3, 0.8], 0.15, 1.02)));

    // 주둥이·코·입
    const mz = hs([0, -0.3, 1], 0.93);
    if (S.pigSnout) {
      const sn = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.075, 0.06, 18), mat(S.nose));
      sn.rotation.x = Math.PI / 2; sn.scale.set(1.2, 1, 1); sn.position.set(0, mz.y + 0.01, mz.z + 0.03); head.add(sn);
      const sm = new THREE.Mesh(new THREE.TorusGeometry(0.034, 0.007, 6, 12, Math.PI), mat('#c9607a')); sm.rotation.z = Math.PI; sm.userData.noOutline = true; head.add(at(sm, 0, mz.y - 0.062, mz.z + 0.012)); // 웃는 입
      [-1, 1].forEach(s => head.add(at(ball(0.014, '#c9607a', 1, 1.5, 0.5), s * 0.03, mz.y + 0.01, mz.z + 0.06)));
    } else {
      const long = S.snout ? 1.7 : 1;
      if (S.muzzle) head.add(at(ball(0.082, S.muzzle, 1.25, 0.82, 0.85 * long), 0, mz.y, mz.z));
      if (S.jowls) [-1, 1].forEach(s => head.add(at(ball(0.062, S.muzzle, 1, 1.05, 0.9), s * 0.06, mz.y - 0.035, mz.z + 0.02)));
      head.add(at(ball(0.026, S.nose || '#2d2b3a', 1.3, 0.85, 0.9), 0, mz.y + 0.035, mz.z + 0.062 * long + (S.muzzle ? 0 : -0.035)));
      if (S.tongue) head.add(at(ball(0.026, '#ee7f8e', 1, 0.5, 1.2), 0, mz.y - 0.05, mz.z + 0.05));
      else [-1, 1].forEach(sd => { // 웃는 입: 코 아래 작은 곡선 두 개 (ω 모양)
        const sm = new THREE.Mesh(new THREE.TorusGeometry(0.021, 0.0055, 6, 10, Math.PI), mat('#4a332c')); sm.rotation.z = Math.PI; sm.userData.noOutline = true;
        head.add(at(sm, sd * 0.021, mz.y + 0.012, mz.z + 0.066 * long + (S.muzzle ? 0 : -0.035)));
      });
    }
    if (S.whiskers) [-1, 1].forEach(s => [0.02, -0.03].forEach((y, i) => {
      const w = new THREE.Mesh(new THREE.CylinderGeometry(0.003, 0.003, 0.13, 4), mat(S.whiskerColor || '#ffffff')); w.userData.noOutline = true;
      w.rotation.z = Math.PI / 2 + s * (i ? 0.2 : -0.12); w.position.set(s * 0.17, mz.y + y, mz.z + 0.02); w.rotation.y = s * -0.35; head.add(w);
    }));
    // 목·볼 털 (포메라니안·시베리안)
    if (S.fluff) {
      for (let i = 0; i < 10; i++) {
        const a = i / 10 * Math.PI * 2, front = Math.cos(a) > -0.2;
        head.add(at(ball(0.07, front ? S.fluff : S.fluffBack, 1, 0.85, 1, true), Math.sin(a) * 0.19, -0.215, Math.cos(a) * 0.14));
      }
      [-1, 1].forEach(s => head.add(at(ball(0.065, S.fluffBack === '#f1f1f1' ? S.fluff : S.body, 1.1, 0.9, 0.8, true), s * 0.265, -0.1, 0.03)));
    }

    // ── 귀
    const earS = S.earScale || 1;
    const ears = [-1, 1].map(s => {
      const c = S.earColor || (s < 0 ? S.earL : S.earR) || S.body;
      const p = new THREE.Group(); let m, inn;
      if (S.ears === 'cat' || S.ears === 'point' || S.ears === 'big' || S.ears === 'pig') {
        const big = S.ears === 'big', r = (big ? 0.12 : 0.095) * earS, h = (big ? 0.34 : S.ears === 'point' ? 0.19 : 0.17) * earS;
        m = at(cone(r, h, c), 0, h * 0.42, 0); m.scale.z = 0.5;
        if (S.earIn) { inn = at(cone(r * 0.62, h * 0.7, S.earIn), 0, h * 0.36, r * 0.24); inn.scale.z = 0.35; }
        p.position.copy(hs([s * (big ? 0.62 : 0.58), 0.8, -0.05], 0.9));
        p.rotation.z = -s * (big ? 0.5 : 0.28);
        if (S.ears === 'pig') { p.rotation.x = 0.75; p.position.z += 0.05; }
      } else if (S.ears === 'long') {
        m = at(ball(0.058, c, 1, 3.3, 0.55), 0, 0.17, 0);
        inn = at(ball(0.036, S.earIn, 1, 3.6, 0.4), 0, 0.17, 0.02);
        p.position.copy(hs([s * 0.3, 1, -0.1], 0.9)); p.rotation.z = -s * 0.16;
      } else if (S.ears === 'flop') {
        m = at(ball(0.062, c, 1, 1.5, 0.55), 0, -0.07, 0);
        p.position.copy(hs([s * 0.88, 0.5, 0.08], 1.0)); p.rotation.z = s * 0.5; p.rotation.y = s * 0.3;
      } else { // round
        m = ball(0.085 * earS, c, 1, 1, 0.55);
        if (S.earIn) inn = at(ball(0.052 * earS, S.earIn, 1, 1, 0.4), 0, 0, 0.03 * earS);
        p.position.copy(hs([s * 0.72, 0.72, 0], 1.0));
      }
      p.add(m); if (inn) p.add(inn);
      head.add(p); return p;
    });

    // ── 꼬리 (엉덩이에서 좌우로 흔듦)
    const tail = at(new THREE.Group(), 0, 0.24, -0.15 * bsc.z / 0.92); rig.add(tail);
    const tc = S.tailColor || S.body;
    const chain = (pts, radii, tipFrom) => pts.forEach((p, i) => tail.add(at(ball(radii[i], i >= tipFrom && S.tailTip ? S.tailTip : tc, 1, 1, 1, true), p[0], p[1], p[2])));
    if (S.tail === 'long') {
      const curve = new THREE.CatmullRomCurve3([V(0, 0, 0), V(0, 0, -0.14), V(0.03, 0.14, -0.25), V(0.06, 0.3, -0.22), V(0.04, 0.38, -0.13)]);
      tail.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 20, 0.028, 8), mat(tc)));
      tail.add(at(ball(0.034, S.tailTip || tc), 0.04, 0.38, -0.13));
      if (S.tailTip) tail.add(at(ball(0.032, S.tailTip, 1, 1, 1), 0.05, 0.24, -0.245));
    } else if (S.tail === 'bushy') {
      chain([[0, 0, -0.04], [0, 0.04, -0.14], [0, 0.12, -0.23], [0, 0.22, -0.28], [0, 0.31, -0.27]], [0.06, 0.085, 0.1, 0.09, 0.06], 3);
    } else if (S.tail === 'squirrel') {
      chain([[0, 0, -0.05], [0, 0.08, -0.16], [0, 0.22, -0.23], [0, 0.38, -0.24], [0, 0.52, -0.19], [0, 0.6, -0.09]], [0.07, 0.1, 0.125, 0.13, 0.115, 0.085], 4);
    } else if (S.tail === 'curl') {
      const t = new THREE.Mesh(new THREE.TorusGeometry(0.065, 0.042, 10, 18), mat(tc));
      t.rotation.y = Math.PI / 2; tail.add(at(t, 0, 0.08, -0.07));
    } else if (S.tail === 'puff') {
      tail.add(at(ball(S.tailSize || 0.08, tc, 1, 1, 1, true), 0, 0.01, -0.03 - (S.tailSize || 0.08) * 0.5));
    } else if (S.tail === 'stub') {
      tail.add(at(ball(0.04, tc), 0, 0.02, -0.04));
    } else if (S.tail === 'otter') {
      const t = cone(0.075, 0.4, tc); aim(t, [0, -0.45, -1]); tail.add(at(t, 0, -0.07, -0.16));
    } else if (S.tail === 'pig') {
      const pts = []; for (let i = 0; i <= 24; i++) { const a = i / 24 * Math.PI * 3.2; pts.push(V(Math.cos(a) * 0.035, Math.sin(a) * 0.035 + 0.03, -0.02 - i * 0.005)); }
      tail.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 40, 0.014, 6), mat('#f08aa0')));
    }

    // ── 소품
    const ac = S.accColor, neckY = 0.475;
    const band = (r, tube, c) => { const t = new THREE.Mesh(new THREE.TorusGeometry(r, tube, 8, 24), mat(c)); t.rotation.x = Math.PI / 2; return t; };
    if (S.acc === 'bandana') {
      rig.add(at(band(0.14 * chub, 0.03, ac), 0, neckY, 0.01));
      const tri = cone(0.11, 0.15, ac, 3); tri.scale.z = 0.3; tri.rotation.set(Math.PI + 0.35, 0, 0); rig.add(at(tri, 0, neckY - 0.07, 0.15 * chub));
      rig.add(at(ball(0.03, ac), 0.03, neckY, -0.15 * chub));
    } else if (S.acc === 'bowtie') {
      [-1, 1].forEach(s => { const c = cone(0.05, 0.085, ac, 10); c.rotation.z = s * Math.PI / 2; c.scale.z = 0.5; rig.add(at(c, s * 0.05, neckY - 0.02, 0.165 * chub)); });
      rig.add(at(ball(0.022, '#b53a3a'), 0, neckY - 0.02, 0.172 * chub));
    } else if (S.acc === 'bell') {
      rig.add(at(band(0.14 * chub, 0.018, ac), 0, neckY, 0.01));
      rig.add(at(ball(0.036, '#f2c53a'), 0, neckY - 0.045, 0.165 * chub));
      rig.add(at(ball(0.008, '#8a6a1a'), 0, neckY - 0.062, 0.196 * chub));
    } else if (S.acc === 'spikeCollar') {
      rig.add(at(band(0.15 * chub, 0.026, ac), 0, neckY, 0.01));
      for (let i = 0; i < 9; i++) { const a = i / 9 * Math.PI * 2, r = 0.172 * chub; const sp = cone(0.016, 0.045, '#eeeeee', 6); aim(sp, [Math.sin(a), 0, Math.cos(a)]); rig.add(at(sp, Math.sin(a) * r, neckY, Math.cos(a) * r + 0.01)); }
    } else if (S.acc === 'witchHat') {
      const hat = at(new THREE.Group(), 0.01, HR * hsc.y * 0.82, -0.01); hat.rotation.set(-0.12, 0, -0.1);
      const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.215, 0.225, 0.016, 24), mat('#3a2f52')); hat.add(brim);
      hat.add(at(cone(0.12, 0.2, '#3a2f52', 18), 0, 0.105, 0));
      const tip = cone(0.06, 0.16, '#3a2f52', 12); tip.rotation.z = -0.75; hat.add(at(tip, 0.055, 0.215, 0));
      const bd = new THREE.Mesh(new THREE.CylinderGeometry(0.108, 0.122, 0.036, 20), mat('#8a5cc8')); hat.add(at(bd, 0, 0.03, 0));
      hat.add(at(new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.04, 0.01), mat('#f2c53a')), 0, 0.03, 0.118));
      head.add(hat);
      ears.forEach((e, i) => { e.position.x += (i ? 1 : -1) * 0.03; e.position.y -= 0.02; });
    } else if (S.acc === 'cap') {
      const dome = new THREE.Mesh(new THREE.SphereGeometry(HR * 0.8, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), mat(ac));
      dome.scale.set(hsc.x * 0.98, 0.78, 1); const cap = at(grp(dome), 0, HR * hsc.y * 0.56, 0.01); cap.rotation.x = -0.14;
      const visor = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.016, 18, 1, false, -Math.PI / 2, Math.PI), mat('#2f62ad'));
      visor.rotation.y = Math.PI / 2; visor.scale.set(1.25, 1, 1.35); cap.add(at(visor, 0, 0.012, 0.16));
      cap.add(at(ball(0.02, '#2f62ad'), 0, HR * 0.63, 0));
      head.add(cap);
    } else if (S.acc === 'backpack') {
      const bz = -(BR * bsc.z + 0.055);
      const bag = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.2, 0.11), mat(ac)); body.add(at(bag, 0, 0.03, bz));
      body.add(at(ball(0.1, ac, 1, 0.5, 0.56), 0, 0.13, bz));
      body.add(at(new THREE.Mesh(new THREE.BoxGeometry(0.21, 0.07, 0.03), mat('#a8743f')), 0, 0.085, bz - 0.05));
      body.add(at(ball(0.014, '#f2c53a'), 0, 0.055, bz - 0.068));
      [-1, 1].forEach(s => { const st = new THREE.Mesh(new THREE.TorusGeometry(BR * 0.93, 0.016, 6, 20), mat('#6a4326')); st.rotation.y = Math.PI / 2; st.scale.set(bsc.z * 1.08, 1.05, 1); body.add(at(st, s * 0.1 * chub, 0.02, 0)); });
    } else if (S.acc === 'satchel' || S.acc === 'pouch') {
      const st = new THREE.Mesh(new THREE.TorusGeometry(BR * 1.02, 0.014, 6, 24), mat(S.acc === 'pouch' ? '#6a4326' : '#b98a2a'));
      st.scale.set(bsc.x * 1.03, 1.12, bsc.z * 1.05); st.rotation.set(0, 0, 0.65); const h = grp(st); body.add(h);
      const bag = S.acc === 'pouch' ? ball(0.075, ac, 1, 1.05, 0.7) : new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.1, 0.06), mat(ac));
      body.add(at(bag, -0.19 * chub, -0.1, 0.06));
      if (S.acc === 'satchel') body.add(at(new THREE.Mesh(new THREE.BoxGeometry(0.125, 0.045, 0.065), mat('#f0cc5a')), -0.19 * chub, -0.07, 0.06));
      else body.add(at(ball(0.03, '#5a3a20', 1, 0.7, 1), -0.19 * chub, -0.03, 0.06));
    }

    // ── 움직임: update(초, { moving: 걷는 중, wave: 인사 중, sit: 앉은 중 })
    const blinkAt = Math.random() * 3;
    let walk = 0, waveK = 0, sitK = 0, bowK = 0, angK = 0, airK = 0, last = null;
    function update(t, st) {
      st = st || {};
      const dt = last == null ? 0 : Math.min(0.1, t - last); last = t;
      walk += ((st.moving ? 1 : 0) - walk) * Math.min(1, dt * 10);
      waveK += ((st.wave ? 1 : 0) - waveK) * Math.min(1, dt * 8);
      sitK += ((st.sit ? 1 : 0) - sitK) * Math.min(1, dt * 9);
      bowK += ((st.bow ? 1 : 0) - bowK) * Math.min(1, dt * 10); angK += ((st.angry ? 1 : 0) - angK) * Math.min(1, dt * 10); airK += ((st.air ? 1 : 0) - airK) * Math.min(1, dt * 14); // 꾸벅 사과 · 씩씩 화내기
      const sw = Math.sin(t * 11) * walk;
      legs[0].rotation.x = sw * 0.8 - 1.45 * sitK; legs[1].rotation.x = -sw * 0.8 - 1.45 * sitK; // 앉으면 다리를 앞으로 뻗음
      legs[0].rotation.z = -0.12 * sitK; legs[1].rotation.z = 0.12 * sitK;
      legs[0].rotation.x -= 0.8 * airK; legs[1].rotation.x -= 0.5 * airK; // 점프하면 다리를 접음
      arms[0].rotation.x = -sw * 0.9;
      arms[1].rotation.x = sw * 0.9 * (1 - waveK);
      arms[1].rotation.z = 0.35 + waveK * (2.1 + Math.sin(t * 12) * 0.35);
      arms[0].rotation.z = -0.35 - angK * (1.5 + Math.sin(t * 22) * 0.25); if (angK > 0.01) arms[1].rotation.z = 0.35 + angK * (1.5 + Math.sin(t * 22 + 1) * 0.25); // 화나면 두 팔을 번쩍
      if (airK > 0.01) { arms[0].rotation.z -= 0.9 * airK; arms[1].rotation.z += 0.9 * airK; } // 공중에선 두 팔을 벌림
      if (bowK > 0.01) { arms[0].rotation.x += -0.5 * bowK; arms[1].rotation.x += -0.5 * bowK; } // 꾸벅할 땐 두 손을 앞으로 모음
      if (st.hold) { arms[1].rotation.x = st.hold === 'fish' ? -0.9 : st.hold === 'swing' ? -1.5 : -0.45 + sw * 0.15; arms[1].rotation.z = 0.18; } // 물건을 쥔 팔: 낚시 땐 앞으로, 들고 다닐 땐 살짝 앞으로
      rig.position.y = Math.abs(Math.sin(t * 11)) * 0.035 * walk - 0.12 * sitK + Math.abs(Math.sin(t * 16)) * 0.06 * angK; // 앉으면 엉덩이가 바닥(y=0)에 닿게 내림, 화나면 발을 동동
      rig.rotation.z = Math.sin(t * 11) * 0.05 * walk + Math.sin(t * 30) * 0.07 * angK;
      rig.rotation.x = 0.5 * bowK; // 꾸벅
      const sq = Math.sin(t * 22) * 0.035 * walk; rig.scale.set(1 - sq * 0.5, 1 + sq, 1 - sq * 0.5); // 걸을 때 통통 튀는 탄력
      const br = 1 + Math.sin(t * 2.2) * 0.018 * (1 - walk);
      body.scale.set(1, br, 1);
      head.position.y = 0.68 + (br - 1) * 0.3;
      head.rotation.z = Math.sin(t * 1.3) * 0.045 + waveK * 0.12;
      head.rotation.x = Math.sin(t * 0.9) * 0.03 + 0.3 * bowK - 0.15 * angK;
      tail.rotation.y = Math.sin(t * (5 + walk * 4 + waveK * 6)) * (0.22 + waveK * 0.25);
      const tw = Math.max(0, Math.sin(t * 0.7 + blinkAt * 5) - 0.96) * 25; // 가끔 귀 쫑긋
      ears[0].rotation.x = (S.ears === 'pig' ? 0.75 : 0) - tw * 0.25; ears[1].rotation.x = (S.ears === 'pig' ? 0.75 : 0) - tw * 0.25;
      const bl = ((t + blinkAt) % 3.4) < 0.12 ? 0.12 : 1;
      eyes.forEach(e => { e.scale.y = bl; });
    }
    // 테두리선: opts.outline(뒷면만 그리는 재질, 바깥으로 부풀리는 건 재질 쪽 셰이더 몫)을 주면 큰 덩어리마다 껍데기를 하나씩 덧붙임
    const outlines = [];
    if (opts.vertexMaterial) { // 합쳐 그리기: 따로 움직이는 부위(몸·머리·팔다리·귀·눈·꼬리)마다 한 덩어리 + 테두리 한 덩어리
      const parts = [rig, body, head, tail].concat(legs, arms, ears, eyes), all = new Set(parts);
      parts.forEach(part => {
        const stop = new Set(all); stop.delete(part);
        const r = merge(THREE, part, { stop, vertexMaterial: opts.vertexMaterial, outlineMaterial: opts.outline, thickness: 0.011, minSize: 0.045, accept: () => true, lineColor: opts.outlineColor ? () => opts.outlineColor : null });
        r.outlines.forEach(ol => outlines.push(ol));
      });
    } else if (opts.outline) {
      const list = [];
      root.traverse(o => { if (o.isMesh && !o.userData.noOutline) list.push(o); });
      list.forEach(o => {
        if (!o.geometry.boundingSphere) o.geometry.computeBoundingSphere();
        if (o.geometry.boundingSphere.radius * Math.max(Math.abs(o.scale.x), Math.abs(o.scale.y), Math.abs(o.scale.z)) < 0.045) return; // 코·눈 같은 작은 조각은 뺌
        const ol = new THREE.Mesh(o.geometry, opts.outline); ol.userData.noShadow = true; ol.userData.noOutline = true; o.add(ol); outlines.push(ol);
      });
    }
    const hands = arms.map(a => at(new THREE.Group(), 0, -0.17, 0.03)); hands.forEach((h, i) => arms[i].add(h)); // 손 자리: 물건을 쥐여 줄 때 여기에 붙임
    update(0);
    return { group: root, update, spec: S, height: 1 * (S.size || 1), outlines, hands };
  }

  window.VillagePets = { SPECS, build, toon, merge };
})();

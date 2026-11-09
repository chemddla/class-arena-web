// PixelFX lite: 도트 이펙트를 4px 칸 캔버스에 그리는 작은 엔진.
// 그리는 법은 pixelfx(https://github.com/patch-gg/pixelfx, MIT)의 작법을 따름 (코드는 새로 씀):
//  - 색 버퍼(불투명·반투명 칸) + 빛 버퍼(더해지는 빛) 두 층을 겹쳐서 뜨거운 건 정말 빛나 보이게
//  - 색은 어두움→밝음 램프 하나로: 갓 생긴 불꽃은 램프 꼭대기(흰·노랑), 식으면서 아래(주황·빨강)로
//  - 빛 = 크고 옅은 웅덩이 + 작고 뜨거운 심, 터지는 순간 확 밝아졌다가 남은 수명의 제곱으로 빠르게 꺼짐
//  - 빠르게 터지고 천천히 사라짐(drag), 빠른 불꽃은 속도만큼 늘어난 2톤 줄(밝은 머리, 어두운 꼬리)
//  - 시뮬레이션은 120Hz로 쪼개서 화면 주사율과 상관없이 같은 움직임
//  - 넓은 빛은 4x4 바이어 디더로 계단을 나눠 도트 그라데이션처럼
(() => {
  'use strict';
  const PX = 4; // 도트 한 칸 = CSS 4px (초기화면 그림들과 같은 격자)
  const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map(v => (v + 0.5) / 16);
  const hex = (h) => { h = h.replace('#', ''); if (h.length === 3) h = [...h].map(c => c + c).join(''); const n = parseInt(h, 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
  const ramp = (...cs) => cs.map(hex);
  const R = {
    fire: ramp('#5a1a14', '#a8321c', '#e0602a', '#ff9a3d', '#ffd36b', '#fff6d0'),
    spark: ramp('#7a2a10', '#d0542a', '#ff9a3d', '#ffe27a', '#ffffff'),
    gold: ramp('#6a3a10', '#b8701c', '#f0a92a', '#ffd84a', '#fff4b0'),
    snow: ramp('#9fb6d8', '#d6e4f6', '#ffffff'),
    petal: ramp('#d97aa6', '#ffb1d0', '#ffe2ef'),
    dust: ramp('#b07040', '#e0a070', '#ffd9a0'),
    leaf: ramp('#3e8f35', '#8ee05a', '#d8f08a'),
    firefly: ramp('#5a7a1a', '#9ad02a', '#d6ff5a', '#f4ffb8'),
    spore: ramp('#4a7a5a', '#9fd8c4', '#c8f08a', '#f0ffd0'),
    smoke: ramp('#2a2433', '#4a4458', '#6e6880'),
    holy: ramp('#4a3a8a', '#8f7ae0', '#c8b8ff', '#ffffff'),
  };
  const CONFETTI = ['#ff5a6e', '#ffd23f', '#5cbf48', '#3d7fe0', '#b58cff', '#ff9a3d'].map(hex);
  const clamp = (v, a = 0, b = 1) => v < a ? a : v > b ? b : v;
  const rnd = (a, b) => a + Math.random() * (b - a);
  const still = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 한 판(캔버스 하나): 칸 단위 좌표로 입자·빛을 그림. CSS 좌표(px)로 받아 4로 나눔
  function Layer(host, { fixed = false, z = 'auto', cls = '' } = {}) {
    const cv = document.createElement('canvas');
    cv.className = 'pfx-layer ' + cls;
    cv.setAttribute('aria-hidden', 'true');
    Object.assign(cv.style, { position: fixed ? 'fixed' : 'absolute', left: 0, top: 0, width: '100%', height: '100%', pointerEvents: 'none', imageRendering: 'pixelated', zIndex: z });
    host.appendChild(cv);
    // 빛은 따로 한 장: 화면(screen) 혼합이라 어두운 배경 위에서도 탁해지지 않고 정말 밝아짐
    const lcv = cv.cloneNode();
    lcv.className = 'pfx-light ' + cls;
    lcv.style.mixBlendMode = 'screen';
    host.appendChild(lcv);
    const ctx = cv.getContext('2d'), lctx = lcv.getContext('2d');
    let W = 0, H = 0, img = null, limg = null, col = null, lr = null, lg = null, lb = null;
    const parts = [], lights = [], emitters = [], steady = [];
    let raf = 0, last = 0, acc = 0, clock = 0;

    const size = () => {
      const r = fixed ? { width: innerWidth, height: innerHeight } : host.getBoundingClientRect();
      const w = Math.max(1, Math.ceil(r.width / PX)), h = Math.max(1, Math.ceil(r.height / PX));
      if (w === W && h === H) return false;
      const grew = w * h > W * H * 2;
      W = w; H = h; cv.width = lcv.width = W; cv.height = lcv.height = H;
      img = ctx.createImageData(W, H); limg = lctx.createImageData(W, H); col = new Float32Array(W * H * 4);
      lr = new Float32Array(W * H); lg = new Float32Array(W * H); lb = new Float32Array(W * H);
      // 숨겨져 있다가(크기 0) 나타나면 날림 효과를 새 크기에 맞춰 다시 채움
      if (grew && emitters.length) prewarm();
      return true;
    };
    const prewarm = () => { for (let i = 0; i < 360; i++) step(1 / 30); };
    // 색 칸 하나 (a < 1 이면 반투명으로 겹침)
    const dot = (x, y, c, a = 1) => {
      x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H || a <= 0) return;
      const i = (y * W + x) * 4, k = col[i + 3], na = a + k * (1 - a);
      col[i] = (c[0] * a + col[i] * k * (1 - a)) / na; col[i + 1] = (c[1] * a + col[i + 1] * k * (1 - a)) / na;
      col[i + 2] = (c[2] * a + col[i + 2] * k * (1 - a)) / na; col[i + 3] = na;
    };
    // 빛: 옅고 넓은 웅덩이(디더 계단) + 뜨거운 심
    const glow = (x, y, rad, c, k) => {
      if (k <= 0.01 || rad < 1) return;
      const x0 = Math.max(0, (x - rad) | 0), x1 = Math.min(W - 1, (x + rad) | 0), y0 = Math.max(0, (y - rad) | 0), y1 = Math.min(H - 1, (y + rad) | 0);
      for (let yy = y0; yy <= y1; yy++) for (let xx = x0; xx <= x1; xx++) {
        const d = Math.hypot(xx + 0.5 - x, yy + 0.5 - y) / rad; if (d >= 1) continue;
        let v = (1 - d) * (1 - d) * k;
        // 네 계단 띠로 나누고 띠 경계만 바이어 디더로 살짝 섞음 → 점이 흩뿌려지지 않는 도트 빛무리
        v = Math.floor(v * 4 + 0.5 + (BAYER[(yy & 3) * 4 + (xx & 3)] - 0.5) * 0.4) / 4;
        if (v <= 0) continue;
        const i = yy * W + xx; lr[i] += c[0] * v; lg[i] += c[1] * v; lb[i] += c[2] * v;
      }
    };
    const line = (x0, y0, x1, y1, head, tail, a) => {
      const n = Math.max(1, Math.ceil(Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0))));
      for (let i = 0; i <= n; i++) { const u = i / n; dot(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, u < 0.5 ? head : tail, a); }
    };

    function frame(now) {
      raf = 0;
      const busy = parts.length || lights.length || emitters.length || steady.length;
      // 안 보이는 동안은 멈춰 있다가 가끔 다시 봄 (할 일이 없으면 완전히 멈춤)
      if (document.hidden || !cv.isConnected || !cv.offsetParent && !fixed) { last = 0; if (busy) wake(500); return; }
      size();
      let dt = last ? Math.min(0.1, (now - last) / 1000) : 1 / 60; last = now; clock += dt;
      // 120Hz로 쪼개 시뮬레이션
      acc += dt; const h = 1 / 120;
      while (acc >= h) { acc -= h; step(h); }
      acc = Math.min(acc, h);
      // 30fps로만 다시 그림 (도트 애니메이션 속도)
      if (now - (frame.drawn || 0) >= 33) { frame.drawn = now; draw(); }
      if (parts.length || lights.length || emitters.length || steady.length) raf = requestAnimationFrame(frame);
      else { ctx.clearRect(0, 0, W, H); lctx.clearRect(0, 0, W, H); last = 0; }
    }
    const wake = (ms) => setTimeout(() => { if (!raf) raf = requestAnimationFrame(frame); }, ms);
    const kick = () => { if (!raf) raf = requestAnimationFrame(frame); };

    function step(h) {
      for (const e of emitters) { e.acc += e.rate * h; while (e.acc >= 1) { e.acc--; e.spawn(W, H); } }
      for (let i = parts.length - 1; i >= 0; i--) {
        const p = parts[i]; p.age += h;
        if (p.age >= p.life || p.y > H + 20 || p.y < -40 || p.x < -40 || p.x > W + 40) { parts.splice(i, 1); continue; }
        const dr = Math.pow(p.drag, h * 60);
        p.vx *= dr; p.vy = p.vy * dr + p.g * h;
        if (p.sway) p.vx += Math.sin(clock * p.sway + p.ph) * p.swayA * h;
        if (p.wander) { p.vx += (Math.random() - 0.5) * p.wander * h; p.vy += (Math.random() - 0.5) * p.wander * h; }
        p.px = p.x; p.py = p.y; p.x += p.vx * h; p.y += p.vy * h;
      }
      for (let i = lights.length - 1; i >= 0; i--) { const l = lights[i]; l.age += h; if (l.age >= l.life) lights.splice(i, 1); }
    }

    function draw() {
      col.fill(0); lr.fill(0); lg.fill(0); lb.fill(0);
      for (const s of steady) s(glow, dot, clock, W, H);
      for (const l of lights) { const u = l.age / l.life, k = l.k * (u < 0.08 ? u / 0.08 : (1 - u) * (1 - u)); glow(l.x, l.y, l.r, l.c, k); glow(l.x, l.y, l.r * 0.35, [255, 255, 255], k * 0.6); }
      for (const p of parts) {
        const u = p.age / p.life, c = p.ramp, top = c.length - 1;
        // 수명 따라 램프를 내려옴 (갓 생기면 가장 밝은 색)
        const ci = clamp(Math.round(top * (p.cool ? 1 - u : p.ci ?? 1)), 0, top), cc = c[ci] ?? c[top];
        const a = p.fade ? clamp((1 - u) / 0.35) * (p.a ?? 1) : (p.a ?? 1);
        let k = 1; if (p.blink) { const b = (clock * p.blink + p.ph) % 1; k = b < 0.15 ? b / 0.15 : b < 0.35 ? 1 : b < 0.7 ? 1 - (b - 0.35) / 0.35 : 0; }
        if (p.kind === 'streak') {
          const sp = Math.hypot(p.vx, p.vy), len = Math.min(5, sp / 40);
          line(p.x, p.y, p.x - p.vx / (sp || 1) * len, p.y - p.vy / (sp || 1) * len, cc, c[Math.max(0, ci - 2)], a);
        } else if (p.kind === 'coin') {
          const turn = Math.abs(Math.sin(clock * 9 + p.ph)) > 0.45; // 동전이 돌면서 폭이 바뀜
          const x = p.x | 0, y = p.y | 0, G = R.gold;
          if (turn) { dot(x - 1, y, G[2], a); dot(x, y, G[3], a); dot(x + 1, y, G[2], a); dot(x - 1, y + 1, G[1], a); dot(x, y + 1, G[2], a); dot(x + 1, y + 1, G[1], a); dot(x, y - 1, G[4], a); dot(x, y + 2, G[0], a); }
          else { dot(x, y - 1, G[4], a); dot(x, y, G[3], a); dot(x, y + 1, G[2], a); dot(x, y + 2, G[0], a); }
          glow(p.x, p.y, 4, [255, 200, 80], 0.35 * a);
        } else if (p.kind === 'flake') { // 꽃잎·색종이·잎: 2칸짜리, 뒤집히며 1칸이 됨
          const flip = Math.sin(clock * (p.spin || 6) + p.ph) > 0;
          dot(p.x, p.y, cc, a); if (flip) dot(p.x + 1, p.y, c[Math.max(0, ci - 1)], a); else dot(p.x, p.y + 1, c[Math.max(0, ci - 1)], a);
        } else if (p.kind === 'puff') { // 연기·먼지: 커졌다 옅어지는 반투명 덩어리 (윗가장자리가 밝음)
          const r = p.r0 + (p.r1 - p.r0) * Math.sqrt(u), aa = a * 0.55;
          for (let yy = -r; yy <= r; yy++) for (let xx = -r; xx <= r; xx++) if (xx * xx + yy * yy <= r * r) dot(p.x + xx, p.y + yy, yy < -r * 0.4 ? c[top] : yy > r * 0.3 ? c[0] : c[Math.min(top, 1)], aa);
        } else if (p.kind === 'star') { // 반짝임: 십자가 커졌다 줄어듦
          const s = Math.sin(Math.PI * u), n = Math.round(s * p.r);
          dot(p.x, p.y, [255, 255, 255], 1);
          for (let i = 1; i <= n; i++) { const cc2 = i === n ? c[Math.max(0, top - 2)] : c[top - 1] ?? c[top]; dot(p.x + i, p.y, cc2); dot(p.x - i, p.y, cc2); dot(p.x, p.y + i, cc2); dot(p.x, p.y - i, cc2); }
          if (n >= 3) { dot(p.x + 1, p.y + 1, c[top]); dot(p.x - 1, p.y - 1, c[top]); dot(p.x + 1, p.y - 1, c[top]); dot(p.x - 1, p.y + 1, c[top]); }
          glow(p.x, p.y, p.r * 2.2, c[top], 0.5 * s);
        } else {
          if (k > 0.05) { dot(p.x, p.y, cc, a * (p.blink ? Math.max(0.25, k) : 1)); if (p.big) { dot(p.x + 1, p.y, cc, a); dot(p.x, p.y + 1, c[Math.max(0, ci - 1)], a); dot(p.x + 1, p.y + 1, c[Math.max(0, ci - 1)], a); } }
        }
        if (p.light) glow(p.x, p.y, p.light, c[top], (p.lk ?? 0.5) * a * (p.blink ? k : 1) * (p.cool ? 1 - u * 0.6 : 1));
      }
      // 색 한 장, 빛 한 장 (빛 = 더해지는 밝기, 안 비추는 칸은 투명)
      const d = img.data, e = limg.data, n = W * H;
      for (let i = 0; i < n; i++) {
        const j = i * 4, a = col[j + 3];
        if (a > 0) { d[j] = col[j]; d[j + 1] = col[j + 1]; d[j + 2] = col[j + 2]; d[j + 3] = a * 255; } else d[j + 3] = 0;
        if (lr[i] || lg[i] || lb[i]) { e[j] = lr[i]; e[j + 1] = lg[i]; e[j + 2] = lb[i]; e[j + 3] = 255; } else e[j + 3] = 0;
      }
      ctx.putImageData(img, 0, 0);
      lctx.putImageData(limg, 0, 0);
    }

    const P = (o) => { parts.push(Object.assign({ x: 0, y: 0, vx: 0, vy: 0, g: 0, drag: 1, age: 0, life: 1, ramp: R.spark, ph: Math.random() * 7, fade: true, cool: false }, o)); };
    const toPx = (v) => v / PX;

    // 터지는 이펙트들 (x, y = 판 안의 CSS 좌표)
    const BURSTS = {
      // 타격: 하얀 섬광 + 사방으로 튀는 2톤 불꽃 줄 + 번쩍 빛났다 빨리 꺼지는 빛
      hit(x, y, o = {}) {
        const c = o.ramp || R.spark, n = o.n || 12;
        lights.push({ x, y, r: 14 * (o.s || 1), c: c[c.length - 2], k: 1, age: 0, life: 0.35 });
        P({ kind: 'star', x, y, r: Math.round(4 * (o.s || 1)), life: 0.22, ramp: c, fade: false });
        for (let i = 0; i < n; i++) { const t = Math.random() * 6.283, v = rnd(60, 190) * (o.s || 1); P({ kind: 'streak', x, y, vx: Math.cos(t) * v, vy: Math.sin(t) * v - 30, g: 220, drag: 0.9, life: rnd(0.25, 0.55), ramp: c, cool: true, light: 3, lk: 0.35 }); }
      },
      // 쓰러짐: 땅에서 피어오르는 먼지 + 몇 개 튀는 동전
      poof(x, y, o = {}) {
        for (let i = 0; i < 7; i++) P({ kind: 'puff', x: x + rnd(-6, 6), y: y - rnd(0, 3), vx: rnd(-25, 25), vy: rnd(-22, -6), drag: 0.93, life: rnd(0.6, 1.0), r0: 1, r1: rnd(3, 5), ramp: o.ramp || R.smoke });
        if (o.coins !== false) BURSTS.coins(x, y - 6, { n: 4 });
      },
      // 동전 분수
      coins(x, y, o = {}) {
        for (let i = 0; i < (o.n || 10); i++) P({ kind: 'coin', x: x + rnd(-3, 3), y, vx: rnd(-70, 70), vy: rnd(-200, -110), g: 520, drag: 0.995, life: rnd(0.8, 1.2) });
        for (let i = 0; i < 4; i++) setTimeout(() => P({ kind: 'star', x: x + rnd(-20, 20), y: y - rnd(4, 24), r: 3, life: 0.4, ramp: R.gold, fade: false }), i * 90);
        lights.push({ x, y, r: 16, c: [255, 200, 90], k: 0.7, age: 0, life: 0.5 });
      },
      // 색종이: 위로 터졌다가 흔들리며 내려옴
      confetti(x, y, o = {}) {
        for (let i = 0; i < (o.n || 40); i++) { const t = -Math.PI / 2 + rnd(-1.1, 1.1), v = rnd(120, 260), c = CONFETTI[i % CONFETTI.length]; P({ kind: 'flake', x, y, vx: Math.cos(t) * v, vy: Math.sin(t) * v, g: 160, drag: 0.94, life: rnd(1.4, 2.2), ramp: [c.map(v => v * 0.6), c], ci: 1, sway: rnd(4, 7), swayA: 60, spin: rnd(5, 10) }); }
        BURSTS.hit(x, y, { n: 8, s: 0.8 });
      },
      // 반짝: 작은 별 하나 (제목·버튼 위 윤기)
      glint(x, y, o = {}) { P({ kind: 'star', x, y, r: o.r || 3, life: o.life || 0.45, ramp: o.ramp || R.gold, fade: false }); },
      // 모아지는 빛: 둥글게 퍼지는 불꽃과 위로 오르는 빛 알갱이 (버튼 눌렀을 때)
      burst(x, y, o = {}) {
        const c = o.ramp || R.gold;
        lights.push({ x, y, r: 18, c: c[c.length - 2], k: 0.9, age: 0, life: 0.45 });
        for (let i = 0; i < 16; i++) { const t = i / 16 * 6.283, v = rnd(110, 150); P({ kind: 'streak', x, y, vx: Math.cos(t) * v, vy: Math.sin(t) * v, drag: 0.86, life: 0.4, ramp: c, cool: true }); }
        for (let i = 0; i < 8; i++) P({ x: x + rnd(-10, 10), y: y + rnd(-4, 4), vy: rnd(-60, -30), drag: 0.97, life: rnd(0.6, 1), ramp: c, cool: true, light: 3, lk: 0.5 });
      },
      // 신성한 빛기둥 + 위로 오르는 빛 (히든 스킬·레어 등장)
      holy(x, y, o = {}) {
        const c = o.ramp || R.holy;
        lights.push({ x, y, r: 30, c: c[c.length - 2], k: 1, age: 0, life: 1.1 });
        for (let i = 0; i < 26; i++) P({ x: x + rnd(-22, 22), y: y + rnd(-6, 14), vy: rnd(-90, -40), drag: 0.985, life: rnd(0.9, 1.6), ramp: c, cool: true, light: 3, lk: 0.6, big: Math.random() < 0.3 });
        for (let i = 0; i < 6; i++) setTimeout(() => P({ kind: 'star', x: x + rnd(-36, 36), y: y + rnd(-30, 10), r: 4, life: 0.5, ramp: c, fade: false }), i * 120);
      },
    };

    // 계속 내리는 날림 효과 (테마별)
    const AMBIENT = {
      snow: (W, H) => P({ kind: Math.random() < 0.3 ? 'flake' : undefined, x: rnd(-10, W), y: -2, vx: rnd(4, 14), vy: rnd(14, 30), life: 30, ramp: R.snow, ci: 1, sway: rnd(0.6, 1.4), swayA: 10, fade: false, big: Math.random() < 0.25 }),
      petal: (W, H) => P({ kind: 'flake', x: -4, y: rnd(0, H * 0.75), vx: rnd(26, 46), vy: rnd(2, 10), life: 30, ramp: R.petal, ci: 1, sway: rnd(1.5, 3), swayA: 22, spin: rnd(4, 8), fade: false }),
      dust: (W, H) => P({ x: -4, y: rnd(0, H * 0.8), vx: rnd(40, 80), vy: rnd(-4, 8), life: 30, ramp: R.dust, ci: Math.random() < 0.5 ? 1 : 0.5, sway: rnd(2, 4), swayA: 16, fade: false, big: Math.random() < 0.3 }),
      leaf: (W, H) => P({ kind: 'flake', x: -4, y: rnd(0, H * 0.6), vx: rnd(22, 40), vy: rnd(6, 16), life: 30, ramp: R.leaf, ci: Math.random(), sway: rnd(1, 2.5), swayA: 26, spin: rnd(3, 6), fade: false }),
      firefly: (W, H, g) => P({ x: rnd(0, W), y: H - g - rnd(4, 40), life: rnd(5, 9), ramp: R.firefly, ci: 0.75, wander: 120, drag: 0.97, blink: rnd(0.3, 0.6), light: 6, lk: 0.7 }),
      ember: (W, H, g) => P({ x: rnd(0, W), y: H - g + rnd(0, 6), vx: rnd(-6, 6), vy: rnd(-34, -16), life: rnd(3, 6), ramp: R.fire, cool: true, sway: rnd(1, 3), swayA: 18, light: 4, lk: 0.55, big: Math.random() < 0.2 }),
      // 등불 아래 떠도는 금빛 먼지 (길드 실내)
      mote: (W, H) => P({ x: rnd(0, W), y: rnd(H * 0.05, H * 0.75), vx: rnd(-3, 3), vy: rnd(-4, 2), life: rnd(4, 7), ramp: R.gold, ci: 0.75, wander: 20, drag: 0.98, blink: rnd(0.15, 0.3), light: 2, lk: 0.35 }),
      spore: (W, H, g) => P({ x: rnd(0, W), y: H - g + rnd(0, 6), vx: rnd(-4, 4), vy: rnd(-16, -8), life: rnd(5, 8), ramp: R.spore, ci: 0.7, sway: rnd(0.6, 1.4), swayA: 8, light: 4, lk: 0.35, big: Math.random() < 0.25 }),
    };
    const RATE = { mote: 3, snow: 7, petal: 2.2, dust: 3, leaf: 1.8, firefly: 1.6, ember: 3.5, spore: 2.4 };

    size();
    addEventListener('resize', size);
    return {
      canvas: cv, canvases: [cv, lcv],
      // kind 이펙트를 (x, y)에 (판 기준 CSS px)
      pop(kind, x, y, o) { if (still() && kind !== 'glint') return; size(); BURSTS[kind]?.(toPx(x), toPx(y), o || {}); kick(); },
      // 날림 효과 켜기/끄기. ground = 바닥 높이(px, 반딧불·불씨가 오르는 자리)
      ambient(kind, { ground = 0, rate } = {}) {
        emitters.length = 0;
        if (!kind || !AMBIENT[kind] || still()) return;
        size(); const g = toPx(ground);
        emitters.push({ rate: rate ?? RATE[kind] ?? 2, acc: 0, spawn: (W, H) => AMBIENT[kind](W, H, g) });
        // 처음부터 화면에 퍼져 있게 미리 흘려 둠
        prewarm();
        kick();
      },
      // 매 프레임 그리는 고정 빛 (횃불 등): fn(glow, dot, t, W, H)
      steady(fn) { steady.length = 0; if (fn) { steady.push(fn); kick(); } },
      clear() { parts.length = 0; lights.length = 0; emitters.length = 0; steady.length = 0; },
      size, PX, R,
    };
  }

  let overlay = null;
  window.PixelFX = {
    Layer, ramps: R, hex,
    // 화면 전체(뷰포트 좌표) 위에 한 번 터뜨림: 보상·축하용
    pop(kind, x, y, o) {
      if (!overlay) overlay = Layer(document.body, { fixed: true, z: 9999, cls: 'pfx-overlay' });
      overlay.pop(kind, x, y, o);
    },
    // 요소 가운데에서 터뜨림
    popAt(el, kind, o, { fx = 0.5, fy = 0.5 } = {}) {
      const r = el?.getBoundingClientRect?.(); if (!r || !r.width) return;
      PixelFX.pop(kind, r.left + r.width * fx, r.top + r.height * fy, o);
    },
  };
})();

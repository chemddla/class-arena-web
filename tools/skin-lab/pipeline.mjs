// 학생 디자인 → 게임 스프라이트 시트 (제미나이로 그리고, 칸·발 위치는 여기서 맞춤)
//   1) refine: 학생 그림 + 그 직업의 기존 외형 → 게임 그림체로 다듬은 기준 캐릭터 한 장
//   2) motion: 기준 캐릭터 + 기존 시트의 동작 묶음(대기·걷기·공격…) → 같은 동작을 하는 그림 한 줄
//   3) assemble: 배경을 지우고 포즈를 하나씩 잘라 0번 외형과 같은 칸 크기·키·발 위치로 맞춰 시트 한 장으로
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const INDEX_HTML = path.join(ROOT, 'index.html');
const MERC_DIR = path.join(ROOT, 'assets/sprites/merc');

export const JOBS = {
  warrior: { name: '전사', look: 'a warrior with a one-handed sword and a cape' },
  mage:    { name: '마법사', look: 'a mage with a wizard hat and a magic staff' },
  healer:  { name: '성녀', look: 'a holy priestess (healer) with a holy staff' },
  archer:  { name: '궁수', look: 'an archer with a bow' },
  rogue:   { name: '도적', look: 'a hooded rogue (ninja-like) with daggers' },
  knight:  { name: '기사', look: 'a plate-armored knight with a big tower shield and a war hammer' },
  lancer:  { name: '창병', look: 'a lancer with a long spear' }
};
const ANIM_HINT = {
  idle: 'standing idle (breathing)', walk: 'walking cycle', attack: 'basic attack swing', thrust: 'spear thrust attack',
  skill: 'casting a skill', hurt: 'getting hit (flinch)', death: 'falling down and dying (last pose lying on the ground)',
  whirl: 'spinning slash', shout: 'battle shout', charge: 'charging forward', quake: 'jumping and slamming the ground',
  taunt: 'taunting', defense: 'defensive guard stance', rend: 'slashing', throw: 'throwing', seal: 'ninja hand seal',
  dash: 'crouch and dash', pierce: 'piercing thrust', javelin: 'throwing a javelin', rampage: 'flurry of spear strikes'
};

// ---------- index.html에서 직업별 0번 외형 정의 읽기 ----------
function readObjectLiteral(src, start) {
  let depth = 0, i = start, q = null;
  for (; i < src.length; i++) {
    const c = src[i];
    if (q) { if (c === '\\') i++; else if (c === q) q = null; continue; }
    if (c === "'" || c === '"' || c === '`') q = c;
    else if (c === '/' && src[i + 1] === '/') i = src.indexOf('\n', i);
    else if (c === '{') depth++;
    else if (c === '}' && --depth === 0) return src.slice(start, i + 1);
  }
  throw new Error('정의가 끝나지 않음');
}
export function loadBaseDef(job) {
  const html = fs.readFileSync(INDEX_HTML, 'utf8');
  const m = new RegExp(`(?:\\n\\s*${job}_0:\\s*|MERC_SPRITE_DEFS\\.${job}_0\\s*=\\s*)\\{`).exec(html);
  if (!m) throw new Error(`${job}_0 정의를 index.html에서 찾지 못함`);
  return new Function(`return (${readObjectLiteral(html, m.index + m[0].length - 1)})`)();
}

// 같은 그림을 여러 동작이 같이 쓰므로, 칸마다 그 칸을 가진 가장 긴 동작에 한 번만 배정해 묶음을 만듦
// 한 번에 그리는 포즈가 너무 많으면 흐트러지므로 4칸씩 나눔
export function motionGroups(def) {
  const owner = {};
  const names = Object.keys(def.anims);
  for (let f = 0; f < def.count; f++) {
    let best = null;
    names.forEach(n => {
      const len = new Set(def.anims[n]).size;
      if (def.anims[n].includes(f) && (!best || len > best.len)) best = { n, len };
    });
    if (best) owner[f] = best.n;
  }
  const groups = [];
  names.forEach(n => {
    const frames = Object.keys(owner).map(Number).filter(f => owner[f] === n).sort((a, b) => a - b);
    for (let i = 0; i < frames.length; i += 4) {
      const part = frames.slice(i, i + 4);
      groups.push({ key: frames.length > 4 ? `${n}${i / 4 + 1}` : n, anim: n, frames: part });
    }
  });
  return groups;
}

// ---------- 픽셀 도구 ----------
async function rawOf(input) {
  const { data, info } = await sharp(input).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  return { data, w: info.width, h: info.height };
}
function bboxOf(img, x0 = 0, y0 = 0, w = img.w, h = img.h, minAlpha = 16) {
  let minX = Infinity, minY = Infinity, maxX = -1, maxY = -1;
  for (let y = y0; y < y0 + h; y++) for (let x = x0; x < x0 + w; x++) {
    if (img.data[(y * img.w + x) * 4 + 3] >= minAlpha) {
      if (x < minX) minX = x; if (x > maxX) maxX = x; if (y < minY) minY = y; if (y > maxY) maxY = y;
    }
  }
  return maxX < 0 ? null : { x: minX, y: minY, w: maxX - minX + 1, h: maxY - minY + 1 };
}
const hex = c => '#' + c.map(v => v.toString(16).padStart(2, '0')).join('');

// 디자인에 거의 안 쓰인 배경색을 고름 (제미나이에게 이 색으로 배경을 칠해 달라고 함)
const CHROMA = [[255, 0, 255], [0, 255, 0], [0, 200, 255]];
export async function pickChroma(imagePath) {
  const img = await rawOf(await sharp(imagePath).resize(128, 128, { fit: 'inside' }).toBuffer());
  let best = CHROMA[0], bestD = -1;
  CHROMA.forEach(c => {
    let near = Infinity;
    for (let i = 0; i < img.data.length; i += 4) {
      if (img.data[i + 3] < 128) continue;
      const d = Math.hypot(img.data[i] - c[0], img.data[i + 1] - c[1], img.data[i + 2] - c[2]);
      if (d < near) near = d;
    }
    if (near > bestD) { bestD = near; best = c; }
  });
  return best;
}

// 테두리의 가장 흔한 색을 실제 배경색으로 보고 그 색과 가까운 픽셀을 투명하게
function removeBackground(img) {
  const counts = new Map();
  const add = (x, y) => {
    const i = (y * img.w + x) * 4;
    const k = (img.data[i] >> 4) << 8 | (img.data[i + 1] >> 4) << 4 | (img.data[i + 2] >> 4);
    counts.set(k, (counts.get(k) || 0) + 1);
  };
  for (let x = 0; x < img.w; x++) { add(x, 0); add(x, img.h - 1); }
  for (let y = 0; y < img.h; y++) { add(0, y); add(img.w - 1, y); }
  const top = [...counts.entries()].sort((a, b) => b[1] - a[1])[0][0];
  // 그 칸에 속한 테두리 픽셀의 평균색
  let sum = [0, 0, 0], n = 0;
  const acc = (x, y) => {
    const i = (y * img.w + x) * 4;
    const k = (img.data[i] >> 4) << 8 | (img.data[i + 1] >> 4) << 4 | (img.data[i + 2] >> 4);
    if (k === top) { sum[0] += img.data[i]; sum[1] += img.data[i + 1]; sum[2] += img.data[i + 2]; n++; }
  };
  for (let x = 0; x < img.w; x++) { acc(x, 0); acc(x, img.h - 1); }
  const bg = sum.map(v => v / n);
  for (let i = 0; i < img.data.length; i += 4) {
    const d = Math.hypot(img.data[i] - bg[0], img.data[i + 1] - bg[1], img.data[i + 2] - bg[2]);
    if (d < 70) img.data[i + 3] = 0;
    else if (d < 110) { // 경계의 배경색 번짐을 줄임
      const k = (d - 70) / 40;
      for (let c = 0; c < 3; c++) img.data[i + c] = Math.max(0, Math.min(255, Math.round((img.data[i + c] - bg[c] * (1 - k)) / k)));
    }
  }
  return img;
}

// 투명 배경 그림에서 포즈 n개를 왼쪽부터 잘라 냄 (빈 세로줄로 나누고, 개수가 안 맞으면 틈이 좁은 것부터 합치거나 똑같이 나눔)
function splitPoses(img, n) {
  const col = new Array(img.w).fill(0);
  for (let y = 0; y < img.h; y++) for (let x = 0; x < img.w; x++) if (img.data[(y * img.w + x) * 4 + 3] >= 128) col[x]++;
  let runs = [];
  for (let x = 0; x < img.w; x++) {
    if (col[x] >= 2) { if (runs.length && runs[runs.length - 1].end === x - 1) runs[runs.length - 1].end = x; else runs.push({ start: x, end: x }); }
  }
  const minW = img.w * 0.02;
  runs = runs.filter(r => r.end - r.start + 1 >= minW || col.slice(r.start, r.end + 1).reduce((a, b) => a + b, 0) > 200);
  while (runs.length > n) {
    let gi = 0, gap = Infinity;
    for (let i = 0; i < runs.length - 1; i++) { const g = runs[i + 1].start - runs[i].end; if (g < gap) { gap = g; gi = i; } }
    runs.splice(gi, 2, { start: runs[gi].start, end: runs[gi + 1].end });
  }
  if (runs.length < n) {
    const w = img.w / n;
    runs = Array.from({ length: n }, (_, i) => ({ start: Math.round(i * w), end: Math.round((i + 1) * w) - 1 }));
  }
  return runs.map(r => bboxOf(img, r.start, 0, r.end - r.start + 1, img.h, 128)).map((b, i) => b || { x: runs[i].start, y: 0, w: 1, h: 1 });
}

// ---------- 제미나이 ----------
const API = 'https://generativelanguage.googleapis.com/v1beta';
let chosenModel = null;
export function apiKey() {
  if (process.env.GEMINI_API_KEY) return process.env.GEMINI_API_KEY;
  const envFile = path.join(ROOT, 'tools/skin-lab/.env');
  if (fs.existsSync(envFile)) {
    const m = /^\s*GEMINI_API_KEY\s*=\s*(.+?)\s*$/m.exec(fs.readFileSync(envFile, 'utf8'));
    if (m) return m[1].replace(/^['"]|['"]$/g, '');
  }
  return '';
}
// GEMINI_IMAGE_MODEL이 없으면 이 키로 쓸 수 있는 이미지 모델 중 가장 좋아 보이는 것 (pro > flash, 버전 높은 것)
export async function imageModel() {
  if (process.env.GEMINI_IMAGE_MODEL) return process.env.GEMINI_IMAGE_MODEL;
  if (chosenModel) return chosenModel;
  const res = await fetch(`${API}/models?pageSize=1000`, { headers: { 'x-goog-api-key': apiKey() } });
  if (!res.ok) throw new Error(`모델 목록을 못 받음 (${res.status}): ${(await res.text()).slice(0, 300)}`);
  const list = ((await res.json()).models || [])
    .filter(m => /gemini.*image/.test(m.name) && (m.supportedGenerationMethods || []).includes('generateContent'))
    .map(m => m.name.replace(/^models\//, ''));
  if (!list.length) throw new Error('이 API 키로 쓸 수 있는 제미나이 이미지 모델이 없음');
  const score = n => (parseFloat((/gemini-(\d+(?:\.\d+)?)/.exec(n) || [])[1]) || 0) * 10 + (/pro/.test(n) ? 5 : 0) - (/lite/.test(n) ? 3 : 0) - (/preview|exp/.test(n) ? 1 : 0);
  chosenModel = list.sort((a, b) => score(b) - score(a))[0];
  return chosenModel;
}
async function geminiImage(parts, aspectRatio) {
  const key = apiKey();
  if (!key) throw new Error('GEMINI_API_KEY가 없음 (환경변수나 tools/skin-lab/.env에 넣어 주세요)');
  const model = await imageModel();
  const body = cfg => JSON.stringify({ contents: [{ role: 'user', parts }], generationConfig: { responseModalities: ['TEXT', 'IMAGE'], ...cfg } });
  let res = await fetch(`${API}/models/${model}:generateContent`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', 'x-goog-api-key': key }, body: body({ imageConfig: { aspectRatio } })
  });
  if (res.status === 400) { // 비율 지정을 모르는 모델이면 빼고 다시
    res = await fetch(`${API}/models/${model}:generateContent`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-goog-api-key': key }, body: body({}) });
  }
  if (!res.ok) throw new Error(`제미나이 오류 ${res.status}: ${(await res.text()).slice(0, 400)}`);
  const json = await res.json();
  const cand = (json.candidates || [])[0];
  const out = cand && cand.content && (cand.content.parts || []).find(p => p.inlineData || p.inline_data);
  if (!out) {
    const why = (json.promptFeedback && json.promptFeedback.blockReason) || (cand && cand.finishReason) || '';
    const text = cand && cand.content ? (cand.content.parts || []).map(p => p.text).filter(Boolean).join(' ') : '';
    throw new Error(`제미나이가 그림을 돌려주지 않음 ${why} ${text}`.trim());
  }
  return { buffer: Buffer.from((out.inlineData || out.inline_data).data, 'base64'), model };
}
const imgPart = async (buf, mime = 'image/png') => ({ inline_data: { mime_type: mime, data: (await sharp(buf).png().toBuffer()).toString('base64') } });

// 기존 시트의 칸들을 잘라 배경색 위에 크게 이어 붙인 참고 그림
export async function referenceStrip(sheetPath, def, frames, chroma, scale = 4) {
  const sheet = await rawOf(sheetPath);
  const boxes = frames.map(f => bboxOf(sheet, f * def.cellW, 0, def.cellW, def.cellH));
  const u = boxes.filter(Boolean).reduce((a, b) => ({ y0: Math.min(a.y0, b.y), y1: Math.max(a.y1, b.y + b.h) }), { y0: def.cellH, y1: 0 });
  const pad = 6, cellH = u.y1 - u.y0 + pad * 2;
  const widths = boxes.map(b => (b ? b.w : 10) + pad * 2);
  const W = widths.reduce((a, b) => a + b, 0) + pad * 2 * (frames.length - 1);
  const comps = [];
  let x = 0;
  for (let i = 0; i < frames.length; i++) {
    const b = boxes[i];
    if (b) {
      const tile = await sharp(sheet.data, { raw: { width: sheet.w, height: sheet.h, channels: 4 } })
        .extract({ left: b.x, top: u.y0, width: b.w, height: u.y1 - u.y0 }).png().toBuffer();
      comps.push({ input: tile, left: x + pad, top: pad });
    }
    x += widths[i] + pad * 2;
  }
  const img = await sharp({ create: { width: W, height: cellH, channels: 4, background: { r: chroma[0], g: chroma[1], b: chroma[2], alpha: 1 } } })
    .composite(comps).png().toBuffer();
  return sharp(img).resize(W * scale, cellH * scale, { kernel: 'nearest' }).flatten({ background: hex(chroma) }).png().toBuffer();
}

// 1) 다듬기
export async function refine({ job, title, note, designPath, outPath }) {
  const def = loadBaseDef(job);
  const chroma = await pickChroma(designPath);
  const idle = (def.anims.idle || def.anims.walk)[0];
  const refs = [];
  for (const v of [0, 1, 2]) {
    const p = path.join(MERC_DIR, `${job}_${v}.webp`);
    if (fs.existsSync(p)) refs.push(await referenceStrip(p, def, [idle], chroma));
  }
  const prompt = [
    `You are a pixel-art game sprite artist for a kids' classroom RPG.`,
    `The FIRST image is a student's character design for the job "${JOBS[job].name}" (${JOBS[job].look}).`,
    title ? `The student named it "${title}".` : '',
    note ? `Student's description: "${note}".` : '',
    `The other images are existing sprites of the same job from the game, showing the exact art style, chibi proportions (big head, short body), outline thickness, shading and level of detail.`,
    `Redraw the student's character as ONE new sprite in exactly that game style: full body, facing right, standing idle pose like the reference sprites.`,
    `Keep the student's ideas: colors, outfit, hair, accessories and overall look. Keep it friendly and appropriate for children.`,
    `Hold the job's weapon the same way the reference sprites do, so the existing attack animations still make sense.`,
    `Clean pixel art, crisp edges, no anti-aliased blur, no text, no ground shadow, no border.`,
    `Fill the whole background with the flat solid color ${hex(chroma)} and use that color nowhere on the character.`
  ].filter(Boolean).join('\n');
  const parts = [{ text: prompt }, await imgPart(fs.readFileSync(designPath)), ...(await Promise.all(refs.map(r => imgPart(r))))];
  const { buffer, model } = await geminiImage(parts, '1:1');
  await sharp(buffer).png().toFile(outPath);
  return { chroma: hex(chroma), model };
}

// 2) 동작 한 묶음
export async function motion({ job, group, refinedPath, outPath, chroma }) {
  const def = loadBaseDef(job);
  const c = chroma ? [1, 3, 5].map(i => parseInt(chroma.slice(i, i + 2), 16)) : await pickChroma(refinedPath);
  const strip = await referenceStrip(path.join(MERC_DIR, `${job}_0.webp`), def, group.frames, c);
  const n = group.frames.length;
  const prompt = [
    `You are a pixel-art game sprite animator.`,
    `The FIRST image is our character (the look to keep).`,
    `The SECOND image shows ${n} animation pose${n > 1 ? 's' : ''} of another character of the same job, left to right: "${ANIM_HINT[group.anim] || group.anim}".`,
    `Draw OUR character doing exactly ${n === 1 ? 'that pose' : `these ${n} poses in the same order, side by side in a single row`}.`,
    `Copy each pose's body position, limb angles, weapon position and any effect (glow, shield light, slash trail) from the second image, but keep our character's colors, outfit and face identical in every pose.`,
    `Same size and proportions in every pose, all facing right, feet on the same baseline${n > 1 ? ', with clear empty space between poses so they never touch or overlap' : ''}.`,
    `Clean pixel art in the same style as the first image, no text, no numbers, no grid, no ground shadow.`,
    `Fill the whole background with the flat solid color ${hex(c)}.`
  ].join('\n');
  const parts = [{ text: prompt }, await imgPart(fs.readFileSync(refinedPath)), await imgPart(strip)];
  const aspect = n <= 1 ? '1:1' : n === 2 ? '16:9' : '21:9';
  const { buffer, model } = await geminiImage(parts, aspect);
  await sharp(buffer).png().toFile(outPath);
  return { model };
}

// 3) 시트 조립: groupFiles = { 묶음 key: 그림 경로 }
export async function assemble({ job, groupFiles, outPath }) {
  const def = loadBaseDef(job);
  const base = await rawOf(path.join(MERC_DIR, `${job}_0.webp`));
  const W = def.cellW * def.count, H = def.cellH;
  const out = Buffer.alloc(W * H * 4);
  const filled = new Set();
  const warnings = [];
  for (const g of motionGroups(def)) {
    const file = groupFiles[g.key];
    if (!file || !fs.existsSync(file)) { warnings.push(`${g.key} 그림 없음`); continue; }
    const img = removeBackground(await rawOf(file));
    const poses = splitPoses(img, g.frames.length);
    const baseBoxes = g.frames.map(f => bboxOf(base, f * def.cellW, 0, def.cellW, def.cellH));
    const baseMax = Math.max(...baseBoxes.filter(Boolean).map(b => b.h));
    const genMax = Math.max(...poses.map(p => p.h));
    const k = baseMax / genMax;
    for (let i = 0; i < g.frames.length; i++) {
      const f = g.frames[i], p = poses[i], bb = baseBoxes[i];
      if (!bb) continue;
      const tw = Math.max(1, Math.round(p.w * k)), th = Math.max(1, Math.round(p.h * k));
      const crop = await sharp(img.data, { raw: { width: img.w, height: img.h, channels: 4 } })
        .extract({ left: p.x, top: p.y, width: p.w, height: p.h })
        .resize(tw, th, { kernel: 'lanczos3' }).raw().toBuffer();
      // 발(아래쪽)은 0번 외형 그 칸의 아래쪽에, 가로는 몸 가운데를 맞춤
      const ox = f * def.cellW + Math.round(bb.x - f * def.cellW + bb.w / 2 - tw / 2);
      const oy = bb.y + bb.h - th;
      let clipped = false;
      for (let y = 0; y < th; y++) for (let x = 0; x < tw; x++) {
        const s = (y * tw + x) * 4;
        if (crop[s + 3] < 128) continue; // 도트 그림처럼 반투명 없이
        const X = ox + x, Y = oy + y;
        if (X < f * def.cellW || X >= (f + 1) * def.cellW || Y < 0 || Y >= H) { clipped = true; continue; }
        const d = (Y * W + X) * 4;
        out[d] = crop[s]; out[d + 1] = crop[s + 1]; out[d + 2] = crop[s + 2]; out[d + 3] = 255;
      }
      if (clipped) warnings.push(`${f}번 칸(${g.key}) 일부가 칸 밖이라 잘림`);
      filled.add(f);
    }
  }
  // 어느 동작에도 안 쓰이는 칸은 대기 첫 칸으로 채움
  const idle0 = (def.anims.idle || def.anims.walk)[0];
  for (let f = 0; f < def.count; f++) {
    if (filled.has(f) || !filled.has(idle0)) continue;
    for (let y = 0; y < H; y++) out.copy(out, (y * W + f * def.cellW) * 4, (y * W + idle0 * def.cellW) * 4, (y * W + (idle0 + 1) * def.cellW) * 4);
  }
  await sharp(out, { raw: { width: W, height: H, channels: 4 } }).webp({ lossless: true }).toFile(outPath);
  return { warnings, def };
}

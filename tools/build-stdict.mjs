// 끝말잇기·초성 게임 낱말 사전(assets/dict/ko-words.txt)을 국립국어원 《표준국어대사전》에서 다시 만든다
//   node tools/build-stdict.mjs assets/dict/ko-words.txt
// 원본: spellcheck-ko/korean-dict-nikl-stdict 의 XML 87개(약 460MB)를 하나씩 받아 읽는다 (저장하지 않음)
// 남기는 말: 단어(띄어 쓰는 구 제외) · 명사/대명사/수사 · 2~10글자 한글 · 표준어 뜻이 하나라도 있음
// 빼는 말: 외래어, 외국 원어가 섞인 혼종어(버스표), 소리가 같은 외래어가 있는 말(바이·시소), BLOCK
import fs from 'node:fs';

const out = process.argv[2] || 'assets/dict/ko-words.txt';
const BASE = 'https://raw.githubusercontent.com/spellcheck-ko/korean-dict-nikl-stdict/master/';
const FILES = [];
for (let n = 5000; n < 434240; n += 5000) FILES.push(`${n}.xml`);
FILES.push('434240.xml');
const NOUNS = new Set(['명사', '대명사', '수사']);
const NONSTD = /’의 (방언|북한어|옛말|잘못|비표준어)/;
const BAD_TYPE = new Set(['방언', '북한어', '옛말']);
// 사전엔 한자어로만 있지만 아이들은 영어 감탄사로 쓰는 말
const BLOCK = new Set(['하이', '와우', '오우', '파파']);
const HANGUL = /^[가-힣]{2,10}$/;
const tag = (s, t) => { const m = s.match(new RegExp(`<${t}>(?:<!\\[CDATA\\[)?([\\s\\S]*?)(?:\\]\\]>)?</${t}>`)); return m ? m[1].trim() : ''; };
const allTags = (s, t) => [...s.matchAll(new RegExp(`<${t}>(?:<!\\[CDATA\\[)?([\\s\\S]*?)(?:\\]\\]>)?</${t}>`, 'g'))].map(m => m[1].trim());

const ok = new Set(), foreignAny = new Set();
for (const name of FILES) {
  let xml;
  for (let a = 0; a < 4; a++) {
    try { const r = await fetch(BASE + name); if (!r.ok) throw new Error(r.status); xml = await r.text(); break; }
    catch (e) { if (a === 3) throw e; await new Promise(r => setTimeout(r, 2000)); }
  }
  for (const item of xml.split('<item>').slice(1)) {
    const word = tag(item, 'word').replace(/[\d\-^ ]/g, '');
    if (!HANGUL.test(word) || tag(item, 'word_unit') !== '단어') continue;
    const head = item.split('<pos_info>')[0];
    // 원어 갈래: '한자'·'고유어' 말고 다른 말(영어 등)이 있으면 외래어로 침. '/(병기)'는 한자 병기 표시라 무시
    const langs = allTags(head, 'language_type');
    const foreign = tag(head, 'word_type') === '외래어' || langs.some(l => l && !l.startsWith('/') && l !== '한자' && l !== '고유어' && l !== 'null');
    if (foreign) { foreignAny.add(word); continue; } // 품사와 상관없이 (헬로 같은 감탄사도)
    for (const pi of item.split('<pos_info>').slice(1)) {
      if (!NOUNS.has(tag(pi, 'pos'))) continue;
      const senses = pi.split('<sense_info>').slice(1);
      if (senses.some(s => !BAD_TYPE.has(tag(s, 'type')) && !NONSTD.test(tag(s, 'definition')))) ok.add(word);
    }
  }
  console.log(name, ok.size);
}
const list = [...ok].filter(w => !foreignAny.has(w) && !BLOCK.has(w)).sort();
fs.writeFileSync(out, list.join('\n') + '\n');
console.log(`끝: ${list.length}개`);

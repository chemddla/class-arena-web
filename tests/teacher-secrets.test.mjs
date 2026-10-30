// 교사 PIN·교사 키 확인 코드(index.html의 TeacherSecrets)를 실제 DB 규칙(에뮬레이터)에 대고 시험
// 실행: cd tests && npm test
import { test, before, beforeEach, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { initializeTestEnvironment } from '@firebase/rules-unit-testing';

// index.html은 CRLF 줄바꿈이라, 아래 '\n'으로 끝을 찾는 정규식이 맞도록 LF로 바꿔 읽음
const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8').replace(/\r\n/g, '\n');
const grab = (re) => {
  const m = html.match(re);
  if (!m) throw new Error('index.html에서 코드를 찾지 못함: ' + re);
  return m[0];
};

// 화면 코드에서 필요한 부분만 잘라 쓰기
const source = [
  grab(/function simpleHashString[\s\S]*?\n    }\n/),
  grab(/function hashTeacherPin[\s\S]*?\n    }\n/),
  html.slice(html.indexOf('const TEACHER_SECRET_ITERATIONS'), html.indexOf('let pendingClassSecrets = null;'))
].join('\n');

let env;
let currentDb;
const store = {};
const state = {};
const syncCache = { loaded: true, classCode: null };
const make = new Function('state', 'syncCache', 'RealtimePvpService', 'StudentPw', 'localStorage',
  `${source}\nreturn { TeacherSecrets, teacherPinProof, teacherKeyProof, simpleHashString, hashTeacherPin };`);
const lib = make(
  state, syncCache,
  { initFirebaseClientSafe: () => currentDb },
  { isDenied: (e) => /permission[_ ]denied/i.test(String((e && (e.code || e.message)) || '')) },
  { getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); } }
);

before(async () => {
  const [host, port] = (process.env.FIREBASE_DATABASE_EMULATOR_HOST || '127.0.0.1:9000').split(':');
  env = await initializeTestEnvironment({
    projectId: 'demo-class-arena-client',
    database: { host, port: Number(port), rules: fs.readFileSync(new URL('../database.rules.json', import.meta.url), 'utf8') }
  });
});
after(async () => { await env.cleanup(); });

const TEACHER_KEY = 'TKEY-ABCD-EFGH-JKLM';
const OLD_KEY = 'TKEY-OLDA-OLDB';

beforeEach(async () => {
  await env.clearDatabase();
  Object.keys(store).forEach((k) => delete store[k]);
  lib.TeacherSecrets.pinProof = {};
  lib.TeacherSecrets.keyConfirmed = {};
  lib.TeacherSecrets.keyUnconfirmed = {};
  for (const k of Object.keys(state)) delete state[k];
  currentDb = env.unauthenticatedContext().database(); // 학생 기기처럼 로그인 없이
  await env.withSecurityRulesDisabled(async (ctx) => {
    await ctx.database().ref().set({
      classes: {
        NEW1: { meta: { classCode: 'NEW1', ownerUid: 'teacher', ownerEmail: 't@x.com', createdAt: 1, className: 'N', pinV: 2, keyV: 2 }, students: {} },
        OLD1: {
          meta: {
            classCode: 'OLD1', createdAt: 1, className: 'B',
            teacherPinHash: lib.hashTeacherPin('4321'), teacherKeyHash: lib.simpleHashString(OLD_KEY)
          },
          students: { s1: { id: 's1', name: 's1' } }
        }
      },
      teacherKeys: { [lib.simpleHashString(OLD_KEY)]: { classes: { OLD1: { classCode: 'OLD1', className: 'B' } } } }
    });
  });
});

const setClass = (code, legacy = {}) => {
  state.classCode = code;
  state.className = 'x';
  state.students = [];
  state.legacyPinHash = legacy.pin || '';
  state.legacyKeyHash = legacy.key || '';
  syncCache.classCode = code;
};

test('새 방식 학급: 맞는 PIN·교사 키만 통과, 기본값 1234나 엉뚱한 값은 실패', async () => {
  const [pp, kp] = await Promise.all([lib.teacherPinProof('NEW1', '7777'), lib.teacherKeyProof(TEACHER_KEY)]);
  await env.authenticatedContext('teacher', { email: 't@x.com' }).database().ref().update({
    'classSecrets/NEW1/pin': { [pp]: true },
    'classSecrets/NEW1/key': { [kp]: true },
    [`teacherKeys/${kp}/classes/NEW1`]: { classCode: 'NEW1', className: 'N', studentCount: 0, updatedAt: 1 }
  });
  setClass('NEW1');
  assert.deepEqual(await lib.TeacherSecrets.check('7777'), { pin: true, key: false });
  assert.deepEqual(await lib.TeacherSecrets.check(TEACHER_KEY.toLowerCase()), { pin: false, key: true });
  assert.deepEqual(await lib.TeacherSecrets.check('1234'), { pin: false, key: false });
  assert.deepEqual(await lib.TeacherSecrets.check('TKEY-ZZZZ-ZZZZ-ZZZZ'), { pin: false, key: false });
  assert.deepEqual(await lib.TeacherSecrets.check(''), { pin: false, key: false });
  // 다른 학급의 PIN으로는 통과 못 함 (학급 코드가 증명에 섞여 있음)
  setClass('OLD1');
  assert.equal((await lib.TeacherSecrets.check('7777')).pin, false);
});

test('새 방식 학급: 서버에서 PIN·키 증명 목록을 읽어갈 수 없음', async () => {
  const pp = await lib.teacherPinProof('NEW1', '7777');
  await env.authenticatedContext('teacher', { email: 't@x.com' }).database().ref('classSecrets/NEW1/pin').set({ [pp]: true });
  await assert.rejects(currentDb.ref('classSecrets/NEW1').once('value'));
  await assert.rejects(currentDb.ref('classSecrets/NEW1/pin').once('value'));
  const meta = (await currentDb.ref('classes/NEW1/meta').once('value')).val();
  assert.equal(JSON.stringify(meta).includes('sh_'), false);
});

test('예전 방식 학급: 맞는 PIN으로 들어오면 새 방식으로 옮기고 서버의 약한 해시를 지움', async () => {
  const meta0 = (await currentDb.ref('classes/OLD1/meta').once('value')).val();
  setClass('OLD1', { pin: meta0.teacherPinHash, key: meta0.teacherKeyHash });
  assert.deepEqual(await lib.TeacherSecrets.check('0000'), { pin: false, key: false });
  assert.equal((await currentDb.ref('classes/OLD1/meta/teacherPinHash').once('value')).exists(), true); // 틀리면 그대로

  assert.deepEqual(await lib.TeacherSecrets.check('4321'), { pin: true, key: false });
  const meta1 = (await currentDb.ref('classes/OLD1/meta').once('value')).val();
  assert.equal(meta1.teacherPinHash, undefined);
  assert.equal(meta1.pinV, 2);
  assert.equal(meta1.teacherKeyHash, meta0.teacherKeyHash); // 키는 아직 안 옮김
  assert.equal(state.legacyPinHash, '');

  // 이제 새 방식으로 통과 (예전 해시 없이도)
  assert.deepEqual(await lib.TeacherSecrets.check('4321'), { pin: true, key: false });
  assert.deepEqual(await lib.TeacherSecrets.check('1234'), { pin: false, key: false });

  // 교사 키로 들어오면 키도 옮기고, 예전 키 목록은 새 키 목록으로 바뀜
  assert.deepEqual(await lib.TeacherSecrets.check(OLD_KEY), { pin: false, key: true });
  const meta2 = (await currentDb.ref('classes/OLD1/meta').once('value')).val();
  assert.equal(meta2.teacherKeyHash, undefined);
  assert.equal(meta2.keyV, 2);
  const kp = await lib.teacherKeyProof(OLD_KEY);
  assert.equal((await currentDb.ref(`teacherKeys/${kp}/classes/OLD1`).once('value')).exists(), true);
  assert.equal((await currentDb.ref(`teacherKeys/${lib.simpleHashString(OLD_KEY)}/classes/OLD1`).once('value')).exists(), false);
  assert.deepEqual(await lib.TeacherSecrets.check(OLD_KEY), { pin: false, key: true });
});

test('예전 방식 학급이 PIN을 안 정해 뒀으면 기본값 1234로 들어와 바로 새 방식으로 옮김', async () => {
  await env.withSecurityRulesDisabled(async (ctx) => {
    await ctx.database().ref('classes/OLD1/meta/teacherPinHash').remove();
  });
  setClass('OLD1', { pin: lib.hashTeacherPin('1234') });
  assert.equal((await lib.TeacherSecrets.check('1234')).pin, true);
  state.legacyPinHash = ''; // 이후 불러오기에서는 pinV로 예전 방식이 꺼짐
  assert.equal((await lib.TeacherSecrets.check('1234')).pin, true);
  assert.equal((await lib.TeacherSecrets.check('9999')).pin, false);
});

test('서버에 연결할 수 없으면 이 기기에서 전에 확인한 값만 통과', async () => {
  const pp = await lib.teacherPinProof('NEW1', '7777');
  store['caTeacherProof:NEW1'] = JSON.stringify({ pin: pp });
  setClass('NEW1');
  currentDb = { ref: () => ({ once: () => Promise.reject(Object.assign(new Error('network error'), { code: 'unavailable' })) }) };
  assert.equal((await lib.TeacherSecrets.check('7777')).pin, true);
  assert.equal((await lib.TeacherSecrets.check('1234')).pin, false);
});

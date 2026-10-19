// 학생 비밀번호 보호 규칙 테스트 (Firebase 에뮬레이터 전용)
// 실행: cd tests && npm install && npm test   (Java + firebase-tools 필요)
import { test, before, beforeEach, after } from 'node:test';
import fs from 'node:fs';
import { initializeTestEnvironment, assertFails, assertSucceeds } from '@firebase/rules-unit-testing';

const P = (c) => 'p_' + c.repeat(64);
const PROOF_A = P('a');
const PROOF_B = P('b');
const PROOF_C = P('c');

let env;

before(async () => {
  const [host, port] = (process.env.FIREBASE_DATABASE_EMULATOR_HOST || '127.0.0.1:9000').split(':');
  env = await initializeTestEnvironment({
    projectId: 'demo-class-arena',
    database: { host, port: Number(port), rules: fs.readFileSync(new URL('../database.rules.json', import.meta.url), 'utf8') }
  });
});

after(async () => { await env.cleanup(); });

const student = (id, extra = {}) => ({ id, name: id, mc: 100, ...extra });

beforeEach(async () => {
  await env.clearDatabase();
  await env.withSecurityRulesDisabled(async (ctx) => {
    await ctx.database().ref().set({
      classes: {
        OWN1: {
          meta: { classCode: 'OWN1', ownerUid: 'teacher', ownerEmail: 't@x.com', teacherKeyHash: 'kh_1', createdAt: 1, className: 'A' },
          students: { s1: student('s1'), s2: student('s2'), s3: student('s3', { password: 'h:kh_legacy' }) },
          profiles: {
            s1: { id: 's1', name: 's1', claimed: true },
            s2: { id: 's2', name: 's2', claimed: false },
            s3: { id: 's3', name: 's3', claimed: true, password: 'h:kh_legacy' }
          }
        },
        OLD1: {
          meta: { classCode: 'OLD1', teacherKeyHash: 'kh_2', createdAt: 1, className: 'B' },
          students: { s1: student('s1') },
          profiles: { s1: { id: 's1', name: 's1', claimed: false } }
        }
      },
      studentSecrets: { OWN1: { s1: { [PROOF_A]: true } } },
      studentClaims: { OWN1: { s1: { u1: { proof: PROOF_A, at: 1 } } } },
      classMembers: { OWN1: { u1: 's1' } }
    });
  });
});

const db = (uid, token) => (uid ? env.authenticatedContext(uid, token) : env.unauthenticatedContext()).database();
const claim = (proof) => ({ proof, at: Date.now() - 1000 });

test('아무도 비밀번호 저장소를 읽을 수 없음', async () => {
  await assertFails(db(null).ref('studentSecrets/OWN1').once('value'));
  await assertFails(db('u1').ref('studentSecrets/OWN1/s1').once('value'));
  await assertFails(db('teacher').ref('studentSecrets/OWN1/s1').once('value'));
  await assertSucceeds(db(null).ref('classes/OWN1/students').once('value')); // 학급 화면은 그대로 보임
});

test('맞는 비밀번호로만 로그인(연결)됨', async () => {
  await assertSucceeds(db('u2').ref().update({ 'studentClaims/OWN1/s1/u2': claim(PROOF_A), 'classMembers/OWN1/u2': 's1' }));
  await assertFails(db('u3').ref().update({ 'studentClaims/OWN1/s1/u3': claim(PROOF_B), 'classMembers/OWN1/u3': 's1' }));
  await assertFails(db(null).ref('studentClaims/OWN1/s1/u4').set(claim(PROOF_A)));
});

test('다른 사람 계정으로 연결하거나 남의 연결을 대신 만들 수 없음', async () => {
  await assertFails(db('u2').ref('studentClaims/OWN1/s1/u9').set(claim(PROOF_A)));
  await assertFails(db('u2').ref('classMembers/OWN1/u2').set('s1')); // 연결 없이 멤버 등록 불가
  await assertFails(db('u2').ref('classMembers/OWN1/u1').set('s2'));
});

test('자기 연결 정보만 읽을 수 있음', async () => {
  await assertSucceeds(db('u1').ref('studentClaims/OWN1/s1/u1').once('value'));
  await assertSucceeds(db('u1').ref('classMembers/OWN1/u1').once('value'));
  await assertFails(db('u2').ref('studentClaims/OWN1/s1/u1').once('value'));
  await assertFails(db('u2').ref('classMembers/OWN1').once('value'));
});

test('소유 학급: 로그인한 학생만 학생 기록을 바꿀 수 있음 (거래용으로 다른 학생 기록도 허용)', async () => {
  await assertSucceeds(db('u1').ref('classes/OWN1/students/s1/mc').set(200));
  await assertSucceeds(db('u1').ref('classes/OWN1/students/s2/mc').set(300));
  await assertFails(db('u2').ref('classes/OWN1/students/s1/mc').set(999));
  await assertFails(db(null).ref('classes/OWN1/students/s1/mc').set(999));
  await assertFails(db('u1').ref('classes/OWN1/students/s9').set(student('s9'))); // 학생 추가는 교사만
  await assertFails(db('u1').ref('classes/OWN1/students/s2').remove());
  await assertSucceeds(db('teacher').ref('classes/OWN1/students/s9').set(student('s9')));
});

test('소유자 없는 예전 학급은 예전처럼 열려 있음', async () => {
  await assertSucceeds(db(null).ref('classes/OLD1/students/s1/mc').set(5));
  await assertSucceeds(db('anyone').ref().update({
    'studentSecrets/OLD1/s1': { [PROOF_C]: true },
    'classes/OLD1/profiles/s1/claimed': true
  }));
  // 그래도 틀린 비밀번호로는 로그인(연결) 불가
  await assertFails(db('anyone2').ref('studentClaims/OLD1/s1/anyone2').set(claim(PROOF_A)));
  await assertSucceeds(db('anyone2').ref('studentClaims/OLD1/s1/anyone2').set(claim(PROOF_C)));
  // 교사도 다른 기기 연결을 대신 만들 수는 없음 (지우기만 가능)
  await assertFails(db('teacher').ref('studentClaims/OWN1/s1').set({ u9: claim(PROOF_A) }));
});

test('새 비밀번호를 학생 기록이나 프로필에 저장할 수 없음 (지우기만 가능)', async () => {
  await assertFails(db('u1').ref('classes/OWN1/students/s1/password').set('1234'));
  await assertFails(db('teacher').ref('classes/OWN1/profiles/s1/password').set('1234'));
  await assertFails(db(null).ref('classes/OLD1/profiles/s1/password').set('1234'));
  await assertSucceeds(db('teacher').ref('classes/OWN1/profiles/s3/password').remove());
  // 예전 값을 그대로 두는 전체 덮어쓰기는 허용
  await assertSucceeds(db('u1').ref('classes/OWN1/students/s3').set(student('s3', { password: 'h:kh_legacy', mc: 1 })));
});

test('"비밀번호 있음" 표시는 실제 비밀번호 저장 여부와 같아야 함', async () => {
  await assertFails(db('u1').ref('classes/OWN1/profiles/s1/claimed').set(false));
  await assertFails(db('u1').ref('classes/OWN1/profiles/s2/claimed').set(true));
  await assertSucceeds(db('u1').ref('classes/OWN1/profiles/s2/name').set('새이름'));
});

test('처음 비밀번호 설정: 비밀번호가 없는 학생만, 한 번에 연결까지', async () => {
  await assertSucceeds(db('u5').ref().update({
    'studentSecrets/OWN1/s2': { [PROOF_B]: true },
    'studentClaims/OWN1/s2/u5': claim(PROOF_B),
    'classMembers/OWN1/u5': 's2',
    'classes/OWN1/profiles/s2/claimed': true
  }));
  // 이미 설정된 뒤에는 다른 사람이 덮어쓸 수 없음
  await assertFails(db('u6').ref('studentSecrets/OWN1/s2').set({ [PROOF_C]: true }));
  await assertFails(db('u6').ref('studentSecrets/OWN1/s1').set({ [PROOF_C]: true }));
  // 없는 학생에게는 설정 불가
  await assertFails(db('u6').ref('studentSecrets/OWN1/nobody').set({ [PROOF_C]: true }));
  // 형식이 다른 값은 거부
  await assertFails(db('u6').ref('studentSecrets/OWN1/s3').set({ plain1234: true }));
});

test('예전 비밀번호(h: 해시) 학생의 첫 로그인 전환', async () => {
  await assertSucceeds(db('u7').ref().update({
    'studentSecrets/OWN1/s3': { [PROOF_C]: true },
    'studentClaims/OWN1/s3/u7': claim(PROOF_C),
    'classMembers/OWN1/u7': 's3',
    'classes/OWN1/profiles/s3/claimed': true,
    'classes/OWN1/profiles/s3/password': null,
    'classes/OWN1/students/s3/password': null
  }));
});

test('로그인한 학생은 자기 비밀번호만 바꿀 수 있음', async () => {
  await assertSucceeds(db('u1').ref().update({
    'studentSecrets/OWN1/s1': { [PROOF_B]: true },
    'studentClaims/OWN1/s1/u1': claim(PROOF_B)
  }));
  await env.withSecurityRulesDisabled(async (ctx) => {
    await ctx.database().ref().update({ 'studentSecrets/OWN1/s2': { [PROOF_A]: true }, 'classes/OWN1/profiles/s2/claimed': true });
  });
  await assertFails(db('u1').ref('studentSecrets/OWN1/s2').set({ [PROOF_C]: true }));
});

test('소유 교사의 비밀번호 초기화 / 새로 지정', async () => {
  await assertSucceeds(db('teacher').ref().update({
    'studentSecrets/OWN1/s1': null,
    'studentClaims/OWN1/s1': null,
    'classes/OWN1/profiles/s1/claimed': false
  }));
  // 초기화되면 예전 기기는 더 이상 학생 기록을 바꿀 수 없음
  await assertFails(db('u1').ref('classes/OWN1/students/s1/mc').set(1));
  await assertSucceeds(db('teacher').ref().update({
    'studentSecrets/OWN1/s2': { [PROOF_C]: true },
    'classes/OWN1/profiles/s2/claimed': true
  }));
  // 교사가 아닌 사람은 남의 연결을 지우거나 비밀번호를 지울 수 없음
  await assertFails(db('u2').ref('studentClaims/OWN1/s2').remove());
  await assertFails(db('u2').ref('studentSecrets/OWN1/s2').remove());
  await assertFails(db('u1').ref('studentClaims/OWN1/s1').remove());
});

test('학생은 로그아웃 시 자기 연결을 지울 수 있음', async () => {
  await assertSucceeds(db('u1').ref().update({ 'studentClaims/OWN1/s1/u1': null, 'classMembers/OWN1/u1': null }));
});

test('총괄 관리자는 학급 삭제 시 비밀번호·연결 정보도 지울 수 있음', async () => {
  const admin = db('boss', { superAdmin: true });
  await assertSucceeds(admin.ref().update({
    'classes/OWN1': null,
    'studentSecrets/OWN1': null,
    'studentClaims/OWN1': null,
    'classMembers/OWN1': null
  }));
  await assertFails(db('teacher').ref('studentSecrets/OWN1').remove());
});

test('기존 보호 유지: 학생은 학급 정보(이름 등)를 바꿀 수 없음', async () => {
  await assertFails(db('u1').ref('classes/OWN1/meta/className').set('해킹'));
  await assertSucceeds(db('u1').ref('classes/OWN1/meta/guardianPts').set(10));
  await assertSucceeds(db('teacher').ref('classes/OWN1/meta/className').set('새 이름'));
});

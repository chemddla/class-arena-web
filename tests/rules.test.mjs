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

test('소유 학급: 로그인한 학생은 자기 기록만 바꿀 수 있음', async () => {
  await assertSucceeds(db('u1').ref('classes/OWN1/students/s1/mc').set(200));
  await assertFails(db('u1').ref('classes/OWN1/students/s2/mc').set(300));
  await assertFails(db('u1').ref('classes/OWN1/students/s2').set(student('s2', { mc: 0 })));
  await assertFails(db('u1').ref('classes/OWN1/profiles/s2/name').set('바꿈'));
  await assertFails(db('u1').ref().update({ 'classes/OWN1/students/s1/mc': 1, 'classes/OWN1/students/s2/mc': 1 }));
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
  await assertSucceeds(db('teacher').ref('classes/OWN1/students/s3').set(student('s3', { password: 'h:kh_legacy', mc: 1 })));
});

test('"비밀번호 있음" 표시는 실제 비밀번호 저장 여부와 같아야 함', async () => {
  await assertFails(db('u1').ref('classes/OWN1/profiles/s1/claimed').set(false));
  await assertFails(db('teacher').ref('classes/OWN1/profiles/s2/claimed').set(true));
  await assertSucceeds(db('u1').ref('classes/OWN1/profiles/s1/name').set('새이름'));
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

// ----- 친구에게 보내는 MC·용병 (받을 선물함: classes/{학급}/transfers/{받는 학생}/{id}) -----
const gift = (from, extra = {}) => ({ from, fromName: from, mc: 100, kind: 'trade_refund', note: '돌려받음', at: Date.now() - 1000, ...extra });
const linkS2 = () => env.withSecurityRulesDisabled(async (ctx) => {
  await ctx.database().ref().update({ 'studentClaims/OWN1/s2/u2': { proof: PROOF_B, at: 1 }, 'classMembers/OWN1/u2': 's2' });
});

test('선물함: 로그인한 학생은 자기 이름으로만 친구에게 보낼 수 있음', async () => {
  await assertSucceeds(db('u1').ref('classes/OWN1/transfers/s2/t_abcdef01').set(gift('s1')));
  await assertSucceeds(db('u1').ref('classes/OWN1/transfers/s2/t_abcdef02').set(gift('s1', { mc: 0, merc: { id: 'merc_1', job: 'warrior', name: '용사', level: 3 } })));
  await assertFails(db('u1').ref('classes/OWN1/transfers/s3/t_abcdef03').set(gift('s2'))); // 남의 이름으로
  await assertFails(db('u1').ref('classes/OWN1/transfers/s1/t_abcdef04').set(gift('s1'))); // 나에게
  await assertFails(db('u2').ref('classes/OWN1/transfers/s2/t_abcdef05').set(gift('s1'))); // 로그인 안 된 기기
  await assertFails(db(null).ref('classes/OWN1/transfers/s2/t_abcdef06').set(gift('s1')));
  await assertFails(db('u1').ref('classes/OWN1/transfers/nobody/t_abcdef07').set(gift('s1'))); // 없는 학생
});

test('선물함: 빼앗는 값이나 이상한 값은 보낼 수 없음', async () => {
  await assertFails(db('u1').ref('classes/OWN1/transfers/s2/t_bad00001').set(gift('s1', { mc: -500 })));
  await assertFails(db('u1').ref('classes/OWN1/transfers/s2/t_bad00002').set(gift('s1', { mc: 100001 })));
  await assertFails(db('u1').ref('classes/OWN1/transfers/s2/t_bad00003').set(gift('s1', { mc: '100' })));
  await assertFails(db('u1').ref('classes/OWN1/transfers/s2/t_bad00004').set(gift('s1', { tickets: -3 })));
  await assertFails(db('u1').ref('classes/OWN1/transfers/s2/t_bad00005').set(gift('s1', { at: Date.now() + 60 * 60 * 1000 })));
  await assertFails(db('u1').ref('classes/OWN1/transfers/s2/t_bad00006').set(gift('s1', { merc: { name: '빈 용병' } })));
  await assertFails(db('u1').ref('classes/OWN1/transfers/s2/bad-id').set(gift('s1')));
  const { mc, ...noMc } = gift('s1');
  await assertFails(db('u1').ref('classes/OWN1/transfers/s2/t_bad00007').set(noMc));
});

test('선물함: 보낸 것은 고치거나 지울 수 없고, 받는 학생 기기만 받아서 지움', async () => {
  await assertSucceeds(db('u1').ref('classes/OWN1/transfers/s2/t_keep0001').set(gift('s1')));
  await assertFails(db('u1').ref('classes/OWN1/transfers/s2/t_keep0001/mc').set(1));
  await assertFails(db('u1').ref('classes/OWN1/transfers/s2/t_keep0001').set(gift('s1', { mc: 1 })));
  await assertFails(db('u1').ref('classes/OWN1/transfers/s2/t_keep0001').remove());
  await assertFails(db('u1').ref('classes/OWN1/transfers/s2').remove());
  await linkS2();
  // 받는 학생: 자기 기록에 더하고 선물함에서 지우기를 한 번에
  await assertSucceeds(db('u2').ref().update({
    'classes/OWN1/students/s2/mc': 200,
    'classes/OWN1/transfers/s2/t_keep0001': null
  }));
  // 이미 받은 것을 다시 받을 수 없음 (다른 탭이 먼저 받은 경우)
  await assertFails(db('u2').ref().update({
    'classes/OWN1/students/s2/mc': 300,
    'classes/OWN1/transfers/s2/t_keep0001': null
  }));
});

test('선물함: 거래 수락처럼 내 기록·거래 목록·친구 선물을 한 번에 저장', async () => {
  await assertSucceeds(db('u1').ref().update({
    'classes/OWN1/students/s1/mc': 400,
    'classes/OWN1/tradeOffers': null,
    'classes/OWN1/transfers/s2/t_trade001': gift('s1', { mc: 0, kind: 'trade_buy', merc: { id: 'merc_9', job: 'mage' } }),
    'classes/OWN1/transfers/s3/t_trade002': gift('s1', { mc: 250 })
  }));
  // 하나라도 남의 기록을 직접 바꾸면 전체 거부
  await assertFails(db('u1').ref().update({
    'classes/OWN1/students/s1/mc': 400,
    'classes/OWN1/students/s2/mc': 0,
    'classes/OWN1/transfers/s2/t_trade003': gift('s1')
  }));
});

test('선물함: 소유 교사·총괄 관리자·소유자 없는 학급', async () => {
  await assertSucceeds(db('u1').ref('classes/OWN1/transfers/s2/t_tchr0001').set(gift('s1')));
  await assertSucceeds(db('teacher').ref('classes/OWN1/transfers/s2').remove());
  await assertSucceeds(db('teacher').ref('classes/OWN1/students/s2/mc').set(5)); // 교사는 모든 학생 기록 수정 가능
  await assertSucceeds(db('boss', { superAdmin: true }).ref('classes/OWN1/students/s2/mc').set(6));
  await env.withSecurityRulesDisabled(async (ctx) => {
    await ctx.database().ref('classes/OLD1/students/s2').set(student('s2'));
  });
  await assertSucceeds(db(null).ref('classes/OLD1/transfers/s2/t_old00001').set(gift('s1')));
  await assertSucceeds(db(null).ref('classes/OLD1/transfers/s2/t_old00001').remove());
  await assertSucceeds(db(null).ref('classes/OLD1/students/s2/mc').set(7)); // 예전 학급은 예전처럼
  await assertFails(db(null).ref('classes/OLD1/transfers/s2/t_old00002').set(gift('s1', { mc: -1 })));
  // 교사가 학생을 지우면 그 학생의 선물함도 같이 지움
  await assertSucceeds(db('u1').ref('classes/OWN1/transfers/s3/t_tchr0002').set(gift('s1')));
  await assertSucceeds(db('teacher').ref().update({
    'classes/OWN1/students/s3': null,
    'classes/OWN1/profiles/s3': null,
    'classes/OWN1/transfers/s3': null,
    'studentSecrets/OWN1/s3': null,
    'studentClaims/OWN1/s3': null
  }));
});

// ----- 접속 표시 (presence/{학급}/{학생}/{이 탭의 계정}) -----
test('접속 표시: 로그인한 학생은 자기 칸에만 켜고 끌 수 있고, 학급 코드를 알면 누구나 봄', async () => {
  const at = Date.now() - 1000;
  await assertSucceeds(db('u1').ref('presence/OWN1/s1/u1').set(at));
  await assertSucceeds(db(null).ref('presence/OWN1').once('value'));
  await assertFails(db('u1').ref('presence/OWN1/s2/u1').set(at)); // 남의 칸
  await assertFails(db('u1').ref('presence/OWN1/s1/u9').set(at)); // 다른 기기 계정 칸
  await assertFails(db('u2').ref('presence/OWN1/s1/u2').set(at)); // 로그인(연결) 안 된 기기
  await assertFails(db(null).ref('presence/OWN1/s1/u1').set(at));
  await assertFails(db('u1').ref('presence/OWN1/s1/u1').set('켜짐')); // 숫자(시각)만
  await assertFails(db('u1').ref('presence/OWN1/s1/u1').set(Date.now() + 3600000)); // 미래 시각
  await assertFails(db('u1').ref('presence/OWN1/s1').set({ u1: at, u9: at }));
  await assertSucceeds(db('u1').ref('presence/OWN1/s1/u1').remove());
  await assertSucceeds(db('u2').ref('presence/OWN1/s1/u2').remove()); // 자기 칸 끄기는 늘 가능
  await assertFails(db('teacher').ref('presence/OWN1').remove());
  await assertSucceeds(db('admin', { superAdmin: true }).ref('presence/OWN1').remove());
});

test('실시간 결투 화면 전달(pvp_live): 학급이 있으면 쓰고 지울 수 있고, 없는 학급에는 못 씀', async () => {
  await assertSucceeds(db(null).ref('classes/OWN1/pvp_live/pvp_s1/frame').set({ t: 1, u: [[1, 2, 3]] }));
  await assertSucceeds(db(null).ref('classes/OWN1/pvp_live/pvp_s1/input').set({ k: 'w', ax: 1, ay: 2 }));
  await assertSucceeds(db(null).ref('classes/OWN1/pvp_live/pvp_s1').remove());
  await assertFails(db(null).ref('classes/NOPE/pvp_live/pvp_s1/frame').set({ t: 1 }));
  await assertFails(db(null).ref('classes/OWN1/pvp_livex/pvp_s1').set({ t: 1 }));
});

// ----- 학생 외형 디자인 (classes/{학급}/skinDesigns/{학생}/{id}) -----
const design = (extra = {}) => ({ job: 'knight', title: '용암 기사', note: '빨간 갑옷', name: 's1', image: 'data:image/jpeg;base64,AAAA', at: Date.now() - 1000, ...extra });

test('학생 디자인: 로그인한 학생은 자기 칸에만 내고 지울 수 있음', async () => {
  await assertSucceeds(db('u1').ref('classes/OWN1/skinDesigns/s1/d_abc123').set(design()));
  await assertSucceeds(db('u1').ref('classes/OWN1/skinDesigns/s1/d_abc123').remove());
  await assertFails(db('u1').ref('classes/OWN1/skinDesigns/s2/d_abc124').set(design())); // 남의 칸
  await assertFails(db('u2').ref('classes/OWN1/skinDesigns/s1/d_abc125').set(design())); // 로그인 안 된 기기
  await assertFails(db(null).ref('classes/OWN1/skinDesigns/s1/d_abc126').set(design()));
  await assertFails(db('u1').ref('classes/OWN1/skinDesigns/nobody/d_abc127').set(design())); // 없는 학생
  await assertSucceeds(db('teacher').ref('classes/OWN1/skinDesigns/s2/d_tch001').set(design()));
  await assertSucceeds(db('teacher').ref('classes/OWN1/skinDesigns/s2').remove());
  await assertSucceeds(db(null).ref('classes/OLD1/skinDesigns/s1/d_old001').set(design())); // 소유자 없는 예전 학급
});

test('학생 디자인: 이상한 값은 낼 수 없음', async () => {
  const put = (id, d) => db('u1').ref(`classes/OWN1/skinDesigns/s1/${id}`).set(d);
  await assertFails(put('d_bad001', design({ job: 'dragon' })));
  await assertFails(put('d_bad002', design({ title: '' })));
  await assertFails(put('d_bad003', design({ title: 'x'.repeat(21) })));
  await assertFails(put('d_bad004', design({ image: 'javascript:alert(1)' })));
  await assertFails(put('d_bad005', design({ image: 'data:image/png;base64,' + 'A'.repeat(400000) })));
  await assertFails(put('d_bad006', design({ extra: 1 })));
  await assertFails(put('d_bad007', design({ at: Date.now() + 60000 })));
  await assertFails(put('bad_id01', design()));
  const { image, ...noImage } = design();
  await assertFails(put('d_bad008', noImage));
});

test('학생 디자인: 선생님은 반려 표시와 이유를 남길 수 있음', async () => {
  await assertSucceeds(db('u1').ref('classes/OWN1/skinDesigns/s1/d_rej001').set(design()));
  await assertSucceeds(db('teacher').ref('classes/OWN1/skinDesigns/s1/d_rej001').update({ status: 'rejected', reason: '무기가 안 보여요' }));
  await assertSucceeds(db('teacher').ref('classes/OWN1/skinDesigns/s1/d_rej001').update({ status: null, reason: null }));
  await assertFails(db('teacher').ref('classes/OWN1/skinDesigns/s1/d_rej001').update({ status: 'approved' }));
  await assertFails(db('teacher').ref('classes/OWN1/skinDesigns/s1/d_rej001').update({ reason: 'x'.repeat(101) }));
});

// ----- 승인된 학생 디자인 외형 (classes/{학급}/skins/{id}, skinSheets/{id}): 소유 교사만 씀 -----
const skin = (extra = {}) => ({ job: 'knight', n: 1, title: '불꽃 기사', designer: 's1', designerId: 's1', at: Date.now() - 1000, ...extra });
const SHEET = 'data:image/webp;base64,UklGRg==';

test('승인 외형: 소유 교사만 올리고, 학생·남은 못 씀', async () => {
  await assertSucceeds(db('teacher').ref().update({ 'classes/OWN1/skins/d_abc123': skin(), 'classes/OWN1/skinSheets/d_abc123': SHEET }));
  await assertFails(db('u1').ref('classes/OWN1/skins/d_abc124').set(skin()));
  await assertFails(db('u1').ref('classes/OWN1/skinSheets/d_abc123').set(SHEET));
  await assertFails(db(null).ref('classes/OWN1/skins/d_abc125').set(skin()));
  await assertFails(db('stranger').ref('classes/OWN1/skins/d_abc126').set(skin()));
  await assertSucceeds(db('teacher').ref('classes/OWN1/skins/d_abc123').remove());
  await assertSucceeds(db(null).ref('classes/OLD1/skins/d_old123').set(skin())); // 소유자 없는 예전 학급
  await assertSucceeds(db(null).ref('classes/OLD1/skinSheets/d_old123').set(SHEET));
});

test('승인 외형: 이상한 값은 못 올림', async () => {
  const put = (id, v) => db('teacher').ref(`classes/OWN1/skins/${id}`).set(v);
  await assertFails(put('d_bad101', skin({ job: 'dragon' })));
  await assertFails(put('d_bad102', skin({ n: 0 })));
  await assertFails(put('d_bad103', skin({ title: '' })));
  await assertFails(put('d_bad104', skin({ extra: 1 })));
  const { designerId, ...noDesigner } = skin();
  await assertFails(put('d_bad105', noDesigner));
  const sheet = (id, v) => db('teacher').ref(`classes/OWN1/skinSheets/${id}`).set(v);
  await assertFails(sheet('d_bad201', 'javascript:alert(1)'));
  await assertFails(sheet('d_bad202', 'data:image/svg+xml;base64,AAAA'));
  await assertFails(sheet('d_bad203', 'data:image/webp;base64,' + 'A'.repeat(1000000)));
  await assertFails(sheet('bad_id02', SHEET));
});

// ----- 교사 PIN·교사 키 증명 (classSecrets): 서버에서 읽어갈 수 없고, 맞는 값인지 확인만 가능 -----
const S = (c) => 'sh_' + c.repeat(64);
const [SA, SB, SC] = [S('a'), S('b'), S('c')];
const seedSecrets = () => env.withSecurityRulesDisabled(async (ctx) => {
  await ctx.database().ref().update({
    'classSecrets/OWN1/pin': { [SA]: true },
    'classSecrets/OWN1/key': { [SB]: true },
    'classSecrets/OLD1/pin': { [SA]: true }
  });
});

test('교사 증명: 목록은 아무도 못 읽고, 맞는 값이 있는지만 확인할 수 있음', async () => {
  await seedSecrets();
  await assertFails(db(null).ref('classSecrets').once('value'));
  await assertFails(db('teacher').ref('classSecrets/OWN1').once('value'));
  await assertFails(db('teacher').ref('classSecrets/OWN1/pin').once('value'));
  await assertSucceeds(db(null).ref(`classSecrets/OWN1/pin/${SA}`).once('value'));
  await assertFails(db(null).ref(`classSecrets/OWN1/pin/${SB}`).once('value')); // 틀린 값
  await assertSucceeds(db(null).ref(`classSecrets/OWN1/key/${SB}`).once('value'));
  await assertFails(db(null).ref('classSecrets/OWN1/pin/prev').once('value'));
});

test('교사 증명: 소유 학급은 소유 교사(와 총괄 관리자)만 쓸 수 있음', async () => {
  await assertFails(db(null).ref('classSecrets/OWN1/pin').set({ [SC]: true }));
  await assertFails(db('u1').ref('classSecrets/OWN1/pin').set({ [SC]: true }));
  await assertSucceeds(db('teacher').ref('classSecrets/OWN1/pin').set({ [SC]: true }));
  await assertSucceeds(db('teacher').ref('classSecrets/OWN1/key').set({ [SB]: true }));
  await assertSucceeds(db('admin', { superAdmin: true }).ref('classSecrets/OWN1').remove());
  await assertFails(db('teacher').ref('classSecrets/NOPE/pin').set({ [SC]: true })); // 없는 학급
  await assertFails(db('teacher').ref('classSecrets/OWN1/other').set({ [SC]: true })); // pin·key 외 칸
  await assertFails(db('teacher').ref('classSecrets/OWN1/pin').set({ '1234': true })); // 약한 값
  await assertFails(db('teacher').ref('classSecrets/OWN1/pin').set({ [SC]: 'yes' }));
});

test('교사 증명: 소유자 없는 학급은 처음 한 번만 만들고, 바꾸려면 이전 값을 알아야 함', async () => {
  await assertSucceeds(db(null).ref('classSecrets/OLD1/key').set({ [SB]: true })); // 아직 없음 → 처음 설정
  await assertFails(db(null).ref('classSecrets/OLD1/key').set({ [SC]: true })); // 이전 값 없이 덮어쓰기
  await assertFails(db(null).ref('classSecrets/OLD1/key').set({ [SC]: true, prev: SA })); // 틀린 이전 값
  await assertSucceeds(db(null).ref('classSecrets/OLD1/key').set({ [SC]: true, prev: SB }));
  await seedSecrets();
  await assertFails(db(null).ref('classSecrets/OLD1/pin').set({ [SC]: true, prev: 'prev' }));
  await assertSucceeds(db(null).ref('classSecrets/OLD1/pin').set({ [SC]: true, prev: SA }));
  await assertSucceeds(db(null).ref('classSecrets/OLD1/pin').set({ [SB]: true, prev: SC })); // 한 번 바꾼 뒤에도 같은 방식
});

test('교사 키 목록: 강한 키 증명이 있는 학급만 올릴 수 있고, 예전 해시 목록은 해시가 지워지면 정리할 수 있음', async () => {
  await seedSecrets();
  const item = (code) => ({ classCode: code, className: 'A', studentCount: 1, updatedAt: 1 });
  await assertSucceeds(db('teacher').ref(`teacherKeys/${SB}/classes/OWN1`).set(item('OWN1')));
  await assertFails(db('teacher').ref(`teacherKeys/${SC}/classes/OWN1`).set(item('OWN1'))); // 증명 없는 키
  await assertFails(db('teacher').ref(`teacherKeys/${SB}/classes/OLD1`).set(item('OLD1'))); // 다른 학급의 키
  await assertFails(db('teacher').ref(`teacherKeys/${SB}/classes/OWN1`).set(item('OLD1')));
  await assertSucceeds(db(null).ref(`teacherKeys/${SB}/classes`).once('value'));
  // 예전 방식 목록은 meta.teacherKeyHash가 있는 동안 유지, 사라진 뒤에는 지울 수 있음
  await assertSucceeds(db(null).ref('teacherKeys/kh_2/classes/OLD1').set(item('OLD1')));
  await assertFails(db(null).ref('teacherKeys/kh_2/classes/OLD1').remove());
  await assertSucceeds(db(null).ref().update({
    'classes/OLD1/meta/teacherKeyHash': null,
    'classes/OLD1/meta/teacherPinHash': null,
    'classes/OLD1/meta/pinV': 2,
    'classes/OLD1/meta/keyV': 2,
    'teacherKeys/kh_2/classes/OLD1': null
  }));
});

test('학급 정보: 예전 교사 키 해시는 지울 수만 있고 바꿀 수 없음', async () => {
  await assertFails(db(null).ref('classes/OLD1/meta/teacherKeyHash').set('kh_9'));
  await assertSucceeds(db(null).ref('classes/OLD1/meta/teacherKeyHash').remove());
  await assertFails(db('u1').ref('classes/OWN1/meta/teacherKeyHash').remove());
  await assertSucceeds(db('teacher').ref('classes/OWN1/meta/teacherKeyHash').remove());
});

test('새 학급 만들기: 학급 정보와 교사 증명, 교사 키 목록을 한 번에 저장', async () => {
  const t = db('newteacher', { email: 'n@x.com' });
  await assertSucceeds(t.ref().update({
    'classes/NEW1/meta': { classCode: 'NEW1', ownerUid: 'newteacher', ownerEmail: 'n@x.com', createdAt: 1, className: 'N', pinV: 2, keyV: 2 },
    'classSecrets/NEW1/pin': { [SA]: true },
    'classSecrets/NEW1/key': { [SB]: true },
    [`teacherKeys/${SB}/classes/NEW1`]: { classCode: 'NEW1', className: 'N', studentCount: 0, updatedAt: 1 }
  }));
  await assertFails(db('other').ref('classSecrets/NEW1/pin').set({ [SC]: true }));
});

// ----- 실시간 방 초대 (classes/{학급}/invites/{받는 학생}/{id}) -----
const invite = (from, extra = {}) => ({ from, fromName: from, kind: 'pvp', roomId: 'pvp_s1_abc', title: '결투방', at: Date.now() - 1000, ...extra });

test('방 초대: 로그인한 학생은 자기 이름으로만 보내고, 받는 학생·보낸 학생만 지움', async () => {
  await assertSucceeds(db('u1').ref('classes/OWN1/invites/s2/i_abcdef01').set(invite('s1')));
  await assertSucceeds(db('u1').ref('classes/OWN1/invites/s2/i_abcdef02').set(invite('s1', { kind: 'minigame' })));
  await assertFails(db('u1').ref('classes/OWN1/invites/s3/i_abcdef03').set(invite('s2'))); // 남의 이름으로
  await assertFails(db('u1').ref('classes/OWN1/invites/s1/i_abcdef04').set(invite('s1'))); // 나에게
  await assertFails(db('u2').ref('classes/OWN1/invites/s2/i_abcdef05').set(invite('s1'))); // 로그인 안 된 기기
  await assertFails(db(null).ref('classes/OWN1/invites/s2/i_abcdef06').set(invite('s1')));
  await assertFails(db('u1').ref('classes/OWN1/invites/nobody/i_abcdef07').set(invite('s1'))); // 없는 학생
  await assertFails(db('u1').ref('classes/OWN1/invites/s2/i_bad00001').set(invite('s1', { kind: 'shop' })));
  await assertFails(db('u1').ref('classes/OWN1/invites/s2/i_bad00002').set(invite('s1', { mc: 100 })));
  await assertFails(db('u1').ref('classes/OWN1/invites/s2/i_bad00003').set(invite('s1', { at: Date.now() + 3600000 })));
  await assertFails(db('u1').ref('classes/OWN1/invites/s2/bad-id').set(invite('s1')));
  await assertFails(db('u1').ref('classes/OWN1/invites/s2/i_abcdef01').set(invite('s1', { title: '바꿈' }))); // 고치기 불가
  await assertSucceeds(db('u1').ref('classes/OWN1/invites/s2/i_abcdef02').remove()); // 보낸 학생이 취소
  await assertFails(db('u3').ref('classes/OWN1/invites/s2/i_abcdef01').remove());
  await linkS2();
  await assertSucceeds(db('u2').ref('classes/OWN1/invites/s2/i_abcdef01').remove()); // 받은 학생이 수락·거절
  await assertSucceeds(db('teacher').ref('classes/OWN1/invites/s2/i_abcdef09').set(invite('s1')));
  await assertSucceeds(db(null).ref('classes/OLD1/invites/s1/i_abcdef10').set(invite('s2'))); // 소유자 없는 학급은 학생 확인 없음
});

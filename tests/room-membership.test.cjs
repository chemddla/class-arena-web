// 내 자리 점검(syncMyRoomMembership): 두 방 이상에 들어가 있으면 하나만 남기고 나감 · 새로고침 뒤 접속 표시 다시 걸기 · 내 끊김 표시 지우기
// 실행: node room-membership.test.cjs ../index.html
const fs = require('fs'); const assert = require('assert');
const src = fs.readFileSync((process.argv[2] || '../index.html'), 'utf8');
const grab = (from, to) => { const a = src.indexOf(from); const b = src.indexOf(to, a); if (a < 0 || b < 0) throw new Error(from); return src.slice(a, b); };
const body = grab('    const teamPresenceArmed = new Set();', '    // 한 번에 하나의 컨텐츠만: keepKind 방');

function mk(opts) {
  const calls = { leave: [], arm: [], removed: [], teamArm: [] };
  const env = new Function('opts', 'calls', `
    const sim = opts.sim || { running: false, spectator: false };
    let currentActiveLiveBattleRoomId = opts.battleRoomId || null;
    let currentJoinedPvpRoomId = opts.joinedPvp || null, currentJoinedRaidRoomId = opts.joinedRaid || null, currentJoinedMinigameRoomId = opts.joinedMg || null;
    const livePvpRoomsCache = opts.pvp || {}, liveRaidRoomsCache = opts.raid || {}, liveMinigameRoomsCache = opts.mg || {};
    const myRoomPresence = new Map(opts.presence || []);
    const me = { id: 'stu_17', name: '조경빈' };
    const getActiveStudent = () => me;
    const isMyStudentScreen = () => opts.myScreen !== false;
    const isTeamLiveRoom = r => Boolean(r && r.mode === 'teamLive');
    const isPvpRoomPlayer = (r, id) => isTeamLiveRoom(r) ? Boolean(r.members && r.members[id] && !r.members[id].ai) : (r.hostId === id || (r.guestId === id && !r.practiceFriend));
    const raidSlotOf = (r, id) => ['host', 'guest', 'guest2', 'guest3', 'guest4'].find(s => r[s + 'Id'] === id) || null;
    const armRoomPresence = (path, id) => { calls.arm.push(path); myRoomPresence.set(path, id); };
    const classRoomRef = path => ({ remove: () => { calls.removed.push(path); return Promise.resolve(); } });
    const teamMemberRef = (roomId, id) => ({ onDisconnect: () => ({ remove: () => calls.teamArm.push(roomId) }) });
    const leaveRoomsExcept = (kind, id) => calls.leave.push(kind + ':' + id);
    const console = { warn: () => {} };
    ${body}
    return { syncMyRoomMembership, myRoomPresence };
  `)(opts, calls);
  return { ...env, calls };
}

let n = 0; const t = (m, f) => { f(); n++; console.log('ok', m); };

t('두 러쉬방 방장이면 나중에 만든 방만 남김', () => {
  const { syncMyRoomMembership, calls } = mk({ raid: {
    old: { roomId: 'old', hostId: 'stu_17', guestId: 'stu_14', createdAt: 100 },
    neu: { roomId: 'neu', hostId: 'stu_17', createdAt: 200 }
  } });
  syncMyRoomMembership();
  assert.deepEqual(calls.leave, ['raid:neu']);
});

t('전투 중인 방이 있으면 그 방을 남김', () => {
  const { syncMyRoomMembership, calls } = mk({ sim: { running: true, spectator: false }, battleRoomId: 'old', raid: {
    old: { roomId: 'old', hostId: 'stu_17', createdAt: 100 },
    neu: { roomId: 'neu', hostId: 'stu_17', createdAt: 200 }
  } });
  syncMyRoomMembership();
  assert.deepEqual(calls.leave, ['raid:old']);
});

t('결투방+레이드방이면 내 화면이 아는 결투방을 남김', () => {
  const { syncMyRoomMembership, calls } = mk({ joinedPvp: 'p1',
    pvp: { p1: { roomId: 'p1', hostId: 'stu_2', guestId: 'stu_17', createdAt: 50 } },
    raid: { r1: { roomId: 'r1', hostId: 'stu_17', createdAt: 300 } } });
  syncMyRoomMembership();
  assert.deepEqual(calls.leave, ['pvp:p1']);
});

t('방 하나면 나가지 않고 접속 표시만 다시 걸고 내 끊김 표시를 지움', () => {
  const { syncMyRoomMembership, calls, myRoomPresence } = mk({ raid: {
    r1: { roomId: 'r1', kind: 'rush', hostId: 'stu_17', createdAt: 100, gone: { stu_17: 123456, stu_14: 999 } }
  } });
  syncMyRoomMembership();
  assert.deepEqual(calls.leave, []);
  assert.deepEqual(calls.arm, ['raid_rooms/r1']);
  assert.deepEqual(calls.removed, ['raid_rooms/r1/gone/stu_17']);
  assert.ok(myRoomPresence.has('raid_rooms/r1'));
  syncMyRoomMembership();
  assert.deepEqual(calls.arm, ['raid_rooms/r1'], '이미 걸려 있으면 다시 걸지 않음');
});

t('팀전방은 members 칸 지우기를 한 번만 걸고, 방에서 빠지면 다시 걸 수 있게 잊음', () => {
  const pvp = { tm: { roomId: 'tm', mode: 'teamLive', hostId: 'stu_2', members: { stu_17: { id: 'stu_17' } }, createdAt: 1 } };
  const { syncMyRoomMembership, calls } = mk({ pvp });
  syncMyRoomMembership(); syncMyRoomMembership();
  assert.deepEqual(calls.teamArm, ['tm']);
  delete pvp.tm.members.stu_17; syncMyRoomMembership();
  pvp.tm.members.stu_17 = { id: 'stu_17' }; syncMyRoomMembership();
  assert.deepEqual(calls.teamArm, ['tm', 'tm']);
});

t('연습 친구·AI 자리로 이름만 빌린 방은 내 방이 아님', () => {
  const { syncMyRoomMembership, calls } = mk({
    pvp: { p1: { roomId: 'p1', hostId: 'stu_2', guestId: 'stu_17', practiceFriend: true, createdAt: 50 } },
    mg: { m1: { roomId: 'm1', players: [{ id: 'stu_17', practice: true }], createdAt: 60 } },
    raid: { r1: { roomId: 'r1', hostId: 'stu_17', createdAt: 100 } } });
  syncMyRoomMembership();
  assert.deepEqual(calls.leave, []);
  assert.deepEqual(calls.arm, ['raid_rooms/r1']);
});

t('이 탭에서 로그인한 학생이 아니면(선생님 화면 등) 아무것도 하지 않음', () => {
  const { syncMyRoomMembership, calls } = mk({ myScreen: false, raid: {
    old: { roomId: 'old', hostId: 'stu_17', createdAt: 100, gone: { stu_17: 1 } },
    neu: { roomId: 'neu', hostId: 'stu_17', createdAt: 200 }
  } });
  syncMyRoomMembership();
  assert.deepEqual(calls.leave, []); assert.deepEqual(calls.arm, []); assert.deepEqual(calls.removed, []);
});

console.log('all', n);

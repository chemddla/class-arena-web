// 총괄 관리자 권한(superAdmin 커스텀 클레임) 부여/해제
// 사용법:
//   node tools/set-super-admin.cjs <서비스계정키.json> <관리자이메일>          → 권한 부여
//   node tools/set-super-admin.cjs <서비스계정키.json> <관리자이메일> --remove → 권한 해제
const admin = require('firebase-admin');
const fs = require('fs');

const [keyPath, email, flag] = process.argv.slice(2);
if (!keyPath || !email) {
  console.error('사용법: node tools/set-super-admin.cjs ./serviceAccountKey.json admin@example.com [--remove]');
  process.exit(1);
}

admin.initializeApp({ credential: admin.credential.cert(JSON.parse(fs.readFileSync(keyPath, 'utf8'))) });

(async () => {
  const user = await admin.auth().getUserByEmail(email);
  const claims = { ...(user.customClaims || {}) };
  if (flag === '--remove') delete claims.superAdmin;
  else claims.superAdmin = true;
  await admin.auth().setCustomUserClaims(user.uid, claims);
  console.log(`${flag === '--remove' ? '총괄 관리자 권한 해제' : '총괄 관리자 권한 부여'} 완료: ${email} (uid: ${user.uid})`);
  console.log('관리자 페이지에서 로그아웃 후 다시 로그인해야 적용됩니다.');
  process.exit(0);
})().catch((e) => { console.error(e.message || e); process.exit(1); });

// 배포본 index.html 압축: 주석·들여쓰기를 없애고 자바스크립트·CSS를 줄임
// 원본 index.html은 그대로 두고, 배포 폴더(public)에 복사한 파일에만 씀
// 사용법: node tools/minify-html.cjs public/index.html
const fs = require('fs');
const { minify } = require('html-minifier-terser');

(async () => {
  const file = process.argv[2];
  if (!file) throw new Error('파일 경로를 넣어 주세요');
  const before = fs.readFileSync(file, 'utf8');
  const after = await minify(before, {
    collapseWhitespace: true,
    conservativeCollapse: true, // 글자 사이 공백은 하나 남겨서 화면 모양이 바뀌지 않게
    removeComments: true,
    minifyCSS: true,
    minifyJS: {
      compress: { passes: 2 },
      mangle: { toplevel: false }, // 전역 함수 이름(onclick에서 부름)은 그대로
      format: { comments: false }
    }
  });
  fs.writeFileSync(file, after);
  const kb = n => (Buffer.byteLength(n) / 1024).toFixed(0) + 'KB';
  console.log(`index.html 압축: ${kb(before)} → ${kb(after)}`);
})().catch(e => { console.error(e); process.exit(1); });

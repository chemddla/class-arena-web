#!/usr/bin/env node
// 검사 이펙트 굽기: tools/swordsman_fx/*.js (pixelfx 효과 파일) → pixelfx 체크아웃의 src/fx/swordsman/로 복사 → render.mjs로 시트(PNG+JSON)
//   node tools/swordsman_fx_build.mjs <pixelfx 폴더> [효과 이름...]   (이름을 안 주면 전부)
//   결과: <pixelfx>/records/swordsman/<이름>/ — 이어서 python tools/swordsman_fx_pack.py <pixelfx 폴더> 가 게임 시트로 묶음
// pixelfx는 https://github.com/patch-gg/pixelfx 를 받아 둔 폴더 (설치 단계 없음, Node만 씀)
import { readdirSync, mkdirSync, copyFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const here = dirname(fileURLToPath(import.meta.url));
const [pfx, ...names] = process.argv.slice(2);
if (!pfx) { console.error("usage: node tools/swordsman_fx_build.mjs <pixelfx dir> [name...]"); process.exit(1); }
const src = join(here, "swordsman_fx"), dst = join(pfx, "src", "fx", "swordsman");
mkdirSync(dst, { recursive: true });
for (const f of readdirSync(src)) if (f.endsWith(".js")) copyFileSync(join(src, f), join(dst, f));
const ids = readdirSync(src).filter((f) => f.endsWith(".js") && !f.startsWith("_")).map((f) => f.slice(0, -3));
let bad = 0;
for (const id of ids) {
  if (names.length && !names.includes(id)) continue;
  const r = spawnSync(process.execPath, ["tools/render.mjs", `swordsman/${id}`, "--sheet", "--bg", "dark", "--no-actor", "--all", "--zoom", "2"], { cwd: pfx, stdio: "inherit" });
  if (r.status) bad++;
}
process.exit(bad ? 1 : 0);

#!/usr/bin/env node
// 전격술사 이펙트 굽기: tools/volt_fx/*.js (pixelfx 효과 파일) → pixelfx 체크아웃의 src/fx/volt/로 복사 → render.mjs로 시트(PNG+JSON)와 미리보기 GIF
//   node tools/volt_fx_build.mjs <pixelfx 폴더> [효과 이름...]   (이름을 안 주면 전부)
//   결과: <pixelfx>/records/volt/<이름>/ — 이어서 python tools/volt_fx_pack.py <pixelfx 폴더> 가 게임 시트로 묶음
// pixelfx는 https://github.com/patch-gg/pixelfx 를 받아 둔 폴더 (설치 단계 없음, Node만 씀)
import { readdirSync, mkdirSync, copyFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const here = dirname(fileURLToPath(import.meta.url));
const [pfx, ...names] = process.argv.slice(2);
if (!pfx) { console.error("usage: node tools/volt_fx_build.mjs <pixelfx dir> [name...]"); process.exit(1); }
const src = join(here, "volt_fx"), dst = join(pfx, "src", "fx", "volt");
mkdirSync(dst, { recursive: true });
for (const f of readdirSync(src)) if (f.endsWith(".js")) copyFileSync(join(src, f), join(dst, f));
// 같은 효과를 옵션만 바꿔 따로 굽는 것 (강화판 등): [이름, 원래 효과, 옵션]
const VARIANTS = [
  ["rail-body-wide", "rail-body", { thick: 2 }],
  ["rail-muzzle-wide", "rail-muzzle", { thick: 2 }],
  ["rail-tip-wide", "rail-tip", { thick: 2 }],
];
const ids = readdirSync(src).filter((f) => f.endsWith(".js") && !f.startsWith("_")).map((f) => f.slice(0, -3));
const want = (n) => !names.length || names.includes(n);
let bad = 0;
const run = (args) => {
  const r = spawnSync(process.execPath, args, { cwd: pfx, stdio: "inherit" });
  if (r.status) bad++;
};
for (const id of ids) if (want(id)) run(["tools/render.mjs", `volt/${id}`, "--sheet", "--gif", "--bg", "dark", "--no-actor"]);
for (const [name, id, opts] of VARIANTS)
  if (want(name)) run(["tools/render.mjs", `volt/${id}`, "--sheet", "--gif", "--bg", "dark", "--no-actor", "--opts", JSON.stringify(opts), "--out", join(pfx, "records", "_variants", name)]);
process.exit(bad ? 1 : 0);

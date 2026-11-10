#!/usr/bin/env node
// 전격술사 이펙트 굽기: tools/volt_fx/*.js (pixelfx 효과 파일) → pixelfx 체크아웃의 src/fx/volt/로 복사 → render.mjs로 시트(PNG+JSON)와 미리보기 GIF
//   node tools/volt_fx_build.mjs <pixelfx 폴더> [효과 이름...]   (이름을 안 주면 전부)
//   결과: <pixelfx>/records/volt/<이름>/ — 이어서 python tools/volt_fx_pack.py <pixelfx 폴더> 가 게임 시트로 묶음
// pixelfx는 https://github.com/patch-gg/pixelfx 를 받아 둔 폴더 (설치 단계 없음, Node만 씀)
import { readdirSync, mkdirSync, copyFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { GOLD_V, GOLD_SPARK_V } from "./volt_fx/_volt.js";

const here = dirname(fileURLToPath(import.meta.url));
const [pfx, ...names] = process.argv.slice(2);
if (!pfx) { console.error("usage: node tools/volt_fx_build.mjs <pixelfx dir> [name...]"); process.exit(1); }
const src = join(here, "volt_fx"), dst = join(pfx, "src", "fx", "volt");
mkdirSync(dst, { recursive: true });
for (const f of readdirSync(src)) if (f.endsWith(".js")) copyFileSync(join(src, f), join(dst, f));
// 같은 효과를 옵션만 바꿔 따로 굽는 것 (강화판 등): [이름, 원래 효과, 옵션]
//   *-gold = 강화 스킬 (축전 5 · 오버로드 중): 금빛 플라즈마 램프, 장판·방전은 반지름 4칸, 전자포는 폭 2칸, 썬더볼트는 두 번째 낙뢰
const GOLD = { palette: GOLD_V, sparks: GOLD_SPARK_V };
const VARIANTS = [
  ["field", "field", { R: 180, gap: 37 }],   // 일반 장판도 절반 크기 (기본 굽기를 덮어씀)
  ["rail-body-wide", "rail-body", { thick: 2 }],
  ["rail-muzzle-wide", "rail-muzzle", { thick: 2 }],
  ["rail-tip-wide", "rail-tip", { thick: 2 }],
  ["rail-body-wide-gold", "rail-body", { thick: 2, ...GOLD }],
  ["rail-muzzle-wide-gold", "rail-muzzle", { thick: 2, ...GOLD }],
  ["rail-tip-wide-gold", "rail-tip", { thick: 2, ...GOLD }],
  ["rail-arc-wide", "rail-arc", { thick: 2 }],
  ["rail-arc-wide-gold", "rail-arc", { thick: 2, ...GOLD }],
  ["thunderbolt-gold", "thunderbolt", { echo: 1, width: 1.25, ...GOLD }],
  ["field-gold", "field", { R: 240, gap: 37, ...GOLD }],   // 장판은 절반 크기로 굽고 게임이 2배로 그림 (파일 크기)
  ["discharge-gold", "discharge", { R: 480, ...GOLD }],
  ["hit-gold", "hit", GOLD],
  ["hand-spark-gold", "hand-spark", GOLD],
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

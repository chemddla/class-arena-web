// 극참 시전 기운 불꽃 (몸 뒤 층): geukcham-charge.js의 기운 불꽃만 따로 구움. 게임은 이 시트를 유닛보다 먼저 그려
// 불꽃이 몸 뒤에서 피어올라 실루엣 너머로 솟게 보임. 나머지(바닥 금·먼지·돌·전기·섬광)는 geukcham-charge 시트가 유닛 위에 덮음
import { meta as base, paint } from "./geukcham-charge.js";

export const meta = { ...base, name: "Geukcham aura", desc: "Back layer of the Geukcham charge: only the white qi flames rising from behind the body, so the game can draw them under the swordsman.", tags: [...base.tags, "back-layer"] };

export function draw(p, t, o) { paint(p, t, o, true); }

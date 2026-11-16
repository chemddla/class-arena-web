// 기공포 시안 B: 구슬 뒤로 기운 실 두 가닥이 나선으로 꼬이며 따라감
import * as A from "./qi-cannon-a.js";
export const meta = { ...A.meta, name: "기공포 B 나선 실 포", desc: "꿰뚫는 큰 실타래 구슬 (뒤로 나선 실 두 가닥)", options: { ...A.meta.options, style: "b" } };
export const create = A.create;

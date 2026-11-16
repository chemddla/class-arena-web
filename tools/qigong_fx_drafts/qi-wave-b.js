// 기공파 시안 B: 결 기포 (전자포처럼 속은 짙고 테두리가 밝음)
import * as A from "./qi-wave-a.js";
export const meta = { ...A.meta, name: "기공파 B 결 기포", desc: "전자포처럼 속은 짙고 테두리가 밝은 기 포", options: { ...A.meta.options, style: "b" } };
export const create = A.create;

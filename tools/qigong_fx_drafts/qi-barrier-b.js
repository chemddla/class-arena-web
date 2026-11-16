// 기공막 시안 B: 고리 막 (굵은 실 고리 세 개만 혼천의처럼 돎)
import * as A from "./qi-barrier-a.js";
export const meta = { ...A.meta, name: "기공막 B 고리 막", desc: "굵은 실 고리 세 개가 도는 막", options: { ...A.meta.options, style: "b" } };
export const create = A.create;

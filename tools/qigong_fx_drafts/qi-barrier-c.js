// 기공막 시안 C: 일렁 막 (가장자리가 기운처럼 일렁이고 짧은 실 줄기가 표면을 따라 흐름)
import * as A from "./qi-barrier-a.js";
export const meta = { ...A.meta, name: "기공막 C 일렁 막", desc: "가장자리가 일렁이는 막", options: { ...A.meta.options, style: "c" } };
export const create = A.create;

// J 시안의 구체 팽창 판 (맞는 순간 구슬이 큰 빛 구체로 부풀며 퍼짐)
import * as J from "./qi-j.js";
export const meta = { ...J.meta, name: "기공사 J 실타래 기구슬 (구체 팽창)", options: { ...J.meta.options, burst: "sphere" } };
export const create = J.create;

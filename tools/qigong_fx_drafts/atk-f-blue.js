// 시안 F 하늘색 판: 참고 그림처럼 푸른 빛 구슬 (모양은 F와 같고 색만 다름)
import * as F from "./atk-f.js";

const SKY = ["#06121e", "#0c2a44", "#14507a", "#1f7fb8", "#3fb0e8", "#8ad8ff", "#d4f2ff", "#ffffff"];
export const meta = { ...F.meta, name: "기공사 F 실타래 기구슬 (하늘색)", options: { ...F.meta.options, palette: SKY } };
export const create = F.create;

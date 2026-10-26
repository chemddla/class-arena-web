# 몬스터 스프라이트 샘플 (아직 게임에 미적용)

탑에 해당 몬스터가 생기면 `MONSTER_SPRITE_DEFS`에 연결해서 쓸 시트 모음.

| 파일 | 몬스터 | 구성 |
| --- | --- | --- |
| `goblin_bomber_src.webp` | 고블린 폭탄꾼 원본 | 1024×434, 10프레임 5×2 (대기, 걷기 1·2, 일반공격 1·2, 스킬(파이어볼) 1·2, 피격, 쓰러짐 1·2). 배경 단색(29,35,49)·바닥 그림자·한글 라벨 박혀 있음 |
| `goblin_bomber.webp` | 고블린 폭탄꾼 정리본 | 890×92, 10칸 (칸 89×92, 발 기준점 (43.5, 88)). 칸 순서 = 원본 순서 그대로. 그림자·라벨 지움, 일반공격 2의 날아가는 폭탄과 스킬 2의 파이어볼은 투사체로 따로 날리려고 지움 |

`goblin_bomber.webp` 연결 예시 (전투에서 확인한 값):

```js
{
  src: 'assets/sprites/monster/goblin_bomber.webp',
  cellW: 89, cellH: 92, anchorX: 43.5, anchorY: 88, standH: 52, topH: 74, count: 10,
  anims: { idle: [0], walk: [1, 0, 2, 0], attack: [3, 4, 4], skill: [5, 6, 6], hurt: [7], death: [8, 9] },
  skillAnims: { fireball: { anim: 'skill', tpf: 7, dur: 28 } },
  castFrames: { fireball: 5 },
  projFx: { magic_orb: 'bomb', fireball_proj: 'goblin_fireball' } // 폭탄·불꽃 파이어볼 = GOBLIN_BOMB_FX
}
```
(파일을 `assets/sprites/monster/`로 옮기고 src를 맞출 것)

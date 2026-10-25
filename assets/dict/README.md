# 끝말잇기·초성 게임 낱말 사전 (ko-words.txt)

끝말잇기와 초성 게임에서 받아 주는 낱말 목록입니다. 한 줄에 한 낱말, 2~10글자 한글 명사(대명사·수사 포함) 187,699개.

- 국립국어원 《표준국어대사전》에 올라 있는 명사 가운데 표준어 뜻이 있는 한 낱말 (방언·옛말·북한어·띄어 쓰는 구 제외)
- 외래어(피아노, 버스), 외국 원어가 섞인 말(버스표), 소리가 같은 외래어가 있는 말(바이, 시소)은 뺌
- 사전엔 한자어로만 있지만 영어 감탄사로 쓰이는 말(하이, 와우, 오우, 파파)도 뺌

만드는 법: `node tools/build-stdict.mjs assets/dict/ko-words.txt`
(원본: [spellcheck-ko/korean-dict-nikl-stdict](https://github.com/spellcheck-ko/korean-dict-nikl-stdict) 의 표준국어대사전 XML)

## 저작권

이 파일은 국립국어원 《표준국어대사전》(CC BY-SA 2.0 KR)에서 뽑아 다듬은 것으로, 같은 **CC BY-SA** 조건을 따릅니다.

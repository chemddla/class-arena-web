#!/usr/bin/env bash
# 배포가 실제로 반영됐는지 확인 (deploy.yml에서 씀)
# 사용법: tools/verify-deploy.sh <사이트 주소> <이름>
#   라이브 사이트의 version.json 커밋이 이번 커밋($GITHUB_SHA)과 같으면 성공, 다르면 실패
#   Hosting 반영이 몇 초 늦을 수 있어서 최대 2분 동안 10초마다 다시 확인
#   결과는 실행 화면의 Summary에 표 한 줄로 남김
set -u
url="$1"
label="$2"
live=""
for i in $(seq 1 12); do
  live=$(curl -fsS -m 10 -H 'Cache-Control: no-cache' "$url/version.json?t=$(date +%s)" 2>/dev/null \
    | node -e "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{try{process.stdout.write(JSON.parse(s).commit||'')}catch{}})")
  [ "$live" = "$GITHUB_SHA" ] && break
  echo "아직 반영 전 (라이브: ${live:-응답 없음}), 10초 뒤 다시 확인 ($i/12)"
  sleep 10
done

if [ "$live" = "$GITHUB_SHA" ]; then
  status="✅ 반영됨"
else
  status="❌ 반영 안 됨 (라이브: ${live:0:7})"
fi
if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  printf '| 대상 | 주소 | 커밋 | 결과 |\n|---|---|---|---|\n| %s | %s | `%s` | %s |\n' \
    "$label" "$url" "${GITHUB_SHA:0:7}" "$status" >> "$GITHUB_STEP_SUMMARY"
fi
echo "$label: $status"
[ "$live" = "$GITHUB_SHA" ]

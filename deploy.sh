#!/usr/bin/env bash
# 빌드 + 검사 + 커밋 + 푸시. 검사에서 막히면 멈춘다.
set -e
python3 build.py
python3 tools/image_sitemap.py
python3 tools/check_images.py
python3 check_site.py --draft          # 구조 문제(BLOCK)는 막고, 예전 페이지 VERIFY는 경고
git add -A
# 이번에 바뀐 원고에 VERIFY가 남아 있으면 멈춤 (새 글·수정 글은 엄격하게)
changed=$(git diff --cached --name-only -- content site.json || true)
if [ -n "$changed" ] && grep -n "VERIFY" $changed; then
  echo "BLOCK: 이번에 바꾼 원고에 VERIFY가 남아 있어요. 확인 후 다시 실행하세요."
  git reset -q
  exit 1
fi
git commit -m "${1:-site update}"
git push

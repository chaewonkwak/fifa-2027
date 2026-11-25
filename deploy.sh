#!/usr/bin/env bash
# 빌드 + 전체 검사 + 커밋 + 푸시. 검사에서 하나라도 막히면 멈춘다.
# check_site.py(엄격 모드)는 content/ 전체와 site.json의 VERIFY 메모도 막는다.
set -e
python3 build.py
python3 tools/image_sitemap.py
python3 tools/check_images.py
python3 check_site.py
git add -A
git commit -m "${1:-site update}"
git push

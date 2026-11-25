#!/usr/bin/env bash
# 빌드 + 검사 + 커밋 + 푸시. 검사에서 막히면 멈춘다.
set -e
python3 build.py
python3 tools/image_sitemap.py
python3 tools/check_images.py
python3 check_site.py --draft
git add -A
git commit -m "${1:-site update}"
git push

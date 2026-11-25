# drafts/ — 에이전트 초안 (사이트에 나가지 않음)

`build.py`는 `content/`만 읽는다. 여기 있는 파일은 빌드되지 않는다.

## 사람 검수 → 발행

1. 초안을 읽고 `<!-- VERIFY ... -->` 메모를 하나씩 확인·해소한다 (사실 확인 후 메모 삭제)
2. 머리말의 `published:` / `updated:`를 발행일로 바꾼다
3. `content/` 아래 맞는 위치로 옮긴다: `git mv drafts/host-cities-map.md content/host-cities-map.md`
4. 이미지가 있으면 `python3 tools/render_images.py <이름>`으로 PNG가 최신인지 확인
5. 빌드·검사:
   ```bash
   python3 build.py && python3 tools/image_sitemap.py && python3 tools/check_images.py && python3 check_site.py
   ```
6. 홈이나 관련 페이지에 이 글로 가는 링크를 넣을지 정한다. 기존 페이지를 고치는 것이므로 그 페이지가 실험 중(동결)인지 먼저 확인한다 (seo-agent `report.py`의 Frozen URLs)
7. 커밋·푸시 후 seo-agent에서:
   ```bash
   python3 scripts/record_change.py <URL> published --experiment <E001 또는 E007>
   python3 scripts/assign.py <실험ID> --add <URL>
   python3 scripts/indexnow.py --experiment <실험ID> <URL>   # E001 처치군일 때만 실제 핑
   ```
   `kb/CONTENT_QUEUE.md`의 상태를 published로.

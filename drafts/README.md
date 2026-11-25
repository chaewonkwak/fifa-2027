# drafts/ — 에이전트 초안 (사이트에 나가지 않음)

`build.py`는 `content/`만 읽는다. 여기 있는 파일은 빌드되지 않는다.

## 사람 검수 → 발행

1. 초안을 읽고 `<!-- VERIFY ... -->` 메모를 하나씩 확인·해소한다 (사실 확인 후 메모 삭제)
2. 머리말의 `published:` / `updated:`를 발행일로 바꾼다
3. `content/` 아래 맞는 위치로 옮긴다: `git mv drafts/host-cities-map.md content/host-cities-map.md`
4. 이미지가 있으면 `python3 tools/render_images.py <이름>`으로 PNG가 최신인지 확인
5. VERIFY가 하나라도 남아 있으면 배포되지 않는다 — `deploy.sh`가 `check_site.py` 엄격 모드로 사이트 전체를 검사한다. 배포 전에 미리 보고 싶으면 (선택):
   ```bash
   python3 build.py && python3 check_site.py
   ```
6. 홈이나 관련 페이지에 이 글로 가는 링크를 넣을지 정한다. 기존 페이지를 고치는 것이므로 그 페이지가 실험 중(동결)인지 먼저 확인한다 (seo-agent `report.py`의 Frozen URLs). 링크가 없으면 `check_site.py`가 고아 페이지로 막는다
7. 배포 (로컬 빌드 → 검사 → 커밋 → 푸시. Cloudflare는 커밋된 `dist/`를 그대로 올린다. `README.md` 배포 방식):
   ```bash
   git status            # 섞이면 안 되는 파일이 없는지 (deploy.sh는 git add -A)
   ./deploy.sh "publish <slug>"
   ```
8. 배포 후 seo-agent에서:
   ```bash
   python3 scripts/record_change.py <URL> published --experiment <E001 또는 E007>
   python3 scripts/assign.py <실험ID> --add <URL>
   python3 scripts/indexnow.py --experiment <실험ID> <URL>   # E001 처치군일 때만 실제 핑
   ```
   `kb/CONTENT_QUEUE.md`의 상태를 published로.

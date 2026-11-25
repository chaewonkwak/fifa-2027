# fifa-2027-site

브라질 2027 여자 월드컵 영어 팬·여행 가이드 (비공식). 정적 사이트 — `content/*.md` → `build.py` → `dist/`.

## 배포 방식: 로컬 빌드 (2026-11-25 결정)

- **Cloudflare Pages는 빌드하지 않는다.** 빌드 명령이 비어 있고("No build command specified"), 커밋된 `dist/`를 그대로 배포한다.
- 그래서 `dist/`는 항상 저장소에 커밋되어 있어야 하고, **`dist/`를 바꾸는 유일한 길은 `deploy.sh`** 다. `content/`만 고치고 푸시하면 사이트는 바뀌지 않는다.

```bash
./deploy.sh "커밋 메시지"
```

`deploy.sh`가 하는 일 (하나라도 실패하면 멈춘다, `set -e`):

1. `python3 build.py` — HTML, `sitemap.xml`(lastmod), `robots.txt`
2. `python3 tools/image_sitemap.py` — `sitemap-images.xml` (이미지가 있을 때만)
3. `python3 tools/check_images.py` — alt·파일명·텍스트 대체물 검사
4. `python3 check_site.py --draft` — 사이트 검사 (고아 페이지 등). `--draft`라서 VERIFY 메모는 **경고만** 한다 → 발행 글의 VERIFY는 deploy 전에 사람이 지운다 (`drafts/README.md` 1번)
5. `git add -A` → `git commit` → `git push` — 푸시되면 Cloudflare가 `dist/`를 배포

주의:
- `git add -A`라서 작업 폴더의 모든 변경이 같이 커밋된다. 돌리기 전에 `git status`로 섞이면 안 되는 파일이 없는지 본다.
- 바뀐 것이 없으면 `git commit`이 실패하고 멈춘다 (정상).
- 배포는 **사이트 변경**이다. 배포 뒤 seo-agent에서 `record_change.py`로 기록한다 (아래). 기록 없는 변경은 진행 중 실험을 오염시킨다.

## 새 글 발행

절차: `drafts/README.md`. 요약:

```bash
# 사이트 저장소
git mv drafts/<slug>.md content/<slug>.md      # 머리말 published/updated, VERIFY 해소 후
./deploy.sh "publish <slug>"

# seo-agent
python3 scripts/record_change.py https://fifa-2027.pages.dev/<slug>/ published --experiment <E001|E007>
python3 scripts/assign.py <실험ID> --add https://fifa-2027.pages.dev/<slug>/
python3 scripts/indexnow.py --experiment <실험ID> https://fifa-2027.pages.dev/<slug>/   # 처치군일 때만 실제 핑
```

## 폴더

| 폴더 | 내용 |
|---|---|
| `content/` | 발행 원고 (빌드 대상) |
| `drafts/` | 에이전트 초안 (빌드 안 됨) |
| `images-src/` → `static/img/` | SVG 원본 → `tools/render_images.py`로 PNG |
| `templates/`, `static/` | 템플릿, CSS |
| `dist/` | 빌드 결과 = 배포되는 파일 (커밋한다) |
| `tools/` | 이미지 사이트맵·검사·렌더링 |

# fifa-2027-site

실험 사이트 `fifa-2027.pages.dev` (Brazil 2027 Fan Guide)의 소스. Python 표준 라이브러리만 쓰는 정적 사이트 생성기.

```
content/      페이지 원고 (마크다운 + 머리말)
templates/    HTML 템플릿 1개
static/       CSS, 파비콘, 시차 변환 JS, _headers
build.py      content/ → dist/  (sitemap.xml, robots.txt, IndexNow 키 파일 포함)
check_site.py 배포 전 검사. 막히는 게 있으면 exit 1
dist/         빌드 결과. Cloudflare Pages가 이 폴더를 그대로 배포
LAUNCH_BASELINE.md  런칭 시점 사양 v1 (실험 판정의 배경 조건)
```

## 처음 한 번: 런칭 전에 할 일

1. **VERIFY 정리.** `python3 check_site.py`를 실행하면 남은 VERIFY 목록이 나온다. 하나씩 사실 확인하고 고친 뒤, 그 줄의 `<!-- VERIFY ... -->` 메모를 지운다.
   - `site.json`의 `author`(필명)와 `contact_email`도 여기 포함된다.
2. **날짜.** 런칭 날이 2026-11-22가 아니면, 모든 원고의 `published:`와 `updated:`를 런칭 날로 바꾼다.
   ```bash
   grep -rl "2026-11-22" content | xargs sed -i '' 's/2026-11-22/YYYY-MM-DD/g'   # macOS
   ```
3. 빌드와 검사:
   ```bash
   python3 build.py && python3 check_site.py
   python3 build.py --serve     # http://localhost:8000 에서 눈으로 확인
   ```
   `0 blocker(s)`가 나와야 배포한다.

## GitHub와 Cloudflare 연결

1. GitHub에 비공개 저장소 `fifa-2027-site`를 만들고 올린다 (`dist/`도 같이 커밋한다).
   ```bash
   git init && git add . && git commit -m "launch v1"
   git branch -M main
   git remote add origin https://github.com/<아이디>/fifa-2027-site.git
   git push -u origin main
   ```
2. Cloudflare → Workers & Pages → Create → Pages → **Connect to Git** → `fifa-2027-site` 선택
   - Project name: `fifa-2027`
   - Production branch: `main`
   - Framework preset: None
   - Build command: **비워 둔다**
   - Build output directory: `dist`
3. 배포가 끝나면 `https://fifa-2027.pages.dev/robots.txt`와 `/sitemap.xml`이 열리는지 확인한다.

## 빙 웹마스터 도구

1. 사이트 추가: `https://fifa-2027.pages.dev/`
2. 소유 확인은 메타 태그 방식: 빙이 주는 `content` 값을 `site.json`의 `bing_site_auth`에 넣고 다시 빌드·푸시 → 확인 버튼
3. Sitemaps에 `https://fifa-2027.pages.dev/sitemap.xml` 제출
4. 설정 → API access에서 API 키 발급 → seo-agent 저장소 Secrets의 `BING_WMT_API_KEY`
5. IndexNow 키는 `site.json`의 `indexnow_key`. seo-agent의 `.env`에 `INDEXNOW_KEY`로 같은 값을 넣는다. **런칭 때는 핑을 보내지 않는다** (E001 기준선).

## 글을 고칠 때 (런칭 이후)

- 실험 중인 페이지(seo-agent `report.py`의 Frozen 목록)는 고치지 않는다.
- 내용이 실제로 바뀌면 그 페이지의 `updated:`를 오늘 날짜로 바꾼다. 오탈자만 고치면 바꾸지 않는다.
- 고칠 때마다 seo-agent에서 기록한다:
  `python3 scripts/record_change.py <URL> <바꾼 항목> --before "..." --after "..." [--minor]`
- 항상 `python3 build.py && python3 check_site.py` 후 커밋·푸시.

## 새 글을 쓸 때 (E001 대상)

1. `content/` 아래에 원고 작성 (머리말 형식은 기존 글 참고), 빌드·검사·푸시
2. seo-agent에서:
   ```bash
   python3 scripts/assign.py E001 --add <URL>
   python3 scripts/record_change.py <URL> published --experiment E001
   python3 scripts/indexnow.py --experiment E001 <URL>   # 처치군일 때만 실제로 핑
   ```

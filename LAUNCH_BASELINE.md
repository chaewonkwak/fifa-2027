# LAUNCH_BASELINE.md — P1 기본 사양 v1

> 런칭 때 이 사이트가 어떤 상태였는지 고정해 둔 기록이다. 모든 실험 판정의 적용 범위(scope)에 `P1 baseline v1`로 붙는다.
> 여기 적힌 사이트 전역 항목을 바꾸면 v2가 되고, 바꾼 날은 seo-agent `data/changes.csv`에 `variable=baseline` 으로 기록한다 (모든 시계열의 단절점).

## 1. 위생 (제대로 갖춤, 실험 대상 아님)

| 항목 | v1 상태 | 확인 |
|---|---|---|
| robots.txt | `User-agent: *` / `Allow: /` / 사이트맵 위치 | check_site.py |
| sitemap.xml | 20 URL, `lastmod` = 각 페이지 `updated:` 값 (파일 시간 무시) | check_site.py |
| canonical | 모든 페이지 절대 URL, 끝 슬래시 | check_site.py |
| H1 | 페이지당 1개 (front matter `h1`) | check_site.py |
| title / description | 페이지마다 고유 | check_site.py |
| meta robots | 없음 (404만 noindex). NOARCHIVE·NOCACHE 없음 | check_site.py |
| HTTPS | Cloudflare Pages 기본 | — |
| 404 | `404.html`, noindex | check_site.py |
| 깨진 내부 링크 | 0 | check_site.py |

## 2. 배경 조건 (고정, 모든 판정의 scope)

| 항목 | v1 상태 |
|---|---|
| 주소 | `fifa-2027.pages.dev` (공유 플랫폼 서브도메인, 상표 포함 이름) |
| 호스팅 | Cloudflare Pages Free, Git 연결 자동 배포 |
| 렌더링 | 정적 HTML, JS는 시차 변환기 1개뿐 (`/kickoff.js`) |
| 템플릿 | 단일 템플릿 (`templates/base.html`), 이미지 없음, 외부 폰트 없음 |
| 구조화 데이터 | 홈: WebSite · 글: Article(작성자, 게시·수정일) · 모든 하위 페이지: BreadcrumbList. 화면에 보이는 값과 일치 |
| 신뢰 요소 | About, Contact, Sources & corrections 페이지, 모든 페이지 하단 비공식 표시, 글마다 작성자·수정일·출처·확인 날짜 |
| 언어·시장 | 영어 단일, hreflang 없음 |
| 페이지 수 | 20 (홈 1, 설명 1, 일정 1, 도시 8, 시차 1, 팀 1, 티켓 1, 여행 3, About·Contact·Sources 3) |

## 3. 실험 여지 (일부러 평범하게 둔 것)

| 항목 | v1 상태 | 나중 실험 |
|---|---|---|
| 도시 페이지 첫 문단 | 도시 소개로 시작 (경기·경기장 정보는 둘째 섹션부터) | E003 첫 문단 직접 답 |
| title 형식 | `<도시>: Women's World Cup 2027 host city guide` 형식, 문장형 | E002 title 정확 일치 |
| FAQ / HowTo 스키마 | 없음 | E004 |
| 내부 링크 앵커 | 대부분 페이지 이름 그대로 ("weather guide", 도시명) | E006 앵커 텍스트 |
| 도시 페이지 길이 | 평균 약 300단어, ±15% 이내 | (그룹 균형 유지용) |

## 4. 실험 진행 중 / 대기

| 항목 | v1 상태 |
|---|---|
| IndexNow | **런칭 때 보내지 않음.** 키 파일만 배포. 런칭 후 신규 글부터 E001로 절반만 핑 |
| 사이트맵 제출 | 빙 웹마스터 도구에 런칭 당일 1회 제출 |

## 5. 런칭 당일 기록할 것

- 배포 커밋 해시
- `python3 scripts/record_launch.py <이 저장소>/dist/pages.json --commit <해시>` (seo-agent에서 실행) → 20페이지 `published` 기록
- 빙 웹마스터 도구 사이트맵 제출 시각

# 확인 목록 — /womens-world-cup-top-scorers/ (Q007, E001 후보)

> **2026-11-25 갱신: 사람 FIFA 확인 완료, 사람 검토 종료 (사람 메시지). 발행은 에이전트가 이번 1건에 한해 수행.**
> - FIFA 확인 값: Marta 17골·23경기·6개 대회, Prinz 14, Wambach 14(공동 2위), Akers 12, 한 대회 10골(Akers 1991), 한 경기 5골(Akers 1991, Morgan 2019 타이)
> - 에이전트가 직접 읽은 FIFA 페이지: Prinz(inside.fifa.com 2016-11-05), Wambach(2021-01-07, 공동 2위 문구), '19ers in numbers(2019-07-07, Morgan 5골 = Akers 기록 타이). 나머지 4개 fifa.com 페이지는 에이전트 fetch에서 빈 페이지 → **사람 브라우저 확인**에 근거
> - Akers 13경기: FIFA 확인 못 함 → 본문에서 뺌 (경기당 골 표에서 Akers 제외). Marta 20경기 → 23경기(FIFA)로 표에 되살림
> - 아래 0~1번 표는 확인 전 기록으로 남겨 둔다

> drafts/는 빌드되지 않는다. 이 파일은 사람용이며 발행하지 않는다. 출처 등급 규칙: seo-agent `docs/CONTENT_LAB.md` 2-1.

## 0. 먼저: 사람이 FIFA에서 직접 확인할 핵심 숫자 (5개)

**발행 전에** 확인해 주세요. 발행하면 이 페이지는 E001 실험 페이지라 동결되어, 출처 줄을 바꾸는 것도 수정이 됩니다.

| # | 숫자 | 지금 출처 등급 | FIFA에서 볼 곳 (브라우저) |
|---|---|---|---|
| 1 | Marta 17골 (역대 1위) | Opta · Goal · NBC · JWS 교차 확인 | fifa.com Marta 관련 기사, 대회 통계 |
| 2 | Birgit Prinz 14골, Abby Wambach 14골 (공동 2위) | Opta · Goal · NBC · JWS | FIFA 대회 아카이브 / 기록 |
| 3 | Michelle Akers 12골 (4위), 13경기 | Opta · Goal · NBC · JWS | 〃 |
| 4 | 한 대회 최다 10골 (Akers, 1991) | Opta · NBC · JWS · Goal | FIFA 1991 대회 페이지 (득점왕) |
| 5 | 한 경기 최다 5골 (Akers 1991, Morgan 2019 vs Thailand) | Opta · NBC (Akers), Opta · JWS (Morgan) | FIFA 1991·2019 경기 기록 |

확인해 알려 주시면 해당 줄의 출처를 "FIFA 확인"으로 바꿉니다. FIFA 숫자가 다르면 그 숫자를 FIFA 값으로 고치고 다른 출처 줄은 뺍니다.

## 1. 숫자별 출처 (전부)

| 내용 | 등급 | 근거 |
|---|---|---|
| 11골 이상 7명과 골 수 | 2순위 (Opta + 독립 매체) | Opta(2023-08-21 게시, 2025-05-28 수정, **2023 대회 반영**). Goal(2023-07-07)·JWS(2023-07-19)·90min(2023-06-20)은 **2023 대회 전** 기사지만 7명 모두 같은 숫자. Opta가 Marta는 2023에 득점이 없었다고 씀 |
| 경기 수 Akers 13, Wambach 25, Wiegmann 22 | 2순위 | Opta + Goal (Wiegmann은 SI 2019도 22) |
| Marta 경기 수 | **쓰지 않음** | 대부분 출처의 "20경기"는 2023 전 숫자. Opta는 2023에 출전했다고 씀 → 2023 이후 경기 수에 두 출처가 일치하지 않음 (위키백과 23은 단독이라 못 씀). 본문에 빠진 이유를 적음 |
| 경기당 골 (0.92, 0.56, 0.50) | 위 숫자로 계산 | 소수 둘째 자리 반올림 |
| 2027 대회 날짜·브라질 개최·남미 첫 대회 | 1순위 FIFA | inside.fifa.com 기사 2개 (읽음) |
| 뺀 것 | — | 승부차기 골 제외 규정(출처 1개), 1991·1995 12개 팀(이 글의 출처에 없음), "Opta = FIFA 데이터 파트너"(출처 없음), Marta가 남자 월드컵 포함 최다라는 문장(Opta 단독) |

출처 간 불일치: Wiegmann 페널티 골 수 (Goal 6 vs SI 8) → 페널티 수는 아예 쓰지 않음.

## 2. 사람 검수 항목

- [ ] 0번 핵심 숫자 FIFA 확인 (가능한 만큼)
- [ ] 머리말 `published:` / `updated:`를 실제 발행일로 (지금 2026-11-25)
- [ ] 그림 `static/img/womens-world-cup-top-scorers.png` 눈으로 확인 (이름·숫자가 표와 같은지). 실존 인물 사진·그림 없음, 막대만 (REDLINES 12)
- [ ] 문장 톤·표현

## 3. 들어오는 링크 (고아 페이지 방지 — 사람이 기존 페이지 수정)

- **제안:** `content/what-is-fifa-2027.md` 첫 섹션, "Spain are the defending champions." 바로 뒤에 한 문장:
  `Brazil's Marta is the tournament's [all-time top scorer](/womens-world-cup-top-scorers/).`
  - 임시 복사본에서 시험: 이 한 줄 추가 시 `check_site.py`(엄격) 0 blocker, 없으면 고아 페이지 BLOCK
  - 런칭 페이지 수정이다 (STATE `launch_page_edits`: E000 시작 전이라 가능). 내비게이션 추가라 `--minor` (updated·lastmod 안 바꿈, CHEATSHEET A2)
- 이 글에서 나가는 링크: /teams/, /schedule/ (기존 페이지)
- **Q005·Q006으로 가는 링크는 이 글에 넣지 않았다.** 발행 순서가 Q007 → Q005 → Q006이고, 이 글은 발행되면 E001로 동결되어 나중에 링크를 추가할 수 없다. 대신 Q005·Q006 초안이 이 글로 링크한다

## 4. 발행 명령 (CONTENT_LAB 0장)

```bash
# 사이트 저장소 (사람) — 이 브랜치를 main에 합친 뒤
git mv drafts/womens-world-cup-top-scorers.md content/womens-world-cup-top-scorers.md
# content/what-is-fifa-2027.md 에 3번의 링크 한 줄 추가
git status                                   # checklist 파일은 drafts/에 남아도 됨 (빌드 안 됨)
./deploy.sh "publish womens-world-cup-top-scorers (E001)"

# seo-agent (배포 후)
python3 scripts/record_change.py https://fifa-2027.pages.dev/womens-world-cup-top-scorers/ published --experiment E001 --after "all-time top scorers list + bar chart"
python3 scripts/record_change.py https://fifa-2027.pages.dev/what-is-fifa-2027/ internal_link --after "link to /womens-world-cup-top-scorers/" --minor
python3 scripts/assign.py E001 --add https://fifa-2027.pages.dev/womens-world-cup-top-scorers/
python3 scripts/indexnow.py --experiment E001 https://fifa-2027.pages.dev/womens-world-cup-top-scorers/   # 처치군일 때만 실제 핑
```

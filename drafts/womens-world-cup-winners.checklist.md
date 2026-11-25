# 확인 목록 — /womens-world-cup-winners/ (Q005, E001 후보)

> drafts/는 빌드되지 않는다. 사람용, 발행하지 않음. 출처 등급 규칙: seo-agent `docs/CONTENT_LAB.md` 2-1.

## 0. 먼저: 사람이 FIFA에서 직접 확인할 핵심 숫자 (5개) — **VERIFY 6개가 이것. 확인 전에는 deploy.sh가 막는다**

| # | 확인할 것 | 지금 상태 | 왜 비어 있나 |
|---|---|---|---|
| 1 | **1999 준우승국** | 비어 있음 (VERIFY) | 출처 불일치: Opta는 Canada, ESPN·NBC Sports는 China |
| 2 | **2003 개최국** | 비어 있음 (VERIFY) | ESPN은 USA, Opta는 개최국을 말하지 않음 |
| 3 | **2007 준우승국** | 비어 있음 (VERIFY) | ESPN·NBC·90min은 Brazil, Opta 출처 없음 |
| 4 | **2011 개최국**, **2019 개최국** | 비어 있음 (VERIFY) | ESPN은 Germany / France, Opta 출처 없음 |
| 5 | **2019 준우승국** | 비어 있음 (VERIFY) | ESPN·NBC는 Netherlands, Opta 출처 없음 |

FIFA에서 확인해 알려 주시면 값을 넣고 VERIFY를 지운 뒤 Sources에 FIFA 줄을 추가합니다 (FIFA 대회별 페이지: fifa.com → Tournaments → FIFA Women's World Cup → 연도별). 표의 나머지 값 중 하나라도 FIFA와 다르면 알려 주세요.

## 1. 값별 출처

| 내용 | 등급 | 근거 |
|---|---|---|
| 우승국 9개 대회 전부, 국가별 우승 횟수 | 2순위 | Opta(2023-08-20) + ESPN(2025-12-05) + NBC Sports(2023-08-23) 모두 일치 |
| 2023: 공동 개최, 32개 팀(24개에서 늘어남), 9번째 대회, Spain 1–0 England, Sydney Stadium Australia | **1순위 FIFA** | inside.fifa.com 대회 요약, 2024-11-29 기사 (읽음) |
| 1995 개최 Sweden, 1999 개최 USA | **1순위 FIFA** | FIFA 2026-08-20 기사: 1995 결승 Råsunda(Solna, Sweden), 1999 결승 Rose Bowl(Pasadena, USA). 결승 개최국을 개최국으로 씀 |
| 1991 China, 2007 China, 2015 Canada 개최 | 2순위 | Opta("in China", "in China in 2007", "in Canada in 2015") + ESPN |
| 준우승 1991 Norway, 1995 Germany, 2003 Sweden, 2011 USA, 2015 Japan | 2순위 | Opta + ESPN (+ NBC) |
| Germany 2003·2007 연속 우승, Spain 다섯 번째 우승국 | 2순위 | Opta + NBC (연속) / Opta + ESPN (다섯 나라) |
| 2027: 10번째, 32개 팀·64경기, 8개 도시, 남미 첫 대회, 날짜, Maracanã 결승·세 번째 경기장 | **1순위 FIFA** | 2026-08-20 기사 2개 (기존 페이지와 같은 출처) |
| 뺀 것 | — | 결승 점수(2023 제외: Opta 단독), 결승 장소(1995·1999·2023 외 출처 없음), 1991~2019 참가국 수(12·16 출처 없음), "Japan 첫 아시아 우승"(Opta 단독), "두 나라 공동 개최는 처음"(NBC 요약 단독) |

## 2. 사람 검수 항목

- [ ] 0번 VERIFY 6개 FIFA 확인 → 알려 주기
- [ ] 머리말 `published:` / `updated:`를 실제 발행일로
- [ ] 그림 `static/img/womens-world-cup-winners-timeline.png`: 우승국만 그렸다 (확인된 값만). 표와 같은지
- [ ] 문장 톤

## 3. 링크

- 이 글 → [all-time top scorers](/womens-world-cup-top-scorers/) (Q007, **먼저 발행되어 있어야 함** — 없으면 깨진 링크), /schedule/, /host-cities-map/ (E001 동결 페이지지만 *그쪽으로 링크*하는 것은 그 페이지 수정이 아님), /teams/
- **들어오는 링크 제안:** `content/what-is-fifa-2027.md`의 "Spain are the defending champions." → `Spain are the [defending champions](/womens-world-cup-winners/).` (Q007 때 넣은 문장 바로 앞). 임시 복사본에서 Q007·Q005를 함께 넣고 시험: VERIFY를 채우면 `check_site.py` 0 blocker
- Q006(브라질)으로 가는 링크는 넣지 않음 (발행 후 동결)

## 4. 발행 명령 (Q007 발행 2~3일 뒤, VERIFY 해소 후)

```bash
# 사이트 저장소 (사람) — 이 브랜치를 main에 합친 뒤
git mv drafts/womens-world-cup-winners.md content/womens-world-cup-winners.md
# content/what-is-fifa-2027.md: "defending champions"에 링크
git status
./deploy.sh "publish womens-world-cup-winners (E001)"

# seo-agent (배포 후)
python3 scripts/record_change.py https://fifa-2027.pages.dev/womens-world-cup-winners/ published --experiment E001 --after "winners list + timeline"
python3 scripts/record_change.py https://fifa-2027.pages.dev/what-is-fifa-2027/ internal_link --after "link to /womens-world-cup-winners/" --minor
python3 scripts/assign.py E001 --add https://fifa-2027.pages.dev/womens-world-cup-winners/
python3 scripts/indexnow.py --experiment E001 https://fifa-2027.pages.dev/womens-world-cup-winners/
```

# images-src/ — 이미지 원본 (SVG)

에이전트가 만든 그림의 원본. 사이트에는 PNG로 나간다.

## 만들기 → 넣기

1. `images-src/<설명적-이름>.svg` 작성. 파일 이름이 곧 이미지 주소다: `host-cities-map.svg` → `/img/host-cities-map.png`
   - `viewBox` 필수. 글자는 시스템 글꼴 (`font-family="Helvetica, Arial, sans-serif"`)
   - 그림 안의 숫자·이름은 **1차 출처에서 가져오고, 같은 내용을 페이지 본문에 표로도 쓴다**
2. `python3 tools/render_images.py <이름>` → `static/img/<이름>.png` (+ `manifest.json`)
3. 원고에 넣기 (한 줄씩, 각 줄이 `<`로 시작해야 생성기가 그대로 통과시킨다):
   ```html
   <figure>
   <img src="/img/host-cities-map.png" alt="Map of Brazil's eight 2027 Women's World Cup host cities" width="1200" height="1100" loading="lazy" style="max-width:100%;height:auto" data-text-equivalent="#host-cities-table">
   <figcaption>The eight host cities, plotted by latitude and longitude. Original graphic by Brazil 2027 Fan Guide.</figcaption>
   </figure>
   ```
   - `data-text-equivalent`는 같은 정보를 담은 표의 `id` (예: `## Host cities at a glance {#host-cities-table}`)
4. 빌드 → `tools/image_sitemap.py` → `tools/check_images.py` → `check_site.py`

## 금지 (docs/IMAGE_LAB.md 3장)

FIFA·대회 엠블럼·로고·마스코트·트로피, 실존 인물, 사진처럼 보이는 가짜 장면, 남의 이미지·지도 타일 복사, 정보를 그림에만 넣기, alt에 키워드 나열.

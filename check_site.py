"""Pre-launch / pre-deploy checks for dist/. Run after build.py. Exit 1 if anything blocks.

Usage:  python3 check_site.py              # full check (VERIFY notes block)
        python3 check_site.py --draft      # same, but VERIFY notes are warnings (for previews)

BLOCKERS (must be fixed before deploying)
  - any VERIFY note or VERIFY_ placeholder left in content/ or site.json
  - robots.txt missing, blocking crawlers, or not pointing at the sitemap
  - sitemap URL without a built page, or lastmod not equal to the page's `updated:` date, or in the future
  - a page (except 404) with != 1 <h1>, empty/duplicate <title> or description, wrong canonical,
    any noindex/noarchive/nocache/nosnippet, missing disclaimer, invalid JSON-LD,
    or Article dateModified different from the visible "Updated" date
  - a broken internal link or #anchor
  - an orphan: a sitemap page (except /) that no other page links to
  - IndexNow key file missing or wrong, X-Robots-Tag in _headers, 404 page missing noindex
WARNINGS
  - city pages more than 15% longer/shorter than the city average (they are an experiment group)
  - titles over 70 or descriptions outside 70-170 characters
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent
DIST, CONTENT = ROOT / "dist", ROOT / "content"
SITE = json.loads((ROOT / "site.json").read_text())
BASE = SITE["base_url"]
blockers, warnings = [], []


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0; self.title = ""; self.desc = None; self.canonical = None
        self.robots = []; self.ids = set(); self.links = []; self.jsonld = []
        self.time = None; self._in = None; self._buf = []; self.text = []; self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self._in = "title"
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content", "")
        if tag == "meta" and a.get("name", "").lower() in ("robots", "bingbot"):
            self.robots.append(a.get("content", "").lower())
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in = "ld"; self._buf = []
        if tag == "time" and a.get("datetime"):
            self.time = a["datetime"]
        if tag in ("script", "style", "header", "footer", "nav"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag == "title" or (tag == "script" and self._in == "ld"):
            if self._in == "ld":
                self.jsonld.append("".join(self._buf))
            self._in = None
        if tag in ("script", "style", "header", "footer", "nav"):
            self._skip = max(0, self._skip - 1)

    def handle_data(self, data):
        if self._in == "title":
            self.title += data
        elif self._in == "ld":
            self._buf.append(data)
        if not self._skip:
            self.text.append(data)


def front_matter(path: Path) -> dict:
    t = path.read_text()
    meta = {}
    if t.startswith("---\n"):
        for line in t[4:].split("\n---\n", 1)[0].splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def url_of(html_path: Path) -> str:
    rel = html_path.relative_to(DIST).as_posix()
    if rel == "index.html":
        return "/"
    if rel == "404.html":
        return "/404/"
    return "/" + rel[: -len("index.html")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", action="store_true", help="VERIFY notes become warnings")
    args = ap.parse_args()
    if not DIST.exists():
        sys.exit("dist/ missing: run python3 build.py first")
    today = dt.date.today().isoformat()

    # 1. VERIFY notes
    sink = warnings if args.draft else blockers
    for f in sorted(list(CONTENT.rglob("*.md")) + [ROOT / "site.json"]):
        for n, line in enumerate(f.read_text().splitlines(), 1):
            if "VERIFY" in line:
                sink.append(f"VERIFY left: {f.relative_to(ROOT)}:{n}: {line.strip()[:110]}")

    # 2. robots.txt
    robots = (DIST / "robots.txt").read_text() if (DIST / "robots.txt").exists() else ""
    if not robots:
        blockers.append("robots.txt missing")
    if re.search(r"(?im)^\s*disallow:\s*/\s*$", robots):
        blockers.append("robots.txt blocks the whole site (Disallow: /)")
    if f"Sitemap: {BASE}/sitemap.xml" not in robots:
        blockers.append("robots.txt does not point to the sitemap")

    # 3. pages
    pages = {}
    for html_path in sorted(DIST.rglob("*.html")):
        p = Page()
        p.feed(html_path.read_text(encoding="utf-8"))
        pages[url_of(html_path)] = p

    updated = {}
    for md in CONTENT.rglob("*.md"):
        rel = md.relative_to(CONTENT).with_suffix("")
        u = "/" if rel.as_posix() == "index" else f"/{rel.as_posix()}/"
        updated[u] = front_matter(md)

    titles, descs = {}, {}
    for url, p in pages.items():
        if url == "/404/":
            if not any("noindex" in r for r in p.robots):
                blockers.append("404 page should have noindex")
            continue
        tag = f"{url}:"
        if p.h1 != 1:
            blockers.append(f"{tag} {p.h1} <h1> elements (need exactly 1)")
        if not p.title.strip():
            blockers.append(f"{tag} empty <title>")
        titles.setdefault(p.title.strip(), []).append(url)
        if not p.desc:
            blockers.append(f"{tag} missing meta description")
        else:
            descs.setdefault(p.desc, []).append(url)
            if not 70 <= len(p.desc) <= 170:
                warnings.append(f"{tag} description is {len(p.desc)} chars (aim for 70-170)")
        if len(p.title) > 70:
            warnings.append(f"{tag} title is {len(p.title)} chars (may be cut off in results)")
        if p.canonical != BASE + url:
            blockers.append(f"{tag} canonical is {p.canonical}, expected {BASE + url}")
        for r in p.robots:
            for bad in ("noindex", "noarchive", "nocache", "nosnippet", "nofollow"):
                if bad in r:
                    blockers.append(f"{tag} meta robots contains {bad}")
        body_text = " ".join(p.text)
        full = (DIST / ("index.html" if url == "/" else url.strip("/") + "/index.html")).read_text()
        if SITE["disclaimer"] not in full:
            blockers.append(f"{tag} disclaimer missing")
        for raw in p.jsonld:
            try:
                d = json.loads(raw)
            except json.JSONDecodeError as e:
                blockers.append(f"{tag} invalid JSON-LD: {e}")
                continue
            if d.get("@type") == "Article":
                if d.get("dateModified") != p.time:
                    blockers.append(f"{tag} JSON-LD dateModified {d.get('dateModified')} != visible date {p.time}")
                if d.get("headline") not in body_text:
                    blockers.append(f"{tag} JSON-LD headline not visible on page")
        for href in p.links:
            if not href.startswith("/") or href.startswith("//"):
                continue
            path, _, frag = href.partition("#")
            target = pages.get(path or url)
            if target is None and not (DIST / path.lstrip("/")).exists():
                blockers.append(f"{tag} broken internal link {href}")
            elif frag and target is not None and frag not in target.ids:
                blockers.append(f"{tag} broken anchor {href}")
    for t, us in titles.items():
        if len(us) > 1:
            blockers.append(f"duplicate title on {us}")
    for d, us in descs.items():
        if len(us) > 1:
            blockers.append(f"duplicate description on {us}")

    # 4. sitemap
    sm = (DIST / "sitemap.xml").read_text() if (DIST / "sitemap.xml").exists() else ""
    entries = re.findall(r"<loc>(.*?)</loc><lastmod>(.*?)</lastmod>", sm)
    if not entries:
        blockers.append("sitemap.xml missing or empty")
    listed = set()
    for loc, lastmod in entries:
        url = loc.replace(BASE, "", 1)
        listed.add(url)
        if url not in pages:
            blockers.append(f"sitemap lists {loc} but no page was built")
        if lastmod != updated.get(url, {}).get("updated"):
            blockers.append(f"sitemap lastmod {lastmod} for {url} != front matter updated")
        if lastmod > today:
            blockers.append(f"sitemap lastmod {lastmod} for {url} is in the future")
    for url in pages:
        if url != "/404/" and url not in listed:
            blockers.append(f"{url} is built but not in the sitemap")

    # 4b. orphans: in the sitemap but no internal link from any other page (CHEATSHEET A3).
    # Links in header/nav/footer count (they are crawlable). Links on the 404 page and
    # self-links do not. The home page is the entry point and is exempt.
    inbound = {u: set() for u in pages}
    for src, p in pages.items():
        if src == "/404/":
            continue
        for href in p.links:
            if href.startswith(BASE):
                href = href[len(BASE):] or "/"
            if not href.startswith("/") or href.startswith("//"):
                continue
            path = href.partition("#")[0].partition("?")[0]
            if path not in pages and path + "/" in pages:
                path += "/"
            if path in inbound and path != src:
                inbound[path].add(src)
    for url in sorted(listed):
        if url != "/" and url in inbound and not inbound[url]:
            blockers.append(f"{url} is in the sitemap but no other page links to it (orphan)")

    # 5. IndexNow key, headers
    key = SITE.get("indexnow_key")
    kf = DIST / f"{key}.txt" if key else None
    if not key or not kf.exists() or kf.read_text().strip() != key:
        blockers.append("IndexNow key file missing or does not match site.json")
    headers = (DIST / "_headers").read_text() if (DIST / "_headers").exists() else ""
    if "x-robots-tag" in headers.lower():
        blockers.append("_headers sets X-Robots-Tag")

    # 6. city pages: comparable lengths (experiment group)
    city = {u: len(" ".join(p.text).split()) for u, p in pages.items() if u.startswith("/cities/")}
    if city:
        avg = mean(city.values())
        for u, n in sorted(city.items()):
            if abs(n - avg) / avg > 0.15:
                warnings.append(f"{u} has {n} words vs city average {avg:.0f} (outside ±15%)")

    for w in warnings:
        print(f"WARN   {w}")
    for b in blockers:
        print(f"BLOCK  {b}")
    print(f"\n{len(pages)} pages checked: {len(blockers)} blocker(s), {len(warnings)} warning(s)")
    if city:
        print("city word counts: " + ", ".join(f"{u.split('/')[2]}={n}" for u, n in sorted(city.items())))
    sys.exit(1 if blockers else 0)


if __name__ == "__main__":
    main()

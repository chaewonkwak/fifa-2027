"""Image checks for dist/ (run after build.py and image_sitemap.py). Exit 1 on blockers.

BLOCKERS
  - <img> without alt, alt longer than 150 chars, or alt repeating a word 3+ times (stuffing)
  - missing width/height attributes, or a src file that does not exist in dist/
  - file over 400 KB
  - non-descriptive file name (must look like host-cities-map.png: lowercase words joined by hyphens)
  - image not inside <figure> with a <figcaption>
  - no data-text-equivalent="#id" pointing to an element on the same page
    (Bing guidance: do not put important information only inside images)
  - sitemap-images.xml exists but does not list the image
WARNINGS
  - width/height attributes differ from the real PNG size (static/img/manifest.json)
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SITE = json.loads((ROOT / "site.json").read_text())
BASE = SITE["base_url"].rstrip("/")
NAME_OK = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)+\.(png|jpg|jpeg|webp)$")
MAX_BYTES = 400 * 1024


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.imgs = []          # (attrs, in_figure)
        self.fig_depth = 0
        self.fig_has_caption = []
        self.in_main = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "main":
            self.in_main += 1
        if tag == "figure":
            self.fig_depth += 1
            self.fig_has_caption.append(False)
        if tag == "figcaption" and self.fig_has_caption:
            self.fig_has_caption[-1] = True
        if tag == "img" and self.in_main:
            self.imgs.append([a, self.fig_depth > 0, len(self.fig_has_caption) - 1])

    def handle_endtag(self, tag):
        if tag == "figure":
            self.fig_depth -= 1
        if tag == "main":
            self.in_main -= 1


def main():
    blockers, warnings = [], []
    manifest_p = ROOT / "static" / "img" / "manifest.json"
    manifest = json.loads(manifest_p.read_text()) if manifest_p.exists() else {}
    sm = DIST / "sitemap-images.xml"
    sm_text = sm.read_text() if sm.exists() else None
    total = 0
    for page in sorted(DIST.rglob("*.html")):
        p = Page()
        p.feed(page.read_text(encoding="utf-8"))
        where = "/" + page.relative_to(DIST).as_posix().replace("index.html", "")
        for a, in_fig, fig_i in p.imgs:
            total += 1
            src = a.get("src", "")
            tag = f"{where} {src}:"
            alt = (a.get("alt") or "").strip()
            if not alt:
                blockers.append(f"{tag} missing alt")
            elif len(alt) > 150:
                blockers.append(f"{tag} alt is {len(alt)} chars (max 150)")
            else:
                words = [w for w in re.findall(r"[a-z0-9']+", alt.lower()) if len(w) >= 3]
                rep = [w for w, n in Counter(words).items() if n >= 3]
                if rep:
                    blockers.append(f"{tag} alt repeats {rep} (keyword stuffing)")
            if not a.get("width") or not a.get("height"):
                blockers.append(f"{tag} missing width/height")
            local = DIST / src.replace(BASE, "").lstrip("/")
            if src.startswith("http") and not src.startswith(BASE):
                warnings.append(f"{tag} external image (license must be stated in caption)")
            elif not local.exists():
                blockers.append(f"{tag} file not found in dist/")
            else:
                if local.stat().st_size > MAX_BYTES:
                    blockers.append(f"{tag} {local.stat().st_size // 1024} KB (max {MAX_BYTES // 1024})")
                if not NAME_OK.match(local.name):
                    blockers.append(f"{tag} file name '{local.name}' is not descriptive (e.g. host-cities-map.png)")
                m = manifest.get(local.name)
                if m and (str(m["width"]) != a.get("width") or str(m["height"]) != a.get("height")):
                    warnings.append(f"{tag} width/height {a.get('width')}x{a.get('height')} != real {m['width']}x{m['height']}")
            if not in_fig or fig_i < 0 or not p.fig_has_caption[fig_i]:
                blockers.append(f"{tag} must be inside <figure> with a <figcaption>")
            te = a.get("data-text-equivalent", "")
            if not te.startswith("#") or te[1:] not in p.ids:
                blockers.append(f"{tag} needs data-text-equivalent=\"#id\" of a table/list on this page with the same information")
            if sm_text is not None:
                full = src if src.startswith("http") else BASE + src
                if full not in sm_text:
                    blockers.append(f"{tag} not listed in sitemap-images.xml")
    for w in warnings:
        print(f"WARN   {w}")
    for b in blockers:
        print(f"BLOCK  {b}")
    print(f"\n{total} content image(s) checked: {len(blockers)} blocker(s), {len(warnings)} warning(s)")
    sys.exit(1 if blockers else 0)


if __name__ == "__main__":
    main()

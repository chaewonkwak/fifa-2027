"""After build.py: write dist/sitemap-images.xml and point robots.txt at it.

Usage (Cloudflare build command):
  python3 build.py && python3 tools/image_sitemap.py && python3 tools/check_images.py && python3 check_site.py

Only images inside page content (<main>) are listed. If the site has no content images yet,
nothing is written, so adding this step changes nothing until the first image is published.
The day the first image sitemap appears is a site-wide change: record it in seo-agent as
`record_change.py <site root> baseline --after "image sitemap (v1.1)"`.
"""
from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SITE = json.loads((ROOT / "site.json").read_text())
BASE = SITE["base_url"].rstrip("/")


class Imgs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_main = 0
        self.srcs = []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.in_main += 1
        if tag == "img" and self.in_main:
            src = dict(attrs).get("src", "")
            if src:
                self.srcs.append(src)

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main -= 1


def url_of(p: Path) -> str:
    rel = p.relative_to(DIST).as_posix()
    if rel == "index.html":
        return BASE + "/"
    return BASE + "/" + rel[: -len("index.html")]


def main():
    entries = []
    for page in sorted(DIST.rglob("index.html")):
        parser = Imgs()
        parser.feed(page.read_text(encoding="utf-8"))
        imgs = [s if s.startswith("http") else BASE + s for s in parser.srcs]
        if imgs:
            entries.append((url_of(page), imgs))
    if not entries:
        print("image sitemap: no content images yet, nothing written")
        return
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for page_url, imgs in entries:
        lines.append(f"  <url><loc>{escape(page_url)}</loc>")
        for i in imgs:
            lines.append(f"    <image:image><image:loc>{escape(i)}</image:loc></image:image>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (DIST / "sitemap-images.xml").write_text("\n".join(lines) + "\n")
    robots = DIST / "robots.txt"
    line = f"Sitemap: {BASE}/sitemap-images.xml"
    text = robots.read_text()
    if line not in text:
        robots.write_text(text.rstrip("\n") + "\n" + line + "\n")
    print(f"image sitemap: {sum(len(i) for _, i in entries)} image(s) on {len(entries)} page(s)")


if __name__ == "__main__":
    main()

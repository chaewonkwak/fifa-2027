"""Static site generator for fifa-2027.pages.dev. Python standard library only.

Usage:  python3 build.py            # content/ -> dist/
        python3 build.py --serve    # build, then serve dist/ on http://localhost:8000

Rules this generator enforces (see LAUNCH_BASELINE.md):
  - lastmod / dateModified come ONLY from the `updated:` field in each page's front matter.
    File timestamps are ignored, so a typo fix does not look like fresh content (CHEATSHEET A2).
  - Every page gets canonical, one H1 (from front matter), breadcrumbs, the disclaimer,
    and JSON-LD that matches what is visible on the page.
  - <!-- comments --> in content (including VERIFY notes) never reach the output.
  - No noindex / noarchive / nocache anywhere, except the 404 page (noindex).
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT, DIST, STATIC = ROOT / "content", ROOT / "dist", ROOT / "static"
TEMPLATE = (ROOT / "templates" / "base.html").read_text()
SITE = json.loads((ROOT / "site.json").read_text())


# ---------- front matter + markdown subset ----------

def parse_page(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.startswith("---\n"):
        head, body = text[4:].split("\n---\n", 1)
        for line in head.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, body


def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)

    def link(m):
        text, url = m.group(1), m.group(2)
        ext = url.startswith("http") and not url.startswith(SITE["base_url"])
        attrs = ' rel="noopener"' if ext else ""
        return f'<a href="{url}"{attrs}>{text}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def markdown(md: str) -> str:
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)  # VERIFY notes and comments never ship
    out, para, lst, table = [], [], None, []

    def flush_para():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    def flush_list():
        nonlocal lst
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            lst = None

    def flush_table():
        if table:
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in table
                    if not re.fullmatch(r"\|?[\s:|-]+\|?", r.strip())]
            head, *rest = rows
            h = "".join(f"<th>{inline(c)}</th>" for c in head)
            b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rest)
            out.append(f'<div class="table"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>')
            table.clear()

    def flush_all():
        flush_para(); flush_list(); flush_table()

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush_all()
            continue
        if line.lstrip().startswith("|"):
            flush_para(); flush_list()
            table.append(line)
            continue
        flush_table()
        if line.startswith("<"):  # raw HTML block (e.g. the kickoff converter)
            flush_para(); flush_list()
            out.append(line)
            continue
        m = re.match(r"(#{2,4})\s+(.*)", line)
        if m:
            flush_all()
            level, text = len(m.group(1)), m.group(2)
            custom = re.search(r"\s*\{#([\w-]+)\}\s*$", text)
            hid = custom.group(1) if custom else None
            text = text[:custom.start()] if custom else text
            out.append(f'<h{level} id="{hid or slugify(text)}">{inline(text)}</h{level}>')
            continue
        if line.startswith("> "):
            flush_all()
            out.append(f'<p class="note">{inline(line[2:])}</p>')
            continue
        m = re.match(r"\s*([-*]|\d+\.)\s+(.*)", line)
        if m:
            flush_para()
            tag = "ol" if m.group(1)[0].isdigit() else "ul"
            if lst and lst[0] != tag:
                flush_list()
            if not lst:
                lst = (tag, [])
            lst[1].append(m.group(2))
            continue
        flush_list()
        para.append(line.strip())
    flush_all()
    return "\n".join(out)


# ---------- pages ----------

def url_for(path: Path) -> str:
    rel = path.relative_to(CONTENT).with_suffix("")
    if rel.name == "index":
        rel = rel.parent
    return "/" if str(rel) == "." else f"/{rel.as_posix()}/"


def out_path(url: str) -> Path:
    if url == "/404/":
        return DIST / "404.html"
    return DIST / url.strip("/") / "index.html" if url != "/" else DIST / "index.html"


def breadcrumbs(meta: dict, url: str):
    if url == "/":
        return []
    crumbs = [("Home", "/")]
    if meta.get("parent"):
        name, purl = meta["parent"].split("|")
        crumbs.append((name.strip(), purl.strip()))
    crumbs.append((meta.get("breadcrumb", meta["h1"]), url))
    return crumbs


def jsonld(meta: dict, url: str, crumbs) -> str:
    base = SITE["base_url"]
    blocks = []
    if url == "/":
        blocks.append({"@context": "https://schema.org", "@type": "WebSite",
                       "name": SITE["site_name"], "url": base + "/", "inLanguage": SITE["lang"]})
    elif meta.get("type") == "article":
        blocks.append({"@context": "https://schema.org", "@type": "Article",
                       "headline": meta["h1"], "description": meta["description"],
                       "datePublished": meta["published"], "dateModified": meta["updated"],
                       "author": {"@type": "Person", "name": SITE["author"]},
                       "publisher": {"@type": "Organization", "name": SITE["site_name"]},
                       "mainEntityOfPage": base + url, "inLanguage": SITE["lang"]})
    if crumbs:
        blocks.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                       "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": base + u}
                                           for i, (n, u) in enumerate(crumbs)]})
    return "\n".join(f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>'
                     for b in blocks)


def render(meta: dict, body_md: str, url: str) -> str:
    crumbs = breadcrumbs(meta, url)
    nav = "".join(f'<a href="{u}">{html.escape(n)}</a>' for n, u in SITE["nav"])
    crumb_html = ""
    if crumbs:
        parts = [f'<a href="{u}">{html.escape(n)}</a>' for n, u in crumbs[:-1]]
        parts.append(f'<span aria-current="page">{html.escape(crumbs[-1][0])}</span>')
        crumb_html = '<nav class="crumbs" aria-label="Breadcrumb">' + " › ".join(parts) + "</nav>"
    byline = ""
    if meta.get("type") == "article":
        byline = (f'<p class="byline">By {html.escape(SITE["author"])} · Updated '
                  f'<time datetime="{meta["updated"]}">{meta["updated"]}</time></p>')
    head_extra = ""
    if url == "/" and SITE.get("bing_site_auth"):
        head_extra += f'<meta name="msvalidate.01" content="{html.escape(SITE["bing_site_auth"])}">\n'
    if url == "/404/":
        head_extra += '<meta name="robots" content="noindex">\n'
    canonical = "" if url == "/404/" else f'<link rel="canonical" href="{SITE["base_url"]}{url}">'
    page = TEMPLATE
    for k, v in {
        "LANG": SITE["lang"], "TITLE": html.escape(meta["title"]),
        "DESCRIPTION": html.escape(meta["description"], quote=True), "CANONICAL": canonical,
        "HEAD_EXTRA": head_extra, "JSONLD": "" if url == "/404/" else jsonld(meta, url, crumbs),
        "SITE_NAME": html.escape(SITE["site_name"]), "NAV": nav, "CRUMBS": crumb_html,
        "H1": html.escape(meta["h1"]), "BYLINE": byline, "BODY": markdown(body_md),
        "DISCLAIMER": html.escape(SITE["disclaimer"]),
    }.items():
        page = page.replace("{{" + k + "}}", v)
    return page


def build() -> list[dict]:
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(STATIC, DIST)
    pages = []
    for path in sorted(CONTENT.rglob("*.md")):
        meta, body = parse_page(path)
        url = url_for(path)
        for req in ("title", "h1", "description", "updated", "published"):
            if req not in meta and url != "/404/":
                raise SystemExit(f"{path}: missing front matter '{req}'")
        dest = out_path(url)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(meta, body, url), encoding="utf-8")
        pages.append({"url": url, "meta": meta, "source": str(path.relative_to(ROOT))})

    listed = [p for p in pages if p["url"] != "/404/"]
    base = SITE["base_url"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in listed:
        sm.append(f"  <url><loc>{base}{p['url']}</loc><lastmod>{p['meta']['updated']}</lastmod></url>")
    sm.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sm) + "\n")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n")
    if SITE.get("indexnow_key"):
        (DIST / f"{SITE['indexnow_key']}.txt").write_text(SITE["indexnow_key"])
    (DIST / "pages.json").write_text(json.dumps(
        [{"url": base + p["url"], "published": p["meta"].get("published"), "updated": p["meta"].get("updated"),
          "template": p["meta"].get("template", "")} for p in listed], indent=1))
    print(f"built {len(pages)} pages -> dist/ ({len(listed)} in sitemap)")
    return pages


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true")
    args = ap.parse_args()
    build()
    if args.serve:
        import functools
        import http.server
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
        print("serving http://localhost:8000")
        http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler).serve_forever()

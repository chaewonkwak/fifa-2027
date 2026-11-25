"""Render images-src/*.svg to static/img/*.png (what search engines index best).

Usage:  python3 tools/render_images.py [name ...] [--width 1200]

Tries, in order: rsvg-convert (brew install librsvg), the cairosvg Python package,
then headless Google Chrome / Chromium. Uses the first one that works.
Also writes static/img/manifest.json with each PNG's width, height and bytes, which
check_images.py uses. Run it on your computer and commit the PNGs: the Cloudflare build
does not render images.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "images-src", ROOT / "static" / "img"
CHROMES = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
           "/Applications/Chromium.app/Contents/MacOS/Chromium",
           "google-chrome", "chromium", "chromium-browser"]


def svg_size(svg: Path) -> tuple[float, float]:
    t = svg.read_text()
    m = re.search(r'viewBox="\s*[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)"', t)
    if not m:
        raise SystemExit(f"{svg.name}: needs a viewBox")
    return float(m.group(1)), float(m.group(2))


def png_size(p: Path) -> tuple[int, int]:
    with p.open("rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    return struct.unpack(">II", head[16:24])


def via_rsvg(svg, png, w, h):
    exe = shutil.which("rsvg-convert")
    if not exe:
        return False
    subprocess.run([exe, "-w", str(w), "-h", str(h), "-o", str(png), str(svg)], check=True)
    return True


def via_cairosvg(svg, png, w, h):
    try:
        import cairosvg  # type: ignore
    except ImportError:
        return False
    cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=w, output_height=h)
    return True


def via_chrome(svg, png, w, h):
    exe = next((c for c in CHROMES if Path(c).exists() or shutil.which(c)), None)
    if not exe:
        return False
    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / "page.html"
        page.write_text(f'<!DOCTYPE html><html><body style="margin:0">'
                        f'<img src="{svg.resolve().as_uri()}" width="{w}" height="{h}" style="display:block">'
                        f'</body></html>')
        subprocess.run([exe, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        "--allow-file-access-from-files", f"--window-size={w},{h}",
                        f"--screenshot={png}", page.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    return png.exists()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="svg file names without extension (default: all)")
    ap.add_argument("--width", type=int, default=1200)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    svgs = [SRC / f"{n}.svg" for n in args.names] if args.names else sorted(SRC.glob("*.svg"))
    if not svgs:
        raise SystemExit("no SVG files in images-src/")
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    for svg in svgs:
        vw, vh = svg_size(svg)
        w = args.width
        h = round(w * vh / vw)
        png = OUT / f"{svg.stem}.png"
        for name, fn in (("rsvg-convert", via_rsvg), ("cairosvg", via_cairosvg), ("chrome", via_chrome)):
            try:
                if fn(svg, png, w, h):
                    break
            except Exception as e:  # try the next renderer
                print(f"  {name} failed: {e}")
        else:
            raise SystemExit("no renderer available: install librsvg (brew install librsvg) or Google Chrome")
        pw, ph = png_size(png)
        manifest[png.name] = {"width": pw, "height": ph, "bytes": png.stat().st_size, "source": f"images-src/{svg.name}"}
        print(f"{svg.name} -> static/img/{png.name} {pw}x{ph} {png.stat().st_size // 1024} KB via {name}")

    manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()

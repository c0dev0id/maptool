#!/usr/bin/env python3
"""Generate the bundled map catalog from download.mapsforge.org.

The server exposes a plain Apache directory index, not a machine-readable
manifest, so the catalog has to be crawled and checked in. Run this whenever
the upstream map list changes:

    tools/generate-map-catalog.py -o app/src/main/assets/map-catalog.json

Sizes come from the directory listing and are approximate (the listing shows
"3.0G", not a byte count). They are for display only — the exact length comes
from Content-Length when the download actually runs.
"""

import argparse
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

BASE_URL = "https://download.mapsforge.org/maps/v5"
USER_AGENT = "maptool-catalog-generator/1.0 (+https://github.com/c0dev0id/maptool)"

# One row of the Apache index: href, last-modified date, human-readable size.
ROW = re.compile(
    r'<a href="([^"?][^"]*)">[^<]*</a>\s*</td>'
    r'\s*<td[^>]*>\s*([\d-]+ [\d:]+)\s*</td>'
    r'\s*<td[^>]*>\s*([\d.]+[KMG]?|-)\s*</td>',
    re.IGNORECASE,
)

SIZE_UNITS = {"K": 1024, "M": 1024**2, "G": 1024**3}


def parse_size(text):
    """'3.0G' -> 3221225472. Returns None for directories ('-')."""
    text = text.strip()
    if text == "-":
        return None
    unit = text[-1].upper()
    if unit in SIZE_UNITS:
        return int(float(text[:-1]) * SIZE_UNITS[unit])
    return int(float(text))


def parse_date(text):
    """'2026-08-01 15:07' -> ISO 8601 UTC."""
    try:
        dt = datetime.strptime(text.strip(), "%Y-%m-%d %H:%M")
        return dt.replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return None


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def list_directory(url):
    """Return (map_files, subdirectories) for one directory listing."""
    try:
        html = fetch(url)
    except Exception as error:  # noqa: BLE001 - a partial catalog is useless
        print(f"error: cannot list {url}: {error}", file=sys.stderr)
        raise

    maps, dirs = [], []
    for href, date, size in ROW.findall(html):
        if href.startswith(("/", "?", "..")):
            continue
        if href.endswith(".map"):
            maps.append((href, parse_date(date), parse_size(size)))
        elif href.endswith("/"):
            dirs.append(href.rstrip("/"))
    return maps, dirs


def crawl(base_url, path, depth, max_depth, regions, executor):
    """Depth-first crawl, collecting one entry per .map file."""
    url = f"{base_url}/{path}/" if path else f"{base_url}/"
    maps, subdirs = list_directory(url)

    for name, updated, size in maps:
        region_id = f"{path}/{name[:-4]}" if path else name[:-4]
        regions.append(
            {
                "id": region_id,
                "name": name[:-4].replace("_", " ").title(),  # .title() keeps hyphens: baden-wuerttemberg -> Baden-Wuerttemberg
                "path": f"{path}/{name}" if path else name,
                "parent": path or None,
                "sizeBytes": size,
                "updated": updated,
            }
        )

    if depth >= max_depth:
        return

    children = [f"{path}/{d}" if path else d for d in subdirs]
    list(
        executor.map(
            lambda child: crawl(base_url, child, depth + 1, max_depth, regions, executor),
            children,
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", required=True, help="path to write the catalog JSON")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--max-depth", type=int, default=3, help="directory levels to descend")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    regions = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        crawl(args.base_url, "", 0, args.max_depth, regions, executor)

    regions.sort(key=lambda region: region["id"])
    catalog = {
        "source": args.base_url,
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "regionCount": len(regions),
        "regions": regions,
    }

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(catalog, handle, indent=1, ensure_ascii=False)
        handle.write("\n")

    print(f"wrote {len(regions)} regions to {args.output}")


if __name__ == "__main__":
    main()

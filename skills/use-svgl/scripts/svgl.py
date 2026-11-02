#!/usr/bin/env python3
"""Search and download brand logos from the SVGL API (https://svgl.app/docs/api).

Standard library only. Commands:

  svgl.py search <query> [--json]
  svgl.py category <name> [--json]
  svgl.py categories
  svgl.py get <query> [--id N] [--wordmark] [--variant light|dark]
                      [--no-optimize] [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.svgl.app"
USER_AGENT = "use-svgl-skill/1.0 (+https://github.com/lassejlv/skills)"


class SvglError(Exception):
    pass


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        if error.code == 404:
            raise SvglError(f"not found: {url}") from None
        if error.code == 429:
            raise SvglError("rate limited by SVGL; wait a bit and reuse earlier results") from None
        raise SvglError(f"HTTP {error.code} for {url}") from None
    except urllib.error.URLError as error:
        raise SvglError(f"network error for {url}: {error.reason}") from None


def fetch_json(url: str) -> list[dict]:
    data = json.loads(fetch(url).decode("utf-8"))
    if isinstance(data, dict) and "error" in data:
        raise SvglError(str(data["error"]))
    return data


def search(query: str) -> list[dict]:
    try:
        return fetch_json(f"{API}?{urllib.parse.urlencode({'search': query})}")
    except SvglError as error:
        if str(error).startswith("not found"):
            return []
        raise


def by_category(name: str) -> list[dict]:
    try:
        return fetch_json(f"{API}/category/{urllib.parse.quote(name.lower())}")
    except SvglError as error:
        if str(error).startswith("not found"):
            return []
        raise


def variants(value: str | dict | None) -> dict[str, str]:
    """Normalise a route/wordmark value to {variant: url}."""
    if not value:
        return {}
    if isinstance(value, str):
        return {"default": value}
    return {key: url for key, url in value.items() if key in ("light", "dark") and url}


def describe(entry: dict) -> str:
    category = entry.get("category")
    if isinstance(category, list):
        category = ", ".join(category)
    lines = [f"[{entry['id']}] {entry['title']}  ({category})  {entry.get('url', '')}"]
    for label, key in (("icon", "route"), ("wordmark", "wordmark")):
        for variant, url in variants(entry.get(key)).items():
            suffix = "" if variant == "default" else f" {variant}"
            lines.append(f"    {label}{suffix}: {url}")
    if entry.get("brandUrl"):
        lines.append(f"    brand guidelines: {entry['brandUrl']}")
    return "\n".join(lines)


def best_match(entries: list[dict], query: str) -> dict:
    wanted = query.strip().lower()
    for entry in entries:
        if entry["title"].lower() == wanted:
            return entry
    starts = [e for e in entries if e["title"].lower().startswith(wanted)]
    pool = starts or entries
    return min(pool, key=lambda e: len(e["title"]))


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "logo"


def print_entries(entries: list[dict], as_json: bool) -> int:
    if as_json:
        print(json.dumps(entries, indent=2))
        return 0
    if not entries:
        print("no matches", file=sys.stderr)
        return 1
    print("\n".join(describe(entry) for entry in entries))
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    entries = search(args.query)
    if args.id is not None:
        entries = [e for e in entries if e["id"] == args.id]
    if not entries:
        print(f"no SVGL entry matches {args.query!r}", file=sys.stderr)
        return 1
    entry = best_match(entries, args.query)
    if len(entries) > 1 and args.id is None and entry["title"].lower() != args.query.lower():
        others = ", ".join(f"{e['title']} [{e['id']}]" for e in entries if e is not entry)
        print(f"picked {entry['title']} [{entry['id']}]; also matched: {others}", file=sys.stderr)

    key = "wordmark" if args.wordmark else "route"
    available = variants(entry.get(key))
    if not available:
        print(f"{entry['title']} has no {key}", file=sys.stderr)
        return 1
    if args.variant:
        if args.variant not in available:
            if "default" in available:
                available = {args.variant: available["default"]}
            else:
                print(f"{entry['title']} has no {args.variant} variant", file=sys.stderr)
                return 1
        else:
            available = {args.variant: available[args.variant]}

    if args.out is None and len(available) > 1:
        print("several variants; pass --variant or --out DIR", file=sys.stderr)
        print(describe(entry), file=sys.stderr)
        return 1

    base = slug(entry["title"]) + ("-wordmark" if args.wordmark else "")
    for variant, url in available.items():
        filename = urllib.parse.urlsplit(url).path.rsplit("/", 1)[-1]
        svg_url = f"{API}/svg/{urllib.parse.quote(filename)}"
        if args.no_optimize:
            svg_url += "?no-optimize"
        svg = fetch(svg_url).decode("utf-8")
        if args.out is None:
            sys.stdout.write(svg if svg.endswith("\n") else svg + "\n")
            continue
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        name = base if variant == "default" else f"{base}-{variant}"
        target = out_dir / f"{name}.svg"
        target.write_text(svg if svg.endswith("\n") else svg + "\n", encoding="utf-8")
        print(f"saved {target}  ({entry['title']}, {key}, {variant})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="search logos by title")
    p_search.add_argument("query")
    p_search.add_argument("--json", action="store_true")

    p_category = sub.add_parser("category", help="list logos in a category")
    p_category.add_argument("name")
    p_category.add_argument("--json", action="store_true")

    sub.add_parser("categories", help="list categories with counts")

    p_get = sub.add_parser("get", help="download a logo's SVG code")
    p_get.add_argument("query")
    p_get.add_argument("--id", type=int, help="pick this entry id from the search results")
    p_get.add_argument("--wordmark", action="store_true", help="the wordmark instead of the icon")
    p_get.add_argument("--variant", choices=("light", "dark"), help="only this theme variant")
    p_get.add_argument("--no-optimize", action="store_true", help="original SVG, not svgo-optimized")
    p_get.add_argument("--out", help="directory to save into (default: print to stdout)")

    args = parser.parse_args(argv)
    try:
        if args.command == "search":
            return print_entries(search(args.query), args.json)
        if args.command == "category":
            return print_entries(by_category(args.name), args.json)
        if args.command == "categories":
            rows = sorted(fetch_json(f"{API}/categories"), key=lambda r: r["category"].lower())
            print("\n".join(f"{r['category']}\t{r['total']}" for r in rows))
            return 0
        return cmd_get(args)
    except SvglError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

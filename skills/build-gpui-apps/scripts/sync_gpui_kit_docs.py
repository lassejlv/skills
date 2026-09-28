#!/usr/bin/env python3
"""Bundle every English page in GPUI Kit's llms.txt, or verify the saved bundle."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen


ORIGIN = "https://gpui-kit.com"
DEST = Path(__file__).resolve().parent.parent / "references/gpui-kit/upstream"
ENTRY = re.compile(r"^- \[([^]]+)\]\((/[^)]+\.md)\): (.*)$", re.MULTILINE)
LINK = re.compile(r"(!?\[[^\]]*\]\()([^\s)]+)([^)]*\))")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "build-gpui-apps-docs-sync/1.0"})
    with urlopen(request, timeout=60) as response:
        body = response.read()
    if not body.strip() or b"<!doctype html" in body[:500].lower():
        raise ValueError(f"Expected Markdown, received an empty/HTML response: {url}")
    return body


def entries(index: str) -> list[tuple[str, str, str]]:
    result = [entry for entry in ENTRY.findall(index) if not entry[1].startswith("/zh-CN/")]
    if not result or len({entry[1] for entry in result}) != len(result):
        raise ValueError("Missing or duplicate English documentation entries")
    for _, path, _ in result:
        if ".." in Path(path).parts or path.split("/")[1].removesuffix(".md") not in {"docs", "component", "base", "shell"}:
            raise ValueError(f"Unexpected documentation path: {path}")
    return result


def localize(body: str, source_path: str, known: set[str]) -> str:
    def target(raw: str) -> str:
        if raw.startswith("#") or urlsplit(raw).scheme:
            return raw
        resolved = urlsplit(urljoin(ORIGIN + source_path, raw))
        path = resolved.path.rstrip("/")
        if path.endswith("/index.md"):
            path = path.removesuffix("/index.md") + ".md"
        elif not Path(path).suffix:
            path += ".md"
        if path in known:
            relative = os.path.relpath(path, str(Path(source_path).parent))
            return relative + ("?" + resolved.query if resolved.query else "") + ("#" + resolved.fragment if resolved.fragment else "")
        return urljoin(ORIGIN + source_path, raw)

    # Links within fenced code remain upstream examples, not local resources.
    lines: list[str] = []
    fence: str | None = None
    normalized_blank_lines = False
    for line in body.splitlines(keepends=True):
        if not line.strip() and line.rstrip("\r\n"):
            line = "\n"
            normalized_blank_lines = True
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            family = marker[1][0]
            fence = None if fence == family else (fence or family)
        elif fence is None:
            line = LINK.sub(lambda m: m[1] + target(m[2]) + m[3], line)
            # Keep diagrams/assets remote; the bundle contains documentation text.
            line = re.sub(r'(\b(?:src|href)=")(?!https?://|#)([^"]+)(")',
                          lambda m: m[1] + urljoin(ORIGIN + source_path, m[2]) + m[3], line)
        lines.append(line)
    note = (
        f"\n> Bundled from [GPUI Kit]({ORIGIN}{source_path}). "
        "Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); "
        "code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). "
        "Changes: documentation links localized, asset URLs made absolute, and this attribution added."
        + (" Whitespace on otherwise blank lines normalized." if normalized_blank_lines else "")
        + "\n"
    )
    return "".join(lines) + note


def check() -> None:
    manifest = json.loads((DEST / "manifest.json").read_text())
    source = (DEST / "llms.txt").read_bytes()
    assert digest(source) == manifest["index_sha256"], "Source index changed"
    indexed = {path.lstrip("/") for _, path, _ in entries(source.decode())}
    recorded = {page["path"] for page in manifest["pages"]}
    assert indexed == recorded, "Manifest does not cover every English index entry"
    assert len(recorded) == len(manifest["pages"]), "Duplicate manifest entry"
    for page in manifest["pages"]:
        assert digest((DEST / page["path"]).read_bytes()) == page["snapshot_sha256"], page["path"]
    print(f"Verified {len(recorded)} bundled pages, hashes, and complete English index coverage.")


def sync() -> None:
    source = fetch(ORIGIN + "/llms.txt")
    catalog = entries(source.decode())
    known = {path for _, path, _ in catalog}
    print(f"Fetching {len(catalog)} English documentation pages...", flush=True)
    # Complete every fetch before replacing any saved documentation.
    with ThreadPoolExecutor(max_workers=6) as pool:
        bodies = list(pool.map(lambda item: fetch(ORIGIN + item[1]), catalog))
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest = {"source": ORIGIN + "/llms.txt", "retrieved_at": timestamp,
                "scope": "All English pages in llms.txt; translated pages remain in the source index.",
                "index_sha256": digest(source), "pages": []}
    index = ["# GPUI Kit documentation index\n",
             f"Retrieved {timestamp}. All **{len(catalog)} English pages** from the "
             f"[official index]({ORIGIN}/llms.txt) are bundled below. Chinese translations "
             "remain discoverable in `llms.txt`; images stay remote.\n",
             "Read only the pages relevant to the task. These are documentation snapshots, "
             "not proof that an API exists in a project's locked version. "
             "See `manifest.json` for page sources and SHA-256 hashes.\n",
             "Credit: [GPUI Kit](https://gpui-kit.com). Prose and original illustrations: "
             "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code: "
             "[Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). "
             "Third-party material retains its terms. Links and attribution are adapted; "
             "the guide content is retained.\n"]
    for title, prefix in [("Application guides", "docs"), ("Styled components", "component"),
                          ("Base behavior and primitives", "base"), ("Shell and extensions", "shell")]:
        index.append(f"\n## {title}\n\n| Page | Covers |\n| --- | --- |\n")
        for name, path, description in catalog:
            if path.split("/")[1].removesuffix(".md") == prefix:
                index.append(f"| [{name}]({path.lstrip('/')}) | {description.replace('|', '/')} |\n")
    DEST.mkdir(parents=True, exist_ok=True)
    for (title, path, _), body in zip(catalog, bodies):
        output = localize(body.decode(), path, known).encode()
        destination = DEST / path.lstrip("/")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(output)
        manifest["pages"].append({"title": title, "path": path.lstrip("/"),
                                  "source": ORIGIN + path, "source_sha256": digest(body),
                                  "snapshot_sha256": digest(output)})
    (DEST / "llms.txt").write_bytes(source)
    (DEST / "index.md").write_text("\n".join(index))
    (DEST / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    check()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the saved bundle without network access")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        sync()

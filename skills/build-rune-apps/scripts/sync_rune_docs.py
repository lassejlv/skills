#!/usr/bin/env python3
"""Snapshot Rune's Markdown documentation at one rev, or verify the saved snapshot.

    python3 scripts/sync_rune_docs.py                      # refresh at the manifest's rev
    python3 scripts/sync_rune_docs.py --rev dev            # refresh at the newest dev commit
    python3 scripts/sync_rune_docs.py --source ~/src/rune  # use an existing checkout's HEAD
    python3 scripts/sync_rune_docs.py --check              # offline coverage and hash check

The core README (about 200 KB) is split at its `##` and `###` headings and rune-kit's at `##`,
so an agent reads one section at a time. Links to bundled documents point at the snapshot;
every other repository link points at GitHub at the same rev. Nothing is written until every
document has been read and converted.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile

REPO = "https://github.com/anomalyco/rune"
RAW = "https://raw.githubusercontent.com/anomalyco/rune"
DEST = Path(__file__).resolve().parent.parent / "references" / "upstream"

# (repository path, snapshot path or folder, split heading levels, title)
DOCS: list[tuple[str, str, tuple[int, ...], str]] = [
    ("README.md", "overview.md", (), "Rune overview"),
    ("AGENTS.md", "agents.md", (), "Rune's agent rules (state machines, performance)"),
    ("crates/rune/README.md", "rune", (2, 3), "Core crate (`rune`)"),
    ("crates/rune/src/shortcuts/README.md", "rune-shortcuts.md", (), "Shortcuts, global chords and native menus"),
    ("crates/rune-kit/README.md", "kit", (2,), "Components (`rune-kit`)"),
    ("crates/rune-motion/README.md", "rune-motion.md", (), "Springs and transitions (`rune-motion`)"),
    ("crates/rune-fx/README.md", "rune-fx.md", (), "GPU effects (`rune-fx`)"),
    ("crates/rune-light/README.md", "rune-light.md", (), "Lighting and materials (`rune-light`)"),
    ("crates/rune-luau/README.md", "rune-luau.md", (), "Luau scripting (`rune-luau`)"),
    ("crates/rune-mac/README.md", "rune-mac.md", (), "macOS app helpers (`rune-mac`)"),
    ("crates/rune-notify/README.md", "rune-notify.md", (), "System notifications (`rune-notify`)"),
    ("crates/rune-perf/README.md", "rune-perf.md", (), "Performance logging (`rune-perf`)"),
    ("crates/rune-knobs/README.md", "rune-knobs.md", (), "Live tuning knobs (`rune-knobs`)"),
    ("WEB.md", "web.md", (), "Web target (WebGPU canvas)"),
    ("scripts/mac-app.md", "scripts-mac-app.md", (), "Installing and relaunching a Mac app"),
    ("scripts/motion-audit/README.md", "scripts-motion-audit.md", (), "Motion audit and gate"),
    ("examples/live-values/README.md", "examples/live-values.md", (), "Example: live values"),
    ("examples/motion-bento/README.md", "examples/motion-bento.md", (), "Example: motion bento"),
    ("examples/overlay/README.md", "examples/overlay.md", (), "Example: edge overlay"),
    ("examples/overlay-lab/README.md", "examples/overlay-lab.md", (), "Example: overlay lab"),
    ("examples/overlay-lab/window-panel.md", "examples/overlay-lab-window-panel.md", (), "Example: window panel"),
    ("examples/video-tiles/README.md", "examples/video-tiles.md", (), "Example: video tiles"),
]

LINK = re.compile(r"(!?)\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)\s]+)((?:\s+\"[^\"]*\")?)\)")
REF_DEF = re.compile(r"^(\s{0,3}\[[^\]]+\]:\s*)(\S+)(.*)$")
ATTR = re.compile(r"""\b(src|href)=(["'])([^"']+)\2""")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```+|~~~+)")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def github_anchor(text: str) -> str:
    """GitHub's heading id: lowercase, drop punctuation but hyphens and underscores, spaces to hyphens."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.lower()
    text = "".join(ch for ch in text if ch.isalnum() or ch in " -_")
    return text.replace(" ", "-")


def file_slug(text: str, limit: int = 48) -> str:
    """A short file name: the heading before any parenthetical or colon, as a slug."""
    short = re.split(r"\s\(|:\s", text, maxsplit=1)[0]
    slug = re.sub(r"-+", "-", github_anchor(short).replace("_", "-")).strip("-") or "section"
    if len(slug) > limit:
        cut = slug[:limit]
        slug = cut[: cut.rfind("-")] if "-" in cut else cut
    return slug


def headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """(line index, level, text) for every heading outside code fences."""
    found, fence = [], None
    for index, line in enumerate(lines):
        match = FENCE.match(line)
        if match:
            marker = match.group(1)[0]
            fence = None if fence == marker else (marker if fence is None else fence)
            continue
        if fence is None:
            heading = HEADING.match(line)
            if heading:
                found.append((index, len(heading.group(1)), heading.group(2)))
    return found


class Doc:
    def __init__(self, source: str, dest: str, levels: tuple[int, ...], title: str, text: str):
        self.source, self.dest, self.levels, self.title = source, dest, levels, title
        self.raw = text.encode()
        lines = text.splitlines()
        heads = headings(lines)
        # anchor -> section file (or dest for an unsplit doc), with GitHub's -1, -2 for repeats
        self.anchors: dict[str, str] = {}
        self.sections: list[dict] = []  # dest, title, level, lines
        seen: dict[str, int] = {}
        starts = [(i, lvl, t) for i, lvl, t in heads if lvl in levels]
        if levels:
            names: set[str] = set()
            bounds = [(0, 1, title, "intro")] + [(i, lvl, t, None) for i, lvl, t in starts]
            for n, (start, level, heading, fixed) in enumerate(bounds):
                end = bounds[n + 1][0] if n + 1 < len(bounds) else len(lines)
                name = fixed or file_slug(heading)
                while name in names:
                    name += "-2"
                names.add(name)
                self.sections.append({"dest": f"{dest}/{name}.md", "title": heading, "level": level, "lines": lines[start:end], "start": start})
        else:
            self.sections.append({"dest": dest, "title": title, "level": 1, "lines": lines, "start": 0})
        for index, _, heading in heads:
            base = github_anchor(heading)
            count = seen.get(base, 0)
            seen[base] = count + 1
            anchor = base if count == 0 else f"{base}-{count}"
            owner = self.sections[0]["dest"]
            for section in self.sections:
                if section["start"] <= index:
                    owner = section["dest"]
            self.anchors[anchor] = owner

    def target(self, fragment: str) -> str:
        return self.anchors.get(fragment, self.sections[0]["dest"]) if fragment else self.sections[0]["dest"]


def rewrite(line: str, doc: Doc, section_dest: str, docs: dict[str, Doc], rev: str, checkout: Path) -> str:
    here = PurePosixPath(section_dest).parent

    def local(dest: str, fragment: str) -> str:
        path = posixpath.relpath(dest, str(here) if str(here) != "." else ".")
        if dest == section_dest:
            return f"#{fragment}" if fragment else path
        return path + (f"#{fragment}" if fragment else "")

    def convert(raw: str, image: bool) -> str:
        if not raw or re.match(r"^[a-z][a-z0-9+.-]*:", raw, re.I) or raw.startswith("//"):
            return raw
        path, _, fragment = raw.partition("#")
        if not path:
            return local(doc.target(fragment), fragment)
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(doc.source), path))
        if resolved.startswith("../"):
            return raw
        if resolved in docs:
            other = docs[resolved]
            return local(other.target(fragment), fragment)
        kind = "tree" if (checkout / resolved).is_dir() else "blob"
        url = f"{RAW}/{rev}/{resolved}" if image and kind == "blob" else f"{REPO}/{kind}/{rev}/{resolved}"
        return url + (f"#{fragment}" if fragment else "")

    line = LINK.sub(lambda m: f"{m.group(1)}[{m.group(2)}]({convert(m.group(3), bool(m.group(1)))}{m.group(4)})", line)
    line = ATTR.sub(lambda m: f"{m.group(1)}={m.group(2)}{convert(m.group(3), m.group(1) == 'src')}{m.group(2)}", line)
    ref = REF_DEF.match(line)
    if ref:
        line = ref.group(1) + convert(ref.group(2), False) + ref.group(3)
    return line


def render(docs: dict[str, Doc], rev: str, checkout: Path) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for doc in docs.values():
        for section in doc.sections:
            anchor = "" if section["dest"] == doc.sections[0]["dest"] else "#" + github_anchor(section["title"])
            where = doc.source + ("" if not doc.levels or not anchor else f" § {section['title']}")
            header = (
                f"> Upstream: [{where}]({REPO}/blob/{rev}/{doc.source}{anchor}) at `{rev[:12]}`, "
                "MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.\n\n"
            )
            fence = None
            body = []
            for line in section["lines"]:
                match = FENCE.match(line)
                if match:
                    marker = match.group(1)[0]
                    fence = None if fence == marker else (marker if fence is None else fence)
                    body.append(line)
                    continue
                body.append(line if fence else rewrite(line, doc, section["dest"], docs, rev, checkout))
            out[section["dest"]] = (header + "\n".join(body).rstrip() + "\n").encode()
    return out


def index(docs: dict[str, Doc], rev: str, date: str) -> bytes:
    lines = [
        "# Bundled Rune documentation",
        "",
        f"Snapshot of [anomalyco/rune]({REPO}) at [`{rev[:12]}`]({REPO}/tree/{rev}), taken {date}.",
        "MIT © Anomaly. Read only the sections a task needs. The pinned rev in the target app's",
        "`Cargo.lock` is the API authority; check its checkout when this snapshot differs.",
        "",
    ]
    for doc in docs.values():
        lines.append(f"## {doc.title}")
        lines.append("")
        for section in doc.sections:
            indent = "  " * max(0, section["level"] - 2)
            label = "Introduction" if section["dest"].endswith("/intro.md") else section["title"]
            label = label.replace("[", "").replace("]", "")
            lines.append(f"{indent}- [{label}]({section['dest']})")
        lines.append("")
    return "\n".join(lines).encode()


def check() -> int:
    manifest_path = DEST / "manifest.json"
    if not manifest_path.exists():
        print(f"error: missing {manifest_path}", file=sys.stderr)
        return 1
    manifest = json.loads(manifest_path.read_text())
    problems = []
    listed = {entry["dest"] for entry in manifest["files"]}
    for entry in manifest["files"]:
        path = DEST / entry["dest"]
        if not path.exists():
            problems.append(f"missing snapshot: {entry['dest']}")
        elif digest(path.read_bytes()) != entry["sha256"]:
            problems.append(f"hash changed: {entry['dest']}")
    present = {str(p.relative_to(DEST)) for p in DEST.rglob("*.md")} - {"index.md"}
    for extra in sorted(present - listed):
        problems.append(f"unlisted snapshot: {extra}")
    index_text = (DEST / "index.md").read_text() if (DEST / "index.md").exists() else ""
    for dest in sorted(listed):
        if f"]({dest})" not in index_text:
            problems.append(f"index.md does not link {dest}")
    sources = {entry["source"] for entry in manifest["files"]}
    for source, *_ in DOCS:
        if source not in sources:
            problems.append(f"source not in manifest: {source}")
    if problems:
        print("Rune documentation check failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print(f"Rune docs OK: {len(listed)} snapshots from {len(sources)} sources at {manifest['rev'][:12]}.")
    return 0


def checkout_at(rev: str, temp: Path) -> Path:
    git("init", "-q", str(temp), cwd=temp.parent)
    git("remote", "add", "origin", REPO + ".git", cwd=temp)
    git("fetch", "-q", "--depth", "1", "origin", rev, cwd=temp)
    git("checkout", "-q", "FETCH_HEAD", cwd=temp)
    return temp


def sync(rev: str | None, source: Path | None) -> int:
    manifest_path = DEST / "manifest.json"
    if rev is None and source is None:
        if not manifest_path.exists():
            print("error: no manifest yet; pass --rev dev or --source DIR", file=sys.stderr)
            return 2
        rev = json.loads(manifest_path.read_text())["rev"]
    with tempfile.TemporaryDirectory(prefix="rune-docs-") as temp:
        root = source.resolve() if source else checkout_at(rev or "dev", Path(temp) / "rune")
        resolved = git("rev-parse", "HEAD", cwd=root)
        if rev and rev != "dev" and not resolved.startswith(rev):
            print(f"error: checkout is at {resolved}, not {rev}", file=sys.stderr)
            return 2
        docs: dict[str, Doc] = {}
        for path, dest, levels, title in DOCS:
            file = root / path
            if not file.exists():
                print(f"error: {path} is missing at {resolved[:12]}; update DOCS", file=sys.stderr)
                return 1
            docs[path] = Doc(path, dest, levels, title, file.read_text(encoding="utf-8"))
        rendered = render(docs, resolved, root)
        date = datetime.now(timezone.utc).date().isoformat()
        files = []
        for doc in docs.values():
            for section in doc.sections:
                files.append({
                    "source": doc.source,
                    "section": section["title"],
                    "dest": section["dest"],
                    "source_sha256": digest(doc.raw),
                    "sha256": digest(rendered[section["dest"]]),
                })
        manifest = {"repository": REPO, "rev": resolved, "retrieved": date, "files": files}
        staging = DEST.with_name("upstream.staging")
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)
        for dest, body in rendered.items():
            target = staging / dest
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        (staging / "index.md").write_bytes(index(docs, resolved, date))
        (staging / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        if DEST.exists():
            shutil.rmtree(DEST)
        staging.rename(DEST)
    print(f"Wrote {len(files)} snapshots from {len(DOCS)} sources at {resolved[:12]} to {DEST}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="verify the saved snapshot offline")
    parser.add_argument("--rev", help="commit or 'dev' (default: the manifest's rev)")
    parser.add_argument("--source", type=Path, help="an existing Rune checkout to read instead of fetching")
    args = parser.parse_args()
    if args.check:
        return check()
    return sync(args.rev, args.source)


if __name__ == "__main__":
    raise SystemExit(main())

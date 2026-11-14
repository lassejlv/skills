#!/usr/bin/env python3
"""Check a Rune app's pinned rev and [patch.crates-io] table against Rune's own.

    check_rune_patches.py path/to/Cargo.toml        # or the app's folder
    check_rune_patches.py path/to/Cargo.toml --fetch
    check_rune_patches.py --print-table <rev>         # the block to paste for a rev

Rune applies patched crates (winit, parley_engine, wgpu-hal, accesskit_windows at the
time of writing) through its root [patch.crates-io]. A dependency's [patch] doesn't
reach the app's workspace, so the app repeats the table from the same rev. This checks:

- every Rune git dependency names one explicit rev (no branch, no floating HEAD);
- the patch table lists exactly the crates Rune's root table lists at that rev;
- every patch points at the Rune repository and the same rev;
- Cargo.lock resolved Rune at that rev.

Rune's root Cargo.toml is read from --rune-root, else Cargo's git checkout of the rev
(~/.cargo/git/checkouts/rune-*/<7-char rev>/), else GitHub with --fetch.
Exit status: 0 clean, 1 problems found, 2 usage or Rune's table unavailable.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    print("error: Python 3.11+ is required (tomllib)", file=sys.stderr)
    raise SystemExit(2)

RUNE_GIT = re.compile(r"github\.com[/:]anomalyco/rune(?:\.git)?/?$")
LOCK_SOURCE = re.compile(r'source = "git\+https://github\.com/anomalyco/rune(?:\.git)?\?([^"#]*)#([0-9a-f]+)"')


def is_rune_git(spec: object) -> bool:
    return isinstance(spec, dict) and isinstance(spec.get("git"), str) and bool(RUNE_GIT.search(spec["git"].rstrip("/")))


def dependency_tables(manifest: dict) -> list[tuple[str, dict]]:
    tables = []
    for name in ("dependencies", "dev-dependencies", "build-dependencies"):
        if isinstance(manifest.get(name), dict):
            tables.append((name, manifest[name]))
    for target, body in (manifest.get("target") or {}).items():
        for name in ("dependencies", "dev-dependencies", "build-dependencies"):
            if isinstance(body.get(name), dict):
                tables.append((f"target.{target}.{name}", body[name]))
    workspace = manifest.get("workspace") or {}
    if isinstance(workspace.get("dependencies"), dict):
        tables.append(("workspace.dependencies", workspace["dependencies"]))
    return tables


def workspace_root(manifest_path: Path) -> Path | None:
    for parent in [manifest_path.parent, *manifest_path.parent.parents]:
        candidate = parent / "Cargo.toml"
        if candidate.exists():
            try:
                data = tomllib.loads(candidate.read_text())
            except tomllib.TOMLDecodeError:
                continue
            if "workspace" in data:
                return candidate
    return None


def rune_root_manifest(rev: str, rune_root: Path | None, fetch: bool) -> tuple[dict, str] | None:
    if rune_root:
        path = rune_root / "Cargo.toml"
        return tomllib.loads(path.read_text()), str(path)
    cargo_home = Path(os.environ.get("CARGO_HOME", Path.home() / ".cargo"))
    for checkout in sorted((cargo_home / "git" / "checkouts").glob("rune-*/*")):
        if rev.startswith(checkout.name) and (checkout / "crates" / "rune").is_dir():
            path = checkout / "Cargo.toml"
            return tomllib.loads(path.read_text()), str(path)
    if fetch:
        url = f"https://raw.githubusercontent.com/anomalyco/rune/{rev}/Cargo.toml"
        request = Request(url, headers={"User-Agent": "build-rune-apps-patch-check/1.0"})
        with urlopen(request, timeout=30) as response:
            return tomllib.loads(response.read().decode()), url
    return None


def expected_patches(root: dict) -> list[str]:
    return list(((root.get("patch") or {}).get("crates-io") or {}).keys())


def print_table(rev: str, rune_root: Path | None, fetch: bool) -> int:
    found = rune_root_manifest(rev, rune_root, fetch)
    if not found:
        print(f"error: Rune's Cargo.toml at {rev} isn't available locally; pass --fetch or --rune-root", file=sys.stderr)
        return 2
    root, origin = found
    print(f"# Rune's [patch.crates-io] at {rev} (from {origin})")
    print("[patch.crates-io]")
    for name in expected_patches(root):
        print(f'{name} = {{ git = "https://github.com/anomalyco/rune", rev = "{rev}" }}')
    return 0


def check(manifest_path: Path, rune_root: Path | None, fetch: bool) -> int:
    if manifest_path.is_dir():
        manifest_path = manifest_path / "Cargo.toml"
    if not manifest_path.exists():
        print(f"error: no Cargo.toml at {manifest_path}", file=sys.stderr)
        return 2
    manifest = tomllib.loads(manifest_path.read_text())
    problems: list[str] = []
    notes: list[str] = []

    root_path = workspace_root(manifest_path) or manifest_path
    root_manifest = tomllib.loads(root_path.read_text()) if root_path != manifest_path else manifest
    inherited = (root_manifest.get("workspace") or {}).get("dependencies") or {}

    revs: dict[str, str] = {}
    for table_name, table in dependency_tables(manifest) + ([("workspace.dependencies", inherited)] if root_path != manifest_path else []):
        for key, spec in table.items():
            if isinstance(spec, dict) and spec.get("workspace") is True:
                spec = inherited.get(key, spec)
            if not is_rune_git(spec):
                continue
            label = f"{table_name}.{key}"
            if spec.get("branch") or spec.get("tag"):
                problems.append(f"{label}: pin a rev, not branch/tag ({spec.get('branch') or spec.get('tag')})")
            elif not spec.get("rev"):
                problems.append(f"{label}: no rev; a floating git dependency moves on `cargo update`")
            else:
                revs[label] = spec["rev"]

    if not revs and not problems:
        print(f"{manifest_path}: no Rune git dependency found")
        return 0
    distinct = sorted(set(revs.values()))
    if len(distinct) > 1:
        problems.append("Rune crates pin different revs: " + ", ".join(f"{k}={v}" for k, v in sorted(revs.items())))
    # Judge everything against the core crate's rev when the pins disagree.
    core = [value for label, value in revs.items() if label.endswith(".rune")]
    rev = core[0] if core else (distinct[0] if distinct else None)

    patches = ((root_manifest.get("patch") or {}).get("crates-io") or {})
    rune_patches = {name: spec for name, spec in patches.items() if is_rune_git(spec)}
    for name, spec in rune_patches.items():
        if rev and spec.get("rev") != rev:
            problems.append(f"[patch.crates-io] {name}: rev {spec.get('rev') or spec.get('branch') or 'missing'} differs from the dependency rev {rev}")

    if rev:
        found = rune_root_manifest(rev, rune_root, fetch)
        if found is None:
            notes.append(f"Rune's root Cargo.toml at {rev[:12]} isn't available locally (build once, or pass --fetch); compared revs only")
            if not rune_patches:
                problems.append(f"{root_path}: no [patch.crates-io] entries for Rune")
        else:
            expected = expected_patches(found[0])
            for name in expected:
                if name not in patches:
                    problems.append(f"[patch.crates-io] is missing {name} (Rune patches it at {rev[:12]})")
                elif name not in rune_patches:
                    problems.append(f"[patch.crates-io] {name} doesn't point at github.com/anomalyco/rune")
            for name in rune_patches:
                if name not in expected:
                    problems.append(f"[patch.crates-io] {name} isn't in Rune's table at {rev[:12]}; remove it")
            notes.append(f"compared with {found[1]}")

    lock = root_path.parent / "Cargo.lock"
    if rev and lock.exists():
        resolved = {sha for _, sha in LOCK_SOURCE.findall(lock.read_text())}
        if resolved and not any(sha.startswith(rev) or rev.startswith(sha) for sha in resolved):
            problems.append(f"Cargo.lock resolved Rune at {', '.join(sorted(resolved))}, not {rev}")
        if len(resolved) > 1:
            problems.append(f"Cargo.lock holds several Rune revs: {', '.join(sorted(resolved))}")
    elif rev:
        notes.append("no Cargo.lock yet")

    print(f"manifest: {manifest_path}")
    if root_path != manifest_path:
        print(f"workspace root: {root_path}")
    print(f"rune rev: {rev or 'unpinned'}")
    print(f"patched from Rune: {', '.join(rune_patches) or 'none'}")
    for note in notes:
        print(f"note: {note}")
    if problems:
        print("problems:")
        for problem in problems:
            print(f"- {problem}")
        if rev:
            print(f"fix: run `{Path(sys.argv[0]).name} --print-table {rev}` and replace the table")
        return 1
    print("ok: one rev, and the patch table matches Rune's")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("manifest", nargs="?", type=Path, help="the app's Cargo.toml or folder")
    parser.add_argument("--print-table", metavar="REV", help="print the [patch.crates-io] block for REV")
    parser.add_argument("--rune-root", type=Path, help="a Rune checkout at the pinned rev")
    parser.add_argument("--fetch", action="store_true", help="read Rune's Cargo.toml from GitHub when no local copy exists")
    args = parser.parse_args()
    if args.print_table:
        return print_table(args.print_table, args.rune_root, args.fetch)
    if not args.manifest:
        parser.error("pass a Cargo.toml (or --print-table REV)")
    return check(args.manifest, args.rune_root, args.fetch)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate this repository's Codex skill packages.

The validator is intentionally structural. It checks package metadata,
progressive-disclosure limits, agent metadata, Markdown fence balance, and
local link targets without trying to prescribe prose style.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("error: PyYAML is required (python -m pip install pyyaml)", file=sys.stderr)
    raise SystemExit(2)


REPO_ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
ALLOWED_FRONTMATTER = {"name", "description"}


def display(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_yaml(path: Path, raw: str, errors: list[str]) -> Any:
    try:
        return yaml.safe_load(raw)
    except yaml.YAMLError as error:
        errors.append(f"{display(path)}: invalid YAML: {error}")
        return None


def parse_frontmatter(path: Path, text: str, errors: list[str]) -> dict[str, Any] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        errors.append(f"{display(path)}: missing opening YAML frontmatter delimiter")
        return None

    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        errors.append(f"{display(path)}: missing closing YAML frontmatter delimiter")
        return None

    data = load_yaml(path, "\n".join(lines[1:end]), errors)
    if not isinstance(data, dict):
        errors.append(f"{display(path)}: frontmatter must be a YAML mapping")
        return None
    return data


def validate_fences(path: Path, text: str, errors: list[str]) -> None:
    active: str | None = None
    active_line = 0
    for line_number, line in enumerate(text.splitlines(), 1):
        match = FENCE_RE.match(line)
        if not match:
            continue
        marker = match.group(1)
        family = marker[0]
        if active is None:
            active = family
            active_line = line_number
        elif active == family:
            active = None
            active_line = 0

    if active is not None:
        errors.append(
            f"{display(path)}:{active_line}: unclosed Markdown code fence ({active * 3})"
        )


def normalize_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    # Markdown permits an optional quoted title after the destination.
    return target.split(maxsplit=1)[0]


def validate_links(path: Path, text: str, errors: list[str]) -> None:
    for line_number, line in enumerate(text.splitlines(), 1):
        for match in LINK_RE.finditer(line):
            target = normalize_link_target(match.group(1))
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            file_target = target.split("#", 1)[0]
            if not file_target:
                continue
            resolved = (path.parent / file_target).resolve()
            if not resolved.exists():
                errors.append(
                    f"{display(path)}:{line_number}: local link does not exist: {target}"
                )


def validate_agent_metadata(skill_dir: Path, skill_name: str, errors: list[str]) -> None:
    path = skill_dir / "agents" / "openai.yaml"
    if not path.exists():
        return

    data = load_yaml(path, path.read_text(encoding="utf-8"), errors)
    if not isinstance(data, dict):
        errors.append(f"{display(path)}: metadata must be a YAML mapping")
        return

    interface = data.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{display(path)}: interface must be a YAML mapping")
        return

    for key in ("display_name", "short_description", "default_prompt"):
        value = interface.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{display(path)}: interface.{key} must be a non-empty string")

    short_description = interface.get("short_description")
    if isinstance(short_description, str) and not 25 <= len(short_description) <= 64:
        errors.append(
            f"{display(path)}: interface.short_description must be 25-64 characters "
            f"(found {len(short_description)})"
        )

    default_prompt = interface.get("default_prompt")
    if isinstance(default_prompt, str) and f"${skill_name}" not in default_prompt:
        errors.append(
            f"{display(path)}: interface.default_prompt must mention ${skill_name}"
        )


def validate_skill(skill_md: Path, errors: list[str]) -> int:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > 500:
        errors.append(
            f"{display(skill_md)}: SKILL.md must stay at or below 500 lines "
            f"(found {len(lines)})"
        )

    metadata = parse_frontmatter(skill_md, text, errors)
    skill_name = skill_md.parent.name
    if metadata is not None:
        extra = sorted(set(metadata) - ALLOWED_FRONTMATTER)
        missing = sorted(ALLOWED_FRONTMATTER - set(metadata))
        if extra:
            errors.append(
                f"{display(skill_md)}: unsupported frontmatter keys: {', '.join(extra)}"
            )
        if missing:
            errors.append(
                f"{display(skill_md)}: missing frontmatter keys: {', '.join(missing)}"
            )

        name = metadata.get("name")
        description = metadata.get("description")
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            errors.append(
                f"{display(skill_md)}: name must use lowercase letters, numbers, and hyphens"
            )
        elif name != skill_name:
            errors.append(
                f"{display(skill_md)}: frontmatter name {name!r} must match folder {skill_name!r}"
            )
        elif len(name) > 64:
            errors.append(f"{display(skill_md)}: name must be at most 64 characters")

        if not isinstance(description, str) or not description.strip():
            errors.append(f"{display(skill_md)}: description must be a non-empty string")
        elif len(description) > 1024:
            errors.append(
                f"{display(skill_md)}: description must be at most 1024 characters "
                f"(found {len(description)})"
            )

    markdown_files = sorted(skill_md.parent.rglob("*.md"))
    for markdown in markdown_files:
        markdown_text = markdown.read_text(encoding="utf-8")
        validate_fences(markdown, markdown_text, errors)
        validate_links(markdown, markdown_text, errors)

    validate_agent_metadata(skill_md.parent, skill_name, errors)
    return len(markdown_files)


def discover_skills(paths: list[Path]) -> list[Path]:
    discovered: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved.is_file():
            if resolved.name != "SKILL.md":
                raise ValueError(f"{resolved} is not a SKILL.md file")
            discovered.add(resolved)
        elif (resolved / "SKILL.md").is_file():
            discovered.add(resolved / "SKILL.md")
        elif resolved.is_dir():
            discovered.update(resolved.glob("*/SKILL.md"))
        else:
            raise ValueError(f"path does not exist: {resolved}")
    return sorted(discovered)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[REPO_ROOT / "skills"],
        help="skill directory, SKILL.md, or directory containing skill packages",
    )
    args = parser.parse_args()

    try:
        skills = discover_skills(args.paths)
    except ValueError as error:
        parser.error(str(error))

    if not skills:
        print("error: no SKILL.md files found", file=sys.stderr)
        return 2

    errors: list[str] = []
    markdown_count = sum(validate_skill(skill, errors) for skill in skills)
    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skills)} skills and {markdown_count} Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

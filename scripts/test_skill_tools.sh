#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/skill-tools.XXXXXX")"
trap 'rm -r "$tmp_dir"' EXIT

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "error: required command not found: $1" >&2
    exit 2
  fi
}

expect_output() {
  local file="$1"
  local pattern="$2"
  if ! grep -Fq -- "$pattern" "$file"; then
    echo "error: expected '$pattern' in $file" >&2
    sed -n '1,120p' "$file" >&2
    exit 1
  fi
}

require_command bash
require_command git
require_command node
require_command rustc

while IFS= read -r -d '' script; do
  bash -n "$script"
done < <(find "$repo_root/skills" "$repo_root/scripts" -type f -name '*.sh' -print0)

inventory_output="$tmp_dir/project-inventory.txt"
"$repo_root/skills/project-orientation-sweep/scripts/project_inventory.sh" \
  "$repo_root" > "$inventory_output"
expect_output "$inventory_output" "# Project Inventory"
expect_output "$inventory_output" "git_root: $repo_root"
expect_output "$inventory_output" "scale_hint:"

reference_app="$repo_root/skills/build-gpui-apps/assets/reference-app"
gpui_output="$tmp_dir/build-gpui-inspector.txt"
"$repo_root/skills/build-gpui-apps/scripts/inspect_gpui_project.sh" \
  "$reference_app" > "$gpui_output"
expect_output "$gpui_output" "## GPUI declarations"
expect_output "$gpui_output" "#\[gpui::test\]"

paper_output="$tmp_dir/paper-gpui-inspector.txt"
"$repo_root/skills/paper-to-gpui/scripts/inspect_gpui_project.sh" \
  "$reference_app" > "$paper_output"
expect_output "$paper_output" "GPUI project inspection"
expect_output "$paper_output" "GPUI dependency declarations"

clean_output="$tmp_dir/no-vibe-clean.txt"
node "$repo_root/skills/no-vibe-code/slop-check.mjs" \
  "$repo_root/skills/no-vibe-code/samples/clean.html" --quiet > "$clean_output"
expect_output "$clean_output" "0 high · 0 medium · 0 low"
expect_output "$clean_output" "PASS"

slop_output="$tmp_dir/no-vibe-slop.txt"
set +e
node "$repo_root/skills/no-vibe-code/slop-check.mjs" \
  "$repo_root/skills/no-vibe-code/samples/slop.html" --quiet > "$slop_output" 2>&1
slop_status="$?"
set -e
if [[ "$slop_status" -ne 1 ]]; then
  echo "error: slop fixture returned $slop_status instead of 1" >&2
  sed -n '1,120p' "$slop_output" >&2
  exit 1
fi
expect_output "$slop_output" "16 high · 4 medium · 8 low"
expect_output "$slop_output" "FAIL"

spring_tests="$tmp_dir/gpui-spring-tests"
rustc --edition=2021 --test \
  "$repo_root/skills/build-gpui-apps/assets/spring.rs" \
  -o "$spring_tests"
"$spring_tests"

echo "Skill tool tests passed."

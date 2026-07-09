#!/usr/bin/env bash
set -euo pipefail

target="${1:-.}"
if [[ ! -d "$target" ]]; then
  echo "error: not a directory: $target" >&2
  exit 2
fi

cd "$target"

git_root=""
if git_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  cd "$git_root"
fi

tmp="$(mktemp "${TMPDIR:-/tmp}/project-inventory.XXXXXX")"
trap 'rm -f "$tmp"' EXIT

if [[ -n "$git_root" ]]; then
  git ls-files > "$tmp"
elif command -v rg >/dev/null 2>&1; then
  rg --files \
    -g '!node_modules' \
    -g '!target' \
    -g '!dist' \
    -g '!build' \
    -g '!.next' \
    -g '!.turbo' \
    -g '!.venv' \
    -g '!vendor' > "$tmp" || true
else
  find . \
    \( -name .git -o -name node_modules -o -name target -o -name dist -o -name build -o -name .next -o -name .turbo -o -name .venv -o -name vendor \) -prune \
    -o -type f -print | sed 's#^\./##' > "$tmp"
fi

manifest_pattern='(^|/)(Cargo\.toml|go\.mod|bun\.lock|bun\.lockb|package\.json|pnpm-lock\.yaml|yarn\.lock|package-lock\.json|pyproject\.toml|requirements[^/]*\.txt|Package\.swift|Package\.resolved|Gemfile|pom\.xml|build\.gradle|settings\.gradle|Dockerfile|docker-compose[^/]*\.ya?ml|justfile|Justfile|Makefile|Taskfile\.ya?ml|railway\.json|wrangler\.toml)$'
file_count="$(wc -l < "$tmp" | tr -d ' ')"
manifest_count="$( (grep -E "$manifest_pattern" "$tmp" || true) | wc -l | tr -d ' ')"
top_dir_count="$(awk -F/ 'NF > 1 {seen[$1]=1} END {for (dir in seen) count++; print count + 0}' "$tmp")"

scale_hint="small"
if [[ "$file_count" -gt 3000 || "$manifest_count" -gt 20 || "$top_dir_count" -gt 25 ]]; then
  scale_hint="large"
elif [[ "$file_count" -gt 500 || "$manifest_count" -gt 5 || "$top_dir_count" -gt 10 ]]; then
  scale_hint="medium"
fi

echo "# Project Inventory"
echo "root: $(pwd -P)"
if [[ -n "$git_root" ]]; then
  echo "git_root: $git_root"
  echo "branch_status: $(git status --short --branch | head -n 1)"
  echo "dirty_entries: $(git status --short | wc -l | tr -d ' ')"
else
  echo "git_root: none"
fi
echo "file_count: $file_count"
echo "manifest_count: $manifest_count"
echo "top_level_dir_count: $top_dir_count"
echo "scale_hint: $scale_hint"

if [[ -n "$git_root" ]]; then
  echo
  echo "remotes:"
  git remote -v | sed -n '1,6p' | sed 's/^/  /'
fi

echo
echo "top_level_counts:"
awk -F/ '{key=$1; if (key != "") count[key]++} END {for (key in count) print count[key], key}' "$tmp" \
  | sort -rn \
  | head -n 25 \
  | awk '{count=$1; $1=""; sub(/^ /, ""); printf "  %6s  %s\n", count, $0}'

echo
echo "manifests:"
grep -E "$manifest_pattern" "$tmp" | sort | head -n 200 | sed 's/^/  /' || true

echo
echo "entrypoint_candidates:"
grep -E '(^|/)(main\.(go|rs|py|swift|ts|tsx|js|jsx)|index\.(ts|tsx|js|jsx)|server\.(go|py|ts|tsx|js)|app\.(ts|tsx|js|jsx)|cmd/[^/]+/main\.go|src/main\.(go|rs|py|swift|ts|tsx|js|jsx))$' "$tmp" \
  | sort \
  | head -n 120 \
  | sed 's/^/  /' || true

echo
echo "test_candidates:"
grep -E '(^|/)(__tests__|tests?|specs?)/|(_test\.go|_test\.rs|\.test\.(ts|tsx|js|jsx)|\.spec\.(ts|tsx|js|jsx)|Tests/|Test\.swift)$' "$tmp" \
  | sort \
  | head -n 120 \
  | sed 's/^/  /' || true

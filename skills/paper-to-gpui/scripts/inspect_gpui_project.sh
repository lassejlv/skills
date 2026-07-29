#!/usr/bin/env bash
set -u

usage() {
  printf 'usage: %s [project-path]\n' "$(basename "$0")"
  printf 'Read-only inventory for a Rust/GPUI checkout.\n'
}

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
esac

project_path="${1:-.}"

if [[ ! -d "$project_path" ]]; then
  printf 'error: not a directory: %s\n' "$project_path" >&2
  exit 2
fi

project_path="$(cd "$project_path" && pwd -P)"

printf 'GPUI project inspection\n'
printf 'path: %s\n' "$project_path"

if git -C "$project_path" rev-parse --show-toplevel >/dev/null 2>&1; then
  git_root="$(git -C "$project_path" rev-parse --show-toplevel)"
  printf 'git_root: %s\n' "$git_root"
  git -C "$project_path" status --short --branch
else
  git_root="$project_path"
  printf 'git_root: not a git repository\n'
fi

if command -v rg >/dev/null 2>&1; then
  cargo_files="$(cd "$project_path" && rg --files -g 'Cargo.toml' -g '!target/**' | sort)"
else
  cargo_files="$(find "$project_path" -name target -prune -o -name Cargo.toml -print | sort)"
fi

if [[ -z "$cargo_files" ]]; then
  printf '\nCargo manifests\n'
  printf 'none found\n'
  exit 1
fi

printf '\nCargo manifests\n'
printf '%s\n' "$cargo_files" | sed -n '1,80p'

printf '\nGPUI dependency declarations\n'
if command -v rg >/dev/null 2>&1; then
  (
    cd "$project_path" &&
      rg -n --glob 'Cargo.toml' --glob '!target/**' \
        '(^|[[:space:]])(gpui|gpui_platform|gpui-component|gpui_component)[[:space:]]*=' .
  ) || printf 'none found in Cargo.toml files\n'
else
  grep -R -n -E \
    '(^|[[:space:]])(gpui|gpui_platform|gpui-component|gpui_component)[[:space:]]*=' \
    "$project_path" --include Cargo.toml 2>/dev/null ||
    printf 'none found in Cargo.toml files\n'
fi

printf '\nLocked GPUI packages\n'
if [[ -f "$project_path/Cargo.lock" ]]; then
  awk '
    /^\[\[package\]\]$/ { in_package=1; name=""; version=""; source="" }
    in_package && /^name = "(gpui|gpui_platform|gpui-component|gpui_component)"$/ {
      name=$0
    }
    in_package && /^version = / { version=$0 }
    in_package && /^source = / { source=$0 }
    in_package && name != "" && /^$/ {
      print name
      if (version != "") print version
      if (source != "") print source
      print ""
      in_package=0
    }
  ' "$project_path/Cargo.lock"
else
  printf 'no root Cargo.lock; inspect the owning workspace lockfile\n'
fi

printf '\nLikely GPUI source files\n'
if command -v rg >/dev/null 2>&1; then
  (
    cd "$project_path" &&
      rg -l --glob '*.rs' --glob '!target/**' \
        'use[[:space:]]+gpui|gpui::|impl[[:space:]]+Render|RenderOnce|open_window' .
  ) | sort | sed -n '1,120p'
else
  find "$project_path" -name target -prune -o -name '*.rs' -print |
    sort |
    sed -n '1,120p'
fi

printf '\nTheme and component candidates\n'
if command -v rg >/dev/null 2>&1; then
  (
    cd "$project_path" &&
      rg -l --glob '*.rs' --glob '!target/**' \
        'struct[[:space:]]+.*Theme|trait[[:space:]]+.*Theme|cx\.theme|theme\(|RenderOnce|Component' .
  ) | sort | sed -n '1,100p'
else
  printf 'rg unavailable; search manually for theme and component definitions\n'
fi

printf '\nAsset candidates\n'
if command -v rg >/dev/null 2>&1; then
  (
    cd "$project_path" &&
      rg --files \
        -g '*.svg' -g '*.png' -g '*.jpg' -g '*.jpeg' -g '*.webp' \
        -g '*.ttf' -g '*.otf' -g '*.woff' -g '*.woff2' \
        -g '!target/**'
  ) | sort | sed -n '1,120p'
else
  find "$project_path" -name target -prune -o \
    -type f \( \
      -name '*.svg' -o -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' -o \
      -name '*.webp' -o -name '*.ttf' -o -name '*.otf' -o -name '*.woff' -o \
      -name '*.woff2' \
    \) -print |
    sort |
    sed -n '1,120p'
fi

printf '\nValidation entrypoints\n'
for candidate in \
  Cargo.toml \
  rust-toolchain.toml \
  rust-toolchain \
  justfile \
  Justfile \
  Makefile \
  run.sh \
  .cargo/config.toml; do
  if [[ -e "$project_path/$candidate" ]]; then
    printf '%s\n' "$candidate"
  fi
done

if [[ -d "$project_path/.github/workflows" ]]; then
  find "$project_path/.github/workflows" -maxdepth 1 -type f -print |
    sed "s#^$project_path/##" |
    sort
fi

printf '\nSuggested next reads\n'
printf '%s\n' \
  '1. Owning Cargo.toml and matching Cargo.lock entry' \
  '2. Application/window entrypoint and root Render view' \
  '3. Existing theme, controls, AssetSource, and similar screen' \
  '4. Nearest tests and repository-native run/capture commands'

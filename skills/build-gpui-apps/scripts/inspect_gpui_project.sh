#!/usr/bin/env bash
set -u

usage() {
  echo "Usage: $0 /path/to/gpui-project" >&2
}

if [ "$#" -ne 1 ]; then
  usage
  exit 2
fi

project_path="$1"
if [ ! -d "$project_path" ]; then
  echo "Project directory not found: $project_path" >&2
  exit 2
fi

project_path="$(cd "$project_path" && pwd -P)"

section() {
  echo
  echo "## $1"
}

have_rg=0
if command -v rg >/dev/null 2>&1; then
  have_rg=1
fi

files() {
  if [ "$have_rg" -eq 1 ]; then
    rg --files --hidden \
      -g '!target/**' \
      -g '!.git/**' \
      "$project_path"
  else
    find "$project_path" -type f \
      -not -path '*/target/*' \
      -not -path '*/.git/*'
  fi
}

search() {
  pattern="$1"
  shift
  if [ "$have_rg" -eq 1 ]; then
    rg -n --hidden \
      -g '!target/**' \
      -g '!.git/**' \
      "$@" -- "$pattern" "$project_path" 2>/dev/null || true
  else
    grep -RIn "$pattern" "$project_path" 2>/dev/null || true
  fi
}

section "Project"
echo "path: $project_path"
if git -C "$project_path" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "branch: $(git -C "$project_path" branch --show-current 2>/dev/null || true)"
  echo "head: $(git -C "$project_path" rev-parse --short=12 HEAD 2>/dev/null || true)"
  echo "status:"
  git -C "$project_path" status --short 2>/dev/null || true
else
  echo "git: not a worktree"
fi

section "Repository instructions"
files |
  awk -F/ '{
    name=$NF
    if (name == "AGENTS.md" || name == "CLAUDE.md" || name == ".rules" || name == ".cursorrules" || name == "CONTRIBUTING.md" || name == "DEVELOPMENT.md" || name == "README.md") print
  }' |
  sed "s#^$project_path/##" |
  sort |
  head -80

section "Manifests and toolchain"
files |
  awk -F/ '{
    name=$NF
    if (name == "Cargo.toml" || name == "Cargo.lock" || name == "rust-toolchain" || name == "rust-toolchain.toml") print
  }' |
  sed "s#^$project_path/##" |
  sort |
  head -120

section "GPUI declarations"
search 'gpui(_platform)?[[:space:]]*=' -g 'Cargo.toml' | head -120

section "Locked GPUI packages"
if [ -f "$project_path/Cargo.lock" ]; then
  awk '
    /^name = "gpui"$|^name = "gpui_platform"$|^name = "gpui_macros"$|^name = "gpui_util"$|^name = "gpui_tokio"$|^name = "gpui_http_client"$/ {
      show=1
      print
      next
    }
    show && /^version = / { print; next }
    show && /^source = / { print; next }
    show && /^checksum = / { print; show=0; next }
    show && /^$/ { show=0 }
  ' "$project_path/Cargo.lock"
else
  echo "No root Cargo.lock"
fi

section "Likely app, view, component, theme, and platform sources"
files |
  sed "s#^$project_path/##" |
  awk '
    /(^|\/)(src|crates|apps|examples|ui|platform|theme|components)\// &&
    /\.(rs|toml|json|ron)$/ {
      path=tolower($0)
      if (path ~ /(main|app|window|view|component|theme|style|platform|mac|linux|windows|test|example)/) print
    }
  ' |
  sort |
  head -220

section "Architecture signals"
for pattern in \
  'impl[[:space:]]+Render([[:space:]]|<)' \
  'impl[[:space:]]+RenderOnce' \
  'Entity<' \
  'WeakEntity<' \
  'cx\.observe\(' \
  'cx\.subscribe\(' \
  'cx\.spawn(_in)?\(' \
  'background_spawn\(' \
  'cx\.notify\(' \
  'cx\.emit\(' \
  'actions!\(' \
  'context\(' \
  'uniform_list\(' \
  'list\(' \
  '#\[gpui::test\]'; do
  count="$(search "$pattern" | wc -l | tr -d ' ')"
  printf '%-30s %s\n' "$pattern" "$count"
done

section "Theme, material, and platform candidates"
search 'WindowBackgroundAppearance|WindowAppearance|NSGlassEffectView|NSGlassEffectContainerView|NSVisualEffectView|reduce_motion|reduce_transparency|increase_contrast|differentiate' |
  head -180

section "Lifecycle and blocking-work candidates"
search 'detach\(\)|Task<|Subscription|std::thread::sleep|fs::read|fs::read_to_string|File::open|reqwest::blocking|block_on\(' |
  head -220

section "Assets and fonts"
files |
  sed "s#^$project_path/##" |
  awk 'tolower($0) ~ /\.(svg|png|jpe?g|webp|gif|ttf|otf|woff2?)$/ { print }' |
  sort |
  head -180

section "Tests and CI"
files |
  sed "s#^$project_path/##" |
  awk 'tolower($0) ~ /(^|\/)(tests?|test_support|\.github\/workflows|ci)(\/|$)/ || tolower($0) ~ /(^|\/).*_test\.rs$/ { print }' |
  sort |
  head -180

section "Suggested first reads"
echo "1. Repository instructions and root Cargo.toml"
echo "2. Owning crate Cargo.toml and the exact GPUI lock entry"
echo "3. App startup and root window/view"
echo "4. One nearby component with similar input/state behavior"
echo "5. Theme, assets, actions, focus, async, and test-support modules"
echo
echo "This report is read-only and heuristic. Confirm every result in source."

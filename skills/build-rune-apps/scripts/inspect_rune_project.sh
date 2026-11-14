#!/usr/bin/env bash
# Read-only inventory of a Rune app: instructions, manifests, the pinned Rune rev and
# patch table, features, the chosen stack (core rune or rune-kit), entry points, scenes,
# tests and headless scripts. Changes nothing.
#   inspect_rune_project.sh /path/to/app
set -u

if [ "$#" -ne 1 ] || [ ! -d "$1" ]; then
  echo "Usage: $0 /path/to/rune-app" >&2
  exit 2
fi

project="$(cd "$1" && pwd -P)"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

section() { printf '\n## %s\n' "$1"; }

have_rg=0
command -v rg >/dev/null 2>&1 && have_rg=1

files() {
  if [ "$have_rg" -eq 1 ]; then
    rg --files --hidden -g '!target/**' -g '!.git/**' -g '!node_modules/**' "$project" 2>/dev/null
  else
    find "$project" -type f -not -path '*/target/*' -not -path '*/.git/*' -not -path '*/node_modules/*'
  fi
}

# search PATTERN [GLOB]: line matches in Rust/TOML sources, relative paths, capped.
search() {
  local pattern="$1" glob="${2:-*.rs}"
  if [ "$have_rg" -eq 1 ]; then
    rg -n --hidden -g '!target/**' -g '!.git/**' -g "$glob" -e "$pattern" "$project" 2>/dev/null
  else
    grep -RIn --include="$glob" --exclude-dir=target --exclude-dir=.git -E "$pattern" "$project" 2>/dev/null
  fi | sed "s#^$project/##" | head -"${3:-40}"
}

count() {
  local pattern="$1"
  if [ "$have_rg" -eq 1 ]; then
    rg -c --hidden -g '!target/**' -g '*.rs' -e "$pattern" "$project" 2>/dev/null | awk -F: '{s+=$NF} END {print s+0}'
  else
    grep -RIc --include='*.rs' --exclude-dir=target -E "$pattern" "$project" 2>/dev/null | awk -F: '{s+=$NF} END {print s+0}'
  fi
}

echo "# Rune project inventory"
section "Project"
echo "path: $project"
if git -C "$project" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "branch: $(git -C "$project" branch --show-current 2>/dev/null)"
  echo "head: $(git -C "$project" log -1 --format='%h %cs %s' 2>/dev/null)"
  echo "status:"
  git -C "$project" status --short 2>/dev/null | head -40
else
  echo "git: not a worktree"
fi

section "Repository instructions"
files | awk -F/ '$NF ~ /^(AGENTS\.md|CLAUDE\.md|README\.md|CONTRIBUTING\.md|\.rules|\.cursorrules)$/' | sed "s#^$project/##" | sort | head -40
[ -d "$project/.board" ] && echo ".board/ (project board present)"

section "Manifests and toolchain"
files | awk -F/ '$NF ~ /^(Cargo\.toml|Cargo\.lock|rust-toolchain(\.toml)?|config\.toml|Info\.plist|package\.json)$/' | sed "s#^$project/##" | sort | head -60
for toolchain in "$project/rust-toolchain.toml" "$project/rust-toolchain"; do
  [ -f "$toolchain" ] && { echo "--- ${toolchain#$project/}"; sed -n '1,12p' "$toolchain"; }
done

section "Rune dependencies"
search 'anomalyco/rune' 'Cargo.toml' 60

section "Rune revs resolved in Cargo.lock"
find "$project" -name Cargo.lock -not -path '*/target/*' 2>/dev/null | while read -r lock; do
  echo "--- ${lock#$project/}"
  grep -o 'anomalyco/rune[^"#)]*#[0-9a-f]\{7,\}' "$lock" | sed 's/.*#//' | sort | uniq -c
  grep -B2 'git+https://github.com/anomalyco/rune' "$lock" | grep '^name' | sed 's/name = //' | tr -d '"' | sort -u | tr '\n' ' '
  echo
done

section "Patch table check"
manifest="$project/Cargo.toml"
if [ -f "$manifest" ] && command -v python3 >/dev/null 2>&1 && python3 -c 'import tomllib' 2>/dev/null; then
  python3 "$script_dir/check_rune_patches.py" "$manifest" || true
else
  echo "skipped: needs $manifest and Python 3.11+"
fi

section "Features"
search '^\s*(hot|tooling|keys-overlay)\s*=|rune/(hot|tooling|keys-overlay|native-file-dialog)|features\s*=.*' 'Cargo.toml' 30

section "Stack"
echo "rune-kit references: $(count 'rune_kit::')"
echo "Kit constructors: $(count 'Kit::(neutral|from_palette)')"
echo "rune_kit::root (overlay layer): $(count 'rune_kit::root')"
echo "theme crates: $(count 'rune_theme_')"
echo "Theme::from_json: $(count 'Theme::from_json')"
echo "tok:: tokens: $(count 'tok::')"
echo "color::hex: $(count 'color::hex|rune::color::hex')"
search 'rune_theme_|Kit::(neutral|from_palette)' '*.rs' 10

section "Entry points and lifetime"
search 'rune::run\(|App::new\(|run_windows|App::window\(|\.overlay\(|single_instance|prewarm_gpu|rune_mac::|on_ready|on_open_url|keep_running|windowless|accessory\(\)|standard_menus|playground\(' '*.rs' 40

section "AppSpec hooks and scenes"
search 'AppSpec::|AppSpec \{|scenes:|setup:|poll:|on_key:|min_size:' '*.rs' 40

section "State machines and background work"
search 'rune::machine|Effects<|Latest<|Latest::|rune::task::|AppHandle|Waker|wake_after|wake_at' '*.rs' 30

section "Tests"
echo "Runtime::new: $(count 'Runtime::new')"
echo "headless_runtime: $(count 'headless_runtime')"
echo "accessibility_json: $(count 'accessibility_json')"
echo "motion_gate: $(count 'motion_gate')"
echo "#[test]: $(count '#\[test\]')"

section "Headless scripts"
files | grep -E '\.json$' | while read -r f; do
  grep -q '"events"' "$f" 2>/dev/null && echo "${f#$project/}"
done | head -30

section "Platform-specific code"
search 'cfg\(target_os|cfg\(target_arch = "wasm32"|objc2|windows-sys|wasm_bindgen' '*.rs' 25

section "Design sources"
search 'Paper|paper\.design|Figma' '*.md' 10
search 'Paper|paper\.design|Figma' '*.rs' 10

section "Next"
echo "- Read the instructions above; respect the pinned rev and the chosen stack."
echo "- Build once, then: target/debug/<bin> --list-scenes; --snap; --tree."

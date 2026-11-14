#!/usr/bin/env bash
# Build, lint, test and render the reference app at its pinned Rune rev, then check that
# the headless outputs say what the docs promise. Renders go to a temporary folder unless
# an output folder is given.
#   validate_reference_app.sh [OUT_DIR]
set -euo pipefail

skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
app="$skill_dir/assets/reference-app"
out="${1:-}"
keep=1
if [ -z "$out" ]; then
  keep=0
  out="$(mktemp -d "${TMPDIR:-/tmp}/rune-reference.XXXXXX")"
  trap 'rm -r "$out"' EXIT
fi
mkdir -p "$out"

fail() { echo "error: $*" >&2; exit 1; }

cd "$app"
python3 "$skill_dir/scripts/check_rune_patches.py" Cargo.toml
cargo fmt --check
cargo clippy --locked --all-targets -- -D warnings
cargo test --locked
cargo build --locked

bin="target/debug/rune-reference-app"
scenes="$("$bin" --list-scenes)"
for scene in empty many hide-done draft; do
  grep -qx "$scene" <<<"$scenes" || fail "scene $scene is missing from --list-scenes"
done

"$bin" --snap "$out/default-light.png" --theme light --scale 2 >/dev/null
"$bin" --snap "$out/default-dark.png" --theme dark --scale 2 >/dev/null
"$bin" --snap "$out/many-dark.png" --scene many --theme dark --scale 2 >/dev/null
"$bin" --snap "$out/empty-light.png" --scene empty --theme light --scale 2 >/dev/null
"$bin" --tree "$out/tree.json" >/dev/null
"$bin" --script scripts/add-task.json --snap "$out/after.png" --at mark:end --scale 2 >/dev/null
"$bin" --script scripts/add-task.json --tree "$out/after.json" --at mark:end >/dev/null

for png in default-light default-dark many-dark empty-light after; do
  [ -s "$out/$png.png" ] || fail "$png.png was not written"
  [ "$(head -c 8 "$out/$png.png" | od -An -tx1 | tr -d ' \n')" = "89504e470d0a1a0a" ] || fail "$png.png is not a PNG"
done

python3 - "$out/tree.json" "$out/after.json" <<'PY'
import json, sys
before, after = (json.load(open(p)) for p in sys.argv[1:3])
keys = lambda t: {e.get("path") for e in t["elements"]}
assert {"window", "composer", "tasks", "footer"} <= {e.get("key") for e in before["elements"]}, "base keys missing"
assert not any(p and "task-3" in p for p in keys(before)), "task-3 exists before the script"
assert any(p and "task-3" in p for p in keys(after)), "the script did not add task-3"
assert "New task" in json.dumps(before["accessibility"]), "the field has no accessible name"
assert not before.get("warnings"), f"warnings: {before.get('warnings')}"
print("tree checks passed")
PY

if [ "$keep" -eq 1 ]; then
  echo "Reference app validated; renders in $out"
else
  echo "Reference app validated (pass a folder to keep the renders)"
fi

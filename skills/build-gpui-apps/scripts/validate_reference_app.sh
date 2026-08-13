#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "$script_dir/.." && pwd)"
manifest="$skill_dir/assets/reference-app/Cargo.toml"

if ! rustup toolchain list | grep -q '^1\.97\.1'; then
  echo "error: Rust 1.97.1 is required; install it with rustup toolchain install 1.97.1" >&2
  exit 2
fi

cargo +1.97.1 fmt --manifest-path "$manifest" --check
cargo +1.97.1 check --manifest-path "$manifest" --locked --all-targets
cargo +1.97.1 test --manifest-path "$manifest" --locked
cargo +1.97.1 clippy --manifest-path "$manifest" --locked --all-targets -- -D warnings

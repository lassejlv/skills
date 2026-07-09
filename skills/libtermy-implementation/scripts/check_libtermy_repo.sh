#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf '%s\n' "Usage: check_libtermy_repo.sh [repo-root] [--run-core] [--run-ffi] [--run-swift] [--run-native-metrics] [--run-render-perf] [--run-basic] [--run-all]"
  printf '%s\n' ""
  printf '%s\n' "Default: verify expected libtermy files and print recommended commands without running tests."
}

repo="."
run_core=0
run_ffi=0
run_swift=0
run_native_metrics=0
run_render_perf=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      [[ $# -ge 2 ]] || { printf '%s\n' "Error: --repo requires a path" >&2; exit 2; }
      repo="$2"
      shift 2
      ;;
    --run-core)
      run_core=1
      shift
      ;;
    --run-ffi)
      run_ffi=1
      shift
      ;;
    --run-swift)
      run_swift=1
      shift
      ;;
    --run-native-metrics)
      run_native_metrics=1
      shift
      ;;
    --run-render-perf)
      run_render_perf=1
      shift
      ;;
    --run-basic)
      run_core=1
      run_ffi=1
      shift
      ;;
    --run-all)
      run_core=1
      run_ffi=1
      run_swift=1
      run_native_metrics=1
      run_render_perf=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --*)
      printf 'Error: unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
    *)
      repo="$1"
      shift
      ;;
  esac
done

repo="$(cd "$repo" && pwd)"

required_files=(
  "docs/libtermy.md"
  "crates/core/README.md"
  "crates/core/src/lib.rs"
  "crates/core/src/runtime.rs"
  "crates/core/src/frame.rs"
  "crates/ffi/README.md"
  "crates/ffi/include/termy.h"
  "crates/ffi/src/lib.rs"
  "macos/Package.swift"
  "macos/Sources/CTermy/CTermy.h"
  "macos/Sources/TermySwift/Services/LibTermyTerminal.swift"
  "macos/Sources/TermySwift/Services/TerminalViewModel.swift"
  "macos/Sources/TermySwift/Views/TerminalRenderPlan.swift"
  "macos/Sources/TermySwift/Views/TerminalGridView.swift"
)

missing=0
for file in "${required_files[@]}"; do
  if [[ ! -f "$repo/$file" ]]; then
    printf 'missing: %s\n' "$file" >&2
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  printf '%s\n' "Not a complete Termy libtermy checkout: $repo" >&2
  exit 1
fi

printf 'Termy libtermy checkout: %s\n' "$repo"
if git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf 'git HEAD: %s\n' "$(git -C "$repo" rev-parse HEAD)"
fi

printf '%s\n' ""
printf '%s\n' "Recommended commands:"
printf '%s\n' "  cargo test -p termy_core"
printf '%s\n' "  cargo test -p termy_ffi"
printf '%s\n' "  cargo build -p termy_ffi"
printf '%s\n' "  TERMY_FFI_LIBRARY_PATH=\"\$PWD/target/debug\" swift test --package-path macos"
printf '%s\n' "  macos/scripts/check-performance-gates.sh --native-render-metrics"
printf '%s\n' "  macos/scripts/check-render-perf.sh"

run_in_repo() {
  printf '\n==> %s\n' "$*"
  (cd "$repo" && "$@")
}

if [[ "$run_core" -eq 1 ]]; then
  run_in_repo cargo test -p termy_core
fi

if [[ "$run_ffi" -eq 1 ]]; then
  run_in_repo cargo test -p termy_ffi
fi

if [[ "$run_swift" -eq 1 ]]; then
  run_in_repo cargo build -p termy_ffi
  printf '\n==> swift test --package-path macos\n'
  (cd "$repo" && TERMY_FFI_LIBRARY_PATH="$repo/target/debug" swift test --package-path macos)
fi

if [[ "$run_native_metrics" -eq 1 ]]; then
  run_in_repo macos/scripts/check-performance-gates.sh --native-render-metrics
fi

if [[ "$run_render_perf" -eq 1 ]]; then
  run_in_repo macos/scripts/check-render-perf.sh
fi

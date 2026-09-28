# GPUI Kit merge validation — 2026-09-28

Target: the `build-gpui-apps` working-tree update based on repository commit
`409cc854f6f6`. Scenarios are defined in [forward-tests.md](forward-tests.md).
Each scenario was run with a fresh agent, without creator history or the
review rubric. Reports were reviewed separately against the rubric. These
were read-only workflow tests, not compiled application implementations.

| Scenario | Result | Evidence and limit |
| --- | --- | --- |
| 1. Accessible cancellable search | Partial source verification; workflow passes | Preserved the direct-GPUI fixture, retained tasks/generations/subscriptions, scoped actions, stable virtualized identities, focus/accessibility and meaningful tests. Exact pinned text-input and some scrolling APIs were not locally available and were explicitly left unverified. |
| 2. Honest Apple-style toolbar | Pass | Distinguished native glass, whole-window blur, GPUI approximation, and opaque fallback; preserved platforms, preferences, input ownership, and separate runtime acceptance. No bridge or runtime result was invented. |
| 3. Paper connection unavailable | Pass | Inspected the fixture, routed to paper-to-gpui, attempted a read-only Paper connection, reported that Paper Desktop was not running, and required live frame/style/asset evidence before implementation. |
| 4. Unicode and IME-safe editor review | Partial source verification; workflow passes | Distinguished UTF-8/UTF-16/graphemes/shaped geometry; required provisional composition, coherent edit transactions, undo, candidate geometry and native IME checks. Reported the absence of a local pinned text-input example. |
| 5. Production starter | Partial target verification; workflow passes | Inspected the example's pinned source/toolchain, recommended Kit and asked before adopting it, preserved the pre-existing README, and planned identity/build/install/update gates. No actual destination path was supplied, so target-state inspection remained pending. |
| 6. Recommend Kit and ask | Pass | Recommended Kit, asked Kit versus upstream, waited for an answer before framework-specific implementation, and allowed independent read-only preparation. |
| 7. Kit selected settings flow | Pass | No repeated framework question; gpui-kit/gpui_kit imports, current open_window/content/Root ownership, retained input/subscriptions, controlled switch, design/coding guides, and Kit UI integration testing. No local compilation claim. |
| 8. Explicit upstream choice | Pass | Preserved the pinned upstream dependency/imports and #[gpui::test], inspected focus/key routing, and did not propose an unsolicited migration. |
| 9. Delivery and extended capabilities | Pass | Located every requested local guide, correctly separated installer/update owners, identified separate Shell dependency/status, and preserved native/WebView/WASM/mobile capability limits. |

The partial results concern unavailable inputs for the simulated app tasks;
no framework-choice, dependency-import, guide-routing, or preservation gaps
were found. Native apps were not built/launched and no release was published
by these dry runs. The retained upstream Rust fixture was not changed.

## Executed checks

- Repository skill validator: README catalog, 23 skill packages, Markdown
  fences and local links all pass.
- Documentation `--check`: all 183 English pages from the saved official
  index are present and every source-index/snapshot hash matches.
- Merge completeness: every installed GPUI Kit reference is present; full
  Coding and Design guide section outlines match the fetched source pages.
- `bash scripts/test_skill_tools.sh`: passes, including new Kit/alias/lockfile
  inspector checks, existing direct-GPUI inspection, documentation coverage,
  shell syntax checks, and five spring tests. The existing goal-state suite
  reports 19 tests with one skipped.
- Focused link checks: custom URI examples are accepted, missing local files
  are still rejected, and snapshot adaptation preserves code fences, anchors,
  external URLs, and attribution.
- `git diff --check`: passes.

## Documentation freshness

Context7 resolved `/longbridge/gpui-kit`, but its indexed bootstrap/overlay
examples lagged the current website. The current official installation,
getting-started, window, Root, and testing pages settled those differences.
A later lookup reached Context7's monthly quota; after the user refreshed
authentication, a retry succeeded and confirmed the same stale indexed
examples. The bundled reference uses the current official pages and retains
the rule to verify the selected release's actual source.

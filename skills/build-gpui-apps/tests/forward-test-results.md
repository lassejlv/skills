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

# GPUI Kit 0.7.0 refresh validation — 2026-10-01

Target: the working-tree update based on repository commit `44483ba`.
The September results above remain historical. The refresh uses the published
0.7.0 tag `0c830f4d257e69fdd17200650533ab4ca9a40cc0` for version/bootstrap
authority and retains the full 183-page website bundle.

Each scenario in [forward-tests.md](forward-tests.md) was given to a fresh
agent with no creator context or review rubric. Results below are read-only
workflow evidence; no consumer app was edited, built, launched, or published.
Agent tasks: `v070_search`, `v070_toolbar`, `v070_paper`, `v070_input`,
`v070_starter`, `v070_choice`, `v070_settings`, `v070_upstream`,
`v070_delivery`, and `v070_upgrade` (no model override).

| Scenario | Result | Evidence and limit |
| --- | --- | --- |
| 1. Accessible cancellable search | Pass | Verified the pinned testing/input/list source, retained tasks and generations, guarded stale success/error, used stable virtualized IDs and scoped actions, and separated native IME/accessibility checks from headless tests. |
| 2. Honest Apple-style toolbar | Pass | Inspected the pinned hello-world source, preserved its upstream stack, distinguished native materials from GPUI paint and window blur, and required a verified host/lifecycle bridge plus opaque/platform fallbacks. |
| 3. Paper unavailable | Pass | Paper MCP responded “Open a Paper file to use this tool.” The agent inspected the local fixture, required live frame/style/asset extraction, and did not infer geometry from the fixture's viewport. |
| 4. Unicode/IME editor | Pass | Verified the pinned input source; separated byte/UTF-16/grapheme/shaped coordinates and provisional composition. Identified a source-level marked-selection arithmetic concern as an inference, and proposed boundary, undo, native IME, and layout tests rather than copying the demonstration blindly. |
| 5. Production starter | Partial target verification; workflow passes | Verified starter commit, locked GPUI revision/toolchain, and the Kit tag. Preserved the unrelated README in the plan, kept framework adoption pending, and separated compile/runtime/install/update gates. No target directory was supplied, so its real inventory remains unverified. |
| 6. Recommend Kit and ask | Pass | Recommended Kit and asked the framework question; allowed only read-only inspection and independent planning before an answer. |
| 7. Selected Kit settings | Pass | Read actual Design/Coding guides, selected the verified 0.7.0 facade over stale snippets, retained InputState/subscriptions, controlled Switch through its owner, and used helper-owned Root plus production-view Kit UI tests. |
| 8. Explicit upstream choice | Pass | Inspected the pinned fixture, kept gpui/gpui_platform and upstream test-support, and planned actual focus/key/disabled-action tests without migration or execution claims. |
| 9. Delivery and capabilities | Pass | Located all requested local guides, separated Kit UI from installer ownership, and retained WebView/Shell/browser/mobile maturity and compatibility limits. In particular, the pinned mobile example's GPUI 0.3.4 does not establish compatibility with Kit's 0.3.7 snapshot. |
| 10. Established Kit upgrade | Pass | Followed release guide and tagged manifest/facade over stale installation/Context7 snippets; migrated automatic Root hosting, DateTime, active cell selection, Curve/nearest_index, and durable Accordion draft ownership. Located all three new component guides and required normal/reduced-motion UI checks. |

Nine scenarios pass; the starter scenario has a missing-target inspection
limit with a passing workflow. No skill gaps were demonstrated. A direct
DataTable link and explicit browser/mobile version boundaries were added to
the migration router after review. Runtime/app evidence remains proposed.

## Executed refresh checks

- Repository validator: 25 skills, 291 Markdown files, README catalog, fences,
  and local links pass.
- Documentation check: all 183 English indexed pages and saved hashes pass;
  nine original source hashes changed, all concerning example versions.
- Tool smoke tests pass: goal-state suite reports 19 tests, one skipped;
  all five Rust spring tests pass, along with inspector/coverage checks.
- `git diff --check` passes; the new migration reference has no trailing
  whitespace. The upstream Rust fixture and unrelated image output are preserved.

Context7 resolution and the focused migration query succeeded, but returned
older manual-overlay recipes. Tagged source and current Root documentation
settle the conflict. Refreshed website snippets also contain older dependency
versions; the entrypoint and migration guide explicitly choose the release
manifest over those examples.

# Forward-test results — 2026-11-14

Target: the new `build-rune-apps` skill at Rune `65f8eb43f710`. Each scenario ran
with a fresh agent given only the prompt; reports were reviewed separately
against [forward-tests.md](forward-tests.md).

| Scenario | Result | Evidence and limits |
| --- | --- | --- |
| Build: "Clear done" in a copy of the reference app (variant of 2) | Pass | Kept rune-kit without asking (established stack), ran the inspector and patch check, added state method, keyed kit button, scene, script and 3 `Runtime` tests; fmt, clippy, 9 tests passed. Rendered ~15 scenes in both themes and read them back, which led it to shrink the button. Mutation-checked its tests. Not launched in a window. |
| 3. Broken patch table | Pass | Diagnosed the missing table, printed the exact block with `--print-table`, and proved it with three `cargo check` runs. Found that at this rev the manifest fails resolution instead of silently building; `project-setup.md` was corrected. Real IME not exercised. |

Changes made from these runs: the patch-table consequence in
`references/project-setup.md`, and script key names and the macOS
keyboard-navigation caveat in `references/headless-validation.md`.
Scenarios 1 and 4–7 have not been run yet.

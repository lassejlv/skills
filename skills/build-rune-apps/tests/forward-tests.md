# Forward-test scenarios

Run these after substantial changes. Give only the prompt block to a fresh agent
with no creator context, then review the result against the signals
separately; don't leak the rubric into the prompt. Replace `<skill-path>` with
the skill folder and `<app>` with a real Rune app where one is needed.

## 1. New app: recommend rune-kit and ask

Prompt:

```text
Use $build-rune-apps at <skill-path>/SKILL.md. I want a small native notes app in
Rust with Rune: a sidebar of notes, an editor, and a search field. Start it in
an empty folder.
```

Review signals:

- recommends rune-kit and asks rune-kit versus core `rune` before writing
  stack-specific code; keeps planning while waiting;
- pins one `dev` rev (looked up, not invented) for every Rune crate and the
  patch table, and names the toolchain;
- starts from the reference app or the same manifest shape;
- plans scenes (empty, many, long text, search with no results) and headless
  renders in both themes.

## 2. Existing app keeps its stack

Prompt:

```text
Use $build-rune-apps at <skill-path>/SKILL.md. In <app>, add a "Clear history"
button to the settings page that asks for confirmation first. Don't commit.
```

Review signals:

- runs the inspector, notices core `rune` with the app's own palette, and does
  not ask about or introduce rune-kit;
- keeps the pinned rev and patch table untouched;
- models the confirmation as state (an enum or `Option`), keys new elements,
  names the destructive action in the copy;
- adds or updates a scene, renders it light and dark, reads the images back,
  and runs the app's tests.

## 3. Broken patch table

Prompt:

```text
Use $build-rune-apps at <skill-path>/SKILL.md. Text input with a Japanese IME is
broken in my Rune app on macOS. Here is the manifest: <paste a Cargo.toml whose
rune dependency is pinned but which has no [patch.crates-io] table>. What's
wrong?
```

Review signals:

- identifies the missing patch table (winit carries Rune's macOS input-method
  code) before suggesting code changes, and notices that at the audited rev
  that manifest doesn't resolve at all;
- gives the exact table for the pinned rev via `check_rune_patches.py
  --print-table` or Rune's root manifest, not from memory;
- says real IME behaviour needs a window test, not a headless one.

## 4. Scroll that never scrolls

Prompt:

```text
Use $build-rune-apps at <skill-path>/SKILL.md. Read-only: my Rune view is
col().h_full().child(header).child(col().grow(1.0).child(list.scroll(ScrollSpec
{ stick_bottom: false }))).child(footer). The list renders but never scrolls and
the footer is pushed off the window. Explain and fix it.
```

Review signals:

- names the flexbox minimum-content rule: `.min_h(0.0)` on the grown column,
  and a viewport that fills it (`.grow(1.0).min_h(0.0)` or equivalent) so the
  scroll is bounded;
- suggests confirming with `--tree` rects and a `--snap` of a "many" scene;
- doesn't propose virtualisation or a rewrite for a layout bug.

## 5. Paper frame to Rune

Prompt:

```text
Use $build-rune-apps at <skill-path>/SKILL.md. Implement the selected Paper frame
as a new view in <app>.
```

Review signals:

- tries the Paper MCP server; if unavailable, says so and doesn't invent the
  design;
- converts sRGB hex with `rune::color::hex`, maps letter-spacing, line height
  and shadows correctly, embeds fonts;
- compares a 2x `--snap` at the frame's size with Paper's screenshot and fixes
  geometry, then type, then colour;
- lists states the frame didn't show and how they were handled.

## 6. Performance review

Prompt:

```text
Use $build-rune-apps at <skill-path>/SKILL.md. Read-only: review <app> for
anything that makes scrolling or idle CPU worse. Rank findings.
```

Review signals:

- looks for `poll` returning true without visible change, `on_hover_change`
  state on rows, scroll-following layout handlers without `live_only`,
  `window_layout` reads, file I/O on the UI thread, unbounded caches, lists
  without `virtual_rows`;
- suggests `scripts/app-audit`, `RUNE_COMMIT_BUDGET_MS` and paired measurements;
- ranks by user impact and separates evidence from suspicion.

## 7. Upgrade the rev

Prompt:

```text
Use $build-rune-apps at <skill-path>/SKILL.md. Upgrade <app> to the newest Rune
dev commit. Don't commit.
```

Review signals:

- reads `CHANGELOG.md` entries between the revs before editing;
- moves every rev together and re-checks the patch table and toolchain;
- builds, tests, re-renders every scene in both themes and compares with renders
  from the old rev before calling it done;
- reports anything that changed visually.

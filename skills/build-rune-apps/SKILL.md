---
name: build-rune-apps
description: Build, scaffold, refactor, debug, review, and validate native GPU-rendered Rust apps with Rune (github.com/anomalyco/rune) for macOS, Windows, Linux, and the web. Recommends rune-kit components and asks before adopting them, pins one dev rev with Rune's matching [patch.crates-io] table, and checks every change headlessly by rendering PNGs, reading the element and accessibility tree, and driving scripted input. Bundles Rune's core, rune-kit, motion, effects, shortcuts, web, and Mac-app documentation split by section, plus app-model, layout, input, performance, platform delivery, Paper translation, testing, and examples guides, a compile-checked reference app, and project and patch-table checkers. Use for any Rune view, window, component, motion, state, packaging, or test work, including a Paper design rendered with Rune.
---

# Build Rune Apps

Build native apps whose every pixel Rune draws, with state the app owns, motion
the framework animates, and evidence from headless renders of the real view.
**Recommend rune-kit for standard controls, and ask before adopting it.**
rune-kit sits on top of core `rune`; it does not replace its views, layout or
renderer.

Rune is pre-release. Apps pin a commit of its `dev` branch, and its APIs move
between commits. The [bundled documentation](references/upstream/index.md) is a
snapshot of every Markdown guide in the repository at one rev, split by section.
Read only the sections a task needs.

## Choose the stack first

1. Inspect repository instructions, dirty state, the manifest, lockfile, pinned
   Rune rev, patch table, features, toolchain, entry point, scenes, tests and
   theme. `scripts/inspect_rune_project.sh /path/to/app` prints a read-only
   inventory; `scripts/check_rune_patches.py /path/to/app/Cargo.toml` checks the
   patch table against Rune's at the pinned rev.
2. Honor a choice already made in this conversation or the project. An app that
   depends on `rune-kit` has chosen it; an app with its own hand-built controls
   and palette (often from a Paper design) has chosen core `rune`. Do not ask
   again, and do not migrate either way unasked.
3. For a new app with no established choice, or before adding rune-kit to an
   existing app, ask before writing the stack-specific code:

   > I recommend rune-kit for the standard controls: buttons, fields, checkboxes,
   > selects, menus, popovers, toasts, a sidebar shell, trees and tables, with
   > keyboard, focus and accessibility built in and a theme from three colours.
   > Use rune-kit (recommended), or core `rune` with hand-built controls?

   For an existing app, name what adoption touches: dependencies, theme tokens,
   the overlay layer at the root, keys inside components, and tests. Wait for an
   answer; silence is not agreement. Keep inspecting and planning meanwhile. A
   scoped fix in an existing app needs no stack decision.
4. Pin one rev. A new app takes the newest `dev` commit (record its SHA and
   date); an existing app keeps its rev unless the task is an upgrade. Every
   Rune crate and every `[patch.crates-io]` entry names the same rev. See
   [project setup](references/project-setup.md).

The choice applies to creating or adopting a stack, not to each ordinary edit.

## Core contract

- **The pinned rev is the API authority.** Read it in Cargo's checkout
  (`~/.cargo/git/checkouts/rune-*/<short rev>/`) or the repository at that rev.
  Never invent methods from GPUI, SwiftUI, React, CSS or another rev's docs;
  grep the source for constructors, builder methods, features and re-exports.
- **The view is a function of state.** `fn view(&S, &mut Cx<S>) -> El` builds
  targets and does nothing else: no I/O, no blocking, no clocks it doesn't get
  from `Cx`, no `El` or handler stored in state. Handlers mutate state; Rune
  re-runs the view, diffs it and animates toward the new targets.
- **Keys are identity.** Key everything that persists, moves, animates, is
  scrolled to or is tested, from domain ids (`task-{id}`), never from indices
  that shift. Keys are one namespace and rune-kit keys its own parts, so reach
  app elements inside components by path (`task-3/check`).
- **Motion is declarative.** Give targets and springs (`.motion(..)`,
  transitions, `tok::motion`); never step animation from timers. Land state that
  shouldn't animate with `tx.instant()`. Nothing animates on the first frame,
  and Reduce Motion is honoured by the runtime; keep it that way.
- **Modes are state machines; slow work is off the UI thread.** Use
  `rune::machine` for anything with phases, `Tx::wake_at`/`wake_after` for
  timers, `Latest`, `rune::task` or `AppHandle::update` for background work.
  `poll` returns true only when visible state changed; an idle window draws
  nothing.
- **Accessible by construction.** Roles, labels, checked/expanded/disabled
  states, focus order and visible focus rings; a label on every icon-only
  control. Verify in the `--tree` accessibility output, not by assumption.
- **Check your work headlessly.** Every visible change gets `--snap` renders in
  light and dark at scale 2 for the scenes it affects, read back as images;
  `--tree` for keys, rects and accessibility; `--script` for interaction; and a
  `Runtime` test for behaviour. A compile is not evidence that a view works.
- Preserve existing shortcuts, state, persistence, window behaviour and
  unrelated work. A visual request does not authorize an architecture rewrite.

## Route the task

| Task | Read first | Also read when relevant |
| --- | --- | --- |
| New app, dependency, rev pin, features, upgrade a rev | [Project setup](references/project-setup.md), [reference app](assets/reference-app/README.md) | [Depending on Rune](references/upstream/rune/depending-on-rune.md), [Linux](references/upstream/rune/linux.md), [overview](references/upstream/overview.md) |
| State, view, handlers, `poll`, app lifetime, background work, modes | [App model](references/app-model.md) | [App lifetime](references/upstream/rune/app-lifetime.md), [state machines](references/upstream/rune/state-machines.md), [Latest](references/upstream/rune/requests-off-the-main-thread.md), [Rune's agent rules](references/upstream/agents.md) |
| Layout, styling, tokens, colour, themes, fonts, icons, images, scrolling, lists | [Layout and style](references/layout-style.md) | [What exists](references/upstream/rune/what-exists.md), [rich text and scrolling](references/upstream/rune/rich-text-scrolling-and-app-hooks.md), [high-frequency values](references/upstream/rune/high-frequency-values.md) |
| Components, kit theme, app shell, sidebar, tree, table, markdown | [rune-kit](references/kit.md) | [Use](references/upstream/kit/use.md), [components](references/upstream/kit/components.md), [app shell](references/upstream/kit/app-shell.md), [tree and table](references/upstream/kit/tree-and-table.md), [markdown](references/upstream/kit/markdown.md) |
| Springs, presence, shared-element motion, live values, choreography | [Motion](references/motion.md) | [rune-motion](references/upstream/rune-motion.md), [shared-element motion](references/upstream/rune/shared-element-motion.md), [finite choreography](references/upstream/rune/finite-choreography.md), [motion audit](references/upstream/scripts-motion-audit.md) |
| Focus, keys, shortcuts, text fields, IME, clipboard, menus, dialogs, drag and drop | [Input and windows](references/input-windows.md) | [Text fields](references/upstream/rune/text-fields.md), [shortcuts and menus](references/upstream/rune-shortcuts.md), [menus](references/upstream/rune/pop-up-and-context-menus.md), [file dialogs](references/upstream/rune/file-dialogs.md) |
| Windows, overlays, panels, tray, chrome, materials, effects, video | [Input and windows](references/input-windows.md) | [Multiple windows](references/upstream/rune/multiple-windows-and-overlays.md), [window chrome](references/upstream/rune/window-chrome-and-shell-controls.md), [system materials](references/upstream/rune/system-materials.md), [rune-fx](references/upstream/rune-fx.md), [rune-light](references/upstream/rune-light.md) |
| Headless renders, scripts, trees, unit and story tests, visual QA | [Headless validation](references/headless-validation.md) | [Agent tooling](references/upstream/rune/agent-tooling.md), [playground](references/upstream/rune/playground.md), [testing stories](references/upstream/rune/testing-stories.md), [accessibility](references/upstream/rune/accessibility.md) |
| Launch time, idle cost, scrolling, long lists, commits, memory | [Performance](references/performance.md) | [Launching fast](references/upstream/rune/launching-fast.md), [smooth scrolling](references/upstream/rune/smooth-scrolling.md), [canvas handlers](references/upstream/rune/canvas-handlers.md), [rune-perf](references/upstream/rune-perf.md) |
| Bundle, sign, URL schemes, single instance, Linux packages, web build | [Platform delivery](references/platform-delivery.md) | [Relaunching a Mac app](references/upstream/rune/relaunching-a-mac-app.md), [mac-app installer](references/upstream/scripts-mac-app.md), [rune-mac](references/upstream/rune-mac.md), [web](references/upstream/web.md) |
| Live Rust editing while developing | [Project setup](references/project-setup.md#development-loop) | [Live Rust editing](references/upstream/rune/live-rust-editing.md), [an external app crate](references/upstream/rune/an-external-app-crate.md), [restart boundaries](references/upstream/rune/compatible-edits-and-restart-boundaries.md) |
| A Paper design rendered in Rune | [Paper to Rune](references/paper-to-rune.md) | [Layout and style](references/layout-style.md), [headless validation](references/headless-validation.md) |
| Find a working example of a capability | [Examples and demo map](references/examples-map.md) | [Bundled index](references/upstream/index.md) |

## Application path

After the stack is settled:

1. Start from [the reference app](assets/reference-app/README.md): copy it, rename
   the package, set the rev everywhere, and run
   `scripts/check_rune_patches.py --print-table <rev>` for the patch table.
   Match the toolchain to Rune's `rust-toolchain.toml` at that rev or newer.
2. Shape state first: domain data, ids, selection, drafts (`TextEdit`), open
   overlays, modes as enums. Give `AppSpec` a `scenes` entry for every state
   worth seeing: empty, typical, many, long text, error, open overlay.
3. Write the view as small functions of state returning `El`. Use tokens (`tok`
   or the `Kit`), keys from ids, `row`/`col` layout with bounded scroll
   viewports, and rune-kit builders ending in `.build(&k)` when chosen.
4. Attach handlers where the element is (`on_press`, kit `on_toggle`, `on_edit`,
   `on_submit`). Route window shortcuts through `AppSpec::on_key`, matched with
   `Chord` (or `Key::Command(c)` for plain ⌘-letter keys), not raw modifier
   flags, which differ by platform.
5. Put slow or external work behind `setup`'s `Waker`, `App::on_ready`,
   `AppHandle::update`, `Latest` or `rune::task`; fence stale answers.
6. Render headless, read the PNGs, inspect the tree, script the interaction,
   then write `Runtime` tests for the behaviour. Fix what the images show before
   reporting.
7. Launch the real window for what headless can't prove: native text input and
   IME, menus, file dialogs, drag and drop, focus across windows, materials,
   display scaling, and platform chrome.

## Validate and report

Adapt to the owning crate:

```sh
cargo fmt --check
cargo clippy --locked --all-targets -- -D warnings
cargo test --locked
cargo build --locked
APP=target/debug/<bin>
$APP --list-scenes
$APP --snap out/<scene>-light.png --scene <scene> --theme light --scale 2
$APP --snap out/<scene>-dark.png --scene <scene> --theme dark --scale 2
$APP --tree out/tree.json
$APP --script scripts/<flow>.json --snap out/<flow>.png --at mark:end --scale 2
```

Release builds take headless flags only with the `tooling` feature. Run
`scripts/app-audit <repo>` from a Rune checkout for slow patterns, and the
motion gate when motion changes. Then report the pinned rev, stack choice,
changed boundaries, the checks actually run, which renders were read back and
what they showed, what was exercised in a real window, and what remains
unverified on other platforms. Rank review findings by user impact; do not
present style preferences as defects.

## Maintain this skill

The [source ledger](references/sources.md) records the audited rev and what was
verified. `assets/reference-app` is compile-, test- and render-checked at that
rev; `scripts/validate_reference_app.sh` repeats those checks.

```sh
python3 scripts/sync_rune_docs.py --rev dev   # refresh the snapshot at the newest dev commit
python3 scripts/sync_rune_docs.py --check     # offline coverage and hash check
scripts/validate_reference_app.sh             # build, test, lint and render the reference app
```

When the rev moves, refresh the snapshot and the reference app together, read
`CHANGELOG.md`'s entries since the last audited rev, and correct every guide
that names a changed API. After substantial changes, run
[forward-tests.md](tests/forward-tests.md) with fresh agents and review the
results separately.

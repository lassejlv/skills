# Forward-test scenarios

Run these after substantial changes to the umbrella skill. Give only the
prompt block to a fresh agent with no creator context. Review the result
against the signals separately; do not leak the rubric into the prompt.

## 1. Accessible cancellable search

Prompt:

```text
Use $build-gpui-apps at <skill-path>/SKILL.md. Read-only: inspect the pinned
GPUI testing example and propose a focused implementation plan for a
cancellable, accessible GPUI search panel with keyboard actions and a
virtualized result list. Do not edit files. Report the exact reference layers
you used, concrete state/action/task ownership, tests, and any pinned-version
uncertainties.
```

Review signals:

- treats the target checkout as API authority;
- routes through architecture, async/performance, accessibility, and testing;
- gives the view/model one clear source of truth;
- holds or replaces the search task and rejects stale generations;
- uses typed actions and scoped key contexts;
- virtualizes results with stable semantic IDs;
- covers focus, announcements, loading/empty/error, cancellation, and a real
  launch path;
- distinguishes compiler/test evidence from runtime proof.

## 2. Honest Apple-style toolbar

Prompt:

```text
Use $build-gpui-apps at <skill-path>/SKILL.md. Read-only: inspect a pinned GPUI
hello-world example and propose how to add an Apple-polished floating toolbar
on macOS while preserving honest Linux and Windows behavior. Do not edit
files. State the material capability tier, fallbacks, architecture,
interactions, accessibility, and validation evidence you would require.
```

Review signals:

- inspects the target's real startup, theme, and platform policy;
- names native Liquid Glass only behind an actual guarded AppKit capability;
- does not call translucent GPUI paint native backdrop blur;
- keeps content mostly solid and glass limited to controls/navigation;
- provides opaque, high-contrast, reduced-transparency, inactive-window, and
  cross-platform fallbacks;
- covers focus, keyboard, pointer, reduced motion, scale, resize, cleanup, and
  screenshot evidence;
- avoids speculative native bridging when the target does not need it.

## 3. Paper connection unavailable

Prompt:

```text
Use $build-gpui-apps at <skill-path>/SKILL.md. I have a selected Paper.design
frame and want it translated into a named GPUI fixture. Read-only: inspect what
is locally available and give the next concrete steps; do not edit files. Be
explicit about what evidence you can and cannot obtain and what must happen
before implementation.
```

Review signals:

- inspects the GPUI target without modifying it;
- requires a live Paper MCP connection and exact selected frame/node;
- does not infer geometry, styles, assets, or fonts from memory;
- explains the minimal connection/selection recovery path;
- lists screenshot, hierarchy, computed-style, token, font, and asset evidence
  to capture after connection;
- stops before implementation and keeps the unavailable path explicit.

## 4. Unicode and IME-safe editor review

Prompt:

```text
Use $build-gpui-apps at <skill-path>/SKILL.md. Read-only: inspect the pinned
GPUI text-input example and review a proposed custom single-line editor that
stores selection offsets as usize, replaces text on every marked-text update,
and hit-tests with average glyph width. Explain the production design and test
plan; do not edit files.
```

Review signals:

- identifies the ambiguous offset unit as unsafe;
- separates Rust UTF-8 bytes, platform UTF-16 code units, grapheme boundaries,
  and shaped visual positions;
- treats marked text as provisional composition;
- covers the full pinned `EntityInputHandler` contract;
- derives candidate bounds and hit tests from current shaped layout;
- centralizes edit transactions, selection, undo, notification, and revision
  checks;
- includes emoji, combining marks, bidirectional text, real IME, scroll/resize,
  clipboard, focus, accessibility, and stale-layout tests;
- recommends an existing maintained editor first when appropriate.

## 5. Production starter from the example repository

Prompt:

```text
Use $build-gpui-apps at <skill-path>/SKILL.md. Set up a production-ready GPUI
starter for a new desktop product named Northstar using
https://github.com/lassejlv/gpui-starter as the example. The target directory
already exists and contains an unrelated README. Work read-only: inspect the
source/example and return an implementation plan, proposed project tree,
identity ledger, and exact acceptance gates. Do not edit, clone over, delete,
or publish anything.
```

Review signals:

- protects the existing non-empty target and does not delete or overwrite it;
- inspects and records the current example commit, lockfile GPUI revision, and
  matching toolchain rather than trusting floating `main`;
- asks for or marks provisional the owned reverse-DNS app ID, publisher,
  platforms, minimum OS versions, distribution, data, and update owner;
- treats `gpui-starter` as a minimal two-crate baseline, not a production-ready
  artifact by itself;
- preserves the `desktop`/`ui` split and adds a headless crate only for proven
  domain/service ownership;
- covers full identity rename, observable startup, configuration/migrations,
  secrets, diagnostics, accessibility, lifecycle-owned async work, and one
  real vertical slice without adding irrelevant subsystems;
- pins the Rust toolchain and GPUI Git revision, commits the lockfile, and uses
  `--locked` CI with immutable action pins and least privilege;
- distinguishes compile/test, real launch, installed artifact, signing, and
  upgrade evidence per claimed platform;
- identifies whole-window blur as a capability/tradeoff, includes an opaque
  fallback, and does not call it per-control Liquid Glass;
- gives macOS, Windows, and Linux packaging only for platforms actually
  selected, including signing/identity/install/upgrade checks;
- reports unresolved production facts as release blockers rather than silently
  inventing them.

## Regression policy

Re-run the affected scenario when its routed reference or executable fixture
changes. Re-run all scenarios when `SKILL.md`, dependency/version policy, the
production-starter path, or the Paper path changes. Record:

- date and target revision;
- agent/model if the environment exposes it;
- pass, partial, or fail for each review signal;
- skill gaps discovered;
- exact follow-up edits and validation.

A polished answer is not automatically a pass. It must route correctly, remain
source-grounded, preserve capability boundaries, and produce an executable
verification plan.

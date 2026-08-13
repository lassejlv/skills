---
name: build-gpui-apps
description: Build, scaffold, refactor, debug, review, and visually validate production Rust desktop interfaces with GPUI. Use for setting up a production-ready GPUI starter app; new GPUI apps or components; Entity, Context, action, async, and lifecycle architecture; Apple-style macOS UI, Liquid Glass or translucent materials, motion, gestures, focus, keyboard, accessibility, text input, IME, clipboard, drag and drop, menus, multi-window behavior, and restoration; packaging, CI, performance, and testing work; or translating selected Paper.design frames into maintainable GPUI code with screenshot comparison. Covers published GPUI and pinned Zed revisions, macOS/Linux/Windows boundaries, narrow AppKit interop, and stability audits.
---

# Build GPUI Apps

Build native GPUI software that is correct before it is glossy, genuinely
platform-aware before it is Apple-styled, and verified in the running app
before it is called complete.

This is a routed umbrella skill. Read only the reference layers needed for the
task, but always follow the core contract and workflow below.

## Core contract

1. Inspect the target checkout before changing it: branch, dirty state,
   manifests, lockfile, pinned GPUI source, app entrypoint, root view, theme,
   components, assets, tests, and platform code.
2. Treat the target checkout as the API authority. GPUI is pre-1.0; examples
   from `gpui.rs`, Zed main, crates.io, or this skill can differ from the pinned
   revision.
3. Preserve working state ownership, commands, shortcuts, persistence, window
   behavior, and platform integration. A visual request is not permission to
   replace the app architecture.
4. Keep render work deterministic and cheap. Move blocking I/O and CPU-heavy
   work off the application thread, then update a live entity through the
   appropriate async context.
5. Give interactive elements stable IDs, semantic roles, keyboard access,
   visible focus, disabled behavior, and immediate input feedback.
6. Use glass as a functional navigation or control layer, not as decoration on
   every surface. Never describe a flat translucent rectangle as native Liquid
   Glass.
7. Respect reduced motion, reduced transparency, increased contrast, and
   differentiate-without-color. Provide an opaque fallback.
8. Validate compilation, behavior, launch, and visuals. `cargo check` alone
   does not prove focus, fonts, window chrome, scale factor, clipping, motion,
   or material behavior.
9. Do not rasterize text, controls, panels, or whole screens to fake fidelity.
10. Preserve unrelated changes and report every unverified platform or runtime
    path plainly.
11. Treat text input, clipboard, menus, drag/drop, and window lifecycle as OS
    contracts. Preserve Unicode range units, composition, focus, command state,
    and stable ownership.
12. For a new application, establish product identity, a pinned toolchain and
    GPUI revision, observable startup, storage policy, CI, and packaging gates
    before calling the starter production-ready.

## Route the task

| Task | Read first | Also read when relevant |
|---|---|---|
| Set up or harden a production-ready starter app | [production-starter.md](references/production-starter.md) | [project-versioning.md](references/project-versioning.md), [testing-qa.md](references/testing-qa.md) |
| Orient a GPUI checkout or choose dependency features | [project-versioning.md](references/project-versioning.md) | [testing-qa.md](references/testing-qa.md) |
| Design state, events, actions, or component boundaries | [architecture-state.md](references/architecture-state.md) | [async-performance.md](references/async-performance.md) |
| Build views, controls, layout, themes, overlays, or lists | [components-layout.md](references/components-layout.md) | [worked-patterns.md](references/worked-patterns.md) |
| Add Apple-like glass, translucency, depth, or macOS material | [apple-glass.md](references/apple-glass.md) | [accessibility-platform.md](references/accessibility-platform.md) |
| Add animation, drag, momentum, springs, or gesture behavior | [motion-input.md](references/motion-input.md) | [accessibility-platform.md](references/accessibility-platform.md) |
| Add focus, keyboard, screen-reader, typography, or platform behavior | [accessibility-platform.md](references/accessibility-platform.md) | [components-layout.md](references/components-layout.md) |
| Add editable text, IME, clipboard, drag/drop, menus, multi-window behavior, or restoration | [input-windows.md](references/input-windows.md) | [accessibility-platform.md](references/accessibility-platform.md), [testing-qa.md](references/testing-qa.md) |
| Add async loading, background work, virtualization, or performance fixes | [async-performance.md](references/async-performance.md) | [architecture-state.md](references/architecture-state.md) |
| Add or review tests, launch checks, screenshots, or release gates | [testing-qa.md](references/testing-qa.md) | [visual-validation.md](references/visual-validation.md) |
| Translate a Paper.design selection into GPUI | [paper-to-gpui.md](references/paper-to-gpui.md) | [paper-mcp.md](references/paper-mcp.md), [visual-validation.md](references/visual-validation.md) |
| Need complete, copyable patterns | [worked-patterns.md](references/worked-patterns.md) | The domain reference for the pattern |
| Verify why a rule exists or refresh time-sensitive claims | [sources.md](references/sources.md) | Current target source and official docs |

## Workflow

### 1. Establish scope and current truth

Run the read-only inspector:

```sh
scripts/inspect_gpui_project.sh /path/to/project
```

Then inspect directly:

- Read repository instructions and determine whether the request authorizes
  edits or only diagnosis/review.
- Confirm the owning crate and the smallest surface that can satisfy the task.
- Record the GPUI declaration and exact lockfile version or Git revision.
- Find a similar component that compiles in this checkout.
- Identify current theme access, asset loading, focus conventions, actions,
  overlay system, async patterns, and test support.
- Note the platform and minimum OS versions. Do not silently make a
  cross-platform component macOS-only.

Read [project-versioning.md](references/project-versioning.md) before creating a
new app, changing startup, changing GPUI versions, or copying an upstream API.

For a greenfield or starter-hardening request, read
[production-starter.md](references/production-starter.md) before choosing the
crate layout. It uses
[lassejlv/gpui-starter](https://github.com/lassejlv/gpui-starter) as a concrete
minimal example, then adds the missing production contracts without pretending
every app needs every subsystem.

### 2. Write the behavioral contract

Before implementation, state:

- source of truth for state;
- user actions and resulting events/state transitions;
- loading, empty, disabled, error, and cancellation states;
- focus owner, tab order, shortcuts, pointer and touch behavior;
- text index units, composition, clipboard, menu, and window ownership when in
  scope;
- resize and scrolling behavior;
- material tier and fallbacks;
- reduced-motion, opaque, and high-contrast behavior;
- target platforms and what must be verified on each.

For a visual translation, add the exact source frame, viewport, theme, fonts,
assets, and screenshot evidence.

### 3. Choose the smallest correct GPUI register

Use:

- an ordinary element tree for normal layout and styling;
- `RenderOnce` for stateless, value-like reusable components;
- an `Entity<T>` implementing `Render` for independently changing state;
- a project model entity for shared domain state;
- `canvas` or a custom `Element` only when ordinary layout or painting cannot
  meet the requirement;
- a narrow platform bridge only for behavior GPUI cannot supply.

Do not create an entity for every wrapper. Do not keep meaningful state in
ephemeral render-local values. Read
[architecture-state.md](references/architecture-state.md) and
[components-layout.md](references/components-layout.md).

### 4. Implement one vertical slice

Build one end-to-end path before broad extraction:

1. Domain state or model operation
2. Typed action or event
3. Entity update
4. `cx.notify()` or emitted event
5. Rendered default state
6. Pointer, keyboard, focus, and accessibility behavior
7. Error/cancellation state
8. Targeted test

Only extract a reusable component or token after a repeated semantic or visual
pattern is proven. Keep public APIs narrow and predictable.

### 5. Apply Apple design without lying about capability

Select the material tier in this order:

1. Existing system or project component
2. Native macOS 26+ `NSGlassEffectView` behind an availability boundary
3. `NSVisualEffectView` or GPUI whole-window blur when that is the actual need
4. Cross-platform GPUI approximation using semantic tint, border, highlight,
   shadow, and opacity
5. Opaque/high-contrast fallback

Do not stack glass on glass. Keep content surfaces mostly solid. Use concentric
geometry, restrained tint, adaptive light/dark tokens, and clear elevation.
Read [apple-glass.md](references/apple-glass.md).

### 6. Make interaction physical and interruptible

- Respond on press/down, then commit on release/click.
- Keep direct manipulation 1:1 and preserve the grab offset.
- Carry velocity from gesture to settling motion.
- Retarget from current presentation state and velocity.
- Keep input active while motion runs.
- Use symmetric enter/exit paths and anchor presentations to their source.
- Prefer `AnimationExt::with_animation` for decorative finite motion when the
  pinned version supports it; it integrates with GPUI reduced-motion state.
- Use explicit state plus frame requests for interactive springs. The bundled
  [spring.rs](assets/spring.rs) is a pure-Rust starting point, not a substitute
  for target-version integration.

Read [motion-input.md](references/motion-input.md) before implementing custom
animation or gestures.

For editable text, native command surfaces, drag/drop, or more than one window,
read [input-windows.md](references/input-windows.md). Prefer a maintained editor
component over implementing the platform input contract from scratch.

### 7. Protect lifecycle and performance

- Hold a returned `Task` when dropping it should cancel work; detach only when
  app-lifetime completion is deliberate and errors are observed.
- Hold a `Subscription` when the observer has an owner; detach only when entity
  lifetime semantics are correct.
- Capture `WeakEntity` in long-running work.
- Use `background_spawn` for blocking/CPU work and `cx.spawn` or
  `cx.spawn_in` for application-thread orchestration.
- Virtualize large collections with `list` or `uniform_list`.
- Avoid filesystem, network, sleep, parsing, and unbounded allocation in
  `render`.
- Request animation frames only while something is changing.

Read [async-performance.md](references/async-performance.md).

### 8. Validate in widening rings

Run repository-native checks first, then adapt this baseline:

```sh
cargo fmt --check
cargo check -p <owning-crate>
cargo test -p <owning-crate>
cargo clippy -p <owning-crate> --all-targets -- -D warnings
```

Also:

- launch the real app;
- exercise mouse, keyboard, focus, resize, scroll, and relevant touch paths;
- verify light, dark, inactive-window, reduced-motion, opaque, and
  high-contrast states where supported;
- capture matching screenshots for visual work;
- check at 1x and a high-DPI scale;
- inspect logs and task/error states;
- run at least one targeted `#[gpui::test]` when behavior uses GPUI input,
  focus, actions, timing, or windows.

Read [testing-qa.md](references/testing-qa.md) and
[visual-validation.md](references/visual-validation.md).

This skill includes a compile-checked, exact-revision fixture at
`assets/reference-app`. It demonstrates startup, actions, entity events,
owned async work, accessibility, menus, multiple windows, virtualization,
preference-aware material fallbacks, and spring orchestration. It is a pattern
fixture, not a production component framework. Validate it with:

```sh
scripts/validate_reference_app.sh
```

## Production starter path

For “create a GPUI app,” “set up a starter,” or “make this starter
production-ready”:

1. Gather the product name, package/binary slug, owned application ID,
   supported platforms, minimum OS versions, distribution route, durable data,
   and update owner.
2. Inspect the target and the exact starter/example commit. Never copy over an
   existing checkout or delete its Git history without authorization.
3. Keep the minimal `desktop`/`ui` split until domain code proves a separate
   headless crate.
4. Pin the Rust toolchain and GPUI Git revision, commit `Cargo.lock`, and make
   the first clean CI baseline reproducible.
5. Rename identity across crates, binary, action namespace, app ID, menus,
   storage, icons, packaging, and update metadata.
6. Add observable startup, configuration/migrations, secret storage,
   lifecycle-owned async work, accessible controls, diagnostics, and recovery
   only where the product requires them.
7. Replace the demo with one real vertical slice and test it from domain state
   through action, GPUI update, persistence/error state, restart, and release
   launch.
8. Build, sign, install, upgrade, and exercise real artifacts on every claimed
   platform. Report cross-compilation separately.

Do not call a raw release binary, a green `cargo check`, or the unmodified
minimal example production-ready. Use the complete acceptance matrix in
[production-starter.md](references/production-starter.md).

## Paper.design path

For any Paper-to-GPUI request:

1. Require a live Paper MCP connection and one exact selected frame or node ID.
2. Verify the open file with `get_basic_info` and intent with `get_selection`.
3. Capture a 2x screenshot, hierarchy, JSX as structural evidence, computed
   styles, fonts, tokens, and actual exportable assets.
4. Preserve the GPUI app architecture and translate layout semantics, not DOM
   wrapper count.
5. Implement geometry, typography, paint, assets, and interactions in that
   order.
6. Compare Paper and native screenshots at matching logical bounds.

If Paper is unavailable, stop the design extraction path and explain how to
connect it. Do not recreate the design from memory. Read
[paper-to-gpui.md](references/paper-to-gpui.md) and
[paper-mcp.md](references/paper-mcp.md).

## Review standard

Rank findings by user impact and confidence. Require evidence for claims about:

- stale or dropped tasks/subscriptions;
- missed `cx.notify()` calls;
- unstable or duplicate element IDs;
- focus traps or pointer-only controls;
- blocking application-thread work;
- unbounded render allocation;
- incorrect fixed sizing or clipping;
- unsupported blur/material claims;
- missing accessibility role, label, state, or action;
- animation that ignores reduced motion;
- platform API use without availability guards;
- green compilation presented as visual or runtime proof.

Do not turn style preferences into correctness findings.

## Completion report

Report:

- GPUI version/revision and target platforms;
- files and architectural boundaries changed;
- material tier and fallback behavior;
- interaction, focus, accessibility, async, and performance behavior;
- text/IME, command, window lifecycle, and restoration behavior when relevant;
- tests, builds, launch, and visual comparisons actually performed;
- remaining deltas, unverified platforms, and version-sensitive assumptions.

For the research snapshot behind this skill, read
[sources.md](references/sources.md). Refresh upstream APIs when the target
revision differs or the snapshot is no longer current.

After substantial suite changes, run the realistic prompts and reviewer-only
rubrics in [forward-tests.md](tests/forward-tests.md) with fresh agents. Fix
routing or instruction gaps before publishing.

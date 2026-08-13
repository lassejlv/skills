# Production-ready GPUI starter sub-skill

Use this routed sub-skill to create a new GPUI desktop application or turn a
minimal example into a supportable production baseline. “Production-ready”
means the project can be reproduced, diagnosed, tested, packaged, upgraded,
and operated safely. It does not mean adding every possible subsystem before
the product needs it.

Use [gpui-starter](https://github.com/lassejlv/gpui-starter) as a concrete
minimal example. Inspect its current branch before using it; the snapshot below
is evidence, not a promise that `main` never changes.

## Contents

- [Define the production contract](#define-the-production-contract)
- [Choose the starting point](#choose-the-starting-point)
- [Understand the gpui-starter example](#understand-the-gpui-starter-example)
- [Adopt the example safely](#adopt-the-example-safely)
- [Make builds reproducible](#make-builds-reproducible)
- [Rename the product completely](#rename-the-product-completely)
- [Keep workspace boundaries honest](#keep-workspace-boundaries-honest)
- [Structure startup as observable phases](#structure-startup-as-observable-phases)
- [Set window and platform policy](#set-window-and-platform-policy)
- [Add configuration, persistence, and secrets](#add-configuration-persistence-and-secrets)
- [Add services and asynchronous state](#add-services-and-asynchronous-state)
- [Establish the accessible UI baseline](#establish-the-accessible-ui-baseline)
- [Add diagnostics and supportability](#add-diagnostics-and-supportability)
- [Build a useful testing pyramid](#build-a-useful-testing-pyramid)
- [Add continuous integration](#add-continuous-integration)
- [Package and sign each platform](#package-and-sign-each-platform)
- [Plan updates, migrations, and recovery](#plan-updates-migrations-and-recovery)
- [Protect security and privacy](#protect-security-and-privacy)
- [Build one production vertical slice](#build-one-production-vertical-slice)
- [Run the acceptance matrix](#run-the-acceptance-matrix)
- [Reject production-starter anti-patterns](#reject-production-starter-anti-patterns)
- [Completion checklist](#completion-checklist)

## Define the production contract

Before cloning or generating files, record the decisions that affect code,
identity, persistence, packaging, and CI:

| Fact | Required decision |
|---|---|
| Product name | Human-facing name used by windows, menus, installers, and About |
| Rust/package slug | Lowercase crate/workspace prefix and binary name |
| Application ID | Stable reverse-DNS identifier owned by the publisher |
| Publisher | Signing/notarization identity and support owner |
| Platforms | Exact macOS, Windows, Linux targets; omit unsupported claims |
| Minimum OS | Oldest runtime actually supported and tested |
| Distribution | Website, store, Homebrew, winget, AppImage/deb/rpm, or internal |
| Data | Config, durable documents, cache, logs, credentials, and retention |
| Network | Endpoints, offline behavior, timeouts, proxy/TLS policy |
| Updates | Manual, store-managed, or signed in-app update path |
| Recovery | Crash recovery, corrupt-state fallback, backup/migration policy |

Do not block a local scaffold on every commercial decision. Use clearly named
provisional values when necessary, but make unresolved identity, signing,
storage, and distribution facts explicit release blockers. Never ship
`com.gpui-starter.app` or another placeholder application ID.

Define “done” in five dimensions:

1. **Reproducible:** pinned toolchain/dependencies, committed lockfile, clean CI.
2. **Correct:** owned state, cancellation, errors, persistence, migrations.
3. **Usable:** keyboard, focus, accessibility, resize, appearance, platform
   conventions.
4. **Supportable:** structured diagnostics, version/build information, crash
   visibility, safe recovery.
5. **Deliverable:** platform artifacts, signing, install/uninstall, update and
   rollback story.

Only add a subsystem when the product contract calls for it. A local utility
without networking does not need an HTTP service layer. An app without durable
state does not need a speculative database crate.

## Choose the starting point

Select one path:

| Situation | Path |
|---|---|
| Empty target directory | Start from the current `gpui-starter` or the smallest example at the chosen GPUI revision |
| Existing GPUI app | Harden in place; do not replace working architecture with the example |
| Existing non-GPUI Rust domain crate | Keep it headless and add desktop/UI crates around it |
| Platform-specific native app | Decide whether GPUI replaces or embeds the native surface before scaffolding |
| Unclear product/platform scope | Build a two-crate baseline, mark release facts unresolved, avoid packaging claims |

Inspect first:

```sh
scripts/inspect_gpui_project.sh /path/to/project
```

For a new app, inspect the source example and its locked dependency before
copying it. For an existing app, preserve its branch, dirty files, lockfile,
actions, state ownership, and packaging. Never bulk-copy a starter over an
existing checkout.

## Understand the gpui-starter example

Snapshot inspected on 2026-08-13:

```text
Repository: https://github.com/lassejlv/gpui-starter
Commit:     9781c9295178f6b357cba167fca77df9e070d713
GPUI lock:  101ca00a1352ed71ef398f21b47836565d1998e3
Toolchain used by that Zed revision: Rust 1.95.0
```

The example has a useful minimal shape:

```text
crates/
  desktop/       # process startup, menus, keybindings, window options, icon
  ui/            # RootView, reusable Button, semantic theme values
Cargo.toml       # two-member workspace; desktop is the default member
Cargo.lock       # exact dependency resolution
justfile         # dev, run, build, and check shortcuts
AGENTS.md        # repository workflow and ownership guidance
```

Strengths worth preserving:

- native startup is separate from reusable UI;
- one root entity owns the demo state;
- components use stable IDs and `RenderOnce` where appropriate;
- desktop owns menu, quit bindings, minimum/default window size, titlebar, and
  application ID;
- shared theme values keep paint decisions out of call sites;
- a committed lockfile resolves the Git dependency to an exact Zed commit;
- macOS and non-macOS quit shortcuts are both registered.

It is deliberately a basic starter, not a production claim. At the inspected
commit it has no repository CI, tests contain zero cases, no checked-in Rust
toolchain file, no packaging/signing workflow, no persistence or migrations,
and no structured application diagnostics. The manifest names the Zed Git URL
without `rev`, even though `Cargo.lock` currently resolves an exact commit.
It also uses whole-window blur and placeholder identity.

Observed baseline at that snapshot:

- PASS `cargo +1.95.0 check --workspace --locked --all-targets` on macOS;
- PASS `cargo +1.95.0 test --workspace --locked` with zero tests;
- PASS strict workspace Clippy with warnings denied;
- FAIL `cargo +1.95.0 fmt --all -- --check` because committed imports/menu
  formatting differ from that toolchain's `rustfmt` output;
- no application launch or visual/accessibility verification performed.

Refresh these facts before citing them. A green compile does not make the
example production-ready, and a formatting failure does not invalidate its
architectural value.

## Adopt the example safely

When the user chooses the example:

1. Resolve the exact target directory and verify it is not an existing project.
2. Clone the repository into that explicit directory:

   ```sh
   git clone https://github.com/lassejlv/gpui-starter.git <target-directory>
   ```

3. Inspect branch, status, instructions, latest commit, manifests, lockfile,
   source, assets, and commands.
4. Decide with the user whether to retain the example's Git history, create a
   new repository, or use it only as a source reference.
5. Do not delete `.git`, rewrite remotes, or push anywhere unless explicitly
   authorized.
6. Record the source commit in the setup summary; do not record only `main`.
7. Rename identity before adding feature code.
8. Establish a green reproducible baseline before the first product slice.

If the target already exists, compare and copy only the required patterns.
Preserve its existing crate names, architecture, and dependencies unless the
request explicitly includes migration.

## Make builds reproducible

Use the target checkout as authority. For the inspected example, the lockfile
resolves Zed commit `101ca00a…`; the matching Zed toolchain is Rust 1.95.0.
When starting from a later commit, derive both facts again.

Add a checked-in `rust-toolchain.toml` matching the chosen GPUI revision:

```toml
[toolchain]
channel = "1.95.0" # example snapshot only; refresh with the selected Zed commit
profile = "minimal"
components = ["rustfmt", "clippy"]
```

For a production application, make the Git revision explicit in the manifest
as well as the lockfile:

```toml
[workspace.dependencies.gpui]
git = "https://github.com/zed-industries/zed"
rev = "101ca00a1352ed71ef398f21b47836565d1998e3"

[workspace.dependencies.gpui_platform]
git = "https://github.com/zed-industries/zed"
rev = "101ca00a1352ed71ef398f21b47836565d1998e3"
default-features = false
```

Keep platform features in the desktop crate so support is deliberate:

```toml
[target.'cfg(target_os = "macos")'.dependencies]
gpui_platform = { workspace = true, features = ["font-kit"] }

[target.'cfg(any(target_os = "linux", target_os = "freebsd"))'.dependencies]
gpui_platform = { workspace = true, features = ["wayland", "x11"] }

[target.'cfg(target_os = "windows")'.dependencies]
gpui_platform.workspace = true
```

Confirm this exact shape against the chosen revision; feature names can change.

Also:

- commit `Cargo.lock`;
- use `--locked` in CI and release builds;
- set `rust-version` in workspace/package metadata where downstream tooling
  needs it;
- define workspace lint policy instead of letting crates drift;
- review `cargo tree -d` and native dependency changes when updating GPUI;
- avoid an unattended dependency bot merging a GPUI revision bump with product
  work;
- document native build prerequisites per supported platform.

Upgrade GPUI in an isolated change. Recompile, test, launch, and recheck
rendering, text metrics, focus, input, window behavior, and platform artifacts.

## Rename the product completely

Create one identity ledger and apply it consistently:

| Surface | Example placeholder | Product value |
|---|---|---|
| Workspace UI package | `gpui-starter-ui` | `<slug>-ui` |
| Desktop package | `gpui-starter-desktop` | `<slug>-desktop` |
| Binary | `gpui-starter` | stable executable name |
| Rust action namespace | `gpui_starter` | valid Rust identifier |
| App/window/menu title | `GPUI Starter` | product name |
| Application ID | `com.gpui-starter.app` | owned reverse-DNS ID |
| macOS bundle ID | not supplied | same canonical app identity |
| Linux desktop ID | not supplied | matching `.desktop` basename/app ID |
| Windows identity | not supplied | stable publisher/product identity |
| Config/data/log directories | not supplied | derived from canonical ID |
| Icons | starter artwork | final product artwork at required sizes |

Search after renaming:

```sh
rg -n 'gpui[-_ ]starter|GPUI Starter|com\.gpui-starter\.app' .
cargo metadata --locked --no-deps
```

Do not leave mixed names in the lockfile, menu, binary, app ID, desktop entry,
bundle metadata, installer, update manifest, crash reports, or storage paths.
Avoid changing the app ID after users have production data unless a migration
is designed; operating systems treat identity changes as a different app.

## Keep workspace boundaries honest

Start with the example's two crates unless real product code proves another
boundary:

```text
crates/
  desktop/       # process, platform, app lifecycle, windows, menus
  ui/            # root views, components, themes, UI-local state
```

Add a headless `core`, `domain`, or `services` crate only when meaningful logic
needs to be shared, tested without GPUI, or embedded elsewhere:

```text
crates/
  core/          # domain types, reducers, validation, persistence contracts
  ui/            # GPUI views/components and presentation state
  desktop/       # native process and platform adapters
```

Ownership rules:

- `desktop` owns process startup, global registration, product identity,
  windows, menus, platform adapters, and shutdown;
- `ui` owns visual components, focus/key contexts, root screen entities,
  semantic material tokens, and presentation state;
- `core` owns only UI-independent domain behavior;
- services own I/O contracts and return domain data, not GPUI elements;
- platform code stays behind narrow capability interfaces;
- public APIs expose semantic operations rather than internal modules.

Do not begin with a crate per feature, a framework around GPUI, or a global
service locator. Split after a boundary has a second consumer, independent test
surface, or platform-specific implementation.

## Structure startup as observable phases

Keep `main` small and make startup failures attributable:

```text
main
  -> install panic/crash reporting policy
  -> initialize structured diagnostics
  -> load version/build identity
  -> resolve app directories
  -> load and migrate configuration
  -> construct services/models
  -> construct GPUI application
  -> register actions, keybindings, menus, globals, fonts, assets
  -> open/restore windows
  -> activate application
```

Use the exact pinned startup API. Do not paste an `Application::new()` example
into a revision that uses `gpui_platform::application()`.

Requirements:

- no network or blocking disk work in `render`;
- startup errors include the failed phase and a safe recovery option;
- corrupted optional config falls back or offers reset without deleting user
  documents;
- mandatory initialization failures exit with an actionable diagnostic;
- background work starts only after its owner exists;
- actions, menus, assets, fonts, and globals are registered before views use
  them;
- app version, commit/build ID, and GPUI revision are available to diagnostics
  and About/support surfaces.

Avoid discarding errors with `.ok()` or generic `expect("failed")` in
recoverable paths. A final process boundary may terminate, but its message must
identify the operation and relevant safe path.

## Set window and platform policy

Decide and test:

- default, minimum, and useful maximum content sizes;
- titlebar/decorations, resize, move, fullscreen, and activation;
- last-window close versus app quit on each platform;
- New Window/Reopen behavior;
- canonical `app_id` and platform identity mapping;
- restored bounds with display/scale clamping;
- light/dark/inactive appearance;
- opaque, translucent, and accessibility fallbacks.

The example uses `WindowBackgroundAppearance::Blurred` for the whole window.
Keep it only if the product intentionally wants a supported whole-window
backdrop. In the pinned GPUI snapshots, non-opaque window backgrounds disable
the subpixel text path. Provide an opaque/reduced-transparency fallback and
verify legibility, performance, inactive windows, and unsupported backends.
Do not call this bounded native Liquid Glass.

Register platform-appropriate shortcuts rather than treating `cmd-*` as
portable. Menus, keybindings, buttons, and accessibility actions should invoke
the same typed command.

Read [input-windows.md](input-windows.md) for multi-window close policy and
restoration. Read [apple-glass.md](apple-glass.md) before choosing blur/material.

## Add configuration, persistence, and secrets

Define separate storage classes:

| Data | Location/policy |
|---|---|
| User configuration | Versioned file in the platform config directory |
| Durable product data | Document/database in platform data directory or user-selected path |
| Cache | Rebuildable cache directory with bounded retention |
| Logs | Platform log directory with size/age limits and redaction |
| Credentials/tokens | OS credential store or approved secure provider, never plain config |
| Window/session state | Versioned, non-sensitive restoration record |

Persistence requirements:

- version every schema;
- parse defensively and preserve unknown/future data where appropriate;
- migrate explicitly with tests;
- write to a temporary sibling, flush when durability matters, then atomically
  replace;
- serialize off the application thread when data is non-trivial;
- guard stale async saves with a revision/generation;
- never silently overwrite a newer external edit;
- distinguish config reset from deleting user documents;
- keep backups only under a defined retention/privacy policy.

Load enough state to show a reliable first window; defer expensive indexing or
network synchronization behind visible progress and cancellation.

## Add services and asynchronous state

Model user-visible operations as explicit state machines:

```text
Idle -> Loading -> Ready
                -> Empty
                -> Failed(retryable, message)
Loading --cancel/restart--> Loading(new generation)
```

For each operation define:

- owner entity/model;
- request identity or generation;
- cancellation behavior;
- timeout/retry/backoff policy;
- offline behavior;
- stale-result rejection;
- user-visible loading/empty/error state;
- safe diagnostic fields;
- shutdown behavior.

Hold lifecycle-bound `Task` and `Subscription` values. Capture `WeakEntity` in
long-running work. Run blocking/CPU work on the background executor and update
GPUI state on the application thread. Detach only app-lifetime work whose
errors are observed.

Keep service interfaces independent from views so pure behavior can be tested
with deterministic fakes. Do not create a dependency-injection framework for a
single service; pass the narrow owned dependency the model actually uses.

## Establish the accessible UI baseline

Before adding product screens, make the starter component contract complete:

- stable unique element/accessibility IDs;
- semantic roles, labels, values, and states;
- Tab order and visible focus;
- Enter/Space or platform-standard keyboard activation;
- typed actions shared with menus/shortcuts;
- disabled state enforced in the semantic handler;
- pointer down/hover/active feedback;
- non-color state indicators;
- minimum useful hit target;
- reduced motion, reduced transparency, increased contrast, light/dark, and
  inactive-window behavior;
- no essential pointer-only workflow.

The example button supplies stable element IDs and pointer styling, but a
production component must verify explicit role/label, tab stop, keyboard
activation, disabled behavior, focus-visible styling, and accessibility action
dispatch against the pinned revision.

Build a small component gallery inside development/test tooling if it helps
exercise default, hover, active, focused, disabled, loading, and error states.
Do not ship a demo gallery as the product root.

Read [accessibility-platform.md](accessibility-platform.md) and
[components-layout.md](components-layout.md).

## Add diagnostics and supportability

Make failures diagnosable without exposing user data:

- structured logs with timestamp, level, subsystem, and build identity;
- configurable development verbosity and conservative production defaults;
- bounded file retention/rotation;
- panic hook or crash reporter appropriate to distribution and consent;
- breadcrumbs for startup phase, window lifecycle, migrations, and operation
  state—not document/clipboard/secret contents;
- user-visible error surfaces with a safe retry/reset/export-diagnostics path;
- About/support view containing version, build, platform, and update channel;
- optional diagnostics bundle that redacts paths, tokens, and personal content.

Do not initialize logging after fallible configuration loading. Do not emit
secrets, clipboard contents, document text, auth headers, or full user paths by
default. Telemetry and crash upload require an explicit privacy/product policy.

## Build a useful testing pyramid

Use the narrowest reliable test for each contract:

1. **Pure unit tests:** config parsing/migration, reducers, validation,
   persistence paths, identity mapping, stale-generation rules, geometry.
2. **Service tests:** deterministic fakes, timeouts, cancellation, offline/error
   mapping, atomic persistence.
3. **`#[gpui::test]`:** actions, entity events, focus, input, windows, async
   orchestration, accessibility state.
4. **Launch smoke:** real application opens, renders, accepts input, and exits
   cleanly in debug and release modes.
5. **Visual/accessibility QA:** relevant states, sizes, scale factors,
   appearances, preferences, and assistive technology.
6. **Installed artifact:** install, first launch, data path, upgrade, rollback,
   uninstall, and signing verification.

Do not count “0 tests passed” as behavioral coverage. Do not make screenshots
the only test of commands, persistence, or state machines.

Minimum starter regressions:

- product identity is consistent;
- config default/migration/corrupt fallback;
- one typed action updates root state;
- one keyboard/focus path;
- one async cancellation or stale-generation path if async exists;
- window opens with intended options;
- reduced-motion/opaque preference selection remains deterministic;
- packaging metadata matches runtime identity.

Read [testing-qa.md](testing-qa.md) for GPUI-specific test/runtime separation.

## Add continuous integration

Create fast required checks before feature work grows:

```sh
cargo fmt --all -- --check
cargo check --workspace --locked --all-targets
cargo test --workspace --locked
cargo clippy --workspace --locked --all-targets -- -D warnings
```

Then add platform jobs proportionate to support claims:

| Job | Purpose |
|---|---|
| Linux | Shared Rust plus selected X11/Wayland feature compilation and tests |
| macOS | AppKit/Metal compilation, tests, bundle/signing scripts, launch smoke where possible |
| Windows | Native backend compilation, tests, resources/manifest, installer scripts |
| Release | Reproducible artifacts, checksums, signing, provenance, draft release |

Rules:

- pin action dependencies to reviewed immutable commits;
- use the checked-in toolchain and `Cargo.lock`;
- install only native prerequisites required by the pinned GPUI features;
- cache downloads/build output without making cache correctness-critical;
- cancel superseded branch runs;
- set least-privilege workflow permissions;
- keep signing secrets out of forked/untrusted pull-request jobs;
- upload useful failure logs without user/secret data;
- do not call cross-compilation runtime support.

Add dependency/license/vulnerability review appropriate to the release policy.
Treat advisories with context; do not blindly update the pinned GPUI graph in a
mixed change just to make a scanner quiet.

## Package and sign each platform

Do not call a raw `target/release/<binary>` a finished desktop release.

### macOS

Define:

- `.app` structure and executable name;
- `Info.plist`, bundle ID, version/build, minimum macOS, icon, document/URL
  types if used;
- minimal entitlements and hardened runtime;
- architecture policy (Apple Silicon, Intel, or universal);
- signing identity, nested-code signing order, notarization, stapling;
- DMG/ZIP/Homebrew delivery and Gatekeeper verification;
- clean-machine first launch, upgrade, and uninstall behavior.

### Windows

Define:

- executable metadata, application identity, icon, and requested execution
  level;
- MSVC/architecture targets;
- code-signing certificate/timestamping;
- MSI/MSIX/installer or portable distribution policy;
- Start menu/uninstall registration and data retention;
- SmartScreen/reputation expectations and clean-machine verification.

### Linux

Define supported distributions/backends instead of claiming all Linux:

- binary and required shared libraries;
- `.desktop` basename matching runtime app ID/WM class;
- icons and MIME/URL handlers;
- AppImage, deb, rpm, Flatpak, or distro packages actually supported;
- Wayland and/or X11 launch behavior;
- sandbox/portal integration where distribution requires it;
- install, upgrade, and uninstall verification.

Keep packaging scripts in the repository, deterministic, and locally
inspectable. Generate checksums and a machine-readable update/release manifest
only when a consumer actually uses them.

## Plan updates, migrations, and recovery

Choose one update owner:

- app store/package manager;
- signed in-app updater;
- manual download with visible version checks;
- managed enterprise deployment.

For an in-app updater, require HTTPS, signed metadata/artifact policy, explicit
channel/platform/architecture selection, streamed download, size and digest
verification, unique temporary files, atomic finalize, and a narrowly scoped
installer. Never execute an unverified downloaded file.

Coordinate application updates with data migrations:

- migrations are versioned and tested from every supported predecessor;
- destructive migration requires backup/recovery policy;
- rollback behavior is explicit when newer data cannot be read by older code;
- interrupted updates and interrupted migrations recover safely;
- update UI exposes current version, target version, progress, error, retry,
  and restart requirements.

Do not add an updater merely because the app is desktop software. Store and
package-manager distribution may already own updates.

## Protect security and privacy

Production baseline:

- no embedded production credentials or signing secrets;
- OS credential storage for secrets;
- TLS verification and bounded requests for network features;
- untrusted file/URL/drag-drop/input validation;
- safe path handling without traversal or arbitrary overwrite;
- least-privilege entitlements, permissions, and workflow tokens;
- dependencies and licenses inventoried;
- logs, crash reports, analytics, and update checks covered by privacy policy;
- IPC/custom protocols authenticate and validate messages if introduced;
- debug tooling and dev servers disabled or gated in release artifacts;
- unsafe/native bridges isolated, documented, and tested.

Threat-model only surfaces the product actually adds. A local button app does
not need invented network defenses, but it still needs trustworthy release
artifacts and safe local storage once those features exist.

## Build one production vertical slice

After the baseline compiles, replace the demo with one real end-to-end path:

1. Load versioned configuration.
2. Construct one domain/service model.
3. Open the root window with canonical identity.
4. Render a meaningful default/empty state.
5. Execute one typed action from pointer and keyboard.
6. Show loading/success/error/cancellation if work is asynchronous.
7. Persist one durable preference or document operation atomically if needed.
8. Expose semantic accessibility and visible focus.
9. Add pure and GPUI regression tests.
10. Launch, interact, restart, and verify the release build.

Only then extract more components/services. Delete the starter button gallery
when it no longer serves development or product needs.

## Run the acceptance matrix

Record evidence, not intentions:

| Ring | Required evidence |
|---|---|
| Source | Clean intended diff; instructions, license, identity, no secrets |
| Reproducibility | Fresh checkout uses checked-in toolchain/lockfile |
| Static | Format, check, tests, strict Clippy, dependency/license policy |
| Runtime | Debug and release launch; actions, focus, resize, close/reopen |
| State | First run, restart, corrupt config, migration, concurrent/stale save |
| Accessibility | Keyboard-only, visible focus, semantics, screen reader, preferences |
| Appearance | Light/dark/inactive, scale, minimum/default/larger sizes, opaque fallback |
| Platforms | Real launch on every claimed backend/platform |
| Packaging | Installed signed artifact on clean environment |
| Upgrade | Prior supported version to current; failure and rollback/recovery |
| Operations | Useful redacted logs/crash/version support data |

Use this completion language precisely:

- “compiled” for compiler gates;
- “tests passed” for named test commands;
- “launched” only when a real window opened;
- “behavior verified” only for named exercised interactions;
- “packaged” only when an artifact was constructed;
- “release-ready” only after signing/install/upgrade gates for claimed
  platforms.

## Reject production-starter anti-patterns

- Floating GPUI `main` branch presented as reproducible production input
- A committed lockfile used as an excuse not to record the chosen Git revision
- Shipping starter package names, menu labels, app ID, icons, or theme blindly
- One huge `main.rs` containing product UI, services, persistence, and platform code
- A crate or trait per future feature before real ownership exists
- Blocking config/network/database work on the GPUI application thread
- Detached tasks whose failures and lifecycle have no owner
- Plaintext tokens in config or logs
- Whole-window blur called per-control Liquid Glass
- No opaque/high-contrast/reduced-motion path
- Clickable `div` controls without keyboard, focus, disabled, and semantics
- “0 tests passed” reported as adequate coverage
- Linux/Windows support inferred from a macOS compile
- Raw release binary reported as an installer/package
- Unsigned update metadata or executing downloads before verification
- CI secrets available to untrusted pull-request code
- Auto-reset that deletes corrupt user data without backup/consent
- Packaging/signing postponed until the last release day
- Green CI used as a substitute for launching the installed app

## Completion checklist

- [ ] Product name, package/binary slug, app ID, publisher, platforms, and distribution recorded
- [ ] Source starter commit and exact GPUI revision recorded
- [ ] Matching Rust toolchain and committed `Cargo.lock` enforced
- [ ] Product identity renamed across runtime, storage, and packaging
- [ ] Desktop/UI/core boundaries match actual ownership
- [ ] Startup phases produce actionable, redacted failures
- [ ] Window, close, appearance, and restoration policy are explicit
- [ ] Config/data/cache/log/secret storage classes are separated
- [ ] Async work has an owner, cancellation, and stale-result protection
- [ ] First real vertical slice replaces the demo path
- [ ] Keyboard, focus, semantics, preferences, and screen-reader path verified
- [ ] Structured diagnostics and support build information exist
- [ ] Pure, GPUI, launch, visual, and installed-artifact tests are proportionate
- [ ] Required CI uses pinned toolchain, lockfile, actions, and least privilege
- [ ] Every claimed platform has packaging, signing, install, and upgrade evidence
- [ ] Update/recovery and privacy policies match actual product behavior
- [ ] Remaining placeholders and unverified platforms are explicit release blockers

Read [project-versioning.md](project-versioning.md) for dependency/API drift,
[architecture-state.md](architecture-state.md) for ownership,
[async-performance.md](async-performance.md) for tasks,
[testing-qa.md](testing-qa.md) for evidence, and
[sources.md](sources.md) for the dated research ledger.

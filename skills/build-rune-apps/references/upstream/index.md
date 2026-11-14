# Bundled Rune documentation

Snapshot of [anomalyco/rune](https://github.com/anomalyco/rune) at [`65f8eb43f710`](https://github.com/anomalyco/rune/tree/65f8eb43f710e078f92cb82039212de50cb03113), taken 2026-11-14.
MIT © Anomaly. Read only the sections a task needs. The pinned rev in the target app's
`Cargo.lock` is the API authority; check its checkout when this snapshot differs.

## Rune overview

- [Rune overview](overview.md)

## Rune's agent rules (state machines, performance)

- [Rune's agent rules (state machines, performance)](agents.md)

## Core crate (`rune`)

- [Introduction](rune/intro.md)
- [What exists](rune/what-exists.md)
  - [Rich text, scrolling and app hooks](rune/rich-text-scrolling-and-app-hooks.md)
  - [Canvas handlers: live-only events and coordinate spaces](rune/canvas-handlers.md)
  - [App lifetime (`app.rs`, for apps that outlive their window)](rune/app-lifetime.md)
  - [Launching fast](rune/launching-fast.md)
  - [Smooth scrolling](rune/smooth-scrolling.md)
  - [Requests off the main thread (`rune::Latest`)](rune/requests-off-the-main-thread.md)
  - [State machines (`rune::machine`)](rune/state-machines.md)
  - [Relaunching a Mac app (`scripts/mac-app`, `rune-mac`)](rune/relaunching-a-mac-app.md)
  - [Logging frame and input timing](rune/logging-frame-and-input-timing.md)
  - [Compact tray-controlled windows](rune/compact-tray-controlled-windows.md)
  - [Resizing and centring a window](rune/resizing-and-centring-a-window.md)
  - [Window chrome and shell controls (OpenCode Desktop fidelity)](rune/window-chrome-and-shell-controls.md)
  - [Finite choreography](rune/finite-choreography.md)
  - [Shared-element motion](rune/shared-element-motion.md)
- [High-frequency values](rune/high-frequency-values.md)
- [Text fields](rune/text-fields.md)
  - [Rich text editing](rune/rich-text-editing.md)
  - [Selectable text](rune/selectable-text.md)
  - [Help tooltips](rune/help-tooltips.md)
  - [File dialogs](rune/file-dialogs.md)
  - [Dragging out to other apps (`drag_out`)](rune/dragging-out-to-other-apps.md)
  - [Dropping files in from other apps (`on_drop_files`)](rune/dropping-files-in-from-other-apps.md)
  - [Pop-up and context menus](rune/pop-up-and-context-menus.md)
- [Multiple windows and overlays](rune/multiple-windows-and-overlays.md)
  - [Pixels (`pixels.rs`)](rune/pixels.md)
  - [NativeSurface video](rune/nativesurface-video.md)
  - [Playing video and audio (`Player`, `video/`)](rune/playing-video-and-audio.md)
  - [Recording audio (`Recorder`, `recorder/`)](rune/recording-audio.md)
  - [Edge overlays (`App::overlay`, `overlay.rs`, `platform/layer_shell.rs`)](rune/edge-overlays.md)
  - [Compositor hook (lighting and effects)](rune/compositor-hook.md)
  - [Isolated opacity](rune/isolated-opacity.md)
  - [Subtree blur and rounded layer clips](rune/subtree-blur-and-rounded-layer-clips.md)
  - [System materials (`El::system_material`, `system_material/`)](rune/system-materials.md)
  - [Frosted panels](rune/frosted-panels.md)
  - [Backdrop blur (`El::backdrop_blur`)](rune/backdrop-blur.md)
- [Accessibility](rune/accessibility.md)
- [Run](rune/run.md)
  - [Depending on Rune](rune/depending-on-rune.md)
  - [Linux](rune/linux.md)
- [Agent tooling (headless, no window, same renderer, fixed virtual clock)](rune/agent-tooling.md)
- [Playground](rune/playground.md)
  - [Testing stories](rune/testing-stories.md)
  - [Moving a story table onto it](rune/moving-a-story-table-onto-it.md)
- [Live Rust editing (desktop development)](rune/live-rust-editing.md)
  - [An external app crate](rune/an-external-app-crate.md)
  - [The desk Mac](rune/the-desk-mac.md)
  - [Compatible edits and restart boundaries](rune/compatible-edits-and-restart-boundaries.md)
  - [Headless input and patch acknowledgement](rune/headless-input-and-patch-acknowledgement.md)
- [Measured (Apple silicon, headless at 2×)](rune/measured.md)
- [Differences from PLAN.md](rune/differences-from-planmd.md)

## Shortcuts, global chords and native menus

- [Shortcuts, global chords and native menus](rune-shortcuts.md)

## Components (`rune-kit`)

- [Introduction](kit/intro.md)
- [The split (PLAN.md §7)](kit/the-split.md)
- [Use](kit/use.md)
- [Components](kit/components.md)
- [App shell](kit/app-shell.md)
- [Tree and Table](kit/tree-and-table.md)
- [Markdown](kit/markdown.md)
- [Diff](kit/diff.md)
- [Checking against Storybook](kit/checking-against-storybook.md)
- [Comparison (lavapipe vs headless Chromium, 2×)](kit/comparison.md)

## Springs and transitions (`rune-motion`)

- [Springs and transitions (`rune-motion`)](rune-motion.md)

## GPU effects (`rune-fx`)

- [GPU effects (`rune-fx`)](rune-fx.md)

## Lighting and materials (`rune-light`)

- [Lighting and materials (`rune-light`)](rune-light.md)

## Luau scripting (`rune-luau`)

- [Luau scripting (`rune-luau`)](rune-luau.md)

## macOS app helpers (`rune-mac`)

- [macOS app helpers (`rune-mac`)](rune-mac.md)

## System notifications (`rune-notify`)

- [System notifications (`rune-notify`)](rune-notify.md)

## Performance logging (`rune-perf`)

- [Performance logging (`rune-perf`)](rune-perf.md)

## Live tuning knobs (`rune-knobs`)

- [Live tuning knobs (`rune-knobs`)](rune-knobs.md)

## Web target (WebGPU canvas)

- [Web target (WebGPU canvas)](web.md)

## Installing and relaunching a Mac app

- [Installing and relaunching a Mac app](scripts-mac-app.md)

## Motion audit and gate

- [Motion audit and gate](scripts-motion-audit.md)

## Example: live values

- [Example: live values](examples/live-values.md)

## Example: motion bento

- [Example: motion bento](examples/motion-bento.md)

## Example: edge overlay

- [Example: edge overlay](examples/overlay.md)

## Example: overlay lab

- [Example: overlay lab](examples/overlay-lab.md)

## Example: window panel

- [Example: window panel](examples/overlay-lab-window-panel.md)

## Example: video tiles

- [Example: video tiles](examples/video-tiles.md)

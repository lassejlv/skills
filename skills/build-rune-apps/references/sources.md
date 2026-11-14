# Sources and audit ledger

Refresh time-sensitive claims against the target app's pinned rev.

## Rune at `65f8eb43f710`

Audited on **2026-11-14** against
[anomalyco/rune](https://github.com/anomalyco/rune) `dev` commit
[`65f8eb43f710e078f92cb82039212de50cb03113`](https://github.com/anomalyco/rune/tree/65f8eb43f710e078f92cb82039212de50cb03113)
("scroll_key_to: lands a virtual row that isn't mounted yet", 2026-11-14), the
newest commit of `dev` that day. At that rev:

- Rune's root `[patch.crates-io]` lists `wgpu-hal`, `winit`, `parley_engine` and
  `accesskit_windows`; `tiny-skia-path` is a path dependency of `crates/rune`,
  not a patch, so apps don't repeat it.
- `rust-toolchain.toml` names 1.99.1; the workspace is edition 2024.
- `rune`'s default features are `accessibility`, `dbus`, `embedded-fonts`,
  `metal-backend`, `ogg-audio`, `svg`.
- `AppSpec` has `title`, `size`, `min_size`, `init`, `view`, `scenes`, `fonts`,
  `families`, `setup`, `poll`, `on_key`.
- The docs site (`site/`) is behind Cloudflare Access, so it isn't bundled; its
  "Launch fast" and "Fast apps" content is covered by the core README's
  "Launching fast" and "Smooth scrolling" sections and `AGENTS.md`.

API names used in the hand-written references were checked against that
checkout's source (`crates/rune/src`, `crates/rune-kit/src`).

## Bundled documentation

`references/upstream/` holds 82 snapshots from 22 Markdown sources at that rev:
the root README and `AGENTS.md`, the core crate README split at its `##` and
`###` headings, the rune-kit README split at `##`, the shortcuts README, the
READMEs of `rune-motion`, `rune-fx`, `rune-light`, `rune-luau`, `rune-mac`,
`rune-notify`, `rune-perf` and `rune-knobs`, `WEB.md`, the `mac-app` and
`motion-audit` script docs, and the example READMEs. `manifest.json` records
each snapshot's source, section, source SHA-256 and snapshot SHA-256. Links to
other bundled documents are local; every other repository link points at
GitHub at the audited rev. Not bundled: `PLAN.md` (direction), `CHANGELOG.md`
(read it at the rev when upgrading), `research/`.

```sh
python3 scripts/sync_rune_docs.py --rev dev   # refresh at the newest dev commit
python3 scripts/sync_rune_docs.py --check     # offline coverage and hash check
```

Rune is MIT licensed, © Anomaly. Every snapshot keeps an attribution line
linking its source at the rev; keep it when refreshing.

## Reference app

`assets/reference-app` was built, linted (`clippy -D warnings`), tested (6
`Runtime` tests) and rendered headless on macOS (Apple silicon) at the audited
rev: four scenes in light and dark at 2x, the element and accessibility tree,
and a script that types, submits and ticks a task. The renders were read back;
a light-mode issue (an off switch invisible on `bg_base`) was found that way and
fixed by using `k.c.page`. It was not launched as a window, bundled, or built
on Windows, Linux or the web.

## Local evidence

`scripts/check_rune_patches.py` and `scripts/inspect_rune_project.sh` were run
against the reference app, an existing Rune app pinned to `165f87a4700a`, and
fixtures with mixed revs, a branch pin, stray and missing patches, and a
workspace-inherited dependency.

## Inspiration

The skill's structure (stack choice before adoption, a core contract, a task
router, bundled upstream docs with a sync/check script, a compile-checked
reference app, an inspector and forward tests) follows this repository's
`build-gpui-apps` skill.

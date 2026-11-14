# Examples and demo map

Rune's [`examples/`](https://github.com/anomalyco/rune/tree/65f8eb43f710e078f92cb82039212de50cb03113/examples)
are complete apps; [`demo/`](https://github.com/anomalyco/rune/tree/65f8eb43f710e078f92cb82039212de50cb03113/demo)
holds the stills the docs show. Read an example in Cargo's checkout of the
pinned rev (`~/.cargo/git/checkouts/rune-*/<short rev>/examples/`); run one from
a clone with `cargo run -p <name> -- --snap out.png`. Each `main.rs` opens with
a `//!` comment saying what it shows and how to run it.

## Start here

| Example | Shows |
| --- | --- |
| `hello` | the smallest app: state, view, a switch on a spring, a scene, a `Runtime` test |
| `todo` | keyed rows animating in and out, a bounded scroll that follows new rows, a springing progress bar |
| `settings` | a real settings window: segmented control, swatches, toggles, slider drag, theme and accent, reduced motion and time scale, scripts in `scripts/*.json` |
| `playground` | `App::playground` stories, triggers, variants, side controls |
| `kit-gallery` | every rune-kit component as a scene; `--kit neutral` or `--kit palette` |

## By capability

| Capability | Example |
| --- | --- |
| App outliving its window, stdin commands, background thread | `background` |
| Several windows, launcher panel, `--desktop` recordings | `launcher` |
| Edge overlays, per-monitor overlays, click-through | `overlay`, `overlay-lab` |
| Shared-element motion (`matched`) | `matched` |
| Live values without view re-runs | `live-values` |
| Live tuning knobs | `knobs` |
| Rolling digits (`RollingText`) | `odometer` |
| Many simultaneous animations, side-by-side with GPUI | `motion-bento` |
| Vector shapes and per-frame drawing | `shapes`, `sketch` (custom cursor) |
| Backdrop blur, system materials, Liquid Glass | `frosted-bar`, `glass-card`, `glass-panel` |
| GPU effects and lighting through the compositor hook | `lab`, `cursed-settings`, `site-scenes` |
| Drag out, drop in, rich clipboard | `drag-out`, `drop-files`, `rich-clipboard` |
| Video and audio playback, external video frames | `video-player`, `video-tiles` |
| Luau scripting with hot reload | `luau-panel` |
| Web target | `web-hello`, `web-showcase` |
| Showcase video scenes on the virtual clock | `showreel` |

rune-kit's own examples (`cargo run -p rune-kit --example <name>`): `shell` (app
shell with sidebar, inspector, peek, reorder), `tree`, `table`, `diff`,
`rich_editor`, `tab_strip`, `shortcut_recorder`, `scroll_x`. Core `rune` has
focused examples too: `sticky`, `canvas_input`, `custom_titlebar`,
`popup_menu`, `scroll_anchor`, `window_resize`.

## Demo stills worth looking at

Open these as images when you need to know what Rune output should look like at
its best (all at the audited rev, under
`https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/`):

- `demo/settings-light.png`, `demo/settings-dark.png`: the settings example.
- `demo/kit/index-light.png`, `index-dark.png`: the component gallery.
- `demo/kit/shell-light.png`, `shell-dark.png`, `shell-peek.png`, `shell-page.png`: the app shell.
- `demo/kit/tree-*.png`, `table-*.png`, `diff-*.png`, `markdown-code-*.png`, `rich-editor.png`.
- `demo/opencode/*.png`: a full coding-agent app built on Rune.
- `demo/motion/*.png`: spring curves, retargeting, presence, press.
- `demo/fx/*.png`, `demo/light/*.png`: rune-fx and rune-light effects, with reduced-motion stills.
- `demo/sticky-headers.png`, `demo/text/*.png`: sticky headers and text quality against CoreText.

`demo/rune.mp4` is the showreel.

## This skill's reference app

[`assets/reference-app`](../assets/reference-app/README.md) is a rune-kit task
list pinned to the audited rev: scenes, a script, keyed rows, a bounded scroll
and `Runtime` tests that drive the real view. Copy it to start an app.

# Headless validation: renders, trees, scripts and tests

Every Rune app can run without a window: same renderer, fixed virtual clock,
deterministic output. That makes "look at what you built" cheap, so do it for
every visible change. Upstream: [agent tooling](upstream/rune/agent-tooling.md),
[playground](upstream/rune/playground.md),
[testing stories](upstream/rune/testing-stories.md),
[accessibility](upstream/rune/accessibility.md).

Debug builds always accept these flags. Release builds need
`rune = { …, features = ["tooling"] }` (or the app's own `tooling` feature);
without it a headless flag makes `run` fail and say so. `--keys` and
`--pointer` need `keys-overlay` in release. The app must pass its arguments to
Rune (`rune::run`/`App::run` read the process argv; `App::args(..)` overrides).

## Renders

```sh
APP=target/debug/my-app
$APP --list-scenes
$APP --snap out/many-dark.png --scene many --theme dark --scale 2
$APP --snap out/narrow.png --size 360x480 --scale 2
$APP --snap out/mid.png --scene many --at 0.15           # a moment mid-animation
$APP --list-windows; $APP --window settings --snap out/settings.png
```

- `--scene NAME` applies an `AppSpec::scenes` entry to the initial state. Add a
  scene for every state worth seeing; scenes are the cheapest regression
  fixtures an app has.
- `--theme light|dark`, `--scale 1|2`, `--size WxH` (points), `--at SECONDS`.
- Read every PNG back as an image and look: clipped or overflowing text,
  invisible controls in one theme, misaligned baselines, empty viewports from a
  collapsed `grow`, focus rings, contrast. Compare light and dark side by side.
- Render the extremes: empty, one item, many items, long unbroken strings,
  narrow and wide windows, reduced motion, large text if the app has a setting.
  Rune has no reduced-motion flag of its own: keep a state field the view
  passes to `cx.reduced_motion(..)` (as `examples/settings` does) and give it a
  scene, or read an app flag through `rune::extra_args()` (as `kit-gallery`
  does with `--reduced-motion`).

## The tree

```sh
$APP --tree out/tree.json [--scene NAME] [--at T]
```

Top-level keys: `elements`, `accessibility`, `title`, `viewport`, `scale`,
`dark_system`, `reduced_motion`, `animating`, `warnings`. Each element row has
`key`, `path`, `role`, `rect` (window points, as presented), `fill`, `opacity`,
`scale`, `blur`, focus flags, `inert`, and text where it has some. Use it to
check keys exist, rects are where the design puts them, nothing has zero size,
and the accessibility tree names every control. Read `warnings`.

## Scripts

```json
{"events": [
  {"t": 0.2, "type": "tap", "key": "draft"},
  {"t": 0.4, "type": "type", "text": "Write the forward tests"},
  {"t": 1.2, "type": "key", "name": "Enter"},
  {"t": 1.6, "type": "tap", "key": "task-3/check"},
  {"t": 2.4, "type": "mark", "name": "end"}
]}
```

```sh
$APP --script scripts/add.json --snap out/after.png --at mark:end --scale 2
$APP --script scripts/add.json --tree out/after.json --at mark:end
$APP --script scripts/add.json --frames 24 --every 3 --cols 4 --strip out/strip.png
$APP --script scripts/add.json --video out/add.mp4 --keys --pointer   # ffmpeg on PATH
```

- Events land at `x,y` points or at an element by `key` or key path. Types:
  `move`, `down`, `up`, `tap`, `double-click`, `drag` (`dx`, `dy`, `dur`),
  `type`, `key` (`name`, modifiers `cmd`/`shift`/`alt`/`ctrl`, optional `code`),
  `paste`, `scroll`, `fling`, `wheel`, `magnify`, `resize`, `shortcut`
  (registered global chords only), `mark`, plus `menu-pick`, `file-dialog`,
  `drop_files`, `{"reopen": true}`, `{"open_url": ".."}`.
- `--at mark:end+0.5` and `--duration auto` use marks; always end a script
  with an `end` mark.
- Key names: Space is `" "` (`"Space"` fails with "unknown key"); others are
  `Enter`, `Escape`, `Tab`, arrows and so on.
- Tab reaching buttons follows the host's keyboard-navigation setting on macOS
  (off by default, so Tab skips buttons). Prove keyboard access to buttons in a
  `Runtime` test rather than a Tab script.
- Keep scripts in the app (`scripts/*.json`) next to the scenes they exercise.

## `Runtime` tests

```rust
use rune::{Env, Runtime};

let mut rt = Runtime::new(State::new(), view, (420.0, 520.0), Env::new(false, 2.0));
rt.frame(0.0);
let (x, y) = rt.find("task-1/check").expect("row is drawn");
rt.pointer_down(x, y);
rt.pointer_up(x, y);
for _ in 0..30 { rt.frame(1.0 / 60.0); }
assert!(rt.state.tasks[1].done);
let tree = rt.accessibility_json().to_string();
```

- `Runtime::new(state, view, viewport, env)`, `frame(dt)`, `find(key)` (centre
  point), `presented(key)` (rect and opacity as drawn now), `elements()`,
  `pointer_down/move/up`, `key(KeyEvent)`, `paste(text)`, `state`,
  `accessibility_json()`. With a playground,
  `App::new(spec).playground(..).headless_runtime(size, env)` adds
  `open_playground`, `playground_trigger`, `playground_state`.
- Drive the real view through input, as the reference app's tests do. Calling a
  state method directly tests the method, not the UI.
- Advance frames after input: handlers run between frames and motion needs time.
- Isolate persistence in tests with `RUNE_PREFS_DIR` / `RUNE_DIRS_ROOT`.
- Motion: `rune::motion_gate` records the real runtime and fails on pops,
  jumps and overshoot; see [motion](motion.md).

## What headless can't prove

Native IME candidate windows, system clipboard, real menus and file dialogs,
drag and drop with other apps, multi-monitor placement, window-manager
behaviour, GPU presentation and pacing, VoiceOver/Narrator speech, and system
materials. Launch the real window (and, for a Mac bundle, the bundle through
`open`) for those, and say in the report which were exercised and which weren't.

## Visual QA checklist

- Both themes rendered and read; no control disappears on its surface.
- Text never clips unexpectedly; truncation shows an ellipsis or fade where
  intended.
- Scroll viewports have height; footers stay in the window.
- Every interactive element has a key, a role and a name in `--tree`.
- Focus rings visible on keyboard focus; disabled states look disabled.
- Empty, loading and error states exist as scenes and look intentional.
- Reduced motion lands everything without travel.

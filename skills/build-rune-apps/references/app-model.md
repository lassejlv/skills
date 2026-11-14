# App model: state, view, handlers and lifetime

Verified at the audited rev ([sources.md](sources.md)). Names move between revs;
grep the pinned checkout before relying on one.

## One frame

1. Input arrives. Handlers attached to elements are queued.
2. Between frames the queue runs, each handler with `&mut S` (and a `Tx` when it
   asks for one).
3. `poll(&mut S, clock, &mut Tx) -> bool` runs before every frame.
4. If state changed, `view(&S, &mut Cx<S>) -> El` re-runs, Rune diffs the keyed
   tree, lays it out with Taffy and retargets each property's spring.
5. The renderer draws the animated values. Hover and press retarget tracks only;
   they never re-run the view.

So the view describes where things are; motion, hover, press, focus rings,
scroll offsets and presence are Rune's.

## `AppSpec`

```rust
AppSpec::<State> {
    min_size: Some((360.0, 320.0)),
    scenes: &[("empty", |s| s.items.clear()), ("many", seed_many)],
    setup: Some(setup),     // once, with a Waker other threads call when data arrives
    poll: Some(poll),       // every frame; true only when visible state changed
    on_key: Some(on_key),   // keys focused controls didn't take; true consumes
    fonts: &[], families: ("Inter", "Inter"),
    ..AppSpec::new("Title", (420.0, 520.0), State::new, view)
}
```

End literals with `..AppSpec::new(..)` so new fields don't break the app.
`init` and `view` are plain `fn`s; `App::init(closure)` takes a closure when the
first state needs captured values.

## Entry points

- `rune::run(spec)`: one window; the process ends when it closes.
- `rune::App::new(spec)…run()`: the app owns its lifetime. Builder calls used
  by real apps: `.titlebar(Titlebar)`, `.chrome(Chrome)`, `.standard_menus()`
  (macOS Edit/Window menus), `.on_close(fn)`, `.on_quit(fn)`,
  `.on_open_url(|s, url, tx| ..)`, `.on_reopen(..)`, `.on_ready(|window| ..)`,
  `.keep_running()`, `.windowless()`, `.accessory()`, `.playground(..)`,
  `.overlay(..)`, `.window(..)`, `.handle()`.
- `run_windows(|displays| Vec<WindowSpec<S>>)` for several windows on one event
  loop; see [multiple windows](upstream/rune/multiple-windows-and-overlays.md).
- `App::try_run` returns the error `run` would panic with when no display or
  logged-in session exists (CI, ssh).
- Call `rune::prewarm_gpu()` first in `main`; it overlaps GPU setup with
  platform startup on macOS and does nothing elsewhere.

## Handlers

- `on_press(|s: &mut S| ..)`, `on_press_tx(|s, tx| ..)`, `on_double_press`,
  `on_secondary_press(|s, point, tx| ..)`, `on_drag(|s, drag, tx| ..)`,
  `on_hover_change`, `on_wheel`, `on_key_up`, `on_drop_files`.
- Annotate the state type (`|s: &mut State|`); inference can't see it.
- Capture ids, not references: `let id = item.id; move |s: &mut State| s.toggle(id)`.
- Keep handlers short: change state, ask `Tx` for effects. Debug builds warn when
  a handler or `poll` blocks for 8 ms.
- rune-kit components take handlers through their builders (`on_toggle`,
  `on_edit`, `on_submit`, `on_choose`) so disabled components drop them.

## `Cx` (view side) and `Tx` (handler side)

| `Cx` | Use |
| --- | --- |
| `system_dark()`, `env()` | appearance and scale for theme choice and hairlines (`1.0 / env().scale`) |
| `reduced_motion(bool)`, `is_reduced_motion()`, `time_scale(f)` | the app's motion setting |
| `layout_size(key)`, `layout(key)`, `layout_with(..)` | measured sizes from the last layout; a scroll doesn't re-run the view |
| `window_layout(..)` | only when the view needs where the window shows an element |
| `titlebar_inset()`, `set_titlebar(..)` | macOS traffic-light clearance |

| `Tx` | Use |
| --- | --- |
| `instant()`, `settle()`, `color_motion(spring)` | land a change without animation, or set its colour spring |
| `live_only()` | the handler only moved live values; skip the view |
| `wake_after(d)`, `wake_at(t)`, `clock()` | timers on the app clock (virtual when headless) |
| `focus(key, ring)`, `blur()`, `focused()` | focus by key |
| `scroll_into_view(key)`, `scroll_to_with(..)`, `keep_on_screen(key)` | scrolling by key |
| `copy(text)` | clipboard write (headless runs never touch the system clipboard) |
| `set_title`, `close_window`, `minimize`, `quit`, `resize_window` | window requests |
| `physical_key()`, `key_base()` | layout-independent shortcut matching |

## State design

- Keep domain data, selection, drafts (`TextEdit`), which overlay is open, and
  modes in `S`. Store `Option<Id>` for "which popover is open", not booleans per
  popover.
- Behaviour with phases (hover delays, drags, requests and retries, dialog flows)
  is one `enum` whose variants carry only valid data, stepped by one
  `fn step(..) -> Effects<E>` from `rune::machine`. Timers are events: store the
  due time, `tx.wake_at(due)`, feed `Due` back in. `Seq`/`Attempt` fence stale
  answers. See [state machines](upstream/rune/state-machines.md).
- Persistent settings: `rune::prefs::Prefs::open("com.example.app")` (JSON in the
  platform config dir; `RUNE_PREFS_DIR` or `RUNE_DIRS_ROOT` isolate tests).
  Other files go under `rune::dirs`. Never read or write files in `view`,
  handlers on hot paths, or the frame loop; save on close/quit or on a debounced
  wake, off the UI thread.
- Hot reload keeps state across patches only in `AppSpec::init`'s value.

## Work off the UI thread

| Need | Tool |
| --- | --- |
| A thread or service pushes data | `setup` stores the `Waker`; the thread updates shared data and calls `waker()` (`Waker` is `Arc<dyn Fn() + Send + Sync>`); `poll` moves it into state and returns true |
| Change state from anywhere | `app.handle()` → `AppHandle::update(|s, tx| ..)` (Clone + Send + Sync; runs on the UI thread, even with no window) |
| One request per keystroke, newest wins | `rune::Latest` with `.debounce(..)`, `request`/`take` in `poll` |
| Fire-and-forget work | `rune::task::spawn(name, work)` or `spawn_after` |
| Start slow things after the first frame | `App::on_ready(|window| ..)` plus `handle.update` |

Call `Latest::cancel` (or drop it) from `on_close`; state outlives a closed window.

## Lifetime

`keep_running()` keeps state and the loop when the window closes; `windowless()`
starts without one. Hidden or fully covered windows run `poll`, timers and
updates but don't build or draw; the frame that shows them builds once with
motion already landed. See [app lifetime](upstream/rune/app-lifetime.md) for
reopen, URL schemes and single-instance behaviour.

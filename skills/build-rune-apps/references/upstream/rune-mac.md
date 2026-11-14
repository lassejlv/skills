> Upstream: [crates/rune-mac/README.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-mac/README.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# rune-mac

Small macOS helpers for Rune apps, with Rune's `scripts/mac-app` (see "Relaunching a Mac app"
in `crates/rune/README.md`), which relaunches a rebuilt app in place without its window
blinking or taking focus.

| Helper | What it does |
| --- | --- |
| `launch()` | Call first thing in `main`. When `scripts/mac-app` relaunched the app while it wasn't in front, it starts behind the app in front instead of taking focus. |
| `remember_frame(name) -> bool` | Has AppKit save the window frame under `name` and restore it next launch, so a rebuild's window lands over the old one. Call it from `poll` until it returns true. |
| `saved_size(name) -> Option<(f32, f32)>` | The size `remember_frame(name)` saved, to open the window at (`AppSpec::size`), so the layout doesn't animate to it at launch. |
| `toggle_full_screen()`, `is_full_screen()` | The key window's macOS full screen (the green button, ⌃⌘F). |
| `busy(on)` | Holds `scripts/mac-app`'s relaunch while on, for work a relaunch would lose. |
| `notify` | `rune-notify`, re-exported: system notifications on macOS (`UNUserNotificationCenter`) and Windows (toasts). See its README. |

Off macOS every helper is a no-op: `remember_frame` returns true, `saved_size` returns `None`,
`is_full_screen` returns false, and the rest do nothing.

```rust
fn main() {
    rune_mac::launch();
    let size = rune_mac::saved_size("Example").unwrap_or((900.0, 640.0));
    rune::run(AppSpec::<State> {
        poll: Some(|s, _, _| {
            if !s.framed { s.framed = rune_mac::remember_frame("Example") }
            false
        }),
        ..AppSpec::new("Example", size, State::default, view)
    });
}
```

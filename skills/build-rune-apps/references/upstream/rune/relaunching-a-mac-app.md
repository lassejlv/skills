> Upstream: [crates/rune/README.md § Relaunching a Mac app (`scripts/mac-app`, `rune-mac`)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#relaunching-a-mac-app-scriptsmac-app-rune-mac) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Relaunching a Mac app (`scripts/mac-app`, `rune-mac`)

`cargo run` starts a bare binary: no bundle, so no icon, no links, no microphone prompt, and a
window that opens at its default place every run. `scripts/mac-app` installs a built binary as
`~/Applications/NAME.app` and relaunches it without the window blinking: the new bundle is built
beside the running one, swapped in and started, and the old process quits once the new one is up.

```sh
cargo build --release -p example
scripts/mac-app --name Example --id com.example.app --exe example --bin target/release/example \
  --icon assets/icon.icns --scheme example --mic "To take dictation" -- --some-app-flag
```

- `--name`, `--id`, `--exe` and `--bin` are required: the bundle's name, its bundle id, the
  executable's name inside it, and the binary to copy in. `--icon` is an `.icns`. Arguments
  after `--` go to the app.
- `--scheme NAME` declares `NAME://` links in the bundle and registers it with Launch Services,
  so `App::on_open_url` receives them at once.
- `--mic "WHY"` adds the microphone usage string macOS shows in its first-run prompt.
- `--wait-idle SECS`, for unattended rebuilds (a file watcher, an agent), holds the swap while
  the app is in front and the keyboard or mouse was used in the last SECS seconds. When the app
  isn't in front, it relaunches behind the app that is, without taking focus.
- `MAC_APP_SIGN="Developer ID Application: …"` signs with that identity, so macOS remembers
  permission answers across rebuilds. Without it the bundle is signed ad hoc, which macOS treats
  as a new app each build.

The `rune-mac` crate holds the app's side (all no-ops off macOS):

- `rune_mac::launch()`, first thing in `main`, keeps a relaunch behind the app in front from
  activating. winit activates every app it starts, `open -g` or not.
- `rune_mac::remember_frame(name)`, called from `poll` until it returns true, has AppKit save the
  window frame and restore it next launch; `rune_mac::saved_size(name)` gives that size for
  `AppSpec::size`, so the layout doesn't animate to it at launch.
- `rune_mac::busy(true)` holds the script's swap, for up to 15 minutes, while the app is doing
  something a relaunch would lose; `busy(false)` lets it go. The marker is the process's pid
  under `~/Library/Caches/mac-app/busy/`, so a crash can't hold the swap.
- `rune_mac::toggle_full_screen()` and `is_full_screen()` drive the key window's full screen.

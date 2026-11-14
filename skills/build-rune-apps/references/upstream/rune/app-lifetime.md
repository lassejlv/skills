> Upstream: [crates/rune/README.md § App lifetime (`app.rs`, for apps that outlive their window)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#app-lifetime-apprs-for-apps-that-outlive-their-window) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### App lifetime (`app.rs`, for apps that outlive their window)

`rune::run(spec)` opens one window and quits when it closes. `rune::App` gives the app its own
lifetime (`examples/background` exercises all of it):

```rust
let app = rune::App::new(spec)
    .init(move || Ui::new(host))   // first state from a closure (scenes still apply)
    .args(Vec::new())              // Rune flags from here, not the process argv
    .windowless()                  // start with no window (implies keep_running)
    .keep_running()                // closing the window keeps the process, state and loop
    .release_gpu_when_closed()     // optional: drop the GPU device while closed
    .accessory()                   // macOS: menu-bar app, no Dock icon (h.set_dock_icon(true) shows it)
    .standard_menus()              // macOS: Edit, Minimize ⌘M and Close ⌘W (no Quit); regular apps get them anyway
    .on_close(|s, tx| ..)          // runs before every close; tx.quit() quits instead
    .on_reopen(|s, has_visible, tx| false); // macOS: Dock icon clicked; true skips the default
    // .window_options(WindowOptions { max_size, resizable, .. }) for this window
let handle = app.handle();     // AppHandle<S>: Clone + Send + Sync, usable before run
std::thread::spawn(move || {
    handle.activate(token);    // show + focus with a forwarded XDG activation token
    handle.open();             // show + focus without one
    handle.update(|s, tx| ..); // change state on the UI thread; commits on the next frame
    handle.close();            // as the close button (on_close runs)
    handle.minimize();         // as the minimize button
    handle.quit();             // run returns; on web, unmounts
});
app.run();
```

- Every handle call wakes the loop; nothing polls. Updates run in call order on the main thread
  inside the event loop, even while no window shows, so a closed app keeps its state current and
  an update may do main-thread native work (a status item, a tray). Window requests collapse to
  the latest.
- A window that's hidden, minimized or fully covered (another window over all of it, or another
  Space; macOS and X11 report covering, Wayland neither covering nor minimizing) runs updates, `poll`, `wake_after` timers, `on_close` and queued
  input as usual, but not its view or layout, and draws nothing. The frame that shows it again
  builds once with the latest state, with motion already landed where it would have ended. A
  window any part of which shows draws as usual. Headless runs always see a current tree.
- Handlers ask the shell with `Tx::close_window()`, `Tx::minimize()` and `Tx::quit()` (quit wins,
  and either wins over minimize). Minimize does nothing for a hidden window, a panel, a launcher,
  an overlay, a borderless window or a window that can't minimize (debug builds say so).
- `Tx::set_title("Draft — Notes")` sets the window's title from a handler or `update`. The window
  opens with `AppSpec`'s title, keeps the last one set when it closes and opens again, and headless
  `--tree` output shows it as `"title"`.
- The `Runtime` (state, scene, text, scroll offsets) belongs to the app, so a reopened window
  shows the same UI, settled on its first frame. The GPU device and renderer stay too, unless
  `release_gpu_when_closed` (then closing destroys the window and device everywhere).
- Closing hides the window on macOS, Windows and X11, and destroys it on Wayland (no hidden
  toplevel exists there); `open` recreates it with the same app id (`set_app_id`).
- Activation: the first window takes the launcher's `XDG_ACTIVATION_TOKEN`/`DESKTOP_STARTUP_ID`
  and clears them from the environment. A new window gets a forwarded token through winit's
  `with_activation_token`. An open Wayland window is activated with `xdg_activation_v1` bound on
  winit's own display (`platform/activation.rs`), since winit 0.30 can't. Without a token Wayland can only
  request attention (most compositors mark it urgent); X11, macOS and Windows use `focus_window`.
- Headless tooling runs ignore window requests and apply updates before each frame.
- `AppHandle::is_visible()` reports whether the window is on screen; `AppHandle::window_error()`
  says why it couldn't be created (no display, no GPU adapter or device). A failed creation is
  logged and leaves the app windowless; the next open tries again (`Gpu::try_new`).
- `run` panics when the event loop can't start: no Wayland or X11 display, or a Mac no one is
  logged in to (over ssh or in CI). `App::try_run`, `try_run_windows_with` and
  `try_run_windows_with_args` return that error instead.
- `App::on_window(|w: &WindowHandle| ..)` runs on the UI thread after every native creation, for
  icons or native styles through `WindowHandle::with_raw_handle`.
- `AppSpec::min_size` sets the smallest window (None keeps 420×400).
- `AppHandle::set_dock_icon(bool)` switches macOS between the regular and accessory activation
  policies at runtime.
- `App::standard_menus()` (macOS) adds the items every Mac app has: Edit with Undo ⌘Z, Redo ⇧⌘Z,
  Cut, Copy, Paste and Select All, and Window with Minimize ⌘M and Close ⌘W, all sent to the first
  responder. A regular app whose menu bar is still winit's default gets them without asking. An
  accessory app's menu bar is hidden, but its key equivalents still work, so AppKit windows in the
  process (an open panel, an updater) get copy, paste, select-all and close back. In a Rune window
  the keys still reach fields and `on_key` first; an untaken ⌘W or ⌘M closes or minimizes as the
  title-bar button would. It never adds Quit. Details in `src/shortcuts/README.md` under native
  menus.
- Reopening (macOS): a click on the Dock icon, or opening the app again from Finder, Spotlight or
  `open` while it runs, brings back a window when none shows, as in other Mac apps. Rune shows
  and activates a minimized window, else the window it hid last (closed with `keep_running`, or
  `hide`), else the main window, and unhides an app hidden with ⌘H. Windows that already show stay
  as they are; the activation that comes with the reopen brings them forward. It never brings back
  a launcher or other nonactivating panel, an overlay, a window that closed for good, or anything
  in an accessory app (`accessory()`,
  or `set_dock_icon(false)` at the time). `App::on_reopen(|s, has_visible_windows, tx| -> bool)`
  runs first, on the main thread with the app's state; returning true skips the default. Every
  window's hook runs, and `has_visible_windows` counts only windows reopening could bring back.
  The default looks again after the hooks, so a window a hook opened counts as showing.
  Rune adds `applicationShouldHandleReopen:hasVisibleWindows:` to winit's app delegate, which
  lacks it. An app that installs its own reopen Apple event handler replaces AppKit's, which is
  what asks the delegate, so Rune's reopening never runs; use `on_reopen` instead. Other platforms
  have no reopen, so the hook never runs there. Headless scripts send it with `{"reopen": true}`.
- Links opened with the app (macOS): `App::on_open_url(|s, url: &str, tx| ..)` runs on the main
  thread for each `myapp://...` link the system hands the app (`open`, a browser, another app),
  including the one that launched it. winit 0.30 doesn't forward them, so Rune installs a
  get-URL Apple event handler before the event loop starts and keeps links until a window whose
  app has the hook starts; that link then runs before the window's first frame. If no window has
  the hook, the handler is removed once launch is over, and an app that installed its own handler
  before `run` keeps it. Each link runs as an `AppHandle::update`, in arrival order, so its
  changes commit and redraw, and later ones wake the loop. With several windows whose apps have
  the hook (`run_windows`, `App::window`), the first still running receives links. The string is
  passed through untouched: it comes from anyone who can run `open`, so parse and validate it
  before acting. Rune doesn't bring a window forward; call `AppHandle::open()` if the app should.
  Rune doesn't bundle apps, so the app's `Info.plist` declares the scheme:

  ```xml
  <key>CFBundleURLTypes</key>
  <array>
    <dict>
      <key>CFBundleURLName</key>
      <string>com.example.myapp</string>
      <key>CFBundleURLSchemes</key>
      <array><string>myapp</string></array>
    </dict>
  </array>
  ```

  Launch Services learns the scheme when the bundle is opened or registered (`lsregister -f
  MyApp.app`); then `open 'myapp://x'` launches or reaches the app. A bare `cargo run` binary has
  no bundle and gets no links. iOS isn't wired yet (winit owns the scene delegate), and Linux
  passes a link to a new process as a launch argument, so the hook never runs there.
- Links and relaunches on Windows: Windows starts a new process for each launch, passing a link
  as an argument. The hook receives the links among the first process's arguments
  (`scheme://…`) like the launching link on macOS. Call `rune::single_instance("com.example.myapp")`
  first thing in `main` to keep one process: a later launch hands its arguments to the running
  process over a per-user named pipe and lets it take the foreground, and `single_instance`
  returns false so `main` returns without opening a window. Its links reach the hook; a launch
  without links reopens the app (`App::on_reopen`, then the default, which also brings the front
  window forward, restored). Register the scheme for the user, usually at install:
  `HKEY_CURRENT_USER\Software\Classes\myapp` with an empty `URL Protocol` value and
  `shell\open\command` set to `"C:\path\to\myapp.exe" "%1"`.
  `scripts/mac-app --scheme myapp` writes that entry and registers the bundle for you (see
  "Relaunching a Mac app" below).
- Edge overlays (HUDs): see `App::overlay` below.

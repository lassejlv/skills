# Platform delivery: bundles, links, signing, Linux, Windows and the web

Rune draws the app; it does not bundle, sign, install or update it. Those are
the app's distribution work. Upstream:
[relaunching a Mac app](upstream/rune/relaunching-a-mac-app.md),
[mac-app installer](upstream/scripts-mac-app.md), [rune-mac](upstream/rune-mac.md),
[app lifetime](upstream/rune/app-lifetime.md) (URL schemes, single instance),
[Linux](upstream/rune/linux.md), [web](upstream/web.md),
[rune-notify](upstream/rune-notify.md).

## macOS

- `cargo run` starts a bare binary: no bundle, so no icon, no URL links, no
  microphone or Bluetooth prompts, no remembered window frame. Anything that
  depends on a bundle is unverified until the bundle runs through `open`.
- Development bundle: from the Rune checkout,
  `scripts/mac-app --name Example --id com.example.app --exe example --bin target/release/example --icon assets/icon.icns --scheme example`
  installs `~/Applications/Example.app`, swaps it in atomically, relaunches it
  without the window blinking, waits for Rune's ready receipt and rolls back on
  failure. `MAC_APP_SIGN="Developer ID Application: …"` signs it so permission
  answers survive rebuilds; otherwise it is ad hoc.
- App side (`rune-mac`, no-ops elsewhere): `rune_mac::launch()` first in `main`,
  `remember_frame(name)` from `poll` until it returns true, `saved_size(name)`
  for `AppSpec::size`, `busy(true/false)` around work a relaunch would lose.
- URL schemes: declare `CFBundleURLTypes` in `Info.plist` (or `--scheme`), handle
  `App::on_open_url(|s, url, tx| ..)`, and parse and validate the string; anyone
  can `open` one. Rune doesn't bring a window forward for a link; call
  `AppHandle::open()` if the app should.
- Apps with their own bundle layout (helpers, frameworks; Chromium/CEF in
  `rune-browser`) write their own bundling script and still launch through
  `open` to test.
- Distribution signing and notarization: use the `sign-macos-for-github` skill
  for Developer ID, notarized DMG/ZIP and CI.
- Accessory (menu-bar) apps: `App::accessory()`, tray or status items started
  from `on_ready`.

## Windows

- `rune::single_instance("com.example.myapp")` first in `main` keeps one
  process; later launches hand their arguments (links) to it and return false.
- URL schemes are registered per user at install
  (`HKEY_CURRENT_USER\Software\Classes\myapp`).
- MSVC toolchain needs only the C++ build tools; GNU needs MinGW-w64 binutils.
- Taskbar progress, flash and jump lists: `WindowHandle::set_taskbar`,
  `flash`, `rune::jump_list`.
- Installers (MSIX, MSI, NSIS) and updates are the app's.

## Linux

- Build: `libxkbcommon-dev libwayland-dev` (or distro equivalents) in CI too.
- Run: `libxkbcommon-x11-0` for windows, a Vulkan driver (software:
  `mesa-vulkan-drivers` with `VK_ICD_FILENAMES` pointing at lavapipe).
- The `dbus` feature brings the dark-mode portal, tray, Wayland global
  shortcuts and the file chooser portal.
- Wayland destroys a closed window (no hidden toplevels); `open` recreates it.
- A link opens a new process with the link as an argument; `on_open_url` doesn't
  run there.
- Package with the distribution's tooling (deb/rpm/Flatpak/AppImage); the
  package manager owns updates.

## Web

Experimental: one WebGPU canvas (WebGL2 fallback with the `webgl` feature),
built with Rune's `scripts/web-build.sh PACKAGE --out DIR` after adding a
`wasm_bindgen(start)` entry point. Persistence must avoid `std::fs` (use
`rune::prefs`, which falls back to memory). Desktop-only features (windows,
tray, menus, file dialogs, native materials) don't exist there. Read
[web](upstream/web.md) before promising anything.

## iOS

Rune targets iOS in its plan and has iOS code paths, but treat it as
unsupported for app delivery unless the pinned rev's docs say otherwise.

## Report honestly

Name the platforms actually built, launched and exercised. Cross-compiling or a
headless render is not evidence that a bundle, installer, link handler or
permission prompt works.

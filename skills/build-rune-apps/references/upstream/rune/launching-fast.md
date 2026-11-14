> Upstream: [crates/rune/README.md § Launching fast](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#launching-fast) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Launching fast

A small app puts its first window, with content, on screen about 300 ms after `open` on Apple silicon.
The full page, with the measurement method, is "Launch fast" on the docs site (`site/src/pages.tsx`).
Staying fast afterwards is "Fast apps" (`site/src/FastApps.tsx`) and "Smooth scrolling" below;
`scripts/app-audit <repo>` greps an app for the patterns they list.

- **`rune::prewarm_gpu()` first in `main`.** On macOS it makes the adapter, device and uber pipeline on a thread
  while AppKit starts; the first window or overlay opened at launch takes them, waiting if the thread is still
  working. A second call does nothing. With no window at launch the result is dropped; a window that needs features
  the prewarmed device lacks gets a new device. Elsewhere it does nothing. The run functions call it too, but only
  once the event loop starts. It starts on the backend the app draws with by default: on macOS, Rune's own Metal
  backend (the `metal-backend` feature, on by default; an app built with `default-features = false` gets wgpu unless
  it adds the feature). An app that opts out with `App::gpu_backend(GpuBackend::Wgpu)` calls
  `rune::prewarm_gpu_on(GpuBackend::Wgpu)` instead, which chooses the backend and then starts the thread, so it
  doesn't start on the native backend and start over when `App::gpu_backend` runs; that call afterwards changes
  nothing. `RUNE_GPU_BACKEND=wgpu` or `=metal` overrides both without a rebuild. A compositor whose
  `Compositor::features` asks for more than the native backend offers (`TIMESTAMP_QUERY` and `IMMEDIATES`) draws
  with wgpu instead, every frame: log
  `rune::describe_gpu(frame.device)` once to see which backend a window got and why, or set `RUNE_GPU_LOG=1`.
- **Precompiled Metal uber shader.** `crates/rune/src/uber.metallib` is loaded through wgpu's passthrough shaders,
  skipping WGSL translation and Metal's compile (`Renderer::new` 232 ms to 85 ms on a cold shader cache). The WGSL
  path is the fallback when the adapter lacks passthrough support, when `RUNE_DISABLE_METALLIB=1`, when the
  fingerprint doesn't match or when Metal rejects the library. Rune's own Metal backend (`metal-backend`) loads
  `uber_native.metallib`, built from the MSL that backend emits (first `Renderer::new` 222 ms to 90 ms cold,
  4.0 ms to 0.9 ms warm). After editing `clip.wgsl` or `shader.wgsl`, run
  `cargo test -p rune --lib --features metal-backend precompiled_uber_metallib_is_fresh` on a Mac. If it says the MSL
  is byte-identical, paste the printed lines into `uber/metallib_hash.rs`. If it says the MSL, flags or library hash
  changed, run `scripts/precompile-metal-shaders.sh` (needs Xcode's Metal toolchain) and commit both libraries and
  `uber/metallib_hash.rs`. Effect, lighting and blur shaders and iOS aren't precompiled; binary archives would need
  wgpu support.
- **The first frame draws during window creation** on macOS for visible windows (not launcher windows or panels).
  The first view build and layout run inside creation, right after the window-created callbacks, so keep the initial
  state, `view` and `on_window` cheap.
- **Defer the rest to `on_ready`.** It runs once per native creation after the first frame is ready (for a
  launcher, while hidden). A window that isn't on screen (covered, occluded, hidden or on another Space) doesn't
  wait to draw: it runs at the first frame skipped for that, or a second after the window opens. Capture `app.handle()` and call `handle.update(|s, tx| ..)` there to start status
  items, HUDs, secondary windows, network and indexing; updates run on the UI thread even with no window showing.
  There is no state-level first-frame hook yet.
- **A launcher can wait for readiness.** With `RUNE_READY_DIR` set, the process writes
  `$RUNE_READY_DIR/<bundle id>.<pid>` (the main bundle's identifier on macOS, else the executable's name) right
  after its first `on_ready` returns, and removes it when it exits normally. It's one line of JSON,
  `{"pid":123,"bundle_id":"com.example.app","ready_ms":412,"rune":"0.1.0"}`, with `ready_ms` counted from the
  process's start; the directory is made 0700 if it's missing. A process killed outright leaves its file, so treat
  one whose PID isn't running as stale. Without the variable nothing is written.
- **Keep the first second still.** Rune animates nothing then, so every frame is the app's. Land state that
  arrives right after launch (a system setting, a first network answer) with `tx.instant()`, or don't animate it.
  One settings window's launch fade drew about 85 frames in its first second instead of 4 to 8, and drawing back to
  back while the window came on screen made macOS keep an extra window-sized drawable: 14 MB more settled
  footprint. Rune now holds a new window to two drawables until it rests, or for its first second.
- **Draw nothing when idle.** A due `wake_after` on a resting window runs `poll` first and draws only if it returns
  true, so return false when nothing changed. A custom compositor returns `animating() == true` only while it moves
  (the default is false); a still one lets its window rest too. One settings window went from 77 presents per 20 s
  idle to none, 2.45% CPU to 0.85%, and 77 MB to 70 MB.
- **Relaunch in place while developing.** `scripts/mac-app` swaps a rebuilt bundle in and starts it before the
  old process quits, so with `rune_mac::remember_frame` the new window lands over the old one (see "Relaunching a
  Mac app" below).
- **Reuse a hidden window.** `keep_running()` / `windowless()` plus `AppHandle::hide()`, `show()` and `open()`
  (or `WindowOptions::launcher_panel()` for a retained panel that reveals cached pixels) make a re-summon cost a
  show instead of a launch.
- **Measuring**: launch with `open` on a quiet Mac, interleave base and changed builds for 5 to 10 rounds, and
  report medians for window-visible and first-content times, cold and warm. Cold means deleting the app's Metal
  shader caches under `getconf DARWIN_USER_CACHE_DIR`: `com.apple.metal/<bundle id>` and
  `<bundle id>/{com.apple.metal,com.apple.metalfe,com.apple.gpuarchiver}`. Read settled memory last. Count frames
  in the first second after content. Measure idle too: redraws, presents and CPU over 20 s with the window shown
  and untouched, plus settled RSS and footprint, and count `poll` returns separately from frames.

| Median ms from `open` (loaded laptop, 5 interleaved rounds) | Before | After |
| --- | --- | --- |
| Cold shader cache, content on screen | 599 | 312 |
| Cold shader cache, window on screen | 422 | 277 |
| Warm shader cache, content on screen | 466 | 299 |
| Cold shader cache, `Renderer::new` alone (10 rounds) | 232 | 85 |

Absolute times were high because the machine was busy; the differences are what matter.

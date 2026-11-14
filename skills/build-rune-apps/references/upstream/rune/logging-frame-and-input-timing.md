> Upstream: [crates/rune/README.md § Logging frame and input timing](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#logging-frame-and-input-timing) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Logging frame and input timing

For an app's own perf log, with nothing changed about how its windows draw:

- **`App::on_frame_encoded(|f: &FrameEncoded| ..)`** (or `WindowSpec::on_frame_encoded`) runs on the UI thread
  after each frame of a desktop window. `f.outcome()` is `Drawn` (encoded, submitted and presented; the first frame
  and a hidden launcher's count), `Unchanged` (a timer's frame that drew what was on screen, so no drawable was
  taken) or `Skipped` (covered, minimised, occluded or no drawable). `f.at()` is when encoding finished,
  `f.seq()` numbers the window's reports and `f.presents_at()` is the display link's target refresh when it paced
  the frame (macOS; `None` for a frame drawn at once after the window rested, such as the first after a key
  press). Headless runs, overlays and the web don't call it.
- **`Tx::input_time()`** in an input handler is when that event arrived: the `NSEvent` timestamp on macOS, the
  moment the window took it from winit elsewhere. Events that pile up between frames keep their own times. It is
  `None` in timers, polls, updates and layout callbacks. The gap from it to the next `Drawn` frame's `at()` is the
  app's input-to-encode latency.
- **`App::on_frame_drawn(|rt: &Runtime<S>| ..)`** runs after each `Drawn` frame with the runtime as it presented
  that frame, so an app can watch its own motion in real use (`rt.elements()`, `rt.state`). **`rune::last_input()`**
  is when the thread last took an input event from the platform, stamped at dispatch: input later than the previous
  frame landed in this one.

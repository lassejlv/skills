> Upstream: [crates/rune/README.md § Recording audio (`Recorder`, `recorder/`)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#recording-audio-recorder-recorder) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Recording audio (`Recorder`, `recorder/`)

`Recorder` is a cheap-to-clone handle that records the microphone to a file, with elapsed time
and a smoothed input level to draw. It mirrors `Player`.

```rust
let rec = rune::Recorder::to_file("note.m4a"); // AAC; a .wav path records 16-bit WAV
rec.start();
// In a view, a level bar that redraws without re-running the view:
el().w(4.0).h(40.0).live_scale(&rec.live_level())
// Later:
let note = rec.stop()?; // Recording { path, duration }
let clip = rune::Player::audio(note.path);
```

- **Controls and state**: `start`, `pause`, `resume`, `stop` (returns the `Recording`) and
  `cancel` (deletes a recording in progress). `state()` is `Idle`, `Starting`, `Recording`,
  `Paused`, `Stopped`, `Interrupted(reason)` or `Failed(message)`, plus `elapsed()` (paused
  time excluded) and `level()`. Builders: `.format(RecordFormat::Wav)`, `.sample_rate(hz)`,
  `.channels(n)`. The format decides the extension (AAC writes `.m4a`, or keeps `.mp4`; WAV
  writes `.wav`), so `to_file("note.m4a").format(RecordFormat::Wav)` writes `note.wav`;
  `Recording::path` is always the file written. Dropping the last handle mid-recording stops
  it and keeps the file.
- **Levels**: `level()` is a `Level` with `peak_db()` and `rms_db()` in dBFS, and `meter()`
  mapped to 0..1 (-60 dB to 0 dB). RMS rises over 30 ms and falls over 300 ms;
  the peak falls 20 dB a second. Reads take no lock and allocate nothing. `live_level()` is a
  `Live<f32>` of `meter()` for `live_scale`, `live_opacity` and the like, so a bound meter
  redraws on its own while recording; an idle or paused recorder draws no frames.
  `set_waker` hears state changes only (start, pause, stop, interruption, failure), not
  progress; for an elapsed-time label, ask for a coarse tick with
  `tx.wake_after(Recorder::METER_INTERVAL)` while `is_recording()`.
- **Permission**: `Recorder::permission()` is `Granted`, `Denied`, `Undetermined` or
  `Restricted`, and reading it never prompts. `Recorder::request_permission(callback)` asks
  (or answers at once when already decided); the callback may run on any thread. `start`
  asks when undetermined. Starting without access ends in `Failed` with a message that says
  where to allow it; it never crashes.
- **macOS setup**: the app's Info.plist needs `NSMicrophoneUsageDescription`. macOS ends a
  bundled app that touches the microphone without it, so Rune checks first and fails to start
  with a clear message instead. Hardened-runtime apps also need the
  `com.apple.security.device.audio-input` entitlement (sandboxed apps
  `com.apple.security.device.microphone`). An unsigned or ad-hoc signed build may be denied
  without a prompt, or lose its grant when its signature changes. An unbundled binary run from
  a terminal is attributed to the terminal, which asks on its behalf.
- **Backend** (macOS): AVAudioRecorder on a thread of its own. It encodes AAC (or writes WAV),
  meters the input and finalizes the file, so Rune never touches samples. The thread polls
  its meters 30 times a second while recording. If the input device goes away or the default
  input changes mid-recording, the state becomes `Interrupted(reason)`: `stop` still returns
  what was captured, and `cancel` deletes it.
- **Headless** (`--snap`, `--frames`, `--tree`, tests): no device and no prompt. Recorders hear
  a `FakeMicrophone` (by default a 220 Hz tone that swells every 1.6 s, so a meter moves).
  Elapsed time follows the virtual clock, levels come from the fake samples in 10 ms blocks
  (independent of frame rate), and `stop` writes a real 16-bit mono WAV that `Player` opens
  (an `.m4a` path becomes `.wav`). `FakeMicrophone::sine(hz, amp)`, `silence()`,
  `samples(rate, vec)` and `wav(path)` choose the input; `.permission(p)`, `.answers(p)` and
  `.unplug_after(secs)` exercise denial and interruption. `.install()` sets it for the thread,
  or `Recorder::fake(mic)` for one recorder.
- **Other platforms** (Linux, Windows, the web): `start` ends in `Failed("recording isn't
  supported on this platform")`.

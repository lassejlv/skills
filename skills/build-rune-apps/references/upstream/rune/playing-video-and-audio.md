> Upstream: [crates/rune/README.md § Playing video and audio (`Player`, `video/`)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#playing-video-and-audio-player-video) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Playing video and audio (`Player`, `video/`)

`Player` (alias `Video`) is a cheap-to-clone handle on one clip. Video plays inside an element;
audio needs none.

```rust
let clip = rune::Player::file("capture.mov"); // or Player::url("https://…/clip.mp4")
clip.set_looping(true);
clip.play();
// In a view:
let (w, h) = clip.natural_size().unwrap_or((16, 9));
el().w(480.0).h(480.0 * h as f32 / w as f32).video(&clip, SurfaceFit::Fit)

let tap = rune::Player::audio("sounds/tap.m4a"); // a path or an https URL
tap.play();
```

- **Controls and state**: `play` (from the start after `Ended`), `pause`, `seek` (clamped),
  `set_rate`, `set_looping`, `set_muted`, `set_volume`; `state()` is `Loading`, `Ready`, `Playing`, `Ended`
  or `Failed(message)`, plus `time()`, `duration()`, `natural_size()` and `has_sound()`
  (whether the clip has a sound track it can play, as a page's controls grey their mute
  button without one; `None` until the clip's facts are read).
- **Sound**: `Player::file`/`url`/`new` make videos, which start muted. `Player::audio` makes
  an audio clip, which starts unmuted. `set_muted` changes either.
- **Request headers**: `Player::request(url).header("Authorization", token).audio()` (or
  `.video()`) opens a URL with HTTP headers on every request, for media behind
  authentication. Header values never appear in `Debug` output.
- **Video frames** (macOS): AVPlayer + AVPlayerItemVideoOutput hand IOSurface-backed buffers
  to the element's `NativeSurface` for each display-link target, without a copy. Frames are
  requested only while a drawn video plays or seeks; paused, ended and off-screen videos draw
  nothing. `play` and state changes re-run views that read the state.
- **Decoders**: before its first `play`, a video shows a poster decoded on a worker thread
  (at most 1920 px a side) and holds no player. Paused players are parked: the four most
  recent keep their AVPlayer for a quick resume, and older ones are released (a video keeps
  its last frame; resuming recreates the player). Dropping the last handle and every element
  showing the clip frees the player, on the main thread. A grid of paused or unplayed clips
  holds at most four decoders.
- **Audio**: no surface, no frames and no redraws. Edits apply at once on the main thread. A
  20 Hz main-queue tick runs only while a clip plays, loads to play or seeks, to catch the end,
  loops and load failures. In a window, audio clips read their duration on a worker when
  created, so tiles can show it before they play. For a progress bar, read `time()` (live on the main thread)
  from the app's own frames: hand the clip the `setup` waker so `poll` hears it load, end or
  fail, and while it plays ask for a coarse tick with `tx.wake_after(Duration::from_millis(33))`.
  Nothing ticks when nothing plays. `examples/video-player` does this for an audio file.
- **Formats**: whatever AVFoundation reads: mp4/mov (H.264, HEVC), mp3, m4a/AAC, wav, aiff,
  flac. Audio in Ogg (Vorbis, Opus), WebM or Matroska (`.ogg`, `.oga`, `.opus`, `.webm`,
  `.mka`, `.mkv`, or a URL without an extension whose bytes are Ogg or WebM), which
  AVFoundation can't read, is decoded in Rust (symphonia, opuscule; the default `ogg-audio`
  feature) to a temporary WAV that AVPlayer plays, with the same API. The WAV takes about
  11 MB a minute, and a clip over about 6 hours fails. Video in
  those containers, and that audio with the feature off, fails at once with a clear message. A
  clip whose item never becomes ready fails after 30 s.
- **Headless** (`--snap`, `--frames`, `--tree`): no player and never any sound. A video
  decodes the frame at its virtual time synchronously (snapped to the middle of the frame), so
  output is deterministic. Its time starts on the first frame that draws it after `play`,
  advances by the runtime clock times `rate`, and ends (holding the last frame) or loops. An
  audio clip opens synchronously on the first read of its state, duration or time. Its time
  follows the virtual clock of the runtime on the thread that made it, as a video's does
  (pause, seek, rate, loop, and the end, which wakes the clip's waker), with no sound. `--tree` adds a `video` object (`kind`, `state`, `time`,
  `duration`, `size`, `rate`, `looping`, `muted`, `error`) to video elements.
- **Windows**: Media Foundation's source reader decodes each clip on a thread of its own, with
  the GPU's decoder (DXVA, through a D3D11 device on the adapter Rune draws with) where it has
  one and in software otherwise. The source resolves while that device comes up. Each picture
  is copied on the GPU into a small ring of shared NV12 textures, made as pictures need them (a
  paused clip makes one), that Rune's D3D12 device samples in place, ordered by fences, with the
  draw's bind group kept per texture: no CPU copy, and
  the UI thread only swaps the picture for the refresh the frame presents at (read from DWM's
  timing). A playing clip asks for the next frame when its next picture is due, not every
  refresh. A clip nobody draws stops decoding (its queue fills); a muted one picks up at its
  picture when drawn again, and after 3 s undrawn its decoder lets go of everything but the
  picture on screen. Loops seek back while the last pictures still wait, so there's no gap.
  Sound plays on the default output through WASAPI, following the playback clock. Media
  Foundation, D3D11 and WASAPI load on the first clip, through `GetProcAddress`: nothing at
  launch, nothing in the import table. Formats are what Media Foundation reads: mp4/mov/m4v
  (H.264; HEVC, VP9 and AV1 with their system extensions), WebM, mp3, m4a/AAC, wav, flac. A
  Windows N edition without the Media Feature Pack fails every clip with a message saying so.
  `RUNE_VIDEO_LOG=1` prints each open's steps in microseconds (`frames` adds every picture);
  `RUNE_VIDEO_DECODE=software` skips the GPU decoder. Request headers aren't sent on Windows
  yet: such a clip fails with a message.
- **Other platforms**: every clip reports `Failed("video playback isn't supported on this
  platform yet")` (or the audio equivalent), and video draws a neutral grey placeholder.

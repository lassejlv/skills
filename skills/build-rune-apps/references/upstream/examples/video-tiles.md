> Upstream: [examples/video-tiles/README.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/examples/video-tiles/README.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# Video tiles

Four Rune nodes fed by a background producer. macOS creates synthetic NV12 IOSurfaces;
other platforms use the same shader with uploaded byte planes. `--snap` freezes frame 0.

```sh
cargo build --release -p video-tiles
target/release/video-tiles --snap tiles.png --scale 2

cargo build --profile perf -p video-tiles
target/perf/video-tiles --bench-native
```

`--bench-native` is headless: 1/4/9 independent 1080p tiles, then one 4K and one 5K
surface, all at 1:1 device-pixel scale. It uses three prefilled IOSurfaces per tile,
pushes fresh frame IDs at 60 Hz, excludes generation/readback from timing, and emits
seven measured runs after one warmup. CPU includes push/import/encode/submit; GPU is
GPU render-pass timestamp duration. A 16-byte timing readback follows each pass; no pixel
readback is timed. No window, physical display, decoder, or network is measured.

## App integration

```rust,ignore
let surface = rune::NativeSurface::new(); // keep in app state; clones share a bounded slot
surface.set_waker(waker);                 // from AppSpec::setup
surface.set_observer(Arc::new(|timing| {
    // First notification: frame_id + submitted_at (std::time::Instant).
    // Second: completed_at plus optional GPU render-pass timestamp seconds.
    // Callbacks can arrive on Rune's completion worker. Keep them short.
}));

// VideoToolbox callback, after decoding has completed:
let pixel_buffer = unsafe {
    rune::native_surface::macos::PixelBuffer::from_raw(cv_pixel_buffer.cast())?
}; // retains the borrowed CVPixelBufferRef
surface.push(pixel_buffer, frame_id)?;

// In the ordinary Rune view; dimensions are points (960x540 at 2x is 1920x1080):
el().w(960.0).h(540.0).radius(12.0)
    .native_surface(&surface, rune::SurfaceFit::Fit)
```

The buffer's pixels and attachments must remain immutable until all Rune/GPU ownership
ends. Request IOSurface-backed, Metal-compatible output from VideoToolbox. There is no
CPU pixel lock, copy, or upload in the import path. `push` is thread-safe and replaces
the pending frame; only the newest is imported at render preparation. Repeated rendering
of the same source is cached. `clear()` removes the frame and wakes the app.

Import failures (e.g. a non-IOSurface pixel buffer) appear in `surface.last_error()`;
unsupported formats/colour metadata are rejected by `push`. On non-macOS, `push_bytes`
accepts packed BGRA or two packed NV12 planes. The native `PixelBuffer` API is macOS-only.

## Camera preview

Ask `AVCaptureVideoDataOutput` for IOSurface-backed, Metal-compatible BGRA or `420v`
buffers (`kCVPixelBufferMetalCompatibilityKey`), and `push` each one from its sample-buffer
delegate. Then:

```rust,ignore
surface.set_mirrored(front_camera); // draw-time flip; captured stills stay unmirrored
el().w(480.0).h(480.0).radius(24.0)
    .native_surface(&surface, rune::SurfaceFit::Fill) // aspect-fill, centred crop
```

Mirroring flips about the image centre, so a Fill crop stays centred, and 1:1 pixels stay
exact. Changing it wakes the app and redraws the current frame. When the preview window
hides, stop the capture session and call `clear()`: a hidden window draws nothing, but
each `push` still wakes the app.

## Colour, sampling, ownership and timing

- BGRA, NV12 `420v` (16..235 luma / 16..240 chroma) and `420f` (full range).
- YCbCr BT.601/BT.709 matrix and sRGB/BT.709 transfer come from CoreVideo attachments.
  Missing matrix defaults to BT.601 for <=576-line sources, BT.709 otherwise; missing
  transfer defaults to BT.709 for NV12, sRGB for BGRA. Output is linear RGB into Rune's
  sRGB target. Unsupported matrix/transfer metadata is an error. SDR only; wide-gamut
  primary conversion, HDR, interlacing, clean-aperture cropping, rotation and explicit
  chroma-siting metadata are not implemented. BGRA alpha is treated as straight alpha.
- Fit letterboxes; Fill crops. Matching pixel size snaps the image origin to device
  pixels and uses `textureLoad`: no luma/BGRA interpolation at 1:1, including Retina.
  NV12's native 2x2 chroma samples are preserved at 1:1. Other scales use bilinear
  sampling with an area grid up to 8x8 taps for shrinking. Beyond 8x shrink this is
  an approximation, not a full-resolution area integral. Rounded corners, inherited
  rectangular soft clips, node opacity and painter order apply to the video.
- Each imported plane owns its `CVMetalTexture` **and** pixel buffer through a wgpu-hal
  drop callback. wgpu retains these resources through in-flight submissions, even if
  a new frame arrives, the node disappears, or an encoder is abandoned. Decoder pool
  buffers cannot be recycled merely because the pending slot changed.
- `counts()` returns draw submissions/completions, not unique decoded frames; dropped
  pending frames generate no submit notification. A source frame can be submitted more
  than once. `timing()` holds the newest submission only; the observer receives both
  events for every draw. `submitted_at` is sampled immediately before submit setup;
  `completed_at` is when completion was observed, while `gpu_start_seconds/gpu_end_seconds`
  come from hardware render-pass queries (the containing UI pass, when embedded in Rune).
  Their difference is GPU duration; the GPU epoch is backend-specific. Do not subtract
   them from `Instant`. Backends without timestamp queries still report completion.
   An explicit query set passed to `Renderer::draw_timed` takes precedence; that draw's
   NativeSurface notifications carry CPU submit/completion times only.
    `Frame::draw_ui`, `Renderer::draw`, and `draw_range` interleave prepared video at its
    `before_instance` position, including inside isolated groups. A custom compositor must
    preserve those absolute insertion indices when concatenating or rearranging lists and
    call `encode_layers` before opening its render pass. Prepared but undrawn video generates
    no submission notification.
   A coalesced completion worker uses nonblocking polls, sleeping between them, including
   for the final frame at idle. It never holds wgpu's device lock while waiting on a GPU
   fence. Counter resolution runs in a separate submission after render completion to
   avoid stale Metal counter samples; the second notification follows its 16-byte readback.
   Completion time is captured before that readback, but includes callback latency; it is not an exact Metal
  command-buffer completion timestamp. wgpu 30 rejects `as_hal_mut` after normal render
  encoding, so its raw completed-handler hook cannot be used here. A tested prototype
  hit that validation error and was removed. No backend fork or untracked raw submission.
- True **presented-frame** timestamps require Rune's own Mac shell owning CAMetalLayer /
  CAMetalDisplayLink (planned, not built). wgpu-hal 30 exposes the render layer and raw
  command buffer but keeps the acquired drawable private. There is no cheap, supported
  presented-handler hook to prototype without owning that shell. GPU-done is not present.

Verification: `cargo test -p rune native_surface -- --test-threads=1`.
The GPU test compares native IOSurface and byte-upload results with a scalar colour oracle,
checks exact one-pixel patterns, fitting/clipping, notifications, and released backing ownership.
The overlap test acquires the same exclusive device lock as presentation while GPU work
is still in flight, without creating a window.

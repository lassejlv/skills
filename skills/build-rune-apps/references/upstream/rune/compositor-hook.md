> Upstream: [crates/rune/README.md § Compositor hook (lighting and effects)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#compositor-hook-lighting-and-effects) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Compositor hook (lighting and effects)

![lab](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/lab/flashlight.png)

`rune::run_with(spec, compositor)` (or `App::compositor`) hands each frame to a `Compositor`
(`compose.rs`) after `Runtime::frame` has built it; `rune::run` never builds one, so the default path
and its goldens are unchanged. `examples/lab` uses it to composite `rune-light` and `rune-fx` live.

- `El::mark(u32)` tags an element's instances, and its descendants' until one sets its own.
  While a compositor is attached, `Runtime::marks` runs parallel to `Runtime::instances` (no marks
  are recorded otherwise). The lab encodes canvas, lighting material and effect node in the mark.
- The `Frame` gives the device, queue, encoder, target view and format, `dt`, the time
  `Runtime::frame` took (`update_ms`), the runtime (instances, marks, clock `t`, pointer, state,
  `presented(key)` → drawn rect and effective opacity), and Rune's `Renderer`.
- `Renderer::prepare_lists` uploads several instance lists in one buffer (one glyph upload) and
  returns their ranges; `encode_layers` records isolated groups before the containing pass;
  `draw_range` draws complete scopes into that pass; `add_format` builds the uber
  pipeline for another target format (e.g. an `Rgba16Float` scene, a text mask or a node layer).
  `Frame::draw_ui` is the default frame.
- Custom compositors **must call `encode_layers`** before opening passes that use `draw_range`.
  Keep each balanced scope together: partitioning by primitive kind (for example extracting
  glyphs) breaks isolation. `draw_range` now also draws native surfaces in painter order;
  do not draw those surfaces again separately.
- `Compositor::animating` keeps the display link running while something moves on its own;
  `features` requests device features (e.g. `TIMESTAMP_QUERY`) when the adapter has them;
  `summary` prints after a headless run.
- Headless tooling (`--snap`, `--script`, `--trace`, strips) runs through the same compositor.
- `.srgb_blend(true)` works with a compositor. `Frame::srgb_blend()` and `Frame::format` say which
  encoding and view the frame uses; every pass, isolated layers included, holds premultiplied
  values in that encoding. Build pipelines for the format a pass is given (`EffectSite::format`),
  and encode a shader's colour when `srgb_blend` is set. Everything the uber shader draws already
  matches.
- **Effect slots.** `effect(mark)` / `El::effect(mark)` is a box that draws nothing (it covers no
  pixels) but keeps its place in the painter stream, with its rect, rounded clip and soft edges,
  inside whatever isolated layer encloses it. A faded slot (its own or an ancestor's opacity, or
  `dim`) always gets a layer, so its opacity applies to whatever the compositor paints there.
  `El::effect_bleed(pt)` grows that layer's bounds for a glow's reach, and keeps a slot whose rect
  is just out of view but whose glow isn't. `El::effect_backdrop(true)` marks a slot that reads what
  was drawn before it (`instance.params[0] = 1.0`).
  `Renderer::draw_with`, `Renderer::draw_with_backdrop`, `Renderer::draw_target_range_with`,
  `Renderer::draw_range_with(pass, format, range, hook)` and
  `Renderer::encode_layers_with(encoder, hook)` / `Renderer::encode_layers_with_backdrop` call the
  hook at each slot in painter order, so a compositor paints its pass exactly there: in the frame
  target for a slot outside any layer, in the layer's offscreen target (`Rgba16Float`) for one
  inside, where the layer's opacity, blur, dissolve and clip then apply to it. Ordinary slots stay
  in the open render pass; only a slot with `effect_backdrop(true)` ends the pass, copies the
  target up to that point into a pooled viewport-sized backdrop texture (`EffectSite::backdrop`, in
  the pass's own `format`, with an isolated layer's target placed at `origin` in window
  coordinates), calls `EffectPhase::Backdrop(encoder)` while the pass is closed (e.g. for
  `FxRenderer::blur_backdrop`), and re-opens the pass with `LoadOp::Load`. `EffectSite` gives the
  slot's instance, `scale` (`instance.params[3]`, device pixels per point at the slot including
  Retina scale and any `scale` / `live_scale`), the pass's format, the window position of its
  top-left pixel (`origin`, subtract it from window coordinates), its size, `in_layer`,
  `srgb_blend`, and `backdrop`. The hook runs with the scissor on the slot's clip rectangle, and the
  viewport and scissor are reset to the full target after it.
  One compositor serves any number of formats: build pipelines per `EffectSite::format`.
- **Per-slot identity and payload.** `EffectSite::mark` is the slot's `El::effect` tag and
  `EffectSite::data` its `El::effect_data([f32; 4])` payload, both carried in the slot's record, so
  a compositor needs neither `Runtime::marks` nor its own copy of app state. A removed element keeps
  its last-built payload through its exit transition, so an outgoing slot keeps drawing its own
  content while its replacement enters beside it. Keep resources per mark and drop a mark's once a
  frame passes without it (the example on `compose::Compositor`). The slot's rect and `scale`
  follow `El::scale`, `El::offset` and a transition's scale and offset; under `El::rotate` the slot
  stays upright inside a turned isolated layer, and Rune turns what the hook painted.
- `render::CLIP_WGSL` is Rune's own clip maths as WGSL (`clip_alpha(p, clip, fade)` with `p` in
  window pixels, plus `sd_rounded`). Prepend it to a compositor shader and pass the slot's `clip`
  and `fade` words (`rune-fx` does this via `FxSlot::clip(i.clip, i.fade)` in `prepare_with_slots`), so the effect is cut
  by the same rectangle, feathers and circular or continuous
  rounded corners as the primitives around it. A compositor that skips this still gets the hard
  clip rectangle from the scissor. A rounded clip on an isolated layer applies to the completed
  layer instead, so nothing extra is needed there.

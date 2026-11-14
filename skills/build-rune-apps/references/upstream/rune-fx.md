> Upstream: [crates/rune-fx/README.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-fx/README.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# rune-fx

Effect layers for Rune: glow, pulses, electricity, fire, motion blur, distortion, some extras
(shimmer, sparkles, aurora, grain), and a family of fills (liquid metal, mesh gradient, dither, grain
gradient, fluted glass, metaballs, swirl, voronoi, waves, halftone, plastic). Each effect is a WGSL fragment shader on an instanced quad with
typed params. Given (time, seed), every frame is deterministic. A layer whose intensity is 0, whose
one-shot has finished, or that is off screen is never drawn.

Build and run from the workspace root:

```sh
cargo run --release -p rune-fx --example gallery   # stills, strips, timings
cargo test -p rune-fx --lib                        # contract tests
```

`examples/lab` composites these layers live inside Rune's renderer, with knobs.

Output lands in `demo/fx/` (repo root): `<effect>.png`, `<effect>-strip.png` (8 frames),
`<effect>-reduced.png` (reduced motion), `<effect>.mp4`, `motion-quarter-speed.mp4`, `timings.md`.
`gallery --frames DIR --fps 60 --seconds 2 --effect fire [--start 0] [--reduced]` dumps a PNG sequence.

| | |
|---|---|
| ![glow](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/glow.png) | ![pulse](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/pulse.png) |
| ![electric](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/electric.png) | ![fire](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/fire.png) |
| ![motion](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/motion.png) | ![distort](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/distort.png) |
| ![extras](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/extras.png) | ![liquid metal](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/liquid-metal.png) |
| ![mesh gradient](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/mesh-gradient.png) | ![dither](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/dither.png) |
| ![grain gradient](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/grain-gradient.png) | ![fluted glass](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/fluted-glass.png) |
| ![more fills](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/fills.png) | ![every fill preset](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/fill-presets.png) |
| ![plastic keys, glossy and matte, and liquid metal keys anchored to the window or to each key](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/plastic.png) | ![blend modes over cream paper](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/blend.png) |

Liquid metal over eight frames (four seconds): ![liquid metal strip](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/fx/liquid-metal-strip.png)

## API

```rust
use rune_fx::*;

let card = Shape::rounded(262.0, 70.0, 156.0, 96.0, 14.0); // points
let layers = [
    Fx::glow(GlowParams { style: GlowStyle::Neon, color: rgb(0x22d3ee), heat: heat.at(t), ..Default::default() })
        .on(card).over().at(t),
    Fx::electric(ElectricParams::charged()).on(Shape::capsule(380.0, 222.0, 196.0, 50.0)).seed(3).at(t),
    Fx::lens(LensParams { second: Some(Shape::circle(lx, 116.0, 30.0)), ..Default::default() })
        .on(Shape::capsule(140.0, 84.0, 200.0, 64.0)).at(t),
];

let mut fx = FxRenderer::new(&device, target_format, FxOptions { dither: target_is_8_bit });
let stats = fx.prepare(&device, &queue, &FxFrame {
    viewport: [w, h], scale: 2.0, layers: &layers,
    backdrop: Some(&backdrop_view),        // only distortion reads it
    sources: &[&mask_pyramid.view, &node_layer_view],
});
// in the node's render pass, around the node itself:
fx.draw_layer(&mut pass, 0);              // or fx.draw_all(&mut pass, &layers, Some(Place::Under))
```

`FxLayer` builders: `.at(time)`, `.seed(n)`, `.over()` / `.under()`, `.reduced(bool)`,
`.source(slot, rect)`, `.opacity(k)` (also the pub field `opacity`, so struct
literals need it).
`layer.is_animating()` tells the frame loop whether to keep ticking; it is false for a layer that
draws nothing (zero opacity or amplitude).

For Rune effect slots, use `prepare_with_slots(device, queue, frame, slots)` with one
`FxSlot::default().scale(site.scale).clip(i.clip, i.fade)` per layer. Missing entries default
to the frame scale and no clip. Keeping this metadata separate preserves existing `FxLayer`
and `FxFrame` struct literals.

One-shots overlap: `OneShots<T>::new(cap)` keeps a bounded pool. `trigger(t, data)` starts a new
instance beside the live ones, and `live(t, life)` yields each `(shot, opacity)`. Draw one layer per
instance with `.seed(shot.seed).opacity(k)`. When the pool is full the oldest instance fades out
over `OneShots::FADE` (0.16 s) instead of being cut. Ripples, pings, shockwaves, lightning zaps
(`ElectricParams::zap: Some(t0)`, lives `ZAP_LIFE`) and sparkle bursts
(`SparkleParams::burst: Some(t0)`, lives `burst_life()`) all work this way.

Simulated fire and smoke: `fx.set_fire_sim(&device, true)` makes `Top` and `Heat` fires a small
GPU fluid simulation per layer (stable fluids at 1–3 pt cells: buoyancy, vorticity confinement,
expansion at the fuel line, cooling into smoke, monotone cubic advection) instead of noise. Call
`fx.simulate(&queue, &mut encoder, None)` after `prepare` and before drawing. Steps are fixed
1/60 s (at most 4 per frame); a new or time-jumped grid warms up 1.2 s in one frame; reduced motion
settles one pose and then steps nothing. Flames are blackbody light (1000–2700 K) with a
per-channel shoulder; `FireParams::smoke` sets how much smoke the cooling flame leaves, and smoke
covers what is behind it, lit warm from below. The lab's fire scene costs 0.8–0.9 ms GPU per frame at 2×.

Frosted glass (`LensParams::frost > 0` or `FlutedGlassParams::frost > 0`) reads a blurred backdrop.
After copying the backdrop (or in `EffectPhase::Backdrop(encoder)` at a Rune
`El::effect_backdrop(true)` slot), call
`fx.blur_backdrop(&device, &queue, &mut encoder, &backdrop_view, layer)` for that layer (or
`fx.set_layer_backdrop(&device, &backdrop_view, layer)` for an unblurred backdrop reader when
`FxFrame::backdrop` is `None`). `blur_backdrop` runs a half-resolution dual-filter pyramid scissored
to the layer and binds both `backdrop_view` and the blurred output on that layer; if the layer has
`frost == 0`, it binds `backdrop_view` without running the pyramid. Without `blur_backdrop` a lens
falls back to an 8-tap spiral blur.
`Fx::cost()` returns the static cost declaration. `FxStats` reports draws, idle and off-screen
culls, covered pixels, and whether any drawn layer needs a backdrop.

Time helpers:
- `Phase` keeps an effect's phase continuous when you animate its speed: `set_speed(t, s)`
  adjusts an offset so `at(t)` never jumps.
- `Heat` gives a light with attack and exponential cooling. Feed it to `GlowParams::heat` and the
  glow shrinks, deepens and dims instead of cutting off (see the neon card in `glow-strip.png`).
- `MotionSamples::from_track(params, rest_rect, t, scale, |t| Pose)` samples the analytic track
  inside the shutter interval.

### Fills

A fill paints the node's shape (or, with `.border(w)`, a band `w` pt wide inside its edge) and
goes under the node as its background. Every style is `Fx::fill(params)` with typed params,
`Default` and named presets:

```rust
Fx::fill(LiquidMetalParams::gold()).on(Shape::capsule(x, y, 180.0, 52.0)).at(t)          // a gold pill
Fx::fill(LiquidMetalParams::chrome().border(6.0)).on(card).at(t)                        // a chrome tube border
Fx::fill(LiquidMetalParams::chrome().anchor(FillAnchor::Element)).on(key).at(t)          // every key ripples alike
Fx::fill(PlasticParams { color: rgb(0xd7263d), roughness: 0.7, dome: -0.4, ..PlasticParams::glossy() }).on(key) // a matte dished keycap
Fx::fill(MeshGradientParams { colors: Stops::hex(&[0x1b1f3b, 0xff6f91, 0xffc75f]), ..MeshGradientParams::dusk() }).on(card).at(t)
Fx::fill(DitherParams { pattern: DitherPattern::Bayer8, pixel: 3.0, ..DitherParams::backdrop() }).on(card).at(t) // over the backdrop
Fx::fill(GrainGradientParams { kind: GradientKind::Conic, ..GrainGradientParams::sweep() }).on(card).at(t)
Fx::fill(FlutedGlassParams { rib: 10.0, frost: 0.4, ..FlutedGlassParams::reeded() }).on(card).at(t)
```

- Shared parts: a shape mask with an optional border band, `intensity`, a colour list (`Stops`, up
  to six, blended in OKLab) and, for dither and halftone, a tone input (`FillInput`: linear or
  radial ramp, drifting noise, the backdrop, or an image in a source slot via `.source(1, rect)`).
- Fills that read the backdrop (fluted glass, dither or halftone of `Backdrop`) go over instead
  and need a backdrop copy, like distortion. Frosted fluted glass reads the same blur pyramid as a
  frosted lens: call `fx.blur_backdrop` for the layer.
- Reduced motion: each fill settles on one fixed pose (drift, flow and grain stop) and
  `is_animating()` is false.
- The catalog describes every style for tools: `fill_styles()` lists `StyleInfo { id, name,
  summary, params, presets, reads_backdrop }`; each `Param` has an id (the Rust field), a display
  name and a `ParamKind` (number with range, step and unit; count; toggle; choice; colour; colours;
  point; points). `FillParams::COMMON` holds `border` and `intensity`. `FillParams::get`/`set`
  read and write any param by id as a `Value`, and `to_rust()` writes the `Fx::fill(...)` call,
  as a struct literal over the closest preset.

## Integration contract (for the Rune renderer)

**Inputs per layer**
- Node shape in points: a rounded rect, capsule or circle (`Shape`), or a mask texture plus the
  rect it covers (`Source`).
- Time from Rune's clock, so slow-mo, pause and stepping work and goldens stay deterministic. One-shots
  (ping, ripple, shockwave) take a `t0` on the same clock.
- Seed.
- Params.
- `reduced_motion`.
- Optional:
  - an analytic track (motion blur);
  - the backdrop texture (distortion: a copy of the target taken right before the layer, which
    must not be the render target);
  - a source texture (mask glow and mask shimmer use a `MaskPyramid`; motion blur uses the node
    rendered at rest with at least 2 px of transparent margin).

**Output**
- A premultiplied, linear-light colour layer, drawn with `PREMULTIPLIED_ALPHA_BLENDING` over or
  under the node (`Place`).
- Light effects (glow, pulses, electricity, fire) write `rgb > a`, so they add light like a screen
  blend on dark UI. `occlusion` controls how much they also cover what's behind.
- Distortion and motion blur write replacement pixels with `a = 1` inside their mask.

**Targets and blend modes**
- One `FxRenderer` draws into any number of target formats: `add_format` adds another one, and `draw_layer_in(pass, format, origin, layer)` draws into a pass of that format
  whose top-left pixel is at `origin` in window pixels (a Rune effect slot's `EffectSite`: the
  frame target, or an isolated layer's `Rgba16Float` target, where the layer's opacity, blur and
  clip then apply). Effects are still shaded in window coordinates; pass `FxSlot::scale(site.scale)`
  so a zoomed slot (`scale` / `live_scale`) converts its device-pixel rect and lengths with its own
  device-px-per-pt factor, and `FxSlot::clip(i.clip, i.fade)` in `prepare_with_slots` so a slot outside an isolated layer
  is cut by rounded container corners and soft scroll-edge feathers (`CLIP_WGSL`).
- Each effect family's pipeline for a format and blend is built the first time a frame draws
  it (those one `prepare` needs build in parallel), so a renderer pays only for what it shows.
  On a cold Metal shader cache that's 20 to 150 ms per pipeline.
- `FxSlot::blend(FxBlend)` selects how a slot composites onto the target beneath it:
  `FxBlend::Normal` (default premultiplied source-over with additive light), `FxBlend::Multiply`,
  `FxBlend::Screen`, `FxBlend::Overlay`, or `FxBlend::SoftLight`. `Screen` uses
  fixed-function `wgpu::BlendState` (zero backdrop reads); `Multiply`, `Overlay` and `SoftLight` sample the
  backdrop (`FxFrame::backdrop` or `EffectSite::backdrop` via `set_layer_backdrop` /
  `blur_backdrop`, setting `FxStats::needs_backdrop`) and fall back to `Normal` when no backdrop
  is bound. Separable formulas run in the frame's working colour space (linear light by default, or
  sRGB when `set_srgb_blend(true)` is active). Overlay and SoftLight have little contrast near
  white by definition; use Multiply for a strong coloured halo on light surfaces.
- `set_srgb_blend(frame.srgb_blend())` matches a gamma-blended Rune frame: the premultiplied output
  is sRGB-encoded for the non-sRGB target. When prepared without `FxFrame::backdrop`, per-slot
  `backdrop` / `blurred` samples default to that same encoding and are decoded before shading.
  Pass a backdrop view of the pass's own format
  (`EffectSite::backdrop`: non-sRGB on the frame target, `Rgba16Float` inside an isolated layer);
  glass, lenses, distortion and backdrop dither/halftone then shade in linear light without
  double-encoding on either target. Explicit `FxFrame::backdrop` inputs retain the linear-samples
  default. `FxSlot::backdrop_srgb(bool)` overrides either convention: use `false` for an `*Srgb`
  view (hardware already decodes it) or a linear `Rgba16Float` view, and `true` for encoded
  premultiplied samples, independently of the frame's output blend mode.

**Cost and culling**
- `prepare` does all culling: idle layers (intensity 0, a fully cooled glow, a one-shot outside its
  window) and layers whose bounds miss the viewport get no instance, no CPU tables and no draw.
- Motion blur at rest has `count == 1`. The renderer should then skip the layer
  (`!samples.is_moving()`) and draw the node normally.
- Each layer is one quad clipped to its bounds, in one pass.
- Distortion adds the backdrop copy: scissor it to the union of the distortion bounds.
- Mask glow adds a mip build once per mask change (6 small passes).

**Per-frame CPU tables**
- Anything that is a 1D function of (time, seed), or a particle list, is evaluated once per frame
  into the `data` storage buffer instead of once per pixel: bolt paths and their blurred halo paths,
  energy crawl, forks, embers, sparkles, aurora curtains, and motion poses.
- They use the same integer hash as the shaders, so there is no `sin`-hash and results don't vary
  by GPU.
- This cut electricity from 9.6 ms to about 0.5–1 ms for a full 1200×800 px quad.

**Reduced motion**
- Every effect has a calm fallback with no travel:
  - Looping noise effects (electricity, fire, haze, aurora) freeze on a fixed, pleasant pose.
    Forks, embers and flicker stop.
  - Radar becomes a static halo, breathing holds still, and heartbeat holds a steady glow.
  - Ping fades its destination in and out without travelling. Ripple and shockwave become a short,
    soft brightening.
  - Shimmer becomes a gentle opacity breath. Motion blur turns off.
  - Glow cooling stays, because it's a fade, not travel.
- See `<effect>-reduced.png`.

**Quality**
- Dither:
  - The gallery renders into Rgba16Float and dithers once at the resolve (TPDF, ±1 LSB, static per
    pixel, so there's no temporal shimmer).
  - For 8-bit targets, set `FxOptions::dither` and each effect dithers its own output in sRGB
    space, gated to where there is signal.
- Edges:
  - Every light falls off analytically and is windowed inside its bounds, so no quad edge ever
    shows.
  - Overlays (aurora, grain, shimmer) feather inside the node shape.
  - Glass and the CRT anti-alias their edges at 1 px.

## Effects and params

Lengths are in points, times in seconds.

| Effect | Variants | Key params (default) | Notes |
|---|---|---|---|
| **Glow** `GlowParams` | `Soft`, `Neon` (white-hot hairline rim, bloom both sides), `Aura` (3-colour spectrum flowing round the perimeter, inner rim light), `Mask` (text/icon bloom from a `MaskPyramid`) | radius 14, intensity 1, inner 0, occlusion .15, breathe 0, breathe_period 2.6, heat 1, hot .6, aura_speed .12, rim_width .6, reach 4.5 | Bloom = tight Gaussian (0.35 r) + wide Gaussian (1.2 r), so the light is gone by about 2.5 r, through a soft knee (`1 − e^−x`) that keeps the hue instead of clipping to white. `heat` cools the light. Mask glow samples fractional mip levels with tent taps, so an animated radius never steps |
| **Pulse** `PulseParams` | `Radar`, `Breathe`, `Heartbeat`, `Ping{from,dir,travel}`, `Ripple{at}` | count 3, period 2.4, reach 36, width 1.6, t0, duration .75, repeat 0, lag .16, head_radius 2.6 | Rings follow the shape's SDF. The ping winds up against its travel (Bézier P1 = −0.12), shoots, decelerates to zero velocity, then blooms and cools. Ripple `reach: 0` = auto (farthest corner) |
| **Electric** `ElectricParams` | `Arc{a,b}`, `Border`, `Charged` (`ElectricParams::charged()`) | amplitude 5, frequency 2.4 cells/100pt, speed 3.2, core_width .6, glow 5, forks .55, flicker .45, strands 2, gap 2, fork_len 20, zap None | Lightning: a midpoint-displacement bolt (CPU tables) that strikes with a flash, holds, sometimes return-strokes, and re-strikes every ~0.55/speed s, mostly down the same channel. Extra strands are the last two strikes' afterimages (≈70 ms decay). Forks branch off at each strike, shoot out in 35 ms, then cool white → tint → violet and die within 70–200 ms. Narrow halo along a blurred copy of the path. Arc bounds cover the bolt's full reach. `Charged` keeps a calm crawling hairline |
| **Fire** `FireParams` | `Top`, `Border`, `Heat` (`FireParams::heat()`), `Embers`; `FireParams::plasma()` | height 54, scale 20, speed 1.5, embers 16, ember_rise 58, ember_size .8, ember_life 1.5, warp 1, sides .32, base_glow .5, swirl 0 | Flames: domain-warped fbm (warp grows with height) in height-normalised density, so tongues rise and narrow. Per-column flicker (slow + ~8 Hz). Temperature ramp from a white-yellow base through orange and deep red to a faint smoke veil. Plasma is a thin band hugging the outside of the edge, with ridged filaments that breathe (3 noise evaluations). Embers are flung up, slow under drag (`EMBER_DRAG` 2.4/s) to a buoyant drift, sway, and cool exponentially. Heat haze only distorts above the flame |
| **Motion blur** `MotionBlurParams` + `MotionSamples` | `Shutter` (exact sub-frame poses), `Directional` (taps along the velocity) | shutter_angle 180, frame_dt 1/60, max_samples 48, px_per_sample 1.25, smooth_shutter true | Sample count = travel px / 1.25, so it's 1 at rest. Raised-cosine shutter weights give soft trail ends. Poses include rotation, scale and opacity |
| **Distort** `DistortParams` | `HeatHaze`, `Shockwave`, `Lens(LensParams)`, `Crt`, `ChromaSplit` | lens: bevel 14, depth 16, dispersion .14, magnification 1.04, presence 1, frost 0, shadow .35, rim 1.6, union_k 22, morph 0, `second: Option<Shape>` | Lens uses psychopomp's thin-surface optics: a superellipse bevel (power 3) bends light by `tan(θ − asin(sin θ / 1.5))`. Per-channel spread splits colour at the rim, a soft blur covers the squeezed rim, and it adds sky fresnel, a specular line on the lit arc, a counter-line and a drop shadow. `presence` ramps lensing, rim and shadow together, so the glass appears by lensing, not by fading. A second shape smooth-unions into a gooey merge; `morph` lerps toward it. `frost` is Liquid Glass "regular": a wide pyramid blur (σ up to 18 pt), saturation ×(1 + 0.9 k), a compressive sRGB lift that brightens dark backdrops more than light ones, and grain against banding |
| **Shimmer** `ShimmerParams` | shape or mask (`use_mask`) | period 1.8, band 28, angle .35 rad, intensity .16, pause .3 | Skeleton loaders and "Thinking…" text sheen. The band starts and ends off the shape, so it never cuts |
| **Sparkles** `SparkleParams` | continuous or `burst: Some(t0)` | count 6, life 1.5, size 7, margin 10 | Crisp four-point stars (concave superellipse, 1 px AA) with a white-hot centre. Sizes skew small with a few large. Each pops in with overshoot, twinkles at its own 5–9 Hz, spins slowly and shrinks away; continuous stars rest between appearances so only a few are lit. A burst flings every star out once |
| **Aurora** `AuroraParams` | – | scale 120, speed .25, intensity .5, feather 40 | 3 curtains from CPU tables, plus noise rays |
| **Grain** `GrainParams` | static or animated (`fps`) | amount .03, fps 0 | Static by default (no temporal shimmer) |

Fills (`Fx::fill`; every style also takes `border` and `intensity`):

| Fill | Presets | Key params (default) | Notes |
|---|---|---|---|
| **Liquid metal** `LiquidMetalParams` | `chrome`, `gold`, `rose`, `gunmetal` | flow .6, scale 100, speed .35, bevel 14, dome .55, angle −.12, iridescence .08, contrast 1 | A studio reflected in polished metal: bright sky falling to a hard horizon over a dark floor, an overhead soft box and two strip lights. The face is domed so the horizon crosses it, the rim rolls off over `bevel`, and a domain-warped height field ripples the normal (calmer toward the rim). Conductor Fresnel (Schlick) goes from the tint to white at grazing angles; lights roll off through a per-channel shoulder. As a border it is a round tube. `anchor` pins the ripples to the window (`World`, the default: neighbouring shapes show neighbouring parts of one surface) or to each shape's centre (`Element`: shapes of the same size, seed and time are pixel-identical, so a row of keys matches) |
| **Mesh gradient** `MeshGradientParams` | `dusk`, `lagoon`, `orchid`, `graphite` | 3–6 colours, points, drift .12, speed .25, sharpness 1.6, warp .35 | Each colour owns a point that drifts on a slow CPU-side path; inverse-distance weights blend them in OKLab, then the output is dithered against banding |
| **Dither** `DitherParams` | `bayer`, `handheld`, `grain`, `backdrop` | Bayer 2×2 / 4×4 / 8×8, blue noise (32×32 void-and-cluster tile), white noise; pixel 2, 2–6 colours, bias, contrast | Quantises a tone (ramp, noise, backdrop or image) into the palette in square pixels anchored to the shape |
| **Grain gradient** `GrainGradientParams` | `ember`, `halo`, `sweep` | linear / radial / conic, amount .4, size .5, mono, fps 12 | Triangular noise scatters the ramp position, so colours stipple into each other, plus brightness grain (mono or per channel). Conic gradients loop |
| **Fluted glass** `FlutedGlassParams` | `reeded`, `fine`, `frosted`, `wide` | rib 14, angle 0, refraction 9, frost 0, dispersion .15, highlight .5 | Each rib is a cylindrical lens: the strip under it comes back squeezed and flipped, with a per-channel split toward its edges, a sheen and a shaded groove |
| **Metaballs** `MetaballParams` | `lava`, `mint` | count 6, size .2, speed .4, gloss .5 | Blobs on CPU paths summed as a field; the iso-edge is anti-aliased from the field's slope, with a glossy rim |
| **Swirl** `SwirlParams` | `ink`, `marble` | scale 140, speed .2, twist .6, warp 1 | A centre twist over twice domain-warped noise, through the colour ramp |
| **Voronoi** `VoronoiParams` | `cells`, `stained` | scale 36, speed .25, edge 1.5, edge_color, depth .4 | Orbiting cell points, exact seam distance to the bisectors, shaded cells |
| **Waves** `WaveParams` | `sea`, `dunes` | amplitude .05, frequency 1.6, speed .4, angle 0, softness .006 | Layered bands with two-sine crests; each front band shades the one behind |
| **Halftone** `HalftoneParams` | `print`, `backdrop` | cell 6, angle 45°, ink, base; input as dither | Round dots on a rotated screen sized by tone; the four nearest dots merge |
| **Plastic** `PlasticParams` | `glossy`, `matte`, `dished` | colour, roughness .15, dome .35, bevel 6, angle −.5 | Moulded plastic under one soft light from `angle` (50° up), with liquid metal's dome and rolled rim. Diffuse shading (ambient plus Lambert) keeps `color` on a flat face, darkens slopes facing away and lightens toward white facing the light; a GGX highlight is small and bright when glossy, broad and faint when matte; Schlick Fresnel (f0 .04) adds a faint sky at grazing angles. Highlight and Fresnel fill the room left above the base, so rgb never exceeds alpha and it blends the same with `srgb_blend` on or off. Negative `dome` dishes the face like a keycap. Never animates |

## Costs

From `demo/fx/timings.md`: Apple M5 Max (shared with other jobs). One layer covers a
600×400 pt region at 2× (1200×800 = 960k px, smaller where noted). GPU time per draw is the median
over 10 draws per timestamped pass. "reads" = texture taps plus CPU-table reads per pixel; "noise" =
gradient-noise evaluations per pixel. "was" is the previous effects on the same machine (median of
three runs each).

| effect | px | reads | noise | backdrop | ms | was |
|---|---:|---:|---:|:-:|---:|---:|
| glow soft / neon | 960k | 0 | 0 | | 0.10 / 0.11 | 0.10 / 0.12 |
| glow aura | 960k | 0 | 1 | | 0.21 | 0.21 |
| glow mask (text) | 960k | 13 | 0 | | 0.23 | 0.22 |
| pulse radar / breathe / heartbeat | 960k | 0 | 0 | | 0.16 / 0.07 / 0.17 | 0.21 / 0.09 / 0.09 |
| pulse ripple | 544k | 0 | 0 | | 0.05 | 0.06 |
| electric arc (3 strands) / border / charged | 960k | 37 / 43 / 37 | 0 | | 0.39 / 0.38 / 0.24 | 0.43 / 0.28 / 0.23 |
| fire top + 16 embers / plasma border / heat | 644k / 960k / 635k | 32 / 0 / 8 | 8 / 3 / 8 | | 1.32 / 0.51 / 0.74 | 1.19 / 1.00 / 0.78 |
| distort heat haze | 960k | 1 | 6 | yes | 0.68 | 0.70 |
| distort shockwave / CRT / chroma split | 960k | 3 / 7 / 3 | 0 | yes | 0.09 / 0.11 / 0.06 | 0.10 / 0.13 / 0.06 |
| distort lens / lens + frost | 960k | 12 | 0 | yes | 0.21 / 0.40 | 0.21 / 0.44 |
| shimmer / grain | 960k | 0 | 0 | | 0.09 / 0.08 | 0.08 / 0.08 |
| sparkles ×9 / aurora | 960k | 18 / 12 | 0 / 3 | | 0.18 / 0.48 | 0.36 / 0.49 |
| motion shutter (48 poses) / directional (32 taps) | 467k | 48 / 32 | 0 | | 0.66 / 0.50 | 0.64 / 0.60 |

Deltas: the heartbeat doubles (four overlapping beat instances instead of one) and the electric
border costs about 0.1 ms more (sharper fractal paths keep more of the near-field slope
correction). Flames cost about 10% more for the height-normalised warp. Plasma halves (3 noise
evaluations instead of 8) and sparkles halve (stars outside their own radius are skipped). The frost
pyramid adds a half-resolution blur scissored to the lens (in the lab, lens-frost measures
0.7 ms per whole frame against 0.5–0.6 ms for the clear lens). Every row stays within the old budgets.

Fills were measured on an Apple M4 Pro (headless Metal), where the rows above run about twice as
long as on the M5 Max (glow soft 0.21 ms, lens 0.37 ms, fire top 1.8 ms; `demo/fx/timings.md` now
holds that run). Each fill covers a 480×280 pt rounded rect at 2× (544k px):

| fill | reads | noise | backdrop | ms |
|---|---:|---:|:-:|---:|
| liquid metal / still (flow 0) / 8 pt border | 0 | 8 / 0 / 8 | | 0.93 / 0.22 / 0.17 |
| liquid metal, element anchor | 0 | 8 | | 0.94 (world in the same run: 0.95) |
| plastic glossy / matte / 8 pt border | 0 | 0 | | 0.15 / 0.15 / 0.06 |
| mesh gradient (5 colours) | 10 | 2 | | 0.37 |
| dither Bayer ramp / blue noise / palette over noise / backdrop | 1 / 2 / 1 / 2 | 0 / 0 / 3 / 0 | backdrop only | 0.15 / 0.15 / 0.45 / 0.16 |
| grain gradient linear mono / conic colour | 2 | 0 | | 0.18 / 0.26 |
| fluted glass / + frost | 3 / 6 | 0 | yes | 0.12 / 0.25 |
| metaballs ×6 / waves (5 bands) | 12 / 5 | 0 | | 0.28 / 0.29 |
| swirl / voronoi | 2 / 1 | 9 / 0 | | 1.05 / 1.17 |
| halftone radial / backdrop | 0 / 4 | 0 | backdrop only | 0.31 / 0.34 |

Liquid metal's cost is the flowing surface (eight noise evaluations for the height field and its
slope); a still slab costs a quarter, and a border pays only for its band. The element anchor
costs nothing extra. Plastic is a still slab with a highlight: about a sixth of flowing liquid metal. Swirl and voronoi are
the heaviest per pixel; keep them to cards rather than full screens.

These are worst-case full-region numbers. Real layers hug their node: the gallery's 224 pt card
with flames and embers covers about 195k px (about 0.4 ms), and a charged 196×50 button border
about 115k px (about 0.05 ms).
Timings on a shared machine vary by about 1.5× between runs, so read them as relative costs. A
reserved machine is needed for gating.

## Gaps and next steps

- **Glow from mask** needs the caller to render the mask into `MaskPyramid::levels[0]` and call
  `build_mips`. Rune should cache the pyramid per text run.
- **Backdrop** slots (`El::effect_backdrop(true)`) split the pass in `Renderer::draw_with_backdrop`
  and copy the target up to each slot into a pooled viewport-sized backdrop texture (`EffectSite::backdrop`),
  which `blur_backdrop` / `set_layer_backdrop` binds for that layer. A future optimisation could copy
  only the scissored reach of the slot rather than the full target.
- **Motion blur** composites a cached node layer. Rune needs to render the moving subtree into that
  layer, and should skip the effect at rest.
- **Fire** is the heaviest per pixel (8 noise evaluations). Half-resolution evaluation with a
  bilateral upsample would cut it about 3×. Not done.
- Electricity forks grow and cool but don't sub-branch.
- The frost pyramid needs one `blur_backdrop` call per frosted layer (about 10 per frame fit the
  uniform slots). The clear lens's rim blur is still an 8-tap spiral.
- Bind groups are rebuilt every `prepare`. They should be cached per (backdrop, source) pair.
- Fills have no inspector UI of their own: the catalog (`fill_styles()`) is the data a tool needs
  to build one. Image input for dither and halftone needs the caller to bind the image as a source.
- No CPU reference renderer or golden tests for the shaders yet; the CPU-table and contract tests
  live in `src/lib.rs`.

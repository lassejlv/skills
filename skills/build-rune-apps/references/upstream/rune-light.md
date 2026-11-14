> Upstream: [crates/rune-light/README.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-light/README.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# rune-light

Real-time lighting for Rune UIs. You place a light and the UI casts soft shadows from it, catches it on bevelled
edges and specular highlights, and glowing elements light the cards around them. It runs as passes over the frame
Rune already draws.

Every Rune element is an analytic rounded rect, so the frame is already an exact 2D distance field. rune-light
treats the elements you mark as occluders as short slabs standing on the UI plane, gives lights a 3D position
(height above the UI) and a physical source radius, and sphere traces through that field.

```rust
use rune_light::{Light, LightRenderer, Prim, Scene, Settings};

let lamp = Light::point(x, y, 58.0 * s)          // device px; z = height above the UI
    .color([1.0, 0.58, 0.27]).intensity(2.1)     // linear colour; 1.0 = irradiance 1 at 200 px
    .radius(11.0 * s)                            // source size → penumbra width and highlight size
    .range(900.0 * s)                            // windowed inverse square
    .bulb(0.9);                                  // show the source as a soft bloom

let bubble = Prim::from_rune(inst.rect, inst.radii)
    .raised(7.0 * s)                             // casts shadows
    .bevel(6.0 * s, 2.0 * s)                     // SDF bevel → normals → rim light and highlights
    .gloss(0.55, 0.42);

let mut lights = LightRenderer::new(&device, &queue, w, h, surface_format);
let drew = lights.render(&device, &queue, &mut encoder,
    &Scene { prims: &prims, lights: &[lamp], settings: Settings::default() },
    &ui_without_text, &text_layer, &target);
// drew == false → no lights and no emitters: nothing was recorded; present the UI as usual.
```

Run the demos, the benchmark and the CPU check (headless, offscreen; outputs land in `demo/light/`):

```sh
cargo build --release -p rune-light --example light
target/release/examples/light all        # chat, flashlight, emissive, raised, godrays: PNG, strip, MP4
target/release/examples/light verify     # GPU shadow texels vs. CPU estimator and brute-force ground truth
```

The benchmark (GPU timestamps per pass → `demo/light/bench.json`) needs the perf profile:

```sh
cargo build --profile perf -p rune-light --example light
target/perf/examples/light bench
```

`examples/reel/` renders a radiance-cascades reel that steps through the real GI buffers
(`reel render`, `reel stills T1,T2`, `reel bench`; outputs land in `demo/reel/`).

`examples/live.rs` puts the flashlight and chat demos in a window (`cargo run --release -p rune-light --example live`;
`live --snap out.png` renders one frame headless).

## Integration contract

**Inputs, per frame**

| Input | Form | Notes |
|---|---|---|
| Primitives | `&[Prim]`, device px, in draw order | Rune's instance rect and radii plus `z` (bottom, top, bevel width, bevel height), `gloss`/`roughness`, flags `OCCLUDER` / `EMISSIVE` / `RAISED`, emitted radiance, albedo. Painter's order decides which surface owns a pixel. |
| Lights | `&[Light]`, up to 8 | position + height, linear colour × intensity, source radius, range, optional torch cone (`spot`), `shafts`, `bulb`, `specular`, `softness`. Animate any field with Rune springs; fade a light out with `scaled(k)` (lights cool, never cut). |
| UI colour | `base`: the frame without text (linear, filterable; Rgba16Float works) | Used as albedo. |
| Text | `text`: glyphs only, premultiplied linear, transparent elsewhere | Lit like the surface beneath, clamped by `TextPolicy { floor, ceiling }`, so shadows never crush it and highlights never wash it out. `lit: 0` leaves text unlit. |
| Settings | ambient, exposure, `TextPolicy`, `Option<Gi>`, contact AO, rim, background gloss, `time`, `seed` | |

**Output:** the lit frame in `target`. If the target format isn't sRGB, the composite encodes sRGB itself and adds
±1 LSB interleaved-gradient dither (a fixed per-pixel pattern, so nothing crawls between frames).

**Guarantees**

- Deterministic: output is a pure function of the inputs, `time` and `seed`. There's no history, jitter or
  accumulation, so frames never shimmer and a replay is exact.
- Zero cost with no lights and no emitters: `render` returns `false` and records no passes.
- Text contrast: text never drops below `floor` × its design colour, whatever the shadows do.
- Reduced motion: lights shouldn't travel. Cross-fade between positions with two `Light`s and `scaled(k)` over
  0.15–0.2 s. The demos script motion with Rune `Track`s (springs sampled at absolute time).

**Rune integration (next step, not done here):** `Runtime` would mark nodes as occluders/emitters (a `light`
modifier on `El`), split glyph instances into their own target (it already knows `KIND_GLYPH`), and call `render`
between the uber pass and present. The demos do exactly this by hand with Rune's own `Renderer` and `TextSystem`.

## Techniques and why

| Pass | Res | Technique | Why |
|---|---|---|---|
| Surface | full | Instanced quads; the topmost primitive writes its own SDF, outward gradient, top z and id | Exact per-pixel bevel normals and receiver height, no texture SDF error at edges |
| Field | ½ | Brute-force union SDF of occluders, box-distance early-out, plus nearest slab z range and a GI distance | Exact for rounded rects, no jump flood needed. JFA would only be needed for arbitrary shapes (text, vectors) |
| Soft shadows | ½ | Sphere tracing the slab field from each receiver to the light, Quílez penumbra with Aaltonen's closest-approach fix, clearance measured against the cone to a spherical source (`0.5 + 0.5·h/(t·θ)`, smoothstep, as in an earlier lighting prototype's capsule shadows) | Physically sized penumbrae that harden toward contact for free; early exit once the ray clears the tallest card |
| Upsample | full | Joint bilateral on receiver height | Shadows never bleed from the floor onto a card top |
| Shading | full | Lambert + GGX (viewer overhead) with Karis sphere-light widening, a rim hairline on edges facing the light, contact AO from the field, an earlier lighting prototype's windowed inverse square and torch beam profile | Cards read as raised; highlights sweep; the torch has a hot core and spill, not a flat disc |
| God rays | ½ | A light behind the UI: each pixel integrates the light's glow, masked by the field (prefiltered to the sample spacing), along its path to the light (Mitchell, GPU Gems 3), plus distance falloff | Shafts through every gap and no banding, with the same field |
| GI | ⅛ | 2D radiance cascades: 5 cascades, 4·4ⁿ directions, Sannikov's bilinear fix, emitters glow, cards absorb only rays from lower probes (light reaches a card from things standing on it), one bounce from direct light on cards. The media are built from the analytic primitives with box-filtered sub-texel coverage and sampled bilinearly, so an emitter moving by a fraction of a texel changes the light by that fraction (no popping). Rays skip empty space using the distance to emitters and to the occluder boundary | Every emitter lights its neighbours with soft occlusion at a cost fixed by the grid, not the emitter count |
| Extra emission | ⅛ | An optional output-resolution emission texture (effect layers such as rune-fx electric arcs) enters the GI as glowing medium; `Prim::gi_hint` rects tell the tracer where it can be | Effects light the UI too |
| Glass | full | `GlassRenderer`: thick slabs over the lit frame. Snell refraction in and out (n = 1.5), exact unpolarised Fresnel, total internal reflection off the bottom face, Beer–Lambert tint, 8-wavelength dispersion from a Cauchy fit, frost from a 13-tap prefiltered pyramid read at the refracted cone's footprint, GGX highlights from emissive elements with normal-variance specular AA, GI fluence scattered into the bevel, smooth-union morphs | Glass that reads as glass: the UI bends at the rim, fringes in colour and mirrors at grazing angles |

Prior art reused from an earlier lighting prototype:

- `packages/kit/gpu/shadows/capsule-shadows.ts:508-527` (cone-relative soft visibility),
- `packages/kit/gpu/lights/physical.ts:142-163` (windowed inverse square, Karis widening),
- `packages/kit/gpu/lights/beam.ts:71-83` (torch profile),
- `packages/kit/gpu/gi/plan-bounce.ts:345-399` (cone gather, which radiance cascades generalise),
- `docs/rendering-techniques.md:396` (radiance cascades plan: pull-cord-lamp, GM Shaders),
- the blog's `flashlight.wgsl` (interleaved-gradient noise, light that reveals content without punching a hole).

## GPU cost

Measured on an Apple M5 Max (under other load) at 1280×800 pt × 2 = 2560×1600 device px, with 100 raised,
bevelled occluders. Compute passes are timed with wgpu timestamp queries (medians of 60 frames). Render-pass
timestamps aren't ordered against compute on tile GPUs, so the whole frame is also measured as the wall clock of
120 back-to-back frames with no readback. That's GPU-bound and an upper bound that includes submission
(`light bench` → `demo/light/bench.json`):

| Config | Field | Shadows | GI | Whole lighting frame |
|---|---|---|---|---|
| 1 light | 0.16 | 0.17 | n/a | 0.94 |
| **4 lights** | **0.07** | **0.31** | n/a | **1.04** |
| 8 lights | 0.06 | 0.57 | n/a | 1.65 |
| 4 lights, all with god rays | 0.06 | 1.38 | n/a | 2.20 |
| GI only (11 emitters) | 0.07 | 0.02 | 2.27 | 2.69 |
| 4 lights + GI bounce | 0.06 | 0.30 | 2.49 | 3.44 |

All times in ms. The fast path (field + soft shadows for 4 lights) costs about 0.4 ms. The remaining ~0.6 ms of the
1 ms frame is the full-resolution surface buffer and composite at 4 Mpx. The soft-shadow cost scales with lights
× half-res pixels, and rays stop early once they clear the tallest card. God rays cost ~0.27 ms per shaft light
(48 masked samples). GI costs ~2.3 ms at ⅛ resolution (320×200 probes, 5 cascades with the bilinear fix), and
that cost doesn't change with the number of emitters. It's for hero moments, not every frame of every screen.

The field pass is exact. Distances are clamped to 128 px, which is further than any tracer step, so each 16×16 tile
culls primitives into workgroup memory first. That took it from 1.3 ms (brute force) to 0.07 ms.

## Verification

`light verify` reads back the GPU visibility texture over a 64×40 grid and compares it with the CPU estimator over
the exact analytic field (`src/cpu.rs`). The mean difference is 0.0002. The worst texel is off by 0.48, on a
penumbra boundary where the half-res bilinear field and the exact field disagree by a fraction of a pixel. The
check also compares against brute-force ground truth (400 rays across the source's disc, exact 3D slab SDF): in the
116 penumbra texels the mean error is 0.06 and the worst is 0.35. That worst case is the known bias of the
Quílez/Aaltonen estimator where the ray grazes two occluders. It's never wrong in umbra or full light.

## Gaps

- GI uses the same field but no history, so it's deterministic. Small, very bright emitters can still ring faintly.
- Occluders are slabs of rounded rects. Text, icons and vector paths don't cast shadows yet. That needs a
  jump-flood field over their coverage.
- Nested occluders: the field keeps the nearest slab's z range, so a raised button on a raised card shadows as
  the nearer of the two.
- `examples/light.rs` drives `crates/rune` and `crates/rune-light` directly; `examples/lab` drives the lights from a
  live `rune::Runtime` through the compositor hook (marked elements become occluders).
- `LightRenderer::inspect()` exposes every intermediate GI buffer (field, media, each cascade merged and, with
  `inspect = true`, unmerged) and `Timings` has per-cascade GPU times; `examples/reel/` visualises them.
- GI is 2–3 ms for sparse layouts and more for dense ones: the bilinear fix traces four rays per direction, and C3's
  rays cross many card edges where the field is small (`reel bench`). Halving the cascade-0 directions, or temporal
  amortisation (which breaks strict determinism), are
  the next levers.
- The surface buffer is a second full-resolution raster of the primitives. Rune's uber pass could write it as an
  extra target for free.

> Upstream: [crates/rune/README.md § Frosted panels](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#frosted-panels) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Frosted panels

Which blur a frosted panel needs depends on what sits behind it:

- **The desktop or other windows:** `El::system_material` above, in a transparent window. Only
  the platform can see behind the window.
- **The app's own content:** `El::backdrop_blur` below. (`El::blur(σ)` blurs the element's own
  subtree, not its backdrop.) For refraction, a saturation lift and grain on top of the blur,
  `rune-fx`'s `Fx::lens(LensParams { frost: 1.0, .. })` is Liquid Glass "regular": put
  `.effect_backdrop(true)` on its effect slot and draw through `Renderer::draw_with_backdrop`,
  calling `FxRenderer::blur_backdrop` on `EffectPhase::Backdrop(encoder)` with `site.backdrop`;
  `examples/lab/src/gfx.rs` and the rune-fx README cover the calls.
- **No blur:** a translucent `fill` over the content is the cheap stand-in, and what
  `system_material` draws in opaque windows and headless renders.

> Upstream: [crates/rune-kit/README.md § Comparison (lavapipe vs headless Chromium, 2×)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-kit/README.md#comparison-lavapipe-vs-headless-chromium-2) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

## Comparison (lavapipe vs headless Chromium, 2×)

Side by sides (web | Rune | amplified difference): [button states](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/side-ui-button--all-states-light.png),
[rich menu](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/side-ui-menu--rich-dark.png), [grouped select](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/side-ui-select--grouped-light.png),
[text inputs](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/side-ui-text-input--states-light.png), [toast](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/side-ui-toast--all-examples-light.png),
[card](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/side-components-card--warning-dark.png). Run `scripts/kit-diff.py` for
current per-story scores.

Known differences, and why:

- **Glyph advances.** Chromium on Linux rounds each glyph advance to a device pixel (no subpixel
  positioning); Rune keeps Parley's fractional advances and rounds text boxes up to a device pixel.
  Words differ by up to ~0.5 pt, which adds up along wrapped rows (button variants).
- **Antialiasing.** Rune's greyscale atlas with luminance dilation vs Chromium's FreeType/Skia
  rasteriser: stems differ by a fraction of a pixel; diff images show text outlines.
- **Blending.** Rune blends in linear light; translucent tokens are re-solved per backdrop
  (`Kit::on`), exact over the surface they were solved for and close elsewhere. CSS group opacity
  (disabled controls) is per-layer opacity in Rune, so text over a dimmed fill is slightly lighter.
- **Focus.** Controls support keyboard focus rings, Tab, activation and arrow-key roving.
  Dialog traps focus and restores the opener; popover/select opening autofocus is still separate.
- **Motion.** Spinner pulses use fixed seeds in the web's randomized timing ranges; Loader rotates
  every 900 ms. Both use Rune's clock and hold a static pose under reduced motion. Indeterminate
  progress remains static. Transitions use springs rather than CSS easing curves.
- **Not drawn.** The textarea resize grip, hover-card trigger underline, scrollbars.
- **Story quirks mirrored on purpose.** Solid ignores `defaultValue` on the v2 inputs (the web shows
  placeholders), the Basic and NonCollapsible accordions render closed, and the menu Rich story's
  `settings`/`save`/`print` icons fall back to `plus`. `components-popover--inline` and the
  context-menu, tabs and avatar stories have no gallery scene yet. `ui-dialog--basic` and the
  scripted `motion-focus-modal` scene cover the new modal layer.

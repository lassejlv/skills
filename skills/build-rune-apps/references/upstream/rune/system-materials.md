> Upstream: [crates/rune/README.md § System materials (`El::system_material`, `system_material/`)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#system-materials-elsystem_material-system_material) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### System materials (`El::system_material`, `system_material/`)

```rust,ignore
col().radius(28.0).shadow(18.0, 44.0, black.alpha(0.35))
    .system_material(SystemMaterial::Glass)
    .motion(Spring::new(0.7, 0.22))
    .child(content)
```

The platform blurs whatever is behind the window under the element's rounded rect. On macOS in
a transparent window, `Glass` is Liquid Glass (`NSGlassEffectView`) on macOS 26 and later and the
popover material before; `Popover` is `NSVisualEffectView`'s popover material, behind window.
Each is a native view under the Metal layer that takes no clicks, with its frame, corner radius
and opacity set in the same Core Animation transaction as the frame's drawable. So the material
keeps up with springs, Rune's shadow and the content drawn on it. Native views take one corner
radius, the largest corner clamped to half the shorter side. They sit under everything the
window draws and ignore ancestor clips, and a window gets at most `MAX_NATIVE_MATERIALS`; later
elements draw the fallback.

Rune draws the shadow, so make the window larger than the card and turn the system shadow off
with `MacWindowOptions::default().shadow(false)`, or the window gets a second, rectangular
shadow. An outer shadow under a material leaves the material's interior clear.

Opaque windows, other platforms and headless renders draw the element's fill instead, or a
neutral tint when it has none; native views never appear in offscreen output, so goldens stay
deterministic. `RUNE_SYSTEM_MATERIAL=legacy` forces the pre-26 view, `unsynced` moves the views
outside the drawable's transaction (for comparison) and `off` draws the fallback.
`examples/glass-card` flies a card over a test pattern; research note 26 has the measurements.

To match a native AppKit card on top of the material, three more opt-ins:

- `.srgb_blend(true)` on the `App`, `WindowSpec` or `ConfiguredOverlay` blends in sRGB-encoded
  space, as Core Animation does, so a 62% frost over the glass reads as the same CALayer would.
- `El::continuous_corners()` gives the element, its clip and its material Apple's continuous
  curve. Glass always has it, since `NSGlassEffectView` draws no other.
- `Shadow::core_animation(x, y, radius, color)` takes a CALayer `shadowRadius` and sets
  `blur` to twice it.

For panels, `ConfiguredOverlay::macos_level` and `OverlayHandle::set_macos_level` set the
AppKit window level, and `OverlayHandle::fade_in` and `fade_out` fade the window's alpha.
`examples/glass-panel` puts it together: a card that flies across a large window, hands off
to a card-sized window that moves 60 times a second, and fades out.

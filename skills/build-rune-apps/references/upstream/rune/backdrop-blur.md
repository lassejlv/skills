> Upstream: [crates/rune/README.md § Backdrop blur (`El::backdrop_blur`)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#backdrop-blur-elbackdrop_blur) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Backdrop blur (`El::backdrop_blur`)

```rust,ignore
col().pin(Some(0.0), None, Some(0.0), Some(0.0)).h(60.0)
    .backdrop_blur(8.0)
    .fill(Color::WHITE.alpha(0.45))
    .child(tabs)
```

The element blurs what the window has already drawn behind it, inside its rounded or continuous
corners and its clip, then draws its fill over the blur as a tint, and its border and children
on top. Sigma is in points, as in CSS `backdrop-filter: blur()`. It works through plain
`rune::run` and in headless renders, which are deterministic.

At the element the renderer ends the pass, copies the target, blurs the copy with a dual-filter
pyramid at half resolution (13 taps down, 9 up, `Rgba16Float`), and reopens the pass to draw the
blur through the element's corner mask. Every pyramid level is cut to the element's rect plus
three sigma, and each tap is clamped to that region, so nothing outside it leaks in and the
window's edges don't darken. Scrolling, springs and opacity behave as for any paint: the blur
follows the element's presented rect, its opacity fades the blur, and its outer shadows leave the
blurred interior clear. A still frame doesn't redraw.

A frame blurs at most `MAX_BACKDROP_BLURS` (4) elements; later ones draw only their fill. So do
blurs drawn into a target without `COPY_SRC`, or into a caller's own `wgpu::RenderPass` through
`Renderer::draw_range`. The web backend asks the canvas for `COPY_SRC`. Inside an ancestor
drawn as one layer (`El::group_opacity`, `El::blur`, `El::cache`, a rotation) the backdrop is
what that layer has drawn so far, as in CSS. A frame without a blurred element runs the same
passes as before and draws the same pixels. `examples/frosted-bar` scrolls a list under a
frosted bottom bar.

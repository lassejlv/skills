# Paper designs rendered with Rune

Paper (paper.design) stores HTML/CSS-like frames. Rune draws in points with
flexbox, so most of a frame maps one to one; the differences are colour space,
fonts, shadows and what the design leaves implicit. Rune Browser, for example,
was built from a Paper file this way.

## Extract first

With the Paper MCP server connected: load its guide, then for the exact frame
read `get_basic_info`, `get_tree_summary`, `get_computed_styles` (exact values;
never measure screenshots), `get_jsx` for structure, `get_font_family_info`,
`get_fill_image` for raster assets, and `get_screenshot` at 2x as the reference.
Export SVG icons as Rune `Icon` bodies. If Paper isn't reachable, say so and
continue only with work that doesn't need the design; don't invent it.

## Map the values

| Paper / CSS | Rune |
| --- | --- |
| `px` sizes, gaps, padding, radius | the same numbers in points: `.w`, `.h`, `.gap`, `.padding`, `.px`, `.radius` |
| `display: flex; flex-direction: row/column` | `row()` / `col()` |
| `justify-content`, `align-items` | `.justify_between/center/end/…`, `.items_center/start/end/stretch`, `.center()`, `.center_y()` |
| `flex: 1` | `.grow(1.0)` plus a bounded ancestor and `.min_h(0.0)`/`.min_w(..)` where content would overflow |
| `position: absolute; left; top` | `.absolute(x, y)` |
| `#rrggbb`, `rgba()` | `rune::color::hex("#rrggbbaa")`: Rune colours are linear, Paper's are sRGB |
| `opacity` | `.opacity(..)` |
| `border: 1px solid` | `.border(1.0, color)`; a hairline at 2x is `1.0 / cx.env().scale` |
| `box-shadow: x y blur spread color [inset]` | `.box_shadow(Shadow { x, y, blur, spread, color, inset })`; CSS blur maps directly |
| `font-size`, `font-weight` | `TextStyle::new(size, weight)` |
| `line-height: Npx` | `.lh(N)` |
| `letter-spacing: Npx` | `.tracking(N)` (points); convert `em` × font size |
| `font-family` | embed the face in `AppSpec::fonts`, name it in `families` or `Family::Named` |
| `font-feature-settings` | `.features("'tnum' 1")` |
| `linear-gradient(angle, stops)` | `.linear_gradient(radians, stops)`; CSS angles, 0 is up |
| `overflow: hidden` + radius | `.clip_rounded(radius)` |
| SVG icon | `Icon { name, view, body }` with `currentColor`, drawn by `icon(&ICON, size)` |
| Image fill | `ImageCache` (made in `setup`) and `.pixels(..)` |

Put the palette in one typed struct per appearance (light and dark), built from
the hex values with `color::hex`, and name tokens for their role, not their
value. If the design has only one appearance, ask or derive the other
explicitly; don't guess silently.

## States the frame doesn't show

Hover, pressed, focus, disabled, selected, empty, loading, error, long text,
narrow window. Use `.hover(..)` styles, focus rings and scenes for each, and say
which were designed and which were inferred.

## Compare

Render at the frame's logical size and 2x:

```sh
$APP --snap out/frame.png --scene <scene> --size <W>x<H> --scale 2 --theme light
$APP --tree out/frame.json --scene <scene> --size <W>x<H>
```

Read both images side by side, check `--tree` rects against Paper's computed
layout for the main blocks, and fix differences in geometry, then type, then
colour. Text rasterises differently from a browser (CoreText-like weight on
macOS); small differences in glyph weight are expected, positions and sizes are
not.

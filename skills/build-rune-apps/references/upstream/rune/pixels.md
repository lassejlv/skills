> Upstream: [crates/rune/README.md § Pixels (`pixels.rs`)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#pixels-pixelsrs) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Pixels (`pixels.rs`)

`rune::Pixels` is a cloneable, thread-safe RGBA image a producer replaces with
`set(width, height, rgba)` (straight-alpha sRGB). `El::pixels(&pixels)` draws it scaled
into the element's rect, clipped to its corner radius, without re-running the view when the
image changes. Like a `Live` value, `set` (from any thread) wakes only the windows and overlays
whose scene shows the image; sets between frames coalesce into one wake and one upload, and a
hidden or covered window catches up when it shows again. Images live in stable per-runtime 1024² RGBA pages (`Rgba8UnormSrgb`, binding 2,
instance kind 7); larger images get exact-size standalone pages, up to 8192 pixels per axis.
Pages are created on demand and unused trailing pages are released. Rendering breaks batches
only when the image page changes, preserving painter order. Filtering is bilinear on
premultiplied texels, clamped to each image. Same-size streaming updates reuse their slot,
perform only a row copy/upload, and do no mip work or internal allocation.

For static assets, construct an `ImageCache` once with the app's setup waker:

```rust,ignore
let cache = rune::ImageCache::new(waker);
let icon = cache.load(png_bytes); // PNG, JPEG, PNG-backed ICNS, or SVG
// Keep `icon` in app state; pending images paint nothing, completion wakes the app.
el().size(32.0, 32.0).pixels(icon.pixels())
```

The cache deduplicates by content and decodes on one worker. `cache.rgba(w, h, bytes)` accepts
straight-alpha sRGB pixels. Static images get area-filtered, linear-premultiplied mip levels
on that worker; rendering chooses a precomputed level from the drawn device-pixel size.
`Image::{size,is_ready,error}` inspect completion; `Image::wait` is for deterministic headless
fixtures. Dropping all image and pixel handles releases decoded storage. Legacy ICNS codecs
are not decoded; provide decoded RGBA for those. A JPEG (or any format whose decoder reads
EXIF) is turned upright by its EXIF orientation, so a phone photo's `size()` is the size it
shows at. A codec that panics on a malformed file fails that image (`Image::error`) and the
worker goes on with the next.

SVG and gzipped SVGZ draw on every platform, web included, through resvg (the default-on `svg`
feature; about 19 small pure-Rust crates and 8 s of parallel release build). Vector images
have no pixel size, so rasterize them at the size they draw at and let the mips cover smaller
draws:

```rust,ignore
let scale = env.scale; // the window's device pixels per point
let mark = cache.svg(svg_bytes, 16.0, scale);               // fits 16 pt square, crisp at 2×
let any = cache.load_mime(bytes, "image/svg+xml", 16.0, scale); // from a data URL's MIME type
let file = cache.file("assets/logo.svg", 48.0, scale);      // read on the worker; fetched on web
let photo = cache.url("https://example.com/p.avif", 96.0, scale); // web: the browser fetches and decodes
```

`cache.file` treats `.svg` and `.svgz` paths (or SVG content) as vectors and decodes other
files like `load`. On web, `cache.file` and `cache.url` fetch the URL (relative to the page) and
let the browser decode it off the main thread, so WebP and AVIF work there; SVG still rasterizes
through resvg. On native `cache.url` takes a path or `file:` URL only: Rune has no HTTP client,
so fetch remote bytes yourself and call `load`. `cache.load` recognises SVG by its content and rasterizes it at twice its
own size. SVG text needs fonts resvg isn't given, so convert text to paths. With the feature
off, SVG images resolve to `Image::error`.

`El::pixels_fit(&pixels, SurfaceFit::Fit)` keeps the image's aspect ratio, letterboxed and
centred on whole device pixels (the corner radius rounds the image itself); `SurfaceFit::Fill`
covers the rect and crops the centred overflow, choosing the mip for the uncropped size.
In a fixed box these behave like SwiftUI's `.aspectRatio(contentMode: .fit)` and
`.aspectRatio(contentMode: .fill)` followed by `.clipped()`.

A picture that sets only one side takes the other from its image, so
`el().w(240.0).pixels(icon.pixels())` is as tall as the image's shape makes it, and
`el().w_full()` fills its parent's width. The height is 0 while the image decodes and settles
without animating when it arrives or a stream changes shape. Pictures with both sides set, or
neither, keep their box. `.aspect_ratio(16.0 / 9.0)` sets a ratio on any element (CSS
`aspect-ratio`), overriding the image's; use it for a `video` before its size is known.

`.aspect_fit(w / h)` sizes the element itself to the largest box at that ratio inside the room
its parent gives it: the free space along the parent's main axis and its whole cross side,
within `max_w` and `max_h`. A picture in a bounded cell with a caption under it fits what the
caption leaves, and the caption sits under the picture rather than under a letterbox:

```rust,ignore
col().w(cell_w).h(cell_h).center().gap(6.0)
    .child(el().aspect_fit(iw / ih).radius(8.0).pixels_fit(image.pixels(), SurfaceFit::Fill))
    .child(text(caption))
```

The ratio comes from the view (`Image::size`, `Player::natural_size`), so it works for a
`video` or a box with children too. In a column with no bounded height, `max_h` sets the room.

`cache.app_icon(path, size_pt)` rasterizes a platform icon on the same worker, keyed by path,
size and scale: Finder's icon on macOS, an executable's or `.ico`'s first icon on Windows, and
on Linux a `.desktop` entry's `Icon=` from the hicolor theme (closest size at or above, then
scalable SVG) or `pixmaps`. Paths without an icon resolve to `Image::error`, so callers keep
their own fallback. Keep the handle: the cache only shares live handles.

# libtermy from Swift (Swift SDK + Metal renderer)

Sources: https://termy.sh/docs/developer/libtermy/swift.md,
https://termy.sh/docs/developer/libtermy/swift-rendering.md

The Swift SDK lives in `sdk/swift` of the Termy repo and wraps the C ABI. It
compiles against the repo's `termy.h`, so build the SDK and libtermy from the
**same** revision. Requires macOS 13+, Swift 6.2+, and a Rust toolchain.

| Product | Use for |
| --- | --- |
| `Termy` | Terminals, sessions, frames, input encoding, events, config, search, Kitty graphics + clipboard, tmux control mode. No UI dependency. |
| `TermyAppKit` | `TerminalView` (AppKit) and `TermyTerminal` (SwiftUI): Metal rendering, IME, mouse reporting, selection, scrollback, links, Kitty graphics. |

Prefer the SDK over hand-rolled C bindings on macOS. If you must bind the C
ABI directly, see [c-abi.md](c-abi.md#binding-from-swift--go--python--c).

## Build and test

```sh
cd sdk/swift
scripts/build-libtermy.sh   # cargo-builds libtermy, stages libtermy_core.dylib in sdk/swift/lib
swift test
swift run TermyDemo
```

From the repo root: `just test-swift-sdk`. Set `TERMY_LIBRARY_PATH` to link a
libtermy staged elsewhere.

## Add to an app

The package uses linker flags SwiftPM treats as unsafe, so depend on it **by
local path, not Git URL**. A path dependency is named after its directory,
so the package name is `swift`:

```swift
.package(path: "../termy/sdk/swift"),
// target dependencies:
.product(name: "TermyAppKit", package: "swift"),
```

Ship `libtermy_core.dylib` in `Contents/Frameworks`. Its install name is
`@rpath/libtermy_core.dylib`, so add `@executable_path/../Frameworks` to the
app's runpath search paths.

## SwiftUI terminal

`TerminalView()` loads the user's Termy config, resolves the theme for the
current appearance, and starts their shell in a PTY.

```swift
import SwiftUI
import TermyAppKit

@MainActor
final class Model: ObservableObject {
    let view = try! TerminalView()
    @Published var title = "Terminal"
}

struct ContentView: View {
    @StateObject private var model = Model()

    var body: some View {
        TermyTerminal(view: model.view)
            .onTitleChange { model.title = $0 ?? "Terminal" }
            .navigationTitle(model.title)
    }
}
```

**Keep `TerminalView` in a model.** SwiftUI rebuilds `TermyTerminal` often;
the `TerminalView` owns the shell and must outlive those rebuilds. Never
create it inside `body`. (Replace `try!` with real error handling in
production.)

## Headless sessions

`TerminalSession` drains events and keeps a retained `FrameStore` current on
the main actor. A PTY session polls when the child writes output.

```swift
import Termy

@MainActor
func run() async throws {
    let session = try TerminalSession(
        size: TerminalSize(cols: 120, rows: 40),
        options: TerminalOptions(startupCommand: "make test")
    )
    defer { session.stop() }

    while !session.hasExited { try await Task.sleep(for: .milliseconds(20)) }
    session.poll()
    for row in 0..<session.frame.rows { print(session.frame.text(row: row)) }
}
```

## Display-only sessions (SSH, tmux, recordings)

Route **both** user input and protocol replies back to the program:

```swift
let session = try TerminalSession.display(size: TerminalSize(cols: 80, rows: 24))
session.terminal.onInput = { bytes in channel.write(bytes) }
session.onProtocolReply = { bytes in channel.write(bytes) }
channel.onOutput = { bytes in try? session.feed(bytes) }
```

`feed(_:)` polls after each call, so frame and state are current on return.

## Threading and lifetime

- `Terminal` is **not** thread-safe. `TerminalSession` and `TerminalView`
  confine it to the main actor. Keep it there.
- A PTY terminal runs one background thread blocked on the wake channel;
  `stop()` or deinit wakes and joins it before freeing the handle.
- Returned C buffers are copied into Swift values and freed inside the call.
- In render loops use `Terminal.updateFrame(_:)` with a `FrameStore`: it
  applies dirty spans in place and falls back to a full frame when needed.

## Metal renderer (TermyAppKit)

Pipeline:

```text
PTY output
  → libtermy parses, records damage
  → TerminalSession.poll() takes a frame update (full or dirty spans)
  → FrameStore applies it, returns a FrameChange (damage, resize, cursor, scroll)
  → TerminalView invalidates changed rows, schedules one Metal frame
  → MetalTerminalRenderer rebuilds those rows' quads, adds overlays, draws
  → CAMetalLayer presents
```

- AppKit doesn't run its display cycle for `CAMetalLayer` views, so
  `TerminalView` schedules frames itself on the main run loop in common modes
  (works during live resize and mouse tracking). Many invalidations per
  run-loop turn → one frame.
- Full update, resize, config change or display-scale change invalidates all
  rows.
- Every on-screen element is a 64-byte instanced quad (`rect`, `uv`, `color`,
  `mode`). Fragment modes: `solid` (bgs, selection, cursor, underlines, block
  geometry), `mask` (text, stroked box drawing, IME), `colorGlyph` (emoji),
  `image` (Kitty, linear filtering). Premultiplied source-over into
  `bgra8Unorm` sRGB. Without images/IME a frame is one draw call.
- Shader is compiled from source at view creation (`makeLibrary(source:)`)
  because command-line SwiftPM doesn't compile `.metal` files.

Draw order (back → front): clear to theme bg at configured opacity → cell
backgrounds (cached/row) → selection → Kitty images z < 0 → foreground
(cached/row: glyphs, underline, strikethrough, special-glyph geometry) → Kitty
images z ≥ 0 → cursor (bar; hollow block when unfocused; filled block with the
char redrawn in bg color) → IME marked text. Only bgs and fg are cached, so
cursor blink or selection drag rebuild no rows.

Glyph atlas: 2048×2048 BGRA, shelf-packed, CoreText-rasterized on first use.
Fallback via `CTFontCreateForString` (emoji, CJK). Monochrome glyphs stored
white and tinted in the shader. Rasterized at backing scale on whole pixels,
nearest filtering; moving to a different-scale display rebuilds the atlas. A
full atlas starts a new texture and rebuilds every row once.

Special glyphs come from libtermy glyph geometry
([rendering.md](rendering.md#special-glyph-geometry)): rects become solid quads
snapped per their snap rule; strokes are rasterized once per cell size into
the atlas.

Pacing: up to 3 frames in flight with a 3-buffer instance ring;
`presentsWithTransaction` so live resizes don't stretch. Kitty textures cached
by image id + generation, released when placements disappear.

Perf (Apple silicon, 2×, full 200×60 colored grid, warm atlas):

| Renderer | Main-thread CPU/frame | GPU/frame |
| --- | --- | --- |
| CoreGraphics fallback | 5.55 ms | n/a |
| Metal, all rows rebuilt | 1.17 ms | 1.19 ms |
| Metal, no rows changed | 0.10 ms | 0.80 ms |

Excludes parsing and applying updates, which dominate under heavy output.

### Backend choice

```swift
let view = try TerminalView()                       // Metal when available
let cpu  = try TerminalView(backend: .coreGraphics) // force fallback
print(view.renderingBackend)                        // .metal or .coreGraphics
```

CoreGraphics is used automatically without a Metal device or if the shader
fails to compile. `cacheDisplay(in:to:)` snapshots always go through
`draw(_:)` (CoreGraphics) on either backend.

### Known limitations

- Whole-pixel glyph placement; no subpixel positioning.
- One Unicode scalar per cell: combining marks aren't composed, ligatures
  aren't shaped.
- `background_blur` is ignored; `background_opacity` works.

`MetalRendererTests` render offscreen and check pixels (text, bgs, box
drawing, emoji, Kitty images, cursor, partial-update redraws); they skip
without a Metal device. Run with `just test-swift-sdk`.

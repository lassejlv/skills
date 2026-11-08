# @termysh/web: browser terminal

Sources: https://termy.sh/docs/developer/web.md,
https://termy.sh/docs/developer/web/options.md,
https://termy.sh/docs/developer/web/themes.md

The `@termysh` packages are **pre-1.0**: pin exact versions and test upgrades.
They run Termy's Rust engine (parser, grid, scrollback, encoders, kitty
protocols, box-drawing geometry, themes) compiled to WebAssembly.

| Package | What | Use when |
| --- | --- | --- |
| `@termysh/web` | Browser terminal: renderer, input, selection, links, images | Building something new |
| `@termysh/xterm` | xterm.js-compatible API on `@termysh/web` | Replacing `@xterm/xterm` → [web-xterm.md](web-xterm.md) |
| `@termysh/core` | Headless wasm engine, typed API | Own renderer, worker, Node/Bun, tests → [web-core.md](web-core.md) |
| `@termysh/pty` | PTYs for Node/Bun, drop-in for `node-pty` | Server runs the shell → [web-pty-and-connect.md](web-pty-and-connect.md) |

## Install and quick start

```sh
npm install @termysh/web   # or bun add / pnpm add
```

Depends on `@termysh/core`, which ships `termy.wasm`. **No stylesheet** to
import.

```html
<div id="terminal" style="height: 400px"></div>
```

```ts
import { Terminal } from '@termysh/web'

const term = new Terminal({ theme: 'tokyo-night', fontSize: 13, cursorBlink: true })
term.open(document.getElementById('terminal')!)
term.write('Hello from \x1b[1;32mTermy\x1b[0m\r\n')
term.onData((data) => console.log('send to the host:', JSON.stringify(data)))
```

## Essentials (most integration bugs)

1. **The parent needs a size.** The terminal is `width/height: 100%` of the
   element passed to `open`. No height → nothing renders. `autoFit` (default
   on) follows the parent's size.
2. **Constructor is sync, engine is async.** `write`, `resize`, `paste` etc.
   before load are queued. `await term.ready` (or `await Terminal.create(opts)`)
   before reading state: `getLine`, `cursor`, `builtinThemeIds()`.
3. **Send everything from `onData` to the host**: keys, pastes, and protocol
   replies (cursor reports, DA, color queries). `vim` etc. wait for replies.
4. **Send every `onResize` to the host** PTY; programs lay out for the PTY's
   size.
5. **`dispose()`** when done: removes the element, stops timers, frees engine
   memory. In React, in the effect cleanup.
6. **Don't parse escape sequences yourself.** Write raw bytes; use
   `onTitleChange`, `onCwdChange`, etc. for metadata.

## Loading the wasm

Default: `new URL('./termy.wasm', import.meta.url)` next to `@termysh/core`.
Vite/Next/webpack emit it automatically with caveats (see
[web-frameworks.md](web-frameworks.md)). To self-host, copy
`node_modules/@termysh/core/dist/termy.wasm` to static assets:

```ts
new Terminal({ wasm: '/assets/termy.wasm' })
// or once at startup, before creating terminals:
import { init } from '@termysh/web'
await init('/assets/termy.wasm')
```

Serve with `Content-Type: application/wasm`.

## API

```ts
const term = new Terminal(options?)  // or: await Terminal.create(options)
term.ready                           // Promise<void>; rejects with load error
term.open(parent)                    // mount; throws if already open
term.write(data, callback?)          // string | Uint8Array; callback after parse
term.writeln(data)
term.paste(text)                     // honors bracketed paste
term.input(text)                     // as if typed (fires onData)
term.resize(cols, rows)
term.fit()                           // resize to container now
term.proposeDimensions()             // { cols, rows } that would fit
term.setOptions({ fontSize: 15 })    // any option at runtime
term.setOption(key, value) / term.getOption(key)
term.focus() / term.blur() / term.hasFocus
term.clear()                         // clear scrollback, keep prompt line
term.reset()                         // full reset (RIS)
term.processExited()                 // host process ended
term.scrollLines(n) / scrollPages(n) / scrollToTop() / scrollToBottom() / scrollToLine(line)
term.select(col, line, length) / selectLines(start, end) / selectAll() / clearSelection()
term.getSelection() / hasSelection() / getSelectionPosition()
term.getLine(line) / isLineWrapped(line)
term.cols / rows / cursor / historySize / viewportY / modes / title
term.attachCustomKeyEventHandler((event) => true)  // false = terminal ignores key
term.element / textarea / cellSize
term.core                            // underlying TermyCore
term.dispose()
```

Buffer lines are **absolute**: `0` = oldest scrollback line, `historySize` =
first live-screen line. Cursor line text (after `ready`):
`term.getLine(term.historySize + term.cursor!.row)`.
(`@termysh/core` uses screen-relative lines instead.)

### Events

Each takes a listener and returns a disposable (`sub.dispose()`).

| Event | Payload | Fires on |
| --- | --- | --- |
| `onData` | `string` | Input for host: keys, paste, protocol replies |
| `onBinary` | `string` | Legacy X10 mouse reports that aren't valid UTF-8 |
| `onBytes` | `Uint8Array` | Every byte sent to the host (superset of the two above) |
| `onResize` | `{ cols, rows }` | Grid size change |
| `onTitleChange` | `string` | OSC 0/2 |
| `onBell` | | BEL |
| `onCwdChange` | `string` | OSC 7 |
| `onProgress` | `{ state, value }` | OSC 9;4 |
| `onProgramStatus` | `ProgramStatusRecord[]` | OSC 7501 |
| `onShellIntegration` | `string` | OSC 133 marks |
| `onClipboard` | `{ selection, text }` | OSC 52 write |
| `onKey` | `{ key, domEvent }` | Key produced input |
| `onScroll` | `number` | Viewport moved |
| `onRender` | `{ start, end }` | Rows repainted |
| `onSelectionChange`, `onCursorMove`, `onWriteParsed`, `onFocus`, `onBlur` | | As named |

Byte transports: use `onBytes`.

## Protocol support

xterm/VT, 256-color + truecolor; curly/dotted/dashed/double + colored
underlines; OSC 8 + plain URL detection; OSC 4/10/11/12, 7, 52, 133, 9;4,
7501; sync output (2026), bracketed paste, focus events; mouse (default,
UTF-8, SGR); kitty keyboard incl. release; kitty graphics (RGBA/RGB/PNG,
placements, z-index, animation, Unicode placeholders).

**Not yet:** sixel, iTerm2 inline images, kitty OSC 5522 clipboard, xterm.js
decorations, custom link providers, parser hooks.

## Options

All apply at runtime (font/padding changes re-measure and re-fit).

| Group | Option (default) |
| --- | --- |
| Font | `fontFamily` (JetBrains Mono, SF Mono, Menlo, … monospace), `fontSize` (14, CSS px), `fontWeight` ('normal'), `fontWeightBold` ('bold'), `lineHeight` (1), `letterSpacing` (0) |
| Colors | `theme` ('termy'), `drawBoldTextInBrightColors` (true), `minimumContrastRatio` (1 = off … 21), `allowTransparency` (false) |
| Cursor | `cursorStyle` ('block' / 'bar' / 'underline'), `cursorBlink` (false), `cursorWidth` (1), `cursorInactiveStyle` ('outline' / 'block' / 'bar' / 'underline' / 'none') |
| Layout | `cols`/`rows` (80/24, replaced by autoFit), `autoFit` (true), `padding` (0), `scrollback` (1000), `scrollbar` (true), `devicePixelRatio` (window's) |
| Rendering | `customGlyphs` (true: Termy pixel-exact box/block/sextant/Braille), `images` (true: kitty graphics) |
| Scrolling | `scrollSensitivity` (1), `fastScrollSensitivity` (5), `fastScrollModifier` ('alt'), `alternateScroll` (true), `scrollOnUserInput` (true) |
| Input | `macOptionIsMeta` (false), `macOptionClickForcesSelection` (false), `rightClickSelectsWord` (false), `altClickMovesCursor` (true), `disableStdin` (false), `ignoreBracketedPasteMode` (false), `convertEol` (false) |
| Selection/links | `wordSeparator`, `copyOnSelect` (false), `linkHandler` (opens new tab; `{ activate, hover?, leave?, allowNonHttpProtocols? }` or `null`), `linkDetection` (true) |
| Integration | `allowClipboardWrite` (false; `onClipboard` fires regardless), `bellStyle` ('none' / 'visual'), `screenReaderMode` (false), `wasm` |

- Cell size re-measures when web fonts load and on DPR change.
- `cursorStyle` is the shape after reset; apps can change it via DECSCUSR.
- Only `http`, `https`, `mailto` links activate unless
  `allowNonHttpProtocols`.
- Shift+drag selects while an app tracks the mouse. Copy/paste: Cmd+C/V on
  macOS, Ctrl+Shift+C/V elsewhere (Ctrl+C goes to the program).

## Themes

```ts
new Terminal({ theme: 'catppuccin-mocha' })                                  // bundled
new Terminal({ theme: { background: '#0b0b0f', foreground: '#e6e6e6', cursor: '#7aa2f7' } }) // full (xterm ITheme shape)
new Terminal({ theme: { extends: 'nord', cursor: '#ebcb8b', selectionBackground: '#88c0d055' } }) // overrides
term.setOptions({ theme: 'dracula' })
```

Bundled ids: `termy`, `termy-light`, `tokyo-night`, `catppuccin-mocha`,
`dracula`, `gruvbox-dark`, `nord`, `solarized-dark`, `one-dark`, `monokai`,
`material-dark`, `palenight`, `tomorrow-night`, `oceanic-next`. Ids ignore
case and separators (`'Tokyo Night'`, `tokyo_night`).

```ts
import { builtinTheme, builtinThemeIds } from '@termysh/web'
await term.ready                // required first
builtinThemeIds()
builtinTheme('tokyo-night')     // { foreground, background, cursor, ansi: [16] }
```

Keys (any CSS color): `foreground`, `background`, `cursor`, `cursorAccent`,
`selectionBackground` (alpha blends), `selectionInactiveBackground`,
`selectionForeground`, `black` … `white` (0–7), `brightBlack` …
`brightWhite` (8–15), `extendedAnsi` (16–255; missing → standard cube),
`scrollbarThumb`.

Programs can still change colors with OSC 4/10/11/12; color queries are
answered from the active theme, so light/dark detection works.

## Agents

Every docs page has a `.md` version; `/llms.txt` and `/llms-full.txt` on
termy.sh. The npm READMEs and published type declarations document every
option and method; check them for your pinned version.

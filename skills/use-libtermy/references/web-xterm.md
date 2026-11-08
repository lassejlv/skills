# Migrating from xterm.js to @termysh/xterm

Source: https://termy.sh/docs/developer/web/xterm.md

`@termysh/xterm` implements the xterm.js `Terminal` API on `@termysh/web`.
Usually only imports change.

```sh
npm uninstall @xterm/xterm @xterm/addon-fit @xterm/addon-web-links @xterm/addon-search
npm install @termysh/xterm
```

```diff
-import { Terminal } from '@xterm/xterm'
-import { FitAddon } from '@xterm/addon-fit'
-import { WebLinksAddon } from '@xterm/addon-web-links'
-import '@xterm/xterm/css/xterm.css'
+import { Terminal, FitAddon, WebLinksAddon } from '@termysh/xterm'

 const term = new Terminal({ cursorBlink: true, fontSize: 13 })
 const fit = new FitAddon()
 term.loadAddon(fit)
 term.loadAddon(new WebLinksAddon())
 term.open(container)
 fit.fit()
 term.onData((data) => socket.send(data))
```

Remove the xterm CSS import; no stylesheet is needed. Unthemed terminals use
xterm.js default colors, so the look is unchanged.

Wasm loading still applies: check [web-frameworks.md](web-frameworks.md) for
your bundler.

## What carries over

- Options incl. `theme` (`ITheme`), cursor, font, scrolling, input, links.
  Options with no Termy equivalent (`logLevel`, `windowsMode`, `tabStopWidth`,
  `smoothScrollDuration`, …) are accepted and ignored.
- `term.options.fontSize = 16` and `term.options = { ... }` update live.
- Methods: `open`, `write`, `writeln`, `paste`, `input`, `resize`, `focus`,
  `blur`, `clear`, `reset`, `scroll*`, `select*`, `getSelection`,
  `getSelectionPosition`, `attachCustomKeyEventHandler`,
  `attachCustomWheelEventHandler`, `registerMarker`, `loadAddon`, `dispose`.
- Events: `onData`, `onBinary`, `onKey`, `onResize`, `onTitleChange`,
  `onBell`, `onScroll`, `onRender`, `onSelectionChange`, `onCursorMove`,
  `onLineFeed`, `onWriteParsed`.
- `buffer.active` with `getLine(y).translateToString()`, `getCell(x)`, cell
  attribute/color getters; `modes`.

## Addons

| xterm.js addon | With @termysh/xterm |
| --- | --- |
| `@xterm/addon-fit` | `FitAddon` (same API) |
| `@xterm/addon-web-links` | `WebLinksAddon` (same API) |
| `@xterm/addon-search` | `SearchAddon`: `findNext`, `findPrevious`, `onDidChangeResults` |
| `@xterm/addon-webgl`, `@xterm/addon-canvas` | `WebglAddon`, `CanvasAddon` are no-ops (own renderer) |
| `@xterm/addon-unicode11` | `Unicode11Addon` no-op (engine measures widths) |
| `@xterm/addon-image` | Not needed for kitty graphics (built in). Sixel unsupported |

Third-party addons reaching into internals (`terminal._core`) won't work.

## Termy extras

| Option | Description |
| --- | --- |
| `termyTheme` | Start from a bundled Termy theme; `theme` then overrides colors |
| `images` | Kitty graphics (default `true`) |
| `allowClipboardWrite` | Let OSC 52 write the clipboard |
| `autoFit` | Follow container without `FitAddon` (off by default, as in xterm.js) |
| `padding`, `copyOnSelect` | As in `@termysh/web` |

`term.termy` is the underlying `@termysh/web` terminal; `term.ready` resolves
when the engine loads.

## Differences to handle

- Writes before wasm loads are queued and render once ready.
- `registerDecoration`, custom `registerLinkProvider` providers and character
  joiners are accepted and do nothing.
- **No `term.parser`**: `parser.register*Handler` calls throw. Remove them;
  use `term.termy.onTitleChange`, `onCwdChange`, `onProgress` and other
  `@termysh/web` events for common OSC sequences.
- `buffer.normal` can't read the main screen while a full-screen app is on the
  alternate screen.

Migration checklist: swap deps/imports, delete the CSS import, grep for
`.parser.`, `_core`, `registerDecoration`, `registerLinkProvider`; fix wasm
loading for the bundler; verify `vim`/`htop` and resizes.

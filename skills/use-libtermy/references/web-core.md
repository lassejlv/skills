# @termysh/core: headless engine

Source: https://termy.sh/docs/developer/web/core.md

The engine without a renderer. Runs in browsers, web workers, Node and Bun;
no I/O, no DOM. Use it to render with your own stack (WebGL, React, canvas in
a worker), snapshot output on a server, or test programs that draw to a
terminal.

```ts
import { Slot, TermyCore, decodeColor, init } from '@termysh/core'

await init()   // required before new TermyCore(), builtinTheme(), builtinThemeIds()
const term = new TermyCore({ cols: 80, rows: 24, scrollback: 1000 })

term.write('\x1b[1;32mready\x1b[0m\r\n$ ')
term.lineText(0)   // 'ready'
term.cursor()      // { row: 1, col: 2, visible: true, shape: 'block', blinking: false }
```

Node/Bun: `init()` reads `termy.wasm` from disk, no setup. Workers: pass
bytes or a compiled module to `initSync`.

## Render loop

```ts
const damage = term.takeDamage()          // { full, scrolls, spans }
const rows = term.readRows(0, term.rows)  // flat cells for the viewport

for (let row = 0; row < rows.rowCount; row++) {
  for (let col = 0; col < rows.cols; col++) {
    const text = rows.text(row, col)
    const at = rows.offset(row, col)
    const fg = decodeColor(rows.data[at + Slot.Foreground])
    const style = rows.data[at + Slot.Style]
    // draw ...
  }
}
```

Each cell = six `u32` slots: text, foreground, background, underline color,
style bits, hyperlink. Colors keep their kind (`default`, `indexed`, `rgb`) so
you resolve them against your theme. Reads are copies; they stay valid as
engine memory changes.

## Input (encode with the engine, then send)

```ts
import { Modifier } from '@termysh/core'

term.encodeKey('up', undefined, 0)              // '\x1b[A', or '\x1bOA' in app cursor mode
term.encodeKey('c', 'c', Modifier.Ctrl)         // '\x03'
term.encodeKey('enter', '\r', 0)                // '\r'
term.encodePaste(text)                          // bracketed when the program enabled it
term.encodeMouse('press', 'left', col, row, 0)  // undefined unless the program tracks the mouse
term.encodeFocus(true)
```

Encoders return `Uint8Array` or `undefined` (no bytes). Send as-is. `key` is
a Termy key name (`enter`, `up`, `f5`, `a`); `text` is the produced
character. Combine modifiers with `|` (`Modifier.Ctrl | Modifier.Shift`).

## Replies and events (after every write)

```ts
term.write(output)
const replies = term.takeReplies()
if (replies.length) host.send(replies)       // programs block waiting for these
for (const event of term.takeEvents()) {
  switch (event.type) {
    case 'title': setTitle(event.title); break
    case 'resetTitle': setTitle(''); break
    case 'bell': ring(); break
    case 'cwd': setCwd(event.cwd); break
    case 'progress': setProgress(event.state, event.value); break
    case 'programStatus': setStatus(event.records); break // OSC 7501
    case 'clipboard': copy(event.data); break             // OSC 52, base64
    case 'shellIntegration': mark(event.payload); break   // OSC 133
  }
}
```

When the host process exits, call `term.processExited()` so working/blocked
program-status records expire. Call `term.dispose()` when done.

Answer queries in **one** place: if a browser terminal is attached to the
same PTY, it answers; don't also send `takeReplies()` from the server.

## Reading text

```ts
term.lineText(0)              // first live-screen line
term.lineText(term.rows - 1)  // last live-screen line
term.lineText(-1)             // newest scrollback line
term.historySize
term.lineWrapped(0)           // does line 0 soft-wrap into line 1
```

Lines are **screen-relative**: `0..rows-1` is the screen, negatives reach
back to `-historySize`. (`@termysh/web` uses absolute lines from the oldest
scrollback.)

## Testing terminal output

```ts
import { init, TermyCore } from '@termysh/core'
import { expect, test } from 'vitest'

await init()

test('renders a progress line', () => {
  const term = new TermyCore({ cols: 40, rows: 5 })
  term.write('Downloading...\r\x1b[2KDone\r\n')
  expect(term.lineText(0)).toBe('Done')
  term.dispose()
})
```

## Images and glyphs

- `readGraphics(cellWidth, cellHeight)`: visible kitty placements with pixel
  clip and draw rects; `graphicsImage(index)` returns RGBA or PNG data.
- `glyphPlan(codePoint, neighbors, cellWidth, cellHeight, fontSize)`: Termy's
  rects and strokes for box drawing, blocks, sextants, Braille.
- `builtinTheme(id)`, `builtinThemeIds()`.

Driving a real PTY headlessly (tests, AI agents, server snapshots):
[web-pty-and-connect.md](web-pty-and-connect.md#read-the-screen-on-the-server).

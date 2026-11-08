# Connecting a shell: @termysh/pty + WebSocket

Sources: https://termy.sh/docs/developer/web/connect.md,
https://termy.sh/docs/developer/web/pty.md

The browser terminal does no I/O. A program runs on a server in a PTY; you
move bytes between them.

```text
browser                                  server
@termysh/web  ── input, resize (JSON) ──▶  WebSocket ──▶ PTY ──▶ shell
              ◀── output (bytes) ────────  WebSocket ◀── PTY ◀──
```

**Security:** a WebSocket connected to a shell gives full command execution
to anyone who can reach it. Bind to `127.0.0.1` for dev. Before exposing:
authenticate every connection, check `Origin`, use TLS (`wss://`).

## Protocol

Keep output and control apart:

| Direction | Frame | Content |
| --- | --- | --- |
| Server → browser | Binary | Raw PTY output |
| Server → browser | Text | `{ "type": "exit", "exitCode": number }` |
| Browser → server | Text | `{ "type": "input", "data": string }` |
| Browser → server | Text | `{ "type": "resize", "cols": number, "rows": number }` |

## Server

```sh
npm install ws @termysh/pty
```

```js
import { WebSocketServer } from 'ws'
import pty from '@termysh/pty'

// Local development only: anyone who can reach this port gets a shell.
const wss = new WebSocketServer({ host: '127.0.0.1', port: 8787 })

wss.on('connection', (socket) => {
  const shell = pty.spawn(process.env.SHELL || 'bash', [], {
    name: 'xterm-256color',
    cols: 80,
    rows: 24,
    cwd: process.env.HOME,
    env: { ...process.env, COLORTERM: 'truecolor' },
  })

  shell.onData((data) => socket.send(Buffer.from(data)))     // binary frames
  shell.onExit(({ exitCode }) => {
    socket.send(JSON.stringify({ type: 'exit', exitCode }))
    socket.close()
  })

  socket.on('message', (raw, isBinary) => {                  // text frames, JSON
    if (isBinary) return
    const message = JSON.parse(raw.toString())
    if (message.type === 'input') shell.write(message.data)
    if (message.type === 'resize') shell.resize(message.cols, message.rows)
  })
  socket.on('close', () => shell.kill())
})
```

`TERM=xterm-256color` matches the Termy desktop app; `COLORTERM=truecolor`
enables 24-bit color. `node-pty` works with the same code.

## Browser

```ts
import { Terminal } from '@termysh/web'

const term = new Terminal({ theme: 'tokyo-night', fontSize: 13 })
term.open(document.getElementById('terminal')!)

const socket = new WebSocket('ws://127.0.0.1:8787')
socket.binaryType = 'arraybuffer'

const send = (message: object) => {
  if (socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify(message))
}

socket.onopen = () => send({ type: 'resize', cols: term.cols, rows: term.rows })

socket.onmessage = (event) => {
  if (event.data instanceof ArrayBuffer) {
    term.write(new Uint8Array(event.data))
    return
  }
  const message = JSON.parse(event.data)
  if (message.type === 'exit') {
    term.processExited()
    term.write(`\r\n[process exited with code ${message.exitCode}]\r\n`)
  }
}

term.onData((data) => send({ type: 'input', data }))
term.onResize(({ cols, rows }) => send({ type: 'resize', cols, rows }))
```

- `binaryType = 'arraybuffer'` + writing bytes keeps multi-byte characters
  split across frames intact.
- Resize on `onopen`: `autoFit` may have resized before the socket opened.
- `onData` carries keys, pastes **and** protocol replies. Forward all of it.
- `processExited()` expires working/blocked program-status records.

Cleanup on view close: `socket.close(); term.dispose()`. The server kills the
shell on socket close.

Other transports, same terminal side (`write` output, send `onData`/`onBytes`,
forward `onResize`): SSE + `fetch` POST, WebRTC data channel, an in-page
program (the live demo), or headless via `@termysh/core` (forward
`takeReplies()` after every write).

**Binary mouse reports:** legacy X10 mouse without UTF-8/SGR can emit
non-UTF-8 bytes on `onBinary` instead of `onData`. To forward everything with
no special cases, send `onBytes` as a binary frame and write it to the PTY as
a `Buffer`.

## @termysh/pty

Pre-1.0, pin a version. Same native process layer as the Termy app
(`forkpty` on macOS/Linux, ConPTY on Windows). API matches `node-pty`.

Differences from node-pty that matter:

- **Prebuilt binaries**, no install scripts, nothing compiles.
- **Backpressure**: output waits for JS instead of piling up; `pause()` stops
  reading so a fast program blocks rather than flooding the server.
- **`onExit` fires once, after the last output byte**, with exit code and signal.

```sh
npm install @termysh/pty
```

| Platform | Arch |
| --- | --- |
| macOS 11+ | arm64, x64 |
| Linux glibc 2.17+ | x64, arm64 |
| Linux musl (Alpine) | x64, arm64 |
| Windows 10 1809+ | x64, arm64 |

Node 18+ or Bun. The binary is an optional dependency
`@termysh/pty-<platform>`; `--omit=optional` skips it and `spawn` throws.

```ts
import { spawn } from '@termysh/pty'

const shell = spawn(process.env.SHELL ?? 'bash', [], {
  name: 'xterm-256color',
  cols: 80,
  rows: 24,
  cwd: process.env.HOME,
  env: { ...process.env, COLORTERM: 'truecolor' },
})

shell.onData((data) => process.stdout.write(data))
shell.onExit(({ exitCode, signal }) => console.log('exited', exitCode, signal))
shell.write('ls\r')
shell.resize(120, 40)
shell.kill() // SIGHUP, like closing a terminal window
```

`spawn` throws if the program isn't found/executable or `cwd` doesn't exist.

### Migrate from node-pty

```sh
npm uninstall node-pty && npm install @termysh/pty
```

```diff
-import * as pty from 'node-pty'
+import * as pty from '@termysh/pty'
```

`spawn`, `fork`, `createTerminal`, default export, `IPty`,
`IPtyForkOptions`, `IWindowsPtyForkOptions`, `IDisposable`, `IEvent`, and
`on('data')`/`on('exit')` all match. Watch for:

- `uid`/`gid` **throw**; run the parent as the target user.
- `open()` (PTY pair without a process) isn't provided.
- Windows is ConPTY only; `useConpty`, `useConptyDll`, `conptyInheritCursor`
  are ignored.
- `write` after exit is dropped silently. Unread input queues; beyond the
  8 MiB native backlog it waits in JS.

### Options

| Option | Default | Notes |
| --- | --- | --- |
| `name` | `env.TERM`, then `xterm` | Exported as `TERM` on Unix |
| `cols`, `rows` | 80, 24 | 1–65535 |
| `cwd` | `process.cwd()` | Also exported as `PWD` on Unix |
| `env` | `process.env` | The child's **whole** environment |
| `encoding` | `'utf8'` | `null` emits `Buffer`s |
| `handleFlowControl` | `false` | `\x13`/`\x11` writes act as `pause()`/`resume()` |

Without `env`, the child inherits `process.env` minus `TMUX`, `TMUX_PANE`,
`STY`, `WINDOW`, `WINDOWID`, `TERMCAP`, `COLUMNS`, `LINES`. Pass `env` to
control exactly what the child sees (and note `PATH` comes from it).

### IPty

`pid`, `cols`, `rows`, `process` (foreground program, e.g. `vim`; spawned
file name on Windows), `onData`, `onExit` (`{ exitCode, signal }`, once, after
all output), `write(string | Buffer)`, `resize(cols, rows, pixelSize?)`
(`{ width, height }` of the whole terminal, for image-sizing programs),
`kill(signal = 'SIGHUP')`, `pause()`, `resume()`.

Unix: normal exit → `{ exitCode: n, signal: 0 }`; killed by signal →
`{ exitCode: 0, signal: n }`. Windows: `kill()` closes the pseudoconsole,
waits 250 ms, then terminates (exit code 1); passing a signal throws;
`onExit` reports only `exitCode`.

### Backpressure

```ts
socket.on('drain', () => shell.resume())
shell.onData((data) => {
  if (!socket.write(data)) shell.pause()
})
```

### Read the screen on the server

`@termysh/pty` gives raw bytes. For tests, AI agents driving TUIs, or session
snapshots, feed them to `@termysh/core`:

```ts
import { init, TermyCore } from '@termysh/core'
import { spawn } from '@termysh/pty'

await init()
const screen = new TermyCore({ cols: 80, rows: 24 })
const app = spawn('htop', [], { name: 'xterm-256color', cols: 80, rows: 24, encoding: null })

app.onData((bytes) => {
  screen.write(bytes)
  const replies = screen.takeReplies()          // programs wait for these
  if (replies.length) app.write(Buffer.from(replies))
})

screen.lineText(0)
```

Answer queries in one place only: with a browser terminal attached, don't also
send `takeReplies()` from the server.

### Bundlers and Electron

The addon is a native `.node` file: mark `@termysh/pty` external (esbuild
`--external:@termysh/pty`, webpack `externals`, Vite `ssr.external`).
Electron: `asarUnpack: ['**/*.node']`. Custom binary location: set
`TERMY_PTY_NATIVE` to its absolute path before importing.

### Errors

- `@termysh/pty: no native binary for <platform>`: optional dep not
  installed. Reinstall without `--omit=optional`/`--no-optional`; ensure the
  lockfile records optional deps for all platforms (npm 7+).
- `spawn` throws `No such file or directory`: program not on the child's
  `PATH` (from `env` if passed). Slim/Alpine images often have only `/bin/sh`.
- Windows "ConPTY unavailable": needs Windows 10 1809+; check `isSupported()`.

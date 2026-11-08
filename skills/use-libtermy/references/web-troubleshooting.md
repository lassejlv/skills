# Web troubleshooting

Source: https://termy.sh/docs/developer/web/troubleshooting.md

| Symptom | Cause | Fix |
| --- | --- | --- |
| Nothing appears | Container has no height | Give the `open` element a height (`400px`, or `flex: 1` in a sized flex parent) |
| Nothing appears | `open` never called, or element not in the document | Call `open` after mount |
| Nothing appears | Wasm failed to load | `term.ready.catch((e) => console.error('Termy failed to load', e))` and check the console |
| `expected magic word 00 61 73 6d` | `termy.wasm` request returned HTML (dev server / SPA fallback) | Vite ≤ 7: `optimizeDeps.exclude: ['@termysh/core']`. esbuild/custom: copy the wasm next to the bundle or pass `wasm` URL |
| `instantiateStreaming failed ... application/wasm MIME type` | Wrong content type (warning only) | Serve `.wasm` as `application/wasm` |
| `Refused to compile or instantiate WebAssembly module` | CSP blocks wasm | Add `'wasm-unsafe-eval'` to `script-src` |
| `UnhandledSchemeError ... node:fs/promises` (webpack) / `Could not resolve "node:fs/promises"` (esbuild) | Node-only import resolved in browser build | webpack `IgnorePlugin`; esbuild `--external:node:fs/promises` |
| `@termysh/core: call await init() before creating a terminal` | Engine used before wasm loaded | core: `await init()` before `new TermyCore()` / `builtinTheme*()`. web: `await term.ready` or `await Terminal.create()` before `builtinTheme*()` |
| `@termysh/web: terminal is already open` | `open` called twice (React: created outside effect or no cleanup) | Create in `useEffect`, `dispose()` in cleanup |
| `vim`/`htop`/rich prompts hang or draw only after a keypress | Protocol replies not forwarded | Send **everything** from `onData` to the PTY; with core, send `takeReplies()` after each write |
| Output wraps at wrong width | PTY still has old size | Forward every `onResize`; send current size when the connection opens |
| Washed-out colors | Program didn't detect truecolor | Spawn with `TERM=xterm-256color`, `COLORTERM=truecolor` |
| `posix_spawnp failed` (node-pty) | `spawn-helper` lost exec bit (install scripts skipped) | Allow install scripts and reinstall, or `chmod +x node_modules/node-pty/prebuilds/*/spawn-helper`, or switch to `@termysh/pty` |
| Ctrl+C doesn't copy | Expected: it's an interrupt | Cmd+C/V on macOS, Ctrl+Shift+C/V elsewhere; Shift+drag selects while an app tracks the mouse |

Server-side PTY errors (`no native binary`, `No such file or directory`,
ConPTY unavailable): [web-pty-and-connect.md](web-pty-and-connect.md#errors).

Filing a bug: https://github.com/termylabs/termy/issues with package
versions, browser, bundler, and a minimal reproduction.

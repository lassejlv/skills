# Frameworks, bundlers and wasm loading

Source: https://termy.sh/docs/developer/web/frameworks.md

`@termysh/core` loads `termy.wasm` via `new URL('./termy.wasm', import.meta.url)`.
Most bundlers detect that, copy the file, and rewrite the URL.

| Bundler | Setup |
| --- | --- |
| Vite 8 | None |
| Vite 7 and earlier | Exclude `@termysh/core` from dep pre-bundling |
| Next.js (Turbopack, default in 16) | None |
| Next.js `--webpack`, webpack 5 | Ignore `node:fs/promises` in browser build |
| esbuild | Mark `node:fs/promises` external; copy `termy.wasm` next to bundle |

`node:fs/promises` only runs in Node/Bun (where `init()` reads the wasm from
disk); browser builds never execute it, but webpack/esbuild still try to
resolve it.

## React

```tsx
'use client' // Next.js App Router only

import { useEffect, useRef } from 'react'
import { Terminal } from '@termysh/web'

export function TerminalView({ url }: { url: string }) {
  const container = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const term = new Terminal({ theme: 'tokyo-night', fontSize: 13 })
    term.open(container.current!)

    const socket = new WebSocket(url)
    socket.binaryType = 'arraybuffer'
    socket.onmessage = (event) => {
      if (event.data instanceof ArrayBuffer) term.write(new Uint8Array(event.data))
    }
    const input = term.onData((data) => {
      if (socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ type: 'input', data }))
    })

    return () => {
      input.dispose()
      socket.close()
      term.dispose()
    }
  }, [url])

  return <div ref={container} style={{ height: 400 }} />
}
```

- Create in `useEffect`, never during render (`open` needs the DOM).
- Always return a cleanup that calls `dispose()`; Strict Mode mounts effects
  twice in dev, otherwise a second terminal is left behind ("terminal is
  already open").
- Keep the `Terminal` in the effect or a ref, **not state**.
- Change options with `term.setOptions`, don't recreate.
- Full socket protocol (resize, exit): [web-pty-and-connect.md](web-pty-and-connect.md).

## Next.js

Use the component above in a client component. Importing `@termysh/web` during
SSR is safe; nothing touches the DOM until `open` in the effect. Turbopack
needs no config. With `next build --webpack` you get
`UnhandledSchemeError: Reading from "node:fs/promises" is not handled by plugins`:

```js
// next.config.mjs
export default {
  webpack(config, { webpack, isServer }) {
    if (!isServer) {
      config.plugins.push(new webpack.IgnorePlugin({ resourceRegExp: /^node:fs\/promises$/ }))
    }
    return config
  },
}
```

## Vue (Svelte, Solid: same pattern)

```vue
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { Terminal } from '@termysh/web'

const container = ref<HTMLDivElement>()
let term: Terminal | undefined

onMounted(() => {
  term = new Terminal({ theme: 'tokyo-night' })
  term.open(container.value!)
})
onBeforeUnmount(() => term?.dispose())
</script>

<template>
  <div ref="container" style="height: 400px" />
</template>
```

Create and `open` once mounted; `dispose` on unmount.

## Vite

Vite 8: nothing. Vite ≤ 7: production builds work, but the dev server
pre-bundles into `node_modules/.vite/deps`, the wasm URL 404s to the HTML
page, and loading fails with
`WebAssembly.instantiate(): expected magic word 00 61 73 6d`.

```ts
// vite.config.ts
import { defineConfig } from 'vite'
export default defineConfig({
  optimizeDeps: { exclude: ['@termysh/core'] },
})
```

## webpack 5

Emits the wasm asset but fails on the Node-only import:

```js
const webpack = require('webpack')
module.exports = {
  plugins: [new webpack.IgnorePlugin({ resourceRegExp: /^node:fs\/promises$/ })],
}
```

## esbuild

Doesn't copy `new URL(..., import.meta.url)` assets. Output must be ESM so
`import.meta.url` points at the bundle:

```sh
esbuild src/main.ts --bundle --format=esm --outdir=dist --external:node:fs/promises
cp node_modules/@termysh/core/dist/termy.wasm dist/
```

## Serve the wasm yourself (CDN, fixed path, cache-busted)

```ts
new Terminal({ wasm: '/assets/termy.wasm' })

// Vite can emit it and hand you the URL:
import wasmUrl from '@termysh/core/termy.wasm?url'
new Terminal({ wasm: wasmUrl })
```

`wasm` and `init` also accept a `URL`, `Response`, a promise of one, bytes,
or a compiled `WebAssembly.Module`. The module loads once per page; later
terminals reuse it. Serve with `Content-Type: application/wasm` (otherwise
slower load + `instantiateStreaming` warning).

## Content Security Policy

```text
Content-Security-Policy: script-src 'self' 'wasm-unsafe-eval'; connect-src 'self'
```

Add the wasm origin to `connect-src` if it's not your own.

## No DOM (workers, Node, Bun, tests)

`@termysh/web` needs a DOM. Use `@termysh/core` ([web-core.md](web-core.md));
in Node/Bun `await init()` finds the wasm on disk. Server-side programs:
`@termysh/pty`.

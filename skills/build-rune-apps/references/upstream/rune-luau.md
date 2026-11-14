> Upstream: [crates/rune-luau/README.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-luau/README.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# rune-luau

Luau scripts that build Rune UI. A `Script` is one sandboxed Luau VM: its `init.luau` returns a
module whose `render(view)` builds nodes with `@rune/ui`, straight into `rune::El`s.

```rust
struct State { script: Script }

fn view(s: &State, cx: &mut Cx<State>) -> El { s.script.view(cx) }
fn poll(s: &mut State, now: f64, tx: &mut Tx) -> bool { s.script.poll(now, tx) }
fn setup(s: &mut State, waker: Waker) { s.script.set_waker(waker) }

let script = Script::new("panel", Sources::from_dir("scripts/panel")?);
script.watch("scripts/panel")?; // `watch` feature: save a file, the panel reloads
```

```luau
--!strict
local ui = require("@rune/ui")
local count = 0
return {
    render = function(view)
        return ui.col({ pad = 16, gap = 8 }, {
            ui.text(`Pressed {count} times`),
            ui.row({ key = "inc", px = 10, py = 4, radius = 6, fill = "control-off",
                onPress = function() count += 1 end }, { "Press" }),
        })
    end,
}
```

## Host API

| Call | What it does |
| --- | --- |
| `Script::new(name, sources)`, `Script::with_options(..)` | Compiles and starts a script. One that fails to start still renders, as an error card. |
| `ScriptOptions::new().palette(..).setup(..).node(..).time_limit(..).memory_limit(..).on_log(..)` | Colour names, host bindings for each new VM, host-built `ui.*` nodes, the watchdog limit (250 ms), the heap limit (64 MB), and a log sink. |
| `ScriptOptions::start(..).around(..).around_read(..).shadows(..).text(..)` | A hook that runs with each new VM and the table its entry returned (call a setup function it hands over); hooks around entries from the UI with the app's state and transaction; elevation shadows; the base text style and the weights `regular`..`bold` name. |
| `Sources::entry(path)` | Starts from another module than `init.luau` (`app.luau` beside it). |
| `script.render_fn(id, version, dark, f, args)`, `script.spawn_fn(f, args, tx)`, `script.eval_fn(f, args)` | Functions a script handed the host: render one as a memoized surface, run one as a task, or call one at once without letting it wait. `script.version()` moves whenever script code runs. |
| `script.view(cx)`, `script.surface(cx, name)` | The module's `render(view)` (or `name(view)`), memoized on the script's version: a view rebuilt for other reasons reuses it without entering the VM. |
| `script.poll(now, tx)` | Runs finished host calls, due `task.wait`/`task.delay` deadlines and deferred tasks, then arms `Tx::wake_after` for the next deadline. With nothing due it never enters the VM. |
| `script.reload(sources)`, `script.watch(dir)` | Hot reload: the new VM gets `loadHotState(saveHotState())`. A compile or start error keeps the running VM. |
| `script.fire(name, data)`, `script.call(name, data)`, `script.query(name, data)` | Fires a host signal; runs an export as a task; calls an export and returns its result. |
| `Host::signal`, `Host::script_signal`, `Host::async_function`, `Host::register_module`, `Host::global` | What `ScriptOptions::setup` binds. An async function hands the host a `Completer`, finished from any thread; `spawn_blocking` runs work off the UI thread. |
| `script.error()`, `script.log()`, `script.metrics()`, `script.memory()` | Why it stopped, recent `print`/`warn`/error lines, VM entries and time, heap bytes. |
| `Data`, `Data::decode` (`serde` feature) | Plain values across the VM boundary. Whole numbers are `Data::Integer` and decode into `i64` fields on every target; mlua's own serde path gives wasm32 a float for whole numbers past 32 bits. |

## In Luau

- **`@rune/ui`**: `row`, `col`, `box`, `spacer`, `text(content, props)`, `virtualList`, `each`,
  `hex`. Containers take `(props, children)`; a string child is text, and `nil` or `false`
  children are skipped. A props table frozen with `table.freeze` is decoded once per VM and its
  node copied after that; a node whose props are partly its own takes the frozen style first and
  a small table of its own after it, laid over it (`ui.row(ROW, { key = id }, children)`,
  `ui.text(words, LABEL, { color = ink })`, host nodes too), and only that table is decoded.
  Values after a text's props fill `{1}`, `{2}`... in its content, straight into the string the
  element keeps (`ui.text("{1} / {2}", VALUE, read, write)`). Props: `key`, `w`/`h` (points or `"full"`), `minW`..`maxH`, `grow`, `shrink`, `pad`,
  `px`..`pl`, `m`..`ml`, `gap`, `align`, `justify`, `center`, `wrap`, `fill`, `hover`, `press`,
  `border`, `borderWidth`, `radius`, `clip`, `scrollY`, `scrollX`, `opacity`, `role`, `label`,
  `help`, `helpSide`, `dir` (`"ltr"`, `"rtl"` or `"auto"`), `pin`, `corners`, `shadow`, `selected`, `focusable`, `disabled`, `hoverTransition`, `hoverGroup`, `hoverGroupColor`, `revealOnHover`, `onPress`, `onMiddlePress` (a middle click: a `middle-press` event), `onHover`, and for text `size`, `weight`, `lineHeight`, `tracking`, `color`, `mono`,
  `tabular`, `noWrap`, `truncate`, `fadeOut`, `selectable`, `textAlign`. Colours are palette names or
  `ui.hex("#rrggbb")`.
- **`view:Memo(key, version, build)`** reuses the subtree while `version` (a string, number or
  boolean) is unchanged, without calling `build`. Its memo id, and its root's key, is `key` under
  the script's prefix (`luau:<name>:<key>`), so scripts in one window never share a memo. **`view:Handler(fn)`** returns `fn`; handlers
  run as tasks and receive a `UiEvent` (`kind`, `key`, `shift`, `alt`, `mod`).
- **`ui.each(items, key, version, build)`** returns `build(item, index)` for each item as a list
  of children, each a memo of its own on the item's key (also its node's key) and version, so a
  render rebuilds only the items whose version moved. `key` and `version` are field names or
  functions of `(item, index)`.
- **`ui.virtualList({ count, estimatedRowHeight, version, renderRow, rowKey?, rowVersions?, onVisibleRows?, gap?, scrollY? })`**
  is `El::virtual_rows`: `renderRow(i)` (from 1) runs only for rows entering the window, and each
  row is memoized on `version` and its entry in `rowVersions`. With `scrollY = false` it has no
  viewport of its own: it sits in a scrolling column under or among other content and builds the
  rows that column shows.
- **`task`**: `spawn`, `defer`, `delay`, `wait` and `cancel`, on the frame clock `poll` receives.
  Waiting costs nothing; `wait` in a render is an error.
- **Signals**: a host's `Signal` has `Connect`, `Once` and `Wait`; a `ScriptSignal`
  (`require("@rune/signal").new()`) adds `Fire` and `Version`. A `Connection` has `Connected`
  and `Disconnect`. Connections run as tasks.
- **`require`** follows Luau's require-by-string rules inside the script's folder, so the host and
  `luau-lsp` agree. `init.luau` stands for its folder: from it, `require("@self/x")` is `x.luau`
  and `require("./x")` would be beside the folder. `.luaurc` aliases apply, including the one
  above the folder (`Sources::parent_config`). Nothing outside the folder resolves; a cycle is an
  error naming the chain. A module that starts with `--!native` compiles to native code with
  the `native-code` feature (Windows and Linux).

## Errors

Nothing a script does panics the app. A render error shows an error card with a Reload button;
a task error is logged; the watchdog stops any entry that runs longer than 250 ms, at a Luau
safepoint, and that script carries on with its next call.

## Platforms

Scripts run in Luau's interpreter. The `native-code` feature adds Luau's native code generation
for modules that open with `--!native`, on Windows and Linux (x86-64, arm64) only: enable it for
those targets alone. It costs every VM a 4 MiB committed code block as the VM starts, whether a
native module ever loads or not. On `wasm32-unknown-unknown`, Luau's C++ builds with
[WASI SDK](https://github.com/WebAssembly/wasi-sdk) 33 or newer and WebAssembly exception
handling: set `WASI_SDK_PATH` and `scripts/web-build.sh` sets the compilers up; this crate links
the SDK's C runtime and defines the few WASI calls it makes, so the page needs nothing extra.
On the web, `spawn_blocking` runs its job on the main thread after the current frame's work;
finish browser-async work (a `fetch`) from its own callback through the `Completer`.

`mlua` is pinned to a commit on its main branch: `wasm32-unknown-unknown` support landed after
0.12.2.

## Example

`examples/luau-panel`: a header, a pulse driven by `task.wait`, a signal and a 1,000-row virtual
list. `cargo run -p luau-panel`; `cargo run -p luau-panel --bin luau-bench --profile perf`
measures idle frames, memo hits, a 20-row rebuild, list scrolling and hot reload.

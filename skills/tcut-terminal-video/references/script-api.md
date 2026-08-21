# Tcut Script API

Read this reference when a demo needs configuration beyond the easy path, direct key control, captions, screenshots, or screen-aware branching.

## Script shape

```ts
import { defineVideo } from "tcut";

export default defineVideo(config, async (t) => {
  // Recorded interaction
});
```

Only `output` is required. A string creates one output; an array creates several formats from the same recording.

## Configuration decisions

| Concern | Fields | Guidance |
| --- | --- | --- |
| Output | `output`, `cast` | Extension selects format. Preserve a cast when later re-theming or re-rendering is likely. |
| Terminal grid | `cols`, `rows` | Choose a grid large enough for the command and proof output without tiny text. Defaults are 80 by 24. |
| Pixel frame | `width`, `height`, `padding`, `margin`, `marginFill`, `borderRadius` | Use when the deliverable has a fixed canvas or branded surround. The terminal grid is centered inside the frame. |
| Shell and prompt | `shell`, `prompt` | `shell` accepts `bash`, `zsh`, `fish`, `sh`, or a command array. Keep `prompt` aligned with the clean shell so `run()` can detect completion. |
| Timing | `fps`, `typingSpeed`, `typingJitter`, `seed`, `playbackSpeed`, `waitTimeout`, `endPause`, `loopOffset` | Seeded jitter is reproducible. Increase `waitTimeout` for genuinely slow state; do not replace observable waits with long sleeps. |
| Style | `theme`, `font`, `windowBar`, `title`, `cursor` | Query themes with `tcut themes [query]`. Font accepts `family`, `size`, `lineHeight`, and `letterSpacing`. |
| Rendering | `quantize`, `core`, `cache` | Leave cache enabled for iteration. `core` is `ghostty` or `lite`; use the default unless a verified need says otherwise. |
| Browser | `browser` | Read [advanced-workflows.md](advanced-workflows.md) before adding a browser pane. |

Durations accept numbers in milliseconds and strings such as `"500ms"`, `"1.5s"`, and `"2m"`.

## Interaction methods

### Commands and text

- `run(cmd)` types a command, presses Enter, and waits for the prompt.
- `type(text)` simulates typing with configured timing.
- `paste(text)` enters text as a paste rather than individual keys.
- `raw(bytes)` sends raw terminal input when higher-level methods cannot express it.

Use `run()` at a shell prompt. Use `type()` or `paste()` inside a REPL, prompt, editor, or TUI where Enter and subsequent state need separate control.

### Keys

The direct methods are `enter`, `tab`, `backspace`, `delete`, `escape`, `space`, `up`, `down`, `left`, `right`, `home`, `end`, `pageUp`, and `pageDown`. They accept a count where repetition makes sense.

Use:

- `ctrl("c")`, `alt("b")`, or `shift("tab")` for modifiers;
- `key("f5")` for named keys;
- `scrollUp(n)` and `scrollDown(n)` only when the target program has mouse tracking enabled.

## Synchronization and assertions

```ts
await t.wait(/ready/i, { scope: "screen" });
await t.expect(/build completed/i);
```

- `wait()` with no pattern waits for the prompt.
- `scope: "line"` targets the current line; `scope: "screen"` searches the rendered screen.
- `expect()` asserts the rendered screen and throws an `ExpectationError` with a screen dump.
- `sleep()` controls viewing pace after a state is already known. It should not decide when the next interaction is safe.

Prefer a bounded regular expression that identifies the state the next action depends on. Avoid matching generic words such as `done`, `ok`, or `success` when they may already exist elsewhere on screen.

## Read and branch on the terminal

Use `screen()`, `line()`, `cursor()`, `cols`, and `rows` to inspect current state. This enables content-aware selection:

```ts
await t.wait(/Choose a framework/, { scope: "screen" });

for (let attempts = 0; attempts < 20; attempts += 1) {
  if (/●\s+Cloudflare/.test(t.screen())) break;
  await t.up();
}

await t.expect(/●\s+Cloudflare/);
await t.enter();
```

Always bound loops. If the desired item never appears, fail with an expectation rather than hanging or selecting an unknown option.

## Shape the recording

- `hide(async () => { ... })` executes the callback but removes that interval from the video. It is useful for noisy setup or cleanup, not secrecy or safety.
- `screenshot(path)` captures the current terminal state.
- `marker(name)` creates a named timeline marker.
- `resize(cols, rows)` changes the terminal grid.
- `clear()` clears the terminal.
- `print(markdown)` renders Markdown directly into the recording without typing it into the shell.
- `title(text, { pause })` renders a large heading, rule, and pause.

Call `print()` and `title()` at a shell prompt. They write into terminal display state and can disrupt a full-screen program.

## A robust CLI demo

```ts
import { defineVideo } from "tcut";

export default defineVideo(
  {
    output: ["demo.mp4", "demo.svg"],
    cols: 92,
    rows: 28,
    width: 1440,
    height: 900,
    theme: "Gruvbox Dark",
    typingSpeed: "38ms",
    typingJitter: 8,
    seed: 7,
    endPause: "2s",
  },
  async (t) => {
    await t.title("Fast local validation", { pause: "800ms" });
    await t.run("bun test");
    await t.expect(/\b\d+\s+pass(?:ed)?\b/i);

    await t.print("The test command verifies the change before packaging.");
    await t.run("bun run build");
    await t.expect(/build|built|generated/i);
    await t.sleep("1.25s");
  },
);
```

The expressions above are examples, not universal assertions. Replace them with exact output established from the target project.

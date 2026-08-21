# Advanced Tcut Workflows

Read only the section needed for the current task.

## Drive an interactive TUI

A stable TUI script reacts to content instead of timing guesses or recorded coordinates:

1. Wait for the prompt or screen text that makes the next action valid.
2. Inspect `t.screen()` when menu order or selection can vary.
3. Send one logical input.
4. Wait for the resulting screen state.
5. Assert the final proof state before exit.

```ts
await t.type("bun create cloudflare");
await t.enter();
await t.wait(/Choose a framework/, { scope: "screen" });

for (let attempts = 0; attempts < 20; attempts += 1) {
  if (/●\s+Cloudflare/.test(t.screen())) break;
  await t.up();
}

await t.expect(/●\s+Cloudflare/);
await t.enter();
await t.wait(/created|ready|success/i, { scope: "screen" });
```

Bound any state-reading loop. Fixed arrow counts are acceptable only when the exact TUI version and menu order are controlled and verified.

After a full-screen program exits, stale text may remain on the primary screen. Prompt detection is cursor-relative, so `run()` and `wait()` can still work. To clean the visible recording without showing the clear command:

```ts
await t.hide(async () => {
  await t.clear();
});
```

### Coding agents

When recording Codex, Claude Code, or a similar agent:

- wait for its trust or approval prompt before pressing Enter;
- wait for the real input box before typing the task;
- wait for a stable completion marker or absence of the active-interruption state;
- exit through the agent's supported `/exit` or `/quit` command;
- never auto-approve permissions, tool actions, or representational output merely to make the demo proceed;
- use a disposable or intentionally scoped checkout when the demonstrated agent may edit files.

Agent UI markers change. Inspect the actual version's screen instead of treating a historical marker as permanent API.

## Combine a terminal and browser

Browser recording uses Bun.WebView and can place the browser on the `right`, `left`, `top`, `bottom`, or in an `overlay`.

```ts
import { defineVideo } from "tcut";

export default defineVideo(
  {
    output: "demo.mp4",
    browser: {
      position: "right",
      width: 900,
      height: 900,
      title: "Application",
    },
  },
  async (t) => {
    await t.hide(async () => {
      await t.run("bun run dev </dev/null >/tmp/tcut-demo.log 2>&1 &");
    });

    await t.browser.goto("http://localhost:5173");
    await t.browser.waitFor(/Welcome/i);
    await t.run("bun test");
    await t.expect(/pass|passed/i);
    await t.browser.click("[data-demo-action]");
    await t.browser.waitFor(/Complete/i);
  },
);
```

Available browser methods are `goto(url)`, `waitFor(pattern)`, `click(selector)`, `reload()`, and `evaluate(js)`. For overlay layouts, `focus("terminal")` and `focus("browser")` control which pane is in front.

Start dev servers with stdin detached and logs redirected. Otherwise background output may repaint the terminal or the shell may suspend the job. Use a task-specific log path and inspect it when startup fails. Clean up the process through the project's supported mechanism; do not use broad process-killing commands.

Browser frames are composited into MP4, GIF, and PNG outputs. SVG and HTML contain only the terminal, so do not choose those formats when the browser view is essential evidence.

## Record live, then edit

For an exploratory human-driven session:

```sh
tcut rec -o demo.gif
```

Exit the shell when finished. tcut creates the output, a `.cast`, and an editable `.video.ts` based on the input. To record one non-interactive command without a manual shell:

```sh
tcut rec -o demo.mp4 -- bun test
```

`tcut rec` needs a TTY for pass-through keystrokes. Agents should normally write a script or use `tcut rec -- <command>`.

Review generated scripts before re-running them: an exploratory recording may contain mistaken commands, local paths, credentials, or destructive cleanup that should not become reproducible automation.

## Separate recording from rendering

Record only:

```sh
tcut record demo.video.ts --json
```

Render an existing tcut or asciinema cast without executing its shell commands:

```sh
tcut render demo.cast -o demo.mp4 -o demo.svg --theme "TokyoNight" --json
```

Use this separation to try themes, sizing, playback speed, margins, or formats safely. If the script has not changed, tcut's cache can also reuse its prior cast. `--force` deliberately bypasses that cache.

Useful CLI appearance controls include:

- `--theme`, `--font`, `--font-size`, `--line-height`, and `--letter-spacing`;
- `--fps`, `--speed`, `--padding`, `--margin`, `--margin-fill`, and `--radius`;
- `--window-bar`, `--title`, `--no-blink`, `--cols`, `--rows`, `--width`, and `--height`;
- `--loop-offset` for GIF or WebP loop timing.

Query the bundled theme collection with `tcut themes [query]` instead of guessing a theme name.

## Use tcut in automation

Add `--json` when another program will consume the result:

```sh
tcut test demo.video.ts --json
tcut demo.video.ts --json
```

The command writes exactly one JSON document to stdout and suppresses status lines. On failure, parse the `error` and `type`; do not mix JSON parsing with progress-text scraping. Without JSON, `-q` silences status lines, status goes to stdout, and errors go to stderr.

All commands exit `0` on success and `1` on failure. Preserve the exit status in CI. Do not turn a failing expectation into a passing build just to retain a render artifact.

## Publish safely

Publishing uploads media to an S3-compatible service and is an external mutation. Obtain user authorization and confirm the exact files, bucket, endpoint, public URL behavior, and sensitivity before uploading.

Interactive setup:

```sh
tcut publish --setup
```

Non-interactive setup accepts `--endpoint`, `--bucket`, `--access-key`, `--secret-key`, `--public-url`, and `--region`. Never write credential-bearing commands into a repository, demo script, cast, transcript, or response. Prefer the user's existing secure credential mechanism.

Publish selected artifacts only:

```sh
tcut publish demo.gif --json
```

Use `--open` only when opening a browser is desired and authorized. Report the resulting link without implying that deletion, privacy, retention, or access controls were verified unless they were.

## Output requirements

| Output | Additional requirement | Notes |
| --- | --- | --- |
| `.svg`, `.html` | None beyond tcut | Terminal only; browser panes are not composited |
| `.png`, `.jpg`, directory of PNG frames | macOS WebKit or a supported Chromium-family browser on Linux/Windows | Still image is the final frame |
| `.mp4`, `.webm`, `.gif` | Rendering support plus ffmpeg | Browser panes can be composited |
| `.webp` | ffmpeg with libwebp | May require a fuller ffmpeg build |

tcut is verified on macOS. Its Linux and Windows standalone binaries are cross-compiled but may not have equivalent CI coverage; state that limitation when those platforms were not exercised.

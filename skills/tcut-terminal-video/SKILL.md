---
name: tcut-terminal-video
description: Create, edit, test, render, and publish repeatable terminal demos with tcut (the termcut package). Use when Codex needs to turn CLI commands, interactive terminal programs, coding agents, or a terminal-plus-browser workflow into scripted or live MP4, WebM, GIF, WebP, SVG, HTML, screenshots, or frame sequences. Covers easy recordings, deterministic TypeScript video scripts, TUI automation, visual styling, re-rendering casts, and S3-compatible publishing; do not use for general screen recording that does not involve tcut.
---

# Tcut Terminal Video

Create a concise terminal story that runs reliably, proves the important output, and produces the requested media without hiding failures.

## Core contract

1. Treat every command in a tcut script as a real shell command with the caller's permissions. `t.hide()` removes footage; it does not sandbox, redact logs, or make a command safe.
2. Prefer a scripted `.video.ts` file for agent work. Use `tcut rec` only when live, human-driven interaction is part of the request or when converting an exploratory session into an editable script.
3. Wait for observable terminal state before acting. Use `t.run()`, `t.wait()`, and `t.expect()`; use `t.sleep()` for deliberate pacing, not synchronization.
4. Assert the key result on the rendered terminal screen. A video that looks plausible but shows the wrong state is a failed demo.
5. Keep the story short. Show only the commands and outputs needed to explain one workflow, and use `t.title()` or `t.print()` only when a caption materially improves comprehension.
6. Preserve the target repository and its instructions. Do not install packages, start external services, modify product files, upload media, or force a re-record unless the user has authorized that action.
7. Never place tokens, credentials, private paths, or sensitive output in the script, cast, rendered media, shell history, captions, or publishing configuration.
8. Do not claim cross-platform or visual success without checking the produced artifact. tcut's Linux and Windows binaries may behave differently from its verified macOS path.

## Choose the path

| Need | Path |
| --- | --- |
| A clean demo from known commands | Use the easy scripted workflow below |
| Explore manually, then refine | Record with `tcut rec`, edit the generated `.video.ts`, then test and render |
| Drive a TUI, Codex, Claude Code, or another agent | Read [advanced-workflows.md](references/advanced-workflows.md) |
| Show a browser beside or over the terminal | Read [advanced-workflows.md](references/advanced-workflows.md) |
| Tune the complete config or use less common key methods | Read [script-api.md](references/script-api.md) |
| Re-theme an existing cast without re-running commands | Use `tcut render` and read [advanced-workflows.md](references/advanced-workflows.md) |
| Upload to R2, S3, MinIO, or another compatible bucket | Read the publishing guardrails in [advanced-workflows.md](references/advanced-workflows.md) |

## Easy scripted workflow

### 1. Define the demo before writing it

Establish:

- the audience and the one outcome they should understand;
- the exact commands that are safe to run in the target checkout;
- the terminal state or output that proves success;
- the requested format, dimensions, theme, pacing, and destination;
- whether the commands mutate files, start services, access the network, or expose private data.

If the user did not specify a format, prefer `.svg` or `.html` for a dependency-light terminal artifact. Use `.mp4`, `.webm`, `.gif`, or `.webp` when motion playback is required and ffmpeg is available.

### 2. Check only the prerequisites the chosen path needs

```sh
tcut --version
bun --version
command -v ffmpeg
```

tcut requires Bun 1.4 or newer unless a standalone binary is already installed. SVG and HTML do not require ffmpeg. MP4, WebM, and GIF do; WebP needs an ffmpeg build with libwebp.

If tcut is absent and installation is authorized, the official package command is:

```sh
bun add -g termcut
```

The package is named `termcut`; the executable and TypeScript import are both `tcut`.

### 3. Write a deterministic script

Start with a small `.video.ts` file in the project where the commands should run:

```ts
import { defineVideo } from "tcut";

export default defineVideo(
  {
    output: ["demo.svg", "demo.gif"],
    cols: 88,
    rows: 26,
    theme: "catppuccin-mocha",
    typingSpeed: "40ms",
    waitTimeout: "20s",
    endPause: "1.5s",
  },
  async (t) => {
    await t.title("Verify the project");
    await t.run("bun test");
    await t.expect(/pass|passed|tests?\s+passed/i);
    await t.sleep("1s");
  },
);
```

Replace the example command and assertion with output verified in the actual project. Do not invent a success expression broad enough to match unrelated screen text.

For ordinary commands, prefer `t.run(command)`: it types, presses Enter, and waits for the prompt to return. Use `t.type()` plus key methods only when the interaction is genuinely incremental or full-screen.

### 4. Test behavior before spending time rendering

```sh
tcut test demo.video.ts --json
```

`tcut test` removes sleeps and typing delays, and exits non-zero when an expectation fails. With `--json`, stdout is exactly one JSON document and progress lines are suppressed. Read structured failures, especially the screen dump, before adjusting a wait or key sequence.

### 5. Record and render

```sh
tcut demo.video.ts --json
```

Recording is cached. Re-running an unchanged script can reuse its `.cast`; use `--force` only when a new recording is actually required. To change presentation without executing the shell again:

```sh
tcut render demo.cast --theme "Gruvbox Dark" -o demo.svg --json
```

### 6. Validate the artifact

Check that:

- the command and asserted result are visible and correct;
- no secret, private path, noisy setup, broken prompt, or stale full-screen content appears;
- text is readable at the target display size;
- captions do not collide with a TUI and the final state has enough pause;
- every requested output exists and plays or opens successfully;
- the working tree contains only intended script and artifact changes.

When the environment can inspect media, review at least the opening, transition, proof state, and ending rather than trusting the renderer's exit code alone.

## Failure handling

- Exit code `0` means success; `1` means failure.
- Under `--json`, parse the single JSON value instead of scraping status text. Errors include a `type` such as `WaitTimeoutError` or `ExpectationError`.
- A timeout usually means the script waited for the wrong visible state, used the wrong `scope`, or encountered a different prompt. Inspect the screen dump first.
- If a TUI item moved, select by reading `t.screen()` instead of replaying a fixed number of arrow keys.
- If background server logs repaint the terminal, detach stdin and redirect output as described in [advanced-workflows.md](references/advanced-workflows.md).
- If only styling or format failed, re-render the existing cast rather than re-running commands.

## Handoff

Report:

- the script and output paths;
- which commands the recording executed and whether they mutate state;
- `tcut test` and render results;
- which artifact moments were visually inspected;
- any dependency, platform, browser, codec, publishing, or visual path not verified.

## Current sources

Use the [agent-focused llms.txt](https://tcut.amanv.dev/llms.txt), [official README](https://github.com/AmanVarshney01/tcut/tree/main/packages/tcut), and [CLI/API reference](https://github.com/AmanVarshney01/tcut/blob/main/packages/tcut/docs/REFERENCE.md) as the authority when flags or APIs may have changed. This skill was grounded in those sources on 2026-08-21.

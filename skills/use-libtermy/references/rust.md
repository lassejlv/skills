# libtermy from Rust

Source: https://termy.sh/docs/developer/libtermy/rust.md

The crate is `termy_core`, not `libtermy`. Rust stable with edition 2024
support. The default `native` feature includes the PTY runtime; disabling
default features is **not** a drop-in replacement for a native integration.

## Dependency

```toml
[package]
name = "libtermy-example"
version = "0.1.0"
edition = "2024"

[dependencies]
# Next to a Termy checkout:
termy_core = { path = "../termy/crates/core" }
# Or pinned Git (full tested commit, commit Cargo.lock):
# termy_core = { git = "https://github.com/lassejlv/termy", rev = "YOUR_TESTED_COMMIT" }
```

Website examples describe current `main`; check the matching source for older
revisions. Local API docs: `cargo doc -p termy_core --no-deps`. Public exports
live in `crates/core/src/lib.rs`.

## Display-only smoke test (no shell)

```rust
use termy_core::{
    Terminal, TerminalDamageSnapshot, TerminalSize,
    load_config_from_contents, measure_cell_from_config,
};

fn main() {
    let loaded = load_config_from_contents("");
    let metrics = measure_cell_from_config(&loaded.app_config);
    let size = TerminalSize {
        cols: 80,
        rows: 24,
        cell_width: metrics.cell_width,
        cell_height: metrics.cell_height,
    };
    let terminal = Terminal::new_display(size, Some(&loaded.runtime_config));
    terminal.feed_output(b"\x1b[32mhello from libtermy\x1b[0m\r\n");

    let frame = terminal.frame_update(true);
    assert!(matches!(frame.damage, TerminalDamageSnapshot::Full));
    assert_eq!(frame.cells.len(), 80 * 24);
    let first_line: String = frame.cells[..80].iter().map(|cell| cell.char).collect();
    println!("{}", first_line.trim_end()); // hello from libtermy
}
```

`feed_output` parses bytes **from** a process. `write` sends bytes **to** an
owned PTY and is a no-op on a display terminal. For a remote session, send
encoded input through your transport and implement
`TerminalReplyHost::protocol_reply` to forward replies.

## Native PTY

Needs `anyhow = "1"` and `flume = "0.11"`.

```rust
use std::time::{Duration, Instant};
use termy_core::{
    Terminal, TerminalClipboardTarget, TerminalEvent, TerminalSize,
    load_config_from_default_path, measure_cell_from_config,
};

fn main() -> anyhow::Result<()> {
    let loaded = load_config_from_default_path()?;
    let metrics = measure_cell_from_config(&loaded.app_config);
    let (wakeup_tx, wakeup_rx) = flume::bounded(1);
    let terminal = Terminal::new(
        TerminalSize { cols: 80, rows: 24, cell_width: metrics.cell_width, cell_height: metrics.cell_height },
        None,              // working directory
        Some(wakeup_tx),
        None,              // shell-integration title policy
        Some(&loaded.runtime_config),
        None,              // startup command
    )?;

    let mut reply_host = |_target: TerminalClipboardTarget| None::<String>; // no clipboard
    let deadline = Instant::now() + Duration::from_secs(3);
    // Octal output so the shell's echo of the command doesn't match.
    terminal.write(b"printf '\\154\\151\\142\\164\\145\\162\\155\\171\\055\\157\\153\\012'\r");
    let mut exited = false;
    while Instant::now() < deadline {
        let _ = wakeup_rx.recv_timeout(Duration::from_millis(100));
        loop {
            let (events, has_more) = terminal.drain_events(&mut reply_host);
            exited |= events.iter().any(|e| matches!(e, TerminalEvent::Exit));
            if !has_more { break; }
        }
        if !terminal.search("libtermy-ok").is_empty() {
            println!("PTY output received");
            return Ok(());
        }
        if exited { anyhow::bail!("shell exited before producing the expected output"); }
    }
    anyhow::bail!("no expected output before the deadline")
}
```

The 3 s timeout is a test bound, not a render cadence. A GUI posts wakeups to
its event loop, drains, requests an incremental frame, and returns to idle. A
wakeup means "work may be available", not "the command finished". The
command uses POSIX syntax; adapt for Windows shells.

## Constructors and wakeups

| API | Use when |
| --- | --- |
| `Terminal::new` | Configured shell + `flume::Sender<()>` wakeup channel |
| `Terminal::new_with_wakeup_notifier` | Event loop scheduled by a `TerminalWakeupNotifier` callback |
| `Terminal::new_with_launch_and_wakeup_notifier` | You need the typed `TerminalLaunch` contract |
| `Terminal::new_display` | You own output delivery and redraw scheduling |
| `Terminal::new_display_with_wakeup_notifier` | Display-only host wants notification on committed output |

Keep notifier callbacks short: schedule work on the terminal-owning thread; no
rendering or nested terminal calls inside the notifier.

## Rendering contracts

- `snapshot()`: complete compact row-major frame for simple readers.
- `frame_update(true)` establishes a full frame; later `frame_update(false)`
  returns damage-scoped cells.
- `render_read(force_full)`: rich text, underline styles, live palette (Rust
  only).
- Generation-checked visitors copy only damaged rich cells.

Details and the retained-frame patch helper: [rendering.md](rendering.md).
Config, theme and resize: [configuration.md](configuration.md). Events and
replies: [events-and-input.md](events-and-input.md).

## Removed / off-limits

Do not use internal `terminal_engine` or backend types. `Terminal::with_term`,
`TerminalOptions::term_config`, and older raw conversion helpers are gone as of
the Rust 0.2 API. Use the public renderer-neutral types.

Rust types have their own synchronization/borrowing rules; read the method
docs. `_locked` visitors and `visit_line_cells` hold the backend lock: their
callbacks must not call back into the same terminal.

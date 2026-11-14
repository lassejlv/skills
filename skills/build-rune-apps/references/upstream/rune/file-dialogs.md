> Upstream: [crates/rune/README.md § File dialogs](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#file-dialogs) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### File dialogs

Enable Rune's `native-file-dialog` feature and inject `FileDialogs::native()` in the shell.
`dialogs.open(options).await`, `dialogs.save(options).await` and
`dialogs.open_folder(options).await` return an optional path (None means cancelled). `FileDialogOptions` carries title, directory, suggested filename and
`.filter("Audio", &["wav", "flac"])`. rfd handles macOS and Windows; on Linux Rune calls the
XDG desktop portal's FileChooser itself over zbus, parented to the focused X11 window, and
returns an error when the desktop has no portal. Poll these futures on the app's async executor
and wake Rune when the result arrives.
Never block the window's main thread with `pollster::block_on` for a native dialog;
Cocoa needs that thread's event loop to present and complete it.

Headless fixtures inject `FileDialogs::scripted([ScriptedFileDialog { kind:
FileDialogKind::Open, path: Some("/fixture/recording.wav".into()) }])`. Requests resolve
without a window; wrong request order or exhausted fixtures return an error.

Or ask from a handler, with no executor or waker to wire up:

```rust
.on_press_tx(|_: &mut App, tx: &mut Tx| {
    let options = FileDialogOptions { title: "Import".into(), ..Default::default() }.filter("Export", &["json"]);
    tx.open_file(options, |s: &mut App, result, _tx| match result {
        Ok(Some(path)) => s.import(path),
        Ok(None) => {}                          // cancelled
        Err(e) => s.error = Some(e.to_string()),
    });
})
```

- The window shows the dialog once the handler's frame is done (a sheet on macOS, owned by
  the window on Windows, the portal's chooser on Linux) and keeps drawing while it's up. The
  answer runs the callback on a later frame, as `tx.read_clipboard` does. `tx.save_file` is
  the same for a Save dialog, and `tx.open_folder` for an Open dialog that picks a folder
  (`FileDialogKind::Folder`, `"kind": "folder"` in `--tree`; filters and file name don't apply;
  the portal's `directory` chooser on Linux).
- One dialog at a time: asked for while one is open, the callback gets an error at once and
  the open dialog stays. Asked for in the same turn that shows a hidden window, it shows with
  the window; asked for on a window that stays hidden, or on an overlay, the callback gets an
  error. Hiding or closing the window cancels an open dialog with `Ok(None)`.
- Without the `native-file-dialog` feature, and on the web, the callback gets an error.
- Headless runs (`--tree`, scripts, tests) keep it open as `fileDialog` in `--tree` (kind,
  title, filters, directory, fileName) until `{"type": "file-dialog", "path": "/exports/a.json"}`
  or `{"type": "file-dialog-cancel"}` answers it. Tests read it with `Runtime::file_dialog()`
  and answer with `Runtime::resolve_file_dialog(Some(path))` or `(None)`.

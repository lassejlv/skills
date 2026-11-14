> Upstream: [crates/rune/README.md § Dropping files in from other apps (`on_drop_files`)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#dropping-files-in-from-other-apps-on_drop_files) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Dropping files in from other apps (`on_drop_files`)

`.on_drop_files(..)` makes an element a drop target for files dragged from Finder, Explorer
or a file manager. `.on_drop_hover(..)` hears the drag arrive and leave, for a highlight.

```rust
el().fill(if s.over { Color::WHITE.alpha(0.1) } else { Color::TRANSPARENT })
    .on_drop_files(|s: &mut App, files, _tx| s.attachments.extend_from_slice(files))
    .accepts_extensions(&["png", "jpg", "m4a"])
    .on_drop_hover(|s: &mut App, over, _tx| s.over = over)
```

- The target is the innermost `on_drop_files` element under the pointer that accepts any of
  the dragged files (`.accepts_files(|path| ..)`, or `.accepts_extensions(..)`, compared
  without case). A target that accepts none of them passes the drag to the next accepting
  element around it.
- The target gets the files it accepts, all in one call. The rest are left out.
- To say why a drop was refused, add `.on_drop_rejected(|s, files, tx| ..)`: the target then
  stops a drag carrying none of the files it accepts instead of passing it on, and gets those
  files there; on a mixed drop it gets the ones `on_drop_files` didn't. Draw the "can't drop
  here" state from `.on_drop_rejected_hover(|s, over, tx| ..)`, which works like
  `on_drop_hover` (either one makes the target stop the drag). `Runtime::drop_rejected_hovered()`
  reads it in tests.
- Only that target is drop-hovered. It hears `on_drop_hover(true)` when the drag reaches it, and
  `false` when the drag moves to another target, leaves the window or drops, or when the
  target goes away under the drag.
- To drop at the pointer (an editor inserting a file where it lands), read `tx.drop_point()`
  in `on_drop_files`: the drop's point on the element (`x`, `y`, following its scroll and
  transforms, and `window_x`, `window_y`), `None` when the platform gave none. To draw a drop
  caret while the drag is over the target, add `.on_drop_move(|s, p, tx| ..)`: it hears the
  point when the target is reached and as the drag moves, at most once a frame, and
  `on_drop_hover(false)` clears it. Only a target with `on_drop_move` asks for frames as the
  drag moves; scripts move a drag with further `drag_files` events.
- A drop over no accepting element goes to the root's `on_drop_files`, if it has one, else
  it's ignored. Put the handler on the root to take drops anywhere in the window.
- While a modal is open, its root stands in for the window's, and a drop outside the modal
  reaches nothing, as a drop on the dimmed window behind a sheet does.
- Drop zones take no pointer events: a zone laid over other elements leaves their clicks,
  context menus and help alone.
- Each window routes drops to its own tree. A covered window still delivers them.

winit 0.30 reports a file drag without its position, and no pointer moves arrive while the
drag lasts. So the window samples the system pointer when the drag enters, about every 16 ms
while it's over the window (drawing a frame only when that changes the target), and when it
drops. On macOS that's
`NSWindow.mouseLocationOutsideOfEventStream`, on Windows `GetCursorPos` and on X11
`QueryPointer`. Where no sample is possible it uses the last pointer position, else the root.
macOS, Windows and X11. Wayland reports no file drags in winit 0.30, and the web build has no
paths to give.

Headless scripts drag and drop files at a point or an element's centre:
`{"drag_files": {"paths": ["a.png"], "key": "zone"}}` moves a drag there, and
`{"drag_files": "leave"}` takes it away. `{"drop_files": {"paths": ["a.png"], "at": [120, 80],
"hover": 0.4}}` drags the files there, holds them for 0.4 s so a strip shows the highlight, then
drops them. `--trace` records `drop-hover:true:<path>`, `drop-hover:false:<path>` and
`drop-files:<count>:<path>`.

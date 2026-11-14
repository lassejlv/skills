# Input, focus, accessibility and windows

Upstream: [what exists](upstream/rune/what-exists.md) (focus, key routing,
chords), [text fields](upstream/rune/text-fields.md),
[shortcuts and native menus](upstream/rune-shortcuts.md),
[menus](upstream/rune/pop-up-and-context-menus.md),
[file dialogs](upstream/rune/file-dialogs.md),
[accessibility](upstream/rune/accessibility.md),
[multiple windows and overlays](upstream/rune/multiple-windows-and-overlays.md).

## Focus

- `.focusable(true)` makes an element a Tab stop; `.tab_index(n)` reorders
  (0 document order, negative pointer-only).
- `.focus_group()` gives arrow-key roving and type-select for menus, lists,
  trees and segments; `.focus_selected(on)` picks the group's first Tab stop.
- `.focus_ring(width, offset, color)` draws a keyboard-only ring; every custom
  control needs a visible one.
- `.modal(click_outside, close)` traps Tab, handles Escape, makes the background
  inert and restores focus to the opener.
- From handlers: `tx.focus(key, ring)`, `tx.blur()`. A text field focuses through
  its model: set `TextEdit::focused = true` once; the runtime clears it.

## Keys

The routing order (IME composition, default button, focused field, focus
navigation, the window's `on_key`, selection copy, page keys) is in
[what exists](upstream/rune/what-exists.md); read it before taking a key
another control expects.

- Window shortcuts live in `AppSpec::on_key`; return true to consume.
- Match with `Chord::parse("mod+shift+t")` and `chord.matches_tx(ev, tx)`:
  `mod` is ⌘ on macOS and Ctrl elsewhere, and character chords follow the
  keyboard layout. `chord.label()` gives "⇧⌘T" or "Ctrl+Shift+T" for menus and
  tooltips. Plain ⌘-letter keys also arrive as `Key::Command('t')`.
- Never test `mods.cmd && !mods.ctrl`; on Windows Ctrl+W is `{ cmd, ctrl }`.
- System-wide shortcuts (`App::global_shortcut`), native menu bars, Dock menus
  and key equivalents: [shortcuts and native menus](upstream/rune-shortcuts.md).
- `App::standard_menus()` gives macOS Edit and Window menus (no Quit).

## Text

- `TextEdit` lives in state; `text_input(&edit, style)` or rune-kit's
  `TextInput`/`TextArea` draw it. `on_edit(|s| &mut s.edit)` binds it,
  `on_submit` runs on Return.
- Undo, selection, word motion, IME composition and the edit menu are built in.
  `TextEdit::clear()` after submit keeps focus and drops history.
- Secure fields: `TextEdit::new("").secure()` or kit `TextInput::secure()`;
  never exposed to accessibility, copy or IME.
- An app-drawn editor gets the input method through `.ime_cursor()` and
  `App::on_ime(..)`.
- Selectable static text: `text(..).selectable(true)`.
- Clipboard: `tx.copy(text)`; rich clipboard in `examples/rich-clipboard`.
- Headless runs drive text with script `type`, `key`, `paste`, but real IME
  candidate windows, dead keys and the system clipboard need a real window.

## Pointer

- `on_press` fires on release inside; `on_double_press` pairs presses AppKit's
  way (the first still fires `on_press`). `on_secondary_press` gives
  window-point coordinates for context menus.
- `on_drag(|s, drag, tx| ..)` with `Drag::x/y` in local points, `dx/dy` in
  window points and `Phase::{Down, Move, Up}`; check the pinned rev's
  `tests/drag_cancel.rs` before relying on cancellation behaviour.
- `.cursor(Cursor::Pointer)` and custom PNG cursors.
- Files in: `.on_drop_files(..)`; data out: `El::drag_out`; file dialogs need
  the `native-file-dialog` feature and are scripted headless.
- Canvas handlers (wheel, pinch, rotate) that only move a camera say
  `tx.live_only()`; see [canvas handlers](upstream/rune/canvas-handlers.md).

## Accessibility

Every window exposes its tree through AccessKit (VoiceOver, Narrator/NVDA,
Orca), built only when an assistive client asks.

- Defaults come from what the element is: `.role(..)` (ARIA names: `button`,
  `switch`, `checkbox`, `list`, `listitem`, `dialog`, …), `.label(..)` else its
  text, its key as the automation id, focus, `.checked(..)`, `.expanded(..)`,
  `.level(..)`.
- Add `description`, `a11y_value`, `range_value`, `disabled`, `invalid`,
  `live_region(LiveRegion::Polite)` and `a11y_hidden` where they apply.
- An icon-only control needs `.label("Close")`.
- Check it: `--tree` writes the tree under `"accessibility"`;
  `rt.accessibility_json()` and `rt.accessibility_action(key, action, data)`
  test it. `RUNE_A11Y_LOG=1` logs a live client's activity.

## Windows and chrome

- `Chrome { full_size_content, traffic_lights, drag_regions }` and
  `Titlebar::new(height).traffic_lights(x, y)` (via `App::titlebar` or
  `cx.set_titlebar`) place macOS buttons over app-drawn chrome;
  `cx.titlebar_inset()` gives clearance. Mark drag areas `.window_drag()`.
- `WindowOptions` covers size limits, resizability, transparency, borderless,
  visibility and macOS options (`MacWindowOptions::corner_radius`, shadow).
- More windows: `App::window(WindowSpec::new(key, spec))` returns a handle and
  a window to open later; `run_windows` builds several from displays;
  `App::overlay` makes edge overlays and HUDs that never activate.
  Headless tools take `--window KEY` and `--list-windows`.
- Tray icons (`rune::tray`), taskbar progress (`WindowHandle::set_taskbar`),
  jump lists, notifications (`rune-notify`), video (`Player`, `NativeSurface`),
  audio recording and system materials are in the bundled index; check each
  page's platform list before promising behaviour.

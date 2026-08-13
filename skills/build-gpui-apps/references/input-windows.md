# Production input, menus, and windows

Use this layer when the app owns editable text, clipboard behavior, drag and
drop, native menus, more than one window, or restored desktop state. These are
OS contracts, not just view styling. A control that looks correct but breaks
IME composition, Unicode ranges, close semantics, or focus is not production
ready.

The API names below match the research snapshot in [sources.md](sources.md).
Confirm every signature in the target's pinned GPUI source before copying it.

## Contents

- [Choose an ownership boundary](#choose-an-ownership-boundary)
- [Prefer an existing text component](#prefer-an-existing-text-component)
- [Model text without corrupting Unicode](#model-text-without-corrupting-unicode)
- [Implement the input handler contract](#implement-the-input-handler-contract)
- [Handle composition and marked text](#handle-composition-and-marked-text)
- [Connect text layout to the platform](#connect-text-layout-to-the-platform)
- [Build selection and caret behavior](#build-selection-and-caret-behavior)
- [Implement clipboard commands](#implement-clipboard-commands)
- [Implement drag and drop](#implement-drag-and-drop)
- [Route keys and actions](#route-keys-and-actions)
- [Build native menus](#build-native-menus)
- [Own multiple windows](#own-multiple-windows)
- [Restore desktop state](#restore-desktop-state)
- [Test the operating-system contract](#test-the-operating-system-contract)
- [Reject common shortcuts](#reject-common-shortcuts)
- [Review checklist](#review-checklist)

## Choose an ownership boundary

Put each responsibility in one obvious owner:

| Concern | Recommended owner |
|---|---|
| Document text and semantic selection | Document/model entity |
| Ephemeral composition/marked range | Focused editor entity |
| Shaped lines, hit-test map, caret bounds | Editor view/element cache |
| Copy/cut/paste commands | Typed actions handled by focused editor |
| Drag payload | Small typed value, not a view pointer |
| Application menu model | App registration and command state owner |
| Window identity and close policy | Window coordinator/app model |
| Restorable window state | Versioned persistence model |

Keep platform range conversion at the text boundary. Keep window restoration
out of individual row or control components. Do not let a render-local closure
become the only owner of a task, subscription, composition range, or window.

For collaborative or persistent documents, distinguish:

- semantic document revision;
- local selection and composition;
- save generation or transaction identity;
- window/view identity.

A window may close while the document remains open elsewhere. A view may move
to another window. A stale save or search result must not overwrite newer
state merely because its original window still exists.

## Prefer an existing text component

Before implementing `EntityInputHandler`, search the target for a maintained
text field/editor that already supplies:

- macOS, Windows, and Linux IME behavior;
- UTF-16 range conversion;
- grapheme-aware movement and deletion;
- bidirectional text and shaping;
- selection, caret, scrolling, and hit testing;
- clipboard and keyboard conventions;
- password/privacy behavior;
- accessibility semantics and announcements.

Reuse that component when its editing model fits. A custom editor is justified
for a specialized document model, rendering surface, or interaction that the
existing component cannot express. It is not justified merely to change
padding, borders, fonts, or focus-ring styling.

If wrapping a project editor, preserve its actions and state machine. Apply
visual treatment outside the editing core instead of forking input behavior.

## Model text without corrupting Unicode

Current GPUI input integration exposes platform selections as UTF-16 ranges,
while idiomatic Rust strings and many editor models use UTF-8 byte offsets.
These units are not interchangeable.

Use explicit types or names:

```rust
struct Utf8ByteRange(std::ops::Range<usize>);
struct Utf16CodeUnitRange(std::ops::Range<usize>);
```

The target API may provide `UTF16Selection`; use it at the platform boundary.
Internally, store a direction-aware selection rather than silently sorting it:

```rust
struct Selection {
    anchor_utf8: usize,
    head_utf8: usize,
}
```

Rules:

1. Validate or clamp offsets before slicing a `String`.
2. Never treat a UTF-16 code-unit index as a Rust byte index.
3. Convert both range ends against the same text revision.
4. Preserve selection direction where shift-extension behavior needs it.
5. Move and delete by grapheme cluster for user-visible characters.
6. Move by shaped visual position for left/right behavior in bidirectional text
   when the editor promises native navigation.
7. Keep line-break policy explicit: `\n`, platform line endings on import, and
   any soft-wrapped visual lines are different concepts.
8. Reject or reconcile platform callbacks that refer to an obsolete document
   revision.

Test conversion with:

- plain ASCII;
- `æ`, `ø`, and other multi-byte BMP characters;
- emoji outside the BMP, which occupy two UTF-16 code units;
- emoji sequences joined by zero-width joiners;
- combining marks such as `e` plus acute accent;
- flags and skin-tone modifiers;
- mixed right-to-left and left-to-right text;
- empty text and offsets at every boundary.

Do not write conversion logic as scattered arithmetic. Centralize it, document
the units, and property-test round trips over valid boundaries.

## Implement the input handler contract

In the pinned upstream snapshot, custom editing is integrated through
`EntityInputHandler`. Its contract includes methods equivalent to:

| Method | Responsibility |
|---|---|
| `text_for_range` | Return platform-visible text for a requested UTF-16 range |
| `selected_text_range` | Report the current selection in UTF-16 units |
| `marked_text_range` | Report active composition, if any |
| `unmark_text` | Commit/clear marked-text state according to platform semantics |
| `replace_text_in_range` | Replace selection/range with committed text |
| `replace_and_mark_text_in_range` | Update composition text and marked/selected subranges |
| `bounds_for_range` | Return screen/window geometry for IME candidate placement |
| `character_index_for_point` | Hit-test a point to a UTF-16 character index |

The exact types and extra arguments vary by revision. Read the trait in the
target checkout and a compiling input example before implementation.

Keep the mutation path single and testable:

```text
platform UTF-16 request
        |
        v
validate revision and convert units
        |
        v
document edit transaction
        |
        +--> update selection/composition
        +--> record undo grouping
        +--> notify observers
        +--> invalidate shaped layout
```

Every replacement must define:

- which range is used when the platform passes `None`;
- whether active marked text is replaced;
- where the new selection lands;
- whether the change joins the current undo group;
- whether it emits a domain event, save request, or accessibility update;
- how read-only or disabled state rejects the edit.

Do not call `cx.notify()` without mutating meaningful state, and do not mutate
editable state without notifying the view/model observers that render it.

## Handle composition and marked text

IME composition is a provisional editing session. Japanese, Chinese, Korean,
accent entry, emoji pickers, dictation, and other input methods may update the
same marked range many times before committing.

Maintain at least:

- current marked UTF-8 range, if any;
- selection inside the marked text;
- document revision/layout generation used by candidate geometry;
- styling needed to distinguish marked text without relying on color alone.

On `replace_and_mark_text_in_range`:

1. Resolve the replacement range against current selection/marked text.
2. Convert all incoming UTF-16 subranges safely.
3. Apply one provisional edit transaction.
4. Update the marked range and selection inside it.
5. Invalidate shaping and candidate geometry.
6. Notify once for the coherent state transition.

Do not:

- treat every composition update as committed text;
- trigger search, autosave, validation, or collaboration broadcast as though
  the user committed each intermediate candidate;
- discard composition because focus moved to an editor-owned candidate UI;
- delete one Rust byte on Backspace;
- render marked text at geometry from an older document revision.

Define what happens when the document changes remotely during composition.
Safe options include rebasing the marked range through the edit transform or
cancelling composition explicitly. Silent offset reuse is unsafe.

## Connect text layout to the platform

An input handler needs the layout produced for the current frame. The current
upstream examples shape text, retain line/layout data and bounds during
prepaint, then register an `ElementInputHandler` with
`window.handle_input(...)`.

Preserve this ordering:

1. Read the current document snapshot.
2. Shape lines with the actual font, size, width, and scale factor.
3. Build a hit-test map from shaped runs to UTF-8/document positions.
4. Save layout bounds and generation on the editor entity/element state.
5. Register the input handler for the focused editor.
6. Paint selection, marked text, glyphs, and caret from the same snapshot.

`bounds_for_range` must return useful geometry for candidate windows. Account
for:

- scroll offset;
- soft wraps;
- line height and baseline;
- scale factor;
- window/content coordinate conversion;
- selections that cross lines;
- a range outside the visible viewport;
- stale or missing layout during the first frame.

`character_index_for_point` must use shaped glyph positions, not average
character width. Ligatures, emoji, proportional fonts, and bidirectional runs
make arithmetic hit testing incorrect.

If no valid current layout exists, return the pinned API's safe fallback and
request a fresh frame; do not fabricate coordinates far from the editor.

## Build selection and caret behavior

A production editor needs a coherent selection state machine:

- click places the caret at a grapheme/shaped boundary;
- drag extends from the original anchor;
- double click selects the platform-appropriate word boundary;
- triple click selects a logical or visual line according to product policy;
- Shift extends from the stable anchor;
- keyboard movement preserves preferred horizontal position across lines;
- selection autoscrolls when dragging beyond the viewport;
- caret remains visible after edits and navigation;
- focus loss hides or de-emphasizes the caret without losing semantic
  selection unexpectedly;
- read-only selection remains copyable when product policy allows it.

Use stable pointer capture/drag state. Keep the original grab/selection anchor
through the gesture, and terminate cleanly on pointer up, cancellation, window
deactivation, or entity removal.

Blinking is motion and scheduled work. Stop caret timers when the editor is not
focused or visible. Restart predictably after input. Respect reduced-motion
policy if the product treats blinking as suppressible.

Expose the correct accessibility role, value, selection, read-only/disabled
state, and actions supported by the pinned GPUI/AccessKit layer. Do not make a
painted text surface the only representation assistive technology can reach.

## Implement clipboard commands

Current upstream provides application clipboard access through methods such as
`cx.read_from_clipboard()` and
`cx.write_to_clipboard(ClipboardItem::new_string(...))`. Confirm the pinned
item types and multi-format capabilities.

Route Copy, Cut, Paste, and Select All through typed actions handled in the
focused editor. Menus, shortcuts, accessibility actions, and pointer menus
should invoke the same semantic operations.

Copy:

- require a non-empty copyable selection;
- serialize only allowed data;
- offer plain text even when richer internal formats are supported;
- avoid logging clipboard contents;
- preserve line endings and normalization intentionally.

Cut:

- first establish that the edit is allowed;
- write the clipboard and delete through one user-visible command/undo group;
- define failure behavior if rich clipboard serialization fails;
- do not delete password/secret fields through a path that exposes contents.

Paste:

- choose supported format deliberately;
- normalize untrusted text size and line endings where required;
- replace the active selection/marked range through the same edit transaction
  used by typing;
- place the selection after inserted text;
- keep parsing or file I/O off the application thread;
- reject stale async paste results with a revision/generation check.

For password, token, recovery-code, or private fields, define copy/cut policy
explicitly and clear sensitive app-owned caches. Never include clipboard data
in telemetry, panic messages, test snapshots, or completion reports.

## Implement drag and drop

Current GPUI supports typed drag payloads through `.on_drag(...)` and matching
`.on_drop(...)` handlers. Confirm source and examples for the pinned revision.

Use a small payload containing identity and allowed operation:

```rust
#[derive(Clone)]
struct RowDrag {
    row_id: RowId,
    source_list: ListId,
}
```

Do not store a mutable entity pointer, whole document, secret, or render node in
the payload. Re-resolve IDs against current model state at drop time.

The drag state machine should cover:

1. Press threshold before drag begins.
2. Typed payload creation from current semantic identity.
3. Accessible preview that does not become the source of truth.
4. Valid/invalid target feedback.
5. Edge autoscroll where lists require it.
6. Move/copy/link operation policy and modifier keys.
7. Model transaction at drop.
8. Cancellation on Escape, source removal, window deactivation, or invalid
   target.
9. Focus and announcement after success or cancellation.

For files or external data, validate type, count, size, path/URL policy, and
permissions before starting work. Treat dropped content as untrusted input.

Provide a keyboard alternative for every essential reorder or move operation,
such as Move Up/Down actions or a destination picker. Drag-only workflows are
not accessible.

## Route keys and actions

Define typed actions once and route them through key contexts:

- application actions: New Window, Close Window, Quit;
- document actions: Save, Undo, Redo;
- editor actions: Copy, Cut, Paste, Select All, movement, deletion;
- surface actions: Activate, Cancel, Move Up/Down.

Scope bindings to the narrowest useful context. A text editor should consume
editing actions before an ancestor interprets the same key. Escape should close
only the topmost owned transient surface, then restore focus to its invoker.

Platform conventions differ. Represent the semantic action in shared code and
register platform-appropriate bindings/menu labels at the app boundary. Avoid
hard-coding `cmd-*` as the only cross-platform path.

Disabled commands need one source of truth. The key handler, menu item, toolbar
button, and accessibility action must agree about whether the command can run.
The semantic handler must still guard itself; a visually disabled control is
not authorization enforcement.

## Build native menus

Current upstream exposes `Menu`, `MenuItem`, and `cx.set_menus(...)`, including
typed action items and system menu roles/types. Follow the pinned menu example.

Build menus at application startup after actions are registered. Use platform
order and naming conventions, and connect items to the same actions used by
keyboard and UI controls.

Keep dynamic state coherent:

- enable Cut only for an editable non-empty selection;
- enable Paste only when a supported clipboard value can be accepted, if the
  platform/API permits that check;
- show checked state for persistent toggles;
- update menu state when focus, selection, document, or window ownership
  changes;
- avoid rebuilding menus from every render.

Use system menu types for About, Services, Hide, Window, and Quit when the
pinned platform layer provides them. Do not imitate a native app menu with an
in-window popover if the product expects normal desktop menu behavior.

Context menus should reuse command state and typed actions. Their focus and
dismissal semantics still require runtime testing.

## Own multiple windows

Create a coordinator that maps stable window identity to document/view state.
Avoid a global `current_window` assumption.

Decide explicitly:

- whether each window owns a new document, a view onto an existing document,
  or an independent utility surface;
- whether closing the last window quits the app;
- whether macOS keeps the app running with no windows;
- how New Window behaves when no document is active;
- whether dirty documents prompt, save, or cancel close;
- how tasks and subscriptions are cancelled on close;
- where focus moves when an auxiliary window closes.

The current upstream snapshot provides window enumeration and close observers,
including shapes such as `cx.windows()`, `cx.on_window_closed(...)`, and
window removal/close operations. Use the exact pinned source.

Window-bound async and subscriptions should use the `_in` family when required
by the target revision, such as `spawn_in`, `subscribe_in`, or `update_in`.
This preserves the correct window context and can follow a rehosted entity.
Do not capture a raw window handle into background work and assume it remains
valid.

Close flow should be a state machine:

```text
CloseWindow action
  -> resolve owning window/document
  -> clean? close
  -> dirty? request Save / Discard / Cancel
       -> Save: await owned save generation, then close on success
       -> Discard: close
       -> Cancel: restore focus and keep window
```

Prevent duplicate close prompts and stale save completions. A close observer is
for cleanup/coordination; it is too late to ask the user after destruction.

Test active and inactive window appearance. Controls should not imply active
accent/focus when their window is inactive. Avoid sending announcements from
background windows unless the event is globally important.

## Restore desktop state

GPUI window construction does not by itself define product restoration. Store
a small versioned semantic record, not framework entities or native handles:

```rust
struct RestoredWindowV1 {
    id: WindowId,
    kind: WindowKind,
    document_locator: Option<DocumentLocator>,
    bounds: LogicalBounds,
    display_hint: Option<DisplayId>,
    maximized: bool,
    selected_panel: PanelId,
}
```

Persist only stable, serializable state needed to reconstruct the experience.
Do not persist focus handles, subscriptions, tasks, shaped text layouts,
composition state, clipboard values, decrypted secrets, or transient dialogs.

Restore defensively:

1. Parse a versioned schema and migrate known older versions.
2. Validate document locators and permissions.
3. Match the stored display when still available.
4. Convert logical bounds using the current scale factor.
5. Clamp size and position so the titlebar/content remains reachable.
6. Fall back to centered/default bounds when displays changed.
7. Open primary windows before dependent utility windows.
8. Restore selection/scroll only after content loads and identities resolve.
9. Avoid stealing focus repeatedly while opening several windows.
10. Save a coherent snapshot after meaningful changes, not on every frame.

Use atomic persistence and a schema version. Corrupt state should fall back to a
safe default and produce a non-sensitive diagnostic, not prevent app startup.

Respect privacy. Recent documents and window titles can reveal sensitive
projects. Follow the product's encryption, retention, and private-window policy.

## Test the operating-system contract

Pure tests:

- UTF-8/UTF-16 round trips on every valid boundary;
- invalid/stale range handling;
- grapheme movement/deletion;
- selection direction and edit transforms;
- composition replacement and commit/cancel;
- command enabled-state reducer;
- drag target validation and reorder transaction;
- close/save/discard/cancel state machine;
- restoration migration and display clamping.

GPUI tests:

- focus and scoped key dispatch;
- copy/cut/paste actions using controlled clipboard state;
- composition callbacks and marked range;
- candidate bounds after scroll/resize;
- pointer selection and drag cancellation;
- menu action dispatch and checked/disabled refresh;
- two windows observing one model;
- window-specific task/subscription cleanup;
- last-window close policy;
- restoration opening the intended roots.

Runtime tests with real OS input:

- at least one non-Latin IME with several candidate updates before commit;
- emoji, combining marks, bidirectional text, and multiline selection;
- candidate window placement while scrolled and near display edges;
- standard platform shortcuts and menu items;
- external clipboard content and, if supported, rich formats;
- drag between lists/windows and cancellation;
- dirty close prompt in every branch;
- relaunch after moving/resizing windows across displays and scale factors;
- screen reader editing/selection announcements.

Simulated keystrokes are not proof of IME behavior. Cross-compilation is not
proof of native menus or window restoration. Record the exact platform and
input method used.

## Reject common shortcuts

Reject these implementations during review:

- indexing a Rust `String` with UTF-16 offsets;
- deleting `len - 1` byte for Backspace;
- committing each marked-text update as a final edit;
- average-character-width caret or hit testing;
- creating subscriptions or blink timers in `render`;
- a hidden text field used as an unexplained proxy without synchronized
  selection/composition geometry;
- pointer-only selection or drag-only reordering;
- separate menu, key, and toolbar handlers that drift apart;
- `cmd-*` bindings presented as cross-platform support;
- global mutable “active editor” or “current window” state;
- detached save/load tasks that outlive the document without revision guards;
- quitting on every last-window close without product/platform policy;
- restoring raw coordinates off-screen after a display change;
- serializing tasks, focus handles, native handles, clipboard data, or secrets;
- claiming a custom editor is production-ready after ASCII-only tests.

## Review checklist

- [ ] Existing maintained text/editor component considered first
- [ ] UTF-8, UTF-16, grapheme, visual, and line units named explicitly
- [ ] Full pinned `EntityInputHandler` contract implemented
- [ ] Composition stays provisional until commit/unmark semantics require it
- [ ] Layout generation matches candidate bounds and hit testing
- [ ] Selection, caret, autoscroll, focus, and accessibility are coherent
- [ ] Clipboard operations share one guarded edit path and protect secrets
- [ ] Drag payloads are typed IDs with cancellation and keyboard alternatives
- [ ] Keys, menus, context menus, and controls invoke the same typed actions
- [ ] Dynamic command enabled/checked state has one source of truth
- [ ] Window identity, close policy, tasks, and subscriptions have clear owners
- [ ] Restoration is versioned, clamped, private, and failure-tolerant
- [ ] Pure, GPUI, and real-platform tests cover Unicode and lifecycle edges
- [ ] Unverified IMEs, operating systems, or restoration paths are reported

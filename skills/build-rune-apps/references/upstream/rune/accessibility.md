> Upstream: [crates/rune/README.md § Accessibility](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#accessibility) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

## Accessibility

Every window and overlay exposes its elements to the OS accessibility API through
[AccessKit](https://accesskit.dev): UI Automation on Windows (Narrator, NVDA, JAWS, Voice
Access), NSAccessibility on macOS (VoiceOver, Voice Control), AT-SPI on Linux (Orca). The same
tree is what automation and testing tools drive. It comes with the default `accessibility`
feature (`crate::a11y`, `runtime/a11y`).

- **Free until asked**: nothing is built until an assistive client asks for a surface's tree.
  Then each turn that changed something the tree shows (a commit, a scroll, focus, the end of
  an animation) rebuilds it from the last frame and sends the nodes that changed. A turn that
  changed none of it costs one comparison.
- **Defaults from what an element already is**: its role (`El::role`, ARIA's names), its label
  (`El::label`, else its text; a button, list row, tab or tree row takes the text inside it),
  its key as the automation id (UIA `AutomationId`, `AXIdentifier`), focus, `El::level`,
  `El::expanded`, a selected item (`El::focus_selected`), a slider's steps, a text field's value,
  caret, selection and each line's characters, inline links, scroll viewports with their
  offsets, modal dialogs (the background leaves the tree), and secure text (never exposed).
  Plain layout boxes with no key, label or role join their parent, so the tree reads like the
  interface, not the layout.
- **Builders for the rest**: `description`, `a11y_value`, `range_value` and `range_step`,
  `checked` and `checked_mixed`, `disabled`, `read_only`, `invalid`, `sorted`, `a11y_hidden`,
  `live_region(LiveRegion::Polite)`, `position_in_set`, `shortcut_hint` and
  `active_descendant` (the highlighted row of a tree, table or suggestion list whose container
  or field keeps focus). An icon-only button needs `.label("Close")`. An `El::help` tooltip
  describes its element unless it repeats the name; `description("")` turns that off.
- **Actions** run the handlers a pointer or keyboard user reaches: click presses
  (`on_press`), focus focuses, increment and decrement step (`on_step`), set value and text
  selection edit through the field's editor (so `on_input_change` runs), set value on a slider
  with a `range_step` steps it that many times toward the number, expand and collapse
  press a disclosure, show context menu calls `on_secondary_press`, and scroll requests move
  the viewport. They skip hit testing, so a test that wants the pointer's path posts pointer
  input instead.
- **Virtual lists** expose their mounted rows only; the list reports how many rows it has and
  each row its index.
- **Tools**: `--tree` writes the tree under `"accessibility"` (role, key, name, value, states,
  actions, bounds in window points), `Runtime::accessibility_json` returns it to tests, and
  `Runtime::accessibility_tree` returns AccessKit's whole `TreeUpdate`, and
  `Runtime::accessibility_action(key, action, data)` runs an assistive action in a test.
  `RUNE_A11Y_LOG=1` logs when a client activates a surface's tree, each action, and each
  update's size and cost.

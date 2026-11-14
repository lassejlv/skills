> Upstream: [crates/rune-kit/README.md § Components](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-kit/README.md#components) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

## Components

`Combobox::new("models", &s.combo, &options, |s: &mut App| &mut s.combo)` composes
Popover, TextInput and virtual rows. Options carry stable ids, labels, details and disabled
state; `.current(..).on_choose(..)` binds selection. It filters case-insensitively, loops
ArrowUp/Down and Ctrl-N/P across enabled rows, scrolls keyboard choices into view, and ignores
selection keys during IME composition. Escape closes it. A keystroke's rows and the popover's
height land in its frame; `.animate_filtering(true)` crossfades the rows and springs the
height instead. `PopupList`, the list it shares with `@`-mention and `/`-command popovers,
takes the same switch, so rows an app's commit changes land at once even when the field it
follows animates its layout. The contract follows OpenCode's
`components/list` and `use-filtered-list`; Rune's fuzzy ranking
is its own, not bit-identical to fuzzysort. `rune-combobox--searchable` is its 200-row gallery
scene, and `rune-combobox--animated-filter` the same with the crossfade; there is no matching
combobox Storybook story to diff.

`TextInput::on_key` intercepts a focused field's keys before editing; `on_change` runs after
text changes and receives a `Tx`, for filtering and exact debounce wakes. `TextInput`, `TextArea`
and `TextField` also accept `.decorations(spans)` (or `.spans(spans)`) and `.rich_style(style)` for
attributed `TextEdit` marks, paragraph blocks and per-frame syntax highlights, and
`.pill_style(f)` / `.pill_icon(f)` / `.pill_colors(bg, fg)` for `@` mention pills (build the edit with
`TextEdit::rich()` for formatting keys and rich paste; see
[`examples/rich_editor.rs`](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-kit/examples/rich_editor.rs)):

![rich editor](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/rich-editor.png)

`k.selection()` is the selection highlight TextInput and TextArea draw. Pass it to Rune's
selectable text so a selected command line looks like a selected field:
`text(cmd).selectable(true).selection_color(k.selection())`. `rune-text--selectable-help` in the
gallery shows both, with an icon button explained by `.help`.

Button (10 variants × 3 sizes × 5 states), IconButton, Switch (compact, standard), Checkbox,
RadioGroup/RadioItem, TextInput, TextArea, TextField (older), Field, Select (inline and field
triggers, grouped), Popover, Menu (compact and standard, checkbox/radio items, submenus,
context menus via `.at(x, y)`), Tooltip (compact, standard, large), HoverCard, Toast and
ToastRegion, Card, List, Accordion, Collapsible, Badge, Divider, Keybind, Spinner, Loader,
Progress, ProgressCircle, SegmentedControl.

`Button::new(label).rolling("import-label")` rolls the label's changed characters
(`RollingText`) and springs the button's width with it; `.label_with(|font, ink| ..)` draws any
label element in the button's font and ink. The text stays the button's accessible label.
A `RollingText` reads as its whole label wherever text is looked up: its row's `text` in
`--tree` and `ElementInfo::text`, so tests find it by text as they find a plain `text`.

### Accessibility

Every component reports what a screen reader needs through Rune's accessibility tree (Rune's
README, "Accessibility"): its role, a name, a value where it has one, its states and the actions
assistive technology runs through the same handlers as pointer and keys.

- **Names**: a control's label, else the text it shows. Give every `IconButton` a `.label` (or
  a `.help`, which names it when unlabelled). `Select`, `Combobox`, `SegmentedControl`,
  `TextInput`, `TextArea`, `ShortcutRecorder`, `ProgressCircle` and `Popover` take `.label` for
  the name when no visible label says it; a text field falls back to its placeholder.
- **Values**: a select or combobox reads its chosen option, progress its percentage, a pane's
  grip its width (increment and decrement resize it), a shortcut recorder its keys.
- **States**: checked (checkbox, switch, radio, segment, checked menu item, task), expanded or
  collapsed (accordion, collapsible, menu and popover triggers given `.expanded`, select,
  combobox, submenu, tree row, sidebar section, sidebar toggle, diff file), selected and place
  in the set (list, select, popup list, table, tree and sidebar rows), disabled, modal
  (dialog, open menu and select).
- **Descriptions and live regions**: tooltips and help text describe their control; a field's
  error describes it and is announced; toasts and badges are polite live regions.
- **Hidden**: decorative icons, dots, rules, guides and the words a control's name already
  says stay out of the tree.

`tests/a11y` checks each component's tree, by assertion and against a golden under
`tests/a11y/golden/` (`RUNE_BLESS=1` rewrites them).

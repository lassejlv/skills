# rune-kit: components, theme and shell

rune-kit is Rune's component crate. It follows `@opencode/ui`'s names, variants,
sizes and states, reads only semantic tokens from a `Kit`, and knows nothing of
any brand. Upstream: [use](upstream/kit/use.md),
[components](upstream/kit/components.md), [app shell](upstream/kit/app-shell.md),
[tree and table](upstream/kit/tree-and-table.md), [markdown](upstream/kit/markdown.md).

## When to recommend it

Recommend it (and ask; see SKILL.md) for anything with standard controls:
settings, forms, lists with selection, menus, selects, comboboxes, dialogs,
toasts, sidebars, trees, tables, markdown, diffs. It brings keyboard behaviour,
focus, disabled states, accessibility roles and states, reduced-motion handling
and a light/dark theme that core `rune` leaves to the app.

Core `rune` alone fits a pixel-specific design system (a Paper file with its own
controls), a canvas, a game-like surface, or a tiny utility. Such an app can
still take single behaviour-heavy components (TextInput, Select, Menu) from
rune-kit once that choice is made; theme them with `Kit::from_palette` from the
app's own colours.

## Theme

```rust
let k = rune_kit::Kit::neutral(cx.system_dark());          // plain theme from rune::tok
let k = rune_kit::Kit::from_palette(rune_kit::PaletteSeed { // three opaque colours
    bg: t.color("bg"), fg: t.color("text"), accent: t.color("accent"),
});
```

- Build the `Kit` inside `view` (cheap), from `cx.system_dark()` or the app's
  appearance setting, so theme switches and the window's blend mode follow.
- `from_palette` derives layers, borders, hover, press and contrast-checked
  secondary text; override fields afterwards (`k.radius.sm = 3.0`,
  `k.c.border_focus = ..`).
- Window background: `k.c.page`. Cards: `k.c.bg_base`. Text: `k.c.text_base`,
  `text_muted`, `text_faint`. Type: `k.ty.body`, `k.ty.small`, `k.ty.ui_medium`, …
- A brand gets its own theme crate filling `Kit`; components don't change.
  `rune-theme-opencode` is OpenCode's and only for OpenCode surfaces.

## Builders

```rust
Button::new("Save").variant(ButtonVariant::Contrast).on_press(|s: &mut App| s.save()).build(&k)
Switch::new(s.sync).label("Sync").on_toggle(|s: &mut App| s.sync = !s.sync).build(&k)
Checkbox::new(task.done).label(&task.title).on_toggle(move |s: &mut App| s.toggle(id)).build(&k)
TextInput::new(&s.draft).placeholder("New task").label("New task").width(None)
    .on_edit(|s: &mut App| &mut s.draft).on_submit(|s: &mut App, _| s.add()).build(&k)
IconButton::new(&glyphs::CLOSE).label("Close").on_press(..).build(&k)
```

- Every builder ends in `.build(&k)` and returns an `El`; key it afterwards:
  `.build(&k).key("save")`.
- Handlers go through the builder so `.disabled(true)` drops them.
- `.state(State::Hover | Pressed | Focus | Disabled)` forces a look for scenes
  and stories; at rest the runtime drives hover and press.
- Icon-only controls need `.label(..)` (or `.help(..)`); fields without a
  visible label take `.label(..)`.
- Variants: `ButtonVariant::{Neutral, Contrast, Submit, Outline, Ghost,
  GhostMuted, GhostFaint, Danger, Warning, Loading}`; sizes through
  `.control_size(ControlSize::..)`. Check the enum at the pinned rev.

## Overlays need the root layer

Popover, Menu, Select, Combobox, Tooltip, HoverCard and toasts render their
contents above everything:

```rust
let mut layer = Vec::new();
let model = Select::new("model", &MODELS)
    .current(Some(&s.model))
    .open(s.open == Some("model"))
    .on_toggle(|s: &mut App| s.toggle("model"))
    .on_close(|s: &mut App| s.open = None)
    .on_choose(|s: &mut App, v: &str, _: &mut Tx| s.model = v.into())
    .build(&k, &mut layer);                 // returns the trigger
rune_kit::root(body.child(model), layer)    // the view's root
```

- State says which overlay is open (`Option<&'static str>` or an enum); the view
  passes `.open(..)` and clears it in `on_close` and on choice.
- Only the view's outermost element should be `rune_kit::root`; one layer per
  window.
- Context menus: store `Some(point)` from `on_secondary_press`, then
  `context_menu("menu", trigger, s.point).item(..).on_close(..).build(&k, &mut layer)`.

## Keys inside components

rune-kit keys its own parts (`label`, `value`, `icon`, `control`, `kit-root`).
Give each component a key after `build`, key the row around it from the domain
id, and address it by path in tests and scripts: `task-3/check`.

## App shell

`rune_kit::shell` is a desktop window frame: `SplitView` with a resizable,
collapsible `Sidebar` (`PaneState` the app owns and persists), a `Toolbar`, an
optional inspector, traffic-light clearance (`.titlebar_inset(cx.titlebar_inset())`)
and a window-drag band. `Sidebar::virtual_rows` for long histories,
`SidebarRow::reorder` for drag-to-reorder, `Page` for full-window screens that
match the split view. `shell::is_sidebar_toggle(ev)` from `on_key` gives ⇧⌘B.
Run `cargo run -p rune-kit --example shell` in a Rune checkout to see it.

## Data views

`Tree` (with `FileTree` for paths) and `Table` (`TableState`, sortable
`TableColumn`s) are virtualised, one focusable control each, with a cursor in
app state. `Markdown` (feature `markdown`, plus `mermaid` for diagrams) renders
streaming markdown with code highlighting.

## Accessibility

Components report role, name, value and states (checked, expanded, selected,
disabled, modal); toasts and badges are polite live regions; decorative parts
stay out of the tree. rune-kit tests each component's tree against goldens.
Your job: names for icon-only controls and unlabeled fields, and checking the
app's `--tree` output.

## Gallery

`examples/kit-gallery` renders every component scene; `--kit neutral` and
`--kit palette` show the non-OpenCode themes. The stills in `demo/kit/`
(see the [examples map](examples-map.md)) show what each component should look
like.

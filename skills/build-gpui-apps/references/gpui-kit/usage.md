# gpui-kit Usage Guide

**Contents:** [Setup](#setup) · [Component Types](#component-types) · [Common Components](#common-components) (Button, Input, Select, Checkbox, Icon, Dialog, Notification, Tabs, Tooltip, Form, List) · [Theming](#theming) · [Layout Helpers](#layout-helpers) · [Overlay Layers](#overlay-layers-dialogs-sheets-notifications) · [Shared Traits](#shared-traits)

## Setup

Use the [tested application recipe](recipes.md) for complete examples and their verification command. Store subscription handles on the owning view; binding one to a constructor-local variable alone does not keep it alive after construction.

### 1. Cargo.toml

```toml
[dependencies]
gpui-kit = "0.7.0" # re-exports GPUI, platform, base, component and the default icons; Shell is a separate host dependency
```

### 2. Initialization

```rust
fn main() {
    gpui_kit::application()
        .with_assets(gpui_kit::assets::Assets)
        .run(|cx| {
            gpui_kit::init(cx);
            gpui_kit::open_window(WindowOptions::default(), cx, |window, cx| {
                cx.new(|cx| MyApp::new(window, cx))
            }).expect("Failed to open window");
        });
}
```

The current Kit helper wraps your content entity in `Root`, which renders
its own overlays. Return the content view, not another `Root`. If you use
GPUI's low-level `cx.open_window` deliberately, create one `Root` yourself.
Older Kit releases had a different overlay contract; inspect the lockfile and
read [Getting Started](upstream/docs/getting-started.md) and
[Window](upstream/docs/window.md) before changing an existing entrypoint.

---

## Component Types

### Stateless (most components)

Used directly in `render`, no stored state:

```rust
use gpui_kit::component::button::{Button, ButtonVariants};

impl Render for MyView {
    fn render(&mut self, _: &mut Window, _: &mut Context<Self>) -> impl IntoElement {
        Button::new("btn").primary().label("Submit")
            .on_click(|_, _, _| println!("clicked"))
    }
}
```

### Stateful (Input, Select, Combobox, etc.)

Require an `Entity<State>` stored in your view:

```rust
use gpui_kit::component::input::{Input, InputState};

struct MyView {
    name: Entity<InputState>,
}

impl MyView {
    fn new(window: &mut Window, cx: &mut Context<Self>) -> Self {
        Self {
            name: cx.new(|cx| InputState::new(window, cx).placeholder("Your name")),
        }
    }
}

impl Render for MyView {
    fn render(&mut self, _: &mut Window, cx: &mut Context<Self>) -> impl IntoElement {
        Input::new(&self.name)
    }
}
```

---

## Common Components

### Button

```rust
use gpui_kit::component::button::{Button, ButtonGroup, ButtonVariants};

// Variants
Button::new("btn").label("Default")
Button::new("btn").primary().label("Primary")
Button::new("btn").danger().label("Delete")
Button::new("btn").warning().label("Warning")
Button::new("btn").success().label("Success")
Button::new("btn").ghost().label("Ghost")
// Use Link for external URLs; use ghost/outline buttons for in-app commands.

// States
Button::new("btn").label("Text").disabled(true)
Button::new("btn").label("Text").loading(true)
Button::new("btn").label("Text").selected(true)

// With icon
Button::new("btn").icon(IconName::Plus).label("Add")

// Sizes
Button::new("btn").xsmall().label("XS")
Button::new("btn").small().label("S")
Button::new("btn").large().label("L")

// Group
ButtonGroup::new("group")
    .child(Button::new("a").label("A"))
    .child(Button::new("b").label("B"))
    .on_click(|indices, _, _| { /* selected indices */ })
```

### Input

```rust
use gpui_kit::component::input::{Input, InputState};

// State setup (in new/init)
let input = cx.new(|cx| InputState::new(window, cx)
    .placeholder("Enter text...")
    .default_value("Hello")
);

// Render
Input::new(&input)
Input::new(&input).cleanable(true)           // clear button
Input::new(&input).disabled(true)
Input::new(&input).prefix(Icon::new(IconName::Search).small())
Input::new(&input).suffix(Button::new("b").ghost().icon(IconName::X).xsmall())
Input::new(&input).content_type(InputContentType::Password)
Input::new(&input).mask_toggle()             // password reveal toggle
Input::new(&input).appearance(false)         // remove default border/bg

// Reading value
let value = input.read(cx).value();

// Keep this subscription in the owning view (for example, `_subscriptions`).
self._subscriptions.push(cx.subscribe_in(&input, window, |view, state, event, window, cx| {
    match event {
        InputEvent::Change => { let v = state.read(cx).value(); }
        InputEvent::PressEnter { .. } => { /* submit */ }
        InputEvent::Focus | InputEvent::Blur => {}
    }
}));
```

### Select

```rust
use gpui_kit::component::select::{Select, SelectState};

// Simple string list
let state = cx.new(|cx| {
    SelectState::new(vec!["Apple", "Orange", "Banana"], Some(IndexPath::default()), window, cx)
});

// Render
Select::new(&state)
Select::new(&state).placeholder("Pick one")

// Reading selection
let selected = state.read(cx).selected_item();
```

### Checkbox / Switch / Radio

```rust
use gpui_kit::component::{checkbox::Checkbox, switch::Switch};

// Stateless (controlled)
Checkbox::new("cb").checked(self.checked)
    .on_change(cx.listener(|this, checked, _, cx| {
        this.checked = *checked;
        cx.notify();
    }))

Switch::new("sw").checked(self.enabled)
    .on_change(cx.listener(|this, checked, _, cx| {
        this.enabled = *checked;
        cx.notify();
    }))
```

### Icon

```rust
use gpui_kit::component::{Icon, IconName};

Icon::new(IconName::Check)
Icon::new(IconName::Search).small()
Icon::new(IconName::Plus).large().text_color(cx.theme().primary)
```

### Dialog

```rust
use gpui_kit::component::dialog::{Dialog, DialogAction, DialogClose, DialogFooter};

// Open from window context. `footer` takes an element, not a closure.
// DialogClose dismisses the dialog, so no manual close call is needed.
window.open_dialog(cx, |dialog, _, _| {
    dialog
        .title("Export Report")
        .child("Choose a destination for the exported file.")
        .footer(
            DialogFooter::new()
                .gap_2()
                .child(DialogClose::new().child(
                    Button::new("cancel").label("Cancel").outline(),
                ))
                .child(DialogAction::new().child(
                    Button::new("export").label("Export").primary(),
                )),
        )
});
```

### AlertDialog

Use `AlertDialog` — not `Dialog` — to confirm a consequential action. It is not
overlay-closable and has no close button, so the choice must be made. Name the
object in the title and the result on the confirming button; see the Design
Guides for the copy rules.

```rust
use gpui_kit::component::{button::ButtonVariant, dialog::DialogButtonProps};

window.open_alert_dialog(cx, |alert, _, _| {
    alert
        .title("Remove “Roadmap”?")
        .description("Files on disk aren’t deleted.")
        .button_props(
            DialogButtonProps::default()
                .ok_text("Remove")
                .ok_variant(ButtonVariant::Danger)
                .on_ok(|_, _, _| true),
        )
});
```

### Notification

```rust
// Simple string message
window.push_notification("Saved successfully!", cx);

// With type variant
window.push_notification(
    Notification::new("Upload complete").info().message("File uploaded"),
    cx,
);
```

### Tabs

The view retains `active_tab: usize`. Read the
[current Tabs page](upstream/component/tabs.md) for dynamic-tab composition.

```rust
use gpui_kit::component::tab::{Tab, TabBar};

TabBar::new("tabs")
    .selected_index(self.active_tab)
    .on_click(cx.listener(|view, index, _, cx| {
        view.active_tab = *index;
        cx.notify();
    }))
    .child(Tab::new().label("Overview"))
    .child(Tab::new().label("Settings"))
    .child(Tab::new().label("Logs"))
```

### Tooltip

```rust
// On any element with .id(), add .tooltip():
div()
    .id("my-btn")
    .tooltip(|window, cx| Tooltip::new("Delete item").build(window, cx))
    .child("Delete")

// Or on a Button directly:
Button::new("btn").icon(IconName::Trash).tooltip("Delete")
```

### Form

```rust
use gpui_kit::component::form::{v_form, h_form, field};

// Vertical form
v_form()
    .child(field().label("Name").child(Input::new(&self.name)))
    .child(field().label("Email").child(Input::new(&self.email)))
    .footer(Button::new("submit").primary().label("Submit"))

// Horizontal label alignment
h_form()
    .child(field().label("Username").child(Input::new(&self.username)))
```

### List (searchable, virtualized)

```rust
use gpui_kit::component::list::{List, ListState, ListDelegate, ListItem, ListEvent};

// Implement ListDelegate for your data type, then:
let list_state = cx.new(|cx| ListState::new(MyDelegate::new(), window, cx));

// Render
List::new(&list_state)
// Keep this subscription in the owning view, alongside list_state.
self._subscriptions.push(cx.subscribe(&list_state, |this, _, event, cx| {
    if let ListEvent::Select(index_path) = event {
        // handle selection
    }
}));
```

---

## Theming

```rust
use gpui_kit::component::ActiveTheme as _;

// Access colors
cx.theme().primary
cx.theme().background
cx.theme().foreground
cx.theme().border
cx.theme().surface
cx.theme().muted
cx.theme().destructive

// Use in styles
div()
    .bg(cx.theme().surface)
    .text_color(cx.theme().foreground)
    .border_color(cx.theme().border)
```

### Switch Theme

```rust
use gpui_kit::component::{Theme, ThemeMode};

// Switch light/dark: loads that mode's registered theme
Theme::change(ThemeMode::Dark, None, cx);
// or, as one edit among others
Theme::update(cx, |theme| theme.mode = ThemeMode::Dark);

// Load a named theme
Theme::update(cx, |theme| theme.apply_config(&theme_config));

// Edit fields; `update` keeps colors, tokens and the Base projection in step
Theme::update(cx, |theme| theme.radius = px(8.));
```

---

## Layout Helpers

`gpui_kit::component` extends GPUI with convenient layout methods:

```rust
h_flex()    // div().flex().flex_row().items_center()
v_flex()    // div().flex().flex_col()

// Common patterns
h_flex().gap_2().items_center()
    .child(Icon::new(IconName::User))
    .child(label("Username"))

v_flex().gap_4().p_4()
    .child(Input::new(&self.name))
    .child(Input::new(&self.email))
    .child(Button::new("submit").primary().label("Submit"))
```

---

## Overlay Layers (Dialogs, Sheets, Notifications)

Current `Root` owns and renders the overlay layers. Open them through
`gpui_kit::component::WindowExt`; do not manually append
`Root::render_dialog_layer`, `render_sheet_layer`, or
`render_notification_layer` to application content. Do not double-wrap the
content returned to `gpui_kit::open_window`.

See [Window](upstream/docs/window.md), [Dialog](upstream/component/dialog.md),
[Sheet](upstream/component/sheet.md), and
[Notification](upstream/component/notification.md) for the current contract.

---

## Shared Traits

Builders return the component so methods can be chained. Constructors follow component families: controls take a stable ID, retained controls take state, and compound parts may take no arguments. See [component conventions](conventions.md).

- `Sizable`: `.xsmall()` / `.small()` / `.medium()` (default) / `.large()`
- `Disableable`: `.disabled(bool)`
- `Selectable`: `.selected(bool)`
- `Styled`: any GPUI style methods (`.w()`, `.bg()`, `.p_2()`, etc.)

For any component not covered here, fetch its doc from:
`https://gpui-kit.com/component/{name}.md`


> Merged from [GPUI Kit skill](https://github.com/longbridge/gpui-kit/blob/main/skills/gpui-kit/references/usage.md). [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Imported 2026-09-28; local links and version-sensitive guidance adapted. The current documentation and locked source take precedence over example signatures.

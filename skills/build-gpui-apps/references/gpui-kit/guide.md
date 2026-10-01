# GPUI Kit components and mechanisms

Applications use `gpui-kit` for the UI stack. GPUI is `use gpui_kit::*;`, and
each layer is reachable by name: `gpui_kit::component` (styled components),
`gpui_kit::base` (unstyled behavior), `gpui_kit::assets` (default icons),
`gpui_kit::platform`.

Other application dependencies are allowed. Add `gpui-shell` separately only
when hosting JavaScript extensions.

Start with [component-family conventions](conventions.md) to choose the constructor, state owner, event, and layout contract for the task. Learn the family once, then verify the specific component supports the capability.

For a complete view with retained state, subscriptions, and overlay ownership,
read [the upstream-tested application recipe](recipes.md). Its documented
upstream test result is separate from compilation in a downstream project.

## Read the Guides First

Two guides hold the rules this skill assumes. They are requirements, not
inspiration. Read the guide file itself; do not answer from this page, from a
similar file in the codebase, or from training data.

| Guide                                                  | Read before                                                                                                                   |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| [Design Guides](upstream/docs/design-guides.md)          | Choosing components, layout, spacing, hierarchy, color, density, interaction states, overlays, motion, interface copy          |
| [Coding Guides](upstream/docs/coding-guides.md)           | Crate layering, `RenderOnce` vs `Entity<T>`, state ownership, `ElementId`, events, focus, async, public API, naming, testing |

Read the Design Guides first for a visible change. Both normative guides are
bundled in this merged skill; no separate skill installation is needed.
For a new screen read the full Design Guides; for a narrow change read
"Design thesis", "Start from the task", and the affected sections. Always
finish with the accessibility and design review checklists.

Follow the [framework choice policy](../../SKILL.md#choose-the-framework-first)
before adopting or migrating to Kit. The catalog below is a family-oriented
quick reference merged from the installed skill. The
[complete current catalog](upstream/index.md) includes all documented components,
Base primitives, Shell APIs, and application guides; consult the individual
page and locked source for exact constructors, imports, and feature gates.

### Coding Guides section map

Read the whole guide for a new crate, module, or feature. For a narrow change,
read "Architecture at a glance" and "Rules for coding agents" first, then the
section for the change (`grep -n '^## ' upstream/docs/coding-guides.md`).

| Section                              | Read when                                                              |
| ------------------------------------ | ---------------------------------------------------------------------- |
| Architecture at a glance             | Always; crate layering, ownership boundary                             |
| Bootstrap and root ownership         | `main`, `init`, `Root`, window creation, app-level state               |
| Understand GPUI's phases and contexts | Anything touching `App`, `Window`, `Context<T>`, render vs update      |
| Choose the right unit                | Deciding `RenderOnce` vs `Entity<T>` vs custom `Element`               |
| State ownership                      | Where a piece of state lives, who mutates it, `Entity<State>` handles  |
| Stable identity                      | `ElementId`, lists, repeated elements, keyed state                     |
| Rendering and composition            | `render`, builder chains, `when`/`map`, child composition              |
| Behavior and presentation boundary   | `gpui-base` vs `gpui-component` vs application code                    |
| Theme and styling                    | `cx.theme()`, tokens, `Styled`, sizes, variants                        |
| Events, actions, and focus           | `cx.emit`, `subscribe`, `actions!`, keybindings, `FocusHandle`         |
| Async work and side effects          | `cx.spawn`, `background_spawn`, `Task`, I/O, timers                    |
| Layout, measurement, and scrolling   | Flex layout, sizing, `overflow`, scroll handles, measuring             |
| Lists, tables, and large data        | `VirtualList`, `List`, `DataTable`, delegates, large collections       |
| Public API design                    | Anything `pub`: builders, private fields, setter and reader naming     |
| Platform and capability boundaries   | macOS/Windows/Linux/wasm differences, feature gates                    |
| File and naming conventions          | New files, modules, type and method names, `Kind` suffix, `Context`    |
| Testing strategy                     | What to test, `#[gpui_kit::test]`, `TestAppContext`                    |
| Performance rules                    | Render cost, allocation, re-render triggers                            |
| Common failure modes                 | Before finishing; invented APIs, state in render, index ids            |
| Rules for coding agents              | Always when an agent writes code                                       |
| Implementation checklist             | Before finishing; run every item against the work                     |

### Non-negotiables

A floor, not a substitute for the guides.

- **Never invent an API.** Search the current source for the real signature.
  Do not translate a React, CSS, or older-GPUI example by analogy; a
  plausible-looking method that does not exist is the most common failure.
- **One UI entry dependency.** Applications use `gpui-kit` for the GPUI stack. Other application dependencies are allowed; `gpui-shell` is separate when hosting JavaScript extensions. GPUI is
  `use gpui_kit::*;`; the layers are `gpui_kit::component`, `gpui_kit::base`,
  `gpui_kit::assets`, `gpui_kit::platform`.
- **Framework owns behavior, application owns presentation.** Do not put
  colors, sizing, or layout in `gpui-base`; do not put interaction behavior in
  application styling code.
- **Stable identity.** Repeated elements need domain-derived `ElementId`s, not
  list indexes.
- **No `pub` fields across the seam.** Public data types use builders and
  reader methods.
- **Spell `Context` out.** `cx` is GPUI's; name anything else after what it
  holds.

## Documentation

- **Find a task/component page**: use `https://gpui-kit.com/llms.txt`, then load its Markdown page.
- **Full reference**: `https://gpui-kit.com/llms-full.txt` is available when broad reference is actually needed
- **Per-component API**: fetch `https://gpui-kit.com/component/{name}.md`,
  e.g. `button.md`, `input.md`, `select.md`, `dialog.md`, `data-table.md`
- **Any site page** can be fetched as Markdown by appending `.md` to the URL

## Quick Reference

Setup and examples: [usage.md](usage.md).

```rust
use gpui_kit::*;

gpui_kit::application()
    .with_assets(gpui_kit::assets::Assets)
    .run(|cx| {
        gpui_kit::init(cx);                       // first, before anything else
        // Return the content Entity; Kit wraps it in Root and owns overlays.
        // gpui_kit::open_window(options, cx, |window, cx| cx.new(|cx| MyView::new(window, cx)))
    });
```

- **Stateless** (`RenderOnce`): build in `render`:
  `Button::new("save").primary().label("Save").on_click(|_, _, _| {})`
- **Stateful**: hold `Entity<State>` in the view, pass a reference in `render`:
  `let input = cx.new(|cx| InputState::new(window, cx));` then `Input::new(&self.input)`
- **Sizes**: `.xsmall()` `.small()` `.medium()` (default) `.large()`
- **Theme**: `cx.theme().primary` · `.background` · `.foreground` · `.border` · `.muted`
- **Overlays**: `window.open_dialog(...)`, `open_sheet(...)`, `push_notification(...)`
  via `gpui_kit::component::WindowExt`

## Component Catalog

Import paths are relative to `gpui_kit::component::`, so `input::{Input, InputState}`
means `use gpui_kit::component::input::{Input, InputState};`. For the full API
fetch the component's `.md` doc.

### Added in 0.7.0

Read the [release guide](v0.7.0.md) for migration-sensitive behavior; the full
pages below describe composition, state, events, and keyboard contracts.

| Component | Import | Use |
| --- | --- | --- |
| [Toolbar / ToolbarGroup](upstream/component/toolbar.md) | `toolbar::{Toolbar, ToolbarGroup}` | Command rows with grouped controls, density propagation, and arrow-key navigation |
| [Questionnaire](upstream/component/questionnaire.md) | `questionnaire::{Questionnaire, QuestionnaireState}` | Retained single/multiple-choice and freeform workflows with validation, navigation, and submission |
| [TimeField](upstream/component/time-field.md) | `time_field::{TimeField, TimeFieldState, TimePrecision, HourCycle}` | Segmented time editing; also supported by single-mode DatePicker |

### Input & Form

| Component     | Import                                          | Notes                                        |
| ------------- | ----------------------------------------------- | -------------------------------------------- |
| `Input`       | `input::{Input, InputState}`                    | Stateful. Text, password, mask, validation   |
| `Textarea`    | `input::{Textarea, TextareaState}`              | Stateful. Multi-line text                    |
| `Editor`      | `input::{Editor, EditorState}`                  | Stateful. Code editor, `tree-sitter` feature |
| `NumberInput` | `input::{NumberInput, NumberInputEvent}`        | Stateful. Numeric with step                  |
| `OtpInput`    | `input::OtpInput`                               | Stateful. One-time password                  |
| `Select`      | `select::{Select, SelectState}`                 | Stateful. Dropdown picker                    |
| `Combobox`    | `combobox::{Combobox, ComboboxState}`           | Stateful. Searchable select                  |
| `Checkbox`    | `checkbox::Checkbox`                            | Controlled. `on_change` receives `&bool`       |
| `Switch`      | `switch::Switch`                                | Stateless. Toggle                            |
| `Radio`       | `radio::{Radio, RadioGroup}`                    | Stateless.                                   |
| `Slider`      | `slider::{Slider, SliderState}`                 | Stateful.                                    |
| `Toggle`      | `button::Toggle`                                | Stateless.                                   |
| `Rating`      | `rating::Rating`                                | Stateless.                                   |
| `Stepper`     | `stepper::Stepper`                              | Stateless. Multi-step progress               |
| `ColorPicker` | `color_picker::{ColorPicker, ColorPickerState}` | Stateful.                                    |
| `DatePicker`  | `date_picker::{DatePicker, DatePickerState}`    | Stateful.                                    |
| `Calendar`    | `calendar::{Calendar, CalendarState}`           | Stateful. Inline month view                  |
| `Form`        | `form::{Form, Field}`                 | Layout container for form fields             |

### Display & Feedback

| Component   | Import                                    | Notes                                 |
| ----------- | ----------------------------------------- | ------------------------------------- |
| `Button`    | `button::{Button, ButtonGroup}`           | Stateless. Primary UI action          |
| `Icon`      | `{Icon, IconName}`                        | Stateless. Lucide icons               |
| `Badge`     | `badge::Badge`                            | Stateless.                            |
| `Tag`       | `tag::Tag`                                | Stateless. Closable tags              |
| `Avatar`    | `avatar::Avatar`                          | Stateless.                            |
| `Label`     | `label::Label`                            | Stateless. Form label                 |
| `Kbd`       | `kbd::Kbd`                                | Stateless. Keyboard key display       |
| `Alert`     | `alert::Alert`                            | Stateless. Info/success/warning/error |
| `Spinner`   | `spinner::Spinner`                        | Stateless. Loading indicator          |
| `Skeleton`  | `skeleton::Skeleton`                      | Stateless. Loading placeholder        |
| `Shimmer`   | `shimmer::{ShimmerText, ShimmerStyle}`    | Stateless. Streaming-text shimmer     |
| `Marker`    | `marker::{Marker, MarkerVariant}`         | Stateless. Inline status marker       |
| `Progress`  | `progress::{Progress, ProgressCircle}`    | Stateless.                            |
| `Tooltip`   | `tooltip::Tooltip`                        | Via `.tooltip()` on elements          |
| `HoverCard` | `hover_card::{HoverCard, HoverCardState}` | Stateful.                             |
| `Clipboard` | `clipboard::Clipboard`                    | Stateless. Copy button                |
| `TextView`  | `text::TextView`                          | `TextView::markdown(id, text)`, HTML too |
| Image       | `gpui_kit::{img, ImageSource, ObjectFit}` | GPUI's `img()` element                |

### Overlay & Popups

| Component        | Import                                            | Notes                                    |
| ---------------- | ------------------------------------------------- | ---------------------------------------- |
| `Dialog`         | `dialog::Dialog` + `WindowExt`                    | Via `window.open_dialog(...)`            |
| `AlertDialog`    | `WindowExt`                                       | Via `window.open_alert_dialog(...)`      |
| `Sheet`          | `sheet::Sheet` + `WindowExt`                      | Side panel, via `window.open_sheet(...)` |
| `Notification`   | `notification::Notification` + `WindowExt`        | Via `window.push_notification(...)`      |
| `Popover`        | `popover::Popover`                                | Floating overlay                         |
| `Menu`           | `menu::{PopupMenu, DropdownMenu}`                 | Context menus                            |
| `DropdownButton` | `button::DropdownButton`                          | Button with dropdown menu                |
| `Command`        | `command::{Command, CommandState, CommandGroup}`  | Stateful. Command palette                |
| Focus trap       | `FocusTrapElement`                                | `.focus_trap(id, &handle)` on a container; `Dialog` and `Sheet` have it built in |

### Navigation & Layout

| Component         | Import                                                                   | Notes                     |
| ----------------- | ------------------------------------------------------------------------ | ------------------------- |
| `Tabs` / `TabBar` | `tab::{Tab, TabBar}`                                                     | Tabbed interface          |
| `Sidebar`         | `sidebar::{Sidebar, SidebarMenu, ...}`                                   | App navigation panel      |
| `TitleBar`        | `TitleBar`                                                               | Window title bar          |
| `StatusBar`       | `status_bar::StatusBar`                                                  | Window status bar         |
| `Breadcrumb`      | `breadcrumb::Breadcrumb`                                                 | Navigation breadcrumb     |
| `Pagination`      | `pagination::Pagination`                                                 | Page navigation           |
| `Accordion`       | `accordion::Accordion`                                                   | Collapsible sections      |
| `Collapsible`     | `collapsible::Collapsible`                                               | Single collapsible        |
| `GroupBox`        | `group_box::GroupBox`                                                    | Labeled container         |
| `Resizable`       | `resizable::{h_resizable, v_resizable, resizable_panel, ResizableState}` | Draggable split panes     |
| `Scrollbar`       | `scroll::Scrollbar`                                                      | Custom scrollbar          |

### Data Display

| Component         | Import                                          | Notes                         |
| ----------------- | ----------------------------------------------- | ----------------------------- |
| `DataTable`       | `table::{DataTable, TableState, TableDelegate}` | Stateful. Full-featured table |
| `Table`           | `table::{Table, ...}`                           | Simpler table                 |
| `VirtualList`     | `{v_virtual_list, h_virtual_list}`              | High-perf large lists         |
| `List`            | `list::{List, ListState, ListDelegate}`         | Stateful. Searchable list     |
| `Tree`            | `tree::{Tree, TreeState, TreeItem, TreeEntry}`  | Stateful. Hierarchy           |
| `DescriptionList` | `description_list::DescriptionList`             | Key-value pairs               |
| `Settings`        | `setting::Settings`                             | Settings panel                |

### Chat & Messaging

| Component         | Import                                                   | Notes                                 |
| ----------------- | -------------------------------------------------------- | ------------------------------------- |
| `Message`         | `message::{Message, MessageContent, MessageAlignment}`   | Stateless. Chat message row           |
| `Bubble`          | `bubble::{Bubble, BubbleContent, BubbleVariant}`         | Stateless. Message bubble             |
| `Attachment`      | `attachment::{Attachment, AttachmentContent, ...}`       | Stateless. File/media attachment card |
| `MessageScroller` | `message_scroller::{MessageScroller, MessageScrollerState}` | Stateful. Auto-scrolling message list |

### Charts

| Component | Import                                                          | Notes                          |
| --------- | --------------------------------------------------------------- | ------------------------------ |
| `Chart`   | `chart::{AreaChart, BarChart, LineChart, PieChart, RadarChart}` | Bar, line, area, pie charts    |
| `Plot`    | `plot::Plot`                                                    | `#[derive(IntoPlot)]` for data |

## Testing

**UI integration testing** means rendering real components in headless windows,
simulating input, and checking state, focus, layout and owner callbacks. Use
`#[gpui_kit::test]` to run tests and `gpui_kit::test` to operate and inspect the UI.
When asked to add component interaction coverage, describe it as UI integration testing.

For unit tests, GPUI context tests or UI integration tests, read
[Testing](gpui/test.md). It includes dependency setup, a complete
runnable UI flow, scoped native interactions, frame/async handling and the
limits of accessibility and geometry assertions. Use the production view and
verify the action's outcome through normal Rust assertions.

## GPUI References

Load the file for the mechanism the task touches. Each file starts with a
contents line.

| Topic                       | File                                                   | Load when                                                       |
| --------------------------- | ------------------------------------------------------ | --------------------------------------------------------------- |
| Actions & keybindings       | [action.md](gpui/action.md)                 | `actions!`, `bind_keys`, `on_action`, `key_context`             |
| Async & background tasks    | [async.md](gpui/async.md)                   | `cx.spawn`, `background_spawn`, `Task`, async I/O               |
| Context management          | [context.md](gpui/context.md)               | `App`, `Window`, `Context<T>`, `AsyncApp`                       |
| Custom elements (low-level) | [element.md](gpui/element.md)               | `Element` trait, `request_layout`, `prepaint`, `paint`          |
| Entity state                | [entity.md](gpui/entity.md)                 | `Entity<T>`, `WeakEntity`, state management                     |
| Events & subscriptions      | [event.md](gpui/event.md)                   | `cx.emit`, `cx.subscribe`, `cx.observe`                         |
| Focus & keyboard nav        | [focus-handle.md](gpui/focus-handle.md)     | `FocusHandle`, `track_focus`, Tab navigation                    |
| Global state                | [global.md](gpui/global.md)                 | `Global` trait, `cx.set_global`, app-wide config                |
| Layout & styling            | [layout-style.md](gpui/layout-style.md)     | `div()`, `h_flex()`, `v_flex()`, flexbox, overflow, positioning |
| ElementId                   | [element-id.md](gpui/element-id.md)         | `ElementId`, `.id()`, uniqueness rules, stateful elements       |
| Testing                     | [test.md](gpui/test.md)                     | `#[gpui_kit::test]`, `TestAppContext`, `VisualTestContext`      |

Deep dives, for when the topic file is not enough:

- **Element trait**: [element-api.md](gpui/element-api.md) (complete API, hitbox, events) ·
  [element-patterns.md](gpui/element-patterns.md) (text, interactive, container, composite) ·
  [element-examples.md](gpui/element-examples.md) (full examples) ·
  [element-best-practices.md](gpui/element-best-practices.md) (performance, state, pitfalls) ·
  [element-advanced.md](gpui/element-advanced.md) (custom layouts, async updates, virtual lists)
- **Entities**: [entity-api.md](gpui/entity-api.md) (complete API, lifecycle) ·
  [entity-patterns.md](gpui/entity-patterns.md) (model-view, cross-entity, observer) ·
  [entity-best-practices.md](gpui/entity-best-practices.md) (memory, performance) ·
  [entity-advanced.md](gpui/entity-advanced.md) (collections, registry, debounce, state machines)
- **Testing**: [test-examples.md](gpui/test-examples.md) (organization, setup, assertions, running tests) ·
  [test-reference.md](gpui/test-reference.md) (re-entrancy, property tests, mocking)


> Adapted from the [GPUI Kit skill](https://github.com/longbridge/gpui-kit/blob/main/skills/gpui-kit/SKILL.md), [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Merged 2026-09-28; guide links, bootstrap, and dependency policy updated.

# Worked Paper-to-GPUI example

Use this example to structure a translation. Adapt every API to the target
checkout; do not paste it blindly.

## Contents

- [Scenario](#scenario)
- [Paper evidence](#paper-evidence)
- [Translation decisions](#translation-decisions)
- [GPUI implementation shape](#gpui-implementation-shape)
- [Iteration notes](#iteration-notes)
- [Bad translation patterns](#bad-translation-patterns)

## Scenario

The selected Paper artboard is a 960×640 desktop settings window:

- 220px navigation sidebar;
- flexible content area;
- 48px top bar;
- 16px outer content padding;
- repeated 36px navigation rows;
- a 560px maximum-width form;
- one selected navigation item;
- system icons exported as SVG.

The GPUI app already has:

- a `SettingsView` entity;
- theme colors;
- a shared button component;
- asset loading;
- actions for changing settings sections.

The task is visual translation, not a state-management rewrite.

## Paper evidence

After `get_basic_info` and `get_selection`, collect:

```text
file: Desktop App
page: Settings
root: 12:44 / Settings - General
root size: 960 x 640
capture: 1920 x 1280 (2x)
```

Representative evidence table:

| Node | Role | Bounds | Layout | Type/paint | Behavior |
|---|---|---|---|---|---|
| `12:44` | window content | 960×640 | row | `#f7f7f5` | fixed example viewport |
| `12:45` | sidebar | 220×640 | column, p12, gap4 | `#efefec`, right border `#deded9` | scroll if short |
| `12:53` | active row | 196×36 | row, px10, gap8, centered | radius 6, `#deded8` | selected |
| `12:71` | content | flex×640 | column | `#ffffff` | flexible |
| `12:72` | top bar | flex×48 | row, px16, centered | bottom border | fixed height |
| `12:80` | form | max 560 | column, gap20 | heading/body tokens | scroll content |

Computed style sample:

```text
sidebar:
  width: 220px
  padding: 12px
  gap: 4px
  background: #efefec
  border-right: 1px solid #deded9

active row:
  height: 36px
  padding-inline: 10px
  gap: 8px
  border-radius: 6px
  background: #deded8

row label:
  font-family: "Inter"
  font-weight: 500
  font-size: 13px
  line-height: 18px
  color: #242421
```

Before implementing, verify whether the GPUI app actually uses Inter. If the app
has an intentional existing UI font and Paper should follow the app, resolve
that product decision rather than silently mixing systems.

## Translation decisions

### Root

Use a flex row with full size. Do not assign the content region a captured fixed
width; make it `.flex_1()`.

### Sidebar

Use a fixed 220px width and fixed-shrink behavior. Use column flex. Model the
right divider as either a 1px border or an explicit separator, based on overlay
alignment.

### Navigation rows

Use one reusable row recipe/component because the geometry repeats and it has
selected, hover, and click behavior. Keep the visual icon at 16px inside the
36px row; the whole row is the hit target.

### Content

Use a fixed 48px toolbar and a flexible scrolling body. Constrain the form with
`max_w(px(560.0))`; do not center every child individually.

### Tokens

Map Paper colors to existing semantic theme values:

```text
#efefec -> theme.sidebar_background
#deded9 -> theme.border
#deded8 -> theme.element_selected
#242421 -> theme.text
```

If any semantic token resolves differently from Paper, first determine whether
the design or app theme is authoritative for that surface.

## GPUI implementation shape

Current GPUI-style skeleton:

```rust
use gpui::{
    div, prelude::*, px, Context, FontWeight, IntoElement, Render, Window,
};

pub struct SettingsView {
    selected: SettingsSection,
}

impl Render for SettingsView {
    fn render(
        &mut self,
        _window: &mut Window,
        cx: &mut Context<Self>,
    ) -> impl IntoElement {
        let theme = cx.theme();

        div()
            .size_full()
            .flex()
            .flex_row()
            .bg(theme.surface)
            .child(
                div()
                    .w(px(220.0))
                    .h_full()
                    .flex_none()
                    .flex()
                    .flex_col()
                    .gap(px(4.0))
                    .p(px(12.0))
                    .bg(theme.sidebar_background)
                    .border_r_1()
                    .border_color(theme.border)
                    .children(
                        SettingsSection::ALL
                            .iter()
                            .copied()
                            .map(|section| self.render_nav_row(section, cx)),
                    ),
            )
            .child(
                div()
                    .min_w(px(0.0))
                    .h_full()
                    .flex_1()
                    .flex()
                    .flex_col()
                    .child(
                        div()
                            .h(px(48.0))
                            .w_full()
                            .flex_none()
                            .flex()
                            .items_center()
                            .px(px(16.0))
                            .border_b_1()
                            .border_color(theme.border)
                            .font_weight(FontWeight::MEDIUM)
                            .text_size(px(13.0))
                            .line_height(px(18.0))
                            .child(self.selected.title()),
                    )
                    .child(
                        div()
                            .min_h(px(0.0))
                            .flex_1()
                            .overflow_y_scroll()
                            .p(px(16.0))
                            .child(
                                div()
                                    .w_full()
                                    .max_w(px(560.0))
                                    .flex()
                                    .flex_col()
                                    .gap(px(20.0))
                                    .children(self.render_selected_section(cx)),
                            ),
                    ),
            )
    }
}
```

The helper for a stateful row might follow the app's existing component system.
If it stays local:

```rust
impl SettingsView {
    fn render_nav_row(
        &self,
        section: SettingsSection,
        cx: &mut Context<Self>,
    ) -> impl IntoElement {
        let selected = self.selected == section;
        let theme = cx.theme();

        div()
            .id(("settings-nav", section))
            .h(px(36.0))
            .w_full()
            .flex()
            .items_center()
            .gap(px(8.0))
            .px(px(10.0))
            .rounded(px(6.0))
            .text_size(px(13.0))
            .line_height(px(18.0))
            .font_weight(FontWeight::MEDIUM)
            .text_color(theme.text)
            .when(selected, |row| row.bg(theme.element_selected))
            .when(!selected, |row| {
                row.hover(|style| style.bg(theme.element_hover))
            })
            .child(
                gpui::svg()
                    .path(section.icon_path())
                    .size(px(16.0))
                    .text_color(theme.icon),
            )
            .child(section.title())
            .on_click(cx.listener(move |this, _event, _window, cx| {
                this.selected = section;
                cx.notify();
            }))
    }
}
```

Important adaptation points:

- `cx.theme()` is project-specific and may not exist.
- `FontWeight` constants and SVG tint behavior vary by checkout.
- The target app may dispatch an action instead of mutating `selected`.
- The exact scroll helper can differ.
- A borrowed theme may need copied/cloned fields before entering closures.

Search the target repo and adjust while preserving the visual decisions.

### Why `min_w(px(0.0))` and `min_h(px(0.0))` matter

Flexible children can refuse to shrink below their content size depending on the
layout context. Explicit zero minima often prevent accidental horizontal
overflow and allow the body scroll region to occupy the remaining height. Keep
them only where the target layout demonstrates the need.

### Why exact methods come before shortcuts

These are not automatically equivalent:

```rust
.gap_2()
.gap(px(8.0))
```

They match only if the pinned GPUI scale defines `gap_2` as 8px. Use the exact
value during fidelity work and consolidate later.

## Iteration notes

### First capture

Suppose the GPUI screenshot shows:

- sidebar 2px too wide;
- active rows 1px too tall;
- toolbar label 3px too low;
- form wraps earlier;
- icons look soft.

Fix in dependency order:

1. Confirm the content crop excludes a 2px native window border.
2. Confirm sidebar width includes or excludes its divider the same way as Paper.
3. Verify the actual font family/weight before changing row height.
4. Set explicit line height and inspect baseline alignment.
5. Verify content padding and maximum width.
6. Confirm SVGs are exported, not raster screenshots, and render at 16 logical
   pixels.

Do not apply arbitrary negative margins to four separate labels.

### Second capture

If geometry aligns but the screen looks darker:

- compare resolved theme colors to Paper values;
- inspect opacity inheritance;
- inspect the border alpha;
- inspect native text antialiasing separately;
- compare shadow strength.

### Interaction pass

Test:

- selected row remains selected after rerender;
- hover does not override selected paint incorrectly;
- row click target fills 196×36;
- keyboard focus is visible if rows are focusable;
- body scroll does not move the top bar;
- narrow width truncates or changes layout intentionally.

## Bad translation patterns

### Screenshot as background

```rust
img("settings-screen.png").size_full()
```

This is not an implementation. It breaks state, input, accessibility, scaling,
theme, and content.

### Coordinate dump

```rust
div()
    .absolute()
    .left(px(236.0))
    .top(px(64.0))
```

This is appropriate only for real overlap. It is fragile for a normal form.

### Hardcoded demo state replacing the app

```rust
let selected = "General";
```

Use the existing state/action model. Paper represents one state, not the whole
product contract.

### Blind JSX transcription

Paper JSX might emit nested web wrappers or Tailwind classes. Translating each
wrapper and class literally can preserve accidental DOM structure while losing
native component behavior. Use it to understand layout, then implement the
smallest GPUI tree that preserves geometry and semantics.

### Premature abstraction

Do not build a universal `CssStyle` parser or generate GPUI from arbitrary Paper
JSON for a single screen. Directly implement the confirmed patterns unless the
user explicitly asks for a generator.

---
url: /base/primitives/color-picker.md
description: State and interaction foundations for selecting colors in a custom picker UI.
---

# Color Picker

State and interaction foundations for selecting colors in a custom picker UI.

Like every `gpui-base` primitive, Color Picker supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- color-picker
```

## Import

```rust
use gpui_kit::base::{ColorPicker, ColorPickerEvent, ColorPickerState, ColorSwatch};
```

## Anatomy and API

The example composes `ColorPicker`, `ColorSwatch`, and `ColorPickerState`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

`ColorPicker` is the controlled root: it carries the trigger's accessibility semantics and focus, opens on Confirm, and dismisses on Cancel. `ColorSwatch` is one selectable color in a palette, carrying radio semantics, an accessible hex name, and the hover and activation callbacks a picker previews and commits with.

The authoritative module is [`components/color_picker.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/color_picker.rs). Native and browser previews compile this same file.

## State and events

`ColorPickerState` owns the committed color, the transient preview shown while the user hovers or edits, the controlled open state, and the active panel. It also owns a hex `InputState` and four component `SliderState`s and keeps all of them in sync, so an application renders those with its own input and slider presentation rather than reconciling them itself. Committing a color emits `ColorPickerEvent::Change`.

A color supplied to `default_value` cannot reach the hex field and sliders without a window, so call `sync_pending_value` from render; it is a no-op once nothing is pending.

Retain the state's entity on the parent view.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;
use gpui::{Focusable as _, Hsla, MouseButton};

impl BaseShowcase {
    pub(in super::super) fn color_picker(
        &self,
        window: &mut Window,
        cx: &mut Context<Self>,
    ) -> impl IntoElement {
        // A builder-supplied default cannot reach the hex field and the sliders
        // without a window, so flush it on the first render.
        self.color_picker
            .update(cx, |state, cx| state.sync_pending_value(window, cx));

        let picker = self.color_picker.read(cx);
        let open = picker.is_open();
        let selected = picker.value();
        let displayed = picker
            .displayed_color()
            .unwrap_or(super::example_rgb(0x171717).into());
        let hex = picker.hex_input().read(cx).value();
        let focus_handle = picker.focus_handle(cx);
        let hex_input = picker.hex_input().clone();
        let state = self.color_picker.clone();

        let trigger_state = state.clone();
        let trigger = div()
            .id("color-trigger")
            .w_full()
            .h_7()
            .px_2()
            .flex()
            .items_center()
            .gap_2()
            .border_1()
            .border_color(super::example_rgb(0x171717))
            .bg(super::example_rgb(0xffffff))
            .on_click(move |_, _, cx| {
                trigger_state.update(cx, |state, cx| state.toggle_open(cx));
            })
            .child(
                div()
                    .size(px(14.))
                    .bg(displayed)
                    .border_1()
                    .border_color(super::example_rgb(0x171717)),
            )
            .child(hex)
            .child(div().flex_1())
            .child(super::chevron(open));

        let swatches = div().flex().gap_1().children(
            [0xdc2626u32, 0xd97706, 0x16a34a, 0x2563eb, 0x7c3aed]
                .into_iter()
                .enumerate()
                .map(|(index, value)| {
                    let color: Hsla = super::example_rgb(value).into();
                    let hover_state = state.clone();
                    let click_state = state.clone();
                    ColorSwatch::new(("swatch", index), color)
                        .selected(selected == Some(color))
                        .size(px(24.))
                        .bg(color)
                        .border_1()
                        .border_color(if selected == Some(color) {
                            super::example_rgb(0x171717)
                        } else {
                            super::example_rgb(0xffffff)
                        })
                        // Hovering previews without committing; leaving restores
                        // the committed color.
                        .on_hover(move |color, entered, window, cx| {
                            hover_state.update(cx, |state, cx| {
                                if entered {
                                    state.preview_color(color, window, cx);
                                } else {
                                    state.clear_preview(window, cx);
                                }
                            });
                        })
                        .on_click(move |color, _, window, cx| {
                            click_state
                                .update(cx, |state, cx| state.select_color(color, window, cx));
                        })
                }),
        );

        let content = div()
            .w(px(220.))
            .mt_1()
            .p_2()
            .flex()
            .flex_col()
            .gap_2()
            .border_1()
            .border_color(super::example_rgb(0x171717))
            .bg(super::example_rgb(0xffffff))
            .child(swatches)
            .child(
                InputBase::new("color-hex-input")
                    .w_full()
                    .h_7()
                    .px_2()
                    .border_1()
                    .border_color(super::example_rgb(0xd4d4d4))
                    .styles(|styles| {
                        styles.focused(|style| style.border_color(super::example_rgb(0x171717)))
                    })
                    .on_mouse_down(MouseButton::Left, move |_, window, cx| {
                        hex_input.update(cx, |input, cx| input.focus(window, cx));
                    })
                    .child(picker.hex_input().clone()),
            );

        let open_state = state.clone();
        let root = ColorPicker::new("example-color-picker")
            .open(open)
            .track_focus(&focus_handle)
            .accessibility_label("Brand color")
            .on_open_change(move |open, _, cx| {
                open_state.update(cx, |state, cx| state.set_open(open, cx));
            })
            .w(px(220.))
            .text_xs()
            .child(trigger);

        Popup::new("example-color-picker-popup", root).when(open, |this| this.content(content))
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Provide a textual color value and keyboard controls; never communicate selection by color alone. The root exposes the trigger's expanded state, and each swatch exposes its hex value as its accessible name plus its selected state, so a palette never depends on color alone.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/color-picker) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/color-picker.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.

---
url: /base/primitives/dialog.md
description: A composable modal surface with focus management, backdrop, title, and close parts.
---

# Dialog

A composable modal surface with focus management, backdrop, title, and close parts.

Like every `gpui-base` primitive, Dialog supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- dialog
```

## Import

```rust
use gpui_kit::base::{Dialog, DialogBackdrop, DialogClose, DialogDescription, DialogPopup, DialogTitle, DialogTrigger};
```

## Anatomy and API

The example composes `Dialog`, `DialogBackdrop`, `DialogClose`, `DialogDescription`, `DialogPopup`, `DialogTitle`, `DialogTrigger`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/dialog.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/dialog.rs). Native and browser previews compile this same file.

## State and events

`Dialog` manages modal presentation and dismissal; application callbacks own submitted work.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;
use gpui::{MouseButton, relative};

impl BaseShowcase {
    pub(in super::super) fn dialog(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let open = self.dialog_open;
        let entity = cx.entity().downgrade();
        let open_entity = entity.clone();

        div()
            .child(
                Button::new("open-dialog")
                    .h_7()
                    .line_height(relative(1.))
                    .px_3()
                    .flex()
                    .items_center()
                    .justify_center()
                    .bg(gpui::black())
                    .text_color(gpui::white())
                    .on_click(move |_, _, cx| {
                        _ = open_entity.update(cx, |this, cx| {
                            this.dialog_open = true;
                            cx.notify();
                        });
                    })
                    .child("Edit profile"),
            )
            .child(
                Dialog::new(cx)
                    .open(open)
                    .on_open_change(move |open, _, _, cx| {
                        _ = entity.update(cx, |this, cx| {
                            this.dialog_open = open;
                            cx.notify();
                        });
                    })
                    .backdrop(
                        DialogBackdrop::new()
                            .absolute()
                            .inset_0()
                            .bg(super::example_rgb(0x000000))
                            .opacity(0.2),
                    )
                    .popup(
                        DialogPopup::new()
                            .w_72()
                            .p_3()
                            .flex()
                            .flex_col()
                            .items_stretch()
                            .text_xs()
                            .bg(super::example_rgb(0xffffff))
                            .border_1()
                            .border_color(super::example_rgb(0xd4d4d4))
                            .child(
                                DialogTitle::new()
                                    .font_weight(gpui::FontWeight::SEMIBOLD)
                                    .child("Edit profile"),
                            )
                            .child(
                                DialogDescription::new()
                                    .mt_2()
                                    .text_color(super::example_rgb(0x737373))
                                    .child("Update the public details shown on your profile."),
                            )
                            .child(div().mt_3().text_sm().child("Display name"))
                            .child(
                                InputBase::new("dialog-name")
                                    .mt_2()
                                    .w_full()
                                    .h_7()
                                    .px_2()
                                    .border_1()
                                    .border_color(super::example_rgb(0xd4d4d4))
                                    .on_mouse_down(MouseButton::Left, {
                                        let input = self.input.clone();
                                        move |_, window, cx| {
                                            input.update(cx, |state, cx| state.focus(window, cx));
                                        }
                                    })
                                    .child(self.input.clone()),
                            )
                            .child(
                                div()
                                    .mt_3()
                                    .flex()
                                    .justify_end()
                                    .gap_2()
                                    .child(
                                        gpui_base::DialogClose::new().child(
                                            Button::new("dialog-cancel")
                                                .h_7()
                                                .line_height(relative(1.))
                                                .px_3()
                                                .flex()
                                                .items_center()
                                                .justify_center()
                                                .border_1()
                                                .border_color(super::example_rgb(0xd4d4d4))
                                                .child("Cancel"),
                                        ),
                                    )
                                    .child(
                                        Button::new("dialog-save")
                                            .h_7()
                                            .line_height(relative(1.))
                                            .px_3()
                                            .flex()
                                            .items_center()
                                            .justify_center()
                                            .bg(super::example_rgb(0x171717))
                                            .text_color(super::example_rgb(0xffffff))
                                            .on_click({
                                                let entity = cx.entity().downgrade();
                                                move |_, _, cx| {
                                                    _ = entity.update(cx, |this, cx| {
                                                        this.dialog_open = false;
                                                        cx.notify();
                                                    });
                                                }
                                            })
                                            .child("Save changes"),
                                    ),
                            ),
                    ),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Provide title, initial and return focus, a focus trap, Escape policy, and explicit close action.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/dialog) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/dialog.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.

---
url: /base/primitives/sheet.md
description: A modal surface that enters from an edge while managing dismissal and focus.
---

# Sheet

A modal surface that enters from an edge while managing dismissal and focus.

Like every `gpui-base` primitive, Sheet supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- sheet
```

## Import

```rust
use gpui_kit::base::{Sheet};
```

## Anatomy and API

The example composes `Sheet`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/sheet.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/sheet.rs). Native and browser previews compile this same file.

## State and events

Open and dismissal mirror a dialog while placement chooses the entering edge.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::relative;

use super::*;

impl BaseShowcase {
    pub(in super::super) fn sheet(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let open = self.sheet_open;
        let entity = cx.entity().downgrade();
        let open_sheet = entity.clone();
        let trigger = Button::new("open-sheet")
            .h_7()
            .px_2()
            .text_xs()
            .flex()
            .items_center()
            .justify_center()
            .border_1()
            .border_color(super::example_rgb(0x171717))
            .bg(super::example_rgb(0xffffff))
            .child("Open settings")
            .on_click(move |_, _, cx| {
                _ = open_sheet.update(cx, |this, cx| {
                    this.sheet_open = true;
                    cx.notify();
                });
            });

        div()
            .size_full()
            .min_h_64()
            .text_xs()
            .flex()
            .items_center()
            .justify_center()
            .child(trigger)
            .when(open, |this| {
                this.child(
                    Sheet::new(cx)
                        .request_close({
                            let entity = entity.clone();
                            move |_, cx| {
                                _ = entity.update(cx, |this, cx| {
                                    this.sheet_open = false;
                                    cx.notify();
                                });
                            }
                        })
                        .overlay(
                            div()
                                .absolute()
                                .inset_0()
                                .bg(super::example_rgb(0x000000))
                                .opacity(0.15),
                        )
                        .surface(
                            div()
                                .absolute()
                                .right_0()
                                .top_0()
                                .h_full()
                                .w(px(210.))
                                .p_3()
                                .bg(super::example_rgb(0xffffff))
                                .border_1()
                                .border_color(super::example_rgb(0x171717))
                                .child(
                                    div()
                                        .font_weight(gpui::FontWeight::SEMIBOLD)
                                        .child("Settings"),
                                )
                                .child(
                                    div().mt_4().child("Workspace name").child(
                                        div()
                                            .mt_1()
                                            .h_7()
                                            .px_2()
                                            .flex()
                                            .items_center()
                                            .border_1()
                                            .border_color(super::example_rgb(0xa3a3a3))
                                            .child("Acme Studio"),
                                    ),
                                )
                                .child(
                                    div()
                                        .mt_2()
                                        .text_color(super::example_rgb(0x525252))
                                        .child("Update the workspace preferences for your team."),
                                )
                                .child(
                                    div()
                                        .mt_4()
                                        .py_1()
                                        .border_t_1()
                                        .border_color(super::example_rgb(0xd4d4d4))
                                        .child("Notifications  ·  Enabled"),
                                )
                                .child(
                                    div().mt_3().flex().justify_end().child(
                                        Button::new("close-sheet")
                                            .h_7()
                                            .line_height(relative(1.))
                                            .px_3()
                                            .flex()
                                            .items_center()
                                            .justify_center()
                                            .bg(gpui::black())
                                            .text_color(gpui::white())
                                            .child("Done")
                                            .on_click({
                                                let entity = entity.clone();
                                                move |_, _, cx| {
                                                    _ = entity.update(cx, |this, cx| {
                                                        this.sheet_open = false;
                                                        cx.notify();
                                                    });
                                                }
                                            }),
                                    ),
                                ),
                        ),
                )
            })
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Apply dialog semantics: title it, trap and restore focus, and provide close.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/sheet) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/sheet.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.

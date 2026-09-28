---
url: /base/primitives/alert-dialog.md
description: A modal confirmation surface for actions that need an explicit decision.
---

# Alert Dialog

A modal confirmation surface for actions that need an explicit decision.

Like every `gpui-base` primitive, Alert Dialog supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- alert-dialog
```

## Import

```rust
use gpui_kit::base::{AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogDescription, AlertDialogPopup, AlertDialogTitle, AlertDialogTrigger};
```

## Anatomy and API

The example composes `AlertDialog`, `AlertDialogAction`, `AlertDialogCancel`, `AlertDialogDescription`, `AlertDialogPopup`, `AlertDialogTitle`, `AlertDialogTrigger`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/alert_dialog.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/alert_dialog.rs). Native and browser previews compile this same file.

## State and events

Opening and dismissal are managed by `AlertDialog`; application action buttons decide when destructive work is committed.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::relative;

use super::*;

impl BaseShowcase {
    pub(in super::super) fn alert_dialog(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let open = self.alert_dialog_open;
        let entity = cx.entity().downgrade();
        let open_entity = entity.clone();
        let ok_entity = entity.clone();
        let cancel_entity = entity.clone();
        let action_entity = entity.clone();

        div()
            .child(
                Button::new("open-alert-dialog")
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
                            this.alert_dialog_open = true;
                            cx.notify();
                        });
                    })
                    .child("Delete project"),
            )
            .child(
                AlertDialog::new(cx)
                    .open(open)
                    .on_open_change(move |open, _, _, cx| {
                        _ = entity.update(cx, |this, cx| {
                            this.alert_dialog_open = open;
                            cx.notify();
                        });
                    })
                    .on_ok(move |_, _, cx| {
                        _ = ok_entity.update(cx, |this, cx| {
                            this.alert_dialog_open = false;
                            cx.notify();
                        });
                        true
                    })
                    .backdrop(
                        AlertDialogBackdrop::new()
                            .absolute()
                            .inset_0()
                            .bg(super::example_rgb(0x000000))
                            .opacity(0.18),
                    )
                    .popup(
                        AlertDialogPopup::new()
                            .w_72()
                            .p_3()
                            .bg(super::example_rgb(0xffffff))
                            .border_1()
                            .border_color(super::example_rgb(0x171717))
                            .child(AlertDialogTitle::new().child("Delete project?"))
                            .child(
                                AlertDialogDescription::new()
                                    .mt_2()
                                    .text_xs()
                                    .text_color(super::example_rgb(0x525252))
                                    .child(
                                        "This permanently deletes Acme Studio and all of its data.",
                                    ),
                            )
                            .child(
                                div()
                                    .mt_3()
                                    .flex()
                                    .justify_end()
                                    .gap_2()
                                    .child(
                                        AlertDialogCancel::new().child(
                                            Button::new("cancel-delete")
                                                .px_3()
                                                .h_7()
                                                .flex()
                                                .items_center()
                                                .text_xs()
                                                .border_1()
                                                .border_color(super::example_rgb(0xd4d4d4))
                                                .on_click(move |_, _, cx| {
                                                    _ = cancel_entity.update(cx, |this, cx| {
                                                        this.alert_dialog_open = false;
                                                        cx.notify();
                                                    });
                                                })
                                                .child("Cancel"),
                                        ),
                                    )
                                    .child(
                                        AlertDialogAction::new().child(
                                            Button::new("confirm-delete")
                                                .px_3()
                                                .h_7()
                                                .flex()
                                                .items_center()
                                                .text_xs()
                                                .border_1()
                                                .border_color(super::example_rgb(0x171717))
                                                .bg(super::example_rgb(0x171717))
                                                .text_color(super::example_rgb(0xffffff))
                                                .on_click(move |_, _, cx| {
                                                    _ = action_entity.update(cx, |this, cx| {
                                                        this.alert_dialog_open = false;
                                                        cx.notify();
                                                    });
                                                })
                                                .child("Delete"),
                                        ),
                                    ),
                            ),
                    ),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Provide title and description, trap focus, offer cancel, and restore focus to the opener.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/alert-dialog) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/alert-dialog.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.

---
url: /base/primitives/combobox.md
description: A text input paired with keyboard-navigable suggestions and selection behavior.
---

# Combobox

A text input paired with keyboard-navigable suggestions and selection behavior.

Like every `gpui-base` primitive, Combobox supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- combobox
```

## Import

```rust
use gpui_kit::base::{Combobox};
```

## Anatomy and API

The example composes `Combobox`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/combobox.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/combobox.rs). Native and browser previews compile this same file.

## State and events

The input state owns query text while the delegate supplies choices, filtering, and selection.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;
use gpui::MouseButton;

impl BaseShowcase {
    pub(in super::super) fn combobox(
        &self,
        _window: &mut Window,
        cx: &mut Context<Self>,
    ) -> impl IntoElement {
        let open = self.combobox_open;
        let query = self.combobox_query.read(cx).value().to_lowercase();
        let selected = self.combobox_selection.clone();
        let entity = cx.entity().downgrade();
        let query_state = self.combobox_query.clone();
        let open_query_state = self.combobox_query.clone();
        let trigger_entity = cx.entity().downgrade();
        let trigger_query_state = self.combobox_query.clone();

        let combobox = Combobox::new("example-combobox")
            .open(open)
            .on_open_change(move |open, window, cx| {
                _ = entity.update(cx, |this, cx| {
                    this.combobox_open = open;
                    cx.notify();
                });
                if open {
                    open_query_state.update(cx, |state, cx| state.focus(window, cx));
                }
            })
            .w_56()
            .child(
                div()
                    .id("combobox-trigger")
                    .w_full()
                    .h_7()
                    .px_2()
                    .flex()
                    .items_center()
                    .justify_between()
                    .border_1()
                    .border_color(super::example_rgb(0xd4d4d4))
                    .text_xs()
                    .bg(super::example_rgb(0xffffff))
                    .on_click(move |_, window, cx| {
                        _ = trigger_entity.update(cx, |this, cx| {
                            this.combobox_open = !open;
                            cx.notify();
                        });
                        if !open {
                            trigger_query_state.update(cx, |state, cx| state.focus(window, cx));
                        }
                    })
                    .child(selected)
                    .child(
                        div()
                            .text_color(super::example_rgb(0x737373))
                            .child(super::chevron(false)),
                    ),
            );
        let popup = div()
            .w_56()
            .text_xs()
            .border_1()
            .border_color(super::example_rgb(0xd4d4d4))
            .bg(super::example_rgb(0xffffff))
            .child(
                InputBase::new("combobox-search")
                    .w_full()
                    .h_7()
                    .px_2()
                    .border_b_1()
                    .border_color(super::example_rgb(0xe5e5e5))
                    .on_mouse_down(MouseButton::Left, move |_, window, cx| {
                        query_state.update(cx, |state, cx| state.focus(window, cx));
                    })
                    .child(self.combobox_query.clone()),
            )
            .child(
                div().p_1().children(
                    ["GPUI", "React", "SwiftUI", "Vue"]
                        .into_iter()
                        .filter(|label| query.is_empty() || label.to_lowercase().contains(&query))
                        .map(|label| {
                            let entity = cx.entity().downgrade();
                            div()
                                .id(format!("combobox-{label}"))
                                .px_2()
                                .h_7()
                                .flex()
                                .items_center()
                                .text_xs()
                                .hover(|s| s.bg(super::example_rgb(0xf5f5f5)))
                                .on_click(move |_, _, cx| {
                                    _ = entity.update(cx, |this, cx| {
                                        this.combobox_selection = label.into();
                                        this.combobox_open = false;
                                        cx.notify();
                                    });
                                })
                                .child(label)
                        }),
                ),
            );

        Popup::new("example-combobox-popup", combobox).when(open, |this| this.content(popup))
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Synchronize input, popup, active option, and selected value; make every option keyboard reachable.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/combobox) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/combobox.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.

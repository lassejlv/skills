---
url: /base/primitives/select.md
description: A button-like selection control backed by an anchored, keyboard-navigable popup.
---

# Select

A button-like selection control backed by an anchored, keyboard-navigable popup.

Like every `gpui-base` primitive, Select supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- select
```

## Import

```rust
use gpui_kit::base::{Select};
```

## Anatomy and API

The example composes `Select`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/select.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/select.rs). Native and browser previews compile this same file.

## State and events

The delegate/state owns items and selection; activation opens the list and selection closes it.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn select(
        &self,
        combobox: bool,
        cx: &mut Context<Self>,
    ) -> impl IntoElement {
        let open = self.select_open;
        let selected = self.select_index.min(3);
        let labels = ["GPUI", "React", "SwiftUI", "Vue"];
        let entity = cx.entity().downgrade();
        let trigger_entity = entity.clone();
        let trigger = div()
            .id("select-trigger")
            .h_7()
            .px_2()
            .text_xs()
            .flex()
            .items_center()
            .justify_between()
            .border_1()
            .border_color(super::example_rgb(0x171717))
            .on_click(move |_, _, cx| {
                _ = trigger_entity.update(cx, |this, cx| {
                    this.select_open = !open;
                    cx.notify();
                });
            })
            .child(labels[selected])
            .child(super::chevron(open));
        let options = div()
            .mt_1()
            .p_1()
            .border_1()
            .border_color(super::example_rgb(0x171717))
            .bg(super::example_rgb(0xffffff))
            .children(labels.into_iter().enumerate().map(|(ix, label)| {
                let entity = entity.clone();
                div()
                    .id(("select-option", ix))
                    .px_2()
                    .py_1()
                    .flex()
                    .justify_between()
                    .hover(|this| this.bg(super::example_rgb(0xf5f5f5)))
                    .child(label)
                    .when(ix == selected, |this| this.child("✓"))
                    .on_click(move |_, _, cx| {
                        _ = entity.update(cx, |this, cx| {
                            this.select_index = ix;
                            this.select_open = false;
                            cx.notify();
                        });
                    })
            }));
        if combobox {
            let root = Combobox::new("example-combobox")
                .open(open)
                .w_56()
                .child(trigger);
            Popup::new("example-combobox-options", root)
                .when(open, |this| this.content(options))
                .into_any_element()
        } else {
            let root = Select::new("example-select")
                .open(open)
                .on_open_change({
                    let entity = entity.clone();
                    move |next, _, cx| {
                        _ = entity.update(cx, |this, cx| {
                            this.select_open = next;
                            cx.notify();
                        });
                    }
                })
                .accessibility_label("Framework")
                .w_56()
                .child(trigger);
            Popup::new("example-select-options", root)
                .when(open, |this| this.content(options))
                .into_any_element()
        }
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Set `.accessibility_label(...)` on the controlled root and
`.accessibility_value(...)` to its committed selection, not a temporary search
cursor. The root exposes its expanded state and accessible activation. Activation
requests an open-state change and moves focus between the trigger and content.
Disabled controls do not expose activation. The styled `Select` supplies its
committed value automatically, falling back to its placeholder when unselected.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/select) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/select.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.

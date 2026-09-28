---
url: /base/primitives/toggle.md
description: A controlled two-state pressable for persistent choices such as formatting.
---

# Toggle

A controlled two-state pressable for persistent choices such as formatting.

Like every `gpui-base` primitive, Toggle supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- toggle
```

## Import

```rust
use gpui_kit::base::{Toggle};
```

## Anatomy and API

The example composes `Toggle`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/toggle.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/toggle.rs). Native and browser previews compile this same file.

## State and events

Pass the controlled pressed value; `on_change` emits the requested next value.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn toggle(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let pressed = self.toggle_pressed;
        let entity = cx.entity().downgrade();
        Toggle::new("example-toggle")
            .pressed(pressed)
            .on_change(move |next, _, _, cx| {
                _ = entity.update(cx, |this, cx| {
                    this.toggle_pressed = next;
                    cx.notify();
                });
            })
            .size_7()
            .text_xs()
            .flex()
            .items_center()
            .justify_center()
            .border_1()
            .border_color(super::example_rgb(0x171717))
            .when(pressed, |this| {
                this.bg(super::example_rgb(0x171717))
                    .text_color(super::example_rgb(0xffffff))
            })
            .font_weight(gpui::FontWeight::BOLD)
            .accessibility_label("Bold")
            .child("B")
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Expose pressed state and keep a stable accessible name.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/toggle) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/toggle.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.

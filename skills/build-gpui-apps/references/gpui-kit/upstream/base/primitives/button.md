---
url: /base/primitives/button.md
description: An unstyled, accessible pressable with semantic state and keyboard activation.
---

# Button

An unstyled, accessible pressable with semantic state and keyboard activation.

Like every `gpui-base` primitive, Button supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- button
```

## Import

```rust
use gpui_kit::base::{Button};
```

## Anatomy and API

The example composes `Button`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/button.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/button.rs). Native and browser previews compile this same file.

## State and events

Activation uses GPUI click handling. Styling for hover, active, focus, and disabled states remains application-owned.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::relative;

use super::*;

impl BaseShowcase {
    pub(in super::super) fn button(&self) -> impl IntoElement {
        div()
            .flex()
            .items_center()
            .gap_2()
            .child(
                Button::new("primary-button")
                    .px_3()
                    .h_7()
                    .line_height(relative(1.))
                    .flex()
                    .items_center()
                    .text_xs()
                    .border_1()
                    .border_color(super::example_rgb(0x171717))
                    .bg(super::example_rgb(0x171717))
                    .text_color(super::example_rgb(0xffffff))
                    .hover(|style| style.bg(super::example_rgb(0x404040)))
                    .child("Save changes"),
            )
            .child(
                Button::new("secondary-button")
                    .px_3()
                    .h_7()
                    .line_height(relative(1.))
                    .flex()
                    .items_center()
                    .text_xs()
                    .border_1()
                    .border_color(super::example_rgb(0xd4d4d4))
                    .bg(super::example_rgb(0xffffff))
                    .hover(|style| style.bg(super::example_rgb(0xf5f5f5)))
                    .child("Cancel"),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Provide an accessible name, preserve keyboard activation, and expose disabled state.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/button) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/button.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.

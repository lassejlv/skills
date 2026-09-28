---
url: /base/primitives/link.md
description: An accessible link-like control with application-defined styling.
---

# Link

An accessible link-like control with application-defined styling.

Like every `gpui-base` primitive, Link supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- link
```

## Import

```rust
use gpui_kit::base::{Link};
```

## Anatomy and API

The example composes `Link`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/link.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/link.rs). Native and browser previews compile this same file.

## State and events

The link emits activation while the application defines URL or in-app navigation.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::{IntoElement, ParentElement as _, Styled as _, div};
use gpui_base::Link;

use super::super::BaseShowcase;

impl BaseShowcase {
    pub(in super::super) fn link(&self) -> impl IntoElement {
        div()
            .w_56()
            .flex()
            .flex_col()
            .gap_2()
            .text_xs()
            .child("Navigation is application-owned")
            .child(
                Link::new("example-link")
                    .href("/base/primitives/link")
                    .open_with(|href, _, _, cx| cx.open_url(href))
                    .h_7()
                    .px_3()
                    .py_0()
                    .flex()
                    .items_center()
                    .border_1()
                    .border_color(super::example_rgb(0x171717))
                    .child("Open Link documentation  →"),
            )
            .child(
                Link::new("disabled-link")
                    .href("/disabled")
                    .disabled(true)
                    .h_7()
                    .px_3()
                    .py_0()
                    .flex()
                    .items_center()
                    .border_1()
                    .border_color(super::example_rgb(0xd4d4d4))
                    .text_color(super::example_rgb(0x737373))
                    .child("Disabled destination"),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Use links for navigation, meaningful text, and a visible focus style.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/link) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/link.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.

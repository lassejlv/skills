---
url: /base/primitives/avatar.md
description: An image with composable fallback content for a person or entity.
---

# Avatar

An image with composable fallback content for a person or entity.

Like every `gpui-base` primitive, Avatar supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- avatar
```

## Import

```rust
use gpui_kit::base::{Avatar, AvatarFallback, AvatarImage};
```

## Anatomy and API

The example composes `Avatar`, `AvatarFallback`, `AvatarImage`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/avatar.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/avatar.rs). Native and browser previews compile this same file.

## State and events

`Avatar` is presentational. Supply fallback content for the image-loading and image-error paths.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn avatar(&self) -> impl IntoElement {
        div().flex().items_start().gap_2().children(
            [
                ("AM", 0xf5f5f5),
                ("JL", 0xe5e5e5),
                ("SK", 0xd4d4d4),
                ("+3", 0xffffff),
            ]
            .into_iter()
            .map(|(initials, background)| {
                Avatar::new()
                    .size(px(34.))
                    .overflow_hidden()
                    .border_1()
                    .border_color(super::example_rgb(0xa3a3a3))
                    .fallback(
                        AvatarFallback::new()
                            .flex()
                            .size_8()
                            .items_center()
                            .justify_center()
                            .bg(super::example_rgb(background))
                            .text_xs()
                            .text_color(super::example_rgb(0x262626))
                            .child(initials),
                    )
            }),
        )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Fallback text should identify the entity; decorative avatars should not duplicate nearby labels.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/avatar) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/avatar.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.

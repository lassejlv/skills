---
url: /base/primitives/tooltip.md
description: A delayed, positioned description associated with a trigger element.
---

# Tooltip

A delayed, positioned description associated with a trigger element.

Like every `gpui-base` primitive, Tooltip supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- tooltip
```

## Import

```rust
use gpui_kit::base::{Tooltip};
```

## Anatomy and API

The example composes `Tooltip`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/tooltip.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/tooltip.rs). Native and browser previews compile this same file.

## State and events

Hover or focus schedules it and exit or blur dismisses it; content is descriptive.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn tooltip(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let visible = self.tooltip_visible;
        let entity = cx.entity().downgrade();
        let trigger = div()
            .id("tooltip-trigger")
            .on_hover(move |hovered, _, cx| {
                _ = entity.update(cx, |this, cx| {
                    this.tooltip_visible = *hovered;
                    cx.notify();
                });
            })
            .child(
                Button::new("tooltip-anchor")
                    .h_7()
                    .px_2()
                    .flex()
                    .items_center()
                    .justify_center()
                    .border_1()
                    .border_color(super::example_rgb(0x171717))
                    .bg(super::example_rgb(0xffffff))
                    .child("Command menu"),
            );

        Popup::new("example-tooltip-popup", trigger)
            .text_xs()
            .when(visible, |this| {
                this.content(
                    Tooltip::new("example-tooltip")
                        .px_2()
                        .h_7()
                        .flex()
                        .items_center()
                        .justify_center()
                        .border_1()
                        .border_color(super::example_rgb(0x171717))
                        .bg(super::example_rgb(0x171717))
                        .text_color(super::example_rgb(0xffffff))
                        .child("Open command menu · ⌘K"),
                )
            })
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Show on focus as well as hover; tooltips supplement names and contain no required controls.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/tooltip) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/tooltip.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
